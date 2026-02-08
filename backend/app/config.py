"""Configuration module for environment variables and settings."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    gemini_api_key: str
    esm_api_key: str
    
    # API Endpoints
    esm_api_url: str = "https://biolm.ai/api/v3/esm1v-all/predict/"
    esmfold_api_url: str = "https://api.esmatlas.com/foldSequence/v1/pdb/"
    
    # Validation Settings
    esm_top_n: int = 3  # Number of top-scoring candidates to return from ESM validation
    rmsd_good_threshold: float = 2.0  # RMSD threshold in Angstroms
    
    # Gemini Model Settings
    # Using model name from official documentation example
    gemini_model_discovery: str = "gemini-3-flash-preview"
    gemini_model_validation: str = "gemini-3-flash-preview"
    
    # Application Settings
    app_name: str = "GeneRescue API"
    debug: bool = False
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env file
    )


# Global settings instance
settings = Settings()

