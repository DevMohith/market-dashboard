# vector_store.py with memory
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from llm import get_embedding, ask_gemini

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTIONS = ["stock-insights", "news-insights"]

client = QdrantClient(url=QDRANT_URL)

chat_history = [] 

def search_qdrant(query: str, top_k: int = 5):
    query_vector = get_embedding(query)
    all_results = []

    for collection in COLLECTIONS:
        try:
            hits = client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=top_k
            )
            for hit in hits:
                all_results.append({
                    "collection": collection,
                    "score": hit.score,
                    "text": hit.payload.get("text"),
                    "source": hit.payload.get("symbol") or hit.payload.get("source")
                })
        except Exception as e:
            print(f"Error querying {collection}: {e}")

    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[:top_k]

def query_and_respond(user_query: str, top_k: int = 5) -> str:
    results = search_qdrant(user_query, top_k=top_k)
    context_chunks = "\n".join([r['text'] for r in results])

    # Building memory-augmented prompt
    memory_text = "\n".join(chat_history)
    prompt = f"""
Use the following memory and context to answer the question.

Memory:
{memory_text}

Context:
{context_chunks}

Question: {user_query}
""".strip()

    response = ask_gemini(prompt)
    chat_history.append(f"Q: {user_query}\nA: {response}")
    return response

if __name__ == "__main__":
    print(" Starting memory-enabled chatbot...\n")
    while True:
        question = input(" You: ")
        if question.lower() in {"exit", "quit"}:
            print(" Goodbye!")
            break
        answer = query_and_respond(question)
        print(f" Gemini: {answer}\n")
