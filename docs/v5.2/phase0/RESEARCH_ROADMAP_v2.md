# SimTrust-Pre — Research Roadmap v2.0

**Decision date:** 2026-10-30  
**Primary estimand:** paired fault-segment utility  
**Secondary estimand:** whole-trajectory utility  
**Dataset:** Zenodo `22250958`, version `1.1.3`  
**Status:** Phase 0 decisions frozen; v5.2 implementation and corrected empirical analysis pending.

## Recommendation

Use the available multi-month window for a full, review-first study. Review every event candidate that can be resolved from evidence; retain unresolved candidates in an audit ledger with explicit exclusion reasons. Do not select runs by their q, ΔAP, correlation sign, p-value or plot appearance. The independent inference unit is the chemical-system/operating-point group, not each time window or every run treated as automatically independent.

## 1. Locked scientific question

> Across independently reviewed paired runs, does the pre-perturbation measurement-tolerance-normalized discrepancy of the paired simulator predict the marginal utility of adding only that run's simulated fault segment to an anomaly detector evaluated on the corresponding later real experiment?

The primary predictor is median `q(t)=abs(real(t)-sim(t))/u(t)` over the 300 seconds before the reviewed real perturbation onset, for `PY23` compared with simulation `pressure stage 12 / Pa` after conversion to mbar and explicit time alignment.

The primary outcome is `ΔAP_fault`: AP on the target real experiment after adding a fixed-budget, fault-only paired simulation segment to the real training pool, minus AP for the real-only baseline. Both models are evaluated on exactly the same target-real windows, after excluding every window overlapping the q window. AP is `sklearn.metrics.average_precision_score`.

This is a paired-scenario marginal-utility estimand, not a claim that the augmented detector generalizes to an entirely unseen operating-point domain. Leave-operating-point-group-out remains a stricter sensitivity.

## 2. Why fault-segment is primary

The q predictor is computed before onset. Including those same pre-onset simulation windows in the primary augmentation would mix the effect of simulated normal-state examples with the effect of the simulated fault segment. The project’s central question is specifically whether *pre-onset agreement predicts fault-segment utility*. Hence only reviewed post-onset fault windows enter the primary synthetic arm.

Whole-trajectory utility remains a prespecified secondary practical estimand. It can answer whether a complete run is useful, but it cannot replace the fault-only primary result or be interpreted as evidence for the same mechanistic question.

The primary arm therefore uses `K` fault windows only, not `K` normal + `K` fault windows. The real training data already provides both classes. Simulation receives 10% total effective sample-weight mass as positive fault data; real negative/positive masses are adjusted to 0.50/0.40 respectively, keeping the total mass at 1.0 and the overall effective class masses at 0.50/0.50. Use explicit sample weights and `class_weight=None`.

## 3. Phase 0 — protocol lock (completed as a document decision)

**Deliverables:** `DECISIONS.md`, `RATIONALE.md`, updated README.  
**Gate:** no corrected model result is run until v5.2 code matches these documents and passes synthetic tests.

The lock is not a blind preregistration: legacy exploratory outputs were already inspected. The v4.x result is withdrawn as evidence. Corrected v5.2 outcomes have not been inspected at the time of this lock.

## 4. Phase 1 — forensic event registry

- Re-run Stage 1 on exact Zenodo version 1.1.3 and save archive checksums, versions and file manifests.
- Preserve every YAML event and the positional YAML–XML anomaly crosswalk. Distinguish a true simulation flag, an event ID, a perturbation onset and a simulator anomaly-label interval.
- Check exact simulation archive membership, not guessed paths.
- Require one reviewed event/mode per primary run under the current implementation; multi-event runs stay in the audit ledger for future event-level modelling.
- For primary fault-segment analysis, review the simulator anomaly interval; do not require all other simulator samples to be normal because those samples are not used in the primary arm.
- For whole-trajectory secondary analysis, separately confirm which outside-interval windows are genuinely normal. Unknown, blind, recovery and unsupported periods are never relabelled as normal.

**Deliverables:** complete candidate registry, exact-path audit, event conflict table, inclusion/exclusion ledger, checksums.

## 5. Phase 2 — physical and time alignment

- Primary physical map: `PY23` at the column/top-vessel pressure location ↔ simulator head stage 12. Convert `Pa` to `mbar` before comparing with `PY23` and its uncertainty denominator.
- A ratio of means near 1 is only a scale check. Validate dynamics using plotted paired time traces, timestamp matching, lag/offset evidence and residual diagnostics.
- Confirm the meaning and units of `±ΔPY23`; do not assume standard deviation or 95% interval semantics.
- For each included event, review real onset, simulator-native anomaly interval, time origins, signed time offset, units and evidence. A blank offset is never interpreted as zero.
- Identify the calibration/reference run only from documentary/configuration evidence; perform a with/without sensitivity if established.
- Keep T705, T703 and PDI701 out of the primary predictor until their physical identity, units, uncertainty and time alignment are reviewed separately.

**Deliverables:** approved registry, sensor map, alignment plots, uncertainty semantics note, calibration-run evidence.

