# Public Release Readiness Audit

**Audit date:** 2026-11-06  
**Repository:** `untidykid/simtrust-pre`  
**Main commit reviewed:** `58b987a9d4e500b6f45600b9c8ffaec603971d41`  
**Review branch:** `public-release-refresh-2026-11-06`  
**Decision:** content is suitable for a carefully labelled public research-software and audit-record snapshot after the owner completes account-level visibility and security settings and confirms licensing rights; **not** a complete reproducible release of the v3.1 evidence and **not** ready to support confirmatory v5.2 empirical claims.

## Executive decision

The repository contains useful, carefully qualified scientific audit records and a separate v5.2 software implementation. Its documentation generally makes the critical distinction between historical v3.1 findings, reported recovery, synthetic software tests, and future real-data analysis.

The repository must not be described as a fully reproducible v3.1 data release. The four original v3.1 evidence CSVs are absent, the exact extraction code for the locked tables is not included, and the retained figures/counts have not been independently regenerated from source archives in this repository. The v5.2 implementation has only synthetic-fixture test evidence and has not been run against the real Zenodo dataset here.

GitHub currently reports the repository visibility as **Private**. The available GitHub connector can edit repository contents and pull requests but does not expose the repository-visibility settings mutation; the owner must change this setting in GitHub.

## Verified GitHub state

