# 📊 Observability & Monitoring Learning Hub

A comprehensive collection of hands-on projects for learning modern observability and monitoring practices. This repository contains multiple projects showcasing different monitoring tools and techniques including DataDog, OpenTelemetry, and distributed tracing.

## 🎯 Overview

This repository is designed as a learning resource for me to understand and implement observability. Each project demonstrates different aspects of monitoring, from basic metrics collection to advanced distributed tracing.

## 🚀 Projects

### 1. 🐕 [DataDog Sandbox](./datadog-sandbox-project/)
**A complete DataDog monitoring environment with Docker Compose**

- **Technology Stack**: Flask, PostgreSQL, Nginx, DataDog Agent
- **Learning Focus**: Basic monitoring setup, custom metrics, dashboards
- **Key Features**:
  - Multi-container application monitoring
  - Database performance tracking
  - Custom business metrics
  - Load testing endpoints
  - System metrics collection

### 2. 🔗 [URL Shortener with DataDog](./url-shortener-project/)
**Production-ready URL shortener with comprehensive monitoring**

- **Technology Stack**: Flask, DataDog, Docker
- **Learning Focus**: Business metrics, performance monitoring, production observability
- **Key Features**:
  - Real-world application monitoring
  - Business KPI tracking
  - Error rate monitoring
  - Response time analysis
  - Custom dashboards

### 3. 🔍 [OpenTelemetry Tracing](./opentelemetry/)
**Distributed tracing with OpenTelemetry and multiple exporters**

- **Technology Stack**: Node.js, Express, OpenTelemetry, Prometheus, Zipkin
- **Learning Focus**: Distributed tracing, OpenTelemetry instrumentation, trace analysis
- **Key Features**:
  - Auto-instrumentation setup
  - Multi-tier application tracing
  - Prometheus metrics export
  - Zipkin trace visualization
  - Request flow analysis

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