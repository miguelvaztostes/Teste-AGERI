import os
import logging
import requests
from fastapi import FastAPI

from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .telemetry import setup_otel

SERVICE = os.getenv("OTEL_SERVICE_NAME", "server-api")
setup_otel(SERVICE)

logger = logging.getLogger("server-api")
app = FastAPI(title="server-api")
FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer("server-api")
meter = metrics.get_meter("server-api")
req_counter = meter.create_counter("ageri_requests_total")
ext_counter = meter.create_counter("ageri_external_calls_total")


@app.get("/users")
def get_users():
    url = os.getenv("EXTERNAL_USERS_URL", "https://jsonplaceholder.typicode.com/users")

    req_counter.add(1, {"route": "/users", "service": "server-api"})
    with tracer.start_as_current_span("server-api /users"):
        logger.info("Fetching external users", extra={"external_url": url})

        with tracer.start_as_current_span("HTTP GET jsonplaceholder"):
            r = requests.get(url, timeout=10)
            ext_counter.add(1, {"host": "jsonplaceholder.typicode.com", "method": "GET"})
            r.raise_for_status()

        return r.json()
