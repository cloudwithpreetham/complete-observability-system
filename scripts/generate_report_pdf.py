import base64
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PDF = ROOT / "docs" / "PROJECT_REPORT.pdf"


def find_browser() -> str:
    env_bin = os.environ.get("CHROME_BIN")
    if env_bin and Path(env_bin).exists():
        return env_bin

    for candidate in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        found = shutil.which(candidate)
        if found:
            return found

    windows_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in windows_paths:
        if Path(path).exists():
            return path

    raise FileNotFoundError("Chrome/Chromium executable not found. Set CHROME_BIN to its path.")


def img_data_uri(rel_path: str) -> str:
    path = ROOT / rel_path
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def build_html() -> str:
    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Complete Observability System — Project Report</title>
<style>
  @page {
    size: letter;
    margin: 0;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1e293b;
    background: #ffffff;
    font-size: 9pt;
    line-height: 1.42;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  code, pre {
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
  }

  .page {
    width: 8.5in;
    height: 11in;
    padding: 0.40in 0.52in 0.62in 0.52in;
    position: relative;
    overflow: hidden;
    page-break-after: always;
    background: #ffffff;
  }

  .page:last-child {
    page-break-after: auto;
  }

  /* Running Header (Pages 2-4) */
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 7.5pt;
    color: #64748b;
    padding-bottom: 6px;
    margin-bottom: 11px;
    border-bottom: 1px solid #cbd5e1;
  }

  .page-header .hdr-left {
    font-weight: 600;
    color: #334155;
    letter-spacing: 0.2px;
  }

  .page-header .hdr-right {
    color: #64748b;
  }

  /* Running Footer (All Pages) */
  .page-footer {
    position: absolute;
    left: 0.52in;
    right: 0.52in;
    bottom: 0.28in;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 7.5pt;
    color: #64748b;
    padding-top: 6px;
    border-top: 1px solid #cbd5e1;
  }

  /* Page 1 Hero Banner */
  .hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 68%, #1d4ed8 100%);
    color: #ffffff;
    border-radius: 8px;
    padding: 13px 18px 12px 18px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
  }

  .hero::after {
    content: "";
    position: absolute;
    right: -35px;
    top: -35px;
    width: 170px;
    height: 170px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
  }

  .hero-badge {
    display: inline-block;
    background: rgba(59, 130, 246, 0.28);
    border: 1px solid rgba(147, 197, 253, 0.45);
    color: #dbeafe;
    font-size: 6.8pt;
    font-weight: 700;
    letter-spacing: 0.7px;
    padding: 2px 8px;
    border-radius: 999px;
    margin-bottom: 5px;
    text-transform: uppercase;
  }

  .hero h1 {
    font-size: 18pt;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -0.3px;
    margin-bottom: 3px;
    color: #ffffff;
  }

  .hero .subtitle {
    font-size: 8.8pt;
    color: #cbd5e1;
    line-height: 1.32;
    max-width: 96%;
  }

  /* Metadata Strip */
  .meta-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 7px;
    margin-bottom: 9px;
  }

  .meta-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-top: 2.5px solid #2563eb;
    border-radius: 5px;
    padding: 5px 8px;
  }

  .meta-label {
    font-size: 6.7pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    font-weight: 700;
    margin-bottom: 1px;
  }

  .meta-val {
    font-size: 8.2pt;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.25;
  }

  .meta-sub {
    font-size: 7pt;
    color: #475569;
  }

  /* Section Headings */
  .sec-title {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 10.6pt;
    font-weight: 800;
    color: #0f172a;
    margin-top: 7px;
    margin-bottom: 5px;
    padding-bottom: 3px;
    border-bottom: 1.5px solid #e2e8f0;
  }

  .sec-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #2563eb;
    color: #ffffff;
    font-size: 7.4pt;
    font-weight: 700;
    width: 16px;
    height: 16px;
    border-radius: 4px;
    flex-shrink: 0;
  }

  p {
    margin-bottom: 5px;
    color: #334155;
    text-align: justify;
    font-size: 8.6pt;
    line-height: 1.38;
  }

  /* Three Pillars Cards */
  .pillars-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin: 5px 0 8px 0;
  }

  .pillar-card {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 7px 9px;
    background: #ffffff;
  }

  .pillar-card.metrics { border-top: 3px solid #059669; background: #f0fdf4; }
  .pillar-card.logs    { border-top: 3px solid #d97706; background: #fffbeb; }
  .pillar-card.traces  { border-top: 3px solid #0891b2; background: #ecfeff; }

  .pillar-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3px;
  }

  .pillar-title {
    font-size: 8.8pt;
    font-weight: 800;
    color: #0f172a;
  }

  .pillar-tag {
    font-size: 6.7pt;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 3px;
    background: rgba(15, 23, 42, 0.08);
    color: #1e293b;
  }

  .pillar-body {
    font-size: 7.7pt;
    line-height: 1.35;
    color: #334155;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 4px 0 6px 0;
    font-size: 7.5pt;
  }

  th {
    background: #0f172a;
    color: #f8fafc;
    text-align: left;
    font-weight: 700;
    padding: 4.5px 6px;
    font-size: 7.3pt;
    letter-spacing: 0.2px;
  }

  td {
    padding: 3.6px 6px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
    color: #1e293b;
    line-height: 1.28;
  }

  tr:nth-child(even) td {
    background: #f8fafc;
  }

  .mono {
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 7.2pt;
    background: #f1f5f9;
    padding: 1px 4px;
    border-radius: 3px;
    color: #0f172a;
  }

  .badge {
    display: inline-block;
    font-size: 6.8pt;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 3px;
  }

  .badge-green { background: #dcfce7; color: #166534; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .badge-red   { background: #fee2e2; color: #991b1b; }
  .badge-blue  { background: #dbeafe; color: #1e40af; }

  /* Architecture Figure */
  .arch-box {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background: #ffffff;
    padding: 6px 8px 4px 8px;
    text-align: center;
    margin-bottom: 6px;
  }

  .arch-box img {
    max-width: 100%;
    max-height: 2.15in;
    object-fit: contain;
  }

  .fig-caption {
    font-size: 7.1pt;
    color: #475569;
    margin-top: 3px;
    text-align: center;
  }

  .fig-caption strong {
    color: #0f172a;
  }

  /* Pipeline 3-column summary */
  .flow-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 7px;
    margin-bottom: 6px;
  }

  .flow-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 5px 7px;
    font-size: 7.25pt;
    line-height: 1.3;
    color: #334155;
  }

  .flow-box h4 {
    font-size: 7.8pt;
    color: #0f172a;
    margin-bottom: 2px;
    font-weight: 700;
  }

  /* Two-column split for Code + Explanation */
  .split-2 {
    display: grid;
    grid-template-columns: 1.12fr 0.88fr;
    gap: 9px;
    align-items: start;
    margin-top: 4px;
  }

  .code-panel {
    background: #0f172a;
    color: #e2e8f0;
    border-radius: 6px;
    padding: 7px 9px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 6.35pt;
    line-height: 1.32;
    white-space: pre;
    overflow: hidden;
    border: 1px solid #1e293b;
  }

  .code-title {
    font-family: 'Segoe UI', sans-serif;
    font-size: 7pt;
    font-weight: 700;
    color: #93c5fd;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
    border-bottom: 1px solid #334155;
    padding-bottom: 3px;
    white-space: normal;
  }

  .c-kw { color: #93c5fd; }
  .c-str { color: #86efac; }
  .c-cmt { color: #94a3b8; }

  /* Query Reference Grid */
  .query-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
    margin-bottom: 8px;
  }

  .query-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #2563eb;
    border-radius: 4px;
    padding: 5px 8px;
  }

  .query-card .q-title {
    font-size: 7.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 2px;
    display: flex;
    justify-content: space-between;
  }

  .query-card .q-src {
    font-size: 6.6pt;
    color: #2563eb;
    font-weight: 700;
  }

  .query-card pre {
    font-size: 6.8pt;
    background: #0f172a;
    color: #e2e8f0;
    padding: 3.5px 6px;
    border-radius: 3px;
    white-space: pre-wrap;
    word-break: break-all;
  }

  /* Screenshot Grids */
  .shot-grid-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 9px;
    margin-top: 5px;
  }

  .shot-card {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background: #ffffff;
    padding: 5px;
    display: flex;
    flex-direction: column;
  }

  .shot-frame {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 1.78in;
  }

  .shot-frame.dark {
    background: #0f172a;
    border-color: #1e293b;
  }

  .shot-frame img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }

  .shot-cap {
    font-size: 7.1pt;
    color: #334155;
    margin-top: 4px;
    line-height: 1.28;
  }

  .shot-cap strong {
    color: #0f172a;
  }

  /* Page 4 Large Correlation Shots */
  .shot-grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 9px;
  }

  .shot-frame-lg {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 4px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 1.88in;
  }

  .shot-frame-lg img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  /* Findings & Hardening Two-Col */
  .insights-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 8px;
  }

  .panel-box {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 10px;
    background: #f8fafc;
  }

  .panel-box.warn {
    background: #fffbeb;
    border-color: #fde68a;
  }

  .panel-box h4 {
    font-size: 8.3pt;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  ul.compact {
    padding-left: 14px;
    margin: 0;
  }

  ul.compact li {
    font-size: 7.5pt;
    line-height: 1.33;
    color: #334155;
    margin-bottom: 3.5px;
  }

  .callout {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-left: 3.5px solid #2563eb;
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 7.7pt;
    color: #1e293b;
    margin-bottom: 8px;
    line-height: 1.36;
  }

  .repo-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
  }

  .repo-item {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 4px 7px;
    font-size: 7pt;
    line-height: 1.28;
  }

  .repo-item code {
    font-weight: 700;
    color: #1d4ed8;
    font-size: 7pt;
  }
