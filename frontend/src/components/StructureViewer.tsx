/** Component for displaying 3D protein structures using NGL viewer (CDN). */
import { useEffect, useRef, useState } from 'react';
import './StructureViewer.css';

interface StructureViewerProps {
  pdbData?: string; // PDB file content as string
  pdbUrl?: string; // URL to fetch PDB file
  title?: string;
  highlightResidues?: number[]; // Residue positions to highlight (1-indexed)
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
}: StructureViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);

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

        // Create NGL stage
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
      } catch (err) {
        console.error('Error loading structure:', err);
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
        {isLoading && <span className="loading-indicator">Loading structure...</span>}
      </div>
      <div ref={containerRef} className="structure-viewer" />
      {highlightResidues.length > 0 && (
        <div className="structure-viewer-info">
          Highlighted residues: {highlightResidues.join(', ')}
        </div>
      )}
    </div>
  );
}

