"""Service for interacting with ESMFold API for structure prediction."""
import logging
import time
import requests
from app.config import settings

logger = logging.getLogger(__name__)

# Full-length sequences (e.g. 400 aa) can take 5-10 min; gateway may timeout
ESMFOLD_TIMEOUT = 600  # 10 min
ESMFOLD_RETRIES = 3
ESMFOLD_RETRY_DELAY = 30


def predict_structure(sequence: str, timeout: int = ESMFOLD_TIMEOUT) -> str:
    """
    Call ESMFold API to predict protein structure.
    Retries on 504 Gateway Timeout (common for long sequences).

    Args:
        sequence: Protein sequence (amino acids)
        timeout: Request timeout in seconds (default: 600)

    Returns:
        PDB format structure as string

    Raises:
        Exception: If ESMFold API call fails after retries
    """
    url = settings.esmfold_api_url
    last_error = None

    for attempt in range(1, ESMFOLD_RETRIES + 1):
        try:
            logger.info(
                f"Calling ESMFold for sequence of length {len(sequence)} "
                f"(attempt {attempt}/{ESMFOLD_RETRIES})"
            )
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
            last_error = f"ESMFold API timeout after {timeout} seconds"
            logger.warning(f"{last_error} (attempt {attempt})")
        except requests.exceptions.HTTPError as e:
            last_error = str(e)
            if e.response is not None and e.response.status_code == 504:
                logger.warning(f"ESMFold 504 Gateway Timeout (attempt {attempt})")
                if attempt < ESMFOLD_RETRIES:
                    logger.info(f"Retrying in {ESMFOLD_RETRY_DELAY}s...")
                    time.sleep(ESMFOLD_RETRY_DELAY)
            else:
                raise Exception(f"ESMFold API error: {last_error}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"ESMFold API error: {e}")

    raise Exception(
        f"ESMFold failed after {ESMFOLD_RETRIES} attempts. {last_error} "
        "Long sequences may hit server limits on free API."
    )

