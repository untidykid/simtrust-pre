# SimTrust-Pre v5.2 Reviewed Research Pipeline

## Status and scope

This directory documents a reviewed software implementation for the v5.2 research protocol. It is deliberately separate from the locked v3.1 evidence cycle documented in `docs/locked-results.md`.

The v5.2 modules have synthetic-only smoke tests. Passing those tests verifies selected software contracts on generated fixtures; it does **not** establish that the real Zenodo archives have been processed, that any event pairing or channel mapping is correct, or that the research hypothesis is supported by empirical results.

No real-data v5.2 result is claimed by this source release. The primary real-data run remains gated by a human-reviewed event registry and verified archive paths, units, uncertainty semantics, and time mappings.

## Module map

| Source file | Responsibility | Embedded synthetic smoke tests |
|---|---|---:|
| `src/SimTrust_Pre_v5_2_Module1_reviewed.py` | Fault-only window construction, deterministic sampling, and class/experiment weight constraints | 9 |
| `src/SimTrust_Pre_v5_2_Module2_reviewed.py` | Train-only preprocessing, paired fault-segment utility, and control-arm checks | 14 |
| `src/SimTrust_Pre_v5_2_Module3_reviewed.py` | Reviewed real/simulation loading, interpolation provenance, time alignment, and 300-second pre-onset `q` | 23 |
| `src/SimTrust_Pre_v5_2_Module4_1_Reviewed.py` | Real Operation-phase window construction and label/quality gates | 18 |
| `src/SimTrust_Pre_v5_2_Module5_reviewed.py` | End-to-end orchestration of reviewed events, `q`, paired utility, and controls, including a donor-matched paired reference arm | 20 |

The five suites contain **84 labelled synthetic smoke checks** in total; Module 5 also contains assertions that verify donor-control baseline parity. These checks use generated fixtures only. Module 5 reports group-level descriptive medians, but it does **not** yet calculate the prespecified group-level Spearman statistic, group-aware uncertainty/permutation inference, or design-sensitivity analysis. Module 5 imports Modules 1–4.1 by their original module names; keep the source files together under `src/`.

## Environment and tests

The tested dependency set is recorded in `requirements-v5.2.txt` at the repository root. From the repository root:

```bash
python -m pip install -r requirements-v5.2.txt
python -m compileall -q src tests scripts
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs the same compile and unit-test commands. The v5.2 test methods use synthetic arrays and temporary ZIP fixtures only; they do not access the Zenodo service or open the project's real archives.

## Protocol reference

See the [full Phase 0 decision record](phase0/DECISIONS.md), [English scientific rationale](phase0/RATIONALE.md), [2026-11-02 matched-baseline decision addendum](phase0/DECISION_ADDENDUM_2026-11-02.md), [Research Roadmap v2.0](phase0/RESEARCH_ROADMAP_v2.md), and [Phase 0 packet README](phase0/README.md), as well as the [concise protocol summary](phase0-protocol-summary.md). The source packet was frozen on 2026-10-30 for the corrected v5.2 analysis; it explicitly acknowledges that earlier exploratory v4.x outputs had already been inspected. It is not a blind preregistration.

## Important boundaries

- The v5.2 implementation does not rebuild any of the four frozen v3.1 CSV artifacts.
- It does not recover the missing original v2.2.5 Crosswalk, the original HV feasibility CSV, or the original P701/P702 CSV.
- A synthetic test pass is not an empirical validation result.
- The six-accepted-event execution gate is a software/feasibility safeguard, not a statistical-power or inferential-sufficiency claim.
- The current Orchestrator produces event-level outputs and group-level descriptive summaries only; confirmatory association claims remain blocked until group-level Spearman, uncertainty/permutation, and design-sensitivity procedures are implemented and tested.
- Resolve the earlier simulator pressure export `/Pa` versus mbar-like numerical-scale discrepancy against the original CSV definitions/export path before treating the v5.2 Pa-to-mbar physical comparison as empirically validated.
- A real-data result must retain the reviewed registry, source archive checksums, selected member paths, exclusions, run manifests, seeds, and per-run/per-seed outputs.
- Do not change the frozen v3.1 cohort, thresholds, or interpretations as part of v5.2 work.
