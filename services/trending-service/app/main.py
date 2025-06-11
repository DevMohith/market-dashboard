from fastapi import FastAPI
from trending import update_trending_stocks

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Trending Stocks Service Running"}

@app.get("/trending")
def get_trending():
    trending_data = update_trending_stocks()
    return {"trending_stocks": trending_data}
