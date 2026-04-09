# Pricing V2 — Project Context for Claude

## What this project is
This is a working copy of the dua.com male pricing A/B test dashboard, duplicated from `pricing-test-results/` (the Codex-generated original). All development happens here. The original is left untouched.

## Owner
Ardit Trikshiqi — Monetization Lead, dua.com

## Project structure
```
pricing-v2/
├── dashboard/          ← All HTML dashboards + CSV/JSON data files
│   ├── age_anchor_analysis.html      ← Active dashboard (localhost:8002)
│   ├── age_anchor_analysis.json      ← Data for age anchor dashboard
│   ├── age_anchor_heatmaps.html
│   ├── pricing_dashboard_v2.html     ← Main A/B test dashboard
│   ├── segment_metrics_v2.json       ← Pre-aggregated metrics cache
│   ├── dashboard_data_*.csv          ← Daily time-series per segment
│   └── daily_cvr_*_mar19.csv         ← Accurate daily CVR per segment
└── scripts/            ← Python scripts that generate the data files
    ├── rebuild_canonical_metrics.py  ← MASTER script: runs all segments, outputs dashboard CSVs + segment_metrics_v2.json
    ├── build_age_anchor_analysis.py  ← Outputs age_anchor_analysis.json
    ├── rebuild_ios_mid_dev_rich_dec19.py
    ├── rebuild_android_poor_three_periods.py
    ├── rebuild_android_mid_three_periods.py
    ├── rebuild_android_dev_three_periods.py
    ├── rebuild_android_rich_dec19.py
    ├── rebuild_dashboard_revenue_and_duration.py
    └── store_currency_rates.json
```

## Raw data
- **Primary CSV:** `/Users/ardittrikshiqi/Desktop/pricing-test-results/pricing_matrix_inc_store_country.csv`
- **Currency rates:** `scripts/store_currency_rates.json`
- The raw CSV is shared with the original project — do NOT modify it.

## Test overview
- **Platform:** dua.com (Albanian dating app), male users only
- **Segments:** iOS Poor, iOS Rich, iOS Mid, iOS Dev, Android Poor, Android Rich, Android Mid, Android Dev
- **Test window:** Dec 19, 2025 – Mar 19, 2026 (Mar 20–24 excluded: Ramadan promo contamination)
- **Jan 30 excluded:** pricing transition day
- **Two periods:**
  - Period 1: Dec 19 – Jan 29
  - Period 2: Jan 31 – Mar 19

## How to regenerate data files
```bash
cd /Users/ardittrikshiqi/Desktop/pricing-v2/scripts

# Regenerate all dashboard CSVs + segment_metrics_v2.json
python3 rebuild_canonical_metrics.py

# Regenerate age_anchor_analysis.json
python3 build_age_anchor_analysis.py
```
Requires: `pip install pandas pycountry`

## How to serve the dashboard locally
```bash
cd /Users/ardittrikshiqi/Desktop/pricing-v2
python3 -m http.server 8002
# Open: http://localhost:8002/dashboard/age_anchor_analysis.html
```

## Key rules
- This is a **read-only data project** — dashboards consume static CSV/JSON files, no backend
- Do NOT modify anything in `pricing-test-results/` — that is the Codex original
- The active dashboard being worked on is `age_anchor_analysis.html`
- Revenue uses EUR, converted from local prices via `store_currency_rates.json`
- CVR = unique converters / unique users (not events / exposures)
- Always normalize period comparisons by Revenue/User/Day (periods have different lengths)
