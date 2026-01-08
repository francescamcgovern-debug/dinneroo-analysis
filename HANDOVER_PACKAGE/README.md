# Dinneroo Analysis Handover Package

**Created:** January 2026  
**Purpose:** Self-contained data package for colleague to analyze and write up findings

---

## What's in This Package

All CSVs are Google Sheets compatible. Open in Sheets to analyze.

### 01_THRESHOLD_EVIDENCE/
**Why we picked these MVP thresholds**

| File | What It Shows |
|------|---------------|
| `partner_count_metrics.csv` | Behavioral + survey metrics by partner count (1-2, 3-4, 5-6, 7-9, 10+) |
| `cuisine_count_metrics.csv` | Behavioral + survey metrics by cuisine count (1-2, 3-4, 5-6, 7+) |
| `dishes_per_partner_metrics.csv` | Behavioral + survey metrics by dishes per partner |
| `inflection_summary.csv` | **THE KEY FILE** - Shows where metrics improve (the "why" for thresholds) |
| `threshold_to_business_target.csv` | Data inflection points vs business targets with rationale |

**Key insight:** Data shows inflection at 3-4 partners/cuisines; business targets are 5 for redundancy.

---

### 02_ZONE_STATUS/
**Which zones meet MVP criteria**

| File | What It Shows |
|------|---------------|
| `zone_mvp_status.csv` | MVP status for all 100 live zones with orders |
| `zone_threshold_breakdown.csv` | Pass/fail on each criterion per zone |
| `zone_supply_detail.csv` | Full supply breakdown for 434 zones with partners |

**MVP Tier Summary:**
- MVP Ready (5+ cuisines): 42 zones
- Near MVP (4 cuisines): 19 zones
- Progressing (3 cuisines): 33 zones
- Developing (1-2 cuisines): 6 zones

---

### 03_ZONE_AVAILABILITY/
**What's available where (Anna's ground truth)**

| File | What It Shows |
|------|---------------|
| `zone_cuisine_availability.csv` | Core 7 cuisine dish counts by zone (1,306 zones) |
| `zone_partner_list.csv` | 40 partners with site counts |
| `dish_types_by_partner.csv` | 142 family dishes with dish type and cuisine |

**This is Anna's curated data - the source of truth for supply.**

---

### 04_SCORING_FRAMEWORK/
**NEW: Three-List Scoring Approach (v3.3)**

| File | What It Shows |
|------|---------------|
| `DISH_RANKINGS_WITH_ROLLUP.csv` | **MASTER FILE** - All 24 dish types with Family + Couple rankings and item rollup |
| `DISH_FAMILY_RANKINGS.csv` | Family Performers list - optimized for families with children |
| `DISH_COUPLE_RANKINGS.csv` | Couple Performers list - optimized for adults without children |
| `DISH_RECRUITMENT_PRIORITIES.csv` | Recruitment list - dishes NOT on Dinneroo with highest potential |
| `dish_taxonomy.csv` | Full 155-item reference showing how items roll up to 24 dish types |
| `weight_configuration.csv` | Current weights with rationale for each list |
| `INSTRUCTIONS_adjust_weights.md` | **READ THIS** - How to adjust weights in Sheets |

**Framework v3.3 Key Changes:**
1. **Aligned to Anna's 24 dish taxonomy** - now matches ground truth exactly
2. **Three separate rankings** - Family, Couple, and Recruitment priorities
3. **Full rollup visibility** - see which menu items make up each dish type

**Family Performers Weights (40/20/20/15/5):**
- Kids happy: 40%
- Fussy eater friendly: 20%
- Orders per zone: 20%
- Adult satisfaction: 15%
- Portions adequate: 5%

**Couple Performers Weights (40/25/20/15):**
- Adult satisfaction: 40%
- Rating: 25%
- Orders per zone: 20%
- Adult appeal: 15%

---

### 05_EVIDENCE_BACKUP/
**Supporting evidence for methodology**

| File | What It Shows |
|------|---------------|
| `factor_correlations.csv` | Why factors were included/excluded (correlation analysis) |
| `latent_demand_scores.csv` | Open-text demand signals |

---

## How to Use This Package

### For Dish Rankings
1. Open `04_SCORING_FRAMEWORK/DISH_RANKINGS_WITH_ROLLUP.csv`
2. **Family view:** Sort by `family_rank` to see best dishes for families
3. **Couple view:** Sort by `couple_rank` to see best dishes for couples/adults
4. See `items_sample` column for which menu items make up each dish type

### For Writing Up Threshold Rationale
1. Open `01_THRESHOLD_EVIDENCE/inflection_summary.csv`
2. This shows WHERE metrics improve (e.g., "+4.5pp repeat rate at 3-4 partners")
3. Use `threshold_to_business_target.csv` for the business rationale

### For Zone Analysis
1. Open `02_ZONE_STATUS/zone_mvp_status.csv`
2. Filter by `mvp_tier` to see which zones are MVP Ready vs developing
3. Use `zone_threshold_breakdown.csv` to see what's missing in each zone

### For Scoring Calibration Meeting
1. Open `04_SCORING_FRAMEWORK/DISH_RANKINGS_WITH_ROLLUP.csv`
2. Read `INSTRUCTIONS_adjust_weights.md` for how to change weights
3. Duplicate the sheet, adjust weights, recalculate to see impact

### For Supply Strategy
1. Open `03_ZONE_AVAILABILITY/zone_cuisine_availability.csv`
2. Filter zones missing key cuisines
3. Cross-reference with `04_SCORING_FRAMEWORK/DISH_RECRUITMENT_PRIORITIES.csv` to see what to recruit

---

## Key Numbers

| Metric | Value | Source |
|--------|-------|--------|
| Total menu items | 155 | Anna's ground truth |
| High-level dish types | 24 | Anna's taxonomy |
| Granular dish types | 58 | Anna's taxonomy |
| Total partners | 41 | Anna's ground truth |
| Zones with supply | 434 | Anna's ground truth |
| Zones with orders | 201 | Snowflake |
| MVP Ready zones | 42 | Threshold analysis |
| Core 7 cuisines | 7 | Framework |

---

## Critical Rules

1. **Supply data** → Use Anna's files (03_ZONE_AVAILABILITY)
2. **Performance data** → Use Snowflake-derived files (02_ZONE_STATUS)
3. **Dish types** → Always use Anna's 24 high-level types for on-Dinneroo analysis
4. **Never use OG Survey alone** for dish recommendations
5. **Non-Dinneroo benchmarks** MUST be filtered to Mon-Thu 16:30-21:00
6. **Zone counts:** Always specify which (1,306 total vs 434 supply vs 201 live)

---

## Questions?

See `HANDOVER_FOR_COLLEAGUE.md` in the project root for full methodology, definitions, and rationale.

---

*The analysis is complete. This package contains everything needed to write it up.*
