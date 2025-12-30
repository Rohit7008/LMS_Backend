FROM python:3.8-slim

# ---------------------------
# System dependencies
# ---------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# Working directory
# ---------------------------
WORKDIR /app

# ---------------------------
# Python dependencies
# ---------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------
# App source
# ---------------------------
COPY . .

# ---------------------------
# Expose FastAPI port
# ---------------------------
EXPOSE 8000

# ---------------------------
# Run migrations + start API
# ---------------------------
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
