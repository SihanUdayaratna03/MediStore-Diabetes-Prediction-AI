# Use an official lightweight Node.js image
FROM node:20-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose the Vite default port
EXPOSE 5173

# Start the Vite development server and bind to all network interfaces (--host)
# so it can be accessed from your Windows browser outside the container.
CMD ["npm", "run", "dev", "--", "--host"]
