"""Service for interacting with Google Gemini API."""
import json
import logging
from typing import List, Dict, Any, Optional
from google import genai
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Gemini API client
# The client automatically picks up GEMINI_API_KEY from environment
# But we pass it explicitly to use our settings
client = genai.Client(api_key=settings.gemini_api_key)

# Prompt templates
def build_discovery_prompt(
    mutation: str,
    protein: str,
    gene_function: Optional[str],
    disease: Optional[str],
    organism: Optional[str],
    wild_type_sequence: Optional[str],
    mutant_sequence: Optional[str]
) -> str:
    """Build rich discovery prompt with context."""
    prompt = f"""You are an expert in protein structure and compensatory mutations.

TASK: Identify potential RESCUE MUTATIONS for a pathogenic variant.

## GENE INFORMATION
- Gene: {protein}"""
    
    if gene_function:
        prompt += f"\n- Protein Function: {gene_function}"
    if disease:
        prompt += f"\n- Disease: {disease}"
    if organism:
        prompt += f"\n- Organism: {organism}"
    
    prompt += f"""

## PATHOGENIC MUTATION
- Mutation: {mutation}"""
    
    # Extract position and amino acids from mutation
    if len(mutation) >= 3:
        from_aa = mutation[0]
        to_aa = mutation[-1]
        try:
            position = ''.join([c for c in mutation[1:-1] if c.isdigit()])
            prompt += f"\n- Position: {position}"
            prompt += f"\n- Change: {from_aa} → {to_aa}"
        except:
            pass
    
    if wild_type_sequence:
        prompt += f"""

## PROTEIN SEQUENCE
Wild-type:
{wild_type_sequence}"""
    
    if mutant_sequence:
        prompt += f"""

Mutant (with {mutation}):
{mutant_sequence}"""
    
    prompt += """

## YOUR TASK

Based on:
1. Known compensatory mutations in literature
2. Structural biology principles
3. Protein chemistry and electrostatics
4. Known protein-protein interaction sites

Identify 3-5 potential rescue mutations that could:
- Restore wild-type-like structure
- Compensate for the pathogenic change
- Maintain protein function

## CONSTRAINTS
- Focus on positions within 15Å of mutation site (if known)
- Consider second-shell interactions
- Avoid positions critical for protein function
- Prefer conservative substitutions

## OUTPUT FORMAT (JSON)
Return your analysis as JSON:

{{
  "analysis_summary": "2-3 sentence explanation of the pathogenic mutation impact",
  "rescue_candidates": [
    {{
      "position": 168,
      "from_aa": "H",
      "to_aa": "R",
      "mutation_notation": "H168R",
      "rationale": "Restores positive charge lost by {mutation}, stabilizing DNA binding",
      "confidence": 0.85,
      "literature_support": "PMID:12345678 shows H168R compensates in similar contexts",
      "structural_basis": "Position 168 is in helix H2, ~12Å from mutation site"
    }}
  ],
  "literature_references": [
    "PMID:12345678 - Compensatory mutations in {protein}",
    "PMID:87654321 - Structural analysis of {mutation}"
  ]
}}

Return ONLY the JSON object, no markdown, no explanation."""
    
    return prompt

