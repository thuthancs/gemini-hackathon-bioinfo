#!/usr/bin/env python3
"""
Test Phase 0: mutant sequence creation from wild-type.

Run from backend directory:
  cd backend && python test/test_mutant_from_fasta.py

Or with FASTA file:
  cd backend && python test/test_mutant_from_fasta.py ../draft1/sequence.fasta R249S -t
"""

import os
import sys

# Ensure backend app is importable
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND_DIR)

from app.utils.sequence_utils import create_mutant, validate_sequence

# TP53 wild-type sequence (from backend example)
TP53_EXAMPLE = (
    "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPV"
    "APAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWV"
    "DSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVP"
    "YEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKK"
    "GEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAH"
    "SSHLKSKKGQSTSRHKKLMFKTEGPDSD"
)


def get_sequence_from_fasta(fasta_path: str, translate: bool = False) -> str:
    """Load sequence from FASTA. Uses draft1/parse_fasta if available."""
    proj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    draft1_path = os.path.join(proj, "draft1")
    if draft1_path not in sys.path:
        sys.path.insert(0, draft1_path)
    try:
        from parse_fasta import parse_fasta_file
        result = parse_fasta_file(fasta_path, translate=translate, return_metadata=True)
        sequences = result["sequences"]
        if not sequences:
            raise ValueError(f"No sequences found in {fasta_path}")
        return sequences[0]
    except ImportError:
        msg = "parse_fasta not found. Use built-in TP53 or ensure draft1/parse_fasta.py"
        raise ImportError(msg)


def test_phase0(sequence: str, mutation: str) -> str | None:
    """Test Phase 0: mutant creation. Returns mutant seq or None."""
    print("=" * 50)
    print("Phase 0: Mutant sequence creation")
    print("=" * 50)
    print(f"Mutation: {mutation}")
    print(f"Wild-type length: {len(sequence)} aa")
    print()

    if not validate_sequence(sequence):
        print("ERROR: Invalid sequence (invalid amino acids)")
        return None

    try:
        mutant = create_mutant(sequence, mutation)
        pos = int(mutation[1:-1])
        wt_aa = sequence[pos - 1]
        mut_aa = mutation[-1]
        print(f"Position {pos}: {wt_aa} -> {mut_aa}")
        print(f"Mutant length: {len(mutant)} aa")
        print()
        start = max(0, pos - 7)
        end = min(len(mutant), pos + 6)
        print(f"Context around position {pos}:")
        print(f"  WT:   ...{sequence[start:end]}...")
        print(f"  Mut:  ...{mutant[start:end]}...")
        print()
        print("OK Phase 0 passed!")
        return mutant
    except ValueError as e:
        print(f"ERROR: {e}")
        return None


def main():
    translate = "-t" in sys.argv or "--translate" in sys.argv
    skip = ("--translate", "-t")
    args = [a for a in sys.argv[1:] if not a.startswith("-") and a not in skip]

    if args:
        fasta_path = os.path.abspath(args[0])
        mutation = args[1] if len(args) > 1 else "R249S"
        if not os.path.exists(fasta_path):
            print(f"File not found: {fasta_path}")
            sys.exit(1)
        sequence = get_sequence_from_fasta(fasta_path, translate=translate)
        src = "translated from DNA" if translate else "protein"
        print(f"Loaded from {fasta_path} ({src})")
    else:
        sequence = TP53_EXAMPLE
        mutation = "R249S"
        print("Using TP53 example")

    print()
    result = test_phase0(sequence, mutation)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
