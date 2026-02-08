"""Utility functions for protein structure manipulation and analysis."""
import base64
import logging
from io import StringIO, BytesIO
from typing import List, Dict, Optional
from Bio.PDB import PDBParser, Superimposer, Atom
from Bio.PDB.Structure import Structure

logger = logging.getLogger(__name__)


def calculate_rmsd(pdb1: str, pdb2: str) -> float:
    """
    Calculate RMSD between two PDB structures using CA atoms.
    
    Args:
        pdb1: First PDB structure as string
        pdb2: Second PDB structure as string
    
    Returns:
        RMSD value in Angstroms
    
    Raises:
        ValueError: If PDB parsing fails or structures are incompatible
    """
    try:
        # #region agent log
        try:
            import os, json, time
            log_path = '/Users/thananhthu/gemini-hackathon-bioinfo/.cursor/debug.log'
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({"location":"structure_utils.py:12","message":"calculate_rmsd entry","data":{"pdb1_length":len(pdb1) if pdb1 else 0,"pdb2_length":len(pdb2) if pdb2 else 0,"pdb1_first_50":pdb1[:50] if pdb1 else None,"pdb2_first_50":pdb2[:50] if pdb2 else None},"timestamp":int(time.time()*1000),"runId":"pre-fix","hypothesisId":"G"})+'\n')
        except: pass
        # #endregion
        
        parser = PDBParser(QUIET=True)
        structure1 = parser.get_structure("s1", StringIO(pdb1))
        structure2 = parser.get_structure("s2", StringIO(pdb2))
        
        # #region agent log
        try:
            import os, json, time
            log_path = '/Users/thananhthu/gemini-hackathon-bioinfo/.cursor/debug.log'
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({"location":"structure_utils.py:30","message":"PDB structures parsed","data":{"structure1_residues":len(list(structure1.get_residues())) if structure1 else 0,"structure2_residues":len(list(structure2.get_residues())) if structure2 else 0},"timestamp":int(time.time()*1000),"runId":"pre-fix","hypothesisId":"H"})+'\n')
        except: pass
        # #endregion
        
        # Get CA atoms
        atoms1 = extract_ca_atoms(structure1)
        atoms2 = extract_ca_atoms(structure2)
        
        # #region agent log
        try:
            import os, json, time
            log_path = '/Users/thananhthu/gemini-hackathon-bioinfo/.cursor/debug.log'
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({"location":"structure_utils.py:35","message":"CA atoms extracted","data":{"atoms1_count":len(atoms1),"atoms2_count":len(atoms2)},"timestamp":int(time.time()*1000),"runId":"pre-fix","hypothesisId":"I"})+'\n')
        except: pass
        # #endregion
        
        if len(atoms1) != len(atoms2):
            raise ValueError(
                f"Structures have different numbers of CA atoms: "
                f"{len(atoms1)} vs {len(atoms2)}"
            )
        
        if len(atoms1) == 0:
            raise ValueError("No CA atoms found in structures")
        
        # Superimpose structures
        super_imposer = Superimposer()
        super_imposer.set_atoms(atoms1, atoms2)
        
        rmsd = super_imposer.rms
        
        # #region agent log
        try:
            import os, json, time
            log_path = '/Users/thananhthu/gemini-hackathon-bioinfo/.cursor/debug.log'
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({"location":"structure_utils.py:50","message":"RMSD calculation complete","data":{"rmsd":rmsd},"timestamp":int(time.time()*1000),"runId":"pre-fix","hypothesisId":"J"})+'\n')
        except: pass
        # #endregion
        
        return rmsd
    
    except Exception as e:
        # #region agent log
        try:
            import os, json, time
            log_path = '/Users/thananhthu/gemini-hackathon-bioinfo/.cursor/debug.log'
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({"location":"structure_utils.py:53","message":"RMSD calculation failed","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(time.time()*1000),"runId":"pre-fix","hypothesisId":"K"})+'\n')
        except: pass
        # #endregion
        raise ValueError(f"Failed to calculate RMSD: {str(e)}")


def parse_pdb(pdb_content: str) -> Structure:
    """
    Parse PDB content into a BioPython Structure object.
    
    Args:
        pdb_content: PDB file content as string
    
    Returns:
        BioPython Structure object
    
    Raises:
        ValueError: If PDB parsing fails
    """
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("structure", StringIO(pdb_content))
        return structure
    except Exception as e:
        raise ValueError(f"Failed to parse PDB: {str(e)}")


def extract_ca_atoms(structure: Structure) -> List[Atom]:
    """
    Extract all CA (alpha carbon) atoms from a structure.
    
    Args:
        structure: BioPython Structure object
    
    Returns:
        List of CA atoms
    """
    ca_atoms = []
    for atom in structure.get_atoms():
        if atom.name == "CA":
            ca_atoms.append(atom)
    return ca_atoms


def get_structure_length(pdb_content: str) -> int:
    """
    Get the number of residues in a PDB structure.
    
    Args:
        pdb_content: PDB file content as string
    
    Returns:
        Number of residues
    """
    try:
        structure = parse_pdb(pdb_content)
        return len(list(structure.get_residues()))
    except Exception:
        return 0


def extract_plddt_scores(pdb_content: str) -> Dict[int, float]:
    """
    Extract pLDDT scores from PDB file B-factor column.
    
    In ESMFold PDB files, pLDDT confidence scores are stored in the B-factor column
    (columns 60-66) of ATOM records. This function extracts per-residue pLDDT scores.
    
    Args:
        pdb_content: PDB file content as string
    
    Returns:
        Dictionary mapping residue number (1-indexed) to pLDDT score
    """
    plddt_scores = {}
    
    try:
        for line in pdb_content.split('\n'):
            if line.startswith('ATOM'):
                # Extract residue number (columns 22-26, 1-indexed)
                try:
                    residue_num = int(line[22:26].strip())
                except (ValueError, IndexError):
                    continue
                
                # Extract B-factor (pLDDT) from columns 60-66
                # Format: "ATOM      1  N   MET A   1       6.003   8.284 -13.774  1.00  0.87"
                #                                                                    ^^^^^^
                if len(line) >= 66:
                    try:
                        # Check if this is a CA atom
                        atom_name = line[12:16].strip()
                        if atom_name == 'CA':
                            plddt = float(line[60:66].strip())
                            # Store the pLDDT for this residue (use the CA atom value)
                            plddt_scores[residue_num] = plddt
                    except (ValueError, IndexError):
                        continue
    
    except Exception as e:
        # If parsing fails, return empty dict
        return {}
    
    return plddt_scores


def calculate_mean_plddt(pdb_content: str) -> float:
    """
    Calculate mean pLDDT score from a PDB file.
    
    Args:
        pdb_content: PDB file content as string
    
    Returns:
        Mean pLDDT score, or 0.0 if extraction fails
    """
    try:
        plddt_scores = extract_plddt_scores(pdb_content)
        if not plddt_scores:
            return 0.0
        return sum(plddt_scores.values()) / len(plddt_scores)
    except Exception:
        return 0.0


def generate_structure_overlay(
    wt_pdb: str,
    rescue_pdb: str,
    mutation_positions: List[int]
) -> Optional[str]:
    """
    Generate a structure overlay visualization using py3Dmol.
    
    Creates an overlay of wild-type (blue) and rescue (green) structures,
    highlighting mutation positions (red spheres).
    
    Args:
        wt_pdb: Wild-type PDB structure as string
        rescue_pdb: Rescue PDB structure as string
        mutation_positions: List of residue positions to highlight (1-indexed)
    
    Returns:
        Base64-encoded PNG image as string, or None if generation fails
    """
    try:
        import py3Dmol
        
        # Create view
        view = py3Dmol.view(width=1200, height=800)
        
        # Add wild-type structure (blue, semi-transparent)
        view.addModel(wt_pdb, 'pdb')
        view.setStyle({'model': 0}, {
            'cartoon': {'color': 'blue', 'opacity': 0.7}
        })
        
        # Add rescue structure (green, semi-transparent)
        view.addModel(rescue_pdb, 'pdb')
        view.setStyle({'model': 1}, {
            'cartoon': {'color': 'green', 'opacity': 0.7}
        })
        
        # Highlight mutation positions with red spheres
        for pos in mutation_positions:
            view.addStyle(
                {'resi': pos},
                {'sphere': {'color': 'red', 'radius': 1.5}}
            )
        
        # Zoom to fit
        view.zoomTo()
        
        # Render to PNG
        # Note: py3Dmol's png() method may require a display
        # If headless rendering fails, we'll catch and return None
        try:
            png_data = view.png()
            if png_data:
                # Encode as base64
                return base64.b64encode(png_data).decode('utf-8')
        except Exception as e:
            logger.warning(f"Failed to generate PNG from py3Dmol: {e}")
            # Try alternative: return None and let caller handle
            return None
        
        return None
    
    except ImportError:
        logger.warning("py3Dmol not available, skipping visualization")
        return None
    except Exception as e:
        logger.error(f"Error generating structure overlay: {e}")
        return None

