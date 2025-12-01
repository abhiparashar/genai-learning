from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0
)

# Define Tool 1: Calculator
@tool
def calculator(expression: str) -> str:
    """Evaluates a math expression like '5 * 10 + 2'"""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except:
        return "Error: Invalid expression"

# Define Tool 2: Text Analyzer
@tool
def text_analyzer(text: str) -> str:
    """Counts words and characters in text"""
    words = len(text.split())
    chars = len(text)
    return f"Words: {words}, Characters: {chars}"

# Bind tools to LLM
tools = [calculator, text_analyzer]
llm_with_tools = llm.bind_tools(tools)

# Test
print("--- Agent with Tools ---\n")
response = llm_with_tools.invoke("What is 25 * 4 + 10?")
print(response)

# Extract tool call
tool_call = response.tool_calls[0]
print(f"AI wants to use: {tool_call['name']}")
print(f"With input: {tool_call['args']}")

# Execute the tool
if tool_call['name'] == 'calculator':
    result = calculator.invoke(tool_call['args'])
    print(f"\nTool result: {result}")

# Test text analyzer
print("\n--- Testing Text Analyzer ---")
response2 = llm_with_tools.invoke("How many words are in this text: Hello world from LangChain")
tool_call2 = response2.tool_calls[0]
result2 = text_analyzer.invoke(tool_call2['args'])
print(f"Result: {result2}")