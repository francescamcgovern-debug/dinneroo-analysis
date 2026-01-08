# Definitions & Calculations

## How to Calculate Key Metrics

This document defines HOW to calculate metrics consistently. It does not contain findings.

---

## Customer Frequency (Based on Recency)

Calculate frequency based on **days since last order**:

| Category | Days Since Last Order | Equivalent Behavior |
|----------|----------------------|---------------------|
| **Very High** | <7 days | Daily / few times a week |
| **High** | 7-14 days | About once a week / few times a month |
| **Medium** | 14-30 days | Once a month |
| **Low** | 30-90 days | Less than once a month / every few months |
| **Very Low** | >90 days | Dormant / churned |

### Implementation

```python
def categorize_frequency(days_since_last_order):
    if days_since_last_order < 7:
        return 'Very High'
    elif days_since_last_order <= 14:
        return 'High'
    elif days_since_last_order <= 30:
        return 'Medium'
    elif days_since_last_order <= 90:
        return 'Low'
    else:
        return 'Very Low'

# Calculate days since last order
from datetime import datetime
today = datetime.now()
df['days_since_last_order'] = (today - pd.to_datetime(df['last_order_date'])).dt.days
df['frequency_category'] = df['days_since_last_order'].apply(categorize_frequency)
```

---

## Satisfaction

### Satisfaction Rate
**Definition:** % of respondents who are "Very Satisfied" OR "Satisfied"

```python
satisfied = df['SATISFACTION'].isin(['Very Satisfied', 'Satisfied'])
satisfaction_rate = satisfied.mean() * 100
```

### Satisfaction Score (Numeric)
| Response | Score |
|----------|-------|
| Very Satisfied | 5 |
| Satisfied | 4 |
| Neutral | 3 |
| Dissatisfied | 2 |
| Very Dissatisfied | 1 |

---

## Dish Sentiment

### "Loved It" Rate
**Definition:** % who selected "Loved it" (highest rating only)

```python
loved_it_rate = (df['DISH_SENTIMENT'] == 'Loved it').mean() * 100
```

### Dish Sentiment Score
| Response | Score |
|----------|-------|
| Loved it | 5 |
| Liked it | 4 |
| Neutral | 3 |
| Disliked it | 2 |
| Hated it | 1 |

---

## Strong Advocates

**Definition:** Customers who meet ALL THREE criteria:
1. `DISH_SENTIMENT` = "Loved it"
2. `SATISFACTION` = "Very Satisfied"
3. `REORDER_NEWPARTNER` in ["Agree", "Strongly agree"]

```python
strong_advocate = (
    (df['DISH_SENTIMENT'] == 'Loved it') &
    (df['SATISFACTION'] == 'Very Satisfied') &
    (df['REORDER_NEWPARTNER'].isin(['Agree', 'Strongly agree']))
)
df['Strong_Advocate'] = strong_advocate
```

**Rationale:** Uses highest bars for each metric to identify genuinely enthusiastic customers with platform loyalty (not just loyalty to one restaurant).

---

## Family Definition

### Is_Family Flag
**Definition:** TRUE if customer has children OR is ordering for family

```python
df['Is_Family'] = (
    (pd.to_numeric(df['NUM_CHILDREN'], errors='coerce') >= 1) |
    df['WHO_ORDERING'].str.contains('family', case=False, na=False)
)
```

### Family Sub-Segments (if needed)

Based on youngest child's age:
| Segment | Youngest Child Age |
|---------|-------------------|
| Young Families | 0-8 years |
| Older Families | 9-15+ years |

---

## Dropoff Segments

Based on survey question: "How far did you get with your exploration?"

| Segment | Response | Interpretation |
|---------|----------|----------------|
| **Tried Before** | "I placed an order" | Retention challenge |
| **Never Tried** | All other responses | Acquisition challenge |

```python
tried_before = df[df['exploration_question'] == 'I placed an order']
never_tried = df[df['exploration_question'] != 'I placed an order']
```

⚠️ **These segments were shown different questions.** Analyze separately.

---

## B10 Issues (Order Problems)

**Definition:** Any order with at least one issue flag = "Yes"

```python
b10_cols = ['ORDER_B10_CANCELLED', 'ORDER_B10_LATE', 'ORDER_B10_VERY_LATE', 
            'ORDER_B10_MISSING', 'ORDER_B10_OMDNR', 'B10_SPOILED']
df['has_b10_issue'] = df[b10_cols].isin(['Yes']).any(axis=1)
b10_rate = df['has_b10_issue'].mean() * 100
```

---

## Zone Metrics

### Zone Counts (Critical Distinction)

| Count | Value | Source | Definition |
|-------|-------|--------|------------|
| **Total Zones** | 1,306 | Anna's ground truth | All Deliveroo zones in UK/Ireland |
| **Supply Zones** | 434 | Anna's ground truth | Zones with Dinneroo partners configured |
| **Live Zones** | 201 | Snowflake orders | Zones with actual Dinneroo orders during trial |
| **Analysis Zones** | 197 | MVP threshold analysis | Live zones with sufficient data for statistical analysis |

