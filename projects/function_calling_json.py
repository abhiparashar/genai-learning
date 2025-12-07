import os
import dotenv
from datetime import datetime
from google import genai

# -----------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------
def setup_gemini():
    dotenv.load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set!")
    return genai.Client(api_key=api_key)

# -----------------------------------------------------------------------------
# LOCAL FUNCTIONS
# -----------------------------------------------------------------------------
def get_weather(location: str, unit: str = "celsius"):
    data = {
        "mumbai": {"temp": 32, "condition": "Sunny", "humidity": 65},
        "delhi": {"temp": 28, "condition": "Cloudy", "humidity": 45},
        "bangalore": {"temp": 25, "condition": "Rainy", "humidity": 80},
    }

    key = location.lower()
    if key not in data:
        return {"error": f"No weather data for {location}"}

    w = data[key].copy()
    if unit == "fahrenheit":
        w["temp"] = round(w["temp"] * 9/5 + 32, 1)
        w["unit"] = "°F"
    else:
        w["unit"] = "°C"

    w["location"] = location
    return w

def calculate(expression: str):
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

def get_current_time(timezone: str):
    offsets = {"UTC": 0, "IST": 5.5, "EST": -5}
    if timezone not in offsets:
        return {"error": f"Invalid timezone {timezone}"}

    from datetime import timedelta
    now = datetime.utcnow() + timedelta(hours=offsets[timezone])

    return {
        "timezone": timezone,
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
    }

# -----------------------------------------------------------------------------
# JSON TOOLS
# -----------------------------------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get city weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "enum": ["UTC", "IST", "EST"]},
                },
                "required": ["timezone"],
            },
        },
    },
]

function_map = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time,
}

# -----------------------------------------------------------------------------
# FUNCTION EXECUTION
# -----------------------------------------------------------------------------
def execute_function_call(fn_call):
    name = fn_call["name"]
    args = fn_call["args"]
    fn = function_map.get(name)
    if not fn:
        return {"error": f"Function {name} not found"}
    return fn(**args)

# -----------------------------------------------------------------------------
# MAIN CHAT LOOP (NEW SDK)
# -----------------------------------------------------------------------------
def run():
    client = setup_gemini()
    chat = client.chats.create(model="gemini-2.5-flash")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("q", "quit", "exit"):
            break

        # send user message with tools embedded
        response = chat.send_message({
            "text": user_input,
            "tools": tools,
        })

        part = response.candidates[0].content.parts[0]

        # function call
        if "function_call" in part:
            fn_call = part["function_call"]
            result = execute_function_call(fn_call)

            response = chat.send_message({
                "function_response": {
                    "name": fn_call["name"],
                    "response": result,
                },
                "tools": tools,
            })

        print("AI:", response.text)

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    run()