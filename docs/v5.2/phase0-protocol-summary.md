# v5.2 Phase 0 Protocol Summary

**Protocol version:** 1.0  
**Frozen date:** 2026-10-30  
**Dataset:** Zenodo record `22250958`, version `1.1.3`  
**Status:** Frozen for the corrected v5.2 implementation before corrected v5.2 outcomes were inspected.

> **Transparency:** This is not a blind preregistration. Exploratory v4.x outputs had already been inspected. The legacy association and its interpretation were withdrawn as evidence. The decisions were frozen before the corrected v5.2 empirical analysis; any later change must be dated, justified, versioned, and labelled as pre- or post-outcome inspection.

## Primary estimand

The sole primary estimand is paired fault-segment utility:

\[
\Delta AP_i^{fault}=AP(M_{-i,+S_i},R_i^{eval})-AP(M_{-i},R_i^{eval}).
\]

The augmented arm adds only `K` reviewed simulated windows that are wholly contained in the simulator-native observable fault interval. The target real experiment is excluded from real training and supplies the later real evaluation set. Every real evaluation window overlapping the 300-second pre-onset predictor window is excluded. This is a paired-scenario, leave-one-experiment-out marginal-utility estimand; it is not, by itself, evidence of generalization to a wholly unseen chemical system or operating-point domain.

## Primary predictor

The primary predictor is the median tolerance-normalized discrepancy between real `PY23` and the paired simulation head-stage pressure over the 300 seconds immediately preceding the reviewed real onset:

\[
Q_i^{300}=\operatorname{median}_{t\in[t_{0,i}-300,t_{0,i})}
\left(\frac{|P_i^{real}(t)-P_i^{sim}(t-\delta_i)|}{u_{PY23,i}(t)}\right).
\]

The registry convention is `t_real = t_sim + delta_i`. The signed offset must be supported by evidence; a blank offset is not zero. The primary physical candidate is `PY23` (mbar) paired with simulation `pressure stage 12 / Pa`, converted by dividing Pa by 100. A ratio of run means near one is only a scale sanity check, not proof of spatial identity, dynamic fidelity, or time alignment.

The `±ΔPY23` denominator is treated as a documented tolerance/uncertainty quantity, not automatically as a calibrated standard deviation, probability, or 95% interval. Missing, non-finite, non-positive, or interpolated entries are not silently repaired and do not enter the primary calculation.

## Evaluation, preprocessing, and model

- Leave one complete real experiment out at a time.
- Use 30-second windows with a 30-second stride.
- Require at least 24 valid observations per window, no within-window sampling gap above 2.5 seconds, and one unambiguous label per window.
- Exclude target-real evaluation windows that overlap the full 300-second `q` window.
- Use the primary PY23 features `PY23_mean`, `PY23_std`, and `PY23_delta`; optional channels must not change the primary PY23 cohort.
- Fit imputation and scaling on real training data only; apply the fitted transformations unchanged to evaluation and simulation data.
- Use Logistic Regression with the frozen settings in the reviewed implementation; do not tune on the primary outcome.
- Use `sklearn.metrics.average_precision_score` for AP.

## Simulation budget and weight policy

- The primary synthetic arm contains fault windows only, not a normal-plus-fault mixture.
- Choose one shared `K` from the minimum eligible fault-window count across the reviewed cohort, capped at 100. Require at least 10 fully contained valid fault windows per accepted run; otherwise stop at the feasibility gate.
- Use 20 fixed sampling seeds per run. Seeds are Monte Carlo repeats, not independent experiments.
- Keep total effective training weight fixed at 1.0 and the effective class masses at 0.50 negative / 0.50 positive. In the augmented arm, allocate 0.50 to real negatives, 0.40 to real positives, and 0.10 to paired simulated fault-positive samples. Use explicit sample weights and `class_weight=None`.

## Controls and inference

Prespecified controls include wrong-run simulated fault segments, a real fault-segment donor, and feature-decorrelated paired simulation windows. Optional secondary analyses must remain distinct from the primary estimand.

The primary association is two-sided Spearman correlation between group-level median `Q_300s` and group-level median `Delta AP_fault`. The inferential unit is the chemical-system × operating-point group, not time windows, seeds, or automatically every run. Run-level associations are descriptive. Dependence among leave-one-out utility estimates must be acknowledged; report group counts, uncertainty, and design-sensitivity/power analysis. If the available group count is too small for informative inference, report descriptive/exploratory results rather than treating a nominal p-value as confirmatory.

## Release gate

A real-data run requires a human-reviewed event registry with exact experiment and simulation-member identity, reviewed onset and simulator fault interval, documented time basis and signed offset, verified channel mapping and units, uncertainty semantics, and interpolation-flag provenance. Synthetic tests do not satisfy these evidence requirements.
