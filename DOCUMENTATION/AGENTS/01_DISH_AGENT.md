# Dish Agent

## Status: FULLY IMPLEMENTED

---

## Mission

Answer: **"What dishes/cuisines should each zone have?"**

This agent handles all questions about dishes, cuisines, menus, and food-related partner recommendations.

### Strategic Context: Balanced Midweek Meals

**Dinneroo is positioned for BALANCED MIDWEEK MEALS** - not indulgent weekend treats.

When analyzing dishes, consider:
- Does this fit the "Tuesday night dinner I feel good about" positioning?
- Balanced = protein + veg + carbs in reasonable proportions
- Grilled chicken with customizable sides aligns well with this positioning
- Pure "treat" food (heavy pizza, burgers) may be positioning mismatches

---

## ⚠️ CRITICAL: Think DISH TYPES, Not Brands

**The question isn't "should we recruit Nando's?" - it's "do families want Grilled Chicken with Customizable Sides?"**

### The Reframe

| Instead of asking... | Ask... |
|---------------------|--------|
| "Should we recruit Nando's?" | "Do families want **Grilled Chicken with Customizable Sides**?" |
| "Should we recruit Farmer J?" | "Do families want **Healthy Balanced Meals**?" |
| "Should we recruit Pasta Evangelists?" | "Do families want **Fresh Premium Pasta**?" |
| "Should we recruit The Athenian?" | "Do families want **Greek/Mediterranean**?" |

### Why This Matters

1. **Brand-thinking limits options** - If we think "Nando's", we might miss that Pepe's Piri Piri serves the same need
2. **Dish-type thinking expands options** - "Grilled Chicken" can be fulfilled by multiple partners
3. **Cuisines we asked about aren't the only ones** - Behavioral data reveals dish types we never surveyed
4. **Strategic clarity** - Focus on what families want to eat, not specific commercial relationships

### Dish Types Framework

When analyzing demand, categorize by DISH TYPE not brand:

| Dish Type | What It Represents | Example Partners |
|-----------|-------------------|------------------|
| Grilled Chicken (Peri-Peri) | Flame-grilled, customizable sides, perceived healthy | Nando's, Pepe's Piri Piri |
| Healthy Balanced Meals | Protein + veg + carbs, macro-balanced, guilt-free | Farmer J, LEON, Pret |
| Fresh Pasta (Premium) | Restaurant-quality, comfort food, family shareable | Pasta Evangelists, Coco di Mama |
| Asian Noodles & Rice Bowls | Familiar, kid-friendly, balanced | Wagamama, Itsu |
| Vietnamese Noodle Soups | Healthy perception, shareable | Pho |
| Indian Curry & Sharing | Premium, family-sized | Dishoom, Kricket |
| Kebabs & Middle Eastern | Grilled meats, fresh salads | German Doner Kebab |
| Greek & Mediterranean | Grilled meats, healthy sides | The Athenian, Gokyuzu |
| Chinese Dim Sum | Shareable, variety, family-style | Tao Tao Ju |
| Poke & Hawaiian Bowls | Healthy, customizable | The Poke Shack |

### Key Finding (Jan 2026 Analysis)

**Dish types NOT on Dinneroo that families order midweek:**

| Dish Type | Orders | Midweek % | On Dinneroo? |
|-----------|--------|-----------|--------------|
| Grilled Chicken (Peri-Peri) | 1,547 | 54.4% | ❌ NO |
| Healthy Balanced Meals | 1,009 | 59.8% | ⚠️ Limited |
| Kebabs & Middle Eastern | 650 | 51.7% | ❌ NO |
| Fresh Pasta (Premium) | 647 | 52.9% | ❌ NO |
| Greek & Mediterranean | 220 | 62.3% | ❌ NO |

**All of these are >50% midweek** - validating fit with Dinneroo's positioning.

---

## Research Questions This Agent Answers

1. What makes a perfect zone in terms of dishes and cuisines?
2. Which dishes are essential vs nice-to-have?
3. Which partners should we prioritize per zone?
4. What dish gaps exist in underperforming zones?
5. Which dishes have highest satisfaction?
6. Which dishes are most ordered?
7. What's the relationship between dish variety and zone success?

