#!/usr/bin/env python3

import csv
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

try:
    import pycountry
except Exception:
    pycountry = None


RAW_CSV = Path("/Users/ardittrikshiqi/Desktop/pricing-test-results/pricing_matrix_inc_store_country.csv")
DASHBOARD_DIR = Path("/Users/ardittrikshiqi/Desktop/pricing-test-results/dashboard")
SUMMARY_JSON = DASHBOARD_DIR / "segment_metrics_v2.json"
RATES_JSON = Path("/Users/ardittrikshiqi/Documents/New project/store_currency_rates.json")
HELPER_SCRIPT = Path("/Users/ardittrikshiqi/Documents/New project/rebuild_dashboard_revenue_and_duration.py")

ns = {}
exec(HELPER_SCRIPT.read_text(), ns)
PRODUCT_MAPPING = ns["PRODUCT_MAPPING"]
convert_nominal_price_to_eur = ns["convert_nominal_price_to_eur"]


DURATIONS = ["All", "Weekly", "Monthly", "3 Months"]
DURATION_FROM_MAPPING = {
    "weekly": "Weekly",
    "monthly": "Monthly",
    "3months": "3 Months",
}
EXCLUDED_DATES = {date(2026, 1, 13), date(2026, 1, 30)}
ISO3_MANUAL = {
    "XKS": "Kosovo",
    "GBR": "United Kingdom",
    "USA": "United States",
    "CHE": "Switzerland",
    "DEU": "Germany",
    "AUT": "Austria",
    "BEL": "Belgium",
    "HRV": "Croatia",
    "MKD": "North Macedonia",
    "ALB": "Albania",
    "SRB": "Serbia",
    "MNE": "Montenegro",
    "SVN": "Slovenia",
    "GRC": "Greece",
    "ITA": "Italy",
    "SWE": "Sweden",
    "DNK": "Denmark",
    "BIH": "Bosnia and Herzegovina",
    "EGY": "Egypt",
    "KAZ": "Kazakhstan",
    "FRA": "France",
}


def p(n):
    return f"P{n}"


PERIODS = {
    "period1": {
        "start": date(2025, 12, 19),
        "end": date(2026, 1, 12),
        "expected": {age: (p(age - 7), p(age - 6)) for age in range(18, 41)},
    },
    "period2": {
        "start": date(2026, 1, 14),
        "end": date(2026, 1, 29),
        "expected": {age: (p(age - 7), p(age - 9 if age < 40 else 30)) for age in range(18, 41)},
    },
    "period3": {
        "start": date(2026, 1, 31),
        "end": date(2026, 3, 19),
        "production": {age: p(age - 9 if age < 40 else 30) for age in range(18, 41)},
    },
}


def country_from_store_code(code):
    code = (code or "").strip().upper()
    if not code:
        return None
    if code in ISO3_MANUAL:
        return ISO3_MANUAL[code]
    if pycountry:
        match = pycountry.countries.get(alpha_3=code)
        if match:
            return match.name
    return None


def parse_date(value):
    return datetime.strptime((value or "").strip(), "%d.%m.%Y").date()


def determine_period(day):
    for period_name, cfg in PERIODS.items():
        if cfg["start"] <= day <= cfg["end"]:
            return period_name, cfg
    return None, None


def empty_bucket():
    return {"users": set(), "converters": set(), "conversion_events": 0, "revenue": 0.0}


def finalize_bucket(bucket, days):
    users = len(bucket["users"])
    converters = len(bucket["converters"])
    revenue = round(bucket["revenue"], 2)
    conversion_events = bucket["conversion_events"]
    cvr = (converters / users * 100) if users else 0
    rev_per_user = (revenue / users) if users else 0
    rev_per_user_day = (rev_per_user / days) if users else 0
    return {
        "users": users,
        "converters": converters,
        "conversion_events": conversion_events,
        "cvr": round(cvr, 4),
        "revenue": revenue,
        "revPerUser": round(rev_per_user, 4),
        "revPerUserDay": round(rev_per_user_day, 4),
    }


