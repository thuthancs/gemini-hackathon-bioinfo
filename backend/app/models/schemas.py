"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class AnalysisRequest(BaseModel):
    """Request model for mutation analysis."""
    sequence: str = Field(..., description="Wild-type protein sequence (amino acids)")
    mutation: str = Field(..., description="Mutation in format like 'R249S'")
    protein: Optional[str] = Field(default="TP53", description="Protein name (optional)")
    gene_function: Optional[str] = Field(None, description="Protein function description")
    disease: Optional[str] = Field(None, description="Disease context")
    organism: Optional[str] = Field(None, description="Organism name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sequence": "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD",
                "mutation": "R249S",
                "protein": "TP53"
            }
        }


class Candidate(BaseModel):
    """Model for a rescue mutation candidate."""
    position: int = Field(..., description="Amino acid position (1-indexed)")
    original_aa: str = Field(..., description="Original amino acid at this position")
    rescue_aa: str = Field(..., description="Rescue amino acid")
    mutation: str = Field(..., description="Mutation notation (e.g., 'H168R')")
    reasoning: str = Field(..., description="Literature-based reasoning for this candidate")
    esm_score: Optional[float] = Field(None, description="ESM-1v validation score")
    rmsd: Optional[float] = Field(None, description="RMSD value in Angstroms (deprecated, use rmsd_wt_vs_rescue)")
    status: Optional[str] = Field(None, description="Validation status: 'validated', 'rejected', or 'approved'")
    structural_recovery: Optional[str] = Field(None, description="Structural recovery assessment: 'good' or 'poor'")
    pdb_structure: Optional[str] = Field(None, description="PDB structure data for the rescued sequence")
    confidence: Optional[float] = Field(None, description="Gemini confidence score (0-1)")
    literature_support: Optional[str] = Field(None, description="Literature references (e.g., PMIDs)")
    structural_basis: Optional[str] = Field(None, description="Structural explanation for the rescue mutation")
    mean_plddt: Optional[float] = Field(None, description="Mean pLDDT confidence score")
    plddt_at_mutation: Optional[float] = Field(None, description="pLDDT score at mutation site")
    rmsd_wt_vs_pathogenic: Optional[float] = Field(None, description="RMSD between wild-type and pathogenic structures")
    rmsd_wt_vs_rescue: Optional[float] = Field(None, description="RMSD between wild-type and rescue structures")
    pathogenic_pdb_structure: Optional[str] = Field(None, description="Pathogenic structure PDB data")
    overlay_image: Optional[str] = Field(None, description="Base64-encoded structure overlay image")


class FinalValidationResult(BaseModel):
    """Model for final validation results from Gemini."""
    approved: List[Candidate] = Field(..., description="List of approved rescue candidates")
    validated: Optional[List[Candidate]] = Field(None, description="List of validated candidates (passed ESM but not approved)")
    summary: str = Field(..., description="Summary explanation of approvals")
    overall_verdict: Optional[str] = Field(None, description="Overall verdict: APPROVED/APPROVED_WITH_CAUTION/REJECTED")
    risk_score: Optional[float] = Field(None, description="Risk score (0-10, lower is safer)")
    structural_restoration: Optional[Dict[str, Any]] = Field(None, description="Structural restoration analysis details")
    aggregation_risk: Optional[Dict[str, Any]] = Field(None, description="Aggregation risk assessment")
    functional_preservation: Optional[Dict[str, Any]] = Field(None, description="Functional preservation analysis")
    amyloid_risk: Optional[Dict[str, Any]] = Field(None, description="Amyloid formation risk assessment")
    recommendations: Optional[List[str]] = Field(None, description="Experimental validation recommendations")
    warnings: Optional[List[str]] = Field(None, description="Warnings and caveats")


class AnalysisResponse(BaseModel):
    """Response model for mutation analysis."""
    original_mutation: str = Field(..., description="Original mutation that was analyzed")
    candidates_discovered: int = Field(..., description="Number of candidates discovered by Gemini")
    candidates_validated: int = Field(..., description="Number of candidates that passed ESM-1v validation")
    results: Dict[str, Any] = Field(..., description="Final validation results with approved candidates")
    wt_pdb_structure: Optional[str] = Field(None, description="Wild-type PDB structure data")
    pathogenic_pdb_structure: Optional[str] = Field(None, description="Pathogenic PDB structure data")
    error: Optional[str] = Field(None, description="Error message if pipeline failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_mutation": "R249S",
                "candidates_discovered": 5,
                "candidates_validated": 3,
                "results": {
                    "approved": [
                        {
                            "position": 168,
                            "original_aa": "H",
                            "rescue_aa": "R",
                            "mutation": "H168R",
                            "reasoning": "Compensatory mutation based on literature",
                            "esm_score": 0.75,
                            "rmsd": 1.5,
                            "status": "approved",
                            "structural_recovery": "good"
                        }
                    ],
                    "summary": "Approved candidates show good structural recovery and high ESM scores"
                }
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(default="ok", description="Health status")
    api_keys_configured: Optional[bool] = Field(None, description="Whether API keys are configured")

