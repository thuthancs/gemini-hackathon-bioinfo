/** TypeScript interfaces matching backend Pydantic models. */

export interface AnalysisRequest {
  sequence: string;
  mutation: string;
  protein?: string;
}

export interface Candidate {
  position: number;
  original_aa: string;
  rescue_aa: string;
  mutation: string;
  reasoning: string;
  esm_score?: number;
  rmsd?: number;
  status?: string;
  structural_recovery?: string;
  pdb_structure?: string;
}

export interface FinalValidationResult {
  approved: Candidate[];
  validated?: Candidate[]; // Validated candidates (passed ESM but not approved)
  summary: string;
}

export interface AnalysisResponse {
  original_mutation: string;
  candidates_discovered: number;
  candidates_validated: number;
  results: FinalValidationResult;
  wt_pdb_structure?: string;
  error?: string;
}

export interface HealthResponse {
  status: string;
  api_keys_configured?: boolean;
}

