# Dish Scoring Methodology

## Purpose

This document describes the complete methodology for scoring and prioritizing dishes for Dinneroo using the **Multi-List Scoring Framework v3.3** with **segment-specific rankings** aligned to **Anna's 24-dish taxonomy**.

---

## Multi-List Scoring Framework v3.3

### Key Insight: Different Segments Need Different Rankings

**We now produce THREE separate rankings** because families and couples have different needs:

1. **Family Performers** - Best dishes for families with children
2. **Couple Performers** - Best dishes for adults without children
3. **Recruitment Priorities** - Dishes NOT on Dinneroo with highest potential

### Dish Taxonomy Alignment

All rankings use **Anna's 24 high-level dish types** as the unit of analysis:

```
155 Menu Items → 58 Granular Dishes → 24 High-Level Dish Types
```

Example rollup:
- "Chicken Berry Britannia" (Dishoom) → Biryani (granular) → **Biryani** (high-level)
- "Mac N Cheese with Brisket" (Bill's) → Mac & Cheese (granular) → **Pasta** (high-level)

**Reference files:**
- `config/dish_taxonomy.csv` - Full 155-item reference
- `DATA/3_ANALYSIS/dish_type_rollup.csv` - Aggregated to 24 types

---

## The Three Lists

### List 1: Family Performers

**For:** Families with children ordering from Dinneroo
**Key question:** "What dishes make kids AND parents happy?"

| Factor | Weight | Source | Rationale |
|--------|--------|--------|-----------|
| Kids happy | 40% | Post-order survey (families) | Kids' reaction determines repeat orders |
| Fussy eater friendly | 20% | dish_opportunity_scores | Must work for picky kids |
| Orders per zone | 20% | Snowflake orders | Proven demand |
| Adult satisfaction | 15% | Post-order survey (families) | Parents must enjoy it too |
| Portions adequate | 5% | Post-order survey | Needs to feed the family |

**Output:** `DATA/3_ANALYSIS/dish_family_performers.csv`

**Top Family Performers:**
1. Rice Bowl (score: 4.45)
2. South Asian / Indian Curry (score: 3.95)
3. Noodles (score: 3.95)
4. Fried Rice (score: 3.85)
5. Pasta (score: 3.65)

---

### List 2: Couple Performers

**For:** Adults/couples without children
**Key question:** "What dishes satisfy adult tastes?"

| Factor | Weight | Source | Rationale |
|--------|--------|--------|-----------|
| Adult satisfaction | 40% | Post-order survey (non-families) | Primary driver |
| Rating | 25% | Snowflake ratings | Quality matters to adults |
| Orders per zone | 20% | Snowflake orders | Proven demand |
| Adult appeal | 15% | dish_opportunity_scores | Sophisticated options |

**Output:** `DATA/3_ANALYSIS/dish_couple_performers.csv`

**Top Couple Performers:**
1. Noodles (score: 5.00)
2. South Asian / Indian Curry (score: 4.80)
3. Pho (score: 4.35)
4. Other (score: 4.15)
5. Grain Bowl (score: 4.00)

---

### List 3: Recruitment Priorities

**For:** Dishes NOT currently on Dinneroo
**Key question:** "What should we recruit next?"

| Factor | Weight | Source | Rationale |
|--------|--------|--------|-----------|
| Latent demand mentions | 30% | Open-text survey | Explicit customer requests |
| Framework score | 25% | dish_opportunity_scores | Overall family meal fit |
| Fussy eater friendly | 15% | dish_opportunity_scores | Family appeal |
| Gap score | 15% | dish_opportunity_scores | Supply gap = opportunity |
| Partner capability | 10% | dish_opportunity_scores | Can we get it? |
| Non-dinneroo demand | 5% | Cuisine-level orders | Proven external demand |

**Output:** `DATA/3_ANALYSIS/dish_recruitment_priorities.csv`

**Top Recruitment Priorities:**
1. Chinese Family Meal (score: 3.65, 58 latent mentions)
2. Rotisserie Chicken (score: 3.10)
3. Greek Mezze (score: 3.05, 6 latent mentions)

---

## Scoring Method: Percentile-Based

All factors use **percentile-based 1-5 scoring**:

| Percentile | Score |
|------------|-------|
| Top 20% | 5 |
| 60-80% | 4 |
| 40-60% | 3 |
| 20-40% | 2 |
| Bottom 20% | 1 |

This ensures natural distribution and avoids compressed score ranges.

---

## Deliverables

### Main Output: DISH_RANKINGS_WITH_ROLLUP.csv

Combined view showing all 24 dish types with:
- Family rank and score
- Couple rank and score
- Item count (how many menu items roll up)
- Items sample (example menu items)
- Partners (which brands offer this dish type)

### Supporting Files

| File | Description |
|------|-------------|
| `DISH_FAMILY_RANKINGS.csv` | Family performers with full detail |
| `DISH_COUPLE_RANKINGS.csv` | Couple performers with full detail |
| `DISH_RECRUITMENT_PRIORITIES.csv` | Off-platform recruitment targets |
| `dish_taxonomy.csv` | Full 155-item reference |

---

## Strategic Context: Balanced Midweek Meals

**Dinneroo is positioned for BALANCED MIDWEEK MEALS** - not indulgent weekend treats.

When analyzing dishes, consider:
- Does this fit the "Tuesday night dinner I feel good about" positioning?
- Balanced = protein + veg + carbs in reasonable proportions
- Grilled chicken with customizable sides aligns well with this positioning
- Pure "treat" food (heavy pizza, burgers) may be positioning mismatches

---

## ⚠️ CRITICAL: Think DISH TYPES, Not Brands

**The question isn't "should we recruit Nando's?" - it's "do families want Grilled Chicken with Customizable Sides?"**

### The Reframe

| Instead of asking... | Ask... |
|---------------------|--------|
| "Should we recruit Nando's?" | "Do families want **Grilled Chicken with Customizable Sides**?" |
| "Should we recruit Farmer J?" | "Do families want **Healthy Balanced Meals**?" |
| "Should we recruit Pasta Evangelists?" | "Do families want **Fresh Premium Pasta**?" |

### Why This Matters

1. **Brand-thinking limits options** - If we think "Nando's", we might miss that Pepe's Piri Piri serves the same need
2. **Dish-type thinking expands options** - "Grilled Chicken" can be fulfilled by multiple partners
3. **Strategic clarity** - Focus on what families want to eat, not specific commercial relationships

---

## ⚠️ CRITICAL: Survivorship Bias

**The dishes performing well are the dishes we HAVE, not necessarily the dishes families WANT.**

### The Problem

Order volume data only shows what succeeds among AVAILABLE options. It does NOT capture:
1. Dishes families want but don't expect on delivery (fish & chips, roast dinner, pies)
2. Cuisines underrepresented in the current partner mix (Chinese family meals)
3. Options for families who CAN'T use Dinneroo due to dietary restrictions

### Required Action

For ANY dish prioritization analysis:
1. **State the survivorship bias caveat** upfront in findings
2. **Analyze open-text** for unprompted dish/cuisine mentions
3. **Use Recruitment Priorities list** to identify unmet demand

---

## The 24 High-Level Dish Types (Anna's Taxonomy)

| # | Dish Type | Menu Items | Partners |
|---|-----------|------------|----------|
| 1 | Pasta | 23 | Bella Italia, Bill's, Prezzo, etc. |
| 2 | Rice Bowl | 21 | Banana Tree, Itsu, Kokoro, etc. |
| 3 | Grain Bowl | 17 | Farmer J, LEON, Remedy Kitchen |
| 4 | South Asian / Indian Curry | 13 | Dishoom, Chaska, Kricket |
| 5 | Noodles | 13 | Wagamama, Pho, Banana Tree |
| 6 | East Asian Curry | 11 | Giggling Squid, Ting Thai |
| 7 | Katsu | 9 | Wagamama, Itsu, Kokoro |
| 8 | Biryani | 6 | Dishoom, Chaska, Tadka House |
| 9 | Fried Rice | 5 | Asia Villa, Pho |
| 10 | Pizza | 5 | Milano, PizzaExpress, Prezzo |
| 11 | Other | 4 | Shaku Maku, Umi Falafel |
| 12 | Protein & Veg | 4 | Cocotte, Shaku Maku |
| 13 | Lasagne | 3 | Bella Italia, Cacciari's |
| 14 | Burrito / Burrito Bowl | 3 | Tula Ireland, Zambrero |
| 15 | Fajitas | 3 | Las Iguanas |
| 16 | Shawarma | 3 | Bill's |
| 17 | Chilli | 3 | Las Iguanas |
| 18 | Tacos | 3 | Tula Ireland, Zambrero |
| 19 | Quesadilla | 1 | Tula Ireland |
| 20 | Nachos | 1 | Zambrero |
| 21 | Pho | 1 | Pho |
| 22 | Poke | 1 | Itsu |
| 23 | Shepherd's Pie | 1 | Bill's |
| 24 | Sushi | 1 | Itsu |

---

## Implementation

### Configuration

`config/scoring_framework_v3.json` - Contains all weights and definitions

### Output Files

```
DATA/3_ANALYSIS/
├── dish_family_performers.csv
├── dish_couple_performers.csv
├── dish_recruitment_priorities.csv
├── dish_type_rollup.csv
└── dish_performance_anna_aligned.csv

DELIVERABLES/reports/
├── DISH_RANKINGS_WITH_ROLLUP.csv
├── DISH_FAMILY_RANKINGS.csv
├── DISH_COUPLE_RANKINGS.csv
└── DISH_RECRUITMENT_PRIORITIES.csv

config/
├── dish_taxonomy.csv
├── dish_type_performance_mapping.csv
└── scoring_framework_v3.json
```

### Quality Checks

Before finalizing:
- [ ] All rankings use Anna's 24 dish types
- [ ] Family list prioritizes kids_happy
- [ ] Couple list prioritizes adult_satisfaction
- [ ] Recruitment list shows dishes NOT on platform
- [ ] No brand names in dish types

---

## Changelog

| Version | Changes |
|---------|---------|
| v3.3 | Three-list approach: Family, Couple, Recruitment. Aligned to Anna's 24 dish taxonomy. |
| v3.2 | Renamed 'Opportunity' to 'Demand'. Added percentile-based scoring. |
| v3.1 | Removed zone_ranking_strength. |
| v3.0 | Unified framework - same 5 factors for cuisine and dish. |

---

*This methodology ensures dish prioritization is based on what different customer segments actually need, with transparent and adjustable weighting.*
