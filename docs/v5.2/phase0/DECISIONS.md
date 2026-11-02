# SimTrust-Pre — Phase 0 Decisions

**Protocol version:** 1.0  
**Frozen for corrected analysis:** 2026-10-30  
**Dataset:** Zenodo record `22250958`, version `1.1.3`  
**DOI:** <https://doi.org/10.5281/zenodo.22250958>  
**Status:** Locked for the v5.2 implementation and before any corrected v5.2 outcome is inspected.

> **Transparency note.** This is not a blind preregistration: exploratory v4.x outputs were already inspected. The legacy association and its interpretation are explicitly withdrawn as evidence (see `RATIONALE.md`). These decisions are frozen before the corrected v5.2 empirical analysis is run. Any later change must be dated, justified, versioned, and labelled as pre- or post-outcome inspection.

## 1. Primary estimand — fault-segment paired utility

**Selected:** Fault-segment utility is the sole primary estimand.

For each reviewed target experiment/run \(i\):

- \(D_{-i}\): labelled real windows from all eligible Operation-phase experiments except target run \(i\).
- \(S_i^{fault}\): a fixed number \(K\) of simulated windows that are fully contained in the independently reviewed simulator-native anomaly interval for the paired scenario. Every selected window must be explicitly supported as part of the simulated fault interval. No simulated pre-onset/normal window enters the primary augmentation arm.
- \(R_i^{eval}\): labelled real windows from target run \(i\), excluding every 30-s window that overlaps the 300-s interval used to compute the primary pre-onset predictor.
- \(M_{-i}\): the pre-specified Logistic Regression model fitted on \(D_{-i}\).
- \(M_{-i,+S_i}\): the same model fitted on \(D_{-i}\) plus the weighted fault-only simulated windows \(S_i^{fault}\).

The run-level outcome is:

\[
\Delta AP_i^{fault} = AP(M_{-i,+S_i}, R_i^{eval}) - AP(M_{-i}, R_i^{eval}).
\]

Both AP values are computed on exactly the same target-real evaluation windows using `sklearn.metrics.average_precision_score`. Positive \(\Delta AP_i^{fault}\) means the paired simulated fault segment improved AP under this training protocol; negative values mean it reduced AP.

**Interpretation boundary:** this is a *paired-scenario, leave-one-experiment-out marginal-utility estimand*. The simulation for target scenario \(i\) is deliberately allowed into the augmented training arm, while the corresponding real experiment remains excluded from real training and supplies the later real evaluation data. This evaluates the utility of that paired simulated fault segment for the corresponding real run. It is **not**, by itself, evidence of generalization to an entirely unseen chemical system or operating-point domain.

## 2. Primary predictor — pre-perturbation discrepancy

The primary predictor is the median tolerance-normalized discrepancy for the pressure channel over the 300 seconds immediately before the reviewed real perturbation onset:

\[
Q_i^{300} = \operatorname{median}_{t\in[t_{0,i}-300,\,t_{0,i})}
\left(\frac{|P_{i}^{real}(t)-P_{i}^{sim}(t-\delta_i)|}{u_{PY23,i}(t)}\right).
\]

The exact implementation must apply the reviewed time transform consistently. The registry convention is:

\[
t_{real}=t_{sim}+\delta_i.
\]

Therefore simulator timestamps are transformed using the reviewed signed offset before time matching. A zero offset is valid only when the evidence supports zero; blank is not zero.

**Primary physical candidate:** `PY23` (mbar) ↔ `pressure stage 12 / Pa` (convert simulator Pa to mbar by dividing by 100). The dataset paper locates PY23 at the top vessel/column-head pressure measurement; the simulation paper identifies stage 12 as the column head. A ratio of run means near one is only a scale sanity check and is not accepted as evidence of spatial identity, dynamic fidelity, or time alignment.

