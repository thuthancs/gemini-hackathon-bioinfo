/** Component for sequence and mutation input. */
import { useState, type ChangeEvent, type FormEvent } from 'react';

interface SequenceInputProps {
  onSubmit: (
    sequence: string,
    mutation: string,
    protein: string,
    geneFunction?: string,
    disease?: string,
    organism?: string
  ) => void;
  isLoading: boolean;
}

export default function SequenceInput({ onSubmit, isLoading }: SequenceInputProps) {
  const [sequence, setSequence] = useState('');
  const [mutation, setMutation] = useState('');
  const [protein, setProtein] = useState('TP53');
  const [error, setError] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [geneFunction, setGeneFunction] = useState('');
  const [disease, setDisease] = useState('');
  const [organism, setOrganism] = useState('');

  const handleFileUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;

      // Try to parse FASTA format
      try {
        const lines = content.split('\n');
        const sequenceLines = lines.filter(line => line.trim() && !line.trim().startsWith('>'));
        const parsedSequence = sequenceLines.join('').replace(/\s/g, '');

        if (parsedSequence) {
          setSequence(parsedSequence);
          setError('');
        } else {
          setError('No sequence found in file');
        }
      } catch {
        setError('Failed to parse FASTA file');
      }
    };
    reader.readAsText(file);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate inputs
    if (!sequence.trim()) {
      setError('Please provide a protein sequence');
      return;
    }

    if (!mutation.trim()) {
      setError('Please provide a mutation (e.g., R249S)');
      return;
    }

    // Validate mutation format (e.g., R249S)
    const mutationPattern = /^[A-Z]\d+[A-Z]$/;
    if (!mutationPattern.test(mutation.trim())) {
      setError('Invalid mutation format. Expected format like R249S');
      return;
    }

    // Validate sequence contains only valid amino acids
    const validAAs = /^[ACDEFGHIKLMNPQRSTVWY]+$/i;
    if (!validAAs.test(sequence.trim())) {
      setError('Sequence contains invalid amino acid characters');
      return;
    }

    onSubmit(
      sequence.trim(),
      mutation.trim().toUpperCase(),
      protein.trim() || 'TP53',
      geneFunction.trim() || undefined,
      disease.trim() || undefined,
      organism.trim() || undefined
    );
  };

  return (
    <form onSubmit={handleSubmit} className="sequence-input-form">
      <div className="form-section">
        <label htmlFor="sequence">Protein Sequence (FASTA or raw sequence)</label>
        <textarea
          id="sequence"
          value={sequence}
          onChange={(e) => {
            setSequence(e.target.value);
            setError('');
          }}
          placeholder="Enter protein sequence or upload FASTA file..."
          rows={6}
          disabled={isLoading}
          className="sequence-textarea"
        />
        <div className="file-upload">
          <label htmlFor="file-upload" className="file-upload-label">
            Upload FASTA File
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".fasta,.fa,.fas,.txt"
            onChange={handleFileUpload}
            disabled={isLoading}
            className="file-input"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="mutation">Mutation</label>
          <input
            id="mutation"
            type="text"
            value={mutation}
            onChange={(e) => {
              setMutation(e.target.value);
              setError('');
            }}
            placeholder="e.g., R249S"
            disabled={isLoading}
            className="mutation-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="protein">Protein Name (optional)</label>
          <input
            id="protein"
            type="text"
            value={protein}
            onChange={(e) => setProtein(e.target.value)}
            placeholder="TP53"
            disabled={isLoading}
            className="protein-input"
          />
        </div>
      </div>

      <div className="advanced-options">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="advanced-toggle"
          disabled={isLoading}
        >
          {showAdvanced ? '▼' : '▶'} Advanced Options
        </button>

        {showAdvanced && (
          <div className="advanced-fields">
            <div className="form-group">
              <label htmlFor="gene-function">Gene Function (optional)</label>
              <textarea
                id="gene-function"
                value={geneFunction}
                onChange={(e) => setGeneFunction(e.target.value)}
                placeholder="e.g., DNA binding tumor suppressor"
                disabled={isLoading}
                rows={2}
                className="gene-function-input"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="disease">Disease (optional)</label>
                <input
                  id="disease"
                  type="text"
                  value={disease}
                  onChange={(e) => setDisease(e.target.value)}
                  placeholder="e.g., Li-Fraumeni syndrome"
                  disabled={isLoading}
                  className="disease-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="organism">Organism (optional)</label>
                <input
                  id="organism"
                  type="text"
                  value={organism}
                  onChange={(e) => setOrganism(e.target.value)}
                  placeholder="e.g., Homo sapiens"
                  disabled={isLoading}
                  className="organism-input"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <button
        type="submit"
        disabled={isLoading || !sequence || !mutation}
        className="submit-button"
      >
        {isLoading ? 'Analyzing...' : 'Analyze Mutation'}
      </button>
    </form>
  );
}

