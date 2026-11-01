# Locked audit results

This document records the artifact-level conclusions frozen on 2026-11-01. It is a narrative companion to the README, not a substitute for the underlying CSV evidence.

## Status ledger

| Artifact | Status | Boundary |
|---|---|---|
| SimTrust-Pre v3.1 H701 cohort | `LOCKED` | Overall `NOT_VERIFIED_UNDER_PREDEFINED_CRITERIA` |
| Archive Crosswalk v2.2.5 | `CLOSED` | 254 parent keys are not 254 physical events |
| Feasibility Map | `CLOSED` | Feasibility differs from validation |
| P701/P702 | `STRONG_FEASIBILITY_DEMONSTRATION` | One independent experiment; not validation |

## H701 candidate register

| Candidate | Duration |
|---|---:|
| `OP003TA001A001` | 481 s |
| `OP004TA001A001` | 616 s |
| `OP009TA001A001` | 680 s |
| `OP001TA009A002` | 319 s |

H701 is a manually operated open-loop heater, not a PI-controlled jacket heater.

The four listed candidates are the duration-qualified subset of six preliminary single-H701 candidate event records across five chemical/operating-point groups. The other two were:
- `OP001TA011A001`: 279 s (nine theoretical non-overlapping 30-s windows), below the ten-window/300-s screen. Its metadata contains a direction-label warning: the perturbation text says H701 power increased while the label says reduced.
- `OP028TA001A002`: 270 s (nine theoretical windows). The selected simulation member spans 39,875–52,775 s while the mapped YAML event interval is 56,700–56,970 s, so the selected member has zero overlap. The check did not exhaustively enumerate alternative/duplicate members.

The broader 2026-10-31 decision memo separately reports five time-evaluable pressure candidates and treats OP028 as missing evidence, not as an invariant trace. These are different denominators from the four-trace locked v3.1 artifact; do not merge them.

### Channel conclusions

#### Stage pressure

For each of the four inspected traces, the 12 exported stage-wise pressure columns each had one unique value across the recorded time series. The result is `NOT_IDENTIFIABLE_FROM_EXPORTED_TRACE` for a pressure-response analysis in these traces; no global claim about simulator pressure modelling follows.

**Unit/scale discrepancy requiring resolution:** in the OP003 diagnostic, the exported column is labelled `pressure stage 12 / Pa` and has the constant value 300.0. The corresponding operating-point metadata says 300 mbar, while the selected XML configuration excerpt reports `pressure_12 = 30000.00`. These values are numerically consistent with a factor-of-100 Pa↔mbar conversion, but the CSV label and numeric scale do not agree. The conversion and exact semantics of the exported column have not been independently confirmed. Pressure constancy can be reported; the absolute unit/value must remain unresolved pending review of the raw CSV, XML definition, and export convention.

#### PY23

| Candidate | H701 metadata perturbation | Expected physical pressure direction | Observed ΔPY23 | Interpretation |
|---|---|---|---:|---|
| OP003 | +25 percentage points (45% → 70%; 157.5 → 245 W) | Up | −1.21 | No sustained response |
| OP004 | −30 percentage points (50% → 20%; 175 → 70 W) | Down | +17.81 | Sustained change opposite to expectation |
| OP009 | +20 percentage points (40% → 60%; 140 → 210 W) | Up | +13.79 | Sustained change consistent with expectation |
| OP001 | Heater off | Down | +0.004 | No sustained response |

The directional relation shown above is an expected physical relation (heating up → pressure up; heating down → pressure down). The available audit record does not establish that this directional expectation itself was preregistered before data inspection. Do not describe it as a confirmed preregistered prediction.

#### Metadata description versus XML heat-duty schedule

The event metadata and the inspected simulation XML provide distinct representations; their percentages must not be assumed numerically interchangeable.

| Candidate | Metadata description | XML time interval (s, simulation-relative) | XML `heat_duty` values (initial → perturbed) | XML relative change |
|---|---|---:|---:|---:|
| OP003 | H701 +25 percentage points (45% → 70%; 157.5 → 245 W) | 1615–2096 (481 s) | 129.575087 → 189.150174 | +46.0% |
| OP004 | H701 −30 percentage points (50% → 20%; 175 → 70 W) | 1273–1889 (616 s) | 146.988148 → 13.976296 | −90.5% |
| OP009 | H701 +20 percentage points (40% → 60%; 140 → 210 W) | 582–1262 (680 s) | 211.901208 → 253.802416 | +19.8% |
| OP001TA009A002 | H701 off | 1975–2294 (319 s) | 185.031024 → −49.937952 | −127.0% |

