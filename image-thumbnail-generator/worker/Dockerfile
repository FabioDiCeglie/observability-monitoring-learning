FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY worker/ /app/worker/

RUN mkdir -p /app/storage/uploads /app/storage/thumbnails/{small,medium,large}

CMD ["ddtrace-run", "python", "-u", "-m", "worker.worker"]
