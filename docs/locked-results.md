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

### Channel conclusions

- Stage pressure outputs: `NOT_IDENTIFIABLE_FROM_EXPORTED_TRACE`. Twelve exported stage-pressure columns were static in the four inspected traces. No global statement about all simulator pressure variables follows.

#### PY23

| Candidate | H701 perturbation | Expected physical pressure direction | Observed ΔPY23 | Interpretation |
|---|---|---|---:|---|
| OP003 | +25% heating | Up | −1.21 | No sustained response |
| OP004 | −30% heating | Down | +17.81 | Sustained change opposite to expectation |
| OP009 | +20% heating | Up | +13.79 | Sustained change consistent with expectation |
| OP001 | Heater off | Down | +0.004 | No sustained response |

The directional relation shown above is an expected physical relation (heating up → pressure up; heating down → pressure down). The available audit record does not establish that this directional expectation itself was preregistered before data inspection. Do not describe it as a confirmed preregistered prediction.

#### Temperature

`NOT_VERIFIED`; T701-stage sign agreement was 2/4. The T701 superheat/heater-surface account is a post-hoc physical hypothesis only.

#### Flow

`COINCIDENTAL_BY_PREDEFINED_TRAJECTORY_SCREEN`; direction matched in 4/4, corrected trajectory mean 0.561, pooled 0.627, and 2/4 cases below threshold 0.70. OP004 contrary bins: 480, 510, 540 s.

The criteria were locked before v3.1 evaluation, but not necessarily before any data inspection. For Spearman calculations with N=4, the exact two-sided permutation minimum for untied ranks is 2/24 = 0.0833; the exact/asymptotic method and any formal alpha preregistration were not independently verified.

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
66 raw metadata records -> 14 parent keys across 6 experiments. Composition: 49 noise injections, 8 compound H701/P702/PDI702, 4 unsuitable sensor placement, 4 temperature ramp, 1 empty. Only one Observation child was tied to T703; all 14 parent configurations had `sim_flag=False`. A zero sensor file from an old path lookup was inconclusive. Verdict: `NOT_FEASIBLE_FOR_CURRENT_PAIRED_VALIDATION`; this does not mean T703 is universally unusable.

### AV716/V001/PDI702
Link counts 4/3/7 respectively; no independent event count is implied. These families were not advanced and were not proven non-feasible.

## P701/P702 feasibility demonstration

121 raw metadata records -> 25 parent keys across 19 experiment keys. A previous text classifier incorrectly assigned four HV004 descriptions to pump P701 because “behind reflux pump P701” appeared in the text. The system_id is HV004, so these are sample-valve metadata, not pump events.

Correct grouping: 12 compound pumps & others, 1 pure P701, 1 pure P702, 3 both-pumps-only, 4 multi-all-actuators-off. Both pure-single events occur in one experiment:
`batch_dist_ternary_butan-1-ol+propan-2-ol+water/operating_point_021/test_anormal_experiment_001`.
Both are `sim_flag=True`; the three both-pumps-only changes are `sim_flag=False`.

OP021 has 18,001 time-series rows spanning 38,253–56,253 s. The inspected extraction reported 179 variables, while an earlier shape summary reported 180 columns; the difference in counting convention (for example, whether a time/index column is included) cannot be resolved without the original trace file.

Config efflux-ratio values: [0.301722, 0, 0.301722, 1, 0.301722]; corresponding times: [0, 1123, 1379, 4924, 5178]. Pump-off windows: P702 1123–1379 (256 s); P701 4924–5178 (254 s). Real-event onset offsets are 2 s and 11 s (9 s spread).

The identity `efflux_ratio = D/(D+R)` has median absolute residual 2.214895e-14, mean 4.972e-05, p99 7.971e-05, p99.9 1.742e-02, max 0.02843. 173 rows (0.9611%) exceed 1e-4; 30 rows (0.1667%) exceed 1e-2. Outliers cluster around two transient windows; a solver-transition explanation is plausible but unproven. A small-value-artifact explanation was refuted.

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
