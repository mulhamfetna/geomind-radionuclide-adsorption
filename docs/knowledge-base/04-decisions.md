# Decisions

Standing decisions. Reversing one requires a new entry, not an edit.

| id | decision | reason |
|---|---|---|
| D1 | Drop Si_Al and Density from physical data | F1 - transplanted, not measured |
| D2 | Re-scope M3b to cross-system transfer | Different material system; no viscosity; 92 mixes |
| D3 | Repo private, all-rights-reserved | Unpublished research |
| D4 | Copyrighted PDFs excluded from git | Copyright + 80 MB; manifest tracks them |
| D5 | Do not use Feasibility_Ranges | F6 - anti-correlated with ground truth |
| D6 | Kd kept in its own column, never in capacity_mg_g | Different physical quantity |
| D7 | Reject Tian supplement's 24-row table | No composition; would pad without features |
| D8 | Quarantine Na-MK, K-MK and all Niu 2022 rows | F7 - not in stated sources |
| D9 | No subagents for extraction or analysis | Missing project context lets silent errors in |
| D10 | Pre-register NMR acceptance at r>=0.9 | Deconvolution is under-determined; stops retroactive tuning |
| D11 | ARI claims are gated on Q4-rich framework sorbents | F19 - Ca-bearing gels have no framework; descriptor is meaningless there, not merely weak |
| D12 | Never pool sorbent structural classes in a correlation | F19 - pooling hid ARI +0.932 and -0.108 behind a single +0.536 |
| D13 | Run adsorption capacity and leach resistance as TWO parallel pools, never merged | PI decision 2026-07-20 on F20. Removal-from-solution and immobilisation are different applications with different targets; the descriptor is available only in the second. Consistent with D12. |
| D15 | Re-read every triage-rejected paper inline before trusting the rejection | F24 - Kurumisawa was rejected on keyword balance, but its Cs capacity lives only in a figure, which keyword counts cannot see |
| D16 | Never compute ARI from a deconvolution whose m-assignment is ambiguous | F23 - Vettese's Table 4 admits ARI 2.289 or 0.861, a 2.7x fork |
| D17 | STOP literature acquisition; advance to the descriptor-and-methodology paper + within-class forward model | F36 - acquisition at negative returns; within-class LOO-CV R2=0.81 but pooled R2<0; more papers add heterogeneity not signal. Generative M5 gated on single-protocol data (GEOMIND request or own-lab), not literature. |
| D14 | Index the corpus by CONTENT, not filename | F13/F20 - Kim 2026 and Nevin 2026, the two most descriptor-rich papers held, were invisible to a filename-based check because their filenames are not in Latin script |
