/** TypeScript interfaces matching backend Pydantic models. */

export interface AnalysisRequest {
  sequence: string;
  mutation: string;
  protein?: string;
  gene_function?: string;
  disease?: string;
  organism?: string;
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
  confidence?: number;
  literature_support?: string;
  structural_basis?: string;
  mean_plddt?: number;
  plddt_at_mutation?: number;
  rmsd_wt_vs_pathogenic?: number;
  rmsd_wt_vs_rescue?: number;
  pathogenic_pdb_structure?: string;
  overlay_image?: string;
}

export interface ValidationDimension {
  verdict: string;
  confidence: number;
  reasoning: string;
}

export interface FinalValidationResult {
  approved: Candidate[];
  validated?: Candidate[]; // Validated candidates (passed ESM but not approved)
  summary: string;
  overall_verdict?: string;
  risk_score?: number;
  structural_restoration?: ValidationDimension;
  aggregation_risk?: ValidationDimension;
  functional_preservation?: ValidationDimension;
  amyloid_risk?: ValidationDimension;
  recommendations?: string[];
  warnings?: string[];
}

export interface AnalysisResponse {
  original_mutation: string;
  candidates_discovered: number;
  candidates_validated: number;
  results: FinalValidationResult;
  wt_pdb_structure?: string;
  pathogenic_pdb_structure?: string;
  error?: string;
}

export interface HealthResponse {
  status: string;
  api_keys_configured?: boolean;
}

