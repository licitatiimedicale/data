# Romanian Medical Procurement Dataset · CPV 9052* + CPV 33*

**Open dataset** of all publicly available contract award notices from the European Union's *Tenders Electronic Daily* (TED) database for **medical procurement in Romania**:

- **CPV 9052*** — Hazardous medical waste collection, transport, disposal services (487 contracts, 2019-2026)
- **CPV 33*** — Medical devices, equipment, consumables, imaging, sterilization (19,087 contracts, 2020-2026)

**Site:** https://licitatiimedicale.com
**Last updated:** see `data/*.csv` timestamps + git log
**License:** Creative Commons Attribution 4.0 ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))

**DOI (academic citation):**
- CPV 9052* (medical waste, 487 records): [10.5281/zenodo.20535486](https://doi.org/10.5281/zenodo.20535486)
- CPV 33* (medical devices, 19,087 records) 🆕: [10.5281/zenodo.20550446](https://doi.org/10.5281/zenodo.20550446)

---

## What's in this repository

| File | Description | Rows |
|---|---|---|
| `data/awards.csv` | Legacy CPV 9052* only file (preserved for backward compat) | 487 |
| `data/awards-cpv9052-deseuri.csv` | Hazardous medical waste contracts (CPV 9052*) | **487** |
| `data/awards-cpv33-dispozitive.csv` | Medical device contracts (CPV 33*) — NEW June 2026 | **19,087** |
| `data/awards-all.csv` | Both niches combined | **19,574** |
| `schema/awards.schema.json` | JSON Schema for the dataset |
| `methodology.md` | Methodology: collection, normalization, Tukey IQR |
| `CITATION.cff` | Citation File Format for academic use |
| `LICENSE` | CC BY 4.0 full text |

### Columns (14)

```
id, tender_id, hospital_name, hospital_slug, entity_key,
winner_name, value_ron, value_currency, value_type, award_date,
niche, cpv_primary, cpv_all, created_at
```

- `niche`: `deseuri_medicale` (CPV 9052*) or `dispozitive_medicale` (CPV 33*)
- `cpv_primary`: primary CPV code (e.g. `33110000` for imaging)
- `cpv_all`: JSON array of all CPV codes for the contract

---

## At a glance (current snapshot — June 2026)

### CPV 9052* (Medical waste services)

- **487 contract award notices** for hazardous medical waste services in Romania
- **155 hospitals** as contracting authorities
- **49 distinct operators** (winning firms)
- **898 million RON cumulative value** (~180 million EUR)
- Time range: **August 2019 → April 2026**
- Top 5 operators concentrate **60.2%** of contracts (concentrated market; Romanian Competition Council decision 100/2025 found cartel practices)
- CPV codes covered: 90520000, 90521000, 90522000, 90523000, 90524000 (and subcodes)

### CPV 33* (Medical devices) — NEW June 2026

- **19,087 contract award notices** for medical devices, equipment, consumables
- **942 hospitals** as contracting authorities
- **1,370 distinct distributors** (winning firms)
- **154 billion RON cumulative ceiling** (framework agreements multi-year)
- Time range: **January 2020 → June 2026**
- Top 10 distributors concentrate only **16.2%** by count (fragmented market — radically different from CPV 9052*)
- Top 10 hospitals concentrate **58.4%** of value (concentrated demand)
- 17 subcategories: imaging (33110000), consumables (33140000), sterilization (33191000), dental (33130000), anesthesia (33170000), mobile equipment (33196000), IT (33197000), paper articles (33198000), etc.

---

## Quick start

```bash
git clone https://github.com/licitatiimedicale/data.git
cd data

# Python
python3 -c "
import pandas as pd
df = pd.read_csv('data/awards-all.csv')
print(df.shape)
print(df.groupby(['niche', 'winner_name']).size().sort_values(ascending=False).head(20))
"

# CSV stats — top distributors by niche
awk -F',' 'NR>1 && $11==\"dispozitive_medicale\" {print $6}' data/awards-cpv33-dispozitive.csv | sort | uniq -c | sort -rn | head -10
```

---

## Source & methodology

- **Source:** TED — Tenders Electronic Daily, Official Journal of the European Union
- **API:** TED v3 Search + XML notice fetch
- **Filter:** `classification-cpv IN (...)` + `place-of-performance IN (ROU)` + `notice-type IN (can-standard, can-social)`
- **Update:** Daily incremental ingestion via cron (07:00 UTC)
- **Parser:** Dual-format (eForms 2025+ + legacy TED ≤2024)
- See `methodology.md` for full details

---

## Live API

For real-time access:

- CSV: `https://licitatiimedicale.com/api/v1/awards.csv?niche=dispozitive_medicale`
- JSON: `https://licitatiimedicale.com/api/v1/awards?niche=deseuri_medicale&limit=100`
- Per-judet: `https://licitatiimedicale.com/api/v1/judet/{slug}`
- Per-operator: `https://licitatiimedicale.com/api/v1/operator/{slug}`
- Benchmark: `https://licitatiimedicale.com/api/v1/benchmark`

---

## Key analyses available on the platform

### CPV 9052* (Medical waste)
- [Top 5 operators hold 52%](https://licitatiimedicale.com/cazuri/concentrarea-pietei-cinci-operatori-cincizeci-doi-procente)
- [STERICYCLE / STERILECO / ECOLOGMED ecosystem](https://licitatiimedicale.com/cazuri/stericycle-stericeo-ecologmed-ecosistem-deseuri-medicale)
- [Cartel decision 100/2025 Competition Council](https://licitatiimedicale.com/cazuri/cartel-deseuri-medicale-consiliul-concurentei-2025)
- [Framework vs single contract reading](https://licitatiimedicale.com/cazuri/acord-cadru-vs-contract-specific-citire-corecta-valoare)
- [Seasonality: 62% of contracts in Q4-Q1](https://licitatiimedicale.com/cazuri/sezonalitatea-pietei-deseuri-medicale-romania)

### CPV 33* (Medical devices) — NEW
- [Top 10 distributors — fragmented market (16% concentration)](https://licitatiimedicale.com/cazuri/top-10-distribuitori-dispozitive-medicale-cpv33)
- [Top 10 hospitals — concentrated buyer side (58%)](https://licitatiimedicale.com/cazuri/top-10-spitale-concentrare-cpv33)
- [Hub CPV 33* — live stats](https://licitatiimedicale.com/licitatii-dispozitive-medicale)
- [Procurement guide for medical device suppliers](https://licitatiimedicale.com/ghid-licitatii-dispozitive-medicale)

---

## Citation

```bibtex
@dataset{licitatiimedicale_cpv9052_2026,
  author       = {{Licitații Medicale}},
  title        = {Romanian Hazardous Medical Waste Procurement (CPV 9052*)},
  year         = 2026,
  publisher    = {Zenodo},
  url          = {https://github.com/licitatiimedicale/data},
  doi          = {10.5281/zenodo.20535486},
  note         = {CC BY 4.0}
}

@dataset{licitatiimedicale_cpv33_2026,
  author       = {{Licitații Medicale}},
  title        = {Romanian Medical Devices Procurement (CPV 33*)},
  year         = 2026,
  publisher    = {Zenodo},
  url          = {https://github.com/licitatiimedicale/data},
  doi          = {10.5281/zenodo.20550446},
  note         = {CC BY 4.0 — 19,087 contracts, 942 hospitals, 1,370 distributors}
}
```

Or plain text:

> Licitații Medicale (2026). *Romanian Medical Procurement Dataset (CPV 9052* + CPV 33*)*. https://github.com/licitatiimedicale/data. CC BY 4.0.

See `CITATION.cff` for machine-readable citation.

---

## Use cases

- Investigative journalism (procurement transparency)
- Academic research (concentration metrics, sectoral analysis, supply chain studies)
- Public policy (anti-corruption monitoring, healthcare procurement reform)
- Distributor due diligence (market share, history, competitive intelligence)
- Hospital procurement teams (benchmark price estimation)
- Audit firms (sector public + healthcare audit, anomaly verification)
- Law firms (procurement disputes, CNSC contestations)

---

## Editorial policy

All analyses on the platform use **exclusively public official sources** (TED, ANAP, CNSC, Romanian Competition Council, Official Gazette court rulings, established press reports). We do not make accusations against individuals or firms. All persons and firms named retain the full presumption of innocence under the Romanian Constitution (Article 23, paragraph 11).

For factual corrections: info@licitatiimedicale.com (response within 24h).

---

## License

CC BY 4.0 — you are free to share and adapt, with attribution to *Licitații Medicale* (https://licitatiimedicale.com).

The underlying data is from TED (Official Journal of the EU), which is also publicly available under EU re-use of public sector information (Directive 2019/1024) and Romanian Law 179/2022.

---

## Contact

- **Email:** info@licitatiimedicale.com
- **Web:** https://licitatiimedicale.com
- **Press kit:** https://licitatiimedicale.com/presa
