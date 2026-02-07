"""API routes for health checks."""
import logging
from fastapi import APIRouter, status
from app.models.schemas import HealthResponse
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with status and API key configuration check
    """
    try:
        # Check if API keys are configured
        api_keys_configured = bool(
            settings.gemini_api_key and
            settings.esm_api_key and
            settings.gemini_api_key != "" and
            settings.esm_api_key != ""
        )
        
        return HealthResponse(
            status="ok",
            api_keys_configured=api_keys_configured
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="error",
            api_keys_configured=False
        )

