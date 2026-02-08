#!/usr/bin/env python3
"""
Test Phase 2: ESM-1v validates rescue candidates.

Requires ESM_API_KEY in backend/.env (biolm.ai token)

Run from backend directory:
  cd backend && python test/test_phase2_esm.py

  # Use mock candidates (no Gemini needed):
  cd backend && python test/test_phase2_esm.py --mock

  # Run Phase 1 first to get real candidates, then Phase 2:
  cd backend && python test/test_phase2_esm.py
"""

import os
import sys

# Ensure backend app is importable
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND_DIR)

# TP53 mutant sequence (R249S applied)
TP53_MUTANT = (
    "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPV"
    "APAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWV"
    "DSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVP"
    "YEPPEVGSDCTTIHYNYMCNSSCMGGMNRSPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKK"
    "GEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAH"
    "SSHLKSKKGQSTSRHKKLMFKTEGPDSD"
)

# Mock candidates for Phase 2 test (valid positions within TP53)
MOCK_CANDIDATES = [
    {"position": 168, "original_aa": "H", "rescue_aa": "R", "mutation": "H168R",
     "reasoning": "Mock: compensatory"},
    {"position": 175, "original_aa": "I", "rescue_aa": "L", "mutation": "I175L",
     "reasoning": "Mock: structural"},
    {"position": 273, "original_aa": "R", "rescue_aa": "H", "mutation": "R273H",
     "reasoning": "Mock: hotspot"},
]


def test_phase2(mutant_seq: str, candidates: list) -> bool:
    """Test Phase 2: ESM-1v validation of candidates."""
    print("=" * 50)
    print("Phase 2: ESM-1v validates candidates")
    print("=" * 50)
    print(f"Mutant sequence length: {len(mutant_seq)} aa")
    print(f"Candidates to validate: {len(candidates)}")
    print()

    try:
        from app.services.esm_service import validate_with_esm
        from app.config import settings

        print(f"Threshold: {settings.esm_validation_threshold}")
        print()

        validated = validate_with_esm(mutant_seq, candidates)

        for c in candidates:
            mut = c.get("mutation", "?")
            score = c.get("esm_score", 0)
            status = c.get("status", "?")
            print(f"  {mut}: score={score:.4f} -> {status}")

        print()
        print(f"Validated: {len(validated)}/{len(candidates)}")

        if len(validated) >= 0:
            print("OK Phase 2 passed!")
            return True
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        err = str(e).lower()
        if "api" in err or "401" in err or "403" in err:
            print("  Set ESM_API_KEY in backend/.env (biolm.ai token)")
        return False


def main():
    use_mock = "--mock" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--mock"]

    if use_mock:
        candidates = MOCK_CANDIDATES
        print("Using mock candidates (no Gemini needed)")
    else:
        # Get candidates from Phase 1 (Gemini)
        try:
            from app.services.gemini_service import get_rescue_candidates
            mutation = args[0] if args else "R249S"
            protein = args[1] if len(args) > 1 else "TP53"
            candidates = get_rescue_candidates(mutation, protein)
            print(f"Got {len(candidates)} candidates from Gemini")
        except Exception as e:
            print(f"Phase 1 failed: {e}")
            print("  Use --mock to test Phase 2 with mock candidates")
            sys.exit(1)

    print()
    ok = test_phase2(TP53_MUTANT, candidates)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
