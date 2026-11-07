from __future__ import annotations

import unittest
import json
from scripts.run_stage1_audit_v4_2 import DEFAULT_NOTEBOOK, run_offline_notebook_self_tests
from scripts.verify_historical_artifacts import ROOT as PROJECT_ROOT, build_report


class HistoricalEvidenceTests(unittest.TestCase):
    def test_artifact_1_matches_historical_fingerprint(self) -> None:
        report = build_report(PROJECT_ROOT)
        artifact_1 = next(x for x in report["historical_artifacts"] if x["filename"] == "artifact_1_h701_cohort.csv")
        self.assertEqual(artifact_1["status"], "HISTORICAL_FINGERPRINT_MATCH")
        self.assertEqual(artifact_1["size_bytes"], 19327)
        self.assertEqual(artifact_1["md5"], "38f395a6e5b32fa7c97a13dc6e0cd208")
        self.assertEqual(artifact_1["csv"]["data_rows"], 40)
        self.assertEqual(artifact_1["csv"]["columns"], 21)

    def test_missing_originals_are_not_replaced_by_candidates(self) -> None:
        report = build_report(PROJECT_ROOT)
        historical = {x["filename"]: x for x in report["historical_artifacts"]}
        self.assertEqual(historical["artifact_2_crosswalk_254_parents.csv"]["status"], "MISSING")
        self.assertEqual(historical["artifact_3_hv_feasibility.csv"]["status"], "MISSING")
        self.assertEqual(historical["artifact_4_p701p702_events.csv"]["status"], "MISSING")
        candidates = {x["filename"]: x for x in report["recovered_candidates"]}
        self.assertEqual(
            candidates["artifact_2_crosswalk_v21_APPROX_371.csv"]["classification"],
            "APPROXIMATE_NOT_ORIGINAL",
        )
        self.assertEqual(
            candidates["artifact_4_p701p702_events_REBUILT.csv"]["classification"],
            "REBUILT_NOT_BYTE_IDENTICAL",
        )
        self.assertEqual(report["summary"]["candidate_files_are_historical_substitutes"], 0)

    def test_recovered_intermediate_files_match_recorded_snapshots(self) -> None:
        report = build_report(PROJECT_ROOT)
        candidates = {x["filename"]: x for x in report["recovered_candidates"]}
        # The standalone kit ships these CSV snapshots. A Git checkout may
        # intentionally omit their non-original payloads; absence must remain
        # explicit and must never be treated as a verification pass.
        for filename in ("CW_v2_raw_525.csv", "CW_v21_events.csv"):
            if candidates[filename]["present"]:
                self.assertTrue(candidates[filename]["snapshot_fingerprint_match"])
            else:
                self.assertEqual(candidates[filename]["status"], "CANDIDATE_FILE_MISSING")


class NotebookReproducibilityTests(unittest.TestCase):
    def test_archived_v4_2_notebook_exists_and_is_pinned(self) -> None:
        self.assertTrue(DEFAULT_NOTEBOOK.is_file())
        notebook = json.loads(DEFAULT_NOTEBOOK.read_text(encoding="utf-8"))
        sources = ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
        combined = "\n".join(sources)
        self.assertIn('RECORD_ID = "22250958"', combined)
        self.assertIn('EXPECTED_VERSION = "1.1.3"', combined)
        self.assertIn("DOWNLOAD_SIMULATION = False", combined)

    def test_notebook_offline_synthetic_self_tests(self) -> None:
        # Executes only the pure helper + synthetic test cells; no network or real dataset access.
        run_offline_notebook_self_tests(DEFAULT_NOTEBOOK)


if __name__ == "__main__":
    unittest.main()
