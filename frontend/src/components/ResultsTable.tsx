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

      {approvedCandidates.length > 0 ? (
        <div className="candidates-table-container">
          <h3>Approved Rescue Candidates</h3>
          <table className="candidates-table">
            <thead>
              <tr>
                <th>Position</th>
                <th>Mutation</th>
                <th>Original AA</th>
                <th>Rescue AA</th>
                <th>ESM Score</th>
                <th>RMSD (Å)</th>
                <th>Structural Recovery</th>
                <th>Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {approvedCandidates.map((candidate: Candidate, index: number) => (
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
                    {candidate.esm_score !== undefined
                      ? candidate.esm_score.toFixed(3)
                      : 'N/A'}
                  </td>
                  <td>
                    {candidate.rmsd !== undefined ? candidate.rmsd.toFixed(2) : 'N/A'}
                  </td>
                  <td>
                    <span
                      className={`recovery-badge ${
                        candidate.structural_recovery === 'good' ? 'good' : 'poor'
                      }`}
                    >
                      {candidate.structural_recovery || 'N/A'}
                    </span>
                  </td>
                  <td className="reasoning-cell">{candidate.reasoning}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="no-results">
          <p>No approved rescue candidates found.</p>
          {results.candidates_discovered > 0 && (
            <p>
              {results.candidates_discovered} candidates were discovered but none were approved
              after validation.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

