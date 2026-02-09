"""Service for structure prediction and RMSD analysis."""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
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
    candidates: List[Dict[str, Any]],
    save_results_to: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], str, str]:
    """
    Predict structures for wild-type, pathogenic, and rescued sequences, then calculate RMSD.

    Args:
        wt_sequence: Wild-type protein sequence
        mutant_sequence: Mutant protein sequence (pathogenic)
        candidates: List of validated candidates to analyze
        save_results_to: Optional directory to save PDB files and rmsd_results.json

    Returns:
        Tuple of (analyzed_candidates, pathogenic_pdb, wt_pdb)
    """
    if not candidates:
        logger.warning("No candidates provided for analysis")
        return [], "", ""
    try:
        logger.info("Predicting mutant structure with ESMFold (baseline for RMSD)")
        mutant_pdb = predict_structure(mutant_sequence)
        pathogenic_pdb = mutant_pdb

        logger.info("Predicting wild-type structure (for reference)")
        wt_pdb = predict_structure(wt_sequence)

        # Calculate WT vs Pathogenic RMSD (once, shared across candidates)
        logger.debug("Calculating RMSD between WT and pathogenic structures")
        try:
            rmsd_wt_vs_pathogenic = round(calculate_rmsd(wt_pdb, pathogenic_pdb), 2)
        except Exception as e:
            logger.warning(f"Failed to calculate RMSD between WT and pathogenic structures: {e}")
            rmsd_wt_vs_pathogenic = None

        out_dir = Path(save_results_to) if save_results_to else None
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "mutant.pdb").write_text(mutant_pdb)
            (out_dir / "wild_type.pdb").write_text(wt_pdb)
            logger.info(f"Saved mutant.pdb and wild_type.pdb to {out_dir}")
        analyzed_candidates = []

        for i, candidate in enumerate(candidates):
            try:
                mut = candidate.get("mutation", "unknown")
                logger.info(f"Analyzing candidate {i+1}/{len(candidates)}: {mut}")

                position = candidate["position"] - 1
                rescue_aa = candidate["rescue_aa"]
                rescue_seq = apply_mutation(mutant_sequence, position, rescue_aa)

                rescue_pdb = predict_structure(rescue_seq)

                # Store PDB structures in candidate
                candidate["pdb_structure"] = rescue_pdb
                candidate["pathogenic_pdb_structure"] = pathogenic_pdb

                # Extract pLDDT scores
                rescue_plddt_scores = extract_plddt_scores(rescue_pdb)
                candidate["mean_plddt"] = round(calculate_mean_plddt(rescue_pdb), 2)
                candidate["plddt_at_mutation"] = round(rescue_plddt_scores.get(candidate["position"], 0.0), 2) if rescue_plddt_scores else None

                # Calculate RMSD values
                logger.debug(f"Calculating RMSD for {candidate.get('mutation', 'unknown')}")
                try:
                    rmsd_wt_vs_rescue = round(calculate_rmsd(wt_pdb, rescue_pdb), 2)
                except Exception as e:
                    logger.warning(f"Failed to calculate RMSD for {candidate.get('mutation', 'unknown')}: {e}")
                    rmsd_wt_vs_rescue = None
                rmsd_vs_mutant = calculate_rmsd(mutant_pdb, rescue_pdb)

                candidate["rmsd"] = round(rmsd_vs_mutant, 2)
                candidate["rmsd_vs_mutant"] = round(rmsd_vs_mutant, 2)
                candidate["rmsd_vs_wt"] = rmsd_wt_vs_rescue
                candidate["rmsd_wt_vs_pathogenic"] = rmsd_wt_vs_pathogenic
                candidate["rmsd_wt_vs_rescue"] = rmsd_wt_vs_rescue

                # Low RMSD(rescue vs mutant) = good structural recovery
                candidate["structural_recovery"] = (
                    "good" if rmsd_vs_mutant < settings.rmsd_good_threshold else "poor"
                )

                # Generate structure overlay visualization
                mutation_positions = [candidate["position"]]
                overlay_image = generate_structure_overlay(wt_pdb, rescue_pdb, mutation_positions)
                if overlay_image:
                    candidate["overlay_image"] = overlay_image

                logger.info(
                    f"Candidate {mut}: RMSD vs mutant={rmsd_vs_mutant:.2f}Å, "
                    f"vs WT={rmsd_wt_vs_rescue or 'N/A'}, "
                    f"pLDDT={candidate.get('mean_plddt', 'N/A')}, "
                    f"recovery={candidate['structural_recovery']}"
                )

                if out_dir:
                    safe_name = mut.replace(" ", "_")
                    (out_dir / f"rescue_{safe_name}.pdb").write_text(rescue_pdb)

                analyzed_candidates.append(candidate)

            except Exception as e:
                logger.error(f"Error analyzing candidate {candidate.get('mutation', 'unknown')}: {e}")
                candidate["rmsd"] = None
                candidate["rmsd_wt_vs_rescue"] = None
                candidate["rmsd_wt_vs_pathogenic"] = None
                candidate["structural_recovery"] = "error"
                candidate["error"] = str(e)
                analyzed_candidates.append(candidate)

        if out_dir:
            summary = {
                "candidates": [
                    {
                        "mutation": c.get("mutation"),
                        "rmsd_vs_mutant": c.get("rmsd_vs_mutant"),
                        "rmsd_vs_wt": c.get("rmsd_vs_wt"),
                        "rmsd": c.get("rmsd"),
                        "structural_recovery": c.get("structural_recovery"),
                        "esm_score": c.get("esm_score"),
                    }
                    for c in analyzed_candidates
                ]
            }
            (out_dir / "rmsd_results.json").write_text(json.dumps(summary, indent=2))
            logger.info(f"Saved rmsd_results.json to {out_dir}")

        logger.info(f"Analysis complete: {len(analyzed_candidates)} candidates analyzed")
        return analyzed_candidates, pathogenic_pdb, wt_pdb

    except Exception as e:
        logger.error(f"Failed to predict and analyze structures: {e}")
        raise Exception(f"Structure analysis failed: {e}")

