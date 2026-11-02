# Recovery Log — SimTrust-Pre Evidence Artifacts

**Recovery record date:** 2026-11-02
**Repository:** untidykid/simtrust-pre
**Baseline GitHub commit before this documentation update:** 47df178d9464af4d5c484c3b9490bfb1edcd46ca

## Purpose and scope

This log records the recovery work following Colab runtime resets. It distinguishes original historical evidence files, byte-fingerprint recovery, and non-byte-identical or approximate reconstructions.

The recovery work does not reopen, recompute, or modify the four artifact-level scientific conclusions frozen on 2026-11-01. It changes the recorded availability and reproducibility status of their supporting files, not the locked scientific interpretation.

The values described as locally calculated below were reported from the project owner's Colab/Google Drive session and pasted into the project conversation. This GitHub documentation update did not have direct access to that runtime or Drive files and did not independently re-hash those CSV or ZIP files.

## 1. Recovery outcome

| Artifact | Recovered file | Recorded status | Main limitation |
|---|---|---|---|
| Artifact 1 — H701 cohort | artifact_1_h701_cohort.csv | EXACT | Reported recovered size and MD5 match the historical fingerprint |
| Artifact 2 — Archive Crosswalk v2.2.5 | artifact_2_crosswalk_v21_APPROX_371.csv | APPROXIMATE | Recovered v2.1 output has 371 rows, not the original 254 parent keys |
| Artifact 3 — HV feasibility | No replacement recovered | UNAVAILABLE | Original CSV was not found; reconstruction procedure was not recovered |
| Artifact 4 — P701/P702 events | artifact_4_p701p702_events_REBUILT.csv | REBUILT_NOT_BYTE_IDENTICAL | 25 rows, matching the recorded original row count, but different size, schema and MD5 |

The recovered/rebuilt CSV copies listed above were reported as being in Google Drive. They are not committed in this GitHub repository by this recovery documentation change. The original evidence payloads also remain absent from the GitHub tree inspected at the baseline commit.

## 2. Reported Colab reset and recovery environment

The project owner reported three Colab runtime resets during this recovery period; exact timestamps for each reset were not retained in the record.

During a later runtime inspection, the top-level /content directory contained only .config and sample_data. The expected temporary directories /content/simtrust_pre_audit and /content/simtrust-pre were absent at that inspection.

The recovery session then used persistent Google Drive storage for the files that could be reconstructed or recovered.

The following files were reported in the Drive evidence directory:

- artifact_1_h701_cohort.csv
- artifact_2_crosswalk_v21_APPROX_371.csv
- artifact_4_p701p702_events_REBUILT.csv
- CW_v21_events.csv
- CW_v2_raw_525.csv

Artifact 3 was not present in that listing.

## 3. Historical fingerprints versus recovered files

The historical expected sizes and MD5 values below are retained in the repository's original evidence README. They are fingerprints recorded before the later runtime resets. Their presence in the manifest does not mean the original file bytes are currently available.

| Artifact | Historical size | Historical MD5 |
|---|---:|---|
| Artifact 1 — H701 cohort | 19,327 bytes | 38f395a6e5b32fa7c97a13dc6e0cd208 |
| Artifact 2 — Crosswalk v2.2.5 | 78,322 bytes | 780886326cbb615cfeb3a4a563ed820b |
| Artifact 3 — HV feasibility | 11,863 bytes | b0345b49abb899a2d7cdca8f65bb1b87 |
| Artifact 4 — P701/P702 | 3,539 bytes | 127ed0fb1ed7145fd439d7c0e3bf08fe |

In particular, the historical MD5 values for Artifacts 2 and 3 were not absent from the repository manifest: they remain recorded in evidence/README.md. The original file bytes are unavailable in the current recovery directory, but the expected fingerprints have been preserved.

### Artifact 1 — H701 cohort

- Recovered filename: artifact_1_h701_cohort.csv
- Reported size: 19,327 bytes
- Historical expected MD5: 38f395a6e5b32fa7c97a13dc6e0cd208
- Reported recovered MD5: 38f395a6e5b32fa7c97a13dc6e0cd208
- Reported row count: 40
- Reported rebuild source: SimTrust_Pre_v5_2_Module5_Orchestrator, cell 41
- Status: EXACT

