# How to Adjust Scoring Weights in Google Sheets

## Framework v3.3: Three-List Approach

We now have three separate ranking lists, each with its own weights optimized for different segments.

---

## Understanding the Lists

### 1. Family Performers (DISH_FAMILY_RANKINGS.csv)
**For:** Families with children ordering from Dinneroo
**Key question:** "What dishes make kids AND parents happy?"

### 2. Couple Performers (DISH_COUPLE_RANKINGS.csv)
**For:** Adults/couples without children
**Key question:** "What dishes satisfy adult tastes?"

### 3. Recruitment Priorities (DISH_RECRUITMENT_PRIORITIES.csv)
**For:** Dishes NOT currently on Dinneroo
**Key question:** "What should we recruit next?"

---

## Current Weights

### Family Performers
| Factor | Weight | Why |
|--------|--------|-----|
| Kids happy | 40% | Kids' reaction determines repeat orders |
| Fussy eater friendly | 20% | Must work for picky kids |
| Orders per zone | 20% | Proven demand |
| Adult satisfaction | 15% | Parents must enjoy it too |
| Portions adequate | 5% | Needs to feed the family |

### Couple Performers
| Factor | Weight | Why |
|--------|--------|-----|
| Adult satisfaction | 40% | Primary driver for couples |
| Rating | 25% | Quality matters to adults |
| Orders per zone | 20% | Proven demand |
| Adult appeal | 15% | Sophisticated options |

### Recruitment Priorities
| Factor | Weight | Why |
|--------|--------|-----|
| Latent demand mentions | 30% | Explicit customer requests |
| Framework score | 25% | Overall family meal fit |
| Fussy eater friendly | 15% | Family appeal |
| Gap score | 15% | Supply gap = opportunity |
| Partner capability | 10% | Can we actually get it? |
| Non-dinneroo demand | 5% | Proven external demand |

---

## How to Recalculate with New Weights

### Step 1: Open in Google Sheets
Upload the relevant CSV to Google Sheets.

### Step 2: Duplicate the Sheet
Right-click tab → "Duplicate" (preserve original)

### Step 3: Add Weight Columns
Create new columns for your adjusted weights:
```
New_Weight_KidsHappy | New_Weight_FussyEater | etc.
```

### Step 4: Create Recalculation Formula

**For Family Performers:**
```
=(@kids_happy_score * NEW_KIDS_WEIGHT) + 
 (@fussy_score * NEW_FUSSY_WEIGHT) + 
 (@orders_score * NEW_ORDERS_WEIGHT) + 
 (@adult_sat_score * NEW_ADULT_WEIGHT) + 
 (@portions_score * NEW_PORTIONS_WEIGHT)
```

### Step 5: Re-Rank
Sort by your new score column, highest first.

---

## Understanding the Rollup (DISH_RANKINGS_WITH_ROLLUP.csv)

This master file shows:
- **24 high-level dish types** (Anna's taxonomy)
- **Family rank + score** for each
- **Couple rank + score** for each
- **items_sample** showing which menu items roll up to each dish type

Example:
| high_level_dish | family_rank | couple_rank | items_sample |
|-----------------|-------------|-------------|--------------|
| Rice Bowl | 1 | 12 | "Mix n Match Rice Bowl Bundle For Four, Teriyaki Rice Bowl Bundle..." |
| South Asian Curry | 2 | 2 | "Butter Chicken, Chicken Ruby, Mattar Paneer..." |

---

## Key Rules for Calibration

1. **Weights must sum to 1.0** (100%) for each list
2. **Family list prioritizes kids_happy** - if you lower this, families may be less satisfied
3. **Couple list prioritizes adult_satisfaction** - adults have different priorities
4. **Recruitment list prioritizes latent demand** - we want to add what customers ask for

---

## Testing Weight Changes

Before finalizing new weights, check:
- [ ] Do the rankings "feel right"? (e.g., Katsu should rank well for families)
- [ ] Are there obvious outliers that suggest a factor is too heavily weighted?
- [ ] Do the top 5 make business sense?

---

## Taxonomy Reference

All rankings use Anna's 24 high-level dish types:
1. Pasta (23 items)
2. Rice Bowl (21 items)
3. Grain Bowl (17 items)
4. South Asian / Indian Curry (13 items)
5. Noodles (13 items)
6. East Asian Curry (11 items)
7. Katsu (9 items)
8. Biryani (6 items)
9. Fried Rice (5 items)
10. Pizza (5 items)
11-24. Other, Protein & Veg, Lasagne, Burrito, Fajitas, Shawarma, Chilli, Tacos, Nachos, Pho, Poke, Quesadilla, Shepherd's Pie, Sushi

See `dish_taxonomy.csv` for full item-level breakdown.
