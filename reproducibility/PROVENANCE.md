# Reproducibility and recovery provenance

## Notebook-source comparison (2026-11-07)

The source of all 32 cells in the user-supplied executed `SimTrust_Pre_Audit_v4_2` notebook was compared with the repository's archived `notebooks/archive/SimTrust_Pre_Audit_v4_2_UNEXECUTED.ipynb`. Every cell's source text matched exactly. The executed notebook therefore adds recorded outputs, not a different v4.2 implementation. The repository keeps the archived unexecuted notebook as the reproducible source and uses `scripts/run_stage1_audit_v4_2.py` to execute it.

## v3.1 recovery boundary

- Artifact 1 is available and matches the preserved historical size and MD5 fingerprint; its SHA-256 is recorded in the evidence manifest.
- Artifact 2's original 254-parent v2.2.5 CSV is absent. The 371-row v2.1 output is approximate and not equivalent.
- Artifact 3's original HV feasibility CSV is absent. The inspected notebooks did not contain its exact generating code.
- Artifact 4's original 3,539-byte CSV is absent. The retained 25-row reconstruction is 14,706 bytes and has a different MD5.

The package does not synthesize historical originals. It preserves the available candidates as separate files and provides a verifier that refuses to count them as historical matches.

## v4.2 execution boundary

The notebook pins Zenodo record 22250958, version 1.1.3, and uses the record API's current file metadata to check download sizes and MD5 checksums. The notebook's offline helper tests use synthetic data. A successful run of those tests is not evidence that the full dataset has been re-audited or that the v3.1 historical outputs have been reconstructed.

The local build environment used for this packaging task did not have outbound network access to download the upstream Zenodo ZIP files. Therefore the full v4.2 notebook was **not executed again here**. The executable runner is included so the full dataset scan can be carried out in Colab or another network-enabled Python environment.