The reported size and MD5 match the historical fingerprint. The recovered file is treated as the exact artifact on that basis. The file itself is not included in this GitHub commit, and its bytes were not independently re-read by the GitHub connector during this documentation update.

### Artifact 2 — Archive Crosswalk v2.2.5

- Recovered filename: artifact_2_crosswalk_v21_APPROX_371.csv
- Reported size: 153,626 bytes
- Reported MD5: 5b5a8fdd1023f09a1ff1832f33fb270e
- Reported row count: 371
- Historical v2.2.5 count: 254 parent keys
- Historical expected MD5: 780886326cbb615cfeb3a4a563ed820b
- Reported rebuild source: v2.1 logic, recovered notebook cells 57–58
- Status: APPROXIMATE

The recovered v2.1 output is not equivalent to the original v2.2.5 crosswalk. The original v2.2.5 extraction logic was not recovered in the inspected notebooks. The 371-row output must not be substituted for the historical 254-parent-key crosswalk or described as an independent reproduction of v2.2.5.

### Artifact 3 — HV feasibility

- Historical filename: artifact_3_hv_feasibility.csv
- Historical size: 11,863 bytes
- Historical expected MD5: b0345b49abb899a2d7cdca8f65bb1b87
- Recovered replacement: none
- Rebuild code: not found in the three notebooks scanned for the recorded search terms
- Status: UNAVAILABLE

The historical size and MD5 remain preserved in evidence/README.md. No replacement was reconstructed. The absence of a matching code fragment in the three scanned notebooks is a bounded search result, not proof that no copy or code exists elsewhere.

### Artifact 4 — P701/P702 events

- Rebuilt filename: artifact_4_p701p702_events_REBUILT.csv
- Reported size: 14,706 bytes
- Reported rebuilt MD5: 52c9c270194ed470fcfc929e7d2d9607
- Reported row count: 25
- Historical original size: 3,539 bytes
- Historical expected MD5: 127ed0fb1ed7145fd439d7c0e3bf08fe
- Historical original row count: 25
- Reported rebuild source: v2.1 filter C minus NOID, using recovered v5.2 cells 57–58 plus a custom filter
- Status: REBUILT_NOT_BYTE_IDENTICAL

The rebuilt file matches the recorded original row count (25) but differs in byte size and MD5. Its reported 16-column schema has not been established as the original schema. Matching row count alone does not establish matching event identities, schema, or semantic equivalence.

Four records have a content-level caution:

- OP017TA001A001
- OP017TA001A002
- OP017TA001A003
- OP017TA001A004

Each was reported with system_ids=HV004 and declared_actuators=P701. These may reflect textual attribution of P701 in a perturbation description rather than a direct P701 pump perturbation. They are retained without modification. Whether the original v2.2.5 artifact included or excluded these records remains unknown.

A projection experiment compared the rebuilt CSV against the historical 3,539-byte size:

| Projection | Columns | Reported size | Difference from historical size |
|---|---:|---:|---:|
| minimal | 2 | 3,170 bytes | −369 bytes |
| with_timing | 4 | 3,656 bytes | +117 bytes |
| with_duration | 5 | 4,544 bytes | +1,005 bytes |
| with_actuators | 6 | 5,082 bytes | +1,543 bytes |

The four-column projection was closest by size, but no projection matched the historical size. File-size proximity does not identify the original schema. This reverse-engineering attempt was stopped as non-diagnostic; no projected file is treated as the original artifact.

## 4. Correction concerning the number 21

No 21-row replacement for Artifact 4 was created.

An earlier conversational statement incorrectly attributed a 21-row expectation to the project owner. The project owner clarified that no such original-file count had been provided; that attribution was withdrawn.

The arithmetic subtotal 12 + 1 + 1 + 3 + 4 = 21 belongs to an earlier category summary whose total coverage was 25 parent keys. That subtotal is a category-summary coverage issue, not the row count of the original Artifact 4 CSV. These two matters must remain separate.

The four OP017 records were not removed from the rebuilt 25-row file. No 21-row derivative is authorized by the recovery evidence.

