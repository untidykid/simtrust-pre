"""Run the reviewed v5.2 modules' synthetic-only smoke-test suites."""
from __future__ import annotations

import sys
import unittest

import pandas as pd
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from SimTrust_Pre_v5_2_Module1_reviewed import run_smoke_tests as module1_smoke_tests
from SimTrust_Pre_v5_2_Module2_reviewed import run_smoke_tests as module2_smoke_tests
from SimTrust_Pre_v5_2_Module3_reviewed import (
    _strict_bool_flag,
    run_smoke_tests as module3_smoke_tests,
)
from SimTrust_Pre_v5_2_Module4_1_Reviewed import run_smoke_tests as module4_1_smoke_tests
from SimTrust_Pre_v5_2_Module5_reviewed import run_smoke_tests as module5_smoke_tests


class ReviewedV52SyntheticSmokeTests(unittest.TestCase):
    """These tests exercise synthetic fixtures; they never download Zenodo data."""

    def test_module_1_sampling_and_weighting(self) -> None:
        module1_smoke_tests()

    def test_module_2_paired_utility_and_controls(self) -> None:
        module2_smoke_tests()

    def test_module_3_pre_onset_q_and_provenance(self) -> None:
        module3_smoke_tests()

    def test_module_3_boolean_parser_accepts_decimal_string_flags(self) -> None:
        parsed = _strict_bool_flag(pd.Series(["1.0", "0.0", "unknown"]), name="fixture")
        self.assertTrue(bool(parsed.iloc[0]))
        self.assertFalse(bool(parsed.iloc[1]))
        self.assertTrue(pd.isna(parsed.iloc[2]))

    def test_module_4_1_real_window_construction(self) -> None:
        module4_1_smoke_tests()

    def test_module_5_end_to_end_orchestration(self) -> None:
        module5_smoke_tests()


if __name__ == "__main__":
    unittest.main()
