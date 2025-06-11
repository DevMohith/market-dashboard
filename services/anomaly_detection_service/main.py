from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import List, Dict, Set
import time
from collections import deque
from redis.asyncio import Redis
import redis.exceptions
import httpx

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
    "http://127.0.0.1:8002",
    "http://localhost:8003",
    "http://127.0.0.1:8003"
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
REDIS_GROUP = os.getenv("REDIS_GROUP", "anomaly_group")
REDIS_CONSUMER = os.getenv("REDIS_CONSUMER", "consumer_1")

WATCHLIST_SERVICE_URL = os.getenv("VITE_APP_WATCHLIST_API_URL", "http://localhost:8003")
WATCHLIST_FETCH_INTERVAL = 10 # seconds, how often to refresh watchlist

recent_data: Dict[str, deque] = {}

# Tuned values for anomaly detection (from previous step)
WINDOW_SIZE = 5
PRICE_CHANGE_THRESHOLD = 0.0001
VOLUME_CHANGE_THRESHOLD_PERCENT = 0.01

connected_alerts_websockets: List[WebSocket] = []

user_watchlists: Dict[str, Set[str]] = {}
watchlist_refresher_tasks: Dict[str, asyncio.Task] = {}


# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    app.state.redis = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
    
    print(f"DEBUG: Type of app.state.redis: {type(app.state.redis)}")

    try:
        await app.state.redis.ping()
        print("✅ Anomaly Detection Service: Connected to Redis")
    except Exception as e:
        print(f"❌ Anomaly Detection Service: Failed to connect to Redis: {e}")

    try:
        await app.state.redis.xgroup_create(REDIS_STREAM, REDIS_GROUP, id='$', mkstream=True)
        print(f"Created Redis consumer group '{REDIS_GROUP}' for stream '{REDIS_STREAM}'")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print(f"Redis consumer group '{REDIS_GROUP}' already exists.")
        else:
            print(f" Error creating Redis consumer group: {e}")

    app.state.stream_reader_task = asyncio.create_task(read_from_redis_stream())
    print("Redis stream reader task started.")


@app.on_event("shutdown")
async def shutdown_event():
    print(" Anomaly Detection Service: Shutting down...")
    app.state.stream_reader_task.cancel()
    try:
        await app.state.stream_reader_task
    except asyncio.CancelledError:
        pass
    print("Redis stream reader task cancelled.")

    for user_id, task in watchlist_refresher_tasks.items():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        print(f"Watchlist refresher task for user {user_id[:8]}... cancelled.")
    watchlist_refresher_tasks.clear()

    await app.state.redis.close()
    print(" Anomaly Detection Service: Redis connection closed")
    print(" Anomaly Detection Service: Shutdown complete.")

