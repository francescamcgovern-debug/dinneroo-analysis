# Data Sources Guide

## Overview

This document explains WHERE data is, HOW to use it correctly, and what LIMITATIONS to be aware of. It does NOT contain findings or conclusions.

---

## Data Structure

```
DATA/
├── 1_SOURCE/           ← Raw data (DO NOT MODIFY)
│   ├── surveys/        ← Survey exports from Alchemer
│   ├── snowflake/      ← Snowflake data pulls
│   ├── external/       ← Third-party data (WBRs, etc.)
│   └── qual_research/  ← Interview transcripts
│
├── 2_ENRICHED/         ← Linked/processed datasets
│
└── 3_ANALYSIS/         ← Analysis outputs
```

**Rule:** Never modify files in `1_SOURCE/`. Create new files in `2_ENRICHED/` or `3_ANALYSIS/`.

---

## Primary Data Sources

### 1. Post-Order Survey

| Attribute | Value |
|-----------|-------|
| **File** | `DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv` |
| **Enriched** | `DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv` |
| **What it is** | Feedback from customers AFTER placing a Dinneroo order |
| **Sample** | Check file for current count |
| **Status** | **ONGOING** - new responses come in continuously |
| **Update Process** | See `07_SURVEY_UPDATE_PROCESS.md` |

**Use for:**
- Satisfaction analysis
- Dish/partner feedback
- Customer demographics
- "What's working" questions

**Limitations:**
- Only captures people who ordered (survivorship bias)
- May skew toward very positive/negative experiences
- Cannot tell you about non-customers

**⚠️ Updating:** This survey is ongoing. When updating, export from Alchemer and run the deduplication script. See `DOCUMENTATION/CONTEXT/07_SURVEY_UPDATE_PROCESS.md` for full instructions.

**Key Columns:**
| Column | Description |
|--------|-------------|
| `ORDER_ID` | Links to Snowflake orders (use for deduplication) |
| `SATISFACTION` | "Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied" |
| `DISH_SENTIMENT` | "Loved it", "Liked it", "Neutral", "Disliked it", "Hated it" |
| `NUM_CHILDREN` | Number of children (families only) |
| `WHO_ORDERING` | Who the order was for |
| `REORDER_*` | Reorder intent questions |
| `ORDER_B10_*` | Issue flags (Late, Missing, Cancelled, etc.) |

**⚠️ Deduplication:** Use `ORDER_ID`, NOT `RESPONSE_ID`. The survey uses collated links so RESPONSE_ID is not unique.

---

### 2. Dropoff Survey

| Attribute | Value |
|-----------|-------|
| **File** | `DATA/1_SOURCE/surveys/DROPOFF_SURVEY-CONSOLIDATED.csv` |
| **Enriched** | `DATA/2_ENRICHED/DROPOFF_ENRICHED.csv` |
| **What it is** | Feedback from people who browsed but didn't order |
| **Sample** | ~795 responses (all-time) |
| **Status** | **CLOSED/COMPLETE** - no new responses expected |
| **Update Process** | See `07_SURVEY_UPDATE_PROCESS.md` |

**Use for:**
- Barrier analysis
- Conversion blockers
- Unmet needs

**Limitations:**
- Self-selection bias (only motivated non-customers respond)
- Cannot extrapolate prevalence to all non-orderers
- Recall may be inaccurate

**Critical: Two Segments**

The survey has TWO distinct segments based on the question "How far did you get?":
- **"Tried Before"**: Answered "I placed an order"
- **"Never Tried"**: All other responses

⚠️ **These segments were shown DIFFERENT questions.** Do not mix them for analysis.

---

### 3. Snowflake Order Data

| File | What it Contains | Coverage |
|------|------------------|----------|
| `ALL_DINNEROO_ORDERS.csv` | All Dinneroo orders | 100% |
| `DINNEROO_RATINGS.csv` | Orders with ratings/comments | ~40% |
| `ALL_DINNEROO_CUSTOMERS.csv` | All Dinneroo customers | 100% |
| `FULL_ORDER_HISTORY.csv` | Full history for survey respondents | Survey respondents only |

**Use for:**
- Actual ordering behavior
- Volume and trends
- Customer segmentation by behavior
- Zone/partner performance

**Limitations:**
- No "why" - only what people did, not why
- Cannot see unmet needs or non-customers

**Key Columns:**
| Column | Description |
|--------|-------------|
| `ORDER_ID` | Unique order identifier |
| `USER_ID` | Customer identifier |
| `CREATED_AT` / `ORDER_DATE` | When order was placed |
| `IS_DINNEROO` / `IS_FAMILY_TIME_ORDER` | Dinneroo flag |
| `PARTNER_NAME` | Restaurant name |
| `ZONE_NAME` | Delivery zone |
| `RATING_STARS` | 1-5 rating (if rated) |

**⚠️ Coverage:** Use `ALL_DINNEROO_ORDERS` for volume analysis. `DINNEROO_RATINGS` only has ~40% of orders.

---

### 4. Partner/Zone Data

| File | What it Contains |
|------|------------------|
| `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` | Partners available in each zone |
| `DINNEROO_DISH_COUNTS_BY_ZONE.csv` | Dish counts per zone |
| `DINNEROO_DISH_COUNTS_BY_PARTNER.csv` | Dish counts per partner |
| `DINNEROO_MENU_CATALOG.csv` | Menu items |

**Use for:**
- Zone coverage analysis
- Partner availability
- Dish/cuisine mapping

---

### 5. Qualitative Data

| Location | What it Contains |
|----------|------------------|
| `qual_research/transcripts/` | Customer interview transcripts (88 files) |
| `qual_research/pascal_reports/` | Research summary reports |
| `external/WBRs/` | Weekly Business Reviews |

**Use for:**
- Understanding "why" behind quantitative patterns
- Verbatim quotes as evidence
- Theme enrichment

**Limitations:**
- Small sample (not for prevalence claims)
- Recruited participants (not random)

---

## Data Freshness

| File Type | Refresh Frequency | Max Age Before Stale |
|-----------|-------------------|---------------------|
| Survey exports | Weekly | 7 days |
| Snowflake orders | Weekly | 7 days |
| Partner catalog | Monthly | 30 days |

**Check file modification dates before analysis.**

---

## Linking Data Sources

### Survey to Orders
1. **Best:** Match on `ORDER_ID` (highest confidence)
2. **Fallback:** Match on `email + date ±1 day` (medium confidence)
3. **Last resort:** Match on `email only` (lowest confidence)

### Customers to Orders
- Link via `USER_ID`

### Orders to Zones
- `ZONE_NAME` column in order data

---

## Which File for Which Question?

| Question | Primary Source |
|----------|----------------|
| "How many orders in this zone?" | `ALL_DINNEROO_ORDERS.csv` |
| "What's the satisfaction rate?" | Post-order survey |
| "Why don't people convert?" | Dropoff survey |
| "Which partners are in this zone?" | `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` |
| "What dishes does this partner have?" | `DINNEROO_DISH_COUNTS_BY_PARTNER.csv` |
| "What do customers say in their own words?" | Transcripts, `DINNEROO_RATINGS.csv` |

---

## Data Source Triangulation

For robust findings, triangulate across sources:

| Finding Type | Ideal Sources |
|--------------|---------------|
| Zone performance | Orders + Survey + Ratings |
| Customer satisfaction | Survey + Ratings |
| Barriers | Dropoff + Qual |
| Partner performance | Orders + Survey |

Single-source findings should be flagged as exploratory.

---

*This document is technical reference only. Derive your own findings from the data.*

