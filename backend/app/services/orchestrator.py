"""Main orchestrator service that coordinates all pipeline phases."""
import logging
from typing import Dict, Any, Optional
from app.services.gemini_service import get_rescue_candidates, final_validation
from app.services.esm_service import validate_with_esm
from app.services.analysis_service import predict_and_analyze
from app.utils.sequence_utils import create_mutant

logger = logging.getLogger(__name__)


async def run_full_pipeline(
    sequence: str,
    mutation: str,
    protein: str = "TP53",
    gene_function: Optional[str] = None,
    disease: Optional[str] = None,
    organism: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute the complete 6-phase mutation rescue pipeline.
    
    Phase 0: Create mutant sequence
    Phase 1: Gemini discovers rescue candidates
    Phase 2: ESM-1v validates candidates
    Phase 3: ESMFold predicts structures
    Phase 4: Calculate RMSD
    Phase 5: Gemini final validation
    
    Args:
        sequence: Wild-type protein sequence
        mutation: Mutation string (e.g., "R249S")
        protein: Protein name (default: "TP53")
    
    Returns:
        Dictionary with pipeline results including candidates and final validation
    """
    try:
        logger.info(f"Starting pipeline for {protein} {mutation}")
        
        # Phase 0: Create mutant sequence
        logger.info("Phase 0: Creating mutant sequence")
        try:
            mutant_seq = create_mutant(sequence, mutation)
            logger.info(f"Mutant sequence created (length: {len(mutant_seq)})")
        except Exception as e:
            logger.error(f"Phase 0 failed: {e}")
            return {
                "error": f"Failed to create mutant sequence: {str(e)}",
                "original_mutation": mutation,
                "candidates_discovered": 0,
                "candidates_validated": 0,
                "results": {},
                "wt_pdb_structure": None
            }
        
        # Phase 1: Gemini discovers candidates
        logger.info("Phase 1: Discovering rescue candidates with Gemini")
        candidates = []
        try:
            candidates = get_rescue_candidates(
                mutation=mutation,
                protein=protein,
                gene_function=gene_function,
                disease=disease,
                organism=organism,
                wild_type_sequence=sequence,
                mutant_sequence=mutant_seq  # Available after Phase 0
            )
            logger.info(f"Phase 1 complete: {len(candidates)} candidates discovered")
        except Exception as e:
            error_str = str(e)
            # Check if it's a 503/overloaded error - treat as "no candidates" and continue
            # Also check for the specific prefix we added in gemini_service
            if "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower() or "503_UNAVAILABLE" in error_str:
                logger.warning(f"Gemini API unavailable (503/overloaded): {error_str}. Continuing with empty candidates for demo.")
                candidates = []  # Continue with empty candidates
            else:
                logger.error(f"Phase 1 failed: {e}")
                return {
                    "error": f"Failed to discover candidates: {str(e)}",
                    "original_mutation": mutation,
                    "candidates_discovered": 0,
                    "candidates_validated": 0,
                    "results": {},
                    "wt_pdb_structure": None
                }
        
        if not candidates:
            logger.warning("No candidates discovered in Phase 1")
            # Still get WT structure for potential future use
            from app.services.esmfold_service import predict_structure
            wt_pdb = predict_structure(sequence)
            return {
                "original_mutation": mutation,
                "candidates_discovered": 0,
                "candidates_validated": 0,
                "results": {
                    "approved": [],
                    "summary": "No rescue candidates were discovered"
                },
                "wt_pdb_structure": wt_pdb
            }
        
        # Phase 2: ESM-1v validates candidates
        logger.info("Phase 2: Validating candidates with ESM-1v")
        try:
            validated = validate_with_esm(mutant_seq, candidates)
            logger.info(f"Phase 2 complete: {len(validated)}/{len(candidates)} candidates validated")
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            return {
                "error": f"Failed to validate candidates: {str(e)}",
                "original_mutation": mutation,
                "candidates_discovered": len(candidates),
                "candidates_validated": 0,
                "results": {},
                "wt_pdb_structure": None
            }
        
        if not validated:
            logger.warning("No candidates passed ESM-1v validation")
            # Generate both WT and pathogenic structures for demo
            from app.services.esmfold_service import predict_structure
            from app.services.gemini_service import generate_mutation_validation
            logger.info("Generating WT and pathogenic structures for demo")
            wt_pdb = predict_structure(sequence)
            pathogenic_pdb = predict_structure(mutant_seq)
            
            # Generate demo validation analysis for the mutation itself
            logger.info("Generating mutation validation analysis for demo")
            try:
                demo_validation = generate_mutation_validation(
                    mutation=mutation,
                    gene_name=protein,
                    gene_function=gene_function,
                    disease=disease,
                    wt_pdb=wt_pdb,
                    pathogenic_pdb=pathogenic_pdb
                )
            except Exception as e:
                logger.error(f"Failed to generate demo validation: {e}")
                # Return basic structure even if validation fails
                demo_validation = {
                    "overall_verdict": "ANALYSIS_UNAVAILABLE",
                    "summary": f"Mutation validation analysis unavailable: {str(e)}"
                }
            
            return {
                "original_mutation": mutation,
                "candidates_discovered": len(candidates),
                "candidates_validated": 0,
                "results": {
                    "approved": [],
                    "summary": "No candidates passed ESM-1v validation. Showing mutation impact analysis instead.",
                    **demo_validation  # Include validation dimensions
                },
                "wt_pdb_structure": wt_pdb,
                "pathogenic_pdb_structure": pathogenic_pdb
            }
        
        # Phase 3 & 4: Structure prediction + RMSD
        logger.info("Phase 3 & 4: Predicting structures and calculating RMSD")
        try:
            # Get wild-type structure for comparison (will be reused in predict_and_analyze)
            from app.services.esmfold_service import predict_structure
            logger.info("Predicting wild-type structure with ESMFold")
            wt_pdb = predict_structure(sequence)
            
            analyzed, pathogenic_pdb = predict_and_analyze(sequence, mutant_seq, validated)
            logger.info(f"Phase 3 & 4 complete: {len(analyzed)} candidates analyzed")
        except Exception as e:
            logger.error(f"Phase 3 & 4 failed: {e}")
            # Try to get WT structure if we got that far
            wt_pdb = None
            pathogenic_pdb = None
            try:
                from app.services.esmfold_service import predict_structure
                wt_pdb = predict_structure(sequence)
                pathogenic_pdb = predict_structure(mutant_seq)
            except:
                pass
            return {
                "error": f"Failed to analyze structures: {str(e)}",
                "original_mutation": mutation,
                "candidates_discovered": len(candidates),
                "candidates_validated": len(validated),
                "results": {},
                "wt_pdb_structure": wt_pdb,
                "pathogenic_pdb_structure": pathogenic_pdb
            }
        
        # Phase 5: Gemini final review
        logger.info("Phase 5: Final validation with Gemini")
        try:
            final = final_validation(
                analyzed,
                gene_name=protein,
                pathogenic_mutation=mutation,
                gene_function=gene_function,
                disease=disease
            )
            logger.info(f"Phase 5 complete: {len(final.get('approved', []))} candidates approved")
        except Exception as e:
            logger.error(f"Phase 5 failed: {e}")
            # Return analyzed candidates even if final validation fails
            return {
                "original_mutation": mutation,
                "candidates_discovered": len(candidates),
                "candidates_validated": len(validated),
                "results": {
                    "approved": analyzed,
                    "validated": analyzed,
                    "summary": f"Final validation failed: {str(e)}. Returning all analyzed candidates."
                },
                "wt_pdb_structure": wt_pdb,
                "pathogenic_pdb_structure": pathogenic_pdb
            }
        
        logger.info("Pipeline complete successfully")
        # Include validated candidates for demo purposes (even if not approved)
        final_with_validated = {
            **final,
            "validated": analyzed  # Include all analyzed candidates for demo
        }
        return {
            "original_mutation": mutation,
            "candidates_discovered": len(candidates),
            "candidates_validated": len(validated),
            "results": final_with_validated,
            "wt_pdb_structure": wt_pdb,
            "pathogenic_pdb_structure": pathogenic_pdb
        }
    
    except Exception as e:
        logger.error(f"Pipeline failed with unexpected error: {e}", exc_info=True)
        return {
            "error": f"Pipeline failed: {str(e)}",
            "original_mutation": mutation,
            "candidates_discovered": 0,
            "candidates_validated": 0,
            "results": {},
            "wt_pdb_structure": None
        }

