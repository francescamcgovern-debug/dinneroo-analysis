# Unified Dish Scoring Framework v3.1

## Overview

This framework scores dishes using a **two-track approach** that works for both existing Dinneroo dishes (with data) and potential new dishes (without data). 

**Key Innovation:** Simplified to 5 core factors with **Performance weighted higher (60%)** because we have more reliable behavioral data from the trial period.

---

## Framework Structure

```
UNIFIED DISH SCORE (1-5 scale)
│
├── PERFORMANCE TRACK (60%) ─────────────────────────────────
│   │   "How well does this dish perform?"
│   │   Source: Snowflake orders + Survey data
│   │
│   ├── Orders per Zone (20%)    - Volume normalized by availability
│   ├── Rating (20%)              - Customer satisfaction
│   └── Kids Happy (20%)          - Core Dinneroo target metric
│
└── OPPORTUNITY TRACK (40%) ─────────────────────────────────
    │   "How much potential does this dish have?"
    │   Source: Latent demand signals
    │
    ├── Latent Demand (20%)       - What families want but can't get
    └── Non-Dinneroo Demand (20%) - Items customers order elsewhere
```

### Changes from v2.0

| Aspect | v2.0 | v3.1 |
|--------|------|------|
| Factors | 10 | 5 |
| Track split | 50/50 | 60/40 |
| Kids Happy | 7.5% | 20% (elevated) |
| Latent demand | 25% | 20% |
| Fit factors | Adult appeal, balanced, fussy eater | Removed (captured in latent demand) |

---

## Two-Track Approach

### Why Two Tracks?

**Performance** shows what's working among available options, but creates **survivorship bias** - unavailable dishes score poorly not because families don't want them, but because they CAN'T order them.

**Opportunity** captures latent demand and fit factors, allowing us to score dishes that aren't currently on Dinneroo.

| Track | What It Measures | Data Source | Applies To |
|-------|-----------------|-------------|------------|
| **Performance** | Revealed preference - what families actually do | Snowflake + Surveys | Existing dishes with 50+ orders |
| **Opportunity** | Latent demand + fit potential | Open-text + LLM | ALL dishes (existing + potential) |

### Scoring Logic for Different Dish Types

| Dish Status | Performance Score | Opportunity Score | Final Score |
|-------------|------------------|-------------------|-------------|
| On Dinneroo (50+ orders) | Calculated from data | Calculated | Weighted average |
| On Dinneroo (<50 orders) | N/A | Calculated | Opportunity only |
| Not on Dinneroo | N/A | Calculated | Opportunity only |

---

## Performance Track Components (50%)

### 1. Normalized Sales (10%)

**What it measures:** Demand for dish, normalized for availability

**Source:** Snowflake orders

**Calculation:** Total orders / (zones available × days listed)

| Score | Criteria |
|-------|----------|
| 5 | Top 10% of normalized sales |
| 4 | Top 25% |
| 3 | Top 50% |
| 2 | Bottom 50% |
| 1 | Bottom 25% |

### 2. Zone Ranking Strength (10%)

**What it measures:** Consistency of demand across zones

**Source:** Snowflake orders

**Calculation:** % of zones where dish ranks in top 5

| Score | Criteria |
|-------|----------|
| 5 | Top 5 in 60%+ of zones |
| 4 | Top 5 in 40%+ of zones |
| 3 | Top 5 in 20%+ of zones |
| 2 | Top 5 in 10%+ of zones |
| 1 | Rarely in top 5 |

### 3. Deliveroo Rating (10%)

**What it measures:** Customer satisfaction signal

**Source:** Snowflake ratings

| Score | Criteria |
|-------|----------|
| 5 | 4.5+ stars |
| 4 | 4.3-4.49 stars |
| 3 | 4.0-4.29 stars |
| 2 | 3.5-3.99 stars |
| 1 | Below 3.5 stars |

### 4. Repeat Intent (5%)

**What it measures:** Forward-looking retention signal

**Source:** Post-order survey

**Question:** "I would like to order the same dish again"

| Score | Criteria |
|-------|----------|
| 5 | 80%+ would reorder |
| 4 | 70-79% |
| 3 | 60-69% |
| 2 | 50-59% |
| 1 | Below 50% |

### 5. Kids Full & Happy (7.5%)

**What it measures:** Critical family success factor

**Source:** Post-order survey

**Question:** "How did your child(ren) react to the meal?"

| Score | Criteria |
|-------|----------|
| 5 | 85%+ "full and happy" |
| 4 | 75-84% |
| 3 | 65-74% |
| 2 | 55-64% |
| 1 | Below 55% |

### 6. Liked/Loved It (7.5%)

