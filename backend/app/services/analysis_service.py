"""Service for structure prediction and RMSD analysis."""
import logging
from typing import List, Dict, Any, Tuple
from app.services.esmfold_service import predict_structure
from app.utils.structure_utils import (
    calculate_rmsd,
    extract_plddt_scores,
    calculate_mean_plddt,
    generate_structure_overlay
)
from app.utils.sequence_utils import apply_mutation
from app.config import settings

logger = logging.getLogger(__name__)


def predict_and_analyze(
    wt_sequence: str,
    mutant_sequence: str,
    candidates: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Predict structures for wild-type, pathogenic, and rescued sequences, then calculate RMSD.
    
    Args:
        wt_sequence: Wild-type protein sequence
        mutant_sequence: Mutant protein sequence (pathogenic)
        candidates: List of validated candidates to analyze
    
    Returns:
        Tuple of (analyzed_candidates, pathogenic_pdb)
        - analyzed_candidates: List of candidates with rmsd and structural_recovery added
        - pathogenic_pdb: PDB structure for the pathogenic mutant
    
    Raises:
        Exception: If structure prediction or RMSD calculation fails
    """
    if not candidates:
        logger.warning("No candidates provided for analysis")
        return [], ""
    
    try:
        # Get wild-type structure
        logger.info("Predicting wild-type structure with ESMFold")
        wt_pdb = predict_structure(wt_sequence)
        
        # Get pathogenic structure
        logger.info("Predicting pathogenic structure with ESMFold")
        pathogenic_pdb = predict_structure(mutant_sequence)
        
        # Calculate WT vs Pathogenic RMSD (once, shared across candidates)
        logger.debug("Calculating RMSD between WT and pathogenic structures")
        try:
            # #region agent log
            try:
                import os, json, time
                log_path = '/Users/thananhthu/gemini-hackathon-bioinfo/.cursor/debug.log'
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                with open(log_path, 'a') as f:
                    f.write(json.dumps({"location":"analysis_service.py:52","message":"Before RMSD calculation WT vs Pathogenic","data":{"wt_pdb_length":len(wt_pdb) if wt_pdb else 0,"pathogenic_pdb_length":len(pathogenic_pdb) if pathogenic_pdb else 0,"wt_pdb_first_100":wt_pdb[:100] if wt_pdb else None,"pathogenic_pdb_first_100":pathogenic_pdb[:100] if pathogenic_pdb else None},"timestamp":int(time.time()*1000),"runId":"pre-fix","hypothesisId":"A"})+'\n')
            except: pass
            # #endregion
            rmsd_wt_vs_pathogenic = round(calculate_rmsd(wt_pdb, pathogenic_pdb), 2)
            # #region agent log
            try:
                import os, json, time
                log_path = '/Users/thananhthu/gemini-hackathon-bioinfo/.cursor/debug.log'
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                with open(log_path, 'a') as f:
                    f.write(json.dumps({"location":"analysis_service.py:60","message":"RMSD calculation succeeded WT vs Pathogenic","data":{"rmsd":rmsd_wt_vs_pathogenic},"timestamp":int(time.time()*1000),"runId":"pre-fix","hypothesisId":"B"})+'\n')
            except: pass
            # #endregion
        except Exception as e:
            # #region agent log
            try:
                import os, json, time
                log_path = '/Users/thananhthu/gemini-hackathon-bioinfo/.cursor/debug.log'
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                with open(log_path, 'a') as f:
                    f.write(json.dumps({"location":"analysis_service.py:63","message":"RMSD calculation failed WT vs Pathogenic","data":{"error":str(e),"error_type":type(e).__name__,"wt_pdb_length":len(wt_pdb) if wt_pdb else 0,"pathogenic_pdb_length":len(pathogenic_pdb) if pathogenic_pdb else 0},"timestamp":int(time.time()*1000),"runId":"pre-fix","hypothesisId":"C"})+'\n')
            except: pass
            # #endregion
            logger.warning(f"Failed to calculate RMSD between WT and pathogenic structures: {e}")
            rmsd_wt_vs_pathogenic = None
        
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
                
                # Store PDB structures in candidate
                candidate["pdb_structure"] = rescue_pdb
                candidate["pathogenic_pdb_structure"] = pathogenic_pdb
                
                # Extract pLDDT scores
                rescue_plddt_scores = extract_plddt_scores(rescue_pdb)
                candidate["mean_plddt"] = round(calculate_mean_plddt(rescue_pdb), 2)
                candidate["plddt_at_mutation"] = round(rescue_plddt_scores.get(candidate["position"], 0.0), 2) if rescue_plddt_scores else None
                
                # Calculate RMSD between WT and rescued structure
                logger.debug(f"Calculating RMSD for {candidate.get('mutation', 'unknown')}")
                try:
                    rmsd_wt_vs_rescue = round(calculate_rmsd(wt_pdb, rescue_pdb), 2)
                except Exception as e:
                    logger.warning(f"Failed to calculate RMSD for {candidate.get('mutation', 'unknown')}: {e}")
                    rmsd_wt_vs_rescue = None
                
                # Store RMSD values (keep old field for backward compatibility)
                candidate["rmsd"] = rmsd_wt_vs_rescue
                candidate["rmsd_wt_vs_pathogenic"] = rmsd_wt_vs_pathogenic
                candidate["rmsd_wt_vs_rescue"] = rmsd_wt_vs_rescue
                
                # Low RMSD = structure similar to WT = good rescue
                if rmsd_wt_vs_rescue is not None and rmsd_wt_vs_rescue < settings.rmsd_good_threshold:
                    candidate["structural_recovery"] = "good"
                elif rmsd_wt_vs_rescue is None:
                    candidate["structural_recovery"] = "unavailable"
                else:
                    candidate["structural_recovery"] = "poor"
                
                # Generate structure overlay visualization
                mutation_positions = [candidate["position"]]
                overlay_image = generate_structure_overlay(wt_pdb, rescue_pdb, mutation_positions)
                if overlay_image:
                    candidate["overlay_image"] = overlay_image
                
                rmsd_pathogenic_str = f"{rmsd_wt_vs_pathogenic:.2f}Å" if rmsd_wt_vs_pathogenic is not None else "N/A"
                rmsd_rescue_str = f"{rmsd_wt_vs_rescue:.2f}Å" if rmsd_wt_vs_rescue is not None else "N/A"
                logger.info(
                    f"Candidate {candidate.get('mutation', 'unknown')}: "
                    f"RMSD(WT vs Pathogenic)={rmsd_pathogenic_str}, "
                    f"RMSD(WT vs Rescue)={rmsd_rescue_str}, "
                    f"pLDDT={candidate.get('mean_plddt', 'N/A')}, "
                    f"recovery={candidate['structural_recovery']}"
                )
                
                analyzed_candidates.append(candidate)
            
            except Exception as e:
                logger.error(f"Error analyzing candidate {candidate.get('mutation', 'unknown')}: {e}")
                candidate["rmsd"] = None
                candidate["rmsd_wt_vs_rescue"] = None
                candidate["rmsd_wt_vs_pathogenic"] = None
                candidate["structural_recovery"] = "error"
                candidate["error"] = str(e)
                analyzed_candidates.append(candidate)
        
        logger.info(f"Analysis complete: {len(analyzed_candidates)} candidates analyzed")
        return analyzed_candidates, pathogenic_pdb
    
    except Exception as e:
        logger.error(f"Failed to predict and analyze structures: {e}")
        raise Exception(f"Structure analysis failed: {e}")

