# SimTrust-Pre v5.2 — Scientific Rationale

**Protocol version:** 1.0  
**Frozen date:** 2026-10-30  
**Dataset:** Zenodo record `22250958`, version `1.1.3`  
**Status:** Rationale for the corrected v5.2 protocol; not an empirical result.

## Research question

The project asks whether the pre-perturbation discrepancy between a real process measurement and its paired simulation can predict the marginal usefulness of that simulation's fault segment when training an anomaly detector for the corresponding real experiment.

The two quantities have distinct roles:

- The predictor, (Q_i^{300}), is calculated only from the 300 seconds before the reviewed real perturbation onset. It measures a tolerance-normalized discrepancy; it is not a probability or a calibrated fidelity score.
- The outcome, (Delta AP_i^{fault}), compares a real-only detector with the same detector trained with a fixed-budget sample of the paired simulator's reviewed fault windows. Both are evaluated on the same later real windows.

The primary association is between these two quantities at the independent chemical-system × operating-point group level.

## Why fault-segment utility is primary

The predictor is measured before the perturbation. Including those same pre-onset simulator windows in the primary augmentation would mix the contribution of simulated normal-state data with the contribution of simulated fault data. That would make it harder to answer the project's central question: whether pre-onset agreement predicts the usefulness of the simulated fault segment.

Therefore, the primary synthetic arm uses only (K) windows fully contained in the reviewed simulator-native observable fault interval. Whole-trajectory augmentation remains a separate secondary estimand and is allowed only when normal labels outside the fault interval have been independently established. The two estimands must not be substituted for one another based on which result is more favourable.

## Why the evaluation is paired

For target experiment (i), the real target experiment is excluded from real training and supplies the later real evaluation set. The baseline and augmented models use exactly the same real test windows, the same training-only preprocessing, the same model settings, and the same evaluation metric. The augmented model receives only the target's paired simulated fault segment.

This is a paired-scenario, leave-one-experiment-out marginal-utility design. It is not equivalent to demonstrating generalization to an entirely unseen chemical system or operating-point domain. A stricter leave-operating-point-group-out analysis is retained as a sensitivity analysis.

## Why the sample-weight mass is fixed

Simply appending synthetic rows would increase total training weight and alter the effective class prior. The protocol instead fixes total effective weight at 1.0 and keeps effective class mass at 0.50 negative / 0.50 positive:

| Arm | Real negative | Real positive | Simulated fault positive |
|---|---:|---:|---:|
| Real-only baseline | 0.50 | 0.50 | 0.00 |
| Fault-only augmented | 0.50 | 0.40 | 0.10 |

The synthetic fault segment therefore replaces 20% of the real positive-class effective mass. Explicit sample weights are used with `class_weight=None`. This makes the augmentation comparison about the information contributed by the paired fault segment under a fixed mass budget, rather than an uncontrolled increase in total sample weight.

## Why controls need matched baselines

Wrong-run simulation and real-donor controls require removing the donor's real experiment from the real training pool. Their baseline therefore differs from the primary leave-one-experiment-out baseline unless the paired simulation is also evaluated on that same donor-excluded pool.

The implementation retains the primary paired result and adds a separate `paired_fault_simulation_matched_baseline` arm whenever a valid donor is available. That matched paired arm, wrong-run simulation, and real-donor augmentation must use the same target-real test rows and the same donor-excluded real training pool. Their baseline AP values are checked for equality before their augmentation effects are compared. The matched-baseline result is a control comparison; it does not replace the primary estimand.

## Why independent groups define inference

Multiple runs can share a chemical system and operating point, and leave-one-run-out estimates share much of their real training data. Time windows and Monte Carlo seeds are repeated measurements, not independent experiments. The primary inferential unit is therefore the chemical-system × operating-point group.

Run-level results remain useful descriptions. Group medians are used for the primary association, with group-aware uncertainty and permutation procedures where the realised group count supports meaningful inference. If the number of independent groups is too small, the association must be reported as descriptive or exploratory. A minimum event-count gate in software is an execution/feasibility safeguard, not evidence of adequate statistical power.

## Retiring the exploratory v4.x association

The previously reported exploratory v4.x association and its interpretation are withdrawn as scientific evidence. The earlier workflow had full-run preprocessing leakage, simplistic label assumptions, and invalid or compound control comparisons. It must not guide cohort selection, model tuning, or a regularization claim. It may be retained only as transparent analysis history.

The v5.2 Phase 0 protocol is not a blind preregistration because exploratory v4.x outputs had already been inspected. It was frozen before the corrected v5.2 empirical analysis. This distinction must remain visible in any report.

## Current evidence boundary

The five reviewed v5.2 modules and their 84 synthetic checks establish selected software contracts on generated fixtures only. They do not establish correct real-event identity, physical sensor equivalence, archive completeness, uncertainty semantics, time alignment, empirical (Q) values, or model utility on the Zenodo dataset.

A real-data run remains blocked until a human-reviewed event registry, exact archive-member paths, source checksums, time basis and signed offsets, channel/unit mapping, interpolation-flag provenance, uncertainty semantics, and window-quality audit have been approved. In particular, the earlier v3.1 diagnostic recorded an unresolved conflict between the simulator pressure-column `/Pa` label and mbar-like numerical values; the v5.2 Pa-to-mbar conversion must not be treated as verified until that source/export discrepancy is resolved.

The current Orchestrator produces event-level results and group-level descriptive summaries. It does not yet calculate the complete prespecified group-level inferential analysis (Spearman statistic, group-aware interval/permutation inference, or design-sensitivity analysis). Those statistical outputs must be implemented and independently tested before a confirmatory association claim.

## Protocol references

The controlling decisions are in [DECISIONS.md](DECISIONS.md). The staged execution plan is in [RESEARCH_ROADMAP_v2.md](RESEARCH_ROADMAP_v2.md), and the repository-level summary is in [the Phase 0 protocol summary](../phase0-protocol-summary.md).

## Core scientific references

- Arweiler et al. (2026), *Batch Distillation Data for Developing Machine Learning Anomaly Detection Methods*, Scientific Data 13, 513. <https://doi.org/10.1038/s41597-026-07124-3>
- Werner et al. (2026), *Automated Batch Distillation Process Simulation for a Large Hybrid Dataset for Deep Anomaly Detection*, Computers & Chemical Engineering, 109827. <https://doi.org/10.1016/j.compchemeng.2026.109827>
- Gonçalves et al. (2024), *Evaluation is key: a survey on evaluation measures for synthetic time series*, Journal of Big Data. <https://doi.org/10.1186/s40537-024-00924-7>
- scikit-learn, [common pitfalls and data leakage](https://scikit-learn.org/stable/common_pitfalls).
- scikit-learn, [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html).
- scikit-learn, [average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html).
- Tobin et al. (2017), *Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World*. <https://doi.org/10.1109/IROS.2017.8202133>
