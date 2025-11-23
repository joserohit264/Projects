# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# install system deps for optional features
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# default to the CLI (non-GUI) entrypoint
ENTRYPOINT ["python3", "main.py"]
