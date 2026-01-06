# Dish Scoring Methodology

## Purpose

This document describes the complete methodology for scoring and prioritizing dishes for Dinneroo using the **Two-Track Scoring System** and **10-Factor Family Meal Framework**.

---

## Two-Track Scoring System

### Why Two Tracks?

**A single blended score creates survivorship bias.** If we score dishes based on performance data (orders, ratings), unavailable dishes automatically score poorly - not because families don't want them, but because they CAN'T order them.

### The Solution: Separate Performance from Opportunity

```
┌─────────────────────────────────────────────────────────────────┐
│  TRACK A: PERFORMANCE SCORE                                     │
│  "How well is this dish doing?"                                 │
│  - Only for dishes with 50+ orders                              │
│  - Repeat rate, rating (4.5+ threshold), satisfaction           │
│  - Used to: Identify winners to expand, underperformers to fix  │
├─────────────────────────────────────────────────────────────────┤
│  TRACK B: OPPORTUNITY SCORE                                     │
│  "How much do families want this?"                              │
│  - For ALL dish types (including unavailable)                   │
│  - Latent demand, 10-factor fit, partner capability             │
│  - Used to: Identify gaps to fill, new dishes to recruit        │
└─────────────────────────────────────────────────────────────────┘
```

### How to Interpret Both Tracks

| Track A (Performance) | Track B (Opportunity) | Interpretation | Action |
|-----------------------|----------------------|----------------|--------|
| High | Any | Proven winner | **Expand** to more zones |
| N/A (not available) | High | High-demand gap | **Recruit** partners to offer |
| Low | High | Something's wrong | **Investigate** mismatch |
| Low | Low | Not working, not wanted | **Fix** or deprioritize |

### Track A: Performance Score Components

For dishes with **50+ orders**, calculate:

| Metric | Source | Weight | Threshold |
|--------|--------|--------|-----------|
| Repeat Rate | Snowflake orders | 30% | 35%+ = good |
| Average Rating | Snowflake ratings | 30% | **4.5+** = good (Deliveroo standard) |
| Adult Satisfaction | Post-order survey | 15% | 80%+ "Loved/Liked it" |
| Kids Happy Rate | Post-order survey | 15% | 70%+ "Full and happy" |
| Portions Adequate | Post-order survey | 10% | 80%+ "Agree/Strongly agree" |

### Track B: Opportunity Score Components

For **ALL dish types** (including unavailable):

| Component | Source | Weight | How Measured |
|-----------|--------|--------|--------------|
| Latent Demand | Dropoff survey, comments | 30% | Mention count + sentiment |
| 10-Factor Framework Fit | Framework scoring | 30% | Weighted factor score |
| Partner Capability | Menu catalog + LLM | 20% | Could existing partners make this? |
| Cuisine Gap Priority | Gap analysis | 20% | Supply/quality gap status |

### Smart Discovery Layer

The LLM is used to **discover new dishes** (not just score existing ones):

1. **Partner Capability Analysis**: What dishes could existing partners realistically make?
   - Example: Dishoom → Biryani Family Pot (not currently on menu but fits their capability)
   
2. **Family Factor Gaps**: What dish types would fill unmet needs?
   - Example: No good vegetarian mains → Halloumi Wrap Family Bundle
   
3. **Cuisine Gap Filling**: What dishes address supply/quality gaps?
   - Example: Chinese = Supply Gap → Sweet & Sour Chicken Family Meal

Discovery dishes are flagged separately with clear LLM reasoning documented.

---

## Strategic Context: Balanced Midweek Meals

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

---

## ⚠️ CRITICAL: Survivorship Bias

**The dishes performing well are the dishes we HAVE, not necessarily the dishes families WANT.**

### The Problem

Order volume data only shows what succeeds among AVAILABLE options. It does NOT capture:
1. Dishes families want but don't expect on delivery (fish & chips, roast dinner, pies)
2. Cuisines underrepresented in the current partner mix (Chinese family meals)
3. Options for families who CAN'T use Dinneroo due to dietary restrictions
4. "Home food" that families don't think to order but would embrace

### Evidence from Analysis

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

---

## The 10-Factor Family Meal Framework

### Factor Definitions

| Factor | Weight | Description |
|--------|--------|-------------|
| **Kid-Friendly** | 15% | Kids will actually eat it - familiar flavours, not too spicy |
| **Balanced/Guilt-Free** | 12% | Parents feel good serving it on a Tuesday |
| **Adult Appeal** | 8% | Adults enjoy it too - important for non-parent orderers |
| **Portion Flexibility** | 15% | Can feed 2 adults + 2 kids appropriately |
| **Fussy Eater Friendly** | 15% | Mild options available, customisable for picky kids |
| **Customisation** | 10% | Individual preferences can be accommodated |
| **Value at £25** | 10% | Feels worth it for a family of 4 |
| **Shareability** | 5% | Can come in one big portion for family sharing |
| **Vegetarian Option** | 5% | Good veggie alternative available |
| **On Dinneroo Menu** | 5% | Actually available (verified against catalog) |

