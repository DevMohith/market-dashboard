from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import threading
import asyncio
import redis.asyncio as redis
from dotenv import load_dotenv
from typing import List
from websocket import WebSocketApp
import time # <--- ADDED THIS LINE

# Load environment variables
load_dotenv()

# --- CORRECTED INDENTATION ---
FINNHUB_API_KEY_LOADED = os.getenv("FINNHUB_API_KEY")
print(f"DEBUG: FINNHUB_API_KEY loaded: {FINNHUB_API_KEY_LOADED[:5]}... (Full length: {len(FINNHUB_API_KEY_LOADED) if FINNHUB_API_KEY_LOADED else 'N/A'})")
# --- END CORRECTED INDENTATION ---

# FastAPI app
app = FastAPI()

# CORS settings for this service (important if frontend directly accesses this)
origins = [
    "http://localhost:5173",  # Your React frontend's development URL
    "http://localhost:8000",  # Allow self-origin for testing
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Environment variables
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_STREAM = os.getenv("REDIS_STREAM", "market:stream")

# Global trackers for Finnhub subscriptions and their WebSocketApp instances
active_finnhub_ws = {}
ws_lock = threading.Lock()


# Set up Redis, queue, and event loop on startup
@app.on_event("startup")
async def startup_event(): # Renamed to avoid conflict with `startup` function name
    app.state.redis = await redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True
    )
    app.state.event_loop = asyncio.get_running_loop() # Get the current event loop
    try:
        await app.state.redis.ping()
        print("✅ Market Data Service: Connected to Redis")
    except Exception as e:
        print(f"❌ Market Data Service: Failed to connect to Redis: {e}")
        # Optionally, you might want to exit or raise an error here if Redis is mandatory for startup

    app.state.queue = asyncio.Queue()
    # Ensure this task runs in the main event loop
    app.state.redis_writer_task = app.state.event_loop.create_task(redis_writer())
    print("Writer task created.")

async def redis_writer():
    print("Redis writer task started...")
    while True:
        data = await app.state.queue.get()
        try:
            await app.state.redis.xadd(REDIS_STREAM, data)
        except Exception as e:
            print("❌ Redis write error:", e)
        finally:
            app.state.queue.task_done()

# Graceful shutdown: cancel redis_writer task and close redis, close Finnhub WS connections
@app.on_event("shutdown")
async def shutdown_event(): # Renamed for clarity
    print("🛑 Market Data Service: Shutting down...")

    # Cancel Redis writer task
    app.state.redis_writer_task.cancel()
    try:
        await app.state.redis_writer_task
    except asyncio.CancelledError:
        pass
    print("Redis writer task cancelled.")

    # Close all active Finnhub WebSocket connections
    with ws_lock:
        for ticker, ws_app_instance in active_finnhub_ws.items():
            if ws_app_instance.sock and ws_app_instance.sock.connected:
                print(f"Closing Finnhub WebSocket for {ticker}")
                ws_app_instance.close()
            # The run_forever() thread needs a way to stop its loop gracefully
            # Forcing it with _thread.interrupt_main() or similar is hacky.
            # A better way for run_forever is to set a `daemon=True` initially
            # and let it die with the main process or use `run_forever(dispatcher=...)`
            # or `terminate()` method if it were a custom thread.
            # For now, close() is the best we have with websocket-client.

    await app.state.redis.close()
    print("✅ Market Data Service: Redis connection closed")
    print("🛑 Market Data Service: Shutdown complete.")


