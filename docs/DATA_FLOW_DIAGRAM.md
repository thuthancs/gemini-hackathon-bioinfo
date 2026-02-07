# Data Flow Diagram

## API Request/Response Flow

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │
       │ POST /analyze
       │ {sequence, mutation, protein}
       ▼
┌─────────────────────┐
│   FastAPI Backend   │
│   (main.py)         │
└──────┬──────────────┘
       │
       │ Route to mutations.py
       ▼
┌─────────────────────┐
│  mutations.py       │
│  analyze_mutation() │
└──────┬──────────────┘
       │
       │ Validate request
       │ Call orchestrator
       ▼
┌─────────────────────┐
│  orchestrator.py    │
│ run_full_pipeline() │
└──────┬──────────────┘
       │
       ├─► Phase 0: create_mutant()
       │
       ├─► Phase 1: GeminiService
       │   └─► Gemini API
       │
       ├─► Phase 2: ESMService
       │   └─► ESM-1v API
       │
       ├─► Phase 3 & 4: AnalysisService
       │   ├─► ESMFoldService (WT)
       │   │   └─► ESMFold API
       │   ├─► ESMFoldService (Rescued)
       │   │   └─► ESMFold API
       │   └─► StructureUtils.calculate_rmsd()
       │
       └─► Phase 5: GeminiService
           └─► Gemini API
       │
       ▼
┌─────────────────────┐
│  AnalysisResponse   │
│  (JSON)             │
└──────┬──────────────┘
       │
       │ HTTP 200 OK
       ▼
┌─────────────┐
│   Frontend  │
│  Display    │
└─────────────┘
```

## Pipeline Execution Flow

```
START
  │
  ▼
┌─────────────────┐
│ Phase 0:        │
│ Create Mutant   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 1:        │
│ Gemini Discovery│
│ (3-5 candidates)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 2:        │
│ ESM-1v Validate │
│ (filter by score)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 3:        │
│ ESMFold Predict │
│ (WT structure)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ For each        │
│ candidate:      │
│                 │
│ 1. Apply rescue │
│ 2. Predict      │
│    structure    │
│ 3. Calculate    │
│    RMSD        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Phase 5:        │
│ Gemini Final    │
│ Validation      │
└────────┬────────┘
         │
         ▼
      END
```

## Error Handling Flow

```
┌─────────────────┐
│  Service Call   │
└────────┬────────┘
         │
         ├─► Success ──► Continue
         │
         └─► Error
             │
             ├─► Log Error
             │
             ├─► Try Recovery (if possible)
             │
             └─► Return Partial Results
                 │
                 └─► Include Error Message
```

## Component Interaction

```
┌──────────────┐
│   App.tsx    │
│  (State Mgmt)│
└──────┬───────┘
       │
       ├─► SequenceInput
       │   └─► Form validation
       │   └─► File upload
       │
       ├─► apiClient
       │   └─► POST /analyze
       │   └─► Error handling
       │
       └─► ResultsTable
           └─► Display results
           └─► Format data
```

## Service Dependencies

```
orchestrator.py
  │
  ├─► sequence_utils.py
  │   └─► create_mutant()
  │
  ├─► gemini_service.py
  │   ├─► get_rescue_candidates()
  │   └─► final_validation()
  │
  ├─► esm_service.py
  │   └─► validate_with_esm()
  │
  └─► analysis_service.py
      ├─► esmfold_service.py
      │   └─► predict_structure()
      └─► structure_utils.py
          └─► calculate_rmsd()
```

## Data Transformation

```
Input:
  sequence: "MEEPQSDPSV..."
  mutation: "R249S"
  protein: "TP53"
  │
  ▼
Phase 0:
  mutant_seq: "MEEPQSDPSV..." (with S at 249)
  │
  ▼
Phase 1:
  candidates: [
    {position: 168, rescue_aa: "R", ...},
    ...
  ]
  │
  ▼
Phase 2:
  validated: [
    {position: 168, esm_score: 0.75, status: "validated", ...},
    ...
  ]
  │
  ▼
Phase 3 & 4:
  analyzed: [
    {position: 168, rmsd: 1.5, structural_recovery: "good", ...},
    ...
  ]
  │
  ▼
Phase 5:
  final: {
    approved: [...],
    summary: "..."
  }
  │
  ▼
Output:
  {
    original_mutation: "R249S",
    candidates_discovered: 5,
    candidates_validated: 3,
    results: {...}
  }
```

