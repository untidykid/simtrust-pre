# Evidence manifest

This directory is intended to hold the four frozen CSV evidence artifacts. The values below were recorded from the verified files in the audit environment; the file bytes were not available when this repository was bootstrapped.

| File | Size (bytes) | MD5 | Repository status |
|---|---:|---|---|
| `artifact_1_h701_cohort.csv` | 19,327 | `38f395a6e5b32fa7c97a13dc6e0cd208` | Awaiting original file |
| `artifact_2_crosswalk_254_parents.csv` | 78,322 | `780886326cbb615cfeb3a4a563ed820b` | Awaiting original file |
| `artifact_3_hv_feasibility.csv` | 11,863 | `b0345b49abb899a2d7cdca8f65bb1b87` | Awaiting original file |
| `artifact_4_p701p702_events.csv` | 3,539 | `127ed0fb1ed7145fd439d7c0e3bf08fe` | Awaiting original file |

The source simulation archive was separately recorded as:

- Filename: `13_Batch_Distillation_Plant_M-202210_Timeseries_Simulation.zip`
- Size: not recorded here
- MD5: `21399c5def2c114bd2461e80270d90cf`
- Repository status: not included

## Integrity versus semantic validity

MD5 hashes verify byte-level integrity of the evidence artifacts. They do not independently re-verify the semantic classification rules used in Crosswalk v2.2.5. The classification labels (`OBSERVATION_DERIVED`, `PROVENANCE_UNRESOLVED`, etc.) are inherited from the original v2.2.5 extraction pipeline, not re-derived from first principles in this audit. The extraction code is not included in this documentation bootstrap, so the current repository does not independently reproduce the crosswalk construction.

A simplified rebuild of the crosswalk from the raw ZIP produced 240 parent keys (5 `PROVENANCE_UNRESOLVED`) versus 254 (19) in the original. The original v2.2.5 crosswalk is retained as the frozen audit artifact. The simplified rebuild is not used as evidence.

## Scope note for Artifact 3

The evidence file `artifact_3_hv_feasibility.csv` contains the HV004/HV005 feasibility audit specifically. The full Feasibility Map covers five families (H701, HV004/HV005, T703, P701/P702, AV716/V001/PDI702); only the HV audit is provided as a separate evidence file. The other family verdicts are documented in the project narrative and in `artifact_1` (H701) and `artifact_4` (P701/P702).
