import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export

from fi_mcp_agent.utils.gcs import create_bucket_if_not_exists
from fi_mcp_agent.utils.tracing import CloudTraceLoggingSpanExporter
from fi_mcp_agent.utils.typing import Feedback
from settings import settings
# from phoenix.otel import register

# # Configure the Phoenix tracer
# tracer_provider = register(
#     project_name="artha",  # Default is 'default'
#     auto_instrument=True        # Auto-instrument your app based on installed OI dependencies
# )

_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
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