</style>
</head>
<body>

<!-- ==================== PAGE 1 ==================== -->
<div class="page">
  <div class="hero">
    <div class="hero-badge">Elevate Labs DevOps Internship &bull; Ministry of MSME, Govt. of India &bull; Project #3</div>
    <h1>Complete Observability System</h1>
    <div class="subtitle">
      Executive Engineering Report &mdash; Unifying Prometheus Metrics, Loki Centralized Logs, and Jaeger Distributed Tracing
      with OpenTelemetry Instrumentation &amp; Declarative Grafana Dashboards
    </div>
  </div>

  <div class="meta-grid">
    <div class="meta-card">
      <div class="meta-label">Author &amp; Maintainer</div>
      <div class="meta-val">Preetham Pereira</div>
      <div class="meta-sub">cloudwithpreetham &bull; MIT 2026</div>
    </div>
    <div class="meta-card">
      <div class="meta-label">Orchestration</div>
      <div class="meta-val">Docker Compose</div>
      <div class="meta-sub">6 Containerized Services</div>
    </div>
    <div class="meta-card">
      <div class="meta-label">Application Runtime</div>
      <div class="meta-val">Python 3.11 / Flask 3.0</div>
      <div class="meta-sub">OTel SDK 1.25 &bull; Port 5000</div>
    </div>
    <div class="meta-card">
      <div class="meta-label">Verification Status</div>
      <div class="meta-val">Deployed &amp; Verified</div>
      <div class="meta-sub">26 Git Commits &bull; Live Telemetry</div>
    </div>
  </div>

  <div class="sec-title"><span class="sec-num">1</span> Executive Summary &amp; Problem Statement</div>
  <p>
    Traditional infrastructure monitoring answers only whether a host or process is reachable (<em>&ldquo;Is it up?&rdquo;</em>),
    leaving engineering teams blind when diagnosing tail latency, intermittent errors, and cascading bottlenecks in distributed
    microservices. Modern Site Reliability Engineering (SRE) replaces siloed health checks with <strong>observability</strong> &mdash;
    the ability to infer internal execution state purely from correlated external telemetry outputs.
  </p>
  <p>
    This project delivers a self-contained, single-command Observability Minimum Viable Product (<span class="mono">docker compose up -d --build</span>)
    built around a custom instrumented Python Flask microservice (<span class="mono">flask-observability-app</span>). By simultaneously exposing
    time-series metrics, shipping trace-annotated container logs, and exporting OpenTelemetry spans via OTLP gRPC, the platform unifies
    all three pillars inside pre-provisioned Grafana dashboards with zero manual UI configuration.
  </p>

  <div class="pillars-grid">
    <div class="pillar-card metrics">
      <div class="pillar-head">
        <span class="pillar-title">1. Metrics Pillar</span>
        <span class="pillar-tag">Prometheus v2.52</span>
      </div>
      <div class="pillar-body">
        <strong>Pull model (5s interval):</strong> Scrapes <span class="mono">/metrics</span> exposed by
        <span class="mono">prometheus-flask-exporter</span>, capturing HTTP request counters, status codes, and latency histograms into TSDB.
      </div>
    </div>
    <div class="pillar-card logs">
      <div class="pillar-head">
        <span class="pillar-title">2. Logging Pillar</span>
        <span class="pillar-tag">Loki &amp; Promtail v3.0</span>
      </div>
      <div class="pillar-body">
        <strong>Push model (Docker SD):</strong> Promtail tails container stdout via <span class="mono">docker.sock</span>, extracts
        <span class="mono">container</span> labels, and ships trace-correlated logs to Loki&rsquo;s v13 TSDB store.
      </div>
    </div>
    <div class="pillar-card traces">
      <div class="pillar-head">
        <span class="pillar-title">3. Tracing Pillar</span>
        <span class="pillar-tag">Jaeger v1.57 + OTel</span>
      </div>
      <div class="pillar-body">
        <strong>Push model (OTLP gRPC):</strong> OpenTelemetry SDK auto-instruments Flask requests and exports custom spans
        (<span class="mono">compute_job</span>, <span class="mono">slow_database_query</span>) to Jaeger port <span class="mono">4317</span>.
      </div>
    </div>
  </div>

  <div class="sec-title"><span class="sec-num">2</span> Containerized Technology Stack &amp; Service Topology</div>
  <table>
    <thead>
      <tr>
        <th style="width: 17%;">Service / Container</th>
        <th style="width: 21%;">Image / Version</th>
        <th style="width: 15%;">Ports &amp; Network</th>
        <th style="width: 20%;">Mounts / Configuration</th>
        <th style="width: 27%;">Architectural Role</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>flask-app</strong><br/><span class="mono">flask-observability-app</span></td>
        <td>Built from <span class="mono">./app</span><br/>Python 3.11-slim</td>
        <td><span class="mono">5000:5000</span><br/>Depends: jaeger</td>
        <td><span class="mono">OTEL_PYTHON_LOG_CORRELATION=true</span></td>
        <td>Simulated microservice exposing workloads, Prometheus metrics, OTLP traces, and trace-injected logs.</td>
      </tr>
      <tr>
        <td><strong>prometheus</strong><br/><span class="mono">prometheus</span></td>
        <td><span class="mono">prom/prometheus:v2.52.0</span></td>
        <td><span class="mono">9090:9090</span></td>
        <td><span class="mono">prometheus/prometheus.yml</span><br/>TSDB: <span class="mono">/prometheus</span></td>
        <td>Time-series database polling <span class="mono">flask-app:5000/metrics</span> and self-monitoring every 5 seconds.</td>
      </tr>
      <tr>
        <td><strong>loki</strong><br/><span class="mono">loki</span></td>
        <td><span class="mono">grafana/loki:3.0.0</span></td>
        <td><span class="mono">3100:3100</span></td>
        <td><span class="mono">loki/loki-config.yml</span><br/>Schema v13 TSDB</td>
        <td>Centralized log aggregator indexing container label metadata with filesystem chunk &amp; 24h index storage.</td>
      </tr>
      <tr>
        <td><strong>promtail</strong><br/><span class="mono">promtail</span></td>
        <td><span class="mono">grafana/promtail:3.0.0</span></td>
        <td>Internal <span class="mono">9080</span><br/>Depends: loki</td>
        <td><span class="mono">promtail-config.yml</span><br/><span class="mono">docker.sock:ro</span></td>
        <td>Discovers running Docker containers every 5s and pushes stdout log streams to Loki Push API.</td>
      </tr>
      <tr>
        <td><strong>jaeger</strong><br/><span class="mono">jaeger</span></td>
        <td><span class="mono">jaegertracing/all-in-one:1.57</span></td>
        <td><span class="mono">16686:16686</span> (UI)<br/><span class="mono">4317:4317</span> (gRPC)</td>
        <td><span class="mono">COLLECTOR_OTLP_ENABLED=true</span></td>
        <td>OTLP gRPC collector, trace storage backend, and waterfall call-graph visualizer.</td>
      </tr>
      <tr>
        <td><strong>grafana</strong><br/><span class="mono">grafana</span></td>
        <td><span class="mono">grafana/grafana:10.4.2</span></td>
        <td><span class="mono">3000:3000</span><br/>Depends: 3 backends</td>
        <td><span class="mono">grafana/provisioning/</span><br/>Admin / Anonymous Admin</td>
        <td>Unified visualization UI auto-provisioning Prometheus, Loki, and Jaeger datasources plus 4-panel dashboard.</td>
      </tr>
    </tbody>
  </table>

  <div class="callout" style="margin-top: 6px; margin-bottom: 0;">
    <strong>Repository Engineering Progression:</strong> Git commit history (26 commits) reflects iterative DevOps refinement &mdash; progressing from
    container build optimization (<span class="mono">.dockerignore</span>) and pipeline configs to targeted bug fixes including dynamic
    <span class="mono">LogRecordFactory</span> trace-ID injection (resolving Werkzeug formatting exceptions) and deterministic Grafana datasource UID normalization.
  </div>

  <div class="page-footer">
    <span>Preetham Pereira &bull; Elevate Labs DevOps Internship (Ministry of MSME, Govt. of India)</span>
    <span>Page 1 of 4</span>
  </div>
