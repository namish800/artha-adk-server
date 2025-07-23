import google.auth
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fast_api_custom import get_fast_api_app
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export

from utils.gcs import create_bucket_if_not_exists
from utils.tracing import CloudTraceLoggingSpanExporter
from utils.typing import Feedback, FIRequest
from settings import settings
# from phoenix.otel import register

import logging  # Import the logging module to configure debug logging

# Configure basic logging to display debug output
logging.basicConfig(level=logging.INFO)

_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
# Enable Cloud Logging to capture messages at DEBUG level
logging_client.setup_logging(log_level=logging.INFO)
logger = logging_client.logger(__name__)


# Create GCS bucket if needed
if settings.google_cloud_storage_bucket:
    create_bucket_if_not_exists(
        bucket_name=settings.google_cloud_storage_bucket, 
        project=project_id, 
        location=settings.google_cloud_location
    )

provider = TracerProvider()
processor = export.BatchSpanProcessor(CloudTraceLoggingSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

import os
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=settings.google_cloud_storage_bucket,
    allow_origins=settings.cors_origins,
    session_service_uri=settings.supabase_db_conn_string,
    memory_service_uri=settings.memory_service_uri,
    trace_to_cloud=settings.trace_to_cloud,
)
app.title = settings.app_title
app.description = settings.app_description


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}

@app.get("/ping")
def ping():
    return {"status": "pong"}


# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.server_host, port=settings.server_port)
