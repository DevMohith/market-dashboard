from fetch_trending_data import fetch_top_volume_stocks
from mongo_client import save_trending_to_mongo
from neo4j_trend_client import update_trending_graph

def update_trending_stocks():
    top_stocks = fetch_top_volume_stocks()
    if not top_stocks:
        return []

    save_trending_to_mongo(top_stocks)
    update_trending_graph(top_stocks)

    # Clean ObjectId for JSON response
    cleaned = [{k: v for k, v in stock.items() if k != "_id"} for stock in top_stocks]
    return cleaned
