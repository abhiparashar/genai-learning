import google.generativeai as genai
import os

def setup_gemini():
    # api_key = os.getenv("API_KEY")
    # if not api_key:
    #     raise ValueError("API_KEY is not set")
    genai.configure(api_key="AIzaSyAfLy8-gaPe8VhcDIFw71CX1miZLmXudzg")  

def create_chat_session(system_prompt):
    model = genai.GenerativeModel(model_name="gemini-2.5-flash",system_instruction=system_prompt)
    return model.start_chat(history=[])

def display_chat_session(chat):
    for message in chat.history:
        role = "You" if message.role =='user' else "AI"
        print(f"{role}: {message.parts[0].text}")


def run_chat_application():
   system_prompt = """
You are a Python assistant. You task is to help beginners to learn python.
Give clear explnation but concise. Response should max 1-2 lines.
"""
   try:
       setup_gemini()
       chat = create_chat_session(system_prompt)
       while True:
           user_input = input("You: ").strip()
           if user_input.lower()=="quit":
               display_chat_session(chat)
               break
           if not user_input:
               continue
           try:
               response = chat.send_message(user_input)
               print(f"AI: {response.text}\n")
           except Exception as e:
               print(f"Error is: str{e}\n")
               
               
   except ValueError as e:
       print(f"onfiguration Error: str{e}\n")

   except Exception as e:
       print(f"Exception is: str{e}\n")    
      

if __name__ == "__main__":
    run_chat_application()