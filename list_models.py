import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport="rest")

models = genai.list_models()
found = []
for m in models:
    if "generateContent" in m.supported_generation_methods:
        found.append(m.name)
        
print("Available generative models:")
for name in found:
    if 'flash' in name or 'lite' in name or '3' in name:
        print(name)
