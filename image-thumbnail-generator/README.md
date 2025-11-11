# Image Thumbnail Generator 🖼️

A distributed image processing system with complete Datadog observability. Upload images via REST API and automatically generate thumbnails in multiple sizes using asynchronous processing.

## 🎯 What It Does

- **Upload** images through a REST API
- **Process** images asynchronously using message queues
- **Generate** thumbnails in three sizes (150x150, 400x400, 800x800)
- **Monitor** everything with Datadog APM, metrics, and logs
- **Scale** workers independently for high throughput

## 🏗️ Architecture

```
┌─────────┐      ┌─────────────┐      ┌────────────┐      ┌─────────────┐
│  User   │─────▶│  API        │─────▶│  Pub/Sub   │─────▶│   Worker    │
│         │      │  (FastAPI)  │      │  Emulator  │      │  (Python)   │
└─────────┘      └─────────────┘      └────────────┘      └─────────────┘
                        │                                          │
                        │                                          ▼
                        │                                   ┌─────────────┐
                        └──────────────────────────────────▶│ PostgreSQL  │
                                                            │   + Files   │
                                                            └─────────────┘
                              ┌──────────────────┐
                              │  Datadog Agent   │◀──── All Services
                              │  (APM + Metrics) │
                              └──────────────────┘
```

**Components:**

