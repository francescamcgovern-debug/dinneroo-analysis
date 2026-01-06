# System Map: Data Sources, Agents & Questions

## Purpose

This document tracks ALL data sources, which agents use them, and ensures every question can be answered with the available data.

---

## Data Source Inventory

### Snowflake Data (`DATA/1_SOURCE/snowflake/`)

| File | Description | Rows (approx) | Key Columns | Used By |
|------|-------------|---------------|-------------|---------|
| `ALL_DINNEROO_ORDERS.csv` | All Dinneroo orders | 70k+ | ORDER_ID, USER_ID, ZONE_NAME, PARTNER_NAME, ORDER_DATE | Dish, Zone, Customer, Gap |
| `ALL_DINNEROO_CUSTOMERS.csv` | All Dinneroo customers | 32k+ | USER_ID, first_order_date, total_orders, frequency | Customer, Zone |
| `DINNEROO_RATINGS.csv` | Orders with ratings (~40% coverage) | ~28k | ORDER_ID, RATING_STARS, RATING_COMMENT | Dish, Zone |
| `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` | Partners available per zone | Varies | ZONE_NAME, PARTNER_NAME, cuisine_type | Dish, Zone, Gap |
| `DINNEROO_DISH_COUNTS_BY_ZONE.csv` | Dish counts per zone | Varies | ZONE_NAME, dish_count, cuisine_count | Dish, Zone, Gap |
| `DINNEROO_DISH_COUNTS_BY_PARTNER.csv` | Dish counts per partner | Varies | PARTNER_NAME, dish_count | Dish |
| `DINNEROO_MENU_CATALOG.csv` | Full menu items | Varies | PARTNER_NAME, dish_name, category | Dish |
| `FULL_ORDER_HISTORY.csv` | Full history for survey respondents | Varies | USER_ID, ORDER_ID, order history | Customer |

### Survey Data (`DATA/1_SOURCE/surveys/`)

| File | Description | Rows (approx) | Key Columns | Used By |
|------|-------------|---------------|-------------|---------|
| `POST_ORDER_SURVEY-CONSOLIDATED.csv` | Post-order feedback | ~1,500 | ORDER_ID, SATISFACTION, DISH_SENTIMENT, demographics | Dish, Customer, Zone |
| `DROPOFF_SURVEY-CONSOLIDATED.csv` | Dropoff/non-customer feedback | ~800 | exploration_question, barriers, unmet_demand | Gap, Customer |
| `dropoff_LATEST.csv` | Latest dropoff export | ~800 | Same as consolidated | Gap, Customer |

### Enriched Data (`DATA/2_ENRICHED/`)

| File | Description | Source Files | Key Additions | Used By |
|------|-------------|--------------|---------------|---------|
| `post_order_enriched_COMPLETE.csv` | Survey linked to orders | POST_ORDER + Snowflake | Order details, revenue, frequency | Dish, Customer, Zone |
| `DROPOFF_ENRICHED.csv` | Dropoff with segments | DROPOFF + Snowflake | Tried Before/Never Tried flag | Gap, Customer |

---

## Complete Data Sources

See `DOCUMENTATION/SHARED/05_DATA_SOURCES_INVENTORY.md` for full inventory.

### Survey/Research Data (FIXED - Cannot Refresh)
| Source | File | Sample | Key Use |
|--------|------|--------|---------|
| Post-Order Survey | `POST_ORDER_SURVEY-CONSOLIDATED.csv` | ~1,500 | Satisfaction, open-text feedback |
| Dropoff Survey | `dropoff_LATEST.csv` | ~800 | Unmet demand, barriers |
| Bounce Survey | `external/Bounce Survey*.xlsx` | TBD | Additional barriers |
| Pulse Survey | `external/Pulse_Survey*.csv` | TBD | Loyalty context |
| Customer Transcripts | `qual_research/transcripts/` | 88 interviews | Unprompted dish mentions |
| WBRs | `external/WBRs/` | 10 weeks | Partner execution |

