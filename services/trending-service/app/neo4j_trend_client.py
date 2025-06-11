from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))
)

def update_trending_graph(stocks):
    with driver.session() as session:
        session.run("MATCH ()-[r:TRENDING]->() DELETE r")  # Reset old links
        for stock in stocks:
            session.run("""
                MERGE (c:Company {symbol: $symbol})
                SET c.name = $name
                MERGE (t:Trend {date: date()})
                MERGE (c)-[:TRENDING]->(t)
            """, symbol=stock["symbol"], name=stock["name"])
