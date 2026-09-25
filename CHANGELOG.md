# Changelog

## v2.0.2 — 2026-09-26

- One duplicate row removed: the SICAP record `CN1021011` (Spitalul Clinic Județean de Urgență „Sf. Apostol Andrei” Galați, Eco Fire Sistems, no published value) is the same procedure as TED `357518-2020` and is now attached to it in `deseuri_grupare.csv`. Cause: hospital-name spelling variants („Sfântul" vs „SF.") were compared literally; the comparison is now tolerant. 291 procedures; totals, dates and the 12-month window are unchanged.
- Four rows gain a note in `avertisment` (no value changes).
- `scripts/build_procedures.py` updated accordingly (also fixes found in the medical-devices audit: military-unit numbers written „U.M. nr. …", cross-format merging restricted to old-format ↔ eForms pairs with compatible titles).

## v2.0.1 — 2026-09-26

Small correction, same 292 procedures, same dates, same 12-month window (18 procedures, 24.96 M RON). An independent audit of the same method applied to medical devices (CPV 33*) found rules that also touched this set:

- `valoare_atribuita_ron` for procedures with several award notices is now the **largest published total** (previously the first notice by identifier). 29 rows changed; for one non-framework row (259994-2020, Tulcea) the value used in totals changes from 865,548 to 1,540,332 RON (dataset total 418.3 → 419.0 M RON).
- Implausible contract dates (before 2010 or more than 5 years before the first notice) are ignored with a note; none in this set.
- Award notices whose XML says no lot was awarded no longer take winners from the SICAP record; no effect here.
- Wider rule for merging the old-format (F03) and eForms notices of the same procedure; no grouping changed here, only the relation label in `deseuri_grupare.csv`.
- New `avertisment` flags for implausible published values and durations (8 rows flagged). Values stay as published.
- The build script is published in `scripts/build_procedures.py`. Details in `metodologie_ro.txt`, section "Actualizare 2.0.1".

The figures given to the press on 2026-09-23 (18 procedures expiring, 24.96 M RON, 292 procedures) are unchanged.

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
