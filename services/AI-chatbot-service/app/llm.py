import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# this model is used for generating text responses
def ask_gemini(prompt: str) -> str:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# this model is used for generating embeddings for text
def get_embedding(text: str) -> list:
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="RETRIEVAL_DOCUMENT"
    )
    return response["embedding"]