# 📊 Observability & Monitoring Learning Hub

A comprehensive collection of hands-on projects for learning modern observability and monitoring practices. This repository contains multiple projects showcasing different monitoring tools and techniques including DataDog, OpenTelemetry, and distributed tracing.

## 🎯 Overview

This repository is designed as a learning resource for me to understand and implement observability. Each project demonstrates different aspects of monitoring, from basic metrics collection to advanced distributed tracing.

## 🚀 Projects

### 1. 🖼️ [Image Thumbnail Generator](./image-thumbnail-generator/)
**A distributed image processing system with complete DataDog observability**

Upload images through a REST API and automatically generate thumbnails in multiple sizes using asynchronous message-driven processing. This project demonstrates how to build, monitor, and trace a real-world microservices architecture where an API service handles uploads, publishes messages to a queue, and worker services process images independently.

- **Technology Stack**: FastAPI, Python Worker, PostgreSQL, Google Pub/Sub, DataDog APM
- **Learning Focus**: Distributed tracing, async processing, microservices monitoring, custom metrics
- **Key Features**:
  - Asynchronous message-driven architecture with Pub/Sub
  - Multi-size thumbnail generation (150px, 400px, 800px)
  - End-to-end distributed tracing across API and worker services
  - Custom business metrics (processing time, success rates, image sizes)
  - Scalable worker pool design for high throughput
  - Complete APM integration with trace correlation
  - Real-world production patterns with health checks and error handling

### 2. 🐕 [DataDog Sandbox](./datadog-sandbox-project/)
**A complete DataDog monitoring environment with Docker Compose**

A beginner-friendly playground for learning DataDog fundamentals. Spin up a full-stack application with Flask API, PostgreSQL database, and Nginx proxy, then explore monitoring with pre-built endpoints that simulate real-world scenarios like slow responses, errors, and high CPU load. Perfect for getting your hands dirty with metrics, dashboards, and alerts.

- **Technology Stack**: Flask, PostgreSQL, Nginx, DataDog Agent
- **Learning Focus**: Basic monitoring setup, custom metrics, dashboards, agent configuration
- **Key Features**:
  - Multi-container application monitoring out of the box
  - Database connection and performance tracking
  - Built-in endpoints for testing (health, slow response, errors, load)
  - System metrics collection (CPU, memory, disk)
  - Ready-to-use monitoring setup for experimentation

### 3. 🔗 [URL Shortener with DataDog](./url-shortener-project/)
**Production-ready URL shortener with comprehensive monitoring**

Build and monitor a fully functional URL shortener service that converts long URLs into short, shareable links. This project demonstrates how to track both business metrics (URLs created, redirect success rates) and technical metrics (response times, error rates) in a production-ready application. Includes custom DataDog dashboards and a complete REST API alongside a web interface.

- **Technology Stack**: Flask, DataDog, Docker
- **Learning Focus**: Business metrics, performance monitoring, production observability, KPI tracking
- **Key Features**:
  - Full-featured URL shortening with web UI and REST API
  - Business KPI tracking (creation rates, access patterns, total URLs)
  - Performance monitoring (response times, request rates)
  - Error tracking and validation monitoring
  - Custom DataDog dashboards with detailed setup guide
  - File-based persistent storage

### 4. 🔍 [OpenTelemetry Tracing](./opentelemetry/)
**Distributed tracing with OpenTelemetry and multiple exporters**

Explore the vendor-neutral OpenTelemetry standard with a multi-tier Node.js application that demonstrates distributed tracing. Watch requests flow through multiple service tiers (frontend → middle-tier → backend) and visualize the complete trace in Zipkin while exporting metrics to Prometheus. Learn how auto-instrumentation captures HTTP calls, database queries, and custom spans without manual code changes.

- **Technology Stack**: Node.js, Express, OpenTelemetry, Prometheus, Zipkin
- **Learning Focus**: Distributed tracing, OpenTelemetry instrumentation, trace analysis, vendor-neutral observability
- **Key Features**:
  - Auto-instrumentation for Express and HTTP clients
  - Multi-tier application architecture (3 levels of service calls)
  - Prometheus metrics exporter for time-series data
  - Zipkin integration for visual trace analysis
  - Request flow visualization across service boundaries
  - Zero-code instrumentation setup

## 🛠️ Prerequisites

- **Docker & Docker Compose** - For containerized environments
- **DataDog Account** - Free tier available for learning
- **Node.js** - For the OpenTelemetry project
- **Basic understanding of**:
  - HTTP/REST APIs
  - Docker concepts
  - Basic monitoring concepts

## 🔧 Common Setup

### DataDog Configuration
Most projects require a DataDog API key. Get yours from:
1. Sign up at [DataDog](https://www.datadoghq.com/)
2. Navigate to Organization Settings → API Keys
3. Create a new API key
4. Copy the key to your project's `.env` file

### Environment Variables Template
```bash
# DataDog Configuration
DD_API_KEY=your_datadog_api_key_here
DD_SITE=datadoghq.com  # or datadoghq.eu for EU
DD_ENV=development
DD_VERSION=1.0.0

# Application specific variables
# (see individual project README files)
```

**Happy Monitoring!** 📈