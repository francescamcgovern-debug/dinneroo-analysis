# CD Forum Reference Document
## Dish Insights & New Partner Onboarding

**Date:** Thursday, 15 January 2026  
**Purpose:** Walk CDs through dish insights and secure agreement on new partner onboarding  
**Presenter Support Document:** Evidence backup for Q&A

---

# EXECUTIVE SUMMARY (One-Page Quick Reference)

## The Ask
Approve onboarding new partners to close cuisine gaps in Indian, British, Mexican, and Middle Eastern categories.

## Why It Matters
- **41% of live zones** meet MVP criteria (5+ partners, 4+ cuisines, 10+ dishes)
- **Gap cuisines** cannot be filled by existing partners due to scale/capability constraints
- **Repeat rate** is the key success metric — cuisine count is the strongest predictor (r=0.514)

## Key Numbers to Remember

| Metric | Value | Source |
|--------|-------|--------|
| Total Dinneroo orders | 82,350 | Snowflake (Jan 2026) |
| Unique customers | 50,744 | Snowflake |
| Live zones with orders | 201 | Snowflake |
| Zones meeting MVP | ~82 (41%) | Zone analysis |
| Current partners | 40 brands | Anna's data |
| Partner sites | 756 | Anna's data |

## The Coverage Problem

| Cuisine | Items | Brands | Gap Type | Action Needed |
|---------|-------|--------|----------|---------------|
| Asian | 410+ | 5+ | OK | Protect |
| Italian | 705 | 6 | OK | Protect |
| **Indian** | 85 | 6 | SUPPLY GAP | **New px** |
| **British** | 292 | 1 | SUPPLY GAP | **New px** |
| **Mexican** | 168 | 2 | QUALITY GAP | **New px** |
| **Middle Eastern** | 30 | 5 | SUPPLY GAP | **New px** |

## Three Levers, One Solution

| Lever | Capability | Verdict |
|-------|------------|---------|
| 1. Expand existing px sites | Limited — scale players already at max | Marginal uplift |
| 2. Add dishes to existing px | Limited — multi-cuisine players lack depth | Marginal uplift |
| 3. **Onboard new px** | Can target specific gap cuisines | **Primary solution** |

## Scoring Framework Evolution (Why We're Confident)

We tested multiple approaches before arriving at the current framework:

| Version | Approach | Result |
|---------|----------|--------|
| v1 | 10 subjective factors | Most factors estimated, not measured — didn't differentiate |
| v2 | 7 factors validated against success metrics | Only 3 showed correlation >0.1 |
| **v3 (Current)** | 5 behavioral factors, 60/40 split | Simplified to what we can actually measure |

**Factors tested and rejected:** Kid-Friendly (0.080), Shareability (0.055), Value at £25 (0.046), Vegetarian Option (0.032) — all below the 0.1 impact threshold.

**Key insight:** Subjective "kid-friendly" scores didn't predict success. Measured "kids happy" outcomes did. We now weight what actually happened.

---

# SLIDE-BY-SLIDE EVIDENCE

## Slides 3-5: Coverage Constraints & Three Levers

### Current State
- **1,571 dishes** offered across Dinneroo, but heavily skewed:
  - Asian: 410+ items (26%)
  - Italian: 705 items (45%)
  - Indian: 85 items (5%)
  - Mexican: 168 items (11%)
  - Middle Eastern: 30 items (2%)
  - British: 292 items but only 1 brand

### Why Existing Partners Can't Fill Gaps

**Scale players are cuisine-specific:**
| Partner | Sites | Primary Cuisine | Can Cover Gaps? |
|---------|-------|-----------------|-----------------|
| PizzaExpress | 166 | Italian | No |
| Wagamama | 103 | Japanese/Asian | No |
| Itsu | 50 | Japanese | No |
| Pho | 46 | Vietnamese | No |
| Bill's | 40 | British (limited menu) | Partially |
| Giggling Squid | 38 | Thai | No |
| Dishoom | 11 | Indian | **Yes but limited scale** |
| Las Iguanas | 29 | Mexican | **Quality issues (3.94 rating)** |

