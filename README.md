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

The source dataset is pinned to [Zenodo record 22250958, version 1.1.3](https://doi.org/10.5281/zenodo.22250958). The source publication describes 119 experimental runs, with simulation predictions available for 115 experiments. Version 1.1.3 corrects a formatting error in one binary ethanol/2-propanol normal run affecting sensor, actuator, and uncertainty modalities; do not silently mix this release with earlier versions. This audit concerns selected event families and selected archive members, not a complete validation of all runs.

This GitHub repository is currently a **documentation bootstrap**, not a computationally reproducible release. The final evidence CSVs, source archives, and the analysis/extraction code that generated the locked tables are not included. The figures and counts below are transcribed from the locked audit record and retained diagnostic outputs; they have not been independently regenerated from raw source files in this repository.

## Principal findings

### Artifact 1 — H701 v3.1

The locked v3.1 H701 cohort contains four duration-qualified candidates: `OP003TA001A001` (481 s), `OP004TA001A001` (616 s), `OP009TA001A001` (680 s), and `OP001TA009A002` (319 s). They were selected from six preliminary single-H701 candidate event records spanning five chemical/operating-point groups; the six records must not be treated as six independent groups.

Two other preliminary records were not included in the four-case cohort: `OP001TA011A001` (279 s; nine theoretical 30-s windows, below the ten-window/300-s screen, with a metadata label-direction warning) and `OP028TA001A002` (270 s; nine theoretical windows and not evaluable in the selected simulation member under the current time mapping). For OP028, the selected member spans 39,875–52,775 s while the mapped YAML interval is 56,700–56,970 s (zero overlap). The check did not enumerate every possible duplicate/alternative archive member, so this is a selected-member result, not a claim that no alternative member exists anywhere in the archive.

#### Stage pressure

For each of the four locked v3.1 traces, all 12 exported stage-wise pressure columns had exactly one unique value across the full recorded time series. The result is `NOT_IDENTIFIABLE_FROM_EXPORTED_TRACE` as a within-event pressure-response channel for this H701 cohort; it is not a claim that the simulator globally lacks pressure variables.

**Model-structure interpretation:** the revised 2026-10-31 pre-lock addendum records the simulator pressure profile as `P^j = P^S + (S-j)·ΔP/(S-1)`. For the head stage `j=S=12`, this gives `P^12=P^S`. With an unchanged head-pressure setpoint during an H701 heat-duty perturbation, stage-12 pressure is therefore expected to remain constant by model construction. This explains why it is unsuitable as the H701 *fault-response* feature; it does not establish a general failure of the simulator's pressure modelling.

**Unit/scale discrepancy requiring resolution:** the retained diagnostic labels the exported columns `pressure stage n / Pa`, but its summary table names the scale fields `min_mbar`, `max_mbar`, `range_mbar` and `delta_raw_mbar`. In that diagnostic, stage-12 values are 300.0, 350.0, 450.0 and 500.0 for the four locked traces, matching the corresponding operating-pressure levels recorded in mbar. The column label and the diagnostic's numerical scale therefore conflict. The raw simulation CSV and exact export/conversion code are not present in this repository; retain the pressure constancy finding, but do not silently assert that the exported `/Pa` label is correct or apply an unverified conversion.

#### PY23

Under the expected physical relation (heating up → pressure up; heating down → pressure down). The H701 perturbation magnitudes below are **percentage-point** changes in the metadata's heater setting, not relative-percent changes in the initial power value. PY23 is the experimental column-top pressure signal; its values and differences in this audit are reported in **mbar**. This experimental sensor unit is separate from the unresolved `/Pa` versus `_mbar` labelling discrepancy in the simulator-export diagnostic.

| Candidate | H701 metadata perturbation | Observed ΔPY23 (mbar) | Interpretation |
|---|---|---:|---|
| `OP003TA001A001` | +25 percentage points (45% → 70%; 157.5 → 245 W) | −1.21 | No sustained response |
| `OP004TA001A001` | −30 percentage points (50% → 20%; 175 → 70 W) | +17.81 | Sustained change opposite to expectation |
| `OP009TA001A001` | +20 percentage points (40% → 60%; 140 → 210 W) | +13.79 | Sustained change consistent with expectation |
| `OP001TA009A002` | Heater off (60% → 0%; 210 → 0 W) | +0.004 | No sustained response |

The available audit record does not establish that this directional physical expectation was preregistered before data inspection. It is used in interpretation, not presented as a confirmed preregistered prediction.

#### Temperature

The locked v3.1 result is `NOT_VERIFIED`; T701-stage sign agreement was 2/4. A separate 2026-10-31 screening memo reports a different metric: the within-event `T_stage1` range crossed its preliminary heuristic, `during_range > max(2.0 °C, 5 × pre-event standard deviation)`, for OP003 (2.70 °C) and OP009 (2.24 °C), but not OP004 (0.14 °C) or OP001TA009 (0.02 °C). OP001TA011 was below the 300-s duration screen and OP028 was not evaluable. These are different metrics and must not be conflated. Neither establishes a confirmed causal thermal response. The superheat/heater-surface explanation remains a post-hoc hypothesis.

**Separate simulator-export diagnostic:** the diagnostic file also reports columns named `temperature stage n / K`. For stage 1, the recorded min/max/range values were OP003 3.109275/3.597901/0.488626, OP004 3.154767/3.634303/0.479537, OP009 3.218939/3.696649/0.477710, and OP001TA009 3.424207/3.722393/0.298187. These are not the same numerical ranges as the `T_stage1` screening values above. The `/K` labels and values near 3–4 do not support interpretation as ordinary absolute kelvin without a variable-definition/export-scale explanation. The mapping between this simulator-export variable and the separately screened `T_stage1` signal is not established.

#### Flow

`COINCIDENTAL_BY_PREDEFINED_TRAJECTORY_SCREEN`. Mean direction agreed in 4/4, but corrected trajectory mean was 0.561 and pooled mean 0.627; 2/4 cases fell below the pre-specified 0.70 threshold. OP004 had contrary bins at 480, 510, and 540 seconds. Directional agreement alone does not satisfy the trajectory screen.

#### Metadata description versus XML heat-duty schedule

The event metadata and the inspected simulation XML provide two distinct representations; their percentages must not be assumed to be numerically interchangeable. The retained XML diagnostic reports:

| Candidate | Metadata description | XML time interval (s, simulation-relative) | XML `heat_duty` values (initial → perturbed) | XML relative change |
|---|---|---:|---:|---:|
| `OP003TA001A001` | H701 +25 percentage points (45% → 70%; 157.5 → 245 W) | 1615–2096 (481 s) | 129.575087 → 189.150174 | +46.0% |
| `OP004TA001A001` | H701 −30 percentage points (50% → 20%; 175 → 70 W) | 1273–1889 (616 s) | 146.988148 → 13.976296 | −90.5% |
| `OP009TA001A001` | H701 +20 percentage points (40% → 60%; 140 → 210 W) | 582–1262 (680 s) | 211.901208 → 253.802416 | +19.8% |
| `OP001TA009A002` | H701 off (60% → 0%; 210 → 0 W) | 1975–2294 (319 s) | 185.031024 → −49.937952 | −127.0% |

Each XML time interval has the same duration as its corresponding metadata event duration in the four inspected cases. This supports duration-level alignment of the schedule windows, but does not establish the unit or meaning of the `heat_duty` magnitudes. These are values from separate metadata and XML fields. The unit/semantic relationship between the metadata's heater-power values and the XML `heat_duty` schedule has not been established in the included evidence. In particular, the negative OP001 XML value has an unresolved sign-convention interpretation. Do not describe these pairs as matching percentages or as a confirmed physical power conversion.

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
- In the retained simulator-side diagnostic, the checked identity was `efflux_ratio = D/(D + R_sim)`; its median absolute residual was 2.214895e-14, but transient outliers remain (maximum 0.02843). The model-level addendum defines `epsilon = D/B`, where `D` is molar distillate and `B` is the total liquid molar stream leaving the buffer. A candidate reflux branch is `B − D`; only if the diagnostic's `R_sim` is confirmed to equal `B − D` does `D/(D + R_sim)` reduce algebraically to `D/B`. This variable identity must be checked against the original simulation equations and CSV definitions.
- The experimental reflux ratio is `R_exp = FT704/FT703`. The candidate cross-domain mapping is `epsilon ≈ FT703/(FT703 + FT704) = 1/(1 + R_exp)`, conditional on FT703 and FT704 being the two branches of the same condensate split and on negligible losses. Directly comparing simulator `epsilon` with experimental `R_exp` is invalid. The FT703/FT704 mapping is provisional and was not independently confirmed against a P&ID. The cause of the transient residuals has not been established.
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
.github/
  workflows/
    tests.yml
docs/
  locked-results.md
evidence/
  README.md
scripts/
  verify_evidence.py
tests/
  test_verify_evidence.py
```

Run `python scripts/verify_evidence.py` from the repository root after placing the four original CSVs in `evidence/`. The verifier checks both recorded byte size and MD5, and prints SHA-256 digests for recording. Run its fixture-based unit tests with `python -m unittest discover -s tests -v` (Python 3.10+). GitHub Actions repeats compile and unit-test checks on pushes and pull requests to `main`; the frozen-file checksum step stays skipped until all four original CSVs are present.

The planned primary predictor was the pre-onset pressure discrepancy over the 300-s window: `q_i^300 = median(|PY23_real(t) − P12_sim(t−δ_i)| / u_PY23(t))`, for `t ∈ [t0−300 s, t0)`, subject to the documented missingness, interpolation, uncertainty, and alignment rules. The offset convention is `t_real = t_sim + δ_i`. The planned primary utility estimand was paired fault-segment `ΔAP_i^fault = AP(M_{−i,+S_i}, R_i^eval) − AP(M_{−i}, R_i^eval)`. Neither the paired `q` values nor `ΔAP` were estimated on a validated H701 cohort. A constant simulated P12 trajectory during the fault does not establish that pre-onset `q` is zero, constant, or uncomputable; the paired pre-onset real/simulation values and valid uncertainties would have to be calculated.

A separate Stage 1 structural/protocol notebook was reviewed during this audit. The reviewed copy had 14 code cells with no execution counts and no saved outputs; it is not included in this repository and is not represented as a reproduction package.

## License and citation

The upstream dataset is described under **CC BY 4.0** in its paper; this applies to the source dataset, not automatically to this repository's original documentation, audit tables, or scripts. This repository has no `LICENSE` or `CITATION.cff` yet; its own reuse terms and formal citation metadata must be set separately by the project owner.

### Upstream citation

Arweiler, J., Jungjohann, I., Muraleedharan, A. et al. *Batch Distillation Data for Developing Machine Learning Anomaly Detection Methods.* Scientific Data 13, 513 (2026). https://doi.org/10.1038/s41597-026-07124-3.

Dataset: *Batch Distillation Data for Developing Machine Learning Anomaly Detection Methods*, version 1.1.3, Zenodo. https://doi.org/10.5281/zenodo.22250958.