Each XML time interval has the same duration as its corresponding metadata event duration in the four inspected cases. This supports duration-level alignment of the schedule windows, but does not establish the unit or meaning of the `heat_duty` magnitudes. These values come from separate metadata and XML fields. The unit/semantic relationship between the metadata's heater-power values and the XML `heat_duty` schedule has not been established in the included evidence. The negative OP001 XML value has an unresolved sign-convention interpretation. Do not describe these pairs as matching percentages or as a confirmed physical power conversion.

#### Temperature

`NOT_VERIFIED`; the locked v3.1 result records T701-stage sign agreement of 2/4. A separate 2026-10-31 screening memo reports a different metric: the within-event `T_stage1` range crossed its preliminary heuristic, `during_range > max(2.0 °C, 5 × pre-event standard deviation)`, in OP003 (2.70 °C) and OP009 (2.24 °C), but not OP004 (0.14 °C) or OP001TA009 (0.02 °C). OP001TA011 was below the 300-s duration screen and OP028 was not evaluable. Do not conflate the range-screen metric with the final sign-agreement statistic. The T701 superheat/heater-surface account is a post-hoc physical hypothesis only.

#### Flow

`COINCIDENTAL_BY_PREDEFINED_TRAJECTORY_SCREEN`; direction matched in 4/4, corrected trajectory mean 0.561, pooled 0.627, and 2/4 cases below threshold 0.70. OP004 contrary bins: 480, 510, 540 s. Directional agreement alone does not satisfy the trajectory screen.
The criteria were locked before v3.1 evaluation, but not necessarily before any data inspection. The planned primary estimand, pre-onset fidelity `q` versus fault-segment utility `ΔAP`, was not estimated on a validated H701 cohort. Invariant simulated stage-12 pressure during the fault does not establish that pre-onset `q` is zero, constant, or uncomputable; paired pre-onset real/simulation values, valid uncertainty measurements, and verified time alignment would be required. For Spearman calculations with N=4, the exact two-sided permutation minimum for untied ranks is 2/24 = 0.0833; the exact/asymptotic method and any formal alpha preregistration were not independently verified.

## Crosswalk counts and boundaries

525 raw metadata records -> 254 parent keys (235 ID-backed, 19 fallback/index-based). There are 181 Observation children within 100 parent keys.

Class counts:
- `OBSERVATION_DERIVED`: 99
- `SYSTEM_ASSOCIATED_NO_RECOGNIZED_ACTUATOR`: 73
- `SINGLE_DECLARED_ACTUATOR`: 38
- `MULTIPLE_DECLARED_ACTUATORS`: 25
- `PROVENANCE_UNRESOLVED`: 19

Safety text coverage classes: `TEXT_MATCH` 19, `NO_TEXT_MATCH` 116, `PARTIAL_TEXT_COVERAGE` 2, `NOT_ASSESSABLE` 117. This is lexical coverage, not a safety-event census.

PerturbationMode duration: 326 raw records had positive duration, 180 had zero, none negative, and 19 missing. 138 parent keys had at least one positive duration; this is not a count of independent physical perturbations.

In train_normal, no label=1 or label=2 was found. One binary mixture CSV had 8,334 rows (7,118 label 0, 1,216 NaN, zero label 1/2). Another OP007 water file had 20 Observation-derived YAML entries while all 3,282 CSV rows had label 0. This is not automatically a label contradiction: Observation may mean a recorded observation rather than an anomaly. NaN denotes missing labels, not normal/anomalous classes.

The published paper's figure 36 was not reproduced from the current archive extraction/grouping. This is not evidence of a contradiction; filtering and unit-of-counting definitions may differ.

## Feasibility Map boundaries

