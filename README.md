# Romanian Hospital Medical Waste Contracts · CPV 90524* · v2

Open dataset of public procurement procedures for **hazardous medical waste services (CPV 90524\*) awarded by public hospitals in Romania**, 2018–2026, built from the TED award notices (read directly from XML) and the SICAP records published through OpenTender/OCDS.

**Version 2 (2026-09-23) replaces version 1 entirely.** Version 1 contained systematic errors (framework values counted once per winner, subsequent award notices counted as new contracts, non-hospital authorities, non-medical CPV codes, unawarded procedures, a uniform 24-month duration assumption). They were found by a journalist during pre-publication verification; we confirmed them and rebuilt the dataset. The details are in [CHANGELOG.md](CHANGELOG.md). The v1 files are kept in `archive/v1/` for traceability only and must not be used.

**The CPV 33\* (medical devices) dataset of v1 is withdrawn** until it is rebuilt with the same method.

**Site:** https://licitatiimedicale.com · **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Files

| File | Content | Rows |
|---|---|---|
| `data/deseuri_medicale_spitale_2018_2026.csv` | One row per procedure: hospital, winners, values, framework flag, dates, duration and its source, expiry, notes, TED link | 292 |
| `data/deseuri_expira_12_luni.csv` | Subset expiring between 2026-09-23 and 2027-09-23 | 18 |
| `data/deseuri_grupare.csv` | Every raw record of our database → procedure it belongs to, with the relation (traceability) | 1,022 |
| `data/deseuri_excluse.csv` | Every excluded notice, with the reason | 38 |
| `data/deseuri_ferestre_12_luni.csv` | Procedures expiring / awarded per 12-month window since 2021 | 6 |
| `data/deseuri_verificari.txt` | Automated checks run before publication | — |
| `metodologie_ro.txt` | Full methodology, Romanian: sources, grouping rules, value and duration rules, limitations | — |
| `CHANGELOG.md` | What was wrong in v1 and what changed | — |
| `archive/v1/` | Withdrawn v1 files, README and methodology | — |

## Columns of `deseuri_medicale_spitale_2018_2026.csv`

`id_procedura` (oldest TED award notice of the procedure, or SICAP number) · `publicat_in_TED` · `autoritate_contractanta` · `castigatori` · `valoare_ron` (value used in totals) · `baza_valorii` · `valoare_atribuita_ron` · `sursa_valoare_atribuita` · `valoare_max_acord_ron` · `sursa_valoare_max` · `valoare_max_estimata_acord_ron` (eForms BT-271) · `acord_cadru` · `titlu` · `cpv` · `data_atribuirii` (first contract signature date published in TED) · `durata_luni` · `data_expirarii` · `sursa_durata` · `expira_in_12_luni` · `avertisment` · `note` · `link`

## Key rules (summary; full text in `metodologie_ro.txt`)

- One procedure = one row. Notices of the same procedure are grouped by eForms `ContractFolderID`, by the F02 contract notice they reference (old format), or by hospital + winners + date.
- Framework agreements: the framework's maximum value is counted once (eForms BT-118, otherwise the published estimate); the awarded value is given in a separate column.
- Hospitals only (including military hospitals); every excluded authority is listed with the reason.
- Cancelled or unawarded procedures are excluded only when the TED notice confirms it.
- Duration: published contract duration (eForms planned period > F02 notice > SICAP); otherwise `ESTIMAT (24 luni)` is stated in `sursa_durata`.
- SICAP/OpenTender covers 2020–2024 only; 2025–2026 rows come from TED (above the EU threshold). Compare years using the `publicate_in_TED` columns.
- No value in this dataset is actual spending; values are those published in the notices.

## Sources

- TED, Tenders Electronic Daily (https://ted.europa.eu): award notices (eForms and F03), the contract notices they reference (eForms CN and F02) and corrigenda (F14), all read from XML.
- SICAP through the OpenTender / OCDS Romania publication (https://data.open-contracting.org, publication 75), years 2020–2024.

Public data only; legal entities only. No accusation is made or implied about any authority or operator; editorial conclusions belong to the reader.

## Citation

See `CITATION.cff`. The Zenodo DOIs of v1 describe the withdrawn files; a new Zenodo version for v2 will be listed here when published.

## Who

An independent project, developed and funded by a single person from own resources; no external funding, no paying customers, no sponsors, no ties to waste operators, distributors or hospitals. Contact: info@licitatiimedicale.com
