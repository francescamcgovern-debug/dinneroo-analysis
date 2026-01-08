#!/usr/bin/env python3
"""
Cuisine Scoring Script

Scores cuisines using the two-track approach:
- Performance Track (50%): Normalized for supply availability
- Opportunity Track (50%): Demand signals from multiple sources

CRITICAL: Performance metrics are normalized by zone count to remove supply bias.
CRITICAL: Non-Dinneroo benchmarks use FILTERED data (Mon-Thu dinner only).

Usage:
    python3 scripts/phase2_analysis/score_cuisines.py

Output:
    DATA/3_ANALYSIS/cuisine_scores.csv
    DATA/3_ANALYSIS/cuisine_quadrants.json
    DATA/3_ANALYSIS/expansion_opportunities.json
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import logging
from collections import defaultdict

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Input files
CUISINE_PERFORMANCE_FILE = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "cuisine_performance.csv"
NON_DINNEROO_MIDWEEK_FILE = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "non_dinneroo_cuisine_demand_midweek.csv"
PARTNER_CUISINE_MATRIX_FILE = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "partner_cuisine_matrix.csv"
CUISINE_HIERARCHY_FILE = PROJECT_ROOT / "config" / "cuisine_hierarchy.json"
CUISINE_SCORING_CONFIG_FILE = PROJECT_ROOT / "config" / "cuisine_scoring.json"

# Output files
OUTPUT_SCORES_FILE = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "cuisine_scores.csv"
OUTPUT_QUADRANTS_FILE = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "cuisine_quadrants.json"
OUTPUT_EXPANSION_FILE = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "expansion_opportunities.json"

# Scoring thresholds (from config, with defaults)
PERFORMANCE_MIDPOINT = 3.5
OPPORTUNITY_MIDPOINT = 3.0
MIN_ZONES_FOR_PERFORMANCE = 15


def load_config():
    """Load scoring configuration."""
    with open(CUISINE_SCORING_CONFIG_FILE) as f:
        config = json.load(f)
    with open(CUISINE_HIERARCHY_FILE) as f:
        hierarchy = json.load(f)
    return config, hierarchy


def load_performance_data():
    """Load cuisine performance data from Snowflake analysis."""
    logger.info("Loading cuisine performance data...")
    
    if not CUISINE_PERFORMANCE_FILE.exists():
        logger.warning(f"Performance file not found: {CUISINE_PERFORMANCE_FILE}")
        return pd.DataFrame()
    
    df = pd.read_csv(CUISINE_PERFORMANCE_FILE)
    logger.info(f"Loaded {len(df)} cuisines with performance data")
    return df


def load_non_dinneroo_demand():
    """Load filtered non-Dinneroo demand data."""
    logger.info("Loading non-Dinneroo demand data (filtered to Mon-Thu dinner)...")
    
    if not NON_DINNEROO_MIDWEEK_FILE.exists():
        logger.warning(f"Non-Dinneroo midweek file not found: {NON_DINNEROO_MIDWEEK_FILE}")
        logger.warning("Run scripts/filter_non_dinneroo_midweek.py first")
        return pd.DataFrame()
    
    df = pd.read_csv(NON_DINNEROO_MIDWEEK_FILE)
    logger.info(f"Loaded {len(df)} cuisines with non-Dinneroo demand data")
    return df


def load_partner_cuisine_matrix():
    """Load partner-cuisine mapping to estimate zone coverage."""
    logger.info("Loading partner-cuisine matrix...")
    
    if not PARTNER_CUISINE_MATRIX_FILE.exists():
        logger.warning(f"Partner matrix not found: {PARTNER_CUISINE_MATRIX_FILE}")
        return pd.DataFrame()
    
    df = pd.read_csv(PARTNER_CUISINE_MATRIX_FILE)
    logger.info(f"Loaded {len(df)} partners with cuisine mapping")
    return df


def estimate_zones_by_cuisine(partner_matrix):
    """Estimate zone count per cuisine based on partner coverage."""
    cuisine_columns = [c for c in partner_matrix.columns if c not in ['brand', 'zone_count', 'zone_coverage_pct']]
    
    cuisine_zones = {}
    for cuisine in cuisine_columns:
        # Sum zone_count for partners that serve this cuisine
        partners_with_cuisine = partner_matrix[partner_matrix[cuisine] == 'Y']
        # Take max zone count (conservative estimate - some zones have multiple partners)
        zone_count = partners_with_cuisine['zone_count'].max() if len(partners_with_cuisine) > 0 else 0
        cuisine_zones[cuisine] = zone_count
    
    return cuisine_zones


def score_performance_component(value, thresholds):
    """Score a performance component on 1-5 scale based on thresholds."""
    if pd.isna(value):
        return np.nan
    
    for score in range(5, 0, -1):
        if str(score) in thresholds:
            threshold_str = thresholds[str(score)]
            # Parse threshold string (e.g., "300+ orders/zone", "23%+ repeat rate")
            if '+' in threshold_str:
                try:
                    threshold_val = float(threshold_str.split('+')[0].replace(',', '').replace('%', ''))
                    if value >= threshold_val:
                        return score
                except:
                    pass
            elif '-' in threshold_str:
                try:
                    parts = threshold_str.replace('%', '').split('-')
                    low = float(parts[0])
                    high = float(parts[1].split()[0])
                    if low <= value <= high:
                        return score
                except:
                    pass
    return 1


def calculate_performance_score(row, config, cuisine_zones):
    """Calculate performance track score for a cuisine."""
    cuisine = row.get('CUISINE', row.get('cuisine', ''))
    
    # Check if cuisine has enough zones for performance scoring
    zones = cuisine_zones.get(cuisine, 0) if cuisine_zones else row.get('zones_count', 0)
    
    if zones < MIN_ZONES_FOR_PERFORMANCE:
        return np.nan, "Insufficient zones"
    
    scores = {}
    weights = {}
    
    # Orders per zone (normalized) - 25%
    if 'order_count' in row and zones > 0:
        orders_per_zone = row['order_count'] / zones
        scores['orders_per_zone'] = score_orders_per_zone(orders_per_zone)
        weights['orders_per_zone'] = 0.25
    
    # Repeat rate - 25%
    if 'repeat_rate' in row:
        repeat_rate = row['repeat_rate'] * 100 if row['repeat_rate'] < 1 else row['repeat_rate']
        scores['repeat_rate'] = score_repeat_rate(repeat_rate)
        weights['repeat_rate'] = 0.25
    
    # Average rating - 15%
    if 'avg_rating' in row:
        scores['avg_rating'] = score_rating(row['avg_rating'])
        weights['avg_rating'] = 0.15
    
    # Kids full & happy - 20% (critical family signal)
    if 'kids_full_happy' in row:
        scores['kids_full_happy'] = score_kids_happy(row['kids_full_happy'])
        weights['kids_full_happy'] = 0.20
    
    # Satisfaction - 15%
    if 'satisfaction' in row:
        scores['satisfaction'] = score_satisfaction(row['satisfaction'])
        weights['satisfaction'] = 0.15
    
    # Calculate weighted average (scores are already 1-5, so result is 1-5)
    if not scores:
        return np.nan, "No performance data"
    
    # Normalize weights if some components missing
    total_weight = sum(weights.values())
    weighted_sum = sum(scores[k] * weights[k] for k in scores)
    performance_score = round(weighted_sum / total_weight, 2)  # Already on 1-5 scale
    
    return performance_score, "Calculated"


def score_kids_happy(kids_happy_rate):
    """Score kids full & happy rate on 1-5 scale."""
    if kids_happy_rate >= 85:
        return 5
    elif kids_happy_rate >= 75:
        return 4
    elif kids_happy_rate >= 65:
        return 3
    elif kids_happy_rate >= 55:
        return 2
    return 1


def score_orders_per_zone(orders_per_zone):
    """Score orders per zone on 1-5 scale."""
    if orders_per_zone >= 300:
        return 5
    elif orders_per_zone >= 200:
        return 4
    elif orders_per_zone >= 100:
        return 3
    elif orders_per_zone >= 50:
        return 2
    return 1


def score_repeat_rate(repeat_rate):
    """Score repeat rate on 1-5 scale."""
    if repeat_rate >= 23:
        return 5
    elif repeat_rate >= 20:
        return 4
    elif repeat_rate >= 17:
        return 3
    elif repeat_rate >= 14:
        return 2
    return 1


def score_rating(rating):
    """Score average rating on 1-5 scale."""
    if rating >= 4.6:
        return 5
    elif rating >= 4.4:
        return 4
    elif rating >= 4.2:
        return 3
    elif rating >= 4.0:
        return 2
    return 1


def score_satisfaction(satisfaction):
    """Score satisfaction on 1-5 scale."""
    if satisfaction >= 90:
        return 5
    elif satisfaction >= 80:
        return 4
    elif satisfaction >= 70:
        return 3
    elif satisfaction >= 60:
        return 2
    return 1


def calculate_opportunity_score(cuisine, non_dinneroo_df, open_text_mentions=None):
    """Calculate opportunity track score for a cuisine.
    
    Pure demand signals only - no supply gap (that would conflate supply with demand).
    All component scores are 1-5, final score is weighted average (also 1-5).
    
    Weights favor high-n sources:
    - Non-Dinneroo demand: 50% (196k+ filtered orders - revealed behavior)
    - OG Wishlist: 30% (~400 respondents - stated preference)
    - Open-text: 20% (low n but valuable unmet demand signal)
    """
    scores = {}
    weights = {}
    
    # Non-Dinneroo demand (FILTERED) - 50% weight (highest n, revealed behavior)
    non_dinneroo_row = non_dinneroo_df[non_dinneroo_df['cuisine'].str.lower() == cuisine.lower()]
    if len(non_dinneroo_row) > 0:
        filtered_orders = non_dinneroo_row.iloc[0]['non_dinneroo_orders']
        scores['non_dinneroo_demand'] = score_non_dinneroo_demand(filtered_orders)
        weights['non_dinneroo_demand'] = 0.50
    
    # OG Wishlist - 30% weight (moderate n, stated preference)
    scores['og_wishlist'] = 3  # Placeholder - would need to load from OG survey
    weights['og_wishlist'] = 0.30
    
    # Open-text requests - 20% weight (low n but valuable for unmet demand)
    if open_text_mentions and cuisine in open_text_mentions:
        mentions = open_text_mentions[cuisine]
        scores['open_text_requests'] = score_open_text_mentions(mentions)
    else:
        scores['open_text_requests'] = 2  # Default to low if no data
    weights['open_text_requests'] = 0.20
    
    # Calculate weighted average (scores are already 1-5, so result is 1-5)
    if not scores:
        return np.nan
    
    total_weight = sum(weights.values())
    weighted_sum = sum(scores[k] * weights[k] for k in scores)
    opportunity_score = round(weighted_sum / total_weight, 2)  # Already on 1-5 scale
    
    return opportunity_score


def score_non_dinneroo_demand(filtered_orders):
    """Score non-Dinneroo demand on 1-5 scale."""
    if filtered_orders >= 15000:
        return 5
    elif filtered_orders >= 8000:
        return 4
    elif filtered_orders >= 4000:
        return 3
    elif filtered_orders >= 2000:
        return 2
    return 1


def score_open_text_mentions(mentions):
    """Score open-text mentions on 1-5 scale."""
    if mentions >= 50:
        return 5
    elif mentions >= 25:
        return 4
    elif mentions >= 10:
        return 3
    elif mentions >= 5:
        return 2
    return 1


def classify_quadrant(performance, opportunity):
    """Classify cuisine into quadrant based on scores."""
    if pd.isna(performance):
        # No performance data
        if opportunity >= OPPORTUNITY_MIDPOINT:
            return "Expansion"
        else:
            return "Watch"
    
    if performance >= PERFORMANCE_MIDPOINT:
        if opportunity >= OPPORTUNITY_MIDPOINT:
            return "Priority"
        else:
            return "Protect"
    else:
        if opportunity >= OPPORTUNITY_MIDPOINT:
            return "Recruit"
        else:
            return "Monitor"


def get_core_category(cuisine, hierarchy):
    """Get the core category for a cuisine from hierarchy."""
    hierarchy_data = hierarchy.get('hierarchy', {})
    
    for core_cuisine, data in hierarchy_data.items():
        if cuisine.lower() == core_cuisine.lower():
            return core_cuisine
        
        sub_cuisines = data.get('sub_cuisines', [])
        for sub in sub_cuisines:
            if cuisine.lower() == sub.get('display_name', '').lower():
                return core_cuisine
            if cuisine.lower() == sub.get('id', '').lower():
                return core_cuisine
    
    # Check expansion opportunities
    for candidate in hierarchy.get('expansion_opportunities', {}).get('candidates', []):
        if cuisine.lower() == candidate.get('display_name', '').lower():
            return "NEW"
        if cuisine.lower() == candidate.get('id', '').lower():
            return "NEW"
    
    return "Other"


def get_level(cuisine, hierarchy):
    """Get the level (core/sub/new) for a cuisine."""
    hierarchy_data = hierarchy.get('hierarchy', {})
    core_cuisines = hierarchy.get('core_cuisines', {}).get('all', [])
    
    if cuisine in core_cuisines:
        return "core"
    
    for core_cuisine, data in hierarchy_data.items():
        sub_cuisines = data.get('sub_cuisines', [])
        for sub in sub_cuisines:
            if cuisine.lower() == sub.get('display_name', '').lower():
                return "sub"
            if cuisine.lower() == sub.get('id', '').lower():
                return "sub"
    
    # Check expansion opportunities
    for candidate in hierarchy.get('expansion_opportunities', {}).get('candidates', []):
        if cuisine.lower() == candidate.get('display_name', '').lower():
            return "new"
    
    return "other"


def score_all_cuisines(performance_df, non_dinneroo_df, partner_matrix, config, hierarchy):
    """Score all cuisines and generate output."""
    logger.info("Scoring all cuisines...")
    
    # Estimate zones by cuisine from partner matrix
    cuisine_zones = estimate_zones_by_cuisine(partner_matrix) if not partner_matrix.empty else {}
    
    # Get all cuisines from both sources
    all_cuisines = set()
    
    if not performance_df.empty:
        all_cuisines.update(performance_df['CUISINE'].str.lower())
    
    if not non_dinneroo_df.empty:
        all_cuisines.update(non_dinneroo_df['cuisine'].str.lower())
    
    # Add cuisines from hierarchy
    for core_cuisine, data in hierarchy.get('hierarchy', {}).items():
        all_cuisines.add(core_cuisine.lower())
        for sub in data.get('sub_cuisines', []):
            all_cuisines.add(sub.get('display_name', '').lower())
    
    results = []
    
    for cuisine in sorted(all_cuisines):
        if not cuisine:
            continue
        
        # Get performance data
        perf_row = performance_df[performance_df['CUISINE'].str.lower() == cuisine] if not performance_df.empty else pd.DataFrame()
        
        # Calculate scores
        if len(perf_row) > 0:
            row_data = perf_row.iloc[0].to_dict()
            zones = cuisine_zones.get(cuisine.title(), cuisine_zones.get(cuisine, 0))
            row_data['zones_count'] = zones
            performance_score, perf_status = calculate_performance_score(row_data, config, cuisine_zones)
            orders_per_zone = row_data.get('order_count', 0) / zones if zones > 0 else 0
            repeat_rate = row_data.get('repeat_rate', 0)
        else:
            performance_score = np.nan
            perf_status = "No data"
            orders_per_zone = 0
            repeat_rate = 0
        
        opportunity_score = calculate_opportunity_score(cuisine, non_dinneroo_df)
        
        # Calculate unified score
        if pd.isna(performance_score):
            unified_score = opportunity_score if not pd.isna(opportunity_score) else 0
        elif pd.isna(opportunity_score):
            unified_score = performance_score
        else:
            unified_score = round((performance_score * 0.5) + (opportunity_score * 0.5), 2)
        
        # Classify quadrant
        quadrant = classify_quadrant(performance_score, opportunity_score)
        
        # Get hierarchy info
        core_category = get_core_category(cuisine.title(), hierarchy)
        level = get_level(cuisine.title(), hierarchy)
        
        results.append({
            'cuisine': cuisine.title(),
            'core_category': core_category,
            'level': level,
            'performance_score': performance_score if not pd.isna(performance_score) else None,
            'opportunity_score': opportunity_score if not pd.isna(opportunity_score) else None,
            'unified_score': unified_score,
            'quadrant': quadrant,
            'zones_available': cuisine_zones.get(cuisine.title(), cuisine_zones.get(cuisine, 0)),
            'orders_per_zone': round(orders_per_zone, 1),
            'repeat_rate': round(repeat_rate * 100 if repeat_rate < 1 else repeat_rate, 1),
            'performance_status': perf_status
        })
    
    df = pd.DataFrame(results)
    df = df.sort_values('unified_score', ascending=False)
    
    return df


def generate_quadrant_summary(scores_df):
    """Generate quadrant summary JSON."""
    quadrant_summary = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "methodology": "Two-track scoring: Performance (normalized for supply) + Opportunity",
        "thresholds": {
            "performance_midpoint": PERFORMANCE_MIDPOINT,
            "opportunity_midpoint": OPPORTUNITY_MIDPOINT,
            "min_zones_for_performance": MIN_ZONES_FOR_PERFORMANCE
        },
        "quadrants": {}
    }
    
    for quadrant in ['Priority', 'Protect', 'Recruit', 'Monitor', 'Expansion', 'Watch']:
        cuisines = scores_df[scores_df['quadrant'] == quadrant]
        quadrant_summary['quadrants'][quadrant] = {
            "count": len(cuisines),
            "cuisines": cuisines['cuisine'].tolist(),
            "avg_unified_score": round(cuisines['unified_score'].mean(), 2) if len(cuisines) > 0 else None
        }
    
    return quadrant_summary


def generate_expansion_opportunities(scores_df, hierarchy, non_dinneroo_df):
    """Generate expansion opportunities JSON."""
    expansion = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "criteria": {
            "midweek_non_dinneroo_orders_min": 2000,
            "filter_applied": "Mon-Thu 16:30-21:00"
        },
        "candidates": []
    }
    
    # Find cuisines with high opportunity but no performance (new cuisines)
    expansion_cuisines = scores_df[
        (scores_df['quadrant'].isin(['Expansion', 'Recruit'])) &
        (scores_df['core_category'].isin(['NEW', 'Other']))
    ]
    
    for _, row in expansion_cuisines.iterrows():
        # Get non-Dinneroo demand
        non_dinneroo_row = non_dinneroo_df[non_dinneroo_df['cuisine'].str.lower() == row['cuisine'].lower()]
        demand_signal = int(non_dinneroo_row.iloc[0]['non_dinneroo_orders']) if len(non_dinneroo_row) > 0 else 0
        unique_customers = int(non_dinneroo_row.iloc[0]['unique_customers']) if len(non_dinneroo_row) > 0 else 0
        
        if demand_signal >= 2000:
            expansion['candidates'].append({
                "cuisine": row['cuisine'],
                "opportunity_score": row['opportunity_score'],
                "midweek_non_dinneroo_orders": demand_signal,
                "unique_customers": unique_customers,
                "recommendation": "Test & Recruit" if row['opportunity_score'] >= 3.5 else "Monitor"
            })
    
    expansion['candidates'] = sorted(expansion['candidates'], key=lambda x: x['midweek_non_dinneroo_orders'], reverse=True)
    
    return expansion


def main():
    """Main execution."""
    logger.info("=" * 60)
    logger.info("CUISINE SCORING")
    logger.info("=" * 60)
    
    # Load config and hierarchy
    config, hierarchy = load_config()
    
    # Load data
    performance_df = load_performance_data()
    non_dinneroo_df = load_non_dinneroo_demand()
    partner_matrix = load_partner_cuisine_matrix()
    
    # Score all cuisines
    scores_df = score_all_cuisines(performance_df, non_dinneroo_df, partner_matrix, config, hierarchy)
    
    # Save scores
    scores_df.to_csv(OUTPUT_SCORES_FILE, index=False)
    logger.info(f"Saved cuisine scores to {OUTPUT_SCORES_FILE}")
    
    # Generate and save quadrant summary
    quadrant_summary = generate_quadrant_summary(scores_df)
    with open(OUTPUT_QUADRANTS_FILE, 'w') as f:
        json.dump(quadrant_summary, f, indent=2)
    logger.info(f"Saved quadrant summary to {OUTPUT_QUADRANTS_FILE}")
    
    # Generate and save expansion opportunities
    expansion = generate_expansion_opportunities(scores_df, hierarchy, non_dinneroo_df)
    with open(OUTPUT_EXPANSION_FILE, 'w') as f:
        json.dump(expansion, f, indent=2)
    logger.info(f"Saved expansion opportunities to {OUTPUT_EXPANSION_FILE}")
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("SCORING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total cuisines scored: {len(scores_df)}")
    logger.info(f"\nQuadrant distribution:")
    for quadrant in ['Priority', 'Protect', 'Recruit', 'Monitor', 'Expansion', 'Watch']:
        count = len(scores_df[scores_df['quadrant'] == quadrant])
        logger.info(f"  {quadrant}: {count}")
    
    logger.info(f"\nTop 10 cuisines by unified score:")
    for _, row in scores_df.head(10).iterrows():
        perf = f"{row['performance_score']:.2f}" if row['performance_score'] else "N/A"
        opp = f"{row['opportunity_score']:.2f}" if row['opportunity_score'] else "N/A"
        logger.info(f"  {row['cuisine']}: {row['unified_score']:.2f} (P:{perf}, O:{opp}) [{row['quadrant']}]")
    
    return scores_df


if __name__ == "__main__":
    result = main()

