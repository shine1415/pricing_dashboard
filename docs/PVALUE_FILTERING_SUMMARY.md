# P-Value Filtering Update Summary

**Date:** March 26, 2026  
**Change:** Filtered data to include ONLY users with correct P-values

---

## What Changed

### Previous Calculation (All Data)
Included all users in the test, even those with mismatched P-values (where `ct_p_value` didn't match `apval` or `bpval`).

### New Calculation (Correct P-Values Only)
Only includes users where the P-value they saw matched their assigned test group's pricing.

---

## Why This Matters

**Wrong P-values = Test Contamination**

When a user has a "wrong" P-value, it means:
- They saw incorrect pricing for their test group
- Backend error or race condition occurred
- User switched between test groups mid-session
- Data quality issue

Including these users distorts the test results because they didn't experience the intended pricing.

---

## Impact on Numbers

### Poor Region (Male | iOS | Poor)

| Metric | All Data | Correct P-Values Only | Change |
|--------|----------|----------------------|--------|
| **Group A Exposures** | 7,301 | 7,246 | -55 (-0.8%) |
| **Group A Converters** | 787 | 755 | -32 (-4.1%) |
| **Group A CVR** | 10.78% | 10.42% | -0.36pp |
| **Group B Exposures** | 7,293 | 7,209 | -84 (-1.2%) |
| **Group B Converters** | 884 | 855 | -29 (-3.3%) |
| **Group B CVR** | 12.12% | 11.86% | -0.26pp |
| **CVR Lift** | +12.4% | +13.8% | +1.4pp |

**Revenue Impact:**
- Group A: €4,972 (correct P-values only)
- Group B: €5,810 (correct P-values only)

### Rich Region (Male | iOS | Rich)

| Metric | All Data | Correct P-Values Only | Change |
|--------|----------|----------------------|--------|
| **Group A Exposures** | 4,083 | 4,052 | -31 (-0.8%) |
| **Group A Converters** | 811 | 801 | -10 (-1.2%) |
| **Group A CVR** | 19.86% | 19.77% | -0.09pp |
| **Group B Exposures** | 4,101 | 4,042 | -59 (-1.4%) |
| **Group B Converters** | 910 | 884 | -26 (-2.9%) |
| **Group B CVR** | 22.19% | 21.87% | -0.32pp |
| **CVR Lift** | +11.7% | +10.6% | -1.1pp |

**Revenue Impact:**
- Group A: €22,908 (FX-corrected, correct P-values)
- Group B: €23,220 (FX-corrected, correct P-values)

---

## Data Quality Breakdown

### Users Excluded (Wrong P-Values)

**Poor Region:**
- Group A: 55 users (0.8% of exposures)
  - 32 had converted with wrong pricing
- Group B: 84 users (1.2% of exposures)
  - 29 had converted with wrong pricing

**Rich Region:**
- Group A: 31 users (0.8% of exposures)
  - 10 had converted with wrong pricing
- Group B: 59 users (1.4% of exposures)
  - 26 had converted with wrong pricing

**Total Excluded:** 229 users across both regions

---

## Final Correct Metrics

### Poor Region
- **Group A:** 10.42% CVR (755 / 7,246) | €4,972 revenue
- **Group B:** 11.86% CVR (855 / 7,209) | €5,810 revenue
- **Winner:** Group B (+13.8% CVR, +16.9% revenue)

### Rich Region
- **Group A:** 19.77% CVR (801 / 4,052) | €22,908 revenue
- **Group B:** 21.87% CVR (884 / 4,042) | €23,220 revenue
- **Winner:** Group B (+10.6% CVR, +1.4% revenue)

---

## Files Updated

1. ✅ `dashboard_data_poor_region.csv` - Poor Region (filtered)
2. ✅ `dashboard_data_rich_region.csv` - Rich Region (filtered)
3. ✅ `pricing_dashboard_v2.html` - Updated user counts (7,246/7,209 and 4,052/4,042)
4. ⏳ Reports need updating with correct CVR numbers

---

## Next Steps

**Reports to Update:**
1. `test_report_male_ios_poor.md` - Update CVR from 10.86%/12.26% to 10.42%/11.86%
2. `test_report_male_ios_rich.md` - Update CVR from 19.86%/22.19% to 19.77%/21.87%

**Dashboard:**
- Already updated with correct unique exposure numbers
- Will calculate CVR accurately when loaded

---

## Technical Notes

**P-Value Validation Logic:**
```python
def check_p_value(row):
    if row['ab_type'] == 'A':
        return row['ct_p_value'] == row['apval']
    elif row['ab_type'] == 'B':
        return row['ct_p_value'] == row['bpval']
    return False
```

**Why Group B Has More Wrong P-Values:**
Group B in both regions had more users with wrong P-values (59 vs 31 in Rich, 84 vs 55 in Poor). This suggests:
- Backend issues affected Group B more
- Or Group B had more complex pricing logic prone to errors

**Impact on Test Validity:**
The filtering strengthens test validity by ensuring all users experienced their intended pricing. The small percentage (<2%) of excluded users doesn't materially change conclusions, but provides more accurate metrics.
