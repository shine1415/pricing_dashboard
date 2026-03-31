# Pricing A/B Test Results
**Segment:** Male | iOS | Poor Region & Rich Region
**Period:** January 12 – March 19, 2026, with January 30 removed (66 analyzed days)
**Author:** Ardit (Monetization Lead, dua.com)
**Status:** Ready for Implementation

---

## Folder Structure

```
pricing-test-results/
├── README.md                        ← You are here
├── dashboard/                       ← Interactive dashboard and CSV inputs
│   ├── pricing_dashboard_v2.html
│   ├── dashboard_data_poor_region.csv
│   ├── dashboard_data_rich_region.csv
│   ├── dashboard_data_poor_region_android.csv
│   ├── dashboard_data_rich_region_android.csv
│   └── daily_cvr_*_mar19.csv
├── summaries/                       ← Quick-reference CSV files (open in Excel/Sheets)
│   ├── test_summary_metrics.csv
│   ├── test_comparison_summary.csv
│   ├── test_period_breakdown.csv
│   ├── test_metrics_complete.csv
│   └── repeat_purchase_analysis.csv
├── reports/                         ← Full written analysis per region
│   ├── test_report_male_ios_poor.md
│   └── test_report_male_ios_rich.md
└── docs/                            ← Reference documentation
    ├── FILE_PACKAGE_GUIDE.md
    ├── PVALUE_FILTERING_SUMMARY.md
    └── DASHBOARD_SETUP.md
```

---

## File Descriptions

### Dashboard (`/dashboard`)

| File | Description |
|------|-------------|
| `pricing_dashboard_v2.html` | Interactive chart dashboard. Filter by segment, age, metric, and smoothing. Event timing is embedded in the chart. |
| `dashboard_data_poor_region.csv` | Daily time-series data for Poor Region (Albania, Kosovo, Bosnia, etc.) — 14,455 users |
| `dashboard_data_rich_region.csv` | Daily time-series data for Rich Region (Germany, US, UK, Switzerland, etc.) — 8,094 users |

### Summaries (`/summaries`)

| File | Description |
|------|-------------|
| `test_summary_metrics.csv` | Side-by-side key metrics for both regions: CVR, revenue, lifts, data quality, recommendations |
| `test_comparison_summary.csv` | Clean Group A vs Group B comparison table with optimal pricing per region |
| `test_period_breakdown.csv` | Period 1 vs Period 2 results showing how CVR evolved across the sequential test |
| `test_metrics_complete.csv` | Complete metrics dataset covering all dimensions of the test |
| `repeat_purchase_analysis.csv` | Breakdown of activation vs reactivation purchase types |

### Reports (`/reports`)

| File | Description |
|------|-------------|
| `test_report_male_ios_poor.md` | Full analysis for Poor Region: test design, age cohort breakdown, external contamination, revenue analysis, and final recommendation |
| `test_report_male_ios_rich.md` | Full analysis for Rich Region: test design, price elasticity, currency/FX breakdown, cross-region comparison, and final recommendation |

### Docs (`/docs`)

| File | Description |
|------|-------------|
| `FILE_PACKAGE_GUIDE.md` | Overview of all files in this package and how to use them |
| `PVALUE_FILTERING_SUMMARY.md` | Explains why 229 users were excluded (incorrect P-value assignments) and impact on metrics |
| `DASHBOARD_SETUP.md` | Step-by-step dashboard setup, browser troubleshooting, and Python server fallback |

---

## How to Use the Dashboard

The dashboard HTML and its CSV files should stay inside the `/dashboard` folder, and reports should stay in `/reports` if you want report links to work when serving the package root locally.

**Option A — Direct open (usually works in Chrome):**
1. Open the `dashboard/` folder
2. Start a simple local server from the package root
3. Open `dashboard/pricing_dashboard_v2.html` in the browser

**Option B — Local server (if browser blocks local file access):**
```bash
cd /path/to/pricing-test-results
python3 -m http.server 8000
# Then open: http://localhost:8000/dashboard/pricing_dashboard_v2.html
```

