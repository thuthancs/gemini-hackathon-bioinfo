/** Component for displaying analysis results. */
import type { AnalysisResponse, Candidate } from '../types';

interface ResultsTableProps {
  results: AnalysisResponse | null;
  onSelectCandidate?: (index: number) => void;
  selectedCandidate?: number | null;
}

export default function ResultsTable({ results, onSelectCandidate, selectedCandidate }: ResultsTableProps) {
  if (!results) {
    return null;
  }

  const approvedCandidates = results.results?.approved || [];
  const validatedCandidates = results.results?.validated || [];
  // Show validated candidates if no approved candidates (for demo purposes)
  const candidatesToDisplay = approvedCandidates.length > 0
    ? approvedCandidates
    : validatedCandidates;
  const isShowingValidated = approvedCandidates.length === 0 && validatedCandidates.length > 0;

  return (
    <div className="results-container">
      <div className="results-summary">
        <h2>Analysis Results</h2>
        <div className="summary-stats">
          <div className="stat">
            <span className="stat-label">Original Mutation:</span>
            <span className="stat-value">{results.original_mutation}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Candidates Discovered:</span>
            <span className="stat-value">{results.candidates_discovered}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Candidates Validated:</span>
            <span className="stat-value">{results.candidates_validated}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Approved Candidates:</span>
            <span className="stat-value">{approvedCandidates.length}</span>
          </div>
        </div>

        {results.results?.overall_verdict && (
          <div className="validation-verdict">
            <div className="verdict-badge">
              <span className="verdict-label">Overall Verdict:</span>
              <span className={`verdict-value verdict-${results.results.overall_verdict.toLowerCase().replace('_', '-')}`}>
                {results.results.overall_verdict.replace('_', ' ')}
              </span>
            </div>
            {results.results.risk_score !== undefined && (
              <div className="risk-score">
                <span className="risk-label">Risk Score:</span>
                <span className={`risk-value risk-${results.results.risk_score !== null && results.results.risk_score !== undefined ? (results.results.risk_score <= 3 ? 'low' : results.results.risk_score <= 6 ? 'medium' : 'high') : 'unknown'}`}>
                  {results.results.risk_score !== null && results.results.risk_score !== undefined
                    ? results.results.risk_score.toFixed(1) + '/10'
                    : 'N/A'}
                </span>
              </div>
            )}
          </div>
        )}

        {results.results?.summary && (
          <div className="summary-text">
            <strong>Summary:</strong> {results.results.summary}
          </div>
        )}
      </div>

      {results.error && (
        <div className="error-message">
          <strong>Error:</strong> {results.error}
        </div>
      )}

      {candidatesToDisplay.length > 0 ? (
        <div className="candidates-table-container">
          <h3>
            {isShowingValidated
              ? 'Validated Rescue Candidates (for demo)'
              : 'Approved Rescue Candidates'}
          </h3>
          <table className="candidates-table">
            <thead>
              <tr>
                <th>Position</th>
                <th>Mutation</th>
                <th>Original AA</th>
                <th>Rescue AA</th>
                <th>Confidence</th>
                <th>ESM Score</th>
                <th>pLDDT</th>
                <th>RMSD WT→Rescue</th>
                <th>RMSD WT→Path</th>
                <th>Recovery</th>
                <th>Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {candidatesToDisplay.map((candidate: Candidate, index: number) => (
                <tr
                  key={`${candidate.position}-${candidate.rescue_aa}-${index}`}
                  className={`${candidate.structural_recovery === 'good' ? 'good-recovery' : ''} ${selectedCandidate === index ? 'selected' : ''}`}
                  onClick={() => onSelectCandidate?.(index)}
                  style={{ cursor: onSelectCandidate ? 'pointer' : 'default' }}
                >
                  <td>{candidate.position}</td>
                  <td>
                    <strong>{candidate.mutation}</strong>
                  </td>
                  <td>{candidate.original_aa}</td>
                  <td>{candidate.rescue_aa}</td>
                  <td>
                    {candidate.confidence !== undefined && candidate.confidence !== null
                      ? (candidate.confidence * 100).toFixed(0) + '%'
                      : 'N/A'}
                  </td>
                  <td>
                    {candidate.esm_score !== undefined && candidate.esm_score !== null
                      ? candidate.esm_score.toFixed(3)
                      : 'N/A'}
                  </td>
                  <td>
                    {candidate.mean_plddt !== undefined && candidate.mean_plddt !== null
                      ? `${candidate.mean_plddt.toFixed(1)}${candidate.plddt_at_mutation !== undefined && candidate.plddt_at_mutation !== null ? ` (${candidate.plddt_at_mutation.toFixed(1)}@mut)` : ''}`
                      : 'N/A'}
                  </td>
                  <td>
                    {candidate.rmsd_wt_vs_rescue !== undefined && candidate.rmsd_wt_vs_rescue !== null
                      ? candidate.rmsd_wt_vs_rescue.toFixed(2)
                      : candidate.rmsd !== undefined && candidate.rmsd !== null
                        ? candidate.rmsd.toFixed(2)
                        : 'N/A'}
                  </td>
                  <td>
                    {candidate.rmsd_wt_vs_pathogenic !== undefined && candidate.rmsd_wt_vs_pathogenic !== null
                      ? candidate.rmsd_wt_vs_pathogenic.toFixed(2)
                      : 'N/A'}
                  </td>
                  <td>
                    <span
                      className={`recovery-badge ${candidate.structural_recovery === 'good' ? 'good' : 'poor'
                        }`}
                    >
                      {candidate.structural_recovery || 'N/A'}
                    </span>
                  </td>
                  <td className="reasoning-cell">
                    <div>{candidate.reasoning}</div>
                    {candidate.literature_support && (
                      <div className="literature-support" title={candidate.literature_support}>
                        📚 {candidate.literature_support.substring(0, 30)}...
                      </div>
                    )}
                    {candidate.structural_basis && (
                      <div className="structural-basis" title={candidate.structural_basis}>
                        🏗️ {candidate.structural_basis.substring(0, 30)}...
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="no-results">
          <p>No rescue candidates available for display.</p>
          {results.candidates_discovered > 0 && (
            <p>
              {results.candidates_discovered} candidates were discovered but none passed validation.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

