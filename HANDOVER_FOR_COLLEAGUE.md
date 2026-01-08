# Dinneroo Zone Analysis - Handover Document

**Date:** January 2026  
**Purpose:** Enable colleague to continue analysis and write reports  
**Note:** This document is designed to be self-contained - all framework decisions and definitions are explained here so you don't need to ask questions.

---

## 🟢 STATE OF THE WORK - WHAT'S DONE

**The analytical work is complete and rigorous.** The challenge is packaging and presenting it effectively. Here's what you're inheriting:

### ✅ COMPLETED & VALIDATED

| Component | Status | Evidence |
|-----------|--------|----------|
| **Scoring Framework (v3.3)** | ✅ Complete | Multi-list approach: Family, Couple, Recruitment |
| **Dish Taxonomy (Anna's 24)** | ✅ Complete | 155 items → 58 granular → 24 high-level types |
| **MVP Zone Thresholds** | ✅ Complete | Data-driven inflection points + business targets |
| **155 Menu Items** | ✅ Curated | Anna's ground truth taxonomy |
| **41 Partners, 756 Sites** | ✅ Mapped | Full coverage by zone |
| **201 Live Zones Analyzed** | ✅ Complete | MVP status calculated for all |
| **Latent Demand Analysis** | ✅ Complete | 2,796 open-text responses mined |
| **Three-List Rankings** | ✅ Complete | Family, Couple, Recruitment priorities |
| **Data Pipeline** | ✅ Working | `run_pipeline.py` orchestrates all phases |
| **Interactive Dashboard** | ✅ Built | `dinneroo_master_dashboard.html` |

### 📊 KEY NUMBERS YOU CAN TRUST

| Metric | Value | Source | Confidence |
|--------|-------|--------|------------|
| Total menu items | 155 | Anna's taxonomy | 🟢 Ground truth |
| High-level dish types | 24 | Anna's taxonomy | 🟢 Ground truth |
| Granular dish types | 58 | Anna's taxonomy | 🟢 Ground truth |
| Total partners | 41 | Anna's spreadsheet | 🟢 Ground truth |
| Total sites | 756 | Anna's spreadsheet | 🟢 Ground truth |
| Zones with supply | 434 | Anna's spreadsheet | 🟢 Ground truth |
| Zones with orders | 201 | Snowflake | 🟢 Behavioral |
| Core 7 cuisines | 7 | Framework | 🟢 Validated |
| Post-order responses | ~1,500 | Survey | 🟢 Primary |
| Dropoff responses | ~800 | Survey | 🟢 Primary |
| Customer interviews | 88 | Transcripts | 🟢 Primary |

### 🔬 METHODOLOGY RIGOR

The frameworks aren't arbitrary - they're evidence-based:

| Decision | How It Was Validated |
|----------|---------------------|
| **Three-list approach (v3.3)** | Families and couples have different needs - one ranking doesn't fit all |
| **Anna's 24-dish taxonomy** | Ground truth alignment - all rankings use authoritative dish types |
| **Family weights (kids_happy 40%)** | Kids' reaction is primary driver for family repeat orders |
| **Couple weights (adult_satisfaction 40%)** | Adult satisfaction is primary driver for couples |
| **Percentile-based scoring** | Natural 1-5 distribution, avoids compressed ranges |
| **MVP cuisine threshold (5 of 7)** | Data inflection at 3+, business target at 5 for redundancy |
| **Orders per zone metric** | Normalizes for supply - a dish in 10 zones with 1000 orders beats a dish in 100 zones with 5000 orders |
| **Non-Dinneroo filtering** | 98% of Dinneroo orders are Mon-Thu dinner - unfiltered comparison is apples-to-oranges |

### 📁 WHAT'S READY TO USE

| Deliverable | Location | Status |
|-------------|----------|--------|
| **Dish Rankings (Combined)** | `DELIVERABLES/reports/DISH_RANKINGS_WITH_ROLLUP.csv` | ✅ Ready |
| **Family Performers** | `DELIVERABLES/reports/DISH_FAMILY_RANKINGS.csv` | ✅ Ready |
| **Couple Performers** | `DELIVERABLES/reports/DISH_COUPLE_RANKINGS.csv` | ✅ Ready |
| **Recruitment Priorities** | `DELIVERABLES/reports/DISH_RECRUITMENT_PRIORITIES.csv` | ✅ Ready |
| **Dish Taxonomy (155 items)** | `config/dish_taxonomy.csv` | ✅ Ready |
| Zone MVP status | `docs/data/zone_mvp_status.json` | Ready |
| Cuisine scores | `DATA/3_ANALYSIS/cuisine_scores.csv` | Ready |
| Latent demand signals | `DATA/3_ANALYSIS/latent_demand_scores.csv` | Ready |
| Partner coverage | `DATA/3_ANALYSIS/anna_partner_coverage.csv` | Ready |
| Zone gap report | `DATA/3_ANALYSIS/zone_gap_report.csv` | Ready |
| Interactive dashboard | `DELIVERABLES/dashboards/dinneroo_master_dashboard.html` | Ready |
| Handover Package | `HANDOVER_PACKAGE/` | ✅ Ready |

### 🎯 THE CHALLENGE: SHOWCASING THE WORK

The analysis is solid. What needs attention is **packaging for stakeholders**:

1. **Dashboard polish** - Data is there, visualization could be refined
2. **Narrative flow** - Connecting findings into a compelling story
3. **Slide-ready outputs** - Turning analysis into presentation format
4. **Executive summary** - Distilling insights for leadership

**Bottom line:** You're not rebuilding analysis. You're presenting complete work effectively.

---

## What Is This Project?

**Dinneroo** is Deliveroo's £25 family meal proposition - fixed-price bundles designed for midweek family dinners (Mon-Thu, 5-7pm).

This project analyzes Dinneroo zones to:
1. **Define MVP zone requirements** - What makes a zone "ready" for launch?
2. **Prioritize dishes** - Which dish types should we focus on?
3. **Understand family behavior** - What do families actually want?

---

## How to Work: The Agent System

Before doing ANY analysis, **read the relevant agent brief** in `DOCUMENTATION/AGENTS/`.

### Agent Routing Table

| What You're Analyzing | Agent Brief to Read |
|----------------------|---------------------|
| Scoring weights, framework validation | `SCORING_AGENT.md` |
| Dish prioritization, performance | `01_DISH_AGENT.md` |
| Zone MVP status, coverage | `ZONE_AGENT.md` |
| Cuisine rankings, Core 7 | `CUISINE_GAP_AGENT.md` |
| Missing dishes within cuisines | `DISH_GAP_AGENT.md` |
| Partner recruitment | `PARTNER_AGENT.md` |
| Family eating patterns, segments | `FAMILY_BEHAVIOR_AGENT.md` |
| Unmet demand from open-text | `LATENT_DEMAND_AGENT.md` |
| Data refresh, validation | `DATA_AGENT.md` |
| Dashboards, charts | `DASHBOARD_AGENT.md` |
| Quality review before sharing | `FEEDBACK_AGENT.md` |

**Example:** If asked "Which cuisines should we prioritize?" → read `CUISINE_GAP_AGENT.md` first.

---

## THE SCORING FRAMEWORK - FULL EXPLANATION

**Location:** `config/scoring_framework_v3.json`  
**Version:** 3.1 (January 2026)  
**Detailed rationale:** `DELIVERABLES/reports/weight_rationale.md`

### Why We Use a Two-Track System

**The Problem:** A single blended score creates survivorship bias. If we only score dishes based on performance data (orders, ratings), unavailable dishes automatically score poorly - not because families don't want them, but because they CAN'T order them.

**The Solution:** Separate **Performance** (supply-side success) from **Demand** (demand-side signal - proven and latent).

### Track Weights: Why 60/40?

| Track | Weight | Rationale |
|-------|--------|-----------|
| **Performance** | 60% | Behavioral data (actual orders) is a stronger signal than stated preference |
| **Demand** | 40% | Still significant weight because demand sources capture unmet needs (latent + proven) |

**Why not 50/50?** We tested different splits. At 70/30 we over-index on existing winners (survivorship bias). At 30/70 we over-index on unproven demand signals. 60/40 balances proven success with growth potential.

---

### PERFORMANCE TRACK (60% Total) - What Each Factor Means

#### 1. Orders per Zone (35% of total)

**What it is:** `total_orders ÷ zones_where_item_is_available`

**Why this calculation:** Raw order volume biases toward widely available items. A dish in 100 zones with 5,000 orders looks better than a dish in 10 zones with 1,000 orders - but the second is actually more efficient (100 orders/zone vs 50 orders/zone).

**Why 35% weight:** This is the primary performance signal. It normalizes for supply so we don't just reward items that are everywhere.

**Scoring thresholds:**
- Score 5: ≥100 orders/zone (top 10%)
- Score 4: 50-99 orders/zone (top 25%)
- Score 3: 20-49 orders/zone (top 50%)
- Score 2: 5-19 orders/zone (bottom 50%)
- Score 1: <5 orders/zone (bottom 25%)

**Data source:** Snowflake orders

---

#### 2. Rating (15% of total)

**What it is:** Average Deliveroo star rating

**Why this exists:** Direct quality signal from customers. Higher ratings correlate with repeat orders.

**Why 15% weight:** Important but secondary to volume. A dish could have high ratings but low orders (niche appeal).

**Scoring thresholds:**
- Score 5: 4.5+ stars
- Score 4: 4.3-4.49 stars
- Score 3: 4.0-4.29 stars
- Score 2: 3.5-3.99 stars
- Score 1: <3.5 stars

**Data source:** Snowflake ratings

---

#### 3. Kids Happy (10% of total)

**What it is:** % of families responding "Full and happy" to "How did your child(ren) react to the meal?"

**Why this exists:** Dinneroo is a FAMILY proposition. Kids not eating the meal = parents won't reorder. This is the #1 success factor.

**Why 10% weight:** Critical signal but limited sample sizes in post-order survey reduce reliability.

**Scoring thresholds:**
- Score 5: 85%+ kids happy
- Score 4: 75-84% kids happy
- Score 3: 65-74% kids happy
- Score 2: 55-64% kids happy
- Score 1: <55% kids happy

**Data source:** Post-order survey, question "How did your child(ren) react to the meal?"

---

### OPPORTUNITY TRACK (40% Total) - What Each Factor Means

#### 4. Latent Demand (20% of total)

**What it is:** Combined score from open-text mentions + wishlist %

**Why this exists:** Captures what families WANT but can't currently get. Without this, we'd only optimize for existing dishes (survivorship bias).

**Why 20% weight:** High weight because this directly addresses "what are we missing?"

**How it's calculated (sub-components):**
- Open-text mentions: 45% - Direct expression of unmet demand
- OG Survey wishlist: 30% - Pre-launch stated preference
- Barrier signals: 25% - Implicit demand from dropoff reasons

**Scoring thresholds:**
- Score 5: 20+ mentions OR 15%+ wishlist
- Score 4: 10-19 mentions OR 10-14% wishlist
- Score 3: 5-9 mentions OR 5-9% wishlist
- Score 2: 2-4 mentions
- Score 1: 0-1 mentions

**Data sources:** Dropoff survey open-text, Post-order survey open-text, Rating comments, OG Survey wishlist

---

#### 5. Non-Dinneroo Demand (20% of total)

**What it is:** Orders outside Dinneroo, filtered to Mon-Thu 16:30-21:00 ONLY

**Why this filter is CRITICAL:** Dinneroo is 98% midweek dinner orders. Unfiltered non-Dinneroo orders include weekend "treat" meals (61% of volume), late-night takeaways, and lunch orders - completely different occasions. Comparing filtered demand validates that demand exists during Dinneroo's actual use case.

**Why 20% weight:** Strong behavioral signal that doesn't rely on stated preference.

**Scoring thresholds:**
- Score 5: Top 10% of midweek evening orders
- Score 4: Top 25%
- Score 3: Top 50%
- Score 2: Bottom 50%
- Score 1: Bottom 25%

**Data source:** Snowflake - non-Dinneroo orders, filtered

---

### FACTORS WE REMOVED (And Why)

These were in earlier versions but dropped because they didn't differentiate rankings:

| Factor | Previous Weight | Why Removed |
|--------|-----------------|-------------|
| **Zone Ranking Strength** | 15% | Penalized dishes with limited availability. Pho scored 1/5 despite 323 orders/zone because it's only in 14 zones. Unfair. |
| **Adult Appeal** | 10.25% | Only 13 dishes had survey-backed scores. The rest defaulted to 3 (neutral). When most dishes score 3, the factor doesn't differentiate. |
| **Balanced/Guilt-Free** | 9.25% | Same problem - mostly estimated scores, not measured. |
| **Fussy Eater Friendly** | 5.5% | Weight too small to impact rankings meaningfully. |
| **Supply Gap Severity** | N/A | Was inflating demand scores for unavailable items artificially. |

**Key insight:** Until we have measured data for fit factors (via direct survey questions), they add complexity without value.

---

### Quadrant Classification - What Each Means

| Quadrant | Criteria | What It Means | Action |
|----------|----------|---------------|--------|
| **Core Drivers** | Performance ≥3.0 AND Demand ≥3.0 | WIN - We're capturing proven demand | Protect and expand to more zones |
| **Preference Drivers** | Performance <3.0 AND Demand ≥3.0 | GAP - Demand exists but we're not capturing it | Investigate why |
| **Demand Boosters** | Performance ≥3.0 AND Demand <3.0 | NICHE - We're good but limited market | Maintain efficiency |
| **Deprioritised** | Performance <3.0 AND Demand <3.0 | AVOID - Neither working nor wanted | Don't invest resources |

---

### Tier Classification (For Priority Lists)

| Tier | Label | Threshold | Action |
|------|-------|-----------|--------|
| Tier 1 | Must-Have | Unified Score ≥3.5 | Essential for every zone |
| Tier 2 | Should-Have | Unified Score ≥3.0 | Important for zone strength |
| Tier 3 | Nice-to-Have | Unified Score ≥2.5 | Good for variety |
| Tier 4 | Monitor | Unified Score <2.5 | Review or deprioritize |

**Why 3.5 threshold for Tier 1?** With a 60/40 split and demand scores typically 1.5-4.0, even perfect performance (5.0) yields ~4.0-4.6 unified depending on demand. The old 3.8 threshold is now achievable.

---

## MVP ZONE THRESHOLDS - FULL EXPLANATION

**Location:** `config/mvp_thresholds.json`

### Business Targets vs Data Inflection Points

There are TWO sets of numbers - don't confuse them:

| Metric | Business Target | Data Inflection Point | Difference |
|--------|-----------------|----------------------|------------|
| **Cuisines** | 5 of 7 | 3+ | Business wants redundancy |
| **Partners** | 5 | 3+ | Business wants choice |
| **Dishes** | 21 | N/A | 3 dishes × 7 cuisines |
| **Rating** | 4.0 | 4.2 benchmark | Floor, not ceiling |
| **Repeat Rate** | 35% | 35%+ top zones at 40% | Floor, not ceiling |

**What's the difference?**
- **Data inflection points** = where metrics actually improve (e.g., repeat rate jumps +4.5pp when zones have 3+ partners)
- **Business targets** = higher thresholds for launch confidence (redundancy, reliability)

**Source:** Data inflection points are in `DATA/3_ANALYSIS/mvp_threshold_discovery.json`

---

### Core 7 Cuisines - Why These 7?

| Cuisine | Why It's Core |
|---------|---------------|
| **Asian** | Highest performance scores, universal family appeal (Japanese, Thai, Vietnamese, Chinese, Korean) |
| **Italian** | Comfort food, kid-friendly, high repeat orders (pizza, pasta) |
| **Indian** | Strong demand, family sharing format (curries, biryanis) |
| **Healthy** | Aligns with "balanced midweek meal" positioning (grain bowls, salads) |
| **Mexican** | Build-your-own format is fussy-eater-friendly (fajitas, burritos) |
| **Middle Eastern** | High ratings, grilled protein fits positioning (shawarma, kebabs) |
| **British** | Cultural expectation, latent demand signals (fish & chips, pies) |

**5 of 7 = MVP Ready because:** Families have diverse preferences. With 5+ cuisines, there's something for everyone. Missing 2 is acceptable; missing 3+ creates exclusion risk.

---

### MVP Status Tiers - Why These Cutoffs?

| Status | Cuisine Count | Why This Cutoff |
|--------|---------------|-----------------|
| **MVP Ready** | 5+ of 7 | North star - full family offering |
| **Near MVP** | 4 of 7 | One gap away - prioritize for quick wins |
| **Progressing** | 3 of 7 | Data shows metrics improve at 3+ cuisines (inflection point) |
| **Developing** | 1-2 of 7 | Early stage - needs significant investment |
| **Supply Only** | 0 with orders | Has partners configured but no customer orders yet |
| **Not Started** | 0 | No Dinneroo partners in zone |

---

## KEY DEFINITIONS - WHAT EACH TERM MEANS

### Customer Segments

#### "Family" Definition
```python
Is_Family = (NUM_CHILDREN >= 1) OR (WHO_ORDERING contains 'family')
```
**Why this definition:** Captures both explicit family households AND people ordering for family occasions.

#### "Strong Advocate" Definition
All 3 must be true:
- `DISH_SENTIMENT` = "Loved it"
- `SATISFACTION` = "Very Satisfied"  
- `REORDER_NEWPARTNER` in ["Agree", "Strongly agree"]

**Why this definition:** Uses the HIGHEST bar for each metric. Identifies genuinely enthusiastic customers with platform loyalty (not just loyalty to one restaurant).

---

### Survey Response Mappings

#### Satisfaction Rate
**Definition:** % of respondents who are "Very Satisfied" OR "Satisfied"
```python
satisfied = df['SATISFACTION'].isin(['Very Satisfied', 'Satisfied'])
satisfaction_rate = satisfied.mean() * 100
```

#### Satisfaction Score (Numeric)
| Response | Score |
|----------|-------|
| Very Satisfied | 5 |
| Satisfied | 4 |
| Neutral | 3 |
| Dissatisfied | 2 |
| Very Dissatisfied | 1 |

#### "Loved It" Rate
**Definition:** % who selected "Loved it" (highest rating only, not "Liked it")
```python
loved_it_rate = (df['DISH_SENTIMENT'] == 'Loved it').mean() * 100
```

---

### Zone Counts - CRITICAL DISTINCTION

| Count | Value | What It Means | When to Use |
|-------|-------|---------------|-------------|
| **Total Zones** | 1,306 | All Deliveroo zones in UK/Ireland | Market size discussions |
| **Supply Zones** | 434 | Zones with Dinneroo partners configured | Expansion planning |
| **Live Zones** | 201 | Zones with actual Dinneroo orders during trial | Performance analysis |
| **Analysis Zones** | 197 | Live zones with sufficient data for stats | Statistical analysis |

**Why the gap?** The Dinneroo trial (Sep-Dec 2025) was limited to specific zones. The 234-zone gap (434-201) = partners are ready but zone wasn't activated for customers.

---

### "Dish Type" vs "Brand"

**THE CRITICAL REFRAME:** Think dish types, not brands.

| Instead of... | Think... |
|--------------|----------|
| "Should we recruit Nando's?" | "Do families want Grilled Chicken with Customizable Sides?" |
| "Should we get Dishoom?" | "Do families want Indian Curry & Sharing Platters?" |
| "Should we add Wagamama?" | "Do families want Asian Noodles & Rice Bowls?" |

**Why this matters:**
1. Brand-thinking limits options - if we think "Nando's" we miss that Pepe's Piri Piri serves the same need
2. Dish-type thinking expands recruitment options
3. Strategic clarity - focus on what families want to EAT, not commercial relationships

---

## EVIDENCE STANDARDS - HOW TO CITE PROPERLY

**Location:** `DOCUMENTATION/SHARED/04_QUALITY_STANDARDS.md`

### Evidence Levels

| Level | Symbol | Definition | Use For |
|-------|--------|------------|---------|
| **Single** | 🔵 | One data source only | Exploration, hypothesis generation |
| **Corroborated** | 🟡 | 2 independent sources | Working hypotheses, internal analysis |
| **Validated** | 🟢 | 3+ sources OR quant+qual | Strategic recommendations, stakeholder presentations |

### What CAN Count as Independent Sources

| Source A | Source B | ✓ Independent Because |
|----------|----------|----------------------|
| Post-Order Survey | Snowflake Orders | Survey vs behavioral data |
| Dropoff Survey | Post-Order Survey | Different populations |
| Any Quantitative | Any Qualitative | Different methods |
| Snowflake Orders | Transcripts | Behavioral vs exploratory |

### What CANNOT Count as Independent

| Source A | Source B | ✗ Not Independent Because |
|----------|----------|--------------------------|
| Two questions from same survey | Same survey | Same respondents |
| Post-Order + Dropoff (same metric) | Both surveys | Method overlap |

### Citation Template

Every claim MUST include:
1. **Source name** - Which data source
2. **Sample size** - n=X
3. **Segment** - If subset (e.g., "families only")
4. **Date** - When data was collected
5. **Caveats** - Relevant limitations

**Good:** "Zone A has 85% satisfaction (n=127, post-order survey, Dec 2025). Note: This represents customers who completed orders."

**Bad:** "Zone A has high satisfaction."

---

### Sample Size Minimums

| Sample Size | Reliability | Action |
|-------------|-------------|--------|
| n < 20 | ❌ Unreliable | Do not report |
| n = 20-50 | ⚠️ Directional | Report with caveat |
| n = 50-100 | ✓ Moderate | Report as finding |
| n > 100 | ✓✓ Strong | Report confidently |

### Statistical Claims

- Only use "significant" when you have a p-value (p < 0.05)
- "Meaningful difference" = practical importance, may not be tested
- "Notable" = worth mentioning, not necessarily tested

---

## DATA SOURCES - FULL INVENTORY

### The Data Hierarchy (MEMORIZE THIS)

| Question Type | Data Source | Why |
|---------------|-------------|-----|
| **What we HAVE** (supply) | Anna's CSVs | Ground truth of what's onboarded |
| **How it PERFORMS** (behavior) | Snowflake orders | Actual customer behavior |
| **What customers WANT** (preference) | Surveys + triangulation | Stated + revealed preference |

---

### SUPPLY DATA → Use Anna's Ground Truth

**Why not derive from orders?** Order data significantly UNDERSTATES availability:
- A partner could be onboarded but have zero orders yet
- A zone could have dishes available that haven't been ordered
- Order data shows what was purchased, not what's available

**Anna's data reconciliation (Jan 2026):**

| Metric | Order-Derived | Anna's Ground Truth | Understatement |
|--------|---------------|---------------------|----------------|
| Partners | ~25-30 | 40 | +33% |
| Sites | ~400 | 756 | +89% |
| Zones with dishes | ~200 | 434 | +117% |

**Files to use:**

| File | Content | Key Numbers |
|------|---------|-------------|
| `DATA/3_ANALYSIS/anna_family_dishes.csv` | Curated family dishes | 142 dishes |
| `DATA/3_ANALYSIS/anna_partner_coverage.csv` | Partner sites | 40 partners, 756 sites |
| `DATA/3_ANALYSIS/anna_zone_dish_counts.csv` | Zone availability | 1,306 zones tracked, 434 with supply |

**Source spreadsheet:** `DATA/1_SOURCE/anna_slides/Dish Analysis Dec-25.xlsx`

---

### PERFORMANCE DATA → Use Snowflake Orders

| File | What It Contains | Use For |
|------|------------------|---------|
| `DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv` | All Dinneroo orders | Volume analysis (100% coverage) |
| `DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv` | Star ratings + comments | Quality analysis (~40% of orders) |
| `DATA/1_SOURCE/snowflake/FULL_ORDER_HISTORY.csv` | Full history for survey respondents | Linking surveys to behavior |
| `DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv` | Actual menu items on Dinneroo | Availability verification |

**Key columns in orders data:**
- `MENU_ITEM_LIST` - actual dishes ordered
- `RESTAURANT_NAME` - partner
- `MENU_CATEGORY` - cuisine
- `ZONE_NAME` - zone

---

### PREFERENCE DATA → Use Surveys WITH Triangulation

#### Post-Order Survey (~1,500 responses)
**File:** `DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv`  
**Enriched:** `DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv`

**What it is:** Feedback from customers AFTER placing a Dinneroo order

**Strengths:** Actual customer experience, satisfaction data, open-text feedback  
**Limitations:** Only orderers (survivorship bias), may skew to extremes

**Use for:** Satisfaction by dish/partner, "what's working", kids happiness

**Key open-text fields for dish discovery:**
- `DISH_IMPROVEMENTS`
- `SUGGESTED_IMPROVEMENTS`

---

#### Dropoff Survey (~800 responses)
**File:** `DATA/1_SOURCE/surveys/dropoff_LATEST.csv`  
**Enriched:** `DATA/2_ENRICHED/DROPOFF_ENRICHED.csv`

**What it is:** Feedback from people who browsed but DIDN'T order

**Strengths:** Unmet demand, barriers, what people wanted but couldn't find  
**Limitations:** Self-selection, recall may be inaccurate

**Use for:** Discovering dishes/cuisines people wanted but we don't have

**⚠️ TWO SEGMENTS (different questions):**
- "Tried Before" - ordered at least once (retention challenge)
- "Never Tried" - never ordered (acquisition challenge)

**These segments were shown different questions. Analyze separately.**

---

#### Customer Interview Transcripts (88 interviews)
**Location:** `DATA/1_SOURCE/qual_research/transcripts/customer_interviews/`

**What it is:** Deep interviews with families (Cycles 2-13)

**Strengths:** Deep "why" context, verbatim quotes, unprompted dish mentions  
**Limitations:** Small sample, recruited participants

**⭐ HIGH VALUE FOR DISH DISCOVERY:** Contains unprompted mentions of dishes/cuisines that weren't in any survey.

---

#### ⚠️ OG Survey - USE WITH EXTREME CAUTION
**Location:** `DATA/1_SOURCE/historical_surveys/og_survey/`

**What it is:** Pre-launch survey asking about dish preferences and family behaviors (~400 responses)

**THE PROBLEM:** This survey was the main source of bias in the old project. It should be ONE input among many, NOT the primary driver.

**Why it's biased:**
1. Only asked about a LIMITED set of dishes
2. Captured STATED preference (what people SAY) not REVEALED preference (what they DO)
3. Was collected PRE-LAUNCH before anyone had tried Dinneroo

**USE FOR (with triangulation):**
- Demographic insights (family composition, ages)
- Decision-making patterns
- Customisation preferences

**NEVER USE ALONE FOR:**
- Dish recommendations
- Cuisine prioritization
- Demand signals

**ALWAYS ASK:** "Does the behavioral data (Snowflake orders) support this?"

---

### OTHER DATA SOURCES

| Source | Location | Use For |
|--------|----------|---------|
| Bounce Survey | `DATA/1_SOURCE/external/Bounce Survey Results*.xlsx` | Barrier data |
| Pulse Survey | `DATA/1_SOURCE/external/Pulse_Survey_Loyalty_Nov2025.csv` | Loyalty/frequency |
| WBRs (Weekly Business Reviews) | `DATA/1_SOURCE/external/WBRs/` | Partner execution context |
| BODS Families Survey | `DATA/1_SOURCE/historical_surveys/bods_families_dec2024/` | Broader family context |

---

## CRITICAL RULES - THE NON-NEGOTIABLES

### 1. Survivorship Bias - THE BIGGEST TRAP

**The problem:** Order volume shows what works among AVAILABLE options, not what families WANT.

**Evidence of latent demand (from open-text analysis, n=2,796):**

| Unmet Need | Mentions | Status |
|------------|----------|--------|
| Vegetarian family options | 87 | Major gap - families excluded |
| Mild/plain kids options | 48 | Major gap - picky eaters excluded |
| Chinese cuisine | 25 | Underrepresented vs cultural expectation |
| Lasagne/comfort pasta | 22 | "Home food" gap |
| Halal options | 12 | Religious dietary needs unmet |
| Fish & Chips | 7 | British staple, zero availability |
| Caribbean | 5 | Zero availability |

**Required action:** For ANY dish prioritization, analyze latent demand from open-text alongside order data. Don't just optimize for what's already there.

---

### 2. Non-Dinneroo Benchmark Filtering - MANDATORY

**The problem:** Dinneroo is 98% midweek orders (Mon-Thu, 5-7pm dinner). Unfiltered non-Dinneroo orders include:
- Weekend "treat" orders (61% of non-Dinneroo volume)
- Late-night takeaways
- Lunch orders
- Grocery/alcohol

Using unfiltered data creates apples-to-oranges comparisons.

**Required filter for non-Dinneroo benchmarks:**
```sql
WHERE ORDER_DAY IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday')
  AND ORDER_TIME BETWEEN '16:30' AND '21:00'
  AND IS_DINNEROO = False
```

**Files:**
- ✅ USE: `DATA/3_ANALYSIS/non_dinneroo_cuisine_demand_midweek.csv` (filtered)
- ❌ DON'T USE: `DATA/3_ANALYSIS/non_dinneroo_cuisine_demand.csv` (unfiltered)

**Filter impact:** Only 26.5% of non-Dinneroo orders are retained. This significantly changes cuisine rankings.

---

### 3. Menu Availability Verification - CHECK THE CATALOG

**The trap:** Assuming a partner serves something on Dinneroo because they serve it on regular Deliveroo.

**Example:** Dishoom serves biryani on regular Deliveroo. That does NOT mean biryani is on their Dinneroo menu.

**How to verify:**
```python
menu = pd.read_csv('DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv')
is_on_dinneroo = menu['ITEM_NAME'].str.contains('biryani', case=False).any()
```

---

### 4. Zone Counts - ALWAYS SPECIFY WHICH

| Count | Value | When to Use |
|-------|-------|-------------|
| **1,306** | Total UK/Ireland zones | Market size |
| **434** | Zones with supply | Expansion planning |
| **201** | Zones with orders | Performance analysis |

**Never say "201 zones" in one breath and "1,306 zones" in another without specifying which.**

---

### 5. MVP Status - DON'T RECALCULATE

**Use established calculations from:** `docs/data/zone_mvp_status.json`

This file contains the official MVP status for all 201 live zones. Don't recalculate from scratch.

---

### 6. Triangulation Rules

| Claim Type | Minimum Evidence |
|------------|------------------|
| Exploratory finding | 🔵 Single source OK |
| Internal recommendation | 🟡 2 independent sources |
| Strategic recommendation | 🟢 3+ sources required |
| Dashboard headline | 🟢 3+ sources required |

**Never weight any single source > 50%**

---

## RUNNING THE ANALYSIS

### Pipeline Commands

```bash
# Full pipeline (data → analysis → synthesis)
python scripts/run_pipeline.py --all

# Specific phases
python scripts/run_pipeline.py --phase 1    # Data preparation
python scripts/run_pipeline.py --phase 2    # Analysis  
python scripts/run_pipeline.py --phase 3    # Synthesis

# Just update dashboards
python scripts/run_pipeline.py --dashboards

# See all available scripts
python scripts/run_pipeline.py --list
```

### Dashboard Regeneration

```bash
# Step 1: Validate data quality
python3 scripts/validate_data_quality.py

# Step 2: Prepare dashboard data (aggregates all outputs)
python3 scripts/prepare_dashboard_data.py

# Step 3: Generate dashboard (embeds data into HTML)
python3 scripts/generate_dashboard.py
```

---

## KEY OUTPUT FILES

### Analysis Outputs (DATA/3_ANALYSIS/)
| File | What It Contains |
|------|------------------|
| `priority_100_dishes.csv` | Ranked dish list with scores |
| `cuisine_scores.csv` | Cuisine rankings using two-track framework |
| `zone_gap_report.csv` | Zone-level gaps and opportunities |
| `latent_demand_scores.csv` | Unmet demand signals from open-text |
| `dish_composite_scores.csv` | Full dish scoring breakdown |
| `anna_family_dishes.csv` | Anna's curated 142 family dishes |
| `anna_partner_coverage.csv` | Partner site coverage |
| `anna_zone_dish_counts.csv` | Zone-level supply data |
| `mvp_threshold_discovery.json` | Data-driven inflection points |
| `non_dinneroo_cuisine_demand_midweek.csv` | Filtered benchmark data |

### Dashboards
| Location | What It Contains |
|----------|------------------|
| `docs/index.html` | Landing page |
| `DELIVERABLES/dashboards/dinneroo_master_dashboard.html` | Master dashboard |
| `docs/dashboards/zone_analysis.html` | Zone-specific analysis |

### Reports (DELIVERABLES/reports/)
| File | What It Contains |
|------|------------------|
| `MASTER_ANALYSIS_REPORT.md` | Full analysis summary |
| `mvp_zone_report_product_director.md` | MVP zone summary for stakeholders |
| `dish_prioritization_2026-01-05.md` | Dish priority recommendations |
| `weight_rationale.md` | Why each scoring weight was chosen |
| `SCORING_FRAMEWORK_CHANGES_v3.md` | Framework change log |
| `factor_validation_analysis.md` | Factor correlation analysis |

### Config Files (config/)
| File | What It Controls |
|------|------------------|
| `scoring_framework_v3.json` | **THE** scoring framework - read this |
| `mvp_thresholds.json` | MVP zone criteria |
| `cuisine_hierarchy.json` | Core 7 → sub-cuisine mapping |
| `dish_types_master.json` | Official dish type list |
| `evidence_standards.json` | Sample size requirements |

---

## BEFORE YOU REPORT ANYTHING - CHECKLIST

### Anti-Drift Verification
- [ ] Did I read the relevant agent brief in `DOCUMENTATION/AGENTS/`?
- [ ] Did I cite sources with sample sizes?
- [ ] Is this from fresh analysis, not assumptions from old project?
- [ ] Does this answer the stated question?
- [ ] Have I used Anna's data for supply metrics?
- [ ] Have I used Snowflake for performance metrics?
- [ ] Have I triangulated for any strategic recommendations?
- [ ] Have I filtered non-Dinneroo benchmarks to midweek evening?
- [ ] Have I specified which zone count I'm using?

### Red Flags That Suggest Drift
- Finding matches old project conclusions exactly
- Specific percentages appear without fresh calculation
- Partner/dish names appear as "winners" without analysis
- Conclusions written before data is loaded
- Examples from briefs copied as findings

---

## QUICK REFERENCE - FILE PATHS

### Documentation
| Resource | Path |
|----------|------|
| Agent briefs | `DOCUMENTATION/AGENTS/` |
| Agent index | `DOCUMENTATION/AGENTS/INDEX.md` |
| Shared context | `DOCUMENTATION/SHARED/` |
| Data sources inventory | `DOCUMENTATION/SHARED/05_DATA_SOURCES_INVENTORY.md` |
| Quality standards | `DOCUMENTATION/SHARED/04_QUALITY_STANDARDS.md` |
| Definitions & calculations | `DOCUMENTATION/SHARED/03_DEFINITIONS.md` |
| Ground truth explanation | `DOCUMENTATION/CONTEXT/08_GROUND_TRUTH_DATA.md` |
| Dish scoring methodology | `DOCUMENTATION/METHODOLOGY/01_DISH_SCORING.md` |
| Zone MVP methodology | `DOCUMENTATION/METHODOLOGY/02_ZONE_MVP.md` |

### Config
| Resource | Path |
|----------|------|
| Scoring framework (v3.1) | `config/scoring_framework_v3.json` |
| MVP thresholds | `config/mvp_thresholds.json` |
| Cuisine hierarchy | `config/cuisine_hierarchy.json` |
| Dashboard metrics | `config/dashboard_metrics.json` |

### Key Data
| Resource | Path |
|----------|------|
| Zone MVP status (DON'T RECALCULATE) | `docs/data/zone_mvp_status.json` |
| MVP inflection analysis | `DATA/3_ANALYSIS/mvp_threshold_discovery.json` |
| Anna's source spreadsheet | `DATA/1_SOURCE/anna_slides/Dish Analysis Dec-25.xlsx` |

### Scripts
| What You Need | Path |
|---------------|------|
| Run full pipeline | `scripts/run_pipeline.py` |
| Validate data quality | `scripts/validate_data_quality.py` |
| Generate dashboard | `scripts/generate_dashboard.py` |
| Shared definitions (Python) | `scripts/utils/definitions.py` |

---

## GETTING STARTED

1. **Read this document thoroughly** - especially the scoring framework and critical rules sections
2. **Browse the agent briefs** at `DOCUMENTATION/AGENTS/INDEX.md` - find the right agent for your task
3. **Check existing analysis** in `DATA/3_ANALYSIS/` - don't recreate what exists
4. **View the dashboards** by opening `docs/index.html` in a browser
5. **Run the pipeline** with `python scripts/run_pipeline.py --list` to see options

---

## GLOSSARY

| Term | Definition |
|------|------------|
| **Core 7** | The 7 cuisine categories: Asian, Italian, Indian, Healthy, Mexican, Middle Eastern, British |
| **MVP Ready** | Zone has 5+ Core 7 cuisines |
| **Latent Demand** | What customers want but can't currently get (from open-text) |
| **Survivorship Bias** | Analyzing only what exists, missing what's wanted but unavailable |
| **Ground Truth** | Anna's curated spreadsheet - authoritative source for supply data |
| **Triangulation** | Using multiple independent sources to validate a finding |
| **Validated Finding** | 🟢 Evidence from 3+ independent sources |
| **Performance Track** | 60% of score - based on behavioral data (orders, ratings) |
| **Demand Track** | 40% of score - based on demand signals (latent + proven non-Dinneroo) |
| **Orders per Zone** | Total orders ÷ zones with item (normalized for supply) |

---

## QUESTIONS REFERENCE

| If You're Asked... | The Answer Is Based On... | Location |
|--------------------|---------------------------|----------|
| "What dishes should we prioritize?" | Two-track scoring framework | `config/scoring_framework_v3.json` |
| "Is Zone X MVP ready?" | Core 7 cuisine count | `docs/data/zone_mvp_status.json` |
| "How many partners do we have?" | Anna's ground truth | `DATA/3_ANALYSIS/anna_partner_coverage.csv` |
| "What do families want that we don't have?" | Latent demand analysis | `DATA/3_ANALYSIS/latent_demand_scores.csv` |
| "Why is this factor weighted 35%?" | Correlation analysis + rationale | `DELIVERABLES/reports/weight_rationale.md` |
| "Why did we remove Adult Appeal factor?" | Not measured, defaulted to neutral | `DELIVERABLES/reports/SCORING_FRAMEWORK_CHANGES_v3.md` |

---

*This document is designed to be self-contained. All decisions are documented. Read the agent brief before starting any analysis. Let the data tell the story.*

