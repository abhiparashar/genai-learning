import os
import json
import dotenv
import traceback
import concurrent.futures
from datetime import datetime
import google.generativeai as genai

# ----------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------

def setup_gemini():
    dotenv.load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set!")
    genai.configure(api_key=api_key)

# ----------------------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------------------

def get_weather(location: str, unit: str = "celsius") -> dict:
    weather_data = {
        "mumbai": {"temp": 32, "condition": "Sunny", "humidity": 65},
        "delhi": {"temp": 28, "condition": "Partly Cloudy", "humidity": 45},
        "bangalore": {"temp": 25, "condition": "Rainy", "humidity": 80},
        "new york": {"temp": 15, "condition": "Cloudy", "humidity": 50},
        "london": {"temp": 10, "condition": "Rainy", "humidity": 75},
    }
    key = (location or "").lower()
    if key not in weather_data:
        return {"error": f"Weather data not available for {location}"}
    data = weather_data[key].copy()
    if (unit or "celsius").lower() == "fahrenheit":
        data["temp"] = round(data["temp"] * 9 / 5 + 32, 1)
        data["unit"] = "\u00b0F"
    else:
        data["unit"] = "\u00b0C"
    data["location"] = location
    return data


def calculate(expression: str) -> dict:
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"expression": expression, "result": result, "success": True}
    except Exception as e:
        return {"expression": expression, "error": str(e), "success": False}


def get_current_time(timezone: str = "UTC") -> dict:
    offsets = {"UTC": 0, "IST": 5.5, "EST": -5, "PST": -8, "JST": 9}
    tz = (timezone or "UTC").upper()
    if tz not in offsets:
        return {"error": f"Timezone {timezone} not supported"}
    from datetime import timedelta
    utc_now = datetime.utcnow()
    local_time = utc_now + timedelta(hours=offsets[tz])
    return {
        "timezone": tz,
        "time": local_time.strftime("%H:%M:%S"),
        "date": local_time.strftime("%Y-%m-%d"),
        "day": local_time.strftime("%A"),
    }

# ----------------------------------------------------------------------------
# FUNCTION METADATA & MAP
# ----------------------------------------------------------------------------

function_map = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time,
}

# ----------------------------------------------------------------------------
# BUILD PROTO TOOLS
# ----------------------------------------------------------------------------

def build_tools_proto():
    def s_type(t):
        return genai.protos.Schema(type=t)

    # get_weather
    loc_schema = s_type(genai.protos.Type.STRING)
    unit_schema = s_type(genai.protos.Type.STRING)
    unit_schema.enum.extend(["celsius", "fahrenheit"]) 

    weather_params = genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={"location": loc_schema, "unit": unit_schema},
    )

    get_weather_decl = genai.protos.FunctionDeclaration(
        name="get_weather",
        description="Get weather information for a city",
        parameters=weather_params,
    )

    # calculate
    calc_params = genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={"expression": s_type(genai.protos.Type.STRING)},
    )
    calculate_decl = genai.protos.FunctionDeclaration(
        name="calculate",
        description="Perform a math calculation",
        parameters=calc_params,
    )

    # get_current_time
    tz_schema = s_type(genai.protos.Type.STRING)
    tz_schema.enum.extend(["UTC", "IST", "EST", "PST", "JST"]) 
    time_params = genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={"timezone": tz_schema},
    )
    time_decl = genai.protos.FunctionDeclaration(
        name="get_current_time",
        description="Get current time for a timezone",
        parameters=time_params,
    )

    tool = genai.protos.Tool(function_declarations=[get_weather_decl, calculate_decl, time_decl])
    return [tool]

# ----------------------------------------------------------------------------
# EXECUTE FUNCTION CALL (with timeout and safety)
# ----------------------------------------------------------------------------

def safe_call(func, args, timeout=5):
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(func, **args)
            return fut.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        return {"error": "function execution timed out"}
    except Exception as e:
        return {"error": str(e)}


def normalize_args(raw_args):
    try:
        if raw_args is None:
            return {}
        if isinstance(raw_args, str):
            return json.loads(raw_args)
        if isinstance(raw_args, dict):
            return raw_args
        return dict(raw_args)
    except Exception:
        return {}


def make_serializable(obj):
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return {"_to_string": str(obj)}

# ----------------------------------------------------------------------------
# RUN LOOP
# ----------------------------------------------------------------------------

def run_function_calling_demo():
    tools_proto = build_tools_proto()
    model = genai.GenerativeModel(model_name="models/gemini-flash-latest", tools=tools_proto)
    chat = model.start_chat(history=[])

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            if not user_input:
                continue

            response = chat.send_message(user_input)
            if not getattr(response, "candidates", None):
                print("Error: no candidates in response; repr:", repr(response))
                continue

            while True:
                function_responses = []
                any_call = False

                for candidate in getattr(response, "candidates", []):
                    parts = getattr(candidate.content, "parts", []) if getattr(candidate, "content", None) else []
                    for part in parts:
                        fc = getattr(part, "function_call", None)
                        if not fc:
                            continue
                        any_call = True
                        fc_name = getattr(fc, "name", None)
                        raw_args = getattr(fc, "args", None)
                        args = normalize_args(raw_args)
                        func = function_map.get(fc_name)
                        if not func:
                            result = {"error": f"Function {fc_name} not found"}
                        else:
                            result = safe_call(func, args, timeout=5)
                        result = make_serializable(result)
                        function_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=fc_name,
                                    response={"result": result},
                                )
                            )
                        )

                if not any_call:
                    break

                response = chat.send_message(function_responses)
                if not getattr(response, "candidates", None):
                    print("Error: no candidates after function response; repr:", repr(response))
                    break

            texts = []
            for candidate in getattr(response, "candidates", []):
                parts = getattr(candidate.content, "parts", []) if getattr(candidate, "content", None) else []
                for part in parts:
                    text = getattr(part, "text", None)
                    if text:
                        texts.append(text)
            final_text = "".join(texts).strip() or "(no text returned)"
            print("AI:", final_text)

        except Exception as e:
            print("Unhandled error:", e)
            traceback.print_exc()

# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------

def main():
    try:
        setup_gemini()
        run_function_calling_demo()
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
