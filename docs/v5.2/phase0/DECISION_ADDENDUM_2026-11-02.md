# Phase 0 Decision Addendum — 2026-11-02

**Applies to:** SimTrust-Pre v5.2 Phase 0, version 1.0  
**Decision timing:** before any corrected v5.2 empirical outcome was inspected  
**Status:** engineering comparability clarification; the frozen primary estimand is unchanged

## Reason for this addendum

A code review identified that the primary paired-simulation arm used the leave-one-experiment-out real training pool, while the wrong-run simulation and real-donor controls removed both the target and donor real experiments from their real training pool.

Those arms therefore had different real-only baselines. Comparing their raw `ΔAP` values would mix the effect of the augmentation source with the effect of changing the training cohort.

## Clarification

Keep the frozen primary estimand unchanged:

`ΔAP_i^fault = AP(paired augmentation on the primary leave-one-experiment-out pool) − AP(real-only baseline on that same pool)`.

For comparisons involving a donor-excluded matched pool, additionally evaluate the target event's own paired simulation on that exact matched pool. Compare only these matched-pool augmentation effects:

- `paired_fault_simulation_matched_baseline`
- `wrong_run_simulation`
- `real_donor_positive`

All three must use the same target-real evaluation windows, donor-excluded real training rows, training-only preprocessing, fixed `K`, model settings, and seed. The implementation checks that their matched-baseline AP values agree within a numerical tolerance of (10^{-12}).

The matched-baseline paired result is a control-comparison reference. It does not replace or overwrite the primary `paired_fault_simulation` result and must be reported separately.

The feature-decorrelation control remains a target-pool sensitivity/control arm and must not be conflated with the donor-matched comparisons.

## Implementation and verification boundary

The reviewed Module 5 implementation adds the matched-baseline paired arm and synthetic assertions for baseline parity. These assertions exercise generated fixtures only. They do not establish any real-data effect or complete the inferential analysis.

This clarification does not change the primary predictor, primary estimand, independent inference unit, windowing, sample-weight policy, or frozen v3.1 results. The reason, timing, and impact are recorded here rather than silently rewriting the 2026-10-30 Phase 0 lock.

## Remaining requirements

- Report the original primary paired result and the matched-baseline control comparison as distinct quantities.
- Keep donor matching rules and donor provenance in the audit outputs.
- Do not interpret a six-event software execution gate as statistical power or inferential sufficiency.
- Complete and test the group-level Spearman analysis, group-aware uncertainty/permutation procedure, and design-sensitivity analysis before making a confirmatory association claim.
