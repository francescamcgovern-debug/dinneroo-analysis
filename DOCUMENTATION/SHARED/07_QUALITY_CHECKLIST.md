# Analysis Quality Validation Checklist

**Document:** Pre-Share Quality Gate  
**Last Updated:** January 2026  
**Purpose:** Catch data integrity, metric definition, and scoring logic issues before sharing analysis

---

## Quick Validation Checklist

Before sharing any analysis, verify ALL of the following:

### Data Integrity

- [ ] Every dish marked `on_dinneroo = TRUE` appears in Item Categorisation ground truth
- [ ] No order volumes shown for dishes NOT on Dinneroo
- [ ] Top 5 dishes by volume match intuition from source data
- [ ] No impossible values (e.g., 100%+ percentages, negative counts)

### Metric Definitions

- [ ] Every composite score has a documented formula
- [ ] Every composite score has explicit weights that sum to 100%
- [ ] No metric appears in multiple scoring tracks (no double-counting)
- [ ] All column names are defined in header comments or COLUMN_DEFINITIONS.md

### Scoring Logic

- [ ] Opportunity scores are based on demand signals, NOT availability gaps
- [ ] Rankings align with or explicitly contradict stated hypotheses (with explanation)
- [ ] No LLM-estimated values without clear flagging

### Completeness

- [ ] All current platform dishes are included (cross-ref Item Categorisation)
- [ ] Sample sizes cited for all survey-based metrics
- [ ] Sales data is normalised (per-dish average, not totals)

---

## Red Flag Categories

### 1. Data Integrity Red Flags

| Red Flag | Example | How to Check |
|----------|---------|--------------|
| **Impossible order volumes** | "Chicken Pie" showing 34,839 orders when no pastry pies exist on Dinneroo | Cross-reference order data against Item Categorisation |
| **Orders for non-existent dishes** | Order volume shown for dishes marked `on_dinneroo = FALSE` | If `on_dinneroo = FALSE`, then `avg_sales_per_dish` should be blank |
| **Metrics don't match source** | Inflated order volumes vs. actual Snowflake data | Spot-check top 5 dishes against source files |
| **Duplicate entries** | Same dish appearing twice with different names | Search for similar dish names, consolidate variants |

### 2. Metric Definition Red Flags

| Red Flag | Example | How to Check |
|----------|---------|--------------|
| **Undefined composite scores** | "What is opportunity_score? What is latent_demand?" | Every composite metric must have explicit formula + weights |
| **Double-counting metrics** | Using "kids full & happy" in both performance AND opportunity | Each metric should appear in exactly ONE scoring track |
| **Same data used twice** | Wishlist in latent_demand AND as separate column | Check for redundant use of same source data |
| **Unclear signal direction** | "Total mentions - is this good or bad?" | Clarify if metric is positive signal, negative signal, or neutral |
| **Missing weights** | "How are these combined?" | All composite scores need explicit percentage weights |

### 3. Scoring Logic Red Flags

| Red Flag | Example | How to Check |
|----------|---------|--------------|
| **Opportunity rewards absence** | "Why would a dish rank highly because it's not available?" | Opportunity = demand signals (wishlist, requests), NOT coverage gaps |
| **Rankings contradict hypotheses** | Noodles/Pasta ranking high when hypothesis said they weren't important | Document if ranking differs from hypothesis and explain why |
| **Arbitrary-looking scores** | LLM-estimated factors producing unexplainable numbers | Flag any score not derived from actual data |
| **Circular logic** | Using dish suitability to calculate opportunity, then using opportunity to recommend dishes | Ensure inputs and outputs are clearly separated |

### 4. Dish List Red Flags

