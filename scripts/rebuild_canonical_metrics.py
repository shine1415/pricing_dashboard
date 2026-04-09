#!/usr/bin/env python3

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from rebuild_dashboard_revenue_and_duration import (
    PRODUCT_MAPPING,
    convert_nominal_price_to_eur,
)
from rebuild_ios_mid_dev_rich_dec19 import (
    ISO3_MANUAL,
    country_from_store_code,
    parse_date,
)
from rebuild_ios_mid_dev_rich_dec19 import SEGMENTS as IOS_SEGMENTS
from rebuild_android_poor_three_periods import PERIODS as ANDROID_POOR_PERIODS
from rebuild_android_mid_three_periods import PERIODS as ANDROID_MID_PERIODS
from rebuild_android_dev_three_periods import PERIODS as ANDROID_DEV_PERIODS
from rebuild_android_rich_dec19 import PERIODS as ANDROID_RICH_PERIODS


RAW_CSV = Path("/Users/ardittrikshiqi/Desktop/pricing-test-results/pricing_matrix_inc_store_country.csv")
OUTPUT_DIR = Path("/Users/ardittrikshiqi/Desktop/pricing-test-results/dashboard")
RATES_JSON = Path("/Users/ardittrikshiqi/Documents/New project/store_currency_rates.json")

DURATION_LABELS = {
    "all": "All",
    "weekly": "Weekly",
    "monthly": "Monthly",
    "3months": "3 Months",
}

FILTERABLE_DURATIONS = ("weekly", "monthly", "3months")


def normalize_pvalue(value):
    value = (value or "").strip()
    if value.isdigit():
        return f"P{value}"
    return value


def is_converted(row):
    product_id = (row.get("product_id") or "").strip()
    if product_id:
        return True
    value = str(row.get("did_subscription_started") or "").strip().lower()
    return value in {"1", "true", "yes"}


def empty_daily_bucket():
    return {
        "users": set(),
        "converters": set(),
        "conversion_events": 0,
        "revenue": 0.0,
    }


def empty_summary_bucket():
    return {
        "users": set(),
        "converters": set(),
        "conversion_events": 0,
        "revenue": 0.0,
    }