**What it measures:** Adult satisfaction

**Source:** Post-order survey

**Question:** "How did you feel about the meal?"

| Score | Criteria |
|-------|----------|
| 5 | 90%+ "Loved it" or "Liked it" |
| 4 | 80-89% |
| 3 | 70-79% |
| 2 | 60-69% |
| 1 | Below 60% |

---

## Opportunity Track Components (50%)

### 1. Latent Demand Score (25%)

**What it measures:** Unmet demand for dish types

**Sources combined:**
- Open-text mentions (45%): Dropoff survey, post-order survey, ratings comments
- OG Survey wishlist (30%): % who want to eat this more
- Barrier signals (25%): Dropoff responses indicating unmet needs

**Methodology:** `scripts/phase2_analysis/extract_latent_demand.py`

| Score | Criteria |
|-------|----------|
| 5 | 20+ combined mentions OR 15%+ wishlist |
| 4 | 10-19 mentions OR 10-14% wishlist |
| 3 | 5-9 mentions OR 5-9% wishlist |
| 2 | 2-4 mentions |
| 1 | 0-1 mentions |

### 2. Validated Fit Factors (25%)

These factors were **validated through correlation analysis** with success metrics. Only factors with impact score > 0.1 are included.

See: `DELIVERABLES/reports/factor_validation_analysis.md`

#### Adult Appeal (10.25%)

**Validation:**
- Impact score: 0.204 (highest of all factors)
- Pearson correlation: 0.196 with success metrics
- Spearman correlation: 0.213

**What it measures:** Adults genuinely enjoy this dish

| Score | Criteria |
|-------|----------|
| 5 | Restaurant-quality that adults actively want |
| 4 | Adults genuinely enjoy it, good flavors |
| 3 | Adults tolerate it, acceptable |
| 2 | More kid-focused, adults wouldn't choose |
| 1 | Adults wouldn't order for themselves |

#### Balanced/Guilt-Free (9.25%)

**Validation:**
- Impact score: 0.184
- Pearson correlation: 0.174
- Spearman correlation: 0.286 (strong rank correlation)

**What it measures:** Fits "balanced midweek meal" positioning

| Score | Criteria |
|-------|----------|
| 5 | Clearly balanced: protein + veg + carbs, grilled/healthy |
| 4 | Mostly balanced, some vegetables |
| 3 | Neutral - can go either way |
| 2 | Indulgent but some redeeming qualities |
| 1 | Pure treat/indulgence |

#### Fussy Eater Friendly (5.5%)

**Validation:**
- Impact score: 0.109 (just above threshold)
- Supported by 1,037 mentions in dropoff survey

**What it measures:** Picky eaters will accept this

| Score | Criteria |
|-------|----------|
| 5 | Mild by default, universally appealing |
| 4 | Mild option available, familiar ingredients |
| 3 | Can be made mild on request |
| 2 | Some unfamiliar ingredients |
| 1 | Spicy/complex by nature |

---

## Factors Excluded from Framework

The following factors were tested but **excluded due to weak correlation** with success metrics:

| Factor | Impact Score | Reason for Exclusion |
|--------|-------------|---------------------|
| Kid-Friendly | 0.080 | Below 0.1 threshold |
| Shareability | 0.055 | No meaningful correlation |
| Value at £25 | 0.046 | Negative correlation with rating |
| Vegetarian Option | 0.032 | No meaningful correlation |
| Portion Flexibility | N/A | Partner-level, not dish-type |
| Customisation | N/A | Partner-level, not dish-type |

---

## Hybrid Scoring Logic

For fit factors, we use a **hybrid approach**:

```
IF survey data exists for this dish type (n >= 5):
    → Use measured score from survey
    → Flag as "Measured"
ELSE:
    → Use LLM estimation based on dish characteristics
    → Flag as "Estimated"
```

### Evidence Levels

| Level | Criteria | Confidence |
|-------|----------|------------|
| **Validated** | Has performance data (50+ orders) AND survey data | High - strategic decisions |
| **Corroborated** | Has performance data OR survey data | Medium - directionally correct |
| **Estimated** | No performance or survey data | Low - exploration only |

---

## Composite Score Calculation

### For dishes WITH performance data:

```
Unified Score = Performance (50%) + Opportunity (50%)

Performance = (normalized_sales × 0.10) + (zone_ranking × 0.10) + 
              (rating × 0.10) + (repeat_intent × 0.05) + 
              (kids_happy × 0.075) + (liked_loved × 0.075)

Opportunity = (latent_demand × 0.25) + (adult_appeal × 0.1025) + 
              (balanced × 0.0925) + (fussy_eater × 0.055)
```

### For dishes WITHOUT performance data:

