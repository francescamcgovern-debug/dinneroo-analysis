# Dinneroo Master Analysis Report

**Date:** January 2026  
**Data:** Snowflake pull 2026-01-05 (80,724 orders, 50,744 customers)

---

## How to Use This Document

This report provides **two tools** for different purposes:

| Tool | Purpose | Key Question | Go To |
|------|---------|--------------|-------|
| **MVP Zone Framework** | Evaluate if a zone has adequate selection | "Is my zone ready?" | [Section 1](#1-mvp-zone-framework) |
| **Priority Dish List** | Identify what dishes to recruit | "What should I recruit?" | [Section 2](#2-priority-dish-list) |

**The workflow:**

```
Zone Evaluation          Gap Identification          Recruitment
(MVP Framework)    →     (What's missing?)     →    (Priority Dish List)
```

---

## 1. MVP Zone Framework

**Purpose:** Evaluate whether a zone has adequate selection to support growth.

### 1.1 Success Metrics

| Metric | Threshold | Evidence |
|--------|-----------|----------|
| **Repeat Rate** | ≥20% | Validated: zones with 20%+ repeat have significantly better outcomes (p<0.001) |
| **Rating** | ≥4.3 | 4.3+ shows significant correlation with repeat rate (p<0.05) |

**Key Finding:** Cuisine count is the STRONGEST predictor of repeat rate (r=0.514). More cuisines = families come back.

### 1.2 Core Cuisines (Need 4 of 5)

These cuisines are required based on **repeat rate performance** (the primary success metric):

| Cuisine | Repeat Rate | Rating | Orders | Why Essential |
|---------|-------------|--------|--------|---------------|
| **Indian** | **23.1%** (highest) | 4.66 | 8,356 | Best retention, excellent family portions |
| **Vietnamese** | **20.7%** | 4.57 | 12,961 | Pho is a top performer, healthy perception |
| **Thai** | 15.8% | 4.33 | 5,098 | Combined with Vietnamese = 18,059 orders |
| **Japanese/Asian** | 16.2% | 4.24 | 14,618 | Highest volume, rice bowls score highest |
| **Italian** | 16.5% | 4.15 | 9,063 | Universal family appeal |

**Note:** "Chicken (Grilled)" was in the original framework but has only 1,077 orders. Consider as Tier 2.

### 1.3 What's Actually Working on Dinneroo

Top 10 dishes by composite score (volume × rating):

| Rank | Dish | Orders | Rating | What It Is |
|------|------|--------|--------|------------|
| 1 | Prawn Crackers | 11,686 | 4.56 | Side dish (accompaniment) |
| 2 | **Family Chicken Katsu** | 11,246 | 4.24 | Japanese rice bowl |
| 3 | **Egg Fried Rice with Chicken** | 9,964 | 4.59 | Asian rice dish |
| 4 | **Pho the Whole Fam** | 7,910 | 4.55 | Vietnamese noodle soup |
| 5 | **Wok-fried Noodles with Chicken** | 7,707 | 4.53 | Asian noodles |
| 6 | **Katsu Chicken Rice Bowl** | 6,144 | 4.44 | Japanese rice bowl |
| 7 | Beef Brisket Pho | 5,419 | 4.58 | Vietnamese noodle soup |
| 8 | **Dishoom Chicken Ruby** | 4,858 | **4.79** | Indian curry (highest rating) |
| 9 | Mini Chicken Noodle Soup | 4,811 | 4.62 | Vietnamese noodle soup |
| 10 | Chicken Teriyaki Rice Bowl | 4,200 | 4.43 | Japanese rice bowl |

**Pattern:** Asian rice bowls, Vietnamese pho, and Indian curries dominate. These are not generic "pizza and pasta" - they're specific dish types that work for families.

### 1.4 AM Zone Checklist

Quick evaluation for Account Managers:

1. Do I have a **Vietnamese partner** (Pho)? ← Top performer
2. Do I have a **Japanese/Asian partner** (Rice bowls, Katsu)?
3. Do I have an **Indian partner** (Curry, highest repeat rate)?
4. Do I have an **Italian partner** (Pasta, Pizza)?
5. Do I have a **Thai partner** (Pad Thai, noodles)?
6. Is my repeat rate above 20%?
7. Is my average rating above 4.3?
8. Do I have at least 4 different cuisines?

| Yes Answers | Status | Action |
|-------------|--------|--------|
| 8 | **MVP Ready** | Focus on growth, not selection |
| 6-7 | **Near MVP** | Fill 1-2 specific gaps |
| 4-5 | **Developing** | Recruit priority cuisines |
| 0-3 | **Early Stage** | Foundational work needed |

### 1.5 Zones Needing Attention

High-priority zones with significant orders but missing core cuisines:

| Zone | Orders | Missing Cuisines | Priority |
|------|--------|------------------|----------|
| Finsbury Park / Harringay | 1,534 | Japanese, Italian, Thai | High |
| Canning Town | 1,314 | Japanese, Vietnamese, Italian, Thai | High |
| Surrey Quays | 1,139 | Japanese, Vietnamese, Italian, Thai | High |
| South Kensington | 676 | Japanese, Vietnamese, Indian, Thai | High |
| St Albans | 559 | Vietnamese, Indian, Thai | High |

---

## 2. Priority Dish List

**Purpose:** Guide recruitment decisions when zones have gaps.

### 2.1 How This List Was Built

Dishes are scored on a **10-factor family meal framework** with survey-backed data where available:

| Factor | Weight | Top Performers |
|--------|--------|----------------|
| Kid-Friendly | 15% | Rice Bowls (95% kids happy), Fajitas (83%) |
| Portion Flexibility | 15% | Fajitas (94%), Rice Bowls (93%) |
| Fussy Eater Friendly | 15% | Fried Rice, Pasta |
| Adult Satisfaction | - | Pho (95%), Pad Thai (92%), Fajitas (94%) |

### 2.2 Tier 1 - Proven Winners (Measured Data)

These dishes have **survey-backed scores** showing they work for families:

| Rank | Dish Type | Score | Orders | Kids Happy | Adults Happy | Evidence |
|------|-----------|-------|--------|------------|--------------|----------|
| 1 | **Rice Bowl** | 3.99 | 6,571 | **95%** | 85% | Measured (n=27) |
| 2 | **Fajitas** | 3.79 | 812 | 83% | **94%** | Measured (n=18) |
| 3 | **Pho** | 3.65 | 9,113 | 84% | **95%** | Measured (n=130) |
| 4 | **Fried Rice** | 3.56 | 11,842 | 88% | 94% | Measured (n=16) |
| 5 | **Shepherd's Pie** | 3.53 | 663 | 75% | **100%** | Measured (n=5) |
| 6 | **Pad Thai** | 3.53 | 5,351 | 79% | 92% | Measured (n=54) |
| 7 | **Pasta** | 3.52 | 4,250 | 82% | 75% | Measured (n=56) |
| 8 | **Shawarma** | 3.44 | 2,603 | 80% | 88% | Measured (n=26) |

### 2.3 Tier 2 - Solid Performers

| Dish Type | Score | Orders | Category | Notes |
|-----------|-------|--------|----------|-------|
| Noodles | 3.29 | 11,783 | Solid Performer | High volume, 72% kids happy |
| Pizza | 3.29 | 2,289 | Solid Performer | 74% kids happy, 76% adult satisfaction |
| Mac & Cheese | 3.29 | 928 | Proven Winner | 81% kids happy |
| Katsu Curry | 3.18 | 2,300 | Solid Performer | 77% kids happy |
| Katsu | 2.97 | 19,220 | Solid Performer | Highest volume single dish type |

### 2.4 Gaps to Fill (Validated Demand)

These dish types have **survey demand but are NOT available** on Dinneroo:

| Dish Type | Score | Survey N | Category | Action |
|-----------|-------|----------|----------|--------|
| **Curry (General)** | 3.18 | 250 | Validated Gap | Recruit Indian partners with family bundles |
| **Chicken (General)** | 2.76 | 115 | Validated Gap | Recruit grilled chicken partners |
| Burrito Bowl | 3.11 | - | Unvalidated Gap | Consider Mexican recruitment |
| Grilled Chicken with Sides | 2.82 | - | Unvalidated Gap | Nando's-style partners |

### 2.5 What Families Mention Most

From survey open-text analysis:

| Dish Type | Mentions | Implication |
|-----------|----------|-------------|
| Rice | 184 | Rice-based dishes are core to family meals |
| Chicken | 131 | Chicken protein is highly desired |
| Curry | 61 | Indian/curry demand is strong |
| Salad | 59 | Healthy options matter |
| Pizza | 39 | Expected but not dominant |
| Pho | 28 | Vietnamese is specifically requested |
| Pasta | 28 | Italian basics expected |
| Vegetarian | 22 | Veggie options are a gap |
| Lasagne | 13 | Specific comfort food request |

---

## 3. Top Recommendations

Based on the actual data analysis:

| Priority | Action | Evidence |
|----------|--------|----------|
| 1 | **Expand Vietnamese coverage** | Pho = top performer, 20.7% repeat rate, 4.57 rating |
| 2 | **Recruit Indian partners in gaps** | Highest repeat rate (23.1%), Dishoom has highest rating (4.79) |
| 3 | **Ensure Japanese/Asian rice bowls** | Rice Bowl = highest composite score (3.99), 95% kids happy |
| 4 | **Add grilled chicken partners** | 131 mentions, validated gap in survey data |
| 5 | **Focus on repeat rate, not volume** | Cuisine count is strongest predictor of repeat (r=0.514) |

### What NOT to Prioritize

| Category | Evidence | Recommendation |
|----------|----------|----------------|
| Burgers | 17.9% repeat rate (below threshold), ranks #83/86 | Do not recruit |
| Sushi | Only 8.5% repeat rate, 65% kids happy (low) | Deprioritize |
| Tacos | 4.7% repeat rate (very low), 3.75 rating | Do not recruit |

---

## 4. Appendix

### 4.1 Data Sources

| Source | Sample Size | Use |
|--------|-------------|-----|
| Snowflake Orders | 80,724 | Order volume, repeat rate, ratings |
| Snowflake Customers | 50,744 | Customer-level metrics |
| Post-Order Survey | 1,564 | Family factors, satisfaction |
| Dropoff Survey | 1,200+ | Unmet demand signals |
| Menu Catalog | 63,990 | Dish availability |

### 4.2 Cuisine Performance Summary

Full cuisine ranking by repeat rate:

| Cuisine | Repeat Rate | Orders | Rating |
|---------|-------------|--------|--------|
| Breakfast | 25.8% | 136 | 4.73 |
| Pho | 23.7% | 793 | 4.72 |
| **Indian** | **23.1%** | 8,356 | 4.66 |
| Curry | 21.0% | 3,355 | 4.75 |
| **Vietnamese** | **20.7%** | 12,961 | 4.57 |
| Mexican | 20.6% | 43 | 4.22 |
| **Asian** | 20.3% | 8,942 | 4.43 |
| Vegan Friendly | 20.0% | 2,053 | 4.43 |
| Salads | 19.7% | 5,330 | 4.58 |
| Shawarma | 19.7% | 84 | 3.86 |
| Mediterranean | 19.5% | 511 | 4.64 |
| Gluten Free | 18.9% | 140 | 4.84 |
| Meal Deals | 18.2% | 1,200 | 4.52 |
| Burgers | 17.9% | 2,485 | 4.49 |
| Chicken | 16.9% | 1,077 | 4.43 |
| Italian | 16.5% | 9,063 | 4.15 |
| Japanese | 16.2% | 14,618 | 4.24 |
| Thai | 15.8% | 5,098 | 4.33 |

### 4.3 10-Factor Scoring Methodology

See `DOCUMENTATION/METHODOLOGY/01_DISH_SCORING.md` for full methodology.

### 4.4 Configuration Files

- `config/mvp_thresholds.json` - Zone MVP criteria (validated thresholds)
- `config/factor_weights.json` - 10-factor weights
- `config/evidence_standards.json` - Sample size requirements

### 4.5 Related Dashboards

- [Zone MVP Dashboard](../../docs/dashboards/zone_mvp.html)
- [Priority Dishes Dashboard](../../docs/dashboards/priority_dishes.html)
- [Unified Dashboard](../../docs/dashboards/dinneroo_unified.html)

---

*Report generated January 2026. Data refreshed from Snowflake 2026-01-05.*
