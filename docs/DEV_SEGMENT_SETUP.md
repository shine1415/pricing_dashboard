# DEV Segment Setup

Files created:
- dashboard/dashboard_data_dev_region.csv
- dashboard/dashboard_data_dev_region_android.csv
- dashboard/daily_cvr_ios_dev_mar19.csv
- dashboard/daily_cvr_android_dev_mar19.csv

Logic used:
- Period 1: 2026-01-12 to 2026-01-29
- Jan 30 removed
- Period 2: 2026-01-31 to 2026-03-19
- DEV uses `abchosen = 2` in Period 1 and `abchosen = 1` in Period 2
- Period 1 keeps A/B groups from `ab_type`
- Period 2 is aggregated into one production group: `P`
- Revenue is derived from actual converted `product_id` SKU values

Observed Period 1 ladders (apval,bpval):

## IOS
- Age 18: A 18 | B 19
- Age 19: A 19 | B 20
- Age 20: A 20 | B 21
- Age 21: A 21 | B 22
- Age 22: A 22 | B 23
- Age 23: A 23 | B 24
- Age 24: A 24 | B 25
- Age 25: A 25 | B 26
- Age 26: A 26 | B 27
- Age 27: A 27 | B 28
- Age 28: A 28 | B 29
- Age 29: A 29 | B 30
- Age 30: A 30 | B 31
- Age 31: A 31 | B 32
- Age 32: A 32 | B 33
- Age 33: A 33 | B 34
- Age 34: A 34 | B 35
- Age 35: A 35 | B 36
- Age 36: A 36 | B 37
- Age 37: A 37 | B 38
- Age 38: A 38 | B 39
- Age 39: A 39 | B 40
- Age 40: A 40 | B 41

Observed Period 2 production SKU mode by age (ios):
- Age 18: P19
- Age 19: P20
- Age 20: P21
- Age 21: P22
- Age 22: P23
- Age 23: P24
- Age 24: P19
- Age 25: P25
- Age 26: P26
- Age 27: P27
- Age 28: P28
- Age 29: P29
- Age 30: P30
- Age 31: P31
- Age 32: P32
- Age 33: P33
- Age 34: P34
- Age 35: P35
- Age 36: P36
- Age 37: P37
- Age 38: P38
- Age 39: P39
- Age 40: P41

## ANDROID
- Age 18: A 13 | B 9
- Age 19: A 14 | B 10
- Age 20: A 15 | B 11
- Age 21: A 16 | B 12
- Age 22: A 17 | B 13
- Age 23: A 18 | B 14
- Age 24: A 19 | B 15
- Age 25: A 20 | B 16
- Age 26: A 21 | B 17
- Age 27: A 22 | B 18
- Age 28: A 23 | B 19
- Age 29: A 24 | B 20
- Age 30: A 25 | B 21
- Age 31: A 26 | B 22
- Age 32: A 27 | B 23
- Age 33: A 28 | B 24
- Age 34: A 29 | B 25
- Age 35: A 30 | B 26
- Age 36: A 31 | B 27
- Age 37: A 32 | B 28
- Age 38: A 33 | B 29
- Age 39: A 34 | B 30
- Age 40: A 35 | B 30

Observed Period 2 production SKU mode by age (android):
- Age 18: P9
- Age 19: P10
- Age 20: P11
- Age 21: P12
- Age 22: P10
- Age 23: P18
- Age 24: P19
- Age 25: P20
- Age 26: P21
- Age 27: P18
- Age 28: P19
- Age 29: P20
- Age 30: P21
- Age 31: P22
- Age 32: P23
- Age 33: P24
- Age 34: P19
- Age 35: P25
- Age 36: P26
- Age 37: P27
- Age 38: P28
- Age 39: P29
- Age 40: P29
