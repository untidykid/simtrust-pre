# Evidence manifest

This directory is intended to hold the four frozen CSV evidence artifacts. The values below were recorded from the verified files in the audit environment; the file bytes were not available when this repository was bootstrapped.

| File | Size (bytes) | MD5 | Repository status |
|---|---:|---|---|
| `artifact_1_h701_cohort.csv` | 19,327 | `38f395a6e5b32fa7c97a13dc6e0cd208` | Awaiting original file |
| `artifact_2_crosswalk_254_parents.csv` | 78,322 | `780886326cbb615cfeb3a4a563ed820b` | Awaiting original file |
| `artifact_3_hv_feasibility.csv` | 11,863 | `b0345b49abb899a2d7cdca8f65bb1b87` | Awaiting original file |
| `artifact_4_p701p702_events.csv` | 3,539 | `127ed0fb1ed7145fd439d7c0e3bf08fe` | Awaiting original file |

## Pinned source dataset

- Record: [Zenodo 22250958, version 1.1.3](https://zenodo.org/records/22250958)
- DOI: `10.5281/zenodo.22250958`
- The following **selected upstream archives relevant to this audit** have names, published sizes, and MD5 checksums transcribed from the Zenodo v1.1.3 record. They identify upstream source files; they are not checksums for the four derived audit CSVs above. This is not a complete list of every file in the 95.2-GB Zenodo record. None of these source archives is currently committed to this GitHub repository. The 2.1-GB simulation archive should remain hosted at Zenodo rather than be copied into ordinary Git; GitHub enforces a 100-MB single-object limit for ordinary Git, and Git LFS file-size limits depend on plan.

| Source archive | Published size | Zenodo MD5 |
|---|---:|---|
| `00_Batch_Distillation_Plant_M-202210_Timeseries_Label_Anomaly_Metadata.zip` | 1.7 MB | `636dcb8188e5eb80f19522e244704e2c` |
| `01_Batch_Distillation_Plant_M-202210_Timeseries_Sensors.zip` | 36.5 MB | `ecf2ee25f32d758bdd1e31820d77883e` |
| `02_Batch_Distillation_Plant_M-202210_Timeseries_Actuators.zip` | 8.8 MB | `d345a725171ea2fecd0b608752998d63` |
| `03_Batch_Distillation_Plant_M-202210_Timeseries_Sensor_Uncertainties.zip` | 31.9 MB | `0ee827ce07f3b520fb61ae15903b06cb` |
| `13_Batch_Distillation_Plant_M-202210_Timeseries_Simulation.zip` | 2.1 GB | `21399c5def2c114bd2461e80270d90cf` |
| `14_Batch_Distillation_Plant_M-202210_Timeseries_Simulation_Configuration.zip` | 258.0 kB | `8676ba6454704dd6829d46dfadd1afe6` |

The upstream MD5 values were checked against the Zenodo v1.1.3 record page on 2026-11-01. The exact archive bytes used in the audit are not available in this repository, so their local digests have not been independently recomputed here. The upstream dataset paper describes the dataset under CC BY 4.0; that license does not automatically assign a license to this repository's original files.

Related upstream resources: [dataset descriptor paper](https://doi.org/10.1038/s41597-026-07124-3), [companion processing-code repository](https://github.com/Jarweile/batch-distillation-anomaly-detection-data), and [archived software release](https://doi.org/10.5281/zenodo.18744032). These are upstream dataset/code references; they are not the SimTrust-Pre analysis pipeline or a reproduction of the four locked audit CSVs.

## Integrity versus semantic validity

MD5 hashes verify byte-level integrity of the evidence artifacts. They do not independently re-verify the semantic classification rules used in Crosswalk v2.2.5. The classification labels (`OBSERVATION_DERIVED`, `PROVENANCE_UNRESOLVED`, etc.) are inherited from the original v2.2.5 extraction pipeline, not re-derived from first principles in this audit. The extraction code is not included in this documentation bootstrap, so the current repository does not independently reproduce the crosswalk construction.

A simplified rebuild of the crosswalk from the raw ZIP produced 240 parent keys (5 `PROVENANCE_UNRESOLVED`) versus 254 (19) in the original. The original v2.2.5 crosswalk is retained as the frozen audit artifact, but its CSV payload is not yet committed. The simplified rebuild is not used as evidence. The final crosswalk CSV and the code that generated the v2.2.5 parent-key classification are not included in this bootstrap; therefore those classification labels and counts are inherited from the frozen extraction and are not independently reproduced from the source archives in this repository.

## Scope note for Artifact 3

The evidence file `artifact_3_hv_feasibility.csv` contains the HV004/HV005 feasibility audit specifically. The full Feasibility Map covers five families (H701, HV004/HV005, T703, P701/P702, AV716/V001/PDI702); only the HV audit is provided as a separate evidence file. The other family verdicts are documented in the project narrative and in `artifact_1` (H701) and `artifact_4` (P701/P702).


## Unresolved source-variable unit audit

A retained OP003 diagnostic labels the exported variable as `pressure stage 12 / Pa` and reports the constant value 300.0. The operating-point metadata reports 300 mbar, while the selected configuration excerpt reports `pressure_12 = 30000.00`. The factor-of-100 relationship is numerically consistent with Pa↔mbar, but the output column's label and value appear inconsistent. The original simulation CSV and the simulator export/unit definition must be checked together before assigning an absolute unit to this time-series column. The current audit conclusion is limited to within-trace constancy, not a validated absolute pressure value.

The same retained diagnostic labels the simulator columns `temperature stage n / K`, but reports stage-1 values around 3.1–3.7 in the inspected traces. These values cannot be interpreted as ordinary absolute temperatures in kelvin without an additional scale/variable-definition explanation. As with the pressure column, the export unit/scale convention is unresolved; do not use these values as absolute kelvin or silently apply a factor of 100.