def build_validation_prompt(
    candidates: List[Dict[str, Any]],
    gene_name: str,
    pathogenic_mutation: str,
    gene_function: Optional[str],
    disease: Optional[str]
) -> str:
    """Build multi-dimensional validation prompt."""
    prompt = f"""You are an expert structural biologist performing final validation of rescue mutations.

## PROTEIN CONTEXT
- Gene: {gene_name}
- Pathogenic Mutation: {pathogenic_mutation}"""
    
    if gene_function:
        prompt += f"\n- Protein Function: {gene_function}"
    if disease:
        prompt += f"\n- Disease: {disease}"
    
    prompt += f"""

## CANDIDATE DATA
{json.dumps(candidates, indent=2)}

## VALIDATION TASKS

Analyze each rescue mutation candidate across 4 critical dimensions:

### 1. STRUCTURAL RESTORATION
Question: Does the rescue mutation successfully restore wild-type-like structure?
Evaluate:
- RMSD quality (target: <1.0 Å excellent, <2.0 Å good)
- pLDDT confidence scores (higher is better, >80 is good)
- Structural recovery assessment
- Visual alignment if overlay images available

### 2. AGGREGATION RISK
Question: Does the rescue mutation create aggregation-prone regions?
Evaluate:
- Surface exposure of hydrophobic residues
- Formation of sticky patches
- β-sheet propensity changes
- Known aggregation motifs

### 3. FUNCTIONAL PRESERVATION
Question: Is the protein's function maintained?
Evaluate:
- Position location relative to functional interfaces
- Electrostatic surface potential changes
- Active site integrity
- Protein-protein interaction surfaces

### 4. AMYLOID FORMATION RISK
Question: Could this rescue mutation promote amyloid structures?
Evaluate:
- β-sheet enrichment
- Amyloidogenic sequence motifs
- Structural context of substitutions

## OUTPUT FORMAT (JSON)

Return a JSON object with this structure:

{{
  "overall_verdict": "APPROVED|APPROVED_WITH_CAUTION|REJECTED",
  "risk_score": 0.0-10.0,  // Lower is safer
  
  "structural_restoration": {{
    "verdict": "POSITIVE|NEUTRAL|NEGATIVE",
    "confidence": 0.0-1.0,
    "reasoning": "3-4 sentence analysis referencing metrics"
  }},
  
  "aggregation_risk": {{
    "verdict": "NO_RISK|LOW|MODERATE|HIGH",
    "confidence": 0.0-1.0,
    "reasoning": "Analysis with specific residue references"
  }},
  
  "functional_preservation": {{
    "verdict": "MAINTAINED|PARTIAL|COMPROMISED",
    "confidence": 0.0-1.0,
    "reasoning": "Function-specific analysis"
  }},
  
  "amyloid_risk": {{
    "verdict": "NO_RISK|LOW|MODERATE|HIGH",
    "confidence": 0.0-1.0,
    "reasoning": "Structural basis for amyloid assessment"
  }},
  
  "approved": [
    // List of approved candidate objects (full candidate data)
  ],
  
  "summary": "Overall summary explanation",
  
  "recommendations": [
    "Specific experimental validation steps",
    "Additional computational checks",
    "Monitoring suggestions"
  ],
  
  "warnings": [
    "Any concerns or caveats"
  ]
}}

Return ONLY the JSON object, no markdown, no explanation."""
    
    return prompt


