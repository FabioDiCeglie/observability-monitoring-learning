# Datadog Integration Guide 🐶

Complete guide for setting up and using Datadog observability in the Image Thumbnail Generator project.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Setup](#quick-setup)
- [What's Being Monitored](#whats-being-monitored)
- [Custom Metrics Reference](#custom-metrics-reference)
- [APM Traces](#apm-traces)

## Overview

This project uses Datadog for complete observability across the entire image processing pipeline. The integration includes:

- **APM (Application Performance Monitoring)** - Distributed tracing across services
- **Custom Metrics** - Business and performance metrics
- **Log Management** - Centralized logs with trace correlation
- **Infrastructure Monitoring** - Container and host metrics

## Quick Setup

### 1. Get Your Datadog Account

Sign up for a free trial at:
- **EU**: https://app.datadoghq.eu
- **US**: https://app.datadoghq.com

### 2. Get Your API Key

1. Log in to Datadog
2. Navigate to **Organization Settings** → **API Keys**
3. Copy your API key

### 3. Configure the Project

Edit `.env` file:

```bash
# Datadog Configuration
DD_API_KEY=your_actual_api_key_here
DD_SITE=datadoghq.eu  # or datadoghq.com for US
DD_ENV=prod
DD_TRACE_ENABLED=true
```

### 4. Restart Services

```bash
docker-compose down
docker-compose up -d
```

### 5. Generate Test Data

```bash
./scripts/test_pipeline.sh
```

### 6. View in Datadog

Wait 1-2 minutes, then check:
- **APM** → **Services**
- **Metrics** → **Explorer**
- **Logs** → **Live Tail**

## What's Being Monitored

### Services

Two main services are instrumented:

#### `image-api` (FastAPI)
- HTTP request/response times
- Database query performance
- Pub/Sub message publishing
- File upload/download operations

#### `image-worker` (Python)
- Message consumption from Pub/Sub
- Image processing duration
- Thumbnail generation times
- Database write operations

### Infrastructure

- Container CPU and memory usage
- PostgreSQL connection pool
- Disk I/O for storage operations
- Network traffic between services

## Custom Metrics Reference

### Upload Metrics

#### `image.upload.count`
Number of image uploads

**Type:** Counter  
**Tags:**
- `status:success` - Successful uploads
- `status:error` - Failed uploads

**Example Query:**
```
sum:image.upload.count{*} by {status}.as_count()
```

**Use Cases:**
- Monitor upload success rate
- Alert on high failure rates
- Track daily/hourly upload patterns

---

#### `image.upload.size_bytes`
Distribution of uploaded image file sizes

**Type:** Histogram  
**Unit:** Bytes

**Example Query:**
```
avg:image.upload.size_bytes{*}
p95:image.upload.size_bytes{*}
```

**Use Cases:**
- Understand typical image sizes
- Plan storage capacity
- Identify unusually large uploads

---

### Download Metrics

#### `thumbnail.download.count`
Number of thumbnail download requests

**Type:** Counter  
**Tags:**
- `status:success` - Successful downloads
- `status:error` - Failed downloads
- `reason:not_found` - Thumbnail doesn't exist
- `reason:invalid_size` - Invalid size parameter
- `reason:file_missing` - File deleted from disk
- `size:small` - 150x150 thumbnails
- `size:medium` - 400x400 thumbnails
- `size:large` - 800x800 thumbnails

**Example Queries:**
```
# Total downloads by size
sum:thumbnail.download.count{status:success} by {size}.as_count()

# Download success rate
sum:thumbnail.download.count{status:success}.as_count() / 
sum:thumbnail.download.count{*}.as_count() * 100
```

**Use Cases:**
- Monitor which thumbnail sizes are most popular
- Track download success rates
- Alert on high error rates

---

### Worker Processing Metrics

#### `worker.process.count`
Number of images processed by workers

**Type:** Counter  
**Tags:**
- `status:success` - Successfully processed
- `status:error` - Processing failed
- `reason:not_found` - Image not in database
- `reason:processing_failed` - Processing exception

**Example Query:**
```
sum:worker.process.count{*} by {status}.as_count()
```

**Use Cases:**
- Monitor worker health
- Track processing success rate
- Alert on processing failures

---

#### `worker.process.total_time`
End-to-end processing time per image (includes all thumbnails)

**Type:** Timing  
**Unit:** Milliseconds

**Example Query:**
```
avg:worker.process.total_time{*}
p95:worker.process.total_time{*}
p99:worker.process.total_time{*}
```

**Use Cases:**
- Monitor processing performance
- Identify slow processing times
- Optimize worker performance

---

#### `thumbnail.generation.time`
Time to generate a single thumbnail

**Type:** Timing  
**Unit:** Milliseconds  
**Tags:**
- `size:small`
- `size:medium`
- `size:large`

**Example Query:**
```
avg:thumbnail.generation.time{*} by {size}
```

**Use Cases:**
- Compare processing times by size
- Identify size-specific performance issues
- Optimize image processing algorithms

---

#### `thumbnail.size_bytes`
Distribution of generated thumbnail file sizes

**Type:** Histogram  
**Unit:** Bytes  
**Tags:**
- `size:small`
- `size:medium`
- `size:large`

**Example Query:**
```
avg:thumbnail.size_bytes{*} by {size}
```

**Use Cases:**
- Monitor compression efficiency
- Plan storage requirements
- Validate thumbnail generation quality

---

## APM Traces

### Trace Structure

Each image upload creates a distributed trace:

```
1. POST /api/images (image-api)
   ├─ Save file to disk
   ├─ INSERT INTO images (PostgreSQL)
   ├─ Publish message (Pub/Sub)
   └─ Return response

2. Consume message (image-worker)
   ├─ SELECT image from DB (PostgreSQL)
   ├─ Generate small thumbnail
   ├─ Generate medium thumbnail
   ├─ Generate large thumbnail
   ├─ INSERT thumbnails (PostgreSQL)
   └─ UPDATE image status (PostgreSQL)

3. GET /api/images/{id}/small (image-api)
   ├─ SELECT thumbnail from DB (PostgreSQL)
   └─ Return file
```

### Key Trace Metrics

#### `trace.fastapi.request.duration`
API request response times

**Service:** `image-api`  
**Resource:** Various endpoints

**Key Endpoints:**
- `POST /api/images` - Upload endpoint
- `GET /api/images/{id}/{size}` - Download endpoint
- `GET /health` - Health check

---

#### `trace.sqlalchemy.query`
Database query performance

**Service:** `image-api`, `image-worker`

**Common Queries:**
- Image INSERT operations
- Thumbnail SELECT queries
- Status UPDATE operations

---

#### `trace.pubsub.publish`
Message publishing latency

**Service:** `image-api`

**Metrics:**
- Time to publish message
- Message size
- Success/failure rate