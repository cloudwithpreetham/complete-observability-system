import logging
import random
import time
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Initialize Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] trace_id=%(otelTraceID)s span_id=%(otelSpanID)s %(message)s')
logger = logging.getLogger("observability-service")

# Setup OpenTelemetry Tracer with Resource Attributes
resource = Resource(attributes={"service.name": "flask-observability-app"})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="jaeger:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Initialize Flask & Prometheus Exporter
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
metrics = PrometheusMetrics(app)

metrics.info('app_info', 'Application info', version='1.0.0')

@app.route("/")
def home():
    logger.info("Root endpoint accessed successfully")
    return jsonify({"message": "Observability Stack Active", "endpoints": ["/work", "/slow", "/error", "/metrics"]})

@app.route("/work")
def work():
    with tracer.start_as_current_span("compute_job"):
        sleep_duration = random.uniform(0.05, 0.25)
        time.sleep(sleep_duration)
        logger.info(f"Processed batch calculation in {sleep_duration:.3f}s")
    return jsonify({"status": "completed", "latency": f"{sleep_duration:.3f}s"})

@app.route("/slow")
def slow():
    with tracer.start_as_current_span("slow_database_query"):
        delay = random.uniform(0.8, 1.5)
        time.sleep(delay)
        logger.warning(f"Slow query detected: latency {delay:.2f}s")
    return jsonify({"status": "slow_response", "delay": f"{delay:.2f}s"})

@app.route("/error")
def simulate_error():
    logger.error("Internal service failure simulated on /error")
    return jsonify({"error": "Internal Server Error", "code": 500}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
