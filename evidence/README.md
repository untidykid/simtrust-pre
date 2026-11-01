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
- The following **selected upstream archives relevant to this audit** have names, published sizes, and MD5 checksums transcribed from the Zenodo v1.1.3 record. They identify upstream source files; they are not checksums for the four derived audit CSVs above. This is not a complete inventory of the Zenodo record. None of these source archives is currently committed to this GitHub repository. The published 2.1-GB simulation archive should remain hosted at Zenodo rather than be copied into ordinary Git. GitHub documents a 100-MB per-file limit for ordinary Git and a 2-GB per-file Git LFS limit on Free/Pro plans; see [repository file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) and [Git LFS limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-storage-and-bandwidth-usage).

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

The retained diagnostic labels the exported columns `pressure stage n / Pa`, while its summary table uses fields named `min_mbar`, `max_mbar`, `range_mbar` and `delta_raw_mbar`. Its stage-12 diagnostic values for the four locked traces are 300.0, 350.0, 450.0 and 500.0, matching the operating-pressure levels recorded in mbar. This is a label-versus-summary-scale discrepancy in the retained diagnostic. No `pressure_12 = 30000.00` value is included here because it could not be verified in the source material available for this repository review. The raw simulation CSV and exact export/conversion code are not present in this repository. The audit conclusion is limited to within-trace constancy; do not assert an absolute unit for the simulator-export column or apply an unverified conversion.

The same retained diagnostic labels the simulator columns `temperature stage n / K`, but reports stage-1 values around 3.1–3.7 in the inspected traces. These values cannot be interpreted as ordinary absolute temperatures in kelvin without an additional scale/variable-definition explanation. The mapping between these export columns and the separate `T_stage1` screening metric (reported in °C) has not been established. Do not treat the two diagnostics as the same signal, use the export values as absolute kelvin, or silently apply a scale conversion.
