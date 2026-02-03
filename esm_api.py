"""
ESM API client for making predictions.
"""

import requests
import os
from dotenv import load_dotenv
from parse_fasta import parse_fasta_file

# Load environment variables from .env file
load_dotenv()


def get_auth_token():
    """
    Get the authentication token from environment variables.
    
    Returns:
        str: The authentication token
        
    Raises:
        ValueError: If BIOLM_API_TOKEN is not set in environment
    """
    token = os.getenv("BIOLM_API_TOKEN")
    if not token:
        raise ValueError(
            "BIOLM_API_TOKEN not found in environment variables. "
            "Please set it in your .env file."
        )
    return token


def predict_sequences(sequences, model="esm1v-all"):
    """
    Make predictions for a list of sequences using the ESM API.
    
    Args:
        sequences: List of sequence strings (can include <mask> tokens)
        model: Model name (default: "esm1v-all")
        
    Returns:
        dict: API response containing predictions
        
    Raises:
        requests.RequestException: If the API request fails
        ValueError: If authentication token is missing
    """
    url = f"https://biolm.ai/api/v3/{model}/predict/"
    token = get_auth_token()
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "params": {},
        "items": [{"sequence": seq} for seq in sequences]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    # Better error handling - show actual API error message
    if not response.ok:
        error_msg = f"HTTP {response.status_code}: {response.reason}"
        try:
            error_detail = response.json()
            if isinstance(error_detail, dict) and 'detail' in error_detail:
                error_msg += f"\nAPI Error: {error_detail['detail']}"
            else:
                error_msg += f"\nResponse: {error_detail}"
        except:
            error_msg += f"\nResponse text: {response.text[:500]}"
        raise requests.RequestException(error_msg)
    
    return response.json()


def add_mask_tokens(sequences, mask_positions=None):
    """
    Add ONE <mask> token to sequences for ESM predictions.
    ESM API requires exactly ONE mask token per sequence.
    
    Args:
        sequences: List of sequence strings
        mask_positions: Position to mask (0-indexed). 
                       If None, masks the middle position.
                       Can be int (same position for all) or list of ints (one per sequence).
        
    Returns:
        List of sequences with ONE <mask> token added
    """
    masked_sequences = []
    
    for i, seq in enumerate(sequences):
        seq_list = list(seq)
        
        if mask_positions is None:
            # Default: mask the middle position
            position = len(seq) // 2
        elif isinstance(mask_positions, int):
            # Single position for all sequences
            position = mask_positions if mask_positions < len(seq) else len(seq) // 2
        elif isinstance(mask_positions, list):
            # Different position per sequence
            if i < len(mask_positions):
                position = mask_positions[i] if mask_positions[i] < len(seq) else len(seq) // 2
            else:
                position = len(seq) // 2
        else:
            position = len(seq) // 2
        
        # Replace ONE position with <mask>
        if 0 <= position < len(seq_list):
            seq_list[position] = '<mask>'
        
        masked_sequences.append(''.join(seq_list))
    
    return masked_sequences


def predict_from_fasta(fasta_path, model="esm1v-all", translate=True, mask_positions=None):
    """
    Convenience function to parse a FASTA file and make predictions.
    Automatically translates nucleotide sequences to amino acids if translate=True.
    Adds ONE <mask> token for ESM predictions (required by API).
    
    Args:
        fasta_path: Path to the FASTA file
        model: Model name (default: "esm1v-all")
        translate: If True, translate nucleotide sequences to amino acids (default: True)
        mask_positions: Position to mask (0-indexed). If None, masks middle position.
                       Can be int (same for all) or list of ints (one per sequence).
        
    Returns:
        dict: API response containing predictions for the masked position
    """
    sequences = parse_fasta_file(fasta_path, translate=translate)
    
    # Add mask tokens if sequences don't already have them
    has_masks = any('<mask>' in seq for seq in sequences)
    if not has_masks:
        sequences = add_mask_tokens(sequences, mask_positions=mask_positions)
    
    return predict_sequences(sequences, model=model)


if __name__ == "__main__":
    import sys
    
    # Example 1: Use FASTA file (recommended)
    if len(sys.argv) > 1:
        fasta_path = sys.argv[1]
        translate = True  # Default: translate nucleotides to amino acids
        if '--no-translate' in sys.argv:
            translate = False
        
        print(f"Processing FASTA file: {fasta_path}")
        try:
            results = predict_from_fasta(fasta_path, translate=translate)
            print("✅ Predictions received!")
            print(f"Number of sequences: {len(results.get('results', []))}")
            # Uncomment to see full results:
            # import json
            # print(json.dumps(results, indent=2))
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        # Example 2: Use sequences directly
        print("Example: Using sequences directly")
        example_sequences = ["ACDG<mask>HIKLMN", "XPQRS<mask>FGT"]
        try:
            results = predict_sequences(example_sequences)
            print("✅ Predictions received!")
            print(f"Number of sequences: {len(results.get('results', []))}")
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            print("Make sure you have a .env file with BIOLM_API_TOKEN set")
        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")
        print("\nUsage: python esm_api.py <fasta_file_path> [--no-translate]")

