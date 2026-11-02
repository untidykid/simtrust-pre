# H701 / OP028 Feasibility Decision Addendum

**Decision date:** 2026-10-31  
**Scope:** The inspected H701 heat-duty candidate cohort and the pressure/temperature operationalisations reviewed at that time.  
**Decision:** No-go for the primary SimTrust-Pre utility experiment on the current H701 cohort; proceed with a bounded feasibility report.

This addendum supplements `docs/locked-results.md`. It does not replace the locked v3.1 results or establish that the simulator or the complete Zenodo dataset is generally unsuitable for simulation-to-real research.

## Pressure route

For five H701 candidate runs whose selected simulation members covered the mapped event intervals, the inspected stage-12 pressure trace was constant over the examined pre-event and event intervals. The reported pre-event means were 300, 350, 450, 500, and 500 mbar. OP028 is **not evaluable**, not a sixth invariant trace: its selected simulation member spans 39,875–52,775 seconds, while the mapped YAML event interval is 56,700–56,970 seconds, with zero overlap.

The decision is limited to the inspected stage-12 output and current H701 mappings. It does not identify a physical mechanism that held pressure constant. Constant simulated pressure during the fault does not by itself establish that the pre-onset discrepancy `q` is zero, constant, or unavailable; `q` requires paired, aligned real and simulated pre-onset data and valid uncertainty values.

## Temperature route

The temperature diagnostic returned data for five candidate events. Under the preliminary screening heuristic

`during_range > max(2.0 °C, 5 × pre-event standard deviation)`,

only OP003 (2.70 °C) and OP009 (2.24 °C) crossed the threshold. OP004 (0.14 °C), OP001TA009 (0.02 °C), and OP001TA011 (0.46 °C) did not. OP001TA011 was below the 300-second duration screen; OP028 returned zero rows in the selected member.

This threshold is an exploratory screening heuristic, not a validated physical-response criterion or calibrated noise threshold. OP003 and OP009 remain exploratory leads only; range crossings do not establish causal attribution, timing coherence, or real/simulation sensor equivalence.

## Event and group accounting

The six preliminary H701 event records span five chemical-system/operating-point groups. Do not report six event records as six independent groups. The current cause classifications and XML associations are rule-based audit outputs, not independently verified ground truth.

## Decision boundary

The selected path was a bounded feasibility report documenting the current dataset–simulator–signal pairing limits and why the primary H701 experiment was not run. Do not generalize the result to every perturbation family, every possible archive member, or all SimTrust-Pre designs.
