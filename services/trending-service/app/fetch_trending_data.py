import requests
import os
import random

API_KEY = os.getenv("TWELVE_API_KEY")

def fetch_top_volume_stocks(limit=100):
    url = f"https://api.twelvedata.com/stocks?source=docs&apikey={API_KEY}"
    response = requests.get(url)
    
    data = response.json().get("data", [])[:limit]

    # 🔥 Dynamically generate random scores for however many stocks are returned
    scores = [random.randint(50, 200) for _ in range(len(data))]
    total = sum(scores)

    trending = []
    for i, stock in enumerate(data):
        investment_percent = round((scores[i] / total) * 200, 2)
        trending.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "investment_percent": investment_percent
        })
    return trending