### Snowflake Data (CAN REFRESH)
| Source | File | Key Use |
|--------|------|---------|
| Orders | `ALL_DINNEROO_ORDERS.csv` | Revealed preference, zone performance |
| Ratings | `DINNEROO_RATINGS.csv` | Feedback (~40% coverage) |
| Catalog | `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` | Availability |
| Customers | `ALL_DINNEROO_CUSTOMERS.csv` | Segmentation |

### ⚠️ CAUTION: OG Survey (Included but Requires Triangulation)
| Location | Status |
|----------|--------|
| `historical_surveys/og_survey/` | **Included** - 13 files covering demographics, dish preferences, decision-making |

**Bias Risk:** This survey was the source of over-reliance in the old project. It contains stated preference (what people SAY) not revealed preference (what they DO), and only asked about a limited set of dishes.

**Rule:** OG Survey data must ALWAYS be triangulated with Snowflake behavioral data before making recommendations.

### Historical Surveys (`DATA/1_SOURCE/historical_surveys/`)
| Source | Location | Key Use |
|--------|----------|---------|
| OG Survey | `og_survey/` | Demographics, decision-making, customisation (triangulate!) |
| BODS Families | `bods_families_dec2024/` | Broader family context, verbatims |

**Weights are NOT prescribed.** Determine per analysis and document reasoning.

---

## Agent Brief Status

| Agent | File | Status | Mission | Key Data Sources |
|-------|------|--------|---------|------------------|
| **Coordinator** | `00_COORDINATOR.md` | ✅ Complete | Route questions to agents | N/A |
| **Data Agent** | `05_DATA_AGENT.md` | ✅ Full | Load, validate, prepare data | Snowflake (all tables) |
| **Dish Agent** | `01_DISH_AGENT.md` | ✅ Full | Dish/cuisine recommendations | Orders (40%), Survey (40%), Dropoff (10%), Ratings (5%), Catalog (5%) |
| **Zone Agent** | `02_ZONE_AGENT.md` | 🔲 Stub | Zone performance analysis | Orders (50%), Survey (20%), Dropoff (10%), Ratings (10%), Catalog (10%) |
| **Customer Agent** | `03_CUSTOMER_AGENT.md` | 🔲 Stub | Customer segmentation | Survey (50%), Orders (30%), Dropoff (10%), Ratings (10%) |
| **Gap Agent** | `04_GAP_AGENT.md` | 🔲 Stub | Gap/opportunity analysis | Orders (30%), Dropoff (30%), Catalog (20%), Survey (20%) |

---

## Question Coverage Matrix

### Can Each Question Be Answered?

| Question | Primary Agent | Data Available? | Notes |
|----------|---------------|-----------------|-------|
| What makes a perfect zone (dishes/cuisines)? | Dish | ✅ Yes | Orders + Survey + Catalog |
| Which dishes are essential vs nice-to-have? | Dish | ✅ Yes | Orders + Survey |
| Which partners should we prioritize per zone? | Dish | ✅ Yes | Orders + Survey + Catalog |
| What dish gaps exist? | Dish/Gap | ✅ Yes | Dropoff + Catalog |
| Which zones are performing best/worst? | Zone | ✅ Yes | Orders + Survey |
| What distinguishes high vs low performing zones? | Zone | ✅ Yes | Orders + Survey + Catalog |
| Who are our most valuable customers? | Customer | ✅ Yes | Survey + Orders |
| What drives customer satisfaction? | Customer | ✅ Yes | Survey |
| Where should we expand? | Gap | ✅ Yes | Dropoff + Catalog + Orders |
| What unmet demand exists? | Gap | ✅ Yes | Dropoff |

---

## Data Gaps & Limitations

### What We DON'T Have

| Missing Data | Impact | Workaround |
|--------------|--------|------------|
| Real-time data | Data may be up to 7 days old | Check file dates before analysis |
| Non-Dinneroo comparison | Can't compare to regular Deliveroo | Use internal benchmarks |
| Cycle 1 transcripts | Missing earliest customer interviews | Use Cycles 2-13 (88 interviews) |

### Survey/Research Data (All Copied)

