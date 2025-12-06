import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# sets behavior
system_prompt = """
You are a helpful Java programming assistant.
- Answer only Java-related questions
- Provide code examples when helpful
- Be concise but clear
- If question is not about Java, politely decline
"""

model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_prompt)

chat = model.start_chat(history=[])

print("=== Java Assistant Chatbot ===\n")

while True:
    user_input = input("You:")

    if user_input.lower=='quit':
        break

    response = chat.send_message(user_input)
    print(f"Bot: {response.text}\n")
