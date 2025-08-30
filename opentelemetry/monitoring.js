'use strict';

// const { DiagConsoleLogger, DiagLogLevel, diag } = require('@opentelemetry/api');
const { MeterProvider } = require('@opentelemetry/sdk-metrics');
const { PrometheusExporter } = require('@opentelemetry/exporter-prometheus');

// Optional and only needed to see the internal diagnostic logging (during development)
// diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);

const { endpoint, port } = PrometheusExporter.DEFAULT_OPTIONS;

const exporter = new PrometheusExporter({}, () => {
  console.log(
    `prometheus scrape endpoint: http://localhost:${port}${endpoint}`,
  );
});

// Creates MeterProvider and installs the exporter as a MetricReader
const meterProvider = new MeterProvider({
  readers: [exporter],
});
const meter = meterProvider.getMeter('opentelemetry-demo');

// Creates metric instruments
const requestCounter = meter.createCounter('http_requests_total', {
  description: 'Count all incoming requests',
});

module.exports.countAllRequests = () => {
    return (req, res, next) => {
        // Record metrics with attributes
        requestCounter.add(1, {
            method: req.method,
            route: req.path,
        });
        next();
    }
};