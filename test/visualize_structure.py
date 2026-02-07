"""
Interactive 3D visualization and PNG export for protein structures.
Supports both Jupyter notebook (interactive 3D) and standalone (PNG export).
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Check and install required dependencies."""
    required = {
        'py3Dmol': 'py3Dmol',
        'PIL': 'Pillow',
        'selenium': 'selenium'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing dependencies: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    return True


def visualize_interactive_3d(pdb_file, style='cartoon', color='spectrum', width=800, height=600):
    """
    Create interactive 3D visualization using py3Dmol.
    Best used in Jupyter notebook.
    
    Args:
        pdb_file: Path to PDB file
        style: Visualization style ('cartoon', 'stick', 'sphere', 'line', 'cross')
        color: Color scheme ('spectrum', 'ss', 'chain', 'residue', 'white', etc.)
        width: View width in pixels
        height: View height in pixels
        
    Returns:
        py3Dmol view object
    """
    try:
        import py3Dmol
    except ImportError:
        print("❌ py3Dmol not installed. Install with: pip install py3Dmol")
        return None
    
    # Read PDB file
    with open(pdb_file, 'r') as f:
        pdb_data = f.read()
    
    # Create viewer
    view = py3Dmol.view(width=width, height=height)
    view.addModel(pdb_data, 'pdb')
    
    # Set style
    if style == 'cartoon':
        view.setStyle({style: {'color': color}})
    elif style == 'stick':
        view.setStyle({style: {'colorscheme': color}})
    elif style == 'sphere':
        view.setStyle({style: {'colorscheme': color}})
    else:
        view.setStyle({style: {}})
    
    # Add surface (optional)
    # view.addSurface(py3Dmol.VDW, {'opacity': 0.7, 'color': 'white'})
    
    view.zoomTo()
    return view


def save_structure_image_pymol(pdb_file, output_png, width=1920, height=1080, ray_trace=True):
    """
    Save high-quality PNG image using PyMOL.
    Requires PyMOL to be installed.
    
    Args:
        pdb_file: Path to PDB file
        output_png: Output PNG file path
        width: Image width in pixels
        height: Image height in pixels
        ray_trace: Whether to use ray tracing for better quality
        
    Returns:
        Path to saved PNG file
    """
    try:
        import pymol
        from pymol import cmd
    except ImportError:
        print("❌ PyMOL not installed.")
        print("Install from: https://pymol.org/")
        return None
    
    # Initialize PyMOL in headless mode
    pymol.finish_launching(['pymol', '-c'])
    
    # Load structure
    cmd.load(pdb_file, 'protein')
    
    # Set visualization
    cmd.hide('everything', 'protein')
    cmd.show('cartoon', 'protein')
    cmd.color('spectrum', 'protein')
    
    # Set background
    cmd.bg_color('white')
    
    # Orient and zoom
    cmd.orient('protein')
    cmd.zoom('protein', 2)
    
    # Set image size
    cmd.viewport(width, height)
    
    # Render and save
    if ray_trace:
        cmd.ray(width, height)
    
    cmd.png(output_png, dpi=300)
    
    # Clean up
    cmd.delete('all')
    pymol.cmd.quit()
    
    print(f"✅ Image saved: {output_png}")
    return output_png


def save_structure_image_py3dmol(pdb_file, output_png, width=1920, height=1080, style='cartoon', color='spectrum'):
    """
    Save PNG image using py3Dmol with selenium.
    Works without PyMOL but requires Chrome/Chromium.
    
    Args:
        pdb_file: Path to PDB file
        output_png: Output PNG file path
        width: Image width in pixels
        height: Image height in pixels
        style: Visualization style
        color: Color scheme
        
    Returns:
        Path to saved PNG file
    """
    try:
        import py3Dmol
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import time
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install py3Dmol selenium")
        return None
    
    # Read PDB file
    with open(pdb_file, 'r') as f:
        pdb_data = f.read()
    
    # Create HTML with embedded viewer
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
    </head>
    <body style="margin:0;padding:0;">
        <div id="viewer" style="width:{width}px;height:{height}px;"></div>
        <script>
            let viewer = $3Dmol.createViewer('viewer');
            viewer.addModel(`{pdb_data}`, 'pdb');
            viewer.setStyle({{{style}: {{'color': '{color}'}}}});
            viewer.zoomTo();
            viewer.render();
        </script>
    </body>
    </html>
    """
    
    # Save temporary HTML
    temp_html = 'temp_viewer.html'
    with open(temp_html, 'w') as f:
        f.write(html_template)
    
    # Setup Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'--window-size={width},{height}')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f'file://{os.path.abspath(temp_html)}')
        time.sleep(2)  # Wait for rendering
        
        driver.save_screenshot(output_png)
        driver.quit()
        
        # Clean up
        os.remove(temp_html)
        
        print(f"✅ Image saved: {output_png}")
        return output_png
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Chrome/Chromium is installed")
        if os.path.exists(temp_html):
            os.remove(temp_html)
        return None


def create_simple_visualization(pdb_file, output_png=None, width=1920, height=1080):
    """
    Create visualization and save as PNG.
    Tries multiple methods in order of preference.
    
    Args:
        pdb_file: Path to PDB file
        output_png: Output PNG path (auto-generated if None)
        width: Image width
        height: Image height
        
    Returns:
        Path to saved PNG file
    """
    if not os.path.exists(pdb_file):
        print(f"❌ File not found: {pdb_file}")
        return None
    
    # Auto-generate output path
    if output_png is None:
        base_name = os.path.splitext(pdb_file)[0]
        output_png = f"{base_name}_visualization.png"
    
    print(f"📊 Creating visualization for: {pdb_file}")
    print(f"📁 Output: {output_png}")
    print()
    
    # Try PyMOL first (best quality)
    print("Attempting PyMOL rendering...")
    result = save_structure_image_pymol(pdb_file, output_png, width, height)
    if result:
        return result
    
    # Try py3Dmol with selenium
    print("\nAttempting py3Dmol rendering...")
    result = save_structure_image_py3dmol(pdb_file, output_png, width, height)
    if result:
        return result
    
    print("\n❌ All visualization methods failed.")
    print("\n💡 Manual options:")
    print(f"   1. Open PyMOL and load: {pdb_file}")
    print(f"   2. Upload to: https://www.rcsb.org/3d-view")
    print(f"   3. Use Jupyter notebook with py3Dmol")
    
    return None


def create_jupyter_notebook_visualization(pdb_file='protein_structures/predicted_mutation_esmfold.pdb'):
    """
    Create a Jupyter notebook with interactive 3D visualization code.
    
    Args:
        pdb_file: Path to PDB file
        
    Returns:
        Path to created notebook
    """
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Interactive 3D Protein Structure Visualization\n",
                    "\n",
                    "This notebook provides interactive visualization of the predicted protein structure."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Install dependencies (run once)\n",
                    "# !pip install py3Dmol biopython"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "import py3Dmol\n",
                    "from IPython.display import display\n",
                    "\n",
                    f"pdb_file = '{pdb_file}'\n",
                    "\n",
                    "# Read PDB file\n",
                    "with open(pdb_file, 'r') as f:\n",
                    "    pdb_data = f.read()\n",
                    "\n",
                    "# Create interactive viewer\n",
                    "view = py3Dmol.view(width=900, height=600)\n",
                    "view.addModel(pdb_data, 'pdb')\n",
                    "view.setStyle({'cartoon': {'color': 'spectrum'}})\n",
                    "view.zoomTo()\n",
                    "\n",
                    "# Display\n",
                    "view.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Alternative Styles\n",
                    "\n",
                    "Try different visualization styles:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Stick representation\n",
                    "view = py3Dmol.view(width=900, height=600)\n",
                    "view.addModel(pdb_data, 'pdb')\n",
                    "view.setStyle({'stick': {'colorscheme': 'chainHetatm'}})\n",
                    "view.zoomTo()\n",
                    "view.show()"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Surface representation\n",
                    "view = py3Dmol.view(width=900, height=600)\n",
                    "view.addModel(pdb_data, 'pdb')\n",
                    "view.setStyle({'cartoon': {'color': 'spectrum'}})\n",
                    "view.addSurface(py3Dmol.VDW, {'opacity': 0.7, 'color': 'white'})\n",
                    "view.zoomTo()\n",
                    "view.show()"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    import json
    notebook_path = "visualize_structure.ipynb"
    with open(notebook_path, 'w') as f:
        json.dump(notebook_content, f, indent=2)
    
    print(f"✅ Created Jupyter notebook: {notebook_path}")
    print(f"\nRun with: jupyter notebook {notebook_path}")
    
    return notebook_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize and export protein structures')
    parser.add_argument('pdb_file', nargs='?', 
                       default='protein_structures/predicted_mutation_esmfold.pdb',
                       help='Path to PDB file')
    parser.add_argument('-o', '--output', help='Output PNG file path')
    parser.add_argument('-w', '--width', type=int, default=1920, help='Image width')
    parser.add_argument('--height', type=int, default=1080, help='Image height')
    parser.add_argument('--notebook', action='store_true', 
                       help='Create Jupyter notebook for interactive visualization')
    
    args = parser.parse_args()
    
    print("🧬 Protein Structure Visualization Tool")
    print("=" * 60)
    
    if args.notebook:
        create_jupyter_notebook_visualization(args.pdb_file)
    else:
        create_simple_visualization(args.pdb_file, args.output, args.width, args.height)

