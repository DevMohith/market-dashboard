import os
import json
import threading
import asyncio
import time

from fastapi import FastAPI, BackgroundTasks, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
import redis.asyncio as redis
from dotenv import load_dotenv
from typing import List
from websocket import WebSocketApp

# Load environment
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
REDIS_URL       = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_STREAM    = os.getenv("REDIS_STREAM", "market:stream")

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000", "http://127.0.0.1:8000",
        "http://localhost:8001", "http://127.0.0.1:8001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
registry = CollectorRegistry()
messages_received = Counter("finnhub_messages_total", "Total Finnhub WS messages received", registry=registry)
redis_writes      = Counter("redis_writes_total",    "Total Redis xadd operations", registry=registry)
queue_size        = Gauge("queue_size",              "Current size of the internal queue", registry=registry)
redis_up          = Gauge("redis_up",                "Redis connectivity status (1=up)", registry=registry)
ws_connected      = Gauge("ws_connected",            "WebSocket connection status (1=connected)", registry=registry)

# Globals for WS management
active_finnhub_ws = {}
ws_lock = threading.Lock()

@app.on_event("startup")
async def startup_event():
    # Capture the running loop
    app.state.loop = asyncio.get_running_loop()

    # Redis client & health
    app.state.redis = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        await app.state.redis.ping()
        redis_up.set(1)
    except:
        redis_up.set(0)

    # Internal queue + writer
    app.state.queue = asyncio.Queue()
    app.state.redis_writer = app.state.loop.create_task(redis_writer())

@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis_writer.cancel()
    with ws_lock:
        for ws in active_finnhub_ws.values():
            if ws and getattr(ws, "sock", None) and ws.sock.connected:
                ws.close()
    await app.state.redis.close()

async def redis_writer():
    while True:
        queue_size.set(app.state.queue.qsize())
        data = await app.state.queue.get()
        try:
            await app.state.redis.xadd(REDIS_STREAM, data)
            redis_writes.inc()
        except Exception as e:
            print("Redis write error:", e)
        finally:
            app.state.queue.task_done()

def on_message(ws, msg):
    messages_received.inc()
    ws_connected.set(1)
    payload = json.loads(msg)
    if payload.get("type") == "trade":
        for t in payload["data"]:
            record = {
                "symbol": t["s"],
                "price": str(t["p"]),
                "timestamp": str(t["t"]),
                "volume": str(t["v"])
            }
            # Schedule queue.put on the main loop
            asyncio.run_coroutine_threadsafe(
                app.state.queue.put(record),
                app.state.loop
            )

def on_error(ws, err):
    print("WS error:", err)
    ws_connected.set(0)

def on_close(ws, code, reason):
    print("WS closed:", code, reason)
    ws_connected.set(0)

def on_open(ws):
    ws_connected.set(1)
    with ws_lock:
        for sym in active_finnhub_ws.keys():
            ws.send(json.dumps({"type": "subscribe", "symbol": sym}))

def ensure_ws():
    if not hasattr(app.state, "ws_thread") or not app.state.ws_thread.is_alive():
        url = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"
        ws_app = WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        app.state.ws_app = ws_app
        thread = threading.Thread(
            target=lambda: ws_app.run_forever(ping_interval=30),
            daemon=True
        )
        app.state.ws_thread = thread
        thread.start()
        time.sleep(1)

@app.post("/subscribe/")
async def subscribe(tickers: List[str]):
    new = []
    with ws_lock:
        for s in tickers:
            if s not in active_finnhub_ws:
                active_finnhub_ws[s] = None
                new.append(s)
    ensure_ws()
    return {"status": "subscribed", "tickers": new}

@app.delete("/subscribe/")
async def unsubscribe(tickers: List[str]):
    """
    Unsubscribe from one or more tickers.
    - Sends an unsubscribe message over the WebSocket for each symbol.
    - Removes each symbol from active_finnhub_ws under lock.
    """
    removed = []
    with ws_lock:
        for sym in tickers:
            if sym in active_finnhub_ws:
                # 1) send Finnhub unsubscribe
                try:
                    app.state.ws_app.send(json.dumps({
                        "type": "unsubscribe",
                        "symbol": sym
                    }))
                except Exception:
                    pass
                # 2) remove from our tracker
                active_finnhub_ws.pop(sym, None)
                removed.append(sym)
    return {"status": "unsubscribed", "tickers": removed}

@app.get("/subscriptions/")
async def list_subscriptions():
    """
    List all currently active subscriptions.
    - Reads active_finnhub_ws under lock for consistency.
    """
    with ws_lock:
        current = list(active_finnhub_ws.keys())
    return {"active_tickers": current}

@app.get("/health/live")
def live():
    return {"status": "alive"}

@app.get("/health/ready")
async def ready():
    try:
        ready_redis = await app.state.redis.ping()
    except:
        ready_redis = False

    ready_ws = ws_connected._value.get() == 1
    return {"redis": ready_redis, "websocket": ready_ws, "ready": ready_redis and ready_ws}

@app.get("/metrics")
def metrics():
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

