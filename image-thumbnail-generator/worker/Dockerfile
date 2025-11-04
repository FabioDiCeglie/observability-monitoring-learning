FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY worker/requirements.txt /app/worker/requirements.txt
RUN pip install --no-cache-dir -r worker/requirements.txt

COPY shared/ /app/shared/
COPY worker/ /app/worker/

RUN mkdir -p /app/storage/uploads /app/storage/thumbnails/{small,medium,large}

CMD ["python", "-u", "worker/worker.py"]
