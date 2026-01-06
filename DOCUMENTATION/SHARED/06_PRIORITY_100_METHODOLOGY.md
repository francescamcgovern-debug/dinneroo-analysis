# Priority Dishes Methodology

## Purpose

This document describes the complete methodology for generating the **Priority Dishes** list - a ranked list of dish types families want, with ideal presentations for £25 family meals.

---

## Philosophy: Smart Discovery

The Priority Dishes approach goes beyond simple open-text mining or survey replication. It uses:

1. **Family Meal Factors Framework** - 10 evidence-based factors for scoring dishes
2. **LLM Reasoning** - Generate candidate dishes based on factors, not just mentions
3. **Supply Mapping** - Deep understanding of current Dinneroo supply by zone
4. **Gap Analysis** - Identify where supply doesn't meet demand

### Why This Approach?

| Old Approach | New Approach |
|--------------|--------------|
| Mine open-text for dish mentions | Extract FACTORS families care about |
| Limited to surveyed dishes | Generate candidates beyond surveys |
| Brand-focused ("recruit Nando's") | Dish-type focused ("Grilled Chicken with Sides") |
| Survivorship bias (what we have) | Include latent demand (what families want) |

---

## The Family Meal Factors Framework

### The 10 Factors

| Factor | Default Weight | Description |
|--------|----------------|-------------|
| **Kid-Friendly** | 15% | Kids will actually eat it - familiar flavours, not too spicy |
| **Balanced/Guilt-Free** | 12% | Parents feel good serving it on a Tuesday |
| **Adult Appeal** | 8% | Adults enjoy it too - important for non-parent orderers |
| **Portion Flexibility** | 15% | Can feed 2 adults + 2 kids appropriately |
| **Fussy Eater Friendly** | 15% | Mild options available, customisable for picky kids |
| **Customisation** | 10% | Individual preferences can be accommodated |
| **Value at £25** | 10% | Feels worth it for a family of 4 |
| **Shareability** | 5% | Can come in one big portion for family sharing |
| **Vegetarian Option** | 5% | Good veggie alternative available |
| **On Dinneroo Menu** | 5% | Actually available (not a gap) |

**Total: 100%**

**Note:** These weights are adjustable in the dashboard. Different stakeholders may weight factors differently based on strategic priorities.

---

## Factor Definitions and Evidence

### Kid-Friendly (15%)

**What it means:** Kids will actually eat this dish - this is the #1 success factor for Dinneroo.

**How we know:**
- Post-order survey feedback: "kids eating it is the main factor that dictates success"
- Dropoff survey: 1,037 mentions of fussy eaters as a barrier to ordering
- Customer transcripts: Parents repeatedly cite kid acceptance as their #1 concern
- Order data: Dishes with kid-friendly attributes have higher repeat rates

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Universally kid-friendly, mild by default, familiar presentation | Plain pasta, chicken nuggets, mild katsu curry |
| 4 | Most kids will eat, familiar ingredients, appealing look | Rice bowls, wraps, mild curry with rice |
| 3 | Some kids will eat with mild option or adaptation | Pho (familiar noodles), fajitas (build-your-own) |
| 2 | Adventurous kids only, unfamiliar ingredients | Sushi, Thai green curry, Korean dishes |
| 1 | Not kid-friendly, spicy/complex flavours | Very spicy dishes, unusual textures, strong flavours |

---

### Balanced/Guilt-Free (12%)

**What it means:** Parents feel good serving this on a Tuesday - not a treat, a proper meal.

**How we know:**
- Dinneroo strategic positioning: "balanced midweek meals" is the core value prop
- Rating comments: 186 mentions of "healthy" or "balanced" in feedback
- Dropoff survey: Families specifically want nutritious options for midweek
- Cannibalization analysis: Dinneroo is 98% midweek orders - this IS the occasion

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Clearly balanced meal, visible protein + veg + carbs, grilled/healthy | Grain bowls, grilled chicken + veg + rice |
| 4 | Mostly balanced, some vegetables included, not too heavy | Katsu with veg side, pasta with salad |
| 3 | Neutral - can go either way depending on presentation | Noodle dishes, rice bowls |
| 2 | Indulgent but has some redeeming qualities | Pizza with salad, quality burger |
| 1 | Pure treat/indulgence, not a balanced meal | Wings, loaded fries, fried chicken bucket |

---

### Adult Appeal (8%)

