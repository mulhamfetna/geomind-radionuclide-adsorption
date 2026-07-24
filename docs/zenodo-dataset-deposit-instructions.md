# How to mint the DATASET DOI — a standalone Zenodo `dataset` record

**Goal:** give the database its own citable DOI, typed **`dataset`**, so a journal's
data-availability statement can cite "the data underlying this article" independently of the code.

This is a **separate** Zenodo record from the software one. The GitHub→Zenodo webhook only creates
the *software* record automatically; a `dataset` record is a **manual, one-time upload**. Everything
you need is pre-built — your part is a ~5-minute upload.

> **Rights are already secured.** The data are CC BY 4.0, so attribution is legally required wherever
> the data live. This deposit adds a citable *identifier*, not rights.

---

## What is prepared for you

| Item | Where |
|---|---|
| The bundle to upload | `dist/GEOMIND-R-dataset.zip` (built by `python -m geomind.dataset_deposit`) |
| The exact metadata to enter | `.zenodo-dataset.json` (copy fields from here) |

The zip contains: the categorised database workbook, the figure source-data workbook, both pools as
CSVs, a full data dictionary, a README, the CC BY 4.0 licence, and a `dataset`-typed `CITATION.cff`.

---

## Steps (do them in this order)

1. Go to **[zenodo.org/uploads/new](https://zenodo.org/uploads/new)** (New upload). Do **not** use the
   GitHub-release path — that produces a *software* record; this one is a manual dataset deposit.
2. **Upload** `dist/GEOMIND-R-dataset.zip`.
3. Set the fields from `.zenodo-dataset.json`:
   - **Resource type:** *Dataset*.
   - **Title / Description / Keywords:** copy from the JSON.
   - **Creators:** both authors with their ORCIDs and affiliations (from the JSON).
   - **Licence:** *Creative Commons Attribution 4.0 International (CC BY 4.0)*.
   - **Related/alternate identifiers:** add
     `10.5281/zenodo.21510123` with relation **"is supplement to"** (this links the dataset to the
     software record), and `10.1039/d5dd00383k` with relation **"is derived from"**.
4. **Publish.** Zenodo mints the dataset's **concept DOI** and its **version DOI**.

## After minting

Tell me the two DOIs and I will:

- add the dataset DOI to the manuscript's **Data availability** statement (as the primary data
  citation) and to `CITATION.cff`;
- add a `related_identifiers` entry on the **software** side (`.zenodo.json`) pointing back with
  relation **"is source of"**, so the two records cross-reference each other in both directions;
- record it in `PROGRESS.md`.

## Keeping the two records consistent

When the data change in a future release, rebuild the bundle (`python -m geomind.dataset_deposit`)
and upload a **new version** to the *same* dataset record on Zenodo (the "New version" button),
which mints a new version DOI under the same dataset concept DOI — mirroring how the software record
versions through GitHub releases.
