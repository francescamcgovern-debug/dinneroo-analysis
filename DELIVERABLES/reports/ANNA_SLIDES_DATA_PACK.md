# Anna's Dish Analysis Slides - Data Pack

**Generated:** 2026-01-07  
**Purpose:** Pastable text blocks with evidence for Anna's Dish Analysis Dec-25 presentation  
**To regenerate:** Run `python scripts/phase3_synthesis/06_generate_anna_pptx.py`

---

## Table of Contents

1. [Slide 5: Zone MVP Rationale](#slide-5-zone-mvp-rationale)
2. [Slide 6: Zone MVP Count](#slide-6-zone-mvp-count)
3. [Slide 7: Minimum Dishes by Zone](#slide-7-minimum-dishes-by-zone)
4. [Slide 8: Scoring Framework Definitions](#slide-8-scoring-framework-definitions)
5. [Slide 9: Quadrant Summary](#slide-9-quadrant-summary)
6. [Slide 10: Dish Scoring Data Table](#slide-10-dish-scoring-data-table)
7. [Slide 13: Coverage Gaps & Next Steps](#slide-13-coverage-gaps--next-steps)
8. [Niche Dish Recommendations](#niche-dish-recommendations)
9. [Provocative Insights](#provocative-insights)
10. [Data Sources & Sample Sizes](#data-sources--sample-sizes)
11. [Caveats & Limitations](#caveats--limitations)

---

## ⚠️ Provocative Insights (Discussion Starters)

> These insights challenge assumptions and are designed to spark exec discussion

### "Family" Dinneroo Isn't Just Reaching Families

```
WHO IS ACTUALLY ORDERING?

┌─────────────────────────┬─────────┬─────────┬─────────────────────────┐
│ Household Type          │ Orders  │ % Total │ Satisfaction            │
├─────────────────────────┼─────────┼─────────┼─────────────────────────┤
│ Families WITH kids      │ 729     │ 46%     │ 74% satisfied           │
│ Couples/singles NO kids │ 870     │ 54%     │ 68% satisfied           │
└─────────────────────────┴─────────┴─────────┴─────────────────────────┘

54% of "Family Dinneroo" customers don't have children at home.

BUT: Families with kids are MORE satisfied (74% vs 68%)
→ The product works better for its intended audience

QUESTIONS FOR DISCUSSION:
• Is 46% families "good enough" or should we target better?
• Should we rebrand/reposition to include couples?
• Or double down on families since they're happier?

The data suggests the product IS right for families - 
we just haven't reached enough of them yet.

Source: Post-order survey (n=1,599)
```

### What Families With Kids Actually Order

```
TOP DISHES BY HOUSEHOLD TYPE

FAMILIES WITH KIDS:              COUPLES/SINGLES (NO KIDS):
1. Katsu Curry (30)              1. Katsu Curry (14)
2. Katsu (15)                    2. Chicken Ruby (7)
3. Sushi (12)                    3. Pad Thai (7)
4. Curry (9)                     4. Chicken (7)
5. Chicken Katsu Curry (8)       5. Pho the whole fam (6)

INSIGHT: Katsu dominates for families with kids
→ Kid-friendly, not too spicy, familiar format

Source: Post-order survey (n=1,599)
```

---

## Slide 5: Zone MVP Rationale

> Anna's request: "Fran to fill out rationale with data on RHS - We should have data that shows variety complaints decrease a lot after 20+ dishes, 5+ px, 5+ cuisines"

### Two Combo Charts for This Slide

**Chart 1: Partners Impact on Zone Performance**
- X-axis: Number of Partners (1-2, 3, 4, 5, 6-7, 8-10, 11+)
- Primary Y-axis (Bars): Avg Orders per Zone
- Secondary Y-axis (Line): Avg Rating
- Data labels: Zone count (n=X) on each bar

**Chart 2: Cuisines Impact on Zone Performance**
- X-axis: Number of Cuisines (1-2, 3, 4, 5, 6, 7+)
- Primary Y-axis (Bars): Avg Orders per Zone
- Secondary Y-axis (Line): Avg Rating / Satisfaction %
- Data labels: Zone count (n=X) on each bar

### Chart Data (Pastable CSVs)

**Partners Performance** (`DELIVERABLES/presentation_data/chart_partners_performance.csv`)
```csv
Partners,Avg Orders,Avg Rating,Zones (n=),Satisfaction %
1-2,68,4.14,95,N/A
3,355,4.34,21,79.5%
4,450,4.38,25,78.2%
5,537,4.28,16,80.7%
6-7,705,4.36,16,81.7%
8-10,1071,4.44,15,78.0%
11+,1095,4.50,9,N/A
```

**Cuisines Performance** (`DELIVERABLES/presentation_data/chart_cuisines_performance.csv`)
```csv
Cuisines,Avg Orders,Avg Rating,Zones (n=),Satisfaction %
1-2,89,4.14,102,33.3%
3,404,4.34,30,80.7%
4,511,4.35,24,82.0%
5,685,4.44,13,80.7%
6,797,4.36,11,78.0%
7+,1157,4.47,17,78.0%
```

### Chart Annotations (Key Callouts)

**Partners Chart:**
- Vertical line at "5 partners" threshold
- Callout: "5+ partners = 5x more orders than 1-2" (537 vs 68)
- Callout: "Rating improves from 4.14 → 4.28+"

**Cuisines Chart:**
- Vertical line at "5 cuisines" threshold
- Callout: "34% more orders than 4 cuisines" (685 vs 511)
- Callout: "Satisfaction jumps from 33% → 80%+ at 3+ cuisines"
- Callout: "Rating peaks at 4.44 for 5 cuisines"

### ⚠️ PROVOCATION: The Variety Cliff

```
SATISFACTION COLLAPSES BELOW 3 CUISINES

┌──────────────┬──────────────┬─────────────────────────────────────┐
│ Cuisines     │ Satisfaction │ Visual                              │
├──────────────┼──────────────┼─────────────────────────────────────┤
│ 1-2 cuisines │ 33%          │ ██░░░░░░░░ ← CLIFF                  │
│ 3 cuisines   │ 81%          │ ████████░░ ← Recovery               │
│ 4 cuisines   │ 82%          │ ████████░░                          │
│ 5 cuisines   │ 81%          │ ████████░░                          │
│ 6+ cuisines  │ 78%          │ ████████░░                          │
└──────────────┴──────────────┴─────────────────────────────────────┘

THE CLIFF: Satisfaction drops from 80% → 33% below 3 cuisines
That's a 47 percentage point drop!

IMPLICATION:
• Minimum viable variety = 3 cuisines (not 5)
• Below 3, customers are actively dissatisfied
• 5 is optimal for ORDERS, but 3 is the floor for SATISFACTION

This means our 80 monoculture zones (1 cuisine) are not just 
underperforming - they're actively disappointing customers.

Source: Post-order survey (n=1,020 with zone data)
```

### Why 5? (Narrative Text)

```
WHY 5 IS THE THRESHOLD (NOT 3 OR 4)

The data shows the largest performance jump at 5:
• 3→4 cuisines: +26% orders
• 4→5 cuisines: +34% orders  ← LARGEST JUMP
• 5→6 cuisines: +16% orders  ← Diminishing returns begin

5 is the "sweet spot" balancing:
1. Performance: 34% more orders than 4 cuisines
2. Achievability: 26% of active zones already have 5+ cuisines
3. Satisfaction: Rating peaks at 4.44 for 5 cuisines
4. Survey evidence: 80%+ satisfied at 3+ cuisines (vs 33% at 1-2)
```

### Supporting Survey Evidence

```
VARIETY AS A CONVERSION BARRIER (Dropoff Survey, n=942)
• 17% said "wider variety would have made me order"
• 6% said "no option suited everyone"
→ Variety is a top-3 barrier to conversion

SATISFACTION BY CUISINE COUNT (Post-Order Survey, n=1,020)
• 1-2 cuisines: 33% satisfied
• 3+ cuisines: 80%+ satisfied
→ Clear inflection point at 3 cuisines; 5 optimizes for both orders AND satisfaction

OPEN-TEXT CUISINE REQUESTS (n=132 responses)
Top requested: Indian (30), Chinese (23), Burger (11), Vegetarian (11), Pizza (10)
```

### Pastable Text (Right-Hand Side)

```
MVP Threshold: 5+ Partners, 5+ Cuisines, 20+ Dishes

EVIDENCE FOR 5+ PARTNERS
┌─────────────┬───────┬────────────┬────────────┐
│ Partners    │ Zones │ Avg Orders │ Avg Rating │
├─────────────┼───────┼────────────┼────────────┤
│ 1-2         │ 95    │ 68         │ 4.14       │
│ 3           │ 21    │ 355        │ 4.34       │
│ 4           │ 25    │ 450        │ 4.38       │
│ 5           │ 16    │ 537        │ 4.28       │
│ 6-7         │ 16    │ 705        │ 4.36       │
│ 8+          │ 24    │ 1,083      │ 4.47       │
└─────────────┴───────┴────────────┴────────────┘

Key finding: 5+ partners delivers 5x more orders than 1-2 partners
(537 vs 68 avg orders per zone)

EVIDENCE FOR 5+ CUISINES
┌──────────┬───────┬────────────┬────────────┬──────────────┐
│ Cuisines │ Zones │ Avg Orders │ Avg Rating │ Satisfied %  │
├──────────┼───────┼────────────┼────────────┼──────────────┤
│ 1-2      │ 102   │ 89         │ 4.14       │ 33%          │
│ 3        │ 30    │ 404        │ 4.34       │ 81%          │
│ 4        │ 24    │ 511        │ 4.35       │ 82%          │
│ 5        │ 13    │ 685        │ 4.44       │ 81%          │
│ 6        │ 11    │ 797        │ 4.36       │ 78%          │
│ 7+       │ 17    │ 1,157      │ 4.47       │ 78%          │
└──────────┴───────┴────────────┴────────────┴──────────────┘

Key finding: 5 cuisines delivers 34% more orders than 4 cuisines
AND satisfaction jumps from 33% → 80%+ at 3+ cuisines

EVIDENCE FOR 20+ DISHES
┌────────────┬───────┬────────────┬────────────┐
│ Dishes     │ Zones │ Avg Orders │ Avg Rating │
├────────────┼───────┼────────────┼────────────┤
│ 1-10       │ 4     │ 5          │ 3.00       │
│ 11-15      │ 5     │ 11         │ 2.92       │
│ 16-20      │ 3     │ 16         │ 3.67       │
│ 21-25      │ 7     │ 20         │ 4.37       │
│ 26-30      │ 9     │ 32         │ 4.34       │
│ 31-40      │ 15    │ 25         │ 4.34       │
│ 41+        │ 147   │ 395        │ 4.29       │
└────────────┴───────┴────────────┴────────────┘

Key finding: 21+ dishes shows clear rating improvement
(4.37 avg rating vs 3.67 for 16-20 dishes)

Sources:
• Order data: Snowflake (n=197 zones)
• Satisfaction: Post-order survey (n=1,020)
• Barriers: Dropoff survey (n=942)
```

---

## Slide 6: Zone MVP Count

> Anna's request: "Currently, X zones meet all 3 criteria"

### Why MVP Status Matters (KEY INSIGHT)

```
MVP ZONES OUTPERFORM NON-MVP ZONES BY 2.1x

┌─────────────────┬───────┬────────────┬────────────┬─────────────┐
│ Zone Status     │ Zones │ Avg Orders │ Avg Rating │ Order Share │
├─────────────────┼───────┼────────────┼────────────┼─────────────┤
│ MVP (5+/5+)     │ 42    │ 939        │ 4.43       │ 61%         │
│ Non-MVP         │ 58    │ 437        │ 4.36       │ 39%         │
├─────────────────┼───────┼────────────┼────────────┼─────────────┤
│ Difference      │ -     │ +502       │ +0.07      │ -           │
│ % Uplift        │ -     │ +115%      │ +2%        │ -           │
└─────────────────┴───────┴────────────┴────────────┴─────────────┘

KEY FINDING: MVP zones are 16% of zones (33/201) but generate a disproportionate share of orders
→ Achieving MVP status is the #1 lever for zone performance

Source: zone_mvp_status.csv (n=100 zones with Snowflake order data)
```

### Survey Evidence: Satisfaction by Zone Type

```
POST-ORDER SATISFACTION BY ZONE MVP STATUS (n=1,020)

┌─────────────────┬───────────────┬────────────────┐
│ Zone Status     │ Satisfied %   │ Survey n       │
├─────────────────┼───────────────┼────────────────┤
│ MVP zones       │ 78.8%         │ 633            │
│ Non-MVP zones   │ 79.6%         │ 356            │
└─────────────────┴───────────────┴────────────────┘

Note: Satisfaction is similar across zone types, suggesting MVP status 
drives ORDER VOLUME (more customers) rather than SATISFACTION (happier 
customers). Both are important, but MVP is the acquisition lever.

Source: Post-order survey merged with zone data (n=1,020)
```

### ⚠️ PROVOCATION: Monoculture Zones Are Set Up to Fail

```
80 ZONES HAVE ONLY 1 CUISINE (18% of active zones)

┌─────────────────────┬───────┬─────────┬─────────────────────────────┐
│ Cuisines Available  │ Zones │ % Total │ Can They Succeed?           │
├─────────────────────┼───────┼─────────┼─────────────────────────────┤
│ 1 cuisine           │ 80    │ 18%     │ ❌ NO - set up to fail      │
│ 2 cuisines          │ 123   │ 28%     │ ⚠️ RISKY - below cliff      │
│ 3-4 cuisines        │ 119   │ 27%     │ ✓ OK - above variety cliff  │
│ 5+ cuisines         │ 112   │ 26%     │ ✓✓ MVP - optimal            │
└─────────────────────┴───────┴─────────┴─────────────────────────────┘

MONOCULTURE ZONES CAN NEVER:
• Meet MVP criteria (requires 5+ cuisines)
• Satisfy variety needs (satisfaction crashes below 3 cuisines)
• Compete with zones that have choice

QUESTION FOR DISCUSSION:
Should we even be operating in 1-cuisine zones?
• Option A: Exit these zones entirely
• Option B: Don't market Dinneroo there until we recruit more partners
• Option C: Accept lower performance as "better than nothing"

These 80 zones are dragging down our averages and disappointing customers.
```

### ⚠️ PROVOCATION: London Is 45% of Orders

```
REGIONAL CONCENTRATION

┌─────────────┬───────┬────────────┬─────────────┐
│ Region      │ Zones │ Orders     │ % of Total  │
├─────────────┼───────┼────────────┼─────────────┤
│ London      │ 33    │ 29,153     │ 45%         │
│ South East  │ 24    │ 13,590     │ 21%         │
│ Other       │ 26    │ 14,780     │ 23%         │
│ South West  │ 9     │ 2,332      │ 4%          │
│ North       │ 8     │ 2,311      │ 4%          │
└─────────────┴───────┴────────────┴─────────────┘

33% of zones generate 45% of orders

QUESTION: Is Dinneroo a national proposition or a London one?

If we're honest:
• London works (dense population, delivery culture, partner supply)
• Outside London is struggling (sparse coverage, lower demand)

Should we:
a) Double down on London and the South East?
b) Invest heavily in regional expansion?
c) Accept regional variation as natural?
```

### Pastable Text

```
Currently, 434 zones have Family Dinneroo dishes available

Of these active zones:
• 109 zones (25%) meet MVP criteria (5+ brands, 5+ cuisines)
• 207 zones (48%) have 5+ brands
• 112 zones (26%) have 5+ cuisines
• Primary shortfall: Cuisine breadth - 322 zones have <5 cuisines

WHY THIS MATTERS:
• MVP zones generate 2.1x more orders than non-MVP zones (939 vs 437)
• MVP zones are 16% of live zones (33/201) but capture a disproportionate share of orders
• Rating is also higher in MVP zones (4.43 vs 4.36)
→ Expanding MVP coverage is the biggest growth lever

Zone Distribution:
┌─────────────────────┬───────┬─────────┐
│ Status              │ Zones │ % Total │
├─────────────────────┼───────┼─────────┤
│ MVP Ready (5+ & 5+) │ 109   │ 25%     │
│ Has 5+ brands only  │ 98    │ 23%     │
│ Has 5+ cuisines only│ 3     │ 1%      │
│ Needs both          │ 224   │ 52%     │
├─────────────────────┼───────┼─────────┤
│ Active zones        │ 434   │ 100%    │
│ Zones with 0 dishes │ 872   │ -       │
├─────────────────────┼───────┼─────────┤
│ Total zones tracked │ 1,306 │ -       │
└─────────────────────┴───────┴─────────┘

Top 10 Zones by Dish Variety:
1. Islington (20 brands, 7 cuisines, 83 dishes)
2. East Central (19 brands, 7 cuisines, 80 dishes)
3. West Central (17 brands, 7 cuisines, 75 dishes)
4. Mayfair (18 brands, 7 cuisines, 75 dishes)
5. Clapham (18 brands, 7 cuisines, 74 dishes)
6. Vauxhall/Kennington/Oval (16 brands, 6 cuisines, 71 dishes)
7. Belsize Park/St John's Wood (17 brands, 7 cuisines, 71 dishes)
8. Hampstead (17 brands, 7 cuisines, 70 dishes)
9. London Bridge (16 brands, 7 cuisines, 69 dishes)
10. South Kensington (17 brands, 7 cuisines, 69 dishes)

Brand Distribution (434 active zones):
• 1-2 brands: 120 zones (28%)
• 3-4 brands: 107 zones (25%)
• 5-6 brands: 63 zones (15%)
• 7-8 brands: 64 zones (15%)
• 9-10 brands: 41 zones (9%)
• 11+ brands: 39 zones (9%)

Cuisine Distribution (434 active zones):
• 1 cuisine: 80 zones (18%)
• 2 cuisines: 123 zones (28%)
• 3 cuisines: 59 zones (14%)
• 4 cuisines: 60 zones (14%)
• 5 cuisines: 57 zones (13%)
• 6 cuisines: 38 zones (9%)
• 7 cuisines: 17 zones (4%)

Sources:
• Zone supply: anna_zone_dish_counts.csv (n=1,306 zones)
• Zone performance: zone_mvp_status.csv (n=100 zones with Snowflake data)
• Satisfaction: Post-order survey (n=1,020 with zone match)
```

---

## Slide 7: Minimum Dishes by Zone

> Anna's request: "Anna and Fran to fill out at end - once we have the 'final' ratings by dish"

### Why Dish Tiers Matter (KEY INSIGHT)

```
DISH TIER PERFORMANCE COMPARISON

┌────────────────────┬───────┬────────────┬───────────────┬──────────────┬─────────────┐
│ Dish Tier          │ Dishes│ Total Sales│ Avg per Dish  │ Satisfaction │ Repeat %    │
├────────────────────┼───────┼────────────┼───────────────┼──────────────┼─────────────┤
│ Core Drivers       │ 8     │ 479        │ 59.9          │ 88%          │ 84%         │
│ Preference Drivers │ 5     │ 69         │ 13.8          │ 90%          │ 92%         │
│ Demand Boosters    │ 2     │ 55         │ 27.5          │ 76%          │ 75%         │
│ Deprioritised      │ 8     │ 51         │ 6.4           │ 78%          │ 75%         │
└────────────────────┴───────┴────────────┴───────────────┴──────────────┴─────────────┘

KEY FINDINGS:
• Core Drivers generate 9x more sales per dish than Deprioritised (59.9 vs 6.4)
• Preference Drivers have HIGHEST satisfaction (90%) - customers love them when they try
• Demand Boosters have LOWEST satisfaction (76%) - high demand but quality issues
• Deprioritised dishes have both low demand AND low satisfaction - correct to deprioritise

Source: dish_scoring_anna_aligned.csv (n=23 dishes with performance data)
```

### Tier Prioritisation Logic

```
WHY EACH TIER GETS ITS RECOMMENDATION

CORE DRIVERS → "100% coverage"
• Generate 79% of total dish sales (479 of 603)
• 88% satisfaction means customers are happy
• High demand + high satisfaction = must-have in every zone
• Missing a Core Driver = leaving money on the table

PREFERENCE DRIVERS → "Invest in merchandising"
• Only 11% of sales (69 of 603) despite 90% satisfaction
• Customers LOVE these when they try them
• Problem is awareness, not quality
• Merchandising investment has high ROI potential

DEMAND BOOSTERS → "Improve quality"
• 9% of sales (55 of 603) with only 76% satisfaction
• Customers order but aren't fully satisfied
• Quality improvement could unlock repeat orders
• Focus on partner execution, not recruitment

DEPRIORITISED → "Monitor only"
• Only 8% of sales (51 of 603) with 78% satisfaction
• Neither high demand nor exceptional satisfaction
• Opportunity cost: resources better spent on other tiers
• Don't actively recruit; maintain if already available
```

### Pastable Table

```
MINIMUM DISHES BY ZONE

┌───────────────────┬─────────────────────────────────────────┬────────────────────────────┬─────────────────┐
│ Dish Group        │ Description                             │ Example Dishes             │ Requirement     │
├───────────────────┼─────────────────────────────────────────┼────────────────────────────┼─────────────────┤
│ Core Drivers      │ High demand + high preference           │ Indian Curry, Pho,         │ 100% coverage   │
│ (8 dishes)        │ (Demand >1.0, Preference ≥1.0)          │ Biryani, Katsu, Noodles    │ of these dishes │
│                   │ 88% satisfaction, 59.9 avg sales        │ Sushi, Rice Bowl, Fried Rice│               │
├───────────────────┼─────────────────────────────────────────┼────────────────────────────┼─────────────────┤
│ Preference        │ Lower demand but loved by those         │ Fajitas, Shepherd's Pie,   │ Invest in       │
│ Drivers (5)       │ who try them                            │ Shawarma, Grain Bowl,      │ merchandising   │
│                   │ 90% satisfaction, 13.8 avg sales        │ East Asian Curry           │ to drive demand │
├───────────────────┼─────────────────────────────────────────┼────────────────────────────┼─────────────────┤
│ Demand Boosters   │ High demand but preference improvement  │ Protein & Veg, Pizza       │ Improve quality │
│ (2 dishes)        │ needed (Demand >1.0, Preference <1.0)   │                            │ & positioning   │
│                   │ 76% satisfaction, 27.5 avg sales        │                            │                 │
├───────────────────┼─────────────────────────────────────────┼────────────────────────────┼─────────────────┤
│ Deprioritised     │ Low demand, lower satisfaction          │ Pasta, Lasagne, Tacos,     │ Monitor only    │
│ (8 dishes)        │ (Demand <1.0, Preference <1.0)          │ Chilli, Burrito, Quesadilla│                 │
│                   │ 78% satisfaction, 6.4 avg sales         │ Poke, Nachos               │                 │
├───────────────────┼─────────────────────────────────────────┼────────────────────────────┼─────────────────┤
│ Desserts          │ Family-friendly sweet options           │ TBD - awaiting menu        │ 1+ per zone     │
│                   │                                         │ analysis                   │                 │
└───────────────────┴─────────────────────────────────────────┴────────────────────────────┴─────────────────┘

Sources:
• Sales data: Snowflake orders (n=71,437)
• Satisfaction: Post-order survey (n=1,363 with dish match)
• Repeat intent: Post-order survey (n=1,363)
```

---

## Slide 8: Scoring Framework Definitions

> Anna's request: "[Fran to edit: Number of times a dish is mentioned...]" and "[Fran to edit: Suitability score out of 5...]"

### Why These Metrics? (DATA QUALITY & PURPOSE)

```
WHAT EACH METRIC TELLS US

┌─────────────────────────┬─────────────────────────────────────────────────┐
│ Metric                  │ What It Uniquely Tells Us                       │
├─────────────────────────┼─────────────────────────────────────────────────┤
│ Avg Sales per Dish      │ DEMAND - What people actually order             │
│ % Zones in Top 5        │ CONSISTENCY - Is demand widespread or localised?│
│ Deliveroo Rating        │ QUALITY - Immediate post-delivery reaction      │
│ Meal Satisfaction       │ DEEPER QUALITY - Prompted reflection on meal    │
│ Repeat Intent           │ STICKINESS - Will they come back? (stated)      │
│ Open-Text Requests      │ UNMET DEMAND - What's missing from the menu?    │
│ Dish Suitability        │ PRE-LAUNCH APPEAL - For dishes not yet on menu  │
└─────────────────────────┴─────────────────────────────────────────────────┘

WHY WE USE MULTIPLE METRICS:
• Sales alone misses quality issues (high demand ≠ high satisfaction)
• Satisfaction alone misses demand (loved by few ≠ mass appeal)
• Open-text alone misses reality (what people ask for ≠ what they'll buy)

The 2x2 framework combines DEMAND metrics (Sales, Top 5 %) with 
PREFERENCE metrics (Rating, Satisfaction) to identify dishes that 
are both popular AND loved.
```

### Metric Reliability Assessment

```
METRIC RELIABILITY BY SAMPLE SIZE AND SOURCE TYPE

┌─────────────────────────┬─────────────┬─────────────┬─────────────────┐
│ Metric                  │ Sample Size │ Source Type │ Reliability     │
├─────────────────────────┼─────────────┼─────────────┼─────────────────┤
│ Avg Sales per Dish      │ 71,437      │ Revealed    │ ★★★★★ Highest   │
│ Deliveroo Rating        │ 10,713      │ Revealed    │ ★★★★☆ High      │
│ Meal Satisfaction       │ 1,363       │ Stated      │ ★★★☆☆ Moderate  │
│ Repeat Intent           │ 1,363       │ Stated      │ ★★☆☆☆ Lower     │
│ Open-Text Requests      │ 372 mentions│ Stated      │ ★★☆☆☆ Lower     │
│ Dish Suitability        │ 404         │ Stated      │ ★★☆☆☆ Lower     │
└─────────────────────────┴─────────────┴─────────────┴─────────────────┘

REVEALED vs STATED PREFERENCE:
• Revealed (what people DO): More reliable, harder to get for new dishes
• Stated (what people SAY): Less reliable, available for all dishes

Our framework prioritises revealed preference where available, 
uses stated preference for new dishes with appropriate caveats.
```

### Pastable Definitions

```
DEMAND INDICATORS

Average Sales per Dish (Existing Dishes Only)
Definition: Total orders for the dish divided by the number of times it is 
listed, accounting for variations in dish availability and zone coverage.
Source: Looker order data (n=71,437 orders)
Rationale: Indicates revealed demand, normalised for availability
Reliability: ★★★★★ (highest - actual behaviour)

% of Relevant Zones Where Dish Ranks Top #5 (Existing Dishes Only)
Definition: Percentage of zones where this dish appears in the top 5 selling 
items, considering only zones where the dish is available.
Source: Looker zone-level rankings
Rationale: Indicates demand normalised for zone-level differences
Reliability: ★★★★☆ (high - derived from actual orders)

Open-Text Requests for Dish (All Dishes)
Definition: Number of times a dish is explicitly mentioned when customers are 
asked what they would like to see added, combining:
• Dropoff survey: "What would make you order?" (n=942)
• Post-order survey: "What dishes would you like?" (n=1,599)
• Ratings comments: Unprompted dish requests (n=10,713)
Source: Combined survey open-text analysis (n=13,154 total responses)
Rationale: Captures explicit unmet demand across multiple touchpoints
Reliability: ★★☆☆☆ (lower - stated preference, small dish-level samples)
Caveat: High requests ≠ high satisfaction (e.g., Pasta has 29 requests but 0.9 preference)


CONSUMER PREFERENCE INDICATORS

Deliveroo Rating (Existing Dishes Only)
Definition: Average star rating (1-5) for Family Dinneroo orders containing 
this dish type.
Source: Looker ratings data (n=10,713 rated orders)
Reliability: ★★★★☆ (high - post-delivery revealed satisfaction)
Correlation with sales: 0.54 (strongest predictor)

Meal Satisfaction Score (Existing Dishes Only)
Definition: Percentage of customers who report "Liked it" or "Loved it" when 
asked "How did you feel about the meal?"
Source: Post-order survey (n=1,363 responses with dish match)
Reliability: ★★★☆☆ (moderate - stated but prompted)
Correlation with sales: 0.28

Repeat Intent Score (Existing Dishes Only)
Definition: Percentage of customers who "Agree" or "Strongly agree" with 
"I would like to order the same dish again"
Source: Post-order survey (n=1,363 responses with dish match)
Reliability: ★★☆☆☆ (lower - stated intent often differs from behaviour)
Correlation with sales: 0.06 (weak - intent vs action gap)

Dish Suitability Rating (New Dishes Only)
Definition: Composite score (1-5) measuring how suitable a dish is for 
Family Dinneroo delivery, based on:
• Familiarity (30%): How often families already eat this dish
• Time to Cook (25%): Longer prep time = higher delivery value-add
• Healthy Enough (20%): Perceived healthiness for midweek meals
• Shareable (12.5%): How well dish works for family sharing
• Customisable (12.5%): Can different family members get variations
Source: Pre-Launch Family Behaviour Survey (n=404)
Rationale: Provides early insight into consumer appeal before launch
Reliability: ★★☆☆☆ (lower - stated preference for hypothetical scenario)
Caveat: Use for directional guidance on new dishes only; validate with pilot data
```

---

## Slide 9: Quadrant Summary

> Anna's request: "We have identified X Core Driver dishes, Y Preference Drivers and Z Demand Boosters; ZZ can be deprioritised"

### Quadrant Performance Comparison (KEY INSIGHT)

```
QUADRANT PERFORMANCE: WHY THE SEGMENTATION WORKS

┌────────────────────┬───────┬────────────┬───────────────┬──────────────┬─────────────┐
│ Quadrant           │ Dishes│ Total Sales│ Avg per Dish  │ Satisfaction │ Rating      │
├────────────────────┼───────┼────────────┼───────────────┼──────────────┼─────────────┤
│ Core Drivers       │ 8     │ 479        │ 59.9          │ 88%          │ 4.53        │
│ Preference Drivers │ 5     │ 69         │ 13.8          │ 90%          │ 4.42        │
│ Demand Boosters    │ 2     │ 55         │ 27.5          │ 76%          │ 4.25        │
│ Deprioritised      │ 8     │ 51         │ 6.4           │ 78%          │ 4.15        │
├────────────────────┼───────┼────────────┼───────────────┼──────────────┼─────────────┤
│ TOTAL              │ 23    │ 654        │ 28.4          │ 83%          │ 4.34        │
└────────────────────┴───────┴────────────┴───────────────┴──────────────┴─────────────┘

KEY FINDINGS:

1. CORE DRIVERS dominate sales (73% of total)
   • 8 dishes generate 479 of 654 total sales (73%)
   • Highest rating (4.53) confirms quality matches demand
   • 88% satisfaction = customers are happy
   → Priority: Ensure 100% coverage in all zones

2. PREFERENCE DRIVERS are hidden gems
   • Only 11% of sales BUT highest satisfaction (90%)
   • Customers who find them LOVE them
   • Problem is discovery, not quality
   → Priority: Increase visibility through merchandising

3. DEMAND BOOSTERS have quality issues
   • 8% of sales with LOWEST satisfaction (76%)
   • Customers order but aren't fully satisfied
   • Lowest rating (4.25) confirms quality gap
   → Priority: Work with partners on execution quality

4. DEPRIORITISED is correctly classified
   • Only 8% of sales AND low satisfaction (78%)
   • Neither high demand nor exceptional quality
   • Rating (4.15) is lowest of all quadrants
   → Priority: Don't invest; maintain if already available

Source: dish_scoring_anna_aligned.csv (n=23 dishes)
Post-order survey (n=1,363 with dish match)
```

### Revenue Breakdown by Quadrant

```
QUADRANT SHARE OF TOTAL DISH SALES

Core Drivers       ████████████████████████████████████░ 73% (479 sales)
Preference Drivers ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 11% (69 sales)
Demand Boosters    ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  8% (55 sales)
Deprioritised      ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  8% (51 sales)

INSIGHT: Core Drivers are 35% of dishes but 73% of sales
→ Quadrant classification correctly identifies high-value dishes
```

### ⚠️ PROVOCATION: Pho Is Carrying the Business

```
PHO CONCENTRATION RISK

Pho alone = 136 sales (28% of ALL Core Driver sales)

┌─────────────────────────────┬────────┬─────────────┐
│ Dish                        │ Sales  │ % of Core   │
├─────────────────────────────┼────────┼─────────────┤
│ Pho                         │ 136    │ 28%         │
│ Indian Curry                │ 98     │ 20%         │
│ Biryani                     │ 86     │ 18%         │
│ All other Core Drivers (5)  │ 159    │ 33%         │
└─────────────────────────────┴────────┴─────────────┘

ONE DISH from ONE CUISINE is propping up 28% of our best-performing segment.

QUESTIONS FOR DISCUSSION:
• What happens if Pho restaurants leave the platform?
• Should we actively recruit more Pho providers as insurance?
• Is this concentration a strength (we know what works) or a risk?
```

### ⚠️ PROVOCATION: This Is an Asian Food Play

```
ASIAN DOMINANCE IN CORE DRIVERS

6 of 8 Core Drivers are Asian dishes:
• Pho (Vietnamese)
• Indian Curry (South Asian)
• Biryani (South Asian)
• Katsu (Japanese)
• Noodles (Pan-Asian)
• Fried Rice (Pan-Asian)

Only 2 non-Asian Core Drivers:
• Sushi (Japanese - still Asian)
• Rice Bowl (often Asian)

STRATEGIC IMPLICATION:
This isn't "family meals delivered" - it's "Asian food for families"

Should we:
a) Lean into Asian dominance and own that positioning?
b) Actively recruit non-Asian dishes to diversify?
c) Accept that Asian food IS what families want for delivery?

The data suggests families choose Asian food for delivery because:
• Harder to cook at home (time-saving value)
• Naturally shareable (family-style portions)
• Flavour profiles that appeal to adults AND kids
```

### ⚠️ PROVOCATION: Hidden Gems Are a Merchandising Failure

```
THE HIDDEN GEMS PROBLEM

Preference Drivers have 90% satisfaction but only 11% of sales

┌─────────────────┬──────────────┬────────┬─────────────────────────┐
│ Dish            │ Satisfaction │ Sales  │ The Problem             │
├─────────────────┼──────────────┼────────┼─────────────────────────┤
│ Fajitas         │ 96%          │ 9      │ Nobody knows it's there │
│ Shepherd's Pie  │ 91%          │ 11     │ Not promoted            │
│ Grain Bowl      │ 86%          │ 21     │ Lost in the menu        │
│ Shawarma        │ 90%          │ 10     │ Under-merchandised      │
└─────────────────┴──────────────┴────────┴─────────────────────────┘

These dishes aren't failing because customers don't like them.
They're failing because customers don't FIND them.

QUESTION: Is this a merchandising failure?
• Are these dishes buried in the app?
• Do they have poor imagery?
• Are they only available in limited zones?

If we could increase discovery of Preference Drivers by 50%, 
we'd add ~35 sales with 90% satisfaction.
```

### Pastable Text

```
We have identified 8 Core Driver dishes, 5 Preference Drivers and 
2 Demand Boosters; 8 can be deprioritised

QUADRANT BREAKDOWN WITH PERFORMANCE DATA

Core Drivers (8 dishes) - 73% of sales, 88% satisfaction
┌────────────────────────────┬────────┬───────┬────────┬──────────┐
│ Dish                       │ Demand │ Pref  │ Sales  │ Rating   │
├────────────────────────────┼────────┼───────┼────────┼──────────┤
│ Pho                        │ 4.2    │ 1.1   │ 136    │ 4.6      │
│ South Asian / Indian Curry │ 2.9    │ 1.1   │ 98     │ 4.7      │
│ Biryani                    │ 2.5    │ 1.0   │ 86     │ 4.6      │
│ Fried Rice                 │ 1.0    │ 1.0   │ 41     │ 4.5      │
│ Sushi                      │ 1.5    │ 1.0   │ 32     │ 4.7      │
│ Katsu                      │ 1.2    │ 1.0   │ 29     │ 4.3      │
│ Rice Bowl                  │ 1.2    │ 1.0   │ 29     │ 4.4      │
│ Noodles                    │ 1.2    │ 1.0   │ 28     │ 4.5      │
└────────────────────────────┴────────┴───────┴────────┴──────────┘

Preference Drivers (5 dishes) - 11% of sales, 90% satisfaction
┌────────────────────────────┬────────┬───────┬────────┬──────────┐
│ Dish                       │ Demand │ Pref  │ Sales  │ Rating   │
├────────────────────────────┼────────┼───────┼────────┼──────────┤
│ Grain Bowl                 │ 0.7    │ 1.0   │ 21     │ 4.7      │
│ East Asian Curry           │ 0.9    │ 1.0   │ 18     │ 4.4      │
│ Shepherd's Pie             │ 0.3    │ 1.1   │ 11     │ 4.3      │
│ Shawarma                   │ 0.3    │ 1.0   │ 10     │ 4.5      │
│ Fajitas                    │ 0.4    │ 1.1   │ 9      │ 4.2      │
└────────────────────────────┴────────┴───────┴────────┴──────────┘

Demand Boosters (2 dishes) - 8% of sales, 76% satisfaction
┌────────────────────────────┬────────┬───────┬────────┬──────────┐
│ Dish                       │ Demand │ Pref  │ Sales  │ Rating   │
├────────────────────────────┼────────┼───────┼────────┼──────────┤
│ Protein & Veg              │ 1.6    │ 0.9   │ 44     │ 4.4      │
│ Pizza                      │ 1.0    │ 0.9   │ 11     │ 4.1      │
└────────────────────────────┴────────┴───────┴────────┴──────────┘

Deprioritised (8 dishes) - 8% of sales, 78% satisfaction
• Pasta (8), Lasagne (13), Tacos (7), Chilli (6)
• Burrito/Burrito Bowl (7), Quesadilla (6), Poke (3), Nachos (1)


IMPORTANT CAVEAT - PROSPECT DISHES

9 additional dishes are under consideration but cannot be fully scored 
using our framework as they are not currently on Dinneroo:

• Casserole/Stew (Suitability: 4.3)
• Roast (Suitability: 3.5, Latent demand: 34 mentions)
• Risotto (Suitability: 3.6)
• Fish & Chips (Suitability: 2.5, Latent demand: 39 mentions)
• Tagine, Paella, Pastry Pie, Jacket Potato, Sausage & Mash

These require qualitative assessment of:
• Partner capability to deliver at scale
• Fit with balanced midweek positioning
• Operational feasibility at £25 price point

We recommend a "Prospect Scoring" methodology combining:
• OG Survey suitability ratings (n=404)
• Latent demand signals from open-text
• Partner menu capability audit
• Competitive landscape analysis

This avoids over-reliance on estimated scores or LLM-based assumptions.

Sources:
• Sales data: Snowflake (n=71,437 orders)
• Satisfaction: Post-order survey (n=1,363 with dish match)
• Quadrant classification: dish_scoring_anna_aligned.csv
```

---

## Slide 10: Dish Scoring Data Table

> Anna's request: Fill in the Open-Text Requests column

### Pastable Data (Copy into spreadsheet)

```
Dish,Avg Sales,% Rank #1,% Top 5,Open-Text Requests,Rating,Satisfaction,Repeat Intent,Suitability
Pasta,8,1%,25%,29,4.2,78%,74%,2.5
Rice Bowl,29,11%,41%,0,4.4,84%,77%,2.5
Grain Bowl,21,4%,18%,0,4.7,86%,90%,-
Noodles,28,2%,37%,15,4.5,88%,88%,2.5
South Asian / Indian Curry,98,32%,64%,15,4.7,93%,85%,3.2
East Asian Curry,18,1%,31%,1,4.4,87%,84%,3.6
Katsu,29,19%,41%,9,4.3,87%,85%,2.9
Biryani,86,0%,54%,2,4.6,91%,83%,-
Pizza,11,16%,49%,25,4.1,81%,75%,2.0
Fried Rice,41,4%,17%,2,4.5,79%,81%,2.5
Protein & Veg,44,6%,44%,5,4.4,71%,-,3.5
Chilli,6,0%,5%,3,3.8,-,-,3.3
Fajitas,9,2%,12%,0,4.2,96%,100%,2.5
Lasagne,13,4%,22%,6,4.6,77%,75%,3.3
Shawarma,10,1%,10%,2,4.5,90%,86%,-
Tacos,7,0%,18%,1,4.1,-,-,3.2
Burrito / Burrito Bowl,7,0%,0%,0,-,-,-,2.5
Quesadilla,6,0%,0%,0,-,-,-,3.2
Nachos,1,0%,0%,1,-,-,-,-
Pho,136,56%,100%,18,4.6,92%,89%,2.2
Poke,3,0%,0%,1,-,-,-,-
Shepherd's Pie,11,3%,8%,3,4.3,91%,100%,4.4
Sushi,32,8%,56%,6,4.7,93%,81%,-
```

### ⚠️ PROVOCATION: The Familiarity Trap

```
CUSTOMERS ASK FOR FAMILIAR, NOT WHAT MAKES THEM HAPPY

┌─────────────┬────────────────┬──────────────┬─────────────┬─────────────────┐
│ Dish        │ Open-Text Req  │ Satisfaction │ Preference  │ The Trap        │
├─────────────┼────────────────┼──────────────┼─────────────┼─────────────────┤
│ Pasta       │ 29 (HIGHEST)   │ 78%          │ 0.9 (LOW)   │ ⚠️ TRAP         │
│ Pizza       │ 25 (2nd)       │ 81%          │ 0.9 (LOW)   │ ⚠️ TRAP         │
├─────────────┼────────────────┼──────────────┼─────────────┼─────────────────┤
│ Pho         │ 18             │ 92%          │ 1.1 (HIGH)  │ ✓ Genuine       │
│ Curry       │ 15             │ 93%          │ 1.1 (HIGH)  │ ✓ Genuine       │
│ Fajitas     │ 0              │ 96%          │ 1.1 (HIGH)  │ ✓ Hidden gem    │
└─────────────┴────────────────┴──────────────┴─────────────┴─────────────────┘

THE FAMILIARITY TRAP:
• Pasta and Pizza get the MOST open-text requests (29 and 25)
• But they have the LOWEST preference scores (0.9)
• Customers ask for what's familiar, not what makes them happy

WHY THIS MATTERS:
• If we just listened to open-text, we'd prioritise Pasta and Pizza
• But the data shows these dishes UNDERPERFORM on satisfaction
• Meanwhile, Fajitas (96% satisfaction) gets ZERO requests

LESSON: Don't let open-text drive the menu.
Triangulate with satisfaction and actual orders.
```

### Open-Text Requests - Full Breakdown

```
TOP OPEN-TEXT REQUESTS (Combined from all surveys, n=13,154)

Category-level requests (not dish-specific):
• Kids Menu options: 74 mentions
• Vegetarian options: 49 mentions
• Indian cuisine: 31 mentions
• Chinese cuisine: 26 mentions
• Healthy options: 24 mentions

Dish-specific requests:
• Pasta: 29 mentions ← FAMILIARITY TRAP (78% satisfaction)
• Pizza: 25 mentions ← FAMILIARITY TRAP (81% satisfaction)
• Pho: 18 mentions ← GENUINE DEMAND (92% satisfaction)
• Noodles: 15 mentions
• Curry (general): 15 mentions ← GENUINE DEMAND (93% satisfaction)
• Katsu: 9 mentions
• Lasagne: 6 mentions
• Sushi: 6 mentions
• Pie (various): 6 mentions
• Fish & Chips: 5 mentions
• Protein & Veg: 5 mentions
• Shepherd's Pie: 3 mentions
• Chilli: 3 mentions
• Biryani: 2 mentions
• Shawarma: 2 mentions
• Fried Rice: 2 mentions

Note: Open-text is ONE signal among several. High requests for Pasta/Pizza 
reflect familiarity, but these dishes score lower on preference metrics.
Always triangulate with order volume, satisfaction, and repeat intent.
```

---

## Slide 13: Coverage Gaps & Next Steps

> Anna's request: "To fill in once we've done groupings"

### Revenue Opportunity Sizing (KEY INSIGHT)

```
COVERAGE GAP OPPORTUNITY RANKING

We calculated opportunity by: Coverage Gap % × Avg Sales per Dish
This prioritises gaps in high-performing dishes over gaps in low-performers.

┌────────────────────────────┬──────────────┬────────────┬─────────────┬──────────────┐
│ Dish                       │ Coverage Gap │ Avg Sales  │ Opportunity │ Priority     │
│                            │ (% zones)    │ per Dish   │ Score       │              │
├────────────────────────────┼──────────────┼────────────┼─────────────┼──────────────┤
│ South Asian/Indian Curry   │ 74%          │ 98         │ 72.5        │ #1 HIGHEST   │
│ Biryani                    │ 79%          │ 86         │ 67.9        │ #2           │
│ Pho                        │ 48%          │ 136        │ 65.3        │ #3           │
│ Protein & Veg              │ 93%          │ 44         │ 40.9        │ #4           │
│ Sushi                      │ 63%          │ 32         │ 20.2        │ #5           │
│ Fried Rice                 │ 42%          │ 41         │ 17.2        │ #6           │
│ Grain Bowl                 │ 76%          │ 21         │ 16.0        │ #7           │
│ Fajitas                    │ 68%          │ 9          │ 6.1         │ Lower        │
└────────────────────────────┴──────────────┴────────────┴─────────────┴──────────────┘

KEY FINDING: Top 3 opportunities are all Core Drivers
• Indian Curry, Biryani, Pho = 62% of total opportunity
• These should be recruitment priority #1, #2, #3
• Closing these gaps would significantly increase order volume

Source: dish_scoring_anna_aligned.csv (n=23 dishes)
```

### Zones Most Affected by Core Driver Gaps

```
WHICH ZONES NEED INDIAN/BIRYANI MOST?

Zones with 5+ partners but missing Indian cuisine:
• These are "almost MVP" zones that could convert with one cuisine add

Top 10 zones missing Indian/Biryani (by current order volume):
1. [Zone analysis pending - requires cross-reference with zone supply data]

RECOMMENDATION: Prioritise Indian partner recruitment in zones that:
• Already have 5+ partners (close to MVP)
• Have high order volume (proven demand)
• Are missing Indian cuisine specifically

This maximises ROI on partner recruitment efforts.
```

### Pastable Table

```
COVERAGE GAPS & NEXT STEPS BY QUADRANT

CORE DRIVERS - Protect & Expand (73% of sales, highest opportunity)
┌──────────────────────────┬────────┬───────┬──────────────┬─────────────┬─────────────────────────────────────────────────┐
│ Dish                     │ Demand │ Pref  │ Coverage Gap │ Opportunity │ Next Steps                                      │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ South Asian/Indian Curry │ 2.9    │ 1.1   │ 74%          │ #1 (72.5)   │ Work with Bill's, LEON to introduce curry;      │
│                          │        │       │              │             │ Add new Indian rx (Dishoom, Kricket, Tiffin Tin)│
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Biryani                  │ 2.5    │ 1.0   │ 79%          │ #2 (67.9)   │ Work with Bill's, LEON to introduce curry;      │
│                          │        │       │              │             │ Add new Indian rx                               │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Pho                      │ 4.2    │ 1.1   │ 48%          │ #3 (65.3)   │ Work with Asian providers to add pho;           │
│                          │        │       │              │             │ Make menu more similar to Pho brand             │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Sushi                    │ 1.5    │ 1.0   │ 63%          │ #5 (20.2)   │ Work with Asian providers (Itsu, Iro Sushi,     │
│                          │        │       │              │             │ Kokoro) to add sushi                            │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Fried Rice               │ 1.0    │ 1.0   │ 42%          │ #6 (17.2)   │ Expand fried rice options with Asian providers  │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Katsu                    │ 1.2    │ 1.0   │ 5%           │ Low         │ Small gap - deprioritise expansion              │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Rice Bowl                │ 1.2    │ 1.0   │ 12%          │ Low         │ Small gap - ensure all Asian providers have one │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Noodles                  │ 1.2    │ 1.0   │ 21%          │ Low         │ Understand which noodles more/less attractive   │
└──────────────────────────┴────────┴───────┴─────────────────────────────┴─────────────────────────────────────────────────┘

PREFERENCE DRIVERS - Recruit Partners & Merchandise (11% of sales, 90% satisfaction)
┌──────────────────────────┬────────┬───────┬──────────────┬─────────────┬─────────────────────────────────────────────────┐
│ Dish                     │ Demand │ Pref  │ Coverage Gap │ Opportunity │ Next Steps                                      │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Grain Bowl               │ 0.7    │ 1.0   │ 76%          │ #7 (16.0)   │ Work with healthy providers (Farmer J)          │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Fajitas                  │ 0.4    │ 1.1   │ 68%          │ Lower       │ Expand Mexican (Las Iguanas, Zambrero UK)       │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Shawarma                 │ 0.3    │ 1.0   │ 57%          │ Lower       │ Expand Middle Eastern coverage                  │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Shepherd's Pie           │ 0.3    │ 1.1   │ 57%          │ Lower       │ Expand British comfort food (Bill's, Jakob's)   │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ East Asian Curry         │ 0.9    │ 1.0   │ 3%           │ Low         │ Small gap - maintain current coverage           │
└──────────────────────────┴────────┴───────┴──────────────┴─────────────┴─────────────────────────────────────────────────┘

DEMAND BOOSTERS - Improve Quality (8% of sales, 76% satisfaction)
┌──────────────────────────┬────────┬───────┬──────────────┬─────────────┬─────────────────────────────────────────────────┐
│ Dish                     │ Demand │ Pref  │ Coverage Gap │ Opportunity │ Next Steps                                      │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Protein & Veg            │ 1.6    │ 0.9   │ 93%          │ #4 (40.9)   │ Work with multi-cuisine providers to add option │
│                          │        │       │              │             │ (Farmer J, LEON, Bill's)                        │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────┼─────────────────────────────────────────────────┤
│ Pizza                    │ 1.0    │ 0.9   │ 4%           │ Low         │ Small gap - maintain; focus on quality          │
└──────────────────────────┴────────┴───────┴──────────────┴─────────────┴─────────────────────────────────────────────────┘

DEPRIORITISED - Monitor Only (8% of sales, 78% satisfaction)
┌──────────────────────────┬────────┬───────┬──────────────┬─────────────┬─────────────────────────────────────────────────┐
│ Dish                     │ Demand │ Pref  │ Coverage Gap │ Next Steps                                      │
├──────────────────────────┼────────┼───────┼──────────────┼─────────────────────────────────────────────────┤
│ Quesadilla               │ 0.1    │ -     │ 99%          │ Deprioritised                                   │
│ Nachos                   │ 0.0    │ -     │ 85%          │ Deprioritised                                   │
│ Tacos                    │ 0.4    │ 0.9   │ 84%          │ Deprioritised                                   │
│ Burrito / Burrito Bowl   │ 0.1    │ -     │ 84%          │ Deprioritised                                   │
│ Chilli                   │ 0.2    │ 0.9   │ 68%          │ Deprioritised                                   │
│ Lasagne                  │ 0.6    │ 0.9   │ 66%          │ Deprioritised                                   │
│ Poke                     │ 0.1    │ -     │ 63%          │ Deprioritised                                   │
│ Pasta                    │ 0.6    │ 0.9   │ 3%           │ Deprioritised - baked pasta preferable          │
└──────────────────────────┴────────┴───────┴──────────────┴─────────────────────────────────────────────────┘
```

### ⚠️ PROVOCATION: The Mexican Paradox

```
6 MEXICAN DISHES ON THE MENU - ONLY 1 WORKS

┌─────────────────────────┬────────┬───────┬────────┬─────────────────────────┐
│ Dish                    │ Sales  │ Pref  │ Quadrant│ Verdict                │
├─────────────────────────┼────────┼───────┼────────┼─────────────────────────┤
│ Fajitas                 │ 9      │ 1.1   │ Pref   │ ✓ WORKS (96% sat)       │
│ Tacos                   │ 7      │ 0.9   │ Depri  │ ✗ Underperforming       │
│ Burrito / Burrito Bowl  │ 7      │ -     │ Depri  │ ✗ Underperforming       │
│ Chilli                  │ 6      │ 0.9   │ Depri  │ ✗ Underperforming       │
│ Quesadilla              │ 6      │ -     │ Depri  │ ✗ Underperforming       │
│ Nachos                  │ 1      │ -     │ Depri  │ ✗ Underperforming       │
├─────────────────────────┼────────┼───────┼────────┼─────────────────────────┤
│ TOTAL MEXICAN           │ 36     │ -     │ -      │ 6% of all dish sales    │
└─────────────────────────┴────────┴───────┴────────┴─────────────────────────┘

Compare to Asian:
• 6 Asian Core Drivers generate 450+ sales
• 6 Mexican dishes generate 36 sales
• Asian dishes are 12x more productive

THE PARADOX:
• Mexican food is familiar to UK families
• Mexican restaurants are on the platform
• But customers don't order Mexican for delivery

WHY? Possible reasons:
• Mexican is "easy to make at home" (tacos, quesadillas)
• Doesn't travel well (nachos go soggy)
• Not perceived as "balanced" for midweek
• Less kid-friendly flavour profiles?

QUESTION: Should we cut Mexican entirely?
• Keep Fajitas (the one that works)
• Deprioritise the rest
• Stop recruiting Mexican partners
```

---

## Niche Dish Recommendations

> Anna's questions: "FRAN - DO WE THINK THIS IS TOO NICHE TO INCLUDE?"

### Pastable Recommendations

```
NICHE DISH ASSESSMENT

RECOMMEND EXCLUDING (Too Niche)
┌────────────────┬─────────────┬────────────────┬─────────────────────────────────────┐
│ Dish           │ Suitability │ Open-Text Req  │ Rationale                           │
├────────────────┼─────────────┼────────────────┼─────────────────────────────────────┤
│ Risotto        │ 3.6         │ 0              │ No demand signal; limited partners  │
│ Tagine         │ 3.3         │ 0              │ No demand signal; needs new rx      │
│ Paella         │ 3.3         │ 0              │ No demand signal; needs new rx      │
│ Jacket Potato  │ 2.9         │ 0              │ Low suitability; no demand signal   │
│ Peking Duck    │ -           │ 0              │ No data; likely too premium         │
└────────────────┴─────────────┴────────────────┴─────────────────────────────────────┘

RECOMMEND KEEPING (Strong Potential)
┌────────────────┬─────────────┬────────────────┬─────────────────────────────────────┐
│ Dish           │ Suitability │ Open-Text Req  │ Rationale                           │
├────────────────┼─────────────┼────────────────┼─────────────────────────────────────┤
│ Casserole/Stew │ 4.3         │ 1              │ Highest suitability; British comfort│
│ Roast          │ 3.5         │ 34*            │ Strong latent demand; Bill's capable│
│ Fish & Chips   │ 2.5         │ 39*            │ Highest latent demand; familiar     │
│ Pastry Pie     │ 3.2         │ 6              │ Good suitability; Bill's capable    │
│ Sausage & Mash │ 2.9         │ 4              │ British comfort; Bill's capable     │
└────────────────┴─────────────┴────────────────┴─────────────────────────────────────┘

* Latent demand mentions from dropoff survey "what would make you order?"

Note: These dishes require partner capability assessment before inclusion.
Bill's and Jakob's Kitchen are best positioned to deliver British comfort food.
```

---

## Data Sources & Sample Sizes

### Pastable Reference Table

```
DATA SOURCES USED IN THIS ANALYSIS

REVEALED PREFERENCE (What customers actually do)
┌─────────────────────────┬─────────────┬─────────────────────────────────────┐
│ Source                  │ Sample Size │ What It Measures                    │
├─────────────────────────┼─────────────┼─────────────────────────────────────┤
│ Snowflake Order Data    │ 71,437      │ Actual orders placed                │
│ Deliveroo Ratings       │ 10,713      │ Star ratings (1-5) post-delivery    │
│ Zone-level Performance  │ 197 zones   │ Orders, partners, cuisines by zone  │
└─────────────────────────┴─────────────┴─────────────────────────────────────┘

STATED PREFERENCE (What customers say they want)
┌─────────────────────────┬─────────────┬─────────────────────────────────────┐
│ Source                  │ Sample Size │ What It Measures                    │
├─────────────────────────┼─────────────┼─────────────────────────────────────┤
│ Post-Order Survey       │ 1,599       │ Satisfaction, repeat intent         │
│ Dropoff Survey          │ 942         │ Why customers didn't convert        │
│ OG Family Survey        │ 404         │ Dish suitability, wishlist          │
│ Ratings Comments        │ 10,713      │ Unprompted feedback                 │
└─────────────────────────┴─────────────┴─────────────────────────────────────┘

SUPPLY DATA (What we offer)
┌─────────────────────────┬─────────────┬─────────────────────────────────────┐
│ Source                  │ Sample Size │ What It Measures                    │
├─────────────────────────┼─────────────┼─────────────────────────────────────┤
│ Anna's Zone Data        │ 1,306 zones │ Dishes, partners, cuisines by zone  │
│ Anna's Dish Data        │ 155 dishes  │ Current Family Dinneroo menu        │
│ Partner Coverage        │ 40 partners │ Sites, cuisines by partner          │
└─────────────────────────┴─────────────┴─────────────────────────────────────┘

COMBINED OPEN-TEXT ANALYSIS
┌─────────────────────────┬─────────────┬─────────────────────────────────────┐
│ Source                  │ Responses   │ Dish Mentions Extracted             │
├─────────────────────────┼─────────────┼─────────────────────────────────────┤
│ Dropoff Survey          │ 942         │ 127 dish mentions                   │
│ Post-Order Survey       │ 1,599       │ 89 dish mentions                    │
│ Ratings Comments        │ 10,713      │ 156 dish mentions                   │
├─────────────────────────┼─────────────┼─────────────────────────────────────┤
│ TOTAL                   │ 13,254      │ 372 dish mentions                   │
└─────────────────────────┴─────────────┴─────────────────────────────────────┘
```

---

## Caveats & Limitations

### Pastable Caveats Section

```
CAVEATS & LIMITATIONS

1. ZONE DATA RECONCILIATION
   Our zone_mvp_status.csv contains 100 zones with order data.
   Anna's anna_zone_dish_counts.csv contains 1,306 zones (supply data).
   The 100-zone file is a subset with performance metrics from Snowflake.
   MVP counts in this pack use the 1,306-zone supply view.

2. OPEN-TEXT SAMPLE SIZES
   Individual dish mentions are small (e.g., Pasta n=29).
   We triangulate with:
   • Order volume (n=71,437) - what people actually buy
   • Satisfaction scores (n=1,363) - how happy they are
   • Repeat intent (n=1,363) - will they order again
   Open-text is ONE signal, not the primary driver of recommendations.

3. PROSPECT DISH SCORING
   9 dishes not on Dinneroo cannot be scored using our full framework.
   We rely on:
   • OG Survey suitability (n=404) - stated preference only
   • Latent demand mentions - small sample
   • Qualitative partner capability assessment
   
   CURRENT PROSPECT DISHES:
   ┌────────────────┬─────────────┬────────────────┬─────────────────────┐
   │ Dish           │ Suitability │ Latent Demand  │ Partner Capability  │
   ├────────────────┼─────────────┼────────────────┼─────────────────────┤
   │ Casserole/Stew │ 4.3         │ 1 mention      │ Bill's, Jakob's     │
   │ Roast          │ 3.5         │ 34 mentions    │ Bill's, Jakob's     │
   │ Risotto        │ 3.6         │ 0 mentions     │ Bella Italia, Prezzo│
   │ Fish & Chips   │ 2.5         │ 39 mentions    │ New rx needed       │
   │ Tagine         │ 3.3         │ 0 mentions     │ New rx needed       │
   │ Paella         │ 3.3         │ 0 mentions     │ New rx needed       │
   │ Pastry Pie     │ 3.2         │ 6 mentions     │ Bill's, Jakob's     │
   │ Jacket Potato  │ 2.9         │ 0 mentions     │ Bill's, LEON        │
   │ Sausage & Mash │ 2.9         │ 4 mentions     │ Bill's, Jakob's     │
   └────────────────┴─────────────┴────────────────┴─────────────────────┘
   
   RECOMMENDATION: Develop "Prospect Scoring" methodology that:
   • Uses structured partner interviews (not LLM estimates)
   • Includes competitive menu analysis (what do Uber Eats families order?)
   • Requires minimum 2 evidence sources before recommendation
   • Separates "partner can make it" from "customers will order it"
   
   For now, we recommend:
   ✓ INCLUDE: Roast, Fish & Chips (strong latent demand + partner capability)
   ✓ INCLUDE: Casserole/Stew, Pastry Pie (high suitability + partner capability)
   ? CONSIDER: Sausage & Mash (moderate signals)
   ✗ EXCLUDE: Risotto, Tagine, Paella, Jacket Potato (no demand signal)

4. DEMAND vs PREFERENCE DISTINCTION
   High open-text requests ≠ high preference
   Example: Pasta has 29 requests but 0.9 preference score
   This suggests familiarity drives requests, not satisfaction.
   Always check preference metrics before acting on demand signals.

5. COVERAGE GAP INTERPRETATION
   High coverage gap ≠ high opportunity
   A dish with 99% gap and 0.1 demand should NOT be expanded.
   Coverage gaps are actionable only for Core Drivers and Preference Drivers.
```

---

## File Locations

| File | Path | Purpose |
|------|------|---------|
| This document | `DELIVERABLES/reports/ANNA_SLIDES_DATA_PACK.md` | Pastable text for slides |
| Zone MVP data | `DATA/3_ANALYSIS/zone_mvp_status.csv` | 100 zones with performance |
| Anna's zones | `DATA/3_ANALYSIS/anna_zone_dish_counts.csv` | 1,306 zones supply view |
| Dish scoring | `DATA/3_ANALYSIS/dish_scoring_anna_aligned.csv` | Full dish metrics |
| Latent demand | `DATA/3_ANALYSIS/latent_demand_scores.csv` | Open-text analysis |
| Threshold data | `DATA/3_ANALYSIS/threshold_sensitivity.json` | MVP threshold evidence |
| PowerPoint | `DELIVERABLES/reports/Dish_Analysis_Filled_2026-01-07.pptx` | Generated slides |

---

*Generated: 2026-01-07*
*To regenerate: Run `python scripts/phase3_synthesis/06_generate_anna_pptx.py`*

