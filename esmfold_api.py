"""
ESMFold API client for structure prediction from ESM sequences.
Direct structure prediction without needing UniProt IDs!
"""

import requests
import os
import json
from pathlib import Path
from datetime import datetime


def extract_top_sequence_from_esm(esm_response):
    """
    Extract the amino acid sequence with the highest score from ESM response.
    
    The ESM response contains predictions for masked positions. This function
    selects the prediction with the highest score and returns the complete
    sequence with the predicted amino acid inserted.
    
    Args:
        esm_response: The JSON response from ESM API
        
    Returns:
        tuple: (sequence, predicted_aa, score) or (None, None, None) if not found
        
    Example:
        >>> esm_response = predict_from_fasta("sequence.fasta")
        >>> sequence, aa, score = extract_top_sequence_from_esm(esm_response)
        >>> print(f"Top sequence: {sequence}")
    """
    if 'results' not in esm_response or not esm_response['results']:
        return None, None, None
    
    # Get the first result (assuming single sequence prediction)
    result = esm_response['results'][0]
    
    # ESM API returns predictions nested under model name (e.g., "esm1v-n4", "esm1v-all")
    # Find the key that contains the predictions (not 'results')
    predictions = None
    for key, value in result.items():
        if isinstance(value, list) and value and 'token' in value[0]:
            predictions = value
            break
    
    if not predictions:
        return None, None, None
    
    # Find prediction with highest score
    top_prediction = max(predictions, key=lambda x: x.get('score', 0))
    
    # Extract sequence and convert from space-separated to continuous
    space_separated_seq = top_prediction.get('sequence', '')
    continuous_seq = space_separated_seq.replace(' ', '')
    
    predicted_aa = top_prediction.get('token_str', '')
    score = top_prediction.get('score', 0)
    
    return continuous_seq, predicted_aa, score


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
        # ESM API returns predictions nested under model name
        # Find the key that contains the predictions
        predictions = None
        for key, value in result.items():
            if isinstance(value, list) and value and 'token' in value[0]:
                predictions = value
                break
        
        if not predictions:
            continue
        
        # Find prediction with highest score
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


def predict_structure_with_esmfold(sequence, output_dir="protein_structures", save_name=None):
    """
    Predict protein structure using ESMFold API.
    This accepts novel/mutated sequences directly - no UniProt ID needed!
    
    Args:
        sequence: Amino acid sequence string
        output_dir: Directory to save structure (default: "protein_structures")
        save_name: Optional custom name for output file
        
    Returns:
        dict: Contains path to PDB file and metadata
    """
    # ESMFold API endpoint (free and public!)
    url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
    
    print(f"🔬 Predicting structure with ESMFold...")
    print(f"   Sequence length: {len(sequence)} amino acids")
    
    # Make prediction request
    response = requests.post(url, data=sequence, headers={'Content-Type': 'text/plain'})
    
    if not response.ok:
        error_msg = f"ESMFold API error: {response.status_code}"
        if response.text:
            error_msg += f"\n{response.text[:200]}"
        raise requests.RequestException(error_msg)
    
    # Save PDB file
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    if save_name:
        filename = f"{save_name}_esmfold.pdb"
    else:
        filename = f"predicted_structure_{len(sequence)}aa_esmfold.pdb"
    
    pdb_path = os.path.join(output_dir, filename)
    
    with open(pdb_path, 'w') as f:
        f.write(response.text)
    
    print(f"✅ Structure predicted and saved: {pdb_path}")
    
    return {
        'pdb_file': pdb_path,
        'sequence': sequence,
        'sequence_length': len(sequence),
        'method': 'ESMFold',
        'prediction_date': datetime.now().isoformat()
    }


