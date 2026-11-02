# Archived v4.2 Audit Notebook

This directory stores the v4.2 Stage 1 audit notebook as a historical source reference. It is **not** an executed analysis result and is **not** part of the tested v5.2 software pipeline.

## Inspection record

- File: [SimTrust_Pre_Audit_v4_2_UNEXECUTED.ipynb](SimTrust_Pre_Audit_v4_2_UNEXECUTED.ipynb)
- Inspected notebook cells: 32 (16 code and 16 Markdown)
- Executed code cells: 0
- Cells with saved outputs: 0
- Saved error outputs: 0
- Persian/Arabic-script characters in notebook source: 0
- The notebook's Colab metadata still names the notebook `SimTrust_Pre_Audit_v4_0.ipynb`, despite the v4.2 filename and headings.

## Intended audit scope described by the notebook

The source contains candidate logic for YAML event identity and mode audits, duplicate-event candidate checks, XML anomaly-flag and list-alignment checks, and YAML-to-XML anomaly crosswalk tables. The notebook describes output files such as `yaml_event_identity_audit_v4_2.csv` and `yaml_xml_anomaly_crosswalk_v4_2.csv`.

## Execution and evidence boundary

No dataset-specific result is claimed from this notebook in this repository. The saved copy inspected for this release has no executed cells and no outputs. Its code must be extracted into tested modules, supplied with the exact version-pinned source archives, and run from a clean environment before any generated table or count is treated as evidence.

The notebook does not contain a direct builder for the historical `artifact_3_hv_feasibility.csv`, and it does not by itself implement the proposed `annotation_hygiene_119_runs.csv` deliverable. Do not describe it as a completed 119-run annotation audit or as a reproduction of any locked v3.1 artifact.
