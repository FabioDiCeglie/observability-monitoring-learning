'use strict';

const { diag, DiagConsoleLogger, DiagLogLevel } = require('@opentelemetry/api');
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.ERROR);

const sdk = new NodeSDK({
  traceExporter: new ZipkinExporter({
    serviceName: 'opentelemetry-demo',
  }),
  instrumentations: [getNodeAutoInstrumentations({
    '@opentelemetry/instrumentation-fs': {
      enabled: false,
    },
  })],
});

sdk.start();