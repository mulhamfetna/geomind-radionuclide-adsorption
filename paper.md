---
title: 'GEOMIND-R: a domain-guarded virtual laboratory for radionuclide uptake in geopolymers'
tags:
  - Python
  - materials informatics
  - geopolymers
  - radionuclide immobilisation
  - nuclear waste
  - reproducible research
authors:
  - name: Mulham Fetna
    orcid: 0009-0006-4432-798X
    corresponding: true
    affiliation: 1
  - name: Abdulrazzaq Hammal
    orcid: 0000-0003-1828-1376
    affiliation: 2
affiliations:
  - name: Department of Mechatronics Engineering, Faculty of Electrical and Electronic Engineering, University of Aleppo, Aleppo, Syria
    index: 1
  - name: Department of Basic Science - Chemistry, Faculty of Electrical Engineering, University of Aleppo, Aleppo, Syria
    index: 2
date: 23 July 2026
bibliography: paper.bib
---

# Summary

`GEOMIND-R` is a Python package and interactive "virtual laboratory" for exploring how geopolymer
composition governs the uptake of caesium and strontium — the two radionuclides that dominate
intermediate-level nuclear waste. It bundles an audited, provenance-tracked meta-analysis database
(195 measurements across 22 published sources, split into separate adsorption and immobilisation
pools), the analysis pipeline that produced our findings, and a graphical interface in which a user
can enter a composition and receive a predicted distribution coefficient together with an explicit
statement of how far that prediction can be trusted.

The scientific result the software encodes is that **framework aluminium**, not specific surface
area, governs cation uptake: tetrahedral Al$^{IV}$ carries the charge-balancing sites that bind the
cation. Within a single structural class and protocol this yields a forward model that predicts
held-out samples (leave-one-out $R^2 = 0.81$); pooled across laboratories the same relationship
performs worse than predicting the mean.

# Statement of need

Screening tools in materials informatics routinely present a number without indicating whether the
input lies inside the region where the model was validated. In this domain that is not a cosmetic
problem: descriptor–property relationships in alkali-activated materials are **class-specific**, and
the sign of a correlation can invert between structural classes. A tool that silently extrapolates
across those boundaries produces confident, wrong guidance.

`GEOMIND-R` is built around that failure mode rather than around a headline accuracy figure. Every
prediction is returned as a result object carrying a **tri-colour confidence flag** — validated,
exploratory, or unsupported — chosen from the input's position relative to the model's trained
domain and structural class, together with a plain-language reason and a provenance string. Inputs
outside the validated envelope are still evaluated, because refusing to answer is unhelpful, but
they are never presented as trustworthy. The honesty rules live in a tested service layer, not in
the interface, so they cannot be bypassed by a caller.

The package also contributes reusable methodology. A **saturation screen**,
$\theta = bC_0/(1 + bC_0) = 1 - R_L$, flags reported Langmuir capacities obtained far below
saturation, where a high reported $R^2$ reflects a fit to the initial slope rather than a real
plateau. A **two-pool audit framework** keeps adsorption and immobilisation measurements separate,
since they are not interconvertible, and records an explicit verdict and reason for every ingested
table. Both address recurring problems in the wider meta-analysis literature and are applicable
beyond geopolymers.

Three interfaces are provided: a Python API, a local Gradio application, and a self-contained
notebook that runs in Google Colab without installation or repository access, so that
non-programming collaborators and reviewers can reproduce every number interactively. The notebook
is generated from the tested modules and verified against them, so it cannot drift from the desktop
application.

# Availability and reuse

The software is released under AGPL-3.0-or-later and the data, figures and documentation under
CC BY 4.0; both require attribution. Releases are archived to Zenodo with a persistent DOI
[@geomindr]. A source-data workbook containing the exact values behind every published figure is
regenerated from the live pipeline and distributed with the package.

# Acknowledgements

We thank the authors of the reference work [@geomind] for the study that motivated this project.

# References
