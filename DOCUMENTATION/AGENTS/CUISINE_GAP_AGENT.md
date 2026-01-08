# Cuisine Gap Agent

## Mission

Score and rank cuisines at both core and granular levels to inform supply strategy. Identify which cuisines to prioritize, which sub-cuisines to focus within, and surface new cuisine opportunities from demand signals.

**CANONICAL DEFINITIONS:** Import all cuisine mappings from `scripts/utils/definitions.py`

```python
from utils.definitions import CORE_7, get_core_7, get_sub_cuisine
```

**Note:** For dish-level gaps within cuisines, use DISH_GAP_AGENT. For partner recruitment, use PARTNER_AGENT.

---

## Questions I Answer

- Which of the Core 7 cuisines should we prioritize?
- Within Asian, should we focus on Thai, Japanese, or Vietnamese?
- Are there cuisines outside the Core 7 we should add?
- Which cuisines are underperforming given their supply footprint?
- What's the cuisine-level opportunity vs performance trade-off?

---

## Two-Level Cuisine Structure

### Level 1: Core 7 Cuisines (Business Framework)

Anna's established categories - used for zone MVP criteria and business reporting:

| Core Cuisine | Sub-Cuisines (Level 2) | MVP Relevance |
|--------------|------------------------|---------------|
| **Asian** | Japanese, Thai, Vietnamese, Chinese, Korean, Pan-Asian | Zone needs 1+ |
| **Italian** | Pizza-focused, Pasta-focused, Premium Italian | Zone needs 1+ |
| **Indian** | North Indian, South Indian, Pan-Indian | Zone needs 1+ |
| **Healthy** | Grain Bowls, Salads, Protein-focused | Zone needs 1+ |
| **Mexican** | Tex-Mex, Burritos, Tacos, Premium Mexican | Zone needs 1+ |
| **Middle Eastern** | Lebanese, Turkish, Shawarma, Mediterranean | Optional |
| **British** | Fish & Chips, Pies, Roasts, Comfort | Optional |

### Level 2: Granular Sub-Cuisines (Analytical Detail)

Each sub-cuisine gets its own score, allowing insights like:
- "Within Asian, Thai outperforms Japanese on repeat rate"
- "Vietnamese has 300 orders/zone vs Japanese at 106/zone"

### Level 3: New Cuisine Opportunities (Demand-Driven)

Cuisines NOT in Core 7 but with demand signals:

| Potential Cuisine | Demand Signal | Source |
|-------------------|---------------|--------|
| Caribbean | 2,490 non-Dinneroo orders | Behavioral |
| Korean | 5,218 non-Dinneroo orders | Behavioral |
| Greek | 5,881 non-Dinneroo orders | Behavioral |
| Portuguese | 19,837 non-Dinneroo orders | Behavioral |
| Turkish | 7,037 non-Dinneroo orders | Behavioral |

---

## Protocol

### Step 1: State the Question

```markdown
## Agent: Cuisine Gap Agent
## Question: [Which cuisines should we prioritize?]
## Scope: [National / Regional / Zone-specific]
## Output: [Cuisine rankings / Gap report / Expansion opportunities]
```

### Step 2: Load Cuisine Data

| Source | File | Use For |
|--------|------|---------|
| Cuisine Performance | `DATA/3_ANALYSIS/cuisine_performance.csv` | Orders, repeat rate, ratings by cuisine |
| Cuisine Scores | `DATA/3_ANALYSIS/cuisine_scores.csv` | Unified cuisine rankings |
| Partner-Cuisine Matrix | `DATA/3_ANALYSIS/partner_cuisine_matrix.csv` | Who serves what |
| Non-Dinneroo Demand | `DATA/3_ANALYSIS/non_dinneroo_cuisine_demand_midweek.csv` | What families order elsewhere (FILTERED) |
| Cuisine Hierarchy | `config/cuisine_hierarchy.json` | Core 7 → sub-cuisine mapping |
| Scoring Config | `config/cuisine_scoring.json` | Weights and thresholds |

### Step 3: Apply Cuisine Scoring Framework

**Config file:** `config/cuisine_scoring.json`

#### Performance Track (50%) - Normalized for Supply

| Component | Weight | Formula | Why |
|-----------|--------|---------|-----|
| **Orders per Zone** | 12.5% | `orders ÷ zones_with_cuisine` | Removes supply bias |
| **Repeat Rate** | 12.5% | Already a % | Best retention signal |
| **Avg Rating** | 7.5% | Weighted by orders | Quality signal |
| **Kids Full & Happy** | 10% | From post-order survey | Critical family signal |
| **Satisfaction** | 7.5% | From survey data | Adult approval |

