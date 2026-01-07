# Column Definitions & Data Sources

**Document:** Master Dish List Column Reference  
**Last Updated:** January 2026  
**Framework Version:** 5.0

---

## Quick Reference

| Column | Source | Description |
|--------|--------|-------------|
| rank | Calculated | Priority order (1 = highest) |
| dish_type | Item Categorisation | Dish category name |
| cuisine | Dec-25 Gsheet | Cuisine classification |
| on_dinneroo | Item Categorisation | TRUE = on platform, FALSE = prospect |
| strategic_priority | Dec-25 Gsheet | Action classification |
| avg_sales_per_dish | Dec-25 Gsheet | Average orders per dish (normalised) |
| pct_zones_top_5 | Dec-25 Gsheet | % zones where dish ranks top 5 |
| deliveroo_rating | Dec-25 Gsheet | Star rating (1-5) |
| meal_satisfaction | Post-order survey | % liked/loved meal |
| repeat_intent | Post-order survey | % would order again |
| dish_suitability | OG Survey analysis | Composite score (1-5) |
| open_text_requests | All surveys | Count of REQUEST mentions (filtered) |
| wishlist_pct | OG Survey | % who want but don't currently eat |
| demand_strength | Dec-25 Gsheet | Composite demand score |
| consumer_preference | Dec-25 Gsheet | Composite preference score |
| coverage_gap | Dec-25 Gsheet | % zones where NOT present |

---

## Identification Columns

### rank
- **Source:** Calculated
- **Description:** Priority order for action (1 = highest priority)
- **Calculation:** On Dinneroo dishes ranked by demand_strength; Prospects ranked by dish_suitability

### dish_type
- **Source:** Item Categorisation file
- **Description:** Dish category name, aligned with Dish Analysis Dec-25

### cuisine
- **Source:** Dec-25 Gsheet
- **Description:** Primary cuisine classification (Italian, Asian, Indian, etc.)

### on_dinneroo
- **Source:** Item Categorisation file (ground truth)
- **Description:** TRUE = currently on platform, FALSE = prospect for recruitment
- **Validation:** Cross-referenced against 155 actual menu items from 40 partners

### strategic_priority
- **Source:** Dec-25 Gsheet
- **Values:**
  - **Core Driver** - High demand + high preference, expand aggressively
  - **Preference Driver** - Lower demand but high preference, maintain quality
  - **Demand Booster** - High demand but lower preference, fix quality issues
  - **Deprioritised** - Low demand + low preference, don't invest
  - **Prospect** - Not on Dinneroo, evaluate for recruitment

---

## Performance Columns

*These metrics show how well dishes perform WHERE THEY EXIST on Dinneroo.*

### avg_sales_per_dish
- **Source:** Dec-25 Gsheet
- **Description:** Average orders per dish, normalised for supply differences
- **Why it matters:** Shows actual demand, not just availability

### pct_zones_top_5
- **Source:** Dec-25 Gsheet
- **Description:** % of zones where this dish ranks in the top 5 by sales
- **Why it matters:** A dish can have high total sales but low top-5 ranking (widely available but not dominant)

### deliveroo_rating
- **Source:** Dec-25 Gsheet
- **Description:** Average star rating (1-5) from Deliveroo customer reviews

### meal_satisfaction
- **Source:** Post-order survey (n=1,363)
- **Description:** % of customers who "liked" or "loved" the meal
- **Why it matters:** Direct measure of customer happiness

### repeat_intent
- **Source:** Post-order survey (n=1,363)
- **Description:** % of customers who would order again
- **Why it matters:** Predicts future demand

---

## Opportunity Columns

*These metrics show DEMAND SIGNALS - is there unmet demand for this dish?*

### dish_suitability
- **Source:** OG Survey analysis (n=404)
- **Description:** Composite score (1-5) representing "How much value can Dinneroo add by offering this dish?"

**Composite formula:**

| Factor | Weight | What it measures |
|--------|--------|------------------|
| Familiar | 30% | % who already eat or want to eat it |
| Time Consuming | 25% | Dishes that take longer to prep = more value from delivery |
| Healthy Enough | 20% | No nutrition "danger signals" |
| Shareable | 12.5% | Can come in one big portion |
| Customisable | 12.5% | Individual portions can be made to preferences |

**Examples:**
- Shepherd's Pie: 4.4 (high familiarity, 75% scratch cook, 34 min prep)
- Casserole/Stew: 4.3 (89% scratch cook, 39 min prep)
- Pizza: 2.0 (only 18% scratch cook, quick to make)

**IMPORTANT:** If blank, dish was not in OG Survey. These dishes are NOT penalised - they are scored on available data only.

### open_text_requests
- **Source:** All surveys (Dropoff n=132 + Post-order n=1,363 + Ratings n=1,061)
- **Description:** Count of REQUEST mentions only

**Filtering:** Only counts text containing request patterns:
- "wish you had..."
- "would love to see..."
- "would like to see..."
- "please add..."
- "why don't you have..."
- etc.

