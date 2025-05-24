import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def ask_gemini(prompt: str) -> str:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text