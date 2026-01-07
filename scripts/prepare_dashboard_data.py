#!/usr/bin/env python3
"""
Prepare Dashboard Data Script

Aggregates all data sources and prepares a unified JSON file for the
Consumer Insight Dashboard.

Output: docs/data/dashboard_data.json

Usage:
    python3 scripts/prepare_dashboard_data.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Output paths
OUTPUT_DIR = PROJECT_ROOT / "docs" / "data"
OUTPUT_FILE = OUTPUT_DIR / "dashboard_data.json"


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if pd.isna(obj):
            return None
        return super().default(obj)


def load_csv_safe(path: Path, comment: str = '#') -> Optional[pd.DataFrame]:
    """Safely load a CSV file, handling errors gracefully."""
    if not path.exists():
        print(f"  ⚠ File not found: {path.name}")
        return None
    try:
        df = pd.read_csv(path, low_memory=False, comment=comment)
        print(f"  ✓ Loaded {path.name}: {len(df):,} rows")
        return df
    except Exception as e:
        print(f"  ✗ Failed to load {path.name}: {e}")
        return None


def load_json_safe(path: Path) -> Optional[Dict]:
    """Safely load a JSON file, handling errors gracefully."""
    if not path.exists():
        print(f"  ⚠ File not found: {path.name}")
        return None
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        print(f"  ✓ Loaded {path.name}")
        return data
    except Exception as e:
        print(f"  ✗ Failed to load {path.name}: {e}")
        return None


def prepare_metadata() -> Dict[str, Any]:
    """Prepare metadata about data sources."""
    return {
        "generated": datetime.now().isoformat(),
        "version": "1.0",
        "sources": {
            "postOrder": {
                "name": "Post-Order Survey",
                "type": "survey",
                "description": "Feedback from customers after placing a Dinneroo order",
                "n": 1599,
                "lastUpdated": "2026-01-06"
            },
            "dropoff": {
                "name": "Dropoff Survey",
                "type": "survey",
                "description": "Feedback from people who browsed but didn't order",
                "n": 838,
                "lastUpdated": "2026-01-06"
            },
            "orders": {
                "name": "Snowflake Orders",
                "type": "behavioral",
                "description": "Actual Dinneroo orders (revealed preference)",
                "n": 82350,
                "lastUpdated": "2026-01-06"
            },
            "ratings": {
                "name": "Snowflake Ratings",
                "type": "behavioral",
                "description": "Customer ratings and comments",
                "n": 10713,
                "lastUpdated": "2026-01-06"
            },
            "annaGroundTruth": {
                "name": "Anna's Ground Truth",
                "type": "supply",
                "description": "Authoritative supply data (what we have)",
                "dishes": 155,
                "partners": 40,
                "sites": 756,
                "lastUpdated": "2025-12-01"
            },
            "transcripts": {
                "name": "Customer Transcripts",
                "type": "qualitative",
                "description": "88 customer interview transcripts",
                "n": 88,
                "lastUpdated": "2025-12-15"
            },
            "ogSurvey": {
                "name": "OG Survey",
                "type": "historical",
                "description": "Pre-launch survey (stated preference)",
                "n": 400,
                "lastUpdated": "2025-06-01",
                "biasWarning": True,
                "warning": "Pre-launch stated preference - validate with behavioral data"
            }
        }
    }


def prepare_dishes(project_root: Path) -> List[Dict[str, Any]]:
    """Prepare dish data from master dish list."""
    path = project_root / "DELIVERABLES" / "reports" / "MASTER_DISH_LIST_WITH_WORKINGS.csv"
    df = load_csv_safe(path)
    
    if df is None:
        return []
    
    dishes = []
    for _, row in df.iterrows():
        dish = {
            "rank": int(row.get("rank", 0)) if pd.notna(row.get("rank")) else None,
            "dishType": row.get("dish_type", ""),
            "cuisine": row.get("cuisine", ""),
            "onDinneroo": str(row.get("on_dinneroo", "")).upper() == "TRUE",
            "strategicPriority": row.get("strategic_priority", ""),
            "performance": {
                "avgSalesPerDish": float(row.get("avg_sales_per_dish")) if pd.notna(row.get("avg_sales_per_dish")) else None,
                "pctZonesTop5": row.get("pct_zones_top_5", ""),
                "deliverooRating": float(row.get("deliveroo_rating")) if pd.notna(row.get("deliveroo_rating")) else None,
                "mealSatisfaction": row.get("meal_satisfaction", ""),
                "repeatIntent": row.get("repeat_intent", "")
            },
            "opportunity": {
                "dishSuitability": float(row.get("dish_suitability")) if pd.notna(row.get("dish_suitability")) else None,
                "openTextRequests": int(row.get("open_text_requests")) if pd.notna(row.get("open_text_requests")) else None,
                "wishlistPct": row.get("wishlist_pct", "")
            },
            "context": {
                "demandStrength": float(row.get("demand_strength")) if pd.notna(row.get("demand_strength")) else None,
                "consumerPreference": float(row.get("consumer_preference")) if pd.notna(row.get("consumer_preference")) else None,
                "coverageGap": row.get("coverage_gap", "")
            }
        }
        dishes.append(dish)
    
    return dishes


def prepare_zones(project_root: Path) -> List[Dict[str, Any]]:
    """Prepare zone data from zone gap report."""
    path = project_root / "DATA" / "3_ANALYSIS" / "zone_gap_report.csv"
    df = load_csv_safe(path)
    
    if df is None:
        return []
    
    zones = []
    for _, row in df.iterrows():
        zone = {
            "zone": row.get("zone", ""),
            "region": row.get("region", ""),
            "orders": int(row.get("orders", 0)) if pd.notna(row.get("orders")) else 0,
            "partners": int(row.get("partners", 0)) if pd.notna(row.get("partners")) else 0,
            "cuisinesCount": int(row.get("cuisines_count", 0)) if pd.notna(row.get("cuisines_count")) else 0,
            "avgRating": float(row.get("avg_rating", 0)) if pd.notna(row.get("avg_rating")) else None,
            "isMvp": str(row.get("is_mvp", "")).lower() == "true",
            "mvpCriteriaMet": int(row.get("mvp_criteria_met", 0)) if pd.notna(row.get("mvp_criteria_met")) else 0,
            "cuisinesAvailable": row.get("cuisines_available", ""),
            "essentialCuisineCoverage": row.get("essential_cuisine_coverage", ""),
            "missingEssentialCuisines": row.get("missing_essential_cuisines", ""),
            "missingRecommendedCuisines": row.get("missing_recommended_cuisines", ""),
            "dishCoverage": row.get("dish_coverage", ""),
            "presentDishTypes": row.get("present_dish_types", ""),
            "missingDishTypes": row.get("missing_dish_types", ""),
            "recruitmentPriority": row.get("recruitment_priority", "")
        }
        zones.append(zone)
    
    return zones


def prepare_cuisine_gaps(project_root: Path) -> List[Dict[str, Any]]:
    """Prepare cuisine gap analysis data."""
    path = project_root / "DATA" / "3_ANALYSIS" / "cuisine_gap_analysis.csv"
    df = load_csv_safe(path)
    
    if df is None:
        return []
    
    gaps = []
    for _, row in df.iterrows():
        gap = {
            "cuisine": row.get("cuisine", ""),
            "itemCount": int(row.get("item_count", 0)) if pd.notna(row.get("item_count")) else 0,
            "brandCount": int(row.get("brand_count", 0)) if pd.notna(row.get("brand_count")) else 0,
            "avgRating": float(row.get("avg_rating", 0)) if pd.notna(row.get("avg_rating")) else None,
            "ratingCount": int(row.get("rating_count", 0)) if pd.notna(row.get("rating_count")) else 0,
            "orderCount": int(row.get("order_count", 0)) if pd.notna(row.get("order_count")) else 0,
            "gapType": row.get("gap_type", ""),
            "supplyVsAvg": float(row.get("supply_vs_avg", 0)) if pd.notna(row.get("supply_vs_avg")) else None,
            "ratingVsBenchmark": float(row.get("rating_vs_benchmark", 0)) if pd.notna(row.get("rating_vs_benchmark")) else None
        }
        gaps.append(gap)
    
    return gaps


def prepare_latent_demand(project_root: Path) -> Dict[str, Any]:
    """Prepare latent demand summary."""
    path = project_root / "DATA" / "3_ANALYSIS" / "latent_demand_summary.json"
    data = load_json_safe(path)
    
    if data is None:
        return {}
    
    return data


def prepare_survey_signals(project_root: Path) -> Dict[str, Any]:
    """Aggregate survey signals from multiple sources."""
    signals = {
        "postOrder": {},
        "dropoff": {},
        "combined": {}
    }
    
    # Load post-order survey
    post_order_path = project_root / "DATA" / "2_ENRICHED" / "post_order_enriched_COMPLETE.csv"
    post_order = load_csv_safe(post_order_path)
    
    if post_order is not None:
        signals["postOrder"] = {
            "totalResponses": len(post_order),
            "satisfactionDistribution": {},
            "topRestaurants": [],
            "topDishes": []
        }
        
        # Get satisfaction distribution if available
        for col in post_order.columns:
            if 'satisfaction' in col.lower() or 'feel about the meal' in col.lower():
                dist = post_order[col].value_counts().to_dict()
                signals["postOrder"]["satisfactionDistribution"] = {str(k): int(v) for k, v in dist.items() if pd.notna(k)}
                break
    
    # Load dropoff survey
    dropoff_path = project_root / "DATA" / "2_ENRICHED" / "DROPOFF_ENRICHED.csv"
    dropoff = load_csv_safe(dropoff_path)
    
    if dropoff is not None:
        signals["dropoff"] = {
            "totalResponses": len(dropoff),
            "barriers": {},
            "wishlistDishes": []
        }
    
    # Combined stats
    signals["combined"] = {
        "totalSurveyResponses": signals["postOrder"].get("totalResponses", 0) + signals["dropoff"].get("totalResponses", 0)
    }
    
    return signals


def prepare_behavioral_data(project_root: Path) -> Dict[str, Any]:
    """Prepare behavioral data summary from Snowflake."""
    behavioral = {
        "orders": {},
        "ratings": {},
        "partners": {}
    }
    
    # Load orders
    orders_path = project_root / "DATA" / "1_SOURCE" / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
    orders = load_csv_safe(orders_path)
    
    if orders is not None:
        behavioral["orders"] = {
            "totalOrders": len(orders),
            "uniqueCustomers": orders["CUSTOMER_ID"].nunique() if "CUSTOMER_ID" in orders.columns else 0,
            "uniquePartners": orders["PARTNER_NAME"].nunique() if "PARTNER_NAME" in orders.columns else 0,
            "uniqueZones": orders["ZONE_NAME"].nunique() if "ZONE_NAME" in orders.columns else 0
        }
        
        # Top zones by orders
        if "ZONE_NAME" in orders.columns:
            top_zones = orders["ZONE_NAME"].value_counts().head(10).to_dict()
            behavioral["orders"]["topZones"] = [{"zone": k, "orders": int(v)} for k, v in top_zones.items()]
        
        # Top partners by orders
        if "PARTNER_NAME" in orders.columns:
            top_partners = orders["PARTNER_NAME"].value_counts().head(10).to_dict()
            behavioral["orders"]["topPartners"] = [{"partner": k, "orders": int(v)} for k, v in top_partners.items()]
    
    # Load ratings
    ratings_path = project_root / "DATA" / "1_SOURCE" / "snowflake" / "DINNEROO_RATINGS.csv"
    ratings = load_csv_safe(ratings_path)
    
    if ratings is not None:
        behavioral["ratings"] = {
            "totalRatings": len(ratings),
            "avgRating": float(ratings["RATING_STARS"].mean()) if "RATING_STARS" in ratings.columns else None,
            "ratingDistribution": {}
        }
        
        if "RATING_STARS" in ratings.columns:
            dist = ratings["RATING_STARS"].value_counts().sort_index().to_dict()
            behavioral["ratings"]["ratingDistribution"] = {str(int(k)): int(v) for k, v in dist.items() if pd.notna(k)}
    
    return behavioral


def prepare_ground_truth(project_root: Path) -> Dict[str, Any]:
    """Prepare Anna's ground truth data."""
    ground_truth = {
        "partners": [],
        "zones": {},
        "dishes": {}
    }
    
    # Load partner coverage
    partners_path = project_root / "DATA" / "3_ANALYSIS" / "anna_partner_coverage.csv"
    partners = load_csv_safe(partners_path)
    
    if partners is not None:
        ground_truth["partners"] = partners.to_dict(orient="records")
        ground_truth["summary"] = {
            "totalBrands": len(partners),
            "totalSites": int(partners["total_sites"].sum()) if "total_sites" in partners.columns else 0
        }
    
    # Load zone dish counts
    zones_path = project_root / "DATA" / "3_ANALYSIS" / "anna_zone_dish_counts.csv"
    zones = load_csv_safe(zones_path)
    
    if zones is not None:
        # Find the total_dishes column
        total_dishes_col = None
        for col in zones.columns:
            if 'total' in col.lower() and 'dish' in col.lower():
                total_dishes_col = col
                break
        
        zones_with_dishes = 0
        if total_dishes_col:
            zones_with_dishes = len(zones[pd.to_numeric(zones[total_dishes_col], errors='coerce') > 0])
        
        ground_truth["zones"] = {
            "totalZones": len(zones),
            "zonesWithDishes": zones_with_dishes
        }
    
    return ground_truth


