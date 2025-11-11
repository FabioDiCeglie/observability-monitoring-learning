FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

COPY shared/ /app/shared/
COPY api/ /app/api/

RUN mkdir -p /app/storage/uploads /app/storage/thumbnails/{small,medium,large}

EXPOSE 8000

CMD ["ddtrace-run", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