**Multi-cuisine players lack depth:**
- Partners like Bill's offer multiple cuisines but lack the depth in any single gap cuisine
- No existing partner can provide Indian family bundles at scale (Dishoom = 11 sites only)

---

## Slide 9: Zone MVP Definition

### MVP Criteria: 5+ partners, 4+ cuisines, 10+ dishes

| Criterion | Business Target | Data Inflection Point | Evidence |
|-----------|-----------------|----------------------|----------|
| Partners | 5+ | 3+ (+4.5pp repeat rate) | mvp_threshold_discovery.json |
| Cuisines | 4+ | 3+ (+4.2pp repeat rate) | mvp_threshold_discovery.json |
| Dishes | 10+ | N/A | Business judgment |

### Why 5 Partners Not 3?
- Data shows meaningful improvement at 3 partners (+4.5pp repeat rate)
- Business target is 5 to provide:
  - Cuisine redundancy (backup if one partner is unavailable)
  - Peak time availability
  - Customer choice within cuisines

### Current MVP Status (201 Live Zones)

| Status | Count | % | Definition |
|--------|-------|---|------------|
| MVP Ready | 25 | 12% | 5+ cuisines |
| Near MVP | ~15 | 7% | 4 cuisines |
| Progressing | ~45 | 22% | 3 cuisines |
| Developing | ~116 | 58% | 1-2 cuisines |

---

## Slides 11-13: Dish Prioritization Scoring

### Scoring Framework Evolution

We tested multiple scoring approaches before arriving at the current framework. This provides confidence that the prioritization is robust.

#### Frameworks Tested

| Version | Factors | Track Split | Key Issue |
|---------|---------|-------------|-----------|
| **v1 (10-factor)** | 10 | 50/50 | Too many factors, most were estimated not measured |
| **v2 (Validated)** | 7 fit factors tested | 50/50 | Only 3 factors showed meaningful correlation |
| **v3 (Current)** | 5 | 60/40 | Simplified, behavioral data weighted higher |

#### Factor Validation Results (Why We Dropped Some Factors)

We ran correlation analysis against success metrics (order volume, rating, satisfaction). Only factors with impact score >0.1 were retained:

| Factor Tested | Impact Score | Verdict | Reason |
|---------------|-------------|---------|--------|
| **Adult Appeal** | 0.204 | ✅ Kept (v2) then dropped (v3) | Strong correlation but mostly estimated, not measured |
| **Balanced/Guilt-Free** | 0.184 | ✅ Kept (v2) then dropped (v3) | Strong correlation but only 13 dishes had survey data |
| **Fussy Eater Friendly** | 0.109 | ✅ Kept (v2) then dropped (v3) | Just above threshold, weight too small to impact |
| **Kid-Friendly** | 0.080 | ❌ Dropped | Below threshold — weak correlation with success |
| **Shareability** | 0.055 | ❌ Dropped | No meaningful correlation |
| **Value at £25** | 0.046 | ❌ Dropped | Negative correlation with rating |
| **Vegetarian Option** | 0.032 | ❌ Dropped | No meaningful correlation |

**Key Finding:** "Kid-Friendly" as a subjective factor (impact 0.080) was dropped, but "Kids Happy" as a measured outcome (from post-order survey) was elevated to 20% weight. **What matters is whether kids actually liked it, not whether we think they would.**

#### Why 60/40 Split (Not 50/50)?

| Reason | Evidence |
|--------|----------|
| Behavioral data is stronger signal | 82,350 orders vs ~1,600 survey responses |
| Opportunity factors had data gaps | Only 13 of 48 dishes had measured fit scores |
| Performance predicts repeat | Correlation analysis showed behavioral metrics more predictive |

### Current Scoring Framework (v3.1)

