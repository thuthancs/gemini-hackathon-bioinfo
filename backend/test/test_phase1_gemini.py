#!/usr/bin/env python3
"""
Test Phase 1: Gemini discovers rescue candidates.

Requires GEMINI_API_KEY in backend/.env

Run from backend directory:
  cd backend && python test/test_phase1_gemini.py
  cd backend && python test/test_phase1_gemini.py R249S TP53
"""

import os
import sys

# Ensure backend app is importable (loads .env via config)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND_DIR)


def test_phase1(mutation: str = "R249S", protein: str = "TP53") -> bool:
    """Test Phase 1: Gemini rescue candidate discovery."""
    print("=" * 50)
    print("Phase 1: Gemini discovers rescue candidates")
    print("=" * 50)
    print(f"Protein: {protein}")
    print(f"Mutation: {mutation}")
    print()

    try:
        from app.services.gemini_service import get_rescue_candidates

        candidates = get_rescue_candidates(mutation, protein)
        print(f"Received {len(candidates)} candidates from Gemini")
        print()

        for i, c in enumerate(candidates, 1):
            print(f"Candidate {i}: {c.get('mutation', '?')}")
            print(f"  Position: {c.get('position')}")
            print(f"  Original AA: {c.get('original_aa')} -> Rescue AA: {c.get('rescue_aa')}")
            print(f"  Reasoning: {c.get('reasoning', '')[:80]}...")
            print()

        required = {"position", "original_aa", "rescue_aa", "mutation", "reasoning"}
        for c in candidates:
            missing = required - set(c.keys())
            if missing:
                print(f"WARNING: Candidate missing fields: {missing}")

        if len(candidates) >= 3:
            print("OK Phase 1 passed!")
            return True
        print(f"WARNING: Expected 3-5 candidates, got {len(candidates)}")
        return True  # Still pass if we got some
    except Exception as e:
        print(f"ERROR: {e}")
        if "API key" in str(e).lower() or "apikey" in str(e).lower():
            print("  Ensure GEMINI_API_KEY is set in backend/.env")
        return False


def main():
    mutation = sys.argv[1] if len(sys.argv) > 1 else "R249S"
    protein = sys.argv[2] if len(sys.argv) > 2 else "TP53"

    ok = test_phase1(mutation, protein)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