SEGMENTS = {
    "poor": {
        "os": "ios",
        "region": "poor",
        "kind": "three_ab",
        "data_file": "dashboard_data_poor_region.csv",
        "cvr_file": "daily_cvr_ios_poor_mar19.csv",
        "exclude_dates": {"12.01.2026", "30.01.2026"},
        "periods": {
            "period1": {
                "start": parse_date("19.12.2025"),
                "end": parse_date("11.01.2026"),
                "expected": {
                    18: ("P14", "P15"), 19: ("P15", "P16"), 20: ("P16", "P17"),
                    21: ("P17", "P18"), 22: ("P18", "P19"), 23: ("P19", "P20"),
                    24: ("P20", "P21"), 25: ("P21", "P22"), 26: ("P22", "P23"),
                    27: ("P23", "P24"), 28: ("P24", "P25"), 29: ("P25", "P26"),
                    30: ("P26", "P27"), 31: ("P27", "P28"), 32: ("P28", "P29"),
                    33: ("P29", "P30"), 34: ("P30", "P31"), 35: ("P31", "P32"),
                    36: ("P32", "P33"), 37: ("P33", "P34"), 38: ("P34", "P35"),
                    39: ("P35", "P36"), 40: ("P36", "P37"),
                },
            },
            "period2": {
                "start": parse_date("13.01.2026"),
                "end": parse_date("29.01.2026"),
                "expected": {
                    18: ("P14", "P5"), 19: ("P15", "P5"), 20: ("P16", "P5"),
                    21: ("P17", "P5"), 22: ("P18", "P10"), 23: ("P19", "P10"),
                    24: ("P20", "P10"), 25: ("P21", "P14"), 26: ("P22", "P14"),
                    27: ("P23", "P14"), 28: ("P24", "P14"), 29: ("P25", "P14"),
                    30: ("P26", "P20"), 31: ("P27", "P20"), 32: ("P28", "P20"),
                    33: ("P29", "P20"), 34: ("P30", "P20"), 35: ("P31", "P28"),
                    36: ("P32", "P28"), 37: ("P33", "P28"), 38: ("P34", "P28"),
                    39: ("P35", "P28"), 40: ("P36", "P28"),
                },
            },
            "period3": {
                "start": parse_date("31.01.2026"),
                "end": parse_date("19.03.2026"),
                "expected": {
                    18: ("P5", "P5"), 19: ("P5", "P5"), 20: ("P5", "P5"),
                    21: ("P5", "P5"), 22: ("P10", "P10"), 23: ("P10", "P10"),
                    24: ("P10", "P10"), 25: ("P14", "P12"), 26: ("P14", "P12"),
                    27: ("P14", "P12"), 28: ("P14", "P12"), 29: ("P14", "P12"),
                    30: ("P20", "P12"), 31: ("P20", "P12"), 32: ("P20", "P12"),
                    33: ("P20", "P12"), 34: ("P20", "P12"), 35: ("P28", "P20"),
                    36: ("P28", "P20"), 37: ("P28", "P20"), 38: ("P28", "P20"),
                    39: ("P28", "P20"), 40: ("P28", "P20"),
                },
            },
        },
    },
    "android_poor": {
        "os": "android",
        "region": "poor",
        "kind": "three_ab",
        "data_file": "dashboard_data_poor_region_android.csv",
        "cvr_file": "daily_cvr_android_poor_mar19.csv",
        "exclude_dates": {"12.01.2026", "30.01.2026"},
        "periods": {
            "period1": {
                "start": ANDROID_POOR_PERIODS["period1"]["start"],
                "end": ANDROID_POOR_PERIODS["period1"]["end"],
                "expected": ANDROID_POOR_PERIODS["period1"]["expected"],
            },
            "period2": {
                "start": ANDROID_POOR_PERIODS["period2"]["start"],
                "end": ANDROID_POOR_PERIODS["period2"]["end"],
                "expected": ANDROID_POOR_PERIODS["period2"]["expected"],
            },
            "period3": {
                "start": ANDROID_POOR_PERIODS["period3"]["start"],
                "end": ANDROID_POOR_PERIODS["period3"]["end"],
                "expected": ANDROID_POOR_PERIODS["period3"]["expected"],
            },
        },
    },
    "mid_ios": {
        "os": "ios",
        "region": "mid",
        "kind": "two_production",
        "data_file": "dashboard_data_mid_region.csv",
        "cvr_file": "daily_cvr_ios_mid_mar19.csv",
        "exclude_dates": {"30.01.2026"},
        "periods": {
            "period1": {
                "start": IOS_SEGMENTS["mid_ios"]["period1_start"],
                "end": IOS_SEGMENTS["mid_ios"]["period1_end"],
                "expected": IOS_SEGMENTS["mid_ios"]["period1_expected"],
            },
            "period2": {
                "start": IOS_SEGMENTS["mid_ios"]["period2_start"],
                "end": IOS_SEGMENTS["mid_ios"]["period2_end"],
                "production": {age: b for age, (_a, b) in IOS_SEGMENTS["mid_ios"]["period1_expected"].items()},
            },
        },
    },
    "dev_ios": {
        "os": "ios",
        "region": "dev",
        "kind": "two_production",
        "data_file": "dashboard_data_dev_region.csv",
        "cvr_file": "daily_cvr_ios_dev_mar19.csv",
        "exclude_dates": {"30.01.2026"},
        "periods": {
            "period1": {
                "start": IOS_SEGMENTS["dev_ios"]["period1_start"],
                "end": IOS_SEGMENTS["dev_ios"]["period1_end"],
                "expected": IOS_SEGMENTS["dev_ios"]["period1_expected"],
            },
            "period2": {
                "start": IOS_SEGMENTS["dev_ios"]["period2_start"],
                "end": IOS_SEGMENTS["dev_ios"]["period2_end"],
                "production": {age: b for age, (_a, b) in IOS_SEGMENTS["dev_ios"]["period1_expected"].items()},
            },
        },
    },
    "rich": {
        "os": "ios",
        "region": "rich",
        "kind": "two_ab",
        "data_file": "dashboard_data_rich_region.csv",
        "cvr_file": "daily_cvr_ios_rich_mar19.csv",
        "exclude_dates": {"30.01.2026"},
        "periods": {
            "period1": {
                "start": IOS_SEGMENTS["rich"]["period1_start"],
                "end": IOS_SEGMENTS["rich"]["period1_end"],
                "expected": IOS_SEGMENTS["rich"]["period1_expected"],
            },
            "period2": {
                "start": IOS_SEGMENTS["rich"]["period2_start"],
                "end": IOS_SEGMENTS["rich"]["period2_end"],
                "expected": IOS_SEGMENTS["rich"]["period2_expected"],
            },
        },
    },
    "mid_android": {
        "os": "android",
        "region": "mid",
        "kind": "three_production",
        "data_file": "dashboard_data_mid_region_android.csv",
        "cvr_file": "daily_cvr_android_mid_mar19.csv",
        "exclude_dates": {"13.01.2026", "30.01.2026"},
        "periods": {
            "period1": {
                "start": ANDROID_MID_PERIODS["period1"]["start"],
                "end": ANDROID_MID_PERIODS["period1"]["end"],
                "expected": ANDROID_MID_PERIODS["period1"]["expected"],
            },
            "period2": {
                "start": ANDROID_MID_PERIODS["period2"]["start"],
                "end": ANDROID_MID_PERIODS["period2"]["end"],
                "expected": ANDROID_MID_PERIODS["period2"]["expected"],
            },
            "period3": {
                "start": ANDROID_MID_PERIODS["period3"]["start"],
                "end": ANDROID_MID_PERIODS["period3"]["end"],
                "production": ANDROID_MID_PERIODS["period3"]["production"],
            },
        },
    },
    "dev_android": {
        "os": "android",
        "region": "dev",
        "kind": "three_production",
        "data_file": "dashboard_data_dev_region_android.csv",
        "cvr_file": "daily_cvr_android_dev_mar19.csv",
        "exclude_dates": {"13.01.2026", "30.01.2026"},
        "periods": {
            "period1": {
                "start": ANDROID_DEV_PERIODS["period1"]["start"],
                "end": ANDROID_DEV_PERIODS["period1"]["end"],
                "expected": ANDROID_DEV_PERIODS["period1"]["expected"],
            },
            "period2": {
                "start": ANDROID_DEV_PERIODS["period2"]["start"],
                "end": ANDROID_DEV_PERIODS["period2"]["end"],
                "expected": ANDROID_DEV_PERIODS["period2"]["expected"],
            },
            "period3": {
                "start": ANDROID_DEV_PERIODS["period3"]["start"],
                "end": ANDROID_DEV_PERIODS["period3"]["end"],
                "production": ANDROID_DEV_PERIODS["period3"]["production"],
            },
        },
    },
    "android_rich": {
        "os": "android",
        "region": "rich",
        "kind": "two_ab",
        "data_file": "dashboard_data_rich_region_android.csv",
        "cvr_file": "daily_cvr_android_rich_mar19.csv",
        "exclude_dates": {"30.01.2026"},
        "periods": {
            "period1": {
                "start": ANDROID_RICH_PERIODS["period1"]["start"],
                "end": ANDROID_RICH_PERIODS["period1"]["end"],
                "expected": ANDROID_RICH_PERIODS["period1"]["expected"],
            },
            "period2": {
                "start": ANDROID_RICH_PERIODS["period2"]["start"],
                "end": ANDROID_RICH_PERIODS["period2"]["end"],
                "expected": ANDROID_RICH_PERIODS["period2"]["expected"],
            },
        },
    },
}


