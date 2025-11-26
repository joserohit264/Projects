FROM python:3.13-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for pycryptodome build)
# RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-m", "backend.app"]
