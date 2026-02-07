"""Utility functions for protein structure manipulation and analysis."""
from io import StringIO
from typing import List
from Bio.PDB import PDBParser, Superimposer, Atom
from Bio.PDB.Structure import Structure


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
        parser = PDBParser(QUIET=True)
        structure1 = parser.get_structure("s1", StringIO(pdb1))
        structure2 = parser.get_structure("s2", StringIO(pdb2))
        
        # Get CA atoms
        atoms1 = extract_ca_atoms(structure1)
        atoms2 = extract_ca_atoms(structure2)
        
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
        
        return super_imposer.rms
    
    except Exception as e:
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