def resolve_row_assignment(segment, row):
    if (row.get("gender") or "").strip().lower() not in {"m", "male"}:
        return None
    if (row.get("os") or "").strip().lower() != segment["os"]:
        return None
    if (row.get("region") or "").strip().lower() != segment["region"]:
        return None

    date_str = (row.get("date") or "").strip()
    if not date_str or date_str in segment["exclude_dates"]:
        return None

    try:
        row_date = parse_date(date_str)
    except Exception:
        return None

    age_raw = (row.get("age") or "").strip()
    if not age_raw.isdigit():
        return None
    age = int(age_raw)

    apval = normalize_pvalue(row.get("apval"))
    bpval = normalize_pvalue(row.get("bpval"))
    ct_pvalue = normalize_pvalue(row.get("\ufeffct_p_value") or row.get("ct_p_value"))
    ab_type = (row.get("ab_type") or "").strip()

    for period_name, period in segment["periods"].items():
        if not (period["start"] <= row_date <= period["end"]):
            continue

        if "expected" in period:
            if age not in period["expected"]:
                return None
            if ab_type not in {"A", "B"}:
                return None
            expected_ct = apval if ab_type == "A" else bpval
            if ct_pvalue != expected_ct:
                return None
            return period_name, ab_type, row_date

        expected_price = period["production"].get(age)
        if not expected_price:
            return None
        if apval != expected_price and bpval != expected_price:
            return None
        return period_name, "P", row_date

    return None