def esm_to_esmfold_pipeline(esm_response, output_dir="protein_structures", save_name="esm_predicted"):
    """
    Complete pipeline: Extract top ESM sequence → Predict structure with ESMFold → Save.
    
    This is what you want! No UniProt ID needed.
    
    Args:
        esm_response: The JSON response from ESM API
        output_dir: Directory to save structure files (default: "protein_structures")
        save_name: Base name for output files (default: "esm_predicted")
        
    Returns:
        dict: Results including sequence, structure file path, and metadata
    """
    print("\n" + "=" * 70)
    print("PIPELINE: ESM Mutation Prediction → ESMFold Structure Prediction")
    print("=" * 70)
    
    # Step 1: Extract top sequence from ESM
    print("\n[Step 1] Extracting highest-scoring sequence from ESM...")
    top_sequence, predicted_aa, score = extract_top_sequence_from_esm(esm_response)
    
    if not top_sequence:
        return {"error": "No sequence found in ESM response"}
    
    print(f"✅ Top sequence extracted:")
    print(f"   - Length: {len(top_sequence)} amino acids")
    print(f"   - Predicted AA: {predicted_aa}")
    print(f"   - Score: {score:.6f}")
    print(f"   - Preview: {top_sequence[:60]}...")
    
    # Step 2: Predict structure with ESMFold
    print("\n[Step 2] Predicting 3D structure with ESMFold...")
    print("   (This may take 30-60 seconds depending on sequence length)")
    
    try:
        structure_result = predict_structure_with_esmfold(
            top_sequence, 
            output_dir=output_dir,
            save_name=save_name
        )
    except Exception as e:
        print(f"❌ Structure prediction failed: {e}")
        return {
            "error": str(e),
            "sequence": top_sequence,
            "predicted_aa": predicted_aa,
            "score": score
        }
    
    # Step 3: Save sequence and metadata for reference
    print("\n[Step 3] Saving sequence and metadata...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save sequence as FASTA
    seq_path = os.path.join(output_dir, f"{save_name}_sequence.fasta")
    with open(seq_path, 'w') as f:
        f.write(f">ESM_Predicted_Mutation|AA={predicted_aa}|Score={score:.6f}\n")
        for i in range(0, len(top_sequence), 60):
            f.write(top_sequence[i:i+60] + "\n")
    print(f"✅ Sequence saved: {seq_path}")
    
    # Save metadata as JSON
    metadata = {
        'sequence': top_sequence,
        'sequence_length': len(top_sequence),
        'predicted_amino_acid': predicted_aa,
        'prediction_score': score,
        'structure_file': structure_result['pdb_file'],
        'prediction_method': 'ESMFold',
        'prediction_date': datetime.now().isoformat()
    }
    
    metadata_path = os.path.join(output_dir, f"{save_name}_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved: {metadata_path}")
    
    print("\n" + "=" * 70)
    print("✅ Pipeline complete!")
    print(f"📁 Structure file: {structure_result['pdb_file']}")
    print(f"📁 Sequence file: {seq_path}")
    print(f"📁 Metadata file: {metadata_path}")
    print("=" * 70)
    
    return {
        'sequence': top_sequence,
        'predicted_aa': predicted_aa,
        'score': score,
        'structure_file': structure_result['pdb_file'],
        'sequence_file': seq_path,
        'metadata_file': metadata_path,
        'method': 'ESMFold',
        'metadata': metadata
    }


def esm_fasta_to_structure(fasta_path, output_dir="protein_structures", translate=True, save_name="esm_predicted"):
    """
    One-command solution: FASTA → ESM prediction → Structure prediction → Save.
    
    Complete end-to-end pipeline from a FASTA file to 3D structure.
    
    Args:
        fasta_path: Path to FASTA file
        output_dir: Directory to save all output files (default: "protein_structures")
        translate: Whether to translate nucleotides to amino acids (default: True)
        save_name: Base name for output files (default: "esm_predicted")
        
    Returns:
        dict: Results including all file paths and metadata
    """
    from esm_api import predict_from_fasta
    
    print("\n" + "=" * 70)
    print("COMPLETE PIPELINE: FASTA → ESM → ESMFold → Structure")
    print("=" * 70)
    print(f"\n📂 Input: {fasta_path}")
    print(f"📁 Output: {output_dir}/")
    
    # Step 1: Get ESM predictions
    print("\n[Step 1/3] Running ESM predictions...")
    try:
        esm_response = predict_from_fasta(fasta_path, translate=translate)
        print("✅ ESM predictions complete")
    except Exception as e:
        print(f"❌ ESM prediction failed: {e}")
        return {"error": f"ESM prediction failed: {e}"}
    
    # Step 2-3: Run the ESMFold pipeline
    result = esm_to_esmfold_pipeline(esm_response, output_dir=output_dir, save_name=save_name)
    
    if 'error' in result:
        print(f"\n❌ Pipeline failed: {result['error']}")
    else:
        print("\n🎉 SUCCESS! Your protein structure is ready.")
        print(f"\nYou can visualize it with:")
        print(f"  - PyMOL: pymol {result['structure_file']}")
        print(f"  - Online: https://www.rcsb.org/3d-view")
    
    return result


def save_sequence_for_manual_prediction(sequence, output_dir="protein_structures", filename="sequence_for_prediction.fasta"):
    """
    Save a sequence in FASTA format for manual submission to structure prediction servers.
    
    Args:
        sequence: Amino acid sequence string
        output_dir: Output directory (default: "protein_structures")
        filename: Output filename (default: "sequence_for_prediction.fasta")
        
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
    print("ESMFold API - Structure Prediction Tool")
    print("=" * 70)
    
    # Example 1: Complete pipeline from FASTA
    if len(sys.argv) > 1 and sys.argv[1].endswith(".fasta"):
        fasta_path = sys.argv[1]
        save_name = sys.argv[2] if len(sys.argv) > 2 else "esm_predicted"
        
        print(f"\nMode: Complete pipeline from FASTA file")
        print(f"Input: {fasta_path}")
        
        try:
            result = esm_fasta_to_structure(
                fasta_path, 
                output_dir="protein_structures",
                save_name=save_name
            )
            
            if 'error' not in result:
                print("\n📦 Output files:")
                print(f"   🧬 Structure: {result['structure_file']}")
                print(f"   📝 Sequence: {result['sequence_file']}")
                print(f"   📊 Metadata: {result['metadata_file']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Example 2: Direct sequence input
    elif len(sys.argv) > 1 and sys.argv[1].startswith("--sequence="):
        sequence = sys.argv[1].split("=", 1)[1]
        save_name = sys.argv[2] if len(sys.argv) > 2 else "direct_prediction"
        
        print(f"\nMode: Direct sequence prediction")
        print(f"Sequence length: {len(sequence)} amino acids")
        
        try:
            result = predict_structure_with_esmfold(
                sequence,
                output_dir="protein_structures",
                save_name=save_name
            )
            
            print(f"\n✅ Structure saved: {result['pdb_file']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Example 3: Show usage
    else:
        print("\nMode: Example usage (no arguments provided)")
        print("\n🚀 Usage examples:")
        print("\n  1. Complete pipeline from FASTA (recommended):")
        print("     python esmfold_api.py sequence.fasta [output_name]")
        print("")
        print("  2. Direct sequence prediction:")
        print("     python esmfold_api.py --sequence=MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL")
        print("")
        print("  3. In your code:")
        print("     from esmfold_api import esm_fasta_to_structure")
        print("     result = esm_fasta_to_structure('sequence.fasta')")
        print("")
        print("📚 Available functions:")
        print("  - esm_fasta_to_structure(fasta_path, output_dir)")
        print("     → Complete end-to-end pipeline")
        print("")
        print("  - esm_to_esmfold_pipeline(esm_response, output_dir)")
        print("     → Pipeline from ESM response")
        print("")
        print("  - predict_structure_with_esmfold(sequence, output_dir)")
        print("     → Direct structure prediction from sequence")
        print("")
        print("  - extract_top_sequence_from_esm(esm_response)")
        print("     → Extract best sequence from ESM results")
        print("")
        print("💡 Note: ESMFold accepts any amino acid sequence - no UniProt ID needed!")
        print("   Predictions are fast (~30-60 seconds) and completely free.")

