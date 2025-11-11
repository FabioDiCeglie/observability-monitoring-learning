import os
from ddtrace import tracer
from datadog import initialize, statsd

_metrics_initialized = False

def init_metrics():
    global _metrics_initialized
    
    if _metrics_initialized:
        return
    
    dd_trace_enabled = os.getenv("DD_TRACE_ENABLED", "false").lower() == "true"
    
    if not dd_trace_enabled:
        return
    
    options = {
        'statsd_host': os.getenv("DD_AGENT_HOST", "datadog-agent"),
        'statsd_port': 8125,
    }
    initialize(**options)
    _metrics_initialized = True


def increment_counter(metric_name: str, value: int = 1, tags: list = None):
    if not _metrics_initialized:
        return
    statsd.increment(metric_name, value=value, tags=tags or [])


def record_gauge(metric_name: str, value: float, tags: list = None):
    if not _metrics_initialized:
        return
    statsd.gauge(metric_name, value, tags=tags or [])


def record_histogram(metric_name: str, value: float, tags: list = None):
    if not _metrics_initialized:
        return
    statsd.histogram(metric_name, value, tags=tags or [])


def record_timing(metric_name: str, value: float, tags: list = None):
    if not _metrics_initialized:
        return
    statsd.timing(metric_name, value, tags=tags or [])

