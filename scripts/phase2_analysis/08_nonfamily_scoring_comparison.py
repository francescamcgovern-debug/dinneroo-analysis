#!/usr/bin/env python3
"""
Non-Family Scoring Framework Comparison
========================================

Compares dish rankings under Family vs Non-Family scoring frameworks.

Family framework includes:
- kids_full_happy (7.5% effective weight)
- fussy_eater_friendly (5.5% effective weight)

Non-Family framework:
- Removes these factors
- Redistributes 13% proportionally to remaining factors

Output:
- family_vs_nonfamily_scores.csv: Side-by-side comparison
- family_vs_nonfamily_comparison.md: Analysis report
"""

import pandas as pd
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "DATA" / "3_ANALYSIS"
DELIVERABLES_DIR = BASE_DIR / "DELIVERABLES" / "reports"
CONFIG_DIR = BASE_DIR / "config"

# ============================================================================
# FRAMEWORK DEFINITIONS
# ============================================================================

# Current Family Framework (from dish_scoring_unified.json)
FAMILY_WEIGHTS = {
    # Performance Track (50%)
    "normalized_sales": 0.10,
    "zone_ranking": 0.10,
    "deliveroo_rating": 0.10,
    "repeat_intent": 0.05,
    "kids_full_happy": 0.075,      # FAMILY-SPECIFIC
    "liked_loved": 0.075,
    
    # Opportunity Track (50%)
    "latent_demand": 0.25,
    "adult_appeal": 0.1025,
    "balanced_guilt_free": 0.0925,
    "fussy_eater_friendly": 0.055,  # FAMILY-SPECIFIC
}

# Non-Family Framework: Remove family factors, redistribute proportionally
def calculate_nonfamily_weights():
    """
    Remove kids_full_happy and fussy_eater_friendly, redistribute their 13% weight
    proportionally to remaining factors.
    """
    family_factors = ["kids_full_happy", "fussy_eater_friendly"]
    removed_weight = sum(FAMILY_WEIGHTS[f] for f in family_factors)  # 0.13
    
    # Remaining factors
    remaining = {k: v for k, v in FAMILY_WEIGHTS.items() if k not in family_factors}
    remaining_total = sum(remaining.values())  # 0.87
    
    # Scale up remaining weights to sum to 1.0
    scale_factor = 1.0 / remaining_total
    
    nonfamily_weights = {k: v * scale_factor for k, v in remaining.items()}
    
    return nonfamily_weights

NONFAMILY_WEIGHTS = calculate_nonfamily_weights()

# ============================================================================
# DATA LOADING
# ============================================================================

def load_master_dish_list():
    """Load the master dish list with workings."""
    master_path = DELIVERABLES_DIR / "MASTER_DISH_LIST_WITH_WORKINGS.csv"
    
    # Skip comment lines
    with open(master_path, 'r') as f:
        lines = f.readlines()
    
    # Find header line (first non-comment line)
    data_lines = [l for l in lines if not l.startswith('#')]
    
    from io import StringIO
    df = pd.read_csv(StringIO(''.join(data_lines)))
    
    return df

def load_priority_dishes():
    """Load priority dishes with component scores."""
    priority_path = DATA_DIR / "priority_dishes.csv"
    return pd.read_csv(priority_path)

# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def normalize_percentage(val):
    """Convert percentage string to float (0-1)."""
    if pd.isna(val) or val == '':
        return None
    if isinstance(val, str):
        val = val.replace('%', '').strip()
        try:
            return float(val) / 100
        except:
            return None
    return float(val)

def score_to_5_scale(value, thresholds):
    """
    Convert a metric value to 1-5 scale based on thresholds.
    thresholds = [(threshold_5, 5), (threshold_4, 4), ...]
    """
    if value is None:
        return 3.0  # Default neutral score
    
    for threshold, score in thresholds:
        if value >= threshold:
            return score
    return 1.0

