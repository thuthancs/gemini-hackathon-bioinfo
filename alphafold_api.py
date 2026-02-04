"""
Utility functions for processing ESM results and preparing sequences for AlphaFold.
"""

import requests
import os
import json
from pathlib import Path
from datetime import datetime

def search_alphafold_database_by_uniprot(uniprot_id):
    """
    Search AlphaFold Database by UniProt ID.
    
    Args:
        uniprot_id: UniProt ID (e.g., "P12345")
        
    Returns:
        dict: Prediction data including URLs to structure files
    """
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    
    response = requests.get(url)
    
    if response.status_code == 404:
        return {"found": False, "message": f"No prediction found for UniProt ID: {uniprot_id}"}
    elif not response.ok:
        raise requests.RequestException(f"API error: {response.status_code}")
    
    return response.json()[0] if response.json() else {"found": False}


def search_alphafold_database(sequence):
    """
    Search AlphaFold Database for existing predictions by sequence.
    Note: This only works if the protein has already been predicted.
    
    Args:
        sequence: Amino acid sequence string
        
    Returns:
        dict: Search results from AlphaFold Database
    """
    # The AlphaFold DB API endpoint for sequence search
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{sequence}"
    
    response = requests.get(url)
    
    if response.status_code == 404:
        return {"found": False, "message": "No prediction found for this sequence"}
    elif not response.ok:
        raise requests.RequestException(f"API error: {response.status_code}")
    
    return response.json()


def download_structure_file(file_url, save_path):
    """
    Download a structure file (PDB, CIF, etc.) from a URL.
    
    Args:
        file_url: URL to the structure file
        save_path: Local path where the file should be saved
        
    Returns:
        str: Path to the saved file
    """
    response = requests.get(file_url)
    
    if not response.ok:
        raise requests.RequestException(f"Failed to download file: {response.status_code}")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
    
    return save_path


