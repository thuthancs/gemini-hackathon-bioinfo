"""Service for interacting with ESMFold API for structure prediction."""
import logging
from typing import Optional
import requests
from app.config import settings

logger = logging.getLogger(__name__)


def predict_structure(sequence: str, timeout: int = 300) -> str:
    """
    Call ESMFold API to predict protein structure.
    
    Args:
        sequence: Protein sequence (amino acids)
        timeout: Request timeout in seconds (default: 300)
    
    Returns:
        PDB format structure as string
    
    Raises:
        Exception: If ESMFold API call fails
    """
    url = settings.esmfold_api_url
    
    try:
        logger.info(f"Calling ESMFold for sequence of length {len(sequence)}")
        response = requests.post(
            url,
            data=sequence,
            headers={"Content-Type": "text/plain"},
            timeout=timeout
        )
        response.raise_for_status()
        
        pdb_content = response.text
        
        if not pdb_content or len(pdb_content) < 100:
            raise ValueError("ESMFold returned empty or invalid PDB content")
        
        logger.info(f"Successfully received PDB structure ({len(pdb_content)} characters)")
        return pdb_content
    
    except requests.exceptions.Timeout:
        logger.error(f"ESMFold API timeout after {timeout} seconds")
        raise Exception(f"ESMFold API request timed out after {timeout} seconds")
    except requests.exceptions.RequestException as e:
        logger.error(f"ESMFold API request failed: {e}")
        raise Exception(f"ESMFold API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error calling ESMFold: {e}")
        raise Exception(f"Failed to predict structure: {e}")

