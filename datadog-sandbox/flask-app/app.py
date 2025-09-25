import os
import time
import random
import psutil
from datetime import datetime
from flask import Flask, request, jsonify
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datadog import initialize, statsd
from ddtrace import tracer, patch_all

# Initialize Datadog tracing
patch_all()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Datadog
options = {
    'statsd_host': os.getenv('DD_AGENT_HOST', 'datadog-agent'),
    'statsd_port': 8125,
}
initialize(**options)

# Database connection helper
def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

# Initialize database (create simple table)
def init_db():
    """Create simple metrics table if it doesn't exist"""
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS simple_metrics (
                        id SERIAL PRIMARY KEY,
                        metric_name VARCHAR(100) NOT NULL,
                        metric_value FLOAT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert some sample data if table is empty
                cur.execute("SELECT COUNT(*) FROM simple_metrics")
                count = cur.fetchone()['count']
                
                if count == 0:
                    sample_data = [
                        ('cpu_usage', 45.2),
                        ('memory_usage', 67.8),
                        ('disk_usage', 23.4)
                    ]
                    for name, value in sample_data:
                        cur.execute(
                            "INSERT INTO simple_metrics (metric_name, metric_value) VALUES (%s, %s)",
                            (name, value)
                        )
                
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

# Initialize database on startup
init_db()

# Middleware for request logging and metrics
@app.before_request
def before_request():
    request.start_time = time.time()
    
    # Custom metric: increment request counter
    statsd.increment('flask_app.requests.count', 
                    tags=[f'endpoint:{request.endpoint}', f'method:{request.method}'])

@app.after_request
def after_request(response):
    # Calculate response time
    response_time = time.time() - request.start_time
    
    # Log request
    logger.info(f"{request.method} {request.path} - {response.status_code} - {response_time:.3f}s")
    
    # Send metrics to Datadog
    statsd.histogram('flask_app.response_time', response_time,
                    tags=[f'endpoint:{request.endpoint}', f'method:{request.method}', f'status:{response.status_code}'])
    
    statsd.increment('flask_app.responses.count',
                    tags=[f'endpoint:{request.endpoint}', f'method:{request.method}', f'status:{response.status_code}'])
    
    return response

# Simple API Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with database check"""
    db_status = 'healthy'
    
    # Simple database health check
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
            conn.close()
        else:
            db_status = 'unhealthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)[:50]}'
        logger.error(f"Database health check failed: {e}")
    
    overall_status = 'healthy' if db_status == 'healthy' else 'degraded'
    
    health_data = {
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'flask-api',
        'database': db_status
    }
    
    status_code = 200 if overall_status == 'healthy' else 503
    return jsonify(health_data), status_code

@app.route('/api/slow', methods=['GET'])
def slow_endpoint():
    """Simulate a slow endpoint for testing monitoring"""
    delay = random.uniform(1, 3)  # 1-3 second delay
    time.sleep(delay)
    
    statsd.histogram('flask_app.slow_endpoint.duration', delay)
    
    return jsonify({
        'message': f'This endpoint took {delay:.2f} seconds',
        'delay': delay,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/error', methods=['GET'])
def error_endpoint():
    """Simulate an error for testing monitoring"""
    error_types = ['timeout', 'validation', 'network', 'processing']
    error_type = random.choice(error_types)
    
    statsd.increment('flask_app.simulated_errors.count', tags=[f'error_type:{error_type}'])
    
    logger.error(f"Simulated {error_type} error")
    
    return jsonify({
        'error': f'Simulated {error_type} error',
        'error_type': error_type,
        'timestamp': datetime.utcnow().isoformat()
    }), 500

@app.route('/api/load', methods=['GET'])
def load_test():
    """Generate some CPU load for testing"""
    operations = int(request.args.get('operations', 1000))
    
    start_time = time.time()
    
    # Simulate CPU work
    result = 0
    for i in range(operations):
        result += sum(range(100))
    
    duration = time.time() - start_time
    statsd.histogram('flask_app.load_test.duration', duration, tags=[f'operations:{operations}'])
    
    return jsonify({
        'operations': operations,
        'duration': f'{duration:.3f}s',
        'result': result,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/system-metrics', methods=['GET'])
def system_metrics():
    """Get system metrics from inside the container
    
    NOTE: This endpoint is specifically needed for Docker Desktop environments
    where the Datadog agent cannot directly access host-level container metrics
    due to the Linux VM layer. We use psutil to get metrics from within the 
    container and send them directly to Datadog as custom metrics.
    """
    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Get memory usage
        memory = psutil.virtual_memory()
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        
        # Send metrics to Datadog
        statsd.gauge('flask_app.system.cpu_percent', cpu_percent, tags=['container:flask-api'])
        statsd.gauge('flask_app.system.memory_percent', memory.percent, tags=['container:flask-api'])
        statsd.gauge('flask_app.system.memory_used_mb', memory.used / 1024 / 1024, tags=['container:flask-api'])
        statsd.gauge('flask_app.system.disk_percent', disk.percent, tags=['container:flask-api'])
        
        metrics_data = {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memory': {
                'percent': memory.percent,
                'used_mb': round(memory.used / 1024 / 1024, 2),
                'available_mb': round(memory.available / 1024 / 1024, 2),
                'total_mb': round(memory.total / 1024 / 1024, 2)
            },
            'disk': {
                'percent': disk.percent,
                'used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                'free_gb': round(disk.free / 1024 / 1024 / 1024, 2)
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return jsonify({'error': 'Failed to get system metrics'}), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    statsd.increment('flask_app.errors.404')
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    statsd.increment('flask_app.errors.500')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)