def calculate_family_score(row):
    """Calculate composite score using Family framework."""
    scores = {}
    
    # Performance metrics (use available data)
    # normalized_sales - proxy from avg_sales_per_dish
    if pd.notna(row.get('avg_sales_per_dish')):
        sales = float(row['avg_sales_per_dish'])
        scores['normalized_sales'] = score_to_5_scale(sales, [(100, 5), (50, 4), (25, 3), (10, 2)])
    else:
        scores['normalized_sales'] = 3.0
    
    # zone_ranking - from pct_zones_top_5
    zone_pct = normalize_percentage(row.get('pct_zones_top_5'))
    if zone_pct is not None:
        scores['zone_ranking'] = score_to_5_scale(zone_pct, [(0.6, 5), (0.4, 4), (0.2, 3), (0.1, 2)])
    else:
        scores['zone_ranking'] = 3.0
    
    # deliveroo_rating
    if pd.notna(row.get('deliveroo_rating')):
        rating = float(row['deliveroo_rating'])
        scores['deliveroo_rating'] = score_to_5_scale(rating, [(4.5, 5), (4.3, 4), (4.0, 3), (3.5, 2)])
    else:
        scores['deliveroo_rating'] = 3.0
    
    # repeat_intent
    repeat = normalize_percentage(row.get('repeat_intent'))
    if repeat is not None:
        scores['repeat_intent'] = score_to_5_scale(repeat, [(0.8, 5), (0.7, 4), (0.6, 3), (0.5, 2)])
    else:
        scores['repeat_intent'] = 3.0
    
    # kids_full_happy - proxy from meal_satisfaction for families
    satisfaction = normalize_percentage(row.get('meal_satisfaction'))
    if satisfaction is not None:
        scores['kids_full_happy'] = score_to_5_scale(satisfaction, [(0.85, 5), (0.75, 4), (0.65, 3), (0.55, 2)])
    else:
        scores['kids_full_happy'] = 3.0
    
    # liked_loved - same as satisfaction
    scores['liked_loved'] = scores['kids_full_happy']
    
    # Opportunity metrics
    # latent_demand - from open_text_requests + wishlist_pct
    open_text = row.get('open_text_requests', 0)
    if pd.isna(open_text):
        open_text = 0
    else:
        open_text = float(open_text)
    
    wishlist = normalize_percentage(row.get('wishlist_pct'))
    wishlist_pct = wishlist * 100 if wishlist else 0
    
    # Combined latent demand score
    if open_text >= 20 or wishlist_pct >= 15:
        scores['latent_demand'] = 5.0
    elif open_text >= 10 or wishlist_pct >= 10:
        scores['latent_demand'] = 4.0
    elif open_text >= 5 or wishlist_pct >= 5:
        scores['latent_demand'] = 3.0
    elif open_text >= 2:
        scores['latent_demand'] = 2.0
    else:
        scores['latent_demand'] = 1.0
    
    # adult_appeal - from dish_suitability or default
    if pd.notna(row.get('dish_suitability')):
        suitability = float(row['dish_suitability'])
        # Higher suitability often correlates with adult appeal
        scores['adult_appeal'] = min(5.0, suitability + 1)  # Boost slightly
    else:
        scores['adult_appeal'] = 3.5  # Default for unknown
    
    # balanced_guilt_free - estimate from dish type
    dish_type = row.get('dish_type', '').lower()
    healthy_keywords = ['bowl', 'grain', 'protein', 'veg', 'salad', 'poke']
    indulgent_keywords = ['pizza', 'nachos', 'fried', 'lasagne', 'mac']
    
    if any(kw in dish_type for kw in healthy_keywords):
        scores['balanced_guilt_free'] = 4.5
    elif any(kw in dish_type for kw in indulgent_keywords):
        scores['balanced_guilt_free'] = 2.5
    else:
        scores['balanced_guilt_free'] = 3.5
    
    # fussy_eater_friendly - estimate from dish type
    fussy_friendly = ['pizza', 'pasta', 'noodles', 'rice', 'katsu', 'shepherd']
    fussy_unfriendly = ['pho', 'sushi', 'curry', 'shawarma', 'tagine']
    
    if any(kw in dish_type for kw in fussy_friendly):
        scores['fussy_eater_friendly'] = 4.5
    elif any(kw in dish_type for kw in fussy_unfriendly):
        scores['fussy_eater_friendly'] = 2.5
    else:
        scores['fussy_eater_friendly'] = 3.5
    
    # Calculate weighted composite
    composite = sum(scores[k] * FAMILY_WEIGHTS[k] for k in FAMILY_WEIGHTS.keys())
    
    return composite, scores

