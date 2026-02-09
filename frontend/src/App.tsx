/** Main application component. */
import { useState, useEffect } from 'react';
import SequenceInput from './components/SequenceInput';
import ResultsTable from './components/ResultsTable';
import PipelineFlow from './components/PipelineFlow';
import StructureViewer from './components/StructureViewer';
import ValidationDetails from './components/ValidationDetails';
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

  const handleSubmit = async (
    sequence: string,
    mutation: string,
    protein: string,
    geneFunction?: string,
    disease?: string,
    organism?: string
  ) => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    setCurrentPhase(0);
    setSelectedCandidate(null);

    try {
      const response = await apiClient.analyzeMutation(
        sequence,
        mutation,
        protein,
        geneFunction,
        disease,
        organism
      );
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
        
        setSelectedCandidate(bestIndex);
      } else {
        // No candidates, but we might have WT or pathogenic structures
        // Set selectedCandidate to null, but visualization will show fallback structures
        setSelectedCandidate(null);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      console.error('Analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Get candidates list (approved first, then validated for demo)
  const getCandidatesList = () => {
    if (!results) return [];
    const approved = results.results?.approved || [];
    const validated = results.results?.validated || [];
    return approved.length > 0 ? approved : validated;
  };

  // Get the selected candidate for structure viewer
  const getSelectedCandidate = () => {
    if (!results || selectedCandidate === null) return null;
    const candidates = getCandidatesList();
    return candidates[selectedCandidate] || null;
  };



  // Check if we have any structure data to display
  const hasStructureData = () => {
    if (!results) return false;
    if (selectedCandidate !== null && getSelectedCandidate()?.pdb_structure) return true;
    if (results.wt_pdb_structure) return true;
    if (results.pathogenic_pdb_structure) return true;
    return false;
  };

  // Parse mutation string to extract position (e.g., "R249S" -> 249)
  const parseMutationPosition = (mutation: string): number | null => {
    if (!mutation) return null;
    const match = mutation.match(/^[A-Z](\d+)[A-Z]$/);
    if (match) {
      return parseInt(match[1], 10);
    }
    return null;
  };

  // Get all mutation positions to highlight
  const getMutationPositions = () => {
    if (!results) return [];
    const positions: number[] = [];
    
    // Add pathogenic mutation position
    const pathogenicPos = parseMutationPosition(results.original_mutation);
    if (pathogenicPos) {
      positions.push(pathogenicPos);
    }
    
    // Add rescue mutation position if candidate is selected
    if (selectedCandidate !== null) {
      const candidate = getSelectedCandidate();
      if (candidate?.position) {
        positions.push(candidate.position);
      }
    }
    
    return positions;
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
            
            {results.results && (
              <div className="validation-section">
                <ValidationDetails validation={results.results} />
              </div>
            )}
            
            {hasStructureData() && (
              <div className="structure-section">
                <div className="structures-grid">
                  {/* Rescue Structure Column */}
                  {selectedCandidate !== null && getSelectedCandidate()?.pdb_structure && (() => {
                    const candidate = getSelectedCandidate();
                    const rescuePos = candidate?.position;
                    const pathogenicPos = parseMutationPosition(results.original_mutation);
                    const highlightResidues = (() => {
                      const positions: number[] = [];
                      if (rescuePos) positions.push(rescuePos);
                      if (pathogenicPos && pathogenicPos !== rescuePos) positions.push(pathogenicPos);
                      return positions;
                    })();
                    const highlightColors = (() => {
                      const colors: { [position: number]: string } = {};
                      if (rescuePos) colors[rescuePos] = 'green';
                      if (pathogenicPos && pathogenicPos !== rescuePos) colors[pathogenicPos] = 'red';
                      return colors;
                    })();
                    return (
                    <div className="structure-grid-item" key="rescue-structure">
                      <StructureViewer
                        key={`rescue-${candidate?.mutation}-${candidate?.pdb_structure?.substring(0, 100)}`}
                        title={`Rescue Structure: ${candidate?.mutation || 'N/A'}`}
                        pdbData={candidate?.pdb_structure}
                        highlightResidues={highlightResidues}
                        highlightColors={highlightColors}
                        overlayImage={candidate?.overlay_image}
                      />
                    </div>
                    );
                  })()}
                  
                  {/* Wild-Type Structure Column */}
                  {results.wt_pdb_structure && (() => {
                    const pathogenicPos = parseMutationPosition(results.original_mutation);
                    const highlightResidues = pathogenicPos ? [pathogenicPos] : [];
                    const highlightColors = pathogenicPos ? { [pathogenicPos]: 'red' } : {};
                    return (
                    <div className="structure-grid-item" key="wt-structure">
                      <StructureViewer
                        key={`wt-${results.wt_pdb_structure?.substring(0, 100)}`}
                        title="Wild-Type Structure"
                        pdbData={results.wt_pdb_structure}
                        highlightResidues={highlightResidues}
                        highlightColors={highlightColors}
                      />
                    </div>
                    );
                  })()}
                  
                  {/* Pathogenic Structure Column */}
                  {results.pathogenic_pdb_structure && (() => {
                    const pathogenicPos = parseMutationPosition(results.original_mutation);
                    const highlightResidues = pathogenicPos ? [pathogenicPos] : [];
                    const highlightColors = pathogenicPos ? { [pathogenicPos]: 'red' } : {};
                    return (
                    <div className="structure-grid-item" key="pathogenic-structure">
                      <StructureViewer
                        key={`pathogenic-${results.original_mutation}-${results.pathogenic_pdb_structure?.substring(0, 100)}`}
                        title={`Pathogenic Structure: ${results.original_mutation}`}
                        pdbData={results.pathogenic_pdb_structure}
                        highlightResidues={highlightResidues}
                        highlightColors={highlightColors}
                      />
                    </div>
                    );
                  })()}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
