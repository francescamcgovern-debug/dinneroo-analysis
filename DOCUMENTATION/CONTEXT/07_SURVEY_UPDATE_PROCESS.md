# Survey Data Update Process

## Overview

This document describes how to update survey data from Alchemer exports. The two main surveys have different characteristics:

| Survey | Status | Update Frequency | Deduplication Required |
|--------|--------|------------------|------------------------|
| **Post-Order Survey** | Ongoing | Weekly/as needed | Yes - overlapping exports |
| **Dropoff Survey** | Closed/Complete | Rarely | No - full replacement |

---

## Post-Order Survey (Ongoing)

### What It Is
Feedback collected from customers AFTER placing a Dinneroo order. New responses come in continuously as customers complete orders.

### Current Data
- **File**: `DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv`
- **Enriched**: `DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv`

### How to Update

#### Step 1: Export from Alchemer
- Export the full survey (Week 6 onwards - this is when Dinneroo launched)
- Alchemer only allows full exports, not incremental
- Save as: `DATA/1_SOURCE/surveys/POST_ORDER_ALCHEMER_YYYY-MM-DD.csv`

#### Step 2: Run Deduplication Script
```bash
python scripts/phase1_data/04_consolidate_surveys.py --post-order
```

The script will:
1. Load the existing consolidated file
2. Load the new Alchemer export
3. Deduplicate using `Response ID` (primary) or `ORDER_ID` (fallback)
4. Keep the most recent version of any duplicate responses
5. Save the updated consolidated file
6. Log how many new responses were added

#### Step 3: Re-run Enrichment
```bash
python scripts/phase1_data/05_enrich_surveys.py --post-order
```

This joins survey responses with Snowflake order data to create the enriched file.

### Key Fields for Deduplication
| Field | Purpose |
|-------|---------|
| `Response ID` | Unique survey response identifier |
| `ORDER_ID` | Links to Snowflake orders (use for cross-referencing) |
| `Date Submitted` | When the response was submitted |

### Expected Overlap
When you export from Alchemer, expect significant overlap with existing data:
- Alchemer exports everything from Week 6 onwards
- Existing consolidated file already has responses up to the last export date
- Deduplication will filter out duplicates and add only new responses

---

## Dropoff Survey (Closed/Complete)

### What It Is
Feedback from people who browsed Dinneroo but didn't order. Captures barriers and unmet demand.

### Current Data
- **File**: `DATA/1_SOURCE/surveys/DROPOFF_SURVEY-CONSOLIDATED.csv` (740 rows)
- **Alternative**: `DATA/1_SOURCE/surveys/dropoff_LATEST.csv` (838 rows)
- **Enriched**: `DATA/2_ENRICHED/DROPOFF_ENRICHED.csv`

### How to Update

#### Step 1: Export from Alchemer
- Export the full survey (all-time)
- This survey is closed/complete (~795 responses total)
- Save as: `DATA/1_SOURCE/surveys/DROPOFF_ALCHEMER_YYYY-MM-DD.csv`

#### Step 2: Compare and Replace
```bash
python scripts/phase1_data/04_consolidate_surveys.py --dropoff
```

The script will:
1. Compare new export row count with existing
2. If new export has more/same responses, replace the consolidated file
3. Log any discrepancies

#### Step 3: Re-run Enrichment
```bash
python scripts/phase1_data/05_enrich_surveys.py --dropoff
```

---

## File Naming Convention

### Raw Exports (from Alchemer)
```
DATA/1_SOURCE/surveys/
├── POST_ORDER_ALCHEMER_2026-01-06.csv    ← New export (keep for audit)
├── DROPOFF_ALCHEMER_2026-01-06.csv       ← New export (keep for audit)
```

### Consolidated Files (pipeline uses these)
```
DATA/1_SOURCE/surveys/
├── POST_ORDER_SURVEY-CONSOLIDATED.csv    ← Deduplicated, complete
├── DROPOFF_SURVEY-CONSOLIDATED.csv       ← Latest complete version
├── dropoff_LATEST.csv                    ← Legacy (may be deprecated)
```

### Enriched Files (analysis uses these)
```
DATA/2_ENRICHED/
├── post_order_enriched_COMPLETE.csv      ← Joined with Snowflake
├── DROPOFF_ENRICHED.csv                  ← Joined with Snowflake
```

---

## Audit Trail

When updating surveys, the consolidation script logs:
- Date of update
- Previous row count
- New export row count
- Duplicates removed
- Net new responses added
- Any data quality issues

Logs are saved to: `DATA/3_ANALYSIS/logs/survey_consolidation_YYYY-MM-DD.log`

---

## Troubleshooting

### "Response ID not unique"
The Post-Order survey uses collated links, so `Response ID` may not be unique across all exports. Use `ORDER_ID` as the primary deduplication key when available.

### Row count mismatch
If the new export has fewer rows than expected:
- Check the export date range in Alchemer
- Verify you exported "Complete" responses only (not partial)
- Check for any filtering applied in Alchemer

### Missing ORDER_ID
Some survey responses may not have an `ORDER_ID` if:
- The customer didn't provide it
- The order lookup failed
- It's a test response

These responses are kept but flagged for manual review.

---

## Schedule

| Survey | Recommended Update Frequency |
|--------|------------------------------|
| Post-Order | Weekly (before any analysis) |
| Dropoff | Monthly (or when notified of new responses) |

---

*Last updated: 2026-01-06*




