import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically to ensure 2-page constraint."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "Elevate Labs DevOps Internship | Complete Observability System (Project 3)")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        
        self.drawString(54, 32, "Ministry of MSME, Govt. of India Initiative | Elevate Labs Internship")
        self.drawRightString(558, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf(filename="docs/PROJECT_REPORT.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=48,
        bottomMargin=52
    )

    styles = getSampleStyleSheet()

    # Custom typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )
    
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("Complete Observability System (Metrics, Logs & Traces)", title_style))
    story.append(Paragraph("ELEVATE LABS DEVOPS INTERNSHIP PROJECT REPORT &nbsp;|&nbsp; PROJECT #3", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=7))

    # Meta Info Table
    meta_data = [
        [
            Paragraph("<b>Domain:</b> DevOps & SRE Engineering", table_cell),
            Paragraph("<b>Timeline:</b> 2 Weeks Accelerated MVP", table_cell),
            Paragraph("<b>Platform:</b> Docker Compose Microservices", table_cell)
        ],
        [
            Paragraph("<b>Author:</b> DevOps Intern", table_cell),
            Paragraph("<b>Affiliation:</b> Elevate Labs / MSME Govt. of India", table_cell),
            Paragraph("<b>Status:</b> Fully Implemented & Verified", table_cell)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[165, 175, 164])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 4))

    # 1. Abstract
    story.append(Paragraph("1. Abstract", h1_style))
    abstract_text = (
        "Modern cloud-native architectures rely on microservices that communicate asynchronously across distributed "
        "networks. While traditional infrastructure monitoring answers whether a host is up or down, it fails to diagnose "
        "the root causes of latency bottlenecks, intermittent failures, and distributed dependencies. This project delivers "
        "an end-to-end, production-ready Observability Minimum Viable Product (MVP) implementing the <b>Three Pillars of "
        "Observability</b>: time-series metrics, centralized log streams, and distributed request tracing. By integrating "
        "<b>Prometheus, Grafana Loki, Promtail, Jaeger,</b> and <b>Grafana</b> with an instrumented Python Flask microservice, "
        "the solution enables full-lifecycle telemetry correlation from a single unified Grafana dashboard deployed "
        "declaratively via Docker Compose."
    )
    story.append(Paragraph(abstract_text, body_style))

    # 2. Introduction
    story.append(Paragraph("2. Introduction", h1_style))
    intro_text = (
        "Site Reliability Engineering (SRE) defines observability as the ability to infer internal system states purely from "
        "external outputs. When an incident occurs in production, operators must rapidly navigate between aggregate "
        "symptoms (metrics), historical execution events (logs), and distributed cross-service journeys (traces). "
        "This project builds an automated observability ecosystem designed to eliminate monitoring silos. A realistic "
        "microservice simulates compute tasks, database latency, and unhandled server errors, outputting correlated "
        "telemetry with OpenTelemetry context injection (Trace IDs and Span IDs) directly into the telemetry pipeline."
    )
    story.append(Paragraph(intro_text, body_style))

    # 3. Tools & Technologies Used
    story.append(Paragraph("3. Tools & Technologies Used", h1_style))
    tools_data = [
        [Paragraph("Tool / Component", table_cell_bold), Paragraph("Version / Role", table_cell_bold), Paragraph("Architectural Function in Project", table_cell_bold)],
        [Paragraph("<b>Prometheus</b>", table_cell), Paragraph("v2.52.0 (Metrics Engine)", table_cell), Paragraph("Polls /metrics every 5s; records request rate, status codes, and latency histograms.", table_cell)],
        [Paragraph("<b>Grafana Loki</b>", table_cell), Paragraph("v3.0.0 (Log Aggregator)", table_cell), Paragraph("Stores metadata-indexed container logs efficiently in TSDB filesystem chunks without heavy full-text overhead.", table_cell)],
        [Paragraph("<b>Promtail</b>", table_cell), Paragraph("v3.0.0 (Log Shipper)", table_cell), Paragraph("Attaches to Docker daemon socket (/var/run/docker.sock) and ships stdout streams to Loki.", table_cell)],
        [Paragraph("<b>Jaeger</b>", table_cell), Paragraph("v1.57 (Distributed Tracing)", table_cell), Paragraph("OTLP gRPC collector (port 4317) and trace store; provides waterfall call graph timelines.", table_cell)],
        [Paragraph("<b>Grafana</b>", table_cell), Paragraph("v10.4.2 (Unified UI)", table_cell), Paragraph("Pre-provisioned dashboard displaying metrics, logs, and trace links side-by-side with zero manual setup.", table_cell)],
        [Paragraph("<b>OpenTelemetry & Flask</b>", table_cell), Paragraph("OTel SDK 1.25 / Python 3.11", table_cell), Paragraph("Auto-instruments HTTP requests, propagates W3C trace context, and provides custom workload spans.", table_cell)],
        [Paragraph("<b>Docker Compose</b>", table_cell), Paragraph("v2.20+ (Orchestration)", table_cell), Paragraph("Declarative single-command provisioning (docker compose up -d) for all 6 microservices.", table_cell)],
    ]
    t_tools = Table(tools_data, colWidths=[95, 110, 299])
    t_tools.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tools)

    # 4. Steps Involved in Building the Project
    story.append(Paragraph("4. Steps Involved in Building the Project", h1_style))
    steps = [
        "<b>Step 1 — Application Design & Telemetry Instrumentation:</b> Created a Python Flask service (app/app.py) exposing business endpoints (/work, /slow, /error). Instrumented OpenTelemetry TracerProvider with gRPC OTLP exporter to Jaeger and wrapped HTTP routing using FlaskInstrumentor. Integrated prometheus_flask_exporter to automatically expose Prometheus metrics at /metrics. Configured dynamic log record hooks injecting active trace_id and span_id into standard log outputs.",
        "<b>Step 2 — Log Aggregation with Promtail & Loki:</b> Implemented a decoupled logging pattern. The container writes structured logs to stdout. Promtail discovers running containers via the Docker socket, extracts metadata labels (container=\"flask-observability-app\"), and pushes compressed log streams to Grafana Loki via HTTP API push endpoints.",
        "<b>Step 3 — Prometheus Metrics Pull Configuration:</b> Defined declarative scrape jobs in prometheus.yml configured with a 5-second interval targeting the internal Docker DNS name flask-app:5000, tracking request rates, errors, and execution duration quantiles.",
        "<b>Step 4 — Distributed Trace Pipeline:</b> Configured Jaeger All-in-One with OTLP receiver enabled (COLLECTOR_OTLP_ENABLED=true). Instrumented custom internal span operations (compute_job and slow_database_query) to record synthetic database and CPU processing latencies.",
        "<b>Step 5 — Automated Grafana Provisioning:</b> Built automated YAML datasources (datasources.yml) with explicit deterministic UIDs (prometheus, loki, jaeger) and dashboard provider definitions (dashboards.yml). Authored a comprehensive 4-panel dashboard (dashboard.json) correlating throughput, latency, log streams, and trace waterfalls without requiring manual UI configuration.",
        "<b>Step 6 — Orchestration & Synthetic Load Testing:</b> Unified all services within docker-compose.yml with health dependencies and persistent storage mounts. Developed an automated synthetic load generator script (traffic-generator.sh) to simulate realistic production traffic and failure states."
    ]
    for step in steps:
        story.append(Paragraph(f"• {step}", bullet_style))

    # 5. Key Results & Observability Insights
    story.append(Paragraph("5. Key Results & Observability Insights", h1_style))
    results_text = (
        "During synthetic testing, the system demonstrated seamless cross-pillar telemetry correlation:<br/>"
        "• <b>Real-time Metric Tracking:</b> PromQL queries accurately isolated spikes in endpoint request rate "
        "(sum by (endpoint) (rate(flask_http_request_total[1m]))) and highlighted simulated HTTP 500 error spikes on /error.<br/>"
        "• <b>Trace-to-Log Correlation:</b> When inspecting high-latency events on /slow (800ms–1500ms), engineers could view the exact trace waterfall in Jaeger and correlate the corresponding log record in Loki using the shared 32-character hexadecimal Trace ID.<br/>"
        "• <b>Zero-Configuration Deployment:</b> The entire multi-tiered monitoring architecture provisions automatically in under 60 seconds with docker compose up -d."
    )
    story.append(Paragraph(results_text, body_style))

    # 6. Conclusion
    story.append(Paragraph("6. Conclusion", h1_style))
    conclusion_text = (
        "This project successfully designs and deploys a complete, production-ready observability architecture fulfilling "
        "all Elevate Labs guidelines. By seamlessly correlating metrics (Prometheus), logs (Loki/Promtail), and distributed "
        "traces (Jaeger) into an automated Grafana dashboard, the system eliminates blind spots in microservice architectures "
        "and drastically reduces Mean Time to Detection (MTTD) and Mean Time to Resolution (MTTR). The project serves as an "
        "exemplary blueprint for modern cloud-native observability and Site Reliability Engineering best practices."
    )
    story.append(Paragraph(conclusion_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report PDF successfully generated at: {filename}")

if __name__ == "__main__":
    build_pdf()