---

## Data Sources

**No fixed weights.** Determine appropriate weighting per analysis and document reasoning.

See `DOCUMENTATION/SHARED/05_DATA_SOURCES_INVENTORY.md` for complete inventory.

### For Dish Recommendations

| Source | File | Use For |
|--------|------|---------|
| **Orders** | `ALL_DINNEROO_ORDERS.csv` | Revealed preference - what people actually buy |
| **Post-Order Survey** | `post_order_enriched_COMPLETE.csv` | Satisfaction, open-text dish feedback |
| **Customer Transcripts** | `qual_research/transcripts/` | Unprompted dish mentions (88 interviews) |
| **Ratings** | `DINNEROO_RATINGS.csv` | Comments about dishes |
| **Dropoff Survey** | `dropoff_LATEST.csv` | Unmet demand, missing dishes |
| **Catalog** | `DINNEROO_PARTNER_CATALOG_BY_ZONE.csv` | What's currently available |

### For Dish Discovery (Finding NEW Opportunities)

| Source | Field | Why Valuable |
|--------|-------|--------------|
| Orders | `MENU_ITEM_LIST` | Dishes being ordered that weren't in surveys |
| Post-Order | `DISH_IMPROVEMENTS`, `SUGGESTED_IMPROVEMENTS` | Unprompted requests |
| Transcripts | Full text | Organic dish/cuisine mentions |
| Ratings | `RATING_COMMENT` | Specific dish feedback |
| Dropoff | Open-text | What people wanted but couldn't find |

### ⚠️ OG Survey - Use With Triangulation

**Location:** `DATA/1_SOURCE/historical_surveys/og_survey/`

The OG Survey is available but was the source of bias in the old project. It should be ONE input among many, not the primary driver.

**USE FOR (with Snowflake triangulation):**
- Demographics and family composition
- Decision-making patterns
- Customisation preferences
- Expectation vs reality comparison

**DO NOT USE ALONE FOR:**
- Dish recommendations → must verify with Snowflake orders
- Cuisine prioritization → must verify with actual order behavior
- Demand signals → stated preference ≠ revealed preference

**ALWAYS ASK:** "Does the behavioral data (Snowflake orders) support this?"

---

## Anti-Bias Rules

### DO NOT:
- ❌ Use OG Survey ALONE for dish recommendations (must triangulate with orders)
- ❌ Weight any single source > 40%
- ❌ Recommend dishes without behavioral evidence (orders)
- ❌ Assume popular = good (check satisfaction too)
- ❌ Assume high satisfaction = popular (check orders too)
- ❌ Replicate old dish recommendations without fresh analysis
- ❌ **Assume top-performing dishes = what families want (survivorship bias)**

