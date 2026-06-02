import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print("API Key loaded:", api_key is not None)
genai.configure(api_key=api_key, transport="rest")

try:
    print("Testing gemini-2.5-flash with REST transport...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    resp = model.generate_content("hello")
    print("Response:", resp.text)
except Exception as e:
    print("Error:", e)
