#!/usr/bin/env python3

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from rebuild_canonical_metrics import RAW_CSV, SEGMENTS, is_converted, normalize_pvalue
from rebuild_ios_mid_dev_rich_dec19 import parse_date


DEFAULT_OUTPUT_JSON = Path("/Users/ardittrikshiqi/Desktop/pricing-test-results/dashboard/age_anchor_analysis.json")


SEGMENT_META = {
    "poor": {"name": "Male | iOS | Poor Region", "platform": "iOS", "region": "Poor"},
    "mid_ios": {"name": "Male | iOS | Mid Region", "platform": "iOS", "region": "Mid"},
    "dev_ios": {"name": "Male | iOS | Dev", "platform": "iOS", "region": "Dev"},
    "rich": {"name": "Male | iOS | Rich Region", "platform": "iOS", "region": "Rich"},
    "android_poor": {"name": "Male | Android | Poor Region", "platform": "Android", "region": "Poor"},
    "mid_android": {"name": "Male | Android | Mid Region", "platform": "Android", "region": "Mid"},
    "dev_android": {"name": "Male | Android | Dev", "platform": "Android", "region": "Dev"},
    "android_rich": {"name": "Male | Android | Rich Region", "platform": "Android", "region": "Rich"},
}

LATEST_PERIOD = {
    "poor": "period3",
    "mid_ios": "period2",
    "dev_ios": "period2",
    "rich": "period2",
    "android_poor": "period3",
    "mid_android": "period3",
    "dev_android": "period3",
    "android_rich": "period2",
}

IOS_CODE_TO_REGION = {
    "ALB": "poor", "AUS": "rich", "AUT": "dev", "BEL": "rich", "BIH": "poor",
    "BGR": "mid", "CAN": "rich", "HRV": "mid", "CZE": "mid", "DNK": "rich",
    "EGY": "poor", "FIN": "rich", "FRA": "dev", "DEU": "dev", "GRC": "mid",
    "HUN": "mid", "ISL": "rich", "IRL": "rich", "ITA": "mid", "KAZ": "poor",
    "XKS": "poor", "LTU": "mid", "LUX": "rich", "MKD": "poor", "MLT": "mid",
    "MNE": "poor", "NLD": "rich", "NOR": "rich", "POL": "mid", "ROU": "mid",
    "SAU": "mid", "SRB": "poor", "SVN": "dev", "ESP": "mid", "SWE": "rich",
    "CHE": "rich", "TUR": "mid", "ARE": "dev", "GBR": "dev", "USA": "rich",
}

ANDROID_CODE_TO_REGION = {
    "AL": "poor", "AU": "rich", "AT": "dev", "BE": "rich", "BA": "poor",
    "BG": "mid", "CA": "rich", "HR": "mid", "CZ": "mid", "DK": "rich",
    "EG": "poor", "FI": "rich", "FR": "dev", "DE": "dev", "GR": "mid",
    "HU": "mid", "IS": "rich", "IE": "rich", "IT": "mid", "KZ": "poor",
    "LT": "mid", "LU": "rich", "MT": "mid", "ME": "poor", "MK": "poor",
    "NL": "rich", "NO": "rich", "PL": "mid", "RO": "mid", "SA": "mid",
    "RS": "poor", "SI": "dev", "ES": "mid", "SE": "rich", "CH": "rich",
    "TR": "mid", "AE": "dev", "GB": "dev", "US": "rich",
}

IOS_NAME_TO_REGION = {
    "albania": "poor",
    "australia": "rich",
    "austria": "dev",
    "belgium": "rich",
    "bosnia and herzegovina": "poor",
    "bulgaria": "mid",
    "canada": "rich",
    "croatia": "mid",
    "czechia": "mid",
    "czech republic": "mid",
    "denmark": "rich",
    "egypt": "poor",
    "finland": "rich",
    "france": "dev",
    "germany": "dev",
    "greece": "mid",
    "hungary": "mid",
    "iceland": "rich",
    "ireland": "rich",
    "italy": "mid",
    "kazakhstan": "poor",
    "kosovo": "poor",
    "lithuania": "mid",
    "luxembourg": "rich",
    "macedonia, the former yugoslav republic of": "poor",
    "north macedonia": "poor",
    "malta": "mid",
    "montenegro": "poor",
    "netherlands": "rich",
    "norway": "rich",
    "poland": "mid",
    "romania": "mid",
    "saudi arabia": "mid",
    "serbia": "poor",
    "slovenia": "dev",
    "spain": "mid",
    "sweden": "rich",
    "switzerland": "rich",
    "turkey": "mid",
    "turkiye": "mid",
    "united arab emirates": "dev",
    "united kingdom": "dev",
    "united states of america": "rich",
    "united states": "rich",
}