⚠️ **Always specify which zone count you're using.** "201 zones" = behavioral data. "1,306 zones" = supply data.

### Zone Health Score Components

| Component | Weight | Source |
|-----------|--------|--------|
| Repeat Rate | 30% | Snowflake orders |
| Satisfaction | 25% | Survey / Ratings |
| Cuisine Coverage | 20% | Anna's zone data |
| Dish Variety | 15% | Anna's zone data |
| Volume | 10% | Snowflake orders |

### MVP Thresholds (Business Targets)

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Repeat Rate | ≥35% | `config/mvp_thresholds.json` |
| Rating | ≥4.0 | `config/mvp_thresholds.json` |
| Core Cuisines | 5 of 7 | `config/mvp_thresholds.json` |
| Partners | ≥5 | `config/mvp_thresholds.json` |

### MVP Status Tiers

**Definition:** Zone readiness based on Core 7 cuisine count

| Status | Cuisine Count | Description |
|--------|---------------|-------------|
| **MVP Ready** | 5+ of 7 | North star - full family offering |
| **Near MVP** | 4 of 7 | Almost there - 1 cuisine gap |
| **Progressing** | 3 of 7 | Data inflection point - meaningful variety |
| **Developing** | 1-2 of 7 | Early stage - limited options |
| **Supply Only** | Any | Has partners but no orders yet |
| **Not Started** | 0 | No Dinneroo partners |

**Implementation:** Use `scripts/utils/definitions.py`:
```python
from utils.definitions import get_mvp_status

mvp_status = get_mvp_status(core_7_count=4, has_orders=True)  # Returns "Near MVP"
```

### MVP Inflection Points (Data-Driven)

| Dimension | Inflection | Evidence | Source |
|-----------|------------|----------|--------|
| Partners | 3-4 | +4.5pp repeat rate | `mvp_threshold_discovery.json` |
| Cuisines | 3-4 | +4.2pp repeat rate | `mvp_threshold_discovery.json` |
| Dishes/Partner | 4-5 | +12.1pp rating | `mvp_threshold_discovery.json` |

**Note:** Inflection points show where metrics improve; business targets are higher to ensure redundancy.

---

## Dish Taxonomy (Anna's 24 Types) - v3.3

### The Three-Level Structure

All dish analysis uses Anna's authoritative taxonomy:

```
155 Menu Items → 58 Granular Dishes → 24 High-Level Dish Types
```

| Level | Count | Example | Use |
|-------|-------|---------|-----|
| **Menu Item** | 155 | "Chicken Berry Britannia" (Dishoom) | Full traceability |
| **Granular Dish** | 58 | "Biryani" | Detailed analysis |
| **High-Level Dish** | 24 | "Biryani" | Rankings, scoring |

### The 24 High-Level Dish Types

| # | Dish Type | Items | Partners |
|---|-----------|-------|----------|
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
| 11-24 | Other, Protein & Veg, Lasagne, Burrito, Fajitas, Shawarma, Chilli, Tacos, Nachos, Pho, Poke, Quesadilla, Shepherd's Pie, Sushi | 1-4 each | Various |

### Reference Files

| File | Description |
|------|-------------|
| `config/dish_taxonomy.csv` | Full 155-item reference with all mappings |
| `DATA/3_ANALYSIS/dish_type_rollup.csv` | Aggregated to 24 high-level types |
| `config/dish_type_performance_mapping.csv` | Maps our performance data to Anna's types |

---

## Multi-List Scoring Framework (v3.3)

### Key Insight: Segment-Specific Rankings

**We now produce THREE separate rankings** because families and couples have different needs:

1. **Family Performers** - Best dishes for families with children
2. **Couple Performers** - Best dishes for adults without children
3. **Recruitment Priorities** - Dishes NOT on Dinneroo with highest potential

### Family Performers Weights (40/20/20/15/5)

| Factor | Weight | Source | Rationale |
|--------|--------|--------|-----------|
| kids_happy | 40% | Post-order survey (families) | Kids' reaction determines repeat |
| fussy_eater_friendly | 20% | dish_opportunity_scores | Must work for picky kids |
| orders_per_zone | 20% | Snowflake | Proven demand |
| adult_satisfaction | 15% | Post-order survey (families) | Parents must enjoy it too |
| portions_adequate | 5% | Post-order survey | Needs to feed the family |

### Couple Performers Weights (40/25/20/15)

| Factor | Weight | Source | Rationale |
|--------|--------|--------|-----------|
| adult_satisfaction | 40% | Post-order survey | Primary driver for couples |
| rating | 25% | Snowflake | Quality matters to adults |
| orders_per_zone | 20% | Snowflake | Proven demand |
| adult_appeal | 15% | dish_opportunity_scores | Sophisticated options |

### Recruitment Priorities Weights (30/25/15/15/10/5)

