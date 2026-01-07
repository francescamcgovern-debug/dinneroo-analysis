# Segment Comparison Analysis: Families vs Non-Families

**Date:** January 2026  
**Data:** Post-order survey (n=1,599) + Dropoff survey (n=942)  
**Purpose:** Determine if families behave differently enough to justify family-specific scoring factors

---

## Executive Summary

**Key Finding: Families and non-families are REMARKABLY SIMILAR on outcome metrics, but differ fundamentally in decision criteria.**

| Metric | Families | Couples | Singles | Significant? |
|--------|----------|---------|---------|--------------|
| Satisfaction (Loved/Liked) | 85.6% | 87.1% | 84.6% | No |
| Repeat Intent | 75.2% | 75.3% | 71.9% | No |
| Overall Satisfied | 81.4% | 87.5% | 84.0% | No |
| Food Adequacy | 77.3% | 81.1% | 80.6% | No |
| **"Child Appeal" Cited** | **30.9%** | **1.1%** | **0.5%** | **YES** |

### Implication for Frameworks

**Outcome metrics are segment-agnostic** - all segments are equally satisfied with Dinneroo.

**Decision criteria are segment-specific** - families uniquely care about "child appeal" (30.9% vs ~1% for others).

---

## Sample Sizes

| Segment | Post-Order | Dropoff | Total |
|---------|------------|---------|-------|
| **Family** | 729 (46%) | 354 (38%) | 1,083 |
| **Couple** | 369 (23%) | 201 (21%) | 570 |
| **Single** | 190 (12%) | 120 (13%) | 310 |
| **Friends/Sharers** | 56 (4%) | 42 (4%) | 98 |
| **Other** | 255 (16%) | 225 (24%) | 480 |

Note: Dinneroo attracts significant non-family usage despite "family" positioning.

---

## Detailed Findings

### 1. Satisfaction & Repeat Intent (No Significant Differences)

All segments report similar satisfaction levels:

| Segment | Loved It | Liked It | Combined |
|---------|----------|----------|----------|
| Family | 46.0% | 39.6% | **85.6%** |
| Couple | 50.8% | 36.3% | **87.1%** |
| Single | 38.3% | 46.3% | **84.6%** |
| Friends/Sharers | 48.1% | 40.7% | **88.9%** |

**Interpretation:** Dinneroo works well for ALL segments, not just families.

### 2. Decision Criteria (KEY DIFFERENCE)

What drives dish choice by segment:

| Criterion | Family | Couple | Single | Friends |
|-----------|--------|--------|--------|---------|
| **Child Appeal** | **30.9%** | 1.1% | 0.5% | 0.0% |
| Good Value | 45.4% | 56.6% | 47.4% | 46.4% |
| Familiar Dish | 30.0% | 28.5% | 36.3% | 42.9% |
| Adult Appeal | 25.5% | 22.2% | 21.1% | 21.4% |
| Portion Size | 17.8% | 24.1% | 26.8% | 26.8% |
| Something we don't cook | 21.5% | 24.9% | 20.0% | 17.9% |

**Key Insight:** "Child appeal" is the ONLY criterion that meaningfully differentiates families (31% cite it vs ~1% for non-families). This validates the `kids_full_happy` and `fussy_eater_friendly` factors in the scoring framework.

### 3. Restaurant Preferences

Top restaurants by segment:

| Rank | Family | Couple | Single |
|------|--------|--------|--------|
| 1 | Wagamama (161) | Pho (91) | Pho (37) |
| 2 | Pho (109) | Dishoom (54) | Dishoom (30) |
| 3 | Dishoom (72) | Wagamama (50) | PizzaExpress (23) |
| 4 | PizzaExpress (65) | Banana Tree (27) | Bill's (10) |
| 5 | Giggling Squid (59) | Giggling Squid (24) | Banana Tree (9) |

**Interpretation:** Wagamama over-indexes with families (possibly due to kid-friendly positioning). Pho and Dishoom are universal favorites across all segments.

### 4. Dropoff Survey: Why Non-Families Explore Dinneroo

Even without children, couples and singles explore Dinneroo because:

| Appealing Aspect | Family | Couple | Single |
|------------------|--------|--------|--------|
| £25 is good value | 59.0% | 53.2% | 55.8% |
| Saves time | 38.7% | 30.3% | 33.3% |
| Don't want to cook | 36.4% | 30.8% | 33.3% |
| Kids love delivery midweek | **17.5%** | 3.0% | 3.3% |
| Balanced/nutritious food | 12.4% | 10.9% | 14.2% |