ANDROID_NAME_TO_REGION = {
    "albania": "poor",
    "australia": "rich",
    "austria": "dev",
    "belgium": "rich",
    "bosnia & herzegovina": "poor",
    "bosnia and herzegovina": "poor",
    "bulgaria": "mid",
    "canada": "rich",
    "croatia": "mid",
    "czechia": "mid",
    "czech republic": "mid",
    "denmark": "rich",
    "egypt": "poor",
    "finland": "rich",
    "france": "dev",
    "germany": "dev",
    "greece": "mid",
    "hungary": "mid",
    "iceland": "rich",
    "ireland": "rich",
    "italy": "mid",
    "kazakhstan": "poor",
    "lithuania": "mid",
    "luxembourg": "rich",
    "malta": "mid",
    "montenegro": "poor",
    "netherlands": "rich",
    "north macedonia": "poor",
    "norway": "rich",
    "poland": "mid",
    "romania": "mid",
    "saudi arabia": "mid",
    "serbia": "poor",
    "slovenia": "dev",
    "spain": "mid",
    "sweden": "rich",
    "switzerland": "rich",
    "türkiye": "mid",
    "turkiye": "mid",
    "turkey": "mid",
    "united arab emirates": "dev",
    "united kingdom": "dev",
    "united states": "rich",
    "united states of america": "rich",
}


def empty_bucket():
    return {
        "users": set(),
        "converters": set(),
        "conversion_events": 0,
    }


def normalize_country(value):
    return " ".join((value or "").strip().lower().split())


def country_region(os_name, row):
    store_code = (row.get("store_country_code") or "").strip().upper()
    country_name = normalize_country(row.get("country"))
    if os_name == "ios":
      if store_code and store_code in IOS_CODE_TO_REGION:
          return IOS_CODE_TO_REGION[store_code], store_code
      if country_name and country_name in IOS_NAME_TO_REGION:
          return IOS_NAME_TO_REGION[country_name], country_name
    if os_name == "android":
      if store_code and store_code in ANDROID_CODE_TO_REGION:
          return ANDROID_CODE_TO_REGION[store_code], store_code
      if country_name and country_name in ANDROID_NAME_TO_REGION:
          return ANDROID_NAME_TO_REGION[country_name], country_name
    return None, None


def resolve_latest_assignment(segment_key, row):
    segment = SEGMENTS[segment_key]
    os_name = (row.get("os") or "").strip().lower()

    if (row.get("gender") or "").strip().lower() not in {"m", "male"}:
        return None
    if os_name != segment["os"]:
        return None

    mapped_region, region_source = country_region(os_name, row)
    if mapped_region != segment["region"]:
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

    latest_period_name = LATEST_PERIOD[segment_key]
    period = segment["periods"][latest_period_name]
    if not (period["start"] <= row_date <= period["end"]):
        return None

    apval = normalize_pvalue(row.get("apval"))
    bpval = normalize_pvalue(row.get("bpval"))
    ct_pvalue = normalize_pvalue(row.get("\ufeffct_p_value") or row.get("ct_p_value"))
    ab_type = (row.get("ab_type") or "").strip()

    if "expected" in period:
        expected = period["expected"].get(age)
        if not expected or ab_type not in {"A", "B"}:
            return None
        expected_ct = apval if ab_type == "A" else bpval
        if ct_pvalue != expected_ct:
            return None
        p_value = expected[0] if ab_type == "A" else expected[1]
        return latest_period_name, ab_type, row_date, age, p_value, region_source

    expected_price = period["production"].get(age)
    if not expected_price:
        return None
    if apval != expected_price and bpval != expected_price:
        return None
    return latest_period_name, "P", row_date, age, expected_price, region_source


