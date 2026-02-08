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
  const [structureViewMode, setStructureViewMode] = useState<'rescue' | 'wt' | 'pathogenic'>('rescue');

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
      // #region agent log
      fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.tsx:64','message':'Response received from API','data':{hasWt:!!response.wt_pdb_structure,hasPathogenic:!!response.pathogenic_pdb_structure,wtLength:response.wt_pdb_structure?.length||0,pathogenicLength:response.pathogenic_pdb_structure?.length||0,wtFirst50:response.wt_pdb_structure?.substring(0,50),pathogenicFirst50:response.pathogenic_pdb_structure?.substring(0,50),structuresIdentical:response.wt_pdb_structure===response.pathogenic_pdb_structure},timestamp:Date.now(),runId:'pre-fix',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
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
      // #region agent log
      fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'App.tsx:95', 'message': 'Error in handleSubmit', 'data': { errorMessage, errorStack: err instanceof Error ? err.stack : undefined }, timestamp: Date.now(), runId: 'post-fix', hypothesisId: 'F' }) }).catch(() => { });
      // #endregion
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

  // Extract PDB data from results based on view mode
  const getStructureData = () => {
    if (!results) return null;
    
    // #region agent log
    fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.tsx:117','message':'getStructureData called','data':{structureViewMode,selectedCandidate,hasWt:!!results.wt_pdb_structure,hasPathogenic:!!results.pathogenic_pdb_structure,wtLength:results.wt_pdb_structure?.length||0,pathogenicLength:results.pathogenic_pdb_structure?.length||0,wtFirst50:results.wt_pdb_structure?.substring(0,50),pathogenicFirst50:results.pathogenic_pdb_structure?.substring(0,50),structuresIdentical:results.wt_pdb_structure===results.pathogenic_pdb_structure},timestamp:Date.now(),runId:'pre-fix',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    
    if (structureViewMode === 'rescue' && selectedCandidate !== null) {
      const candidate = getSelectedCandidate();
      if (candidate?.pdb_structure) {
        return candidate.pdb_structure;
      }
    }
    
    if (structureViewMode === 'wt' && results.wt_pdb_structure) {
      // #region agent log
      fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.tsx:127','message':'Returning WT structure','data':{wtLength:results.wt_pdb_structure.length,wtFirst50:results.wt_pdb_structure.substring(0,50)},timestamp:Date.now(),runId:'pre-fix',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      return results.wt_pdb_structure;
    }
    
    if (structureViewMode === 'pathogenic' && results.pathogenic_pdb_structure) {
      // #region agent log
      fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.tsx:131','message':'Returning pathogenic structure','data':{pathogenicLength:results.pathogenic_pdb_structure.length,pathogenicFirst50:results.pathogenic_pdb_structure.substring(0,50)},timestamp:Date.now(),runId:'pre-fix',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      return results.pathogenic_pdb_structure;
    }
    
    // Fallback: try to get any available structure
    if (selectedCandidate !== null) {
      const candidate = getSelectedCandidate();
      if (candidate?.pdb_structure) {
        return candidate.pdb_structure;
      }
    }
    
    if (results.wt_pdb_structure) {
      return results.wt_pdb_structure;
    }
    
    if (results.pathogenic_pdb_structure) {
      return results.pathogenic_pdb_structure;
    }
    
    return null;
  };

  // Get structure title based on view mode
  const getStructureTitle = () => {
    if (!results) return 'Protein Structure';
    
    if (structureViewMode === 'rescue' && selectedCandidate !== null) {
      const candidate = getSelectedCandidate();
      if (candidate?.pdb_structure) {
        return `Rescue Structure: ${candidate.mutation}`;
      }
    }
    
    if (structureViewMode === 'wt') {
      return 'Wild-Type Structure';
    }
    
    if (structureViewMode === 'pathogenic') {
      return `Pathogenic Structure: ${results.original_mutation}`;
    }
    
    // Fallback titles
    if (results.wt_pdb_structure) {
      return 'Wild-Type Structure';
    }
    
    if (results.pathogenic_pdb_structure) {
      return `Pathogenic Structure: ${results.original_mutation}`;
    }
    
    return 'Protein Structure';
  };

  // Get available structure types
  const getAvailableStructures = () => {
    if (!results) return [];
    const available: string[] = [];
    
    if (selectedCandidate !== null && getSelectedCandidate()?.pdb_structure) {
      available.push('rescue');
    }
    if (results.wt_pdb_structure) {
      available.push('wt');
    }
    if (results.pathogenic_pdb_structure) {
      available.push('pathogenic');
    }
    
    return available;
  };

  // Auto-select appropriate view mode when results change
  useEffect(() => {
    if (!results) return;
    
    const available: string[] = [];
    if (selectedCandidate !== null && getSelectedCandidate()?.pdb_structure) {
      available.push('rescue');
    }
    if (results.wt_pdb_structure) {
      available.push('wt');
    }
    if (results.pathogenic_pdb_structure) {
      available.push('pathogenic');
    }
    
    if (available.length === 0) return;
    
    // If current mode is not available, switch to first available
    if (!available.includes(structureViewMode)) {
      if (available.includes('rescue')) {
        setStructureViewMode('rescue');
      } else if (available.includes('wt')) {
        setStructureViewMode('wt');
      } else if (available.includes('pathogenic')) {
        setStructureViewMode('pathogenic');
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [results, selectedCandidate, structureViewMode]);

  // Check if we have any structure data to display
  const hasStructureData = () => {
    if (!results) return false;
    if (selectedCandidate !== null && getSelectedCandidate()?.pdb_structure) return true;
    if (results.wt_pdb_structure) return true;
    if (results.pathogenic_pdb_structure) return true;
    return false;
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
                {getAvailableStructures().length > 1 && (
                  <div className="structure-view-selector">
                    {getAvailableStructures().includes('rescue') && (
                      <button
                        className={structureViewMode === 'rescue' ? 'active' : ''}
                        onClick={() => setStructureViewMode('rescue')}
                      >
                        Rescue Structure
                      </button>
                    )}
                    {getAvailableStructures().includes('wt') && (
                      <button
                        className={structureViewMode === 'wt' ? 'active' : ''}
                        onClick={() => setStructureViewMode('wt')}
                      >
                        Wild-Type
                      </button>
                    )}
                    {getAvailableStructures().includes('pathogenic') && (
                      <button
                        className={structureViewMode === 'pathogenic' ? 'active' : ''}
                        onClick={() => setStructureViewMode('pathogenic')}
                      >
                        Pathogenic
                      </button>
                    )}
                  </div>
                )}
                {(() => {
                  try {
                    const structureData = getStructureData();
                    return (
                      <StructureViewer
                        title={getStructureTitle()}
                        pdbData={structureData}
                        highlightResidues={
                          structureViewMode === 'rescue' && getSelectedCandidate()
                            ? [getSelectedCandidate()!.position]
                            : structureViewMode === 'pathogenic' && results
                            ? [] // Could extract mutation position from results.original_mutation
                            : []
                        }
                        overlayImage={
                          structureViewMode === 'rescue' ? getSelectedCandidate()?.overlay_image : undefined
                        }
                      />
                    );
                  } catch (err) {
                    // #region agent log
                    fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'App.tsx:301', 'message': 'Error rendering StructureViewer', 'data': { errorMessage: err instanceof Error ? err.message : String(err), errorStack: err instanceof Error ? err.stack : undefined }, timestamp: Date.now(), runId: 'post-fix', hypothesisId: 'G' }) }).catch(() => { });
                    // #endregion
                    console.error('Error rendering StructureViewer:', err);
                    return (
                      <div className="error-container">
                        <div className="error-message">
                          Error loading structure viewer: {err instanceof Error ? err.message : 'Unknown error'}
                        </div>
                      </div>
                    );
                  }
                })()}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
