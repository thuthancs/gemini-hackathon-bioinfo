"""
FASTA file parsing utilities
FASTA file can be DNA and RNA
"""

# Standard genetic code table (DNA codons)
GENETIC_CODE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}


def translate_nucleotide_to_amino_acid(nucleotide_seq, find_start_codon=True):
    """
    Translate a nucleotide sequence (DNA/RNA) to an amino acid sequence.
    
    Args:
        nucleotide_seq: String of nucleotides (DNA or RNA)
        find_start_codon: If True, find ATG start codon and translate from there.
                         If False, translate from position 0.
        
    Returns:
        String of amino acids (single letter code)
    """
    # Convert RNA to DNA if needed (U -> T)
    seq = nucleotide_seq.upper().replace('U', 'T')
    
    # Remove any non-nucleotide characters
    seq = ''.join(c for c in seq if c in 'ATCG')
    
    # Find start codon (ATG) if requested
    start_pos = 0
    if find_start_codon:
        start_pos = seq.find('ATG')
        if start_pos == -1:
            # No start codon found, return empty sequence
            return ''
    
    # Translate codons to amino acids
    amino_acids = []
    for i in range(start_pos, len(seq) - 2, 3):
        codon = seq[i:i+3]
        if len(codon) == 3:
            amino_acid = GENETIC_CODE.get(codon, 'X')  # 'X' for unknown codons
            if amino_acid == '*':  # Stop codon
                break
            amino_acids.append(amino_acid)
    
    return ''.join(amino_acids)


def parse_fasta_file(fasta_path, translate=False, return_metadata=False, find_start_codon=True):
    """
    Parse a FASTA file and return a list of sequences.
    Uses pure Python - no external dependencies required.
    
    Args:
        fasta_path: Path to the FASTA file
        translate: If True, translate nucleotide sequences to amino acids
        return_metadata: If True, return dictionary with sequences and metadata
        find_start_codon: If True and translating, find ATG start codon first (default: True)
        
    Returns:
        If return_metadata=False: List of sequence strings (nucleotides or amino acids)
        If return_metadata=True: Dictionary with 'sequences' and 'metadata' keys
            - 'sequences': List of sequence strings
            - 'metadata': List of dicts with 'base_pairs', 'amino_acids' (if translated), etc.
    """
    sequences = []
    nucleotide_seqs = []  # Store original nucleotide sequences
    current_seq = ""
    
    with open(fasta_path, 'r') as handle:
        for line in handle:
            line = line.strip()
            if line.startswith('>'):
                # Header line - save previous sequence if exists
                if current_seq:
                    nucleotide_seqs.append(current_seq)
                    if translate:
                        sequences.append(translate_nucleotide_to_amino_acid(current_seq, find_start_codon))
                    else:
                        sequences.append(current_seq)
                    current_seq = ""
            else:
                # Sequence line - append to current sequence
                current_seq += line
        
        # Don't forget the last sequence
        if current_seq:
            nucleotide_seqs.append(current_seq)
            if translate:
                sequences.append(translate_nucleotide_to_amino_acid(current_seq, find_start_codon))
            else:
                sequences.append(current_seq)
    
    if return_metadata:
        metadata = []
        for i, (nuc_seq, seq) in enumerate(zip(nucleotide_seqs, sequences)):
            # Count base pairs (nucleotides)
            base_pairs = len(''.join(c for c in nuc_seq.upper() if c in 'ATCGU'))
            meta = {
                'base_pairs': base_pairs,
                'nucleotides': len(nuc_seq)
            }
            if translate:
                meta['amino_acids'] = len(seq)
            metadata.append(meta)
        
        return {
            'sequences': sequences,
            'metadata': metadata
        }
    
    return sequences


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        fasta_path = sys.argv[1]
        translate = '--translate' in sys.argv or '-t' in sys.argv
        
        result = parse_fasta_file(fasta_path, translate=translate, return_metadata=True)
        sequences = result['sequences']
        metadata = result['metadata']
        
        seq_type = "amino acids" if translate else "nucleotides"
        print(f"Loaded {len(sequences)} sequences from {fasta_path}")
        for i, (seq, meta) in enumerate(zip(sequences, metadata), 1):
            print(f"  Sequence {i}:")
            print(f"    Base pairs: {meta['base_pairs']}")
            if translate:
                print(f"    Amino acids: {meta['amino_acids']}")
                if len(seq) > 0:
                    print(f"    First 50 AA: {seq[:50]}")
            else:
                print(f"    Nucleotides: {len(seq)}")
    else:
        print("Usage: python parse_fasta.py <fasta_file_path> [--translate|-t]")
        print("  Use --translate or -t to convert nucleotide sequences to amino acids")

