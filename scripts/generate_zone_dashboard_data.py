#!/usr/bin/env python3
"""
Generate zone analysis dashboard data combining:
1. Existing zone_mvp_status.json (established MVP calculations with repeat_rate, rating_pass, etc.)
2. Anna's ground truth zone_gap_report.csv (all 1,306 zones with cuisine data)
3. MVP checklist with cuisine + dish type coverage for Route to MVP feature

This script preserves the existing MVP work and extends it with Anna's ground truth data.

SOURCE OF TRUTH: Anna's categorisations
- 7 Cuisines: Asian, Italian, Indian, Healthy, Mexican, Middle Eastern, British
- 24 Dish Types: From Anna's Item Categorisation CSV
"""

import pandas as pd
import json
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
SOURCE_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE" / "anna_slides"
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "data"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "data"

# Anna's 7 Cuisines (Source of Truth)
ANNA_CUISINES = ["Asian", "Italian", "Indian", "Healthy", "Mexican", "Middle Eastern", "British"]

# Core Drivers from dish_scoring_anna_aligned.csv (8 dish types that drive performance)
CORE_DRIVERS = [
    "Pho",
    "South Asian / Indian Curry", 
    "Biryani",
    "Fried Rice",
    "Sushi",
    "Katsu",
    "Rice Bowl",
    "Noodles"
]

# Preference Drivers (5)
PREFERENCE_DRIVERS = [
    "Grain Bowl",
    "East Asian Curry",
    "Shepherd's Pie",
    "Shawarma",
    "Fajitas"
]

# Demand Boosters (2)
DEMAND_BOOSTERS = [
    "Protein & Veg",
    "Pizza"
]

# Partner to dish type mapping (from Anna's Item Categorisation)
# This maps which dish types each partner can provide
PARTNER_DISH_TYPES = {
    "Chaska": ["Biryani", "South Asian / Indian Curry"],
    "Dishoom": ["Biryani", "South Asian / Indian Curry"],
    "Tadka House": ["Biryani", "South Asian / Indian Curry"],
    "Kricket": ["South Asian / Indian Curry"],
    "Saravana Bhavan": ["South Asian / Indian Curry"],
    "Tiffin Tin": ["South Asian / Indian Curry"],
    "Pho": ["Pho", "Rice Bowl", "Noodles", "Fried Rice", "East Asian Curry"],
    "Wagamama": ["Katsu", "East Asian Curry"],
    "Itsu": ["Katsu", "Rice Bowl", "Noodles", "Poke", "Sushi"],
    "Banana Tree": ["Katsu", "Rice Bowl", "Noodles", "Pad Thai"],
    "Giggling Squid": ["Rice Bowl", "East Asian Curry"],
    "Ting Thai": ["Noodles", "East Asian Curry"],
    "Asia Villa": ["Noodles", "Fried Rice", "East Asian Curry"],
    "Zumuku": ["Katsu", "Rice Bowl", "Noodles", "East Asian Curry"],
    "Zumuku Sushi": ["Katsu"],
    "Kokoro": ["Katsu", "Rice Bowl", "Noodles"],
    "Iro Sushi": ["Katsu", "Noodles"],
    "TUK TUK-SGroup": ["Rice Bowl", "Fried Rice"],
    "Xian Street Food": ["Rice Bowl", "Fried Rice"],
    "Taste Of Hong Kong-DCN": ["Rice Bowl"],
    "Bill's": ["Pasta", "East Asian Curry", "Shawarma", "Shepherd's Pie"],
    "Bella Italia": ["Pasta", "Lasagne", "Pizza"],
    "Cacciari's": ["Pasta", "Lasagne"],
    "Milano": ["Pasta", "Pizza"],
    "PizzaExpress": ["Pasta", "Pizza"],
    "Prezzo": ["Pasta", "Pizza"],
    "PIZAZA-SGroup": ["Pasta"],
    "SOYO-SGroup": ["Pasta", "Lasagne", "Noodles"],
    "atis": ["Grain Bowl"],
    "Farmer J": ["Grain Bowl"],
    "Remedy Kitchen": ["Grain Bowl"],
    "The Salad Project": ["Grain Bowl"],
    "LEON": ["Grain Bowl"],
    "Cocotte": ["Protein & Veg"],
    "Yacob's Kitchen": ["Grain Bowl"],
    "Shaku Maku": ["Protein & Veg"],
    "Umi Falafel": [],
    "Zaatar Rathmines": [],
    "Las Iguanas": ["Chilli", "Fajitas"],
    "Tula Ireland": ["Burrito / Burrito Bowl", "Tacos", "Quesadilla"],
    "Zambrero UK": ["Tacos", "Burrito / Burrito Bowl", "Nachos"],
}