def resolve_history_assignments(row):
    assignments = []
    os_name = (row.get("os") or "").strip().lower()

    if (row.get("gender") or "").strip().lower() not in {"m", "male"}:
        return assignments

    date_str = (row.get("date") or "").strip()
    if not date_str:
        return assignments

    try:
        row_date = parse_date(date_str)
    except Exception:
        return assignments

    age_raw = (row.get("age") or "").strip()
    if not age_raw.isdigit():
        return assignments
    age = int(age_raw)

    apval = normalize_pvalue(row.get("apval"))
    bpval = normalize_pvalue(row.get("bpval"))
    ct_pvalue = normalize_pvalue(row.get("\ufeffct_p_value") or row.get("ct_p_value"))
    ab_type = (row.get("ab_type") or "").strip()
    mapped_region, region_source = country_region(os_name, row)

    for segment_key, segment in SEGMENTS.items():
        if segment["os"] != os_name:
            continue
        if mapped_region != segment["region"]:
            continue
        if date_str in segment["exclude_dates"]:
            continue

        for period_name, period in segment["periods"].items():
            if not (period["start"] <= row_date <= period["end"]):
                continue

            if "expected" in period:
                expected = period["expected"].get(age)
                if not expected or ab_type not in {"A", "B"}:
                    continue
                expected_ct = apval if ab_type == "A" else bpval
                if ct_pvalue != expected_ct:
                    continue
                p_value = expected[0] if ab_type == "A" else expected[1]
                assignments.append((segment_key, period_name, ab_type, row_date, age, p_value, region_source))
                break

            expected_price = period["production"].get(age)
            if not expected_price:
                continue
            if apval != expected_price and bpval != expected_price:
                continue
            assignments.append((segment_key, period_name, "P", row_date, age, expected_price, region_source))
            break

    return assignments


def period_label(period):
    start = period["start"].strftime("%b %-d")
    end = period["end"].strftime("%b %-d")
    return f"{start} - {end}"


def anchor_score(users, converters, events):
    if users <= 0:
        return 0.0
    cvr = converters / users
    return round((cvr * 100) * (events ** 0.5), 6)


