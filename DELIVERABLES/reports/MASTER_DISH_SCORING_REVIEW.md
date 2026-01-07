# Master Dish Scoring Framework - Review Document

**Generated:** 2026-01-07  
**Version:** 5.0  
**Status:** Ready for Review

---

## Executive Summary

### What This Framework Does

Scores dish types to help Account Managers identify:
- Which dishes to prioritize for zone expansion
- Which dishes represent untapped opportunities
- Which dishes are performing well but have limited growth potential

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Two-track scoring (Performance + Opportunity)** | Avoids survivorship bias |
| **Request-filtered open-text** | Only counts actual requests, not complaints |
| **Item Categorisation as ground truth** | on_dinneroo validated against actual menu items |
| **Missing data NOT penalised** | Dishes without dish_suitability scored on available data |
| **Correct source attribution** | Each metric traced to actual source |

---

## Data Sources

| Source | Sample Size | Used For |
|--------|-------------|----------|
| Dec-25 Gsheet | 23 dishes | Performance metrics, strategic priority |
| Item Categorisation | 155 items | on_dinneroo ground truth |
| Post-order survey | n=1,363 | meal_satisfaction, repeat_intent |
| OG Survey | n=404 | dish_suitability, wishlist_pct |
| Dropoff survey | n=132 | open_text_requests |
| Ratings | n=1,061 | open_text_requests |

---

## Performance Metrics

*How well does the dish perform WHERE IT EXISTS?*

| Metric | Source | Description |
|--------|--------|-------------|
| avg_sales_per_dish | Dec-25 Gsheet | Average orders (normalised) |
| pct_zones_top_5 | Dec-25 Gsheet | % zones where dish ranks top 5 |
| deliveroo_rating | Dec-25 Gsheet | Star rating (1-5) |
| meal_satisfaction | Post-order survey | % liked/loved meal |
| repeat_intent | Post-order survey | % would order again |

---

## Opportunity Metrics

*Is there DEMAND for this dish?*

### dish_suitability

**Source:** OG Survey analysis (n=404)

**NOT a single question.** Composite score representing "How much value can Dinneroo add?"

| Factor | Weight | What it measures |
|--------|--------|------------------|
| Familiar | 30% | % who already eat or want to eat it |
| Time Consuming | 25% | Longer prep = more value from delivery |
| Healthy Enough | 20% | No nutrition "danger signals" |
| Shareable | 12.5% | Can come in one big portion |
| Customisable | 12.5% | Individual portions customisable |

**Examples:**
- Shepherd's Pie: 4.4 (high familiarity, 75% scratch cook)
- Casserole/Stew: 4.3 (89% scratch cook, 39 min prep)
- Pizza: 2.0 (only 18% scratch cook, quick to make)

### open_text_requests

**Source:** All surveys (Dropoff + Post-order + Ratings)

**FILTERED for requests only.** Patterns matched:
- "wish you had..."
- "would love to see..."
- "please add..."
- "why don't you have..."
- etc.

**NOT counted:**
- Complaints: "the curry was cold"
- Neutral: "the lasagne was ok"

**Result:** Post-order 25/1,837 responses contained request patterns. Ratings 15/1,061 comments contained request patterns.

### wishlist_pct

**Source:** OG Survey (n=404)

% who want this dish but don't currently eat it.

---

## Strategic Priority Classifications

From Dec-25 Gsheet:

| Classification | Meaning | Action |
|---------------|---------|--------|
| **Core Driver** | High demand + high preference | Expand aggressively |
| **Preference Driver** | Lower demand, high preference | Maintain quality |
| **Demand Booster** | High demand, lower preference | Fix quality issues |
| **Deprioritised** | Low demand + low preference | Don't invest |
| **Prospect** | Not on Dinneroo | Evaluate for recruitment |

---

## Dish List Summary

**Total: 32 dishes**
- On Dinneroo: 23 dishes
- Prospects: 9 dishes

### Top 10 Dishes (by demand_strength)

| Rank | Dish | Priority | Demand | Top 5 % | Requests | Wishlist |
|------|------|----------|--------|---------|----------|----------|
| 1 | Pho | Core Driver | 4.2 | 100% | 18 | - |
| 2 | Indian Curry | Core Driver | 2.9 | 64% | 15 | 5.9% |
| 3 | Biryani | Core Driver | 2.5 | 54% | 2 | - |
| 4 | Protein & Veg | Demand Booster | 1.6 | 44% | 5 | 7.9% |
| 5 | Sushi | Core Driver | 1.5 | 56% | 6 | - |
| 6 | Rice Bowl | Core Driver | 1.2 | 41% | 0 | 4.2% |
| 7 | Noodles | Core Driver | 1.2 | 37% | 15 | 12.9% |
| 8 | Katsu | Core Driver | 1.2 | 41% | 9 | 11.1% |
| 9 | Pizza | Demand Booster | 1.0 | 49% | 25 | 3.7% |
| 10 | Fried Rice | - | 1.0 | 17% | 2 | - |

### Top Prospects (by dish_suitability)

| Dish | Suitability | Requests | Wishlist | Notes |
|------|-------------|----------|----------|-------|
| Casserole / Stew | 4.3 | 1 | 12.3% | High suitability |
| Risotto | 3.6 | 0 | 15.1% | High wishlist |
| Roast | 3.5 | 1 | 4.7% | British staple |
| Tagine | 3.3 | 0 | 9.9% | Niche |
| Paella | 3.3 | 0 | 14.9% | High wishlist |
| Pastry Pie | 3.2 | 6 | 17.3% | Highest wishlist |

---

## Data Quality

### Dishes Missing dish_suitability

These 6 dishes were not in the OG Survey and have no dish_suitability score:
- Biryani
- Sushi
- Grain Bowl
- Shawarma
- Poke
- Nachos

**These dishes are NOT penalised.** They are scored on available data only.

### Removed Dishes (No Data Backing)

- Peking duck - No suitability, no requests, no wishlist
- Mezze - No suitability, no requests, no wishlist

---

## Files

| File | Description |
|------|-------------|
| MASTER_DISH_LIST_WITH_WORKINGS.csv | Full dish list with all metrics |
| COLUMN_DEFINITIONS.md | Column definitions and sources |
| latent_demand_scores.csv | Request-filtered open-text analysis |

---

*Document generated: 2026-01-07 | Version 5.0*
