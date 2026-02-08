#!/usr/bin/env python3
"""
Test Phase 3 & 4: ESMFold structure prediction + RMSD.

Phase 3: ESMFold predicts structures (no API key; api.esmatlas.com is free)
Phase 4: RMSD between WT and rescued structures

Full sequences supported; retries on 504. Use --save to write PDB files and RMSD.

Run from backend directory:
  cd backend && python test/test_phase3_4_esmfold_rmsd.py --mock --save

  # Full pipeline (Phase 1 -> 2 -> 3&4):
  cd backend && python test/test_phase3_4_esmfold_rmsd.py --save

  # Shorter sequence for faster test:
  cd backend && python test/test_phase3_4_esmfold_rmsd.py --mock --short --save
"""

import os
import sys
from datetime import datetime

# Ensure backend app is importable
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND_DIR)

# TP53 sequences (full and truncated for --short)
TP53_WT = (
    "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPV"
    "APAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWV"
    "DSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVP"
    "YEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKK"
    "GEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAH"
    "SSHLKSKKGQSTSRHKKLMFKTEGPDSD"
)
TP53_MUTANT = (
    "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPV"
    "APAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWV"
    "DSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVP"
    "YEPPEVGSDCTTIHYNYMCNSSCMGGMNRSPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKK"
    "GEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAH"
    "SSHLKSKKGQSTSRHKKLMFKTEGPDSD"
)

# Mock validated candidate (1 for faster test)
MOCK_VALIDATED = [
    {"position": 168, "original_aa": "H", "rescue_aa": "R", "mutation": "H168R",
     "reasoning": "Mock", "esm_score": 0.05, "status": "validated"},
]


def test_phase3_4(wt_seq: str, mutant_seq: str, candidates: list, save: bool = False) -> bool:
    """Test Phase 3 & 4: ESMFold + RMSD."""
    print("=" * 50)
    print("Phase 3 & 4: ESMFold structure prediction + RMSD")
    print("=" * 50)
    print(f"WT length: {len(wt_seq)} aa")
    print(f"Candidates: {len(candidates)}")
    print()

    try:
        from app.services.analysis_service import predict_and_analyze
        from app.config import settings

        print(f"RMSD threshold: <{settings.rmsd_good_threshold} Å = good")
        print()
        print("Calling ESMFold (full sequence; retries on 504)...")
        print()

        out_dir = None
        if save:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dir = os.path.join(_BACKEND_DIR, "test", "results", ts)
            print(f"Saving to: {out_dir}")
            print()

        analyzed, _, _ = predict_and_analyze(
            wt_seq, mutant_seq, candidates, save_results_to=out_dir
        )

        for c in analyzed:
            mut = c.get("mutation", "?")
            rmsd_m = c.get("rmsd_vs_mutant", c.get("rmsd"))
            rmsd_wt = c.get("rmsd_vs_wt")
            rec = c.get("structural_recovery", "?")
            err = c.get("error", "")
            rmsd_str = f" vs mutant={rmsd_m} Å"
            if rmsd_wt is not None:
                rmsd_str += f", vs WT={rmsd_wt} Å"
            print(f"  {mut}: RMSD{rmsd_str}, recovery={rec}")
            if err:
                print(f"    Error: {err}")

        if save and out_dir:
            print()
            print(f"Results saved to {out_dir}:")
            print("  - mutant.pdb (pathogenic baseline)")
            print("  - wild_type.pdb (reference)")
            for c in analyzed:
                mut = c.get("mutation", "?")
                print(f"  - rescue_{mut}.pdb")
            print("  - rmsd_results.json")

        print()
        print("OK Phase 3 & 4 passed!")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    use_mock = "--mock" in sys.argv
    use_short = "--short" in sys.argv
    use_save = "--save" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--mock", "--short", "--save")]

    if use_short:
        wt_seq = TP53_WT[:80]
        mutant_seq = TP53_MUTANT[:80]
        # Position 14 = L in TP53 (MEEPQSDPSVEPPL...)
        candidates = [
            {"position": 14, "original_aa": "L", "rescue_aa": "I",
             "mutation": "L14I", "reasoning": "Mock", "status": "validated"}
        ]
        print("Using short sequence (80 aa) for faster test")
    elif use_mock:
        wt_seq = TP53_WT
        mutant_seq = TP53_MUTANT
        candidates = MOCK_VALIDATED
        print("Using mock validated candidate")
    else:
        # Run Phase 1 + 2 first
        try:
            from app.services.gemini_service import get_rescue_candidates
            from app.services.esm_service import validate_with_esm
            mutation = args[0] if args else "R249S"
            protein = args[1] if len(args) > 1 else "TP53"
            cands = get_rescue_candidates(mutation, protein)
            candidates = validate_with_esm(TP53_MUTANT, cands)
            wt_seq = TP53_WT
            mutant_seq = TP53_MUTANT
            print(f"Got {len(candidates)} validated candidates from Phase 1+2")
        except Exception as e:
            print(f"Phase 1 or 2 failed: {e}")
            print("  Use --mock to test Phase 3&4 with mock candidates")
            sys.exit(1)

    print()
    ok = test_phase3_4(wt_seq, mutant_seq, candidates, save=use_save)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