```
Unified Score = Opportunity Score (normalized to 1-5 scale)
```

---

## Tier Classification

| Tier | Score | Label | Action |
|------|-------|-------|--------|
| **Tier 1** | 4.0+ | Must-Have | Essential for every MVP zone |
| **Tier 2** | 3.0-3.49 | Should-Have | Strong contributor, high priority |
| **Tier 3** | 2.5-2.99 | Nice-to-Have | Add if resources allow |
| **Tier 4** | <2.5 | Monitor | Watch for changes, don't prioritize |

---

## 2x2 Quadrant Analysis (Anna's Official Names)

### For Dishes ON Dinneroo (with performance data)

Plot dishes on **Performance vs Opportunity** axes:

```
                    HIGH OPPORTUNITY (≥3.0)
                          │
    PREFERENCE DRIVERS    │      CORE DRIVERS
    (High want, low       │    (Proven winner)
     volume - build it)   │    
                          │    ACTION: Protect & expand
    ACTION: Build volume  │
                          │
                          │
    ──────────────────────┼──────────────────────
                          │
      DEPRIORITISED       │    DEMAND BOOSTERS
    (Low want, low        │    (Volume exists but 
     volume)              │     limited demand)
                          │    
    ACTION: Don't invest  │    ACTION: Improve demand
                          │    signals
                          │
                    LOW OPPORTUNITY (<3.0)
```

### For Dishes NOT on Dinneroo (no performance data)

Since these dishes have no performance data, we use **opportunity score only**:

| Quadrant | Opportunity | What To Do |
|----------|-------------|------------|
| **Preference Drivers** | High (≥3.0) | Expansion opportunity - recruit partners for these dishes |
| **Deprioritised** | Low (<3.0) | Low priority for expansion |

### Quadrant Actions Summary (v3.1)

| Quadrant | Performance | Opportunity | What To Do |
|----------|-------------|-------------|------------|
| **Core Drivers** | High (≥3.0) | High (≥3.0) | Protect and expand - these are your winners |
| **Demand Boosters** | High (≥3.0) | Low (<3.0) | Volume exists, improve demand signals |
| **Preference Drivers** | Low (<3.0) | High (≥3.0) | High customer want, build volume |
| **Deprioritised** | Low (<3.0) | Low (<3.0) | Don't invest resources here |

---

## Implementation

### Config File
`config/scoring_framework_v3.json`

### Scoring Script
`scripts/phase2_analysis/regenerate_dish_scores_v3_1.py`

### Outputs
- `DATA/3_ANALYSIS/priority_100_unified.csv` - Master list
- `DATA/3_ANALYSIS/dish_2x2_unified.csv` - Quadrant assignments
- `docs/data/priority_100_unified.json` - Dashboard data (auto-generated)
- `docs/dish_data.js` - Dashboard embedded data (auto-synced)

### Auto-Sync
The regenerate script automatically syncs to the dashboard:
```bash
python3 scripts/phase2_analysis/regenerate_dish_scores_v3_1.py
# Outputs CSV + JSON, then auto-runs sync_dish_data.py
```

---

## Changelog

### v3.1 (2026-01-08)
- **Simplified to 5 factors:** From 10 factors to 5 core metrics
- **Rebalanced to 60/40 split:** Performance weighted higher due to reliable trial data
- **Anna's quadrant names:** Core Drivers, Demand Boosters, Preference Drivers, Deprioritised
- **Auto-sync to dashboard:** Script generates JSON and syncs to dish_data.js
- **Updated tier thresholds:** 3.5/3.0/2.5 instead of 4.0/3.5/3.0

### v2.1 (2026-01-07)
- **Expanded dish list:** 48 → 100 dish types
- **Added non-Dinneroo dishes:** 69 dishes not currently on platform (expansion opportunities)
- **Renamed quadrants:** Action-oriented names (Priority, Protect, Develop, Monitor)
- **Added master config:** `config/dish_types_master.json` with all 100 dishes

### v2.0 (2026-01-07)
- **Factor validation:** Added correlation analysis to validate which factors impact success
- **Removed factors:** Kid-friendly, shareability, value, vegetarian (weak correlation)
- **Removed factors:** Portion flexibility, customisation (partner-level, not dish-type)
- **Added:** Comprehensive latent demand scoring from all sources
- **Added:** Hybrid scoring logic (survey data + LLM fallback)
- **Added:** Evidence level flagging

### v1.0 (2026-01-06)
- Initial unified framework merging Anna's Hit List with Family Fit Framework

---

*Configuration: `config/dish_scoring_unified.json`*
*Validation Report: `DELIVERABLES/reports/factor_validation_analysis.md`*
