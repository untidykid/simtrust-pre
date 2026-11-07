# SimTrust-Pre reproducibility kit

This kit creates a clean execution path for the **v4.2 Stage 1 metadata/feasibility audit** while preserving the distinction between the locked **v3.1 historical evidence** and later, non-equivalent reconstructions.

It does **not** claim that the original v3.1 Artifacts 2–4 have been recovered, and it does not relabel approximate/rebuilt CSVs as originals.

## What this kit can reproduce

The archived notebook at `notebooks/archive/SimTrust_Pre_Audit_v4_2_UNEXECUTED.ipynb` is the source of the v4.2 Stage 1 audit. It is pinned to Zenodo record `22250958`, version `1.1.3`, DOI `10.5281/zenodo.22250958`. It obtains record metadata from the Zenodo API, downloads the selected small audit files, and verifies each downloaded file against the size and checksum exposed by that exact record response.

The notebook audits:

- archive member inventories and structural experiment/phase identities;
- label CSV schemas and selected categorical values;
- all uncertainty-archive interpolation flags and per-column dynamics;
- YAML anomaly and perturbation-mode records;
- all XML simulation-configuration files and candidate time/calibration references;
- candidate YAML/XML event identity and anomaly-flag alignments;
- human-review ledgers and variable-mapping templates;
- synthetic helper-function self-tests.

The v4.2 outputs include the nine event/XML review tables listed in notebook section 14, together with the Stage 1 inventory, schema, uncertainty, interpolation, candidate registry, and compact-summary outputs. They are **audit candidates for human review**, not automatic proof of physical pairing or grounds for propagating labels.

The approximately 2.1-GB simulation time-series archive (modality 13) remains disabled in the notebook by default. It is not required for the v4.2 metadata/YAML/XML inventory path.

## Install

Use Python 3.12 in a fresh virtual environment:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r reproducibility/requirements-v4.2.txt
```

## Run the offline checks first

```bash
python scripts/run_stage1_audit_v4_2.py --self-test-only
python -m unittest discover -s tests -v
python scripts/verify_historical_artifacts.py
```

The offline notebook self-test runs only the pure v4.2 helper functions and synthetic fixtures. It makes no network requests and does not inspect the real dataset.

The historical verifier reads the four expected filenames under `evidence/` and computes byte size, MD5, SHA-256, and CSV shape. It separately checks the clearly labelled files under `reproducibility/recovered_candidates/`. Missing original files stay `MISSING`; the approximate/rebuilt/intermediate candidates are never counted as original substitutes. The standalone ZIP kit includes the candidate CSV payloads; a GitHub checkout may retain only their metadata/README to avoid presenting non-original derived CSVs as frozen evidence.

Add `--strict` to make the historical verifier return a non-zero exit code until all four original artifacts match their historical fingerprints:

```bash
python scripts/verify_historical_artifacts.py --strict
```

A non-zero result is expected at the present recovery state because the original v3.1 Artifacts 2–4 are still absent.

## Run the full v4.2 Stage 1 audit

```bash
python scripts/run_stage1_audit_v4_2.py
```

The runner first executes the notebook's offline synthetic helper tests. It then executes the archived v4.2 notebook in a clean Jupyter kernel, saves an executed copy to `reproducibility/runs/v4_2_executed.ipynb`, and uses `reproducibility/runs/v4_2_data/` as the working directory by default. The notebook fetches the pinned Zenodo record and downloads/verifies the selected small audit files. Expected output files and the convenience ZIP are created beneath `reproducibility/runs/`.

To use a different working directory:

```bash
python scripts/run_stage1_audit_v4_2.py \
  --work-dir /path/to/simtrust_pre_audit \
  --output-notebook /path/to/v4_2_executed.ipynb
```

Do not silently change the dataset record, version, checksum metadata, source archive contents, or notebook's scientific decision gates. If the Zenodo API reports a version different from `1.1.3`, the notebook stops rather than silently switching data versions.

## Historical v3.1 artifact status

The historical fingerprints are preserved in `reproducibility/historical_fingerprints.json` and `evidence/MANIFEST_v3_1_rebuild.json`:

| Historical artifact | Expected size | Expected MD5 | Current status |
|---|---:|---|---|
| Artifact 1 — H701 cohort | 19,327 bytes | `38f395a6e5b32fa7c97a13dc6e0cd208` | Present; size and MD5 match |
| Artifact 2 — v2.2.5 Crosswalk | 78,322 bytes | `780886326cbb615cfeb3a4a563ed820b` | Original absent; v2.1 371-row approximation retained separately |
| Artifact 3 — HV feasibility | 11,863 bytes | `b0345b49abb899a2d7cdca8f65bb1b87` | Original absent; exact generating code not recovered |
| Artifact 4 — P701/P702 | 3,539 bytes | `127ed0fb1ed7145fd439d7c0e3bf08fe` | Original absent; a 25-row rebuild with a different fingerprint is retained separately |

**Do not edit the historical expected sizes or MD5 values to make a reconstructed file pass.** A matching size+MD5 is recorded only as a historical byte-fingerprint match; it is not independent proof of authenticity or semantic validity.

The four CSV snapshots in the standalone kit's `reproducibility/recovered_candidates/` directory are intentionally classified as approximate, rebuilt, or intermediate. The v2.1 crosswalk work also has a known extraction caveat: the source description is truncated to 200 characters before re-parsing actuator declarations; this must be investigated before treating its actuator classifications as final.

## Provenance and licensing

The source dataset is the Zenodo release [10.5281/zenodo.22250958](https://zenodo.org/records/22250958), version `1.1.3`. The Zenodo record reports CC BY 4.0. Cite the dataset authors and record when redistributing derived data, and verify the license on the record before redistributing upstream archive files. This does not change the repository's separate code license.

The v4.2 notebook is an audit notebook, not a detector-training notebook. Its synthetic tests validate software mechanics only. They do not validate real-data pairings, event semantics, physical channel mappings, uncertainty interpretation, empirical model performance, or the SimTrust-Pre primary estimand.

## Output and storage guidance

The full source archives are downloaded into the working directory at run time and are not committed to ordinary Git. Generated audit outputs and executed notebooks under `reproducibility/runs/` should remain local unless separately reviewed and intentionally released. The original v3.1 CSV evidence belongs under `evidence/` only after byte-level recovery and provenance review; approximate/rebuilt candidates belong in the explicitly labelled candidate area.
