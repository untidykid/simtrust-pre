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

## Principal findings

### Artifact 1 — H701 v3.1

Four candidates were evaluated: `OP003TA001A001` (481 s), `OP004TA001A001` (616 s), `OP009TA001A001` (680 s), and `OP001TA009A002` (319 s).

- **Stage pressure:** the 12 exported stage-pressure columns inspected were static across the four traces. The result is `NOT_IDENTIFIABLE_FROM_EXPORTED_TRACE`; it does not establish that pressure is absent from the simulator globally.
- **PY23:** sustained changes occurred in OP004 (+17.81) and OP009 (+13.79), but opposite to the predicted direction. OP003 (-1.21) and OP001 (+0.004) showed no sustained response.
- **Temperature:** `NOT_VERIFIED`; T701-stage sign agreement was 2/4. The proposed superheat/heater-surface explanation remains a post-hoc hypothesis, not a confirmed mechanism.
- **Flow:** `COINCIDENTAL_BY_PREDEFINED_TRAJECTORY_SCREEN`. Mean direction agreed in 4/4, but corrected trajectory mean was 0.561 and pooled mean 0.627; 2/4 cases fell below the pre-specified 0.70 threshold. OP004 had contrary bins at 480, 510, and 540 seconds.

The predefined criteria were locked before the v3.1 evaluation, but not necessarily before any data inspection.

### Artifact 2 — Archive Crosswalk v2.2.5

- 525 raw metadata records were grouped into 254 parent keys: 235 ID-backed and 19 fallback/index-based.
- 181 Observation children were associated with 100 parent keys.
- Parent-key class counts: 99 `OBSERVATION_DERIVED`, 73 `SYSTEM_ASSOCIATED_NO_RECOGNIZED_ACTUATOR`, 38 `SINGLE_DECLARED_ACTUATOR`, 25 `MULTIPLE_DECLARED_ACTUATORS`, and 19 `PROVENANCE_UNRESOLVED`.
- A parent key is not necessarily an independent physical event. In particular, raw metadata counts and parent-key counts must not be presented as physical-event counts.
- Safety metadata classification is lexical/text-coverage evidence, not a census of safety events.
- The original v2.2.5 crosswalk is retained as the frozen audit artifact. A simplified rebuild produced 240 keys rather than 254 and is **not** used as evidence.

### Artifact 3 — Feasibility Map

The complete map screened five families: H701, HV004/HV005, T703, P701/P702, and AV716/V001/PDI702.

- **HV004/HV005:** 69 raw metadata links grouped into 42 parent keys. The 59 descriptions “Improperly sealed sample valve” are raw descriptions, not 59 independent events. The family was judged `NOT_FEASIBLE_FOR_DIRECT_ACTUATOR_PAIRED_STUDY` based on the inspected evidence; the actuator/configuration inspection was not exhaustive across every simulation output.
- **T703:** 66 raw records grouped into 14 parent keys across 6 experiments. The 49 noise-injection records are not 49 independent events. Status: `NOT_FEASIBLE_FOR_CURRENT_PAIRED_VALIDATION`, not a universal claim that T703 can never be studied.
- **AV716/V001/PDI702:** link counts were 4/3/7 respectively; these are not independent event counts and were not advanced.

The separate evidence CSV in this repository is scoped specifically to the HV004/HV005 audit, not the entire five-family Feasibility Map.

### Artifact 4 — P701/P702 feasibility demonstration

- 121 raw metadata records were grouped into 25 parent keys across 19 experiment keys.
- The two genuine pure-single parent events (one P701, one P702) occur in the same experiment: `batch_dist_ternary_butan-1-ol+propan-2-ol+water/operating_point_021/test_anormal_experiment_001`.
- The OP021 trace contains 18,001 rows and 179 variables. The pump-off windows are 256 s (P702) and 254 s (P701); observed onset offsets were 2 s and 11 s, with a 9 s spread.
- The relationship `efflux_ratio = D/(D+R)` matched to a median absolute residual of 2.214895e-14, but transient outliers remain (maximum 0.02843). Their cause has not been established.
- The FT703/FT704 mapping to distillate/reflux is provisional and was not independently confirmed against a P&ID.
- Directional real/sim alignment is descriptive evidence under that provisional mapping, not four independent validation tests. Both pump cases come from one independent experiment.

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
```

## License and citation

No license or formal citation metadata is assigned in this bootstrap. Reuse permissions and citation details should be added only after the project owner confirms them.
