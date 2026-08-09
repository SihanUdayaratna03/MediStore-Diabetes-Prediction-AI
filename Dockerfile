# Backend image — serves both the v2 and v3 FastAPI apps.
# docker-compose overrides CMD to select which one starts.
FROM python:3.12-slim

# LightGBM and XGBoost require libgomp1 at runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the requirements files first so pip install stays cached
COPY requirements.txt requirements_uci130.txt ./

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements_uci130.txt

# Backend package, trained artifacts and datasets
COPY backend/ ./backend/
COPY models/  ./models/
COPY data/    ./data/

# No CMD: docker-compose supplies the uvicorn target for the v2 or v3 service.
