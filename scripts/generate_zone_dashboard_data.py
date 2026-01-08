#!/usr/bin/env python3
"""
Generate zone analysis dashboard data with unified definitions.

This script uses:
1. Anna's ground truth (anna_zone_dish_counts.csv) for Core 7 cuisine counts
2. Zone gap report for additional zone metadata
3. Existing zone_mvp_status.json for performance data where available
4. Canonical definitions from scripts/utils/definitions.py

OUTPUT: Two-level cuisine structure (Core 7 + sub-cuisines)
- MVP status calculated from Core 7 counts using tiered approach
- Sub-cuisines for drill-down analysis

SOURCE OF TRUTH: Anna's categorisations via definitions.py
- 7 Cuisines: Asian, Italian, Indian, Healthy, Mexican, Middle Eastern, British
- MVP Ready = 5+ cuisines, Near MVP = 4, Progressing = 3
"""

import pandas as pd
import json
from pathlib import Path
import sys

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import canonical definitions
from utils.definitions import (
    CORE_7,
    REQUIRED_FOR_MVP,
    get_core_7,
    get_mvp_status,
    get_cuisine_pass,
    MVP_STATUS_TIERS,
)

# Paths
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
SOURCE_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE"
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "data"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "data"

# Core Drivers from Anna's Dish Scoring (for reference)
CORE_DRIVERS = [
    "Pho", "South Asian / Indian Curry", "Biryani", "Fried Rice",
    "Sushi", "Katsu", "Rice Bowl", "Noodles"
]

# Recruitment suggestions by cuisine gap
RECRUITMENT_SUGGESTIONS = {
    "Indian": ["Dishoom", "Kricket", "Tiffin Tin", "Tadka House", "Chaska"],
    "Asian": ["Wagamama", "Itsu", "Pho", "Banana Tree", "Giggling Squid"],
    "Italian": ["PizzaExpress", "Prezzo", "Bella Italia", "Milano"],
    "Healthy": ["Farmer J", "LEON", "atis", "Cocotte"],
    "Mexican": ["Las Iguanas", "Zambrero UK", "Tula Ireland"],
    "Middle Eastern": ["Shaku Maku", "Umi Falafel", "Yacob's Kitchen"],
    "British": ["Bill's"],
}


def load_anna_ground_truth():
    """
    Load Anna's ground truth Core 7 cuisine counts per zone.
    This is the SOURCE OF TRUTH for cuisine coverage.
    """
    file_path = DATA_DIR / "anna_zone_dish_counts.csv"
    df = pd.read_csv(file_path)
    print(f"Loaded Anna's ground truth: {len(df)} zones")
    return df


def load_zone_gap_report():
    """Load additional zone metadata from gap report."""
    file_path = DATA_DIR / "zone_gap_report.csv"
    if file_path.exists():
        df = pd.read_csv(file_path)
        print(f"Loaded zone gap report: {len(df)} zones")
        return df
    return None


def load_existing_mvp_data():
    """Load existing MVP status data for performance metrics."""
    mvp_file = DOCS_DATA_DIR / "zone_mvp_status.json"
    if mvp_file.exists():
        with open(mvp_file) as f:
            data = json.load(f)
        print(f"Loaded existing MVP data: {len(data)} zones")
        return {z['zone']: z for z in data}
    return {}


def load_snowflake_sub_cuisines():
    """
    Load sub-cuisine data from Snowflake for granular drill-down.
    Filters to valid cuisine tags only.
    """
    orders_file = SOURCE_DIR / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
    if not orders_file.exists():
        print("Snowflake orders file not found, skipping sub-cuisine data")
        return {}
    
    # Valid sub-cuisine tags (filter out junk like "Burgers", "Meal Deals")
    VALID_SUB_CUISINES = [
        'japanese', 'thai', 'vietnamese', 'chinese', 'korean', 'asian',
        'italian', 'indian', 'mexican', 'lebanese', 'mediterranean',
        'latin american', 'turkish', 'greek', 'british'
    ]
    
    df = pd.read_csv(orders_file, usecols=['ZONE_NAME', 'CUISINE'])
    
    # Filter to valid cuisines and aggregate by zone
    df['cuisine_lower'] = df['CUISINE'].str.lower().str.strip()
    df = df[df['cuisine_lower'].isin(VALID_SUB_CUISINES)]
    
    # Count orders per sub-cuisine per zone
    zone_sub_cuisines = {}
    for zone, group in df.groupby('ZONE_NAME'):
        sub_counts = group['cuisine_lower'].value_counts().to_dict()
        zone_sub_cuisines[zone] = sub_counts
    
    print(f"Loaded sub-cuisine data for {len(zone_sub_cuisines)} zones")
    return zone_sub_cuisines