def choose_best(rows, key_fn):
    if not rows:
        return None
    return max(rows, key=key_fn)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    output_json = Path(args.output)

    observations = defaultdict(empty_bucket)
    history_observations = defaultdict(empty_bucket)

    with RAW_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            user_id = (row.get("cognito_user_id") or "").strip()
            if not user_id:
                continue

            for segment_key in SEGMENTS:
                assignment = resolve_latest_assignment(segment_key, row)
                if not assignment:
                    continue

                period_name, group, _row_date, age, p_value, region_source = assignment
                key = (age, segment_key, period_name, group, p_value, region_source)
                bucket = observations[key]
                bucket["users"].add(user_id)
                if is_converted(row):
                    bucket["converters"].add(user_id)
                    bucket["conversion_events"] += 1

            for assignment in resolve_history_assignments(row):
                segment_key, period_name, group, _row_date, age, p_value, region_source = assignment
                key = (age, segment_key, period_name, group, p_value, region_source)
                bucket = history_observations[key]
                bucket["users"].add(user_id)
                if is_converted(row):
                    bucket["converters"].add(user_id)
                    bucket["conversion_events"] += 1

    # Pre-aggregate P1 A/B data for production-mode segments so the recommendation
    # engine can see what was already tested before the production price was locked in.
    # Key: (age, segment_key) → {group: {users, converters, cvr, p_value}}
    prior_ab_lookup = defaultdict(lambda: defaultdict(
        lambda: {"users": set(), "converters": set(), "_pv_counts": {}}
    ))
    for (h_age, h_seg, h_period, h_group, h_pval, _h_reg), h_bucket in history_observations.items():
        if h_period != "period1" or h_group not in ("A", "B"):
            continue
        agg = prior_ab_lookup[(h_age, h_seg)][h_group]
        agg["users"].update(h_bucket["users"])
        agg["converters"].update(h_bucket["converters"])
        agg["_pv_counts"][h_pval] = agg["_pv_counts"].get(h_pval, 0) + len(h_bucket["users"])

    # --- Prior periods A/B lookup for A/B-mode segments ---
    # Covers ALL periods except the latest for each segment.
    # Used to surface full price history in next-test recommendations.
    LATEST_PERIOD_BY_SEG = {
        "poor": "period3", "android_poor": "period3",
        "rich": "period2", "android_rich": "period2",
        "mid_ios": "period2", "dev_ios": "period2",
        "mid_android": "period2", "dev_android": "period2",
    }

    prior_periods_ab_lookup = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(lambda: {"users": set(), "converters": set(), "_pv_counts": {}})
        )
    )

    for (h_age, h_seg, h_period, h_group, h_pval, _h_reg), h_bucket in history_observations.items():
        latest = LATEST_PERIOD_BY_SEG.get(h_seg)
        if h_period == latest:
            continue  # skip latest — already captured in cohort_performance
        if h_group not in ("A", "B"):
            continue  # skip production "P" entries
        agg = prior_periods_ab_lookup[(h_age, h_seg)][h_period][h_group]
        agg["users"].update(h_bucket["users"])
        agg["converters"].update(h_bucket["converters"])
        agg["_pv_counts"][h_pval] = agg["_pv_counts"].get(h_pval, 0) + len(h_bucket["users"])

    age_payload = {}

    for age in range(18, 41):
        records = []
        for (row_age, segment_key, period_name, group, p_value, region_source), bucket in observations.items():
            if row_age != age:
                continue
            users = len(bucket["users"])
            converters = len(bucket["converters"])
            if users == 0:
                continue
            meta = SEGMENT_META[segment_key]
            cvr = round((converters / users) * 100, 4)
            records.append({
                "age": age,
                "segment_key": segment_key,
                "segment_name": meta["name"],
                "platform": meta["platform"],
                "region": meta["region"],
                "period_key": period_name,
                "period_label": period_label(SEGMENTS[segment_key]["periods"][period_name]),
                "group": group,
                "p_value": p_value,
                "users": users,
                "converters": converters,
                "conversion_events": bucket["conversion_events"],
                "cvr": cvr,
                "anchor_score": anchor_score(users, converters, bucket["conversion_events"]),
                "region_source": region_source,
            })

        if not records:
            continue

        cohort_performance = []
        by_segment = defaultdict(list)
        for record in records:
            by_segment[record["segment_key"]].append(record)

        for segment_key, rows in by_segment.items():
            rows = sorted(rows, key=lambda item: item["group"])
            total_users = sum(item["users"] for item in rows)
            total_converters = sum(item["converters"] for item in rows)
            total_events = sum(item["conversion_events"] for item in rows)
            leading = choose_best(rows, lambda item: (item["cvr"], item["converters"], item["conversion_events"]))
            group_data = {}
            for row in rows:
                g = row["group"]
                if g not in group_data:
                    group_data[g] = {"users": 0, "converters": 0, "_pv_counts": {}}
                group_data[g]["users"] += row["users"]
                group_data[g]["converters"] += row["converters"]
                pv = row["p_value"]
                group_data[g]["_pv_counts"][pv] = group_data[g]["_pv_counts"].get(pv, 0) + row["users"]
            for g, gd in group_data.items():
                gd["cvr"] = round((gd["converters"] / gd["users"]) * 100, 4) if gd["users"] else 0
                gd["p_value"] = max(gd["_pv_counts"], key=lambda pv: gd["_pv_counts"][pv])
                del gd["_pv_counts"]
            entry = {
                "segment_key": segment_key,
                "segment_name": rows[0]["segment_name"],
                "platform": rows[0]["platform"],
                "region": rows[0]["region"],
                "period_label": rows[0]["period_label"],
                "users": total_users,
                "converters": total_converters,
                "conversion_events": total_events,
                "aggregate_cvr": round((total_converters / total_users) * 100, 4) if total_users else 0,
                "group_data": group_data,
            }

            # For production-mode segments (P2 single price), surface the P1 A/B
            # test results so downstream tools know what prices were already tested.
            if list(group_data.keys()) == ["P"]:
                prior_raw = prior_ab_lookup.get((age, segment_key), {})
                if prior_raw:
                    prior_ab = {}
                    for g, agg in prior_raw.items():
                        u = len(agg["users"])
                        c = len(agg["converters"])
                        pv = max(agg["_pv_counts"], key=lambda pv: agg["_pv_counts"][pv]) if agg["_pv_counts"] else None
                        prior_ab[g] = {
                            "users":      u,
                            "converters": c,
                            "cvr":        round((c / u) * 100, 4) if u else 0,
                            "p_value":    pv,
                        }
                    if prior_ab:
                        entry["prior_period_ab"] = prior_ab

            # Detect when both groups share the same price in the latest period
            if "A" in group_data and "B" in group_data:
                if group_data["A"].get("p_value") == group_data["B"].get("p_value"):
                    entry["same_price_latest"] = True

            # Inject prior_periods_ab for A/B segments
            if "A" in group_data or "B" in group_data:
                prior_raw = prior_periods_ab_lookup.get((age, segment_key), {})
                if prior_raw:
                    prior_periods_ab = {}
                    for period_name in sorted(prior_raw.keys()):
                        groups = prior_raw[period_name]
                        prior_periods_ab[period_name] = {}
                        for g, agg in groups.items():
                            u = len(agg["users"])
                            c = len(agg["converters"])
                            pv = max(agg["_pv_counts"], key=lambda pv: agg["_pv_counts"][pv]) if agg["_pv_counts"] else None
                            prior_periods_ab[period_name][g] = {
                                "users": u,
                                "converters": c,
                                "cvr": round((c / u) * 100, 4) if u else 0,
                                "p_value": pv,
                            }
                    if prior_periods_ab:
                        entry["prior_periods_ab"] = prior_periods_ab

            cohort_performance.append(entry)

        p_rollups = defaultdict(lambda: {"users": 0, "converters": 0, "conversion_events": 0, "contexts": []})
        for record in records:
            roll = p_rollups[record["p_value"]]
            roll["users"] += record["users"]
            roll["converters"] += record["converters"]
            roll["conversion_events"] += record["conversion_events"]
            roll["contexts"].append({
                "platform": record["platform"],
                "region": record["region"],
                "segment_key": record["segment_key"],
                "group": record["group"],
                "cvr": record["cvr"],
                "users": record["users"],
                "converters": record["converters"],
            })

        p_value_analysis = []
        for p_value, roll in p_rollups.items():
            users = roll["users"]
            converters = roll["converters"]
            events = roll["conversion_events"]
            p_value_analysis.append({
                "p_value": p_value,
                "users": users,
                "converters": converters,
                "conversion_events": events,
                "cvr": round((converters / users) * 100, 4) if users else 0,
                "anchor_score": anchor_score(users, converters, events),
                "contexts": sorted(roll["contexts"], key=lambda item: (-item["converters"], -item["cvr"])),
            })

        p_value_analysis.sort(key=lambda item: (-item["anchor_score"], -item["converters"], -item["cvr"], item["p_value"]))
        best_cvr = choose_best(p_value_analysis, lambda item: (item["cvr"], item["converters"], item["users"]))
        most_converters = choose_best(p_value_analysis, lambda item: (item["converters"], item["conversion_events"], item["cvr"]))
        best_balanced = choose_best(
            [item for item in p_value_analysis if item["users"] >= 25] or p_value_analysis,
            lambda item: (item["anchor_score"], item["converters"], item["cvr"]),
        )

        by_platform_region = defaultdict(list)
        for record in records:
            by_platform_region[(record["platform"], record["region"])].append(record)

        regional_equivalents = []
        for platform, region, segment_key in [
            ("iOS",     "Poor", "poor"),
            ("iOS",     "Mid",  "mid_ios"),
            ("iOS",     "Dev",  "dev_ios"),
            ("iOS",     "Rich", "rich"),
            ("Android", "Poor", "android_poor"),
            ("Android", "Mid",  "mid_android"),
            ("Android", "Dev",  "dev_android"),
            ("Android", "Rich", "android_rich"),
        ]:
            region_rows = by_platform_region.get((platform, region), [])
            if not region_rows:
                continue
            region_rollups = defaultdict(lambda: {"users": 0, "converters": 0, "conversion_events": 0})
            for record in region_rows:
                roll = region_rollups[record["p_value"]]
                roll["users"] += record["users"]
                roll["converters"] += record["converters"]
                roll["conversion_events"] += record["conversion_events"]

            candidates = []
            for p_value, roll in region_rollups.items():
                users = roll["users"]
                converters = roll["converters"]
                cvr = round((converters / users) * 100, 4) if users else 0
                candidates.append({
                    "p_value": p_value,
                    "users": users,
                    "converters": converters,
                    "conversion_events": roll["conversion_events"],
                    "cvr": cvr,
                    "anchor_score": anchor_score(users, converters, roll["conversion_events"]),
                })
            best_region = choose_best(
                [item for item in candidates if item["users"] >= 25] or candidates,
                lambda item: (item["anchor_score"], item["converters"], item["cvr"]),
            )
            regional_equivalents.append({
                "region": region,
                "platform": platform,
                "segment_key": segment_key,
                "best_p_value": best_region["p_value"] if best_region else None,
                "users": best_region["users"] if best_region else 0,
                "converters": best_region["converters"] if best_region else 0,
                "conversion_events": best_region["conversion_events"] if best_region else 0,
                "cvr": best_region["cvr"] if best_region else 0,
                "anchor_score": best_region["anchor_score"] if best_region else 0,
                "gap_to_anchor_cvr": round(best_region["cvr"] - best_balanced["cvr"], 4) if best_region and best_balanced else None,
            })

        age_payload[str(age)] = {
            "cohort_performance": sorted(cohort_performance, key=lambda item: (item["platform"], item["region"])),
            "converter_analysis": {
                "best_cvr": best_cvr,
                "most_converters": most_converters,
                "best_balanced": best_balanced,
                "leaderboard": p_value_analysis,
            },
            "cross_regional_anchor": {
                "global_anchor": best_balanced,
                "regional_equivalents": regional_equivalents,
                "ppp_status": "PPP adjustment not applied yet. This first step uses observed latest-period performance only.",
            },
            "anchor_validation": {
                "anchor_p_value": best_balanced["p_value"] if best_balanced else None,
                "why": [
                    f"Converted at {best_balanced['cvr']:.2f}% CVR" if best_balanced else None,
                    f"Drove {best_balanced['conversion_events']} conversion units" if best_balanced else None,
                    f"Converted {best_balanced['converters']} unique users" if best_balanced else None,
                    f"Backed by {best_balanced['users']} users in the latest-period read" if best_balanced else None,
                ],
                "score": best_balanced["anchor_score"] if best_balanced else 0,
                "definition": "Anchor = best balanced candidate using latest-period-only CVR plus conversion volume, with a minimum user floor of 25 when possible.",
            },
            "history_check": {
                "anchor_p_value": best_balanced["p_value"] if best_balanced else None,
                "summary": None,
                "contexts": [],
            },
            "observations": sorted(records, key=lambda item: (item["platform"], item["region"], item["group"], item["p_value"])),
        }

        if best_balanced:
            anchor_p_value = best_balanced["p_value"]
            history_contexts = []
            hist_users = hist_converters = hist_events = 0

            for (row_age, segment_key, period_name, group, p_value, region_source), bucket in history_observations.items():
                if row_age != age or p_value != anchor_p_value:
                    continue
                users = len(bucket["users"])
                converters = len(bucket["converters"])
                if users == 0:
                    continue
                meta = SEGMENT_META[segment_key]
                hist_users += users
                hist_converters += converters
                hist_events += bucket["conversion_events"]
                history_contexts.append({
                    "segment_key": segment_key,
                    "segment_name": meta["name"],
                    "platform": meta["platform"],
                    "region": meta["region"],
                    "period_key": period_name,
                    "period_label": period_label(SEGMENTS[segment_key]["periods"][period_name]),
                    "group": group,
                    "users": users,
                    "converters": converters,
                    "conversion_events": bucket["conversion_events"],
                    "cvr": round((converters / users) * 100, 4),
                    "region_source": region_source,
                })

            age_payload[str(age)]["history_check"] = {
                "anchor_p_value": anchor_p_value,
                "summary": {
                    "users": hist_users,
                    "converters": hist_converters,
                    "conversion_events": hist_events,
                    "cvr": round((hist_converters / hist_users) * 100, 4) if hist_users else 0,
                    "contexts": len(history_contexts),
                },
                "contexts": sorted(history_contexts, key=lambda item: (item["platform"], item["region"], item["period_key"], item["group"])),
            }

    payload = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": str(RAW_CSV),
        "methodology": {
            "scope": "Latest period only for each segment",
            "latest_periods": LATEST_PERIOD,
            "ab_periods": "Correct P-values only",
            "single_price_periods": "Both correct and incorrect P-values",
            "anchor_definition": "Anchor is the best balanced candidate by latest-period CVR and conversion volume, not highest CVR alone.",
            "region_mapping": "Uses explicit iOS and Android country lists provided for Poor, Mid, Dev, and Rich.",
            "ppp_status": "Not applied yet in this step.",
        },
        "ages": sorted(int(age) for age in age_payload.keys()),
        "age_analysis": age_payload,
    }

    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {output_json}")


if __name__ == "__main__":
    main()
