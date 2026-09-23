# Changelog

## v2 — 2026-09-23

**All v1 files have been withdrawn from `data/` and moved to `archive/v1/`. They contain systematic errors and must not be used.**

A journalist who checked the v1 files before publication found the errors listed below. We confirmed every one of them and rebuilt the hazardous medical waste dataset from the source XML notices. The medical devices dataset (CPV 33*) had the same errors and is withdrawn until it is rebuilt with the same method.

### What was wrong in v1

1. **Framework agreements were counted once per winner.** TED publishes one award record per winner of a multi-winner framework, each carrying the framework's total value. v1 stored every record as a separate contract, so a 912 million RON framework with 6 winners appeared six times. Across the database this inflated totals by roughly 90%.
2. **Subsequent award notices were counted as new contracts.** Authorities publish a new award notice for each contract based on a framework (sometimes 6–10 notices for one framework). v1 counted each as a separate contract with the framework's full value.
3. **The CPV filter `9052*` included non-medical waste.** `90522000` (contaminated soil) put a 318.6 million RON OMV Petrom contract in a "hospital waste" table. v2 uses only `90524*`.
4. **"Hospitals" included all contracting authorities** (military units, social care directorates, veterinary authorities, city halls). v2 keeps hospitals only, with an explicit rule and a list of every excluded authority.
5. **Cancelled or unawarded procedures were counted as contracts.** v2 excludes them only when the TED notice confirms it.
6. **Old-format TED award notices (F03, before 2023) were not parsed**; hundreds of them were mislabelled "no award" by our own code. v2 reads every XML notice directly.
7. **Expiry dates were award date + 24 months for every row.** v2 uses the published contract duration (eForms planned period, F02 contract notice, or SICAP contract period) and marks the remaining rows as estimates.
8. Old-format notices imported through OpenTender carried the publication date instead of the contract date; v2 uses the first contract signature date from the XML.

### What v2 contains

- `data/deseuri_medicale_spitale_2018_2026.csv` — one row per procedure, 292 procedures, hospitals only, CPV 90524*.
- `data/deseuri_expira_12_luni.csv` — the subset expiring between 2026-09-23 and 2027-09-23 (18 rows; duration source given per row).
- `data/deseuri_grupare.csv` — every raw record of our database and the procedure it was assigned to, with the relation (traceability).
- `data/deseuri_excluse.csv` — every excluded notice with the reason.
- `data/deseuri_ferestre_12_luni.csv` — 12-month windows since 2021 (use the `publicate_in_TED` columns for year-to-year comparison).
- `data/deseuri_verificari.txt` — the automated checks run before publication.
- `metodologie_ro.txt` — full methodology (Romanian).

### Zenodo

The DOIs cited in v1 (10.5281/zenodo.20535486, 10.5281/zenodo.20550446) describe the v1 files and inherit their errors. Monthly automatic deposits are suspended. The v2 files are published as a new Zenodo record, **DOI 10.5281/zenodo.22908874**; every v1 record (10.5281/zenodo.20503071, 20535487, 20550446, 21096793, 21096797, 21736017, 21736019, 22226079) is annotated as withdrawn and points to it.

## v1 — 2026-06-03 / 2026-06-05

Initial publication (487 waste records, 19,087 device records). Withdrawn, see above.
