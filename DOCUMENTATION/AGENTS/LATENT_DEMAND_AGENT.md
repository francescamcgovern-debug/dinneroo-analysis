# Latent Demand Agent

## Mission

Mine open-text responses and customer transcripts to discover unmet needs that behavioral data can't capture.

---

## Why This Agent Exists

**Survivorship Bias Problem:** Order data only shows what succeeds among AVAILABLE options. It does NOT capture:
- Dishes families want but don't expect on delivery
- Cuisines underrepresented in current partner mix
- Options for families who CAN'T use Dinneroo due to dietary restrictions
- "Home food" families wish they could order

This agent finds the demand that's invisible in order volume data.

---

## Questions I Answer

- What dishes do customers mention wanting but we don't offer?
- What barriers do families cite for not ordering?
- What dietary needs are unmet?
- What "home food" do families wish they could order?
- What would make non-customers convert?

---

## Protocol

### Step 1: State the Discovery Question

```markdown
## Agent: Latent Demand Agent
## Question: [What unmet demand are we looking for?]
## Sources: [Which open-text fields will we analyze?]
## Method: [Theme extraction / Keyword search / Both]
```

### Step 2: Load Open-Text Data

| Source | File | Key Fields | Sample Size |
|--------|------|------------|-------------|
| Dropoff Survey | `DATA/1_SOURCE/surveys/dropoff_LATEST.csv` | `What dishes would you like to see?`, `What kid-friendly options?` | ~800 |
| Post-Order Survey | `DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv` | `DISH_IMPROVEMENTS`, `SUGGESTED_IMPROVEMENTS` | ~1,500 |
| Ratings Comments | `DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv` | `RATING_COMMENT` | ~10,000 |
| Customer Transcripts | `DATA/1_SOURCE/qual_research/transcripts/` | Full interview text | 88 interviews |

### Step 3: Extract Themes (LLM Task)

**Prompt Template:**
```
Analyze these customer responses about Dinneroo.
Extract ALL mentions of:
- Specific dishes (by name)
- Cuisine types
- Food categories
- Dietary needs
- Barriers to ordering

Do NOT use predefined categories. Discover themes fresh.

For each theme:
- Theme name
- Frequency (count)
- Example quotes (2-3)
- Sentiment (positive/negative/neutral)
```

### Step 4: Quantify Mentions

| Theme | Dropoff | Post-Order | Ratings | Total | Signal Strength |
|-------|---------|------------|---------|-------|-----------------|
| [Theme A] | X | X | X | X | 🔴 High / 🟡 Medium / 🔵 Low |

### Step 5: Categorize by Tier

| Tier | Focus | Action |
|------|-------|--------|
| **Tier 1** | Optimize Existing | Dishes we have that need improvement |
| **Tier 2** | High-Signal Gaps | Dishes frequently requested, not available |
| **Tier 3** | Cultural Inference | "Home food" families eat but don't think to order |
| **Tier 4** | Dietary Inclusion | Families who CAN'T use Dinneroo at all |

---

## Key Files

| File | Purpose |
|------|---------|
| `DATA/1_SOURCE/surveys/dropoff_LATEST.csv` | Non-customer barriers |
| `DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv` | Customer improvement suggestions |
| `DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv` | Rating comments |
| `DATA/1_SOURCE/qual_research/transcripts/customer_interviews/` | 88 interview transcripts |
| `DATA/3_ANALYSIS/latent_demand_scores.csv` | Calculated demand scores |
| `DATA/3_ANALYSIS/latent_demand_summary.json` | Summary by category |

---

## Known Latent Demand (Jan 2026)

From prior analysis of 2,796 open-text responses:

| Category | Mentions | Status | Implication |
|----------|----------|--------|-------------|
| Vegetarian family options | 87 | 🔴 Major gap | Families with 1 veggie can't use Dinneroo |
| Mild/plain kids options | 48 | 🔴 Major gap | Picky eaters excluded |
| Chinese cuisine | 25 | 🟡 Underrepresented | Cultural expectation gap |
| Lasagne/comfort pasta | 22 | 🟡 Limited | "Home food" gap |
| Halal options | 12 | 🟡 Limited | Religious dietary needs |
| Fish & Chips | 7 | 🔵 Zero availability | British staple missing |
| Grilled Chicken (Nando's-style) | 5 | 🔵 Zero availability | Balanced midweek fit |
| Caribbean | 5 | 🔵 Zero availability | Cultural gap |

---

## Latent Demand Score Calculation

**Config reference:** `config/dish_scoring_unified.json` → `tracks.opportunity.components.latent_demand`

### Source Weights

| Source | Weight | Description |
|--------|--------|-------------|
| Open-text mentions | 45% | Dropoff + Post-order + Ratings comments |
| OG Survey wishlist | 30% | "Which dishes do you WANT but don't currently eat?" |
| Barrier signals | 25% | Dropoff barriers implying unmet demand |

### Scoring Formula

```
mentions_score = min(total_mentions / 50, 1.0) × 5
wishlist_score = min(wishlist_pct / 20, 1.0) × 5
barrier_score  = min(barrier_count / 100, 1.0) × 5

latent_demand_raw = (mentions_score × 0.45) + (wishlist_score × 0.30) + (barrier_score × 0.25)
latent_demand_final = max(1, min(5, round(latent_demand_raw)))
```

### Score Interpretation

| Score | Criteria |
|-------|----------|
| 5 | 20+ combined mentions OR 15%+ wishlist |
| 4 | 10-19 mentions OR 10-14% wishlist |
| 3 | 5-9 mentions OR 5-9% wishlist |
| 2 | 2-4 mentions |
| 1 | 0-1 mentions |

---

## Output Format

### Latent Demand Report

```markdown
# Latent Demand Analysis: [Topic]

## Key Findings
- [Top 3-5 unmet needs with mention counts]

## Methodology
- Sources analyzed: [list with sample sizes]
- Theme extraction method: [LLM / keyword / manual]

## Demand by Tier

### Tier 1: Optimize Existing
[Dishes we have that need work]

### Tier 2: High-Signal Gaps
[Frequently requested, not available]

### Tier 3: Cultural Inference
[Home food opportunities]

### Tier 4: Dietary Inclusion
[Who can't use Dinneroo at all]

## Recommendations
[Actionable next steps]

## Appendix: Raw Theme Extraction
[Full list of themes with quotes]
```

---

## Anti-Bias Rules

- ❌ Don't assume themes from prior analysis - extract fresh
- ❌ Don't count the same response twice across sources
- ❌ Don't conflate "would be nice" with "blocking me from ordering"
- ✅ Distinguish between "optimize existing" and "recruit new"
- ✅ Flag dietary inclusion as addressable market expansion

---

## Handoff

| Finding | Route To |
|---------|----------|
| Need to score dishes with latent demand | SCORING_AGENT |
| Need to check if dish is on Dinneroo | DISH_AGENT |
| Need zone-specific gaps | GAP_AGENT |
| Need to pull fresh rating comments | DATA_AGENT |

---

*This agent finds what order data can't see. Listen to what customers are asking for.*

