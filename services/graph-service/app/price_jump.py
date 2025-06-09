from mongo_client import get_mongo_connection
from neo4j_client import driver, create_price_jump
from datetime import datetime

def run_price_jump_detection():
    db = get_mongo_connection()
    collection = db.prices  # assumes documents: {symbol, history: [prices...]}

    for doc in collection.find():
        symbol = doc.get("symbol")
        prices = doc.get("history", [])
        
        if not symbol or len(prices) < 2:
            continue

        latest = prices[-1]
        previous = prices[-2]

        if previous == 0:
            continue

        change = ((latest - previous) / previous) * 100

        if abs(change) >= 2:
            timestamp = datetime.now().isoformat()
            with driver.session() as session:
                session.write_transaction(create_price_jump, symbol, round(change, 2), timestamp)
                print(f"⚠️ Price jump logged: {symbol} {round(change, 2)}% at {timestamp}")