def calculate_nonfamily_score(row, family_scores):
    """
    Calculate composite score using Non-Family framework.
    Uses same component scores but different weights.
    """
    # Filter out family-specific factors
    nonfamily_factors = [k for k in family_scores.keys() 
                         if k not in ['kids_full_happy', 'fussy_eater_friendly']]
    
    composite = sum(family_scores[k] * NONFAMILY_WEIGHTS[k] for k in nonfamily_factors)
    
    return composite

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def run_comparison():
    """Run the full comparison analysis."""
    print("Loading data...")
    
    # Load master dish list
    df = load_master_dish_list()
    print(f"Loaded {len(df)} dishes from master list")
    
    # Calculate scores for each dish
    results = []
    
    for _, row in df.iterrows():
        dish_type = row['dish_type']
        
        # Calculate family score
        family_score, component_scores = calculate_family_score(row)
        
        # Calculate non-family score
        nonfamily_score = calculate_nonfamily_score(row, component_scores)
        
        results.append({
            'dish_type': dish_type,
            'cuisine': row.get('cuisine', ''),
            'on_dinneroo': row.get('on_dinneroo', ''),
            'family_score': round(family_score, 3),
            'nonfamily_score': round(nonfamily_score, 3),
            'score_diff': round(nonfamily_score - family_score, 3),
            # Component scores for transparency
            'normalized_sales': round(component_scores['normalized_sales'], 2),
            'zone_ranking': round(component_scores['zone_ranking'], 2),
            'deliveroo_rating': round(component_scores['deliveroo_rating'], 2),
            'repeat_intent': round(component_scores['repeat_intent'], 2),
            'kids_full_happy': round(component_scores['kids_full_happy'], 2),
            'liked_loved': round(component_scores['liked_loved'], 2),
            'latent_demand': round(component_scores['latent_demand'], 2),
            'adult_appeal': round(component_scores['adult_appeal'], 2),
            'balanced_guilt_free': round(component_scores['balanced_guilt_free'], 2),
            'fussy_eater_friendly': round(component_scores['fussy_eater_friendly'], 2),
        })
    
    # Create DataFrame and rank
    results_df = pd.DataFrame(results)
    
    # Add ranks
    results_df['family_rank'] = results_df['family_score'].rank(ascending=False, method='min').astype(int)
    results_df['nonfamily_rank'] = results_df['nonfamily_score'].rank(ascending=False, method='min').astype(int)
    results_df['rank_change'] = results_df['family_rank'] - results_df['nonfamily_rank']
    
    # Classify movers
    def classify_mover(change):
        if change >= 3:
            return "Up (benefits from non-family)"
        elif change <= -3:
            return "Down (benefits from family)"
        else:
            return "Stable"
    
    results_df['mover_type'] = results_df['rank_change'].apply(classify_mover)
    
    # Sort by family rank
    results_df = results_df.sort_values('family_rank')
    
    return results_df