**Dashboard features:**
- Switch between Poor Region and Rich Region
- Filter by age group (All, 18-21, 22-24, 25-29, 30-34, 35-40)
- Select metric (CVR, Revenue/User, etc.)
- Apply 7-day or 14-day moving average smoothing
- Read fixed event timing directly inside the chart timeline

---

## Key Findings

### Test Structure

The test ran in two sequential periods for both regions:

- **Period 1 (Jan 12–29, 18 days):** Established a baseline and tested the opening price ladders
- **Jan 30:** Removed as a mixed pricing-transition day
- **Period 2 (Jan 31–Mar 19, 48 days):** Clean post-change measurement window

### Poor Region Results

| Metric | Group A | Group B | Winner |
|--------|---------|---------|--------|
| CVR | 10.47% | 11.93% | B (+14.0%) |
| Revenue/User | €0.70 | €0.81 | B (+16.1%) |

- **Period 1:** Dropping from high (P14–P36) to moderate prices (P5–P28) → **+50.6% CVR lift**
- **Period 2:** Dropping further to even lower prices → only **+4.7% CVR**, with revenue loss
- **Conclusion:** Diminishing returns set in — moderate pricing is the sweet spot

**Recommended pricing (P5–P28):**

| Age | Weekly | Monthly |
|-----|--------|---------|
| 18–21 | €2.49 | €4.99 |
| 22–24 | €4.99 | €9.99 |
| 25–29 | €6.99 | €13.99 |
| 30–34 | €9.99 | €19.99 |
| 35–40 | €13.99 | €27.99 |

### Rich Region Results

| Metric | Group A | Group B | Winner |
|--------|---------|---------|--------|
| CVR | 19.63% | 21.96% | B (+11.9%) |
| Revenue/User | €1.51 | €1.67 | B (+10.6%) |

- **Period 1:** Testing high vs slightly higher prices → negligible difference (-4.3%)
- **Period 2:** Dropping 13–38% → **+16.5% CVR** AND **+1% revenue** (win-win)
- **Conclusion:** Rich Region is more price-sensitive than expected — lower prices improve both conversion and revenue

**Recommended pricing (P18–P40):**

| Age | Weekly | Monthly |
|-----|--------|---------|
| 18–21 | €8.99–€10.49 | €17.99–€20.99 |
| 22–24 | €10.99–€11.99 | €21.99–€23.99 |
| 25–29 | €12.49–€14.49 | €24.99–€28.99 |
| 30–34 | €14.99–€16.99 | €29.99–€33.99 |
| 35–40 | €17.49–€19.99 | €34.99–€39.99 |

### Cross-Region Comparison

| Metric | Poor Region | Rich Region |
|--------|-------------|-------------|
| Optimal CVR | 11.93% | 21.96% |
| Revenue/User | €0.81 | €1.67 |
| Price multiplier | 1x | ~3.6x higher |
| Price sensitivity | High (elasticity –1.8) | Moderate (elasticity –1.2) |

### External Contamination

Both regions were affected by multiple events that suppressed conversion rates:

| Event | Duration | Impact |
|-------|----------|--------|
| Female UX Issue | Jan 14–30 (17 days) | Negative — reduced male engagement |
| Profile Builder v5.0.0 | Jan 19–Mar 19 | Mixed — free likes reduced urgency to convert |
| Paywall Experiment | Feb 4–15 (12 days) | Negative — paywall fatigue |
| Free Female Premium | Feb 10–17 (8 days) | Mixed — more matches, less conversion urgency |
| Ramadan | Feb 17–Mar 20 (31 days) | Negative for Poor Region only (Albania, Kosovo) |
| Promotional Offers | Mar 20–24 (5 days) | Severe — excluded from clean analysis |

Even with multiple time-based events, the pricing signal remains interpretable because both groups were exposed to the same calendar effects. The clean production view excludes Jan 30 and Mar 20-24.

---

## Data Quality Notes

- **229 users excluded** across both regions due to P-value mismatches (incorrect pricing assignments)
  - Poor Region: 139 excluded (0.8% A / 1.2% B)
  - Rich Region: 90 excluded (0.8% A / 1.4% B)
- All metrics in this package reflect **correct P-value users only**
- See `docs/PVALUE_FILTERING_SUMMARY.md` for full details

---

*Report Prepared: March 26, 2026*
