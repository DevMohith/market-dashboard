from fastapi import FastAPI, BackgroundTasks
import os
import json
import threading
import asyncio
import redis.asyncio as redis
from dotenv import load_dotenv
from typing import List
from websocket import WebSocketApp

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()

# Environment variables
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_STREAM = os.getenv("REDIS_STREAM", "market:stream")

# Global trackers
active_subscriptions = set()

# Set up Redis, queue, and event loop on startup
@app.on_event("startup")
async def startup():
    app.state.redis = await redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True
    )
    app.state.event_loop = asyncio.get_running_loop()
    await app.state.redis.ping()
    print("✅ Connected to Redis")

    app.state.queue = asyncio.Queue()
    app.state.redis_writer_task = app.state.event_loop.create_task(redis_writer())

async def redis_writer():
    while True:
        data = await app.state.queue.get()
        try:
            await app.state.redis.xadd(REDIS_STREAM, data)
        except Exception as e:
            print("❌ Redis write error:", e)
        finally:
            app.state.queue.task_done()

# Graceful shutdown: cancel redis_writer task and close redis
@app.on_event("shutdown")
async def shutdown():
    print("🛑 Shutting down...")
    app.state.redis_writer_task.cancel()
    try:
        await app.state.redis_writer_task
    except asyncio.CancelledError:
        pass
    await app.state.redis.close()
    print("✅ Redis connection closed")

# WebSocket message handler
def run_finnhub_websocket(tickers: List[str]):
    def on_message(ws, message):
        print("📩 Received from WebSocket:", message)
        try:
            data = json.loads(message)
            if data.get("type") == "trade":
                for trade in data["data"]:
                    redis_data = {
                        "event": "price",
                        "symbol": trade["s"],
                        "price": str(trade["p"]),
                        "timestamp": str(trade["t"]),
                    }
                    print("🔁 About to enqueue for Redis:", redis_data)

                    # Enqueue Redis write safely from thread
                    asyncio.run_coroutine_threadsafe(
                        app.state.queue.put(redis_data),
                        app.state.event_loop
                    )
        except Exception as e:
            print(f"❌ Error handling WebSocket message or enqueueing Redis data: {e}")

    def on_error(ws, error):
        print("WebSocket error:", error)

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")

    def on_open(ws):
        for ticker in tickers:
            sub_msg = json.dumps({"type": "subscribe", "symbol": ticker})
            ws.send(sub_msg)
            print(f"Subscribed to {ticker}")

    ws = WebSocketApp(
        f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )

    print("🚀 Started Finnhub WebSocket thread")
    ws.run_forever()

# REST API endpoint to subscribe
@app.post("/subscribe/")
async def subscribe(tickers: List[str], background_tasks: BackgroundTasks):
    new_tickers = [t for t in tickers if t not in active_subscriptions]
    if new_tickers:
        print("📥 Received new tickers to subscribe:", new_tickers)
        active_subscriptions.update(new_tickers)
        background_tasks.add_task(
            lambda: threading.Thread(target=run_finnhub_websocket, args=(new_tickers,), daemon=True).start()
        )
        return {"status": "Subscribed", "tickers": new_tickers}
    else:
        return {"status": "Already subscribed", "tickers": tickers}
