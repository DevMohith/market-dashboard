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
        # Removed the check for existing data.
        # MERGE statements are idempotent and will ensure data is present.
        print("🚀 Attempting to populate/ensure initial Neo4j data...")
        
        # Create all company nodes
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
            MERGE (ibm:Company {symbol: 'IBM', name: 'International Business Machines Corp.'})
            MERGE (adbe:Company {symbol: 'ADBE', name: 'Adobe Inc.'})
            MERGE (wmt:Company {symbol: 'WMT', name: 'Walmart Inc.'})
            MERGE (nflx:Company {symbol: 'NFLX', name: 'Netflix Inc.'})
            MERGE (orcl:Company {symbol: 'ORCL', name: 'Oracle Corp.'})
            MERGE (f:Company {symbol: 'F', name: 'Ford Motor Co.'})
            MERGE (gm:Company {symbol: 'GM', name: 'General Motors Co.'})
            MERGE (tgt:Company {symbol: 'TGT', name: 'Target Corp.'})
            MERGE (vwagy:Company {symbol: 'VWAGY', name: 'Volkswagen AG'})
            MERGE (poahy:Company {symbol: 'POAHY', name: 'Porsche Automobil Holding SE'})
            MERGE (byddy:Company {symbol: 'BYDDY', name: 'BYD Co. Ltd.'})
            MERGE (tm:Company {symbol: 'TM', name: 'Toyota Motor Corp.'})
            MERGE (beats:Company {symbol: 'BEATS', name: 'Beats Electronics'})
        """)
        
        # Create all relationships
        await session.run("""
            MATCH (a:Company {symbol: 'AAPL'})
            MATCH (m:Company {symbol: 'MSFT'})
            MATCH (g:Company {symbol: 'GOOG'})
            MATCH (ts:Company {symbol: 'TSLA'})
            MATCH (nvd:Company {symbol: 'NVDA'})
            MATCH (s:Company {symbol: 'SBUX'})
            MATCH (ko:Company {symbol: 'KO'})
            MATCH (pep:Company {symbol: 'PEP'})
            MATCH (amz:Company {symbol: 'AMZN'})
            MATCH (dis:Company {symbol: 'DIS'})
            MATCH (ibm:Company {symbol: 'IBM'})
            MATCH (adbe:Company {symbol: 'ADBE'})
            MATCH (wmt:Company {symbol: 'WMT'})
            MATCH (nflx:Company {symbol: 'NFLX'})
            MATCH (orcl:Company {symbol: 'ORCL'})
            MATCH (f:Company {symbol: 'F'})
            MATCH (gm:Company {symbol: 'GM'})
            MATCH (tgt:Company {symbol: 'TGT'})
            MATCH (vwagy:Company {symbol: 'VWAGY'})
            MATCH (poahy:Company {symbol: 'POAHY'})
            MATCH (byddy:Company {symbol: 'BYDDY'})
            MATCH (tm:Company {symbol: 'TM'})
            MATCH (beats:Company {symbol: 'BEATS'})

            MERGE (a)-[:COMPETES_WITH]->(m)
            MERGE (a)-[:COMPETES_WITH]->(g)
            MERGE (m)-[:COMPETES_WITH]->(g)
            MERGE (ts)-[:SUPPLIES_SOFTWARE_TO]->(m)
            MERGE (nvd)-[:SUPPLIES_CHIPS_TO]->(ts)
            MERGE (s)-[:PARTNERS_WITH]->(ko)
            MERGE (ko)-[:COMPETES_WITH]->(pep)
            MERGE (a)-[:SELLS_THROUGH]->(amz)
            MERGE (dis)-[:DISTRIBUTES_THROUGH]->(amz)
            MERGE (dis)-[:HAS_STORE_IN]->(s)
            MERGE (nvd)-[:SUPPLIES_TO]->(g)
            MERGE (a)-[:OWNS {subsidiary: 'Beats Electronics'}]->(beats)
            
            
            MERGE (ibm)-[:COMPETES_WITH]->(m)
            MERGE (ibm)-[:COMPETES_WITH]->(g)
            MERGE (ibm)-[:BUYS_FROM]->(nvd)
            MERGE (ibm)-[:COMPETES_WITH]->(orcl)

           
            MERGE (amz)-[:COMPETES_WITH]->(g)
            MERGE (adbe)-[:PARTNERS_WITH]->(m)
            MERGE (adbe)-[:COMPETES_WITH]->(orcl)
            MERGE (wmt)-[:COMPETES_WITH]->(amz)
            MERGE (wmt)-[:COMPETES_WITH]->(tgt)
            MERGE (nflx)-[:COMPETES_WITH]->(dis)
            MERGE (nflx)-[:COMPETES_WITH]->(amz)
            MERGE (nflx)-[:ADVERTISING_ON]->(g)
            MERGE (orcl)-[:COMPETES_WITH]->(m)
            MERGE (ts)-[:BUYS_SOFTWARE_FROM]->(m)
            MERGE (ts)-[:BUYS_CHIPS_FROM]->(nvd)
            MERGE (f)-[:COMPETES_WITH]->(ts)
            MERGE (f)-[:COMPETES_WITH]->(gm)
            MERGE (gm)-[:COMPETES_WITH]->(ts)
            MERGE (gm)-[:COMPETES_WITH]->(byddy)
            MERGE (tgt)-[:COMPETES_WITH]->(amz)
            MERGE (s)-[:COMPETES_WITH]->(pep)

            
            MERGE (vwagy)-[:COMPETES_WITH]->(ts)
            MERGE (vwagy)-[:COMPETES_WITH]->(byddy)
            MERGE (vwagy)-[:COMPETES_WITH]->(gm)
            MERGE (vwagy)-[:COMPETES_WITH]->(f)
            MERGE (vwagy)-[:COMPETES_WITH]->(tm)
            MERGE (vwagy)-[:OWNS]->(poahy)

            MERGE (poahy)-[:OWNED_BY]->(vwagy)
            MERGE (poahy)-[:COMPETES_WITH]->(ts)

            MERGE (byddy)-[:COMPETES_WITH]->(ts)
            MERGE (byddy)-[:COMPETES_WITH]->(vwagy)
            MERGE (byddy)-[:COMPETES_WITH]->(gm)

            MERGE (tm)-[:COMPETES_WITH]->(ts)
            MERGE (tm)-[:COMPETES_WITH]->(vwagy)
            MERGE (tm)-[:COMPETES_WITH]->(gm)
            MERGE (tm)-[:COMPETES_WITH]->(f)
            MERGE (tm)-[:COMPETES_WITH]->(byddy)

            MERGE (nvd)-[:SUPPLIES_AI_COMPUTING_TO]->(vwagy)
        """)
        
        print("✅ Initial Neo4j data populated.")

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    await get_neo4j_driver()
    await populate_initial_data() # This will now always attempt to MERGE data

@app.on_event("shutdown")
async def shutdown_event():
    await close_neo4j_driver()

# --- API Endpoints ---
@app.get("/relationships/{symbol}", response_model=GraphData)
async def get_company_relationships(symbol: str):
    """
    Fetches direct relationships for a given company symbol from the already populated Neo4j.
    """
    driver = await get_neo4j_driver()
    
    symbol_upper = symbol.upper()
    nodes_data: List[Dict[str, Any]] = []
    links_data: List[Dict[str, Any]] = []
    
    seen_node_ids: Set[str] = set()
    seen_link_hashes: Set[frozenset] = set()

    print(f"DEBUG (Backend): Processing request for symbol: {symbol_upper}")

    async with driver.session() as session:
        # 1. Fetch the central node first
        central_node_result = await session.run(
            "MATCH (n:Company {symbol: $symbol}) RETURN n",
            symbol=symbol_upper
        )
        central_node_record = await central_node_result.single()
        
        if not central_node_record:
            print(f"DEBUG (Backend): Central node '{symbol_upper}' not found in populated data.")
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
            
        # 2. Fetch all relationships and connected nodes for the central node
        relationships_result = await session.run(
            """
            MATCH (n:Company {symbol: $symbol})-[r]-(m:Company)
            RETURN n, r, m
            """,
            symbol=symbol_upper
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
                
            link_type = relationship_data.type
            link_hash = frozenset({source_id, target_id, link_type})

            if link_hash not in seen_link_hashes:
                links_data.append(GraphLink(source=source_id, target=target_id, type=link_type).dict())
                seen_link_hashes.add(link_hash)

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