### HV004/HV005
69 raw metadata links -> 42 parent keys. 59 raw descriptions say “Improperly sealed sample valve”. These are not 59 independent events. Interpretation as manual sample-valve cases is strongly supported but not fully verified. In the checked actuator archive/config, no matching direct actuator/control signal was identified; only a representative simulator file was checked, not all simulation outputs. Verdict: `NOT_FEASIBLE_FOR_DIRECT_ACTUATOR_PAIRED_STUDY`.

### T703
66 raw metadata records -> 14 parent keys across 6 experiments. Raw-record description counts: 49 noise injections, 8 compound H701/P702/PDI702, 4 unsuitable sensor placement, 4 temperature ramp, and 1 empty. These counts sum to the 66 raw metadata records, not to 66 independent events. Only one Observation child was tied to T703; all 14 parent configurations had `sim_flag=False`. A zero sensor file from an old path lookup was inconclusive. Verdict: `NOT_FEASIBLE_FOR_CURRENT_PAIRED_VALIDATION`; this does not mean T703 is universally unusable.

### AV716/V001/PDI702
Link counts 4/3/7 respectively; no independent event count is implied. These families were not advanced and were not proven non-feasible.

## P701/P702 feasibility demonstration

121 raw metadata records -> 25 parent keys across 19 experiment keys. A previous text classifier incorrectly assigned four HV004 descriptions to pump P701 because “behind reflux pump P701” appeared in the text. The system_id is HV004, so these are sample-valve metadata, not pump events.

The detailed summary lists 12 compound pumps & others, 1 pure P701, 1 pure P702, 3 both-pumps-only, and 4 multi-all-actuators-off. These categories sum to 21, not 25 parent keys; four parent keys are not accounted for in this breakdown. The original event CSV is required to determine whether this reflects omitted categories or a reporting error; no class is inferred for the four-key difference. Both pure-single events occur in one experiment:
`batch_dist_ternary_butan-1-ol+propan-2-ol+water/operating_point_021/test_anormal_experiment_001`.
Both are `sim_flag=True`; the three both-pumps-only changes are `sim_flag=False`.

OP021 has 18,001 time-series rows spanning 38,253–56,253 s. The inspected extraction reported 179 variables, while an earlier shape summary reported 180 columns; the difference in counting convention (for example, whether a time/index column is included) cannot be resolved without the original trace file.

Config efflux-ratio values: [0.301722, 0, 0.301722, 1, 0.301722]; corresponding times: [0, 1123, 1379, 4924, 5178]. Pump-off windows: P702 1123–1379 (256 s); P701 4924–5178 (254 s). Real-event onset offsets are 2 s and 11 s (9 s spread).

For the simulator-side identity check, `efflux_ratio = D/(D+R)` (where `D` and `R` are the simulator-side distillate and reflux terms used in this calculation; this is distinct from the experimental reflux ratio `FT704/FT703`) has median absolute residual 2.214895e-14, mean 4.972e-05, p99 7.971e-05, p99.9 1.742e-02, max 0.02843. 173 rows (0.9611%) exceed 1e-4; 30 rows (0.1667%) exceed 1e-2. Outliers cluster around two transient windows; a solver-transition explanation is plausible but unproven. A small-value-artifact explanation was refuted.

Mass-derived ratio median absolute error was 0, maximum 0.03152; effective MW median 0.0455 kg/mol. Do not claim the ratios are identical or composition-equivalent.

FT703/FT704 are both described as mass-flux sensors. FT703 -> distillate and FT704 -> reflux remains provisional and not independently confirmed with a P&ID. Directional real/sim alignment under this mapping is descriptive. If mapping was selected using one event, that event is mapping-selection data; the second is descriptive cross-event consistency, not independent validation.

No direct P701/P702 power/state variables were found in the inspected OP021 file. Do not generalize this to the entire simulation archive.

## Claims explicitly not made

- No claim that the simulator globally lacks pressure modelling.
- No claim that the PY23 physical direction expectation was preregistered before data inspection.
- No claim that H701 passed validation.
- No claim that raw metadata rows or parent keys equal independent physical events.
- No claim that the P701/P702 demonstration validates the simulator.
- No confirmed causal explanation for the transient efflux-ratio residuals.
- No definitive FT703/FT704 process mapping.
- No claim that P701/P702 state variables are absent from every simulation output.
