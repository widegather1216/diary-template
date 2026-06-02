import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print("API Key loaded:", api_key is not None)
genai.configure(api_key=api_key)

try:
    print("Testing gemini-2.5-flash...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    resp = model.generate_content("hello")
    print("Response:", resp.text)
except Exception as e:
    print("Error with gemini-2.5-flash:", e)

try:
    print("Testing gemini-3.1-flash-lite...")
    model = genai.GenerativeModel('gemini-3.1-flash-lite')
    resp = model.generate_content("hello")
    print("Response:", resp.text)
except Exception as e:
    print("Error with gemini-3.1-flash-lite:", e)
