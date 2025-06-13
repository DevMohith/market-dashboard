**Conversational Stock Live Dashboard – Fullstack AI Microservices Application**
This project is a Live stock market dashboard built with a microservices architecture. It enables users to interact with stock data in real-time 
using websockets that fetch real time stock data using 3rd party API's real amd Live data, natural language queries, supported by LLM-based chat responses,
Redis-streamed pricing, Qdrant-powered semantic search, and Neo4j-based graph analytics and Redis Caching 
for speed data retrieval and responses.

**The backend is fully containerized using Dockerfiles and Docker Compose, while the frontend runs on Vite + React with WebSocket integration.**

**Project Architecture**
Frontend (React + Vite)
Real-time chat UI with WebSocket listeners and dynamic dashboards.

Backend Microservices (FastAPI + Docker):

**market-data-service**: REST API and WebSocket price streamer

**AI-Chatbot-service:** Embedding-powered RAG backend (Qdrant) & Redis to fetch and respond to users on live stocks queries.

**realtime-gateway:** Redis stream reader and WebSocket bridge

**watchlist-service:** Manages user stock watchlists (MongoDB)

**graph-service:** Graph-based query analysis (Neo4j)

**redis, mongo, neo4j:** Containerized data services


**Requirements:**

Docker

Node.js (v18+ recommended)

Git

**Backend Setup (All Microservices)**
Step 1: Run Backend with Docker Compose   -get into  **cd services/marketdashboard**
**docker-compose up -d --build**

This command:

Builds all Docker images for backend microservices

Starts Redis, MongoDB, Neo4j, Qdrant containers

Spins up all FastAPI services on defined ports (e.g., 8000–8004)

Connects all services under a common Docker network

Wait a few seconds for services to initialize.

💻 Frontend Setup (React + Vite)
Step 2: Start Frontend App - **cd services/frontend**
npm install
npm run dev
This starts the development server at:

**http://localhost:5173** 

Ensure the backend containers are running before starting the frontend to prevent WebSocket connection errors.


Each FastAPI microservice requires:

fastapi

uvicorn

python-dotenv

redis[asyncio]

pymongo, neo4j, qdrant-client (per service-specific needs)

Frontend
Frontend uses:

React, Vite

axios

socket.io-client or native WebSocket

.env config for WebSocket and API endpoints

{{{ we have created requirements.txt files for each services everything but how ever we containerized app with docker will will also runs all dependecies when building image}}}}

Troubleshooting
❌ WebSocket Disconnected?
Ensure realtime-gateway is running and has access to Redis.

❌ MongoDB or Neo4j errors?
Check that .env uses container names (e.g., mongo, neo4j) instead of localhost.

Use docker logs <container_name> to debug individual services.

Live Features
Real-time stock price streaming via Redis

Conversational chat interface (AI stockbot) using LLMs and Redis

Semantic search with Qdrant embeddings

Graph-based querying via Neo4j

Dynamic frontend with WebSocket updates