The denominator `±ΔPY23` must be reviewed against the uncertainty archive and its processing documentation. It is treated as a documented measurement-tolerance/uncertainty quantity, **not** as a calibrated standard deviation, probability, or 95% confidence interval unless the source explicitly establishes that interpretation. Missing, zero, negative, non-finite, and interpolated entries are excluded; no epsilon is added.

The primary q summary is `q_median_300s`. Also retain, without substituting them for the primary predictor: valid matched-point count, valid fraction, q90, and exclusion diagnostics.

Larger `Q` means greater pre-onset discrepancy (lower agreement/fidelity). It is not itself a fidelity score. The original directional idea “higher fidelity predicts higher utility” corresponds to a negative association between `Q` and `ΔAP`.

## 3. Primary association test and inference unit

- **Primary statistic:** Spearman correlation between `Q_300s` and `ΔAP_fault`.
- **Primary inferential unit:** independent chemical-system/operating-point groups, not raw time windows and not automatically every experiment as an independent observation.
- Within each group, aggregate run-level `Q_300s` and `ΔAP_fault` using the median; each group receives equal weight in the primary group-level association.
- Report the run-level scatter/correlation descriptively, but do not treat its nominal p-value as confirmatory because runs within operating groups and leave-one-out utility estimates are dependent.
- Report the number of included experiments **and** the number of independent groups. Provide a group-level confidence interval and a group-level permutation result where the number of groups permits meaningful inference. Also report design-sensitivity/power simulations for the realised number of groups; do not represent repeated windows or repeated seeds as new independent experiments.
- The primary p-value is two-sided. The originally motivated direction (higher fidelity / lower Q → higher utility) is stated, but a one-sided test is not used because the legacy exploratory analysis already exposed an opposite-sign association. This avoids choosing the test direction after seeing the old result.
- If the group count is too small for informative inference, label the result descriptive/exploratory. A nominal p-value alone does not upgrade it to confirmatory evidence.

## 4. Evaluation data and preprocessing

- **Primary split:** leave one complete real experiment out at a time. The target real experiment is not used in real training.
- **Primary evaluation set:** target-real Operation windows with reviewed, unambiguous labels, after removing all windows overlapping `[real_onset - 300 s, real_onset)`.
- **Windowing:** 30-s windows, 30-s stride; retain only windows with at least 24 valid observations, no within-window sampling gap above 2.5 s, and a single unambiguous label across the window. Windows crossing label boundaries are excluded.
- **Primary feature set:** `PY23_mean`, `PY23_std`, `PY23_delta` computed on the 30-s windows. Optional channels are not allowed to change the primary PY23 cohort.
- **Preprocessing:** imputer and scaler are fitted only on the real training data for that target fold, then applied unchanged to the target real evaluation windows and simulated windows. No target-run or simulated data may fit the transformation.
- **Model:** `sklearn.linear_model.LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", class_weight=None, max_iter=3000)`. No tuning of `C`, features, threshold, or window length using the primary outcome. Any future tuning must occur only inside training data and be versioned before outer evaluation.
- **Metric:** `average_precision_score`, not trapezoidal PR-AUC. Report target-test prevalence, number of positive/negative windows, baseline AP and augmented AP with every ΔAP value. AP is prevalence-sensitive; paired comparisons use the identical target test set, but prevalence differences across target runs remain a diagnostic limitation.

## 5. Fixed fault-only simulation budget and class-mass policy

- The primary simulation arm contains **fault windows only**. There is no `K normal + K anomaly` simulated sample in the primary arm.
- Select exactly `K` fault windows per accepted target run without replacement. Determine `K` from the minimum eligible fault-window count across the reviewed cohort, capped at 100. The cohort eligibility and `K` are fixed before inspecting any AP/ΔAP values. If fewer than 10 wholly-contained fault windows are available per run after the pre-specified quality checks, stop at the feasibility gate; do not change window length or cohort according to the effect size.
- Use 20 predeclared sampling seeds per run to quantify sensitivity to which `K` fault windows are sampled. Average the 20 ΔAP draws to form that run's primary utility estimate; retain all per-seed draws. These 20 draws are Monte Carlo repeats, not 20 independent runs.
- **Synthetic effective sample-weight mass:** 10% of total training weight. Preserve total effective weight and the 50:50 class-weight mass used in the real-only baseline:
  - real-only baseline: real negative mass = 0.50; real positive mass = 0.50;
  - fault-only augmented arm: real negative mass = 0.50; real positive mass = 0.40; paired simulated fault-positive mass = 0.10.
