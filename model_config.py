import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file or server environment variables.")
    
    genai.configure(api_key=api_key)
    # Using Gemini 3.1 Flash Lite as requested for cost efficiency
    model = genai.GenerativeModel('gemini-3.1-flash-lite')
    return model
