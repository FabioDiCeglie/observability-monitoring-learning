#!/bin/bash

# Datadog Sandbox Setup Script
set -e

echo "🐕 Setting up Datadog Sandbox Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install it and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are available${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo -e "${YELLOW}⚠️  No .env file found. Copying from env.example...${NC}"
        cp env.example .env
        echo -e "${YELLOW}📝 Please edit .env file and add your Datadog API key${NC}"
        echo -e "${BLUE}   You can get your API key from: https://app.datadoghq.com/organization-settings/api-keys${NC}"
        
        # Check if DD_API_KEY is set
        if grep -q "your_datadog_api_key_here" .env; then
            echo -e "${RED}❌ Please set your DD_API_KEY in the .env file before continuing${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ No .env file found and no env.example to copy from${NC}"
        exit 1
    fi
fi

# Validate DD_API_KEY
source .env
if [ -z "$DD_API_KEY" ] || [ "$DD_API_KEY" = "your_datadog_api_key_here" ]; then
    echo -e "${RED}❌ DD_API_KEY is not set in .env file${NC}"
    echo -e "${BLUE}   Please edit .env and set your Datadog API key${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment configuration looks good${NC}"

# Build and start services
echo -e "${BLUE}🚀 Building and starting services...${NC}"
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${BLUE}🔍 Checking service health...${NC}"

# Check Flask API
if curl -f http://localhost/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Flask API is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Flask API is not responding yet, checking logs...${NC}"
    docker-compose logs flask-api | tail -10
fi

# Check Nginx
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx is not responding${NC}"
fi

# Check Datadog Agent
echo -e "${BLUE}🔍 Checking Datadog Agent status...${NC}"
docker-compose exec -T datadog-agent agent status || echo -e "${YELLOW}⚠️  Could not get agent status${NC}"

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo -e "${BLUE}📊 Access your services:${NC}"
echo -e "   • API Health: ${YELLOW}http://localhost/api/health${NC}"
echo -e "   • System Metrics: ${YELLOW}http://localhost/api/system-metrics${NC}"
echo -e "   • Slow Endpoint: ${YELLOW}http://localhost/api/slow${NC}"
echo -e "   • Error Simulation: ${YELLOW}http://localhost/api/error${NC}"
echo -e "   • Load Test: ${YELLOW}http://localhost/api/load?operations=1000${NC}"
echo ""
echo -e "${BLUE}🐕 Datadog Resources:${NC}"
echo -e "   • Infrastructure: ${YELLOW}https://app.datadoghq.com/infrastructure${NC}"
echo -e "   • APM: ${YELLOW}https://app.datadoghq.com/apm${NC}"
echo -e "   • Logs: ${YELLOW}https://app.datadoghq.com/logs${NC}"
echo -e "   • Metrics: ${YELLOW}https://app.datadoghq.com/metric/explorer${NC}"
echo ""
echo -e "${BLUE}🛠️  Useful commands:${NC}"
echo -e "   • View logs: ${YELLOW}docker-compose logs -f${NC}"
echo -e "   • Restart services: ${YELLOW}docker-compose restart${NC}"
echo -e "   • Stop services: ${YELLOW}docker-compose down${NC}"
echo -e "   • Agent status: ${YELLOW}docker-compose exec datadog-agent agent status${NC}"
echo ""
echo -e "${GREEN}Happy monitoring! 📈${NC}"
