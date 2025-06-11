from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from trending import update_trending_stocks

app = FastAPI()

# ✅ Allow frontend to access backend API (CORS fix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Trending Stocks Service Running"}

@app.get("/trending")
def get_trending():
    trending_data = update_trending_stocks()
    return {"trending_stocks": trending_data}
