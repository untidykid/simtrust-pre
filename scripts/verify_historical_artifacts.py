#!/usr/bin/env python3
"""Check historical v3.1 CSV fingerprints without promoting reconstructions."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reproducibility" / "historical_fingerprints.json"


def digests(path: Path) -> dict[str, str]:
    md5, sha256 = hashlib.md5(), hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            md5.update(chunk)
            sha256.update(chunk)
    return {"md5": md5.hexdigest(), "sha256": sha256.hexdigest()}


def csv_shape(path: Path) -> dict[str, int]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration:
            return {"data_rows": 0, "columns": 0, "malformed_rows": 0}
        width, rows, malformed = len(header), 0, 0
        for row in reader:
            rows += 1
            malformed += len(row) != width
    return {"data_rows": rows, "columns": width, "malformed_rows": malformed}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def inspect(path: Path, item: dict[str, Any], candidate: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "filename": item["filename"], "path": relative(path), "present": path.is_file()
    }
    if candidate:
        result["classification"] = item["status"]
        result["historical_equivalence"] = False
        result["limitation"] = item.get("limitation", "Not a historical original artifact.")
    if not path.is_file():
        result["status"] = "CANDIDATE_FILE_MISSING" if candidate else "MISSING"
        return result
    result["size_bytes"] = path.stat().st_size
    result.update(digests(path))
    result["csv"] = csv_shape(path)
    if candidate:
        match = (
            result["size_bytes"] == item["size_bytes"]
            and result["md5"] == item["md5"]
            and result["sha256"] == item["sha256"]
            and result["csv"]["data_rows"] == item["rows"]
            and result["csv"]["columns"] == item["columns"]
            and result["csv"]["malformed_rows"] == 0
        )
        result["classification"] = item["status"]
        result["snapshot_fingerprint_match"] = bool(match)
        result["historical_equivalence"] = False
        result["status"] = "CANDIDATE_SNAPSHOT_MATCH" if match else "CANDIDATE_SNAPSHOT_MISMATCH"
        result["limitation"] = item.get("limitation", "Not a historical original artifact.")
    else:
        size_match = result["size_bytes"] == item["expected_size_bytes"]
        md5_match = result["md5"] == item["expected_md5"]
        rows = item.get("expected_rows")
        rows_match = rows is None or result["csv"]["data_rows"] == rows
        result.update({"size_match": size_match, "md5_match": md5_match, "row_count_match": rows_match})
        result["byte_fingerprint_match"] = bool(size_match and md5_match)
        result["status"] = (
            "HISTORICAL_FINGERPRINT_MATCH"
            if size_match and md5_match and rows_match and result["csv"]["malformed_rows"] == 0
            else "PRESENT_BUT_NOT_HISTORICAL_MATCH"
        )
    return result


def build_report(root: Path = ROOT) -> dict[str, Any]:
    manifest = json.loads((root / "reproducibility" / "historical_fingerprints.json").read_text(encoding="utf-8"))
    historical = [inspect(root / "evidence" / x["filename"], x) for x in manifest["historical_artifacts"]]
    candidates = [
        inspect(root / "reproducibility" / "recovered_candidates" / x["filename"], x, candidate=True)
        for x in manifest["recovered_candidates"]
    ]
    count = lambda rows, status: sum(x["status"] == status for x in rows)
    return {
        "report_schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "historical_artifacts": historical,
        "recovered_candidates": candidates,
        "summary": {
            "historical_artifacts_total": len(historical),
            "historical_artifacts_fingerprint_matched": count(historical, "HISTORICAL_FINGERPRINT_MATCH"),
            "historical_artifacts_missing": count(historical, "MISSING"),
            "historical_artifacts_present_but_not_matching": count(historical, "PRESENT_BUT_NOT_HISTORICAL_MATCH"),
            "candidate_files_snapshot_verified": count(candidates, "CANDIDATE_SNAPSHOT_MATCH"),
            "candidate_files_are_historical_substitutes": 0,
        },
        "interpretation": "A size+MD5 match is a byte-fingerprint match, not proof of provenance or semantic validity. Approximate, rebuilt, and intermediate files never satisfy a missing historical original.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reproducibility" / "runs" / "historical_fingerprint_report.json")
    parser.add_argument("--strict", action="store_true", help="Fail unless all four historical artifacts match.")
    args = parser.parse_args()
    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for item in report["historical_artifacts"]:
        print(f"{item['filename']}: {item['status']}")
    for item in report["recovered_candidates"]:
        print(f"{item['filename']}: {item['status']} [{item.get('classification', 'unavailable')}]" )
    print("Summary:", json.dumps(report["summary"], sort_keys=True))
    return int(args.strict and report["summary"]["historical_artifacts_fingerprint_matched"] != 4)


if __name__ == "__main__":
    raise SystemExit(main())
