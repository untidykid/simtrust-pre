# Public Release Readiness Audit

**Audit date:** 2026-11-03  
**Repository:** `untidykid/simtrust-pre`  
**Branch reviewed:** `main`  
**Main commit reviewed:** `cf8f6b92cd868a224a5bb7d5fe8d94ca562c1050`  
**Decision:** suitable for a carefully labelled public research-software and audit-record snapshot after completion of the remaining historical-security and owner-controlled visibility gates; **not** a complete reproducible release of the v3.1 evidence and **not** ready to support confirmatory v5.2 empirical claims.

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
- The successful run above was on PR #1's head and is historical context only. PR #3 has since run independently; see the 2026-11-03 follow-up verification below.

## Security and repository-hygiene checks (2026-11-04 follow-up)

- The PR #3 review branch contained **33 tracked files**; the current `main` tree and PR #4 review branch also contain **33 tracked files**. All 33 files in the final PR #4 tree are included in the current-content scan, including the archived notebook and the final audit document.
- The historical scan performed for PR #3 covered **103 unique tracked text-blob versions**: 87 versions across the then-current 72-commit main ancestry / 70 unique tree snapshots, plus 16 additional versions across the 17 PR #3 commits. PR #3 was subsequently squash-merged; `main` now contains **73 commits / 71 unique tree snapshots**. PR #4 adds two audit-document revisions beyond that baseline; these PR #4-specific versions were reviewed separately.
- The current branch listing contains **five refs** (`main`, `docs/merge-v5-2-audit-note-2026-11-02`, `reproducible-v5-2-source-package-2026-11-02`, `pre-publication-audit-fixes-2026-11-03`, and `post-merge-ci-record-2026-11-04`). GitHub currently reports **all five as unprotected**. This replaces the earlier four-branch snapshot recorded during the PR #3 review.
- Heuristic patterns covered common private-key headers, GitHub personal-access-token formats, AWS access-key IDs, Slack and GitLab token formats, Google API-key formats, JWT-like strings, credential-like assignments, email addresses, common user-home absolute paths, and Persian/Arabic Unicode ranges. **No matches were found** in the scanned blobs.
- This is a thorough tracked-blob heuristic scan, not a guarantee that every possible secret format or personal-data pattern was detected. The GitHub integration does not expose the repository's secret-scanning administration endpoint; GitHub Secret Scanning and push-protection status were therefore not independently inspected. External release assets or content outside the scanned Git refs are not covered.
- The PR #4 review added preventive `.gitignore` rules for `.env.*` files (while allowing `.env.example`) and common private certificate/key containers (`*.pem`, `*.p12`, `*.pfx`). These rules prevent accidental future adds when they are untracked; they do not remove or protect secrets already committed.
- The four current branch refs (main and three working branches) report `protected: false`. The branch-protection read was denied by the integration, so required review/check policies could not be inspected. Configure protection for `main` before accepting outside contributions.
- All **47 GitHub Actions workflow-run logs** currently recorded for the repository were scanned with the same targeted private-key, GitHub/AWS/Slack/GitLab/Google token, JWT-like, credential-assignment, and email patterns. No matches were found. This is a pattern-based scan of these 47 runs only; it does not guarantee detection of every form of private data, nor cover future runs.
- GitHub Actions run [41753914447](https://github.com/untidykid/simtrust-pre/actions/runs/41753914447) passed on PR head `6664d0d7e639b5fe56a6ae2593863c313e67a9dc` after the supported scikit-learn pin update: dependency installation, Python compilation, **14 unit tests**, and all five synthetic smoke suites passed.
- The subsequent audit-document consolidation passed on final PR head `78f03a0c32d20eec0cfb9f87e0ce6679060921ec` in [run 41754725696](https://github.com/untidykid/simtrust-pre/actions/runs/41754725696), with the same 14-unit-test and five-smoke-suite outcome.
- After PR #3 was squash-merged as commit `893622b3ff02deec7c383fac41a27630a1f7e7cf`, the `main` push workflow passed on that exact merge commit in [run 41755565717](https://github.com/untidykid/simtrust-pre/actions/runs/41755565717): dependency installation, Python compilation, **14 unit tests**, and all five synthetic smoke suites succeeded.
- In each run, the four original v3.1 CSVs were absent, so the workflow explicitly skipped evidence checksum verification. This is not a checksum pass or a reproduction of the locked evidence.

## Dependency maintenance review (2026-11-04)

- The previous pin `scikit-learn==1.8.0` was outside the versions currently supported by the project's security policy; that policy marks only `1.9.1` as supported. The pin is updated to `1.9.1` in `requirements-v5.2.txt`. See the [scikit-learn security policy](https://github.com/scikit-learn/scikit-learn/blob/main/SECURITY.md), [1.9.1 release notes](https://github.com/scikit-learn/scikit-learn/blob/main/doc/whats_new/v1.9.rst), and [PyPI release metadata](https://pypi.org/project/scikit-learn/1.9.1/).
- The 1.9.1 release supports Python 3.12, and its documented minimum NumPy version is below the project's current NumPy pin. The CI run on this updated dependency set is the compatibility check for this branch; passing synthetic tests does not establish unchanged real-data outputs.
- `numpy==2.3.5` and `pandas==2.2.3` remain pinned for now to avoid combining an unrelated NumPy/pandas modernization with this low-risk pre-publication patch. Current releases are newer (NumPy 2.5.4 and pandas 3.1.0); schedule a separate, explicit compatibility review before changing these pins. See the [NumPy release list](https://numpy.org/news/) and [pandas version policy](https://pandas.pydata.org/docs/development/policies.html).
- No vulnerability-free claim is made for the complete dependency tree. Transitive dependencies and the newer NumPy/pandas candidates have not undergone a full advisory/compatibility audit in this pass.

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

- [x] Scan the 33-file current PR #4 tree and the 103 tracked text-blob versions from the PR #3 historical review for the listed common secret/private-data patterns; no matches were found. The two PR #4 audit-document revisions were also reviewed separately. The scan is heuristic and does not replace GitHub Secret Scanning.
- [x] Scan the 103 historical tracked text-blob versions and all current PR #4 files for Persian/Arabic Unicode characters; no matches were found. This does not certify untracked material, external assets, or future additions.
- [x] Add `.gitignore` protections for common local environment and private certificate/key files. These are preventive only.
- [x] Add a scoped MIT license for original project software/code configuration in `src/`, `scripts/`, `tests/`, `.github/workflows/`, `requirements-v5.2.txt`, `.gitignore`, and `notebooks/`.
- [x] Add a separate CC BY 4.0 notice for project-authored documentation and audit materials in `README.md`, `RECOVERY_LOG.md`, `docs/`, `evidence/`, and notebook README files. Third-party and upstream dataset materials retain their own terms.
- [x] Add machine-readable citation metadata in `CITATION.cff`. The author is currently represented by the GitHub handle `untidykid`; the owner can substitute a preferred scholarly name and add an ORCID/DOI if appropriate. No DOI was invented.
- [x] Update `scikit-learn` to the currently supported `1.9.1` release and pass CI on that dependency pin.
- [ ] Owner must change the repository visibility from Private to Public in GitHub repository settings. The available GitHub connection used for this audit can inspect and edit repository contents but does not expose a repository-visibility mutation.
- [ ] Enable appropriate protection for `main` before inviting outside contributions. Current branch refs report unprotected; the integration could not inspect required-check/review policies.

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

The repository now declares separate reuse terms for original software and project-authored documentation/audit materials. These terms do not cover third-party material, upstream archives, or content the project does not have the right to license.
