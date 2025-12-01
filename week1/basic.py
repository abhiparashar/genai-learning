import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 2.5 Flash
model = genai.GenerativeModel("gemini-2.5-flash")

# Send prompt
response = model.generate_content(
    "Explain quantum computing in simple terms, like I'm 10 years old",
    generation_config={
        "temperature": 0.7
        # ✅ DO NOT set max_output_tokens for gemini-2.5 here
    }
)

# Print safely
if response.candidates and response.candidates[0].content.parts:
    text = "".join(
        part.text for part in response.candidates[0].content.parts
        if hasattr(part, "text")
    )
    print("\n✅ AI RESPONSE:\n")
    print(text)
else:
    print("\n❌ No text returned. Finish reason:",
          response.candidates[0].finish_reason)
