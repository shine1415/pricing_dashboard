#!/usr/bin/env python3

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


RAW_CSV = Path("/Users/ardittrikshiqi/Desktop/pricing_matrix_export_data.csv")
DASHBOARD_DIR = Path("/Users/ardittrikshiqi/Desktop/pricing-test-results/dashboard")
RATES_JSON = Path("/Users/ardittrikshiqi/Documents/New project/store_currency_rates.json")


DURATION_LABELS = {
    "all": "All",
    "weekly": "Weekly",
    "monthly": "Monthly",
    "3months": "3 Months",
}

FILTERABLE_DURATIONS = ["weekly", "monthly", "3months"]
ONE_TO_ONE_CURRENCIES = {"EUR", "USD", "GBP", "CHF"}


SEGMENTS = {
    "poor": {
        "os": "ios",
        "region": "poor",
        "mode": "ab",
        "start_date": "13.1.2026",
        "data_file": "dashboard_data_poor_region.csv",
        "cvr_file": "daily_cvr_ios_poor_mar19.csv",
    },
    "rich": {
        "os": "ios",
        "region": "rich",
        "mode": "ab",
        "data_file": "dashboard_data_rich_region.csv",
        "cvr_file": "daily_cvr_ios_rich_mar19.csv",
    },
    "mid_ios": {
        "os": "ios",
        "region": "mid",
        "mode": "production",
        "data_file": "dashboard_data_mid_region.csv",
        "cvr_file": "daily_cvr_ios_mid_mar19.csv",
    },
    "android_poor": {
        "os": "android",
        "region": "poor",
        "mode": "ab",
        "start_date": "13.1.2026",
        "data_file": "dashboard_data_poor_region_android.csv",
        "cvr_file": "daily_cvr_android_poor_mar19.csv",
    },
    "android_rich": {
        "os": "android",
        "region": "rich",
        "mode": "ab",
        "data_file": "dashboard_data_rich_region_android.csv",
        "cvr_file": "daily_cvr_android_rich_mar19.csv",
    },
    "mid_android": {
        "os": "android",
        "region": "mid",
        "mode": "production",
        "start_date": "14.1.2026",
        "data_file": "dashboard_data_mid_region_android.csv",
        "cvr_file": "daily_cvr_android_mid_mar19.csv",
    },
    "dev_ios": {
        "os": "ios",
        "region": "dev",
        "mode": "production",
        "data_file": "dashboard_data_dev_region.csv",
        "cvr_file": "daily_cvr_ios_dev_mar19.csv",
    },
    "dev_android": {
        "os": "android",
        "region": "dev",
        "mode": "production",
        "start_date": "14.1.2026",
        "data_file": "dashboard_data_dev_region_android.csv",
        "cvr_file": "daily_cvr_android_dev_mar19.csv",
    },
}


