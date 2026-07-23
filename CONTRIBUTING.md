# Contributing to GEOMIND-R

Thank you for your interest. This project is research software backing a scientific result, so
contributions are welcome but held to the evidence standard described below.

## How to report a problem

Open an issue: <https://github.com/mulhamfetna/geomind-radionuclide-adsorption/issues>

Please include:

- what you ran (the exact command or code), and what you expected;
- what actually happened, with the full error or the wrong value;
- your Python version and operating system.

**If you believe a published number is wrong, say so.** Data-integrity reports are the most
valuable issues this project can receive. Please point at the specific row, figure or finding and,
where possible, the primary source that contradicts it.

## How to get support

- **Usage questions** — open an issue with the `question` label.
- **Scientific or data-provenance questions** — contact the authors directly (see the
  *Authors & contact* section of the [README](README.md#authors--contact)).

## How to contribute code or data

1. **Open an issue first** for anything beyond a typo, so the approach can be agreed before you
   spend effort.
2. Fork the repository and create a branch off `main`.
3. **Write a failing test first.** Every behavioural change ships with a test; the suite is the
   contract.
4. Make the change, and run the full suite:
   ```bash
   PYTHONPATH=src python -m pytest -q
   ```
   All tests must pass (the `test_warehouse.py` tests skip unless the 31 MB warehouse database has
   been built locally — that is expected).
5. Open a pull request describing **what you ran and what the output was**. The PR template asks
   for this; it is not a formality.

### Standards specific to this project

- **No number without provenance.** Any added or corrected data row must carry its source, and the
  claim must be verifiable against the primary publication — not against another compilation.
- **Never merge the two pools.** Pool A (adsorption) and Pool B (immobilisation) measure different
  quantities and are deliberately kept separate (finding F19, decision D12).
- **Do not weaken the confidence flags.** Predictions outside the validated domain must remain
  flagged. The honesty rules live in `app/engine.py` and are covered by tests; changes that would
  present an unvalidated prediction as trustworthy will not be accepted.
- **Do not commit copyrighted material.** Publisher PDFs and HTML are excluded by `.gitignore`;
  the corpus is tracked reproducibly through `papers/MANIFEST.md`.
- Match the surrounding style: type hints, short focused functions, and a docstring saying *why*.

## Licensing of contributions

By contributing you agree that your contributions are licensed under the same terms as the
project: **AGPL-3.0-or-later** for software, **CC BY 4.0** for data, figures and documentation
(see [`NOTICE.md`](NOTICE.md)).

## Code of Conduct

All participants are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
