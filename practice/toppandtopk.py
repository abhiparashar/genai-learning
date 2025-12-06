import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

prompt = "Complete the sentence: The robot walked into the bar and"
print("Default Settings")
response = model.generate_content(prompt)
print(response.text)
print()

print("top_p = 0.5 (More Focused)")
response = model.generate_content(prompt,generation_config=genai.types.GenerationConfig(top_p=0.5, temperature=1))
print(response.text)
print()

print("top_p = 0.95 (More Diverse)")
response = model.generate_content(prompt,generation_config=genai.types.GenerationConfig(top_p=0.95, temperature=1))
print(response.text)
print()

print("top_k = 10 (Only top 10 words)")
response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(top_k=10))
print(response.text)
