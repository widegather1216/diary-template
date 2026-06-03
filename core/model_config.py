import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file or server environment variables.")
    
    # Use REST transport to prevent gRPC infinite hanging issues on Mac
    genai.configure(api_key=api_key, transport="rest")
    
    # Using Gemini 3.1 Flash Lite as requested for cost efficiency
    # Set max_output_tokens to 8192 to prevent complex HTML from being cut off
    model = genai.GenerativeModel(
        'gemini-3.1-flash-lite',
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=8192,
        )
    )
    return model
