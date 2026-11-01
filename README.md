# SimTrust-Pre

**Repository status:** documentation bootstrap committed; evidence payload pending.

SimTrust-Pre is a structured audit of whether selected simulated process-plant perturbations support predefined sensor-response expectations. The project deliberately distinguishes trace-level observations, archive metadata, feasibility evidence, and validation claims.

## Scientific status

The audit cycle was closed at the artifact level on **2026-11-01**. The four locked artifacts and their interpretation are:

| Artifact | Scope | Locked status |
|---|---|---|
| 1. H701 cohort (v3.1) | Four manually operated, open-loop heater cases | `NOT_VERIFIED_UNDER_PREDEFINED_CRITERIA` |
| 2. Archive Crosswalk (v2.2.5) | Archive metadata and Observation-to-parent crosswalk | `CLOSED` |
| 3. Feasibility Map | Feasibility screening across five perturbation families | `CLOSED` |
| 4. P701/P702 | Paired-pump feasibility demonstration | `STRONG_FEASIBILITY_DEMONSTRATION` — **not validation** |

The project’s central conclusion is not that the simulator is generally invalid. It is that the inspected evidence does not support the predefined H701 validation claim, and the available P701/P702 evidence is a feasibility demonstration from one independent experiment, not an independent validation.

## Dataset version and scope

