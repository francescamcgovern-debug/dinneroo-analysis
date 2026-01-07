# Agent Index

**Framework Version:** 2.0 (Jan 2026)  
**Config:** `config/dish_scoring_unified.json`

This index helps you find the right agent for your task. Each agent has a specific mission and pulls only the context it needs.

## Quick Reference

| Agent | Mission | Use When You Ask About... |
|-------|---------|---------------------------|
| [SCORING_AGENT](SCORING_AGENT.md) | Design & validate scoring frameworks | weights, factors, correlations, framework design |
| [DISH_AGENT](01_DISH_AGENT.md) | Prioritize dishes, analyze performance | dish rankings, partner performance, Priority 100 |
| [ZONE_AGENT](ZONE_AGENT.md) | Zone health & MVP status | zone coverage, MVP criteria, zone performance |
| [GAP_AGENT](GAP_AGENT.md) | Identify expansion opportunities | missing cuisines, recruitment priorities, supply gaps |
| [PARTNER_AGENT](PARTNER_AGENT.md) | Partner recruitment & expansion | which partners to recruit, Nando's, partner fit |
| [FAMILY_BEHAVIOR_AGENT](FAMILY_BEHAVIOR_AGENT.md) | What families actually eat | home cooking, regional patterns, price sensitivity |
| [LATENT_DEMAND_AGENT](LATENT_DEMAND_AGENT.md) | Mine open-text for unmet needs | customer requests, barriers, dietary needs |
| [DATA_AGENT](DATA_AGENT.md) | Data operations & validation | Snowflake refresh, data quality, reconciliation |
| [DASHBOARD_AGENT](DASHBOARD_AGENT.md) | Create visualizations | charts, dashboards, interactive HTML |

---

## Agent Capabilities

### Tier 1: Core Analysis

#### SCORING_AGENT
- Design scoring frameworks (dish, zone, partner)
- Validate factors via correlation analysis
- Calculate weight rationale with evidence
- Run sensitivity analysis on thresholds

#### DISH_AGENT
- Generate Priority 100 dish rankings
- Analyze dish/partner performance
- Compare performance vs opportunity scores
- Classify dishes into quadrants (Priority/Protect/Develop/Monitor)

#### ZONE_AGENT
- Evaluate MVP status for zones
- Calculate zone health scores
- Identify top/bottom performing zones
- Compare zone characteristics

#### GAP_AGENT
- Identify missing cuisines by zone
- Prioritize partner recruitment
- Find supply gaps vs demand
- Generate expansion recommendations

#### PARTNER_AGENT (NEW)
- Map dish/cuisine gaps to specific partners
- Assess partner fit (bundles, price, ratings)
- Identify partners on Deliveroo but not Dinneroo
- Prioritize partner expansion to new zones

#### FAMILY_BEHAVIOR_AGENT (NEW)
- Analyze non-Dinneroo order patterns
- Identify regional eating preferences
- Assess price sensitivity for family meals
- Mine transcripts for home cooking patterns
- **Compare families vs couples/singles** (segment comparison)

### Tier 2: Discovery

#### LATENT_DEMAND_AGENT
- Extract themes from open-text responses
- Quantify unmet demand signals
- Identify dietary inclusion gaps
- Discover "home food" opportunities

### Tier 3: Operations

#### DATA_AGENT
- Pull fresh data from Snowflake
- Validate data quality
- Reconcile Anna's ground truth vs behavioral data
- Generate data quality reports

#### DASHBOARD_AGENT
- Create self-contained HTML dashboards
- Design interactive filters
- Embed data as JSON
- Apply consistent styling

---

## Routing Examples

| Question | Routes To |
|----------|-----------|
| "How should we weight the family fit factors?" | SCORING_AGENT |
| "What are the top 10 dishes we should prioritize?" | DISH_AGENT |
| "Does Clapham meet MVP criteria?" | ZONE_AGENT |
| "What cuisines are missing in Brighton?" | GAP_AGENT |
| "Which partners should we recruit for grilled chicken?" | PARTNER_AGENT |
| "What do families order outside Dinneroo?" | FAMILY_BEHAVIOR_AGENT |
| "How do eating patterns vary by region?" | FAMILY_BEHAVIOR_AGENT |
| "How do families differ from couples/singles?" | FAMILY_BEHAVIOR_AGENT |
| "What do customers say they want but can't get?" | LATENT_DEMAND_AGENT |
| "Refresh the Snowflake order data" | DATA_AGENT |
| "Create a dashboard showing zone performance" | DASHBOARD_AGENT |

---

## Shared Context

All agents should read these when needed:

| Document | When to Read |
|----------|--------------|
| `SHARED/01_BUSINESS_CONTEXT.md` | Understanding Dinneroo positioning |
| `SHARED/05_DATA_SOURCES_INVENTORY.md` | Choosing data sources |
| `SHARED/04_QUALITY_STANDARDS.md` | Evidence levels, citation standards |
| `CONTEXT/08_GROUND_TRUTH_DATA.md` | Supply metrics (use Anna's data) |

---

## Current Framework Summary (v2.0)

### Dish Scoring: Two-Track (50/50)

| Track | Weight | Key Components |
|-------|--------|----------------|
| Performance | 50% | Sales, Rating, Kids Happy, Liked/Loved |
| Opportunity | 50% | Latent Demand (25%), Adult Appeal, Balanced, Fussy Eater Friendly |

### Zone MVP Thresholds (Selection Criteria)

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Partners | ≥5 | Selection |
| Core Cuisines | 5 of 5 | Selection |
| Tier-1 Dishes | 3 of 5 | Selection |

### Zone Success Metrics (Outcomes)

| Metric | Benchmark | Type |
|--------|-----------|------|
| Repeat Rate | ≥35% | Outcome |
| Rating | ≥4.0 | Outcome |

### Evidence Levels

| Level | Symbol | Use For |
|-------|--------|---------|
| Validated | 🟢 | Strategic recommendations |
| Corroborated | 🟡 | Working hypotheses |
| Single/Estimated | 🔵 | Exploration only |

---

*For detailed protocols, read the individual agent briefs.*
