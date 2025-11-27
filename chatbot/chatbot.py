# Import os module to access environment variables
import os
# Import load_dotenv to read .env file
from dotenv import load_dotenv
# Import Google's Generative AI library
import google.generativeai as genai
# Import json to save conversations in JSON format
import json
# Import datetime to add timestamps
from datetime import datetime

# Load environment variables from .env file into memory
load_dotenv()

# Configure the Gemini API with your API key from .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Create a model instance (gemini-2.5-flash is the AI model we're using)
model = genai.GenerativeModel("gemini-2.5-flash")

# Create an empty list to store all chat messages
conversation_history = []

def save_conversation():
    """Save conversation to JSON file"""
    # Create filename with current date and time (e.g., chat_20241128_143052.json)
    filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    # Open file in write mode
    with open(filename, 'w') as f:
        # Write conversation history to file in pretty JSON format
        json.dump(conversation_history, f, indent=2)
    # Print confirmation message
    print(f"\n✅ Conversation saved to {filename}")

def chat():
    """Main chatbot function"""
    # Print welcome message
    print("🤖 CLI Chatbot Started!")
    # Print available commands
    print("Commands: 'exit' to quit, 'save' to save conversation\n")
    
    # Infinite loop - keeps chatbot running
    while True:
        # Get user input and remove extra spaces
        user_input = input("You: ").strip()
        
        # Check if user wants to exit
        if user_input.lower() == 'exit':
            # Save conversation before closing
            save_conversation()
            # Print goodbye message
            print("👋 Goodbye!")
            # Break the loop and end program
            break
        
        # Check if user wants to save conversation
        if user_input.lower() == 'save':
            # Call save function
            save_conversation()
            # Skip rest of loop, go back to input
            continue
        
        # If user pressed enter without typing, skip this iteration
        if not user_input:
            continue
        
        # Add user's message to history with timestamp
        conversation_history.append({
            "role": "user",  # Mark this message as from user
            "content": user_input,  # The actual message
            "timestamp": datetime.now().isoformat()  # Current time in ISO format
        })
        
        # Try to get AI response (wrapped in try-catch for error handling)
        try:
            # Send user message to Gemini AI
            response = model.generate_content(user_input)
            # Extract the text from AI response
            bot_response = response.text
            
            # Add AI's response to history with timestamp
            conversation_history.append({
                "role": "bot",  # Mark this message as from bot
                "content": bot_response,  # AI's response
                "timestamp": datetime.now().isoformat()  # Current time
            })
            
            # Print AI's response to screen
            print(f"Bot: {bot_response}\n")
            
        # If any error occurs (network issue, API error, etc.)
        except Exception as e:
            # Print error message
            print(f"❌ Error: {e}\n")

# Check if this file is being run directly (not imported)
if __name__ == "__main__":
    # Start the chatbot
    chat()