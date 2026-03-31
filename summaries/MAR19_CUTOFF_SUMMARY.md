# Dashboard Update Summary - March 19 Cutoff

## What Changed

**Date Range:**
- OLD: Jan 12 - Mar 24, 2026 (71 days)
- NEW: Jan 12 - Mar 19, 2026 with Jan 30 removed (66 analyzed days)

**Reason:**
- Excluded Mar 20-24 due to Ramadan promotion contamination
- Excluded Jan 30 because it is a mixed transition day when pricing changed

---

## Updated Metrics (All Segments)

### iOS Poor
- **Group A:** 7,021 users | 735 converters | **10.47% CVR**
- **Group B:** 6,955 users | 830 converters | **11.93% CVR**

### iOS Rich
- **Group A:** 3,928 users | 771 converters | **19.63% CVR**
- **Group B:** 3,912 users | 859 converters | **21.96% CVR**

### Android Poor
- **Group A:** 2,449 users | 167 converters | **6.82% CVR**
- **Group B:** 2,454 users | 207 converters | **8.44% CVR**

### Android Rich
- **Group A:** 902 users | 147 converters | **16.30% CVR**
- **Group B:** 995 users | 191 converters | **19.20% CVR**

---

## Updated Period Analysis

- **Period 1:** Jan 12-29, 2026 (18 days)
- **Jan 30:** removed as a mixed pricing-transition day
- **Period 2:** Jan 31-Mar 19, 2026 (48 days)

**Ratio:** Period 2 is now **2.7x longer** than Period 1.

---

## Files Updated

### Updated dashboard inputs
1. `dashboard_data_poor_region.csv`
2. `dashboard_data_rich_region.csv`
3. `dashboard_data_poor_region_android.csv`
4. `dashboard_data_rich_region_android.csv`
5. `daily_cvr_ios_poor_mar19.csv`
6. `daily_cvr_ios_rich_mar19.csv`
7. `daily_cvr_android_poor_mar19.csv`
8. `daily_cvr_android_rich_mar19.csv`

### Updated dashboard
- `pricing_dashboard_v2.html`
  - Removes Jan 30 from analysis and chart continuity
  - Removes purchase-type filtering from CVR views
  - Keeps event timing as fixed context in the chart
  - Uses Jan 12-Mar 19 only

### Updated summaries and reports
- `complete_metrics_mar19.csv`
- all `*_mar19.md` reports

---

## Notes

- Dashboard CVR in overview and time-series should now be interpreted only as all-user CVR for the selected segment.
- Purchase type should not be used as a CVR denominator filter because it labels conversion outcomes, not exposed populations.
- Any older files that still reference Jan 12-30 as Period 1 or describe purchase-type CVR filtering are outdated.
