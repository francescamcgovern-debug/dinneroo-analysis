# Complete Data Sources Inventory

## Purpose

This document lists ALL available data sources for the project. The agent should determine appropriate weighting based on the specific question being answered.

**No fixed weights are prescribed.** Weight decisions should be documented and justified for each analysis.

---

## The Research Goal

**Define an MVP Zone:**
- Minimum number of partners needed
- Which cuisines must be represented
- Which dishes are essential
- How to present dishes to be family-friendly

**Key Constraint:** We can recommend dishes/cuisines that weren't in the original survey - use behavioral data and open-text to discover opportunities.

**Key Reframe:** Think DISH TYPES, not brands. The question isn't "should we recruit Nando's?" - it's "do families want Grilled Chicken with Customizable Sides?" See `01_DISH_AGENT.md` for the Dish Types Framework.

---

## Survey Data

### 1. Post-Order Survey (ONGOING)
| Attribute | Value |
|-----------|-------|
| **File** | `DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv` |
| **Enriched** | `DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv` |
| **What it is** | Feedback from customers AFTER placing a Dinneroo order |
| **Sample** | Check file for current count (grows weekly) |
| **Status** | **ONGOING** - new responses continuously |
| **Strengths** | Actual customer experience, satisfaction data, open-text feedback |
| **Limitations** | Only orderers (survivorship bias), may skew to extremes |
| **Use for** | Satisfaction by dish/partner, customer feedback, "what's working" |
| **Update Process** | See `07_SURVEY_UPDATE_PROCESS.md` |

**Key open-text fields for dish discovery:**
- `DISH_IMPROVEMENTS`
- `SUGGESTED_IMPROVEMENTS`
- Any open-text about what they'd like to see

**⚠️ Before analysis:** Check the data freshness. If more than 7 days old, request a fresh Alchemer export.

---

### 2. Dropoff Survey (CLOSED)
| Attribute | Value |
|-----------|-------|
| **File** | `DATA/1_SOURCE/surveys/DROPOFF_SURVEY-CONSOLIDATED.csv` |
| **Enriched** | `DATA/2_ENRICHED/DROPOFF_ENRICHED.csv` |
| **What it is** | Feedback from people who browsed but didn't order |
| **Sample** | ~795 responses (all-time, complete) |
| **Status** | **CLOSED** - no new responses expected |
| **Strengths** | Unmet demand, barriers, what people wanted but couldn't find |
| **Limitations** | Self-selection, recall may be inaccurate |
| **Use for** | Discovering dishes/cuisines people wanted but we don't have |
| **Update Process** | See `07_SURVEY_UPDATE_PROCESS.md` |

**Two segments (different questions):**
- "Tried Before" - ordered at least once
- "Never Tried" - never ordered

---

### 3. Bounce Survey
| Attribute | Value |
|-----------|-------|
| **File** | `DATA/1_SOURCE/external/Bounce Survey Results*.xlsx` |
| **What it is** | Survey of people who bounced from Dinneroo |
| **Strengths** | Different methodology, barrier focus |
| **Limitations** | May overlap with dropoff |
| **Use for** | Additional barrier data, triangulation |

---

### 4. Pulse Survey
| Attribute | Value |
|-----------|-------|
| **File** | `DATA/1_SOURCE/external/Pulse_Survey_Loyalty_Nov2025.csv` |
| **What it is** | Loyalty-focused survey |
| **Strengths** | Frequency and loyalty context |
| **Limitations** | Specific focus |
| **Use for** | Understanding repeat behavior drivers |

---

### 5. Customer Interview Transcripts
| Attribute | Value |
|-----------|-------|
| **Location** | `DATA/1_SOURCE/qual_research/transcripts/customer_interviews/` |
| **What it is** | 88 customer interview transcripts (Cycles 2-13) |
| **Strengths** | Deep "why" context, verbatim quotes, unprompted dish mentions |
| **Limitations** | Small sample, recruited participants |
| **Use for** | Discovering dishes/cuisines mentioned organically, understanding family needs |

**⭐ HIGH VALUE FOR DISH DISCOVERY:** These transcripts contain unprompted mentions of dishes and cuisines that weren't in any survey. Use LLM to extract.

---

### 6. WBR Reports (Weekly Business Reviews)
| Attribute | Value |
|-----------|-------|
| **Location** | `DATA/1_SOURCE/external/WBRs/` |
| **What it is** | 10 weeks of operational partner feedback (W6-W15) |
| **Strengths** | Partner execution context, operational issues |
| **Limitations** | Partner perspective, not customer |
| **Use for** | Understanding what partners can/can't do, execution constraints |

