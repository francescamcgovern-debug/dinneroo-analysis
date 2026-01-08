# Scoring Framework v3.0 - Change Log

**Date:** 2026-01-08  
**Status:** Implemented

---

## Executive Summary

Simplified the scoring framework from 11 factors to **6 factors** with a **60/40 Performance/Opportunity split**. Same framework now applies to both **cuisine** and **dish** analysis for consistency.

---

## What Changed

### Track Weights

| Track | Before (v2) | After (v3) | Rationale |
|-------|-------------|------------|-----------|
| Performance | 50% | **60%** | Behavioral data is stronger signal |
| Opportunity | 50% | **40%** | Demand sources need strengthening |

### Factor Count

| Category | Before | After | Change |
|----------|--------|-------|--------|
| Performance factors | 6 | 4 | Consolidated |
| Opportunity factors | 5 | 2 | Dropped fit factors |
| **Total** | **11** | **6** | -5 factors |

---

## Final Framework (6 Factors)

### Performance Track (60%)

| Factor | Weight | Source | Calculation |
|--------|--------|--------|-------------|
| Orders per Zone | 20% | Snowflake | `total_orders ÷ zones_with_item` |
| Zone Ranking Strength | 15% | Snowflake | `% zones where item ranks top 5` |
| Rating | 15% | Snowflake | Average Deliveroo star rating |
| Kids Happy | 10% | Post-order survey | `% full and happy` |

### Opportunity Track (40%)

| Factor | Weight | Source | Calculation |
|--------|--------|--------|-------------|
| Latent Demand | 20% | Surveys | Open-text mentions + wishlist % |
| Non-Dinneroo Demand | 20% | Snowflake | **Mon-Thu 16:30-21:00 only** |

---

## Factors Removed

| Factor | Previous Weight | Reason for Removal |
|--------|-----------------|-------------------|
| Adult Appeal | 10.25% | Mostly estimated (not measured), not differentiating |
| Balanced/Guilt-Free | 9.25% | Mostly estimated (not measured), not differentiating |
| Fussy Eater Friendly | 5.5% | Weight too small to impact rankings |
| Repeat Intent | 5% | Merged into Rating signal |
| Adult Satisfaction | 7.5% | Merged into Rating signal |
| Supply Gap Severity | N/A | Was inflating opportunity for unavailable items |

### Why Fit Factors Were Dropped

The factor validation analysis showed:
- Only 13 dishes had survey-backed fit factor scores
- The remaining 35+ dishes defaulted to score of 3 (neutral)
- With most dishes scoring 3, fit factors weren't differentiating rankings
- Until we have measured data, these factors add complexity without value

---

## Quadrant Names (Action-Oriented)

Replaced generic quadrant names with action-oriented alternatives:

| Before | After | Definition | Action |
|--------|-------|------------|--------|
| Priority | **Core Drivers** | High Perf + High Opp | Protect and expand |
| Develop | **Preference Drivers** | Low Perf + High Opp | Build demand |
| Protect | **Demand Boosters** | High Perf + Low Opp | Improve quality |
| Monitor | **Deprioritised** | Low both | Don't invest |

---

## Key Normalizations

### Orders per Zone (New)

Previously used raw order volume, which biased toward widely available items.

**Before:** Curry with 5,897 orders in 100 zones scores higher than Pho with 4,530 orders in 50 zones.

**After:** 
- Curry: 5,897 ÷ 100 = 59 orders/zone
- Pho: 4,530 ÷ 50 = 91 orders/zone
- Pho now scores higher (correctly rewards efficiency)

### Non-Dinneroo Demand (Filter Added)

Previously used all non-Dinneroo orders. Now filtered to match Dinneroo's use case:
- **Days:** Monday - Thursday only
- **Time:** 16:30 - 21:00 only
- **Rationale:** Validates demand exists during midweek family dinner window

---

## Files Changed

### New Files
- `config/scoring_framework_v3.json` - Unified config for both cuisine and dish
- `scripts/phase2_analysis/01_score_dishes_v3.py` - Updated dish scoring
- `scripts/phase2_analysis/score_cuisines_v3.py` - New cuisine scoring (same framework)

### Files to Deprecate
- `config/factor_weights.json` - Old 10-factor framework
- `config/dish_scoring_unified.json` - Superseded by v3
- `scripts/phase2_analysis/01_score_dishes_v2.py` - Uses old config

---

## Consistency Across Deliverables

| Deliverable | Before | After |
|-------------|--------|-------|
| Dashboard | Performance/Opportunity | Same + action quadrant names |
| slides_data.csv | Demand Strength/Consumer Preference | Performance/Opportunity |
| dish_tiers.csv | Priority Score | Unified Score |
| Reports | Mixed terminology | Consistent throughout |

---

## Validation Checklist

Before sharing any deliverable, verify:

- [ ] Track weights are 60% Performance / 40% Opportunity
- [ ] Quadrant names are action-oriented (Core Drivers, etc.)
- [ ] Orders per zone is used (not raw volume)
- [ ] Non-Dinneroo demand is filtered to Mon-Thu 16:30-21:00
- [ ] Fit factors are NOT included
- [ ] Same framework used for both cuisine and dish analysis

---

## Next Steps

1. Run scoring scripts to regenerate data
2. Update dashboard with new quadrant names
3. Regenerate slides_data.csv with consistent terminology
4. Archive deprecated files

---

*Framework v3.0 - Simplified, Consistent, Action-Oriented*


