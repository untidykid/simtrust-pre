# SimTrust-Pre Source Inventory and Inclusion Decisions

**Review date:** 2026-11-02  
**Purpose:** identify which previously prepared source assets are suitable for the repository, what they support, and what must remain outside the reproducible release until further verification.

## Repository boundaries

The repository contains two distinct work streams:

1. **v3.1 locked audit:** the four artifact-level outcomes recorded in `docs/locked-results.md`, with recovery state in `RECOVERY_LOG.md` and historical evidence fingerprints in `evidence/`.
2. **v5.2 research implementation:** a separate software pipeline governed by the v5.2 Phase 0 protocol. It is not a builder for the four v3.1 CSV artifacts and has only synthetic-fixture test evidence at this stage.

Do not blend v5.2 software tests with v3.1 scientific evidence, and do not interpret synthetic test success as a real-data result.

## Included in this repository change

| Asset | Repository location | Why it is useful | Verification boundary |
|---|---|---|---|
| Reviewed v5.2 Module 1 | `src/SimTrust_Pre_v5_2_Module1_reviewed.py` | Fault-only windows, deterministic sampling, class/experiment weight constraints | 9 synthetic checks; no Zenodo data |
| Reviewed v5.2 Module 2 | `src/SimTrust_Pre_v5_2_Module2_reviewed.py` | Train-only preprocessing, paired fault-segment utility, control checks | 14 synthetic checks; no Zenodo data |
| Reviewed v5.2 Module 3 | `src/SimTrust_Pre_v5_2_Module3_reviewed.py` | Reviewed loading, interpolation provenance, time alignment, 300-second `q` | 23 synthetic checks; no Zenodo data |
| Reviewed v5.2 Module 4.1 | `src/SimTrust_Pre_v5_2_Module4_1_Reviewed.py` | Real Operation window construction and label/quality gates | 18 synthetic checks; no Zenodo data |
| Reviewed v5.2 Module 5 | `src/SimTrust_Pre_v5_2_Module5_reviewed.py` | End-to-end event orchestration and matched controls | 20 synthetic checks; no Zenodo data |
| v5.2 protocol summary | `docs/v5.2/phase0-protocol-summary.md` | Records the predictor, estimand, windowing, weights, controls, and inference unit | Summary of the Phase 0 source packet, not an empirical result |
| H701 / OP028 decision addendum | `docs/decisions/h701-op028-decision-addendum-2026-10-31.md` | Preserves the bounded pressure/temperature feasibility decision | Supplementary decision record; see locked results for the controlling v3.1 record |

The five reviewed Python modules passed their embedded synthetic smoke suites in a local run using the versions pinned in `requirements-v5.2.txt`: 9 + 14 + 23 + 18 + 20 = **84 synthetic checks**. These checks do not access the real Zenodo archives and do not validate event selection, real/simulation alignment, physical mappings, empirical q values, or model utility on the real dataset.

## Reviewed but not promoted as executable source

### v5.2 Module 5 Orchestrator notebook

The uploaded `SimTrust_Pre_v5_2_Module5_Orchestrator.ipynb` is retained as a historical extraction/recovery source, not as the canonical implementation. The inspected copy has 97 cells (91 code, 6 Markdown), 16 saved error outputs, stale saved output that reports an earlier 70-cell state, runtime-specific `/content` and Drive paths, and mixed-language comments. It is not a clean top-to-bottom reproducible notebook.

Relevant cell-level findings:

