#!/usr/bin/env python3
"""
Test Phase 5: Gemini final validation of rescue candidates.

Requires GEMINI_API_KEY in backend/.env

Phase 5 reviews candidates with ESM scores and RMSD, then approves the best.

Run from backend directory:
  cd backend && python test/test_phase5_gemini.py --mock

  # Full pipeline (Phase 1 -> 2 -> 3&4 -> 5):
  cd backend && python test/test_phase5_gemini.py R249S TP53
"""

import os
import sys

# Ensure backend app is importable
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND_DIR)

# Mock analyzed candidates (from Phase 3&4) for testing Phase 5
MOCK_ANALYZED = [
    {
        "position": 168,
        "original_aa": "H",
        "rescue_aa": "R",
        "mutation": "H168R",
        "reasoning": "Compensatory mutation based on literature",
        "esm_score": 0.05,
        "rmsd": 1.2,
        "rmsd_vs_mutant": 1.2,
        "rmsd_vs_wt": 2.1,
        "structural_recovery": "good",
        "status": "validated",
    },
    {
        "position": 273,
        "original_aa": "R",
        "rescue_aa": "H",
        "mutation": "R273H",
        "reasoning": "Hotspot rescue from literature",
        "esm_score": 0.03,
        "rmsd": 2.5,
        "rmsd_vs_mutant": 2.5,
        "rmsd_vs_wt": 3.0,
        "structural_recovery": "poor",
        "status": "validated",
    },
]


def test_phase5(candidates: list) -> bool:
    """Test Phase 5: Gemini final validation."""
    print("=" * 50)
    print("Phase 5: Gemini final validation")
    print("=" * 50)
    print(f"Input candidates: {len(candidates)}")
    print()

    try:
        from app.services.gemini_service import final_validation

        result = final_validation(candidates)
        approved = result.get("approved", [])
        summary = result.get("summary", "")

        print(f"Approved: {len(approved)}/{len(candidates)}")
        print(f"Summary: {summary}")
        print()

        for c in approved:
            mut = c.get("mutation", "?")
            rmsd = c.get("rmsd")
            rec = c.get("structural_recovery", "?")
            print(f"  {mut}: RMSD={rmsd} Å, recovery={rec}")

        print()
        print("OK Phase 5 passed!")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        if "503" in str(e) or "overloaded" in str(e).lower():
            print("  Gemini API overloaded. Try again later or use --mock.")
        if "API key" in str(e).lower():
            print("  Ensure GEMINI_API_KEY is set in backend/.env")
        return False


def main():
    use_mock = "--mock" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--mock"]

    if use_mock:
        candidates = MOCK_ANALYZED
        print("Using mock analyzed candidates")
    else:
        # Run full pipeline Phases 1-4
        try:
            from app.services.gemini_service import get_rescue_candidates
            from app.services.esm_service import validate_with_esm
            from app.services.analysis_service import predict_and_analyze

            mutation = args[0] if args else "R249S"
            protein = args[1] if len(args) > 1 else "TP53"

            TP53_WT = (
                "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPR"
                "MPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPAL"
                "NKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHL"
                "IRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLED"
                "SSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPL"
                "DGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTE"
                "GPDSD"
            )
            TP53_MUTANT = (
                "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPR"
                "MPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPAL"
                "NKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHL"
                "IRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRSPILTIITLED"
                "SSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPL"
                "DGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTE"
                "GPDSD"
            )

            cands = get_rescue_candidates(mutation, protein)
            validated = validate_with_esm(TP53_MUTANT, cands)
            candidates, _, _ = predict_and_analyze(TP53_WT, TP53_MUTANT, validated)
            print(f"Got {len(candidates)} analyzed candidates from Phases 1-4")
        except Exception as e:
            print(f"Phases 1-4 failed: {e}")
            print("  Use --mock to test Phase 5 with mock candidates")
            sys.exit(1)

    print()
    ok = test_phase5(candidates)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
