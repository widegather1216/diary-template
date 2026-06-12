import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file or server environment variables.")
    
    # Initialize the modern google-genai Client
    # Client will use httpx REST transport under the hood, avoiding gRPC issues on Mac
    client = genai.Client(api_key=api_key)
    return client