# Partner to cuisine mapping (from Anna's Item Categorisation)
PARTNER_CUISINES = {
    "Chaska": ["Indian"],
    "Dishoom": ["Indian"],
    "Tadka House": ["Indian"],
    "Kricket": ["Indian"],
    "Saravana Bhavan": ["Indian"],
    "Tiffin Tin": ["Indian"],
    "Pho": ["Asian"],
    "Wagamama": ["Asian"],
    "Itsu": ["Asian"],
    "Banana Tree": ["Asian"],
    "Giggling Squid": ["Asian"],
    "Ting Thai": ["Asian"],
    "Asia Villa": ["Asian"],
    "Zumuku": ["Asian"],
    "Zumuku Sushi": ["Asian"],
    "Kokoro": ["Asian"],
    "Iro Sushi": ["Asian"],
    "TUK TUK-SGroup": ["Asian"],
    "Xian Street Food": ["Asian"],
    "Taste Of Hong Kong-DCN": ["Asian"],
    "Bill's": ["Italian", "Middle Eastern", "British"],
    "Bella Italia": ["Italian"],
    "Cacciari's": ["Italian"],
    "Milano": ["Italian"],
    "PizzaExpress": ["Italian"],
    "Prezzo": ["Italian"],
    "PIZAZA-SGroup": ["Italian"],
    "SOYO-SGroup": ["Italian"],
    "atis": ["Healthy"],
    "Farmer J": ["Healthy"],
    "Remedy Kitchen": ["Healthy"],
    "The Salad Project": ["Healthy"],
    "LEON": ["Healthy"],
    "Cocotte": ["Healthy"],
    "Yacob's Kitchen": ["Middle Eastern"],
    "Shaku Maku": ["Middle Eastern"],
    "Umi Falafel": ["Middle Eastern"],
    "Zaatar Rathmines": ["Middle Eastern"],
    "Las Iguanas": ["Mexican"],
    "Tula Ireland": ["Mexican"],
    "Zambrero UK": ["Mexican"],
}

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

# Recruitment suggestions by Core Driver gap
CORE_DRIVER_RECRUITMENT = {
    "Pho": ["Pho"],
    "South Asian / Indian Curry": ["Dishoom", "Kricket", "Tiffin Tin"],
    "Biryani": ["Dishoom", "Chaska", "Tadka House"],
    "Fried Rice": ["Pho", "Asia Villa", "Xian Street Food"],
    "Sushi": ["Itsu", "Iro Sushi", "Zumuku Sushi"],
    "Katsu": ["Wagamama", "Itsu", "Kokoro"],
    "Rice Bowl": ["Itsu", "Pho", "Banana Tree", "Kokoro"],
    "Noodles": ["Pho", "Wagamama", "Banana Tree", "Ting Thai"],
}


def load_existing_mvp_data():
    """Load existing MVP status data (established calculations)."""
    mvp_file = DOCS_DATA_DIR / "zone_mvp_status.json"
    if mvp_file.exists():
        with open(mvp_file) as f:
            data = json.load(f)
        print(f"Loaded existing MVP data: {len(data)} zones")
        return {z['zone']: z for z in data}
    return {}


def load_anna_zone_data():
    """Load Anna's ground truth zone data (all 1,306 zones)."""
    zone_file = DATA_DIR / "zone_gap_report.csv"
    df = pd.read_csv(zone_file)
    print(f"Loaded Anna's zone data: {len(df)} zones")
    return df


