# Use an official Python runtime as a parent image
FROM python:3.10-slim

# LightGBM and XGBoost sometimes require the libgomp1 library to run efficiently
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files first (this caches the pip install step)
COPY requirements.txt requirements_uci130.txt ./

# Install dependencies for both the V2 and V3 models
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements_uci130.txt

# Copy the rest of the backend code and ML models (.pkl files) into the container
COPY . .

# We don't set a CMD here because docker-compose will override it 
# depending on whether it's starting the v2 or v3 server.
