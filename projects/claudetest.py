"""
Project 3: Function Calling Demo (ABSOLUTELY FINAL - TESTED)
=============================================================
Topics: Tool use, function calling, multi-step reasoning

Features:
- Define functions (weather, calculator, get_time)
- AI automatically decides when to call functions
- Multi-step function calling
- Display function execution flow

ALL BUGS FIXED:
- MapComposite conversion
- None response handling
- Safety filter handling
- Proper iteration checks
"""

import google.generativeai as genai
import os
import json
import dotenv
from datetime import datetime, timedelta


# ============================================================================
# SETUP
# ============================================================================

def setup_gemini():
    """Configure Gemini API"""
    dotenv.load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set!")
    genai.configure(api_key=api_key)


# ============================================================================
# FUNCTION DEFINITIONS (Tools that AI can use)
# ============================================================================

def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    Get current weather for a location
    
    Args:
        location: City name (e.g., "Mumbai", "New York")
        unit: Temperature unit - "celsius" or "fahrenheit"
    
    Returns:
        Weather information dictionary
    """
    # Simulated weather data (in real app, call actual weather API)
    weather_data = {
        "mumbai": {"temp": 32, "condition": "Sunny", "humidity": 65},
        "delhi": {"temp": 28, "condition": "Partly Cloudy", "humidity": 45},
        "bangalore": {"temp": 25, "condition": "Rainy", "humidity": 80},
        "new york": {"temp": 15, "condition": "Cloudy", "humidity": 50},
        "london": {"temp": 10, "condition": "Rainy", "humidity": 75},
        "tokyo": {"temp": 18, "condition": "Clear", "humidity": 55},
    }
    
    location_lower = location.lower()
    
    if location_lower not in weather_data:
        return {"error": f"Weather data not available for {location}"}
    
    data = weather_data[location_lower].copy()
    
    # Convert to fahrenheit if requested
    if unit.lower() == "fahrenheit":
        data["temp"] = round(data["temp"] * 9/5 + 32, 1)
        data["unit"] = "°F"
    else:
        data["unit"] = "°C"
    
    data["location"] = location.title()
    
    return data


def calculate(expression: str) -> dict:
    """
    Perform mathematical calculations
    
    Args:
        expression: Math expression (e.g., "25 * 4 + 10")
    
    Returns:
        Calculation result dictionary
    """
    try:
        # Safe evaluation (limited to math operations)
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names, {})
        return {
            "expression": expression,
            "result": result,
            "success": True
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "success": False
        }


def get_current_time(timezone: str = "UTC") -> dict:
    """
    Get current time for a timezone
    
    Args:
        timezone: Timezone name (e.g., "UTC", "IST", "EST")
    
    Returns:
        Current time information
    """
    # Simulated timezone offsets
    timezone_offsets = {
        "UTC": 0,
        "IST": 5.5,
        "EST": -5,
        "PST": -8,
        "JST": 9,
    }
    
    timezone_upper = timezone.upper()
    
    if timezone_upper not in timezone_offsets:
        return {"error": f"Timezone {timezone} not supported. Available: UTC, IST, EST, PST, JST"}
    
    # Get current UTC time and adjust
    utc_now = datetime.utcnow()
    offset_hours = timezone_offsets[timezone_upper]
    local_time = utc_now + timedelta(hours=offset_hours)
    
    return {
        "timezone": timezone_upper,
        "time": local_time.strftime("%H:%M:%S"),
        "date": local_time.strftime("%Y-%m-%d"),
        "day": local_time.strftime("%A")
    }


# ============================================================================
# FUNCTION DECLARATIONS FOR GEMINI
# ============================================================================

function_declarations = [
    {
        "name": "get_weather",
        "description": "Get current weather information for any city worldwide",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name (e.g., Mumbai, New York, London)"
                },
                "unit": {
                    "type": "string",
                    "description": "Temperature unit: 'celsius' or 'fahrenheit'",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform mathematical calculations. Supports +, -, *, /, **, (), etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '25 * 4 + 10')"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_current_time",
        "description": "Get current time and date for a specific timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone code (e.g., UTC, IST, EST, PST, JST)",
                    "enum": ["UTC", "IST", "EST", "PST", "JST"]
                }
            },
            "required": ["timezone"]
        }
    }
]


# ============================================================================
# FUNCTION MAPPING
# ============================================================================

function_map = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time
}


# ============================================================================
# EXECUTE FUNCTION CALLS
# ============================================================================

def execute_function_call(function_call):
    """
    Execute a function call from the AI
    
    Args:
        function_call: FunctionCall object from Gemini
    
    Returns:
        Function execution result
    """
    function_name = function_call.name
    
    # Convert MapComposite to regular dict
    function_args = dict(function_call.args)
    
    print(f"\n🔧 Executing: {function_name}({json.dumps(function_args, indent=2)})")
    
    # Get the actual function
    func = function_map.get(function_name)
    
    if not func:
        return {"error": f"Function {function_name} not found"}
    
    # Execute function with arguments
    try:
        result = func(**function_args)
        print(f"✅ Result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        error_result = {"error": str(e)}
        print(f"❌ Error: {error_result}")
        return error_result


# ============================================================================
# SAFE FUNCTION CALLING HANDLER
# ============================================================================

def handle_function_calling(chat, user_input):
    """
    Handle complete function calling flow with proper error handling
    
    Args:
        chat: Chat session
        user_input: User's input message
    
    Returns:
        Final AI response text
    """
    try:
        # Send initial message
        print("\n🤖 AI is thinking...")
        response = chat.send_message(user_input)
        
        # Handle function calls with safety checks
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Safety check: Response exists
            if not response:
                print("⚠️ No response from AI")
                return None
            
            # Safety check: Has candidates
            if not response.candidates:
                print("⚠️ Response blocked or empty")
                return None
            
            # Safety check: Has content
            if not response.candidates[0].content:
                print("⚠️ No content in response")
                return None
            
            # Safety check: Has parts
            if not response.candidates[0].content.parts:
                break
            
            # Check for function calls
            function_calls_found = []
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls_found.append(part.function_call)
            
            # No function calls - we're done
            if not function_calls_found:
                break
            
            # Execute all function calls
            function_responses = []
            for function_call in function_calls_found:
                result = execute_function_call(function_call)
                
                # Build function response
                function_responses.append({
                    'function_response': {
                        'name': function_call.name,
                        'response': result
                    }
                })
            
            # Send function results back to AI
            if function_responses:
                print("\n🤖 AI processing function results...")
                try:
                    response = chat.send_message(function_responses)
                except Exception as e:
                    print(f"⚠️ Error sending function results: {e}")
                    return None
            else:
                break
        
        # Extract final text response
        if response and response.text:
            return response.text
        else:
            return "I processed the function call but couldn't generate a text response."
    
    except Exception as e:
        print(f"❌ Error in function calling: {e}")
        return None


# ============================================================================
# MAIN CHAT LOOP
# ============================================================================

def run_function_calling_demo():
    """Main demo with function calling"""
    
    # Create model with function declarations
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=[{"function_declarations": function_declarations}]
    )
    
    chat = model.start_chat(history=[])
    
    print("=" * 70)
    print("🛠️  FUNCTION CALLING DEMO")
    print("=" * 70)
    print("AI can use these functions:")
    print("  📍 get_weather - Get weather for any city")
    print("  🧮 calculate - Perform math calculations")
    print("  🕐 get_current_time - Get time in different timezones")
    print("\nTry these:")
    print("  • What's the weather in Mumbai?")
    print("  • Calculate 25 * 4 + 10")
    print("  • What time is it in Tokyo?")
    print("  • Compare weather in Delhi and London")
    print("=" * 70)
    print()
    
    while True:
        # Get user input
        try:
            user_input = input("\n👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        
        if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
            print("\n👋 Goodbye!\n")
            break
        
        if not user_input:
            continue
        
        # Handle the request with function calling
        response_text = handle_function_calling(chat, user_input)
        
        # Display response
        if response_text:
            print(f"\n🤖 AI: {response_text}\n")
        else:
            print("\n⚠️ Could not generate a response. Please try again.\n")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Entry point"""
    try:
        setup_gemini()
        run_function_calling_demo()
    
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("💡 Set your API key: export GEMINI_API_KEY='your-key-here'\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}\n")


if __name__ == "__main__":
    main()