# SimTrust-Pre v5.2 Merge Record

**Record date:** 2026-11-02  
**Pull request:** [#1 — Review SimTrust-Pre v5.2 package and v3.1 recovery provenance](https://github.com/untidykid/simtrust-pre/pull/1)  
**Merge commit:** `e6a75c5aaa78a08ecc29d72efc780127c126f39c`  
**Merged head:** `f0873481ce60484c05cba494d3a496a2ec719d39`  
**Target branch:** `main`  
**Merge method:** merge commit

## What the merge adds

- Five reviewed v5.2 Python modules under `src/`.
- 84 labelled synthetic smoke checks across the five modules: 9 + 14 + 23 + 18 + 20.
- Eight verifier unit tests and five v5.2 smoke-wrapper tests, for 13 unittest tests in total.
- The v5.2 Phase 0 protocol bundle, scientific rationale, roadmap, source inventory, and matched-baseline decision addendum.
- A separately archived v4.2 notebook, explicitly marked as unexecuted source rather than a validated analysis artifact.
- Recovery documentation and machine-readable metadata for the v3.1 evidence files, preserving the original historical fingerprints and distinguishing reported recovered/rebuilt copies from original committed evidence.

## Verification

GitHub Actions run [41518313759](https://github.com/untidykid/simtrust-pre/actions/runs/41518313759) completed successfully for merged PR head `f0873481ce60484c05cba494d3a496a2ec719d39`.

The run completed:
- Python dependency installation and source compilation.
- All 13 unittest tests.
- The 84 labelled synthetic smoke checks.
- Module 5 matched-baseline assertions for the paired, wrong-run, and real-donor controls across all 20 seeds.

The four-file v3.1 checksum gate was skipped with the configured notice because the four original CSV payloads were absent from `evidence/`. This skip is not a checksum pass.

## What this merge does not claim or change

- It does not add or restore any of the four original v3.1 evidence CSV payloads.
- It does not modify `scripts/verify_evidence.py` or the four historical expected size/MD5 pairs; the evidence verifier continues to check the original files only.
- It does not treat the 371-row Crosswalk approximation or the 25-row P701/P702 rebuild as byte-identical originals.
- It does not change the locked v3.1 scientific conclusions.
- It does not execute the v5.2 pipeline on the real Zenodo dataset or establish an empirical result.
- It does not complete the pending group-level Spearman, group-aware uncertainty/permutation, or design-sensitivity analyses.
- It does not create a release or Git tag.

The repository therefore has a reviewed and synthetic-test-validated v5.2 source package, but it is not a byte-for-byte reproducible release of the v3.1 evidence artifacts and does not yet contain a real-data v5.2 result.

## Recovery-log scope clarification

The sentence in `RECOVERY_LOG.md` stating that the recovery documentation change did not modify the verifier or CI workflow refers only to the recovery-documentation change relative to its recorded baseline commit. The complete PR #1 also included separate v5.2 source-package commits that changed `.github/workflows/tests.yml` to install the pinned v5.2 dependencies, compile the `src/` package, and run the synthetic smoke-test wrapper. Those workflow changes did not modify the historical v3.1 fingerprints, the verifier's expected original-file hashes, or the availability of the original evidence CSVs.
