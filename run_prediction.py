"""
Example script to run ESM predictions on a FASTA file.
"""

from esm_api import predict_from_fasta
import json
import requests

# Path to your FASTA file
fasta_file = "sequence.fasta"

print(f"Loading and processing {fasta_file}...")

# First, let's see what sequences we're working with
from parse_fasta import parse_fasta_file

parsed_result = parse_fasta_file(fasta_file, translate=True, return_metadata=True)
sequences = parsed_result['sequences']
metadata = parsed_result['metadata']

print(f"Found {len(sequences)} sequence(s)")
for i, (seq, meta) in enumerate(zip(sequences, metadata), 1):
    print(f"  Sequence {i}: {meta['amino_acids']} amino acids")
    print(f"    First 50 chars: {seq[:50]}...")

print("\nAdding ONE <mask> token for ESM predictions...")
print("(ESM API predicts what amino acid should be at the masked position)")
print(f"(Masking middle position - you can customize with mask_positions parameter)\n")

try:
    # This function automatically:
    # 1. Parses the FASTA file
    # 2. Translates nucleotides to amino acids (if translate=True)
    # 3. Adds ONE <mask> token (required by ESM API - exactly 1 per sequence)
    # 4. Sends sequences to ESM API
    # 5. Returns predictions for what should be at the masked position
    
    # Example: mask position 50 (0-indexed)
    # Or use None to mask the middle position (default)
    print("Making API request...")
    results = predict_from_fasta(fasta_file, translate=True, mask_positions=None)
    print("API request completed!")
    
    print("✅ Predictions received!")
    print(f"Number of sequences processed: {len(results.get('results', []))}\n")
    
    # Print results in a readable format
    print(json.dumps(results, indent=2))
    
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("Make sure you have a .env file with BIOLM_API_TOKEN set")
except requests.RequestException as e:
    print(f"❌ API Request Error: {e}")
    print("\nPossible issues:")
    print("  1. Sequences need <mask> tokens for ESM predictions")
    print("  2. Sequence might be too long")
    print("  3. Invalid sequence format")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

