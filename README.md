# Romanian Hazardous Medical Waste Procurement Dataset

**Open dataset** of all publicly available contract award notices from the European Union's *Tenders Electronic Daily* (TED) database for services related to **hazardous medical waste management** in Romania (**CPV 9052***).

**Site:** https://licitatiimedicale.com
**Last updated:** see `data/awards.csv` timestamps
**License:** Creative Commons Attribution 4.0 ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))

---

## What's in this repository

| File | Description |
|---|---|
| `data/awards.csv` | All 487+ contract award notices (2019-2026), 11 fields, UTF-8 |
| `schema/awards.schema.json` | JSON Schema for the dataset |
| `methodology.md` | Methodology: data collection, normalization, Tukey IQR anomaly detection |
| `CITATION.cff` | Citation File Format for academic use |
| `LICENSE` | CC BY 4.0 full text |

## At a glance (current snapshot)

- **487 contract award notices** for medical waste services in Romania
- **155 hospitals** (county, clinical, university, military) as contracting authorities
- **49 distinct operators** (winning firms)
- **898 million RON cumulative value** (~ 180 million EUR)
- Time range: **August 2019 → April 2026**
- Source: TED (Tenders Electronic Daily — Official Journal of the EU)
- CPV codes covered: 90520000, 90521000, 90522000, 90523000, 90524000 (and subcodes 90524100-90524400)

## Quick start

```bash
# Clone
git clone https://github.com/[YOUR-USERNAME]/licitatiimedicale-data.git
cd licitatiimedicale-data

# Load into Python
python3 -c "
import pandas as pd
df = pd.read_csv('data/awards.csv')
print(df.shape)
print(df.groupby('winner_name').agg({'value_ron': 'sum'}).sort_values('value_ron', ascending=False).head(10))
"
```

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | int | Internal numeric ID |
| `tender_id` | string | TED notice publication number (`{year}-{seq}` format) |
| `hospital_name` | string | Contracting authority full name as published in TED |
| `hospital_slug` | string | URL-safe slug for the hospital page on licitatiimedicale.com |
| `entity_key` | string | Normalized entity key (city slug) for cross-referencing |
| `winner_name` | string | Winning operator(s), may include joint ventures separated by `/` |
| `value_ron` | float | Contract value in RON (Romanian Leu) |
| `value_currency` | string | Currency code, typically `RON` |
| `value_type` | string | Either `framework` (multi-year framework agreement) or `single` (specific contract) |
| `award_date` | date | Date when the contract was awarded (YYYY-MM-DD) |
| `created_at` | timestamp | When this row was added to our database |

## Key analyses available on the platform

- [Market concentration: top 5 operators hold 52%](https://licitatiimedicale.com/cazuri/concentrarea-pietei-cinci-operatori-cincizeci-doi-procente)
- [STERICYCLE / STERILECO / ECOLOGMED ecosystem analysis](https://licitatiimedicale.com/cazuri/stericycle-stericeo-ecologmed-ecosistem-deseuri-medicale)
- [Framework vs specific contract: how to read values correctly](https://licitatiimedicale.com/cazuri/acord-cadru-vs-contract-specific-citire-corecta-valoare)
- [ANAP 2021 report: 39.15% deviation in non-publication procedures](https://licitatiimedicale.com/cazuri/anap-2021-proceduri-fara-publicare-prealabila-sanatate)
- [Variance of 691× between contracts: methodological interpretation](https://licitatiimedicale.com/cazuri/varianta-pret-pe-piata-deseuri-medicale-saizeci-ori)
- [Seasonality: 62% of contracts awarded in Q4-Q1](https://licitatiimedicale.com/cazuri/sezonalitatea-pietei-deseuri-medicale-romania)
- [CPV 9052* classification guide for journalists](https://licitatiimedicale.com/cazuri/clasificare-cpv-9052-ce-include-ce-nu-include)

## Methodology

See [`methodology.md`](methodology.md) for:

1. Data collection pipeline (TED API v3 polling)
2. Entity resolution (hospital name → canonical city slug)
3. Value normalization (framework contracts → annualized RON/year)
4. Tukey IQR outlier detection (1977)
5. Quality caveats and known limitations

## Live API

For real-time access:

- CSV: `https://licitatiimedicale.com/api/v1/awards.csv`
- JSON: `https://licitatiimedicale.com/api/v1/awards`
- Per-judet: `https://licitatiimedicale.com/api/v1/judet/{slug}`
- Per-operator: `https://licitatiimedicale.com/api/v1/operator/{slug}`
- Benchmark calculator: `https://licitatiimedicale.com/api/v1/benchmark`

## Citation

If you use this dataset in academic work, please cite as:

```bibtex
@dataset{licitatiimedicale_2026,
  author       = {{Licitații Medicale}},
  title        = {Romanian Hazardous Medical Waste Procurement Dataset (CPV 9052*)},
  year         = 2026,
  publisher    = {licitatiimedicale.com},
  url          = {https://licitatiimedicale.com/dataset},
  note         = {CC BY 4.0}
}
```

Or in plain text:

> Licitații Medicale (2026). *Romanian Hazardous Medical Waste Procurement Dataset (CPV 9052\*)*. Available at https://licitatiimedicale.com/dataset. CC BY 4.0.

## Use cases

- Investigative journalism (procurement transparency)
- Academic research (concentration metrics, sectoral analysis)
- Public policy (anti-corruption monitoring)
- Operator due diligence (market share, history)
- Hospital procurement teams (benchmark price estimation)

## Editorial policy

All analyses on the platform use **exclusively public official sources** (TED, ANAP, CNSC, Romanian Competition Council decisions, court rulings published in the Official Gazette, established press reports). We do not make accusations against individuals or firms. All persons and firms named retain the full presumption of innocence under the Romanian Constitution (Article 23, paragraph 11) and procedural-criminal law.

For factual corrections: info@licitatiimedicale.com (response within 24h).

## Related

- [Methodology document](methodology.md)
- [Anomalies dashboard](https://licitatiimedicale.com/anomalii)
- [Press kit for journalists](https://licitatiimedicale.com/presa)
- [Free price-check calculator (Tukey IQR)](https://licitatiimedicale.com/verifica-pret)

## Contact

- **Email:** info@licitatiimedicale.com
- **Web:** https://licitatiimedicale.com
- **Press kit:** https://licitatiimedicale.com/presa

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).
You are free to share and adapt the material for any purpose, including commercial, with attribution.
