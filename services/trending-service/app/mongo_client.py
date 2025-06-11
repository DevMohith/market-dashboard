import pymongo
import os
from dotenv import load_dotenv
load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["market"]
collection = db["trending"]

def save_trending_to_mongo(stocks):
    collection.delete_many({})
    collection.insert_many(stocks)
