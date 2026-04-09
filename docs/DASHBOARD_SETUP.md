# Dashboard Setup Instructions

## Required Files

To use the current dashboard locally, keep the package structure intact:

```
pricing-test-results/
├── dashboard/
│   ├── pricing_dashboard_v2.html
│   ├── dashboard_data_poor_region.csv
│   ├── dashboard_data_rich_region.csv
│   ├── dashboard_data_poor_region_android.csv
│   ├── dashboard_data_rich_region_android.csv
│   └── daily_cvr_*_mar19.csv
└── reports/
    └── test_report_*.md
```

The dashboard should be served from the package root so report links can resolve correctly.

## Local Server

```bash
cd /Users/ardittrikshiqi/Desktop/pricing-test-results
python3 -m http.server 8000
```

Then open:

```
http://localhost:8000/dashboard/pricing_dashboard_v2.html
```

## What the dashboard now shows

- Segment-level all-user CVR and revenue views
- Daily CVR through the clean March 19 cutoff
- January 30 removed as a mixed transition day
- Event timing embedded directly in the chart
- No purchase-type CVR filter

## Common Issues

### Could not load dashboard files
Make sure you opened the dashboard through a local server from the package root, not by double-clicking the HTML file directly.

### Open report returns 404
This usually means the server was started from the `dashboard/` folder instead of the package root.

### Chart looks compressed on first load
Refresh once after the server starts. If it still happens, interact with the chart once and the layout should recalculate.