- JSON cell index 41 contains the H701 cohort extraction that writes `H701_crosswalk_v3.csv`; a later copy step names the file `artifact_1_h701_cohort.csv`. The cell relies on notebook state (including `Path`) and was not independently rerun against the original archive during this review. The previously reported exact Artifact 1 fingerprint therefore remains a reported recovery claim, not an independent rebuild performed by this repository change.
- Cell indices 57–58 generate the v2.1 metadata/event crosswalk path. The saved v2.1 output has 371 event keys; it is not the original v2.2.5 crosswalk with 254 parent keys.
- Cell indices 84–86 select 25 P701/P702 event keys from the v2.1 table and create a rebuilt 16-column CSV. The saved output is 14,706 bytes with MD5 `52c9c270194ed470fcfc929e7d2d9607`, not the historical original fingerprint. It is a rebuilt, non-byte-identical file.
- Cell index 87 exports the 371-row v2.1 approximation. It is not Artifact 2 v2.2.5.
- No direct builder for the original `artifact_3_hv_feasibility.csv` was identified in this notebook.

The notebook also contains a temporary manifest with an incomplete historical checksum literal (`780886???`). That temporary manifest must not replace the complete recovery manifest in the repository. The raw notebook is not copied into Git because its saved outputs and runtime state are not a trustworthy build interface; the reviewed standalone Python modules are the canonical v5.2 source instead.

### v4.2 audit notebook

`notebooks/archive/SimTrust_Pre_Audit_v4_2_UNEXECUTED.ipynb` is retained as a historical source candidate for a future YAML/XML event-identity audit. The inspected file has 32 cells (16 code and 16 Markdown), no executed code cells, no saved outputs, and no saved errors. It describes outputs such as YAML event identity/mode audits and YAML–XML anomaly crosswalks. It does **not** produce `annotation_hygiene_119_runs.csv` or the historical `artifact_3_hv_feasibility.csv` in the inspected source. Its Colab metadata still names the notebook `SimTrust_Pre_Audit_v4_0.ipynb`, so it must be normalized and tested before being treated as a versioned runnable notebook. No empirical findings are claimed from it. See [the archive README](../notebooks/archive/README.md).

### Earlier notebooks and wrappers

- v4.0 and v4.1 are earlier Stage 1 audit iterations; v4.2 is the later source candidate reviewed here.
- The v3.1 Stage 1 notebook is an earlier structural/protocol source, not an independently verified builder for all four locked v3.1 evidence CSVs.
- The Module 3.5 and Module 4.1 notebooks are Colab-oriented wrappers around reviewed Python code. The standalone `.py` modules are the canonical sources included in this change; the duplicate notebooks are not required for CI.

## Artifact reproducibility status after this change

| Frozen v3.1 artifact | What the reviewed sources support | What this repository does not claim |
|---|---|---|
| Artifact 1 — H701 | The notebook contains a candidate extraction cell; the recovery manifest records a reported size/MD5 match | No standalone builder has yet been independently executed against the original archive in this repository |
| Artifact 2 — Crosswalk v2.2.5 | The notebook contains a v2.1 path producing 371 event keys | No recovered v2.2.5 builder; v2.1 is not a substitute for the 254-parent original |
| Artifact 3 — HV feasibility | The v4.2 notebook contains broader YAML/XML audit code that may inform a new audit | No builder or recovered file equivalent to the historical Artifact 3 CSV was identified |
| Artifact 4 — P701/P702 | The notebook reproduces a 25-row rebuilt selection from v2.1 | The rebuilt file is not byte-identical to the historical original and is not a substitute |

## Next engineering gates

1. Refactor and validate the Artifact 1 extraction against the actual original label/metadata archive; only then publish a standalone builder and record an independently computed digest.
2. Treat any new Crosswalk or feasibility table as a new version with explicit schema, algorithm, and provenance. Do not label it as a reconstruction of the historical v2.2.5 or Artifact 3 without evidence.
3. Extract the v4.2 YAML/XML logic into tested modules and run it against the pinned source archives before reporting dataset-wide results.
4. Extend annotation consistency checks only after defining the semantic relation between `Observation`, YAML anomaly metadata, and numeric CSV labels.
5. Develop TwinLinter rules as diagnostics with `INFO`, `WARNING`, or `REQUIRES_ENGINEERING_REVIEW` outcomes; do not hard-code unresolved unit or physical interpretations as automatic failures.