- PR #1 was merged into `main` as `e6a75c5aaa78a08ecc29d72efc780127c126f39c`.
- PR #2 was merged into `main` as `cf8f6b92cd868a224a5bb7d5fe8d94ca562c1050`.
- GitHub Actions run [41518313759](https://github.com/untidykid/simtrust-pre/actions/runs/41518313759) completed successfully for PR #1 head `f0873481ce60484c05cba494d3a496a2ec719d39`.
- The run used Python 3.12 and completed dependency installation, compilation, all 13 then-existing unittest tests, and the 84 synthetic smoke checks.
- The evidence-verification step reported all four original CSVs missing and explicitly emitted a notice that checksum verification was skipped. This is **not** a successful evidence checksum verification.
- The successful run above was on PR #1's head and is historical context only. PR #3 has since run independently; see the 2026-11-03 follow-up verification below.

## Security and repository-hygiene checks (2026-11-04)

- The current `main` tree contains **35 tracked files**, including the English `CONTRIBUTING.md` and `.github/dependabot.yml` added in PR #4.
- The main ancestry contains **74 commits / 72 unique tree snapshots** as of the reviewed main commit. The earlier PR #3 historical scan covered 103 unique tracked text-blob versions: 87 from the then-current main ancestry and 16 additional blobs introduced in PR #3. The current PR #4 adds **9 additional unique blob versions** beyond main. In total, **112 unique tracked text-blob versions** across the reviewed main/PR history have been scanned.
- The current-content review covers all 35 files in the merged main tree. Previously scanned unchanged blobs are counted in the historical review; all nine distinct PR #4 blob versions beyond the pre-PR #4 main tree were separately fetched and rescanned.
- Heuristic patterns covered common private-key headers, GitHub personal-access-token formats, AWS access-key IDs, Slack and GitLab token formats, Google API-key formats, JWT-like strings, credential-like assignments, email addresses, common user-home absolute paths, and Persian/Arabic Unicode ranges. **No matches were found** in the scanned tracked blobs.
- All **59 GitHub Actions job logs** recorded through the PR #4 main workflow runs as of this audit update were scanned with the targeted private-key, GitHub/AWS/Slack/GitLab/Google token, JWT-like, credential-assignment, and email patterns. No matches were found. This is a pattern-based scan, not a guarantee that every possible secret or personal-data format was detected.
- These scans do not replace GitHub Secret Scanning or push protection. The repository's security administration endpoints are not accessible through the current connector, so the status of secret scanning and push protection could not be independently inspected. External artifacts and content outside scanned Git refs and logs are not covered.
- The PR #4 changes add preventive `.gitignore` rules for `.env`, `.env.*` (while allowing `.env.example`), common private-key/certificate extensions, SSH private-key filenames, and common local credential files. These rules prevent accidental future adds when files are untracked; they do not remove or protect secrets already committed.
- GitHub currently lists **five branches**, and all five report `protected: false`. The branch-protection/ruleset read is unavailable for this private repository under its current GitHub plan. Before accepting outside contributions, enable protection for `main` and require the CI check.
- The CI workflow now uses the pinned `ubuntu-24.04` runner label, immutable full commit SHAs for `actions/checkout` and `actions/setup-python`, `contents: read` permissions, a 15-minute timeout, and `persist-credentials: false` for checkout.
- Dependabot is configured for weekly Python dependency and GitHub Actions updates. It proposes updates through pull requests; updates must still be reviewed and tested.
- PR #3 was squash-merged as `893622b3ff02deec7c383fac41a27630a1f7e7cf`. Its post-merge `main` workflow [41755565717](https://github.com/untidykid/simtrust-pre/actions/runs/41755565717) passed on that exact commit using the previous pinned dependency set.
- The updated dependency set (NumPy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1 plus pinned runtime dependencies) passed dependency installation, `pip check`, Python compilation, **14 unit tests**, and all five synthetic smoke suites in [run 41758359755](https://github.com/untidykid/simtrust-pre/actions/runs/41758359755).
- The subsequent PR #4 review/documentation revisions passed on the then-current head `86ae47f517fcc868ab35158aa394abef723b9b19` in [run 41758710161](https://github.com/untidykid/simtrust-pre/actions/runs/41758710161): dependency installation, `pip check`, compilation, 14 unit tests, and all five synthetic smoke suites. This run also explicitly skipped the four original evidence CSV checksums.
- On the current dependency set, CI installed NumPy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, and exact versions for the listed runtime dependencies. `pip check` reported no broken requirements. The tests were still synthetic-only.
- The current `main` commit `58b987a9d4e500b6f45600b9c8ffaec603971d41` passed the main push workflow in [run 41759087595](https://github.com/untidykid/simtrust-pre/actions/runs/41759087595): `pip check`, compilation, **14 unit tests**, and all five synthetic smoke suites passed.
- The two Dependabot runs on the same main commit [41759102039](https://github.com/untidykid/simtrust-pre/actions/runs/41759102039) and [41759102454](https://github.com/untidykid/simtrust-pre/actions/runs/41759102454) completed successfully; their logs contained only routine dependency-update checks.
- In every workflow run, the four original v3.1 CSVs were absent, so the evidence checksum step explicitly skipped verification. This is not a checksum pass or a reproduction of the locked evidence.

## Dependency maintenance review (2026-11-04)

- The previous `scikit-learn==1.8.0` pin was outside the versions currently supported by the project's security policy. The policy marks 1.9.1 as supported; the repository now pins `scikit-learn==1.9.1`. See the [scikit-learn security policy](https://github.com/scikit-learn/scikit-learn/blob/main/SECURITY.md) and [1.9.1 release notes](https://github.com/scikit-learn/scikit-learn/blob/main/doc/whats_new/v1.9.rst).
- NumPy is pinned to `2.5.4` and pandas was pinned to `3.1.0` on main. pandas `3.1.1`, released on 2026-11-04, is the newer patch release and is proposed in this refresh PR; pandas recommends that users of the 3.1.x series upgrade to it. All direct scientific packages and the runtime dependencies observed in CI are now exact-version pinned in `requirements-v5.2.txt`.
- The main dependency set was installed successfully under Python 3.12 on the `ubuntu-24.04` runner. `pip check` reported no broken requirements; Python compilation, all **14 unit tests**, and all five synthetic smoke suites passed on the PR #4 head. See [run 41758359755](https://github.com/untidykid/simtrust-pre/actions/runs/41758359755). The refresh PR additionally adds an isolated vulnerability scan using `pip-audit==2.10.1` and upgrades pandas to `3.1.1`; those changes are not treated as verified until their own PR CI completes.
- These exact version pins improve repeatability but do not constitute a hash-locked supply-chain build. The requirements file does not include wheel/source distribution hashes, and no full vulnerability audit of every dependency or transitive package is claimed. Dependabot is enabled to propose weekly updates, which require review and CI before merging.
- Passing the updated synthetic test suite establishes only the tested software contracts on synthetic inputs. It does not establish unchanged real-data output, physical validity, or reproducibility of the v3.1 scientific evidence.

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

### Corrected and merged on main

1. **Boolean flag parsing:** Module 4.1 accepted the string tokens `"1.0"` and `"0.0"`, while Module 3 did not. Module 3 now accepts the same decimal-string spellings. A focused unit test checks true, false, and unknown handling. Numeric 1/0 parsing and nullable unknown handling remain intact.

2. **README accuracy and clarity:** the incomplete sentence describing the expected H701/PY23 physical direction has been repaired. The generic Python 3.10+ statement has been narrowed to Python 3.12, the version actually exercised by the checked-in workflow. The README links to the audit and the English contribution guide.

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

- [x] Scan all 35 current PR #4 tracked files and all 112 unique tracked text-blob versions across the reviewed main/PR history for common secret/private-data patterns; no matches were found. The scan is heuristic and does not replace GitHub Secret Scanning.
- [x] Scan the 112 reviewed historical tracked text-blob versions and the current PR #4 tree for Persian/Arabic Unicode characters; no matches were found. This does not certify untracked material, external assets, or future additions.
- [x] Scan all 56 recorded GitHub Actions workflow logs for common private-key/token/credential/email patterns; no matches were found.
- [x] Add `.gitignore` protections for common local environment, credential, and private certificate/key files.
- [x] Harden CI permissions and checkout credential persistence; pin Actions by immutable commit SHA and add `pip check`.
- [x] Add weekly Dependabot updates for pip and GitHub Actions.
- [x] Pin direct and observed runtime dependencies and pass CI on NumPy 2.5.4 / pandas 3.1.0 / scikit-learn 1.9.1. This improves version repeatability; package hashes and a complete software-supply-chain audit remain out of scope.
- [ ] Validate the proposed pandas 3.1.1 patch upgrade and isolated `pip-audit==2.10.1` scan on the refresh PR before merge.
- [x] Add a scoped MIT license for original project software/code configuration in `src/`, `scripts/`, `tests/`, `.github/workflows/`, `requirements-v5.2.txt`, `.gitignore`, and `notebooks/`.
- [x] Add a separate CC BY 4.0 notice for project-authored documentation and audit materials in `README.md`, `RECOVERY_LOG.md`, `CONTRIBUTING.md`, `docs/`, `evidence/`, and notebook README files. Third-party and upstream dataset materials retain their own terms.
- [x] Add machine-readable citation metadata in `CITATION.cff`. The author is currently represented by the GitHub handle `untidykid`; the owner can substitute a preferred scholarly name and add an ORCID/DOI if appropriate. No DOI was invented.
- [x] Add the English `CONTRIBUTING.md` guide covering setup, scientific boundaries, data provenance, and contribution expectations.
- [ ] Owner must change the repository visibility from Private to Public in GitHub repository settings. The available GitHub connection used for this audit can inspect and edit repository contents but does not expose a repository-visibility mutation.
- [ ] After changing the repository to Public, enable `main` branch protection / rulesets and require the CI workflow. All five branches are currently unprotected; private-repository rulesets are unavailable under the current GitHub plan.
- [ ] After changing the repository to Public, verify GitHub Secret Scanning is active and enable push protection in repository security settings. The connector cannot inspect or mutate these account-level settings.
- [ ] Owner should confirm that all material covered by the MIT and CC BY 4.0 notices is owned or authorized for licensing. Replace the GitHub handle in `CITATION.cff` with a preferred scholarly author name/ORCID when desired; no DOI should be invented.

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

The defensible near-term publication target is a **public research-software and audit-record repository**, clearly labelled as a synthetic-tested prototype plus a bounded historical audit. Its current contents and CI are ready for that limited kind of public release once the owner-controlled visibility and security settings are completed. It must not be advertised as a complete reproducible v3.1 data release, a validated simulator, or a completed confirmatory v5.2 study.

The repository declares separate reuse terms for original software and project-authored documentation/audit materials. The new English `CONTRIBUTING.md` describes the scientific boundaries, reproduction commands, and contribution rules. These terms do not cover third-party material, upstream archives, or content the project does not have the right to license.
