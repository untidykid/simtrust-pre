# Public Release Readiness Audit

**Audit date:** 2026-11-07  
**Repository:** `untidykid/simtrust-pre`  
**Audit base `main` commit (before PR #9):** `521bfbacb0cc979baa683437442057fbfc9ccf95`  
**PR #9 merge commit:** `8887916a7aaae1322e175c8108f16c297a914069`  
**PR #9 validation:** [run 42302142124](https://github.com/untidykid/simtrust-pre/actions/runs/42302142124) passed on PR head `bfd6407597f91b023157457eaf841ce075dcb313`. **Post-PR #9 merge validation:** [run 42302341445](https://github.com/untidykid/simtrust-pre/actions/runs/42302341445) passed on merge commit `8887916a7aaae1322e175c8108f16c297a914069`. **PR #10 `main` validation:** [run 42302712511](https://github.com/untidykid/simtrust-pre/actions/runs/42302712511) passed on `05e1a2fe7c434724955cbbc40809bc7efa2910e3`. **PR #11:** merged as `19eb99ec5b7d3be0503912bc6ef57b5077a7a643`; PR workflow [run 42307153659](https://github.com/untidykid/simtrust-pre/actions/runs/42307153659) passed, and post-merge `main` CI [run 42375080651](https://github.com/untidykid/simtrust-pre/actions/runs/42375080651) passed on that exact commit.  
**Decision:** the repository is **Public** and is suitable as a carefully labelled public research-software and historical audit-record snapshot. It is **not** a complete reproducible release of the v3.1 evidence and is **not** ready to support confirmatory v5.2 empirical claims. `main` branch protection is configured. The owner reports Secret Scanning and push protection enabled; those two settings are not independently readable through the current GitHub connection. License-rights confirmation remains with the owner.

## Executive decision

The public repository contains useful, qualified historical audit records and a separate v5.2 software implementation. The critical distinction must be preserved between (1) locked historical v3.1 findings, (2) reported recovery fingerprints whose file bytes are not committed, (3) synthetic software tests, and (4) future real-data analysis.

Do **not** describe this repository as a fully reproducible v3.1 data release. Artifact 1 has now been uploaded and independently checked against its historical size and MD5 fingerprint; it is included in the current evidence-recovery PR #12. The original CSV payloads for Artifacts 2–4 remain absent, the exact extraction/build code for the locked tables is not included, and the historical tables have not been independently regenerated from the source archives in this repository. The v5.2 implementation has passed synthetic-fixture tests only; it has not been run against the real Zenodo dataset here.

## Verified GitHub state — 2026-11-07

- **Visibility:** GitHub repository metadata reports `visibility: public` and `private: false`.
- **Pull requests:** PRs **#1 through #11 are merged**. PR #12 is the current evidence-recovery PR and adds the fingerprint-verified Artifact 1 CSV plus corresponding metadata updates.
- **Audit base main:** `521bfbacb0cc979baa683437442057fbfc9ccf95` (`Update release audit for verified public repository state`) is the pre-PR #9 commit reviewed for this audit. PR #9's documentation-only update was merged as `8887916a7aaae1322e175c8108f16c297a914069`; its PR validation and post-merge `main` validation both passed, as linked above. The audit does not label the pre-PR #9 SHA as the current `main` head.
- **Latest merged `main` CI:** [run 42375080651](https://github.com/untidykid/simtrust-pre/actions/runs/42375080651) completed successfully on exact head `19eb99ec5b7d3be0503912bc6ef57b5077a7a643` after PR #11. The workflow passed dependency installation, `pip check`, `pip-audit` (**No known vulnerabilities found**), Python compilation, **14 unit tests**, and all five synthetic smoke suites. PR #12 introduces one evidence payload and is subject to its own required CI run.
- **Evidence gate:** [run 42375080651](https://github.com/untidykid/simtrust-pre/actions/runs/42375080651) ran before Artifact 1 was added and skipped the all-four-file checksum gate. PR #12 adds Artifact 1, but Artifacts 2–4 remain absent; therefore the all-four-file verifier still cannot run. A successful software CI result must not be described as a passed evidence checksum gate.
- **Tracked files:** the PR #11 `main` base contains 35 tracked files. PR #12 adds `evidence/artifact_1_h701_cohort.csv`, bringing the proposed PR tree to 36 tracked files. The `evidence/` directory then contains the manifest, README, and Artifact 1; original CSV payloads for Artifacts 2–4 remain absent.
- **Branches and rulesets:** The earlier pre-PR #10 snapshot had no ruleset. On 2026-11-06, a repository ruleset named `Protect main` (ID `26731306`) was created and independently read back as **Active**, targeting the default branch (`main`) with an empty bypass list. It requires a pull request, `unit-tests`, up-to-date branches, conversation resolution, linear history, Squash-only merging, and blocks deletion and force pushes. See [the active ruleset](https://github.com/untidykid/simtrust-pre/rules/26731306). This is the current verified protection state; the earlier branch-list snapshot is historical.
- **Security settings:** the repository owner reports that **Secret Scanning** and **push protection** have both been enabled in GitHub Settings → Advanced Security. The current GitHub connection cannot independently read either toggle, so this is recorded as owner-confirmed, not independently API-verified. Earlier heuristic secret scans are not a substitute for GitHub Secret Scanning.
- **Formal release:** the GitHub Releases API returned an empty list; no formal GitHub Release object was published at this snapshot.
- **Owner confirmation:** the owner still needs to confirm that all material covered by the MIT and CC BY 4.0 notices is owned or authorized for those licenses. The GitHub handle in `CITATION.cff` may be replaced with the preferred scholarly author name/ORCID; no DOI should be invented.

## Security and repository-hygiene checks (scope and limitations)

- Earlier pattern-based reviews covered the then-current tracked files, reviewed historical text-blob versions, and recorded GitHub Actions logs through the PR #5 / post-merge audit period. Those reviews found no matches for the selected common private-key, token, credential-assignment, JWT-like, and email patterns. They are **historical, heuristic scans**, not a complete security certification of every possible format or a substitute for GitHub Secret Scanning.
- The PR #11 main tree contained 35 tracked files before PR #12. PR #12 adds only the recovered Artifact 1 payload and evidence metadata/documentation; it does not change source code, scientific results, dependencies, or CI. CI is not a secret-scanning service.
- The `.gitignore` rules cover common local environment, credential, and private-key/certificate filenames. They reduce accidental future additions; they do not remove or protect secrets already committed.
- `main` protection is now configured through active repository ruleset `Protect main` (ID `26731306`). Its live rules require PRs, the `unit-tests` check, up-to-date branches, conversation resolution, linear history, Squash-only merges, and prohibit deletion and force pushes. The prior statement that no ruleset existed describes only the historical pre-PR #10 snapshot.
- The owner reports Secret Scanning and push protection enabled. The current connection cannot independently read these settings; retain this distinction in any security statement. Do not present the owner confirmation as an independent security audit or certification.
- The CI workflow uses the pinned `ubuntu-24.04` runner label, immutable full commit SHAs for `actions/checkout` and `actions/setup-python`, `contents: read` permissions, a 15-minute timeout, and `persist-credentials: false` for checkout.
- Dependabot is configured for weekly Python dependency and GitHub Actions updates. Proposed updates still require review and CI.
- The latest requirements file pins NumPy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, and the listed runtime dependencies. The post-merge CI run installed these dependencies and reported no broken requirements. The isolated vulnerability scan found no known vulnerabilities at scan time; this does not rule out zero-days, malicious packages, or supply-chain compromise.
- The requirements are exact-version pinned but are **not hash-locked**. No complete software-supply-chain audit is claimed.
- Previous historical scans and run records are retained below as context; they should not be mistaken for new scans of every historical object after every change.

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
| Artifact 1 — H701 cohort | `EXACT` historical size+MD5 fingerprint match; uploaded copy independently re-hashed on 2026-11-07 | Yes, in PR #12 branch; awaiting merge | Size 19,327 bytes; MD5 matches historical value; SHA-256 and Git blob SHA recorded in `evidence/README.md`. Integrity check only, not a new semantic derivation |
| Artifact 2 — Crosswalk v2.2.5 | Original unavailable; v2.1 approximation has 371 rows | No | Approximation is not the original 254-parent-key artifact |
| Artifact 3 — HV feasibility | `UNAVAILABLE` | No | Do not claim reconstruction |
| Artifact 4 — P701/P702 | 25-row `REBUILT_NOT_BYTE_IDENTICAL` file | No | Rebuild is not the original artifact |

The verifier correctly retains the historical original-file fingerprints and does not accept approximate or rebuilt files as originals. Artifact 1's uploaded copy matches its historical size and MD5; Artifacts 2–4 are still absent, and the verifier must continue to reject approximations or rebuilds as substitutes.

## Public-release status and remaining owner-controlled settings

### Verified public-release prerequisites

- [x] Scan all 35 current main tracked files and all 117 unique tracked text-blob versions across the reviewed main/PR history for common secret/private-data patterns; no matches were found. The scan is heuristic and does not replace GitHub Secret Scanning.
- [x] Scan the 117 reviewed historical tracked text-blob versions and the current main tree for Persian/Arabic Unicode characters; no matches were found. This does not certify untracked material, external assets, or future additions.
- [x] Scan all 62 recorded GitHub Actions job logs for common private-key/token/credential/email patterns; no matches were found.
- [x] Add `.gitignore` protections for common local environment, credential, and private certificate/key files.
- [x] Harden CI permissions and checkout credential persistence; pin Actions by immutable commit SHA and add `pip check`.
- [x] Add weekly Dependabot updates for pip and GitHub Actions.
- [x] Pin direct and observed runtime dependencies and pass CI on NumPy 2.5.4 / pandas 3.1.1 / scikit-learn 1.9.1. This improves version repeatability; package hashes and a complete software-supply-chain audit remain out of scope.
- [x] Validate the pandas 3.1.1 patch upgrade and isolated `pip-audit==2.10.1` scan on PR #5; run 42294987058 passed and reported no known vulnerabilities. The post-PR #9 main CI run is [42302341445](https://github.com/untidykid/simtrust-pre/actions/runs/42302341445), on the PR #9 merge commit listed above.
- [x] Add a scoped MIT license for original project software/code configuration in `src/`, `scripts/`, `tests/`, `.github/`, `requirements-v5.2.txt`, `.gitignore`, and `notebooks/`.
- [x] Add a separate CC BY 4.0 notice for project-authored documentation and audit materials in `README.md`, `RECOVERY_LOG.md`, `CONTRIBUTING.md`, `CITATION.cff`, `docs/`, `evidence/`, and notebook README files. Third-party and upstream dataset materials retain their own terms.
- [x] Add machine-readable citation metadata in `CITATION.cff`. The author is currently represented by the GitHub handle `untidykid`; the owner can substitute a preferred scholarly name and add an ORCID/DOI if appropriate. No DOI was invented.
- [x] Add the English `CONTRIBUTING.md` guide covering setup, scientific boundaries, data provenance, and contribution expectations.
- [x] Verify that GitHub reports the repository as Public (`visibility: public`, `private: false`) and that the public repository endpoint resolves.
- [x] Configure active branch ruleset `Protect main` (ID `26731306`) with PR, `unit-tests`, up-to-date branch, linear-history, conversation-resolution, Squash-only, deletion, and force-push protections. Independently read back the active ruleset on 2026-11-06.
- [x] Owner confirmed that GitHub Secret Scanning and push protection are enabled on 2026-11-06. These owner-reported settings are not independently API-verifiable through the current connection; do not characterize them as independently audited.
- [ ] Owner should confirm that all material covered by the MIT and CC BY 4.0 notices is owned or authorized for licensing. Replace the GitHub handle in `CITATION.cff` with a preferred scholarly author name/ORCID when desired; no DOI should be invented.

### Required before a complete reproducible v3.1 data release

- [x] Independently verify the uploaded Artifact 1 copy against its historical size and MD5; record SHA-256 and Git blob SHA. [ ] Recover and independently verify original Artifacts 2–4 against their historical size and MD5 values.
- [ ] Include the exact source archives and extraction/build code, or provide durable, versioned access to them with clear provenance and licensing.
- [ ] Re-run the frozen extraction from the pinned source data and independently reproduce the locked tables without changing the v3.1 cohort or criteria.

### Required before confirmatory v5.2 empirical claims

- [ ] Resolve the sample-instant versus sample-support interval convention and align Module 1/Module 4.1 edge-gap calculations.
- [ ] Reconcile the donor matching rule with the frozen Phase 0 protocol before outcomes are inspected.
- [ ] Implement and test group-level Spearman, group-aware uncertainty/permutation inference, the full secondary-family BH correction, and group-count-aware design sensitivity.
- [ ] Verify pressure channel identity, units, export conversion, uncertainty meaning, and time alignment from the original source files.
- [ ] Execute the frozen pipeline on the real dataset with a complete review registry and preserve all rejection/provenance outputs.

## Publication recommendation

The repository is a **public research-software and historical audit-record repository**, clearly labelled as a synthetic-tested prototype plus a bounded historical audit. Artifact 1 has a fingerprint-matched upload included in PR #12; Artifacts 2–4, the exact source archives, and the extraction/build code remain outstanding. Remaining owner-controlled item for the public repository snapshot is confirmation that the project has rights to license all project-authored material under the scoped MIT and CC BY 4.0 notices. The owner reports Secret Scanning and push protection enabled, but those toggles were not independently API-verified. It must not be advertised as a complete reproducible v3.1 data release, a validated simulator, or a completed confirmatory v5.2 study.

The repository declares separate reuse terms for original software and project-authored documentation/audit materials. The new English `CONTRIBUTING.md` describes the scientific boundaries, reproduction commands, and contribution rules. These terms do not cover third-party material, upstream archives, or content the project does not have the right to license.
