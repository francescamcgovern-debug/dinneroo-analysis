# Data Sources Quick Reference

## Overview

This is a quick reference for data sources. For full inventory with bias warnings, see `05_DATA_SOURCES_INVENTORY.md`.

---

## Data Hierarchy

### Supply Metrics (What We Have) → Anna's Data

| Metric | File |
|--------|------|
| Family dishes | `DATA/3_ANALYSIS/anna_family_dishes.csv` |
| Partner coverage | `DATA/3_ANALYSIS/anna_partner_coverage.csv` |
| Zone dish counts | `DATA/3_ANALYSIS/anna_zone_dish_counts.csv` |

**Why:** Order data understates availability. Anna's spreadsheet is ground truth.

### Performance Metrics (How It Performs) → Snowflake

| Metric | File |
|--------|------|
| Orders | `DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv` |
| Ratings | `DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv` |
| Customers | `DATA/1_SOURCE/snowflake/ALL_DINNEROO_CUSTOMERS.csv` |

### Preference Metrics (What Customers Want) → Surveys

| Metric | File |
|--------|------|
| Satisfaction | `DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv` |
| Barriers | `DATA/1_SOURCE/surveys/dropoff_LATEST.csv` |
| Latent demand | Open-text fields across sources |

---

## Key Files by Agent

### DISH_AGENT
- `DATA/3_ANALYSIS/anna_family_dishes.csv` - Ground truth dishes
- `DATA/3_ANALYSIS/priority_100_unified.csv` - Rankings
- `DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv` - Order volume

### ZONE_AGENT
- `DATA/3_ANALYSIS/anna_zone_dish_counts.csv` - Zone supply
- `DATA/3_ANALYSIS/zone_mvp_status.csv` - MVP calculations
- `config/mvp_thresholds.json` - Criteria

### GAP_AGENT
- `DATA/3_ANALYSIS/cuisine_gap_analysis.csv` - Gap data
- `DATA/3_ANALYSIS/anna_partner_coverage.csv` - Partner availability

### LATENT_DEMAND_AGENT
- `DATA/1_SOURCE/surveys/dropoff_LATEST.csv` - Barriers
- `DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv` - Improvements
- `DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv` - Comments

---

## ⚠️ OG Survey Warning

**Location:** `DATA/1_SOURCE/historical_surveys/og_survey/`

The OG Survey was the source of bias in the old project. It captures stated preference (what people SAY) not revealed preference (what they DO).

**Rule:** OG Survey data must ALWAYS be triangulated with Snowflake behavioral data.

---

*For full inventory with sample sizes and bias warnings, see `05_DATA_SOURCES_INVENTORY.md`.*


