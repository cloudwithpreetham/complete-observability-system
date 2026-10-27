FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV OTEL_PYTHON_LOG_CORRELATION=true

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
