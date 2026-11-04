# Public Release Readiness Audit

**Audit date:** 2026-11-03  
**Repository:** `untidykid/simtrust-pre`  
**Branch reviewed:** `main`  
**Main commit reviewed:** `cf8f6b92cd868a224a5bb7d5fe8d94ca562c1050`  
**Decision:** suitable for a carefully labelled public research-software snapshot after owner-controlled visibility and licensing decisions; **not** a complete reproducible release of the v3.1 evidence and **not** ready to support confirmatory v5.2 empirical claims.

## Executive decision

The repository contains useful, carefully qualified scientific audit records and a separate v5.2 software implementation. Its documentation generally makes the critical distinction between historical v3.1 findings, reported recovery, synthetic software tests, and future real-data analysis.

The repository must not be described as a fully reproducible v3.1 data release. The four original v3.1 evidence CSVs are absent, the exact extraction code for the locked tables is not included, and the retained figures/counts have not been independently regenerated from source archives in this repository. The v5.2 implementation has only synthetic-fixture test evidence and has not been run against the real Zenodo dataset here.

At the time of this audit, GitHub reports the repository visibility as **Private**. This audit does not change repository visibility.

## Verified GitHub state

- PR #1 was merged into `main` as `e6a75c5aaa78a08ecc29d72efc780127c126f39c`.
- PR #2 was merged into `main` as `cf8f6b92cd868a224a5bb7d5fe8d94ca562c1050`.
- GitHub Actions run [41518313759](https://github.com/untidykid/simtrust-pre/actions/runs/41518313759) completed successfully for PR #1 head `f0873481ce60484c05cba494d3a496a2ec719d39`.
- The run used Python 3.12 and completed dependency installation, compilation, all 13 then-existing unittest tests, and the 84 synthetic smoke checks.
- The evidence-verification step reported all four original CSVs missing and explicitly emitted a notice that checksum verification was skipped. This is **not** a successful evidence checksum verification.
- The successful run above was on PR #1's head. It is not evidence that the current post-PR #2 main commit or this audit branch has passed CI; the current pull request must run independently.

## Security and repository-hygiene checks (2026-11-03 follow-up)

- A targeted heuristic scan was run against all **29 tracked blobs on the current `main` tree**, plus all **4 files changed by PR #3**. The scan looked for common private-key headers, common GitHub token formats, AWS access-key IDs, credential-like assignments, email addresses, Persian/Arabic Unicode ranges, and common user-home absolute paths. No matches were found in the scanned current-tree/PR content.
- Targeted GitHub code-search probes for common token/credential indicators returned no indexed matches. Search indexing and pattern coverage are incomplete; this is corroborating evidence only, not a guarantee.
- The `main` ancestry currently contains **72 commits**. Commit metadata reviewed from the returned history uses the repository owner's GitHub noreply address; this does not establish that every historical blob is free of secrets or private data.
- **A complete historical secret scan has not been completed.** The GitHub connection does not expose the repository's secret-scanning/secret-alert administration endpoints, and this review did not download and inspect every historical tree/blob across all refs. Do not describe this as a clean full-history security audit.
- The four listed branch refs (`main` and three working branches) currently report `protected: false`. A branch-protection read was denied by the integration, so required checks/ruleset settings could not be fully inspected. Before a public collaboration workflow, configure protection for `main` and require passing CI/review as appropriate.
- PR #3 workflow run [41681399095](https://github.com/untidykid/simtrust-pre/actions/runs/41681399095) completed successfully: Python compilation passed, **14 unit tests passed**, and all five synthetic smoke suites passed (84 labelled checks as documented by the suite). The four original v3.1 CSVs were absent, so the evidence checksum step was skipped. This remains a software-test result, not evidence verification.

## What is useful and should remain in the project

| Component | Value | Correct publication treatment |
|---|---|---|
| Locked v3.1 findings | A bounded negative/inconclusive audit, including the H701 non-verification result and P701/P702 feasibility demonstration | Publish with the existing limitations; do not turn feasibility into validation |
| Archive Crosswalk counts and classifications | Useful metadata/provenance audit with explicit distinctions between raw records, parent keys, experiments, and physical events | Publish as recorded audit findings, not as a regenerated dataset |
| Feasibility Map | Useful screening of five perturbation families and explicit non-feasibility boundaries | Preserve the bounded scope; do not generalize beyond inspected evidence |
| Recovery log and manifest | Valuable provenance record distinguishing original, reported-exact, approximate, unavailable, and rebuilt artifacts | Keep; do not substitute approximate/rebuilt files for originals |
| v5.2 Modules 1–5 | Useful research-software implementation of sampling, weighting, preprocessing, q calculation, window construction, orchestration, and controls | Publish as a synthetic-tested software prototype, not as empirically validated software |
| v4.2 archived notebook | Potential historical source material | Keep explicitly labelled unexecuted/archive-only; do not present it as a reproducible analysis |

The 371-row v2.1 crosswalk is not the original 254-parent-key v2.2.5 artifact. The 25-row P701/P702 rebuild is not byte-identical to the original. Artifact 3 remains unavailable. Artifact 1's matching historical fingerprint is a reported recovery result; its bytes are not present in this repository and were not independently re-hashed by this audit.

## Technical review findings

### Corrected in this audit branch

1. **Boolean flag parsing:** Module 4.1 accepted the string tokens `"1.0"` and `"0.0"`, while Module 3 did not. Module 3 now accepts the same decimal-string spellings. A focused unit test checks true, false, and unknown handling. Numeric 1/0 parsing and nullable unknown handling remain intact.

2. **README accuracy and clarity:** the incomplete sentence describing the expected H701/PY23 physical direction has been repaired. The generic Python 3.10+ statement has been narrowed to Python 3.12, the version actually exercised by the checked-in workflow. The README now links to this audit.

### Deliberately not changed

1. **Window edge-gap semantics:** Module 1 calculates the right-edge gap as `window_end - last_sample_timestamp`; Module 4.1 calculates it as `window_end - (last_sample_timestamp + nominal_dt)`. The latter treats each sample as covering an inferred interval, while the former treats timestamps as sample instants. The protocol needs an explicit timestamp/support-interval convention before either implementation is changed. Do not silently harmonize these expressions. Resolve this before any real-data v5.2 run.

2. **Donor matching strictness:** Module 5 currently requires a donor from the exact chemical-system × operating-point group and, when the target has a reviewed perturbation family, an exact family match. The Phase 0 decision text describes a broader fallback to the closest eligible operating point. The implementation is therefore more restrictive than the written donor-selection rule and may yield missing controls. This audit does not loosen the code: define a deterministic operating-point distance, tie-breaking rule, and pre-outcome decision before changing donor selection. Until then, report the implementation's stricter rule and donor-control gaps.

3. **Group-level inference:** Module 5 produces event-level results and group-level descriptive summaries, but the protocol's primary group-level Spearman association and the planned group-aware permutation/uncertainty and design-sensitivity analyses are not implemented. The complete secondary-family Benjamini–Hochberg procedure is also pending. These are required before making confirmatory association claims; the six-event execution gate is not a power calculation.

4. **Pressure mapping and units:** the v3.1 record retains a conflict between the simulator export's `/Pa` label and mbar-like reported numerical values. The original raw simulation export and exact conversion path are not included. The v5.2 primary conversion of Pa to mbar must not be treated as empirically verified until the source/export definitions and mapping are independently checked.

5. **Real-data execution:** no v5.2 empirical result is established by the synthetic tests. A real-data run still requires a reviewed event registry, verified archive-member identities, time bases and signed offsets, physical channel mapping, units, uncertainty semantics, interpolation provenance, and the frozen quality gates.

## Evidence availability

| v3.1 artifact | Historical status | Present in GitHub? | Permitted interpretation |
|---|---|---:|---|
| Artifact 1 — H701 cohort | Reported `EXACT` fingerprint recovery | No | Reported match only; not independently verified from committed bytes |
| Artifact 2 — Crosswalk v2.2.5 | Original unavailable; v2.1 approximation has 371 rows | No | Approximation is not the original 254-parent-key artifact |
| Artifact 3 — HV feasibility | `UNAVAILABLE` | No | Do not claim reconstruction |
| Artifact 4 — P701/P702 | 25-row `REBUILT_NOT_BYTE_IDENTICAL` file | No | Rebuild is not the original artifact |

The verifier correctly retains the historical original-file fingerprints and does not accept approximate or rebuilt files as originals. Keep this behavior.

## Public-release gates

### Required before changing visibility

- [x] Run a targeted heuristic scan across all 29 current `main` blobs and all 4 PR #3 changed files; no matches were found for the listed common secret/private-data patterns. **A complete historical secret scan remains open** because every historical tree/blob across all refs was not inspected and the integration does not expose GitHub secret-scanning administration.
- [x] Scan all 29 current `main` blobs and all 4 PR #3 changed files for Persian/Arabic Unicode characters; no matches were found. This does not certify uninspected historical snapshots or future additions.
- [ ] Decide the repository's own license. There is no `LICENSE` file. The upstream dataset's stated CC BY 4.0 terms do not automatically license this repository's original code, documentation, or derived tables. Do not add a license without the owner's explicit choice and confirmation of rights.
- [ ] Add accurate citation metadata (`CITATION.cff`) after confirming the preferred author/citation identity and versioning details. Do not invent an author name or DOI for this repository.
- [ ] Owner must change the repository visibility from Private to Public in GitHub repository settings. The available GitHub connection used for this audit can inspect and edit repository contents but does not expose a repository-visibility mutation.

### Required before a complete reproducible v3.1 data release

- [ ] Recover and independently verify all four original evidence CSVs against their historical size and MD5 values.
- [ ] Include the exact source archives and extraction/build code, or provide durable, versioned access to them with clear provenance and licensing.
- [ ] Re-run the frozen extraction from the pinned source data and independently reproduce the locked tables without changing the v3.1 cohort or criteria.

### Required before confirmatory v5.2 empirical claims

- [ ] Resolve the sample-instant versus sample-support interval convention and align Module 1/Module 4.1 edge-gap calculations.
- [ ] Reconcile the donor matching rule with the frozen Phase 0 protocol before outcomes are inspected.
- [ ] Implement and test group-level Spearman, group-aware uncertainty/permutation inference, the full secondary-family BH correction, and group-count-aware design sensitivity.
- [ ] Verify pressure channel identity, units, export conversion, uncertainty meaning, and time alignment from the original source files.
- [ ] Execute the frozen pipeline on the real dataset with a complete review registry and preserve all rejection/provenance outputs.

## Publication recommendation

The defensible near-term publication target is a **public research-software and audit-record repository**, clearly labelled as a synthetic-tested prototype plus a bounded historical audit. It must not be advertised as a complete reproducible v3.1 release, a validated simulator, or a completed confirmatory v5.2 study.

A public repository without a license is viewable but does not grant the public permission to reuse the code. If the intention is open-source publication, choose and add an appropriate license before describing the project as open source.
