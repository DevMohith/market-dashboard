#official py image
FROM python:3.10-slim
#my dir
WORKDIR /app
#my dep file
COPY requirements.txt .
#to get my dep run this so that will store in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# copy my code into your cont
COPY . .
# comm to run my app
CMD ["python", "main.py"]


# then run anywhere 
# docker build -t chatbot-service .