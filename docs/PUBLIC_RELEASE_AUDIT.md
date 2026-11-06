# Public Release Readiness Audit

**Audit date:** 2026-11-06  
**Repository:** `untidykid/simtrust-pre`  
**Base `main` commit reviewed:** `0dbe6e2fec84130b6357b26f922c664c4a8ed780`  
**Review branch:** `public-repository-state-audit-2026-11-06`  
**Decision:** the repository is **Public** as verified through GitHub repository metadata on 2026-11-06 and is suitable as a carefully labelled public research-software and historical audit-record snapshot. Remaining owner-controlled hardening and rights checks are listed below. It is **not** a complete reproducible release of the v3.1 evidence and is **not** ready to support confirmatory v5.2 empirical claims.

## Executive decision

The repository contains useful, carefully qualified scientific audit records and a separate v5.2 software implementation. Its documentation generally makes the critical distinction between historical v3.1 findings, reported recovery, synthetic software tests, and future real-data analysis.

The repository must not be described as a fully reproducible v3.1 data release. The four original v3.1 evidence CSVs are absent, the exact extraction code for the locked tables is not included, and the retained figures/counts have not been independently regenerated from source archives in this repository. The v5.2 implementation has only synthetic-fixture test evidence and has not been run against the real Zenodo dataset here.

GitHub repository metadata currently reports `visibility: public` (`private: false`). The repository is publicly accessible at https://github.com/untidykid/simtrust-pre. This is a verified current state, not an assumption based on a browser-rendered page.

## Verified GitHub state