</div>

<!-- ==================== PAGE 2 ==================== -->
<div class="page">
  <div class="page-header">
    <span class="hdr-left">Complete Observability System &mdash; Executive Project Report</span>
    <span class="hdr-right">Architecture &amp; Microservice Instrumentation</span>
  </div>

  <div class="sec-title" style="margin-top: 0;"><span class="sec-num">3</span> System Architecture &amp; Telemetry Pipelines</div>
  <div class="arch-box">
    <img src="__ARCH_IMG__" alt="System Architecture Diagram" />
    <div class="fig-caption">
      <strong>Figure 1:</strong> End-to-End Observability Architecture (<span class="mono">docs/architecture/observability-architecture.png</span>) showing the instrumented Flask service feeding Prometheus, Promtail/Loki, and Jaeger into Grafana.
    </div>
  </div>

  <div class="flow-grid">
    <div class="flow-box">
      <h4>Metrics Pull Pipeline</h4>
      <span class="mono">prometheus.yml</span> defines global <span class="mono">scrape_interval: 5s</span> and <span class="mono">evaluation_interval: 5s</span> across two static jobs: <span class="mono">flask-app</span> (<span class="mono">flask-app:5000/metrics</span>) and <span class="mono">prometheus</span> (<span class="mono">localhost:9090</span>). Metrics include <span class="mono">app_info</span>, <span class="mono">flask_http_request_total</span>, and duration buckets.
    </div>
    <div class="flow-box">
      <h4>Decoupled Log Shipping</h4>
      Flask writes logs unbuffered (<span class="mono">PYTHONUNBUFFERED=1</span>) to stdout. Promtail mounts <span class="mono">/var/run/docker.sock</span> and <span class="mono">/var/lib/docker/containers</span> read-only, relabeling <span class="mono">__meta_docker_container_name</span> to <span class="mono">container</span> and shipping to <span class="mono">loki:3100/loki/api/v1/push</span>.
    </div>
    <div class="flow-box">
      <h4>OTLP Distributed Tracing</h4>
      <span class="mono">TracerProvider</span> tags spans with <span class="mono">service.name="flask-observability-app"</span> and streams via <span class="mono">BatchSpanProcessor</span> + <span class="mono">OTLPSpanExporter</span> over gRPC (<span class="mono">jaeger:4317</span>). Both auto-instrumented HTTP spans and manual workload spans are captured.
    </div>
  </div>

  <div class="sec-title"><span class="sec-num">4</span> Flask Application Instrumentation &amp; Endpoint Specifications</div>
  <p>
    The target microservice (<span class="mono">app/app.py</span>, 80 lines) uses <span class="mono">Flask==3.0.3</span>, <span class="mono">prometheus-flask-exporter==0.23.1</span>,
    and OpenTelemetry SDK <span class="mono">1.25.0</span> (<span class="mono">0.46b0</span> instrumentation packages). Five routes model normal traffic,
    compute work, slow database queries, and server faults:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 13%;">Endpoint</th>
        <th style="width: 10%;">HTTP Status</th>
        <th style="width: 24%;">Simulated Workload / Latency</th>
        <th style="width: 24%;">OpenTelemetry Span</th>
        <th style="width: 29%;">Log &amp; Metric Telemetry Emitted</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><span class="mono">GET /</span></td>
        <td><span class="badge badge-green">200 OK</span></td>
        <td>Service index &amp; endpoint list</td>
        <td>Auto HTTP root span</td>
        <td><span class="mono">INFO</span> log + request counter</td>
      </tr>
      <tr>
        <td><span class="mono">GET /work</span></td>
        <td><span class="badge badge-green">200 OK</span></td>
        <td>Batch compute (<span class="mono">50&ndash;250 ms</span>)</td>
        <td>Child span <span class="mono">compute_job</span></td>
        <td><span class="mono">INFO</span> latency log + duration histogram</td>
      </tr>
      <tr>
        <td><span class="mono">GET /slow</span></td>
        <td><span class="badge badge-amber">200 OK</span></td>
        <td>Slow DB query (<span class="mono">800&ndash;1500 ms</span>)</td>
        <td>Child span <span class="mono">slow_database_query</span></td>
        <td><span class="mono">WARNING</span> alert log + latency tail spike</td>
      </tr>
      <tr>
        <td><span class="mono">GET /error</span></td>
        <td><span class="badge badge-red">500 ERR</span></td>
        <td>Simulated internal server fault</td>
        <td>Auto HTTP span (<span class="mono">status=500</span>)</td>
        <td><span class="mono">ERROR</span> log + HTTP 500 metric counter</td>
      </tr>
      <tr>
        <td><span class="mono">GET /metrics</span></td>
        <td><span class="badge badge-blue">200 OK</span></td>
        <td>Prometheus exposition endpoint</td>
        <td>Auto HTTP span (scraped /5s)</td>
        <td>Counter, histogram &amp; <span class="mono">app_info</span> gauges</td>
      </tr>
    </tbody>
  </table>

  <div class="split-2">
    <div class="code-panel"><div class="code-title">app/app.py &mdash; Trace-to-Log Context Injection &amp; OTLP Setup</div><span class="c-cmt"># Safely inject active Trace ID &amp; Span ID into every Python LogRecord</span>
