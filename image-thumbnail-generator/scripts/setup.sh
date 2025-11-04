#!/bin/bash

set -e

echo "🚀 Setting up Image Thumbnail Generator..."

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env created"
else
    echo "ℹ️  .env already exists"
fi

echo "📁 Creating storage directories..."
mkdir -p storage/uploads
mkdir -p storage/thumbnails/small
mkdir -p storage/thumbnails/medium
mkdir -p storage/thumbnails/large

echo "🐳 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 15

echo ""
echo "✅ Setup complete!"
echo ""
echo "Test the API:"
echo "  curl http://localhost:8000/health"
echo ""
