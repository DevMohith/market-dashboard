import os
import redis
import httpx
from urllib.parse import urlparse
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("REDIS_URI")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

# Parse Redis URL
parsed = urlparse(REDIS_URL)
redis_client = redis.Redis(
    host=parsed.hostname,
    port=parsed.port,
    decode_responses=True
)

# ✅ Known company-to-ticker mappings
STOCK_NAME_TO_TICKER = {
    "apple": "AAPL",
    "nvidia": "NVDA",
    "microsoft": "MSFT",
    "amazon": "AMZN",
    "google": "GOOGL",
    "meta": "META",
    "tesla": "TSLA",
    "coca-cola": "KO",
    "cocacola": "KO",
    "airbnb": "ABNB",
    "adobe": "ADBE",
    "deutsche bank": "DB",
    "sap": "SAP",
    "infosys": "INFY",
    "ashok leyland": "ASHOKLEY",
    "diebold": "DBD"
}

def get_stock_price(ticker: str) -> str:
    """Fetch stock price from Redis or Twelve Data API."""
    cache_key = f"live_price:{ticker}"
    cached_price = redis_client.get(cache_key)
    if cached_price:
        print(f"[Cache Hit] {ticker} => ${cached_price}")
        return cached_price

    print(f"[Cache Miss] Fetching from Twelve Data for {ticker}...")
    url = f"https://api.twelvedata.com/price?symbol={ticker}&apikey={TWELVE_DATA_API_KEY}"

    try:
        response = httpx.get(url)
        data = response.json()
        price = data.get("price")
        if price:
            redis_client.setex(cache_key, 300, price)  # Cache for 5 minutes
            return price
        return "N/A"
    except Exception as e:
        return f"Error: {str(e)}"

def resolve_name_to_ticker(name: str) -> str:
    """Use static mapping to get ticker."""
    return STOCK_NAME_TO_TICKER.get(name.lower(), name.upper())


def extract_company_name(question: str) -> str | None:
    """Extract a company name from user question using substring match."""
    question = question.lower()
    question = re.sub(r'[^\w\s]', '', question) 
    question = question.replace("stocks", "stock") 

    for name in STOCK_NAME_TO_TICKER:
        if name in question:
            return name
    return None


def check_live_stock_question(user_question: str) -> str | None:
    lower = user_question.lower()
    print(f"[LiveStock] Received question: {lower}")

    if any(k in lower for k in ["live", "price", "current", "stock"]):
        company = extract_company_name(lower)
        if company:
            print(f"[LiveStock] Extracted company: {company}")
            ticker = resolve_name_to_ticker(company)
            print(f"[LiveStock] Resolved ticker: {ticker}")
            price = get_stock_price(ticker)
            print(f"[LiveStock] Fetched price: {price}")
            if "Error" in price or price == "N/A":
                return f"Could not fetch live stock data for {company.title()}."
            return f"The current stock price of {company.title()} ({ticker}) is ${price}."

    return None