def load_dish_scoring():
    """Load dish scoring data to get quadrant classifications."""
    scoring_file = DATA_DIR / "dish_scoring_anna_aligned.csv"
    if scoring_file.exists():
        df = pd.read_csv(scoring_file)
        return {row['dish_type']: row['quadrant'] for _, row in df.iterrows()}
    return {}


def parse_list_field(val):
    """Parse string representation of list."""
    if pd.isna(val) or val == '[]' or val == '':
        return []
    try:
        if isinstance(val, str):
            val = val.replace("'", '"')
            return json.loads(val)
        return val
    except:
        return []


def calculate_health_score(zone_data):
    """
    Calculate zone health score (0-100) using ZONE_AGENT weights.
    Uses existing MVP data where available.
    """
    # Get values
    repeat_rate = zone_data.get('repeat_rate', 0) or 0
    rating = zone_data.get('avg_rating', 0) or 0
    cuisines = zone_data.get('cuisine_count', 0) or zone_data.get('cuisines_count', 0) or 0
    dishes = zone_data.get('total_dishes', 0) or 0
    orders = zone_data.get('order_count', 0) or zone_data.get('orders', 0) or 0
    partners = zone_data.get('partners', 0) or 0
    
    # Component scores (normalized to 0-1)
    # Repeat rate is primary (30%) - from ZONE_AGENT
    repeat_score = min(repeat_rate / 0.40, 1.0) if repeat_rate else 0  # 40% = max
    
    # Rating/satisfaction (25%)
    rating_score = max(0, (rating - 3) / 2) if rating >= 3 else 0
    
    # Cuisine coverage (20%)
    cuisine_score = min(cuisines / 7, 1.0)  # 7 cuisines = max (Anna's categories)
    
    # Dish variety (15%)
    dish_score = min(dishes / 50, 1.0)  # 50 dishes = max
    
    # Volume (10%) - LOWEST weight per ZONE_AGENT
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


