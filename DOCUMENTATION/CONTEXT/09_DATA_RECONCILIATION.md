# Data Reconciliation: Zone and Order Counts

## Summary

There are discrepancies between counts in different data sources. This document explains the differences and confirms our analysis is valid.

### Zone Counts

| Data Source | Zone Count | What It Represents |
|-------------|------------|-------------------|
| Anna's Zone X Dish Mapping | **434 zones** | Zones with partners **configured/onboarded** |
| Snowflake Orders | **201 zones** | Zones with **actual Dinneroo orders** during trial |
| Zones with sufficient data | **197 zones** | Zones meeting minimum sample size for analysis |
| Gap | **233 zones** | Partners onboarded but **no orders yet** |

### Order Counts

| Data Source | Order Count | What It Represents |
|-------------|-------------|-------------------|
| ALL_DINNEROO_ORDERS.csv (current) | **82,350 orders** | Total Dinneroo orders as of 2026-01-07 |
| Historical reference (2026-01-05) | 80,724 orders | Earlier Snowflake pull - **DEPRECATED** |

**Note:** Reports referencing 80,724 orders should be updated to 82,350.

---

## Root Cause

**The Dinneroo trial period ran from September to December 2025.**

- Anna's data shows all zones where Dinneroo bundles are **configured** in the system
- Snowflake data shows zones where customers **actually ordered** during the trial
- The 233 zones with partners but no orders are **expansion zones** awaiting activation

---

## Data Sources Explained

### 1. Anna's Zone X Dish Mapping (Supply Data)
- **Source:** `DATA/1_SOURCE/anna_slides/Dish Analysis Dec-25 - Zone X Dish Mapping.csv`
- **Processed to:** `DATA/3_ANALYSIS/anna_zone_dish_counts.csv`
- **Total zones:** 1,306 (all Deliveroo zones in UK/Ireland)
- **Zones with 0 partners:** 872 (no Dinneroo coverage)
- **Zones with 1+ partners:** **434** (Dinneroo configured)

This represents **potential coverage** based on:
- Which brands have agreed to offer Dinneroo bundles
- Delivery radius from onboarded restaurant sites
- Not all zones are "live" for customers yet

**Verification:**
```bash
# Zones with num_brands > 0
awk -F',' 'NR>1 && $6>0 {count++} END {print count}' DATA/3_ANALYSIS/anna_zone_dish_counts.csv
# Result: 434
```

### 2. Snowflake Orders (Behavioral Data)
- **Source:** `DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv`
- **Date range:** Aug 2025 - Jan 2026
- **Total orders:** **82,350** (as of 2026-01-07)
- **Unique zones with orders:** **201**

This represents **actual customer behavior** during the trial period.

**Note on 197 vs 201:** The MVP threshold analysis (`mvp_threshold_discovery.json`) uses 197 zones because 4 zones had orders but insufficient data for reliable statistical analysis (below minimum sample size thresholds).

### 3. The Gap (233 Zones)

Zones in Anna's data with partners but no Snowflake orders:

| Region | Zones Without Orders |
|--------|---------------------|
| South England and Wales | 63 |
| Greater London | 62 |
| North England | 62 |
| Ireland and Scotland | 40 |
| Core London | 6 |

**Examples of high-partner zones without orders:**
- Walworth (London): 14 partners, 61 dishes
- Chorlton (Manchester): 12 partners, 60 dishes
- Caversham (Reading): 12 partners, 59 dishes
- Bow (London): 10 partners, 37 dishes

---

## Why This Happened

1. **Trial Period Scope:** The trial focused on specific zones, not all configured zones
2. **Phased Rollout:** Partners were onboarded progressively; some zones weren't activated for customers
3. **AM Expansion:** Account Managers are now (Jan 2026) onboarding new sites to activate these zones

---

## Historical Discrepancies

### Order Count: 82,350 vs 80,724

| Value | Source | Date | Status |
|-------|--------|------|--------|
| 82,350 | ALL_DINNEROO_ORDERS.csv | 2026-01-07 | **Current - use this** |
| 80,724 | Earlier Snowflake pull | 2026-01-05 | Deprecated |

The difference of 1,626 orders represents new orders between the two data pulls.

**Files to update:**
- `DELIVERABLES/reports/MASTER_ANALYSIS_REPORT.md` - says 80,724
- `DELIVERABLES/reports/mvp_zone_report_product_director.md` - says 80,724

### Zone Count: 434 vs 435

Some documents reference 435 zones with partners. The verified count is **434** (from `anna_zone_dish_counts.csv` with `num_brands > 0`).

---

## Impact on Analysis

### Our Analysis Is Valid

The MVP threshold analysis uses **behavioral data from zones with actual orders**. This is the correct approach because:

1. **We're measuring real customer behavior** - repeat rate, ratings, satisfaction
2. **Zones without orders have no behavioral data** - we can't analyze what doesn't exist
3. **Trial data is representative** - 82,350 orders across 201 zones is a robust sample

### Dashboard Clarification

The dashboard should clearly state:
- "Trial period: 201 zones · 82,350 orders"
- Data scope callout explaining the 434 vs 201 difference
- Note that 233 zones are ready for expansion

---

## Recommendations

1. **For MVP thresholds:** Continue using trial data (197-201 zones) - this is valid
2. **For expansion planning:** Use Anna's data (434 zones) to identify activation priorities
3. **For future analysis:** Re-run threshold analysis once expansion zones have order data
4. **For all reports:** Use 82,350 as the order count (not 80,724)

---

## Key Files

| File | Purpose | Key Count |
|------|---------|-----------|
| `DATA/3_ANALYSIS/anna_zone_dish_counts.csv` | Processed Anna zone data | 434 zones with partners |
| `DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv` | Order data | 82,350 orders, 201 zones |
| `DATA/3_ANALYSIS/zone_quality_scores.csv` | Derived zone metrics | 197 zones analyzed |
| `DATA/3_ANALYSIS/mvp_threshold_discovery.json` | Threshold analysis | 197 zones analyzed |
| `config/dashboard_metrics.json` | Single source of truth | All reconciled counts |

---

## Authoritative Source

For all dashboard and report metrics, refer to:

**`config/dashboard_metrics.json`**

This file contains reconciled counts with provenance and verification dates.

---

*Last updated: January 7, 2026*
*Verified by: Feedback Agent review*