def main():
    rates = json.loads(RATES_JSON.read_text())
    daily = defaultdict(empty_bucket)
    summary = defaultdict(empty_bucket)
    first_date = min(cfg["start"] for cfg in PERIODS.values())
    last_date = max(cfg["end"] for cfg in PERIODS.values())
    total_days = (last_date - first_date).days + 1 - len(EXCLUDED_DATES)

    with RAW_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row.get("gender") or "").strip().lower() not in {"m", "male"}:
                continue
            if (row.get("os") or "").strip().lower() != "android":
                continue
            if (row.get("region") or "").strip().lower() != "mid":
                continue

            row_date = parse_date(row.get("date"))
            if row_date in EXCLUDED_DATES:
                continue

            period_name, period_cfg = determine_period(row_date)
            if not period_name:
                continue

            age_raw = (row.get("age") or "").strip()
            if not age_raw.isdigit():
                continue
            age = int(age_raw)
            if age < 18 or age > 40:
                continue

            apval_raw = (row.get("apval") or "").strip()
            bpval_raw = (row.get("bpval") or "").strip()
            apval = f"P{apval_raw}" if apval_raw.isdigit() else apval_raw
            bpval = f"P{bpval_raw}" if bpval_raw.isdigit() else bpval_raw

            if period_name in {"period1", "period2"}:
                expected = period_cfg["expected"].get(age)
                if not expected or (apval, bpval) != expected:
                    continue
                group = (row.get("ab_type") or "").strip()
                if group not in {"A", "B"}:
                    continue
            else:
                expected_p = period_cfg["production"].get(age)
                if not expected_p:
                    continue
                abchosen = (row.get("abchosen") or "").strip()
                if abchosen and abchosen != "1":
                    continue
                if apval != expected_p and bpval != expected_p:
                    continue
                group = "P"

            user_id = (row.get("cognito_user_id") or "").strip()
            if not user_id:
                continue

            row_date_iso = row_date.isoformat()
            for duration in DURATIONS:
                daily[(row_date_iso, str(age), group, duration)]["users"].add(user_id)
                summary[("overall", duration, group)]["users"].add(user_id)
                summary[(period_name, duration, group)]["users"].add(user_id)

            product_id = (row.get("product_id") or "").strip()
            mapping = PRODUCT_MAPPING.get(product_id)
            if not mapping:
                continue

            _, duration_key, nominal_price = mapping
            duration_label = DURATION_FROM_MAPPING[duration_key]
            country = country_from_store_code(row.get("store_country_code")) or (row.get("country") or "").strip()
            eur_price = convert_nominal_price_to_eur(nominal_price, "android", country, rates)

            for duration in ("All", duration_label):
                daily_bucket = daily[(row_date_iso, str(age), group, duration)]
                daily_bucket["conversion_events"] += 1
                daily_bucket["revenue"] += eur_price
                daily_bucket["converters"].add(user_id)

                summary[("overall", duration, group)]["conversion_events"] += 1
                summary[("overall", duration, group)]["revenue"] += eur_price
                summary[("overall", duration, group)]["converters"].add(user_id)

                summary[(period_name, duration, group)]["conversion_events"] += 1
                summary[(period_name, duration, group)]["revenue"] += eur_price
                summary[(period_name, duration, group)]["converters"].add(user_id)

    dashboard_rows = []
    for (row_date, age, group, duration), bucket in sorted(daily.items()):
        users = len(bucket["users"])
        unique_converters = len(bucket["converters"])
        conversion_events = bucket["conversion_events"]
        revenue = round(bucket["revenue"], 2)
        user_cvr = round((unique_converters / users * 100), 4) if users else 0
        revenue_per_user = round((revenue / users), 4) if users else 0
        dashboard_rows.append({
            "date": row_date,
            "age": age,
            "group": group,
            "duration": duration,
            "purchase_type": "All",
            "users": users,
            "exposures": users,
            "unique_converters": unique_converters,
            "converted_users": conversion_events,
            "events": conversion_events,
            "user_cvr": user_cvr,
            "revenue": revenue,
            "revenue_per_user": revenue_per_user,
        })

    cvr_rows = []
    daily_totals = defaultdict(empty_bucket)
    for (row_date, _age, group, duration), bucket in daily.items():
        total_bucket = daily_totals[(row_date, group, duration)]
        total_bucket["users"].update(bucket["users"])
        total_bucket["converters"].update(bucket["converters"])
        total_bucket["conversion_events"] += bucket["conversion_events"]

    for (row_date, group, duration), bucket in sorted(daily_totals.items()):
        users = len(bucket["users"])
        converters = len(bucket["converters"])
        cvr_rows.append({
            "date": row_date,
            "group": group,
            "duration": duration,
            "unique_users": users,
            "unique_converters": converters,
            "conversion_events": bucket["conversion_events"],
            "daily_cvr": round((converters / users * 100), 4) if users else 0,
        })

    payload = {
        "mode": "production",
        "overall": {},
        "periods": {"period1": {}, "period2": {}, "period3": {}},
    }

    period_days = {
        "period1": (PERIODS["period1"]["end"] - PERIODS["period1"]["start"]).days + 1,
        "period2": (PERIODS["period2"]["end"] - PERIODS["period2"]["start"]).days + 1,
        "period3": (PERIODS["period3"]["end"] - PERIODS["period3"]["start"]).days + 1,
    }

    for duration in DURATIONS:
        payload["overall"][duration] = {}
        for group in ("A", "B", "P"):
            payload["overall"][duration][group] = finalize_bucket(summary[("overall", duration, group)], total_days)

        for period_name, days in period_days.items():
            payload["periods"][period_name][duration] = {}
            groups = ("A", "B") if period_name in {"period1", "period2"} else ("P",)
            for group in groups:
                payload["periods"][period_name][duration][group] = finalize_bucket(summary[(period_name, duration, group)], days)

    with (DASHBOARD_DIR / "dashboard_data_mid_region_android.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(dashboard_rows[0].keys()))
        writer.writeheader()
        writer.writerows(dashboard_rows)

    with (DASHBOARD_DIR / "daily_cvr_android_mid_mar19.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(cvr_rows[0].keys()))
        writer.writeheader()
        writer.writerows(cvr_rows)

    summary_json = json.loads(SUMMARY_JSON.read_text())
    summary_json["mid_android"] = payload
    SUMMARY_JSON.write_text(json.dumps(summary_json, indent=2))

    print(json.dumps(payload["overall"]["All"], indent=2))


if __name__ == "__main__":
    main()
