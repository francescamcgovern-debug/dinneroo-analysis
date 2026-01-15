# MVP Threshold Strengthening Report

**Generated**: 2026-01-13 12:37:03
**North-star targets (business)**: 5+ partners, 5+ cuisines, 21+ dishes

## Executive Summary (multi-metric)

This strengthens the MVP thresholds using **multiple independent outcome metrics** (not just repeat rate):
- Behavioral: repeat rate, average rating, order volume
- Survey: kids happy, liked/loved, enough food, food hot, on-time

**Headline:** The 5/5/20 direction is supported across multiple outcomes, with important nuance:
- Data-driven **inflection often starts around ~3–4** (minimum viable)
- **5+ is the product “north star”** for redundancy and family variety

### Scorecard at the thresholds (Below vs At/Above)

| Dimension | Threshold | Repeat Rate | Avg Rating | Kids Happy | Enough Food | Food Hot | On Time |
|----------|-----------|------------|-----------|-----------|------------|---------|--------|
| Partners | 5+ | 16.2% → 23.0% (+6.8pp) | 4.25 → 4.40 | 67.6% → 71.3% | 73.1% → 76.7% | 64.2% → 63.3% | 82.8% → 83.3% |
| Cuisines | 5+ | 18.7% → 23.5% (+4.8pp) | 4.30 → 4.44 | 71.8% → 68.7% | 71.9% → 77.6% | 64.3% → 63.0% | 84.3% → 84.0% |
| Dishes | 20+ | 16.8% → 21.0% (+4.3pp) | 4.08 → 4.41 | 40.0% → 73.7% | 66.7% → 77.9% | 66.7% → 67.2% | 71.1% → 86.7% |

## Inflection vs Target (what to say in CD)

- **Data inflection (minimum viable)**: partners ~3+ and cuisines ~3+ show meaningful improvement in the underlying analysis (see `mvp_threshold_discovery.json` inflection_analysis).
- **Business target (north star)**: 5+ partners and 5+ cuisines support redundancy and choice (see `config/mvp_thresholds.json`).
- **Interpretation**: “3+ is where performance starts to lift; 5+ is the intended family proposition.”

## Monotonicity Checks (diagnostic only)

Monotonicity is mixed because bucket sizes are uneven and supply factors are correlated; we treat this as **context**, not the core proof.

| Dimension | Repeat Rate | Kids Happy | Avg Rating |
|-----------|-------------|------------|------------|
| Partners | Mostly monotonic (3/4 increases) | Non-monotonic (2/4 increases) | Mostly monotonic (3/4 increases) |
| Cuisines | Perfectly monotonic | Non-monotonic (2/3 increases) | Perfectly monotonic |
| Dishes | Non-monotonic (2/3 increases) | Non-monotonic (2/3 increases) | Perfectly monotonic |

## Confounding Factors

**Important caveat**: Partners and cuisines are highly correlated (r=0.89).

This means:
- Zones with more partners tend to also have more cuisines
- It’s difficult to isolate the independent effect of each factor
- The thresholds should be seen as a **package**, not independent requirements

**Mitigation**: The underlying analysis is hierarchical (partners → cuisines controlling for partners → dishes controlling for both), which provides **directional evidence** rather than causal claims.

## Recommendation

**Maintain the 5/5/21 north-star thresholds** and communicate:
- “Minimum viable lift starts around ~3–4”
- “5+ is where the proposition becomes reliably good for families”

---

*This analysis strengthens (rather than replaces) the existing threshold recommendation.*
