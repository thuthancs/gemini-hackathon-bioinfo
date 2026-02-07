/** Component for sequence and mutation input. */
import { useState, ChangeEvent, FormEvent } from 'react';

interface SequenceInputProps {
  onSubmit: (sequence: string, mutation: string, protein: string) => void;
  isLoading: boolean;
}

export default function SequenceInput({ onSubmit, isLoading }: SequenceInputProps) {
  const [sequence, setSequence] = useState('');
  const [mutation, setMutation] = useState('');
  const [protein, setProtein] = useState('TP53');
  const [fileContent, setFileContent] = useState('');
  const [error, setError] = useState('');

  const handleFileUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setFileContent(content);
      
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
      } catch (err) {
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

    onSubmit(sequence.trim(), mutation.trim().toUpperCase(), protein.trim() || 'TP53');
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