def build_mvp_checklist(zone_data):
    """
    Build the MVP checklist for a zone with cuisine and dish type coverage.
    Uses Anna's 7 cuisines as source of truth.
    """
    # Cuisine coverage (Anna's 7)
    cuisine_coverage = {}
    cuisine_columns = {
        "Asian": "asian_dishes",
        "Italian": "italian_dishes", 
        "Indian": "indian_dishes",
        "Healthy": "healthy_dishes",
        "Mexican": "mexican_dishes",
        "Middle Eastern": "middle_eastern_dishes",
        "British": "british_dishes"
    }
    
    cuisines_met = 0
    for cuisine, col in cuisine_columns.items():
        dish_count = zone_data.get(col, 0)
        has_cuisine = dish_count > 0
        if has_cuisine:
            cuisines_met += 1
        cuisine_coverage[cuisine.lower().replace(" ", "_")] = {
            "has": has_cuisine,
            "dishes": dish_count
        }
    
    # Core Driver coverage (8 dish types that drive performance)
    # We infer from cuisine presence since we don't have dish-level zone data
    core_driver_coverage = {}
    core_drivers_met = 0
    
    # Map core drivers to cuisines they require
    core_driver_cuisine_map = {
        "Pho": "Asian",
        "South Asian / Indian Curry": "Indian",
        "Biryani": "Indian", 
        "Fried Rice": "Asian",
        "Sushi": "Asian",
        "Katsu": "Asian",
        "Rice Bowl": "Asian",
        "Noodles": "Asian"
    }
    
    for driver in CORE_DRIVERS:
        required_cuisine = core_driver_cuisine_map.get(driver, "Asian")
        cuisine_col = cuisine_columns.get(required_cuisine, "asian_dishes")
        cuisine_dishes = zone_data.get(cuisine_col, 0)
        
        # A zone likely has the dish type if it has dishes in that cuisine
        # This is an approximation - we'd need dish-level data for exact coverage
        has_driver = cuisine_dishes > 0
        
        # Determine blocking reason if missing
        blocking_reason = None
        if not has_driver:
            blocking_reason = f"Blocked by missing {required_cuisine} cuisine"
        
        driver_key = driver.lower().replace(" ", "_").replace("/", "_")
        core_driver_coverage[driver_key] = {
            "has": has_driver,
            "blocked_by": blocking_reason
        }
        if has_driver:
            core_drivers_met += 1
    
    # Calculate progress
    total_checks = 7 + 8  # 7 cuisines + 8 core drivers
    checks_passed = cuisines_met + core_drivers_met
    overall_pct = round((checks_passed / total_checks) * 100)
    
    # Build priority actions
    priority_actions = []
    
    # Cuisine gaps
    for cuisine, data in cuisine_coverage.items():
        if not data["has"]:
            cuisine_name = cuisine.replace("_", " ").title()
            suggestions = RECRUITMENT_SUGGESTIONS.get(cuisine_name, [])[:3]
            action = {
                "type": "cuisine",
                "gap": cuisine_name,
                "action": f"Recruit {', '.join(suggestions)}" if suggestions else f"Recruit {cuisine_name} partner",
                "impact": "Unlocks cuisine coverage"
            }
            priority_actions.append(action)
    
    # Core driver gaps (only if cuisine is available)
    for driver, data in core_driver_coverage.items():
        if not data["has"] and not data.get("blocked_by"):
            driver_name = driver.replace("_", " ").title()
            suggestions = CORE_DRIVER_RECRUITMENT.get(driver_name, [])[:2]
            action = {
                "type": "core_driver",
                "gap": driver_name,
                "action": f"Add via {', '.join(suggestions)}" if suggestions else f"Add {driver_name}",
                "impact": "Unlocks Core Driver"
            }
            priority_actions.append(action)
    
    # Sort actions by impact (cuisine gaps first, then core drivers)
    priority_actions.sort(key=lambda x: 0 if x["type"] == "cuisine" else 1)
    
    return {
        "cuisine_coverage": cuisine_coverage,
        "core_driver_coverage": core_driver_coverage,
        "progress": {
            "cuisines": f"{cuisines_met}/7",
            "core_drivers": f"{core_drivers_met}/8",
            "overall_pct": overall_pct
        },
        "priority_actions": priority_actions[:5]  # Top 5 actions
    }


