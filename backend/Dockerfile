FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# curl se usa en el healthcheck; las dependencias Python se instalan como wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python primero para aprovechar la cach\u00e9
COPY requirements-production.txt .
RUN pip install --upgrade pip && pip install --only-binary=:all: -r requirements-production.txt

# Copiar el c\u00f3digo
COPY . .

# Render expone $PORT din\u00e1micamente
ENV PORT=8000
EXPOSE 8000

# El puerto no se publica; solo el proxy Nginx de la red Docker accede a Uvicorn.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