The source dataset is pinned to [Zenodo record 22250958, version 1.1.3](https://doi.org/10.5281/zenodo.22250958). The audit must not silently mix this version with earlier dataset releases. The Zenodo record describes 119 experimental runs and simulation predictions for 115 of them; this audit concerns selected event families and selected archive members, not a complete validation of all runs.

This GitHub repository is currently a **documentation bootstrap**, not a computationally reproducible release. The final evidence CSVs, source archives, and the analysis/extraction code that generated the locked tables are not included. The figures and counts below are transcribed from the locked audit record and retained diagnostic outputs; they have not been independently regenerated from raw source files in this repository.

## Principal findings

### Artifact 1 — H701 v3.1

The locked v3.1 H701 cohort contains four duration-qualified candidates: `OP003TA001A001` (481 s), `OP004TA001A001` (616 s), `OP009TA001A001` (680 s), and `OP001TA009A002` (319 s). They were selected from six preliminary single-H701 candidate event records spanning five chemical/operating-point groups; the six records must not be treated as six independent groups.

Two other preliminary records were not included in the four-case cohort: `OP001TA011A001` (279 s; nine theoretical 30-s windows, below the ten-window/300-s screen, with a metadata label-direction warning) and `OP028TA001A002` (270 s; nine theoretical windows and not evaluable in the selected simulation member under the current time mapping). For OP028, the selected member spans 39,875–52,775 s while the mapped YAML interval is 56,700–56,970 s (zero overlap). The check did not enumerate every possible duplicate/alternative archive member, so this is a selected-member result, not a claim that no alternative member exists anywhere in the archive.

- **Stage pressure:** the 12 exported stage-pressure columns inspected were static across the four traces. The result is `NOT_IDENTIFIABLE_FROM_EXPORTED_TRACE`; it does not establish that pressure is absent from the simulator globally.
- **PY23:** Under the expected physical relation (heating up → pressure up; heating down → pressure down), OP004 (H701 −30%; ΔPY23 +17.81) showed a sustained change opposite to expectation, while OP009 (H701 +20%; ΔPY23 +13.79) was consistent with expectation. OP003 (H701 +25%; ΔPY23 −1.21) and OP001 (H701 off; ΔPY23 +0.004) showed no sustained response. The available audit record does not establish that this directional expectation was preregistered before data inspection; it is therefore described here as a physical expectation used in interpretation, not as a confirmed preregistered prediction.

#### Metadata description versus XML heat-duty schedule

The event metadata and the inspected simulation XML provide two distinct representations; their percentages must not be assumed to be numerically interchangeable. The retained XML diagnostic reports:

| Candidate | Metadata description | XML `heat_duty` values (initial → perturbed) | XML relative change |
|---|---|---:|---:|
| OP003 | H701 +25% (to 245 W) | 129.575087 → 189.150174 | +46.0% |
| OP004 | H701 −30% (to 70 W) | 146.988148 → 13.976296 | −90.5% |
| OP009 | H701 +20% (to 210 W) | 211.901208 → 253.802416 | +19.8% |
| OP001TA009A002 | H701 off | 185.031024 → −49.937952 | −127.0% |

These are values from separate metadata and XML fields. The unit/semantic relationship between the metadata's heater-power values and the XML `heat_duty` schedule has not been established in the included evidence. In particular, the negative OP001 XML value has an unresolved sign-convention interpretation. Do not describe these pairs as matching percentages or as a confirmed physical power conversion.
- **Temperature:** `NOT_VERIFIED`; the locked v3.1 result records T701-stage sign agreement of 2/4. A separate 2026-10-31 screening memo reported a different metric: the within-event `T_stage1` range crossed its preliminary heuristic in OP003 (2.70 °C) and OP009 (2.24 °C), but not OP004 (0.14 °C) or OP001TA009 (0.02 °C). OP001TA011 was below the 300-s duration screen and OP028 was not evaluable. Do not conflate this range-screen metric with the final sign-agreement statistic; neither establishes a confirmed causal thermal response. The proposed superheat/heater-surface explanation remains a post-hoc hypothesis.
- **Flow:** `COINCIDENTAL_BY_PREDEFINED_TRAJECTORY_SCREEN`. Mean direction agreed in 4/4, but corrected trajectory mean was 0.561 and pooled mean 0.627; 2/4 cases fell below the pre-specified 0.70 threshold. OP004 had contrary bins at 480, 510, and 540 seconds. Directional agreement alone therefore does not satisfy the trajectory screen.

The predefined criteria were locked before the v3.1 evaluation, but not necessarily before any data inspection.

### Artifact 2 — Archive Crosswalk v2.2.5

- 525 raw metadata records were grouped into 254 parent keys: 235 ID-backed and 19 fallback/index-based.
- 181 Observation children were associated with 100 parent keys.
- Parent-key class counts: 99 `OBSERVATION_DERIVED`, 73 `SYSTEM_ASSOCIATED_NO_RECOGNIZED_ACTUATOR`, 38 `SINGLE_DECLARED_ACTUATOR`, 25 `MULTIPLE_DECLARED_ACTUATORS`, and 19 `PROVENANCE_UNRESOLVED`.
- A parent key is not necessarily an independent physical event. In particular, raw metadata counts and parent-key counts must not be presented as physical-event counts.
- Safety metadata classification is lexical/text-coverage evidence, not a census of safety events.
- The original v2.2.5 crosswalk remains the frozen audit artifact for this audit. Its CSV payload is **not yet present in this GitHub repository**; see the evidence manifest. A simplified rebuild produced 240 keys rather than 254 and is **not** used as evidence.

### Artifact 3 — Feasibility Map

The complete map screened five families: H701, HV004/HV005, T703, P701/P702, and AV716/V001/PDI702.

- **HV004/HV005:** 69 raw metadata links grouped into 42 parent keys. The 59 descriptions “Improperly sealed sample valve” are raw descriptions, not 59 independent events. The family was judged `NOT_FEASIBLE_FOR_DIRECT_ACTUATOR_PAIRED_STUDY` based on the inspected evidence; the actuator/configuration inspection was not exhaustive across every simulation output.
- **T703:** 66 raw records grouped into 14 parent keys across 6 experiments. The 49 noise-injection records are not 49 independent events. Status: `NOT_FEASIBLE_FOR_CURRENT_PAIRED_VALIDATION`, not a universal claim that T703 can never be studied.
- **AV716/V001/PDI702:** link counts were 4/3/7 respectively; these are not independent event counts and were not advanced.

When the planned evidence file `artifact_3_hv_feasibility.csv` is added, it will cover the HV004/HV005 audit specifically, not the entire five-family Feasibility Map.

### Artifact 4 — P701/P702 feasibility demonstration

- 121 raw metadata records were grouped into 25 parent keys across 19 experiment keys.
- The two genuine pure-single parent events (one P701, one P702) occur in the same experiment: `batch_dist_ternary_butan-1-ol+propan-2-ol+water/operating_point_021/test_anormal_experiment_001`.
- The OP021 trace contains 18,001 time-series rows spanning 38,253–56,253 s. The final extraction inventory lists 179 variables, while an earlier shape summary reported 180 columns; the counting convention cannot be resolved without the original trace file. The pump-off windows are 256 s (P702) and 254 s (P701); observed onset offsets were 2 s and 11 s, with a 9 s spread.
- The relationship `efflux_ratio = D/(D+R)` matched to a median absolute residual of 2.214895e-14, but transient outliers remain (maximum 0.02843). Their cause has not been established.
- The FT703/FT704 mapping to distillate/reflux is provisional and was not independently confirmed against a P&ID.
- Directional real/sim alignment is descriptive evidence under that provisional mapping, not four independent validation tests. If one event informed selection of the sensor mapping, that event is mapping-selection evidence; the second event provides descriptive cross-event consistency, not an independent validation set. Both pump cases come from one independent experiment.
- The listed P701/P702 parent-key categories in the detailed record (12 compound pumps & others, 1 pure P701, 1 pure P702, 3 both-pumps-only, 4 multi-all-actuators-off) sum to 21, not 25. Four of the 25 parent keys are not accounted for by that category summary and are left unclassified here pending the original event CSV; no category is inferred for them.

## Evidence and integrity

See [the evidence manifest](evidence/README.md) for filenames, sizes, and recorded MD5 values.

**Important:** this initial repository commit does not yet contain the four CSV evidence payloads or the original simulation ZIP. The manifest records previously verified metadata only. Hashes cannot reconstruct missing files, and MD5 integrity checks do not establish semantic correctness.

Do not treat this documentation bootstrap as a complete data release. The evidence files should be added from the original verified files, without regenerating or substituting them from summaries.

## Reproducibility and interpretation rules

1. Do not reopen the locked v3.1 cycle by changing channels, cohorts, thresholds, or criteria post hoc.
2. Keep feasibility demonstrations separate from independent validation.
3. Report raw metadata records, parent keys, experiment keys, and physical events as different units.
4. Treat unverified sensor mappings and causal explanations as provisional hypotheses.
5. Preserve the negative and inconclusive findings; do not convert them into positive validation claims.

## Repository layout

```
README.md
docs/
  locked-results.md
evidence/
  README.md
scripts/
  verify_evidence.py
```

Run `python scripts/verify_evidence.py` from the repository root after placing the four original CSVs in `evidence/`.

The planned primary estimand, pre-onset fidelity `q` versus fault-segment utility `ΔAP`, was **not estimated** on a validated H701 cohort. Invariant simulated stage-12 pressure during the perturbation does not establish that pre-onset `q` is zero, constant, or uncomputable; paired pre-onset real/simulation values and valid uncertainty measurements would be required.

The notebook `SimTrust_Pre_Audit_v3_1.ipynb` retained in the Library is a Stage 1 structural/protocol audit notebook, not the executed pipeline that generated all four locked artifact CSVs. The stored copy has 14 code cells with no execution counts and no saved outputs. It is therefore not represented here as a reproduction package.

## License and citation

No license or formal citation metadata is assigned in this bootstrap. Reuse permissions and citation details should be added only after the project owner confirms them.