def pack_summary(bucket, num_days):
    users = len(bucket["users"])
    converters = len(bucket["converters"])
    revenue = round(bucket["revenue"], 2)
    conversion_events = bucket["conversion_events"]
    cvr = round((converters / users) * 100, 4) if users else 0
    rev_per_user = round(revenue / users, 4) if users else 0
    rev_per_user_day = round(rev_per_user / num_days, 4) if users and num_days else 0
    return {
        "users": users,
        "converters": converters,
        "conversion_events": conversion_events,
        "cvr": cvr,
        "revenue": revenue,
        "revPerUser": rev_per_user,
        "revPerUserDay": rev_per_user_day,
    }


def main():
    rates = json.loads(RATES_JSON.read_text(encoding="utf-8"))

    daily_data = {
        key: defaultdict(empty_daily_bucket)
        for key in SEGMENTS
    }
    daily_all_age = {
        key: defaultdict(empty_daily_bucket)
        for key in SEGMENTS
    }
    summaries = {
        key: {
            "overall": defaultdict(lambda: defaultdict(empty_summary_bucket)),
            "periods": {
                period_name: defaultdict(lambda: defaultdict(empty_summary_bucket))
                for period_name in cfg["periods"]
            },
        }
        for key, cfg in SEGMENTS.items()
    }

    with RAW_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            user_id = (row.get("cognito_user_id") or "").strip()
            if not user_id:
                continue

            for segment_key, segment in SEGMENTS.items():
                assignment = resolve_row_assignment(segment, row)
                if not assignment:
                    continue

                period_name, group, row_date = assignment
                row_date_iso = row_date.isoformat()
                age = int((row.get("age") or "0").strip() or 0)

                for duration_key in ("all",) + FILTERABLE_DURATIONS:
                    daily_data[segment_key][(row_date_iso, age, group, duration_key)]["users"].add(user_id)
                    daily_all_age[segment_key][(row_date_iso, group, duration_key)]["users"].add(user_id)
                    summaries[segment_key]["overall"][DURATION_LABELS[duration_key]][group]["users"].add(user_id)
                    summaries[segment_key]["periods"][period_name][DURATION_LABELS[duration_key]][group]["users"].add(user_id)

                converted = is_converted(row)
                if not converted:
                    continue

                product_id = (row.get("product_id") or "").strip()
                mapping = PRODUCT_MAPPING.get(product_id)
                revenue_value = 0.0
                duration_key = None
                if mapping:
                    _p, duration_key, nominal_price = mapping
                    country = country_from_store_code(row.get("store_country_code")) or (row.get("country") or "").strip()
                    revenue_value = round(
                        convert_nominal_price_to_eur(nominal_price, segment["os"], country, rates),
                        6,
                    )

                for bucket_space, bucket_key in (
                    (daily_data[segment_key], (row_date_iso, age, group, "all")),
                    (daily_all_age[segment_key], (row_date_iso, group, "all")),
                ):
                    bucket_space[bucket_key]["converters"].add(user_id)
                    bucket_space[bucket_key]["conversion_events"] += 1
                    bucket_space[bucket_key]["revenue"] += revenue_value

                summaries[segment_key]["overall"]["All"][group]["converters"].add(user_id)
                summaries[segment_key]["overall"]["All"][group]["conversion_events"] += 1
                summaries[segment_key]["overall"]["All"][group]["revenue"] += revenue_value
                summaries[segment_key]["periods"][period_name]["All"][group]["converters"].add(user_id)
                summaries[segment_key]["periods"][period_name]["All"][group]["conversion_events"] += 1
                summaries[segment_key]["periods"][period_name]["All"][group]["revenue"] += revenue_value

                if duration_key:
                    for bucket_space, bucket_key in (
                        (daily_data[segment_key], (row_date_iso, age, group, duration_key)),
                        (daily_all_age[segment_key], (row_date_iso, group, duration_key)),
                    ):
                        bucket_space[bucket_key]["converters"].add(user_id)
                        bucket_space[bucket_key]["conversion_events"] += 1
                        bucket_space[bucket_key]["revenue"] += revenue_value

                    duration_label = DURATION_LABELS[duration_key]
                    summaries[segment_key]["overall"][duration_label][group]["converters"].add(user_id)
                    summaries[segment_key]["overall"][duration_label][group]["conversion_events"] += 1
                    summaries[segment_key]["overall"][duration_label][group]["revenue"] += revenue_value
                    summaries[segment_key]["periods"][period_name][duration_label][group]["converters"].add(user_id)
                    summaries[segment_key]["periods"][period_name][duration_label][group]["conversion_events"] += 1
                    summaries[segment_key]["periods"][period_name][duration_label][group]["revenue"] += revenue_value

    summary_json = {}

    for segment_key, segment in SEGMENTS.items():
        data_rows = []
        for (date_iso, age, group, duration_key), bucket in sorted(daily_data[segment_key].items()):
            users = len(bucket["users"])
            converters = len(bucket["converters"])
            conversion_events = bucket["conversion_events"]
            revenue = round(bucket["revenue"], 2)
            data_rows.append(
                {
                    "date": date_iso,
                    "age": age,
                    "group": group,
                    "duration": DURATION_LABELS[duration_key],
                    "purchase_type": "All",
                    "users": users,
                    "exposures": users,
                    "unique_converters": converters,
                    "converted_users": conversion_events,
                    "events": conversion_events,
                    "user_cvr": round((converters / users) * 100, 4) if users else 0,
                    "revenue": revenue,
                    "revenue_per_user": round(revenue / users, 4) if users else 0,
                }
            )

        with (OUTPUT_DIR / segment["data_file"]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "date", "age", "group", "duration", "purchase_type", "users",
                    "exposures", "unique_converters", "converted_users", "events",
                    "user_cvr", "revenue", "revenue_per_user",
                ],
            )
            writer.writeheader()
            writer.writerows(data_rows)

        cvr_rows = []
        for (date_iso, group, duration_key), bucket in sorted(daily_all_age[segment_key].items()):
            users = len(bucket["users"])
            converters = len(bucket["converters"])
            cvr_rows.append(
                {
                    "date": date_iso,
                    "group": group,
                    "duration": DURATION_LABELS[duration_key],
                    "unique_users": users,
                    "unique_converters": converters,
                    "conversion_events": bucket["conversion_events"],
                    "daily_cvr": round((converters / users) * 100, 4) if users else 0,
                }
            )

        with (OUTPUT_DIR / segment["cvr_file"]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["date", "group", "duration", "unique_users", "unique_converters", "conversion_events", "daily_cvr"],
            )
            writer.writeheader()
            writer.writerows(cvr_rows)

        overall_json = {}
        for duration_label, groups in summaries[segment_key]["overall"].items():
            overall_json[duration_label] = {}
            overall_days = 0
            for period in segment["periods"].values():
                overall_days += (period["end"] - period["start"]).days + 1
            for group, bucket in groups.items():
                overall_json[duration_label][group] = pack_summary(bucket, overall_days)

        periods_json = {}
        for period_name, duration_map in summaries[segment_key]["periods"].items():
            periods_json[period_name] = {}
            num_days = (segment["periods"][period_name]["end"] - segment["periods"][period_name]["start"]).days + 1
            for duration_label, groups in duration_map.items():
                periods_json[period_name][duration_label] = {
                    group: pack_summary(bucket, num_days)
                    for group, bucket in groups.items()
                }

        summary_json[segment_key] = {"overall": overall_json, "periods": periods_json}

    with (OUTPUT_DIR / "segment_metrics_v2.json").open("w", encoding="utf-8") as handle:
        json.dump(summary_json, handle, indent=2)


if __name__ == "__main__":
    main()