old_factory = logging.getLogRecordFactory()
<span class="c-kw">def</span> record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    span = trace.get_current_span()
    ctx = span.get_span_context() <span class="c-kw">if</span> span <span class="c-kw">else</span> <span class="c-kw">None</span>
    <span class="c-kw">if</span> ctx <span class="c-kw">and</span> ctx.is_valid:
        record.otelTraceID = format(ctx.trace_id, <span class="c-str">"032x"</span>)
        record.otelSpanID  = format(ctx.span_id,  <span class="c-str">"016x"</span>)
    <span class="c-kw">else</span>:
        record.otelTraceID, record.otelSpanID = <span class="c-str">"0"</span>*32, <span class="c-str">"0"</span>*16
    <span class="c-kw">return</span> record
logging.setLogRecordFactory(record_factory)

<span class="c-cmt"># OTLP gRPC Exporter &amp; Flask/Prometheus Instrumentation</span>
res = Resource(attributes={<span class="c-str">"service.name"</span>: <span class="c-str">"flask-observability-app"</span>})
provider = TracerProvider(resource=res)
exporter = OTLPSpanExporter(endpoint=<span class="c-str">"jaeger:4317"</span>, insecure=<span class="c-kw">True</span>)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
LoggingInstrumentor().instrument()
FlaskInstrumentor().instrument_app(app)
metrics = PrometheusMetrics(app)</div>

    <div>
      <div class="panel-box" style="margin-bottom: 6px; padding: 6px 9px;">
        <h4 style="font-size: 7.9pt; margin-bottom: 3px;">Why the Custom <span class="mono">LogRecordFactory</span> Matters</h4>
        <p style="font-size: 7.25pt; line-height: 1.3; margin-bottom: 3px;">
          Format strings expecting <span class="mono">%(otelTraceID)s</span> raise <span class="mono">KeyError</span> when
          background loggers (e.g. Werkzeug&rsquo;s HTTP logger) emit events outside an active span.
        </p>
        <p style="font-size: 7.25pt; line-height: 1.3; margin-bottom: 0;">
          Wrapping <span class="mono">getLogRecordFactory()</span> ensures every record includes a 32-hex
          <span class="mono">trace_id</span> and 16-hex <span class="mono">span_id</span> (or zero fallback) for reliable
          Promtail/Loki ingestion and cross-pillar pivoting.
        </p>
      </div>
      <div class="panel-box" style="padding: 6px 9px;">
        <h4 style="font-size: 7.9pt; margin-bottom: 3px;">Synthetic Load (<span class="mono">traffic-generator.sh</span>)</h4>
        <p style="font-size: 7.25pt; line-height: 1.3; margin-bottom: 0;">
          Loops continuously across <span class="mono">/</span>, <span class="mono">/work</span>,
          <span class="mono">/slow</span>, and <span class="mono">/error</span> at <span class="mono">0.3s</span> intervals,
          generating realistic throughput curves, tail-latency spans, warning logs, and HTTP 500 errors.
        </p>
      </div>
    </div>
  </div>

  <div class="page-footer">
    <span>Preetham Pereira &bull; Elevate Labs DevOps Internship (Ministry of MSME, Govt. of India)</span>
    <span>Page 2 of 4</span>
  </div>
