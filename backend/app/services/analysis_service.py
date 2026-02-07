"""Service for structure prediction and RMSD analysis."""
import logging
from typing import List, Dict, Any
from app.services.esmfold_service import predict_structure
from app.utils.structure_utils import calculate_rmsd
from app.utils.sequence_utils import apply_mutation
from app.config import settings

logger = logging.getLogger(__name__)


def predict_and_analyze(
    wt_sequence: str,
    mutant_sequence: str,
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Predict structures for wild-type and rescued sequences, then calculate RMSD.
    
    Args:
        wt_sequence: Wild-type protein sequence
        mutant_sequence: Mutant protein sequence
        candidates: List of validated candidates to analyze
    
    Returns:
        List of candidates with rmsd and structural_recovery added
    
    Raises:
        Exception: If structure prediction or RMSD calculation fails
    """
    if not candidates:
        logger.warning("No candidates provided for analysis")
        return []
    
    try:
        # Get wild-type structure
        logger.info("Predicting wild-type structure with ESMFold")
        wt_pdb = predict_structure(wt_sequence)
        
        analyzed_candidates = []
        
        for i, candidate in enumerate(candidates):
            try:
                logger.info(f"Analyzing candidate {i+1}/{len(candidates)}: {candidate.get('mutation', 'unknown')}")
                
                # Apply rescue mutation to mutant sequence
                position = candidate["position"] - 1  # Convert to 0-indexed
                rescue_aa = candidate["rescue_aa"]
                rescue_seq = apply_mutation(mutant_sequence, position, rescue_aa)
                
                # Get rescued structure
                logger.debug(f"Predicting rescued structure for {candidate.get('mutation', 'unknown')}")
                rescue_pdb = predict_structure(rescue_seq)
                
                # Store PDB structure in candidate
                candidate["pdb_structure"] = rescue_pdb
                
                # Calculate RMSD between WT and rescued structure
                logger.debug(f"Calculating RMSD for {candidate.get('mutation', 'unknown')}")
                rmsd = calculate_rmsd(wt_pdb, rescue_pdb)
                
                candidate["rmsd"] = round(rmsd, 2)
                
                # Low RMSD = structure similar to WT = good rescue
                if rmsd < settings.rmsd_good_threshold:
                    candidate["structural_recovery"] = "good"
                else:
                    candidate["structural_recovery"] = "poor"
                
                logger.info(
                    f"Candidate {candidate.get('mutation', 'unknown')}: "
                    f"RMSD={rmsd:.2f}Å, recovery={candidate['structural_recovery']}"
                )
                
                analyzed_candidates.append(candidate)
            
            except Exception as e:
                logger.error(f"Error analyzing candidate {candidate.get('mutation', 'unknown')}: {e}")
                candidate["rmsd"] = None
                candidate["structural_recovery"] = "error"
                candidate["error"] = str(e)
                analyzed_candidates.append(candidate)
        
        logger.info(f"Analysis complete: {len(analyzed_candidates)} candidates analyzed")
        return analyzed_candidates
    
    except Exception as e:
        logger.error(f"Failed to predict and analyze structures: {e}")
        raise Exception(f"Structure analysis failed: {e}")

