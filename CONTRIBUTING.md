# Contributing to SimTrust-Pre

Thank you for your interest in using, reviewing, or improving this research-software repository.

## Project boundaries

SimTrust-Pre contains two deliberately separate work streams:

1. The **v3.1 locked audit** is a historical scientific record. Do not silently change its cohorts, thresholds, criteria, or conclusions. Corrections must be clearly documented as corrections, not folded into the locked result.
2. The **v5.2 research implementation** is a software prototype. Its automated tests use synthetic arrays and temporary ZIP fixtures only. Passing tests do not establish real-data event selection, sensor mapping, physical validity, or the research hypothesis.

The four original v3.1 evidence CSVs are not included. Approximate or rebuilt files must never be renamed or presented as byte-identical originals. New reconstructions need distinct filenames, schemas, provenance, and explicit status labels.

## Development setup

Use Python 3.12, the version exercised by the repository workflow.

From the repository root:

```bash
python -m pip install -r requirements-v5.2.txt
python -m pip check
python -m compileall -q scripts tests src
python -m unittest discover -s tests -v
```

The CI workflow runs dependency consistency checks, compilation, and the unit/synthetic smoke suites on pull requests and pushes to `main`. The evidence checksum step remains skipped until all four original v3.1 CSVs are available; that skip is not a successful evidence verification.

## Scientific and data-integrity requirements

- State explicitly whether a result comes from synthetic fixtures, a documented historical audit record, or a new run on the real dataset.
- For real-data work, record the exact Zenodo record/version, archive member paths and checksums, event registry, timestamp conventions, offsets, units, uncertainty semantics, exclusions, code revision, and random seeds.
- Do not claim independent validation from the two P701/P702 cases; they originate from one independent experiment.
- Do not treat the 371-row v2.1 crosswalk as the original 254-parent-key v2.2.5 artifact.
- Do not treat the 25-row P701/P702 rebuild as the historical original CSV.
- Do not infer physical units or sensor equivalence from labels alone. Preserve unresolved pressure-scale and temperature-scale discrepancies as unresolved.
- Do not relax the v5.2 donor-selection rule or alter the window-edge convention after inspecting outcomes. Record a dated, pre-outcome protocol decision before changing either rule.
- Confirmatory v5.2 claims require group-level inference, group-aware uncertainty/permutation procedures, the complete secondary-family correction, design sensitivity, and independently reviewed real-data mappings.

## Pull requests

A useful pull request should:

- Explain the problem, proposed change, and affected scientific or software boundary.
- List the exact commands/tests run and whether inputs were synthetic or real.
- Preserve provenance and show how the change affects reproducibility.
- Avoid committing credentials, local environment files, or upstream dataset archives.
- Keep source code, documentation, derived tables, and upstream third-party material under their separately applicable licenses.

Please prefer small, reviewable changes. When a proposal changes scientific interpretation or the frozen protocol, open a discussion and document the decision before implementing it.