**Supply threshold:** Need 15+ zones to score performance (otherwise N/A)

#### Opportunity Track (50%) - Pure Demand Signals

Weights favor high-n sources:

| Component | Weight | Source | Sample Size |
|-----------|--------|--------|-------------|
| **Non-Dinneroo Orders** | 25% | `non_dinneroo_cuisine_demand_midweek.csv` | 196k+ orders (revealed behavior) |
| **OG Wishlist** | 15% | Historical survey | ~400 respondents (stated preference) |
| **Open-Text Requests** | 10% | Dropoff + Post-order + Ratings | Low n (directional signal) |

**Note:** Supply gap is NOT included - that would conflate supply with demand.

### Step 4: Classify into Quadrants

**2x2 Matrix: Performance vs Opportunity**

```
                    OPPORTUNITY
                 Low (<3.0)    High (≥3.0)
              ┌─────────────┬─────────────┐
    High      │   PROTECT   │  PRIORITY   │
   (≥3.5)     │  Maintain   │   Expand    │
PERFORMANCE   ├─────────────┼─────────────┤
    Low       │   MONITOR   │   RECRUIT   │
   (<3.5)     │ Deprioritize│  Fill gap   │
              └─────────────┴─────────────┘
```

**For cuisines WITH performance data (15+ zones):**

| Quadrant | Performance | Opportunity | Action |
|----------|-------------|-------------|--------|
| **Priority** | High (≥3.5) | High (≥3.0) | Expand aggressively - recruit more partners |
| **Protect** | High (≥3.5) | Low (<3.0) | Maintain quality, geographic expansion |
| **Recruit** | Low (<3.5) | High (≥3.0) | Supply gap - recruit aggressively |
| **Monitor** | Low (<3.5) | Low (<3.0) | Deprioritize expansion efforts |

**For cuisines WITHOUT performance data (<15 zones or new):**

| Quadrant | Opportunity | Action |
|----------|-------------|--------|
| **Expansion** | High (≥3.0) | New cuisine opportunity - test & recruit |
| **Watch** | Low (<3.0) | Low priority for expansion |

### Step 5: Generate Output

Include for each cuisine:
- Core Category (or "NEW" if expansion opportunity)
- Level (core/sub/new)
- Unified Score
- Performance Score (or N/A if insufficient data)
- Opportunity Score
- Quadrant
- Zones Available
- Orders per Zone
- Repeat Rate
- Supply Gap %

---

## CRITICAL: Non-Dinneroo Benchmark Filtering

### The Problem

Dinneroo is **98% midweek orders** (Mon-Thu, 5-7pm dinner). Non-Dinneroo orders include:
- Weekend "treat" orders (61% of non-Dinneroo volume)
- Late-night takeaways
- Lunch orders
- Different customer psychology

Using unfiltered non-Dinneroo data creates **apples-to-oranges comparisons**.

### Required Filters

When using non-Dinneroo orders as a demand benchmark, ALWAYS filter to:

```sql
WHERE ORDER_DAY IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday')
  AND ORDER_TIME BETWEEN '16:30' AND '21:00'
```

### Files

| File | Use |
|------|-----|
| `non_dinneroo_cuisine_demand.csv` | Raw - DO NOT USE for benchmarks |
| `non_dinneroo_cuisine_demand_midweek.csv` | Filtered - USE THIS |

---

## Key Files

| File | Purpose |
|------|---------|
| `DATA/3_ANALYSIS/cuisine_scores.csv` | Master cuisine rankings |
| `DATA/3_ANALYSIS/cuisine_quadrants.json` | Quadrant assignments |
| `DATA/3_ANALYSIS/cuisine_performance.csv` | Order/rating data by cuisine |
| `DATA/3_ANALYSIS/expansion_opportunities.json` | New cuisines to consider |
| `DATA/3_ANALYSIS/partner_cuisine_matrix.csv` | Partner-cuisine mapping |
| `DATA/3_ANALYSIS/non_dinneroo_cuisine_demand_midweek.csv` | Filtered demand benchmark |
| `config/cuisine_hierarchy.json` | Core 7 → sub-cuisine mapping |
| `config/cuisine_scoring.json` | Framework configuration |

---

## New Cuisine Detection

Automatically flag cuisines for expansion consideration when:

```python
if midweek_non_dinneroo_orders > 2000 AND unique_customers > 1000:
    flag_as_expansion_opportunity()
```

Current candidates meeting threshold (based on Mon-Thu dinner filtering):
- Caribbean
- Korean  
- Greek
- Portuguese
- Turkish

