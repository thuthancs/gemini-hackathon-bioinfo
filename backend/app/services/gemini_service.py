"""Service for interacting with Google Gemini API."""
import json
import logging
from typing import List, Dict, Any
from google import genai
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Gemini API client
# The client automatically picks up GEMINI_API_KEY from environment
# But we pass it explicitly to use our settings
client = genai.Client(api_key=settings.gemini_api_key)

# Prompt templates
DISCOVERY_PROMPT_TEMPLATE = """You are a protein biology expert. Find 3-5 compensatory mutations 
that could rescue the pathogenic {protein} {mutation} mutation based on literature.

Return ONLY a JSON array with this exact format:
[
  {{
    "position": 168,
    "original_aa": "H",
    "rescue_aa": "R",
    "mutation": "H168R",
    "reasoning": "Brief explanation from literature"
  }}
]

No markdown, no explanation, just the JSON array."""

VALIDATION_PROMPT_TEMPLATE = """Review these rescue mutation candidates with their validation scores:

{data}

Based on:
1. ESM-1v evolutionary score (>0.6 is good)
2. RMSD structural similarity (<2.0Å is good)
3. Literature reasoning

Return JSON with approved candidates only:
{{
  "approved": [...],
  "summary": "Brief explanation of why these were approved"
}}"""


def get_rescue_candidates(mutation: str, protein: str = "TP53") -> List[Dict[str, Any]]:
    """
    Ask Gemini for 3-5 compensatory mutation candidates based on literature.
    
    Args:
        mutation: Mutation string (e.g., "R249S")
        protein: Protein name (default: "TP53")
    
    Returns:
        List of candidate dictionaries with position, original_aa, rescue_aa, mutation, reasoning
    
    Raises:
        Exception: If Gemini API call fails or response cannot be parsed
    """
    try:
        prompt = DISCOVERY_PROMPT_TEMPLATE.format(protein=protein, mutation=mutation)
        
        logger.info(f"Requesting rescue candidates from Gemini for {protein} {mutation}")
        response = client.models.generate_content(
            model=settings.gemini_model_discovery,
            contents=prompt
        )
        
        # Handle different response formats (new API might use different attribute)
        if hasattr(response, 'text'):
            candidates_json = response.text.strip()
        elif hasattr(response, 'content'):
            candidates_json = str(response.content).strip()
        else:
            # Try to get text from response object
            candidates_json = str(response).strip()
        
        # Remove markdown code blocks if present
        if "```json" in candidates_json:
            candidates_json = candidates_json.split("```json")[1].split("```")[0]
        elif "```" in candidates_json:
            candidates_json = candidates_json.split("```")[1].split("```")[0]
        
        candidates = json.loads(candidates_json.strip())
        
        if not isinstance(candidates, list):
            raise ValueError("Gemini response is not a list")
        
        logger.info(f"Received {len(candidates)} candidates from Gemini")
        return candidates
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        if 'response' in locals():
            response_text = getattr(response, 'text', getattr(response, 'content', str(response)))
            logger.error(f"Response text: {response_text}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise Exception(f"Failed to get rescue candidates from Gemini: {e}")


def final_validation(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gemini reviews structural metrics and literature reasoning to approve candidates.
    
    Args:
        candidates: List of candidate dictionaries with validation scores
    
    Returns:
        Dictionary with 'approved' list and 'summary' string
    
    Raises:
        Exception: If Gemini API call fails or response cannot be parsed
    """
    try:
        prompt = VALIDATION_PROMPT_TEMPLATE.format(data=json.dumps(candidates, indent=2))
        
        logger.info(f"Requesting final validation from Gemini for {len(candidates)} candidates")
        response = client.models.generate_content(
            model=settings.gemini_model_validation,
            contents=prompt
        )
        
        # Handle different response formats (new API might use different attribute)
        if hasattr(response, 'text'):
            result = response.text.strip()
        elif hasattr(response, 'content'):
            result = str(response.content).strip()
        else:
            # Try to get text from response object
            result = str(response).strip()
        
        # Remove markdown code blocks if present
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        validation_result = json.loads(result.strip())
        
        if not isinstance(validation_result, dict) or "approved" not in validation_result:
            raise ValueError("Gemini response missing 'approved' field")
        
        logger.info(f"Gemini approved {len(validation_result.get('approved', []))} candidates")
        return validation_result
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini validation response as JSON: {e}")
        if 'response' in locals():
            response_text = getattr(response, 'text', getattr(response, 'content', str(response)))
            logger.error(f"Response text: {response_text}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    except Exception as e:
        logger.error(f"Gemini API error during validation: {e}")
        raise Exception(f"Failed to get final validation from Gemini: {e}")

