# GeneRescue

A comprehensive mutation rescue analysis platform that discovers and validates compensatory mutations to rescue pathogenic protein mutations. The system combines AI-powered literature analysis, evolutionary fitness validation, and structural prediction to identify potential therapeutic rescue mutations.

## Overview

GeneRescue implements a 6-phase pipeline that:
1. Creates mutant sequences from wild-type proteins
2. Discovers rescue candidates using Google Gemini AI
3. Validates candidates with ESM-1v evolutionary fitness model
4. Predicts 3D structures using ESMFold
5. Calculates structural similarity (RMSD)
6. Performs final multi-dimensional validation

The platform provides both a REST API backend and an interactive web frontend for visualizing protein structures and analysis results.

## Features

- **AI-Powered Discovery**: Uses Google Gemini to discover rescue mutations from scientific literature
- **Evolutionary Validation**: ESM-1v validates candidates based on evolutionary fitness
- **Structure Prediction**: ESMFold generates 3D protein structures
- **Visual Comparison**: Interactive 3D structure viewer comparing wild-type, pathogenic, and rescue structures
- **Multi-Dimensional Analysis**: Combines evolutionary, structural, and functional metrics
- **Real-time Pipeline**: Track analysis progress through all 6 phases

## Project Structure

```
gemini-hackathon-bioinfo/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic services
│   │   ├── models/      # Pydantic schemas
│   │   └── utils/       # Utility functions
│   └── README.md        # Backend documentation
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── README.md        # Frontend documentation
├── docs/                # Architecture and design docs
└── test/                # Test scripts and notebooks
```

## Quick Start

### Prerequisites

- **Backend**: Python 3.9+, pip
- **Frontend**: Node.js 18+, npm
- **API Keys**: 
  - Google Gemini API key
  - ESM API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Usage

### API Endpoint

**POST /analyze**

Analyze a mutation and discover rescue candidates:

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
    "validated": [...],
    "summary": "..."
  },
  "wt_pdb_structure": "...",
  "pathogenic_pdb_structure": "..."
}
```

### Web Interface

1. Open the frontend application in your browser
2. Enter or upload a protein sequence
3. Specify the mutation (e.g., "R249S")
4. Optionally provide protein name, gene function, disease, or organism
5. Click "Analyze Mutation"
6. View results including:
   - Discovered rescue candidates
   - ESM validation scores
   - RMSD structural comparisons
   - 3D structure visualizations

## Pipeline Phases

The analysis pipeline consists of 6 phases:

1. **Phase 0**: Create mutant sequence from wild-type and mutation
2. **Phase 1**: Gemini discovers rescue candidates from literature
3. **Phase 2**: ESM-1v validates candidates (evolutionary fitness)
4. **Phase 3**: ESMFold predicts structures for wild-type and rescued sequences
5. **Phase 4**: Calculate RMSD between structures
6. **Phase 5**: Gemini final validation based on all metrics

## Visualization

The frontend provides interactive 3D structure visualization using NGL.js:

- **3-Column Grid Layout**: Compare Rescue, Wild-Type, and Pathogenic structures side-by-side
- **Color-Coded Highlights**: 
  - Green for rescue mutation sites
  - Red for pathogenic mutation sites
  - Gray base structure for all types
- **Strand Highlighting**: Mutation sites highlighted as colored cartoon strands with visible side chains

## Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
ESM_API_KEY=your_esm_api_key_here
ESM_VALIDATION_THRESHOLD=0.6
RMSD_GOOD_THRESHOLD=2.0
DEBUG=false
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory (optional):

```env
VITE_API_BASE_URL=http://localhost:8000
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Google Gemini API**: AI-powered candidate discovery
- **ESM-1v API**: Evolutionary fitness validation
- **ESMFold API**: Protein structure prediction
- **Pydantic**: Data validation and serialization

### Frontend
- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **NGL.js**: 3D molecular visualization
- **Axios**: HTTP client

## Documentation

- [Backend README](backend/README.md) - Detailed backend setup and API documentation
- [Frontend README](frontend/README.md) - Frontend development guide
- [Architecture Documentation](docs/REVISED_ARCHITECTURE.md) - System architecture and pipeline details
- [ESMFold Usage Guide](ESMFOLD_USAGE.md) - ESMFold API usage

## Error Handling

The system includes comprehensive error handling:

- Input validation (sequence format, mutation format)
- API error handling with retries and fallbacks
- Graceful degradation (returns partial results if some phases fail)
- Detailed error messages in responses
- User-friendly error display in frontend

## Deployment

### Frontend on Vercel

The frontend can be easily deployed to Vercel:

#### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Navigate to frontend directory:
```bash
cd frontend
```

3. Deploy:
```bash
vercel
```

4. Follow the prompts to:
   - Link to your Vercel account
   - Set up the project
   - Configure environment variables (see below)

#### Option 2: Deploy via GitHub Integration

1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New Project"
4. Import your GitHub repository
5. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. Add environment variables (see below)
7. Click "Deploy"

#### Environment Variables

In Vercel dashboard, add these environment variables:

- `VITE_API_BASE_URL`: Your backend API URL (e.g., `https://your-backend.herokuapp.com` or `https://api.yourdomain.com`)

**Note**: If your backend is on a different domain, you may need to configure CORS on the backend to allow requests from your Vercel domain.

#### Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

### Backend Deployment

The backend can be deployed to various platforms:

- **Heroku**: Use a `Procfile` with `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Railway**: Supports Python applications directly
- **AWS/GCP/Azure**: Use containerized deployment (Docker)
- **Fly.io**: Supports Python applications

For production, use a production ASGI server:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Development

### Running Tests

Backend tests are located in `backend/test/`:
```bash
cd backend
python -m pytest test/
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
The backend runs as a standard FastAPI application. For production, use a production ASGI server like Gunicorn with Uvicorn workers.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license here]

## Acknowledgments

- Google Gemini for AI-powered candidate discovery
- Meta AI for ESM-1v and ESMFold models
- NGL.js for molecular visualization