PRODUCT_MAPPING = {
    "com.duaag.premium.1wk.p5": ("P5", "weekly", 2.49),
    "com.duaag.premium.1mo.p5": ("P5", "monthly", 4.99),
    "com.duaag.premium.3mo.p5": ("P5", "3months", 9.99),
    "com.duaag.premium.1wk.p6": ("P6", "weekly", 2.99),
    "com.duaag.premium.1mo.p6": ("P6", "monthly", 5.99),
    "com.duaag.premium.3mo.p6": ("P6", "3months", 11.99),
    "com.duaag.premium.1wk.p7": ("P7", "weekly", 3.49),
    "com.duaag.premium.1mo.p7": ("P7", "monthly", 6.99),
    "com.duaag.premium.3mo.p7": ("P7", "3months", 13.99),
    "com.duaag.premium.1wk.p8": ("P8", "weekly", 3.99),
    "com.duaag.premium.1mo.p8": ("P8", "monthly", 7.99),
    "com.duaag.premium.3mo.p8": ("P8", "3months", 15.99),
    "com.duaag.premium.1wk.p9": ("P9", "weekly", 4.49),
    "com.duaag.premium.1mo.p9": ("P9", "monthly", 8.99),
    "com.duaag.premium.3mo.p9": ("P9", "3months", 17.99),
    "com.duaag.premium.1wk.p10": ("P10", "weekly", 4.99),
    "com.duaag.premium.1mo.p10": ("P10", "monthly", 9.99),
    "com.duaag.premium.3mo.p10": ("P10", "3months", 19.99),
    "com.duaag.premium.1wk.p11": ("P11", "weekly", 5.49),
    "com.duaag.premium.1mo.p11": ("P11", "monthly", 10.99),
    "com.duaag.premium.3mo.p11": ("P11", "3months", 21.99),
    "com.duaag.premium.1wk.p12": ("P12", "weekly", 5.99),
    "com.duaag.premium.1mo.p12": ("P12", "monthly", 11.99),
    "com.duaag.premium.3mo.p12": ("P12", "3months", 23.99),
    "com.duaag.premium.1wk.p13": ("P13", "weekly", 6.49),
    "com.duaag.premium.1mo.p13": ("P13", "monthly", 12.99),
    "com.duaag.premium.3mo.p13": ("P13", "3months", 25.99),
    "com.duaag.premium.ks.1wk.18": ("P14", "weekly", 6.99),
    "com.duaag.premium.ks.1mo.18": ("P14", "monthly", 13.99),
    "com.duaag.premium.3mon.p14": ("P14", "3months", 27.99),
    "com.duaag.premium.ks.1wk.19": ("P15", "weekly", 7.49),
    "com.duaag.premium.ks.1mo.19": ("P15", "monthly", 14.99),
    "com.duaag.premium.ks.3mo.18": ("P15", "3months", 29.99),
    "com.duaag.premium.ks.1wk.20": ("P16", "weekly", 7.99),
    "com.duaag.premium.ks.1mo.20": ("P16", "monthly", 15.99),
    "com.duaag.premium.3mo.p16": ("P16", "3months", 31.99),
    "com.duaag.premium.ks.1wk.21": ("P17", "weekly", 8.49),
    "com.duaag.premium.ks.1mo.21": ("P17", "monthly", 16.99),
    "com.duaag.premium.3mo.p17": ("P17", "3months", 33.99),
    "com.duaag.premium.de.1wk.18": ("P18", "weekly", 8.99),
    "com.duaag.premium.de.1mo.18": ("P18", "monthly", 17.99),
    "com.duaag.premium.3mo.p18": ("P18", "3months", 35.99),
    "com.duaag.premium.de.1wk.19": ("P19", "weekly", 9.49),
    "com.duaag.premium.de.1mo.19": ("P19", "monthly", 18.99),
    "com.duaag.premium.3mo.p19": ("P19", "3months", 37.99),
    "com.duaag.premium.de.1wk.20": ("P20", "weekly", 9.99),
    "com.duaag.premium.de.1mo.20": ("P20", "monthly", 19.99),
    "com.duaag.premium.de.3mo.24": ("P20", "3months", 39.99),
    "com.duaag.premium.de.1wk.21": ("P21", "weekly", 10.49),
    "com.duaag.premium.de.1mo.21": ("P21", "monthly", 20.99),
    "com.duaag.premium.3mo.p21": ("P21", "3months", 41.99),
    "com.duaag.premium.de.1wk.22": ("P22", "weekly", 10.99),
    "com.duaag.premium.de.1mo.22": ("P22", "monthly", 21.99),
    "com.duaag.premium.3mo.p22": ("P22", "3months", 43.99),
    "com.duaag.premium.de.1wk.23": ("P23", "weekly", 11.49),
    "com.duaag.premium.de.1mo.23": ("P23", "monthly", 22.99),
    "com.duaag.premium.3mo.p23": ("P23", "3months", 45.99),
    "com.duaag.premium.de.1wk.24": ("P24", "weekly", 11.99),
    "com.duaag.premium.de.1mo.24": ("P24", "monthly", 23.99),
    "com.duaag.premium.3mo.p24": ("P24", "3months", 47.99),
    "com.duaag.premium.rich.1wk.19": ("P25", "weekly", 12.49),
    "com.duaag.premium.rich.1mo.19": ("P25", "monthly", 24.99),
    "com.duaag.premium.de.3mo.25": ("P25", "3months", 49.99),
    "com.duaag.premium.de.1wk.25": ("P26", "weekly", 12.99),
    "com.duaag.premium.de.1mo.25": ("P26", "monthly", 25.99),
    "com.duaag.premium.3mo.p26": ("P26", "3months", 51.99),
    "com.duaag.premium.de.1wk.26": ("P27", "weekly", 13.49),
    "com.duaag.premium.de.1mo.26": ("P27", "monthly", 26.99),
    "com.duaag.premium.3mo.p27": ("P27", "3months", 53.99),
    "com.duaag.premium.de.1wk.27": ("P28", "weekly", 13.99),
    "com.duaag.premium.de.1mo.27": ("P28", "monthly", 27.99),
    "com.duaag.premium.3mo.p28": ("P28", "3months", 55.99),
    "com.duaag.premium.de.1wk.28": ("P29", "weekly", 14.49),
    "com.duaag.premium.de.1mo.28": ("P29", "monthly", 28.99),
    "com.duaag.premium.3mo.p29": ("P29", "3months", 57.99),
    "com.duaag.premium.de.1wk.29": ("P30", "weekly", 14.99),
    "com.duaag.premium.de.1mo.29": ("P30", "monthly", 29.99),
    "com.duaag.premium.de.3mo.30": ("P30", "3months", 59.99),
    "com.duaag.premium.de.1wk.30": ("P31", "weekly", 15.49),
    "com.duaag.premium.de.1mo.30": ("P31", "monthly", 30.99),
    "com.duaag.premium.3mo.p31": ("P31", "3months", 61.99),
    "com.duaag.premium.de.1wk.31": ("P32", "weekly", 15.99),
    "com.duaag.premium.de.1mo.31": ("P32", "monthly", 31.99),
    "com.duaag.premium.3mo.p32": ("P32", "3months", 63.99),
    "com.duaag.premium.de.1wk.32": ("P33", "weekly", 16.49),
    "com.duaag.premium.de.1mo.32": ("P33", "monthly", 32.99),
    "com.duaag.premium.3mo.p33": ("P33", "3months", 65.99),
    "com.duaag.premium.de.1wk.33": ("P34", "weekly", 16.99),
    "com.duaag.premium.de.1mo.33": ("P34", "monthly", 33.99),
    "com.duaag.premium.3mo.p34": ("P34", "3months", 67.99),
    "com.duaag.premium.de.1wk.34": ("P35", "weekly", 17.49),
    "com.duaag.premium.de.1mo.34": ("P35", "monthly", 34.99),
    "com.duaag.premium.de.3mo.35": ("P35", "3months", 69.99),
    "com.duaag.premium.de.1wk.35": ("P36", "weekly", 17.99),
    "com.duaag.premium.de.1mo.35": ("P36", "monthly", 35.99),
    "com.duaag.premium.3mo.p36": ("P36", "3months", 71.99),
    "com.duaag.premium.3mon.p36": ("P36", "3months", 71.99),
    "com.duaag.premium.de.1wk.36": ("P37", "weekly", 18.49),
    "com.duaag.premium.de.1mo.36": ("P37", "monthly", 36.99),
    "com.duaag.premium.3mo.p37": ("P37", "3months", 73.99),
    "com.duaag.premium.de.1wk.37": ("P38", "weekly", 18.99),
    "com.duaag.premium.de.1mo.37": ("P38", "monthly", 37.99),
    "com.duaag.premium.3mo.p38": ("P38", "3months", 75.99),
    "com.duaag.premium.de.1wk.38": ("P39", "weekly", 19.49),
    "com.duaag.premium.de.1mo.38": ("P39", "monthly", 38.99),
    "com.duaag.premium.3mo.p39": ("P39", "3months", 77.99),
    "com.duaag.premium.de.1wk.39": ("P40", "weekly", 19.99),
    "com.duaag.premium.de.1mo.39": ("P40", "monthly", 39.99),
    "com.duaag.premium.3mo.p40": ("P40", "3months", 79.99),
    "com.duaag.premium.1wk.p41": ("P41", "weekly", 20.49),
    "com.duaag.premium.1mo.p41": ("P41", "monthly", 40.99),
    "com.duaag.premium.3mo.p41": ("P41", "3months", 81.99),
    "com.duaag.premium.1wk.p42": ("P42", "weekly", 20.99),
    "com.duaag.premium.1mo.p42": ("P42", "monthly", 41.99),
    "com.duaag.premium.3mo.p42": ("P42", "3months", 83.99),
    "com.duaag.premium.1wk.p43": ("P43", "weekly", 21.49),
    "com.duaag.premium.1mo.p43": ("P43", "monthly", 42.99),
    "com.duaag.premium.3mo.p43": ("P43", "3months", 85.99),
    "com.duaag.premium.1wk.p44": ("P44", "weekly", 21.99),
    "com.duaag.premium.1mo.p44": ("P44", "monthly", 43.99),
    "com.duaag.premium.3mo.p44": ("P44", "3months", 87.99),
    "com.duaag.premium.1wk.p45": ("P45", "weekly", 22.49),
    "com.duaag.premium.1mo.p45": ("P45", "monthly", 44.99),
    "com.duaag.premium.3mo.p45": ("P45", "3months", 89.99),
    "com.duaag.premium.1wk.p46": ("P46", "weekly", 22.99),
    "com.duaag.premium.1mo.p46": ("P46", "monthly", 45.99),
    "com.duaag.premium.3mo.p46": ("P46", "3months", 91.99),
}


