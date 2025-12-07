# test.py
from google import genai
from google.genai import types
import os
import dotenv
import json

# --------------------------------------------------
# SETUP CLIENT (NEW SDK)
# --------------------------------------------------
def setup_client():
    dotenv.load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set!")
    return genai.Client(api_key=api_key)


# --------------------------------------------------
# LOCAL FUNCTIONS (TOOLS)
# --------------------------------------------------
def get_weather(location: str, unit: str = "celsius"):
    return {
        "location": location,
        "temp": 30,
        "unit": unit,
        "status": "Sunny"
    }

def calculate(expression: str):
    return {"result": eval(expression)}

def get_current_time(timezone: str):
    return {"timezone": timezone, "time": "12:00:00"}

function_map = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time,
}


# --------------------------------------------------
# FUNCTION DECLARATIONS
# --------------------------------------------------
weather_fn = types.FunctionDeclaration(
    name="get_weather",
    description="Get weather",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
        },
        "required": ["location"]
    }
)

calc_fn = types.FunctionDeclaration(
    name="calculate",
    description="Calculator",
    parameters_json_schema={
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"]
    }
)

time_fn = types.FunctionDeclaration(
    name="get_current_time",
    description="Get current time for a timezone",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "enum": ["UTC","IST","EST","PST","JST"]
            }
        },
        "required": ["timezone"]
    }
)

tool = types.Tool(function_declarations=[weather_fn, calc_fn, time_fn])
default_config = types.GenerateContentConfig(tools=[tool])


# --------------------------------------------------
# EXTRACT FUNCTION CALL
# --------------------------------------------------
def extract_function_call(response):
    for cand in getattr(response, "candidates", []) or []:
        for part in getattr(cand, "content", []) or []:
            if hasattr(part, "function_call") and part.function_call:
                return part.function_call

    # fallback: new field
    fcs = getattr(response, "function_calls", None)
    if fcs:
        return fcs[0]

    return None


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------
def run():
    client = setup_client()

    while True:
        user_in = input("You: ").strip()
        if user_in.lower() in ("quit", "exit"):
            break
        if not user_in:
            continue

        # 1) Ask model
        response = client.models.generate_content(
            model="gemini-2.5-flash",     # as you wanted
            contents=user_in,
            config=default_config
        )

        fc = extract_function_call(response)

        # 2) Model requested a function call
        if fc:
            func = function_map.get(fc.name)
            if not func:
                tool_result = {"error": f"{fc.name} not implemented"}
            else:
                try:
                    tool_result = func(**fc.args)
                except Exception as e:
                    tool_result = {"error": str(e)}

            # Build tool response part
            function_response_part = types.Part.from_function_response(
                name=fc.name,
                response=tool_result
            )

            # 3) Send back function output to model
            final = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    user_in,  # plain string OK
                    types.Content(role="tool", parts=[function_response_part])
                ],
                config=default_config
            )

            print("AI:", final.text)
            continue

        # 4) No function call → normal answer
        print("AI:", response.text)


if __name__ == "__main__":
    run()