def main():
    """Main entry point."""
    print("=" * 60)
    print("PREPARING DASHBOARD DATA")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Initialize dashboard data
    dashboard_data = {
        "metadata": prepare_metadata()
    }
    
    print("Loading data sources...")
    print()
    
    # Prepare each data section
    print("1. Preparing dish data...")
    dashboard_data["dishes"] = prepare_dishes(PROJECT_ROOT)
    print()
    
    print("2. Preparing zone data...")
    dashboard_data["zones"] = prepare_zones(PROJECT_ROOT)
    print()
    
    print("3. Preparing cuisine gap data...")
    dashboard_data["cuisineGaps"] = prepare_cuisine_gaps(PROJECT_ROOT)
    print()
    
    print("4. Preparing latent demand data...")
    dashboard_data["latentDemand"] = prepare_latent_demand(PROJECT_ROOT)
    print()
    
    print("5. Preparing survey signals...")
    dashboard_data["surveySignals"] = prepare_survey_signals(PROJECT_ROOT)
    print()
    
    print("6. Preparing behavioral data...")
    dashboard_data["behavioral"] = prepare_behavioral_data(PROJECT_ROOT)
    print()
    
    print("7. Preparing ground truth data...")
    dashboard_data["groundTruth"] = prepare_ground_truth(PROJECT_ROOT)
    print()
    
    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(dashboard_data, f, indent=2, cls=NumpyEncoder)
    
    print("=" * 60)
    print("DASHBOARD DATA PREPARED")
    print("=" * 60)
    print(f"Output: {OUTPUT_FILE}")
    print(f"Dishes: {len(dashboard_data['dishes'])}")
    print(f"Zones: {len(dashboard_data['zones'])}")
    print(f"Cuisine gaps: {len(dashboard_data['cuisineGaps'])}")
    print()
    
    return dashboard_data


if __name__ == "__main__":
    main()

