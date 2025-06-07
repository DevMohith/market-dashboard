#official py image
FROM python:3.10-slim
#my dir
WORKDIR /app
#my dep file
COPY requirements.txt .
#to get my dep run this so that will store in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y iputils-ping
# copy my code into your cont
COPY . .
# comm to run my app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]




# then run anywhere 
# docker build -t chatbot-service .