import os
import logging
import requests
from fastapi import FastAPI

from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .telemetry import setup_otel

SERVICE = os.getenv("OTEL_SERVICE_NAME", "client-api")
setup_otel(SERVICE)

logger = logging.getLogger("client-api")
app = FastAPI(title="client-api")
FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer("client-api")
meter = metrics.get_meter("client-api")
req_counter = meter.create_counter("ageri_requests_total")


@app.get("/getUsers")
def get_users():
    server_url = os.getenv("SERVER_API_URL", "http://server-api:8000")
    url = f"{server_url}/users"

    req_counter.add(1, {"route": "/getUsers", "service": "client-api"})
    with tracer.start_as_current_span("client-api /getUsers"):
        logger.info("Calling server-api", extra={"server_url": url})
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
