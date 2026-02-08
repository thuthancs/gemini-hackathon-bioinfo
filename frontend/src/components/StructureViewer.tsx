/** Component for displaying 3D protein structures using NGL viewer (CDN). */
import { useEffect, useRef, useState } from 'react';
import './StructureViewer.css';

interface StructureViewerProps {
    pdbData?: string; // PDB file content as string
    pdbUrl?: string; // URL to fetch PDB file
    title?: string;
    highlightResidues?: number[]; // Residue positions to highlight (1-indexed)
    overlayImage?: string; // Base64-encoded overlay image
}

declare global {
    interface Window {
        NGL: any;
    }
}

export default function StructureViewer({
    pdbData,
    pdbUrl,
    title = 'Protein Structure',
    highlightResidues = [],
    overlayImage,
}: StructureViewerProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const stageRef = useRef<any>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [scriptLoaded, setScriptLoaded] = useState(false);
    const [viewMode, setViewMode] = useState<'structure' | 'overlay'>('structure');

    // Load NGL viewer from CDN
    useEffect(() => {
        if (window.NGL) {
            setScriptLoaded(true);
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://unpkg.com/ngl@2.0.0-dev.35/dist/ngl.js';
        script.async = true;
        script.onload = () => {
            setScriptLoaded(true);
        };
        script.onerror = () => {
            setError('Failed to load NGL viewer library');
        };
        document.head.appendChild(script);

        return () => {
            if (script.parentNode) {
                script.parentNode.removeChild(script);
            }
        };
    }, []);

    // Load structure when script is loaded
    useEffect(() => {
        if (!scriptLoaded || !containerRef.current || (!pdbData && !pdbUrl)) {
            return;
        }

        const loadStructure = async () => {
            try {
                setIsLoading(true);
                setError(null);

                // #region agent log
                fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'StructureViewer.tsx:64', 'message': 'Loading structure in NGL viewer', 'data': { hasPdbData: !!pdbData, hasPdbUrl: !!pdbUrl, pdbDataLength: pdbData?.length || 0, pdbDataFirst50: pdbData?.substring(0, 50), title }, timestamp: Date.now(), runId: 'post-fix', hypothesisId: 'D' }) }).catch(() => { });
                // #endregion

                // Dispose old stage before creating new one
                if (stageRef.current) {
                    try {
                        stageRef.current.dispose();
                    } catch (e) {
                        // Ignore disposal errors
                    }
                    stageRef.current = null;
                }

                // Create NGL stage (NGL will handle container cleanup)
                // Ensure container is still valid (React might have unmounted)
                if (!containerRef.current) {
                    // #region agent log
                    fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'StructureViewer.tsx:83', 'message': 'Container ref is null, aborting', 'data': {}, timestamp: Date.now(), runId: 'post-fix', hypothesisId: 'H' }) }).catch(() => { });
                    // #endregion
                    setIsLoading(false);
                    return;
                }

                const stage = new window.NGL.Stage(containerRef.current, {
                    backgroundColor: 'white',
                });
                stageRef.current = stage;

                let component: any;

                if (pdbData) {
                    // Load from string data
                    const blob = new Blob([pdbData], { type: 'text/plain' });
                    component = await stage.loadFile(blob, { ext: 'pdb' });
                } else if (pdbUrl) {
                    // Load from URL
                    component = await stage.loadFile(pdbUrl, { ext: 'pdb' });
                }

                if (component) {
                    // Add default representation
                    component.addRepresentation('cartoon', {
                        color: 'sstruc',
                    });
                    component.addRepresentation('ball+stick', {
                        sele: 'hetero',
                    });

                    // Highlight specific residues if provided
                    if (highlightResidues.length > 0) {
                        const selection = highlightResidues.map((pos) => `:${pos}`).join(' or ');
                        component.addRepresentation('licorice', {
                            sele: selection,
                            color: 'red',
                        });
                    }

                    // Auto-view
                    stage.autoView();
                }

                setIsLoading(false);
                // #region agent log
                fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'StructureViewer.tsx:122', 'message': 'Structure loaded successfully', 'data': { hasComponent: !!component, pdbDataLength: pdbData?.length || 0 }, timestamp: Date.now(), runId: 'post-fix', hypothesisId: 'D' }) }).catch(() => { });
                // #endregion
            } catch (err) {
                console.error('Error loading structure:', err);
                // #region agent log
                fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'StructureViewer.tsx:124', 'message': 'Error in loadStructure', 'data': { errorMessage: err instanceof Error ? err.message : String(err), errorStack: err instanceof Error ? err.stack : undefined, pdbDataLength: pdbData?.length || 0 }, timestamp: Date.now(), runId: 'post-fix', hypothesisId: 'D' }) }).catch(() => { });
                // #endregion
                setError(err instanceof Error ? err.message : 'Failed to load structure');
                setIsLoading(false);
            }
        };

        loadStructure();

        // Cleanup
        return () => {
            if (stageRef.current) {
                stageRef.current.dispose();
                stageRef.current = null;
            }
        };
    }, [scriptLoaded, pdbData, pdbUrl, highlightResidues]);

    if (error) {
        return (
            <div className="structure-viewer-error">
                <p>Error loading structure: {error}</p>
                <p className="structure-viewer-hint">
                    Structure visualization requires PDB format data. If available, it will be displayed here.
                </p>
            </div>
        );
    }

    if (!pdbData && !pdbUrl) {
        return (
            <div className="structure-viewer-placeholder">
                <p>No structure data available</p>
                <p className="structure-viewer-hint">
                    PDB structure data will be displayed here when available from the pipeline.
                </p>
            </div>
        );
    }

    return (
        <div className="structure-viewer-container">
            <div className="structure-viewer-header">
                <h4>{title}</h4>
                {overlayImage && (
                    <div className="view-mode-toggle">
                        <button
                            className={viewMode === 'structure' ? 'active' : ''}
                            onClick={() => setViewMode('structure')}
                            disabled={!pdbData && !pdbUrl}
                        >
                            3D Structure
                        </button>
                        <button
                            className={viewMode === 'overlay' ? 'active' : ''}
                            onClick={() => setViewMode('overlay')}
                        >
                            Overlay Image
                        </button>
                    </div>
                )}
                {isLoading && viewMode === 'structure' && (
                    <span className="loading-indicator">Loading structure...</span>
                )}
            </div>
            {viewMode === 'overlay' && overlayImage ? (
                <div className="overlay-image-container">
                    <img
                        src={`data:image/png;base64,${overlayImage}`}
                        alt="Structure overlay"
                        className="overlay-image"
                    />
                    <div className="overlay-legend">
                        <div className="legend-item">
                            <span className="legend-color blue"></span>
                            <span>Wild-type</span>
                        </div>
                        <div className="legend-item">
                            <span className="legend-color green"></span>
                            <span>Rescue</span>
                        </div>
                        <div className="legend-item">
                            <span className="legend-color red"></span>
                            <span>Mutation sites</span>
                        </div>
                    </div>
                </div>
            ) : (
                <>
                    <div ref={containerRef} className="structure-viewer" />
                    {highlightResidues.length > 0 && (
                        <div className="structure-viewer-info">
                            Highlighted residues: {highlightResidues.join(', ')}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