---

## Example Output: Cuisine Scores

```csv
cuisine,core_category,level,performance_score,opportunity_score,unified_score,quadrant,zones_available,orders_per_zone,repeat_rate,supply_gap_pct
Vietnamese,Asian,sub,4.3,2.8,3.55,Protect,44,300,0.209,-
Indian,Indian,core,4.5,3.0,3.75,Priority,24,350,0.231,-
Japanese,Asian,sub,3.8,2.6,3.20,Protect,140,106,0.163,-
Thai,Asian,sub,3.6,2.7,3.15,Protect,40,130,0.158,-
Chinese,Asian,sub,N/A,4.2,4.2,Recruit,8,36,0.086,-76%
Italian,Italian,core,3.6,2.4,3.00,Monitor,170,54,0.165,-
Caribbean,NEW,new,N/A,3.5,3.5,Expansion,0,N/A,N/A,100%
Korean,NEW,new,N/A,3.0,3.0,Expansion,0,N/A,N/A,100%
```

---

## Output Format

### Cuisine Prioritization Report

```markdown
# Cuisine Prioritization: [Scope]

## Key Findings
- [Top 3-5 insights with evidence levels]

## Core 7 Status
| Core Cuisine | Score | Quadrant | Action |
|--------------|-------|----------|--------|
| [Cuisine] | X.XX | [Quadrant] | [Action] |

## Sub-Cuisine Rankings (within Core 7)
### Asian
| Sub-Cuisine | Score | Orders/Zone | Repeat Rate | Quadrant |
|-------------|-------|-------------|-------------|----------|
| Vietnamese | X.XX | XXX | XX% | [Quadrant] |
| Thai | X.XX | XXX | XX% | [Quadrant] |

## Expansion Opportunities (Outside Core 7)
| Cuisine | Opportunity Score | Demand Signal | Recommendation |
|---------|-------------------|---------------|----------------|
| [Cuisine] | X.XX | [Signal] | [Action] |

## Recommendations
🟢 VALIDATED: [Recommendation with 3+ sources]
🟡 CORROBORATED: [Recommendation with 2 sources]
🔵 SINGLE: [Exploratory finding]

## Data Sources
[Tables with sample sizes and filtering applied]
```

---

## Dashboard Integration

This agent feeds the **Cuisine Gaps** section in the Master Dashboard.

| Output | Dashboard Location | Data File |
|--------|-------------------|-----------|
| Core 7 scores | Cuisine Gaps > Core Overview | `cuisine_scores.csv` |
| Sub-cuisine rankings | Cuisine Gaps > Granular Rankings | `cuisine_scores.csv` |
| Quadrant classification | Cuisine Gaps > Quadrant Chart | `cuisine_quadrants.json` |
| Expansion opportunities | Cuisine Gaps > New Cuisines | `expansion_opportunities.json` |

**Dashboard panels:**
- **Panel 1: Core 7 Overview** - Radar chart + traffic lights
- **Panel 2: Granular Rankings** - Bar chart by sub-cuisine
- **Panel 3: Expansion Opportunities** - Table of new cuisine candidates
- **Panel 4: Cuisine → Dish Drilldown** - Link to DISH_GAP_AGENT

**To update dashboard with cuisine data:**
```bash
python3 scripts/phase2_analysis/score_cuisines.py
python3 scripts/prepare_dashboard_data.py
python3 scripts/generate_dashboard.py
```

---

## Anti-Drift Rules

- ❌ Don't use raw volume without normalizing for supply (zones/partners)
- ❌ Don't use unfiltered non-Dinneroo data for benchmarks (must be Mon-Thu dinner)
- ❌ Don't recommend cuisines without demand evidence
- ❌ Don't confuse Core 7 business categories with granular sub-cuisines
- ✅ Always normalize performance metrics by zone count
- ✅ Always use `non_dinneroo_cuisine_demand_midweek.csv` for demand benchmarks
- ✅ Distinguish cuisines with performance data (15+ zones) from new opportunities
- ✅ Cite sample sizes for all demand signals

---

## Handoff

| Finding | Route To |
|---------|----------|
| Need dish-level gaps within cuisine | DISH_GAP_AGENT |
| Need partner recommendations for cuisine | PARTNER_AGENT |
| Need zone-specific cuisine analysis | ZONE_AGENT |
| Need latent demand signals | LATENT_DEMAND_AGENT |
| Need fresh data pull | DATA_AGENT |
| Need visualization | DASHBOARD_AGENT |

---

*This agent prioritizes cuisines. Let normalized performance and filtered demand data guide rankings.*

