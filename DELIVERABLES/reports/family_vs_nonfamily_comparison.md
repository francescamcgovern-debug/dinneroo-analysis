# Family vs Non-Family Scoring Comparison

**Generated:** 2026-01-07
**Purpose:** Understand how dish prioritization changes when family-specific factors are removed

## Executive Summary

This analysis compares dish rankings under two scoring frameworks:
1. **Family Framework** (current): Includes `kids_full_happy` (7.5%) and `fussy_eater_friendly` (5.5%)
2. **Non-Family Framework** (variant): Removes these factors and redistributes 13% to remaining factors

**Key Finding:** 5 dishes rank HIGHER without family factors, 4 rank LOWER. 10 dishes are stable in top 10 under both frameworks.

---

## 1. Framework Weight Comparison

### Family Framework Weights (Current)

| Factor | Weight | Family-Specific? |
|--------|--------|------------------|
| Normalized Sales | 10.0% | No |
| Zone Ranking | 10.0% | No |
| Deliveroo Rating | 10.0% | No |
| Repeat Intent | 5.0% | No |
| Kids Full Happy | 7.5% | Yes |
| Liked Loved | 7.5% | No |
| Latent Demand | 25.0% | No |
| Adult Appeal | 10.2% | No |
| Balanced Guilt Free | 9.2% | No |
| Fussy Eater Friendly | 5.5% | Yes |

**Total:** 100%

### Non-Family Framework Weights (Variant)

| Factor | Weight |
|--------|--------|
| Normalized Sales | 11.5% |
| Zone Ranking | 11.5% |
| Deliveroo Rating | 11.5% |
| Repeat Intent | 5.7% |
| Liked Loved | 8.6% |
| Latent Demand | 28.7% |
| Adult Appeal | 11.8% |
| Balanced Guilt Free | 10.6% |

**Total:** 100%

**Redistribution Logic:** The 13% from removed family factors is distributed proportionally to remaining factors (each factor increases by ~15% relative to its original weight).

---

## 2. Top 20 Dishes: Side-by-Side Comparison

### Under Family Framework

| Rank | Dish | Family Score | Non-Family Rank |
|------|------|--------------|-----------------|
| 1 | Indian Curry | 4.29 | 1 |
| 2 | Pho | 4.29 | 2 |
| 3 | East Asian Curry | 4.08 | 3 |
| 4 | Katsu | 4.07 | 4 |
| 5 | Noodles | 4.03 | 6 |
| 6 | Lasagne | 3.91 | 5 |
| 7 | Sushi | 3.77 | 9 |
| 8 | Risotto | 3.74 | 7 |
| 9 | Pizza | 3.74 | 10 |
| 10 | Pastry Pie | 3.70 | 8 |
| 11 | Pasta | 3.68 | 11 |
| 12 | Biryani | 3.67 | 13 |
| 13 | Casserole / Stew | 3.53 | 12 |
| 14 | Protein & Veg | 3.52 | 14 |
| 15 | Paella | 3.46 | 15 |
| 16 | Shepherd's Pie | 3.28 | 22 |
| 17 | Fajitas | 3.23 | 23 |
| 18 | Shawarma | 3.22 | 20 |
| 19 | Fried Rice | 3.19 | 24 |
| 20 | Rice Bowl | 3.17 | 25 |

### Under Non-Family Framework

| Rank | Dish | Non-Family Score | Family Rank |
|------|------|------------------|-------------|
| 1 | Indian Curry | 4.34 | 1 |
| 2 | Pho | 4.34 | 2 |
| 3 | East Asian Curry | 4.10 | 3 |
| 4 | Katsu | 3.96 | 4 |
| 5 | Lasagne | 3.93 | 6 |
| 6 | Noodles | 3.92 | 5 |
| 7 | Risotto | 3.82 | 8 |
| 8 | Pastry Pie | 3.77 | 10 |
| 9 | Sushi | 3.74 | 7 |
| 10 | Pizza | 3.67 | 9 |
| 11 | Pasta | 3.60 | 11 |
| 12 | Casserole / Stew | 3.58 | 13 |
| 13 | Biryani | 3.57 | 12 |
| 14 | Protein & Veg | 3.57 | 14 |
| 15 | Paella | 3.49 | 15 |
| 16 | Tagine | 3.21 | 23 |
| 17 | Sausage & Mash | 3.16 | 21 |
| 17 | Jacket Potato | 3.16 | 21 |
| 19 | Tacos | 3.14 | 24 |
| 20 | Shawarma | 3.11 | 18 |

