# ESMFold Structure Prediction - Usage Guide

## Overview

This pipeline predicts protein 3D structures from mutated sequences using **ESM** (mutation prediction) + **ESMFold** (structure prediction).

**No UniProt ID needed!** ESMFold accepts any amino acid sequence directly.

## Quick Start

### Option 1: One-Command Solution (Recommended)

```bash
python run_structure_prediction.py sequence.fasta
```

This will:
1. Parse your FASTA file
2. Translate DNA to protein (if needed)
3. Run ESM mutation prediction
4. Extract the highest-scoring sequence
5. Generate 3D structure with ESMFold
6. Save all results to `protein_structures/`

### Option 2: Step-by-Step

```python
from esmfold_api import esm_fasta_to_structure

# Complete pipeline
result = esm_fasta_to_structure(
    fasta_path="sequence.fasta",
    output_dir="protein_structures",
    translate=True,
    save_name="my_protein"
)

# Access results
print(f"Structure: {result['structure_file']}")
print(f"Sequence: {result['sequence_file']}")
print(f"Score: {result['score']}")
```

### Option 3: Custom Workflow

```python
from esm_api import predict_from_fasta
from esmfold_api import esm_to_esmfold_pipeline

# Step 1: Get ESM predictions
esm_response = predict_from_fasta("sequence.fasta", translate=True)

# Step 2: Get structure prediction
result = esm_to_esmfold_pipeline(
    esm_response=esm_response,
    output_dir="protein_structures",
    save_name="predicted_mutation"
)
```

## Output Files

All files are saved to `protein_structures/`:

```
protein_structures/
├── predicted_mutation_esmfold.pdb       # 3D structure (PDB format)
├── predicted_mutation_sequence.fasta    # Amino acid sequence
└── predicted_mutation_metadata.json     # Prediction metadata
```

## Visualizing Structures

### Option 1: PyMOL (Desktop)
```bash
pymol protein_structures/predicted_mutation_esmfold.pdb
```

### Option 2: Online Viewers
- Upload to: https://www.rcsb.org/3d-view
- Or: https://molstar.org/viewer/

### Option 3: Python (Py3Dmol)
```python
import py3Dmol

with open('protein_structures/predicted_mutation_esmfold.pdb', 'r') as f:
    pdb_data = f.read()

view = py3Dmol.view(width=800, height=600)
view.addModel(pdb_data, 'pdb')
view.setStyle({'cartoon': {'color': 'spectrum'}})
view.zoomTo()
view.show()
```

## Command-Line Options

```bash
# Basic usage
python esmfold_api.py sequence.fasta

# Custom output name
python esmfold_api.py sequence.fasta my_protein

# Direct sequence input
python esmfold_api.py --sequence=MKTAYIAKQRQISFVK...
```

## API Functions

### `esm_fasta_to_structure(fasta_path, output_dir, translate, save_name)`
**Complete end-to-end pipeline from FASTA to structure.**

### `esm_to_esmfold_pipeline(esm_response, output_dir, save_name)`
**Pipeline from ESM response to structure.**

### `predict_structure_with_esmfold(sequence, output_dir, save_name)`
**Direct structure prediction from amino acid sequence.**

### `extract_top_sequence_from_esm(esm_response)`
**Extract highest-scoring sequence from ESM results.**

## Advantages of ESMFold

✅ **No UniProt ID needed** - accepts any sequence  
✅ **Fast predictions** - 30-60 seconds per structure  
✅ **Free API** - no authentication required  
✅ **Novel sequences** - works with mutated/engineered proteins  
✅ **Good accuracy** - competitive with AlphaFold2  

## Workflow Diagram

```
FASTA File
    ↓
Parse & Translate (parse_fasta.py)
    ↓
ESM Mutation Prediction (esm_api.py)
    ↓
Extract Top Sequence (esmfold_api.py)
    ↓
ESMFold Structure Prediction (esmfold_api.py)
    ↓
Save PDB + Metadata (protein_structures/)
```

## Troubleshooting

### Error: "ESMFold API error: 400"
- Check that your sequence contains only valid amino acids (A-Z)
- Remove any special characters or spaces

### Error: "No sequence found in ESM response"
- Ensure your FASTA file has a `<mask>` token, or let the script add it automatically
- Check that ESM API credentials are set in `.env`

### Prediction takes too long
- ESMFold is slower for very long sequences (>1000 amino acids)
- Consider splitting large proteins into domains

## References

- ESM: https://github.com/facebookresearch/esm
- ESMFold: https://esmatlas.com/about
- ESMFold API: https://api.esmatlas.com/

