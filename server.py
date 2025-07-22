import os

import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export

from fi_mcp_agent.utils.gcs import create_bucket_if_not_exists
from fi_mcp_agent.utils.tracing import CloudTraceLoggingSpanExporter
from fi_mcp_agent.utils.typing import Feedback

from dotenv import load_dotenv
# from phoenix.otel import register

# # Configure the Phoenix tracer
# tracer_provider = register(
#     project_name="artha",  # Default is 'default'
#     auto_instrument=True        # Auto-instrument your app based on installed OI dependencies
# )

load_dotenv()

_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)


bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
create_bucket_if_not_exists(
    bucket_name=bucket_name, project=project_id, location="us-central1"
)

provider = TracerProvider()
processor = export.BatchSpanProcessor(CloudTraceLoggingSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))


# Set session_service_uri if database credentials are available
session_service_uri = os.getenv("SUPABASE_DB_CONN_STRING")

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=bucket_name,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    trace_to_cloud=True,
)
app.title = "artha"
app.description = "API for interacting with the Agent artha"


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

    uvicorn.run(app, host="0.0.0.0", port=8000)