| Track | Weight | Components |
|-------|--------|------------|
| **Performance** | 60% | Orders per Zone (20%), Rating (20%), Kids Happy (20%) |
| **Opportunity** | 40% | Latent Demand (20%), Non-Dinneroo Demand (20%) |

### Top 10 Priority Dishes

| Rank | Dish Type | Cuisine | Score | Orders | Kids Happy |
|------|-----------|---------|-------|--------|------------|
| 1 | Katsu | Japanese | 3.40 | 19,534 | 78% |
| 2 | Noodles | Global | 3.90 | 18,180 | 80% |
| 3 | Curry | Indian | 3.70 | 13,302 | 81% |
| 4 | Fried Rice | Chinese | 3.50 | 12,180 | 80% |
| 5 | Pho | Vietnamese | 3.70 | 9,392 | 80% |
| 6 | Bowl | Healthy | 3.60 | 6,866 | 100% |
| 7 | Rice Bowl | Healthy | 3.35 | 6,866 | 85% |
| 8 | Pad Thai | Thai | 3.25 | 5,507 | 72% |
| 9 | Pasta | Italian | 3.40 | 5,305 | 79% |
| 10 | Salad | Healthy | 3.55 | 5,296 | 80% |

### Quadrant Classification

| Quadrant | Definition | Action |
|----------|------------|--------|
| **Core Drivers** | High Performance + High Opportunity | Protect & expand |
| **Demand Boosters** | High Performance + Low Opportunity | Build demand signals |
| **Preference Drivers** | Low Performance + High Opportunity | Recruit partners |
| **Deprioritised** | Low Performance + Low Opportunity | Don't invest |

---

## Slides 14-17: Coverage Analysis

### Aggregate Coverage (1,571 dishes)

| Cuisine | Items | % of Total | Status |
|---------|-------|------------|--------|
| Italian | 705 | 45% | Over-indexed |
| Asian (all) | 410+ | 26% | Adequate |
| British | 292 | 19% | 1 brand only |
| Mexican | 168 | 11% | Quality issues |
| Indian | 85 | 5% | Under-indexed |
| Middle Eastern | 30 | 2% | Under-indexed |

### Zone-Level Analysis

The issue is NOT wrong dishes — it's **insufficient scale partners in gap cuisines**:

| Zone Example | Cuisines Present | Missing | Status |
|--------------|------------------|---------|--------|
| Clapham | 9 | None | MVP Ready |
| Brighton Central | 8 | None | MVP Ready |
| Brixton | 4 | Indian, British, Healthy | Near MVP |
| Croydon | 3 | Indian, Mexican, Middle Eastern, British | Developing |

### Priority Gap Dishes by Cuisine

| Cuisine | Priority Dishes to Recruit | Current Coverage |
|---------|---------------------------|------------------|
| **Indian** | Curry, Biryani, Butter Chicken | 85 items, 6 brands |
| **British** | Shepherd's Pie, Roast Dinner, Fish & Chips | 292 items, 1 brand |
| **Mexican** | Fajitas, Tacos, Burrito | 168 items, 2 brands (quality gap) |
| **Middle Eastern** | Shawarma, Falafel | 30 items, 5 brands |

---

## Slides 18-21: Three Levers Deep Dive

### Lever 1: Expand Existing Partner Sites

| Partner | Current Sites | Expansion Potential | Verdict |
|---------|---------------|---------------------|---------|
| Dishoom (Indian) | 11 | Limited by restaurant capacity | **Insufficient** |
| Las Iguanas (Mexican) | 29 | Quality issues (3.94 rating) | **Not recommended** |
| Bill's (British) | 40 | Limited menu depth | **Partial** |

### Lever 2: Add Dishes to Existing Partners

