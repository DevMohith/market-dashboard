import os
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# Load env vars
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Embedding model (MiniLM)
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Gemini 1.5 Flash LLM call
def ask_gemini(prompt: str) -> str:
    print("[LLM] Calling Gemini 1.5 Flash...")
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def get_embedding(text: str) -> list:
    print(f"[Embedding] Generating real embedding for: {text[:50]}...")
    return embedding_model.encode(text).tolist()
