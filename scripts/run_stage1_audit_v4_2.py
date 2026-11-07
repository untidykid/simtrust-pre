#!/usr/bin/env python3
"""Execute the archived SimTrust-Pre v4.2 Stage 1 audit notebook reproducibly.

The notebook pins Zenodo record 22250958, version 1.1.3, validates the small
source archives using the record's own size/MD5 metadata, and leaves the 2.1-GB
simulation time-series archive disabled by default.
"""
from __future__ import annotations

import argparse
import json
import os
import warnings
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOK = ROOT / "notebooks" / "archive" / "SimTrust_Pre_Audit_v4_2_UNEXECUTED.ipynb"


def read_notebook_json(notebook_path: Path) -> dict[str, Any]:
    """Read notebook JSON with the standard library for offline helper tests."""
    return json.loads(notebook_path.read_text(encoding="utf-8"))


def read_nbformat_notebook(notebook_path: Path):
    """Read/normalize a notebook for nbclient without changing the archived file."""
    import nbformat

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Cell is missing an id field")
        notebook = nbformat.read(notebook_path, as_version=4)
    _, notebook = nbformat.validator.normalize(notebook)
    return notebook


def run_offline_notebook_self_tests(notebook_path: Path = DEFAULT_NOTEBOOK) -> None:
    """Run only the notebook's pure synthetic helper tests; no network or data access."""
    notebook = read_notebook_json(notebook_path)
    helper_cell = None
    self_test_cell = None
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "def simtrust_pre_window_metrics(" in source:
            helper_cell = source
        if "All offline synthetic self-tests passed" in source:
            self_test_cell = source
    if helper_cell is None or self_test_cell is None:
        raise RuntimeError("Could not identify the v4.2 helper and offline self-test cells.")

    namespace: dict[str, Any] = {
        "np": np,
        "pd": pd,
        "Any": Any,
        "Optional": Optional,
    }
    exec(compile(helper_cell, f"{notebook_path}::helper-cell", "exec"), namespace)
    exec(compile(self_test_cell, f"{notebook_path}::self-test-cell", "exec"), namespace)


def execute_notebook(
    notebook_path: Path,
    output_notebook: Path,
    work_dir: Path,
    timeout: int,
    kernel_name: str,
) -> None:
    if not notebook_path.is_file():
        raise FileNotFoundError(f"Audit notebook not found: {notebook_path}")
    work_dir.mkdir(parents=True, exist_ok=True)
    output_notebook.parent.mkdir(parents=True, exist_ok=True)

    # The notebook source is kept unchanged in Git. This environment variable
    # only selects the execution output/cache directory for this run.
    os.environ["SIMTRUST_WORK_DIR"] = str(work_dir.resolve())
    import nbformat
    from nbclient import NotebookClient

    notebook = read_nbformat_notebook(notebook_path)

    # Make the work directory configurable without editing the source notebook.
    target = 'WORK_DIR = Path("/content/simtrust_pre_audit") if Path("/content").exists() else Path("simtrust_pre_audit")'
    replacement = 'WORK_DIR = Path(os.environ.get("SIMTRUST_WORK_DIR", "/content/simtrust_pre_audit" if Path("/content").exists() else "simtrust_pre_audit"))'
    patched = False
    for cell in notebook.cells:
        if cell.cell_type == "code" and target in cell.source:
            cell.source = cell.source.replace(target, replacement, 1)
            patched = True
            break
    if not patched:
        raise RuntimeError("Notebook work-directory assignment was not found; refusing an unreviewed run.")

    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name=kernel_name,
        allow_errors=False,
        resources={"metadata": {"path": str(ROOT)}},
    )
    executed = client.execute()
    nbformat.write(executed, output_notebook)
    print(f"Executed notebook saved to: {output_notebook}")
    print(f"Audit working directory: {work_dir}")
    print("The notebook itself verifies the pinned Zenodo version and downloaded-file size/MD5 metadata.")
    print("The 2.1-GB simulation archive remains disabled unless its notebook flag is explicitly changed.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--work-dir", type=Path, default=ROOT / "reproducibility" / "runs" / "v4_2_data")
    parser.add_argument("--output-notebook", type=Path, default=ROOT / "reproducibility" / "runs" / "v4_2_executed.ipynb")
    parser.add_argument("--timeout", type=int, default=7200, help="Per-cell execution timeout in seconds.")
    parser.add_argument("--kernel-name", default="python3")
    parser.add_argument("--self-test-only", action="store_true", help="Run the notebook's synthetic helper tests only; do not contact Zenodo.")
    args = parser.parse_args()

    run_offline_notebook_self_tests(args.notebook)
    if args.self_test_only:
        print("Offline v4.2 synthetic self-tests passed. No Zenodo download or dataset-level analysis was performed.")
        return 0

    execute_notebook(
        notebook_path=args.notebook.resolve(),
        output_notebook=args.output_notebook.resolve(),
        work_dir=args.work_dir.resolve(),
        timeout=args.timeout,
        kernel_name=args.kernel_name,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