**Total: 100%**

**Note:** Weights are configurable in `config/factor_weights.json`. Different stakeholders may weight factors differently.

---

## Factor Scoring Details

### Kid-Friendly (15%)

**What it means:** Kids will actually eat this dish - this is the #1 success factor for Dinneroo.

**Evidence:**
- Post-order survey: "kids eating it is the main factor that dictates success"
- Dropoff survey: 1,037 mentions of fussy eaters as a barrier
- Customer transcripts: Parents repeatedly cite kid acceptance as #1 concern

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Universally kid-friendly, mild by default, familiar | Plain pasta, chicken nuggets, mild katsu |
| 4 | Most kids will eat, familiar ingredients | Rice bowls, wraps, mild curry with rice |
| 3 | Some kids will eat with mild option | Pho (familiar noodles), fajitas |
| 2 | Adventurous kids only, unfamiliar ingredients | Sushi, Thai green curry |
| 1 | Not kid-friendly, spicy/complex flavours | Very spicy dishes, unusual textures |

---

### Balanced/Guilt-Free (12%)

**What it means:** Parents feel good serving this on a Tuesday - not a treat, a proper meal.

**Evidence:**
- Dinneroo strategic positioning: "balanced midweek meals" is core value prop
- Rating comments: 186 mentions of "healthy" or "balanced"
- Cannibalization analysis: Dinneroo is 98% midweek orders

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Clearly balanced, visible protein + veg + carbs | Grain bowls, grilled chicken + veg + rice |
| 4 | Mostly balanced, some vegetables included | Katsu with veg side, pasta with salad |
| 3 | Neutral - can go either way | Noodle dishes, rice bowls |
| 2 | Indulgent but has some redeeming qualities | Pizza with salad, quality burger |
| 1 | Pure treat/indulgence | Wings, loaded fries, fried chicken bucket |

---

### Adult Appeal (8%)

**What it means:** Adults enjoy it too - not just "kids menu" food.

**Evidence:**
- Order data shows non-parents also order Dinneroo
- Customer transcripts: Parents want food THEY enjoy
- Brand perception: "Family food" shouldn't mean "boring food"

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Restaurant-quality that adults actively want | Dishoom curry, quality pasta, authentic pho |
| 4 | Adults genuinely enjoy it, good flavours | Good katsu, well-made fajitas |
| 3 | Adults tolerate it, basic but acceptable | Standard pizza, basic noodles |
| 2 | More kid-focused, adults wouldn't choose it | Chicken nuggets, very plain pasta |
| 1 | Adults wouldn't order this for themselves | Very basic/bland options |

---

### Portion Flexibility (15%)

**What it means:** Can appropriately feed 2 adults + 2 kids.

**Evidence:**
- Rating comments: 405 mentions of portions
- Post-order survey: Portion size is key satisfaction driver
- £25 price point: Must feel like good value for family of 4

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Explicitly designed for 4 people, family-sized | "Family Feast for 4", sharing platters |
| 4 | Sharing platters or 4 individual portions work | Rice bowl bundle x4, wrap box |
| 3 | Can be ordered in quantities for 4 | Order 4x individual dishes |
| 2 | Individual portions only, awkward for family | Single-serve meals |
| 1 | Single-serve only, not suitable for sharing | Individual snacks |

---

### Fussy Eater Friendly (15%)

**What it means:** Mild options available, customisable for picky kids.

**Evidence:**
- Dropoff survey: 1,037 mentions of fussy eaters as barrier
- Customer transcripts: "My kids won't eat anything spicy/unusual"

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Mild by default, universally appealing | Plain pasta, chicken + rice |
| 4 | Mild option available, familiar ingredients | Katsu (mild sauce), fajitas (plain option) |
| 3 | Can be made mild on request | Curry with "mild" option |
| 2 | Some unfamiliar ingredients, may need adaptation | Pho, sushi |
| 1 | Spicy/complex by nature, difficult to adapt | Thai green curry, Korean fried chicken |

---

### Customisation (10%)

**What it means:** Individual preferences can be accommodated.

**Evidence:**
- Dropoff survey: 125 selected "more options to customise"
- Customer transcripts: Families have mixed preferences

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Build-your-own format, fully customisable | Fajita kit, poke bowl, wrap bar |
| 4 | Multiple options/swaps available | Rice bowl with choice of protein |
| 3 | Some customisation possible | Sides can be swapped |
| 2 | Limited customisation | Fixed menu with few options |
| 1 | No customisation, take it or leave it | Set meal, no changes |

---

### Value at £25 (10%)

**What it means:** Feels worth it for a family of 4 at the £25 price point.

