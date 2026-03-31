# A/B Pricing Test Report: Male iOS Users - Poor Region

**Test Period:** January 12 - March 19, 2026, with January 30 removed (66 analyzed days)  
**Platform:** iOS  
**Region:** Poor (Albania, Kosovo, North Macedonia)  
**Gender:** Male  
**Sample Size:** 13,976 users (Group A: 7,021 | Group B: 6,955)  
**Data Quality:** Correct P-values only. Jan 30 removed as a mixed pricing-transition day. March 20-24 excluded due to Ramadan promo contamination.

---

## Executive Summary

**Winner: Group B**

- Group B achieved **11.93% CVR** vs Group A's **10.47%** (+14.0% lift)
- Group B generated **€0.81/user** vs Group A's **€0.70/user** (+16.1%)
- Group B also led on total modeled revenue: **€5,650.88** vs **€4,916.18**

**Recommendation:** Use **Group B's Period 1 price structure (P5-P28)** as the operating floor for iOS Poor. The lower ladder still wins overall, but the further drop used in Period 2 weakens daily monetization.

---

## Overall Performance

### Group A
- Exposures: **7,021** unique users
- Converters: **735** unique users
- CVR: **10.47%**
- Revenue per user: **€0.70**

### Group B
- Exposures: **6,955** unique users
- Converters: **830** unique users
- CVR: **11.93%**
- Revenue per user: **€0.81**

**Lift:** +14.0% CVR and +16.1% revenue per user in favor of Group B.

---

## Period Comparison

**Period definitions:**
- Period 1: **Jan 12-29** (18 days)
- Jan 30: removed
- Period 2: **Jan 31-Mar 19** (48 days)

### Group A: P14-P36 -> P5-P28
| Metric | Period 1 | Period 2 | Change |
|--------|----------|----------|--------|
| CVR | 4.51% | 9.62% | **+113%** |
| Rev/User | €0.12 | €0.73 | +497% |
| Rev/User/Day | €0.0064 | €0.0151 | **+126%** |

**Read:** Moving Group A down to the Period 1 Group B ladder was a clear improvement on both CVR and daily monetization.

### Group B: P5-P28 -> lower Period 2 ladder
| Metric | Period 1 | Period 2 | Change |
|--------|----------|----------|--------|
| CVR | 6.87% | 10.15% | **+48%** |
| Rev/User | €0.48 | €0.62 | +30% |
| Rev/User/Day | €0.0266 | €0.0130 | **-51%** |

**Read:** The extra cut in Period 2 kept CVR moving up, but the monetization rate per day fell sharply. That is the key reason not to go below the Period 1 Group B ladder.

---

## Recommendation

**Deploy P5-P28 for iOS Poor male users.**

Why this is the best call:
- It is the winning overall group after the clean filtering.
- It improved both CVR and revenue versus Group A.
- The lower Period 2 ladder looks too aggressive once Jan 30 is removed and the periods are normalized properly.

**Bottom line:** iOS Poor still supports lower pricing, but **P5-P28 looks like the floor**. Going lower improves conversion but harms revenue velocity.