| Data Type | Location | Files | Status |
|-----------|----------|-------|--------|
| **Post-Order Survey** | `DATA/1_SOURCE/surveys/` | Consolidated + enriched | ✅ Copied |
| **Dropoff Survey** | `DATA/1_SOURCE/surveys/` | Latest + enriched | ✅ Copied |
| **Qual Transcripts** | `DATA/1_SOURCE/qual_research/transcripts/` | 88 customer interviews | ✅ Copied |
| **WBR Reports** | `DATA/1_SOURCE/external/WBRs/` | 10 weekly reviews (W6-W15) | ✅ Copied |
| **Bounce Survey** | `DATA/1_SOURCE/external/` | Wave 1 results | ✅ Copied |
| **Pulse Survey** | `DATA/1_SOURCE/external/` | Nov 2025 | ✅ Copied |
| **Pascal Reports** | `DATA/1_SOURCE/qual_research/pascal_reports/` | Cycle 19 | ✅ Copied |
| **Doordash Research** | `DATA/1_SOURCE/external/` | Competitive reference | ✅ Copied |

### OG Survey (Included - Use With Caution)

| Data Type | Location | Status |
|-----------|----------|--------|
| **OG Survey** | `historical_surveys/og_survey/` | ✅ Copied - 13 files |

**⚠️ TRIANGULATION REQUIRED:** The OG Survey was the source of bias in the old project. It must ALWAYS be triangulated with Snowflake behavioral data before making recommendations. See `05_DATA_SOURCES_INVENTORY.md` for details.

### Known Biases by Source

| Source | Bias | Mitigation |
|--------|------|------------|
| Post-Order Survey | Survivorship (only orderers) | Use for "what works", not barriers |
| Dropoff Survey | Self-selection | Use for themes, not prevalence |
| Snowflake Orders | No "why" | Combine with survey for context |
| Ratings | 40% coverage only | Don't use for volume, only sentiment |

---

## Shared Context Documents

| Document | Purpose | Used By |
|----------|---------|---------|
| `01_BUSINESS_CONTEXT.md` | What is Dinneroo, stakeholders | All agents |
| `02_DATA_SOURCES.md` | Where data is, how to use it | All agents |
| `03_DEFINITIONS.md` | How to calculate metrics | All agents |
| `04_QUALITY_STANDARDS.md` | Evidence rules, sample sizes | All agents |
| `05_DATA_SOURCES_INVENTORY.md` | Complete data inventory with bias warnings | All agents |

---

## Agent Brief → Data File Cross-Reference

### Dish Agent (`01_DISH_AGENT.md`)

| Data File | Mentioned in Brief? | Weight | Purpose |
|-----------|:-------------------:|--------|---------|
| `ALL_DINNEROO_ORDERS.csv` | ✅ Yes | 40% | Order counts by dish/zone |
| `post_order_enriched_COMPLETE.csv` | ✅ Yes | 40% | Satisfaction by dish |
| `dropoff_LATEST.csv` | ✅ Yes | 10% | Unmet demand |
| `DINNEROO_RATINGS.csv` | ✅ Yes | 5% | Star ratings |
| `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` | ✅ Yes | 5% | Availability |
| `DINNEROO_DISH_COUNTS_BY_ZONE.csv` | ✅ Yes | - | Variety analysis |
| `DINNEROO_DISH_COUNTS_BY_PARTNER.csv` | ✅ Yes | - | Partner variety |
| `DINNEROO_MENU_CATALOG.csv` | ✅ Yes | - | Menu items |

### Zone Agent (`02_ZONE_AGENT.md`) - STUB

| Data File | Will Need | Weight (planned) | Purpose |
|-----------|:---------:|------------------|---------|
| `ALL_DINNEROO_ORDERS.csv` | ✅ | 50% | Zone volume, trends |
| `post_order_enriched_COMPLETE.csv` | ✅ | 20% | Zone satisfaction |
| `DROPOFF_ENRICHED.csv` | ✅ | 10% | Zone barriers |
| `DINNEROO_RATINGS.csv` | ✅ | 10% | Zone ratings |
| `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` | ✅ | 10% | Zone coverage |
| `ALL_DINNEROO_CUSTOMERS.csv` | ✅ | - | Customers per zone |

### Customer Agent (`03_CUSTOMER_AGENT.md`) - STUB

