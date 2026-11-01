#!/usr/bin/env python3
"""Verify the frozen SimTrust-Pre evidence CSVs by size and MD5.

SHA-256 is also computed and printed for stronger future provenance records.
These checks establish byte-level integrity only; they do not validate the
scientific meaning or correctness of the CSV contents.

Run from the repository root:
    python scripts/verify_evidence.py

Or provide an evidence directory:
    python scripts/verify_evidence.py /path/to/evidence
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Mapping, TextIO

EXPECTED: dict[str, dict[str, int | str]] = {
    "artifact_1_h701_cohort.csv": {
        "size": 19327,
        "md5": "38f395a6e5b32fa7c97a13dc6e0cd208",
    },
    "artifact_2_crosswalk_254_parents.csv": {
        "size": 78322,
        "md5": "780886326cbb615cfeb3a4a563ed820b",
    },
    "artifact_3_hv_feasibility.csv": {
        "size": 11863,
        "md5": "b0345b49abb899a2d7cdca8f65bb1b87",
    },
    "artifact_4_p701p702_events.csv": {
        "size": 3539,
        "md5": "127ed0fb1ed7145fd439d7c0e3bf08fe",
    },
}


def _new_md5():
    """Return an MD5 object for legacy integrity checking, including FIPS builds."""
    try:
        return hashlib.md5(usedforsecurity=False)
    except TypeError:  # Python/OpenSSL builds without the usedforsecurity keyword.
        return hashlib.md5()


def file_digests(path: Path) -> tuple[int, str, str]:
    """Return (size in bytes, MD5 hex digest, SHA-256 hex digest)."""
    md5 = _new_md5()
    sha256 = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            md5.update(chunk)
            sha256.update(chunk)
    return size, md5.hexdigest(), sha256.hexdigest()


def verify_directory(
    evidence_dir: Path,
    expected: Mapping[str, Mapping[str, int | str]] = EXPECTED,
    output: TextIO = sys.stdout,
) -> int:
    """Verify all expected files. Return 0 on success, 1 on evidence failures, 2 on path errors."""
    if not evidence_dir.is_dir():
        print(
            f"ERROR: evidence directory not found or not a directory: {evidence_dir}",
            file=output,
        )
        return 2

    failures = 0
    for filename, record in expected.items():
        path = evidence_dir / filename
        if not path.is_file():
            print(f"MISSING  {filename}", file=output)
            failures += 1
            continue

        try:
            actual_size, actual_md5, actual_sha256 = file_digests(path)
        except OSError as exc:
            print(f"ERROR    {filename}: could not read file ({exc})", file=output)
            failures += 1
            continue

        size_ok = actual_size == int(record["size"])
        md5_ok = actual_md5.lower() == str(record["md5"]).lower()
        if size_ok and md5_ok:
            print(
                f"OK       {filename}  size={actual_size}  md5={actual_md5}",
                file=output,
            )
        else:
            print(f"MISMATCH {filename}", file=output)
            if not size_ok:
                print(f"         expected size: {record['size']}", file=output)
                print(f"         actual size:   {actual_size}", file=output)
            if not md5_ok:
                print(f"         expected MD5: {record['md5']}", file=output)
                print(f"         actual MD5:   {actual_md5}", file=output)
            failures += 1

        print(f"         SHA-256: {actual_sha256}", file=output)

    if failures:
        print(
            f"\nFAILED: {failures} file(s) missing, unreadable, or mismatched.",
            file=output,
        )
        return 1

    print(
        f"\nPASS: all {len(expected)} evidence files match their recorded size and MD5 values.",
        file=output,
    )
    print(
        "SHA-256 values are printed for recording alongside the original artifacts.",
        file=output,
    )
    print("Integrity checks do not validate scientific semantics.", file=output)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print(
            "Usage: python scripts/verify_evidence.py [evidence_directory]",
            file=sys.stderr,
        )
        return 2

    evidence_dir = Path(args[0]) if args else Path("evidence")
    return verify_directory(evidence_dir)


if __name__ == "__main__":
    raise SystemExit(main())
