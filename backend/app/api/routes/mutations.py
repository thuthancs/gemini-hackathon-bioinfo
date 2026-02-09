"""API routes for mutation analysis."""
import logging
import re
from fastapi import APIRouter, HTTPException, Request, status
from app.config import settings
from app.limiter import limiter
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    CreateMutantRequest,
    CreateMutantResponse,
)
from app.services.orchestrator import run_full_pipeline
from app.utils.sequence_utils import create_mutant, validate_sequence

logger = logging.getLogger(__name__)

router = APIRouter(tags=["mutations"])


@router.post("/create-mutant", response_model=CreateMutantResponse, status_code=status.HTTP_200_OK)
@limiter.limit(settings.rate_limit_create_mutant)
async def create_mutant_sequence(request: Request, body: CreateMutantRequest):
    """
    Phase 0 only: Create mutant sequence from wild-type. No API keys needed.
    """
    if not validate_sequence(body.sequence):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sequence: contains invalid amino acid characters",
        )
    try:
        mutant = create_mutant(body.sequence, body.mutation)
        m = re.match(r"^([A-Z])(\d+)([A-Z])$", body.mutation)
        if not m:
            raise HTTPException(status_code=400, detail=f"Invalid mutation format: {body.mutation}")
        orig_aa, pos_str, new_aa = m.groups()
        return CreateMutantResponse(
            mutation=body.mutation,
            wild_type_sequence=body.sequence,
            mutant_sequence=mutant,
            position=int(pos_str),
            original_aa=orig_aa,
            new_aa=new_aa,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
@limiter.limit(settings.rate_limit_analyze)
async def analyze_mutation(request: Request, body: AnalysisRequest):
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
        logger.info(f"Analyzing mutation request: {body.mutation} for {body.protein}")
        
        # Validate sequence
        if not validate_sequence(body.sequence):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sequence: contains invalid amino acid characters"
            )
        
        # Run pipeline
        result = await run_full_pipeline(
            sequence=body.sequence,
            mutation=body.mutation,
            protein=body.protein,
            gene_function=body.gene_function,
            disease=body.disease,
            organism=body.organism
        )
        
        # Check for errors
        if "error" in result:
            logger.error(f"Pipeline error: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analysis failed. Please try again later.",
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
            detail="An unexpected error occurred. Please try again later.",
        )