def generate_report(results_df):
    """Generate markdown report."""
    
    # Calculate weight comparison
    family_weights_table = "\n".join([
        f"| {k.replace('_', ' ').title()} | {v*100:.1f}% | {'Yes' if k in ['kids_full_happy', 'fussy_eater_friendly'] else 'No'} |"
        for k, v in FAMILY_WEIGHTS.items()
    ])
    
    nonfamily_weights_table = "\n".join([
        f"| {k.replace('_', ' ').title()} | {v*100:.1f}% |"
        for k, v in NONFAMILY_WEIGHTS.items()
    ])
    
    # Top 20 under each framework
    top20_family = results_df.nsmallest(20, 'family_rank')[['dish_type', 'family_rank', 'family_score', 'nonfamily_rank']]
    top20_nonfamily = results_df.nsmallest(20, 'nonfamily_rank')[['dish_type', 'nonfamily_rank', 'nonfamily_score', 'family_rank']]
    
    # Biggest movers
    movers_up = results_df[results_df['rank_change'] >= 3].sort_values('rank_change', ascending=False)
    movers_down = results_df[results_df['rank_change'] <= -3].sort_values('rank_change')
    
    # Stable dishes (top 10 in both)
    stable = results_df[(results_df['family_rank'] <= 10) & (results_df['nonfamily_rank'] <= 10)]
    
    report = f"""# Family vs Non-Family Scoring Comparison

**Generated:** 2026-01-07
**Purpose:** Understand how dish prioritization changes when family-specific factors are removed

## Executive Summary

This analysis compares dish rankings under two scoring frameworks:
1. **Family Framework** (current): Includes `kids_full_happy` (7.5%) and `fussy_eater_friendly` (5.5%)
2. **Non-Family Framework** (variant): Removes these factors and redistributes 13% to remaining factors

**Key Finding:** {len(movers_up)} dishes rank HIGHER without family factors, {len(movers_down)} rank LOWER. {len(stable)} dishes are stable in top 10 under both frameworks.

---

## 1. Framework Weight Comparison

### Family Framework Weights (Current)

| Factor | Weight | Family-Specific? |
|--------|--------|------------------|
{family_weights_table}

**Total:** 100%

### Non-Family Framework Weights (Variant)

| Factor | Weight |
|--------|--------|
{nonfamily_weights_table}

**Total:** 100%

**Redistribution Logic:** The 13% from removed family factors is distributed proportionally to remaining factors (each factor increases by ~15% relative to its original weight).

---

## 2. Top 20 Dishes: Side-by-Side Comparison

### Under Family Framework

| Rank | Dish | Family Score | Non-Family Rank |
|------|------|--------------|-----------------|
{chr(10).join([f"| {row['family_rank']} | {row['dish_type']} | {row['family_score']:.2f} | {row['nonfamily_rank']} |" for _, row in top20_family.iterrows()])}

### Under Non-Family Framework

| Rank | Dish | Non-Family Score | Family Rank |
|------|------|------------------|-------------|
{chr(10).join([f"| {row['nonfamily_rank']} | {row['dish_type']} | {row['nonfamily_score']:.2f} | {row['family_rank']} |" for _, row in top20_nonfamily.iterrows()])}

---

## 3. Biggest Movers

### Dishes That BENEFIT from Non-Family Focus (Rank UP)

These dishes rank higher when family factors are removed - good candidates if targeting couples/singles.

| Dish | Family Rank | Non-Family Rank | Change | Why |
|------|-------------|-----------------|--------|-----|
{chr(10).join([f"| {row['dish_type']} | {row['family_rank']} | {row['nonfamily_rank']} | +{row['rank_change']} | Lower fussy-eater score ({row['fussy_eater_friendly']}) doesn't penalize |" for _, row in movers_up.head(10).iterrows()]) if len(movers_up) > 0 else "| No significant upward movers | - | - | - | - |"}

### Dishes That BENEFIT from Family Focus (Rank DOWN without it)

These dishes depend on family factors for their ranking - validates family-specific curation.

| Dish | Family Rank | Non-Family Rank | Change | Why |
|------|-------------|-----------------|--------|-----|
{chr(10).join([f"| {row['dish_type']} | {row['family_rank']} | {row['nonfamily_rank']} | {row['rank_change']} | High fussy-eater score ({row['fussy_eater_friendly']}) no longer helps |" for _, row in movers_down.head(10).iterrows()]) if len(movers_down) > 0 else "| No significant downward movers | - | - | - | - |"}

---

## 4. Universally Strong Dishes

These dishes rank in the top 10 under BOTH frameworks - they work for families AND non-families.

| Dish | Family Rank | Non-Family Rank | Family Score | Non-Family Score |
|------|-------------|-----------------|--------------|------------------|
{chr(10).join([f"| {row['dish_type']} | {row['family_rank']} | {row['nonfamily_rank']} | {row['family_score']:.2f} | {row['nonfamily_score']:.2f} |" for _, row in stable.iterrows()]) if len(stable) > 0 else "| No dishes in top 10 under both | - | - | - | - |"}

**Implication:** These dishes are "safe bets" regardless of target audience.

---

## 5. Strategic Implications

### If Rankings Change Significantly
- Family-specific curation **matters** - the 13% weight on family factors creates meaningful differentiation
- Removing family factors would change which dishes we prioritize

### If Rankings Are Stable
- Family factors **don't significantly change** the priority order
- Core dishes work for everyone - family positioning is about marketing, not menu

### Recommendation

Based on this analysis:

1. **Universally strong dishes** ({len(stable)} dishes): Prioritize regardless of segment
2. **Family-dependent dishes** ({len(movers_down)} dishes): Important for family value prop
3. **Non-family opportunities** ({len(movers_up)} dishes): Consider if expanding beyond families

---

## 6. Full Comparison Data

See `DATA/3_ANALYSIS/family_vs_nonfamily_scores.csv` for complete dish-by-dish comparison including all component scores.

### Column Definitions

| Column | Description |
|--------|-------------|
| dish_type | Dish category |
| family_score | Composite score under Family framework |
| nonfamily_score | Composite score under Non-Family framework |
| family_rank | Rank under Family framework (1 = highest) |
| nonfamily_rank | Rank under Non-Family framework |
| rank_change | Positions moved (+ = up in non-family, - = down) |
| mover_type | Classification: Up/Down/Stable |
| [component scores] | Individual factor scores (1-5 scale) |

---

*Analysis generated by `scripts/phase2_analysis/08_nonfamily_scoring_comparison.py`*
"""
    
    return report

