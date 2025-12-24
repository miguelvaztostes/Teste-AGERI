# AGERI - Teste (Client API → Server API → External API)

Este projeto implementa duas APIs instrumentadas com **OpenTelemetry** (traces, logs e metrics), com **propagação de contexto** entre:

**client-api → server-api → API externa (jsonplaceholder)**

A telemetria é enviada via **OTLP** para um **OpenTelemetry Collector**, que:
- exporta **traces** para o **Jaeger**
- expõe **metrics** em formato Prometheus
- imprime **logs** em JSON no stdout do Collector (via exporter `debug`)

---

## ✅ Requisitos

- Docker + Docker Compose (Docker Desktop)
- Portas livres no host: `18080`, `18081`, `16686`, `9090`, `13133`, `8889`, `14317`, `14318`

---

## 🚀 Como rodar

Na raiz do projeto:

Teste-AGERI-main:
cd Teste-AGERI-main

```bash
docker compose up -d --build


Verifique containers:

docker ps

🌐 Endpoints
Client API

GET http://localhost:18080/getUsers
chama server-api → chama API externa

Server API

GET http://localhost:18081/users
chama API externa: https://jsonplaceholder.typicode.com/users

🔭 Observabilidade
Jaeger (Traces)

UI: http://localhost:16686

Procure pelos serviços:

client-api

server-api

Prometheus (Metrics)

UI: http://localhost:9090

Targets: http://localhost:9090/targets

O Prometheus faz scrape do endpoint de métricas do Collector:

http://otel-collector:8889/metrics (interno)

http://localhost:8889/metrics (host)

Health do Collector

http://localhost:13133/

✅ Teste rápido (gera tráfego + traces + metrics)

No navegador:

http://localhost:18080/getUsers

http://localhost:18081/users

Depois:

Veja traces no Jaeger:


Veja metrics no Prometheus


📊 Queries de exemplo (Prometheus)

Ver o que chegou do collector (geral)

{__name__=~".+"}


(vai vir muita coisa)

(C) Ver suas métricas custom (as APIs)

sum(rate(ageri_requests_total[1m])) by (route, service)


(D) Ver chamadas externas medidas no server-api

sum(rate(ageri_external_calls_total[1m])) by (host, method)


(E) Latência via buckets (se aparecer o histogram)

Você mostrou que apareceu *_duration_milliseconds_bucket, então:

{__name__=~".*duration.*bucket"}

📌 Portas usadas

client-api: 18080 → 8000

server-api: 18081 → 8000

Jaeger UI: 16686

Prometheus: 9090

Collector health: 13133

Collector metrics: 8889

OTLP gRPC: 14317 → 4317

OTLP HTTP: 14318 → 4318

👤 Autor

Miguel Vaz
