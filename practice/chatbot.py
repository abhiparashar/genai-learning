import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Start a chat session
model = genai.GenerativeModel("gemini-2.5-flash")
chat = model.start_chat(history=[])

while True:
    user_input = input("You: ")

    if user_input.lower == 'quit':
            break
    
    response = chat.send_message(user_input)
    print(f"Bot: {response.text}\n")