# --- Watchlist Refresh Logic ---
async def fetch_watchlist_from_service(user_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{WATCHLIST_SERVICE_URL}/watchlist/{user_id}")
            response.raise_for_status()
            watchlist_data = response.json()
            if "stocks" in watchlist_data and isinstance(watchlist_data["stocks"], list):
                user_watchlists[user_id] = set(stock.upper() for stock in watchlist_data["stocks"])
                print(f"🔄 Watchlist refreshed for user {user_id[:8]}...: {user_watchlists[user_id]}")
            else:
                print(f"❌ Watchlist service returned unexpected data for user {user_id[:8]}...: {watchlist_data}")
    except httpx.RequestError as e:
        print(f"❌ Error fetching watchlist for user {user_id[:8]}... from service: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during watchlist fetch for user {user_id[:8]}...: {e}")

async def refresh_watchlist_periodically(user_id: str):
    while True:
        await fetch_watchlist_from_service(user_id)
        await asyncio.sleep(WATCHLIST_FETCH_INTERVAL)

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
            print(f"DEBUG: Processing incoming trade for symbol: {symbol.upper()}")

            is_on_any_watchlist = False
            for user_id, watchlist_set in user_watchlists.items():
                if symbol.upper() in watchlist_set:
                    is_on_any_watchlist = True
                    break

            if is_on_any_watchlist:
                print(f"DEBUG: {symbol.upper()} is on an active watchlist. Proceeding to anomaly detection.")
                if symbol not in recent_data:
                    recent_data[symbol] = deque(maxlen=WINDOW_SIZE)
                recent_data[symbol].append({"timestamp": timestamp, "price": price, "volume": volume})

                if len(recent_data[symbol]) == WINDOW_SIZE:
                    print(f"DEBUG: Calling detect_anomaly for {symbol.upper()}. Window size reached.")
                    await detect_anomaly(symbol, price, volume, timestamp)
                else:
                    print(f"DEBUG: Not yet enough data for {symbol.upper()} to detect anomaly. ({len(recent_data[symbol])}/{WINDOW_SIZE})")
            else:
                print(f"DEBUG: Skipping anomaly detection for {symbol.upper()} (not on any active watchlist).")


    except (ValueError, TypeError) as e:
        print(f"❌ Data parsing error for message {message_id}: {e} - Data: {message_data}")
    except Exception as e:
        print(f"❌ Unexpected error in process_market_data for message {message_id}: {e}")

async def detect_anomaly(symbol: str, current_price: float, current_volume: int, current_timestamp: int):
    history = list(recent_data[symbol])

    if len(history) < 2:
        return

    # Price Anomaly Detection
    reference_price = history[0]['price']
    price_change_abs = abs(current_price - reference_price)
    price_change_percent = price_change_abs / reference_price if reference_price != 0 else 0

    if price_change_percent > PRICE_CHANGE_THRESHOLD:
        alert_message = (
            f"📈📉 ALERT: {symbol} price changed by {price_change_percent:.4%}! "
            f"From ${reference_price:.2f} to ${current_price:.2f} in last {WINDOW_SIZE} trades."
        )
        await send_alert_to_frontend(symbol, "price_anomaly", alert_message)
        print(f"🔔 {alert_message}")

    # Volume Anomaly Detection
    historical_volumes = [d['volume'] for d in history[:-1] if d['volume'] > 0]
    if historical_volumes:
        avg_volume = sum(historical_volumes) / len(historical_volumes)
        if avg_volume > 0:
            volume_change_ratio = current_volume / avg_volume
            if (current_volume > avg_volume * (1 + VOLUME_CHANGE_THRESHOLD_PERCENT)) or \
               (current_volume < avg_volume * (1 - VOLUME_CHANGE_THRESHOLD_PERCENT)):
                alert_message = (
                    f"📊 ALERT: {symbol} volume change detected! Current: {current_volume}, Avg (last {WINDOW_SIZE-1}): {avg_volume:.0f}. Ratio: {volume_change_ratio:.2f}."
                )
                await send_alert_to_frontend(symbol, "volume_anomaly", alert_message)
                print(f"🔔 {alert_message}")

# --- Alerts WebSocket Endpoint ---
@app.websocket("/ws/alerts/{user_id}")
async def websocket_alerts_endpoint(websocket: WebSocket, user_id: str):
    # Debug print immediately on function entry
    print(f"DEBUG: WebSocket endpoint /ws/alerts/{user_id} entered. Attempting to accept connection.")

    await websocket.accept()
    connected_alerts_websockets.append(websocket)

    print(f"🔗 Frontend client {user_id[:8]}... connected to Alerts WS: {websocket.client}")
    
    if user_id not in watchlist_refresher_tasks or watchlist_refresher_tasks[user_id].done():
        watchlist_refresher_tasks[user_id] = asyncio.create_task(refresh_watchlist_periodically(user_id))
        print(f"Started watchlist refresher for user {user_id[:8]}...")
    
    try:
        while True:
            # WebSocket must receive messages to stay open if client expects it to.
            # A simple `receive_text()` with no explicit send from frontend can cause disconnects.
            # For debugging, we can just await forever, or handle expected pings.
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_alerts_websockets.remove(websocket)
        print(f"👋 Frontend client {user_id[:8]}... disconnected from Alerts WS: {websocket.client}")
    except Exception as e:
        print(f"❌ Alerts WebSocket error for user {user_id[:8]}...: {e}")

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
@app.get("/trigger_test_alert/{symbol}/{user_id}")
async def trigger_test_alert(symbol: str, user_id: str):
    if user_id not in user_watchlists:
        await fetch_watchlist_from_service(user_id)

    if symbol.upper() in user_watchlists.get(user_id, set()):
        alert_message = f"TEST ALERT: This is a test anomaly for {symbol} (on watchlist of {user_id[:8]}...)."
        await send_alert_to_frontend(symbol, "test_anomaly", alert_message)
        return {"message": alert_message, "status": "triggered"}
    else:
        return {"message": f"Test alert not triggered for {symbol} (not on watchlist of {user_id[:8]}...).", "status": "skipped"}
