# Ground Truth Data: Anna's Spreadsheet

## Overview

As of January 2026, Anna's spreadsheet (`Dish Analysis Dec-25.xlsx`) serves as the **authoritative source** for supply data. This document explains what data comes from where and when to use each source.

---

## The Problem We Solved

Previously, we derived supply metrics (partner counts, dish availability) from **order history**. This significantly **understated** actual availability because:

1. A partner could be onboarded but have zero orders yet
2. A zone could have dishes available that haven't been ordered
3. Order data only shows what was purchased, not what's available

**Anna's spreadsheet** contains the actual ground truth of what's onboarded and available.

---

## Data Sources Hierarchy

### Supply Metrics (What We Have) → Use Anna's Data

| Metric | Source File | Description |
|--------|-------------|-------------|
| Family dishes | `DATA/3_ANALYSIS/anna_family_dishes.csv` | 142 curated family dishes |
| Partner coverage | `DATA/3_ANALYSIS/anna_partner_coverage.csv` | 40 partners, 756 sites |
| Zone dish counts | `DATA/3_ANALYSIS/anna_zone_dish_counts.csv` | 1,306 zones with dish/cuisine counts |

### Performance Metrics (How It Performs) → Use Snowflake Data

| Metric | Source File | Description |
|--------|-------------|-------------|
| Order volume | `DATA/2_ENRICHED/orders_enriched.csv` | Actual orders placed |
| Repeat rate | `DATA/2_ENRICHED/orders_enriched.csv` | Customer retention |
| Ratings | `DATA/2_ENRICHED/ratings_enriched.csv` | Customer satisfaction |

### Preference Metrics (What Customers Want) → Use Surveys (with triangulation)

| Metric | Source | Description |
|--------|--------|-------------|
| Dish preferences | OG Survey | What families say they want |
| Latent demand | Open-text responses | Unmet needs mentioned |
| Kids feedback | Post-order survey | Child satisfaction |

---

## Anna's Source Files

Located in `DATA/1_SOURCE/anna_slides/`:

| File | Contains | Used For |
|------|----------|----------|
| `Dish Analysis Dec-25 - Item Categorisation.csv` | 155 rows of family dishes | `anna_family_dishes.csv` |
| `Dish Analysis Dec-25 - Onboarded Sites.csv` | 763 restaurant sites | `anna_partner_coverage.csv` |
| `Dish Analysis Dec-25 - Zone X Dish Mapping.csv` | Zone-level dish availability | `anna_zone_dish_counts.csv` |
| `Dish Analysis Dec-25 - Px Coverage.csv` | Partner zone coverage % | Reference |
| `Dish Analysis Dec-25 - Summary by Zone.csv` | Order volume by zone | Behavioral metrics |

---

## Key Numbers (Ground Truth)

| Metric | Value | Source |
|--------|-------|--------|
| Total family dishes | 142 | anna_family_dishes.csv |
| Total partners | 40 | anna_partner_coverage.csv |
| Total sites | 756 | anna_partner_coverage.csv |
| Zones with dishes | 434 | anna_zone_dish_counts.csv |
| Total zones tracked | 1,306 | anna_zone_dish_counts.csv |

### Top Partners by Site Count
1. PizzaExpress: 166 sites
2. Wagamama: 103 sites
3. Itsu: 50 sites
4. Pho: 46 sites
5. Bill's: 40 sites

### Top Zones by Dish Count
1. Islington: 83 dishes
2. East Central: 80 dishes
3. West Central: 75 dishes
4. Mayfair: 75 dishes
5. Clapham: 74 dishes

---

## When to Use What

### "How many partners do we have?"
→ Use `anna_partner_coverage.csv` (40 partners)

### "How many dishes in Zone X?"
→ Use `anna_zone_dish_counts.csv`

### "Which dishes sell best?"
→ Use `priority_100_dishes.csv` (derived from Snowflake orders)

### "What cuisines are missing in Zone X?"
→ Use `anna_zone_dish_counts.csv` (has cuisine breakdown per zone)

### "Does Zone X meet MVP criteria?"
→ Use `anna_zone_dish_counts.csv` with thresholds:
- 5+ partners
- 5+ cuisines

---

## Config Files

These config files document the data hierarchy:

- `config/analysis_registry.json` - Lists all analyses with their sources
- `config/data_source_map.json` - Maps questions to data sources
- `config/brief_intake.json` - Maps brief types to required data

---

## Reconciliation Summary

| Metric | Order-Derived | Anna's Ground Truth | Difference |
|--------|---------------|---------------------|------------|
| Partners | ~25-30 | 40 | +33% |
| Sites | ~400 | 756 | +89% |
| Zones with dishes | ~200 | 434 | +117% |

**Key insight**: Order data significantly understates availability. Always use Anna's data for "what we have" questions.

---

## Zone Count Discrepancy (Important!)

See `09_DATA_RECONCILIATION.md` for full details.

**Summary:**
- Anna's data shows **435 zones** with Dinneroo partners configured
- Snowflake orders show only **201 zones** with actual orders
- **Gap of 234 zones** = expansion opportunity (partners onboarded, awaiting customer activation)

**Why?** The Dinneroo trial period (Sep-Dec 2025) was limited to specific zones. The remaining 234 zones have partners ready but weren't activated for customers during the trial.

**For MVP threshold analysis:** Use Snowflake data (201 zones) - this is behavioral data from real orders.
**For expansion planning:** Use Anna's data (435 zones) - this shows where we can activate.

---

*Last updated: 2026-01-07*


