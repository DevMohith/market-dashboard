from fastapi import FastAPI, Request
from pydantic import BaseModel
from llm import get_embedding, ask_gemini
from vector_store import query_and_respond
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI()

QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTIONS = ["stock-insights", "news-insights"]
qdrant = QdrantClient(url=QDRANT_URL)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    query = request.question
    top_k = request.top_k
    query_vector = get_embedding(query)

    all_results = []
    for collection in COLLECTIONS:
        try:
            hits = qdrant.search(
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
    top_chunks = all_results[:top_k]
    if not top_chunks:
        return {"answer": "Sorry, I couldn't find relevant information."}

    context = "\n".join([r['text'] for r in top_chunks])
    prompt = f"Answer the following question using the context below:\n\n{context}\n\nQuestion: {query}"
    response = ask_gemini(prompt)

    return {"answer": response}
