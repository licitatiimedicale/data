# Methodology

This document describes the data pipeline, normalization steps, and statistical method (Tukey IQR) used by [licitatiimedicale.com](https://licitatiimedicale.com).

## 1. Data collection

### Source

Primary source: **TED — Tenders Electronic Daily**, the official Romanian-EU public procurement journal (https://ted.europa.eu). All contract award notices (Form F03 / `notice-type: "can-standard"`) are pulled via the TED Search API v3.

### CPV filter

We filter on the family **CPV 9052*** (with wildcard for subcodes):
- `90520000` — Radioactive, toxic, medical and hazardous waste services
- `90521000` — Radioactive waste services
- `90522000` — Toxic waste services
- `90523000` — Hazardous non-medical waste services
- `90524000` — Medical waste services (primary)
- `90524100` — Medical waste collection
- `90524200` — Medical waste disposal
- `90524300` — Biological waste treatment
- `90524400` — Specific medical waste services

### Country filter

All notices with `place-of-performance` country code `ROU` (Romania) are included.

### Polling cadence

Daily at 07:00 UTC. Last 2 days of TED publications are pulled and merged into the SQLite database. Initial backfill (2019-2026) was performed on 2026-06-03.

## 2. Entity resolution

Hospital names in TED are inconsistent (different capitalizations, abbreviations, city omission). We normalize:

1. **Strip diacritics, lowercase, remove punctuation**
2. **Abbreviation expansion**: `SJU` → `Spitalul Județean de Urgență`, `SCU` → `Spitalul Clinic de Urgență`, etc.
3. **City extraction**: lookup table for ~40 Romanian cities (`Bucuresti`, `Cluj-Napoca`, `Iasi`, …)
4. **Manual overrides**: for hospitals without city in title (`Matei Bals` → Bucuresti, `Marius Nasta` → Bucuresti, etc.)
5. **`entity_key`** = canonical city slug, used for cross-reference

## 3. Value normalization

### Framework vs specific contracts

TED distinguishes between:

- **Framework agreements** (`framework`): multi-year (2-4) agreements; declared value is **ceiling**, not actual spend
- **Specific contracts** (`single`): individual one-time contracts

For benchmark comparisons, we **annualize** framework values by dividing by 2 years (default duration). This avoids comparing a 4-year ceiling to a 1-month specific contract.

```python
def annualize(record):
    v = record["value_ron"]
    if record["value_type"] == "framework":
        return v / 2.0  # default 2-year duration
    return v
```

### Currency

All Romanian medical waste contracts are denominated in **RON**. The `value_currency` field is informational only.

## 4. Tukey IQR outlier detection (1977)

### Method

Following John W. Tukey's *Exploratory Data Analysis* (1977):

```
Q1   = 25th percentile of annualized values
Q3   = 75th percentile of annualized values
IQR  = Q3 - Q1

Upper threshold = Q3 + 1.5 × IQR
Lower threshold = Q1 - 1.5 × IQR

A value is an "outlier" if it falls outside [lower, upper].
```

### Implementation

```python
import statistics
all_vals = sorted([annualize(r) for r in awards if r["value_ron"] > 0])
n = len(all_vals)
q1 = all_vals[n // 4]
q3 = all_vals[3 * n // 4]
iqr = q3 - q1
upper = q3 + 1.5 * iqr
outliers = [v for v in all_vals if v > upper]
```

### Current snapshot (2026-06-03)

| Statistic | Value (RON, annualized) |
|---|---|
| N (valid values) | 173 |
| Q1 (25%) | 1,782,277 |
| Median (Q50) | 2,304,000 |
| Q3 (75%) | 3,977,424 |
| IQR | 2,195,148 |
| Upper threshold (Q3 + 1.5 × IQR) | 7,270,146 |
| **Outliers identified** | **16** |

### What an outlier means (and what it does NOT mean)

**Outlier statistic = "this value falls far from the typical distribution"**

**NOT equivalent to:**
- Fraud
- Overpricing
- Wrongdoing of any kind

**Possible legitimate causes:**
- Large hospital with high volumes
- Specific technical requirements (on-site incinerator, isolated transport)
- Geographic isolation (long-distance transport)
- Epidemiological emergency (COVID-19 era)
- Mixed services (waste + cleaning + audit bundled)
- Pricing for hazardous + radioactive waste (combined CPV)

The outlier classification is a flag for **manual verification**, not an accusation. All operators and contracting authorities mentioned retain the full presumption of innocence under Romanian Constitutional law.

## 5. Per-hospital benchmark

For each hospital page (155 in the dataset), we compute:

- Median of this hospital's annualized values
- Ratio of this hospital's median to the national median
- Number of contracts that fall above the Tukey upper threshold
- Peer comparison: top 5 hospitals in the same region by total value

Verdict categories:

| Verdict | Condition |
|---|---|
| `OUTLIER_HIGH` | At least 1 contract above Tukey threshold AND ratio_vs_national > 1.5 |
| `ABOVE_MEDIAN` | Ratio 1.2 - 1.5 |
| `NEAR_MEDIAN` | Ratio 0.8 - 1.2 |
| `BELOW_MEDIAN` | Ratio < 0.8 |
| `INSUFFICIENT_DATA` | Less than 2 contracts |

## 6. Known limitations

1. **Backfill gaps**: pre-2019 data is not in the dataset (TED v3 API limitations)
2. **Value missing**: ~30% of older records have `value_ron = NULL` (TED publication completeness varies)
3. **Joint ventures**: a contract awarded to "STERICYCLE / ECOLOGMED" is counted once for each operator if computing solo cumulative shares; we provide both individual and ecosystem analyses
4. **Currency assumption**: all values assumed RON; rare EUR-denominated contracts (mostly via EU funds) are flagged but not converted
5. **Below EU threshold**: contracts below the EU procurement threshold (~215,000 EUR) are NOT in TED. The Romanian SEAP/SICAP system includes these, but we currently only ingest TED. Local small contracts (e.g., ad-hoc, negotiated, < 135,000 RON direct award) are absent.
6. **CPV 9052 generic**: includes contracts that are not strictly "medical" (e.g., OMV Petrom industrial waste — correctly classified under 90523 but appears in 9052* wildcard). See [CPV 9052 classification guide](https://licitatiimedicale.com/cazuri/clasificare-cpv-9052-ce-include-ce-nu-include).

## 7. Reproducibility

All code is open. The TED API is open. The Tukey method is in the public domain since 1977.

To reproduce locally:

```bash
git clone https://github.com/[YOUR-USERNAME]/licitatiimedicale-data.git
pip install pandas
python3 -c "
import pandas as pd
df = pd.read_csv('data/awards.csv')
vals = df[df['value_ron'] > 0]['value_ron'].copy()
vals.loc[df['value_type'] == 'framework'] /= 2.0
vals = sorted(vals)
q1, q3 = vals[len(vals)//4], vals[3*len(vals)//4]
iqr = q3 - q1
print(f'N={len(vals)}, Q1={q1:,.0f}, Q3={q3:,.0f}, IQR={iqr:,.0f}, threshold={q3+1.5*iqr:,.0f}')
"
```

## References

- Tukey, J. W. (1977). *Exploratory Data Analysis*. Reading, MA: Addison-Wesley.
- European Union. (2024). *TED API v3 documentation*. https://ted.europa.eu
- ANAP. (2022). *Analiza Indicatorilor de Monitorizare a Eficienței Procedurilor de Achiziție Publice 2021*. https://anap.gov.ro
- Legea 98/2016 privind achizițiile publice. https://legislatie.just.ro
- Consiliul Concurenței. (2025). Decizia 100/2025 (cartel deșeuri medicale). https://www.consiliulconcurentei.ro

## Contact

- Email: info@licitatiimedicale.com
- Web: https://licitatiimedicale.com
- Methodology questions: replies in 24h