| Partner Type | Can Add Gap Cuisines? | Why/Why Not |
|--------------|----------------------|-------------|
| Scale Asian (Wagamama, Pho) | No | Core competency is Asian |
| Scale Italian (PizzaExpress) | No | Core competency is Italian |
| Multi-cuisine (Bill's) | Limited | Lack depth in any single cuisine |

### Lever 3: Onboard New Partners (Recommended)

| Gap Cuisine | Target Partner Profile | Example Candidates |
|-------------|----------------------|-------------------|
| Indian | Family-friendly curry houses with bundles | Regional chains, dark kitchens |
| British | Comfort food specialists | Pie chains, roast dinner specialists |
| Mexican | Quality Mexican (4.0+ rating) | Alternative to Las Iguanas |
| Middle Eastern | Shawarma/falafel specialists | Regional chains |

---

## Slide 24: Protein Analysis

### Current Protein Distribution

| Protein | Representation | Notes |
|---------|---------------|-------|
| Chicken | Dominant | Well covered across cuisines |
| Other meats | Under-represented | Beef, lamb options limited |
| Fish | Under-represented | Fish & chips = 1 order only |
| Vegetarian | Under-represented | 22 survey mentions for veggie options |

---

# ANTICIPATED Q&A

## Q1: "Why can't existing partners fill these gaps?"

**Answer:** Our scale partners are cuisine-specialists:
- PizzaExpress (166 sites) = Italian only
- Wagamama (103 sites) = Japanese/Asian only
- Pho (46 sites) = Vietnamese only

The only Indian partner with scale potential is **Dishoom with just 11 sites**. For Mexican, Las Iguanas has 29 sites but a **3.94 rating** (below our 4.0 threshold).

**Evidence:** `DATA/3_ANALYSIS/anna_partner_coverage.csv`

---

## Q2: "How confident are we in the dish prioritization?"

**Answer:** High confidence — we triangulated across three data sources AND tested multiple scoring approaches:

| Source | Sample Size | What It Tells Us |
|--------|-------------|------------------|
| Snowflake Orders | 82,350 orders | What families actually buy |
| Post-Order Survey | 1,599 responses | Kids happy, adult satisfaction |
| Ratings | 10,713 ratings | Quality perception |

No single source weighted >50%. Strategic recommendations require 3+ sources (our standard).

**We also validated the framework itself:**
- Tested 7 different factors for correlation with success metrics
- Only kept factors with impact score >0.1
- Dropped subjective "kid-friendly" (0.080) in favor of measured "kids happy" (from surveys)
- Iterated through 3 framework versions before landing on current approach

**Evidence:** `config/evidence_standards.json`, `config/dashboard_metrics.json`, `DELIVERABLES/reports/factor_validation_analysis.md`

---

## Q3: "Why 5 partners for MVP, not 3?"

**Answer:** Data shows the inflection point at 3 partners (+4.5pp repeat rate), but we set 5 as the business target for:

1. **Cuisine redundancy** — if one partner is offline, families still have options
2. **Peak availability** — multiple partners handle dinner rush better
3. **Choice within cuisine** — families want options, not just one Indian restaurant

The gap between data (3) and target (5) is intentional — it's the difference between "metrics improve" and "families are delighted."

**Evidence:** `DATA/3_ANALYSIS/mvp_threshold_discovery.json`

---

## Q4: "What's the business case for new partner onboarding?"

**Answer:** This document focuses on the **opportunity size** from customer data. The commercial case (costs, timelines, partner economics) should come from the partnerships team.

What we can say from data:
- **59% of zones** are below MVP (opportunity to improve)
- **Repeat rate** is the key metric — adding cuisines drives +4.2pp improvement
- **Indian cuisine** has the highest repeat rate (23.1%) — high-value gap to fill

**Flag for Anna:** Commercial input needed for full business case.

---

## Q5: "What happens if we don't act?"

**Answer:** Zones remain stuck in "Developing" status:
- 58% of live zones have only 1-2 cuisines
- These zones have lower repeat rates (families don't come back)
- We're leaving demand on the table — survey shows unmet demand for Indian, Mexican, British options

**Evidence:** `DATA/3_ANALYSIS/zone_mvp_status.csv`

---

## Q6: "Which zones should we prioritize for new partners?"

**Answer:** High-order zones missing key cuisines:

| Zone | Orders | Current Cuisines | Missing | Priority |
|------|--------|------------------|---------|----------|
| Canning Town | 1,314 | 3 | Indian, Mexican, Middle Eastern | High |
| Brockley/Forest Hill | 1,478 | 3 | Indian, Mexican, Middle Eastern | High |
| Edgbaston | 574 | 3 | Indian, Mexican, Middle Eastern | High |
| Croydon | 519 | 3 | Indian, Mexican, Middle Eastern | High |

**Evidence:** `DATA/3_ANALYSIS/anna_zone_dish_counts.csv`

---

## Q7: "How do we know families want these cuisines?"

**Answer:** Multiple signals converge:

| Signal | Indian | Mexican | British | Middle Eastern |
|--------|--------|---------|---------|----------------|
| Repeat rate | **23.1%** (highest) | 20.6% | N/A | 19.7% |
| Survey mentions | 61 (curry) | Limited | 13 (lasagne) | Limited |
| Order volume | 8,356 | 43 | 3,358 | 1,023 |

Indian shows strongest signal across all metrics. Mexican has quality issues with current supply (Las Iguanas = 3.94 rating).

**Evidence:** `DELIVERABLES/reports/MASTER_ANALYSIS_REPORT.md`

---

## Q8: "What about vegetarian options?"

**Answer:** Survey data shows 22 explicit mentions for vegetarian options — a validated gap. Current coverage is limited:
- Most vegetarian dishes are sides or salads
- No dedicated vegetarian partner at scale
- Opportunity to recruit vegetarian-friendly partners (e.g., Farmer J expansion)

**Evidence:** Open-text survey analysis

---

## Q9: "How does this align with Dinneroo's positioning?"

**Answer:** Dinneroo is positioned for **balanced midweek meals** — not indulgent weekend treats.

The gap cuisines align well:
- **Indian curry** = balanced protein + veg + carbs
- **British comfort food** = shepherd's pie, roast dinner = family classics
- **Mexican** = fajitas = customizable, balanced
- **Middle Eastern** = shawarma = protein-focused, healthy perception

What doesn't fit: Heavy pizza, burgers (already deprioritized in our framework).

**Evidence:** `DOCUMENTATION/AGENTS/01_DISH_AGENT.md`

---

## Q10: "What's the timeline expectation?"

**Answer:** Data team cannot provide timelines — this is a partnerships/commercial question.

What we can say:
- Priority should be **Indian first** (highest repeat rate, clearest gap)
- **Mexican second** (need quality alternative to Las Iguanas)
- **British/Middle Eastern** can follow based on partner availability

---

## Q11: "Why did you change the scoring framework? What didn't work before?"

**Answer:** We evolved through three framework versions based on data validation:

| Version | What We Tried | What We Learned |
|---------|--------------|-----------------|
| **v1 (10-factor)** | 10 subjective factors (kid-friendly, shareability, value, etc.) | Most factors were estimated, not measured — didn't differentiate dishes |
| **v2 (Validated)** | Tested 7 factors against success metrics | Only 3 factors (adult appeal, balanced, fussy eater) showed correlation >0.1 |
| **v3 (Current)** | 5 factors, 60/40 split | Simplified to factors with actual data; elevated behavioral metrics |

**Key insight:** Subjective factors like "kid-friendly" (scored by judgment) had weak correlation (0.080). But measured outcomes like "kids happy" (from post-order survey) are strong predictors. **We now weight what actually happened over what we think should happen.**

**Evidence:** `DELIVERABLES/reports/factor_validation_analysis.md`, `DELIVERABLES/reports/SCORING_FRAMEWORK_CHANGES_v3.md`

---

## Q12: "What factors did you test and reject?"

**Answer:** We tested 7 factors and rejected 4 based on correlation analysis:

| Factor Rejected | Impact Score | Why It Failed |
|-----------------|-------------|---------------|
| **Kid-Friendly** | 0.080 | Subjective judgment didn't predict actual orders or satisfaction |
| **Shareability** | 0.055 | No meaningful correlation with any success metric |
| **Value at £25** | 0.046 | Actually had *negative* correlation with rating |
| **Vegetarian Option** | 0.032 | No correlation — nice to have but doesn't drive success |

**What we kept (in v2, later simplified in v3):**
- Adult Appeal (0.204) — strongest predictor
- Balanced/Guilt-Free (0.184) — second strongest
- Fussy Eater Friendly (0.109) — just above threshold

**Why we simplified further in v3:** Even the "kept" factors only had measured data for 13 of 48 dishes. The rest defaulted to score of 3 (neutral), meaning they weren't actually differentiating rankings. We dropped them in favor of purely behavioral metrics.

**Evidence:** `DATA/3_ANALYSIS/factor_impact_summary.csv`, `DATA/3_ANALYSIS/factor_correlations.csv`

---

# DATA SOURCE APPENDIX

## Primary Data Sources

| Source | File | Records | Last Updated | Use |
|--------|------|---------|--------------|-----|
| Snowflake Orders | `ALL_DINNEROO_ORDERS.csv` | 82,350 | 2026-01-07 | Order volume, repeat rate |
| Snowflake Customers | (derived) | 50,744 | 2026-01-07 | Customer-level metrics |
| Post-Order Survey | `post_order_enriched_COMPLETE.csv` | 1,599 | Dec 2025 | Family satisfaction |
| Dropoff Survey | `DROPOFF_ENRICHED.csv` | 838 | Dec 2025 | Unmet demand |
| Ratings | `DINNEROO_RATINGS.csv` | 10,713 | 2026-01-07 | Quality perception |
| Anna's Partner Data | `anna_partner_coverage.csv` | 40 brands | Dec 2025 | Supply ground truth |
| Anna's Zone Data | `anna_zone_dish_counts.csv` | 1,306 zones | Dec 2025 | Zone supply |

## Key Configuration Files

| File | Purpose |
|------|---------|
| `config/mvp_thresholds.json` | MVP criteria (5 px, 4 cuisines, etc.) |
| `config/scoring_framework_v3.json` | Dish scoring methodology |
| `config/dashboard_metrics.json` | Authoritative metric counts |
| `config/evidence_standards.json` | Sample size requirements |

## Sample Size Standards

| Claim Type | Minimum n |
|------------|-----------|
| Percentage claim | n ≥ 30 |
| Comparison (A vs B) | n ≥ 20 per group |
| Dish recommendation | n ≥ 50 orders + n ≥ 10 survey |
| Zone assessment | n ≥ 100 orders |

## Evidence Levels Used

| Level | Symbol | Meaning | Sources Required |
|-------|--------|---------|------------------|
| Validated | 🟢 | High confidence | 3+ sources |
| Corroborated | 🟡 | Medium confidence | 2 sources |
| Single | 🔵 | Exploratory | 1 source |

---

# QUICK REFERENCE CARD

## Numbers to Know

- **82,350** total orders
- **50,744** unique customers
- **201** live zones with orders
- **41%** zones meeting MVP
- **40** partner brands
- **756** partner sites

## Gap Cuisines (Priority Order)

1. **Indian** — highest repeat rate (23.1%), only 6 brands
2. **Mexican** — quality gap (3.94 rating), need alternative to Las Iguanas
3. **British** — only 1 brand (Bill's), limited menu depth
4. **Middle Eastern** — supply gap (30 items only)

## MVP Definition

- 5+ partners
- 4+ cuisines (from Core 7: Asian, Italian, Indian, Healthy, Mexican, Middle Eastern, British)
- 10+ dishes

## The Ask

Approve new partner onboarding to close cuisine gaps — existing partner levers are insufficient.

---

*Document prepared for CD Forum, January 2026*  
*Data sources: Snowflake (2026-01-07), Anna's supply data (Dec 2025), Post-order surveys (Dec 2025)*