- This is a **fixed-mass, class-prior-preserving replacement/augmentation policy**, not unweighted addition of rows: the synthetic fault segment replaces 20% of the positive-class effective mass while total mass and effective class prior stay fixed. State this explicitly in the paper.
- Use explicit `sample_weight`; keep `class_weight=None`. Do not combine `class_weight="balanced"` with these hand-designed weights, since scikit-learn multiplies class weights and sample weights.

## 6. Prespecified primary controls

Every control must use the same target-real test set, feature pipeline, total effective training mass, class-mass policy, `K` fault-window budget, and documented seed policy as the paired-simulation arm.

1. **Wrong-run simulated fault segment:** fault-only simulation from another reviewed run, selected by a predeclared match rule (same chemical system and anomaly family where possible; closest eligible operating-point match based only on metadata). Never select a donor using its ΔAP.
2. **Real-donor fault augmentation:** hold a donor real experiment out of the real training pool, then add exactly `K` real fault windows from that donor using the same 10% positive-class mass. Use a matched baseline that excludes both the target run and donor run. Compare the paired simulation and real donor on that identical matched baseline/test set.
3. **Feature-decorrelation control:** independently permute the feature columns across the `K` simulated fault windows, preserving each feature's marginal distribution and the all-positive fault label, but disrupting their joint row-level structure. This replaces the old ambiguous “marginal noise” label in the primary analysis.
4. **Optional pre-onset-normal control:** only if a separate stable/normal interval outside the primary q window is verified. Use the same 10% total mass assigned to normal simulated windows and preserve the class-mass prior by reducing real-negative mass from 0.50 to 0.40 while retaining real-positive mass at 0.50. This control is reported separately and cannot replace the primary fault-only estimand.

**Label shuffling is not a primary fault-only control.** All selected primary simulated samples are labelled fault-positive, so permuting their labels is degenerate or changes the intervention into a different class mixture. Label-shuffle remains available only for the whole-trajectory secondary analysis, where both simulated normal and fault labels are independently supported.

## 7. Prespecified secondary analyses

1. **Whole-trajectory utility:** a separate, secondary practical estimand using `K` simulator-normal and `K` simulator-fault windows, only when normal labels outside the reviewed fault interval are explicitly confirmed. This estimates the utility of a complete synthetic trajectory, not fault-segment utility. It must never replace the primary estimand based on which result is more favorable.
2. **Normal-only pre-onset simulation control**, if a valid normal interval outside the q window can be established.
3. Alternative q horizons: 60, 180, and 600 seconds; 300 seconds remains primary.
4. Alternative discrepancy summaries: q90 and valid fraction; q median remains primary.
5. Alternative physical maps only after separate review: T705 ↔ stage-12 fluid temperature; T703 ↔ stage-1 reboiler-liquid temperature; PDI701 ↔ pressure drop (stage 1 minus stage 12), each with its own units, uncertainty and timing evidence.
6. Leave-operating-point-group-out real-training sensitivity. The target paired simulation remains the intervention; the target real group is held out of real training.
7. Calibration/reference-run exclusion sensitivity, only after canonical reference-run identification from the source paper/configuration.
8. Dose sensitivity at synthetic total-mass fractions 5% and 20%; 10% remains primary.

Apply Benjamini–Hochberg correction to the complete, predeclared secondary test family and publish the full family, not only selected rows. Exploratory extensions (e.g. t7 slopes, other feature sets, additional horizons) must be clearly marked and cannot be promoted to primary after results are viewed.