**NOT counted:** Complaints ("the curry was cold") or neutral mentions ("the lasagne was ok")

### wishlist_pct
- **Source:** OG Survey (n=404)
- **Description:** % of respondents who want this dish but don't currently eat it
- **Why it matters:** Direct measure of unmet demand

---

## Context Columns

*These are informational only - NOT used in scoring.*

### demand_strength
- **Source:** Dec-25 Gsheet
- **Description:** Composite demand score combining avg_sales, % rank #1, % top 5
- **Scale:** 1.0 = average

### consumer_preference
- **Source:** Dec-25 Gsheet
- **Description:** Composite preference score combining rating, satisfaction, repeat intent
- **Scale:** 1.0 = average

### coverage_gap
- **Source:** Dec-25 Gsheet
- **Description:** % of zones where this dish is NOT present
- **Note:** This is context only - high coverage gap does NOT mean high opportunity (availability ≠ demand)

---

## Data Sources

| Abbreviation | Full Name | Sample Size |
|--------------|-----------|-------------|
| Dec-25 Gsheet | Dish Analysis Dec-25 - Dish Scoring.csv | 23 dishes |
| Item Categorisation | Dish Analysis Dec-25 - Item Categorisation.csv | 155 menu items |
| Post-order survey | Post-order satisfaction survey | n=1,363 responses |
| OG Survey | Original family behavior survey | n=404 respondents |
| Dropoff survey | Dropoff/churn survey | n=132 responses |
| Ratings | Deliveroo rating comments | n=1,061 comments |

---

## Dishes Summary

**Total: 32 dishes**
- On Dinneroo: 23 dishes
- Prospects: 9 dishes

### Dishes Missing dish_suitability (NOT penalised)

These dishes were not in the OG Survey:
- Biryani
- Sushi
- Grain Bowl
- Shawarma
- Poke
- Nachos

They are scored on available data only (open_text_requests, wishlist_pct, performance metrics).

---

## Family vs Non-Family Scoring Comparison

**Analysis File:** `DATA/3_ANALYSIS/family_vs_nonfamily_scores.csv`  
**Report:** `DELIVERABLES/reports/family_vs_nonfamily_comparison.md`  
**Script:** `scripts/phase2_analysis/08_nonfamily_scoring_comparison.py`

### Purpose

Shows how dish prioritization changes when family-specific factors are removed from the scoring framework. This helps validate whether family-focused curation matters for dish selection.

### Framework Variants

| Framework | Family Factors Included | Total Weight |
|-----------|------------------------|--------------|
| **Family** (current) | `kids_full_happy` (7.5%) + `fussy_eater_friendly` (5.5%) | 13% |
| **Non-Family** (variant) | Removed, redistributed proportionally | 0% |

### Weight Redistribution

When family factors are removed, their 13% weight is redistributed proportionally to remaining factors:

| Factor | Family Weight | Non-Family Weight | Change |
|--------|---------------|-------------------|--------|
| Normalized Sales | 10.0% | 11.5% | +1.5% |
| Zone Ranking | 10.0% | 11.5% | +1.5% |
| Deliveroo Rating | 10.0% | 11.5% | +1.5% |
| Repeat Intent | 5.0% | 5.7% | +0.7% |
| Kids Full Happy | 7.5% | **0%** | **Removed** |
| Liked/Loved | 7.5% | 8.6% | +1.1% |
| Latent Demand | 25.0% | 28.7% | +3.7% |
| Adult Appeal | 10.2% | 11.8% | +1.6% |
| Balanced/Guilt-Free | 9.2% | 10.6% | +1.4% |
| Fussy Eater Friendly | 5.5% | **0%** | **Removed** |

### Comparison Columns

| Column | Description |
|--------|-------------|
| family_score | Composite score under Family framework |
| nonfamily_score | Composite score under Non-Family framework |
| family_rank | Rank under Family framework (1 = highest) |
| nonfamily_rank | Rank under Non-Family framework |
| rank_change | Positions moved (+ = up in non-family, - = down) |
| mover_type | Classification: "Up (benefits from non-family)", "Down (benefits from family)", or "Stable" |

### Key Findings

**Stability at the top:** 10 of the top 10 dishes are the same under both frameworks. The core menu works for everyone.

**Dishes that benefit from family factors (drop without them):**
- Shepherd's Pie (-6 ranks)
- Fajitas (-6 ranks)
- Fried Rice (-5 ranks)
- Rice Bowl (-5 ranks)

**Dishes that benefit from non-family focus (rise without family factors):**
- Tagine (+7 ranks)
- Tacos (+5 ranks)
- Fish & Chips (+5 ranks)

### Interpretation

- **Top dishes are universal** - Indian Curry, Pho, Katsu, Noodles, Lasagne rank highly regardless of framework
- **Family factors matter for mid-tier** - Dishes ranked 15-25 show the most movement
- **Non-family opportunities exist** - If targeting couples/singles, Tagine and Tacos would be higher priority

---

*For methodology details, see MASTER_DISH_SCORING_REVIEW.md*
