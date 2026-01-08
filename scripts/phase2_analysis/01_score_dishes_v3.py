"""
Unified Dish Scoring Script v3.0
================================
Scores dishes using simplified 6-factor framework:

PERFORMANCE TRACK (60%):
- Orders per Zone (20%) - normalized for supply
- Zone Ranking Strength (15%) - consistency across zones
- Rating (15%) - Deliveroo star rating
- Kids Happy (10%) - survey satisfaction

OPPORTUNITY TRACK (40%):
- Latent Demand (20%) - open-text mentions + wishlist
- Non-Dinneroo Demand (20%) - midweek evening filtered

Quadrants use action-oriented names:
- Core Drivers (high perf + high opp)
- Preference Drivers (low perf + high opp)
- Demand Boosters (high perf + low opp)
- Deprioritised (low both)

Output: Master list of dish types with unified scores.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "DATA"
CONFIG_PATH = BASE_PATH / "config"

def load_config():
    """Load the v3 scoring configuration."""
    config_path = CONFIG_PATH / "scoring_framework_v3.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def load_dish_data():
    """Load all dish-related data sources."""
    data = {}
    
    # Performance data
    perf_path = DATA_PATH / "3_ANALYSIS" / "dish_performance.csv"
    if perf_path.exists():
        data['performance'] = pd.read_csv(perf_path)
        print(f"  Loaded dish_performance.csv: {len(data['performance'])} dishes")
    
    # Zone-level data for orders per zone calculation
    zone_dish_path = DATA_PATH / "3_ANALYSIS" / "dish_rank_by_zone.csv"
    if zone_dish_path.exists():
        data['zone_dish'] = pd.read_csv(zone_dish_path)
        print(f"  Loaded dish_rank_by_zone.csv: {len(data['zone_dish'])} records")
    
    # Latent demand
    latent_path = DATA_PATH / "3_ANALYSIS" / "latent_demand_scores.csv"
    if latent_path.exists():
        data['latent_demand'] = pd.read_csv(latent_path)
        print(f"  Loaded latent_demand_scores.csv: {len(data['latent_demand'])} dishes")
    
    # Opportunity scores (includes on_dinneroo status)
    opp_path = DATA_PATH / "3_ANALYSIS" / "dish_opportunity_scores.csv"
    if opp_path.exists():
        data['opportunity'] = pd.read_csv(opp_path)
        print(f"  Loaded dish_opportunity_scores.csv: {len(data['opportunity'])} dishes")
    
    # Non-Dinneroo demand (midweek filtered)
    non_dinneroo_path = DATA_PATH / "3_ANALYSIS" / "non_dinneroo_dish_demand_midweek.csv"
    if non_dinneroo_path.exists():
        data['non_dinneroo'] = pd.read_csv(non_dinneroo_path)
        print(f"  Loaded non_dinneroo_dish_demand_midweek.csv: {len(data['non_dinneroo'])} dishes")
    
    return data


def calculate_orders_per_zone(data):
    """Calculate orders per zone for each dish type.
    
    This normalizes for supply - a dish available in 10 zones with 500 orders
    scores higher than a dish in 100 zones with 1000 orders.
    
    Uses:
    - order_volume from dish_opportunity_scores.csv
    - zones_available from dish_rank_by_zone.csv
    """
    orders_per_zone = {}
    
    # Get order volumes from opportunity data
    order_volumes = {}
    if 'opportunity' in data:
        opp_df = data['opportunity']
        for _, row in opp_df.iterrows():
            dish = row.get('dish_type')
            vol = row.get('order_volume', 0)
            if dish and pd.notna(vol):
                order_volumes[dish] = vol
    
    # Get zone counts from zone_dish data
    zone_counts = {}
    if 'zone_dish' in data:
        zone_df = data['zone_dish']
        for _, row in zone_df.iterrows():
            dish = row.get('dish_type')
            zones = row.get('zones_available', 0)
            if dish and pd.notna(zones):
                zone_counts[dish] = zones
    
    # Calculate orders per zone
    for dish in set(order_volumes.keys()) | set(zone_counts.keys()):
        vol = order_volumes.get(dish, 0)
        zones = zone_counts.get(dish, 1)
        if zones > 0 and vol > 0:
            orders_per_zone[dish] = {
                'total_orders': vol,
                'zone_count': zones,
                'orders_per_zone': vol / zones
            }
    
    return orders_per_zone


def calculate_zone_ranking_strength(data):
    """Calculate % of zones where dish ranks in top 5.
    
    Uses zones_top_5_pct from dish_rank_by_zone.csv if available.
    """
    if 'zone_dish' not in data:
        return {}
    
    zone_df = data['zone_dish']
    strength = {}
    
    # Use pre-calculated zones_top_5_pct if available
    if 'zones_top_5_pct' in zone_df.columns:
        for _, row in zone_df.iterrows():
            dish = row.get('dish_type')
            pct = row.get('zones_top_5_pct', 0)
            if dish and pd.notna(pct):
                strength[dish] = pct
        return strength
    
    # Fallback: calculate from raw data
    if 'dish_type' not in zone_df.columns or 'rank' not in zone_df.columns:
        return {}
    
    zone_df['in_top_5'] = zone_df['rank'] <= 5
    grouped = zone_df.groupby('dish_type').agg({
        'in_top_5': 'sum',
        'zone_id': 'nunique'
    }).reset_index()
    
    for _, row in grouped.iterrows():
        pct_top_5 = (row['in_top_5'] / row['zone_id']) * 100 if row['zone_id'] > 0 else 0
        strength[row['dish_type']] = pct_top_5
    
    return strength


def score_performance(dish_type, perf_data, orders_per_zone, zone_strength, config):
    """Calculate performance track score (60% of total).
    
    Components:
    - Orders per Zone (20%)
    - Zone Ranking Strength (15%)
    - Rating (15%)
    - Kids Happy (10%)
    """
    perf_config = config['tracks']['performance']['components']
    
    scores = {}
    weights = {}
    
    # 1. Orders per Zone (20%)
    if dish_type in orders_per_zone:
        opz = orders_per_zone[dish_type]['orders_per_zone']
        if opz >= 50:
            scores['orders_per_zone'] = 5
        elif opz >= 30:
            scores['orders_per_zone'] = 4
        elif opz >= 15:
            scores['orders_per_zone'] = 3
        elif opz >= 5:
            scores['orders_per_zone'] = 2
        else:
            scores['orders_per_zone'] = 1
        weights['orders_per_zone'] = perf_config['orders_per_zone']['weight']
    
    # 2. Zone Ranking Strength (15%)
    if dish_type in zone_strength:
        pct = zone_strength[dish_type]
        if pct >= 60:
            scores['zone_ranking'] = 5
        elif pct >= 40:
            scores['zone_ranking'] = 4
        elif pct >= 20:
            scores['zone_ranking'] = 3
        elif pct >= 10:
            scores['zone_ranking'] = 2
        else:
            scores['zone_ranking'] = 1
        weights['zone_ranking'] = perf_config['zone_ranking_strength']['weight']
    
    # 3. Rating (15%)
    if perf_data is not None and 'avg_rating' in perf_data and pd.notna(perf_data['avg_rating']):
        rating = perf_data['avg_rating']
        if rating >= 4.5:
            scores['rating'] = 5
        elif rating >= 4.3:
            scores['rating'] = 4
        elif rating >= 4.0:
            scores['rating'] = 3
        elif rating >= 3.5:
            scores['rating'] = 2
        else:
            scores['rating'] = 1
        weights['rating'] = perf_config['rating']['weight']
    
    # 4. Kids Happy (10%)
    kids_col = 'kids_happy_rate' if perf_data is not None and 'kids_happy_rate' in perf_data else 'kids_happy'
    if perf_data is not None and kids_col in perf_data and pd.notna(perf_data.get(kids_col)):
        kids = perf_data[kids_col]
        # Handle both 0-1 and 0-100 scales
        if kids > 1:
            kids = kids / 100
        if kids >= 0.85:
            scores['kids_happy'] = 5
        elif kids >= 0.75:
            scores['kids_happy'] = 4
        elif kids >= 0.65:
            scores['kids_happy'] = 3
        elif kids >= 0.55:
            scores['kids_happy'] = 2
        else:
            scores['kids_happy'] = 1
        weights['kids_happy'] = perf_config['kids_happy']['weight']
    
    if not scores:
        return None, scores
    
    # Calculate weighted average
    total_weight = sum(weights.values())
    if total_weight == 0:
        return None, scores
    
    weighted_score = sum(scores[k] * weights[k] for k in scores) / total_weight
    
    return weighted_score, scores


def score_opportunity(dish_type, opp_data, latent_data, non_dinneroo_data, config):
    """Calculate opportunity track score (40% of total).
    
    Components:
    - Latent Demand (20%)
    - Non-Dinneroo Demand (20%) - midweek evening only
    """
    opp_config = config['tracks']['opportunity']['components']
    
    scores = {}
    weights = {}
    
    # 1. Latent Demand (20%)
    latent_score = 2  # Default
    if latent_data is not None:
        latent_row = latent_data[latent_data['dish_type'] == dish_type]
        if len(latent_row) > 0:
            latent_score = latent_row.iloc[0].get('latent_demand_score', 2)
    elif opp_data is not None and 'latent_demand_score' in opp_data:
        latent_score = opp_data.get('latent_demand_score', 2)
    
    scores['latent_demand'] = latent_score
    weights['latent_demand'] = opp_config['latent_demand']['weight']
    
    # 2. Non-Dinneroo Demand (20%) - midweek evening filtered
    non_dinneroo_score = 2  # Default
    if non_dinneroo_data is not None:
        nd_row = non_dinneroo_data[non_dinneroo_data['dish_type'] == dish_type]
        if len(nd_row) > 0:
            # Score based on percentile of midweek evening orders
            non_dinneroo_score = nd_row.iloc[0].get('demand_score', 2)
    
    scores['non_dinneroo'] = non_dinneroo_score
    weights['non_dinneroo'] = opp_config['non_dinneroo_demand']['weight']
    
    # Calculate weighted average
    total_weight = sum(weights.values())
    weighted_score = sum(scores[k] * weights[k] for k in scores) / total_weight
    
    return weighted_score, scores


def assign_quadrant(perf_score, opp_score, on_dinneroo=True, threshold=3.0):
    """Assign action-oriented quadrant name.
    
    Quadrants:
    - Core Drivers: High performance + High opportunity (expand)
    - Preference Drivers: Low performance + High opportunity (build demand)
    - Demand Boosters: High performance + Low opportunity (improve quality)
    - Deprioritised: Low both (don't invest)
    """
    # For dishes not on Dinneroo, they're prospects if high opportunity
    if not on_dinneroo:
        if opp_score and opp_score >= threshold:
            return 'Prospect'
        else:
            return 'Deprioritised'
    
    # No performance data - classify by opportunity only
    if perf_score is None:
        if opp_score and opp_score >= threshold:
            return 'Preference Drivers'
        else:
            return 'Deprioritised'
    
    # Standard 2x2
    if perf_score >= threshold and opp_score >= threshold:
        return 'Core Drivers'
    elif perf_score < threshold and opp_score >= threshold:
        return 'Preference Drivers'
    elif perf_score >= threshold and opp_score < threshold:
        return 'Demand Boosters'
    else:
        return 'Deprioritised'


def assign_tier(unified_score, config):
    """Assign tier based on unified score."""
    tiers = config['tier_classification']
    
    if unified_score >= tiers['tier_1']['threshold']:
        return 'Tier 1: Must-Have'
    elif unified_score >= tiers['tier_2']['threshold']:
        return 'Tier 2: Should-Have'
    elif unified_score >= tiers['tier_3']['threshold']:
        return 'Tier 3: Nice-to-Have'
    else:
        return 'Tier 4: Monitor'


def main():
    """Run the unified dish scoring."""
    print("=" * 60)
    print("UNIFIED DISH SCORING v3.0")
    print("6-Factor Framework | 60/40 Split | Action-Oriented Quadrants")
    print("=" * 60)
    
    # Load config
    print("\n1. Loading configuration...")
    config = load_config()
    print(f"   Framework version: {config['version']}")
    
    # Load data
    print("\n2. Loading data...")
    data = load_dish_data()
    
    # Calculate derived metrics
    print("\n3. Calculating derived metrics...")
    orders_per_zone = calculate_orders_per_zone(data)
    print(f"   Orders per zone: {len(orders_per_zone)} dish types")
    
    zone_strength = calculate_zone_ranking_strength(data)
    print(f"   Zone ranking strength: {len(zone_strength)} dish types")
    
    # Get master list of dish types
    print("\n4. Building dish list...")
    dish_types = set()
    
    if 'opportunity' in data:
        dish_types.update(data['opportunity']['dish_type'].tolist())
    if 'performance' in data:
        dish_types.update(data['performance']['dish_type'].tolist())
    if orders_per_zone:
        dish_types.update(orders_per_zone.keys())
    
    print(f"   Total dish types: {len(dish_types)}")
    
    # Score each dish
    print("\n5. Scoring dishes...")
    results = []
    
    perf_df = data.get('performance', pd.DataFrame())
    opp_df = data.get('opportunity', pd.DataFrame())
    latent_df = data.get('latent_demand')
    non_dinneroo_df = data.get('non_dinneroo')
    
    for dish_type in dish_types:
        # Get dish data
        perf_row = None
        if len(perf_df) > 0:
            perf_matches = perf_df[perf_df['dish_type'] == dish_type]
            if len(perf_matches) > 0:
                perf_row = perf_matches.iloc[0].to_dict()
        
        opp_row = None
        on_dinneroo = True
        cuisine = ''
        if len(opp_df) > 0:
            opp_matches = opp_df[opp_df['dish_type'] == dish_type]
            if len(opp_matches) > 0:
                opp_row = opp_matches.iloc[0].to_dict()
                on_dinneroo = opp_row.get('on_dinneroo', True)
                cuisine = opp_row.get('cuisine', '')
        
        # Calculate scores
        perf_score, perf_components = score_performance(
            dish_type, perf_row, orders_per_zone, zone_strength, config
        )
        
        opp_score, opp_components = score_opportunity(
            dish_type, opp_row, latent_df, non_dinneroo_df, config
        )
        
        # Unified score (60/40 weighted)
        perf_weight = config['tracks']['performance']['weight']
        opp_weight = config['tracks']['opportunity']['weight']
        
        if perf_score is not None:
            unified_score = (perf_score * perf_weight) + (opp_score * opp_weight)
        else:
            # No performance data - use opportunity only
            unified_score = opp_score
        
        # Classifications
        quadrant = assign_quadrant(perf_score, opp_score, on_dinneroo)
        tier = assign_tier(unified_score, config)
        
        # Get additional metrics
        order_volume = None
        zone_count = None
        opz_value = None
        if dish_type in orders_per_zone:
            order_volume = orders_per_zone[dish_type]['total_orders']
            zone_count = orders_per_zone[dish_type]['zone_count']
            opz_value = orders_per_zone[dish_type]['orders_per_zone']
        
        results.append({
            'rank': 0,
            'dish_type': dish_type,
            'cuisine': cuisine,
            'on_dinneroo': on_dinneroo,
            'unified_score': round(unified_score, 2),
            'performance_score': round(perf_score, 2) if perf_score else None,
            'opportunity_score': round(opp_score, 2),
            'tier': tier,
            'quadrant': quadrant,
            
            # Performance components
            'order_volume': order_volume,
            'zone_count': zone_count,
            'orders_per_zone': round(opz_value, 1) if opz_value else None,
            'zone_ranking_pct': round(zone_strength.get(dish_type, 0), 1),
            'avg_rating': perf_row.get('avg_rating') if perf_row else None,
            'kids_happy': perf_row.get('kids_happy_rate', perf_row.get('kids_happy')) if perf_row else None,
            
            # Opportunity components
            'latent_demand_score': opp_components.get('latent_demand'),
            'non_dinneroo_score': opp_components.get('non_dinneroo'),
            
            # Component scores for transparency
            'perf_orders_per_zone': perf_components.get('orders_per_zone'),
            'perf_zone_ranking': perf_components.get('zone_ranking'),
            'perf_rating': perf_components.get('rating'),
            'perf_kids_happy': perf_components.get('kids_happy'),
        })
    
    # Create DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('unified_score', ascending=False).reset_index(drop=True)
    results_df['rank'] = results_df.index + 1
    
    # Limit to top 100
    results_df = results_df.head(100)
    
    print(f"   Scored {len(results_df)} dishes")
    
    # Save outputs
    print("\n6. Saving outputs...")
    
    # CSV
    csv_path = DATA_PATH / "3_ANALYSIS" / "priority_100_unified.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"   Saved: {csv_path}")
    
    # JSON for dashboard
    json_path = BASE_PATH / "docs" / "data" / "priority_100_unified.json"
    json_data = {
        'generated': datetime.now().isoformat(),
        'framework_version': config['version'],
        'total_dishes': len(results_df),
        'tier_distribution': results_df['tier'].value_counts().to_dict(),
        'quadrant_distribution': results_df['quadrant'].value_counts().to_dict(),
        'dishes': results_df.to_dict('records')
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"   Saved: {json_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print("\nQuadrant Distribution:")
    for quad, count in results_df['quadrant'].value_counts().items():
        print(f"  {quad}: {count}")
    
    print("\nTier Distribution:")
    for tier, count in results_df['tier'].value_counts().items():
        print(f"  {tier}: {count}")
    
    print("\nTop 15 Dishes:")
    top_cols = ['rank', 'dish_type', 'unified_score', 'quadrant', 'on_dinneroo']
    print(results_df[top_cols].head(15).to_string(index=False))
    
    print("\n✓ Dish scoring complete!")
    
    return results_df


if __name__ == "__main__":
    main()
