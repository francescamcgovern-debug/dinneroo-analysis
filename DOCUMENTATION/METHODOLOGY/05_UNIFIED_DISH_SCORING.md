# Unified Dish Scoring Framework

## Overview

This framework merges **Anna's Hit List** (performance-focused) with the **Family Fit Framework** (positioning-focused) to create a comprehensive dish scoring system.

---

## Why Merge?

| Approach | Strength | Weakness |
|----------|----------|----------|
| **Anna's Hit List** | Strong behavioral data (what sells) | Doesn't capture family-specific fit |
| **Family Fit Framework** | Captures Dinneroo positioning | Light on actual performance data |
| **Unified** | Both performance AND fit | More complex, more data required |

**The unified approach ensures we prioritize dishes that BOTH perform well AND fit Dinneroo's family positioning.**

---

## Framework Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                 UNIFIED DISH SCORING (100%)                      │
├─────────────────────────────────────────────────────────────────┤
│  PERFORMANCE (35%)                    ← Anna's behavioral data  │
│  ├── Normalized Sales (10.5%)         Looker                    │
│  ├── Zone Ranking Strength (8.75%)    Looker                    │
│  ├── Deliveroo Rating (8.75%)         Looker                    │
│  └── Repeat Intent (7%)               Post-Order Survey         │
├─────────────────────────────────────────────────────────────────┤
│  SATISFACTION (20%)                   ← Blended survey signals  │
│  ├── Meal Satisfaction (10%)          Post-Order Survey         │
│  └── Kids Happy Rate (10%)            Post-Order Survey         │
├─────────────────────────────────────────────────────────────────┤
│  FAMILY FIT (30%)                     ← Dinneroo positioning    │
│  ├── Kid-Friendly (7.5%)              Survey + Assessment       │
│  ├── Fussy Eater Friendly (7.5%)      Dropoff Survey            │
│  ├── Balanced/Guilt-Free (6%)         Survey + Positioning      │
│  ├── Portion Flexibility (6%)         Post-Order Survey         │
│  └── Customisation (3%)               Dropoff Survey            │
├─────────────────────────────────────────────────────────────────┤
│  OPPORTUNITY (15%)                    ← Growth potential        │
│  ├── Dish Suitability Rating (5.25%)  Pre-launch R&I (Anna)     │
│  ├── Open-Text Requests (5.25%)       Post-Launch Survey        │
│  └── Availability Gap (4.5%)          Menu Catalog              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Category Details

### 1. Performance (35%) — Anna's Contribution

**Purpose:** What families actually do. Behavioral data showing revealed demand.

| Factor | Weight | Source | Calculation |
|--------|--------|--------|-------------|
| **Normalized Sales** | 10.5% | Looker | Orders / (zones × days listed) |
| **Zone Ranking Strength** | 8.75% | Looker | % zones #1 + % zones top 5 |
| **Deliveroo Rating** | 8.75% | Looker | Average star rating |
| **Repeat Intent** | 7% | Survey | % likely to reorder |

**Why 35%:** Behavioral data is the strongest signal. Anna's normalized metrics prevent availability bias (dishes in more zones don't automatically score higher).

---

### 2. Satisfaction (20%) — Blended Signals

**Purpose:** How families feel about the dish. Combines adult and child satisfaction.

| Factor | Weight | Source | Calculation |
|--------|--------|--------|-------------|
| **Meal Satisfaction** | 10% | Post-Order Survey | % satisfied/very satisfied |
| **Kids Happy Rate** | 10% | Post-Order Survey | % "full and happy" |

**Why 20%:** Satisfaction predicts retention. Kids happy rate is critical—if kids don't eat it, families won't return.

---

### 3. Family Fit (30%) — Dinneroo Positioning

**Purpose:** Does this dish work for Dinneroo's "balanced midweek family meal" positioning?

| Factor | Weight | Source | What It Captures |
|--------|--------|--------|------------------|
| **Kid-Friendly** | 7.5% | Survey + Assessment | Kids will actually eat it |
| **Fussy Eater Friendly** | 7.5% | Dropoff Survey | Mild options for picky eaters |
| **Balanced/Guilt-Free** | 6% | Survey + Positioning | Parents feel good serving it |
| **Portion Flexibility** | 6% | Post-Order Survey | Feeds family of 4 |
| **Customisation** | 3% | Dropoff Survey | Accommodates preferences |

**Why 30%:** Dinneroo isn't just food delivery—it's positioned for balanced midweek family meals. A dish that sells well but doesn't fit this positioning shouldn't be prioritized.

---

### 4. Opportunity (15%) — Growth Potential

**Purpose:** Forward-looking signals for dishes with untapped potential.

| Factor | Weight | Source | What It Captures |
|--------|--------|--------|------------------|
| **Dish Suitability Rating** | 5.25% | Pre-launch R&I | Consumer appeal before launch |
| **Open-Text Requests** | 5.25% | Post-Launch Survey | Explicit unmet demand |
| **Availability Gap** | 4.5% | Menu Catalog | Room for expansion |

