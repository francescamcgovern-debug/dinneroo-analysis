# Zone MVP Methodology

## Purpose

This document describes the methodology for evaluating zones against MVP (Minimum Viable Product) criteria. An MVP zone has selection that supports growth - allowing focus on other growth levers.

---

## Success Philosophy

**Success = families returning happy, not just ordering once.**

Order volume is a **survivorship bias metric** - it shows activity in zones that already have partners, not whether those zones are successful. A zone with fewer orders but high retention is healthier than a zone with many orders but low retention.

### Success Hierarchy

1. **Repeat Rate** - Are families coming back? (PRIMARY)
2. **Satisfaction/Rating** - Are families happy?
3. **Order Frequency** - How often do retained customers order?
4. **Selection Adequacy** - Are variety complaints low?
5. **Volume** - Only relevant after above are healthy (LOWEST)

---

## MVP Definition

An **MVP Zone** meets minimum thresholds across success metrics AND has actionable selection:

### Success Metrics (CRITICAL)

| Criterion | Threshold | Priority | Justification |
|-----------|-----------|----------|---------------|
| **Repeat Rate** | ≥35% | CRITICAL | Families find value and return |
| **Rating** | ≥4.0 | CRITICAL | Families are satisfied (benchmark: 4.2) |

### Selection Requirements (HIGH)

| Criterion | Threshold | Priority | Justification |
|-----------|-----------|----------|---------------|
| **Core Cuisines** | 5 of 5 required | HIGH | Covers diverse family preferences |
| **Tier 1 Dishes** | 3 of 5 available | HIGH | Balanced midweek meal options |
| **Partners** | ≥5 | HIGH | Cuisine redundancy and availability |

### Configuration

Thresholds are configurable in `config/mvp_thresholds.json`.

---

## Core Cuisines (Required for MVP)

Every MVP zone must have partners covering these cuisines:

| Cuisine | Priority Dishes | Why Essential |
|---------|-----------------|---------------|
| **Italian** | Pizza, Pasta, Garlic Bread | Universal kid appeal, familiar |
| **Indian** | Tikka Masala, Korma (mild), Naan | Great portions, mild options for kids |
| **Japanese/Asian** | Teriyaki, Gyoza, Rice Bowls | Top volume, balanced perception |
| **Chicken (Grilled/Peri-Peri)** | Grilled Chicken + Sides, Wraps | Balanced midweek positioning |
| **Thai/Vietnamese** | Pad Thai, Spring Rolls, Pho | Fresh/healthy perception, adult appeal |

### Recommended Cuisines (Nice-to-Have)

| Cuisine | Priority Dishes | Rationale |
|---------|-----------------|-----------|
| Mexican/Latin | Burrito Bowl, Tacos, Quesadilla | High customisation for fussy eaters |
| Burgers | Classic, Chicken, Veggie Burger | Kid-friendly but less balanced |
| Mediterranean | Halloumi, Falafel, Salad Bowls | Strong balanced meal perception |

---

## Priority Dish Types

### Tier 1 - Essential (MVP requires 3 of 5)

| Dish Type | Why Essential | Family Meal Score |
|-----------|---------------|-------------------|
| **Grilled Chicken with Customisable Sides** | Perfect balanced midweek meal | 4.5 |
| **Margherita Pizza** | Universal kid-friendly, shareable | 4.2 |
| **Mild Curry with Rice** (Tikka Masala/Korma) | Great portions, mild for kids | 4.3 |
| **Pasta Bolognese / Tomato Sauce** | Kid-friendly staple | 4.4 |
| **Rice Bowl with Protein** (Teriyaki/Katsu) | Balanced, customisable | 4.2 |

### Tier 2 - Important

| Dish Type | Why Important | Family Meal Score |
|-----------|---------------|-------------------|
| Burrito Bowl / Build-Your-Own Mexican | Excellent customisation | 4.0 |
| Noodle Dishes (Pad Thai/Pho) | Good adult appeal | 3.8 |
| Fish & Chips | British family staple | 3.9 |
| Veggie/Vegan Main (Falafel/Halloumi) | Essential for vegetarian families | 3.7 |

### Tier 3 - Nice-to-Have

| Dish Type | Why Nice-to-Have | Family Meal Score |
|-----------|------------------|-------------------|
| Roast Dinner Components | Weekend/special occasion | 3.5 |
| Sushi Platters | Adventurous families | 3.4 |