---

### 7. Pascal Research Reports
| Attribute | Value |
|-----------|-------|
| **Location** | `DATA/1_SOURCE/qual_research/pascal_reports/` |
| **What it is** | Synthesized qualitative research reports |
| **Strengths** | Professional analysis of qual data |
| **Limitations** | Already interpreted |
| **Use for** | Context, but verify against raw transcripts |

---

## ⚠️ CAUTION: OG Survey (Pre-Launch)

| Attribute | Value |
|-----------|-------|
| **Location** | `DATA/1_SOURCE/historical_surveys/og_survey/` |
| **Files** | Dishes Ranking.csv, Dishes Scorecard.csv, Key Dishes Data.csv, Final Survey Data.csv, Activity Analysis.csv, Age.csv, Decision Making Analysis.csv, Diary Study Charts.csv, Dishes Charts.csv, Dishes Customisation.csv, Influences Analysis.csv, Time Taken.csv |
| **What it is** | Pre-launch survey asking about dish preferences and family behaviors |
| **Sample** | ~400 responses |
| **Strengths** | Rich demographic data, decision-making insights, customisation preferences |
| **Limitations** | Stated preference (not revealed), limited dish list, pre-launch |

### ⚠️ BIAS RISK - USE WITH TRIANGULATION

**This survey was the main source of bias in the old project.** It should be ONE input among many, not the primary driver.

**The problem:** Previous analysis over-relied on the dish rankings from this survey, which:
1. Only asked about a limited set of dishes
2. Captured stated preference (what people SAY) not revealed preference (what they DO)
3. Was collected pre-launch before anyone had tried Dinneroo

**USE FOR (triangulate with other sources):**
- Demographic insights (family composition, ages)
- Decision-making patterns
- Customisation preferences
- Expectation vs reality comparison

**DO NOT USE ALONE FOR:**
- Dish recommendations (must triangulate with Snowflake orders)
- Cuisine prioritization (must triangulate with actual orders)
- Demand signals (must validate with revealed behavior)

**ALWAYS ASK:** "Does the behavioral data (Snowflake orders) support this?"

---

### 8. BODS Families Survey (Dec 2024)

| Attribute | Value |
|-----------|-------|
| **Location** | `DATA/1_SOURCE/historical_surveys/bods_families_dec2024/` |
| **Files** | Deliveroo Families - Data tables (1).xlsx, Deliveroo Families - Verbatim.xlsx |
| **What it is** | Broader Deliveroo families research |
| **Strengths** | Wider context, verbatim responses |
| **Limitations** | Not Dinneroo-specific |
| **Use for** | General family ordering context, triangulation

---

### 9. Additional External Sources

| Source | Location | Use For |
|--------|----------|---------|
| YouGov Moments | `DATA/1_SOURCE/external/YouGov Moments.png` | Market context |
| Medallia Restaurant | `DATA/1_SOURCE/external/Medallia. Mission - Restaurant.*` | Restaurant mission data |
| Joe Dinneroo Analysis | `DATA/1_SOURCE/external/Joe Dinneroo Analysis.txt` | Internal analysis context |
| Deliveroo Families Verbatim | `DATA/1_SOURCE/surveys/Deliveroo Families dec 24 - Verbatim.xlsx` | Additional verbatim responses |

---

## Snowflake Data (CAN REFRESH)

These can be pulled fresh from Snowflake.

### Orders Data
| File | Description | Refresh |
|------|-------------|---------|
| `ALL_DINNEROO_ORDERS.csv` | All Dinneroo orders | Weekly |
| `FULL_ORDER_HISTORY.csv` | Full history for survey respondents | As needed |

**Key for dish analysis:**
- `MENU_ITEM_LIST` - actual dishes ordered
- `RESTAURANT_NAME` - partner
- `MENU_CATEGORY` - cuisine
- `ZONE_NAME` - zone

### Ratings Data
| File | Description | Coverage |
|------|-------------|----------|
| `DINNEROO_RATINGS.csv` | Star ratings + comments | ~40% of orders |

**Key for dish analysis:**
- `RATING_COMMENT` - open-text feedback about dishes

### Catalog Data
| File | Description |
|------|-------------|
| `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` | Partners per zone |
| `DINNEROO_DISH_COUNTS_BY_ZONE.csv` | Dish counts per zone |
| `DINNEROO_DISH_COUNTS_BY_PARTNER.csv` | Dish counts per partner |
| `DINNEROO_MENU_CATALOG.csv` | Full menu items |

### Customer Data
| File | Description |
|------|-------------|
| `ALL_DINNEROO_CUSTOMERS.csv` | All Dinneroo customers |

