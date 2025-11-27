import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use one of the available models
model = genai.GenerativeModel("gemini-2.5-flash")  # Latest fast model

response = model.generate_content("Say hello in 3 words")
print(response.text)