def calculate_health_score(zone_data):
    """
    Calculate zone health score (0-100) using ZONE_AGENT weights.
    """
    repeat_rate = zone_data.get('repeat_rate', 0) or 0
    rating = zone_data.get('avg_rating', 0) or 0
    core_7_count = zone_data.get('core_7_count', 0) or 0
    dishes = zone_data.get('total_dishes', 0) or 0
    orders = zone_data.get('orders', 0) or 0
    
    # Component scores (normalized to 0-1)
    repeat_score = min(repeat_rate / 0.40, 1.0) if repeat_rate else 0
    rating_score = max(0, (rating - 3) / 2) if rating >= 3 else 0
    cuisine_score = min(core_7_count / 7, 1.0)
    dish_score = min(dishes / 50, 1.0)
    volume_score = min(orders / 1000, 1.0) if orders > 0 else 0
    
    # Weighted composite per ZONE_AGENT
    health = (
        repeat_score * 0.30 +
        rating_score * 0.25 +
        cuisine_score * 0.20 +
        dish_score * 0.15 +
        volume_score * 0.10
    ) * 100
    
    return round(health, 1)


def build_priority_actions(zone_data):
    """Build priority recruitment actions based on cuisine gaps."""
    actions = []
    core_7 = zone_data.get('core_7', {})
    
    for cuisine in CORE_7:
        cuisine_key = cuisine.lower().replace(' ', '_')
        dish_count = core_7.get(cuisine_key, 0)
        if dish_count == 0:
            suggestions = RECRUITMENT_SUGGESTIONS.get(cuisine, [])[:3]
            actions.append({
                "type": "cuisine",
                "gap": cuisine,
                "action": f"Recruit {', '.join(suggestions)}" if suggestions else f"Recruit {cuisine} partner",
                "impact": f"Adds {cuisine} coverage"
            })
    
    return actions[:5]  # Top 5 actions


