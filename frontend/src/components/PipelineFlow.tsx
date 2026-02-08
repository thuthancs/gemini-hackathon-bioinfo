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
      if (isLoading) {
        // Pipeline is running: mark only phases before current as completed (current phase is still active)
        setCompletedPhases(Array.from({ length: currentPhase }, (_, i) => i));
      } else {
        // Pipeline completed: mark all phases up to and including current as completed
        setCompletedPhases(Array.from({ length: currentPhase + 1 }, (_, i) => i));
      }
    } else if (!isLoading && currentPhase === -1) {
      // Only reset if pipeline hasn't started yet (not when it's completed)
      // Keep completed phases if we had any (pipeline finished)
      if (completedPhases.length === 0) {
        setCompletedPhases([]);
      }
    }
  }, [currentPhase, isLoading]);

  // Get phases to display: completed phases + current active phase
  const getPhasesToDisplay = () => {
    const phases: Array<{ phase: typeof PHASES[0]; status: 'completed' | 'active' | 'error' }> = [];
    
    // Add all completed phases
    completedPhases.forEach(phaseId => {
      const phase = PHASES.find(p => p.id === phaseId);
      if (phase) {
        phases.push({ phase, status: 'completed' });
      }
    });
    
    // Add current active phase if loading
    if (isLoading && currentPhase >= 0) {
      const activePhase = PHASES.find(p => p.id === currentPhase);
      if (activePhase && !completedPhases.includes(currentPhase)) {
        phases.push({ 
          phase: activePhase, 
          status: error ? 'error' : 'active' 
        });
      }
    }
    
    return phases;
  };

  const phasesToDisplay = getPhasesToDisplay();

  return (
    <div className="pipeline-flow-container">
      <h3>Pipeline Status</h3>
      <div className="pipeline-messages-box">
        {phasesToDisplay.length === 0 && !isLoading && (
          <div className="pipeline-placeholder">
            Pipeline will start when analysis begins...
          </div>
        )}
        {phasesToDisplay.map(({ phase, status }) => (
          <div key={phase.id} className={`pipeline-message ${status}`}>
            {status === 'completed' && (
              <>
                <span className="message-checkmark">✓</span>
                <span className="message-text">
                  <strong>{phase.name}</strong> - {phase.description}
                </span>
              </>
            )}
            {status === 'active' && (
              <>
                <div className="message-spinner"></div>
                <span className="message-text">
                  <strong>{phase.name}</strong> - {phase.description}
                </span>
              </>
            )}
            {status === 'error' && (
              <>
                <span className="message-error-icon">✗</span>
                <span className="message-text">
                  <strong>{phase.name}</strong> - {phase.description}
                </span>
              </>
            )}
          </div>
        ))}
      </div>
      {error && (
        <div className="pipeline-error">
          <strong>Error at Phase {currentPhase + 1}:</strong> {error}
        </div>
      )}
    </div>
  );
}