</div>

<!-- ==================== PAGE 3 ==================== -->
<div class="page">
  <div class="page-header">
    <span class="hdr-left">Complete Observability System &mdash; Executive Project Report</span>
    <span class="hdr-right">Grafana Provisioning &amp; Live Verification Evidence</span>
  </div>

  <div class="sec-title" style="margin-top: 0;"><span class="sec-num">5</span> Declarative Grafana Provisioning &amp; Telemetry Queries</div>
  <p>
    Grafana (<span class="mono">v10.4.2</span>) boots completely pre-configured via mounted YAML and JSON provisioning artifacts.
    <span class="mono">datasources.yml</span> assigns deterministic UIDs (<span class="mono">prometheus</span>, <span class="mono">loki</span>, <span class="mono">jaeger</span>)
    using proxy mode over internal Docker DNS, while <span class="mono">dashboards.yml</span> loads <span class="mono">dashboard.json</span>
    (UID <span class="mono">eg2gkti31bls0b</span>, 10s refresh scan) presenting four correlated telemetry panels:
  </p>

  <div class="query-grid">
    <div class="query-card">
      <div class="q-title"><span>Panel 1: HTTP Request Throughput (req/sec)</span><span class="q-src">PromQL &bull; uid: prometheus</span></div>
      <pre>sum by (endpoint) (rate(flask_http_request_total[1m]))</pre>
    </div>
    <div class="query-card">
      <div class="q-title"><span>Panel 2: Average Request Latency (seconds)</span><span class="q-src">PromQL &bull; uid: prometheus</span></div>
      <pre>rate(flask_http_request_duration_seconds_sum[1m]) / rate(flask_http_request_duration_seconds_count[1m])</pre>
    </div>
    <div class="query-card">
      <div class="q-title"><span>Panel 3: Application Centralized Logs</span><span class="q-src">LogQL &bull; uid: loki</span></div>
      <pre>{container="flask-observability-app"}</pre>
    </div>
    <div class="query-card">
      <div class="q-title"><span>Panel 4: Distributed Trace Waterfall</span><span class="q-src">Jaeger &bull; uid: jaeger</span></div>
      <pre>service: "flask-observability-app" | limit: 20</pre>
    </div>
  </div>

  <div class="sec-title"><span class="sec-num">6</span> Live Verification &amp; Runtime Evidence</div>
  <p>
    The stack was deployed via Docker Compose and exercised using the synthetic traffic generator. All six service containers
    reached <span class="mono">Up</span> state and every telemetry pipeline was validated across Prometheus, Jaeger, Loki, and Grafana:
  </p>

  <div class="shot-grid-2x2">
    <div class="shot-card">
      <div class="shot-frame dark"><img src="__IMG_PS__" alt="docker compose ps output" /></div>
      <div class="shot-cap">
        <strong>Figure 2 &mdash; Container Orchestration (<span class="mono">docker compose ps</span>):</strong>
        All 6 services (<span class="mono">flask-observability-app</span>, <span class="mono">grafana</span>, <span class="mono">jaeger</span>,
        <span class="mono">loki</span>, <span class="mono">prometheus</span>, <span class="mono">promtail</span>) active with host ports bound (<span class="mono">5000, 3000, 16686, 4317, 3100, 9090</span>).
      </div>
    </div>

    <div class="shot-card">
      <div class="shot-frame dark"><img src="__IMG_PROM__" alt="Prometheus scrape targets" /></div>
      <div class="shot-cap">
        <strong>Figure 3 &mdash; Prometheus Target Health:</strong>
        Both <span class="mono">flask-app</span> (<span class="mono">http://flask-app:5000/metrics</span>, scrape duration <span class="mono">4.226 ms</span>)
        and <span class="mono">prometheus</span> (<span class="mono">3.113 ms</span>) report healthy <span class="mono">UP</span> status at 5s polling intervals.
      </div>
    </div>

    <div class="shot-card">
      <div class="shot-frame dark"><img src="__IMG_DS__" alt="Grafana provisioned datasources" /></div>
      <div class="shot-cap">
        <strong>Figure 4 &mdash; Grafana Provisioned Datasources:</strong>
        Zero-touch YAML provisioning registers <strong>Jaeger</strong> (<span class="mono">jaeger:16686</span>), <strong>Loki</strong>
        (<span class="mono">loki:3100</span>), and <strong>Prometheus</strong> (<span class="mono">prometheus:9090</span>, marked <span class="mono">default</span>).
      </div>
    </div>

    <div class="shot-card">
      <div class="shot-frame"><img src="__IMG_JAEGER__" alt="Jaeger distributed traces" /></div>
      <div class="shot-cap">
        <strong>Figure 5 &mdash; Jaeger Trace Ingestion:</strong>
        Jaeger UI Search shows <span class="mono">flask-observability-app</span> active with <span class="mono">7</span> operations and
        <span class="mono">20</span> recent traces plotted by duration (~<span class="mono">1.89&ndash;3.02 ms</span> for <span class="mono">GET /metrics</span> scrapes).
      </div>
    </div>
  </div>

  <div class="page-footer">
    <span>Preetham Pereira &bull; Elevate Labs DevOps Internship (Ministry of MSME, Govt. of India)</span>
    <span>Page 3 of 4</span>
  </div>
</div>

<!-- ==================== PAGE 4 ==================== -->
<div class="page">
  <div class="page-header">
    <span class="hdr-left">Complete Observability System &mdash; Executive Project Report</span>
    <span class="hdr-right">Correlation Evidence, Engineering Audit &amp; Conclusion</span>
  </div>

  <div class="sec-title" style="margin-top: 0;"><span class="sec-num">6</span> Verification Evidence (Continued): Logs &amp; Unified Correlation</div>

  <div class="shot-grid-2">
    <div class="shot-card">
      <div class="shot-frame-lg"><img src="__IMG_LOKI__" alt="Loki log exploration in Grafana" /></div>
      <div class="shot-cap">
        <strong>Figure 6 &mdash; Grafana Explore (Loki Log Stream):</strong>
        Query <span class="mono">{container="flask-observability-app"}</span> displays live log volume distribution across severities:
        <strong>info: 761</strong>, <strong>error: 40</strong>, and <strong>warning: 21</strong> (<span class="mono">822</span> lines, <span class="mono">105 kB</span> processed).
      </div>
    </div>

    <div class="shot-card">
      <div class="shot-frame-lg"><img src="__IMG_DASH__" alt="Unified Grafana dashboard" /></div>
      <div class="shot-cap">
        <strong>Figure 7 &mdash; Unified Grafana Dashboard:</strong>
        Four-quadrant view correlating Prometheus throughput &amp; endpoint latency (<span class="mono">/</span>, <span class="mono">/work</span>, <span class="mono">/slow</span>, <span class="mono">/error</span>),
        Loki logs, and Jaeger waterfall (<span class="mono">1.85 ms</span>). <em>Note:</em> Captured prior to commits <span class="mono">9b85787</span>/<span class="mono">3c3b8b6</span> that refined log trace injection &amp; panel titles.
      </div>
    </div>
  </div>

  <div class="sec-title"><span class="sec-num">7</span> Key Results &amp; Production Hardening Roadmap</div>
  <div class="insights-grid">
    <div class="panel-box">
      <h4>&#10003; Key Outcomes &amp; Triage Workflow</h4>
      <ul class="compact">
        <li><strong>Zero-Touch Provisioning:</strong> Single <span class="mono">docker compose up -d --build</span> launches all 6 services with pre-linked datasources and dashboard UIDs.</li>
        <li><strong>Root-Cause Triangulation:</strong> PromQL highlights <span class="mono">/slow</span> latency (<span class="mono">0.8&ndash;1.5s</span>) or <span class="mono">/error</span> 500 spikes; engineers inspect the <span class="mono">slow_database_query</span> span in Jaeger and match its 32-hex <span class="mono">trace_id</span> directly in Loki.</li>
        <li><strong>Low-Overhead Log Indexing:</strong> Loki indexes only container metadata labels rather than full-text payloads, minimizing CPU and memory footprint.</li>
        <li><strong>Automated Validation:</strong> Traffic harness confirmed simultaneous ingestion across Prometheus, Loki, and Jaeger.</li>
      </ul>
    </div>

    <div class="panel-box warn">
      <h4>&#9888; Codebase Audit &amp; Production Hardening</h4>
      <ul class="compact">
        <li><strong>Persistent Storage Volumes:</strong> Add named Docker volumes for <span class="mono">/prometheus</span>, <span class="mono">/loki</span>, and <span class="mono">/var/lib/grafana</span> so telemetry survives container recreation.</li>
        <li><strong>Security Posture:</strong> Disable <span class="mono">GF_AUTH_ANONYMOUS_ENABLED=true</span>, rotate <span class="mono">admin/admin</span>, enable TLS on Jaeger OTLP gRPC (<span class="mono">4317</span>), and replace Promtail&rsquo;s host <span class="mono">docker.sock</span> mount with a scoped log driver.</li>
        <li><strong>WSGI Server &amp; Trace Noise Filtering:</strong> Run Flask behind Gunicorn instead of Werkzeug&rsquo;s dev server, and pass <span class="mono">excluded_urls="/metrics"</span> to <span class="mono">FlaskInstrumentor</span> so 5s Prometheus scrapes do not pollute Jaeger traces.</li>
        <li><strong>Healthchecks &amp; Alerting:</strong> Define Compose <span class="mono">healthcheck</span> probes and add Prometheus/Grafana alerts for 5xx error rates and p95 latency SLOs.</li>
      </ul>
    </div>
  </div>

  <div class="sec-title"><span class="sec-num">8</span> Conclusion &amp; Repository Deliverables Index</div>
  <p style="margin-bottom: 7px;">
    The <strong>Complete Observability System</strong> satisfies all Elevate Labs DevOps Internship Project #3 objectives by bridging
    metrics, logs, and distributed traces into an integrated, reproducible architecture. By eliminating telemetry silos and embedding
    OpenTelemetry trace context directly inside application logs, the system provides a practical, extensible blueprint for reducing
    Mean Time to Detection (MTTD) and Mean Time to Resolution (MTTR) in cloud-native environments.
  </p>

  <div class="repo-grid">
    <div class="repo-item"><code>docker-compose.yml</code><br/>6-service stack orchestration, ports &amp; configs</div>
    <div class="repo-item"><code>app/app.py</code> &amp; <code>Dockerfile</code><br/>Instrumented Flask microservice &amp; OTel hooks</div>
    <div class="repo-item"><code>prometheus/prometheus.yml</code><br/>5s scrape jobs for Flask &amp; self-metrics</div>
    <div class="repo-item"><code>loki/</code> &amp; <code>promtail/</code><br/>TSDB v13 store &amp; Docker SD log shipping</div>
    <div class="repo-item"><code>grafana/provisioning/</code><br/>Automated datasources &amp; 4-panel dashboard JSON</div>
    <div class="repo-item"><code>scripts/traffic-generator.sh</code><br/>Synthetic load testing &amp; fault injection</div>
  </div>

  <div class="page-footer">
    <span>Preetham Pereira &bull; Elevate Labs DevOps Internship (Ministry of MSME, Govt. of India)</span>
    <span>Page 4 of 4</span>
  </div>
</div>

</body>
</html>
"""
    replacements = {
        "__ARCH_IMG__": img_data_uri("docs/architecture/observability-architecture.png"),
        "__IMG_PROM__": img_data_uri("docs/screenshots/1-prometheus-targets.png"),
        "__IMG_JAEGER__": img_data_uri("docs/screenshots/2-jaeger-traces.png"),
        "__IMG_DS__": img_data_uri("docs/screenshots/3-grafana-datasources.png"),
        "__IMG_DASH__": img_data_uri("docs/screenshots/4-grafana-unified-dashboard.png"),
        "__IMG_LOKI__": img_data_uri("docs/screenshots/5-loki-log-exploration.png"),
        "__IMG_PS__": img_data_uri("docs/screenshots/6-docker-compose-ps.png"),
    }
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html


def build_pdf(filename: str | Path = DEFAULT_PDF) -> Path:
    pdf_path = Path(filename)
    if not pdf_path.is_absolute():
        pdf_path = ROOT / pdf_path
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    browser = find_browser()
    html_content = build_html()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        html_file = tmp / "project_report.html"
        profile_dir = tmp / "browser_profile"
        html_file.write_text(html_content, encoding="utf-8")

        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile_dir}",
            f"--print-to-pdf={pdf_path}",
            html_file.as_uri(),
        ]
        subprocess.run(cmd, check=True)

    print(f"Report PDF successfully generated at: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    build_pdf()
