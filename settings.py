"""
Centralized configuration for the Artha Agent application.

This module provides a single source of truth for all application settings,
using Pydantic BaseSettings for environment variable management and validation.
"""

from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Server Configuration
    server_host: str = Field(default="0.0.0.0", description="Server host address")
    server_port: int = Field(default=8000, description="Server port")
    
    # Application Configuration
    app_title: str = Field(default="artha", description="FastAPI application title")
    app_description: str = Field(default="API for interacting with the Agent artha", description="Application description")
    
    # Google Cloud Configuration
    google_cloud_storage_bucket: Optional[str] = Field(default=None, description="GCS bucket name for artifact storage")
    google_cloud_location: str = Field(default="us-central1", description="Google Cloud region")
    
    # Database Configuration
    supabase_db_conn_string: Optional[str] = Field(default=None, description="Supabase database connection string")
    
    # CORS Configuration
    allow_origins: Optional[str] = Field(default=None, description="Comma-separated list of allowed origins")
    
    # Tracing Configuration
    trace_to_cloud: bool = Field(default=True, description="Enable cloud tracing")
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment
    
    @property
    def cors_origins(self) -> Optional[List[str]]:
        """Parse CORS origins from comma-separated string."""
        if self.allow_origins:
            return [origin.strip() for origin in self.allow_origins.split(",") if origin.strip()]
        return None
    
    @property
    def gcs_bucket_uri(self) -> Optional[str]:
        """Get the GCS bucket URI for artifact storage."""
        if self.google_cloud_storage_bucket:
            if self.google_cloud_storage_bucket.startswith("gs://"):
                return self.google_cloud_storage_bucket
            return f"gs://{self.google_cloud_storage_bucket}"
        return None


# Global settings instance
settings = Settings() 