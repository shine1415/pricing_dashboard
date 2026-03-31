# A/B Pricing Test Report: Male Android Users - Poor Region

**Test Period:** January 12 - March 19, 2026, with January 30 removed (66 analyzed days)  
**Platform:** Android  
**Region:** Poor (Albania, Kosovo, North Macedonia)  
**Gender:** Male  
**Sample Size:** 4,903 users (Group A: 2,449 | Group B: 2,454)  
**Data Quality:** Correct P-values only. Jan 30 removed as a mixed pricing-transition day. March 20-24 excluded due to Ramadan promo contamination.

---

## Executive Summary

**Winner: Group B**

- Group B achieved **8.44% CVR** vs Group A's **6.82%** (+23.8% lift)
- Group B generated **€0.72/user** vs Group A's **€0.51/user** (+41.2%)
- Group B led on modeled revenue: **€1,772.16** vs **€1,250.04**

**Recommendation:** Use **P5-P28** for Android Poor as well. The pattern matches iOS Poor: lower pricing helps, but the deeper Period 2 cut weakens daily monetization.

---

## Overall Performance

### Group A
- Exposures: **2,449** unique users
- Converters: **167** unique users
- CVR: **6.82%**
- Revenue per user: **€0.51**

### Group B
- Exposures: **2,454** unique users
- Converters: **207** unique users
- CVR: **8.44%**
- Revenue per user: **€0.72**

**Lift:** +23.8% CVR and +41.2% revenue per user in favor of Group B.

---

## Period Comparison

**Period definitions:**
- Period 1: **Jan 12-29** (18 days)
- Jan 30: removed
- Period 2: **Jan 31-Mar 19** (48 days)

### Group A: P14-P36 -> P5-P28
| Metric | Period 1 | Period 2 | Change |
|--------|----------|----------|--------|
| CVR | 3.92% | 6.00% | **+53%** |
| Rev/User | €0.05 | €0.58 | +1,060% |
| Rev/User/Day | €0.0029 | €0.0120 | **+297%** |

### Group B: P5-P28 -> lower Period 2 ladder
| Metric | Period 1 | Period 2 | Change |
|--------|----------|----------|--------|
| CVR | 4.71% | 7.27% | **+54%** |
| Rev/User | €0.44 | €0.56 | +27% |
| Rev/User/Day | €0.0245 | €0.0117 | **-49%** |

**Read:** Android Poor lands in the same place as iOS Poor. P5-P28 is the useful lower ladder; the extra price cut in Period 2 gives up too much revenue velocity.

---

## Recommendation

**Deploy P5-P28 for Android Poor male users.**

Why:
- It wins the cleaned overall comparison.
- The platform still shows the same floor behavior as Poor Region on iOS.
- Going lower increases CVR, but not efficiently enough on a daily revenue basis.
