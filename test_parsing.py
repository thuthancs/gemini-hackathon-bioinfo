"""
Test script to verify FASTA parsing and mask token addition (no API call).
"""

from parse_fasta import parse_fasta_file
from esm_api import add_mask_tokens

# Path to your FASTA file
fasta_file = "sequence.fasta"

print(f"Testing FASTA parsing: {fasta_file}\n")

# Parse and translate
result = parse_fasta_file(fasta_file, translate=True, return_metadata=True)
sequences = result['sequences']
metadata = result['metadata']

print(f"✅ Found {len(sequences)} sequence(s)")
for i, (seq, meta) in enumerate(zip(sequences, metadata), 1):
    print(f"\nSequence {i}:")
    print(f"  Base pairs: {meta['base_pairs']}")
    print(f"  Amino acids: {meta['amino_acids']}")
    print(f"  First 80 AA: {seq[:80]}")

print("\n" + "="*80)
print("Testing mask token addition:")
print("="*80)

# Test adding mask token
masked_sequences = add_mask_tokens(sequences, mask_positions=None)

for i, (original, masked) in enumerate(zip(sequences, masked_sequences), 1):
    print(f"\nSequence {i}:")
    print(f"  Original length: {len(original)}")
    print(f"  Masked length: {len(masked)}")
    
    # Find the mask position
    mask_pos = masked.find('<mask>')
    if mask_pos != -1:
        print(f"  Mask position: {mask_pos}")
        print(f"  Original AA at that position: {original[mask_pos]}")
        print(f"  Context (10 chars before and after mask):")
        start = max(0, mask_pos - 10)
        end = min(len(masked), mask_pos + 16)  # +16 because '<mask>' is 6 chars
        print(f"    ...{masked[start:end]}...")
    
    # Count mask tokens
    mask_count = masked.count('<mask>')
    print(f"  Total <mask> tokens: {mask_count} {'✅' if mask_count == 1 else '❌'}")

print("\n✅ All tests completed!")
print("\nReady to send to ESM API!")
print("The API will predict what amino acid should be at the <mask> position.")

