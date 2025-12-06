import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from datetime import datetime

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

conversation_history = []

def save_conversation():
    # Create filename with current date and time (e.g., chat_20241128_143052.json)
    filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    # Open file in write mode
    with open(filename, 'w') as f:
        # Write conversation history to file in pretty JSON format
        json.dump(conversation_history, f, indent=2)
    # Print confirmation message
    print(f"\n Conversation saved to {filename}")

def chat():
    while True:
        # Get user input and remove extra spaces
        user_input = input("You: ").strip()
        
        # Check if user wants to exit
        if user_input.lower() == 'exit':
            save_conversation()
            print("Goodbye!")
            break
        
        if user_input.lower() == 'save':
            save_conversation()
            continue
        
        if not user_input:
            continue
        
        conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            response = model.generate_content(user_input)
            bot_response = response.text
            
            conversation_history.append({
                "role": "bot",
                "content": bot_response,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"Bot: {bot_response}\n")
            
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    chat()