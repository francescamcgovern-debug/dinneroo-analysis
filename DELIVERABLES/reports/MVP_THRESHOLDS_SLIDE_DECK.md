# MVP Selection Thresholds — Slide Deck Content

**Purpose:** Content for presentation on Dinneroo zone MVP thresholds  
**For:** Formatting by colleague  
**Date:** January 2026

---

## SLIDE 1: Title

**Title:** MVP Zone Selection Thresholds

**Subtitle:** What does a zone need before we launch Dinneroo?

**Tagline:** Data-backed requirements for zone readiness

---

## SLIDE 2: The Core Question

**Title:** Selection vs Success — Two Different Questions

| Question | What We're Asking | When We Answer It |
|----------|-------------------|-------------------|
| **Selection** | "Can we launch this zone?" | Before launch |
| **Success** | "Is it working?" | After launch |

**Key Message:**  
MVP thresholds answer the **selection** question — what partners, cuisines, and dishes must be in place before we turn on a zone.

Success metrics (rating, repeat rate) tell us if our selection was right — but they're measured *after* families start ordering.

---

## SLIDE 3: MVP Selection Thresholds

**Title:** Three Requirements for Zone Launch

| Criterion | Target | What It Means |
|-----------|--------|---------------|
| **Partners** | ≥5 | Five restaurant partners offering Dinneroo bundles |
| **Cuisines** | ≥5 of 7 | Coverage across Anna's 7 cuisine categories |
| **Unique Dishes** | ≥21 | Distinct meal options within £25 bundles* |

**Footnote:**  
*A "dish" = a unique meal option families can choose (e.g., Pho, Rice Bowl, Chicken Platter) — NOT sides or components like spring rolls or prawn crackers.

**Source:** Anna's ground truth data (142 dishes across 40 partners)

---

## SLIDE 4: Why These Numbers? (Data Inflection Points)

**Title:** The Data Shows Improvement at 3+ — We Target 5+ for Redundancy

| Criterion | Data Inflection | Business Target | Why Higher? |
|-----------|-----------------|-----------------|-------------|
| **Partners** | 3+ | 5+ | Ensures availability if one partner is busy/offline |
| **Cuisines** | 3+ | 5+ | Covers diverse family preferences |
| **Dishes** | 16+ | 21+ | 3 options per cuisine for fussy eaters |

**Visual suggestion:** Show two bars per criterion — where data shows lift vs. where we set the target

---

## SLIDE 5: Behavioral Evidence — Partners

**Title:** More Partners = Dramatically More Orders

| Partner Count | Avg Orders/Zone | Repeat Rate | Zones |
|---------------|-----------------|-------------|-------|
| **10+** | 724 | 22.8% | 12 |
| **7-9** | 676 | 24.7% | 17 |
| **5-6** | 399 | 21.6% | 27 |
| **3-4** | 262 | 18.4% | 46 |
| **1-2** | 44 | 13.9% | 95 |

**Key Stat:**  
Zones with 5+ partners have **8x more orders** than zones with 1-2 partners

**Inflection Point:**  
Moving from 1-2 → 3-4 partners shows **+4.5pp repeat rate**

**Source:** Snowflake orders (n=57,320 orders across 197 zones)

---

## SLIDE 6: Behavioral Evidence — Cuisines

**Title:** More Cuisines = Higher Orders and Ratings

| Cuisine Count | Avg Orders/Zone | Avg Rating | Zones |
|---------------|-----------------|------------|-------|
| **7+** | 802 | 4.47 | 17 |
| **5-6** | 491 | 4.40 | 24 |
| **3-4** | 296 | 4.35 | 54 |
| **1-2** | 224 | 4.25 | 7 |

**Key Stat:**  
5 cuisines vs 4 cuisines = **+34% orders** and **+0.09 rating**

**Inflection Point:**  
Moving from 3-4 → 5-6 cuisines shows **+4.2pp repeat rate**

**Source:** Snowflake orders, zones with 3+ partners (n=102 zones)

**Note:** Analysis controls for partner count to isolate cuisine effect

---

## SLIDE 7: Behavioral Evidence — Dishes per Partner

**Title:** Menu Depth Drives Satisfaction

| Dishes/Partner | Avg Rating | Kids Happy | Zones |
|----------------|------------|------------|-------|
| **6+** | 4.44 | 76% | 41 |
| **5-6** | 4.40 | 67% | 24 |
| **4-5** | 4.36 | 61% | 15 |
| **3-4** | 4.24 | 84%* | 14 |

*Small sample (n=41) — interpret with caution

**Key Stat:**  
Partners with 5+ dishes/partner show **+12.1pp rating improvement**

**Why It Matters:**  
More dishes per partner = more choice within the £25 bundle for families with fussy kids or dietary needs

**Source:** Snowflake + Post-Order Survey (n=94 zones with 3+ partners and 3+ cuisines)

---

