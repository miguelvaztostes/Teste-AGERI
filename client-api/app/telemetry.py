import os
import logging
from pythonjsonlogger import jsonlogger

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter


def setup_otel(service_name: str):
    resource = Resource.create({"service.name": service_name})

    traces_ep = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "http://otel-collector:4318/v1/traces")
    tp = TracerProvider(resource=resource)
    tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=traces_ep)))
    trace.set_tracer_provider(tp)

    metrics_ep = os.getenv("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT", "http://otel-collector:4318/v1/metrics")
    reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=metrics_ep), export_interval_millis=5000)
    mp = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(mp)

    logs_ep = os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT", "otel-collector:4317")
    lp = LoggerProvider(resource=resource)
    lp.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=logs_ep, insecure=True)))

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    fmt = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "%(otelTraceID)s %(otelSpanID)s %(otelServiceName)s"
    )
    handler.setFormatter(fmt)
    root.handlers = [handler]

    LoggingInstrumentor().instrument(set_logging_format=False)

    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=lp)
    root.addHandler(otel_handler)

    RequestsInstrumentor().instrument()

    return {
        "tracer": trace.get_tracer(service_name),
        "meter": metrics.get_meter(service_name),
    }