**Evidence:**
- Dropoff survey: 135 selected "discount or loyalty offer"
- Rating comments: 212 mentions of value/price

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Excellent value, generous portions, premium feel | Large sharing platter, "feast" format |
| 4 | Good value, appropriate portions for £25 | Family bundle deals |
| 3 | Fair value, meets expectations | Standard family meal |
| 2 | Slightly expensive for what you get | Premium items that feel small |
| 1 | Poor value, feels overpriced at £25 | Small portions, basic ingredients |

---

### Shareability (5%)

**What it means:** Can come in one big portion for family sharing.

**Evidence:**
- OG Survey: 19 dishes rated HIGH on "Shareable"
- Customer transcripts: Some families prefer communal eating

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Designed for sharing, communal eating | Mezze platter, family curry pot |
| 4 | Works well as shared meal | Large pizza, sharing noodles |
| 3 | Can be shared with some effort | Rice bowls in centre of table |
| 2 | Better as individual portions | Wraps, individual bowls |
| 1 | Not suitable for sharing | Single-serve items |

---

### Vegetarian Option (5%)

**What it means:** Good veggie alternative available (not an afterthought).

**Evidence:**
- Dropoff survey: 41 vegetarian mentions
- Rating comments: 32 vegetarian mentions

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Excellent veggie option, equally appealing | Veggie fajitas, halloumi wrap |
| 4 | Good veggie alternative available | Veggie katsu, vegetable curry |
| 3 | Basic veggie option exists | Cheese pizza, plain pasta |
| 2 | Limited veggie options, afterthought | Side salad only |
| 1 | No veggie option | Meat-only dish |

---

### On Dinneroo Menu (5%)

**What it means:** Actually available on Dinneroo (verified against catalog).

**Source:** `DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv`

**Scoring (1-5):**
| Score | Criteria |
|-------|----------|
| 5 | Widely available (50+ menu items across partners) |
| 4 | Good availability (20-49 menu items) |
| 3 | Some availability (5-19 menu items) |
| 2 | Limited availability (1-4 menu items) |
| 1 | Not on Dinneroo menu (gap) |

---

## Survey-Backed Scoring

### Overview

Where possible, factor scores are derived from **actual survey outcomes** rather than estimates.

### Evidence Types

| Type | Definition | Reliability |
|------|------------|-------------|
| **Measured** | 3+ factors have direct survey data (n≥5 per dish) | High |
| **Blended** | 1-2 factors have survey data, rest estimated | Medium |
| **Estimated** | No matching survey data available | Lower |

### Survey Data Mapping

| Factor | Survey Question | Calculation |
|--------|----------------|-------------|
| **Kid-Friendly** | "How did your child(ren) react to the meal?" | % "full and happy" |
| **Adult Appeal** | "How did you feel about the meal?" | % "Loved it" or "Liked it" |
| **Portion Flexibility** | "There was enough food for everyone" | % "Agree" or "Strongly agree" |
| **Value at £25** | "Good value for money" (dish choice reason) | % who selected |
| **Balanced/Guilt-Free** | "Healthy option" (dish choice reason) | % who selected |

### Score Conversion

| Success Rate | Score |
|--------------|-------|
| 90-100% | 5 |
| 75-89% | 4 |
| 60-74% | 3 |
| 40-59% | 2 |
| 0-39% | 1 |

---

## Composite Score Calculation

```
Composite Score = 
  (Kid-Friendly × 0.15) +
  (Balanced/Guilt-Free × 0.12) +
  (Adult Appeal × 0.08) +
  (Portion Flexibility × 0.15) +
  (Fussy Eater Friendly × 0.15) +
  (Customisation × 0.10) +
  (Value at £25 × 0.10) +
  (Shareability × 0.05) +
  (Vegetarian Option × 0.05) +
  (On Dinneroo Menu × 0.05)
```

---

## Output Format

### Priority Dishes Table

| Field | Description |
|-------|-------------|
| **Rank** | Position in list |
| **Dish Type** | Generic name (e.g., "Grilled Chicken with Customisable Sides") |
| **Cuisine** | Category |
| **Factor Scores** | Individual scores for all 10 factors (1-5 each) |
| **Composite Score** | Weighted total |
| **Evidence Type** | Measured / Blended / Estimated |
| **On Dinneroo Menu** | Yes/No + item count |
| **Ideal Presentation** | How to prepare for £25 family meal |

---

## Implementation

### Script Location

`scripts/phase2_analysis/01_score_dishes.py`

### Configuration

`config/factor_weights.json` - Contains all factor weights and definitions

### Quality Checks

Before finalizing:
- [ ] List includes dishes NOT in original survey
- [ ] Each dish has scores on all 10 factors
- [ ] Factor scores are evidence-based where possible
- [ ] No brand names in dish types
- [ ] Menu availability verified against catalog

---

*This methodology ensures dish prioritization is based on what families actually need, with transparent and adjustable weighting.*

