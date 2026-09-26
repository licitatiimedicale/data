# Romanian Hospital Procurement Datasets · Medical Waste (CPV 90524*) v2 · Medical Devices (CPV 33*) v2

Open dataset of public procurement procedures for **hazardous medical waste services (CPV 90524\*) awarded by public hospitals in Romania**, 2018–2026, built from the TED award notices (read directly from XML) and the SICAP records published through OpenTender/OCDS.

**Version 2 (2026-09-23, corrected 2.0.1/2.0.2 on 2026-09-26) replaces version 1 entirely.** Version 1 contained systematic errors (framework values counted once per winner, subsequent award notices counted as new contracts, non-hospital authorities, non-medical CPV codes, unawarded procedures, a uniform 24-month duration assumption). They were found by a journalist during pre-publication verification; we confirmed them and rebuilt the dataset. The details are in [CHANGELOG.md](CHANGELOG.md). The v1 files are kept in `archive/v1/` for traceability only and must not be used.

**The CPV 33\* (medical devices) dataset was rebuilt with the same method and republished on 2026-09-26** (files `data/dispozitive_*`, methodology `metodologie_dispozitive_ro.txt`). **Devices v2 DOI: [10.5281/zenodo.22969660](https://doi.org/10.5281/zenodo.22969660)** (the v1 devices record 10.5281/zenodo.20550446 is annotated as withdrawn). It went through three rounds of independent audit before publication; what each round found and what changed is in the methodology note and in [CHANGELOG.md](CHANGELOG.md).

**Site:** https://licitatiimedicale.com · **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Files

| File | Content | Rows |
|---|---|---|
| `data/deseuri_medicale_spitale_2018_2026.csv` | One row per procedure: hospital, winners, values, framework flag, dates, duration and its source, expiry, notes, TED link | 291 |
| `data/deseuri_expira_12_luni.csv` | Subset expiring between 2026-09-23 and 2027-09-23 | 18 |
| `data/deseuri_grupare.csv` | Every raw record of our database → procedure it belongs to, with the relation (traceability) | 1,022 |
| `data/deseuri_excluse.csv` | Every excluded notice, with the reason | 38 |
| `data/deseuri_ferestre_12_luni.csv` | Procedures expiring / awarded per 12-month window since 2021 | 6 |
| `data/deseuri_verificari.txt` | Automated checks run before publication | — |
| `data/dispozitive_medicale_spitale_2018_2026.csv` | Medical devices (CPV 33*, excl. 336*): one row per procedure, same columns | 16,072 |
| `data/dispozitive_expira_12_luni.csv` | Subset expiring between 2026-09-25 and 2027-09-25 | 1,035 |
| `data/dispozitive_grupare.csv` · `dispozitive_excluse.csv` · `dispozitive_ferestre_12_luni.csv` · `dispozitive_verificari.txt` | Traceability, exclusions, 12-month windows and automated checks for the devices set | — |
| `metodologie_dispozitive_ro.txt` | Devices: what differs from the waste method, limits, audit summary (Romanian) | — |
| `metodologie_ro.txt` | Full methodology, Romanian: sources, grouping rules, value and duration rules, limitations; section "Actualizare 2.0.1" | — |
| `scripts/build_procedures.py` | The build script (Python; reads the TED XML archive, the OpenTender CSVs and our SQLite index) | — |
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

See `CITATION.cff`. **v2 DOI: [10.5281/zenodo.22908874](https://doi.org/10.5281/zenodo.22908874)**. The Zenodo records of v1 (June–September 2026) are annotated as withdrawn and point to this record.

## Who

An independent project, developed and funded by a single person from own resources; no external funding, no paying customers, no sponsors, no ties to waste operators, distributors or hospitals. Contact: info@licitatiimedicale.com