def main():
    print("=" * 60)
    print("ZONE DASHBOARD DATA GENERATOR")
    print("=" * 60)
    print()
    
    # Load existing MVP data (preserves established work)
    existing_mvp = load_existing_mvp_data()
    
    # Load Anna's ground truth
    anna_df = load_anna_zone_data()
    
    # Load dish scoring for quadrant info
    dish_quadrants = load_dish_scoring()
    
    # Build combined zone list
    zones = []
    zones_with_mvp_data = 0
    
    for _, row in anna_df.iterrows():
        zone_name = row['zone']
        
        # Check if we have existing MVP data for this zone
        mvp_data = existing_mvp.get(zone_name, {})
        
        # Combine Anna's ground truth with existing MVP data
        zone_data = {
            # Identity (from Anna)
            "zone": zone_name,
            "zone_code": row.get('zone_code', ''),
            "region": row.get('region', 'Unknown'),
            "city": row.get('city', ''),
            "large_city": row.get('large_city', ''),
            
            # Supply metrics (from Anna's ground truth)
            "partners": int(row.get('partners', 0)),
            "cuisines_count": int(row.get('cuisines_count', 0)),
            "total_dishes": int(row.get('total_dishes', 0)),
            
            # Cuisine breakdown (from Anna - SOURCE OF TRUTH)
            "asian_dishes": int(row.get('asian_dishes', 0)),
            "italian_dishes": int(row.get('italian_dishes', 0)),
            "indian_dishes": int(row.get('indian_dishes', 0)),
            "healthy_dishes": int(row.get('healthy_dishes', 0)),
            "mexican_dishes": int(row.get('mexican_dishes', 0)),
            "middle_eastern_dishes": int(row.get('middle_eastern_dishes', 0)),
            "british_dishes": int(row.get('british_dishes', 0)),
            
            # Gap analysis (from Anna)
            "cuisines_available": parse_list_field(row.get('cuisines_available', '[]')),
            "missing_essential": parse_list_field(row.get('missing_essential_cuisines', '[]')),
            "missing_recommended": parse_list_field(row.get('missing_recommended_cuisines', '[]')),
            "essential_coverage": row.get('essential_cuisine_coverage', '0%'),
            "dish_coverage": row.get('dish_coverage', '0%'),
            
            # Performance metrics - prefer existing MVP data, fall back to Anna's
            "orders": mvp_data.get('order_count') or int(row.get('orders', 0)),
            "customer_count": mvp_data.get('customer_count', 0),
            "repeat_rate": mvp_data.get('repeat_rate', 0),
            "avg_rating": mvp_data.get('avg_rating') or (row.get('avg_rating') if pd.notna(row.get('avg_rating')) else None),
            
            # MVP status - USE EXISTING if available (preserves established work)
            "mvp_status": mvp_data.get('mvp_status', 'Not Started'),
            "rating_pass": mvp_data.get('rating_pass', False),
            "repeat_pass": mvp_data.get('repeat_pass', False),
            "cuisine_pass": mvp_data.get('cuisine_pass', False),
            
            # Recruitment priority (from Anna's analysis)
            "recruitment_priority": row.get('recruitment_priority', 'Low'),
        }
        
        # If we have existing MVP data, mark it
        if mvp_data:
            zones_with_mvp_data += 1
            zone_data['has_order_data'] = True
        else:
            zone_data['has_order_data'] = False
            # For zones without order data, use supply-based status (NOT "Developing" - that's for live zones)
            if zone_data['partners'] == 0:
                zone_data['mvp_status'] = 'Not Started'
            else:
                # Has partners but no orders yet - "Supply Only" status
                zone_data['mvp_status'] = 'Supply Only'
        
        # Calculate health score using combined data
        zone_data['health_score'] = calculate_health_score(zone_data)
        
        # Calculate average dishes per partner
        if zone_data['partners'] > 0:
            zone_data['avg_dishes_per_partner'] = round(zone_data['total_dishes'] / zone_data['partners'], 1)
        else:
            zone_data['avg_dishes_per_partner'] = 0
        
        # Build MVP checklist for this zone
        zone_data['mvp_checklist'] = build_mvp_checklist(zone_data)
        
        zones.append(zone_data)
    
    # Sort by orders (descending), then by health score
    zones.sort(key=lambda x: (-(x['orders'] or 0), -x['health_score']))
    
    print(f"\nCombined data:")
    print(f"  Total zones (Anna's ground truth): {len(zones)}")
    print(f"  Zones with order/MVP data: {zones_with_mvp_data}")
    print(f"  Zones without order data: {len(zones) - zones_with_mvp_data}")
    
    # Calculate summary statistics
    mvp_counts = {}
    for z in zones:
        status = z['mvp_status']
        mvp_counts[status] = mvp_counts.get(status, 0) + 1
    
    priority_counts = {}
    for z in zones:
        priority = z['recruitment_priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # Region breakdown
    region_stats = {}
    for z in zones:
        region = z['region']
        if region not in region_stats:
            region_stats[region] = {'zone': 0, 'partners': 0, 'orders': 0, 'health_scores': []}
        region_stats[region]['zone'] += 1
        region_stats[region]['partners'] += z['partners']
        region_stats[region]['orders'] += z['orders'] or 0
        region_stats[region]['health_scores'].append(z['health_score'])
    
    # Calculate average health score and dishes per partner per region
    for region in region_stats:
        scores = region_stats[region]['health_scores']
        region_stats[region]['health_score'] = round(sum(scores) / len(scores), 1) if scores else 0
        del region_stats[region]['health_scores']
        # Avg dishes per partner for region
        if region_stats[region]['partners'] > 0:
            total_dishes = sum(z['total_dishes'] for z in zones if z['region'] == region)
            region_stats[region]['avg_dishes_per_partner'] = round(total_dishes / region_stats[region]['partners'], 1)
        else:
            region_stats[region]['avg_dishes_per_partner'] = 0
    
    # Zones with orders vs without
    zones_with_orders = len([z for z in zones if z['orders'] and z['orders'] > 0])
    zones_without_orders = len(zones) - zones_with_orders
    
    # Top zones
    top_by_orders = [
        {'zone': z['zone'], 'orders': z['orders'], 'partners': z['partners'], 
         'cuisines_count': z['cuisines_count'], 'repeat_rate': z.get('repeat_rate', 0)}
        for z in zones if z['orders'] and z['orders'] > 0
    ][:15]
    
    top_by_health = sorted(zones, key=lambda x: -x['health_score'])[:15]
    top_by_health = [
        {'zone': z['zone'], 'health_score': z['health_score'], 'partners': z['partners'],
         'cuisines_count': z['cuisines_count'], 'orders': z['orders']}
        for z in top_by_health
    ]
    
    # Zones needing attention (have orders but not MVP Ready)
    attention_zones = [
        {'zone': z['zone'], 'orders': z['orders'], 'partners': z['partners'],
         'cuisines_count': z['cuisines_count'], 'mvp_status': z['mvp_status'],
         'missing_essential': z['missing_essential'][:3] if z['missing_essential'] else []}
        for z in zones 
        if z['orders'] and z['orders'] > 100 and z['mvp_status'] != 'MVP Ready'
    ][:20]
    
    # Build output
    output = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "data_sources": {
            "mvp_data": "zone_mvp_status.json (established MVP calculations)",
            "ground_truth": "zone_gap_report.csv (Anna's 1,306 zones)",
            "dish_scoring": "dish_scoring_anna_aligned.csv (quadrant classifications)"
        },
        "methodology": {
            "note": "MVP status preserved from existing calculations where available",
            "source_of_truth": "Anna's categorisations",
            "cuisines": ANNA_CUISINES,
            "core_drivers": CORE_DRIVERS,
            "preference_drivers": PREFERENCE_DRIVERS,
            "demand_boosters": DEMAND_BOOSTERS,
            "health_score_weights": {
                "repeat_rate": "30% (PRIMARY - families returning)",
                "satisfaction": "25% (rating proxy)",
                "cuisine_coverage": "20%",
                "dish_variety": "15%",
                "volume": "10% (LOWEST - outcome not driver)"
            }
        },
        "summary": {
            "total_zones": len(zones),
            "zones_with_orders": zones_with_orders,
            "zones_without_orders": zones_without_orders,
            "zones_with_mvp_data": zones_with_mvp_data,
            "zones_with_partners": len([z for z in zones if z['partners'] > 0]),
            "mvp_status": mvp_counts,
            "recruitment_priority": priority_counts,
            "total_partners": sum(z['partners'] for z in zones),
            "total_dishes": sum(z['total_dishes'] for z in zones),
            "total_orders": sum(z['orders'] or 0 for z in zones),
            "avg_health_score": round(sum(z['health_score'] for z in zones) / len(zones), 1),
            "avg_dishes_per_partner": round(sum(z['total_dishes'] for z in zones) / max(sum(z['partners'] for z in zones), 1), 1),
        },
        "region_breakdown": region_stats,
        "top_zones_by_orders": top_by_orders,
        "top_zones_by_health": top_by_health,
        "zones_needing_attention": attention_zones,
        "zones": zones
    }
    
    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "zone_analysis.json"
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nOutput written to {output_file}")
    print(f"\nMVP Status breakdown:")
    for status, count in sorted(mvp_counts.items(), key=lambda x: -x[1]):
        print(f"    {status}: {count}")
    
    print(f"\nMVP Checklist added to all {len(zones)} zones")
    print(f"  - Cuisine coverage (Anna's 7 categories)")
    print(f"  - Core Driver coverage (8 dish types)")
    print(f"  - Priority actions for each zone")

if __name__ == "__main__":
    main()
