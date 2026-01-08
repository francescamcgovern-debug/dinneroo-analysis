"""
Unified Cuisine Scoring Script v3.0
===================================
Scores cuisines using the SAME 6-factor framework as dishes:

PERFORMANCE TRACK (60%):
- Orders per Zone (20%) - normalized for supply
- Zone Ranking Strength (15%) - consistency across zones
- Rating (15%) - Deliveroo star rating
- Kids Happy (10%) - survey satisfaction

OPPORTUNITY TRACK (40%):
- Latent Demand (20%) - open-text mentions + wishlist
- Non-Dinneroo Demand (20%) - midweek evening filtered

Same quadrant names as dish analysis:
- Core Drivers (high perf + high opp)
- Preference Drivers (low perf + high opp)
- Demand Boosters (high perf + low opp)
- Deprioritised (low both)

Output: Cuisine rankings with unified scores.
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


def load_cuisine_data():
    """Load all cuisine-related data sources."""
    data = {}
    
    # Cuisine performance from orders
    perf_path = DATA_PATH / "3_ANALYSIS" / "cuisine_performance.csv"
    if perf_path.exists():
        df = pd.read_csv(perf_path)
        # Normalize column names
        df.columns = df.columns.str.lower()
        data['performance'] = df
        print(f"  Loaded cuisine_performance.csv: {len(data['performance'])} cuisines")
    
    # Zone-level data for orders per zone calculation
    zone_cuisine_path = DATA_PATH / "3_ANALYSIS" / "cuisine_by_zone.csv"
    if zone_cuisine_path.exists():
        data['zone_cuisine'] = pd.read_csv(zone_cuisine_path)
        print(f"  Loaded cuisine_by_zone.csv: {len(data['zone_cuisine'])} records")
    
    # Latent demand for cuisines
    latent_path = DATA_PATH / "3_ANALYSIS" / "cuisine_latent_demand.csv"
    if latent_path.exists():
        data['latent_demand'] = pd.read_csv(latent_path)
        print(f"  Loaded cuisine_latent_demand.csv: {len(data['latent_demand'])} cuisines")
    
    # Non-Dinneroo demand (midweek filtered)
    non_dinneroo_path = DATA_PATH / "3_ANALYSIS" / "non_dinneroo_cuisine_demand_midweek.csv"
    if non_dinneroo_path.exists():
        data['non_dinneroo'] = pd.read_csv(non_dinneroo_path)
        print(f"  Loaded non_dinneroo_cuisine_demand_midweek.csv: {len(data['non_dinneroo'])} cuisines")
    
    # Existing cuisine analysis
    cuisine_analysis_path = DATA_PATH / "3_ANALYSIS" / "cuisine_gap_analysis.csv"
    if cuisine_analysis_path.exists():
        data['gap_analysis'] = pd.read_csv(cuisine_analysis_path)
        print(f"  Loaded cuisine_gap_analysis.csv: {len(data['gap_analysis'])} cuisines")
    
    return data


def calculate_orders_per_zone(data):
    """Calculate orders per zone for each cuisine.
    
    Uses order_count from cuisine_performance.csv divided by estimated zone count.
    """
    # Fall back to performance data if zone-level not available
    if 'performance' in data:
        perf = data['performance']
        result = {}
        
        # Estimate zone count based on unique customers (rough proxy)
        # Or use a fixed estimate of ~200 zones
        estimated_zones = 200
        
        for _, row in perf.iterrows():
            cuisine = row.get('cuisine')
            orders = row.get('order_count', 0)
            if cuisine and pd.notna(orders) and orders > 0:
                result[cuisine] = {
                    'total_orders': orders,
                    'zone_count': estimated_zones,
                    'orders_per_zone': orders / estimated_zones
                }
        return result
    
    if 'zone_cuisine' not in data:
        return {}
    
    zone_df = data['zone_cuisine']
    orders_per_zone = {}
    
    if 'cuisine' in zone_df.columns:
        grouped = zone_df.groupby('cuisine').agg({
            'total_orders': 'sum',
            'zone_id': 'nunique'
        }).reset_index()
        
        grouped['orders_per_zone'] = grouped['total_orders'] / grouped['zone_id']
        
        for _, row in grouped.iterrows():
            orders_per_zone[row['cuisine']] = {
                'total_orders': row['total_orders'],
                'zone_count': row['zone_id'],
                'orders_per_zone': row['orders_per_zone']
            }
    
    return orders_per_zone


def calculate_zone_ranking_strength(data):
    """Calculate % of zones where cuisine ranks in top 5."""
    if 'zone_cuisine' not in data:
        return {}
    
    zone_df = data['zone_cuisine']
    
    if 'cuisine' not in zone_df.columns or 'rank' not in zone_df.columns:
        return {}
    
    zone_df['in_top_5'] = zone_df['rank'] <= 5
    
    strength = {}
    grouped = zone_df.groupby('cuisine').agg({
        'in_top_5': 'sum',
        'zone_id': 'nunique'
    }).reset_index()
    
    for _, row in grouped.iterrows():
        pct_top_5 = (row['in_top_5'] / row['zone_id']) * 100 if row['zone_id'] > 0 else 0
        strength[row['cuisine']] = pct_top_5
    
    return strength


def score_performance(cuisine, perf_data, orders_per_zone, zone_strength, config):
    """Calculate performance track score (60% of total)."""
    perf_config = config['tracks']['performance']['components']
    
    scores = {}
    weights = {}
    
    # 1. Orders per Zone (20%)
    if cuisine in orders_per_zone:
        opz = orders_per_zone[cuisine]['orders_per_zone']
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
    if cuisine in zone_strength:
        pct = zone_strength[cuisine]
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
    if perf_data is not None and 'avg_rating' in perf_data and pd.notna(perf_data.get('avg_rating')):
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
    kids_col = 'kids_happy_rate' if perf_data and 'kids_happy_rate' in perf_data else 'kids_happy'
    if perf_data is not None and perf_data.get(kids_col) is not None and pd.notna(perf_data.get(kids_col)):
        kids = perf_data[kids_col]
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
    
    total_weight = sum(weights.values())
    if total_weight == 0:
        return None, scores
    
    weighted_score = sum(scores[k] * weights[k] for k in scores) / total_weight
    
    return weighted_score, scores


def score_opportunity(cuisine, latent_data, non_dinneroo_data, config):
    """Calculate opportunity track score (40% of total)."""
    opp_config = config['tracks']['opportunity']['components']
    
    scores = {}
    weights = {}
    
    # 1. Latent Demand (20%)
    latent_score = 2
    if latent_data is not None:
        latent_row = latent_data[latent_data['cuisine'] == cuisine]
        if len(latent_row) > 0:
            latent_score = latent_row.iloc[0].get('latent_demand_score', 2)
    
    scores['latent_demand'] = latent_score
    weights['latent_demand'] = opp_config['latent_demand']['weight']
    
    # 2. Non-Dinneroo Demand (20%)
    non_dinneroo_score = 2
    if non_dinneroo_data is not None:
        nd_row = non_dinneroo_data[non_dinneroo_data['cuisine'] == cuisine]
        if len(nd_row) > 0:
            non_dinneroo_score = nd_row.iloc[0].get('demand_score', 2)
    
    scores['non_dinneroo'] = non_dinneroo_score
    weights['non_dinneroo'] = opp_config['non_dinneroo_demand']['weight']
    
    total_weight = sum(weights.values())
    weighted_score = sum(scores[k] * weights[k] for k in scores) / total_weight
    
    return weighted_score, scores


def assign_quadrant(perf_score, opp_score, on_dinneroo=True, threshold=3.0):
    """Assign action-oriented quadrant name."""
    if not on_dinneroo:
        if opp_score and opp_score >= threshold:
            return 'Prospect'
        else:
            return 'Deprioritised'
    
    if perf_score is None:
        if opp_score and opp_score >= threshold:
            return 'Preference Drivers'
        else:
            return 'Deprioritised'
    
    if perf_score >= threshold and opp_score >= threshold:
        return 'Core Drivers'
    elif perf_score < threshold and opp_score >= threshold:
        return 'Preference Drivers'
    elif perf_score >= threshold and opp_score < threshold:
        return 'Demand Boosters'
    else:
        return 'Deprioritised'


def main():
    """Run the unified cuisine scoring."""
    print("=" * 60)
    print("UNIFIED CUISINE SCORING v3.0")
    print("6-Factor Framework | 60/40 Split | Action-Oriented Quadrants")
    print("=" * 60)
    
    # Load config
    print("\n1. Loading configuration...")
    config = load_config()
    print(f"   Framework version: {config['version']}")
    
    # Load data
    print("\n2. Loading data...")
    data = load_cuisine_data()
    
    # Calculate derived metrics
    print("\n3. Calculating derived metrics...")
    orders_per_zone = calculate_orders_per_zone(data)
    print(f"   Orders per zone: {len(orders_per_zone)} cuisines")
    
    zone_strength = calculate_zone_ranking_strength(data)
    print(f"   Zone ranking strength: {len(zone_strength)} cuisines")
    
    # Get master list of cuisines
    print("\n4. Building cuisine list...")
    cuisines = set()
    
    if 'gap_analysis' in data:
        cuisines.update(data['gap_analysis']['cuisine'].tolist())
    if orders_per_zone:
        cuisines.update(orders_per_zone.keys())
    
    print(f"   Total cuisines: {len(cuisines)}")
    
    # Score each cuisine
    print("\n5. Scoring cuisines...")
    results = []
    
    perf_df = data.get('performance', pd.DataFrame())
    latent_df = data.get('latent_demand')
    non_dinneroo_df = data.get('non_dinneroo')
    gap_df = data.get('gap_analysis', pd.DataFrame())
    
    for cuisine in cuisines:
        # Get cuisine data
        perf_row = None
        if len(perf_df) > 0:
            perf_matches = perf_df[perf_df['cuisine'] == cuisine]
            if len(perf_matches) > 0:
                perf_row = perf_matches.iloc[0].to_dict()
        
        # Check if on Dinneroo
        on_dinneroo = True
        gap_type = 'Unknown'
        if len(gap_df) > 0:
            gap_matches = gap_df[gap_df['cuisine'] == cuisine]
            if len(gap_matches) > 0:
                gap_type = gap_matches.iloc[0].get('gap_type', 'Unknown')
                on_dinneroo = gap_type != 'Not on Dinneroo'
        
        # Calculate scores
        perf_score, perf_components = score_performance(
            cuisine, perf_row, orders_per_zone, zone_strength, config
        )
        
        opp_score, opp_components = score_opportunity(
            cuisine, latent_df, non_dinneroo_df, config
        )
        
        # Unified score
        perf_weight = config['tracks']['performance']['weight']
        opp_weight = config['tracks']['opportunity']['weight']
        
        if perf_score is not None:
            unified_score = (perf_score * perf_weight) + (opp_score * opp_weight)
        else:
            unified_score = opp_score
        
        # Classifications
        quadrant = assign_quadrant(perf_score, opp_score, on_dinneroo)
        
        # Get metrics
        order_volume = None
        zone_count = None
        opz_value = None
        if cuisine in orders_per_zone:
            order_volume = orders_per_zone[cuisine]['total_orders']
            zone_count = orders_per_zone[cuisine]['zone_count']
            opz_value = orders_per_zone[cuisine]['orders_per_zone']
        
        results.append({
            'rank': 0,
            'cuisine': cuisine,
            'on_dinneroo': on_dinneroo,
            'unified_score': round(unified_score, 2),
            'performance_score': round(perf_score, 2) if perf_score else None,
            'opportunity_score': round(opp_score, 2),
            'quadrant': quadrant,
            'gap_type': gap_type,
            
            # Performance components
            'order_volume': order_volume,
            'zone_count': zone_count,
            'orders_per_zone': round(opz_value, 1) if opz_value else None,
            'zone_ranking_pct': round(zone_strength.get(cuisine, 0), 1),
            'avg_rating': perf_row.get('avg_rating') if perf_row else None,
            'kids_happy': perf_row.get('kids_happy_rate') if perf_row else None,
            
            # Opportunity components
            'latent_demand_score': opp_components.get('latent_demand'),
            'non_dinneroo_score': opp_components.get('non_dinneroo'),
        })
    
    # Create DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('unified_score', ascending=False).reset_index(drop=True)
    results_df['rank'] = results_df.index + 1
    
    print(f"   Scored {len(results_df)} cuisines")
    
    # Save outputs
    print("\n6. Saving outputs...")
    
    csv_path = DATA_PATH / "3_ANALYSIS" / "cuisine_scores_unified.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"   Saved: {csv_path}")
    
    json_path = BASE_PATH / "docs" / "data" / "cuisine_scores_unified.json"
    json_data = {
        'generated': datetime.now().isoformat(),
        'framework_version': config['version'],
        'total_cuisines': len(results_df),
        'quadrant_distribution': results_df['quadrant'].value_counts().to_dict(),
        'cuisines': results_df.to_dict('records')
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
    
    print("\nTop 10 Cuisines:")
    top_cols = ['rank', 'cuisine', 'unified_score', 'quadrant', 'on_dinneroo']
    print(results_df[top_cols].head(10).to_string(index=False))
    
    print("\n✓ Cuisine scoring complete!")
    
    return results_df


if __name__ == "__main__":
    main()

