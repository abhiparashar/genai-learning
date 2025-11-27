# Import os module to access environment variables
import os
# Import load_dotenv to read .env file
from dotenv import load_dotenv
# Import Google's Generative AI library
import google.generativeai as genai
# Import json to save conversations in JSON format
import json
# Import csv to save conversations in CSV format
import csv
# Import datetime to add timestamps
from datetime import datetime
# Import glob to find files
import glob
# Import time for typing indicator
import time
# Import threading for async typing indicator
import threading

# Load environment variables from .env file into memory
load_dotenv()

# Configure the Gemini API with your API key from .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Create a model instance (gemini-2.5-flash is the AI model we're using)
model = genai.GenerativeModel("gemini-2.5-flash")

# Create an empty list to store all chat messages
conversation_history = []
# Flag to control typing indicator
is_typing = False

def typing_indicator():
    """Show typing indicator while bot is thinking"""
    # List of animation frames
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    # Index for current animation frame
    idx = 0
    # Loop while bot is typing
    while is_typing:
        # Print current frame with carriage return (overwrites same line)
        print(f"\rBot is thinking {animation[idx % len(animation)]}", end="", flush=True)
        # Move to next frame
        idx += 1
        # Wait 0.1 seconds
        time.sleep(0.1)
    # Clear the typing indicator line
    print("\r" + " " * 50 + "\r", end="", flush=True)

def save_conversation(format_type='json'):
    """Save conversation to file in specified format (json/txt/csv)"""
    # Create base filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save based on format type
    if format_type == 'json':
        # JSON format - structured data
        filename = f"chat_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(conversation_history, f, indent=2)
    
    elif format_type == 'txt':
        # TXT format - human readable
        filename = f"chat_{timestamp}.txt"
        with open(filename, 'w') as f:
            # Write header
            f.write(f"Chat Conversation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            # Write each message
            for msg in conversation_history:
                role = "You" if msg['role'] == 'user' else "Bot"
                f.write(f"[{msg['timestamp']}] {role}: {msg['content']}\n\n")
    
    elif format_type == 'csv':
        # CSV format - for data analysis
        filename = f"chat_{timestamp}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            # Define CSV columns
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'role', 'content'])
            # Write header row
            writer.writeheader()
            # Write all messages
            writer.writerows(conversation_history)
    
    # Print success message
    print(f"✅ Conversation saved to {filename}")

def load_conversation():
    """Load a previous conversation from JSON file"""
    # Find all chat JSON files in current directory
    files = glob.glob("chat_*.json")
    
    # If no files found
    if not files:
        print("❌ No saved conversations found!")
        return
    
    # Show available files
    print("\n📂 Available conversations:")
    for i, file in enumerate(files, 1):
        # Get file modification time
        mod_time = datetime.fromtimestamp(os.path.getmtime(file))
        print(f"{i}. {file} (Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
    
    # Ask user to choose
    try:
        choice = int(input("\nEnter file number to load (0 to cancel): "))
        # If user cancelled
        if choice == 0:
            return
        # Load selected file
        if 1 <= choice <= len(files):
            with open(files[choice-1], 'r') as f:
                # Load conversation into global variable
                global conversation_history
                conversation_history = json.load(f)
            print(f"✅ Loaded {len(conversation_history)} messages from {files[choice-1]}")
            # Show loaded conversation
            print("\n--- Conversation History ---")
            for msg in conversation_history:
                role = "You" if msg['role'] == 'user' else "Bot"
                print(f"{role}: {msg['content'][:50]}...")  # Show first 50 chars
            print("--- End of History ---\n")
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Invalid input!")

def clear_history():
    """Clear conversation history"""
    # Access global variable
    global conversation_history
    # Ask for confirmation
    confirm = input("⚠️  Clear all conversation history? (yes/no): ").lower()
    if confirm == 'yes':
        # Clear the list
        conversation_history = []
        print("✅ Conversation history cleared!")
    else:
        print("❌ Clear cancelled")

def show_help():
    """Show available commands"""
    print("\n" + "="*60)
    print("📚 AVAILABLE COMMANDS:")
    print("="*60)
    print("  exit          - Quit chatbot (auto-saves)")
    print("  save [format] - Save conversation (json/txt/csv)")
    print("                  Example: 'save txt' or just 'save'")
    print("  load          - Load previous conversation")
    print("  clear         - Clear conversation history")
    print("  help          - Show this help message")
    print("="*60 + "\n")

def get_ai_response_with_context(user_input):
    """Get AI response with conversation context"""
    # Build context from last 10 messages (to avoid token limits)
    context_messages = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    
    # Create context string
    context = ""
    for msg in context_messages:
        role = "User" if msg['role'] == 'user' else "Assistant"
        context += f"{role}: {msg['content']}\n"
    
    # Add current message
    full_prompt = f"Previous conversation:\n{context}\nUser: {user_input}\nAssistant:"
    
    # Get response from AI
    response = model.generate_content(full_prompt)
    return response.text

def chat():
    """Main chatbot function with all features"""
    # Print banner
    print("\n" + "="*60)
    print("🤖 CLI CHATBOT v2.0")
    print("="*60)
    print("Type 'help' for available commands\n")
    
    # Infinite loop - keeps chatbot running
    while True:
        # Get user input and remove extra spaces
        user_input = input("You: ").strip()
        
        # If user pressed enter without typing, skip
        if not user_input:
            continue
        
        # Convert to lowercase for command checking
        command = user_input.lower().split()
        
        # Handle 'exit' command
        if command[0] == 'exit':
            # Save before exit
            print("\n💾 Saving conversation before exit...")
            save_conversation('json')
            print("👋 Goodbye!")
            break
        
        # Handle 'save' command with optional format
        elif command[0] == 'save':
            # Get format (default to json)
            format_type = command[1] if len(command) > 1 and command[1] in ['json', 'txt', 'csv'] else 'json'
            save_conversation(format_type)
            continue
        
        # Handle 'load' command
        elif command[0] == 'load':
            load_conversation()
            continue
        
        # Handle 'clear' command
        elif command[0] == 'clear':
            clear_history()
            continue
        
        # Handle 'help' command
        elif command[0] == 'help':
            show_help()
            continue
        
        # Add user's message to history
        conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get AI response with error handling
        try:
            # Start typing indicator in separate thread
            global is_typing
            is_typing = True
            typing_thread = threading.Thread(target=typing_indicator)
            typing_thread.start()
            
            # Get AI response with conversation context
            bot_response = get_ai_response_with_context(user_input)
            
            # Stop typing indicator
            is_typing = False
            typing_thread.join()
            
            # Add bot response to history
            conversation_history.append({
                "role": "bot",
                "content": bot_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Print bot response
            print(f"Bot: {bot_response}\n")
            
        except Exception as e:
            # Stop typing indicator if error occurs
            is_typing = False
            print(f"❌ Error: {e}\n")

# Check if this file is being run directly (not imported)
if __name__ == "__main__":
    # Start the chatbot
    chat()