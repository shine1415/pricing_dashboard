# Dashboard File Guide for Claude Code

## File Structure Overview

### Dashboard HTML
- **pricing_dashboard.html** - Main dashboard (works for both iOS and Android)

### iOS Dashboard Data Files
**Poor Region (Albania, Kosovo, etc.):**
- `dashboard_data_poor_region.csv` - Revenue, users, events (daily aggregates)
- `daily_cvr_ios_poor.csv` - True daily CVR (unique converters/users)

**Rich Region (Germany, Austria, US, UK, etc.):**
- `dashboard_data_rich_region.csv` - Revenue, users, events (daily aggregates)
- `daily_cvr_ios_rich.csv` - True daily CVR (unique converters/users)

### Android Dashboard Data Files
**Poor Region:**
- `dashboard_data_poor_region_android.csv` - Revenue, users, events
- `daily_cvr_android_poor.csv` - True daily CVR

**Rich Region:**
- `dashboard_data_rich_region_android.csv` - Revenue, users, events
- `daily_cvr_android_rich.csv` - True daily CVR

---

## How Files Work Together

Each segment requires **TWO files**:
1. `dashboard_data_*.csv` → Revenue, users, events metrics
2. `daily_cvr_*.csv` → CVR graph (unique converters only)

**Example for iOS Poor:**
```
dashboard_data_poor_region.csv + daily_cvr_ios_poor.csv
```

---

## Key Data Points

### iOS Poor
- Group A: 7,246 users | 755 converters | 10.42% CVR
- Group B: 7,209 users | 855 converters | 11.86% CVR

### iOS Rich
- Group A: 4,052 users | 801 converters | 19.77% CVR
- Group B: 4,042 users | 884 converters | 21.87% CVR

### Android Poor
- Group A: 2,523 users | 169 converters | 6.70% CVR
- Group B: 2,541 users | 213 converters | 8.38% CVR

### Android Rich
- Group A: 919 users | 149 converters | 16.21% CVR
- Group B: 1,010 users | 194 converters | 19.21% CVR

---

## Critical Notes

**❌ Don't use these (obsolete):**
- cumulative_cvr_*.csv
- dashboard_data.csv
- dashboard_data_with_*.csv

**✅ CVR Calculation:**
- Dashboard CSV: `converted_users` = package events (NOT unique)
- Daily CVR CSV: `unique_converters` = actual unique users (CORRECT)
- Always use daily_cvr_*.csv for CVR graphs

**⚠️ Period Length:**
- Period 1: 18 days (Jan 12-29)
- Jan 30 removed as a mixed transition day
- Period 2: 48 days (Jan 31-Mar 19)
- Always normalize by days when comparing periods

---

## Usage for Claude Code

**When analyzing iOS Poor data:**
```python
import pandas as pd

# Load both files
revenue_data = pd.read_csv('dashboard_data_poor_region.csv')
cvr_data = pd.read_csv('daily_cvr_ios_poor.csv')

# Revenue metrics from dashboard_data
# CVR from daily_cvr
```

**When working with any segment:**
1. Identify platform (iOS/Android) and region (poor/rich)
2. Load corresponding dashboard_data_*.csv for revenue/users
3. Load corresponding daily_cvr_*.csv for true CVR
4. Use hardcoded unique converters for overall CVR calculations

**Test Period:** Jan 12 - Mar 19, 2026, with Jan 30 removed (66 analyzed days)
**Gender:** Male only
**Filters Applied:** Correct P-values only (is_correct_pvalue = True)
