import google.generativeai as genai
import json
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

prompt="""
Extract information from this text and return ONLY valid JSON:
Text: "John Smith works at Google as a Software Engineer. 
His email is john.smith@google.com and phone is 555-1234."

Required JSON format:
{
  "name": "...",
  "company": "...",
  "role": "...",
  "email": "...",
  "phone": "..."
}

Return ONLY the JSON, no other text.
"""

response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0))

# Parse JSON
try:
    # Remove markdown code blocks if present
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    
    data = json.loads(text.strip())
    print("Extracted data:")
    print(json.dumps(data, indent=2))
except json.JSONDecodeError:
    print("Failed to parse JSON")
    print("Raw response:", response.text)