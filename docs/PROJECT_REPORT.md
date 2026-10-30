# Project Report: Complete Observability System (Metrics, Logs & Traces)

**Elevate Labs DevOps Internship (2 Weeks) — Ministry of MSME, Govt. of India**
**Project Selection:** Project #3 — Complete Observability System
**Deliverable File:** [`docs/PROJECT_REPORT.pdf`](PROJECT_REPORT.pdf) (Exact 2-Page Submission PDF)

---

## 1. Abstract

Modern cloud-native architectures rely on microservices that communicate asynchronously across distributed networks. While traditional infrastructure monitoring answers whether a host is reachable, it fails to diagnose the root causes of latency bottlenecks, intermittent failures, and complex distributed dependencies.

This project delivers an end-to-end, production-ready Observability Minimum Viable Product (MVP) implementing the **Three Pillars of Observability**: time-series metrics, centralized log streams, and distributed request tracing. By integrating **Prometheus, Grafana Loki, Promtail, Jaeger,** and **Grafana** with an instrumented Python Flask microservice, the solution enables full-lifecycle telemetry correlation from a single unified Grafana dashboard deployed declaratively via Docker Compose.

---

## 2. Introduction

Site Reliability Engineering (SRE) defines observability as the ability to infer internal system states purely from its external outputs. When an incident occurs in production, operators must rapidly navigate between aggregate symptoms (metrics), historical execution events (logs), and distributed cross-service journeys (traces).

This project builds an automated observability ecosystem designed to eliminate monitoring silos. A realistic microservice simulates compute tasks, database latency, and unhandled server errors, outputting correlated telemetry with OpenTelemetry context injection (Trace IDs and Span IDs) directly into the telemetry pipeline.

---

## 3. Tools Used

| Tool / Technology          | Version / Role                  | Purpose in Architecture                                                                                                                   |
| :------------------------- | :------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------- |
| **Prometheus**             | v2.52.0 (Metrics Engine)        | Periodically scrapes `/metrics` at 5s intervals; records request throughput, HTTP error rates, and latency histograms.                    |
| **Grafana Loki**           | v3.0.0 (Log Aggregator)         | Ingests and stores metadata-indexed container logs in TSDB chunks without the overhead of full-text indexing.                             |
| **Promtail**               | v3.0.0 (Log Shipper)            | Discovers running containers via the Docker daemon socket (`/var/run/docker.sock`) and ships stdout streams to Loki.                      |
| **Jaeger**                 | v1.57 (Distributed Tracing)     | All-in-One collector with OTLP gRPC endpoint (port 4317); provides waterfall call graphs and request latency breakdowns.                  |
| **Grafana**                | v10.4.2 (Unified Visualization) | Pre-configured dashboard automatically visualizing metrics, logs, and trace links side-by-side with zero manual UI setup.                 |
| **OpenTelemetry & Python** | OTel SDK 1.25 / Python 3.11     | Instruments Flask requests, generates custom span operations (`compute_job`, `slow_database_query`), and injects trace context into logs. |
| **Docker Compose**         | v2.20+ (Orchestration)          | Declaratively manages container lifecycles, health dependencies, networking, and volume provisioning with a single command.               |

---

## 4. Steps Involved in Building the Project

1. **Application Design & Telemetry Instrumentation:**
   - Developed a Python Flask microservice (`app/app.py`) providing simulated production workloads (`/work`, `/slow`, `/error`).
   - Integrated OpenTelemetry SDK with `OTLPSpanExporter` routing trace spans to Jaeger over gRPC port `4317`.
   - Instrumented `prometheus_flask_exporter` to expose real-time time-series metrics at `/metrics`.
   - Configured dynamic logging record hooks to inject active `trace_id` and `span_id` into all application log statements.

2. **Decoupled Centralized Logging Pipeline:**
   - Established non-intrusive container logging where the application writes structured logs to standard stdout.
   - Configured Promtail (`promtail/promtail-config.yml`) to mount `/var/run/docker.sock`, inspect Docker metadata, and label logs by `container="flask-observability-app"`.
   - Configured Loki (`loki/loki-config.yml`) with 24-hour TSDB schemas for filesystem storage.

3. **Metrics Scrape Architecture:**
   - Created `prometheus/prometheus.yml` defining scrape intervals of 5 seconds targeting `flask-app:5000` via internal Docker DNS.

4. **Distributed Request Tracing:**
   - Enabled native OpenTelemetry protocol (`COLLECTOR_OTLP_ENABLED=true`) on the Jaeger All-in-One container.
   - Wrapped critical paths in spans to record execution phases (`compute_job` and simulated database queries).

5. **Automated Grafana Provisioning:**
   - Formatted YAML datasource declarations (`grafana/provisioning/datasources/datasources.yml`) specifying deterministic UIDs (`prometheus`, `loki`, `jaeger`).
   - Authored a declarative dashboard JSON model (`grafana/provisioning/dashboards/dashboard.json`) and provider definition (`dashboards.yml`) to render a four-quadrant unified view (Throughput, Latency, Logs, Traces).

6. **Orchestration & Verification:**
   - Unified all 6 services within `docker-compose.yml` with health checks, restart policies, and isolated bridge networking.
   - Created an automated synthetic traffic generator (`traffic-generator.sh`) to trigger and verify cross-pillar telemetry in real time.

---

## 5. Key Results & Observability Insights

- **Zero-Touch Provisioning:** Executing `docker compose up -d` brings up all 6 services with datasources and dashboards pre-wired in under 60 seconds.
- **Trace-to-Log Correlation:** High latency spikes detected on `/slow` (800ms–1500ms) can be traced from Jaeger's waterfall view directly to Loki logs using the matching 32-character hexadecimal Trace ID.
- **Root-Cause Analysis:** The Prometheus error rate panel highlights sudden 500 status codes on `/error`, while Loki filters (`{container="flask-observability-app"} |= "ERROR"`) immediately reveal the responsible stack trace.

---

## 6. Conclusion

This project successfully constructs an enterprise-grade observability architecture adhering to all Elevate Labs specifications. By unifying Prometheus metrics, Loki log streams, and Jaeger distributed traces into an automated Grafana dashboard, the system eliminates operational blind spots and drastically reduces Mean Time to Detection (MTTD) and Mean Time to Resolution (MTTR).
