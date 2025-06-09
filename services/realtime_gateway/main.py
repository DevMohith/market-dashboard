from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
import redis.asyncio as redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()

# CORS settings
# IMPORTANT: Adjust allow_origins to your frontend URL in production
origins = [
    "http://localhost:5173",  # Your React frontend's development URL
    # Add other frontend URLs if deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_STREAM = os.getenv("REDIS_STREAM", "market:stream")

# Set up Redis connection on startup
@app.on_event("startup")
async def startup():
    app.state.redis = await redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True
    )
    await app.state.redis.ping()
    print("✅ Real-time Gateway: Connected to Redis")

# Graceful shutdown: close redis
@app.on_event("shutdown")
async def shutdown():
    print("🛑 Real-time Gateway: Shutting down...")
    await app.state.redis.close()
    print("✅ Real-time Gateway: Redis connection closed")

# WebSocket endpoint to stream market data to frontend
@app.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"🔗 Frontend client connected: {websocket.client}")

    # Use a unique consumer group for each WebSocket client or manage persistent group
    # For simplicity, we'll read from the stream from the last delivered ID
    # For robust production, consider consumer groups for load balancing and message acknowledgment
    last_id = '$' # Read from the latest entry

    try:
        while True:
            # XREAD block for a short duration to prevent busy-waiting
            # Timeout (milliseconds): 1000 means wait up to 1 second for new data
            stream_data = await app.state.redis.xread(
                {REDIS_STREAM: last_id},
                count=1, # Read one message at a time
                block=1000 # Block for up to 1000ms if no new data
            )

            if stream_data:
                for stream_name, messages in stream_data:
                    for message_id, message_data in messages:
                        # Decode message_data if necessary (Redis might store bytes)
                        # Your friend's code is putting dicts, which redis-py handles well.
                        try:
                            # message_data values are strings, convert price to float if possible
                            parsed_data = {k: v for k, v in message_data.items()}
                            if 'price' in parsed_data:
                                parsed_data['price'] = float(parsed_data['price'])
                            
                            await websocket.send_json(parsed_data)
                            print(f"➡️ Sent to frontend: {parsed_data}")
                            last_id = message_id # Update last_id to read next messages

                        except json.JSONDecodeError as e:
                            print(f"❌ Error decoding message from Redis: {message_data}, Error: {e}")
                            # Still update last_id to move past the problematic message
                            last_id = message_id 
                        except Exception as e:
                            print(f"❌ Error processing message for frontend: {message_data}, Error: {e}")
                            last_id = message_id # Update last_id

            # Keep the loop running, even if no new data arrived
            await asyncio.sleep(0.01) # Small sleep to yield control

    except WebSocketDisconnect:
        print(f"👋 Frontend client disconnected: {websocket.client}")
    except Exception as e:
        print(f"❌ Real-time Gateway WebSocket error: {e}")

