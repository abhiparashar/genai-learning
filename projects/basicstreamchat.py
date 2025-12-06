import google.generativeai as genai
import os
import sys

# Force unbuffered output (streaming-friendly)
sys.stdout.reconfigure(line_buffering=True)

def initiate_app():
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found")
    genai.configure(api_key="API_KEY")

def create_chat_session(system_prompt):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_prompt,
        generation_config=genai.types.GenerationConfig(temperature=0)
    )
    return model.start_chat(history=[])

def display_chat_session(chat):
    for message in chat.history:
        role = "You" if message.role == "user" else "AI"
        print(f"{role}: {message.parts[0].text}")

def run_app():
    try:
        initiate_app()
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)

    system_prompt = """
You are a doctor.
Explain medical topics step-by-step in many small chunks.
Always write at least 20 short steps so responses stream clearly.
If the question is not medical, politely decline.
"""

    try:
        chat = create_chat_session(system_prompt)

        while True:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                display_chat_session(chat)
                break

            # STREAMING
            try:
                response = chat.send_message(user_input, stream=True)

                for chunk in response:
                    print(chunk.text, end="", flush=True)

                print()

            except Exception as e:
                print(f"Streaming error: {e}")
                response = chat.send_message(user_input)
                print(response.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_app()
