# Data Consistency Validation Report

**Generated:** 2026-01-08  
**Status:** ⚠️ REQUIRES ATTENTION  
**Purpose:** Ensure all analysis files use consistent frameworks for dashboard

---

## Executive Summary

After auditing the 96 analysis files, I identified a **dual-taxonomy architecture** that is intentional but needs clear usage rules:

| Taxonomy | Purpose | Column Name | File Count |
|----------|---------|-------------|------------|
| **Anna's 24-Dish** | What's ON Dinneroo | `high_level_dish` | 6 files |
| **Master 110-Dish** | What COULD be on Dinneroo | `dish_type` | 36+ files |

**This is not a conflict** - it's complementary. Anna's taxonomy covers existing supply; Master taxonomy includes recruitment/discovery dishes.

---

## 🚨 CRITICAL: Taxonomy Usage Rules

### Anna's 24-Dish Taxonomy (Supply Analysis)

**When to use:** Analyzing what we HAVE on Dinneroo today

**Authoritative Files:**
```
DATA/3_ANALYSIS/dish_family_performers.csv     ← Family segment rankings
DATA/3_ANALYSIS/dish_couple_performers.csv     ← Couple segment rankings
DATA/3_ANALYSIS/dish_type_rollup.csv           ← 155 items → 58 granular → 24 high-level
DATA/3_ANALYSIS/anna_family_dishes.csv         ← Source data
DELIVERABLES/reports/DISH_FAMILY_RANKINGS.csv  ← Final deliverable
DELIVERABLES/reports/DISH_COUPLE_RANKINGS.csv  ← Final deliverable
```

**Column:** `high_level_dish`

**Types (24):**
- Biryani, Burrito/Burrito Bowl, Chilli, East Asian Curry, Fajitas
- Fried Rice, Grain Bowl, Katsu, Lasagne, Nachos
- Noodles, Other, Pasta, Pho, Pizza, Poke
- Protein & Veg, Quesadilla, Rice Bowl, Shawarma, Shepherd's Pie
- South Asian/Indian Curry, Sushi, Tacos

### Master 110-Dish Taxonomy (Demand/Discovery Analysis)

**When to use:** Analyzing what we SHOULD have (including recruitment targets)

**Authoritative Files:**
```
config/dish_types_master.json                  ← Full taxonomy definition
DATA/3_ANALYSIS/dish_2x2_unified.csv           ← Quadrant classification
DATA/3_ANALYSIS/latent_demand_scores.csv       ← Open-text demand signals
DATA/3_ANALYSIS/smart_discovery_dishes.csv     ← New dish recommendations
DATA/3_ANALYSIS/priority_100_unified.csv       ← All dishes ranked
DELIVERABLES/reports/DISH_RECRUITMENT_PRIORITIES.csv ← Recruitment deliverable
```

**Column:** `dish_type`

**Types:** 110 dishes across all cuisines (existing + potential)

---

## 🔴 Version Inconsistencies (Minor)

| File | Version | Track Name | Issue |
|------|---------|------------|-------|
| `scoring_framework_v3.json` | 3.3 | Demand | ✅ Canonical |
| `MASTER_DISH_LIST_UNIFIED_v3.csv` | 3.2 | Demand | Minor lag |
| `priority_100_unified.json` | 3.1 | Opportunity | ⚠️ Uses old track name |

**Resolution:** `priority_100_unified.json` uses `opportunity_score` but this maps to `demand_score` in v3.3.

---

## 🟡 Files to IGNORE (Legacy)

These files should NOT be used in dashboard:

```
DATA/3_ANALYSIS/LEGACY_dish_2x2_matrix.csv
DATA/3_ANALYSIS/LEGACY_dish_scoring_anna_aligned.csv
DATA/3_ANALYSIS/archive/*  (6 archived files)
```

---

## ✅ Mapping Between Taxonomies

| Anna's 24-Dish | Master 110-Dish | Notes |
|----------------|-----------------|-------|
| South Asian / Indian Curry | Curry, Butter Chicken, Tikka Masala, Korma, Daal | Anna = grouped |
| Noodles | Noodles, Pad Thai, Chow Mein, Udon, Ramen | Anna = grouped |
| Rice Bowl | Rice Bowl, Teriyaki, Bibimbap | Anna = grouped |
| East Asian Curry | Thai Curry, Massaman, Yellow Curry | Anna = grouped |
| Pasta | Pasta, Lasagne, Mac & Cheese, Gnocchi | Anna = grouped |

**Key insight:** When displaying rankings:
- **Family/Couple Rankings → Use Anna's 24** (what we actually sell)
- **Recruitment Priorities → Use Master 110** (what we could add)
- **2x2 Quadrant → Use Master 110** (strategic view of all dishes)

---

## Dashboard Data Source Matrix

| Dashboard Section | Source File | Taxonomy |
|-------------------|-------------|----------|
| **Family Top Dishes** | `dish_family_performers.csv` | Anna 24 |
| **Couple Top Dishes** | `dish_couple_performers.csv` | Anna 24 |
| **Dish Quadrant (2x2)** | `dish_2x2_unified.csv` | Master 110 |
| **Smart Discovery** | `smart_discovery_dishes.csv` | Master 110 |
| **Latent Demand** | `latent_demand_scores.csv` | Master 110 |
| **Recruitment Priorities** | `dish_recruitment_priorities.csv` | Master 110 |
| **Zone MVP Status** | `zone_mvp_status.json` | N/A (zone-level) |
| **Cuisine Gaps** | `cuisine_gap_summary.json` | Core 7 cuisines |

