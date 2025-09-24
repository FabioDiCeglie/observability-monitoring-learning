# Datadog Sandbox Project 🐕

A complete local development environment for practicing Datadog monitoring with Docker Compose.

## Architecture

- **Flask API**: Simple REST API with database operations
- **PostgreSQL**: Database with sample data
- **Nginx**: Reverse proxy for the API
- **Datadog Agent**: Monitoring and log collection
- **Redis**: Caching layer (optional)

## Prerequisites

1. **Docker & Docker Compose** installed
2. **Datadog Account** with API key
3. **Git** (optional, for version control)

## Quick Start

1. **Set up your Datadog API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your DD_API_KEY
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Check services are running**:
   ```bash
   docker-compose ps
   curl http://localhost/api/health
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

## What You'll Monitor

### 📊 **Metrics**
- Flask application metrics (requests, response times, errors)
- PostgreSQL database metrics (connections, queries, performance)
- Nginx web server metrics (requests, status codes)
- System metrics (CPU, memory, disk, network)

### 📝 **Logs**
- Application logs from Flask
- Database logs from PostgreSQL  
- Access logs from Nginx
- Datadog Agent logs

### 🔍 **Traces** (APM)
- HTTP request traces through the stack
- Database query traces
- Service dependencies and performance

## Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 80 | Reverse proxy |
| Flask API | 5000 | Python web application |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache (optional) |
| Datadog Agent | 8126 | APM traces |

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/metrics` - Custom metrics endpoint
- `GET /api/slow` - Simulate slow response (for testing)
- `GET /api/error` - Simulate error (for testing)

## Datadog Integration Features

- **Infrastructure Monitoring**: Host and container metrics
- **APM**: Distributed tracing across services
- **Log Management**: Centralized logging with parsing
- **Database Monitoring**: PostgreSQL performance insights
- **Custom Metrics**: Business-specific metrics
- **Alerts**: Set up monitors for key metrics

## Learning Objectives

After completing this sandbox, you'll know how to:

1. ✅ Deploy Datadog Agent in containerized environments
2. ✅ Configure service discovery and auto-configuration
3. ✅ Set up database monitoring and integrations
4. ✅ Implement distributed tracing (APM)
5. ✅ Create custom metrics and dashboards
6. ✅ Configure log collection and parsing
7. ✅ Set up alerts and notifications
8. ✅ Monitor multi-service applications

## Troubleshooting

### Common Issues
- **Agent not reporting**: Check DD_API_KEY in .env file
- **No metrics**: Ensure containers can reach Datadog Agent
- **Permission errors**: Check Docker socket permissions

### Useful Commands
```bash
# Check agent status
docker-compose exec datadog-agent agent status

# View agent logs
docker-compose logs datadog-agent

# Restart specific service
docker-compose restart flask-api

# Clean up everything
docker-compose down -v
```

## Next Steps

1. **Explore Datadog UI**: Check Infrastructure, APM, and Logs
2. **Create Dashboards**: Build custom dashboards for your services  
3. **Set up Alerts**: Configure monitors for critical metrics
4. **Extend the Stack**: Add more services (Redis, Elasticsearch, etc.)
5. **Deploy to Cloud**: Move to AWS/GCP/Azure for real-world practice

---

Happy monitoring! 📈