**Why 15%:** Opportunity signals help identify growth, but shouldn't override proven performance. A dish people SAY they want isn't as strong as one they actually order.

---

## Scoring Scale

All factors are scored 1-5:

| Score | Meaning |
|-------|---------|
| 5 | Excellent - top performer |
| 4 | Good - above average |
| 3 | Average - meets expectations |
| 2 | Below average - needs improvement |
| 1 | Poor - significant concerns |

**Composite Score** = Weighted sum of all factors (range 1.0 - 5.0)

---

## Tier Classification

Based on composite score:

| Tier | Score | Label | Action |
|------|-------|-------|--------|
| **Tier 1** | 4.0+ | **Must-Have** | Essential for every MVP zone. Prioritize availability. |
| **Tier 2** | 3.5-3.99 | **Should-Have** | Important for zone strength. Recruit where gaps exist. |
| **Tier 3** | 3.0-3.49 | **Nice-to-Have** | Good for variety. Add opportunistically. |
| **Tier 4** | <3.0 | **Monitor** | Investigate underperformance. Consider removal. |

---

## Quadrant Analysis

Plot dishes on **Performance vs Family Fit** axes:

```
                    HIGH FAMILY FIT
                          │
         POTENTIAL        │        STAR ⭐
    (Good fit, not        │    (Proven winner)
     selling - why?)      │    
                          │    ACTION: EXPAND
    ACTION: INVESTIGATE   │
                          │
    ──────────────────────┼──────────────────────
                          │
         QUESTION MARK    │      CASH COW 💰
    (Not fit, not         │    (Selling but 
     selling)             │     off-brand)
                          │    
    ACTION: REVIEW/REMOVE │    ACTION: MAINTAIN
                          │
                    LOW FAMILY FIT
```

---

## Data Requirements

### From Looker (Anna's data)
- [ ] Average sales per dish (normalized for availability)
- [ ] % zones where dish ranks #1
- [ ] % zones where dish ranks top 5
- [ ] Deliveroo rating by dish

### From Post-Order Survey
- [ ] Meal satisfaction score by dish
- [ ] Kids happy rate by dish
- [ ] Repeat intent by dish

### From Pre-Launch Research
- [ ] Dish suitability rating (Anna's R&I)

### From Open-Text Analysis
- [ ] Dish request counts

### From Menu Catalog
- [ ] Dish availability by zone

---

## Evidence Levels

| Level | Criteria | Confidence |
|-------|----------|------------|
| 🟢 **Validated** | 8+ of 13 factors have data | High - strategic decisions |
| 🟡 **Corroborated** | 5-7 factors have data | Medium - directionally correct |
| 🔵 **Estimated** | <5 factors have data | Low - exploration only |

---

## Example Scoring

### Family Chicken Katsu (Wagamama)

| Category | Factor | Score | Weighted |
|----------|--------|-------|----------|
| **Performance** | Normalized Sales | 5 | 0.525 |
| | Zone Ranking | 5 | 0.4375 |
| | Deliveroo Rating | 4 | 0.35 |
| | Repeat Intent | 4 | 0.28 |
| **Satisfaction** | Meal Satisfaction | 4 | 0.40 |
| | Kids Happy | 4 | 0.40 |
| **Family Fit** | Kid-Friendly | 5 | 0.375 |
| | Fussy Eater | 4 | 0.30 |
| | Balanced | 3 | 0.18 |
| | Portions | 4 | 0.24 |
| | Customisation | 3 | 0.09 |
| **Opportunity** | Suitability | 4 | 0.21 |
| | Open-Text | 2 | 0.105 |
| | Availability Gap | 2 | 0.09 |
| | | | |
| **TOTAL** | | | **4.08** |

**Tier: 1 (Must-Have)** ✅

---

## Implementation

### Config File
`config/dish_scoring_unified.json`

### Scoring Script
`scripts/phase2_analysis/01_score_dishes.py` (update to use unified framework)

### Output
- `DATA/3_ANALYSIS/dish_scores_unified.csv`
- `docs/data/priority_dishes.json`

---

## Comparison: Old vs Unified

| Aspect | Old 10-Factor | Unified 13-Factor |
|--------|---------------|-------------------|
| Performance data | 5% (on menu only) | 35% (Anna's metrics) |
| Satisfaction | 8% (adult appeal) | 20% (adult + kids) |
| Family fit | 87% | 30% |
| Opportunity | 0% | 15% |
| Behavioral vs Survey | Survey-heavy | Balanced |

**Key improvement:** The unified framework balances what families SAY (survey) with what they DO (behavioral).

---

## When to Use Which

| Scenario | Framework | Why |
|----------|-----------|-----|
| Scoring existing dishes | Unified | Full data available |
| Evaluating new dish ideas | Family Fit only | No performance data yet |
| Partner recruitment | Opportunity factors | Focus on gaps |
| Zone prioritization | Performance factors | Focus on proven demand |

---

*Configuration: `config/dish_scoring_unified.json`*
*Last updated: 2026-01-06*