# WebSocket message handler for Finnhub
def on_message_finnhub(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "trade":
            for trade in data["data"]:
                redis_data = {
                    "event": "price",
                    "symbol": trade["s"],
                    "price": str(trade["p"]), # Keep as string for Redis
                    "timestamp": str(trade["t"]),
                    "volume": str(trade["v"]), # Include volume
                }
                print(f"🔁 About to enqueue for Redis: {redis_data['symbol']} @ {redis_data['price']}")

                asyncio.run_coroutine_threadsafe(
                    app.state.queue.put(redis_data),
                    app.state.event_loop
                )
        elif data.get("type") == "ping":
            pass # No need to process pings
        else:
            print(f"ℹ️ Received other Finnhub message type: {data.get('type')}, Message: {message}")

    except json.JSONDecodeError as e:
        print(f"❌ Error decoding Finnhub WebSocket message JSON: {message}, Error: {e}")
    except Exception as e:
        print(f"❌ Error handling Finnhub WebSocket message or enqueueing Redis data: {e}")

def on_error_finnhub(ws, error):
    print(f"❌ Finnhub WebSocket ERROR for {ws.url}: {error}")

def on_close_finnhub(ws, close_status_code, close_msg):
    closed_ticker = None
    with ws_lock:
        for ticker, ws_app_instance in active_finnhub_ws.items():
            if ws_app_instance == ws:
                closed_ticker = ticker
                del active_finnhub_ws[ticker]
                break
    print(f"💔 Finnhub WebSocket for {closed_ticker or 'unknown'} CLOSED. Status: {close_status_code}, Message: {close_msg}")

def on_open_finnhub(ws):
    print(f"🎉 Finnhub WebSocket connection OPENED for {ws.url}!")
    # Send subscriptions for all currently tracked tickers immediately on open
    with ws_lock:
        for ticker in active_finnhub_ws.keys():
            sub_msg = json.dumps({"type": "subscribe", "symbol": ticker})
            ws.send(sub_msg)
            print(f"Sent subscribe message for {ticker} via central WS (on_open).")


# Helper to manage the single Finnhub WebSocket thread
def start_finnhub_websocket_thread_manager():
    # This function ensures that the central Finnhub WebSocket thread is running
    # and sends subscription messages for all currently tracked tickers.
    # This will be called from startup and from /subscribe/ endpoint.

    # Only create and start the thread if it's not already running
    if not hasattr(app.state, 'finnhub_ws_thread') or not app.state.finnhub_ws_thread.is_alive():
        print("Initializing central Finnhub WebSocket connection and thread...")
        
        # This debug print is already in place from previous steps
        # print(f"DEBUG: Finnhub WS connecting with key: '{FINNHUB_API_KEY}' (Length: {len(FINNHUB_API_KEY) if FINNHUB_API_KEY else 'N/A'})")

        finnhub_ws_url = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"
        app.state.finnhub_ws_app = WebSocketApp(
            finnhub_ws_url,
            on_message=on_message_finnhub,
            on_error=on_error_finnhub,
            on_close=on_close_finnhub,
            on_open=on_open_finnhub
        )
        app.state.finnhub_ws_thread = threading.Thread(
            target=lambda: app.state.finnhub_ws_app.run_forever(ping_interval=30, ping_timeout=10),
            daemon=True
        )
        app.state.finnhub_ws_thread.start()
        time.sleep(1) # Give it time to connect

    # If already connected, or just connected, send subscriptions for active tickers.
    # The on_open_finnhub will handle initial subscriptions.
    # This block is primarily for cases where new tickers are added while WS is already open.
    with ws_lock:
        if app.state.finnhub_ws_app.sock and app.state.finnhub_ws_app.sock.connected:
            for ticker in active_finnhub_ws.keys():
                sub_msg = json.dumps({"type": "subscribe", "symbol": ticker})
                try:
                    app.state.finnhub_ws_app.send(sub_msg)
                    print(f"Sent subscribe message for {ticker} via central WS (after check).")
                except Exception as e:
                    print(f"Error sending subscribe message for {ticker}: {e}")
        else:
            print("Central Finnhub WS not connected yet, subscriptions will be delayed until open.")


# REST API endpoint to subscribe
@app.post("/subscribe/")
async def subscribe_tickers(tickers: List[str], background_tasks: BackgroundTasks):
    new_tickers_to_add = []
    with ws_lock:
        for t in tickers:
            if t not in active_finnhub_ws:
                active_finnhub_ws[t] = None # Add to our tracking set
                new_tickers_to_add.append(t)

    if new_tickers_to_add:
        print(f"📥 Received new tickers to subscribe (internally): {new_tickers_to_add}")
        # Call the manager to ensure WS is running and sends subscriptions
        start_finnhub_websocket_thread_manager()
        return {"status": "Subscribed", "tickers": new_tickers_to_add}
    else:
        return {"status": "Already subscribed", "tickers": tickers}

# Add a test endpoint for easy subscription from browser
@app.get("/test_subscribe/")
async def test_subscribe_endpoint(background_tasks: BackgroundTasks):
    # EXPANDED LIST OF TICKERS (50 unique popular symbols)
    default_tickers = [
        "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NVDA", "NFLX", "META", "IBM", "ORCL"
        # "JPM", "V", "MA", "DIS", "KO", "PEP", "INTC", "CSCO", "CMCSA", "T",
        # "VZ", "ADBE", "CRM", "PYPL", "SBUX", "COST", "HD", "PG", "NKE", "WMT",
        # "XOM", "CVX", "BAC", "WFC", "GS", "MS", "C", "PFE", "JNJ", "UNH",
        # "MRK", "ABBV", "LLY", "MCD", "BA", "GE", "CAT", "MMM", "GSK", "BHP" # Added more tickers
    ]
    return await subscribe_tickers(default_tickers, background_tasks)
