# Revised Architecture Documentation

## Overview

GeneRescue implements a 6-phase pipeline for discovering and validating compensatory mutations that can rescue pathogenic mutations. The system uses multiple AI/ML services to provide comprehensive analysis.

## Pipeline Phases

### Phase 0: Mutant Sequence Creation

**Purpose**: Create the mutant sequence from wild-type sequence and mutation specification.

**Implementation**: `backend/app/utils/sequence_utils.py::create_mutant()`

**Input**: 
- Wild-type sequence (string)
- Mutation (format: "R249S" = replace position 249 with S)

**Output**: Mutant sequence (string)

**Details**:
- Validates mutation format
- Checks position is within sequence bounds
- Verifies original amino acid matches
- Applies mutation to create new sequence

---

### Phase 1: Candidate Discovery (Gemini)

**Purpose**: Use Gemini AI to discover potential rescue mutations based on literature and protein biology knowledge.

**Implementation**: `backend/app/services/gemini_service.py::get_rescue_candidates()`

**Input**:
- Mutation string (e.g., "R249S")
- Protein name (default: "TP53")

**Output**: List of candidate dictionaries with:
- `position`: Amino acid position
- `original_aa`: Original amino acid
- `rescue_aa`: Proposed rescue amino acid
- `mutation`: Mutation notation (e.g., "H168R")
- `reasoning`: Literature-based explanation

**Details**:
- Uses Gemini 1.5 Pro model
- Prompts for 3-5 candidates
- Returns structured JSON response
- Handles markdown code block removal

---

### Phase 2: ESM-1v Validation

**Purpose**: Validate candidates using ESM-1v evolutionary fitness model.

**Implementation**: `backend/app/services/esm_service.py::validate_with_esm()`

**Input**:
- Mutant sequence
- List of candidates from Phase 1

**Output**: Filtered list of validated candidates with:
- `esm_score`: Probability score (0-1)
- `status`: "validated" or "rejected"

**Details**:
- Masks candidate position in mutant sequence
- Calls ESM-1v API to predict amino acid probabilities
- Accepts candidates with score > threshold (default: 0.6)
- Handles API errors gracefully

---

### Phase 3: Structure Prediction (ESMFold)

**Purpose**: Predict 3D structures for wild-type and rescued sequences.

**Implementation**: `backend/app/services/esmfold_service.py::predict_structure()`

**Input**: Protein sequence

**Output**: PDB format structure (string)

**Details**:
- Calls ESMFold API
- Handles long-running requests (5-minute timeout)
- Returns PDB content for RMSD calculation

---

### Phase 4: RMSD Calculation

**Purpose**: Calculate structural similarity between wild-type and rescued structures.

**Implementation**: 
- `backend/app/services/analysis_service.py::predict_and_analyze()`
- `backend/app/utils/structure_utils.py::calculate_rmsd()`

**Input**:
- Wild-type sequence
- Mutant sequence
- Validated candidates

**Output**: Candidates with:
- `rmsd`: RMSD value in Angstroms
- `structural_recovery`: "good" (< 2.0Å) or "poor" (≥ 2.0Å)

**Details**:
- Predicts WT structure once
- Predicts rescued structure for each candidate
- Uses BioPython to parse PDB files
- Calculates RMSD using CA atoms
- Superimposes structures before calculation

---

### Phase 5: Final Validation (Gemini)

**Purpose**: Gemini reviews all metrics and approves final candidates.

**Implementation**: `backend/app/services/gemini_service.py::final_validation()`

**Input**: List of analyzed candidates with all metrics

**Output**: Dictionary with:
- `approved`: List of approved candidates
- `summary`: Explanation of approvals

**Details**:
- Uses Gemini 2.0 Flash Exp model
- Considers ESM score, RMSD, and literature reasoning
- Returns only approved candidates with summary

---

## Service Architecture

### Service Layer

Each external API has its own service module:

- **GeminiService**: Handles both discovery (Phase 1) and validation (Phase 5)
- **ESMService**: ESM-1v API integration (Phase 2)
- **ESMFoldService**: Structure prediction (Phase 3)
- **AnalysisService**: Coordinates structure prediction and RMSD (Phases 3 & 4)

### Orchestrator

`backend/app/services/orchestrator.py` coordinates all phases:

- Executes phases sequentially
- Handles errors at each phase
- Returns partial results if pipeline fails
- Comprehensive logging

### Utilities

- **SequenceUtils**: Sequence manipulation, FASTA parsing, validation
- **StructureUtils**: PDB parsing, RMSD calculation, structure analysis

## API Layer

### Routes

- **POST /analyze**: Main analysis endpoint
- **GET /health**: Health check

### Request/Response Models

All models use Pydantic for validation:

- `AnalysisRequest`: Input validation
- `AnalysisResponse`: Structured output
- `Candidate`: Individual candidate data
- `HealthResponse`: Health status

## Error Handling Strategy

1. **Input Validation**: Pydantic models validate requests
2. **Service Errors**: Each service handles its own API errors
3. **Graceful Degradation**: Pipeline continues if possible, returns partial results
4. **User-Friendly Messages**: Errors are logged and returned in responses

## Configuration

All settings via environment variables:

- API keys (required)
- API endpoints (optional, defaults provided)
- Validation thresholds (optional, defaults provided)
- Model selection (optional, defaults provided)

## Frontend Integration

Frontend communicates via REST API:

- Axios client with error handling
- TypeScript types matching backend models
- Loading states and error display
- Form validation before submission

## Data Flow

```
User Input (Frontend)
  ↓
POST /analyze (FastAPI)
  ↓
Orchestrator.run_full_pipeline()
  ↓
Phase 0: create_mutant()
  ↓
Phase 1: GeminiService.get_rescue_candidates()
  ↓
Phase 2: ESMService.validate_with_esm()
  ↓
Phase 3 & 4: AnalysisService.predict_and_analyze()
  ├─ ESMFoldService.predict_structure() (WT)
  ├─ ESMFoldService.predict_structure() (Rescued)
  └─ StructureUtils.calculate_rmsd()
  ↓
Phase 5: GeminiService.final_validation()
  ↓
AnalysisResponse (JSON)
  ↓
Frontend Display
```

## Future Enhancements

- Caching of structure predictions
- Batch processing of multiple mutations
- Structure visualization (3D viewer)
- Export results to CSV/JSON
- Historical analysis tracking