| Factor | Weight | Source | Rationale |
|--------|--------|--------|-----------|
| latent_demand_mentions | 30% | Open-text surveys | Explicit customer requests |
| framework_score | 25% | dish_opportunity_scores | Overall family meal fit |
| fussy_eater_friendly | 15% | dish_opportunity_scores | Family appeal |
| gap_score | 15% | dish_opportunity_scores | Supply gap = opportunity |
| partner_capability | 10% | dish_opportunity_scores | Can we get it? |
| non_dinneroo_demand | 5% | Cuisine-level orders | Proven external demand |

### Scoring Method

All factors use **percentile-based 1-5 scoring**:

| Percentile | Score |
|------------|-------|
| Top 20% | 5 |
| 60-80% | 4 |
| 40-60% | 3 |
| 20-40% | 2 |
| Bottom 20% | 1 |

### Output Files

| File | Description |
|------|-------------|
| `dish_family_performers.csv` | Family rankings |
| `dish_couple_performers.csv` | Couple rankings |
| `dish_recruitment_priorities.csv` | Off-platform targets |
| `DISH_RANKINGS_WITH_ROLLUP.csv` | Combined view with item rollup |

---

## Cuisine Definitions (Unified)

**CANONICAL SOURCE:** `scripts/utils/definitions.py`

All agents MUST import from this module to ensure consistency.

### Core 7 Cuisines

| Cuisine | Required for MVP | Description |
|---------|-----------------|-------------|
| Asian | Yes | Japanese, Thai, Vietnamese, Chinese, Korean |
| Italian | Yes | Pizza, pasta, Italian classics |
| Indian | Yes | Curries, biryanis, Indian classics |
| Healthy | Yes | Grain bowls, salads, protein-focused |
| Mexican | Yes | Burritos, tacos, Latin flavours |
| Middle Eastern | No | Lebanese, Turkish, shawarma |
| British | No | Fish & chips, pies, roasts |

### Two-Level Cuisine Structure

| Level | Purpose | Example |
|-------|---------|---------|
| **Core 7** | MVP calculations, zone status | "Asian" |
| **Sub-Cuisine** | Granular analysis, drill-down | "Japanese", "Vietnamese" |

**Implementation:**
```python
from utils.definitions import get_core_7, get_sub_cuisine

get_core_7("Japanese")     # Returns "Asian"
get_core_7("Italian")      # Returns "Italian"
get_sub_cuisine("Katsu")   # Returns "Japanese"
```

### Sub-Cuisine to Core 7 Mapping

| Sub-Cuisine | Core 7 |
|-------------|--------|
| Japanese, Thai, Vietnamese, Chinese, Korean | Asian |
| Lebanese, Turkish, Mediterranean, Greek | Middle Eastern |
| Tex-Mex, Latin American | Mexican |
| Salads, Grain Bowls | Healthy |
| Pizza, Pasta | Italian |
| Roasts, Pies | British |

### Cuisine Pass

**Definition:** Zone has 5+ of 7 Core cuisines

```python
from utils.definitions import get_cuisine_pass

cuisine_pass = get_cuisine_pass(core_7_count=5)  # Returns True
```

---

## Dinneroo Menu Structure

### What is a "Dish"?

A **dish** is a meal option within a Dinneroo family bundle - NOT individual components or sides.

**Example:** A Pho family bundle (£25) might include:
- Adult: Pho soup (1 dish)
- Kid: Rice bowl (1 dish)
- Sides: Spring rolls, prawn crackers (not counted as dishes)

This bundle contains **2 dishes** - the main meal choices available to family members.

### Dishes per Partner

**Definition:** The total number of distinct meal options a partner offers across all their Dinneroo bundles.

**Example:**
- Pho offers: Pho, Rice Bowl, Pad Thai, Kids Noodles = 4 dishes
- Nando's offers: Chicken Platter, Wrap, Kids Chicken, Veggie Option = 4 dishes

### Why This Matters

- Partners with more dishes give families more choice within the £25 bundle
- A partner with 5+ dishes can satisfy diverse family preferences (fussy kids, dietary needs)
- "Dishes per partner" is a measure of menu depth, not bundle count

### Source

Dish counts come from Anna's curated data: `anna_family_dishes.csv` (142 total dishes across 40 partners)

---

## Statistical Thresholds

| Threshold | Value | Use |
|-----------|-------|-----|
| Statistical significance | p < 0.05 | Only use "significant" with p-value |
| Minimum segment size | n ≥ 20 | Don't report segments smaller than this |
| Minimum for stats | n ≥ 30 | For reliable statistical tests |
| Minimum per group | n ≥ 20 | For comparison analyses |

---

## Reorder Intent

### Positive Reorder Intent
**Definition:** % who "Agree" or "Strongly agree" to reorder

```python
reorder_intent = df['REORDER_DISH'].isin(['Agree', 'Strongly agree']).mean() * 100
```

---

*These are calculation methods. Apply them to derive your own findings.*


