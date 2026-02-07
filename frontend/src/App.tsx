/** Main application component. */
import { useState, useEffect } from 'react';
import SequenceInput from './components/SequenceInput';
import ResultsTable from './components/ResultsTable';
import PipelineFlow from './components/PipelineFlow';
import StructureViewer from './components/StructureViewer';
import { apiClient } from './services/api';
import type { AnalysisResponse } from './types';
import './App.css';

function App() {
  const [results, setResults] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPhase, setCurrentPhase] = useState<number>(-1);
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(null);

  // Simulate pipeline phases during loading
  useEffect(() => {
    if (!isLoading) {
      setCurrentPhase(-1);
      return;
    }

    // Simulate phase progression (this would ideally come from backend via WebSocket or polling)
    const phases = [0, 1, 2, 3, 4, 5];
    let phaseIndex = 0;

    const phaseInterval = setInterval(() => {
      if (phaseIndex < phases.length) {
        setCurrentPhase(phases[phaseIndex]);
        phaseIndex++;
      }
    }, 10000); // Move to next phase every 10 seconds (adjust based on actual timing)

    return () => clearInterval(phaseInterval);
  }, [isLoading]);

  const handleSubmit = async (sequence: string, mutation: string, protein: string) => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    setCurrentPhase(0);
    setSelectedCandidate(null);

    try {
      const response = await apiClient.analyzeMutation(sequence, mutation, protein);
      setResults(response);
      setCurrentPhase(5); // Mark all phases as complete
      
      // Auto-select candidate with highest ESM score for 3D structure demo
      // Use approved candidates first, fallback to validated candidates if no approved
      const approved = response.results?.approved || [];
      const validated = response.results?.validated || [];
      const candidatesToUse = approved.length > 0 ? approved : validated;
      
      if (candidatesToUse.length > 0) {
        // Find candidate with highest ESM score
        let bestIndex = 0;
        let bestScore = candidatesToUse[0]?.esm_score || 0;
        
        candidatesToUse.forEach((candidate, index) => {
          const score = candidate.esm_score || 0;
          if (score > bestScore) {
            bestScore = score;
            bestIndex = index;
          }
        });
        
        // If using validated candidates, we need to track that
        setSelectedCandidate(bestIndex);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      console.error('Analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Extract PDB data from results if available
  const getStructureData = () => {
    if (!results || selectedCandidate === null) return null;
    
    const approved = results.results?.approved || [];
    const validated = results.results?.validated || [];
    const candidatesToUse = approved.length > 0 ? approved : validated;
    const candidate = candidatesToUse[selectedCandidate];
    
    // Return PDB structure data from the candidate
    return candidate?.pdb_structure || null;
  };

  // Get the selected candidate for structure viewer
  const getSelectedCandidate = () => {
    if (!results || selectedCandidate === null) return null;
    
    const approved = results.results?.approved || [];
    const validated = results.results?.validated || [];
    const candidatesToUse = approved.length > 0 ? approved : validated;
    return candidatesToUse[selectedCandidate] || null;
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>GeneRescue</h1>
        <p>Mutation Rescue Analysis Pipeline</p>
      </header>

      <main className="app-main">
        <div className="input-section">
          <h2>Analyze Mutation</h2>
          <SequenceInput onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {(isLoading || results) && (
          <div className="pipeline-section">
            <PipelineFlow 
              isLoading={isLoading} 
              currentPhase={currentPhase}
              error={error}
            />
          </div>
        )}

        {error && (
          <div className="error-container">
            <div className="error-message">{error}</div>
          </div>
        )}

        {results && (
          <div className="results-section">
            <ResultsTable 
              results={results} 
              onSelectCandidate={setSelectedCandidate}
              selectedCandidate={selectedCandidate}
            />
            
            {selectedCandidate !== null && getSelectedCandidate() && (
              <div className="structure-section">
                <StructureViewer
                  title={`Structure for ${getSelectedCandidate()?.mutation || `Candidate ${selectedCandidate + 1}`}`}
                  pdbData={getStructureData()}
                  highlightResidues={
                    getSelectedCandidate()
                      ? [getSelectedCandidate()!.position]
                      : []
                  }
                />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
