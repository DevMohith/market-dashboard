import os
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from neo4j import GraphDatabase

app = FastAPI()

# Allow frontend (React) to access this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client: MongoClient[Any] = MongoClient(mongo_uri)
mongo_db: Database[Any] = mongo_client["stock_data"]
companies_collection: Collection[Dict[str, Any]] = mongo_db["companies"]

# Neo4j connection
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(
        os.getenv("NEO4J_USER", "neo4j"),
        os.getenv("NEO4J_PASS", "Neo4j123"),
    ),
)

# 🟢 Route: Get all companies from MongoDB
@app.get("/companies")
def get_companies():
    return list(companies_collection.find({}, {"_id": 0}))

# 🔵 Route: Get company partnerships from Neo4j
@app.get("/partnerships")
def get_partnerships():
    try:
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (a:Company)-[:PARTNER_WITH]->(b:Company)
                RETURN a.name AS source, b.name AS target
            """)
            return [record.data() for record in result]
    except Exception as e:
        return {"error": str(e)}

# 🔁 Route: Sync MongoDB data to Neo4j
@app.post("/sync-to-neo4j")
def sync_to_neo4j():
    try:
        companies = list(companies_collection.find({}, {"_id": 0}))
        with neo4j_driver.session() as session:
            for company in companies:
                ticker = company.get("ticker")
                if not ticker:
                    print("⚠️ Missing ticker. Skipping:", company)
                    continue

                session.run("""
                    MERGE (c:Company {ticker: $ticker})
                    SET c.name = $name, c.sector = $sector, c.market_cap = $market_cap
                """, {
                    "ticker": ticker,
                    "name": company.get("name", ""),
                    "sector": company.get("sector", ""),
                    "market_cap": float(company.get("market_cap", 0))
                })

                for partner in company.get("partners", []):
                    if not isinstance(partner, str):
                        print(f"⚠️ Skipping invalid partner in {ticker}: {partner}")
                        continue
                    session.run("""
                        MATCH (a:Company {ticker: $ticker}), (b:Company {ticker: $partner})
                        MERGE (a)-[:PARTNER_WITH]->(b)
                    """, {
                        "ticker": ticker,
                        "partner": partner
                    })
        return {"message": "Synced to Neo4j"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# 🧪 Health check
@app.get("/")
async def root():
    return {"message": "Hello, your FastAPI app is running!"}

