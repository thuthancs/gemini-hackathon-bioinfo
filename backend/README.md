# GeneRescue Backend

FastAPI backend for mutation rescue analysis using Gemini, ESM-1v, and ESMFold.

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
ESM_API_KEY=your_esm_api_key_here
```

## Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /analyze

Analyze a mutation and find potential rescue mutations.

**Request Body:**
```json
{
  "sequence": "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD",
  "mutation": "R249S",
  "protein": "TP53"
}
```

**Response:**
```json
{
  "original_mutation": "R249S",
  "candidates_discovered": 5,
  "candidates_validated": 3,
  "results": {
    "approved": [...],
    "summary": "..."
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "api_keys_configured": true
}
```

## Pipeline Phases

The analysis pipeline consists of 6 phases:

1. **Phase 0**: Create mutant sequence from wild-type and mutation
2. **Phase 1**: Gemini discovers rescue candidates from literature
3. **Phase 2**: ESM-1v validates candidates (evolutionary fitness)
4. **Phase 3**: ESMFold predicts structures for wild-type and rescued sequences
5. **Phase 4**: Calculate RMSD between structures
6. **Phase 5**: Gemini final validation based on all metrics

## Configuration

All configuration is done via environment variables in `.env`:

- `GEMINI_API_KEY`: Google Gemini API key (required)
- `ESM_API_KEY`: ESM API key (required)
- `ESM_VALIDATION_THRESHOLD`: ESM-1v score threshold (default: 0.6)
- `RMSD_GOOD_THRESHOLD`: RMSD threshold in Angstroms (default: 2.0)
- `DEBUG`: Enable debug logging (default: false)

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── mutations.py    # Analysis endpoint
│   │       └── health.py        # Health check
│   ├── services/
│   │   ├── gemini_service.py    # Gemini API integration
│   │   ├── esm_service.py       # ESM-1v validation
│   │   ├── esmfold_service.py   # ESMFold structure prediction
│   │   ├── analysis_service.py # Structure analysis
│   │   └── orchestrator.py      # Pipeline coordination
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   ├── utils/
│   │   ├── sequence_utils.py    # Sequence manipulation
│   │   └── structure_utils.py    # PDB/RMSD utilities
│   ├── config.py                # Configuration
│   └── main.py                  # FastAPI app
├── requirements.txt
└── .env.example
```

## Error Handling

The API includes comprehensive error handling:

- Input validation (sequence format, mutation format)
- API error handling (Gemini, ESM, ESMFold)
- Graceful degradation (returns partial results if some phases fail)
- Detailed error messages in responses

## Logging

Logging is configured in `main.py`. Set `DEBUG=true` in `.env` for detailed logs.

