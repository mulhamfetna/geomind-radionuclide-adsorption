# How to mint the DOI — public Zenodo archival via GitHub Releases

**Goal:** a real, citable, timestamped DOI for each release, minted automatically by Zenodo when a
GitHub Release is published.

Zenodo (zenodo.org) is a free CERN-run archive that mints DOIs through DataCite. It connects to
GitHub via a webhook that fires on **Releases** — not on ordinary commits.

> *Superseded:* an earlier version of this document described a manual, **restricted** deposit,
> used while the repository was private. The repository is now public under AGPL-3.0, so the
> standard automatic flow below applies.

---

## ⚠️ The ordering gotcha — read this first

> **The repository must be switched ON in Zenodo *before* the GitHub Release is published.**
> If you publish the release first, Zenodo never receives the webhook and never archives it — and
> the fix is to delete the release and cut a new one. This is the single most common failure.

Correct order: **connect → enable the repo → *then* publish the release.**

---

## One-time setup

1. Go to [zenodo.org](https://zenodo.org) → **Log in with GitHub** → authorise the application.
2. In your Zenodo profile, connect your **ORCID** (0009-0006-4432-798X) so deposits link to you
   automatically.
3. Go to [zenodo.org/account/settings/github/](https://zenodo.org/account/settings/github/).
   Find **`mulhamfetna/geomind-radionuclide-adsorption`** and flip the toggle **ON**.
   - If it is not listed, press **Sync now** (Zenodo lists only repositories you own, and only
     public ones).

## Publishing a release

Once the toggle is ON:

```bash
git tag -a v1.0.0 -m "GEOMIND-R v1.0.0 — first public release"
git push origin v1.0.0
gh release create v1.0.0 --title "..." --notes "..."
```

Zenodo picks up the webhook within a minute or two, archives the source tarball, and mints:

- a **concept DOI** — always resolves to the newest version;
- a **version DOI** — pins this exact release.

Deposit metadata comes from [`.zenodo.json`](../.zenodo.json) (title, description, authors,
ORCIDs, keywords, license, `access_right: open`).

## After minting

Read the DOIs back and record them:

```bash
# take the record id from the Zenodo page URL, then:
curl -s https://zenodo.org/api/records/<id> \
  | python -c "import json,sys; d=json.load(sys.stdin); print('version:', d['doi']); print('concept:', d['conceptdoi'])"
```

Then write them into:

- [`CITATION.cff`](../CITATION.cff) — uncomment the `doi:` line (use the **concept** DOI) and the
  `identifiers:` block listing both.
- [`README.md`](../README.md) — replace `ZENODO_CONCEPT_ID` / `ZENODO_VERSION_ID` in the
  *Citation & DOI* section and in the BibTeX block.

The README DOI badge needs no editing — it uses the numeric repository id (`1309918660`) and
resolves to the latest version automatically.

## Later versions

Bump `version` + `date-released` in `CITATION.cff` and `version` + `publication_date` in
`.zenodo.json`, then publish another GitHub Release (`v1.1.0`, …). Zenodo archives it as a new
version under the **same concept DOI** — no re-enabling needed.