def download_alphafold_structure(uniprot_id, output_dir="protein_structures", formats=["pdb", "cif"]):
    """
    Download AlphaFold structure files for a given UniProt ID.
    
    Args:
        uniprot_id: UniProt ID (e.g., "P12345")
        output_dir: Directory to save structure files (default: "protein_structures")
        formats: List of file formats to download (default: ["pdb", "cif"])
                 Options: "pdb", "cif", "bcif"
        
    Returns:
        dict: Dictionary with paths to downloaded files and metadata
    """
    # Search for the protein
    result = search_alphafold_database_by_uniprot(uniprot_id)
    
    if not result.get('found', True):  # found=False or missing key
        return result
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    downloaded_files = {
        'uniprot_id': uniprot_id,
        'files': {},
        'metadata': {}
    }
    
    # Download requested formats
    for fmt in formats:
        if fmt.lower() == "pdb":
            url = result.get('pdbUrl')
            if url:
                filename = f"{uniprot_id}_alphafold.pdb"
                save_path = os.path.join(output_dir, filename)
                download_structure_file(url, save_path)
                downloaded_files['files']['pdb'] = save_path
                print(f"✅ Downloaded PDB: {save_path}")
        
        elif fmt.lower() == "cif":
            url = result.get('cifUrl')
            if url:
                filename = f"{uniprot_id}_alphafold.cif"
                save_path = os.path.join(output_dir, filename)
                download_structure_file(url, save_path)
                downloaded_files['files']['cif'] = save_path
                print(f"✅ Downloaded CIF: {save_path}")
        
        elif fmt.lower() == "bcif":
            url = result.get('bcifUrl')
            if url:
                filename = f"{uniprot_id}_alphafold.bcif"
                save_path = os.path.join(output_dir, filename)
                download_structure_file(url, save_path)
                downloaded_files['files']['bcif'] = save_path
                print(f"✅ Downloaded BCIF: {save_path}")
    
    # Download PAE (Predicted Aligned Error) JSON if available
    pae_url = result.get('paeImageUrl')
    if pae_url:
        # Convert image URL to JSON URL
        pae_json_url = pae_url.replace('pae_image', 'predicted_aligned_error').replace('.png', '_v4.json')
        try:
            filename = f"{uniprot_id}_pae.json"
            save_path = os.path.join(output_dir, filename)
            download_structure_file(pae_json_url, save_path)
            downloaded_files['files']['pae'] = save_path
            print(f"✅ Downloaded PAE: {save_path}")
        except:
            pass  # PAE JSON might not be available
    
    # Save metadata
    downloaded_files['metadata'] = {
        'uniprotAccession': result.get('uniprotAccession'),
        'gene': result.get('gene'),
        'organism': result.get('organism'),
        'sequenceLength': len(result.get('uniprotSequence', '')),
        'globalMetricValue': result.get('globalMetricValue'),
        'downloadDate': datetime.now().isoformat()
    }
    
    # Save metadata to JSON file
    metadata_path = os.path.join(output_dir, f"{uniprot_id}_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(downloaded_files['metadata'], f, indent=2)
    downloaded_files['files']['metadata'] = metadata_path
    print(f"✅ Saved metadata: {metadata_path}")
    
    return downloaded_files

def extract_top_sequence_from_esm(esm_response):
    """
    Extract the amino acid sequence with the highest score from ESM response.
    
    The ESM response contains predictions for masked positions. This function
    selects the prediction with the highest score and returns the complete
    sequence with the predicted amino acid inserted.
    
    Args:
        esm_response: The JSON response from ESM API
        
    Returns:
        str: Continuous amino acid sequence (space-separated converted to continuous)
             Returns None if no valid sequence found
        
    Example:
        >>> esm_response = predict_from_fasta("sequence.fasta")
        >>> top_sequence = extract_top_sequence_from_esm(esm_response)
        >>> print(f"Top sequence: {top_sequence}")
    """
    if 'results' not in esm_response or not esm_response['results']:
        return None
    
    # Get the first result (assuming single sequence prediction)
    result = esm_response['results'][0]
    
    if 'predictions' not in result or not result['predictions']:
        return None
    
    # Find prediction with highest score
    predictions = result['predictions']
    top_prediction = max(predictions, key=lambda x: x.get('score', 0))
    
    # Extract sequence and convert from space-separated to continuous
    space_separated_seq = top_prediction.get('sequence', '')
    continuous_seq = space_separated_seq.replace(' ', '')
    
    return continuous_seq


def extract_top_sequences_from_esm(esm_response):
    """
    Extract the top-scoring sequence from each result in ESM response.
    Useful when processing multiple sequences.
    
    Args:
        esm_response: The JSON response from ESM API
        
    Returns:
        list: List of dictionaries containing:
            - 'sequence': Continuous amino acid string
            - 'predicted_aa': The predicted amino acid at masked position
            - 'score': Confidence score
    """
    sequences = []
    
    if 'results' not in esm_response:
        return sequences
    
    for result in esm_response['results']:
        if 'predictions' not in result or not result['predictions']:
            continue
        
        # Find prediction with highest score
        predictions = result['predictions']
        top_prediction = max(predictions, key=lambda x: x.get('score', 0))
        
        # Extract sequence and convert from space-separated to continuous
        space_separated_seq = top_prediction.get('sequence', '')
        continuous_seq = space_separated_seq.replace(' ', '')
        
        sequences.append({
            'sequence': continuous_seq,
            'predicted_aa': top_prediction.get('token_str', ''),
            'score': top_prediction.get('score', 0)
        })
    
    return sequences


def esm_to_alphafold_pipeline(fasta_path, output_dir="protein_structures", translate=True):
    """
    Complete pipeline: FASTA → ESM prediction → Extract top sequence → Query AlphaFold → Save structures.
    
    Note: This searches the AlphaFold Database for existing predictions.
    For novel sequences, the structure won't be found and you'll need to use
    AlphaFold Server manually or other prediction services.
    
    Args:
        fasta_path: Path to FASTA file
        output_dir: Directory to save structure files (default: "protein_structures")
        translate: Whether to translate nucleotides to amino acids (default: True)
        
    Returns:
        dict: Results including sequences and downloaded files
    """
    from esm_api import predict_from_fasta
    
    print("=" * 70)
    print("PIPELINE: ESM → AlphaFold Structure Prediction")
    print("=" * 70)
    
    # Step 1: Get ESM predictions
    print("\n[Step 1] Running ESM predictions...")
    esm_response = predict_from_fasta(fasta_path, translate=translate)
    print("✅ ESM predictions complete")
    
    # Step 2: Extract top sequence
    print("\n[Step 2] Extracting top-scoring sequence...")
    top_sequence = extract_top_sequence_from_esm(esm_response)
    
    if not top_sequence:
        return {"error": "No sequence found in ESM response"}
    
    print(f"✅ Top sequence: {len(top_sequence)} amino acids")
    print(f"   Preview: {top_sequence[:60]}...")
    
    # Step 3: Search AlphaFold Database
    print("\n[Step 3] Searching AlphaFold Database...")
    print("   Note: This searches for existing predictions in the database.")
    print("   Novel/mutated sequences may not be found.")
    
    # Try to search by sequence (this might not work for novel sequences)
    alphafold_result = search_alphafold_database(top_sequence)
    
    results = {
        'esm_response': esm_response,
        'top_sequence': top_sequence,
        'alphafold_search': alphafold_result,
        'downloaded_files': None
    }
    
    # Step 4: Download structures if found
    if isinstance(alphafold_result, dict) and alphafold_result.get('found') == False:
        print("❌ Sequence not found in AlphaFold Database")
        print("\n💡 Options:")
        print("   1. Use AlphaFold Server: https://alphafold.ebi.ac.uk/")
        print("   2. Use ESMFold for structure prediction")
        print("   3. If this is a known protein, search by UniProt ID")
        print(f"\n   Your sequence has been saved for manual submission:")
        
        # Save sequence to file
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        seq_file = os.path.join(output_dir, "predicted_sequence.fasta")
        with open(seq_file, 'w') as f:
            f.write(f">ESM_Predicted_Sequence\n{top_sequence}\n")
        print(f"   {seq_file}")
        results['sequence_file'] = seq_file
        
    else:
        print("✅ Found in AlphaFold Database!")
        # If we have a UniProt ID, download the structures
        if isinstance(alphafold_result, list) and len(alphafold_result) > 0:
            uniprot_id = alphafold_result[0].get('uniprotAccession')
            if uniprot_id:
                print(f"\n[Step 4] Downloading structures for {uniprot_id}...")
                downloaded = download_alphafold_structure(uniprot_id, output_dir=output_dir)
                results['downloaded_files'] = downloaded
    
    print("\n" + "=" * 70)
    print("✅ Pipeline complete!")
    print("=" * 70)
    
    return results


def save_sequence_for_alphafold(sequence, output_dir="protein_structures", filename="sequence_for_alphafold.fasta"):
    """
    Save a sequence in FASTA format for manual submission to AlphaFold Server.
    
    Args:
        sequence: Amino acid sequence string
        output_dir: Output directory (default: "protein_structures")
        filename: Output filename (default: "sequence_for_alphafold.fasta")
        
    Returns:
        str: Path to saved file
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(f">Predicted_Sequence|Length={len(sequence)}\n")
        # Write sequence in 60-character lines
        for i in range(0, len(sequence), 60):
            f.write(sequence[i:i+60] + "\n")
    
    return filepath


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("AlphaFold API - Structure Download Tool")
    print("=" * 70)
    
    # Example 1: Download by UniProt ID
    if len(sys.argv) > 1 and sys.argv[1].startswith("--uniprot="):
        uniprot_id = sys.argv[1].split("=")[1]
        print(f"\nMode: Download structure by UniProt ID: {uniprot_id}")
        
        try:
            result = download_alphafold_structure(uniprot_id, output_dir="protein_structures")
            print(f"\n✅ Download complete!")
            print(f"   Files saved to: protein_structures/")
            for fmt, path in result.get('files', {}).items():
                print(f"   - {fmt.upper()}: {os.path.basename(path)}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Example 2: Complete pipeline from FASTA
    elif len(sys.argv) > 1 and sys.argv[1].endswith(".fasta"):
        fasta_path = sys.argv[1]
        print(f"\nMode: Complete pipeline from FASTA file")
        
        try:
            result = esm_to_alphafold_pipeline(fasta_path, output_dir="protein_structures")
            
            if result.get('downloaded_files'):
                print(f"\n📁 Files saved to: protein_structures/")
                for fmt, path in result['downloaded_files'].get('files', {}).items():
                    print(f"   - {fmt.upper()}: {os.path.basename(path)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Example 3: Extract sequence from ESM response
    else:
        print("\nMode: Example usage (no arguments provided)")
        print("\nUsage examples:")
        print("  1. Download by UniProt ID:")
        print("     python alphafold_api.py --uniprot=P12345")
        print("")
        print("  2. Complete pipeline from FASTA:")
        print("     python alphafold_api.py sequence.fasta")
        print("")
        print("  3. In your code:")
        print("     from alphafold_api import extract_top_sequence_from_esm, download_alphafold_structure")
        print("")
        print("Available functions:")
        print("  - extract_top_sequence_from_esm(esm_response)")
        print("  - search_alphafold_database(sequence)")
        print("  - search_alphafold_database_by_uniprot(uniprot_id)")
        print("  - download_alphafold_structure(uniprot_id, output_dir)")
        print("  - esm_to_alphafold_pipeline(fasta_path, output_dir)")
        print("  - save_sequence_for_alphafold(sequence, output_dir)")
        print("")
        print("Note: AlphaFold Database only contains pre-computed predictions.")
        print("      Novel/mutated sequences need manual submission to AlphaFold Server.")
        print("      https://alphafold.ebi.ac.uk/")

