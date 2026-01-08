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

### MVP Inflection Points (Data-Driven)

| Dimension | Inflection | Evidence | Source |
|-----------|------------|----------|--------|
| Partners | 3-4 | +4.5pp repeat rate | `mvp_threshold_discovery.json` |
| Cuisines | 3-4 | +4.2pp repeat rate | `mvp_threshold_discovery.json` |
| Dishes/Partner | 4-5 | +12.1pp rating | `mvp_threshold_discovery.json` |

**Note:** Inflection points show where metrics improve; business targets are higher to ensure redundancy.

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


