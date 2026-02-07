"""Utility functions for sequence manipulation and validation."""
import re
from typing import Optional


VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")


def create_mutant(wt_sequence: str, mutation: str) -> str:
    """
    Create a mutant sequence by applying a mutation.
    
    Args:
        wt_sequence: Wild-type protein sequence
        mutation: Mutation in format like 'R249S' (replace position 249 with S)
    
    Returns:
        Mutant sequence with the mutation applied
    
    Raises:
        ValueError: If mutation format is invalid or position is out of range
    """
    if not mutation or len(mutation) < 3:
        raise ValueError(f"Invalid mutation format: {mutation}. Expected format like 'R249S'")
    
    # Parse mutation: R249S -> position 249, new_aa = S
    match = re.match(r'^([A-Z])(\d+)([A-Z])$', mutation)
    if not match:
        raise ValueError(f"Invalid mutation format: {mutation}. Expected format like 'R249S'")
    
    original_aa, position_str, new_aa = match.groups()
    position = int(position_str) - 1  # Convert to 0-indexed
    
    if position < 0 or position >= len(wt_sequence):
        raise ValueError(f"Position {position + 1} is out of range for sequence of length {len(wt_sequence)}")
    
    if wt_sequence[position] != original_aa:
        raise ValueError(
            f"Expected {original_aa} at position {position + 1}, but found {wt_sequence[position]}"
        )
    
    if new_aa not in VALID_AMINO_ACIDS:
        raise ValueError(f"Invalid amino acid: {new_aa}")
    
    mutant = list(wt_sequence)
    mutant[position] = new_aa
    return ''.join(mutant)


def parse_fasta(fasta_content: str) -> str:
    """
    Parse FASTA format and extract sequence.
    
    Args:
        fasta_content: FASTA file content (may include header lines)
    
    Returns:
        Protein sequence as a single string
    
    Raises:
        ValueError: If FASTA format is invalid or no sequence found
    """
    lines = [line.strip() for line in fasta_content.strip().split('\n')]
    sequence_lines = [line for line in lines if line and not line.startswith('>')]
    
    if not sequence_lines:
        raise ValueError("No sequence found in FASTA content")
    
    sequence = ''.join(sequence_lines)
    
    # Remove any whitespace that might be in the sequence
    sequence = re.sub(r'\s+', '', sequence)
    
    if not validate_sequence(sequence):
        raise ValueError("Invalid amino acid characters found in sequence")
    
    return sequence


def apply_mutation(sequence: str, position: int, new_aa: str) -> str:
    """
    Apply a mutation to a sequence at a specific position.
    
    Args:
        sequence: Protein sequence
        position: 0-indexed position
        new_aa: New amino acid to insert
    
    Returns:
        Mutated sequence
    
    Raises:
        ValueError: If position is out of range or amino acid is invalid
    """
    if position < 0 or position >= len(sequence):
        raise ValueError(f"Position {position} is out of range for sequence of length {len(sequence)}")
    
    if new_aa not in VALID_AMINO_ACIDS:
        raise ValueError(f"Invalid amino acid: {new_aa}")
    
    seq_list = list(sequence)
    seq_list[position] = new_aa
    return ''.join(seq_list)


def validate_sequence(sequence: str) -> bool:
    """
    Validate that a sequence contains only valid amino acid characters.
    
    Args:
        sequence: Protein sequence to validate
    
    Returns:
        True if sequence is valid, False otherwise
    """
    if not sequence:
        return False
    
    return all(aa in VALID_AMINO_ACIDS for aa in sequence.upper())


def get_amino_acid_at_position(sequence: str, position: int) -> str:
    """
    Get the amino acid at a specific position (1-indexed).
    
    Args:
        sequence: Protein sequence
        position: 1-indexed position
    
    Returns:
        Amino acid at that position
    
    Raises:
        ValueError: If position is out of range
    """
    if position < 1 or position > len(sequence):
        raise ValueError(f"Position {position} is out of range for sequence of length {len(sequence)}")
    
    return sequence[position - 1]