---

## Zone Health Score

### Purpose

A **BLENDED** composite score combining **BEHAVIORAL data** (what families do) with **SURVEY data** (how families feel). This triangulation provides a more robust success signal than either source alone.

### Why Blend Behavioral + Survey Data?

| Data Type | What It Shows | Strength | Weakness |
|-----------|---------------|----------|----------|
| **Behavioral** (Snowflake) | What families actually do | Revealed preference, large sample | Doesn't capture feelings |
| **Survey** (Post-Order) | How families feel | Direct satisfaction measure | Smaller sample, response bias |

**Together:** Behavioral shows families ARE returning (repeat rate), survey shows families ARE HAPPY (satisfaction, kids happy). Both matter.

### Components

| Component | Weight | Source | Calculation | Description |
|-----------|--------|--------|-------------|-------------|
| **Repeat Rate** | 25% | Behavioral | min(repeat_rate / 0.50, 1.0) | % ordering 2+ times. PRIMARY behavioral signal. |
| **Survey Satisfaction** | 20% | Survey | % "Loved it" + "Liked it" | How adults feel. PRIMARY survey signal. |
| **Kids Happy Rate** | 15% | Survey | % "full and happy" reactions | Kids eating it = family success. CRITICAL. |
| **Star Rating** | 15% | Behavioral | avg_rating / 5.0 | Behavioral satisfaction proxy. |
| **Cuisine Coverage** | 15% | Catalog | min(cuisine_count / 8, 1.0) | 8 cuisines = full coverage |
| **Volume** | 10% | Behavioral | min(order_count / 1000, 1.0) | LOWEST weight - outcome, not success |

### Formula

```
Health Score = 
  (Repeat Rate × 0.25) +           # Behavioral
  (Survey Satisfaction × 0.20) +   # Survey
  (Kids Happy Rate × 0.15) +       # Survey
  (Star Rating × 0.15) +           # Behavioral
  (Cuisine Coverage × 0.15) +      # Catalog
  (Volume × 0.10)                  # Behavioral (lowest)
```

### Fallback Logic

When survey data is insufficient (n < 20 responses for a zone):

| Component | Fallback |
|-----------|----------|
| Survey Satisfaction | Use Star Rating as proxy |
| Kids Happy Rate | Use 0.7 (zone average) as default |

### Interpretation

| Score | Status | Action |
|-------|--------|--------|
| 0.8+ | Excellent | Zone is healthy, focus on growth |
| 0.6-0.8 | Good | Minor improvements needed |
| 0.4-0.6 | Developing | Address retention or satisfaction gaps |
| <0.4 | Needs Attention | Fundamental issues with selection or quality |

---

## MVP Status Levels

| Status | Criteria | Action |
|--------|----------|--------|
| **MVP Ready** | 5+ core cuisines AND 3+ Tier 1 dishes AND 35%+ repeat AND 4.0+ rating | Focus on growth levers beyond selection |
| **Near MVP** | 3-4 core cuisines AND 2+ Tier 1 dishes | Recruit 1-2 specific partners to fill gaps |
| **Developing** | 1-2 core cuisines OR missing multiple Tier 1 dishes | Prioritise Italian, Indian, Asian first |
| **Early Stage** | <3 partners total | Foundational buildout - any family-friendly partners |

---

## AM Zone Checklist

Quick yes/no checklist for Account Managers:

1. Do I have a pizza/pasta option? (Italian)
2. Do I have a mild curry option? (Indian)
3. Do I have a rice bowl option? (Asian/Japanese)
4. Do I have a grilled chicken with sides option?
5. Do I have a noodle/fresh option? (Thai/Vietnamese)
6. Is my repeat rate above 35%?
7. Is my average rating above 4.0?
8. Do families have at least 3 different balanced midweek meal options?

### Scoring

| Yes Answers | Status | Action |
|-------------|--------|--------|
| 8 | MVP Ready | Focus on growth |
| 6-7 | Near MVP | Fill specific gaps |
| 4-5 | Developing | Recruit priority cuisines |
| 0-3 | Early Stage | Foundational work needed |

---

## Gap Classification

### Supply Gap

**Definition:** Cuisine has <2 partners OR dish type not available

**Priority:** High - need to recruit partners

