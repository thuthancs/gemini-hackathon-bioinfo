/** Component for visualizing the 6-phase pipeline flow. */
import { useEffect, useState } from 'react';
import './PipelineFlow.css';

interface PipelineFlowProps {
  isLoading: boolean;
  currentPhase?: number; // 0-5 for phases, -1 if not started
  error?: string | null;
}

const PHASES = [
  { id: 0, name: 'Create Mutant', description: 'Generate mutant sequence' },
  { id: 1, name: 'Candidate Discovery', description: 'Gemini finds rescue candidates' },
  { id: 2, name: 'ESM-1v Validation', description: 'Evolutionary validation' },
  { id: 3, name: 'Structure Prediction', description: 'ESMFold structure prediction' },
  { id: 4, name: 'RMSD Analysis', description: 'Structural similarity calculation' },
  { id: 5, name: 'Final Validation', description: 'Gemini final approval' },
];

export default function PipelineFlow({ isLoading, currentPhase = -1, error }: PipelineFlowProps) {
  const [completedPhases, setCompletedPhases] = useState<number[]>([]);

  useEffect(() => {
    if (currentPhase >= 0) {
      // Mark all phases up to current as completed
      setCompletedPhases(Array.from({ length: currentPhase + 1 }, (_, i) => i));
    } else if (!isLoading) {
      // If not loading and no current phase, reset
      setCompletedPhases([]);
    }
  }, [currentPhase, isLoading]);

  const getPhaseStatus = (phaseId: number): 'pending' | 'active' | 'completed' | 'error' => {
    if (error && phaseId === currentPhase) return 'error';
    if (completedPhases.includes(phaseId)) return 'completed';
    if (phaseId === currentPhase && isLoading) return 'active';
    return 'pending';
  };

  return (
    <div className="pipeline-flow-container">
      <h3>Pipeline Status</h3>
      <div className="pipeline-flow">
        {PHASES.map((phase, index) => {
          const status = getPhaseStatus(phase.id);
          const isLast = index === PHASES.length - 1;
          const prevPhaseCompleted = index > 0 && completedPhases.includes(PHASES[index - 1].id);

          return (
            <div key={phase.id} className="pipeline-phase-wrapper">
              <div className={`pipeline-phase ${status}`}>
                <div className="phase-icon">
                  {status === 'completed' && '✓'}
                  {status === 'active' && '⟳'}
                  {status === 'error' && '✗'}
                  {status === 'pending' && (index + 1)}
                </div>
                <div className="phase-content">
                  <div className="phase-name">{phase.name}</div>
                  <div className="phase-description">{phase.description}</div>
                </div>
              </div>
              {!isLast && (
                <div className={`phase-connector ${prevPhaseCompleted || status === 'completed' ? 'completed' : ''}`} />
              )}
            </div>
          );
        })}
      </div>
      {error && (
        <div className="pipeline-error">
          <strong>Error at Phase {currentPhase + 1}:</strong> {error}
        </div>
      )}
    </div>
  );
}

