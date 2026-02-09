"""Service for interacting with ESM-1v API."""
import logging
from typing import List, Dict, Any
import requests
from app.config import settings

logger = logging.getLogger(__name__)


def validate_with_esm(mutant_sequence: str, candidates: List[Dict[str, Any]], top_n: int = None) -> List[Dict[str, Any]]:
    """
    Validate rescue candidates using ESM-1v by checking if the model predicts
    the rescue amino acid with high probability at the masked position.
    
    Returns the top N candidates ranked by ESM-1v score (highest first).
    
    Args:
        mutant_sequence: Mutant protein sequence
        candidates: List of candidate dictionaries with position and rescue_aa
        top_n: Number of top-scoring candidates to return (defaults to settings.esm_top_n)
    
    Returns:
        List of top N validated candidates (sorted by esm_score, highest first)
        with esm_score and status added
    
    Raises:
        Exception: If ESM API call fails
    """
    if top_n is None:
        top_n = settings.esm_top_n
    
    url = settings.esm_api_url
    headers = {
        "Authorization": f"Token {settings.esm_api_key}",
        "Content-Type": "application/json"
    }
    
    scored = []
    for candidate in candidates:
        try:
            position = candidate["position"] - 1  # Convert to 0-indexed
            target_aa = candidate["rescue_aa"]

            if position < 0 or position >= len(mutant_sequence):
                logger.warning(f"Position {position + 1} out of range for candidate {candidate.get('mutation', 'unknown')}")
                candidate["esm_score"] = 0.0
                candidate["status"] = "error"
                continue

            # Create masked sequence (mask the rescue position)
            masked_seq = list(mutant_sequence)
            masked_seq[position] = '<mask>'
            masked_seq = ''.join(masked_seq)

            # Call ESM-1v API
            payload = {
                "params": {"model_number": "all"},
                "items": [{"sequence": masked_seq}]
            }

            logger.debug(f"Calling ESM-1v API for position {position + 1}, target {target_aa}")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()
            target_prob = 0.0

            if isinstance(result, dict) and 'results' in result:
                results_list = result.get('results', [])
                if len(results_list) > 0:
                    first_result = results_list[0]

                    predictions_list = None
                    if 'esm1v-all' in first_result:
                        predictions_list = first_result['esm1v-all']
                    else:
                        all_predictions = {}
                        for key in ['esm1v-n1', 'esm1v-n2', 'esm1v-n3', 'esm1v-n4', 'esm1v-n5']:
                            if key in first_result and isinstance(first_result[key], list):
                                for pred in first_result[key]:
                                    if isinstance(pred, dict):
                                        aa = pred.get('token_str')
                                        score = pred.get('score', 0)
                                        if aa:
                                            if aa not in all_predictions:
                                                all_predictions[aa] = []
                                            all_predictions[aa].append(score)

                        if all_predictions:
                            predictions_list = [
                                {'token_str': aa, 'score': sum(s) / len(s)}
                                for aa, s in all_predictions.items()
                            ]

                    if predictions_list and isinstance(predictions_list, list):
                        for pred in predictions_list:
                            if isinstance(pred, dict) and pred.get('token_str') == target_aa:
                                target_prob = pred.get('score', 0)
                                break

            if target_prob == 0.0:
                logger.warning(f"Could not extract probability for {target_aa} at position {position + 1}")

            candidate["esm_score"] = round(float(target_prob), 3)
            candidate["status"] = "scored"

        except requests.exceptions.RequestException as e:
            logger.error(f"ESM API request failed for candidate {candidate.get('mutation', 'unknown')}: {e}")
            candidate["esm_score"] = 0.0
            candidate["status"] = "error"
        except Exception as e:
            logger.error(f"Error validating candidate {candidate.get('mutation', 'unknown')}: {e}")
            candidate["esm_score"] = 0.0
            candidate["status"] = "error"

    # Rank by score and take top N
    scored_candidates = [c for c in candidates if c.get("status") != "error" and c.get("esm_score", 0) > 0]
    scored_candidates.sort(key=lambda x: x.get("esm_score", 0), reverse=True)
    validated = scored_candidates[:top_n]

    for candidate in validated:
        candidate["status"] = "validated"
        logger.info(f"Candidate {candidate.get('mutation', 'unknown')} validated with score {candidate.get('esm_score', 0):.3f} (ranked in top {top_n})")

    for candidate in scored_candidates[top_n:]:
        candidate["status"] = "rejected"

    for candidate in candidates:
        if candidate.get("status") == "error":
            candidate["status"] = "rejected"

    logger.info(f"ESM validation complete: {len(validated)}/{len(candidates)} candidates validated (top {top_n} by score)")
    return validated