## 8. Cohort and event inclusion rules

- Review all YAML/XML/event candidates; do not select the first 10–15 or select based on expected effect size.
- Primary cohort rows must have a unique, reviewed event/run identity; an exact simulation archive member; XML simulated status `TRUE`; a single event/simulation mode supported by the current primary implementation; an explicitly reviewed real perturbation time; a confirmed simulator anomaly interval; a documented simulator-to-real time transform; and a reviewed physical mapping/uncertainty field.
- For **fault-segment primary analysis**, only the simulated fault interval must be reviewed and labelled. Do not require all simulator data outside the fault interval to be normal, because outside-interval samples are not used in the primary augmentation arm.
- For **whole-trajectory secondary analysis**, normal labels outside the fault interval must be independently confirmed. Unknown, blind, recovery, or unsupported intervals must not be silently relabelled normal.
- Exclude unresolved/multiple-event cases from the primary cohort with explicit reasons; keep them in the audit ledger for future event-level modelling.
- Use the primary PY23 mapping regardless of missing optional T705 data. Secondary-channel absence may only reduce secondary-analysis coverage.

## 9. Retired legacy result and forbidden practices

The previously reported v4.x exploratory association (approximately `rho=+0.405`, nominal `p=0.045`) and the `H1_FINAL_SUMMARY.png` narrative are **withdrawn as scientific evidence** because the old analysis had full-run preprocessing leakage, simplistic label assumptions, and invalid/compound control comparisons. The result may be mentioned only in a transparent analysis-history note; it must not appear as a confirmed result, guide cohort selection, guide model tuning, or support a “low-fidelity regularizer” claim.

Not allowed:

- changing the primary estimand after inspecting corrected v5.2 outcomes;
- selecting/excluding runs based on q, ΔAP, correlation sign, p-value, or plot appearance;
- treating runs in the same operating-point group or overlapping windows as independent observations;
- interpreting q≤1 as a probability statement or physical indistinguishability without documentation;
- claiming causality, universal Sim2Real generalization, or regularization without dedicated mechanism evidence;
- promoting secondary/ exploratory findings to confirmatory findings after seeing their results.

## 10. Required v5.2 implementation changes before Colab execution

The v5.1 notebook is a predecessor and does **not** implement this Phase 0 choice. Before the corrected empirical run, the new notebook must:

1. Build simulated fault windows directly from the reviewed `[sim_label_start, sim_label_end]` interval and pass only fully-contained positive windows to the primary model. Do not mark all outside simulator rows normal in this primary path.
2. Change the cohort gate from “at least K normal and K anomalous simulation windows” to “at least K confirmed fault windows.”
3. Replace the primary fixed-class sampler with a fault-only fixed-K sampler.
4. Implement the class-mass allocation in Section 5 with total weight=1, class masses=0.50/0.50, `class_weight=None`, and fixed `C`.
5. Remove label-shuffle from primary controls; move it to whole-trajectory sensitivity only.
6. Rebuild wrong-run, real-donor, and feature-decorrelation controls for positive-only simulated fault data with identical class mass, total mass and K.
7. Retain whole-trajectory augmentation as a separately named secondary estimand, with its stricter normal-outside-interval label gate.
8. Aggregate primary association by independent operating-point group and report run-level analysis as descriptive; include design-sensitivity calculations for the realised group count.
9. Save per-seed/per-run provenance, exact train/test group IDs, sample-weight totals by class/source, K, donor IDs, excluded-window counts, test prevalence, and every cohort rejection reason.
10. Run synthetic unit tests for the new fault-only sampler, label interval boundaries, weight-mass invariants, fixed test parity, and control comparability before any dataset outcome is inspected.

**Gate 0:** do not run corrected v5.2 model outcomes until `DECISIONS.md`, `RATIONALE.md`, the event-review rules, and the v5.2 implementation all agree with one another.