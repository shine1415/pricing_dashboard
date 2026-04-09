#!/usr/bin/env python3
"""
Price recommendation engine for dua.com male users.

Reference segment: iOS Dev — highest converter volume, most reliable signal.

Per (age, segment), combines:
  1. Direct CVR evidence from A/B tests (age_anchor_analysis.json)
  2. Empirical cross-segment signal: scale iOS Dev's best price by the
     observed median price ratio for the target segment
     (derived from ages where BOTH segments have strong evidence)

No external GDP/PPP tables are used. The region assignment already encodes
behavioral WTP — Belgium in Rich and Germany in Dev have similar GDP but
different observed WTP. The data knows better than any index.
"""

import argparse, json, statistics
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_INPUT_JSON  = Path("/Users/ardittrikshiqi/Desktop/pricing-v2/dashboard/age_anchor_analysis.json")
DEFAULT_OUTPUT_JSON = Path("/Users/ardittrikshiqi/Desktop/pricing-v2/dashboard/price_recommendations.json")

# Reference segment: iOS Dev — most converters, strongest signal overall
REFERENCE_SEGMENT = "dev_ios"

# Segment metadata
SEGMENT_META = {
    "poor":         {"platform": "iOS",     "region": "poor",  "label": "iOS Poor"},
    "mid_ios":      {"platform": "iOS",     "region": "mid",   "label": "iOS Mid"},
    "dev_ios":      {"platform": "iOS",     "region": "dev",   "label": "iOS Dev"},
    "rich":         {"platform": "iOS",     "region": "rich",  "label": "iOS Rich"},
    "android_poor": {"platform": "Android", "region": "poor",  "label": "Android Poor"},
    "mid_android":  {"platform": "Android", "region": "mid",   "label": "Android Mid"},
    "dev_android":  {"platform": "Android", "region": "dev",   "label": "Android Dev"},
    "android_rich": {"platform": "Android", "region": "rich",  "label": "Android Rich"},
}

SEGMENT_ORDER = ["poor", "mid_ios", "dev_ios", "rich",
                 "android_poor", "mid_android", "dev_android", "android_rich"]

# Fallback ratios (vs iOS Dev) if not enough overlapping ages to compute empirically.
# Based on observed medians: Poor ~0.46, Mid ~0.93, Rich ~1.03,
# Android discount ~0.68-0.80 of iOS equivalent.
RATIO_FALLBACK = {
    "poor":         0.46,
    "mid_ios":      0.93,
    "dev_ios":      1.00,
    "rich":         1.03,
    "android_poor": 0.48,
    "mid_android":  0.68,
    "dev_android":  0.68,
    "android_rich": 0.80,
}

# Minimum evidence to include an age in ratio computation
MIN_USERS_RATIO = 25
MIN_CONV_RATIO  = 2

# Confidence thresholds
MIN_USERS_FULL_CONF   = 100
MIN_USERS_HALF_CONF   = 25
MIN_CONVERTERS_SIGNAL = 2

PRICE_LADDER = list(range(5, 47))

# ---------------------------------------------------------------------------
# Price ladder — EUR prices per P-value (USD/EUR/CHF/GBP are 1:1)
# Formula: 1wk = P×0.50−0.01 | 1mo = P×1.00−0.01 | 3mo = P×2.00−0.01
# ---------------------------------------------------------------------------

def eur(p):
    """Return dict of EUR prices for a given integer P-value."""
    n = int(str(p).replace("P", ""))
    return {
        "wk":  round(n * 0.50 - 0.01, 2),
        "mo":  round(n * 1.00 - 0.01, 2),
        "3mo": round(n * 2.00 - 0.01, 2),
    }


def breakeven_lift(p_current, p_test):
    """
    Relative CVR lift needed at p_test so that revenue/exposed-user stays equal.
    Revenue/user = CVR × monthly_price, so new_cvr/old_cvr = old_price/new_price.
    Returns percentage (e.g. 4.0 means 4.0% relative lift required).
    """
    old_mo = eur(p_current)["mo"]
    new_mo = eur(p_test)["mo"]
    if new_mo <= 0:
        return None
    return round((old_mo / new_mo - 1) * 100, 1)


