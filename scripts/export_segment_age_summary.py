#!/usr/bin/env python3
"""
Export: unique users, conversions, CVR per os x region x age x group
Period: Jan 31 - Mar 19 2026 (latest for all segments)
Exclusions: Jan 30 (transition), Mar 20-24 (Ramadan promo)

Method: find dominant price per (os, region, age, group), then aggregate
only users with that price — filters out carryover from earlier periods.
Production segments (mid, dev): A+B combined into group P.
"""

import csv
from collections import defaultdict, Counter
from datetime import date, datetime
from pathlib import Path

RAW_CSV     = Path("/Users/ardittrikshiqi/Desktop/pricing-test-results/pricing_matrix_inc_store_country.csv")
OUT_CSV     = Path("/Users/ardittrikshiqi/Desktop/pricing-v2/dashboard/segment_age_summary.csv")

PERIOD_START = date(2026, 1, 31)
PERIOD_END   = date(2026, 3, 19)
EXCLUDED     = {date(2026, 1, 30)} | {date(2026, 3, d) for d in range(20, 25)}

# Production segments — A/B labels irrelevant, all go into group P
PROD_SEGMENTS = {('ios','mid'), ('ios','dev'), ('android','mid'), ('android','dev')}

def parse_date(s):
    return datetime.strptime(s.strip(), "%d.%m.%Y").date()

# Pass 1: find dominant price per key
price_counts = defaultdict(Counter)   # key -> Counter{price: user_count}
user_prices  = {}                      # (uid, key) -> price seen (for consistency check)

print("Pass 1: counting prices per segment/age/group...")
with open(RAW_CSV, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            d = parse_date(row['date'])
        except Exception:
            continue
        if not (PERIOD_START <= d <= PERIOD_END) or d in EXCLUDED:
            continue

        os_    = (row['os'] or '').strip().lower()
        region = (row['region'] or '').strip().lower()
        if not os_ or region in ('', 'other'):
            continue

        try:
            age = int(float(row.get('final_age') or row.get('age') or ''))
        except Exception:
            continue
        if not (18 <= age <= 40):
            continue

        uid   = (row['cognito_user_id'] or '').strip()
        ab    = (row['ab_type'] or '').strip().upper()
        try:
            price = f"P{int(float(row['ct_p_value']))}"
        except Exception:
            continue

        group = 'P' if (os_, region) in PROD_SEGMENTS else (ab if ab in ('A','B') else 'P')
        key   = (os_, region, age, group)
        price_counts[key][price] += 1

# Dominant price per key
dominant = {k: c.most_common(1)[0][0] for k, c in price_counts.items()}

# Pass 2: aggregate users/conversions using only dominant price
users_set = defaultdict(set)
conv_set  = defaultdict(set)

print("Pass 2: aggregating users/conversions...")
with open(RAW_CSV, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            d = parse_date(row['date'])
        except Exception:
            continue
        if not (PERIOD_START <= d <= PERIOD_END) or d in EXCLUDED:
            continue

        os_    = (row['os'] or '').strip().lower()
        region = (row['region'] or '').strip().lower()
        if not os_ or region in ('', 'other'):
            continue

        try:
            age = int(float(row.get('final_age') or row.get('age') or ''))
        except Exception:
            continue
        if not (18 <= age <= 40):
            continue

        uid   = (row['cognito_user_id'] or '').strip()
        ab    = (row['ab_type'] or '').strip().upper()
        try:
            price = f"P{int(float(row['ct_p_value']))}"
        except Exception:
            continue

        converted = str(row.get('did_subscription_started', '0')).strip() == '1'
        group = 'P' if (os_, region) in PROD_SEGMENTS else (ab if ab in ('A','B') else 'P')
        key   = (os_, region, age, group)

        if price != dominant.get(key):
            continue   # skip carryover from other periods

        users_set[key].add(uid)
        if converted:
            conv_set[key].add(uid)

# Write output
print(f"Writing {OUT_CSV}...")
REGION_ORDER = ['poor', 'mid', 'dev', 'rich']

with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['os', 'region', 'age', 'group', 'price',
                     'unique_users', 'conversions', 'cvr_pct'])
    for key in sorted(users_set.keys(),
                      key=lambda k: (k[0],
                                     REGION_ORDER.index(k[1]) if k[1] in REGION_ORDER else 99,
                                     k[2], k[3])):
        os_, region, age, group = key
        price = dominant[key]
        u = len(users_set[key])
        c = len(conv_set[key])
        cvr = round(c / u * 100, 2) if u else 0.0
        writer.writerow([os_, region, age, group, price, u, c, f"{cvr}%"])

print("Done.")