def parse_date(value):
    return datetime.strptime(value.strip(), "%d.%m.%Y").date()


def normalize_country_name(country, os_name):
    normalized = (country or "").strip()
    mapping = {
        "United States of America": "United States",
        "South Korea": "Korea, Republic of",
        "Turkey": "Türkiye",
    }
    if os_name == "ios" and normalized == "Czechia":
        return "Czech Republic"
    return mapping.get(normalized, normalized)


def convert_nominal_price_to_eur(nominal_price, os_name, country, rates):
    platform_rates = rates.get(os_name, {})
    country_key = normalize_country_name(country, os_name)
    rate_info = platform_rates.get(country_key)
    if not rate_info:
        return nominal_price
    currency = rate_info["currency"]
    rate = float(rate_info["rate"])
    if currency in ONE_TO_ONE_CURRENCIES or not rate:
        return nominal_price
    return nominal_price / rate


def should_keep_ab_row(row):
    group = (row.get("ab_type") or "").strip()
    ct = (row.get("\ufeffct_p_value") or row.get("ct_p_value") or "").strip()
    apval = (row.get("apval") or "").strip()
    bpval = (row.get("bpval") or "").strip()
    if group == "A":
        return ct == apval and ct != ""
    if group == "B":
        return ct == bpval and ct != ""
    return False


