#!/usr/bin/env python3
"""Verify byte-level MD5 hashes for the frozen SimTrust-Pre evidence CSVs.

Run from the repository root:
    python scripts/verify_evidence.py

Or provide a different evidence directory:
    python scripts/verify_evidence.py /path/to/evidence
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPECTED_MD5 = {
    "artifact_1_h701_cohort.csv": "38f395a6e5b32fa7c97a13dc6e0cd208",
    "artifact_2_crosswalk_254_parents.csv": "780886326cbb615cfeb3a4a563ed820b",
    "artifact_3_hv_feasibility.csv": "b0345b49abb899a2d7cdca8f65bb1b87",
    "artifact_4_p701p702_events.csv": "127ed0fb1ed7145fd439d7c0e3bf08fe",
}


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    evidence_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("evidence")
    if not evidence_dir.is_dir():
        print(f"ERROR: evidence directory not found: {evidence_dir}", file=sys.stderr)
        return 2

    failures = 0
    for filename, expected in EXPECTED_MD5.items():
        path = evidence_dir / filename
        if not path.is_file():
            print(f"MISSING  {filename}")
            failures += 1
            continue

        actual = md5_file(path)
        if actual == expected:
            print(f"OK       {filename}  {actual}")
        else:
            print(f"MISMATCH {filename}")
            print(f"         expected: {expected}")
            print(f"         actual:   {actual}")
            failures += 1

    if failures:
        print(f"\nFAILED: {failures} file(s) missing or mismatched.")
        return 1

    print("\nPASS: all four evidence files match their recorded MD5 hashes.")
    print("Note: an MD5 match confirms byte-level integrity only; it does not validate semantics.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
