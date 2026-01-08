# Deprecated Files - 2026-01-08

The following files have been deprecated as part of the v3.0 scoring framework update.

## Why Deprecated

The project moved from an 11-factor framework to a simplified 6-factor framework with:
- 60/40 Performance/Opportunity split (was 50/50)
- Orders per zone normalization (was raw volume)
- Action-oriented quadrant names (Core Drivers, etc.)
- Removed fit factors (adult_appeal, balanced_guilt_free) - were mostly estimated

## Config Files Deprecated

| File | Replacement | Reason |
|------|-------------|--------|
| `DEPRECATED_factor_weights.json` | `scoring_framework_v3.json` | Old 10-factor framework |
| `DEPRECATED_dish_scoring_unified_v2.json` | `scoring_framework_v3.json` | Old 11-factor framework |

## Scripts Deprecated

| File | Replacement | Reason |
|------|-------------|--------|
| `DEPRECATED_01_score_dishes_v2.py` | `01_score_dishes_v3.py` | Used old config |

## Data Files Archived

| File | Replacement | Reason |
|------|-------------|--------|
| `LEGACY_dish_2x2_matrix.csv` | `priority_100_unified.csv` | Different framework |
| `LEGACY_dish_scoring_anna_aligned.csv` | `priority_100_unified.csv` | Old scoring |
| `LEGACY_priority_dishes.json` | `priority_100_unified.json` | Incomplete data |

## Current Source of Truth

**Single source for dish rankings:** `DATA/3_ANALYSIS/priority_100_unified.csv`

**Single source for cuisine rankings:** `DATA/3_ANALYSIS/cuisine_scores_unified.csv`

**Config:** `config/scoring_framework_v3.json`

---

*Do not use deprecated files for any new analysis.*


