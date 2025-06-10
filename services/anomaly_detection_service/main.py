from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import List
import time
from collections import deque

# FIX: Explicitly import Redis from redis.asyncio
from redis.asyncio import Redis # <--- CHANGED THIS IMPORT
import redis.exceptions # For Redis exceptions

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
    "http://localhost:8002", # This service's own URL
    "http://127.0.0.1:8002"
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
REDIS_GROUP = os.getenv("REDIS_GROUP", "anomaly_group") # Consumer group name
REDIS_CONSUMER = os.getenv("REDIS_CONSUMER", "consumer_1") # Consumer name

# In-memory store for recent stock data for anomaly detection
recent_data = {}
WINDOW_SIZE = 20
PRICE_CHANGE_THRESHOLD = 0.03
VOLUME_CHANGE_THRESHOLD_PERCENT = 1.00

# WebSocket connections for sending alerts to frontend
connected_alerts_websockets: List[WebSocket] = []

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    # FIX: Use the imported Redis class directly
    app.state.redis = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True # Ensure responses are decoded to Python strings/ints
    )
    
    # DEBUG: Print the type of the Redis client to confirm it's async
    print(f"DEBUG: Type of app.state.redis: {type(app.state.redis)}")

    try:
        await app.state.redis.ping() # This should now be awaitable
        print("✅ Anomaly Detection Service: Connected to Redis")
    except Exception as e:
        print(f"❌ Anomaly Detection Service: Failed to connect to Redis: {e}")
        # Fatal error if cannot connect to Redis

    # Create consumer group if it doesn't exist
    try:
        await app.state.redis.xgroup_create(REDIS_STREAM, REDIS_GROUP, id='$', mkstream=True)
        print(f"Created Redis consumer group '{REDIS_GROUP}' for stream '{REDIS_STREAM}'")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print(f"Redis consumer group '{REDIS_GROUP}' already exists.")
        else:
            print(f"❌ Error creating Redis consumer group: {e}")

    # Start the stream reader task in the background
    app.state.stream_reader_task = asyncio.create_task(read_from_redis_stream())
    print("Redis stream reader task started.")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Anomaly Detection Service: Shutting down...")
    app.state.stream_reader_task.cancel()
    try:
        await app.state.stream_reader_task
    except asyncio.CancelledError:
        pass
    print("Redis stream reader task cancelled.")
    await app.state.redis.close()
    print("✅ Anomaly Detection Service: Redis connection closed")
    print("🛑 Anomaly Detection Service: Shutdown complete.")

# --- Redis Stream Consumer Logic ---
async def read_from_redis_stream():
    print(f"Listening to Redis stream '{REDIS_STREAM}' with group '{REDIS_GROUP}'...")
    while True:
        try:
            messages = await app.state.redis.xreadgroup(
                REDIS_GROUP,
                REDIS_CONSUMER,
                {REDIS_STREAM: '>'},
                count=1,
                block=1000
            )

            if messages:
                for stream_name, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        await process_market_data(message_id, message_data)
                        await app.state.redis.xack(REDIS_STREAM, REDIS_GROUP, message_id)

            await asyncio.sleep(0.01)
        except Exception as e:
            print(f"❌ Error reading from Redis stream: {e}")
            await asyncio.sleep(1)

async def process_market_data(message_id: str, message_data: dict):
    try:
        event_type = message_data.get("event")
        symbol = message_data.get("symbol")
        price = float(message_data.get("price"))
        timestamp = int(message_data.get("timestamp"))
        volume = int(message_data.get("volume", 0))

        if event_type == "price" and symbol and price is not None:
            if symbol not in recent_data:
                recent_data[symbol] = deque(maxlen=WINDOW_SIZE)
            recent_data[symbol].append({"timestamp": timestamp, "price": price, "volume": volume})

            if len(recent_data[symbol]) == WINDOW_SIZE:
                await detect_anomaly(symbol, price, volume, timestamp)

    except (ValueError, TypeError) as e:
        print(f"❌ Data parsing error for message {message_id}: {e} - Data: {message_data}")
    except Exception as e:
        print(f"❌ Unexpected error in process_market_data for message {message_id}: {e}")

async def detect_anomaly(symbol: str, current_price: float, current_volume: int, current_timestamp: int):
    history = list(recent_data[symbol])

    if len(history) < 2:
        return

    reference_price = history[0]['price']
    price_change_abs = abs(current_price - reference_price)
    price_change_percent = price_change_abs / reference_price if reference_price != 0 else 0

    if price_change_percent > PRICE_CHANGE_THRESHOLD:
        alert_message = (
            f"📈📉 ALERT: {symbol} price changed by {price_change_percent:.2%}! "
            f"From ${reference_price:.2f} to ${current_price:.2f} in last {WINDOW_SIZE} trades."
        )
        await send_alert_to_frontend(symbol, "price_anomaly", alert_message)
        print(f"🔔 {alert_message}")

    historical_volumes = [d['volume'] for d in history[:-1] if d['volume'] > 0]
    if historical_volumes:
        avg_volume = sum(historical_volumes) / len(historical_volumes)
        if avg_volume > 0:
            volume_change_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            if (current_volume > avg_volume * (1 + VOLUME_CHANGE_THRESHOLD_PERCENT)) or \
               (current_volume < avg_volume * (1 - VOLUME_CHANGE_THRESHOLD_PERCENT)):
                alert_message = (
                    f"📊 ALERT: {symbol} volume change detected! Current: {current_volume}, Avg (last {WINDOW_SIZE-1}): {avg_volume:.0f}. Ratio: {volume_change_ratio:.2f}."
                )
                await send_alert_to_frontend(symbol, "volume_anomaly", alert_message)
                print(f"🔔 {alert_message}")

# --- Alerts WebSocket Endpoint ---
@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_alerts_websockets.append(websocket)
    print(f"🔗 Frontend client connected to Alerts WS: {websocket.client}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_alerts_websockets.remove(websocket)
        print(f"👋 Frontend client disconnected from Alerts WS: {websocket.client}")
    except Exception as e:
        print(f"❌ Alerts WebSocket error: {e}")

async def send_alert_to_frontend(symbol: str, alert_type: str, message: str):
    alert_data = {
        "id": str(time.time()),
        "symbol": symbol,
        "type": alert_type,
        "message": message,
        "timestamp": int(time.time() * 1000)
    }
    for connection in connected_alerts_websockets:
        try:
            await connection.send_json(alert_data)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"❌ Failed to send alert to frontend client: {e}")

# --- Test Endpoint for Manual Alert Trigger ---
@app.get("/trigger_test_alert/{symbol}")
async def trigger_test_alert(symbol: str):
    await send_alert_to_frontend(
        symbol,
        "test_anomaly",
        f"TEST ALERT: This is a test anomaly for {symbol}."
    )
    return {"message": f"Test alert triggered for {symbol}"}
