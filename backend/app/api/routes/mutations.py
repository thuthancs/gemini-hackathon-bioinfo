"""API routes for mutation analysis."""
import logging
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.services.orchestrator import run_full_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(tags=["mutations"])


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_mutation(request: AnalysisRequest):
    """
    Analyze a mutation and find potential rescue mutations.
    
    This endpoint runs the complete 6-phase pipeline:
    1. Creates mutant sequence
    2. Discovers rescue candidates with Gemini
    3. Validates candidates with ESM-1v
    4. Predicts structures with ESMFold
    5. Calculates RMSD
    6. Final validation with Gemini
    
    Args:
        request: AnalysisRequest with sequence, mutation, and optional protein name
    
    Returns:
        AnalysisResponse with discovered candidates and final results
    
    Raises:
        HTTPException: If request validation fails or pipeline errors occur
    """
    try:
        logger.info(f"Analyzing mutation request: {request.mutation} for {request.protein}")
        
        # Validate sequence
        from app.utils.sequence_utils import validate_sequence
        if not validate_sequence(request.sequence):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sequence: contains invalid amino acid characters"
            )
        
        # Run pipeline
        result = await run_full_pipeline(
            sequence=request.sequence,
            mutation=request.mutation,
            protein=request.protein,
            gene_function=request.gene_function,
            disease=request.disease,
            organism=request.organism
        )
        
        # Check for errors
        if "error" in result:
            logger.error(f"Pipeline error: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        # Convert to response model
        response = AnalysisResponse(**result)
        logger.info(f"Analysis complete: {response.candidates_validated} candidates validated")
        return response
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in analyze_mutation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