| Data File | Will Need | Weight (planned) | Purpose |
|-----------|:---------:|------------------|---------|
| `post_order_enriched_COMPLETE.csv` | ✅ | 50% | Demographics, satisfaction |
| `ALL_DINNEROO_ORDERS.csv` | ✅ | 30% | Behavior, frequency |
| `DROPOFF_ENRICHED.csv` | ✅ | 10% | Non-customer barriers |
| `DINNEROO_RATINGS.csv` | ✅ | 10% | Sentiment by segment |
| `ALL_DINNEROO_CUSTOMERS.csv` | ✅ | - | Customer base |
| `FULL_ORDER_HISTORY.csv` | ✅ | - | Individual histories |

### Gap Agent (`04_GAP_AGENT.md`) - STUB

| Data File | Will Need | Weight (planned) | Purpose |
|-----------|:---------:|------------------|---------|
| `ALL_DINNEROO_ORDERS.csv` | ✅ | 30% | Current performance |
| `DROPOFF_ENRICHED.csv` | ✅ | 30% | Unmet demand |
| `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` | ✅ | 20% | Current availability |
| `post_order_enriched_COMPLETE.csv` | ✅ | 20% | What's working |
| `DINNEROO_DISH_COUNTS_BY_ZONE.csv` | ✅ | - | Gap identification |

---

## Checklist: Is the System Complete?

### Data
- [x] All primary Snowflake files copied
- [x] All survey files copied
- [x] Enriched datasets copied
- [x] Qual transcripts (88 customer interviews, Cycles 2-13)
- [x] WBR data (10 weeks, W6-W15)
- [x] OG Survey (13 files - use with triangulation)
- [x] BODS Families Survey (Dec 2024)
- [x] External sources (YouGov, Medallia, Doordash, etc.)

### Agents
- [x] Coordinator routes all question types
- [x] Data Agent fully implemented (Snowflake pulls, validation)
- [x] Dish Agent fully implemented
- [ ] Zone Agent needs full implementation
- [ ] Customer Agent needs full implementation
- [ ] Gap Agent needs full implementation

### Infrastructure
- [x] Snowflake connector copied (`integrations/snowflake_connector.py`)

### Documentation
- [x] Business context documented
- [x] Data sources documented
- [x] Definitions documented
- [x] Quality standards documented
- [x] Data sources inventory documented
- [x] Research questions structured

### Outputs
- [x] Reports folder ready
- [x] Dashboards folder ready
- [ ] First deliverable produced (pending)

---

## How to Use This Document

1. **Before analysis:** Check that required data sources are available
2. **When adding data:** Update the inventory tables
3. **When building agents:** Verify data coverage in the matrix
4. **When answering questions:** Confirm the question is covered
5. **When debugging:** Check for gaps or missing data

---

## Anti-Replication Checklist

Before accepting any finding, verify it's NOT just repeating old insights:

### Things That Must Be Calculated Fresh (Not Assumed)

| Assumption to Avoid | Verify By |
|---------------------|-----------|
| "Pizza is a top dish" | Run order counts + satisfaction by dish |
| "Zone X is high performing" | Calculate zone metrics from current data |
| "Families prefer X" | Segment analysis on fresh survey data |
| "40% of orders have ratings" | Check actual coverage in current data |
| "We have 70k orders" | Count rows in current data pull |
| "Wagamama has high satisfaction" | Calculate partner satisfaction fresh |

### Red Flags That Suggest Replication

- Finding matches old project conclusions exactly
- Specific percentages appear without fresh calculation
- Partner/dish names appear as "winners" without analysis
- Conclusions written before data is loaded
- Examples from briefs copied as findings

### Validation Questions

Before reporting any insight, ask:
1. Did I calculate this from the current data?
2. Can I show the code/query that produced this number?
3. Is this different from what I might have assumed?
4. Would this finding change if the data changed?

---

## Update Log

| Date | Change | By |
|------|--------|-----|
| 2026-01-05 | Initial system map created | Setup |
| 2026-01-05 | Added anti-replication checklist | Setup |

---

*Keep this document updated as the system evolves.*