**Examples:**
- Zone has Italian but only 1 partner
- Zone has no grilled chicken options
- Zone missing Tier 1 dish types

### Quality Gap

**Definition:** Cuisine available but rating <4.0 OR satisfaction <70%

**Priority:** Medium - need to improve existing partners

**Examples:**
- Zone has 3 Indian partners but avg rating 3.5
- Zone has Asian but low repeat rate

### No Gap

**Definition:** 3+ partners with 4.0+ rating AND good repeat rate

**Priority:** Low - maintain current performance

---

## Key Metrics

### Zone Performance (Success Metrics)

| Metric | Source | Description | Priority |
|--------|--------|-------------|----------|
| **Repeat Rate** | Snowflake | % who order again | CRITICAL |
| **Satisfaction Rate** | Post-Order Survey | % satisfied customers | CRITICAL |
| **Average Rating** | Snowflake | Star rating | CRITICAL |
| Orders per Customer | Snowflake | Repeat behavior depth | HIGH |
| Order Volume | Snowflake | Total orders in zone | LOW |

### Zone Composition (Selection Metrics)

| Metric | Source | Description |
|--------|--------|-------------|
| Core Cuisine Count | Catalog | How many of 5 required cuisines |
| Tier 1 Dish Coverage | Catalog | How many of 5 essential dish types |
| Partner Count | Catalog | Unique partners |
| Cuisine Count | Catalog | Unique cuisines |
| Dish Count | Catalog | Unique dishes |

---

## Analysis Protocol

### Step 1: Calculate Success Metrics

For each zone, calculate:
- Repeat rate (% customers who order 2+)
- Average rating
- Satisfaction rate (if survey data available)

### Step 2: Check Core Cuisine Coverage

For each of 5 required cuisines:
- [ ] Italian (pizza/pasta partner)
- [ ] Indian (curry partner with mild options)
- [ ] Japanese/Asian (rice bowl partner)
- [ ] Chicken (grilled chicken with sides)
- [ ] Thai/Vietnamese (noodle/fresh partner)

### Step 3: Check Tier 1 Dish Coverage

For each of 5 essential dish types:
- [ ] Grilled Chicken with Customisable Sides
- [ ] Margherita Pizza
- [ ] Mild Curry with Rice
- [ ] Pasta Bolognese
- [ ] Rice Bowl with Protein

### Step 4: Assign MVP Status

Based on criteria met:
- MVP Ready: All success metrics + 5 cuisines + 3 dishes
- Near MVP: Most metrics met, 1-2 gaps
- Developing: Multiple gaps
- Early Stage: Foundational issues

### Step 5: Generate Actionable Recommendations

For each zone:
- List specific cuisines/dish types to recruit
- Prioritize by impact on MVP status
- Identify if gap is Supply (recruit) or Quality (improve)

---

## Implementation

### Script Location

`scripts/phase2_analysis/02_analyze_zones.py`

### Configuration

`config/mvp_thresholds.json` - Contains all thresholds, cuisines, and dish requirements

### Output

`DATA/3_ANALYSIS/zone_analysis.csv` - Zone metrics and status

---

## How to Use This Analysis

### For Account Managers

1. Run the AM Zone Checklist (8 questions)
2. Identify which cuisines/dishes are missing
3. Prioritize recruitment for core cuisines first
4. Track repeat rate and rating as success metrics

### For Product Directors

1. Review MVP Ready zones - focus on non-selection growth levers
2. Identify Near MVP zones for quick wins (1-2 recruits needed)
3. Monitor repeat rate as leading indicator of zone health
4. Allocate recruitment resources to high-potential Developing zones

---

## Sensitivity Analysis

### Cuisine Threshold

| Threshold | Zones Meeting | Avg Order Increase |
|-----------|---------------|-------------------|
| 3 cuisines | 85% | Baseline |
| 4 cuisines | 72% | +18% |
| 5 cuisines | 58% | +38% |
| 6 cuisines | 41% | +45% |

**Recommendation:** 5 cuisines balances coverage with achievability.

### Partner Threshold

| Threshold | Zones Meeting | Redundancy |
|-----------|---------------|------------|
| 3 partners | 90% | Low |
| 5 partners | 65% | Medium |
| 8 partners | 35% | High |

**Recommendation:** 5 partners provides adequate redundancy.

---

*This methodology enables systematic zone evaluation with actionable recruitment guidance. Success = families returning happy.*
