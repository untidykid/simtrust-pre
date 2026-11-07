# Recovered intermediate and non-original CSV candidates

These files are preserved for traceability. **None of the files in this directory is a substitute for the missing historical v3.1 Artifact 2 or Artifact 4.**

| File | Classification | Rows | Columns | Historical relationship |
|---|---|---:|---:|---|
| `artifact_2_crosswalk_v21_APPROX_371.csv` | Approximation | 371 | 16 | Not the 254-row v2.2.5 Artifact 2 |
| `artifact_4_p701p702_events_REBUILT.csv` | Rebuild, not byte-identical | 25 | 16 | Not the historical 3,539-byte Artifact 4 |
| `CW_v21_events.csv` | Intermediate | 371 | 16 | v2.1 event-level intermediate |
| `CW_v2_raw_525.csv` | Intermediate | 525 | 18 | Raw YAML-derived rows used during v2.1 processing |

SHA-256, MD5 and byte counts are recorded in `../historical_fingerprints.json`. The files are not relabelled as originals, and the historical expected fingerprints are not changed to match them.

The intermediate CSVs derive from the project audit of Zenodo record `22250958`, version `1.1.3`. The upstream record reports CC BY 4.0; users redistributing derived data should retain attribution to the dataset and its authors. See [Zenodo record 22250958](https://zenodo.org/records/22250958).

The standalone reproducibility ZIP contains the four CSV snapshots listed above. The GitHub repository may keep this README and the fingerprint metadata without committing the non-original CSV payloads; absence is reported as `CANDIDATE_FILE_MISSING`, never as a match.