**Key Insight:** Non-families value Dinneroo for **value + convenience**, not family-specific features. The £25 price point is the #1 driver across ALL segments.

### 5. Barriers by Segment

What stopped non-completers:

| Barrier | Family | Couple | Single |
|---------|--------|--------|--------|
| Not enough food for price | 7.3% | 6.0% | 3.3% |
| No option for everyone | 8.2% | 5.5% | 6.7% |
| Can't customise | 4.2% | 2.0% | 6.7% |
| Price higher than expected | 5.4% | 3.5% | 5.0% |
| Meals didn't appeal to kids | **3.1%** | 0.0% | 0.8% |

**Key Insight:** "Meals didn't appeal to kids" is exclusively a family barrier (3.1% vs 0% for couples). This validates the need for family-specific dish curation.

---

## Framework Implications

### Dish Scoring Framework

| Factor | Current Weight | Segment Evidence | Recommendation |
|--------|----------------|------------------|----------------|
| `kids_full_happy` | 7.5% | Only families cite "child appeal" (31% vs 1%) | **KEEP** - validates family focus |
| `fussy_eater_friendly` | 5.5% | "Meals didn't appeal to kids" is family-only barrier | **KEEP** - family-specific |
| `adult_appeal` | 10.25% | Similar across segments (~22-25%) | **KEEP** - universal factor |
| `balanced_guilt_free` | 9.25% | "Balanced/nutritious" similar across segments | **KEEP** - universal factor |

**Conclusion:** Current weights are appropriate. Family-specific factors (`kids_full_happy`, `fussy_eater_friendly`) are validated by the 30x difference in "child appeal" citation rates.

### MVP Thresholds

| Criterion | Segment Evidence | Recommendation |
|-----------|------------------|----------------|
| Repeat Rate ≥35% | Similar across segments | **KEEP** - universal success metric |
| Rating ≥4.0 | Similar across segments | **KEEP** - universal success metric |
| Core Cuisines | Similar restaurant preferences | **KEEP** - universal appeal |
| Tier 1 Dishes | Family-specific criteria matter | **KEEP** - but acknowledge non-family usage |

**Conclusion:** MVP thresholds are appropriate. Outcome metrics (repeat, rating) are segment-agnostic. Selection criteria (dishes, cuisines) work for all segments.

---

## Strategic Implications

### 1. Dinneroo Works for Non-Families Too

54% of post-order respondents are NOT traditional families (couples, singles, friends, other). They're equally satisfied and equally likely to repeat.

**Opportunity:** Consider broadening positioning from "Family Dinneroo" to "Share for £25" or "Dinner for 2-4" without changing the product.

### 2. Family-Specific Factors Are Validated

The 30x difference in "child appeal" citation (31% families vs 1% others) validates:
- Keeping `kids_full_happy` in scoring
- Keeping `fussy_eater_friendly` in scoring
- Maintaining family-focused dish curation

### 3. Value is Universal

£25 value proposition is the #1 driver across ALL segments:
- Families: 59% cite it
- Couples: 53% cite it
- Singles: 56% cite it

**Implication:** Price positioning is working universally, not just for families.

---

## Recommendations

### No Changes Needed to Frameworks

1. **Dish Scoring:** Keep current weights. Family-specific factors validated.
2. **MVP Thresholds:** Keep current criteria. Work for all segments.

### Consider for Future

1. **Positioning Research:** Test "Share for £25" messaging with non-families
2. **Segment Tracking:** Monitor non-family usage as % of orders
3. **Cuisine Curation:** Current approach works for all segments

---

## Data Sources

| Source | Records | Used For |
|--------|---------|----------|
| `POST_ORDER_ALCHEMER_2026-01-06.csv` | 1,599 | Satisfaction, repeat intent, decision criteria |
| `DROPOFF_ALCHEMER_2026-01-06.csv` | 942 | Barriers, appeal factors |

## Output Files

| File | Description |
|------|-------------|
| `DATA/3_ANALYSIS/segment_comparison.csv` | Summary of segment differences |
| `DATA/3_ANALYSIS/segment_comparison_detailed.json` | Full analysis with all metrics |

---

*Analysis completed January 2026. Frameworks validated - no changes required.*


