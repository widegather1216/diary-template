import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file or server environment variables.")
    
    genai.configure(api_key=api_key)
    # Using the latest Gemini model for fast and high-quality generation
    model = genai.GenerativeModel('gemini-2.0-flash')
    return model
