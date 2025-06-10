from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from typing import Dict, Optional, Any
import requests  
from requests import Response  

# ✅ MongoDB setup 
client: MongoClient[Any] = MongoClient("mongodb://localhost:27017/")
db: Database[Any] = client["stock_data"]
companies_collection: Collection[Dict[str, Any]] = db["companies"]

# Twelve Data API setup
API_KEY = "887f8ca2776d40e7904c46c5daab595b"
BASE_URL = "https://api.twelvedata.com"

tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NFLX", "NVDA"]


def fetch_company_data(ticker: str) -> Optional[Dict[str, Any]]:
    response: Response = requests.get(
        f"{BASE_URL}/quote", params={"symbol": ticker, "apikey": API_KEY}
    )
    data: Dict[str, Any] = response.json()

    print(f"Response for {ticker}: {data}")  

    if "code" in data:
        print(f"Error fetching {ticker}: {data['message']}")
        return None

    return {
        "ticker": ticker,
        "name": data.get("name"),
        "market_cap": float(data.get("market_cap", 0)),
        "sector": "Technology",
        "partners": []
    }


def main() -> None:
   
    for ticker in tickers:
        existing = companies_collection.find_one({"ticker": ticker})
        if existing:
            print(f"{ticker} already exists. Skipping insert.")
            continue

        company = fetch_company_data(ticker)
        if company:
            companies_collection.insert_one(company)
            print(f"Inserted {company['ticker']} into MongoDB")


if __name__ == "__main__":
    main()  