- GitHub reports the repository as **Public**; the repository metadata response has `visibility: public` and `private: false`.
- Pull requests **#1 through #7 are all merged**; the repository currently has no open pull requests.
- The reviewed `main` commit is `0dbe6e2fec84130b6357b26f922c664c4a8ed780` (2026-11-06). Its GitHub commit object reports a valid verified signature.
- The latest `main` push workflow, [run 42296764020](https://github.com/untidykid/simtrust-pre/actions/runs/42296764020), completed successfully on that exact commit. It passed dependency installation, `pip check`, the isolated `pip-audit==2.10.1` check (**No known vulnerabilities found**), Python compilation, **14 unittest tests**, and all five synthetic smoke suites. The evidence step explicitly skipped checksums because all four original v3.1 CSVs remain absent; this is not an evidence verification pass.
- The GitHub Releases API currently returns no formal Release objects. The repository therefore has no published GitHub Release at the time of this audit.
- PR #1 was merged into `main` as `e6a75c5aaa78a08ecc29d72efc780127c126f39c`.
- PR #2 was merged into `main` as `cf8f6b92cd868a224a5bb7d5fe8d94ca562c1050`.
- GitHub Actions run [41518313759](https://github.com/untidykid/simtrust-pre/actions/runs/41518313759) completed successfully for PR #1 head `f0873481ce60484c05cba494d3a496a2ec719d39`.
- The run used Python 3.12 and completed dependency installation, compilation, all 13 then-existing unittest tests, and the 84 synthetic smoke checks.
- The evidence-verification step reported all four original CSVs missing and explicitly emitted a notice that checksum verification was skipped. This is **not** a successful evidence checksum verification.
- The successful run above was on PR #1's head and is historical context only. PR #3 has since run independently; see the 2026-11-03 follow-up verification below.

## Security and repository-hygiene checks (refreshed 2026-11-06)

- The current `main` tree contains **35 tracked files**, including the English `CONTRIBUTING.md` and `.github/dependabot.yml` added in PR #4.
- The main ancestry at the reviewed base contains **75 commits / 73 unique tree snapshots**. The earlier PR #3/#4 scans covered 112 unique tracked text-blob versions; PR #5 changed five additional tracked blobs. In total, **117 unique tracked text-blob versions** across the reviewed history and PR #5 have been scanned.
- The current-content review covers all 35 files in the merged main tree. Previously scanned unchanged blobs are counted in the historical review; all five distinct PR #5 blob versions were separately fetched and rescanned.
- Heuristic patterns covered common private-key headers, GitHub personal-access-token formats, AWS access-key IDs, Slack and GitLab token formats, Google API-key formats, JWT-like strings, credential-like assignments, email addresses, common user-home absolute paths, and Persian/Arabic Unicode ranges. **No matches were found** in the scanned tracked blobs.
- The refreshed version of this audit file on the final pre-publication branch was separately rescanned for the same patterns; no matches were found. This additional audit-file version is not included in the 117 historical blob-version total above.
- All **62 GitHub Actions job logs** recorded through the PR #5 branch and post-merge main verification were scanned with the targeted private-key, GitHub/AWS/Slack/GitLab/Google token, JWT-like, credential-assignment, and email patterns. No matches were found. This is a pattern-based scan, not a guarantee that every possible secret or personal-data format was detected.
- The PR #5 workflow log was additionally scanned for the same common secret/token/credential/email patterns; no matches were found.
- These scans do not replace GitHub Secret Scanning or push protection. The repository's security administration endpoints are not accessible through the current connector, so the status of secret scanning and push protection could not be independently inspected. External artifacts and content outside scanned Git refs and logs are not covered.
- The PR #4 changes add preventive `.gitignore` rules for `.env`, `.env.*` (while allowing `.env.example`), common private-key/certificate extensions, SSH private-key filenames, and common local credential files. These rules prevent accidental future adds when files are untracked; they do not remove or protect secrets already committed.
- GitHub currently lists **eight branches**, and each branch object reports `protected: false`, including `main` and temporary audit branches. The repository rulesets endpoint returned an empty list (`[]`), so no repository rulesets were visible at the time of this audit. The classic branch-protection endpoint returned HTTP 403 (`Resource not accessible by integration`), so its detailed settings could not be read directly. Treat `main` as unprotected unless the owner verifies otherwise in GitHub settings; require the CI workflow before accepting outside contributions.
- The CI workflow now uses the pinned `ubuntu-24.04` runner label, immutable full commit SHAs for `actions/checkout` and `actions/setup-python`, `contents: read` permissions, a 15-minute timeout, and `persist-credentials: false` for checkout.
- Dependabot is configured for weekly Python dependency and GitHub Actions updates. It proposes updates through pull requests; updates must still be reviewed and tested.
- PR #3 was squash-merged as `893622b3ff02deec7c383fac41a27630a1f7e7cf`. Its post-merge `main` workflow [41755565717](https://github.com/untidykid/simtrust-pre/actions/runs/41755565717) passed on that exact commit using the previous pinned dependency set.
- The updated dependency set (NumPy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1 plus pinned runtime dependencies) passed dependency installation, `pip check`, Python compilation, **14 unit tests**, and all five synthetic smoke suites in [run 41758359755](https://github.com/untidykid/simtrust-pre/actions/runs/41758359755).
- The subsequent PR #4 review/documentation revisions passed on the then-current head `86ae47f517fcc868ab35158aa394abef723b9b19` in [run 41758710161](https://github.com/untidykid/simtrust-pre/actions/runs/41758710161): dependency installation, `pip check`, compilation, 14 unit tests, and all five synthetic smoke suites. This run also explicitly skipped the four original evidence CSV checksums.
- On the current dependency set, CI installed NumPy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, and exact versions for the listed runtime dependencies. `pip check` reported no broken requirements. The tests were still synthetic-only.
- The pre-refresh `main` commit `58b987a9d4e500b6f45600b9c8ffaec603971d41` passed the main push workflow in [run 41759087595](https://github.com/untidykid/simtrust-pre/actions/runs/41759087595): `pip check`, compilation, **14 unit tests**, and all five synthetic smoke suites passed.
- PR #5 was squash-merged as `a1129281a1e4770695b4cbb9fdec891038e28e6d`. The post-merge `main` push workflow [42295490612](https://github.com/untidykid/simtrust-pre/actions/runs/42295490612) passed dependency installation, `pip check`, the isolated `pip-audit` scan (**No known vulnerabilities found**), Python compilation, **14 unit tests**, and all five synthetic smoke suites.
- The two Dependabot runs on the same main commit [41759102039](https://github.com/untidykid/simtrust-pre/actions/runs/41759102039) and [41759102454](https://github.com/untidykid/simtrust-pre/actions/runs/41759102454) completed successfully; their logs contained only routine dependency-update checks.
- In every workflow run, the four original v3.1 CSVs were absent, so the evidence checksum step explicitly skipped verification. This is not a checksum pass or a reproduction of the locked evidence.

## Dependency maintenance review (2026-11-06)

- The previous `scikit-learn==1.8.0` pin was outside the versions currently supported by the project's security policy. The policy marks 1.9.1 as supported; the repository now pins `scikit-learn==1.9.1`. See the [scikit-learn security policy](https://github.com/scikit-learn/scikit-learn/blob/main/SECURITY.md) and [1.9.1 release notes](https://github.com/scikit-learn/scikit-learn/blob/main/doc/whats_new/v1.9.rst).
- NumPy is pinned to `2.5.4`, pandas is now pinned to [`3.1.1`](https://pandas.pydata.org/pandas-docs/stable/whatsnew/v3.1.1.html), and scikit-learn is pinned to `1.9.1`. pandas 3.1.1 was released on 2026-11-04 and includes patch fixes for datetime, timezone, and IO behavior. All direct scientific packages and the runtime dependencies observed in CI are exact-version pinned in `requirements-v5.2.txt`.
- The main dependency set was installed successfully under Python 3.12 on the `ubuntu-24.04` runner. `pip check` reported no broken requirements; Python compilation, all **14 unit tests**, and all five synthetic smoke suites passed on the PR #4 head. See [run 41758359755](https://github.com/untidykid/simtrust-pre/actions/runs/41758359755).
- PR #5 upgrades pandas to `3.1.1` and adds an isolated known-vulnerability scan using `pip-audit` [2.10.1](https://pypi.org/project/pip-audit/2.10.1/), the current published version verified on 2026-11-06. On PR #5 head `4ea2ce0c28337b01a0ad867ef46fd868b9587f78`, [run 42294987058](https://github.com/untidykid/simtrust-pre/actions/runs/42294987058) passed dependency installation, `pip check`, the isolated vulnerability scan (**No known vulnerabilities found**), compilation, **14 unit tests**, and all five synthetic smoke suites.
- `pip-audit` runs in a temporary virtual environment so its dependencies do not alter the scientific test environment. A clean result means no matching published advisories were found for the pinned requirements at scan time; it does not guarantee protection against zero-days, malicious packages, or supply-chain compromise. The requirements file also remains version-pinned rather than hash-locked.
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

## Public-release status and remaining owner-controlled settings

### Verified public-release prerequisites

- [x] Scan all 35 current main tracked files and all 117 unique tracked text-blob versions across the reviewed main/PR history for common secret/private-data patterns; no matches were found. The scan is heuristic and does not replace GitHub Secret Scanning.
- [x] Scan the 117 reviewed historical tracked text-blob versions and the current main tree for Persian/Arabic Unicode characters; no matches were found. This does not certify untracked material, external assets, or future additions.
- [x] Scan all 62 recorded GitHub Actions job logs for common private-key/token/credential/email patterns; no matches were found.
- [x] Add `.gitignore` protections for common local environment, credential, and private certificate/key files.
- [x] Harden CI permissions and checkout credential persistence; pin Actions by immutable commit SHA and add `pip check`.
- [x] Add weekly Dependabot updates for pip and GitHub Actions.
- [x] Pin direct and observed runtime dependencies and pass CI on NumPy 2.5.4 / pandas 3.1.0 / scikit-learn 1.9.1. This improves version repeatability; package hashes and a complete software-supply-chain audit remain out of scope.
- [x] Validate the pandas 3.1.1 patch upgrade and isolated `pip-audit==2.10.1` scan on PR #5; run 42294987058 passed and reported no known vulnerabilities. Re-run CI on the final PR head after audit-document updates.
- [x] Add a scoped MIT license for original project software/code configuration in `src/`, `scripts/`, `tests/`, `.github/`, `requirements-v5.2.txt`, `.gitignore`, and `notebooks/`.
- [x] Add a separate CC BY 4.0 notice for project-authored documentation and audit materials in `README.md`, `RECOVERY_LOG.md`, `CONTRIBUTING.md`, `CITATION.cff`, `docs/`, `evidence/`, and notebook README files. Third-party and upstream dataset materials retain their own terms.
- [x] Add machine-readable citation metadata in `CITATION.cff`. The author is currently represented by the GitHub handle `untidykid`; the owner can substitute a preferred scholarly name and add an ORCID/DOI if appropriate. No DOI was invented.
- [x] Add the English `CONTRIBUTING.md` guide covering setup, scientific boundaries, data provenance, and contribution expectations.
- [x] Verify that GitHub reports the repository as Public (`visibility: public`, `private: false`) and that the public repository endpoint resolves.
- [ ] Enable branch protection for `main` and require the CI workflow. The branch listing currently reports `protected: false` for all eight branches; ruleset enforcement has not been independently verified.
- [ ] Verify GitHub Secret Scanning status and enable push protection in repository security settings if available. The current connection cannot independently inspect or change these owner-level security settings.
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

The repository is now a **public research-software and historical audit-record repository**, clearly labelled as a synthetic-tested prototype plus a bounded historical audit. Its current `main` commit and CI have been verified in the public state. Remaining hardening items are branch protection, independently checking GitHub Secret Scanning / push-protection settings, and the owner's confirmation of licensing rights. It must not be advertised as a complete reproducible v3.1 data release, a validated simulator, or a completed confirmatory v5.2 study.

The repository declares separate reuse terms for original software and project-authored documentation/audit materials. The new English `CONTRIBUTING.md` describes the scientific boundaries, reproduction commands, and contribution rules. These terms do not cover third-party material, upstream archives, or content the project does not have the right to license.