## 5. Upstream archive checks during recovery

The owner reported downloading six upstream archives from the pinned Zenodo record during the recovery session. The locally calculated MD5 results pasted into the project conversation were:

| Archive | Reported local MD5 | Comparison result |
|---|---|---|
| 00 — Label Anomaly Metadata | 636dcb8188e5eb80f19522e244704e2c | Matches the MD5 recorded in the repository's Zenodo manifest |
| 01 — Sensors | ecf2ee25f32d758bdd1e31820d77883e | Matches the MD5 recorded in the repository's Zenodo manifest |
| 02 — Actuators | d345a725171ea2fecd0b608752998d63 | Matches the MD5 recorded in the repository's Zenodo manifest |
| 03 — Sensor Uncertainties | 0ee827ce07f3b520fb61ae15903b06cb | Matches the MD5 recorded in the repository's Zenodo manifest |
| 06 — Tabular Plant Information | 1ec30434ba3fd058ad1969e526ce9698 | Local MD5 recorded; no expected comparison value was included in the recovery output |
| 14 — Simulation Configuration | 8676ba6454704dd6829d46dfadd1afe6 | Matches the MD5 recorded in the repository's Zenodo manifest |

The 13-series simulation archive was not part of this six-file recovery download. Its MD5, 21399c5def2c114bd2461e80270d90cf, had been reported as locally verified during the initial audit, but it was not re-downloaded or re-hashed during this recovery session.

The recovery comparison establishes agreement with the checksum values already transcribed in the repository manifest for the five matching archives. It does not constitute a new independent check of the Zenodo record metadata in this commit.

## 6. Search and inspection record

The owner reported scanning the following notebook code cells for references including class_v223, class_v224, 254, artifact_2, artifact_3, artifact_4, hv_feasibility, p701p702, parent_event_key, and Anomaly.id:

- SimTrust_Pre_Audit_v3_1.ipynb
- SimTrust_Pre_Audit_v4_1.ipynb
- Untitled0.ipynb

The scan output reported no matching code-cell references in those three notebooks. This was a targeted search, not an exhaustive inventory of every notebook or backup.

A search for Artifact 4 files under /content/drive/.Trash returned no match in that searched path.

A local Git-history command was attempted against /content/simtrust-pre, but that clone directory had been reported absent in the same runtime inspection. The command's stderr and exit status were not retained. Therefore its empty stdout is inconclusive and must not be interpreted as an exhaustive GitHub remote-history search.

Separately, the GitHub main tree at baseline commit 47df178d9464af4d5c484c3b9490bfb1edcd46ca was inspected. It contained the documentation, verifier, tests, and workflow, but none of the four original CSV evidence payloads.

## 7. Integrity and repository handling rules

1. Preserve the historical expected MD5 values. Do not replace them with hashes of rebuilt files.
2. Do not modify scripts/verify_evidence.py to accept rebuilt or approximate files as original evidence.
3. Keep rebuilt and approximate artifacts under distinct filenames and statuses.
4. Do not infer original schema from file-size proximity.
5. Do not remove the four OP017 records from the 25-row rebuilt Artifact 4 file.
6. Do not describe the v2.1 371-row output as a reproduction of the v2.2.5 254-parent-key crosswalk.
7. Do not describe Artifact 3 as reconstructed.
8. Do not reopen or revise the locked scientific conclusions through this recovery exercise.

This documentation update does not add any CSV payload, modify the verifier or CI workflow, create a release, or create a Git tag.

## 8. Current recovery boundary

As of 2026-11-02, the repository remains a documentation bootstrap with a recorded partial recovery. The exact Artifact 1 fingerprint is reported recovered; Artifact 2 has only an approximate v2.1 reconstruction; Artifact 3 remains unavailable; Artifact 4 has a 25-row non-byte-identical reconstruction.

The recovery manifest at evidence/MANIFEST_v3_1_rebuild.json provides the machine-readable inventory, historical fingerprints, reported rebuilt-file fingerprints, and source-archive checksum record.

Future recovery of an original file should be tested against its historical size and MD5 before it is substituted for, or given the original filename of, a rebuilt copy.