---

## Scoring Framework Consistency Check

### Factor Weights (Family Performers) - VERIFIED CONSISTENT

| Factor | Weight | Source |
|--------|--------|--------|
| kids_happy | 40% | Post-order survey |
| fussy_eater_friendly | 20% | dish_opportunity_scores |
| orders_per_zone | 20% | Snowflake orders |
| adult_satisfaction | 15% | Post-order survey |
| portions_adequate | 5% | Post-order survey |

**Files checked:**
- `config/scoring_framework_v3.json` ✅
- `DELIVERABLES/reports/DISH_FAMILY_RANKINGS.csv` ✅
- `DATA/3_ANALYSIS/dish_family_performers.csv` ✅

### Factor Weights (Couple Performers) - VERIFIED CONSISTENT

| Factor | Weight | Source |
|--------|--------|--------|
| adult_satisfaction | 40% | Post-order survey |
| rating | 25% | Snowflake ratings |
| orders_per_zone | 20% | Snowflake orders |
| adult_appeal | 15% | dish_opportunity_scores |

---

## Action Items for Dashboard

### 1. Do NOT mix taxonomies in the same view
- Family/Couple rankings: Anna's 24 only
- Discovery/Recruitment: Master 110 only

### 2. Add "taxonomy" field to unified JSON
When building `unified_zones.json`, include:
```json
{
  "zone_id": "brighton-central",
  "dishes_available": [/* Anna 24 taxonomy */],
  "dishes_recommended": [/* Master 110 taxonomy */]
}
```

### 3. Display labels should match taxonomy
- "Rice Bowl" (Anna) ≠ "Teriyaki" (Master)
- Show at appropriate aggregation level

### 4. Evidence drill-down can show both
- "Rice Bowl performs well (Family #1)"
- "Includes: Teriyaki Rice Bowl, Thai Rice Bowl..." (granular)

---

## Summary: No Conflicts, Just Different Lenses

| Question | Use This | Taxonomy |
|----------|----------|----------|
| What dishes work for families? | `dish_family_performers.csv` | Anna 24 |
| What dishes work for couples? | `dish_couple_performers.csv` | Anna 24 |
| What dishes should we add? | `smart_discovery_dishes.csv` | Master 110 |
| What's high demand but low supply? | `dish_2x2_unified.csv` | Master 110 |
| What are customers asking for? | `latent_demand_scores.csv` | Master 110 |

**The dual-taxonomy is intentional and correct.** Just ensure dashboard displays use the right taxonomy for the question being answered.

---

## Zone Data Consistency Check

### Zone Identifiers - VERIFIED CONSISTENT

| File | Zone Count | ID Format | Notes |
|------|------------|-----------|-------|
| `zone_mvp_status.json` | 201 | zone name + zone_code | ✅ Canonical |
| `zone_gap_report.csv` | 1,307 | zone name + zone_code | Includes all zones (supply) |
| `zone_stats.csv` | 201 | zone name | Live zones only |

### Cuisine Naming - ⚠️ MINOR INCONSISTENCY

| Source | Cuisine Names | Issue |
|--------|---------------|-------|
| `mvp_thresholds.json` | Asian, Italian, Indian, Healthy, Mexican, Middle Eastern, British | ✅ Canonical |
| `zone_mvp_status.json` | asian, italian, indian, healthy, mexican, middle_eastern, british | ✅ Matches (lowercase) |
| `zone_gap_report.csv` | Japanese/Asian, Healthy/Fresh, Thai/Southeast Asian | ⚠️ Different format |

**Resolution:** When displaying, normalize to Core 7 canonical names:
- "Japanese/Asian" → "Asian"
- "Healthy/Fresh" → "Healthy"
- "Thai/Southeast Asian" → "Asian" (subset)

### MVP Status Tiers - VERIFIED CONSISTENT

| Status | Definition | Count |
|--------|------------|-------|
| MVP Ready | ≥5 Core 7 cuisines | 23 zones |
| Near MVP | 4 cuisines | 45 zones |
| Progressing | 3 cuisines | 71 zones |
| Developing | 1-2 cuisines | 62 zones |

Source: `zone_mvp_status.json` and `mvp_thresholds.json` are aligned.

---

## Final Validation Summary

| Check | Status | Action Required |
|-------|--------|-----------------|
| **Dish Taxonomy** | ⚠️ Dual system | Use correct taxonomy per context |
| **Scoring Framework** | ✅ Consistent | v3.3 is canonical |
| **Zone MVP Status** | ✅ Consistent | Use zone_mvp_status.json |
| **Cuisine Names** | ⚠️ Minor variation | Normalize in display |
| **Legacy Files** | ✅ Identified | Exclude from dashboard |
| **Factor Weights** | ✅ Consistent | All match framework |

**Dashboard can proceed with confidence** - inconsistencies are documented and resolvable at display time.

