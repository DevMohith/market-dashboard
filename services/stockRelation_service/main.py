from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from neo4j import AsyncGraphDatabase
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Set
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS settings
origins = [
    "http://localhost:5173",  # Your React frontend's development URL
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://localhost:8002",
    "http://127.0.0.1:8002",
    "http://localhost:8003",
    "http://127.0.0.1:8003",
    "http://localhost:8004", # This service's own URL
    "http://127.0.0.1:8004"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j Environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

# Neo4j Driver instance
driver: Optional[AsyncGraphDatabase.driver] = None

# Pydantic models for response
class GraphNode(BaseModel):
    id: str
    symbol: str
    label: str
    type: str

class GraphLink(BaseModel):
    source: str
    target: str
    type: str

class GraphData(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

# --- Neo4j Operations ---
async def get_neo4j_driver():
    global driver
    if driver is None:
        driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        try:
            await driver.verify_connectivity()
            print("✅ Stock Relation Service: Connected to Neo4j")
        except Exception as e:
            print(f"❌ Stock Relation Service: Failed to connect to Neo4j: {e}")
            driver = None
            raise

    return driver

async def close_neo4j_driver():
    global driver
    if driver:
        await driver.close()
        driver = None
        print("✅ Stock Relation Service: Neo4j connection closed")

async def populate_initial_data():
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        # Check if data already exists to avoid duplicates
        result = await session.run("MATCH (n:Company) RETURN count(n) AS nodeCount")
        record = await result.single()
        if record and record["nodeCount"] > 0:
            print("ℹ️ Neo4j already contains data. Skipping initial population.")
            return

        print("🚀 Populating initial Neo4j data...")
        # Create companies
        await session.run("""
            MERGE (a:Company {symbol: 'AAPL', name: 'Apple Inc.'})
            MERGE (m:Company {symbol: 'MSFT', name: 'Microsoft Corp.'})
            MERGE (g:Company {symbol: 'GOOG', name: 'Alphabet Inc. (Google)'})
            MERGE (ts:Company {symbol: 'TSLA', name: 'Tesla Inc.'})
            MERGE (nvd:Company {symbol: 'NVDA', name: 'NVIDIA Corp.'})
            MERGE (s:Company {symbol: 'SBUX', name: 'Starbucks Corp.'})
            MERGE (ko:Company {symbol: 'KO', name: 'Coca-Cola Co.'})
            MERGE (pep:Company {symbol: 'PEP', name: 'PepsiCo Inc.'})
            MERGE (amz:Company {symbol: 'AMZN', name: 'Amazon.com Inc.'})
            MERGE (dis:Company {symbol: 'DIS', name: 'Walt Disney Co.'})
        """)
        
        # Create relationships (split into individual MERGE statements for robustness)
        await session.run("MATCH (a:Company {symbol: 'AAPL'}), (m:Company {symbol: 'MSFT'}) MERGE (a)-[:COMPETES_WITH]->(m)")
        await session.run("MATCH (a:Company {symbol: 'AAPL'}), (g:Company {symbol: 'GOOG'}) MERGE (a)-[:COMPETES_WITH]->(g)")
        await session.run("MATCH (m:Company {symbol: 'MSFT'}), (g:Company {symbol: 'GOOG'}) MERGE (m)-[:COMPETES_WITH]->(g)")
        await session.run("MATCH (ts:Company {symbol: 'TSLA'}), (m:Company {symbol: 'MSFT'}) MERGE (ts)-[:SUPPLIES]->(m)")
        await session.run("MATCH (nvd:Company {symbol: 'NVDA'}), (ts:Company {symbol: 'TSLA'}) MERGE (nvd)-[:SUPPLIES]->(ts)")
        await session.run("MATCH (s:Company {symbol: 'SBUX'}), (ko:Company {symbol: 'KO'}) MERGE (s)-[:PARTNERS_WITH]->(ko)")
        await session.run("MATCH (ko:Company {symbol: 'KO'}), (pep:Company {symbol: 'PEP'}) MERGE (ko)-[:COMPETES_WITH]->(pep)")
        await session.run("MATCH (a:Company {symbol: 'AAPL'}), (amz:Company {symbol: 'AMZN'}) MERGE (a)-[:SELLS_THROUGH]->(amz)")
        await session.run("MATCH (dis:Company {symbol: 'DIS'}), (amz:Company {symbol: 'AMZN'}) MERGE (dis)-[:DISTRIBUTES_THROUGH]->(amz)")
        await session.run("MATCH (dis:Company {symbol: 'DIS'}), (s:Company {symbol: 'SBUX'}) MERGE (dis)-[:HAS_STORE_IN]->(s)")
        await session.run("MATCH (nvd:Company {symbol: 'NVDA'}), (g:Company {symbol: 'GOOG'}) MERGE (nvd)-[:SUPPLIES]->(g)")
        # This last one creates a new node within the query itself
        await session.run("MATCH (a:Company {symbol: 'AAPL'}) MERGE (a)-[:OWNS {subsidiary: 'Beats Electronics'}]->(:Company {symbol: 'BEATS', name: 'Beats Electronics'})")
        
        print("✅ Initial Neo4j data populated.")

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    await get_neo4j_driver()
    await populate_initial_data()

@app.on_event("shutdown")
async def shutdown_event():
    await close_neo4j_driver()

# --- API Endpoints ---
@app.get("/relationships/{symbol}", response_model=GraphData)
async def get_company_relationships(symbol: str):
    """
    Fetches direct relationships for a given company symbol.
    """
    driver = await get_neo4j_driver()
    
    nodes_data: List[Dict[str, Any]] = []
    links_data: List[Dict[str, Any]] = []
    
    seen_node_ids: Set[str] = set()
    seen_link_hashes: Set[frozenset] = set()

    print(f"DEBUG (Backend): Fetching relationships for symbol: {symbol.upper()}")

    async with driver.session() as session:
        # 1. Fetch the central node first
        central_node_result = await session.run(
            "MATCH (n:Company {symbol: $symbol}) RETURN n",
            symbol=symbol.upper()
        )
        central_node_record = await central_node_result.single()
        
        if not central_node_record:
            print(f"DEBUG (Backend): Central node '{symbol.upper()}' not found.")
            return GraphData(nodes=[], links=[])

        n_data = central_node_record["n"]
        node_id = n_data["symbol"]
        if node_id not in seen_node_ids:
            nodes_data.append(GraphNode(
                id=node_id, 
                symbol=node_id, 
                label=n_data.get("name", node_id), 
                type="Company"
            ).dict())
            seen_node_ids.add(node_id)
            # print(f"DEBUG (Backend): Added central node: {node_id}") # Commenting out for cleaner logs

        # 2. Fetch all relationships and connected nodes for the central node
        # This query ensures that for each record, n, r, and m are all present
        # if a relationship exists.
        relationships_result = await session.run(
            """
            MATCH (n:Company {symbol: $symbol})-[r]-(m:Company)
            RETURN n, r, m
            """,
            symbol=symbol.upper()
        )

        async for record in relationships_result:
            source_node_data = record["n"]
            relationship_data = record["r"]
            target_node_data = record["m"]

            # Add source node if not already added
            source_id = source_node_data["symbol"]
            if source_id not in seen_node_ids:
                nodes_data.append(GraphNode(
                    id=source_id, 
                    symbol=source_id, 
                    label=source_node_data.get("name", source_id), 
                    type="Company"
                ).dict())
                seen_node_ids.add(source_id)
                # print(f"DEBUG (Backend): Added source node for link: {source_id}") # Commenting out for cleaner logs
            
            # Add target node if not already added
            target_id = target_node_data["symbol"]
            if target_id not in seen_node_ids:
                nodes_data.append(GraphNode(
                    id=target_id, 
                    symbol=target_id, 
                    label=target_node_data.get("name", target_id), 
                    type="Company"
                ).dict())
                seen_node_ids.add(target_id)
                # print(f"DEBUG (Backend): Added target node for link: {target_id}") # Commenting out for cleaner logs

            # Add relationship link (deduplicate based on source, target, type)
            link_type = relationship_data.type
            # Use frozenset for a unique hashable representation for a link,
            # treating A-R-B as the same link as B-R-A if undirected.
            link_hash = frozenset({source_id, target_id, link_type})

            if link_hash not in seen_link_hashes:
                links_data.append(GraphLink(source=source_id, target=target_id, type=link_type).dict())
                seen_link_hashes.add(link_hash)
                # print(f"DEBUG (Backend): Added link: {source_id}-[{link_type}]->{target_id}") # Commenting out for cleaner logs

    # Final lists to return
    final_nodes = [node for node in nodes_data if node['id'] in seen_node_ids] 
    final_links = links_data

    print(f"DEBUG (Backend): Final nodes to return: {len(final_nodes)} nodes")
    print(f"DEBUG (Backend): Final links to return: {len(final_links)} links")
    
    return GraphData(nodes=final_nodes, links=final_links)


# Test Endpoint for checking Neo4j connection and data
@app.get("/neo4j_status")
async def neo4j_status():
    try:
        driver = await get_neo4j_driver()
        await driver.verify_connectivity()
        async with driver.session() as session:
            result = await session.run("RETURN 'Neo4j is connected and operational!' AS message")
            message = await result.single()
            return {"status": "success", "message": message["message"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j connection failed: {e}")

