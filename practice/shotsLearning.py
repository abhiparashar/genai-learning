import google.generativeai as genai
import os

# Configure
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# ZERO-SHOT (no examples)
print("=== ZERO-SHOT ===")
prompt_zero = """
Classify the urgency: HIGH, MEDIUM, or LOW
Customer message: "The dashboard is a bit slow sometimes"
Urgency:
"""
response = model.generate_content(prompt_zero)
print(response.text)
print()

print("=== FEW-SHOT ===")
prompt_few = """
Classify the urgency: HIGH, MEDIUM, or LOW

Examples:
Message: "Entire website is down! Customers can't access anything"
Urgency: HIGH

Message:"Can I change my email address?"
urgency: LOW

Message:"Checkout page showing errors intermittently"
urgency: "MEDIUM"

Now classify this:
Message: "The dashboard is a bit slow sometimes"
urgency:
"""

response = model.generate_content(prompt_few)
print(response.text)