---

## 3. Biggest Movers

### Dishes That BENEFIT from Non-Family Focus (Rank UP)

These dishes rank higher when family factors are removed - good candidates if targeting couples/singles.

| Dish | Family Rank | Non-Family Rank | Change | Why |
|------|-------------|-----------------|--------|-----|
| Tagine | 23 | 16 | +7 | Lower fussy-eater score (2.5) doesn't penalize |
| Tacos | 24 | 19 | +5 | Lower fussy-eater score (3.5) doesn't penalize |
| Fish & Chips | 25 | 20 | +5 | Lower fussy-eater score (3.5) doesn't penalize |
| Sausage & Mash | 21 | 17 | +4 | Lower fussy-eater score (3.5) doesn't penalize |
| Jacket Potato | 21 | 17 | +4 | Lower fussy-eater score (3.5) doesn't penalize |

### Dishes That BENEFIT from Family Focus (Rank DOWN without it)

These dishes depend on family factors for their ranking - validates family-specific curation.

| Dish | Family Rank | Non-Family Rank | Change | Why |
|------|-------------|-----------------|--------|-----|
| Shepherd's Pie | 16 | 22 | -6 | High fussy-eater score (4.5) no longer helps |
| Fajitas | 17 | 23 | -6 | High fussy-eater score (3.5) no longer helps |
| Fried Rice | 19 | 24 | -5 | High fussy-eater score (4.5) no longer helps |
| Rice Bowl | 20 | 25 | -5 | High fussy-eater score (4.5) no longer helps |

---

## 4. Universally Strong Dishes

These dishes rank in the top 10 under BOTH frameworks - they work for families AND non-families.

| Dish | Family Rank | Non-Family Rank | Family Score | Non-Family Score |
|------|-------------|-----------------|--------------|------------------|
| Indian Curry | 1 | 1 | 4.29 | 4.34 |
| Pho | 2 | 2 | 4.29 | 4.34 |
| East Asian Curry | 3 | 3 | 4.08 | 4.10 |
| Katsu | 4 | 4 | 4.07 | 3.96 |
| Noodles | 5 | 6 | 4.03 | 3.92 |
| Lasagne | 6 | 5 | 3.91 | 3.93 |
| Sushi | 7 | 9 | 3.77 | 3.74 |
| Risotto | 8 | 7 | 3.74 | 3.82 |
| Pizza | 9 | 10 | 3.74 | 3.67 |
| Pastry Pie | 10 | 8 | 3.70 | 3.77 |

**Implication:** These dishes are "safe bets" regardless of target audience.

---

## 5. Strategic Implications

### If Rankings Change Significantly
- Family-specific curation **matters** - the 13% weight on family factors creates meaningful differentiation
- Removing family factors would change which dishes we prioritize

### If Rankings Are Stable
- Family factors **don't significantly change** the priority order
- Core dishes work for everyone - family positioning is about marketing, not menu

### Recommendation

Based on this analysis:

1. **Universally strong dishes** (10 dishes): Prioritize regardless of segment
2. **Family-dependent dishes** (4 dishes): Important for family value prop
3. **Non-family opportunities** (5 dishes): Consider if expanding beyond families

---

## 6. Full Comparison Data

See `DATA/3_ANALYSIS/family_vs_nonfamily_scores.csv` for complete dish-by-dish comparison including all component scores.

### Column Definitions

| Column | Description |
|--------|-------------|
| dish_type | Dish category |
| family_score | Composite score under Family framework |
| nonfamily_score | Composite score under Non-Family framework |
| family_rank | Rank under Family framework (1 = highest) |
| nonfamily_rank | Rank under Non-Family framework |
| rank_change | Positions moved (+ = up in non-family, - = down) |
| mover_type | Classification: Up/Down/Stable |
| [component scores] | Individual factor scores (1-5 scale) |

---

*Analysis generated by `scripts/phase2_analysis/08_nonfamily_scoring_comparison.py`*
