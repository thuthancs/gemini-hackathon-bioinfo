# GeneRescue Frontend

React + TypeScript frontend for the GeneRescue mutation analysis application.

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional):
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173` (or the port Vite assigns).

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Deployment

### Deploy to Vercel

#### Quick Deploy (CLI)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. From the frontend directory, run:
```bash
vercel
```

3. Follow the prompts and add environment variables when asked.

#### Deploy via GitHub

1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New Project" → Import your repository
4. Configure:
   - **Root Directory**: `frontend` (or leave blank if deploying from frontend directory)
   - **Framework Preset**: Vite (auto-detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - `VITE_API_BASE_URL`: Your backend API URL
6. Click "Deploy"

#### Environment Variables

In Vercel, add this environment variable:
- `VITE_API_BASE_URL`: Your backend API URL (e.g., `https://your-backend.herokuapp.com`)

**Important**: Make sure your backend CORS settings allow requests from your Vercel domain.

#### Preview Deployments

Vercel automatically creates preview deployments for every push to a branch, making it easy to test changes before merging to main.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SequenceInput.tsx    # Input form component
│   │   └── ResultsTable.tsx     # Results display component
│   ├── services/
│   │   └── api.ts               # API client
│   ├── types/
│   │   └── index.ts             # TypeScript interfaces
│   ├── App.tsx                  # Main app component
│   ├── App.css                  # Styles
│   └── main.tsx                 # Entry point
├── package.json
└── vite.config.ts
```

## Features

- **Sequence Input**: 
  - Manual sequence entry
  - FASTA file upload
  - Mutation input with validation
  - Optional protein name

- **Results Display**:
  - Summary statistics
  - Table of approved candidates
  - ESM scores and RMSD values
  - Structural recovery indicators

- **Error Handling**:
  - Input validation
  - API error display
  - Loading states

## API Integration

The frontend communicates with the backend API via Axios. The API base URL can be configured via the `VITE_API_BASE_URL` environment variable (defaults to `http://localhost:8000`).

## Styling

Styles are in `App.css` using modern CSS with:
- Responsive design
- Gradient backgrounds
- Clean table layouts
- Loading animations

## TypeScript

All components and services are fully typed with TypeScript interfaces matching the backend Pydantic models.
