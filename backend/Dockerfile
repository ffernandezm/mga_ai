FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias del sistema (psycopg2 / pymupdf / build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python primero para aprovechar la cach\u00e9
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el c\u00f3digo
COPY . .

# Render expone $PORT din\u00e1micamente
ENV PORT=8000
EXPOSE 8000

# Arranque: aplica migraciones y luego levanta uvicorn
CMD ["sh", "-c", "alembic upgrade head || true; uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
