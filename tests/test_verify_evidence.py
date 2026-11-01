from __future__ import annotations

import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_evidence import file_digests, main, verify_directory  # noqa: E402


def md5_hex(data: bytes) -> str:
    try:
        return hashlib.md5(data, usedforsecurity=False).hexdigest()
    except TypeError:
        return hashlib.md5(data).hexdigest()


class VerifyEvidenceTests(unittest.TestCase):
    def test_file_digests_reports_size_md5_sha256(self):
        payload = b"SimTrust-Pre test fixture\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.csv"
            path.write_bytes(payload)
            size, md5, sha256 = file_digests(path)
        self.assertEqual(size, len(payload))
        self.assertEqual(md5, md5_hex(payload))
        self.assertEqual(sha256, hashlib.sha256(payload).hexdigest())

    def test_verify_directory_accepts_exact_size_and_md5(self):
        payload = b"a,b\n1,2\n"
        expected = {
            "sample.csv": {
                "size": len(payload),
                "md5": md5_hex(payload),
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.csv").write_bytes(payload)
            output = io.StringIO()
            status = verify_directory(root, expected, output)
        self.assertEqual(status, 0)
        self.assertIn("PASS: all 1 evidence files", output.getvalue())
        self.assertIn("SHA-256:", output.getvalue())

    def test_verify_directory_flags_missing_file(self):
        expected = {"missing.csv": {"size": 1, "md5": "0" * 32}}
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            status = verify_directory(Path(tmp), expected, output)
        self.assertEqual(status, 1)
        self.assertIn("MISSING  missing.csv", output.getvalue())

    def test_verify_directory_flags_size_and_md5_mismatch(self):
        expected = {"sample.csv": {"size": 100, "md5": "0" * 32}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.csv").write_bytes(b"wrong")
            output = io.StringIO()
            status = verify_directory(root, expected, output)
        self.assertEqual(status, 1)
        self.assertIn("MISMATCH sample.csv", output.getvalue())
        self.assertIn("expected size: 100", output.getvalue())
        self.assertIn("expected MD5:", output.getvalue())

    def test_verify_directory_handles_digest_unavailable_error(self):
        expected = {"sample.csv": {"size": 1, "md5": "0" * 32}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.csv").write_bytes(b"x")
            output = io.StringIO()
            with patch("verify_evidence.file_digests", side_effect=ValueError("MD5 unavailable under FIPS policy")):
                status = verify_directory(root, expected, output)
        self.assertEqual(status, 1)
        self.assertIn("could not compute/read digest", output.getvalue())
        self.assertIn("MD5 unavailable under FIPS policy", output.getvalue())

    def test_verify_directory_handles_read_error(self):
        expected = {"sample.csv": {"size": 1, "md5": "0" * 32}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.csv").write_bytes(b"x")
            output = io.StringIO()
            with patch("verify_evidence.file_digests", side_effect=PermissionError("denied")):
                status = verify_directory(root, expected, output)
        self.assertEqual(status, 1)
        self.assertIn("could not read file", output.getvalue())

    def test_main_rejects_more_than_one_argument(self):
        with patch("sys.stderr", io.StringIO()):
            status = main(["evidence", "unexpected"])
        self.assertEqual(status, 2)

    def test_main_rejects_nonexistent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "does-not-exist"
            output = io.StringIO()
            status = verify_directory(path, {}, output)
        self.assertEqual(status, 2)
        self.assertIn("not found or not a directory", output.getvalue())


if __name__ == "__main__":
    unittest.main()
