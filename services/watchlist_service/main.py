from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS settings
origins = [
    "http://localhost:5173",  # Your React frontend's development URL
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://localhost:8002",
    "http://127.0.0.1:8002",
    "http://localhost:8003", # This service's own URL
    "http://127.0.0.1:8003"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables for MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/market_dashboard")
MONGO_DB_NAME = MONGO_URI.split('/')[-1].split('?')[0] # Extract db name from URI

# Pydantic model for watchlist data
class Watchlist(BaseModel):
    user_id: str
    stocks: List[str] # List of stock symbols

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    # MongoDB setup
    try:
        app.state.mongo_client = AsyncIOMotorClient(MONGO_URI)
        app.state.mongo_db = app.state.mongo_client[MONGO_DB_NAME]
        # Ping the MongoDB server to ensure connection
        await app.state.mongo_db.command('ping')
        print(f"✅ Watchlist Service: Connected to MongoDB database '{MONGO_DB_NAME}'")
    except Exception as e:
        print(f"❌ Watchlist Service: Failed to connect to MongoDB: {e}")
        # Fatal error if cannot connect to MongoDB

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Watchlist Service: Shutting down...")
    if hasattr(app.state, 'mongo_client'):
        app.state.mongo_client.close()
        print("✅ Watchlist Service: MongoDB connection closed")
    print("🛑 Watchlist Service: Shutdown complete.")

# --- API Endpoints ---

@app.get("/watchlist/{user_id}", response_model=Watchlist)
async def get_watchlist(user_id: str):
    """
    Retrieve a user's watchlist.
    If no watchlist exists, return an empty watchlist.
    """
    watchlist_doc = await app.state.mongo_db.watchlists.find_one({"user_id": user_id})
    if watchlist_doc:
        # MongoDB _id is ObjectId, needs to be excluded or converted if returned
        watchlist_doc.pop('_id', None)
        return Watchlist(**watchlist_doc)
    return Watchlist(user_id=user_id, stocks=[]) # Return empty watchlist if not found

@app.post("/watchlist", response_model=Watchlist)
async def update_watchlist(watchlist: Watchlist):
    """
    Create or update a user's watchlist.
    """
    update_result = await app.state.mongo_db.watchlists.update_one(
        {"user_id": watchlist.user_id},
        {"$set": {"stocks": watchlist.stocks}},
        upsert=True # Creates the document if it doesn't exist
    )
    if update_result.upserted_id:
        print(f"➕ Created new watchlist for user: {watchlist.user_id}")
    else:
        print(f"🔄 Updated watchlist for user: {watchlist.user_id}")
    
    # Return the updated watchlist (fetch it back to ensure consistency)
    updated_watchlist_doc = await app.state.mongo_db.watchlists.find_one({"user_id": watchlist.user_id})
    if updated_watchlist_doc:
        updated_watchlist_doc.pop('_id', None)
        return Watchlist(**updated_watchlist_doc)
    raise HTTPException(status_code=500, detail="Failed to retrieve updated watchlist")

