import os
import time
import random
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

@app.route('/api/hello', methods=['GET'])
def hello():
    """Simple hello endpoint"""
    return jsonify({
        'message': 'Hello from Flask API!',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/db-metrics', methods=['GET'])
def get_db_metrics():
    """Get metrics from database - simple database operation"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        with conn.cursor() as cur:
            # Get recent metrics
            cur.execute("""
                SELECT metric_name, metric_value, timestamp 
                FROM simple_metrics 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            metrics = cur.fetchall()
            
            # Get count for monitoring
            cur.execute("SELECT COUNT(*) as total FROM simple_metrics")
            total_count = cur.fetchone()['total']
        
        conn.close()
        
        # Send database query metrics to Datadog
        statsd.increment('flask_app.database.queries.count', tags=['operation:select'])
        statsd.gauge('flask_app.database.metrics.total', total_count)
        
        return jsonify({
            'metrics': [dict(row) for row in metrics],
            'total_count': total_count,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        statsd.increment('flask_app.database.errors.count', tags=['operation:select'])
        return jsonify({'error': 'Database query failed'}), 500

@app.route('/api/add-metric', methods=['POST'])
def add_metric():
    """Add a new metric to database - simple insert operation"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'value' not in data:
            return jsonify({'error': 'name and value are required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO simple_metrics (metric_name, metric_value) VALUES (%s, %s) RETURNING id",
                (data['name'], float(data['value']))
            )
            new_id = cur.fetchone()['id']
        
        conn.commit()
        conn.close()
        
        # Send database insert metrics to Datadog
        statsd.increment('flask_app.database.queries.count', tags=['operation:insert'])
        statsd.increment('flask_app.database.metrics.created')
        
        return jsonify({
            'id': new_id,
            'message': 'Metric added successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Database insert failed: {e}")
        statsd.increment('flask_app.database.errors.count', tags=['operation:insert'])
        return jsonify({'error': 'Database insert failed'}), 500

@app.route('/api/metrics', methods=['GET'])
def custom_metrics():
    """Endpoint to demonstrate custom metrics"""
    
    # Simulate some business metrics
    active_users = random.randint(50, 200)
    cpu_usage = random.uniform(10, 90)
    memory_usage = random.uniform(30, 80)
    
    # Send custom metrics to Datadog
    statsd.gauge('business.active_users', active_users)
    statsd.gauge('system.cpu_usage', cpu_usage)
    statsd.gauge('system.memory_usage', memory_usage)
    
    metrics_data = {
        'active_users': active_users,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(metrics_data)

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