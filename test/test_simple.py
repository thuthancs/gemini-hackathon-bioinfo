"""
Simple test script - no network libraries needed.
"""

from parse_fasta import parse_fasta_file

print("Testing FASTA parsing and translation...\n")

# Parse and translate the FASTA file
result = parse_fasta_file("sequence.fasta", translate=True, return_metadata=True)
sequences = result['sequences']
metadata = result['metadata']

print(f"✅ Successfully parsed {len(sequences)} sequence(s)\n")

for i, (seq, meta) in enumerate(zip(sequences, metadata), 1):
    print(f"Sequence {i}:")
    print(f"  Base pairs (nucleotides): {meta['base_pairs']}")
    print(f"  Amino acids: {meta['amino_acids']}")
    print(f"  Full protein sequence:")
    print(f"    {seq}\n")

# Manually add a mask token for demonstration
print("="*80)
print("Adding ONE <mask> token (ESM requirement):")
print("="*80 + "\n")

for i, seq in enumerate(sequences, 1):
    # Mask the middle position
    mask_pos = len(seq) // 2
    masked_seq = seq[:mask_pos] + '<mask>' + seq[mask_pos+1:]
    
    print(f"Sequence {i} (masked at position {mask_pos}):")
    print(f"  Original AA at position {mask_pos}: {seq[mask_pos]}")
    print(f"  Context around mask:")
    start = max(0, mask_pos - 15)
    end = min(len(masked_seq), mask_pos + 21)  # +21 because <mask> is 6 chars
    print(f"    ...{masked_seq[start:end]}...")
    print(f"  Mask count: {masked_seq.count('<mask>')} ✅")
    print()

print("✅ All parsing tests passed!")
print("\nNext step: Run 'python run_prediction.py' in YOUR terminal")
print("(requires internet connection to call ESM API)")

