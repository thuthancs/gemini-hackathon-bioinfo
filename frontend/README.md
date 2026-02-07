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
