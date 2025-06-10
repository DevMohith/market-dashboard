from pymongo import MongoClient

def get_mongo_connection():
    client = MongoClient("mongodb://mongodb:27017/")
    return client["stock_db"]
