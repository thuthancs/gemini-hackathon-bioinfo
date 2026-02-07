"""
Neurosnap ProteinMPNN API client for protein design predictions.
Uses all the preprocessing steps: FASTA parsing → Translation → PDB conversion → API prediction
"""

import requests
import os
import time
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder
from parse_fasta import parse_fasta_file
from io import BytesIO

# Load environment variables from .env file
load_dotenv()


def get_auth_token():
    """
    Get the authentication token from environment variables.
    
    Returns:
        str: The authentication token
        
    Raises:
        ValueError: If NEUROSNAP_API_KEY is not set in environment
    """
    token = os.getenv("NEUROSNAP_API_KEY")
    if not token:
        raise ValueError(
            "NEUROSNAP_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    return token


def sequence_to_pdb(sequence, chain_id='A'):
    """
    Convert an amino acid sequence to a simple PDB format string.
    Creates a linear backbone structure (not folded).
    
    Args:
        sequence: Amino acid sequence string
        chain_id: Chain identifier (default: 'A')
        
    Returns:
        str: PDB format string
    """
    # Three-letter amino acid codes
    aa_codes = {
        'A': 'ALA', 'C': 'CYS', 'D': 'ASP', 'E': 'GLU', 'F': 'PHE',
        'G': 'GLY', 'H': 'HIS', 'I': 'ILE', 'K': 'LYS', 'L': 'LEU',
        'M': 'MET', 'N': 'ASN', 'P': 'PRO', 'Q': 'GLN', 'R': 'ARG',
        'S': 'SER', 'T': 'THR', 'V': 'VAL', 'W': 'TRP', 'Y': 'TYR'
    }
    
    pdb_lines = []
    pdb_lines.append("HEADER    GENERATED FROM SEQUENCE")
    pdb_lines.append("TITLE     AMINO ACID SEQUENCE TO PDB CONVERSION")
    
    atom_number = 1
    for res_num, aa in enumerate(sequence, start=1):
        if aa not in aa_codes:
            continue  # Skip unknown amino acids
            
        res_name = aa_codes[aa]
        
        # Create CA atom (alpha carbon) - simplified structure
        x = res_num * 3.8  # Approximate spacing
        y = 0.0
        z = 0.0
        
        pdb_line = f"ATOM  {atom_number:>5}  CA  {res_name} {chain_id}{res_num:>4}    {x:>8.3f}{y:>8.3f}{z:>8.3f}  1.00  0.00           C"
        pdb_lines.append(pdb_line)
        atom_number += 1
    
    pdb_lines.append("END")
    return "\n".join(pdb_lines)


def submit_job(pdb_content, job_note="ProteinMPNN prediction", **kwargs):
    """
    Submit a ProteinMPNN job to Neurosnap API.
    
    Args:
        pdb_content: PDB file content as string or bytes
        job_note: Description for the job
        **kwargs: Additional parameters (see Neurosnap docs)
        
    Returns:
        dict: Job ID and submission response
    """
    api_key = get_auth_token()
    
    # Convert string to bytes if needed
    if isinstance(pdb_content, str):
        pdb_content = pdb_content.encode('utf-8')
    
    # Prepare multipart data
    fields = {
        "Input Structure": ("structure.pdb", BytesIO(pdb_content), "chemical/x-pdb")
    }
    
    # Add optional parameters
    optional_params = {
        "Number Sequences": "50",
        "Sampling Temperature": "0.1",
        "Model Type": "v_48_020",
        "Model Version": "original"
    }
    optional_params.update(kwargs)
    
    for key, value in optional_params.items():
        if value is not None and value != "false":
            fields[key] = str(value)
    
    multipart_data = MultipartEncoder(fields=fields)
    
    url = f"https://neurosnap.ai/api/job/submit/ProteinMPNN?note={job_note}"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": multipart_data.content_type,
    }
    
    print(f"Submitting job to Neurosnap ProteinMPNN API...")
    start_time = time.time()
    response = requests.post(url, headers=headers, data=multipart_data)
    elapsed_time = time.time() - start_time
    print(f"Job submitted in {elapsed_time:.2f}s")
    
    if not response.ok:
        error_msg = f"HTTP {response.status_code}: {response.reason}"
        try:
            error_detail = response.json()
            error_msg += f"\nAPI Error: {error_detail}"
        except:
            error_msg += f"\nResponse text: {response.text[:500]}"
        raise requests.RequestException(error_msg)
    
    return response.json()


def predict_from_fasta(fasta_path, translate=True, find_start_codon=True, **kwargs):
    """
    Complete pipeline: Parse FASTA → Translate → Convert to PDB → Submit to ProteinMPNN.
    
    Preprocessing steps:
    1. Parse FASTA file
    2. Translate nucleotides to amino acids (if translate=True)
    3. Find start codon (if find_start_codon=True)
    4. Convert to PDB format
    5. Submit to Neurosnap ProteinMPNN API
    
    Args:
        fasta_path: Path to the FASTA file (can be nucleotides or amino acids)
        translate: If True, translate nucleotide sequences to amino acids (default: True)
        find_start_codon: If True, find ATG start codon before translating (default: True)
        **kwargs: Additional ProteinMPNN parameters
        
    Returns:
        dict: Job ID and submission response
    """
    print(f"Step 1: Parsing FASTA file: {fasta_path}")
    
    # Use all preprocessing: parse + translate with metadata
    result = parse_fasta_file(fasta_path, translate=translate, return_metadata=True, 
                             find_start_codon=find_start_codon)
    sequences = result['sequences']
    metadata = result['metadata']
    
    print(f"Step 2: Preprocessing complete")
    for i, (seq, meta) in enumerate(zip(sequences, metadata), 1):
        print(f"  Sequence {i}:")
        print(f"    Base pairs: {meta['base_pairs']}")
        if translate:
            print(f"    Amino acids: {meta['amino_acids']}")
            print(f"    Preview: {seq[:50]}...")
    
    # For now, use first sequence only
    sequence = sequences[0]
    
    print(f"\nStep 3: Converting sequence to PDB format")
    pdb_content = sequence_to_pdb(sequence)
    print(f"  Generated PDB with {len(sequence)} residues")
    
    print(f"\nStep 4: Submitting to Neurosnap ProteinMPNN API")
    job_response = submit_job(pdb_content, job_note=f"FASTA: {fasta_path}", **kwargs)
    
    return job_response


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        fasta_path = sys.argv[1]
        
        print("="*80)
        print("Neurosnap ProteinMPNN Prediction Pipeline")
        print("="*80 + "\n")
        
        try:
            result = predict_from_fasta(fasta_path, translate=True, find_start_codon=True)
            
            print("\n" + "="*80)
            print("✅ Job submitted successfully!")
            print("="*80)
            print(f"Job ID: {result}")
            print("\nCheck job status at: https://neurosnap.ai")
            
        except ValueError as e:
            print(f"\n❌ Configuration error: {e}")
            print("Make sure you have a .env file with NEUROSNAP_API_KEY set")
        except requests.RequestException as e:
            print(f"\n❌ API request failed: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Usage: python protein_mpn_api.py <fasta_file_path>")
        print("\nExample:")
        print("  python protein_mpn_api.py sequence.fasta")