| Red Flag | Example | How to Check |
|----------|---------|--------------|
| **Missing dishes from current mix** | "Where's Fried Rice, Biryani, Chilli, Nachos, Poke, Burrito Bowl?" | Cross-reference against Item Categorisation |
| **Non-dishes included** | "Dumplings aren't dishes, they're sides" | Verify each entry is a standalone meal, not a side/component |
| **Ambiguous dish types** | "What is 'Greek'? What is 'Sweet & Sour'?" | Every dish_type should be a specific, orderable dish category |
| **Granularity inconsistency** | Indian Curry, Korma, Butter Chicken as separate entries | Consolidate variants under parent category |
| **Niche cuisines without justification** | Russian, Indonesian dishes with no Deliveroo supply | Include only if there's realistic recruitment potential |

### 5. Source Data Red Flags

| Red Flag | Example | How to Check |
|----------|---------|--------------|
| **Using total sales instead of average** | "Total sales unfairly biases dishes that appear a lot" | Confirm normalisation: avg_sales_per_dish, not total_sales |
| **Missing key metrics** | "Where's 'ranked top 5 in a zone'?" | Check all metrics from original framework are present |
| **Uncited sample sizes** | No indication of survey response counts | Every survey metric needs n= sample size |
| **Stale data** | Using order data from 6+ months ago | Confirm data recency, flag if outdated |

---

## Validation Rules

### Rule 1: on_dinneroo Consistency

```
IF on_dinneroo = FALSE:
  THEN avg_sales_per_dish = blank
  AND pct_zones_top_5 = blank
  AND deliveroo_rating = blank
  AND meal_satisfaction = blank
  AND repeat_intent = blank
```

### Rule 2: Composite Score Documentation

Every composite score MUST have:
1. **Formula**: How components are combined
2. **Weights**: Percentage contribution of each component (summing to 100%)
3. **Source**: Where each component comes from
4. **Scale**: What the output range means (e.g., 1-5)

**Example - dish_suitability:**
```
Formula: Weighted average of 5 factors
Weights: Familiar (30%) + Time Consuming (25%) + Healthy Enough (20%) + Shareable (12.5%) + Customisable (12.5%)
Source: OG Survey
Scale: 1-5 where 5 = highest Dinneroo value-add
```

### Rule 3: No Double-Counting

Each metric appears in exactly ONE of:
- Performance Track (how well it performs)
- Opportunity Track (is there unmet demand)
- Informational (context only, not in scoring)

**Bad Example:**
- kids_full_happy in Performance (7.5%) AND in Opportunity family_fit (10%)

**Good Example:**
- kids_full_happy in Performance only (7.5%)
- dish_suitability in Opportunity only (15%)

### Rule 4: Demand-Based Opportunity

Opportunity scores should reflect **demand signals**, not **availability**:

| Valid Opportunity Signal | Invalid Opportunity Signal |
|-------------------------|---------------------------|
| Wishlist % (people want it) | Coverage gap % (it's missing) |
| Open-text requests (people ask for it) | Low zone count (few places have it) |
| dish_suitability (families would value it) | Competitor availability |

### Rule 5: Ground Truth Validation

Before finalising any dish list:
1. Load `Dish Analysis Dec-25 - Item Categorisation.csv`
2. Extract unique High-Level Dish values where Include = 1
3. Verify every `on_dinneroo = TRUE` dish appears in this list
4. Flag any discrepancies

---

## Pre-Share Sign-Off

Before sharing analysis externally:

| Check | Owner | Date | Pass/Fail |
|-------|-------|------|-----------|
| Data integrity validation | | | |
| Metric definitions documented | | | |
| No double-counting verified | | | |
| Dish list cross-referenced | | | |
| Sample sizes cited | | | |
| Hypotheses alignment noted | | | |

---

## Related Documents

- [COLUMN_DEFINITIONS.md](../../DELIVERABLES/reports/COLUMN_DEFINITIONS.md) - Full column definitions
- [04_QUALITY_STANDARDS.md](04_QUALITY_STANDARDS.md) - General quality standards
- [03_DEFINITIONS.md](03_DEFINITIONS.md) - Term definitions

---

*Document created: January 2026*  
*Based on: Lessons learned from Dish Analysis Dec-25 feedback*