def get_segment_group(segment_key, config, row, row_date):
    gender = (row.get("gender") or "").strip().lower()
    if gender not in {"m", "male"}:
        return None
    if row.get("os", "").lower() != config["os"]:
        return None
    if row.get("region", "").lower() != config["region"]:
        return None
    start_date = parse_date(config.get("start_date", "12.1.2026"))
    end_date = parse_date(config.get("end_date", "19.3.2026"))
    if row_date < start_date or row_date > end_date:
        return None
    if row_date == datetime(2026, 1, 30).date():
        return None

    if config["mode"] == "ab":
        if not should_keep_ab_row(row):
            return None
        return (row.get("ab_type") or "").strip()

    abchosen = (row.get("abchosen") or "").strip()
    if row_date <= datetime(2026, 1, 29).date():
        if abchosen != "2":
            return None
        return (row.get("ab_type") or "").strip()
    if row_date >= datetime(2026, 1, 31).date():
        if abchosen != "1":
            return None
        return "P"
    return None


def blank_daily_bucket():
    return {
        "users": set(),
        "conversion_events": 0,
        "revenue": 0.0,
        "unique_converters": set(),
    }


def blank_summary_bucket():
    return {
        "users": set(),
        "conversion_events": 0,
        "revenue": 0.0,
        "unique_converters": set(),
    }