- **API Service** (FastAPI) - Handles image uploads and thumbnail downloads
- **Worker Service** (Python) - Processes images and generates thumbnails
- **PostgreSQL** - Stores image metadata and processing status
- **Google Pub/Sub Emulator** - Message queue for async processing
- **Datadog Agent** - Complete observability (APM, custom metrics, logs)
- **Shared Storage** - Volume for original images and generated thumbnails

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Datadog account (get your API key from https://app.datadoghq.com/)

### Setup

1. **Run the setup script:**
```bash
./scripts/setup.sh
```

This will:
- Create `.env` file from template
- Set up storage directories
- Build and start all services

2. **Configure Datadog (optional but recommended):**

Edit `.env` and add your Datadog API key:
```bash
DD_API_KEY=your_actual_api_key_here
DD_SITE=datadoghq.eu  # or datadoghq.com for US
```

Restart the Datadog agent:
```bash
docker-compose restart datadog-agent
```

3. **Test the pipeline:**
```bash
./scripts/test_pipeline.sh
```

This will upload a test image, wait for processing, and download all thumbnail sizes.

## 📊 Monitoring with Datadog

### What's Monitored

#### APM Traces
- HTTP requests (FastAPI endpoints)
- Database queries (SQLAlchemy)
- Pub/Sub message publishing
- Image processing tasks
- Full distributed tracing across services

#### Custom Metrics
- `image.upload.count` - Upload success/failure rates
- `image.upload.size_bytes` - Distribution of uploaded image sizes
- `thumbnail.download.count` - Download requests by size
- `thumbnail.generation.time` - Processing time per thumbnail size
- `worker.process.count` - Worker success/failure rates
- `worker.process.total_time` - End-to-end processing duration

#### Logs
- Container logs with trace correlation
- Application logs from API and Worker
- Error tracking and stack traces

### Viewing Your Data

1. Go to **https://app.datadoghq.eu** (or `.com` for US)
2. Navigate to:
   - **APM** → **Services** - See `image-api` and `image-worker`
   - **Metrics** → **Explorer** - Search for `image.*` or `worker.*`
   - **Logs** → **Live Tail** - Filter by `service:image-api` or `env:prod`

### Key Dashboards to Create

- **Processing Pipeline Health** - Upload rate, success rate, queue depth
- **Performance Metrics** - P50/P95/P99 latency, processing times
- **Error Tracking** - Failed uploads, processing errors, retries
- **Resource Utilization** - CPU, memory, database connections

## 🛠️ Development

### Project Structure

```
image-thumbnail-generator/
├── api/                      # FastAPI service
│   ├── app.py               # Main application
│   ├── routes/              # API endpoints
│   │   └── images.py        # Image upload/download
│   ├── models/              # Pydantic schemas
│   ├── storage/             # File handling
│   └── requirements.txt
├── worker/                   # Processing service
│   ├── worker.py            # Main worker loop
│   ├── processors/          # Image processing logic
│   │   └── image_processor.py
│   └── requirements.txt
├── shared/                   # Shared code
│   ├── config.py            # Configuration
│   ├── database.py          # SQLAlchemy models
│   ├── pubsub_client.py     # Pub/Sub wrapper
│   └── metrics.py           # Datadog metrics
├── scripts/                  # Helper scripts
│   ├── setup.sh             # Initial setup
│   └── test_pipeline.sh     # End-to-end test
├── storage/                  # File storage (gitignored)
│   ├── uploads/             # Original images
│   └── thumbnails/          # Generated thumbnails
├── docker-compose.yml        # Service orchestration
├── .env.example             # Environment template
├── DATADOG_SETUP.md         # Datadog configuration guide
└── README.md                # This file
```

### Running Locally

**Start all services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker logs image-api -f
docker logs image-worker -f
docker logs datadog-agent -f
```

**Stop services:**
```bash
docker-compose down
```

**Rebuild after changes:**
```bash
docker-compose up --build -d
```

### Environment Variables

Key configuration in `.env`:

```bash
# Database
POSTGRES_USER=imageprocessor
POSTGRES_PASSWORD=imageprocessor123
POSTGRES_DB=image_processing

# Pub/Sub
PUBSUB_PROJECT_ID=image-thumbnail-project
PUBSUB_TOPIC=image-processing-tasks

# API
API_PORT=8000

# Datadog
DD_API_KEY=your_api_key_here
DD_SITE=datadoghq.eu
DD_ENV=prod
DD_TRACE_ENABLED=true
```

## 📝 API Reference

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "image-api",
  "database": "healthy",
  "pubsub": "healthy"
}
```

### Upload Image
```bash
POST /api/images
Content-Type: multipart/form-data

curl -X POST -F "file=@image.jpg" http://localhost:8000/api/images

Response:
{
  "id": "uuid",
  "filename": "image.jpg",
  "status": "uploaded",
  "size_bytes": 87272,
  "uploaded_at": "2025-11-11T09:00:52.357309",
  "message": "Image uploaded successfully and queued for processing"
}
```

### Download Thumbnail
```bash
GET /api/images/{id}/{size}

curl http://localhost:8000/api/images/{id}/small -o thumbnail-small.jpg

Sizes: small (150x150) | medium (400x400) | large (800x800)
```

## 🧪 Testing

### Automated Test Pipeline

Run the complete end-to-end test:
```bash
./scripts/test_pipeline.sh
```

This test:
1. Checks API health
2. Uploads a test image
3. Waits for processing
4. Downloads all thumbnail sizes
5. Verifies file sizes
6. Generates traces and metrics in Datadog

### Manual Testing

**Upload an image:**
```bash
curl -X POST \
  -F "file=@your-image.jpg" \
  http://localhost:8000/api/images
```

**Download thumbnails:**
```bash
# Get the image ID from upload response
IMAGE_ID="your-image-id"

curl http://localhost:8000/api/images/$IMAGE_ID/small -o small.jpg
curl http://localhost:8000/api/images/$IMAGE_ID/medium -o medium.jpg
curl http://localhost:8000/api/images/$IMAGE_ID/large -o large.jpg
```

## 🎓 Learning Outcomes

This project demonstrates:

### Distributed Systems
- ✅ Microservices architecture
- ✅ Asynchronous message processing
- ✅ Service decoupling with message queues
- ✅ Horizontal scaling patterns

### Observability
- ✅ Application Performance Monitoring (APM)
- ✅ Custom business metrics
- ✅ Distributed tracing
- ✅ Log aggregation and correlation
- ✅ Real-time monitoring and alerting

### Best Practices
- ✅ Docker containerization
- ✅ Environment-based configuration
- ✅ RESTful API design
- ✅ Database migrations and ORM usage
- ✅ Error handling and retry logic
- ✅ Health checks and readiness probes

**Built with ❤️ for learning observability and monitoring with Datadog**