**What it means:** Adults enjoy it too - not just "kids menu" food.

**How we know:**
- Order data shows non-parents also order Dinneroo (they want quality food at good value)
- Customer transcripts: Parents explicitly say they want food THEY enjoy, not just kid-friendly
- Post-order survey: Adult satisfaction correlates with repeat orders
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

**What it means:** Can appropriately feed 2 adults + 2 kids (or other family configurations).

**How we know:**
- Rating comments: 405 mentions of portions (too much, too little, just right)
- Post-order survey: Portion size is a key satisfaction driver
- £25 price point: Must feel like good value for family of 4

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Explicitly designed for 4 people, family-sized | "Family Feast for 4", sharing platters |
| 4 | Sharing platters or 4 individual portions work well | Rice bowl bundle x4, wrap box |
| 3 | Can be ordered in quantities for 4 | Order 4x individual dishes |
| 2 | Individual portions only, awkward for family | Single-serve meals |
| 1 | Single-serve only, not suitable for family sharing | Individual snacks |

---

### Fussy Eater Friendly (15%)

**What it means:** Mild options available, customisable for picky kids.

**How we know:**
- Dropoff survey: 1,037 mentions of fussy eaters as barrier
- Customer transcripts: "My kids won't eat anything spicy/unusual"
- This overlaps with Kid-Friendly but specifically about having OPTIONS for picky eaters

**Scoring (1-5):**
| Score | Criteria | Examples |
|-------|----------|----------|
| 5 | Mild by default, universally appealing, no "scary" ingredients | Plain pasta, chicken + rice |
| 4 | Mild option available, familiar ingredients throughout | Katsu (mild sauce), fajitas (plain option) |
| 3 | Can be made mild on request | Curry with "mild" option |
| 2 | Some unfamiliar ingredients, may need adaptation | Pho, sushi |
| 1 | Spicy/complex by nature, difficult to adapt | Thai green curry, Korean fried chicken |

---

### Customisation (10%)

**What it means:** Individual preferences can be accommodated within the order.

**How we know:**
- Dropoff survey: 125 selected "more options to customise" as improvement
- Customer transcripts: Families have mixed preferences (one kid likes X, other likes Y)
- Build-your-own formats consistently score well

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

**How we know:**
- Dropoff survey: 135 selected "discount or loyalty offer" as motivator
- Rating comments: 212 mentions of value/price
- £25 is the Dinneroo promise - must deliver perceived value

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

**What it means:** Can come in one big portion for family sharing at the table.

**How we know:**
- OG Survey: 19 dishes rated HIGH on "Shareable"
- Customer transcripts: Some families prefer communal eating
- Cultural context: Many cuisines are traditionally shared

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

**How we know:**
- Dropoff survey: 41 vegetarian mentions
- Rating comments: 32 vegetarian mentions
- Customer transcripts: Mixed households need options

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

**What it means:** Actually available on Dinneroo (verified against menu catalog).

**How we know:**
- `DINNEROO_MENU_CATALOG.csv` - the source of truth for what's actually available
- Important: Partners may serve different items on Dinneroo vs regular Deliveroo

**Scoring (1-5):**
| Score | Criteria |
|-------|----------|
| 5 | Widely available (50+ menu items across partners) |
| 4 | Good availability (20-49 menu items) |
| 3 | Some availability (5-19 menu items) |
| 2 | Limited availability (1-4 menu items) |
| 1 | Not on Dinneroo menu (gap) |

---

## Evidence Sources Summary

| Factor | Primary Source | Sample Size | Key Finding |
|--------|---------------|-------------|-------------|
| Kid-Friendly | Post-order + Transcripts | n=1,564 + 88 | #1 success factor cited by parents |
| Balanced/Guilt-Free | Rating comments | n=1,061 | 186 healthy/balanced mentions |
| Adult Appeal | Transcripts + Orders | n=88 + 71k | Parents want quality, not just "kids food" |
| Portion Flexibility | Rating comments | n=1,061 | 405 portion mentions |
| Fussy Eater Friendly | Dropoff open-text | n=3,835 | 1,037 fussy eater mentions |
| Customisation | Dropoff survey | n=838 | 125 selected "more options to customise" |
| Value at £25 | Dropoff + Ratings | n=838 + 1,061 | 135 + 212 value mentions |
| Shareability | OG Survey | n=404 | 19 dishes rated HIGH on Shareable |
| Vegetarian Option | Dropoff + Ratings | n=4,896 | 41 + 32 vegetarian mentions |
| On Dinneroo Menu | Menu catalog | 2,490 items | Verified availability |

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