## SLIDE 8: Consumer Validation — Cuisine Impact

**Title:** Families in 5+ Cuisine Zones Are Happier

| Metric | 5+ Cuisines | 3-4 Cuisines | 1-2 Cuisines |
|--------|-------------|--------------|--------------|
| **Kids Happy** | 82% | 78% | 80%* |
| **Reorder Intent** | 79% | 70% | 82%* |
| **Variety Complaints** | 17% | 17% | 15%* |

*1-2 cuisine sample is small (n=27) — interpret with caution

**Sample Sizes:**
- 5+ cuisines: n=699-811 responses
- 3-4 cuisines: n=510-551 responses

**Source:** Post-Order Survey joined to zone data

---

## SLIDE 9: Consumer Validation — Variety Demand

**Title:** 1 in 6 Dropoffs Want More Variety

**From Dropoff Survey (n=942 responses):**

| Response | % |
|----------|---|
| "Wider variety would make me order" | **17.2%** |
| "Variety is great" | 13.0% |
| Other reasons | 69.8% |

**Key Insight:**  
Variety is a real barrier for ~17% of dropoffs — more cuisines and dishes directly addresses this.

**Source:** Dropoff Survey (closed-response question)

---

## SLIDE 10: The 7 Cuisines

**Title:** Anna's 7 Cuisine Categories (Source of Truth)

| Cuisine | Example Dishes | Notes |
|---------|----------------|-------|
| **Asian** | Pho, Pad Thai, Rice Bowls, Katsu | Includes Japanese, Vietnamese, Thai, Chinese, Korean |
| **Italian** | Pizza, Pasta, Lasagne | Universal kid appeal |
| **Indian** | Curry, Biryani, Tikka Masala | Great portions, mild options available |
| **Healthy** | Grain Bowls, Protein & Veg, Salads | Appeals to health-conscious parents |
| **Mexican** | Burritos, Tacos, Quesadilla | High customisation for fussy eaters |
| **Middle Eastern** | Shawarma, Falafel, Kebab | Growing family favourite |
| **British** | Shepherd's Pie, Fish & Chips, Roasts | Comfort food, familiar |

**MVP Target:** 5 of 7 cuisines covered

**Source:** Anna's categorisation from Dish Analysis Dec-25

---

## SLIDE 11: What is a "Dish"?

**Title:** Dish Definition — Unique Meals, Not Sides

**A dish = a meal option within a Dinneroo £25 family bundle**

**Example: Pho Family Bundle (£25)**

| Item | Counted as Dish? |
|------|------------------|
| Adult: Pho soup | ✅ Yes |
| Kid: Rice bowl | ✅ Yes |
| Sides: Spring rolls | ❌ No |
| Sides: Prawn crackers | ❌ No |

**This bundle = 2 dishes**

**Example: Dishes per Partner**

| Partner | Unique Dishes |
|---------|---------------|
| Pho | Pho, Rice Bowl, Pad Thai, Kids Noodles = **4 dishes** |
| Nando's | Chicken Platter, Wrap, Kids Chicken, Veggie = **4 dishes** |

**Current Supply:** 142 unique dishes across 40 partners

---

## SLIDE 12: Summary — MVP Selection Checklist

**Title:** Zone Launch Checklist

| ✓ | Requirement | Target |
|---|-------------|--------|
| ☐ | Partners | ≥5 |
| ☐ | Cuisines (of 7) | ≥5 |
| ☐ | Unique Dishes | ≥21 |

**If all three are met → Zone is MVP Ready for launch**

**After Launch — Track Success:**
- Rating ≥4.0
- Repeat Rate ≥35%

---

## SLIDE 13: Data Sources

**Title:** Where This Comes From

| Data Type | Source | Sample Size |
|-----------|--------|-------------|
| **Supply** (partners, cuisines, dishes) | Anna's ground truth | 1,306 zones, 40 partners, 142 dishes |
| **Behavioral** (orders, ratings, repeat) | Snowflake | 57,320 orders, 197 zones |
| **Consumer** (satisfaction, intent) | Post-Order Survey | ~1,000 responses |
| **Dropoff** (variety demand) | Dropoff Survey | 942 responses |
| **Inflection Analysis** | MVP Threshold Discovery | 197 zones |

**Key Files:**
- `config/mvp_thresholds.json` — Business targets
- `DATA/3_ANALYSIS/mvp_threshold_discovery.json` — Data-driven inflection points
- `docs/data/mvp_consumer_validation.json` — Survey validation

---

## END OF DECK

**Questions to address in Q&A:**

1. Why 5+ when data shows improvement at 3+?
   → Redundancy and availability — if one partner is offline, families still have choice

2. Why is repeat rate not part of MVP selection?
   → It's a success metric measured after launch, not something we control before launch

3. What about the 35% repeat rate target?
   → That's our north star for success — current top zones are at ~24%, so this is aspirational

---

*Document created for formatting into presentation slides*


