"""
Regenerate Dish Scores v3.1
===========================
Uses the fixed scoring framework without zone_ranking_strength penalty.

Key changes from v3.0:
- Removed zone_ranking_strength (was penalizing low-availability dishes)
- Increased orders_per_zone weight from 20% to 35%
- Validates against Anna's Core Drivers list

Performance Track (60%):
- Orders per Zone: 35% (primary metric, supply-normalized)
- Rating: 15%
- Kids Happy: 10%

Opportunity Track (40%):
- Latent Demand: 20%
- Non-Dinneroo Demand (midweek filtered): 20%
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "DATA"
CONFIG_PATH = BASE_PATH / "config"
OUTPUT_PATH = DATA_PATH / "3_ANALYSIS"
DELIVERABLES_PATH = BASE_PATH / "DELIVERABLES" / "presentation_data"

# Anna's Core Drivers - these should rank in top tier
ANNA_CORE_DRIVERS = [
    "Pho", "South Asian / Indian Curry", "Biryani", "Fried Rice",
    "Sushi", "Katsu", "Rice Bowl", "Noodles"
]

def load_data():
    """Load all required data sources."""
    data = {}
    
    # Dish performance from survey
    perf_path = DATA_PATH / "3_ANALYSIS" / "dish_performance.csv"
    if perf_path.exists():
        data['performance'] = pd.read_csv(perf_path)
        print(f"  Loaded dish_performance.csv: {len(data['performance'])} dishes")
    
    # Order data for orders_per_zone calculation
    orders_path = DATA_PATH / "1_SOURCE" / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
    if orders_path.exists():
        data['orders'] = pd.read_csv(orders_path)
        print(f"  Loaded ALL_DINNEROO_ORDERS.csv: {len(data['orders'])} orders")
    
    # Latent demand
    latent_path = DATA_PATH / "3_ANALYSIS" / "latent_demand_scores.csv"
    if latent_path.exists():
        data['latent_demand'] = pd.read_csv(latent_path)
        print(f"  Loaded latent_demand_scores.csv: {len(data['latent_demand'])} dishes")
    
    # Non-Dinneroo demand (midweek filtered)
    non_din_path = DATA_PATH / "3_ANALYSIS" / "non_dinneroo_dish_demand_midweek.csv"
    if non_din_path.exists():
        data['non_dinneroo'] = pd.read_csv(non_din_path)
        print(f"  Loaded non_dinneroo_dish_demand_midweek.csv")
    
    # Opportunity scores (for on_dinneroo status and cuisine)
    opp_path = DATA_PATH / "3_ANALYSIS" / "dish_opportunity_scores.csv"
    if opp_path.exists():
        data['opportunity'] = pd.read_csv(opp_path)
        print(f"  Loaded dish_opportunity_scores.csv: {len(data['opportunity'])} dishes")
    
    return data


def calculate_orders_per_zone(data):
    """Calculate orders per zone for each dish type."""
    results = {}
    
    if 'opportunity' not in data:
        return results
    
    opp_df = data['opportunity']
    
    for _, row in opp_df.iterrows():
        dish = row.get('dish_type')
        if not dish:
            continue
            
        order_vol = row.get('order_volume', 0) or 0
        zone_count = row.get('zones_available', 1) or 1
        
        if zone_count > 0 and order_vol > 0:
            opz = order_vol / zone_count
        else:
            opz = 0
            
        results[dish] = {
            'total_orders': order_vol,
            'zone_count': zone_count,
            'orders_per_zone': opz
        }
    
    return results


def score_orders_per_zone(opz):
    """Score orders per zone on 1-5 scale (35% weight)."""
    if opz >= 100:
        return 5
    elif opz >= 50:
        return 4
    elif opz >= 20:
        return 3
    elif opz >= 5:
        return 2
    else:
        return 1


def score_rating(rating):
    """Score Deliveroo rating on 1-5 scale (15% weight)."""
    if pd.isna(rating):
        return 3  # Default
    if rating >= 4.5:
        return 5
    elif rating >= 4.3:
        return 4
    elif rating >= 4.0:
        return 3
    elif rating >= 3.5:
        return 2
    else:
        return 1


def score_kids_happy(pct):
    """Score kids happy rate on 1-5 scale (10% weight)."""
    if pd.isna(pct):
        return 3  # Default
    if pct >= 0.85:
        return 5
    elif pct >= 0.75:
        return 4
    elif pct >= 0.65:
        return 3
    elif pct >= 0.55:
        return 2
    else:
        return 1


def score_latent_demand(mentions, wishlist_pct=0):
    """Score latent demand on 1-5 scale (20% weight)."""
    if mentions >= 20 or wishlist_pct >= 0.15:
        return 5
    elif mentions >= 10 or wishlist_pct >= 0.10:
        return 4
    elif mentions >= 5 or wishlist_pct >= 0.05:
        return 3
    elif mentions >= 2:
        return 2
    else:
        return 1


def score_non_dinneroo_demand(orders, percentile_rank):
    """Score non-Dinneroo midweek demand on 1-5 scale (20% weight)."""
    if percentile_rank >= 90:
        return 5
    elif percentile_rank >= 75:
        return 4
    elif percentile_rank >= 50:
        return 3
    elif percentile_rank >= 25:
        return 2
    else:
        return 1


def calculate_performance_score(dish, perf_df, opz_data):
    """Calculate performance track score (60% weight).
    
    Components:
    - orders_per_zone: 35%
    - rating: 15%
    - kids_happy: 10%
    """
    scores = {}
    
    # Orders per zone (35%)
    if dish in opz_data:
        scores['opz'] = score_orders_per_zone(opz_data[dish]['orders_per_zone'])
    else:
        scores['opz'] = 1
    
    # Get performance data
    perf_row = perf_df[perf_df['dish_type'] == dish] if len(perf_df) > 0 else pd.DataFrame()
    
    if len(perf_row) > 0:
        row = perf_row.iloc[0]
        
        # Kids happy (10%) - from survey
        scores['kids_happy'] = score_kids_happy(row.get('kids_happy_rate'))
        
        # Use adult satisfaction as proxy for rating if no direct rating
        adult_sat = row.get('adult_satisfaction_rate')
        if pd.notna(adult_sat):
            # Map satisfaction to rating-like scale
            if adult_sat >= 0.9:
                scores['rating'] = 5
            elif adult_sat >= 0.85:
                scores['rating'] = 4
            elif adult_sat >= 0.8:
                scores['rating'] = 3
            elif adult_sat >= 0.7:
                scores['rating'] = 2
            else:
                scores['rating'] = 1
        else:
            scores['rating'] = 3
    else:
        scores['kids_happy'] = 3
        scores['rating'] = 3
    
    # Weighted score (out of 5)
    # opz: 35/60, rating: 15/60, kids_happy: 10/60
    perf_score = (
        scores['opz'] * (0.35 / 0.60) +
        scores['rating'] * (0.15 / 0.60) +
        scores['kids_happy'] * (0.10 / 0.60)
    )
    
    return perf_score, scores


def calculate_opportunity_score(dish, latent_df, non_din_df):
    """Calculate opportunity track score (40% weight).
    
    Components:
    - latent_demand: 20%
    - non_dinneroo_demand: 20%
    """
    scores = {}
    
    # Latent demand (20%)
    latent_row = latent_df[latent_df['dish_type'] == dish] if len(latent_df) > 0 else pd.DataFrame()
    if len(latent_row) > 0:
        scores['latent'] = latent_row.iloc[0].get('latent_demand_score', 2)
    else:
        scores['latent'] = 2
    
    # Non-Dinneroo demand (20%)
    if len(non_din_df) > 0 and dish in non_din_df['dish_type'].values:
        non_din_row = non_din_df[non_din_df['dish_type'] == dish].iloc[0]
        orders = non_din_row.get('orders', 0)
        # Calculate percentile rank
        all_orders = non_din_df['orders'].values
        percentile = (all_orders < orders).sum() / len(all_orders) * 100
        scores['non_din'] = score_non_dinneroo_demand(orders, percentile)
    else:
        scores['non_din'] = 2
    
    # Weighted score (out of 5)
    # latent: 20/40, non_din: 20/40
    opp_score = (
        scores['latent'] * 0.5 +
        scores['non_din'] * 0.5
    )
    
    return opp_score, scores


def assign_quadrant(perf_score, opp_score, on_dinneroo=True):
    """Assign to Anna's official quadrant names.
    
    Official names from config/mvp_thresholds.json:
    - Core Drivers: High Performance + High Opportunity (protect & expand)
    - Preference Drivers: Low Performance + High Opportunity (build volume)
    - Demand Boosters: High Performance + Low Opportunity (improve demand signals)
    - Deprioritised: Low Performance + Low Opportunity (don't invest)
    """
    threshold = 3.0
    
    if perf_score is None:
        # No performance data - use opportunity only
        if opp_score >= threshold:
            return "Preference Drivers"  # High opportunity, needs volume
        else:
            return "Deprioritised"  # Low opportunity
    
    if perf_score >= threshold and opp_score >= threshold:
        return "Core Drivers"
    elif perf_score >= threshold and opp_score < threshold:
        return "Demand Boosters"
    elif perf_score < threshold and opp_score >= threshold:
        return "Preference Drivers"
    else:
        return "Deprioritised"


def assign_tier(unified_score):
    """Assign tier based on unified score.
    
    Thresholds adjusted for 60/40 performance/opportunity split reality:
    - With opportunity scores mostly 1.5-2.5, even perfect perf (5.0) only yields 3.6
    - Old 3.8 threshold was mathematically unreachable for most dishes
    """
    if unified_score >= 3.5:
        return "Tier 1: Must-Have"
    elif unified_score >= 3.0:
        return "Tier 2: Should-Have"
    elif unified_score >= 2.5:
        return "Tier 3: Nice-to-Have"
    else:
        return "Tier 4: Monitor"


def main():
    print("=" * 60)
    print("DISH SCORING v3.1 - Fixed Framework")
    print("=" * 60)
    print("\nKey fix: Removed zone_ranking_strength penalty")
    print("- Was penalizing dishes with limited availability")
    print("- Pho had 323 orders/zone but scored 1/5 on zone_ranking")
    print("- Redistributed weight to orders_per_zone (now 35%)")
    
    # Load data
    print("\n1. Loading data...")
    data = load_data()
    
    # Calculate orders per zone
    print("\n2. Calculating orders per zone...")
    opz_data = calculate_orders_per_zone(data)
    print(f"   Calculated for {len(opz_data)} dishes")
    
    # Get dish list
    perf_df = data.get('performance', pd.DataFrame())
    opp_df = data.get('opportunity', pd.DataFrame())
    latent_df = data.get('latent_demand', pd.DataFrame())
    non_din_df = data.get('non_dinneroo', pd.DataFrame())
    
    # Combine dish types from all sources
    all_dishes = set()
    if len(perf_df) > 0:
        all_dishes.update(perf_df['dish_type'].dropna().tolist())
    if len(opp_df) > 0:
        all_dishes.update(opp_df['dish_type'].dropna().tolist())
    
    print(f"\n3. Scoring {len(all_dishes)} dishes...")
    
    results = []
    for dish in sorted(all_dishes):
        # Performance score (60%)
        perf_score, perf_components = calculate_performance_score(dish, perf_df, opz_data)
        
        # Opportunity score (40%)
        opp_score, opp_components = calculate_opportunity_score(dish, latent_df, non_din_df)
        
        # Unified score (60/40 weighted)
        unified_score = perf_score * 0.6 + opp_score * 0.4
        
        # Get metadata
        on_dinneroo = True
        cuisine = ''
        order_volume = None
        zone_count = None
        opz_value = None
        
        if len(opp_df) > 0 and dish in opp_df['dish_type'].values:
            row = opp_df[opp_df['dish_type'] == dish].iloc[0]
            on_dinneroo = row.get('on_dinneroo', True)
            cuisine = row.get('cuisine', '')
            order_volume = row.get('order_volume')
            zone_count = row.get('zones_available')
        
        if dish in opz_data:
            opz_value = opz_data[dish]['orders_per_zone']
        
        # Kids happy from performance
        kids_happy = None
        if len(perf_df) > 0 and dish in perf_df['dish_type'].values:
            kids_happy = perf_df[perf_df['dish_type'] == dish].iloc[0].get('kids_happy_rate')
        
        # Quadrant and tier
        quadrant = assign_quadrant(perf_score, opp_score, on_dinneroo)
        tier = assign_tier(unified_score)
        
        results.append({
            'dish_type': dish,
            'cuisine': cuisine,
            'on_dinneroo': on_dinneroo,
            'unified_score': round(unified_score, 2),
            'performance_score': round(perf_score, 2),
            'opportunity_score': round(opp_score, 2),
            'tier': tier,
            'quadrant': quadrant,
            'order_volume': order_volume,
            'zone_count': zone_count,
            'orders_per_zone': round(opz_value, 1) if opz_value else None,
            'kids_happy': round(kids_happy, 2) if kids_happy and pd.notna(kids_happy) else None,
            'perf_opz_score': perf_components.get('opz'),
            'perf_rating_score': perf_components.get('rating'),
            'perf_kids_score': perf_components.get('kids_happy'),
            'opp_latent_score': opp_components.get('latent'),
            'opp_nondin_score': opp_components.get('non_din'),
            'is_core_driver': dish in ANNA_CORE_DRIVERS
        })
    
    # Create dataframe and sort by unified score
    df = pd.DataFrame(results)
    df = df.sort_values('unified_score', ascending=False).reset_index(drop=True)
    df['rank'] = df.index + 1
    
    # Reorder columns
    col_order = ['rank', 'dish_type', 'cuisine', 'on_dinneroo', 'unified_score',
                 'performance_score', 'opportunity_score', 'tier', 'quadrant',
                 'order_volume', 'zone_count', 'orders_per_zone', 'kids_happy',
                 'is_core_driver', 'perf_opz_score', 'perf_rating_score', 
                 'perf_kids_score', 'opp_latent_score', 'opp_nondin_score']
    df = df[[c for c in col_order if c in df.columns]]
    
    # Save outputs
    print("\n4. Saving outputs...")
    
    # Priority 100
    priority_path = OUTPUT_PATH / "priority_100_unified.csv"
    df.head(100).to_csv(priority_path, index=False)
    print(f"   Saved: {priority_path}")
    
    # 2x2 Matrix
    matrix_df = df[['dish_type', 'performance_score', 'opportunity_score', 'quadrant', 'unified_score']].copy()
    matrix_path = OUTPUT_PATH / "dish_2x2_unified.csv"
    matrix_df.to_csv(matrix_path, index=False)
    print(f"   Saved: {matrix_path}")
    
    # Dish tiers
    tiers_df = df[['rank', 'dish_type', 'tier', 'unified_score', 'performance_score', 
                   'opportunity_score', 'quadrant', 'cuisine', 'on_dinneroo',
                   'order_volume', 'orders_per_zone']].copy()
    tiers_df.columns = ['Rank', 'Dish', 'Tier', 'Unified Score', 'Performance Score',
                        'Opportunity Score', 'Quadrant', 'Cuisine', 'On Dinneroo',
                        'Order Volume', 'Orders per Zone']
    tiers_df['Tier'] = tiers_df['Tier'].str.replace('Tier \\d+: ', '', regex=True)
    tiers_path = DELIVERABLES_PATH / "dish_tiers.csv"
    tiers_df.to_csv(tiers_path, index=False)
    print(f"   Saved: {tiers_path}")
    
    # JSON for dashboard (docs/data/priority_100_unified.json)
    json_output_path = BASE_PATH / "docs" / "data" / "priority_100_unified.json"
    json_data = {
        "generated": datetime.now().isoformat(),
        "framework_version": "3.1",
        "total_dishes": len(df),
        "tier_distribution": df['tier'].value_counts().to_dict(),
        "quadrant_distribution": df['quadrant'].value_counts().to_dict(),
        "dishes": df.head(100).to_dict(orient='records')
    }
    # Clean NaN values for JSON
    import math
    def clean_for_json(obj):
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(v) for v in obj]
        elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj
    json_data = clean_for_json(json_data)
    with open(json_output_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"   Saved: {json_output_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print("\nTier Distribution:")
    for tier, count in df['tier'].value_counts().sort_index().items():
        print(f"  {tier}: {count}")
    
    print("\nTop 15 Dishes:")
    print(df[['rank', 'dish_type', 'unified_score', 'tier', 'is_core_driver']].head(15).to_string(index=False))
    
    # Validate against Anna's Core Drivers
    print("\n" + "=" * 60)
    print("VALIDATION: Anna's Core Drivers")
    print("=" * 60)
    
    core_driver_ranks = df[df['is_core_driver']][['rank', 'dish_type', 'unified_score', 'tier']]
    print("\nCore Driver Rankings:")
    print(core_driver_ranks.to_string(index=False))
    
    # Check if core drivers are in top tiers
    cd_in_top_10 = len(core_driver_ranks[core_driver_ranks['rank'] <= 10])
    cd_in_tier_1_2 = len(core_driver_ranks[core_driver_ranks['tier'].isin(['Tier 1: Must-Have', 'Tier 2: Should-Have'])])
    
    print(f"\nCore Drivers in Top 10: {cd_in_top_10}/8")
    print(f"Core Drivers in Tier 1-2: {cd_in_tier_1_2}/8")
    
    if cd_in_tier_1_2 >= 6:
        print("\n✓ Framework validated - Core Drivers ranking correctly")
    else:
        print("\n⚠ Warning: Some Core Drivers may still be ranking too low")
    
    print("\n✓ Dish scoring v3.1 complete!")
    
    # Auto-sync to dashboard
    print("\n" + "=" * 60)
    print("AUTO-SYNCING TO DASHBOARD")
    print("=" * 60)
    
    sync_script = BASE_PATH / "scripts" / "sync_dish_data.py"
    if sync_script.exists():
        import subprocess
        import sys
        result = subprocess.run([sys.executable, str(sync_script)], cwd=BASE_PATH)
        if result.returncode == 0:
            print("\n✓ Dashboard sync complete!")
        else:
            print("\n⚠ Dashboard sync failed - run manually: python3 scripts/sync_dish_data.py")
    else:
        print(f"\n⚠ Sync script not found: {sync_script}")
        print("  Dashboard data not updated")
    
    return df


if __name__ == "__main__":
    main()