**Note:** Weights are adjustable in the dashboard. Use the sliders to test different weightings and see how rankings change.

---

## Output Format

### Priority Dishes Table

For each dish in the priority list:

| Field | Description |
|-------|-------------|
| **Rank** | Position in list |
| **Dish Type** | Generic name (e.g., "Grilled Chicken with Customisable Sides") |
| **Cuisine** | Category |
| **Factor Scores** | Individual scores for all 10 factors (1-5 each) |
| **Composite Score** | Weighted total |
| **On Dinneroo Menu** | Yes/No + item count |
| **Dinneroo Guidance** | How to prepare this dish for Dinneroo success |

### Dinneroo Preparation Guidance

For each dish, guidance on how it should be made for Dinneroo:
- Kid-friendly adaptations (mild options, familiar presentation)
- Portion format (family platter, 4 individual, sharing pot)
- Customisation options (build-your-own, sides, sauces on side)
- Balanced presentation (visible veg, protein + carbs)

---

## Quality Checks

Before finalizing the Priority Dishes:

- [ ] List includes dishes NOT in original survey
- [ ] Each dish has scores on all 10 factors
- [ ] Factor scores are evidence-based, not guessed
- [ ] Dinneroo guidance is actionable
- [ ] No brand names in dish types
- [ ] Menu availability verified against catalog

---

## Survey-Backed Scoring (v3.0)

### Overview

Where possible, factor scores are derived from **actual survey outcomes** rather than estimates. This provides more accurate scoring based on real family feedback.

### Evidence Types

| Type | Definition | Reliability |
|------|------------|-------------|
| **Measured** | 3+ factors have direct survey data (n≥5 per dish) | High - based on actual outcomes |
| **Blended** | 1-2 factors have survey data, rest estimated | Medium - partial validation |
| **Estimated** | No matching survey data available | Lower - based on dish characteristics |

### Survey Data Used

| Factor | Survey Question | Calculation |
|--------|----------------|-------------|
| **Kid-Friendly** | "How did your child(ren) react to the meal?" | % "full and happy" responses |
| **Adult Appeal** | "How did you feel about the meal?" | % "Loved it" or "Liked it" |
| **Portion Flexibility** | "There was enough food for everyone" | % "Agree" or "Strongly agree" |
| **Value at £25** | "Good value for money" (dish choice reason) | % who selected this reason |
| **Balanced/Guilt-Free** | "Healthy option" (dish choice reason) | % who selected this reason |

### Score Conversion

Survey success rates are converted to 1-5 scores:

| Success Rate | Score |
|--------------|-------|
| 90-100% | 5 |
| 75-89% | 4 |
| 60-74% | 3 |
| 40-59% | 2 |
| 0-39% | 1 |

### Sample Size Requirements

- Minimum 5 survey responses per dish to use measured scores
- Dishes with fewer responses use estimated scores
- Survey sample sizes are recorded in `survey_sample_size` column

### Key Findings from Survey Data

| Restaurant | Kid Success Rate | Sample Size |
|------------|-----------------|-------------|
| Las Iguanas | 92.9% | n=14 |
| Iro Sushi | 90.9% | n=11 |
| Banana Tree | 86.4% | n=44 |
| PizzaExpress | 80.6% | n=72 |
| Pho | 78.3% | n=115 |
| Wagamama | 75.9% | n=195 |

**Top dishes by "kids full & happy":**
- Rice bowls: 100% (n=5)
- Pho: 87.5% (n=8)
- Curry: 83.3% (n=12)
- Katsu curry: 82.1% (n=39)
- Sushi: 80% (n=15)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-05 | Initial methodology with 8 factors |
| 2.0 | 2026-01-05 | Split Midweek Fit into 3 explicit factors (Kid-Friendly, Balanced/Guilt-Free, Adult Appeal). Now 10 factors total. Added interactive weight sliders. |
| 3.0 | 2026-01-05 | Survey-backed scoring: Replace estimated scores with actual survey outcomes where available. Added evidence_type and survey_sample_size columns. |

---

*This methodology ensures dish prioritization is based on what families actually need, with transparent and adjustable weighting. Where possible, scores are measured from actual survey outcomes rather than estimated.*