---

## Data Source Selection Guidelines

### For MVP Zone Definition

**Primary signals:**
- Snowflake orders (what's actually ordered in successful zones)
- Partner catalog (what's available)
- Zone performance metrics

**Supporting signals:**
- Post-order survey (satisfaction by zone)
- Dropoff survey (what's missing)

### For Dish Recommendations

**Primary signals:**
- Snowflake orders (revealed preference - what people actually buy)
- Post-order survey open-text (unprompted dish feedback)
- Customer transcripts (unprompted dish mentions)

**Supporting signals:**
- Ratings comments
- Dropoff survey (unmet demand)

**⚠️ DO NOT USE:** OG Survey dish rankings

### For Family-Friendly Presentation

**Primary signals:**
- Post-order survey (family segment feedback)
- Customer transcripts (family interviews)
- WBRs (partner execution capabilities)

**Supporting signals:**
- Dropoff survey (family barriers)

---

## Discovering New Dishes/Cuisines

The goal is to find opportunities BEYOND what the OG survey asked about.

### ⚠️ CRITICAL: Survivorship Bias Warning

**Order volume shows what works among AVAILABLE options, not what families actually WANT.**

This is a fundamental limitation of behavioral data:
- People don't order dishes that aren't offered
- People don't ask for things they don't expect on delivery
- Top performers are top performers OF WHAT WE HAVE

**Always analyze LATENT DEMAND alongside order volume.**

### Sources for Discovery

1. **Snowflake MENU_ITEM_LIST** - What dishes are actually being ordered that we didn't ask about?

2. **Open-text fields (CRITICAL FOR LATENT DEMAND)** - What dishes do customers mention wanting?
   - Post-order: `DISH_IMPROVEMENTS`, `SUGGESTED_IMPROVEMENTS`
   - Dropoff: `What dishes and cuisines would you like to see more of?`
   - Dropoff: `What kid-friendly options would you like to see?`
   - Ratings: `RATING_COMMENT`

3. **Transcripts** - What dishes/cuisines come up organically in interviews?

4. **Competitive research** - What does Doordash offer for families?

### Latent Demand Categories (from Jan 2026 analysis)

| Category | Open-text Mentions | Status |
|----------|-------------------|--------|
| Vegetarian family options | 87 | Major gap - families excluded |
| Mild/plain kids options | 48 | Major gap - picky eaters excluded |
| Chinese family meals | 25 | Underrepresented vs cultural expectation |
| Lasagne/comfort pasta | 22 | "Home food" gap |
| Halal options | 12 | Dietary inclusion gap |
| Fish & Chips | 7 | British staple, zero availability |
| Caribbean | 5 | Zero availability |

### LLM Task: Extract Dish Mentions

```
Analyze these open-text responses and interview transcripts.
Extract ALL mentions of:
- Specific dishes (by name)
- Cuisine types
- Food categories
- Meal occasions

Include dishes that are:
- Currently offered and liked
- Currently offered and disliked
- NOT currently offered but requested
- Mentioned as alternatives to Dinneroo

Do NOT limit to any predefined list. Discover what customers actually talk about.

IMPORTANT: Pay special attention to:
- Things people say they WISH they could order
- Complaints about limited options for dietary needs
- References to what they cook at home or order elsewhere
- Kids' preferences that aren't being met
```

---

## For Family Meal Factors Analysis (Priority 100)

When running the Priority 100 Dishes analysis, use this mapping to extract evidence for each factor:

| Factor | Primary Source | Secondary Source | Key Metric |
|--------|---------------|------------------|------------|
| **Portion Flexibility** | Rating comments (`RATING_COMMENT`) | Dropoff open-text | 405 portion mentions |
| **Fussy Eater Friendly** | Dropoff survey open-text | Customer transcripts | 1,037 fussy eater mentions |
| **Customisation** | Dropoff survey (structured) | OG Survey | 125 selected "more options to customise" |
| **Balanced Nutrition** | OG Survey (Healthy ratings) | Rating comments | 12 dishes rated HIGH |
| **Value at £25** | Dropoff survey (structured) | Rating comments | 135 selected "discount/loyalty", 212 value mentions |
| **Shareability** | OG Survey (Shareable ratings) | - | 19 dishes rated HIGH |
| **Midweek Fit** | Business positioning doc | - | Core Dinneroo value proposition |
| **Vegetarian Option** | Dropoff + Rating comments | Transcripts | 41 + 32 vegetarian mentions |

### Factor Extraction Process

1. **Load structured data** (OG Survey) for Shareable, Customisable, Healthy ratings
2. **Analyze open-text** (Dropoff, Ratings, Post-Order) for factor-related mentions
3. **Scan transcripts** (88 interviews) for family meal decision factors
4. **Synthesize** into the Family Meal Factors Framework

### Key Files for Factor Extraction

| Factor Type | Files |
|-------------|-------|
| Structured ratings | `og_survey/Families - Master Survey Data - Dishes Ranking.csv` |
| Dropoff barriers | `surveys/dropoff_LATEST.csv` |
| Rating feedback | `snowflake/DINNEROO_RATINGS.csv` |
| Post-order feedback | `surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv` |
| Qualitative depth | `qual_research/transcripts/customer_interviews/*.docx` |

See `DOCUMENTATION/SHARED/06_PRIORITY_100_METHODOLOGY.md` for the complete methodology.

---

## Menu Gap Analysis Methodology

### ⚠️ CRITICAL: Dinneroo Menu vs Regular Deliveroo

When identifying menu gaps, you MUST distinguish between:

1. **Dinneroo menu items** - Items specifically available in the Dinneroo/Family offering
2. **Regular Deliveroo items** - Items the same partner serves on regular Deliveroo

**The same partner may serve DIFFERENT items on Dinneroo vs regular Deliveroo.**

### How to Check Menu Availability

**Source:** `DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv`

This file contains ALL items currently available on Dinneroo menus. Use `ITEM_NAME` column.

```python
# Correct way to check if a dish is on Dinneroo
menu = pd.read_csv('DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv')
is_on_dinneroo = menu['ITEM_NAME'].str.contains('biryani', case=False).any()
```

### Common Mistakes to Avoid

❌ **WRONG:** "Dishoom serves biryani, so biryani is on Dinneroo"
- Dishoom may serve biryani on regular Deliveroo but not on their Dinneroo menu

❌ **WRONG:** "We have 500 orders containing 'satay', so satay is available"
- Those orders may be from regular Deliveroo, not Dinneroo

✅ **CORRECT:** Check `DINNEROO_MENU_CATALOG.csv` for actual Dinneroo menu items

### Verified Menu Status (Jan 2026)

**ON Dinneroo Menu:**
| Dish | Menu Items | Partners |
|------|------------|----------|
| Katsu | 253 | Wagamama, Banana Tree, Zumuku |
| Curry | 316 | Asia Villa, Giggling Squid, Tiffin Tin |
| Pizza | 175 | PizzaExpress, Milano |
| Pasta | 185 | PizzaExpress, Milano |
| Pho | 46 | Pho |
| Shawarma | 128 | Yacob's Kitchen, Bill's |
| Rice Bowl | 80 | Banana Tree, Zumuku |
| Biryani | 16 | Dishoom, Chaska, Tadka House |

**NOT on Dinneroo Menu (Genuine Gaps):**
- Korma, Karahi, Paratha (Indian comfort)
- Satay, Laksa, Rendang (Southeast Asian)
- Ramen (Japanese)
- Kebab, Hummus (Middle Eastern)
- Jerk, Jollof, Plantain (Caribbean)
- Burger, Wings (Western comfort)

---

## Complete Data Inventory

### ✅ All Research Data Copied to NEW_PROJECT

| Category | Files | Location |
|----------|-------|----------|
| **Surveys** | Post-order (consolidated), Dropoff (latest + consolidated), Deliveroo Families Verbatim | `DATA/1_SOURCE/surveys/` |
| **OG Survey** | 13 files (Dishes Ranking, Scorecard, Demographics, etc.) | `DATA/1_SOURCE/historical_surveys/og_survey/` |
| **BODS Families** | Data tables + Verbatim | `DATA/1_SOURCE/historical_surveys/bods_families_dec2024/` |
| **Transcripts** | 88 customer interviews (Cycles 2-13) | `DATA/1_SOURCE/qual_research/transcripts/customer_interviews/` |
| **Pascal Reports** | Cycle 19 Report | `DATA/1_SOURCE/qual_research/pascal_reports/` |
| **WBRs** | 10 weekly reviews (W6-W15) | `DATA/1_SOURCE/external/WBRs/` |
| **Bounce Survey** | Wave 1 results | `DATA/1_SOURCE/external/` |
| **Pulse Survey** | Nov 2025 loyalty data | `DATA/1_SOURCE/external/` |
| **External** | YouGov, Medallia, Joe Analysis, Doordash | `DATA/1_SOURCE/external/` |

### Snowflake Data (To Be Refreshed)
- Orders, Customers, Ratings, Catalogs - pull fresh via Data Agent

---

*This inventory is for reference. Weight decisions should be made per analysis and documented.*

