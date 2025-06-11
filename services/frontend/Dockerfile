
# Using node:20-alpine for a smaller image size
FROM node:20-alpine
 
# Set the working directory in the container
WORKDIR /app
 
# Copy package.json and package-lock.json (or yarn.lock)
# to leverage Docker cache for npm install
COPY package*.json ./
 
# Install project dependencies
# Using npm ci for clean install, respecting package-lock.json
RUN npm ci
 
# Copy the rest of the application code into the container
COPY . .
 
# Expose the port that the Vite development server will run on
EXPOSE 5173
 

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