def format_chain(chain):
    """Format the price history chain into a human-readable string."""
    parts = []
    for step in chain:
        period_label = step["period"].replace("period", "P")
        parts.append(
            f"{period_label}: {step['A']['p_value']} ({step['A']['cvr']:.1f}% CVR) vs "
            f"{step['B']['p_value']} ({step['B']['cvr']:.1f}% CVR) → Group {step['winner_group']} ({step['winner_price']}) won"
        )
    return " · ".join(parts)


def next_test_suggestion(direct_ev, rec_price_str):
    """
    Generate an actionable next-test recommendation.
    - Single price: propose testing one step below
    - A/B tested, lower won: test one step below the winner
    - A/B tested, higher won: test one step above the winner
    - A/B same price: flag as non-informative, suggest a real price test
    """
    if not direct_ev:
        return None

    rec_p = p_int(rec_price_str)

    if not direct_ev["is_ab"]:
        prior_loser   = direct_ev.get("prior_ab_loser")
        prior_winner  = direct_ev.get("prior_ab_winner")
        prior_loser_p = p_int(prior_loser) if prior_loser else None

        if prior_loser_p is not None:
            # We have a confirmed P1 A/B result: prior_winner beat prior_loser.
            # The current live price is the P1 winner rolled out to production.
            # Never retest the known loser — find the first un-tested price instead.
            prior_winner_p = p_int(prior_winner) if prior_winner else rec_p

            if prior_winner_p >= prior_loser_p:
                # Higher price won P1 → natural next step: test one above the winner
                test_p = rec_p + 1
                if test_p > PRICE_LADDER[-1]:
                    return {
                        "type":          "at_ceiling",
                        "current_price": f"P{rec_p}",
                        "current_eur":   eur(rec_p),
                        "rationale": (
                            f"P{prior_loser_p} (Group A) was already tested in Period 1 and lost to "
                            f"P{rec_p} (Group B). P{rec_p} is now live. "
                            f"P{rec_p + 1} would exceed the price ladder ceiling."
                        ),
                    }
                lift = breakeven_lift(test_p, rec_p)
                return {
                    "type":           "explore_higher",
                    "current_price":  f"P{rec_p}",
                    "current_eur":    eur(rec_p),
                    "test_price":     f"P{test_p}",
                    "test_eur":       eur(test_p),
                    "breakeven_lift": lift,
                    "risk":           "Low" if lift < 5 else "Moderate",
                    "rationale": (
                        f"P{prior_loser_p} (€{eur(prior_loser_p)['mo']}/mo, Period 1 Group A) was already tested "
                        f"and lost to P{rec_p} (€{eur(rec_p)['mo']}/mo, Period 1 Group B). "
                        f"P{rec_p} is confirmed by P1 and now live as the production price. "
                        f"The next un-tested frontier is P{test_p} (€{eur(test_p)['mo']}/mo) — "
                        f"test whether demand holds at the higher price. "
                        f"Revenue is maintained as long as CVR drops by less than {lift}%."
                    ),
                }
            else:
                # Lower price won P1 → test one below the known loser (skip the loser)
                test_p = prior_loser_p - 1
                if test_p < PRICE_LADDER[0]:
                    return {
                        "type":          "at_floor",
                        "current_price": f"P{rec_p}",
                        "current_eur":   eur(rec_p),
                        "rationale": (
                            f"P{prior_loser_p} was tested in Period 1 and lost to P{rec_p}. "
                            f"P{rec_p} is now live. No lower price remains to test above the floor."
                        ),
                    }
                lift = breakeven_lift(rec_p, test_p)
                risk = "Low" if lift < 5 else ("Moderate" if lift < 10 else "High")
                return {
                    "type":           "explore_lower",
                    "current_price":  f"P{rec_p}",
                    "current_eur":    eur(rec_p),
                    "test_price":     f"P{test_p}",
                    "test_eur":       eur(test_p),
                    "breakeven_lift": lift,
                    "risk":           risk,
                    "rationale": (
                        f"P{prior_loser_p} (€{eur(prior_loser_p)['mo']}/mo, Period 1 Group A) was already tested "
                        f"and lost to P{rec_p}. Retesting P{prior_loser_p} would add no new information. "
                        f"Run P{test_p} (€{eur(test_p)['mo']}/mo) to explore whether demand continues rising "
                        f"further below the known loser. "
                        f"Break-even: ≥{lift}% CVR lift needed at P{test_p} to match current revenue/user."
                    ),
                }

        # No prior test known — standard explore-lower
        test_p = rec_p - 1
        if test_p < PRICE_LADDER[0]:
            return None
        lift = breakeven_lift(rec_p, test_p)
        risk = "Low" if lift < 5 else ("Moderate" if lift < 10 else "High")
        return {
            "type":           "explore_lower",
            "current_price":  f"P{rec_p}",
            "current_eur":    eur(rec_p),
            "test_price":     f"P{test_p}",
            "test_eur":       eur(test_p),
            "breakeven_lift": lift,
            "risk":           risk,
            "rationale": (
                f"P{rec_p} (€{eur(rec_p)['mo']}/mo) is the current live price — "
                f"no challenger was run against it in this period. "
                f"This may be a validated winner from a prior A/B test now serving as the confirmed price. "
                f"Run P{test_p} (€{eur(test_p)['mo']}/mo) as a new variant B to explore "
                f"whether a lower price unlocks incremental volume. "
                f"Break-even: the lower price needs ≥{lift}% relative CVR lift to match current revenue/user."
            ),
        }

    # ── A/B test segment ──────────────────────────────────────────────
    same_price = direct_ev.get("same_price_latest", False)
    tested_set = set(direct_ev.get("tested_prices", []))
    chain      = direct_ev.get("price_chain", [])
    chain_str  = format_chain(chain) if chain else ""

    w_p = p_int(direct_ev["winner_price"]) if direct_ev.get("winner_price") else None
    l_p = p_int(direct_ev["loser_price"])  if direct_ev.get("loser_price")  else None

    if same_price and w_p is not None:
        # Both groups at the same price — test concluded at floor.
        # Next: explore one step above to check revenue upside.
        test_p = w_p + 1
        while f"P{test_p}" in tested_set and test_p <= PRICE_LADDER[-1]:
            test_p += 1
        if test_p > PRICE_LADDER[-1]:
            return {
                "type": "at_ceiling",
                "current_price": f"P{w_p}",
                "current_eur": eur(w_p),
                "rationale": (
                    f"Both A and B groups are at P{w_p} — the test has converged at this price. "
                    f"No higher untested price is available within the ladder."
                    + (f" Price history: {chain_str}." if chain_str else "")
                ),
            }
        lift = breakeven_lift(test_p, w_p)
        return {
            "type": "explore_higher_from_floor",
            "current_price": f"P{w_p}",
            "current_eur": eur(w_p),
            "test_price": f"P{test_p}",
            "test_eur": eur(test_p),
            "breakeven_lift": lift,
            "risk": "Low" if abs(lift) < 5 else "Moderate",
            "rationale": (
                f"Both A and B are at P{w_p} — the A/B test has converged at the floor price. "
                f"P{w_p} is the confirmed winner across earlier periods. "
                + (f"Price history: {chain_str}. " if chain_str else "")
                + f"Test P{test_p} (€{eur(test_p)['mo']}/mo) to explore whether a small price lift "
                f"is viable without significant CVR loss. "
                f"Break-even: CVR at P{test_p} can drop by up to {abs(lift):.1f}% vs P{w_p} and still match revenue/user."
            ),
        }

    if w_p is None:
        return None

    if l_p is not None and w_p < l_p:
        # Lower price won — explore one step lower, skipping already-tested prices
        test_p = w_p - 1
        while f"P{test_p}" in tested_set and test_p >= PRICE_LADDER[0]:
            test_p -= 1
        if test_p < PRICE_LADDER[0]:
            return {
                "type": "at_floor",
                "current_price": f"P{w_p}",
                "current_eur": eur(w_p),
                "rationale": (
                    f"P{w_p} won against P{l_p}. No lower untested price remains above the price floor."
                    + (f" Price history: {chain_str}." if chain_str else "")
                ),
            }
        lift = breakeven_lift(w_p, test_p)
        risk = "Low" if abs(lift) < 5 else ("Moderate" if abs(lift) < 10 else "High")
        skipped = [p for p in tested_set if p_int(p) is not None and p_int(p) < w_p and p_int(p) > test_p] if tested_set else []
        skip_note = f" (skipping {', '.join(sorted(skipped))} — already tested)" if skipped else ""
        return {
            "type": "explore_lower",
            "current_price": f"P{w_p}",
            "current_eur": eur(w_p),
            "test_price": f"P{test_p}",
            "test_eur": eur(test_p),
            "breakeven_lift": lift,
            "risk": risk,
            "rationale": (
                (f"Price history: {chain_str}. " if chain_str else "")
                + f"Latest period: P{w_p} beat P{l_p} — lower price keeps winning. "
                + f"Next un-tested frontier: P{test_p} (€{eur(test_p)['mo']}/mo){skip_note}. "
                + f"Break-even: P{test_p} needs ≥{abs(lift):.1f}% CVR lift vs P{w_p} to match revenue/user."
            ),
        }

    if l_p is not None and w_p > l_p:
        # Higher price won — explore one step higher, skipping already-tested prices
        test_p = w_p + 1
        while f"P{test_p}" in tested_set and test_p <= PRICE_LADDER[-1]:
            test_p += 1
        if test_p > PRICE_LADDER[-1]:
            return {
                "type": "at_ceiling",
                "current_price": f"P{w_p}",
                "current_eur": eur(w_p),
                "rationale": (
                    f"P{w_p} beat P{l_p}. No higher untested price remains within the ladder."
                    + (f" Price history: {chain_str}." if chain_str else "")
                ),
            }
        lift = breakeven_lift(test_p, w_p)
        return {
            "type": "explore_higher",
            "current_price": f"P{w_p}",
            "current_eur": eur(w_p),
            "test_price": f"P{test_p}",
            "test_eur": eur(test_p),
            "breakeven_lift": lift,
            "risk": "Low" if abs(lift) < 5 else "Moderate",
            "rationale": (
                (f"Price history: {chain_str}. " if chain_str else "")
                + f"Latest period: P{w_p} beat P{l_p} — higher price is viable. "
                + f"Test P{test_p} (€{eur(test_p)['mo']}/mo) to explore further upside. "
                + f"Break-even: CVR at P{test_p} can drop by up to {abs(lift):.1f}% vs P{w_p} and still match revenue/user."
            ),
        }

    # Equal prices / no loser
    return {
        "type": "same_price_test",
        "current_price": f"P{w_p}",
        "current_eur": eur(w_p),
        "rationale": (
            "Both groups received the same price — no A/B signal available from this period."
            + (f" Price history: {chain_str}." if chain_str else "")
        ),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def snap(price_float):
    return min(PRICE_LADDER, key=lambda p: abs(p - price_float))


def p_int(p_str):
    if p_str is None:
        return None
    return int(str(p_str).replace("P", "").replace("p", ""))


def confidence_from_users(users, converters):
    user_conf   = min(1.0, users / MIN_USERS_FULL_CONF)
    conv_weight = 1.0 if converters >= MIN_CONVERTERS_SIGNAL else 0.4
    return round(user_conf * conv_weight, 3)


def label_confidence(score):
    if score >= 0.7:  return "High"
    if score >= 0.4:  return "Moderate"
    if score >= 0.15: return "Low"
    return "Insufficient"


def best_strong_price(seg_data):
    """
    From a cohort_performance entry, return the integer price of the group
    with the highest CVR that meets minimum evidence thresholds.
    Returns None if no group qualifies.
    """
    gd = seg_data.get("group_data", {})
    candidates = []
    for g, v in gd.items():
        if v["users"] >= MIN_USERS_RATIO and v["converters"] >= MIN_CONV_RATIO:
            candidates.append((v["cvr"], p_int(v["p_value"])))
    return max(candidates)[1] if candidates else None


# ---------------------------------------------------------------------------
# Step 1 — Compute empirical price ratios vs iOS Dev
# ---------------------------------------------------------------------------

def compute_empirical_ratios(age_analysis):
    """
    For each segment, collect (other_best_price / dev_ios_best_price) across
    every age where BOTH dev_ios AND the target segment have strong evidence.
    Use the median as the ratio (robust to outlier ages).

    Returns {segment_key: float ratio_vs_dev_ios}
    """
    raw_ratios = defaultdict(list)

    for age_str, age_data in age_analysis.items():
        cp = {s["segment_key"]: s for s in age_data.get("cohort_performance", [])}
        ref_seg = cp.get(REFERENCE_SEGMENT)
        if not ref_seg:
            continue
        ref_price = best_strong_price(ref_seg)
        if not ref_price:
            continue
        for seg_key, meta in SEGMENT_META.items():
            if seg_key == REFERENCE_SEGMENT:
                continue
            other = cp.get(seg_key)
            if not other:
                continue
            other_price = best_strong_price(other)
            if not other_price:
                continue
            raw_ratios[seg_key].append(other_price / ref_price)

    ratios = {REFERENCE_SEGMENT: 1.0}
    for seg_key in SEGMENT_META:
        if seg_key == REFERENCE_SEGMENT:
            continue
        rs = raw_ratios[seg_key]
        if len(rs) >= 3:
            ratios[seg_key] = round(statistics.median(rs), 3)
        elif len(rs) >= 1:
            # Small sample — average but flag as less reliable
            ratios[seg_key] = round(sum(rs) / len(rs), 3)
        else:
            ratios[seg_key] = RATIO_FALLBACK[seg_key]

    return ratios, {k: len(v) for k, v in raw_ratios.items()}


# ---------------------------------------------------------------------------
# Step 2 — Extract direct evidence from age_anchor_analysis.json
# ---------------------------------------------------------------------------

def extract_direct_evidence(age_analysis):
    evidence = {}
    for age_str, age_data in age_analysis.items():
        age = int(age_str)
        evidence[age] = {}
        for seg in age_data.get("cohort_performance", []):
            seg_key = seg["segment_key"]
            gd      = seg.get("group_data", {})
            a, b, p = gd.get("A"), gd.get("B"), gd.get("P")

            if a and b:
                if a["users"] >= 5 and b["users"] >= 5:
                    if a["cvr"] >= b["cvr"]:
                        winner, loser, winner_group, loser_group = a, b, "A", "B"
                    else:
                        winner, loser, winner_group, loser_group = b, a, "B", "A"
                elif a["users"] >= b["users"]:
                    winner, loser, winner_group, loser_group = a, b, "A", "B"
                else:
                    winner, loser, winner_group, loser_group = b, a, "B", "A"
                ev = {
                    "is_ab":             True,
                    "winner_group":      winner_group,
                    "winner_price":      winner["p_value"],
                    "winner_cvr":        winner["cvr"],
                    "winner_users":      winner["users"],
                    "winner_converters": winner["converters"],
                    "loser_group":       loser_group,
                    "loser_price":       loser["p_value"],
                    "loser_cvr":         loser["cvr"],
                    "loser_users":       loser["users"],
                    "has_signal":        winner["users"] >= MIN_USERS_HALF_CONF,
                    "direct_conf":       confidence_from_users(winner["users"], winner["converters"]),
                }

                # Build prior period chain for A/B segments
                prior_periods = seg.get("prior_periods_ab", {})
                same_price_latest = seg.get("same_price_latest", False)

                price_chain = []
                for period_name in sorted(prior_periods.keys()):
                    pa_hist = prior_periods[period_name].get("A")
                    pb_hist = prior_periods[period_name].get("B")
                    if pa_hist and pb_hist:
                        w_group = "A" if pa_hist["cvr"] >= pb_hist["cvr"] else "B"
                        w_price = pa_hist["p_value"] if w_group == "A" else pb_hist["p_value"]
                        price_chain.append({
                            "period": period_name,
                            "A": pa_hist,
                            "B": pb_hist,
                            "winner_group": w_group,
                            "winner_price": w_price,
                        })

                ev["price_chain"] = price_chain
                ev["same_price_latest"] = same_price_latest

                # Collect all prices already tested across all periods
                tested_prices = set()
                for step in price_chain:
                    if step["A"].get("p_value"): tested_prices.add(step["A"]["p_value"])
                    if step["B"].get("p_value"): tested_prices.add(step["B"]["p_value"])
                if ev.get("winner_price"): tested_prices.add(ev["winner_price"])
                if ev.get("loser_price"):  tested_prices.add(ev["loser_price"])
                ev["tested_prices"] = sorted(tested_prices)  # list for JSON serialisation

                evidence[age][seg_key] = ev
            elif p:
                ev = {
                    "is_ab":             False,
                    "winner_price":      p["p_value"],
                    "winner_cvr":        p["cvr"],
                    "winner_users":      p["users"],
                    "winner_converters": p["converters"],
                    "loser_price":       None,
                    "loser_cvr":         None,
                    "loser_users":       None,
                    "has_signal":        p["users"] >= MIN_USERS_HALF_CONF,
                    "direct_conf":       confidence_from_users(p["users"], p["converters"]),
                    # Prior-period A/B fields (None if no prior test found)
                    "prior_ab_winner":       None,
                    "prior_ab_winner_cvr":   None,
                    "prior_ab_winner_users": None,
                    "prior_ab_loser":        None,
                    "prior_ab_loser_cvr":    None,
                    "prior_ab_loser_users":  None,
                }
                prior = seg.get("prior_period_ab", {})
                pa, pb = prior.get("A"), prior.get("B")
                prod_price = p["p_value"]  # the implemented production price
                if pa and pb and pa.get("p_value") and pb.get("p_value"):
                    # Identify winner as whichever P1 group matches the production price.
                    # (The implementation decision may have been revenue-based, not just CVR.)
                    if pa["p_value"] == prod_price:
                        pw, pl = pa, pb
                    elif pb["p_value"] == prod_price:
                        pw, pl = pb, pa
                    else:
                        # Production price doesn't match either P1 group exactly — fall back to CVR
                        pw, pl = (pa, pb) if pa["cvr"] >= pb["cvr"] else (pb, pa)
                    ev.update({
                        "prior_ab_winner":       pw["p_value"],
                        "prior_ab_winner_cvr":   pw["cvr"],
                        "prior_ab_winner_users": pw["users"],
                        "prior_ab_loser":        pl["p_value"],
                        "prior_ab_loser_cvr":    pl["cvr"],
                        "prior_ab_loser_users":  pl["users"],
                    })
                evidence[age][seg_key] = ev
            else:
                evidence[age][seg_key] = None

    return evidence


# ---------------------------------------------------------------------------
# Step 3 — Cross-segment signal via empirical ratio
# ---------------------------------------------------------------------------

def cross_segment_signal(age, target_seg, evidence_by_age, emp_ratios):
    """
    Scale iOS Dev's best price at this age (or a nearby age) by the
    empirical ratio for the target segment.
    """
    ratio = emp_ratios[target_seg]

    for delta in [0, 1, -1, 2, -2]:
        src_age = age + delta
        ref_ev  = evidence_by_age.get(src_age, {}).get(REFERENCE_SEGMENT)
        if ref_ev and ref_ev["has_signal"]:
            ref_price  = p_int(ref_ev["winner_price"])
            scaled_int = snap(ref_price * ratio)
            return {
                "source_age":   src_age,
                "source_price": ref_ev["winner_price"],
                "ratio":        ratio,
                "scaled_price": f"P{scaled_int}",
                "scaled_int":   scaled_int,
            }
    return None


# ---------------------------------------------------------------------------
# Step 4 — Build final recommendation
# ---------------------------------------------------------------------------

def build_recommendation(age, seg_key, direct_ev, cross_sig):
    meta = SEGMENT_META[seg_key]

    # No direct evidence at all
    if not direct_ev:
        if cross_sig:
            rec_price = cross_sig["scaled_price"]
            return {
                "recommended_price": rec_price,
                "recommended_eur":   eur(p_int(rec_price)),
                "confidence":        0.15,
                "confidence_label":  "Insufficient",
                "method":            "cross_segment",
                "direct_evidence":   None,
                "cross_signal":      cross_sig,
                "next_test":         next_test_suggestion(None, rec_price),
                "reasoning": (
                    f"No data for {meta['label']} age {age}. "
                    f"iOS Dev age {cross_sig['source_age']} ({cross_sig['source_price']}) "
                    f"× {cross_sig['ratio']}× empirical ratio → {cross_sig['scaled_price']}."
                ),
            }
        return None

    direct_conf      = direct_ev["direct_conf"]
    direct_price     = direct_ev["winner_price"]
    direct_price_int = p_int(direct_price)

    # Strong direct evidence — trust it entirely
    if direct_conf >= 0.65:
        agree = cross_sig and abs(direct_price_int - cross_sig["scaled_int"]) / max(direct_price_int, cross_sig["scaled_int"]) <= 0.20
        return {
            "recommended_price": direct_price,
            "recommended_eur":   eur(direct_price_int),
            "confidence":        round(min(0.97, direct_conf + (0.05 if agree else 0.0)), 3),
            "confidence_label":  label_confidence(direct_conf),
            "method":            "direct",
            "direct_evidence":   direct_ev,
            "cross_signal":      cross_sig,
            "signals_agree":     agree,
            "next_test":         next_test_suggestion(direct_ev, direct_price),
            "reasoning":         _reason_direct(meta, direct_ev, cross_sig, agree),
        }

    # No cross-segment signal — report direct as-is
    if not cross_sig:
        return {
            "recommended_price": direct_price,
            "recommended_eur":   eur(direct_price_int),
            "confidence":        direct_conf,
            "confidence_label":  label_confidence(direct_conf),
            "method":            "direct",
            "direct_evidence":   direct_ev,
            "cross_signal":      None,
            "next_test":         next_test_suggestion(direct_ev, direct_price),
            "reasoning":         _reason_direct(meta, direct_ev, None, False),
        }

    cross_int = cross_sig["scaled_int"]
    diff_pct  = abs(direct_price_int - cross_int) / max(direct_price_int, cross_int)
    agree     = diff_pct <= 0.20

    if direct_conf >= 0.25:
        w_d    = 0.5 + direct_conf * 0.5
        final  = f"P{snap(w_d * direct_price_int + (1 - w_d) * cross_int)}"
        conf   = round(min(0.97, max(0.05, direct_conf + (0.10 if agree else -0.05))), 3)
        method = "blended"
    else:
        final  = cross_sig["scaled_price"]
        conf   = round(min(0.30, 0.15 + (0.05 if agree else 0.0)), 3)
        method = "cross_segment"

    final_int = p_int(final)
    return {
        "recommended_price": final,
        "recommended_eur":   eur(final_int),
        "confidence":        conf,
        "confidence_label":  label_confidence(conf),
        "method":            method,
        "direct_evidence":   direct_ev,
        "cross_signal":      cross_sig,
        "signals_agree":     agree,
        "next_test":         next_test_suggestion(direct_ev, final),
        "reasoning":         _reason_blended(meta, direct_ev, cross_sig, agree, final),
    }


def _reason_direct(meta, ev, cross, agree):
    if ev["is_ab"]:
        loser_str = f" vs {ev['loser_price']} at {ev['loser_cvr']:.1f}%" if ev["loser_price"] else ""
        base = (f"A/B winner: {ev['winner_price']} at {ev['winner_cvr']:.2f}% CVR "
                f"({ev['winner_users']} users, {ev['winner_converters']} conv){loser_str}.")
    else:
        base = (f"Single price: {ev['winner_price']} at {ev['winner_cvr']:.2f}% CVR "
                f"({ev['winner_users']} users, {ev['winner_converters']} conv).")
    if cross:
        cross_str = f" Cross-segment signal: {cross['scaled_price']} ({'✓ agrees' if agree else '⚠ diverges'})."
        return base + cross_str
    return base


def _reason_blended(meta, ev, cross, agree, final):
    direct_str = f"{ev['winner_price']} ({ev['winner_cvr']:.1f}% CVR, {ev['winner_users']} users)"
    cross_str  = (f"iOS Dev age {cross['source_age']} ({cross['source_price']}) "
                  f"× {cross['ratio']}× → {cross['scaled_price']}")
    agree_str  = "✓ Signals agree." if agree else "⚠ Signals diverge — blended."
    return f"Direct: {direct_str} | Cross-segment: {cross_str} → {final}. {agree_str}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  default=str(DEFAULT_INPUT_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    print("Loading age anchor analysis …")
    with open(args.input) as f:
        anchor_data = json.load(f)

    print("Computing empirical price ratios vs iOS Dev …")
    emp_ratios, ratio_counts = compute_empirical_ratios(anchor_data["age_analysis"])
    print(f"  {'Segment':<20} {'Ratio':>8}   {'Ages used':>10}   {'Method'}")
    print("  " + "-" * 60)
    for seg in SEGMENT_ORDER:
        r  = emp_ratios[seg]
        n  = ratio_counts.get(seg, 0)
        fb = " (fallback)" if n < 3 else ""
        print(f"  {SEGMENT_META[seg]['label']:<20} {r:>7.3f}×   {n:>6} ages{fb}")

    print("\nExtracting direct CVR evidence …")
    evidence_by_age = extract_direct_evidence(anchor_data["age_analysis"])

    ages = [int(a) for a in anchor_data["ages"]]
    recommendations = {}
    for age in ages:
        recommendations[str(age)] = {}
        for seg_key in SEGMENT_ORDER:
            direct_ev = evidence_by_age.get(age, {}).get(seg_key)
            cross_sig = cross_segment_signal(age, seg_key, evidence_by_age, emp_ratios)
            rec = build_recommendation(age, seg_key, direct_ev, cross_sig)
            if rec:
                recommendations[str(age)][seg_key] = rec

    output = {
        "generated_at":    anchor_data.get("generated_at", ""),
        "ages":            [str(a) for a in ages],
        "segments":        SEGMENT_ORDER,
        "segment_meta":    SEGMENT_META,
        "reference_segment": REFERENCE_SEGMENT,
        "empirical_ratios":  emp_ratios,
        "ratio_sample_sizes": ratio_counts,
        "recommendations": recommendations,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {out_path}")

    print("\nSample — Age 20:")
    print(f"  {'Segment':<20} {'Price':>6}  {'Conf':>6}  {'Label':<14} {'Method'}")
    for seg_key in SEGMENT_ORDER:
        r = recommendations.get("20", {}).get(seg_key)
        if r:
            print(f"  {SEGMENT_META[seg_key]['label']:<20} {r['recommended_price']:>6}  "
                  f"{r['confidence']:>6.2f}  {r['confidence_label']:<14} {r['method']}")


if __name__ == "__main__":
    main()