def period_key_for(date_value, mode):
    if date_value <= datetime(2026, 1, 29).date():
        return "period1"
    if mode == "dev":
        return "period2"
    return "period2"


def finalize_metric(bucket, day_count):
    users = len(bucket["users"])
    unique_converters = len(bucket["unique_converters"])
    revenue = round(bucket["revenue"], 2)
    conversion_events = bucket["conversion_events"]
    cvr = (unique_converters / users * 100) if users else 0.0
    rev_per_user = (revenue / users) if users else 0.0
    rev_per_user_day = (rev_per_user / day_count) if users and day_count else 0.0
    return {
        "users": users,
        "converters": unique_converters,
        "conversion_events": conversion_events,
        "cvr": round(cvr, 4),
        "revenue": revenue,
        "revPerUser": round(rev_per_user, 4),
        "revPerUserDay": round(rev_per_user_day, 4),
    }


def main():
    rates = json.loads(RATES_JSON.read_text(encoding="utf-8"))
    daily_rows = {
        key: defaultdict(blank_daily_bucket)
        for key in SEGMENTS
    }
    daily_all_age = {
        key: defaultdict(blank_daily_bucket)
        for key in SEGMENTS
    }
    summaries = {
        key: {
            "mode": config["mode"],
            "overall": defaultdict(lambda: defaultdict(blank_summary_bucket)),
            "periods": {
                "period1": defaultdict(lambda: defaultdict(blank_summary_bucket)),
                "period2": defaultdict(lambda: defaultdict(blank_summary_bucket)),
            },
        }
        for key, config in SEGMENTS.items()
    }

    with RAW_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            date_str = (row.get("date") or "").strip()
            if not date_str:
                continue
            row_date = parse_date(date_str)
            user_id = (row.get("cognito_user_id") or "").strip()
            if not user_id:
                continue

            for segment_key, config in SEGMENTS.items():
                group = get_segment_group(segment_key, config, row, row_date)
                if group not in {"A", "B", "P"}:
                    continue

                age = int((row.get("age") or "0").strip() or 0)
                period_key = period_key_for(row_date, config["mode"])
                base_key = (row_date.isoformat(), age, group)
                all_age_key = (row_date.isoformat(), group)

                daily_rows[segment_key][(base_key + ("all",))]["users"].add(user_id)
                daily_all_age[segment_key][(all_age_key + ("all",))]["users"].add(user_id)
                summaries[segment_key]["overall"]["All"][group]["users"].add(user_id)
                summaries[segment_key]["periods"][period_key]["All"][group]["users"].add(user_id)
                for duration_key in FILTERABLE_DURATIONS:
                    duration_label = DURATION_LABELS[duration_key]
                    daily_rows[segment_key][(base_key + (duration_key,))]["users"].add(user_id)
                    daily_all_age[segment_key][(all_age_key + (duration_key,))]["users"].add(user_id)
                    summaries[segment_key]["overall"][duration_label][group]["users"].add(user_id)
                    summaries[segment_key]["periods"][period_key][duration_label][group]["users"].add(user_id)

                product_id = (row.get("product_id") or "").strip()
                mapping = PRODUCT_MAPPING.get(product_id)
                if not mapping:
                    continue

                _, duration_key, nominal_price = mapping
                eur_price = round(
                    convert_nominal_price_to_eur(
                        nominal_price,
                        config["os"],
                        row.get("country"),
                        rates,
                    ),
                    6,
                )
                duration_label = DURATION_LABELS[duration_key]

                for keyspace, row_key in (
                    (daily_rows[segment_key], base_key + (duration_key,)),
                    (daily_rows[segment_key], base_key + ("all",)),
                ):
                    keyspace[row_key]["conversion_events"] += 1
                    keyspace[row_key]["revenue"] += eur_price
                    keyspace[row_key]["unique_converters"].add(user_id)

                for keyspace, row_key in (
                    (daily_all_age[segment_key], all_age_key + (duration_key,)),
                    (daily_all_age[segment_key], all_age_key + ("all",)),
                ):
                    keyspace[row_key]["conversion_events"] += 1
                    keyspace[row_key]["revenue"] += eur_price
                    keyspace[row_key]["unique_converters"].add(user_id)

                for scope, label in (
                    ("overall", duration_label),
                    ("periods", duration_label),
                    ("overall", "All"),
                    ("periods", "All"),
                ):
                    if scope == "overall":
                        bucket = summaries[segment_key]["overall"][label][group]
                    else:
                        bucket = summaries[segment_key]["periods"][period_key][label][group]
                    bucket["conversion_events"] += 1
                    bucket["revenue"] += eur_price
                    bucket["unique_converters"].add(user_id)

    for segment_key, config in SEGMENTS.items():
        data_rows = []
        for (date_iso, age, group, duration_key), bucket in sorted(daily_rows[segment_key].items()):
            users = len(bucket["users"])
            conversion_events = bucket["conversion_events"]
            unique_converters = len(bucket["unique_converters"])
            revenue = round(bucket["revenue"], 2)
            user_cvr = (unique_converters / users * 100) if users else 0.0
            revenue_per_user = (revenue / users) if users else 0.0
            data_rows.append({
                "date": date_iso,
                "age": age,
                "group": group,
                "duration": DURATION_LABELS[duration_key],
                "purchase_type": "All",
                "users": users,
                "exposures": users,
                "unique_converters": unique_converters,
                "converted_users": conversion_events,
                "events": conversion_events,
                "user_cvr": round(user_cvr, 4),
                "revenue": revenue,
                "revenue_per_user": round(revenue_per_user, 4),
            })

        with (DASHBOARD_DIR / config["data_file"]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "date", "age", "group", "duration", "purchase_type", "users",
                    "exposures", "unique_converters", "converted_users", "events", "user_cvr",
                    "revenue", "revenue_per_user",
                ],
            )
            writer.writeheader()
            writer.writerows(data_rows)

        cvr_rows = []
        for (date_iso, group, duration_key), bucket in sorted(daily_all_age[segment_key].items()):
            users = len(bucket["users"])
            unique_converters = len(bucket["unique_converters"])
            cvr_rows.append({
                "date": date_iso,
                "group": group,
                "duration": DURATION_LABELS[duration_key],
                "unique_users": users,
                "unique_converters": unique_converters,
                "conversion_events": bucket["conversion_events"],
                "daily_cvr": round((unique_converters / users * 100) if users else 0.0, 4),
            })

        with (DASHBOARD_DIR / config["cvr_file"]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["date", "group", "duration", "unique_users", "unique_converters", "conversion_events", "daily_cvr"],
            )
            writer.writeheader()
            writer.writerows(cvr_rows)

    summary_output = {}
    for segment_key, payload in summaries.items():
        summary_output[segment_key] = {
            "mode": payload["mode"],
            "overall": {},
            "periods": {"period1": {}, "period2": {}},
        }
        segment_start_date = parse_date(SEGMENTS[segment_key].get("start_date", "12.1.2026"))
        segment_end_date = parse_date(SEGMENTS[segment_key].get("end_date", "19.3.2026"))
        overall_day_count = (segment_end_date - segment_start_date).days + 1
        if segment_start_date <= datetime(2026, 1, 30).date() <= segment_end_date:
            overall_day_count -= 1
        for duration_label, group_map in payload["overall"].items():
            summary_output[segment_key]["overall"][duration_label] = {
                group: finalize_metric(bucket, overall_day_count)
                for group, bucket in group_map.items()
            }
        for period_key, duration_map in payload["periods"].items():
            if period_key == "period1":
                day_count = (datetime(2026, 1, 29).date() - segment_start_date).days + 1
            else:
                day_count = (segment_end_date - datetime(2026, 1, 31).date()).days + 1
            for duration_label, group_map in duration_map.items():
                summary_output[segment_key]["periods"][period_key][duration_label] = {
                    group: finalize_metric(bucket, day_count)
                    for group, bucket in group_map.items()
                }

    with (DASHBOARD_DIR / "segment_metrics_v2.json").open("w", encoding="utf-8") as handle:
        json.dump(summary_output, handle, indent=2)


if __name__ == "__main__":
    main()