## 6. Phase 3 — window and cohort validation

- Use 30-s windows with 30-s stride for the primary run; require at least 24 valid observations and no within-window gap greater than 2.5 s.
- Require label purity; reject windows crossing event boundaries or containing unknown labels.
- The primary simulation cohort requires a minimum count of wholly-contained confirmed fault windows per run. Select one shared `K` from the smallest eligible count, capped at 100, before inspecting model outcomes. Require at least 10 fault windows per included run; otherwise stop and record a feasibility failure rather than tuning window duration to improve results.
- Use at least 20 fixed sampling seeds for the K-window draw and preserve all per-seed results; sampling repeats do not increase N.
- Confirm that target-real test windows exclude the complete 300-s q window.

**Deliverables:** sample-flow chart, window-quality audit, fault-window counts, frozen eligible cohort and K.

## 7. Phase 4 — primary utility and matched controls

For each target run, exclude its real data from the real training pool. Compare:

- real-only baseline;
- baseline plus K paired simulated fault windows;
- wrong-run simulated fault windows under a predeclared donor match;
- a real fault-segment donor held out of the matched baseline before augmentation;
- feature-decorrelated paired simulation windows preserving feature marginals;
- optional verified pre-onset normal-only simulation augmentation outside the q window.

Use the same target-real test data, same transformations fitted only on real training data, same K, same total weight and class-mass policy, same C and fixed seeds across comparisons. The 10% total synthetic mass replaces 20% of real positive-class mass, preserving total weight and a 50:50 class mass.

Label shuffle is not a meaningful primary control when the primary synthetic set contains only positive labels. It is reserved for the two-class whole-trajectory secondary analysis.

**Deliverables:** run-level ΔAP, 20-seed draws, matched control table, donor provenance and sample-weight audit.

## 8. Phase 5 — association, uncertainty and sensitivity

- Primary predictor-outcome statistic: Spearman association between q300 and fault-only ΔAP.
- Primary inferential summary aggregates run-level q and ΔAP within chemical-system/operating-point groups and gives each group equal weight. Run-level association is descriptive.
- Because leave-one-run-out utility estimates share much of their training data, state dependence explicitly. Use group-aware resampling/permutation and design-sensitivity simulations for the realised independent-group count; do not overstate nominal p-values.
- Use a two-sided primary test because the legacy exploratory analysis already exposed an opposite-sign association. Larger q means lower fidelity; the original high-fidelity-benefit expectation corresponds to negative rho.
- Secondary family: q horizons 60/180/600s, q90/valid fraction, approved T705/T703/PDI701 maps, whole-trajectory utility, normal-only control, leave-operating-point-group-out, calibration-run exclusion, and synthetic mass 5%/20%. Apply BH to the complete secondary family.
- Report target-test prevalence, number of positives/negatives, baseline AP and augmented AP; AP is prevalence-sensitive even though paired comparisons use the same test windows.

**Deliverables:** primary group-level association, interval/permutation, full secondary BH table, robustness matrix, diagnostics.

## 9. Phase 6 — code release and report

- Implement v5.2 according to `DECISIONS.md`; v5.1 is a predecessor and still uses mixed normal+fault synthetic windows in its primary path.
- Unit-test fault-interval boundaries, positive-only fixed-K sampling, weight-mass invariants, class prior preservation, matched-test parity, control comparability, exact time conversion, and review-gate blocking.
- Execute from a clean Colab runtime using pinned package versions and the exact dataset record. Save archive checksums, code revision, seeds, registry, all per-run/per-seed outputs, errors and exclusions.
- Build report figures and tables only from clean-run output files. Keep confirmatory primary, prespecified secondary and exploratory results visually and textually distinct.
- Do not commit raw dataset archives unless license/terms and repository size policy permit it.

## 10. Current go/no-go

**Go:** Phase 0 documents are locked; proceed to the v5.2 implementation and registry review.  
**Not yet approved:** the existing v5.1 notebook as the final empirical pipeline, the legacy v4.x correlation, any regularization claim, or any final paper abstract claiming an empirical discovery.

## Core references

- Arweiler et al. (2026), *Batch Distillation Data for Developing Machine Learning Anomaly Detection Methods*, Scientific Data 13, 513. <https://doi.org/10.1038/s41597-026-07124-3>
- Werner et al. (2026), *Automated Batch Distillation Process Simulation for a Large Hybrid Dataset for Deep Anomaly Detection*, Computers & Chemical Engineering, 109827. <https://doi.org/10.1016/j.compchemeng.2026.109827>
- Gonçalves et al. (2024), *Evaluation is key: a survey on evaluation measures for synthetic time series*, Journal of Big Data. <https://doi.org/10.1186/s40537-024-00924-7>
- scikit-learn, data leakage guidance. <https://scikit-learn.org/stable/common_pitfalls>
- scikit-learn, LogisticRegression. <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html>
- scikit-learn, average_precision_score. <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html>
- Tobin et al. (2017), *Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World*. <https://doi.org/10.1109/IROS.2017.8202133>