def main():
    print("=" * 60)
    print("NON-FAMILY SCORING COMPARISON")
    print("=" * 60)
    
    # Run comparison
    results_df = run_comparison()
    
    # Save CSV
    csv_path = DATA_DIR / "family_vs_nonfamily_scores.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"\nSaved comparison data to: {csv_path}")
    
    # Generate report
    report = generate_report(results_df)
    
    # Save report
    report_path = DELIVERABLES_DIR / "family_vs_nonfamily_comparison.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Saved report to: {report_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    movers_up = len(results_df[results_df['rank_change'] >= 3])
    movers_down = len(results_df[results_df['rank_change'] <= -3])
    stable = len(results_df[(results_df['family_rank'] <= 10) & (results_df['nonfamily_rank'] <= 10)])
    
    print(f"\nDishes analyzed: {len(results_df)}")
    print(f"Rank UP without family factors: {movers_up}")
    print(f"Rank DOWN without family factors: {movers_down}")
    print(f"Stable in top 10 (both frameworks): {stable}")
    
    print("\n" + "-" * 60)
    print("WEIGHT COMPARISON")
    print("-" * 60)
    print("\nFamily Framework:")
    for k, v in FAMILY_WEIGHTS.items():
        marker = " *" if k in ['kids_full_happy', 'fussy_eater_friendly'] else ""
        print(f"  {k}: {v*100:.1f}%{marker}")
    
    print("\nNon-Family Framework:")
    for k, v in NONFAMILY_WEIGHTS.items():
        print(f"  {k}: {v*100:.1f}%")
    
    print("\n* = Family-specific factor (removed in non-family variant)")

if __name__ == "__main__":
    main()

