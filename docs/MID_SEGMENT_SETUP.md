# Mid Segment Setup

Mid Region is treated as a production-handoff segment rather than a clean two-period A/B test.

Rules used:
- Period 1: `2026-01-12` to `2026-01-29`
- `2026-01-30` removed
- Period 2: `2026-01-31` to `2026-03-19`
- Period 1 uses `abchosen = 2` and keeps `A/B` from `ab_type`
- Period 2 uses `abchosen = 1` and is aggregated into one production group: `P`

Observed pattern:
- Male iOS Mid Period 1 uses an A/B ladder around `P16-P38` vs `P17-P39`
- Male iOS Mid Period 2 appears to roll the lower `B` ladder into production
- Male Android Mid Period 1 uses an A/B ladder around `P11-P33` vs `P9-P30`
- Male Android Mid Period 2 appears to roll the lower `B` ladder into production

Revenue logic:
- Duration comes from canonical package mapping
- Store-currency conversion uses the platform-specific country tables provided for iOS and Android