def main():
    print("=" * 60)
    print("ZONE DASHBOARD DATA GENERATOR (Unified Definitions)")
    print("=" * 60)
    print()
    print(f"Using canonical Core 7: {CORE_7}")
    print()
    
    # Load data sources
    anna_df = load_anna_ground_truth()
    gap_df = load_zone_gap_report()
    existing_mvp = load_existing_mvp_data()
    sub_cuisines = load_snowflake_sub_cuisines()
    
    # Create lookup from gap report by zone name
    gap_lookup = {}
    if gap_df is not None:
        for _, row in gap_df.iterrows():
            gap_lookup[row['zone']] = row
    
    # Build zone data with two-level cuisine structure
    zones = []
    
    for _, row in anna_df.iterrows():
        zone_name = row['zone_name']
        zone_code = row['zone_code']
        
        # Get existing MVP data if available
        mvp_data = existing_mvp.get(zone_name, {})
        gap_data = gap_lookup.get(zone_name, {})
        
        # Core 7 cuisine counts from Anna's ground truth (SOURCE OF TRUTH)
        core_7 = {
            'asian': int(row.get('asian', 0) or 0),
            'italian': int(row.get('italian', 0) or 0),
            'indian': int(row.get('indian', 0) or 0),
            'healthy': int(row.get('healthy', 0) or 0),
            'mexican': int(row.get('mexican', 0) or 0),
            'middle_eastern': int(row.get('middle_eastern', 0) or 0),
            'british': int(row.get('british', 0) or 0),
        }
        
        # Calculate core_7_count (number of cuisines with dishes > 0)
        core_7_count = sum(1 for v in core_7.values() if v > 0)
        
        # Build cuisines list (Core 7 cuisines present)
        cuisines_present = [
            cuisine for cuisine in CORE_7 
            if core_7.get(cuisine.lower().replace(' ', '_'), 0) > 0
        ]
        
        # Get sub-cuisines from Snowflake (for granular drill-down)
        zone_sub_cuisines = sub_cuisines.get(zone_name, {})
        
        # Determine if zone has orders
        orders = mvp_data.get('order_count', 0) or 0
        if isinstance(gap_data, pd.Series):
            orders = orders or int(gap_data.get('orders', 0) or 0)
        has_orders = orders > 0
        
        # Calculate MVP status using canonical function
        mvp_status = get_mvp_status(core_7_count, has_orders)
        cuisine_pass = get_cuisine_pass(core_7_count)
        
        # Build zone data structure
        zone_data = {
            # Identity
            "zone": zone_name,
            "zone_code": zone_code,
            "region": row.get('region', 'Unknown'),
            "city": row.get('city', ''),
            "large_city": row.get('large_city', ''),
            
            # TWO-LEVEL CUISINE STRUCTURE
            "core_7": core_7,
            "sub_cuisines": zone_sub_cuisines,
            
            # Cuisine summary
            "core_7_count": core_7_count,
            "cuisines": cuisines_present,
            "cuisine_pass": cuisine_pass,
            
            # MVP status (using canonical tiered approach)
            "mvp_status": mvp_status,
            
            # Supply metrics
            "partners": int(row.get('num_brands', 0) or 0),
            "total_dishes": int(row.get('total_dishes', 0) or 0),
            
            # Performance metrics (from existing MVP data)
            "orders": orders,
            "customer_count": mvp_data.get('customer_count', 0),
            "repeat_rate": mvp_data.get('repeat_rate', 0),
            "avg_rating": mvp_data.get('avg_rating'),
            "rating_pass": mvp_data.get('rating_pass', False),
            "repeat_pass": mvp_data.get('repeat_pass', False),
            
            # Flags
            "has_order_data": has_orders,
        }
        
        # Calculate health score
        zone_data['health_score'] = calculate_health_score(zone_data)
        
        # Build priority actions
        zone_data['priority_actions'] = build_priority_actions(zone_data)
        
        zones.append(zone_data)
    
    # Sort by orders (descending), then by health score
    zones.sort(key=lambda x: (-(x['orders'] or 0), -x['health_score']))
    
    # Calculate summary statistics
    mvp_counts = {}
    for z in zones:
        status = z['mvp_status']
        mvp_counts[status] = mvp_counts.get(status, 0) + 1
    
    # Zones with orders vs without
    zones_with_orders = len([z for z in zones if z['orders'] and z['orders'] > 0])
    zones_without_orders = len(zones) - zones_with_orders
    
    # Top zones by orders
    top_by_orders = [
        {'zone': z['zone'], 'orders': z['orders'], 'core_7_count': z['core_7_count'],
         'mvp_status': z['mvp_status'], 'repeat_rate': z.get('repeat_rate', 0)}
        for z in zones if z['orders'] and z['orders'] > 0
    ][:15]
    
    # Top zones by health
    top_by_health = sorted(zones, key=lambda x: -x['health_score'])[:15]
    top_by_health = [
        {'zone': z['zone'], 'health_score': z['health_score'], 'core_7_count': z['core_7_count'],
         'mvp_status': z['mvp_status'], 'orders': z['orders']}
        for z in top_by_health
    ]
    
    # Zones needing attention (high orders but not MVP Ready)
    attention_zones = [
        {'zone': z['zone'], 'orders': z['orders'], 'core_7_count': z['core_7_count'],
         'mvp_status': z['mvp_status'], 'missing_cuisines': [c for c in CORE_7 if z['core_7'].get(c.lower().replace(' ', '_'), 0) == 0][:3]}
        for z in zones 
        if z['orders'] and z['orders'] > 100 and z['mvp_status'] != 'MVP Ready'
    ][:20]
    
    # Build output
    output = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "data_sources": {
            "core_7_counts": "anna_zone_dish_counts.csv (Anna's ground truth)",
            "sub_cuisines": "ALL_DINNEROO_ORDERS.csv (Snowflake)",
            "performance": "zone_mvp_status.json (existing calculations)",
        },
        "methodology": {
            "definitions_module": "scripts/utils/definitions.py",
            "core_7_cuisines": CORE_7,
            "mvp_tiers": {
                "MVP Ready": "5+ Core 7 cuisines (North star)",
                "Near MVP": "4 cuisines (Almost there)",
                "Progressing": "3 cuisines (Data inflection point)",
                "Developing": "1-2 cuisines (Early stage)",
                "Supply Only": "Has partners, no orders",
                "Not Started": "No partners",
            },
            "health_score_weights": {
                "repeat_rate": "30%",
                "satisfaction": "25%",
                "cuisine_coverage": "20%",
                "dish_variety": "15%",
                "volume": "10%",
            }
        },
        "summary": {
            "total_zones": len(zones),
            "zones_with_orders": zones_with_orders,
            "zones_without_orders": zones_without_orders,
            "mvp_status_breakdown": mvp_counts,
            "total_partners": sum(z['partners'] for z in zones),
            "total_dishes": sum(z['total_dishes'] for z in zones),
            "avg_health_score": round(sum(z['health_score'] for z in zones) / len(zones), 1),
        },
        "cuisine_coverage": {
            cuisine: len([z for z in zones if z['core_7'].get(cuisine.lower().replace(' ', '_'), 0) > 0])
            for cuisine in CORE_7
        },
        "top_zones_by_orders": top_by_orders,
        "top_zones_by_health": top_by_health,
        "zones_needing_attention": attention_zones,
        "zones": zones
    }
    
    # Write zone_analysis.json
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "zone_analysis.json"
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nOutput written to {output_file}")
    
    # Also update zone_mvp_status.json with new structure
    mvp_status_file = OUTPUT_DIR / "zone_mvp_status.json"
    mvp_status_data = [
        {
            "zone": z['zone'],
            "zone_code": z['zone_code'],
            "core_7": z['core_7'],
            "sub_cuisines": z['sub_cuisines'],
            "core_7_count": z['core_7_count'],
            "cuisine_count": z['core_7_count'],  # Alias for backwards compatibility
            "cuisines": z['cuisines'],
            "cuisine_pass": z['cuisine_pass'],
            "mvp_status": z['mvp_status'],
            "orders": z['orders'],
            "order_count": z['orders'],  # Alias for backwards compatibility
            "repeat_rate": z['repeat_rate'],
            "avg_rating": z['avg_rating'],
            "rating_pass": z['rating_pass'],
            "repeat_pass": z['repeat_pass'],
            "partners": z['partners'],
            "total_dishes": z['total_dishes'],
            "health_score": z['health_score'],
        }
        for z in zones
    ]
    
    with open(mvp_status_file, 'w') as f:
        json.dump(mvp_status_data, f, indent=2, default=str)
    
    print(f"Updated {mvp_status_file}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"\nMVP Status Breakdown:")
    for status in ['MVP Ready', 'Near MVP', 'Progressing', 'Developing', 'Supply Only', 'Not Started']:
        count = mvp_counts.get(status, 0)
        print(f"  {status:<15} {count:>5} zones")
    
    print(f"\nCuisine Coverage (of {len(zones)} zones):")
    for cuisine in CORE_7:
        count = output['cuisine_coverage'][cuisine]
        pct = count / len(zones) * 100
        print(f"  {cuisine:<18} {count:>4} zones ({pct:>5.1f}%)")
    
    print(f"\nTwo-level structure enabled:")
    print(f"  - Core 7 for MVP calculations")
    print(f"  - Sub-cuisines for drill-down analysis")


if __name__ == "__main__":
    main()
