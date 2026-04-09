# 📦 Pricing A/B Test - Complete File Package

**Test:** Male | iOS | Poor Region & Rich Region  
**Period:** January 12 - March 24, 2026 (71 days)  
**Data Quality:** Filtered for correct P-values only

---

## 🎯 REQUIRED FILES (For Dashboard to Work)

### **Download these 3 files and put in the same folder:**

1. **pricing_dashboard_v2.html** ← The interactive dashboard
2. **dashboard_data_poor_region.csv** ← Poor Region data (7,246 A / 7,209 B)
3. **dashboard_data_rich_region.csv** ← Rich Region data (4,052 A / 4,042 B)

**Then:** serve the package root locally and open `dashboard/pricing_dashboard_v2.html`

---

## 📊 SUMMARY FILES (Quick Reference)

### **For quick metrics overview - open in Excel/Sheets:**

4. **test_summary_metrics.csv**
   - Key metrics for both regions side-by-side
   - CVR, revenue, lifts, recommendations
   - Data quality notes

5. **test_comparison_summary.csv**
   - Clean A vs B comparison table
   - Both Poor and Rich regions
   - Optimal pricing per region

6. **test_period_breakdown.csv**
   - Period 1 vs Period 2 results
   - Sequential test structure
   - CVR progression by period

---

## 📄 FULL REPORTS (Detailed Analysis)

### **Complete test analysis - open in any markdown reader:**

7. **test_report_male_ios_poor.md**
   - Full Poor Region analysis
   - Test design, results, recommendations
   - Age cohorts, external factors, revenue analysis
   - **Recommendation:** Adopt P5-P28 pricing (€2.49-€13.99 weekly)

8. **test_report_male_ios_rich.md**
   - Full Rich Region analysis
   - Test design, results, recommendations
   - Currency breakdown (FX-corrected)
   - **Recommendation:** Adopt P18-P40 pricing (€8.99-€19.99 weekly)

---

## 📖 DOCUMENTATION

9. **PVALUE_FILTERING_SUMMARY.md**
   - Explains P-value filtering (why 229 users excluded)
   - Before/after comparison
   - Data quality breakdown

10. **DASHBOARD_SETUP.md**
    - Dashboard installation instructions
    - Troubleshooting guide
    - Browser compatibility notes

---

## 📁 RECOMMENDED FOLDER STRUCTURE

```
pricing-test-results/
│
├── 🎯 DASHBOARD (3 files - required to work together)
│   ├── pricing_dashboard.html
│   ├── dashboard_data_poor_region.csv
│   └── dashboard_data_rich_region.csv
│
├── 📊 SUMMARIES (3 CSV files - open in Excel)
│   ├── test_summary_metrics.csv
│   ├── test_comparison_summary.csv
│   └── test_period_breakdown.csv
│
├── 📄 REPORTS (2 detailed reports)
│   ├── test_report_male_ios_poor.md
│   └── test_report_male_ios_rich.md
│
└── 📖 DOCS (2 reference docs)
    ├── PVALUE_FILTERING_SUMMARY.md
    └── DASHBOARD_SETUP.md
```

---

## ✅ FINAL METRICS (Correct P-Values Only)

### Poor Region (Male | iOS | Poor)
- **Sample:** 7,246 A / 7,209 B unique users
- **CVR:** 10.42% A / 11.86% B → **+13.8% lift**
- **Revenue:** €4,972 A / €5,810 B → **+16.9% lift**
- **Winner:** Group B (P5-P28 pricing)
- **Recommendation:** €2.49-€13.99 weekly by age

### Rich Region (Male | iOS | Rich)
- **Sample:** 4,052 A / 4,042 B unique users
- **CVR:** 19.77% A / 21.87% B → **+10.6% lift**
- **Revenue:** €22,908 A / €23,220 B → **+1.4% lift**
- **Winner:** Group B (P18-P40 pricing)
- **Recommendation:** €8.99-€19.99 weekly by age

---

## 🚀 QUICK START

### Option 1: View Dashboard
1. Download 3 dashboard files
2. Put in same folder
3. Open `pricing_dashboard.html`
4. Select Poor or Rich region from dropdown

### Option 2: View Summaries
1. Download the 3 CSV summaries
2. Open in Excel or Google Sheets
3. Quick metrics at a glance

### Option 3: Read Full Reports
1. Download the 2 markdown reports
2. Open in any text editor or markdown viewer
3. Complete analysis with recommendations

---

## ⚠️ IMPORTANT NOTES

**Data Quality:**
- All files filtered for correct P-values only
- Excludes 229 users (139 Poor, 90 Rich) with pricing mismatches
- This gives true conversion rates for users who saw correct pricing

**Dashboard:**
- Requires all 3 files in same folder
- If browser blocks: `python3 -m http.server 8000`
- Then open: `http://localhost:8000/dashboard/pricing_dashboard_v2.html`

**CSVs:**
- Use UTF-8 encoding
- Compatible with Excel, Google Sheets, Numbers
- Dashboard CSVs have 4,659 (Poor) and 4,916 (Rich) rows

**Reports:**
- Markdown format (.md)
- View in GitHub, VS Code, Typora, or any text editor
- Contains complete analysis with recommendations

---

## 📞 SUPPORT

If you have questions about:
- **Dashboard not loading:** Check DASHBOARD_SETUP.md
- **Data filtering:** Check PVALUE_FILTERING_SUMMARY.md
- **Metrics:** Check test_summary_metrics.csv
- **Full analysis:** Check the two test_report_*.md files

---

**Package Created:** March 26, 2026  
**Test Period:** Jan 12 - Mar 19, 2026, with Jan 30 removed (66 analyzed days)  
**Status:** ✅ Ready for Implementation
