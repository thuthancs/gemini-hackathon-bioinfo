# Protein Structure Visualization Guide

## Quick Start 🚀

### Option 1: Jupyter Notebook (Recommended)

**Best for: Interactive 3D visualization + PNG export**

```bash
# 1. Install dependencies
pip install py3Dmol biopython pillow jupyter

# 2. Open the notebook
jupyter notebook visualize_structure.ipynb

# 3. Run all cells (Cell → Run All)
```

The notebook will:
- Show interactive 3D visualization
- Let you rotate, zoom, and pan
- Export PNG images automatically

### Option 2: Python Script

```bash
# Install dependencies
pip install py3Dmol selenium biopython pillow

# Create PNG image
python visualize_structure.py protein_structures/predicted_mutation_esmfold.pdb -o output.png
```

### Option 3: Online Viewer (No Installation)

1. Go to https://www.rcsb.org/3d-view
2. Upload `protein_structures/predicted_mutation_esmfold.pdb`
3. Take screenshots as needed

## Methods Comparison

| Method | Interactive | PNG Export | Installation |
|--------|------------|------------|--------------|
| Jupyter Notebook | ✅ Yes | ✅ Yes | Easy |
| PyMOL | ✅ Yes | ✅ High Quality | Medium |
| Online Viewer | ✅ Yes | ✅ Screenshot | None |
| Python Script | ❌ No | ✅ Yes | Medium |

## Jupyter Notebook Features

### 1. Interactive 3D Viewing
- **Rotate**: Click and drag
- **Zoom**: Scroll wheel
- **Pan**: Right-click and drag (or Shift + drag)
- **Reset View**: Double-click

### 2. PNG Export
The notebook automatically saves images to:
```
protein_structures/predicted_mutation_visualization.png
```

You can customize the size:
```python
view = py3Dmol.view(width=3840, height=2160)  # 4K resolution
# ... rest of code ...
png_data = view.png()
```

### 3. Visualization Styles

**Cartoon** (Default):
```python
view.setStyle({'cartoon': {'color': 'spectrum'}})
```

**Stick**:
```python
view.setStyle({'stick': {'colorscheme': 'chainHetatm'}})
```

**Sphere**:
```python
view.setStyle({'sphere': {'colorscheme': 'whiteCarbon'}})
```

**Surface**:
```python
view.addSurface(py3Dmol.VDW, {'opacity': 0.7, 'color': 'white'})
```

### 4. Color Schemes

- `'spectrum'` - Rainbow (N→C terminus, blue→red)
- `'ss'` - Secondary structure (helix=magenta, sheet=yellow, loop=white)
- `'chain'` - Different colors per chain
- `'residue'` - Color by residue type

## PyMOL (Professional Quality)

If you have PyMOL installed:

```bash
pymol protein_structures/predicted_mutation_esmfold.pdb
```

Then in PyMOL:
```
# Ray traced image
ray 3840, 2160
png output_4k.png
```

## Customizing Visualization

### Highlight Specific Residues

```python
# Highlight residue 50
view = py3Dmol.view(width=900, height=600)
view.addModel(pdb_data, 'pdb')
view.setStyle({'cartoon': {'color': 'spectrum'}})
view.addStyle({'resi': 50}, {'stick': {'colorscheme': 'redCarbon', 'radius': 0.3}})
view.zoomTo()
view.show()
```

### Show Mutation Site

If you know the mutation position:

```python
mutation_position = 74  # Example position

view = py3Dmol.view(width=900, height=600)
view.addModel(pdb_data, 'pdb')
view.setStyle({'cartoon': {'color': 'spectrum'}})

# Highlight mutation in red
view.addStyle({'resi': mutation_position}, 
              {'stick': {'color': 'red', 'radius': 0.5}})
view.addStyle({'resi': mutation_position}, 
              {'sphere': {'color': 'red', 'radius': 0.8}})

view.zoomTo({'resi': mutation_position})
view.show()
```

### Side-by-Side Comparison

```python
import py3Dmol

# Load two structures
with open('wild_type.pdb', 'r') as f:
    wt_data = f.read()
with open('mutant.pdb', 'r') as f:
    mut_data = f.read()

# Create viewer
view = py3Dmol.view(width=1200, height=600, linked=False, viewergrid=(1,2))

# Left: Wild type
view.addModel(wt_data, 'pdb', viewer=(0,0))
view.setStyle({'cartoon': {'color': 'blue'}}, viewer=(0,0))
view.zoomTo(viewer=(0,0))

# Right: Mutant
view.addModel(mut_data, 'pdb', viewer=(0,1))
view.setStyle({'cartoon': {'color': 'red'}}, viewer=(0,1))
view.zoomTo(viewer=(0,1))

view.show()
```

## Exporting High-Resolution Images

### Method 1: py3Dmol (in Jupyter)

```python
view = py3Dmol.view(width=3840, height=2160)  # 4K
view.addModel(pdb_data, 'pdb')
view.setStyle({'cartoon': {'color': 'spectrum'}})
view.setBackgroundColor('white')
view.zoomTo()

png_data = view.png()
with open('high_res_output.png', 'wb') as f:
    f.write(png_data)
```

### Method 2: PyMOL (Best Quality)

```python
import pymol
from pymol import cmd

pymol.finish_launching(['pymol', '-c'])
cmd.load('protein.pdb')
cmd.show('cartoon')
cmd.color('spectrum')
cmd.bg_color('white')
cmd.viewport(3840, 2160)
cmd.ray(3840, 2160)
cmd.png('high_quality.png', dpi=300)
```

## Troubleshooting

### Issue: "py3Dmol not displaying"

**Solution**: Make sure you're in Jupyter notebook, not a regular Python script.

```bash
jupyter notebook visualize_structure.ipynb
```

### Issue: "PNG export is blank"

**Solution**: Wait a moment after creating the view before calling `png()`:

```python
view.show()
import time
time.sleep(2)  # Wait for rendering
png_data = view.png()
```

### Issue: "PyMOL not found"

**Solution**: Install PyMOL:
- macOS: `brew install pymol`
- Linux: `sudo apt install pymol`
- Windows: Download from https://pymol.org/

## Gallery Examples

Check out these visualization examples in the notebook:

1. **Rainbow Cartoon** - Standard protein structure view
2. **Secondary Structure** - Highlights helices and sheets
3. **Surface View** - Shows protein surface
4. **Mutation Highlight** - Emphasizes specific residues
5. **Multiple Conformations** - Compare different structures

## Resources

- py3Dmol Documentation: https://3dmol.csb.pitt.edu/
- PyMOL Wiki: https://pymolwiki.org/
- Protein Data Bank: https://www.rcsb.org/
- RCSB 3D Viewer: https://www.rcsb.org/3d-view

## Questions?

For issues or questions, check the notebook cells for inline comments and examples.

