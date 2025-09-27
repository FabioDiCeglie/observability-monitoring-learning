# 📊 DataDog Dashboard Setup Guide

## 🚀 Quick Setup

1. **Start your application:**
   ```bash
   cp env.example .env
   # Add your DD_API_KEY to .env
   docker-compose up --build
   ```

2. **Generate some test data:**
   ```bash
   # Create URLs via API
   curl -X POST http://localhost:8080/shorten -H "Content-Type: application/json" -d '{"url": "https://www.google.com"}'
   curl -X POST http://localhost:8080/shorten -H "Content-Type: application/json" -d '{"url": "https://www.github.com"}'
   curl -X POST http://localhost:8080/shorten -H "Content-Type: application/json" -d '{"url": "https://www.stackoverflow.com"}'

   # Create URLs via web interface
   curl -X POST http://localhost:8080/shorten -d "url=https://www.reddit.com"
   curl -X POST http://localhost:8080/shorten -d "url=https://www.youtube.com"

   # Access some URLs (replace with actual short codes from responses)
   curl -L http://localhost:8080/abc123
   curl -L http://localhost:8080/def456

   # Test some 404s
   curl http://localhost:8080/nonexistent
   curl http://localhost:8080/invalid

   # Check stats
   curl http://localhost:8080/stats
   ```

---

## 📊 Production Dashboard: "URL Shortener Overview"

### **Create New Dashboard**
1. Go to **Dashboards** → **New Dashboard**
2. Name: **"URL Shortener - Production Overview"**
3. Description: **"Production monitoring for URL shortener service"**
4. **Time range:** Last 4 hours

### **Row 1: Key Performance Indicators (3 widgets)**

#### **Widget 1: Request Rate**
- **Widget Type:** Query Value (Big Number)
- **Title:** "Requests/min"
- **Metric Selection:**
  - **Metric:** Search and select `url_shortener.requests.count`
  - **From:** `*` (all sources)
  - **Aggregation:** `sum`
- **Display:** Rate per minute
- **Color:** Blue

#### **Widget 2: Average Response Time**
- **Widget Type:** Query Value (Big Number)
- **Title:** "Avg Response Time"
- **Metric Selection:**
  - **Metric:** Search and select `url_shortener.response_time.avg`
  - **From:** `*` (all sources)
  - **Aggregation:** `avg` (or leave default)
- **Display:** Milliseconds
- **Conditional Formatting:** Green (< 100ms), Orange (> 500ms)

#### **Widget 3: Error Rate**
- **Widget Type:** Query Value (Big Number)
- **Title:** "Error Rate %"
- **Metric Selection (Formula):**
  - Click **"Advanced"** → **"Formula"**
  - **Query A:** `url_shortener.errors` -> `count` -> `sum`
  - **Query B:** `url_shortener.responses` -> `count` -> `sum`
  - **Formula:** `(a / b) * 100`
- **Display:** Percentage
- **Conditional Formatting:** Red (if > 1%)

### **Row 2: Business Metrics (3 widgets)**

#### **Widget 4: URLs Created**
- **Widget Type:** Timeseries
- **Title:** "URLs Created Over Time"
- **Metric Selection:**
  - **Metric:** Search and select `url_shortener.urls.created`
  - **From:** `*` (all sources)
  - **Aggregation:** `sum`
  - **Function:** Click "Advanced" → Select `as_count()`
- **Display:** Line chart

#### **Widget 5: URL Accesses**
- **Widget Type:** Timeseries  
- **Title:** "URL Redirections"
- **Multiple Queries:**
  - **Query A (Success):**
    - **Metric:** `url_shortener.urls.accessed`
    - **From:** `status:success`
    - **Aggregation:** `sum`
    - **Color:** Green
  - **Query B (404s):**
    - **Metric:** `url_shortener.urls.accessed`
    - **From:** `status:not_found`
    - **Aggregation:** `sum`
    - **Color:** Red
- **Display:** Line chart

#### **Widget 6: Total URLs Stored**
- **Widget Type:** Query Value
- **Title:** "Total URLs"
- **Metric Selection:**
  - **Metric:** Search and select `url_shortener.urls.total`
  - **From:** `*` (all sources)
  - **Aggregation:** `max`
- **Display:** Number

### **Row 3: Performance & Health (2 widgets)**

#### **Widget 7: Response Time by Endpoint**
- **Widget Type:** Timeseries
- **Title:** "Response Time by Endpoint"
- **Metric Selection:**
  - **Metric:** Search and select `url_shortener.response_time.avg`
  - **From:** `*` (all sources)
  - **Aggregation:** `avg`
  - **Group by:** Select `endpoint` in the "Group by" field
- **Display:** Line chart
- **Legend:** Show endpoint names

#### **Widget 8: HTTP Status Codes**
- **Widget Type:** Stacked Bar
- **Title:** "Response Status Distribution"
- **Metric Selection:**
  - **Metric:** Search and select `url_shortener.responses.count`
  - **From:** `*` (all sources)
  - **Aggregation:** `sum`
  - **Group by:** Select `status` in the "Group by" field
- **Display:** Stacked percentage
- **Colors:** Green (2xx), Orange (3xx), Red (4xx/5xx)

Happy monitoring! 📈