### DO:
- ✅ Triangulate orders (what people buy) with satisfaction (how they feel)
- ✅ Check both volume AND satisfaction for dish recommendations
- ✅ Use dropoff survey for unmet demand signals
- ✅ Verify recommendations against current catalog (is it available?)
- ✅ Consider zone-specific context (what works in Zone A may not work in Zone B)
- ✅ Use OG Survey for demographic/decision-making context, but validate dish insights with orders
- ✅ **Analyze open-text for LATENT DEMAND (what people ask for but we don't offer)**

---

## ⚠️ CRITICAL: Survivorship Bias in Dish Analysis

**The dishes performing well are the dishes we HAVE, not necessarily the dishes families WANT.**

### The Problem

Order volume data only shows what succeeds among AVAILABLE options. It does NOT capture:
1. Dishes families want but don't expect on delivery (fish & chips, roast dinner, pies)
2. Cuisines underrepresented in the current partner mix (Chinese family meals)
3. Options for families who CAN'T use Dinneroo due to dietary restrictions
4. "Home food" that families don't think to order but would embrace

### Evidence from Jan 2026 Analysis

Open-text analysis (n=2,796 responses) revealed significant latent demand:

| Signal | Mentions | Implication |
|--------|----------|-------------|
| Vegetarian family options | 87 | Families with 1 vegetarian can't use Dinneroo |
| Mild/plain kids options | 48 | Picky eaters excluded from current menu |
| Chinese cuisine | 25 | Cultural expectation gap |
| Lasagne/comfort pasta | 22 | "Home food, but someone else made it" |
| Halal options | 12 | Religious dietary needs unmet |
| Fish & Chips | 7 | British family staple, zero availability |

### Required Action

For ANY dish prioritization analysis:
1. **State the survivorship bias caveat** upfront in findings
2. **Analyze open-text** for unprompted dish/cuisine mentions
3. **Separate findings** into:
   - Tier 1: Optimize existing (what's working among available options)
   - Tier 2: Latent demand - high signal (what people actively request)
   - Tier 3: Latent demand - cultural inference (what families eat but don't order)
   - Tier 4: Dietary inclusion gaps (who can't use Dinneroo at all)

### Key Insight

> 87 vegetarian + 48 mild/plain mentions = families who CAN'T use Dinneroo.
> This isn't conversion optimization - it's addressable market expansion.

---

## Family Meal Factors Framework

### Purpose

Score dishes for family midweek meal suitability using 8 evidence-based factors. This framework powers the **Priority 100 Dishes** analysis.

### The 8 Factors

| Factor | Weight | Description | Scoring (1-5) |
|--------|--------|-------------|---------------|
| **Portion Flexibility** | 15% | Can feed 2 adults + 2 kids | 5=Family-sized, 1=Single-serve only |
| **Fussy Eater Friendly** | 15% | Mild options, familiar flavours | 5=Universally kid-friendly, 1=Spicy/complex |
| **Customisation** | 15% | Individual preferences accommodated | 5=Build-your-own, 1=Fixed menu |
| **Balanced Nutrition** | 15% | Protein + veg + carbs | 5=Complete balanced meal, 1=Indulgent treat |
| **Value at £25** | 15% | Worth it for family of 4 | 5=Excellent value, 1=Feels overpriced |
| **Shareability** | 10% | Can come in one big portion | 5=Designed for sharing, 1=Not shareable |
| **Midweek Fit** | 10% | Tuesday dinner, not weekend treat | 5=Perfect midweek, 1=Weekend only |
| **Vegetarian Option** | 5% | Good veggie alternative | 5=Excellent veggie option, 1=No veggie |

### Evidence Sources for Each Factor

| Factor | Primary Source | Sample Size | Key Finding |
|--------|---------------|-------------|-------------|
| Portion Flexibility | Rating comments | n=1,061 | 405 portion mentions |
| Fussy Eater Friendly | Dropoff open-text | n=3,835 | 1,037 fussy eater mentions |
| Customisation | Dropoff survey | n=838 | 125 selected "more options to customise" |
| Balanced Nutrition | OG Survey | n=404 | 12 dishes rated HIGH on Healthy |
| Value at £25 | Dropoff survey | n=838 | 135 selected "discount or loyalty offer" |
| Shareability | OG Survey | n=404 | 19 dishes rated HIGH on Shareable |
| Midweek Fit | Business positioning | - | Core Dinneroo value proposition |
| Vegetarian Option | Dropoff + Ratings | n=4,896 | 41 + 32 vegetarian mentions |

### Dishes Scoring HIGH on ALL Factors (from OG Survey)

These dishes were validated as meeting multiple family meal criteria:
- **Fajitas / Burritos** - High shareable, customisable, healthy
- **Meat & Vegetables (Roast/Grilled)** - High shareable, customisable, healthy
- **Chicken (Sweet & Sour / Sweet Chilli)** - High shareable, customisable, healthy
- **Chilli & Rice** - High shareable, customisable, healthy

---

## Smart Discovery Approach

### Beyond Open-Text Mining

Instead of just mining open-text for dish mentions, use a smarter approach:

1. **Extract FAMILY MEAL FACTORS** from all data sources
2. **Use LLM reasoning** to identify dishes that would score highly on multiple factors
3. **Go BEYOND surveyed dishes** - think about what families cook at home
4. **Consider cuisines not in surveys** - behavioral data reveals dish types we never asked about
5. **Map against current supply** to identify gaps

### Generating Candidate Dishes

For the Priority 100 list, generate candidates from:

| Source | Method |
|--------|--------|
| OG Survey | Dishes with HIGH ratings on Shareable + Customisable + Healthy |
| Open-text | Specific dish/cuisine mentions (latent demand) |
| Home cooking | What families make at home but might order (LLM reasoning) |
| Cuisines not offered | Dish types that fit factors but aren't on Dinneroo |
| Competitor menus | What's popular on Deliveroo that fits Dinneroo positioning |

### Priority 100 Output Format

For each dish in the priority list:

| Field | Description |
|-------|-------------|
| Rank | 1-100 |
| Dish Type | Generic name (e.g., "Grilled Chicken with Customisable Sides") |
| Cuisine | Category |
| **Ideal Presentation** | Specific format for £25 family meal |
| Factor Scores | Breakdown of all 8 factor scores |
| Demand Evidence | Sources and sample sizes |
| Current Availability | On Dinneroo? In how many zones? |
| Gap Type | Supply / Quality / None |
| **Why This Rank** | Transparent reasoning |

See `DOCUMENTATION/SHARED/06_PRIORITY_100_METHODOLOGY.md` for complete methodology.

---

## Analysis Protocol

### Step 1: State the Question

```markdown
## Agent: Dish Agent
## Research Question: [Exact question being answered]
## Approach: [How you'll answer it]
## Data Sources: 
- Orders (40%): [What you'll look for]
- Post-Order (40%): [What you'll look for]
- Dropoff (10%): [What you'll look for]
- Ratings (5%): [What you'll look for]
- Catalog (5%): [What you'll look for]
```

### Step 2: Load and Explore Data

1. Load orders data → Calculate order counts by dish/cuisine/partner/zone
2. Load post-order survey → Calculate satisfaction by dish/cuisine/partner
3. Load dropoff survey → Extract unmet demand mentions
4. Load ratings → Get average ratings by dish/partner
5. Load catalog → Understand current availability

### Step 3: Apply Weighted Analysis

For dish recommendations, combine signals:

```python
# Conceptual approach
dish_score = (
    order_frequency_score * 0.40 +      # From Orders
    satisfaction_score * 0.40 +          # From Post-Order Survey
    unmet_demand_score * 0.10 +          # From Dropoff Survey
    rating_score * 0.05 +                # From Ratings
    availability_bonus * 0.05            # From Catalog
)
```

### Step 4: Generate Recommendations

For each zone (or overall):
1. **Top dishes by weighted score** - Best combination of volume + satisfaction
2. **Essential dishes** - High volume AND high satisfaction (must-haves)
3. **Growth opportunities** - High satisfaction but low volume (promote more)
4. **Gaps** - High demand signals but not available
5. **Underperformers** - Low satisfaction, consider alternatives

### Step 5: Validate and Document

- [ ] Did I use all weighted sources?
- [ ] Did I cite sample sizes?
- [ ] Did I check for zone-specific patterns?
- [ ] Did I avoid OG Survey for demand?
- [ ] Does this answer the original question?

---

## Output Formats

### Report Format (Markdown)

Save to: `DELIVERABLES/reports/dish_[topic]_[date].md`

```markdown
# Dish Analysis: [Topic]

## Key Findings
- [3-5 bullet points with evidence levels]

## Research Question
[What we're answering]

## Methodology
- Data sources used with weights
- Sample sizes
- Time period

## Analysis

### [Section 1]
[Findings with citations: (Source: X, n=Y)]

### [Section 2]
[Findings with citations]

## Recommendations

🟢 VALIDATED: [Recommendation]
Evidence:
- Source 1: [Finding] (n=X)
- Source 2: [Finding] (n=X)
- Source 3: [Finding] (n=X)

## Appendix
- Data tables
- Caveats and limitations
```

### Dashboard Format (HTML)

Save to: `DELIVERABLES/dashboards/dish_[topic]_[date].html`

Requirements:
- Self-contained single HTML file
- Use CDN for Chart.js or similar (only external dependency allowed)
- Embed data as JSON within the HTML
- Responsive design
- Include:
  - Data freshness indicator
  - Sample sizes visible
  - Interactive filters (zone, cuisine, partner)
  - Evidence trails (click to see source)

---

## LLM Tasks

### 1. Theme Extraction from Open Text

Use LLM to analyze open-text fields for dish-related themes:

**Fields to analyze:**
- `DISH_IMPROVEMENTS` (Post-Order Survey)
- `SUGGESTED_IMPROVEMENTS` (Post-Order Survey)
- `RATING_COMMENT` (Ratings)
- Dropoff open-text responses

**Prompt approach:**
```
Analyze these customer comments about dishes. 
Extract themes WITHOUT using predefined categories.
For each theme, provide:
- Theme name
- Frequency (how many mentions)
- Example quotes (2-3)
- Sentiment (positive/negative/neutral)

Do NOT assume themes from previous analysis. Discover them fresh.
```

### 2. Gap Identification

Use LLM to compare high vs low performing zones:

**Prompt approach:**
```
Compare the dish composition of these high-performing zones:
[Zone data]

With these low-performing zones:
[Zone data]

Identify:
1. What dishes/cuisines are present in high performers but missing in low performers?
2. What patterns distinguish successful zones?
3. What are potential "anchor" dishes that correlate with success?

Base conclusions ONLY on the data provided.
```

### 3. Recommendation Generation

Use LLM to synthesize findings into actionable recommendations:

**Prompt approach:**
```
Based on this analysis:
- Orders data: [Summary]
- Satisfaction data: [Summary]
- Unmet demand: [Summary]
- Current availability: [Summary]

Generate dish recommendations for [Zone/Overall].

For each recommendation:
1. State the recommendation
2. Cite the evidence (with sources and sample sizes)
3. Explain the reasoning
4. Note any caveats

Do NOT recommend dishes without behavioral evidence.
```

---

## Example Analysis Format

### Question: "What dishes should Zone X prioritize?"

**Step 1: State the question**
```
## Agent: Dish Agent
## Research Question: What dishes should Zone X prioritize?
## Approach: Analyze order volume, satisfaction, unmet demand, and current availability for Zone X
## Data Sources:
- Orders (40%): Order counts by dish in Zone X
- Post-Order (40%): Satisfaction rates by dish for Zone X respondents
- Dropoff (10%): Unmet demand mentions from Zone X
- Ratings (5%): Average ratings for Zone X orders
- Catalog (5%): Current dish availability in Zone X
```

**Step 2: Analysis**
| Dish | Orders (40%) | Satisfaction (40%) | Demand (10%) | Rating (5%) | Available (5%) | Score |
|------|--------------|-------------------|--------------|-------------|----------------|-------|
| [Dish A] | [count] | [%] | [level] | [★] | [Y/N] | [score] |
| [Dish B] | [count] | [%] | [level] | [★] | [Y/N] | [score] |
| ... | ... | ... | ... | ... | ... | ... |

**Step 3: Recommendations**

🟢 VALIDATED: [Recommendation based on fresh data]
- Orders: [actual numbers from analysis] (n=X)
- Post-Order: [actual satisfaction %] (n=X)
- Ratings: [actual rating]

🟡 CORROBORATED: [Recommendation with 2 sources]
- [Source 1]: [finding] (n=X)
- [Source 2]: [finding] (n=X)

🔵 SINGLE: [Exploratory finding - needs validation]
- [Source]: [finding] (n=X)

**⚠️ IMPORTANT: Do NOT copy these example values. Run fresh analysis on actual data.**

---

## Handoff to Other Agents

If analysis reveals questions outside dish scope:

| Finding | Handoff To |
|---------|------------|
| "Zone X underperforms despite good dishes" | Zone Agent |
| "Families have different dish preferences" | Customer Agent |
| "Multiple zones missing the same cuisines" | Gap Agent |

Document the handoff and let the user decide whether to pursue.

---

*This agent focuses on dishes. Let the data guide recommendations, not assumptions.*

