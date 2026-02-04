"""
Complete workflow: ESM mutation prediction → ESMFold structure prediction.
One-command solution to get protein structures from FASTA files.
"""

from esmfold_api import esm_fasta_to_structure
import sys

def main():
    # Configuration
    fasta_file = "sequence.fasta"
    output_dir = "protein_structures"
    save_name = "predicted_mutation"
    
    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        fasta_file = sys.argv[1]
    if len(sys.argv) > 2:
        save_name = sys.argv[2]
    
    print("🧬 Protein Structure Prediction Pipeline")
    print("=" * 60)
    print(f"Input FASTA: {fasta_file}")
    print(f"Output directory: {output_dir}/")
    print(f"Output name: {save_name}")
    print("=" * 60)
    
    try:
        # Run the complete pipeline
        result = esm_fasta_to_structure(
            fasta_path=fasta_file,
            output_dir=output_dir,
            translate=True,  # Translate DNA to protein
            save_name=save_name
        )
        
        if 'error' in result:
            print(f"\n❌ Pipeline failed: {result['error']}")
            return 1
        
        # Success! Show results
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Structure prediction complete")
        print("=" * 60)
        print("\n📦 Generated files:")
        print(f"   🧬 3D Structure (PDB): {result['structure_file']}")
        print(f"   📝 Sequence (FASTA): {result['sequence_file']}")
        print(f"   📊 Metadata (JSON): {result['metadata_file']}")
        
        print("\n📊 Prediction details:")
        print(f"   Sequence length: {len(result['sequence'])} amino acids")
        print(f"   Predicted mutation: {result['predicted_aa']}")
        print(f"   Confidence score: {result['score']:.6f}")
        print(f"   Method: {result['method']}")
        
        print("\n💡 Next steps:")
        print("   1. Visualize structure:")
        print(f"      pymol {result['structure_file']}")
        print("      OR upload to: https://www.rcsb.org/3d-view")
        print("")
        print("   2. Analyze structure quality")
        print("   3. Compare with wild-type structure")
        print("   4. Study mutation impact")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

