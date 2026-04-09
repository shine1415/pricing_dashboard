#!/usr/bin/env python3
"""
Export: unique users, conversions, CVR per os x region x age x group
Uses identical filtering logic as build_age_anchor_analysis.py:
  - Male users only
  - Country-based region lookup (not raw region column)
  - apval/bpval expected-price matching
  - is_converted = product_id OR did_subscription_started == 1
  - Latest period per segment (Jan 31 - Mar 19 for all)
"""

import csv, sys
from collections import defaultdict
from pathlib import Path

SCRIPTS_DIR = Path("/Users/ardittrikshiqi/Desktop/pricing-v2/scripts")
sys.path.insert(0, str(SCRIPTS_DIR))

from build_age_anchor_analysis import (
    resolve_latest_assignment,
    SEGMENTS,
    LATEST_PERIOD,
    country_region,
)
from rebuild_canonical_metrics import RAW_CSV, is_converted, normalize_pvalue

OUT_CSV = Path("/Users/ardittrikshiqi/Desktop/pricing-v2/dashboard/segment_age_summary.csv")

REGION_ORDER = ['poor', 'mid', 'dev', 'rich']

SEG_TO_OS_REGION = {
    'poor':          ('ios',     'poor'),
    'mid_ios':       ('ios',     'mid'),
    'dev_ios':       ('ios',     'dev'),
    'rich':          ('ios',     'rich'),
    'android_poor':  ('android', 'poor'),
    'mid_android':   ('android', 'mid'),
    'dev_android':   ('android', 'dev'),
    'android_rich':  ('android', 'rich'),
}

users_set = defaultdict(set)
conv_set  = defaultdict(set)

print("Reading raw CSV...")
with RAW_CSV.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = (row.get('cognito_user_id') or '').strip()
        if not user_id:
            continue

        converted = is_converted(row)

        for seg_key in SEGMENTS:
            result = resolve_latest_assignment(seg_key, row)
            if not result:
                continue
            _period, group, _date, age, p_value, _src = result
            os_, region = SEG_TO_OS_REGION[seg_key]
            key = (os_, region, age, group, p_value)
            users_set[key].add(user_id)
            if converted:
                conv_set[key].add(user_id)

print(f"Writing {OUT_CSV.name}...")
with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['os', 'region', 'age', 'group', 'price',
                     'unique_users', 'conversions', 'cvr_pct'])
    for key in sorted(users_set.keys(),
                      key=lambda k: (k[0],
                                     REGION_ORDER.index(k[1]) if k[1] in REGION_ORDER else 99,
                                     k[2], k[3])):
        os_, region, age, group, p_value = key
        u = len(users_set[key])
        c = len(conv_set[key])
        cvr = round(c / u * 100, 2) if u else 0.0
        writer.writerow([os_, region, age, group, p_value, u, c, f"{cvr}%"])

print("Done.")
