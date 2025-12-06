import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

prompt = "Write a creative tagline for a coffee shop"

print("=== Temperature = 0 (Deterministic) ===")

response = model.generate_content(prompt,generation_config=genai.types.GenerationConfig(temperature=0,))

print(response.text)
print()

print("=== Temperature = 1 (Balanced) ===")
response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=1))
print(response.text)
print()

print("=== Temperature = 2 (Very Creative) ===")
response = model.generate_content(prompt,generation_config=genai.types.GenerationConfig(temperature=2))
print(response.text)
print()

