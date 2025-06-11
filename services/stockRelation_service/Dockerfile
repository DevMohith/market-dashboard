FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Start FastAPI app
CMD ["uvicorn", "mongo_to_neo4j:app", "--host", "0.0.0.0", "--port", "8004"]
