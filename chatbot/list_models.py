import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available models that support generateContent:")
print("-" * 50)
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)