def get_rescue_candidates(
    mutation: str,
    protein: str = "TP53",
    gene_function: Optional[str] = None,
    disease: Optional[str] = None,
    organism: Optional[str] = None,
    wild_type_sequence: Optional[str] = None,
    mutant_sequence: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Ask Gemini for 3-5 compensatory mutation candidates based on literature.
    
    Args:
        mutation: Mutation string (e.g., "R249S")
        protein: Protein name (default: "TP53")
        gene_function: Optional protein function description
        disease: Optional disease context
        organism: Optional organism name
        wild_type_sequence: Optional wild-type sequence
        mutant_sequence: Optional mutant sequence
    
    Returns:
        List of candidate dictionaries with position, original_aa, rescue_aa, mutation, reasoning,
        confidence, literature_support, structural_basis
    
    Raises:
        Exception: If Gemini API call fails or response cannot be parsed
    """
    try:
        prompt = build_discovery_prompt(
            mutation=mutation,
            protein=protein,
            gene_function=gene_function,
            disease=disease,
            organism=organism,
            wild_type_sequence=wild_type_sequence,
            mutant_sequence=mutant_sequence
        )
        
        logger.info(f"Requesting rescue candidates from Gemini for {protein} {mutation}")
        try:
            response = client.models.generate_content(
                model=settings.gemini_model_discovery,
                contents=prompt
            )
        except Exception as api_error:
            error_str = str(api_error)
            error_type = type(api_error).__name__
            # Check if it's a 503/overloaded error
            if "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower() or hasattr(api_error, 'status_code') and getattr(api_error, 'status_code', None) == 503:
                logger.warning(f"Gemini API unavailable (503/overloaded): {error_str}")
                # Re-raise with a specific message that orchestrator can detect
                raise Exception(f"503_UNAVAILABLE: {error_str}")
            # Re-raise other errors as-is
            raise
        
        # Handle different response formats (new API might use different attribute)
        if hasattr(response, 'text'):
            response_text = response.text.strip()
        elif hasattr(response, 'content'):
            response_text = str(response.content).strip()
        else:
            # Try to get text from response object
            response_text = str(response).strip()
        
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        result = json.loads(response_text.strip())
        
        # Handle both old format (list) and new format (dict with rescue_candidates)
        if isinstance(result, list):
            # Old format - return as is
            candidates = result
        elif isinstance(result, dict) and "rescue_candidates" in result:
            # New format - extract candidates
            candidates = result["rescue_candidates"]
        else:
            raise ValueError("Gemini response format not recognized")
        
        # Normalize candidate format
        normalized_candidates = []
        for candidate in candidates:
            normalized = {
                "position": candidate.get("position"),
                "original_aa": candidate.get("from_aa") or candidate.get("original_aa"),
                "rescue_aa": candidate.get("to_aa") or candidate.get("rescue_aa"),
                "mutation": candidate.get("mutation_notation") or candidate.get("mutation"),
                "reasoning": candidate.get("rationale") or candidate.get("reasoning", ""),
                "confidence": candidate.get("confidence"),
                "literature_support": candidate.get("literature_support"),
                "structural_basis": candidate.get("structural_basis")
            }
            normalized_candidates.append(normalized)
        
        logger.info(f"Received {len(normalized_candidates)} candidates from Gemini")
        return normalized_candidates
    
    except ValueError as e:
        # json.JSONDecodeError is a subclass of ValueError, so this catches both
        # This avoids scoping issues with json.JSONDecodeError
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        if 'response' in locals():
            response_text = getattr(response, 'text', getattr(response, 'content', str(response)))
            logger.error(f"Response text: {response_text}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    except Exception as e:
        error_str = str(e)
        # If it's already a 503_UNAVAILABLE error, preserve it
        if "503_UNAVAILABLE" in error_str:
            logger.warning(f"Gemini API unavailable: {error_str}")
            raise Exception(error_str)  # Re-raise as-is to preserve the prefix
        logger.error(f"Gemini API error: {e}")
        raise Exception(f"Failed to get rescue candidates from Gemini: {e}")


def final_validation(
    candidates: List[Dict[str, Any]],
    gene_name: str = "TP53",
    pathogenic_mutation: str = "",
    gene_function: Optional[str] = None,
    disease: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gemini reviews structural metrics and literature reasoning to approve candidates.
    Performs multi-dimensional analysis across 4 critical dimensions.
    
    Args:
        candidates: List of candidate dictionaries with validation scores
        gene_name: Gene/protein name
        pathogenic_mutation: Original pathogenic mutation
        gene_function: Optional protein function description
        disease: Optional disease context
    
    Returns:
        Dictionary with 'approved' list, multi-dimensional analysis, and recommendations
    
    Raises:
        Exception: If Gemini API call fails or response cannot be parsed
    """
    try:
        prompt = build_validation_prompt(
            candidates=candidates,
            gene_name=gene_name,
            pathogenic_mutation=pathogenic_mutation,
            gene_function=gene_function,
            disease=disease
        )
        
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
        
        if not isinstance(validation_result, dict):
            raise ValueError("Gemini response is not a dictionary")
        
        # Ensure required fields exist (backward compatibility)
        if "approved" not in validation_result:
            validation_result["approved"] = []
        if "summary" not in validation_result:
            validation_result["summary"] = "Validation completed"
        
        logger.info(
            f"Gemini validation complete: {len(validation_result.get('approved', []))} approved, "
            f"verdict={validation_result.get('overall_verdict', 'N/A')}, "
            f"risk_score={validation_result.get('risk_score', 'N/A')}"
        )
        return validation_result
    
    except ValueError as e:
        # json.JSONDecodeError is a subclass of ValueError
        logger.error(f"Failed to parse Gemini validation response as JSON: {e}")
        if 'response' in locals():
            response_text = getattr(response, 'text', getattr(response, 'content', str(response)))
            logger.error(f"Response text: {response_text}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    except Exception as e:
        logger.error(f"Gemini API error during validation: {e}")
        raise Exception(f"Failed to get final validation from Gemini: {e}")


def generate_mutation_validation(
    mutation: str,
    gene_name: str,
    gene_function: Optional[str],
    disease: Optional[str],
    wt_pdb: Optional[str] = None,
    pathogenic_pdb: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate validation analysis for the mutation itself (demo mode).
    Analyzes the pathogenic mutation's impact across 4 dimensions when no rescue candidates are available.
    
    Args:
        mutation: Pathogenic mutation string (e.g., "R249S")
        gene_name: Gene/protein name
        gene_function: Optional protein function description
        disease: Optional disease context
        wt_pdb: Optional wild-type PDB structure (for future use)
        pathogenic_pdb: Optional pathogenic PDB structure (for future use)
    
    Returns:
        Dictionary with multi-dimensional validation analysis
    """
    try:
        prompt = f"""You are an expert structural biologist analyzing a pathogenic mutation.

## PROTEIN CONTEXT
- Gene: {gene_name}
- Pathogenic Mutation: {mutation}"""
        
        if gene_function:
            prompt += f"\n- Protein Function: {gene_function}"
        if disease:
            prompt += f"\n- Disease: {disease}"
        
        prompt += f"""

## TASK

Since no rescue candidates passed validation, analyze the pathogenic mutation {mutation} itself 
across 4 critical dimensions to understand its impact:

### 1. STRUCTURAL IMPACT
Question: How does {mutation} affect the protein structure?
Evaluate:
- Expected structural changes
- Domain/region affected
- Secondary structure disruption
- Stability implications

### 2. AGGREGATION RISK
Question: Does {mutation} increase aggregation propensity?
Evaluate:
- Surface exposure changes
- Hydrophobic patch formation
- β-sheet enrichment
- Known aggregation motifs

### 3. FUNCTIONAL IMPACT
Question: How does {mutation} affect protein function?
Evaluate:
- Active site disruption
- Binding interface changes
- Regulatory domain impact
- Protein-protein interactions

### 4. AMYLOID FORMATION RISK
Question: Could {mutation} promote amyloid structures?
Evaluate:
- β-sheet propensity changes
- Amyloidogenic sequence motifs
- Structural context

## OUTPUT FORMAT (JSON)

{{
  "overall_verdict": "ANALYZED",
  "risk_score": 0.0-10.0,  // Higher indicates more severe impact
  
  "structural_restoration": {{
    "verdict": "SEVERE|MODERATE|MILD",
    "confidence": 0.0-1.0,
    "reasoning": "Analysis of structural impact of {mutation}"
  }},
  
  "aggregation_risk": {{
    "verdict": "NO_RISK|LOW|MODERATE|HIGH",
    "confidence": 0.0-1.0,
    "reasoning": "Analysis of aggregation potential"
  }},
  
  "functional_preservation": {{
    "verdict": "SEVERELY_COMPROMISED|PARTIALLY_COMPROMISED|MAINTAINED",
    "confidence": 0.0-1.0,
    "reasoning": "Analysis of functional impact"
  }},
  
  "amyloid_risk": {{
    "verdict": "NO_RISK|LOW|MODERATE|HIGH",
    "confidence": 0.0-1.0,
    "reasoning": "Analysis of amyloid formation risk"
  }},
  
  "recommendations": [
    "Experimental validation approaches",
    "Therapeutic strategies",
    "Further analysis suggestions"
  ],
  
  "warnings": [
    "Key concerns about this mutation",
    "Clinical implications"
  ]
}}

Return ONLY the JSON object, no markdown, no explanation."""
        
        logger.info(f"Requesting mutation validation analysis from Gemini for {gene_name} {mutation}")
        response = client.models.generate_content(
            model=settings.gemini_model_validation,
            contents=prompt
        )
        
        # Handle different response formats
        if hasattr(response, 'text'):
            result = response.text.strip()
        elif hasattr(response, 'content'):
            result = str(response.content).strip()
        else:
            result = str(response).strip()
        
        # Remove markdown code blocks if present
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        validation_result = json.loads(result.strip())
        
        if not isinstance(validation_result, dict):
            raise ValueError("Gemini response is not a dictionary")
        
        logger.info(f"Mutation validation analysis complete: risk_score={validation_result.get('risk_score', 'N/A')}")
        return validation_result
    
    except ValueError as e:
        # json.JSONDecodeError is a subclass of ValueError
        logger.error(f"Failed to parse Gemini mutation validation response as JSON: {e}")
        if 'response' in locals():
            response_text = getattr(response, 'text', getattr(response, 'content', str(response)))
            logger.error(f"Response text: {response_text}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    except Exception as e:
        logger.error(f"Gemini API error during mutation validation: {e}")
        raise Exception(f"Failed to get mutation validation from Gemini: {e}")

