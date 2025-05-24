# the Pipeline for our project from ingecting stock data to storing in Qdrant
import os
import httpx
from dotenv import load_dotenv
from llm import get_embedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY = os.getenv("TWELVE_DATA_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = "stock-insights"

qdrant = QdrantClient(url=QDRANT_URL)

# Processed file to keep track of already processed symbols, so we don't reprocess them next day
PROCESSED_FILE = "processed_symbols.txt"

def get_stock_data(symbol: str):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=10&apikey={API_KEY}"
    response = httpx.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch stock data")
    return response.json()

def format_stock_data(json_data: dict) -> str:
    if "values" not in json_data:
        return "No data available."
    values = json_data["values"]
    lines = [f"Stock Time Series for {json_data['meta']['symbol']}"]
    for item in values:
        lines.append(f"{item['datetime']}: Open={item['open']}, Close={item['close']}, High={item['high']}, Low={item['low']}, Volume={item['volume']}")
    return "\n".join(lines)

def chunk_text(text: str, chunk_size: int = 500) -> list:
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def embed_chunks(chunks: list) -> list:
    return [get_embedding(chunk) for chunk in chunks]

def upload_to_qdrant(chunks: list, embeddings: list, symbol: str):
    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    #combining chunks and embeddings into points and processing it to Qdrant to store
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=embed, payload={"text": chunk, "symbol": symbol})
        for chunk, embed in zip(chunks, embeddings)
    ]

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

# fun to get new symbols from Twelve Data API
def get_new_symbols(limit=5):
    url = f"https://api.twelvedata.com/stocks?exchange=NASDAQ&apikey={API_KEY}"
    response = httpx.get(url)
    data = response.json().get("data", [])
    all_symbols = [entry["symbol"] for entry in data if "symbol" in entry]
    return all_symbols[:limit]

# main function to process the symbols and store them in Qdrant
def load_processed_symbols():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r") as file:
        return set(line.strip() for line in file.readlines())
    
# fun to save processed symbols to a file
def save_processed_symbol(symbol: str):
    with open(PROCESSED_FILE, "a") as file:
        file.write(symbol + "\n")

# creating list of companies to loop through all company symbols to get  data from twelvedata and process them to Qdrant as metadata
if __name__ == "__main__":
    processed_symbols = load_processed_symbols()
    new_symbols = get_new_symbols(limit=5)

    for symbol in new_symbols:
        if symbol in processed_symbols:
            print(f"___ Skipping already processed symbol: {symbol}")
            continue

        try:
            data = get_stock_data(symbol)
            readable_text = format_stock_data(data)
            chunks = chunk_text(readable_text)
            embeddings = embed_chunks(chunks)
            upload_to_qdrant(chunks, embeddings, symbol)
            save_processed_symbol(symbol)
            print(f"** Ingested and embedded {len(chunks)} chunks for {symbol}")
        except Exception as e:
            print(f"x Failed to ingest {symbol}: {e}")