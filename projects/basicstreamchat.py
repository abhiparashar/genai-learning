import google.generativeai as genai
import os

def initiate_app():
    api_key = os.getenv("API_KEY")
    if not api_key:
        return ValueError("API_KEY Not found")

def run_app():
    initiate_app()

if __name__=="__main__":
    run_app()