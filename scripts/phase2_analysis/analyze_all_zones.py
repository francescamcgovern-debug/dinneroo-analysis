"""
Script: analyze_all_zones.py
Phase: 2 - Analysis
Purpose: Generate comprehensive zone gap analysis using ALL zones from Anna's ground truth

This script follows the ZONE_AGENT protocol:
- Uses Anna's data (anna_zone_dish_counts.csv) as the ground truth for supply metrics
- Uses Snowflake data for performance metrics (orders, ratings)
- Generates zone_gap_report.csv covering ALL 1,306 zones

Outputs:
    - DATA/3_ANALYSIS/zone_gap_report.csv (replaces limited 100-zone version)
"""

import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
SNOWFLAKE_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE" / "snowflake"
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"

# Essential cuisines (from ZONE_AGENT.md)
ESSENTIAL_CUISINES = ['Japanese/Asian', 'Vietnamese', 'Indian', 'Italian', 'Thai/Southeast Asian']
RECOMMENDED_CUISINES = ['British', 'Mexican', 'Healthy/Fresh', 'Middle Eastern', 'Chinese']

# Essential dish types (from ZONE_AGENT.md)
ESSENTIAL_DISHES = ['katsu', 'pho', 'curry', 'noodle', 'rice', 'pasta', 'pizza', 'fajita', 'burrito', 'taco', 'sushi', 'biryani', 'grilled chicken']


def load_anna_zone_data():
    """Load Anna's ground truth zone data (1,306 zones)."""
    path = ANALYSIS_DIR / "anna_zone_dish_counts.csv"
    df = pd.read_csv(path)
    logger.info(f"Loaded Anna's zone data: {len(df)} zones")
    return df


def load_snowflake_orders():
    """Load Snowflake order data for performance metrics."""
    path = SNOWFLAKE_DIR / "ALL_DINNEROO_ORDERS.csv"
    if not path.exists():
        logger.warning("Snowflake orders not found - using supply-only analysis")
        return None
    df = pd.read_csv(path)
    logger.info(f"Loaded Snowflake orders: {len(df)} rows")
    return df


def load_snowflake_ratings():
    """Load Snowflake ratings for quality metrics."""
    path = SNOWFLAKE_DIR / "DINNEROO_RATINGS.csv"
    if not path.exists():
        logger.warning("Snowflake ratings not found")
        return None
    df = pd.read_csv(path)
    logger.info(f"Loaded Snowflake ratings: {len(df)} rows")
    return df


def load_mvp_config():
    """Load MVP thresholds configuration."""
    config_path = CONFIG_DIR / "mvp_thresholds.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    # Default thresholds from ZONE_AGENT.md
    return {
        "mvp_criteria": {
            "cuisines_min": {"value": 5},
            "partners_min": {"value": 5},
            "dishes_min": {"value": 21},
            "rating_min": {"value": 4.0}
        }
    }


def map_anna_cuisines_to_essential(row):
    """Map Anna's cuisine columns to our essential cuisine framework."""
    cuisines_available = []
    
    # Map Anna's columns to cuisine categories
    if row.get('asian', 0) > 0:
        cuisines_available.append('Japanese/Asian')
    if row.get('italian', 0) > 0:
        cuisines_available.append('Italian')
    if row.get('indian', 0) > 0:
        cuisines_available.append('Indian')
    if row.get('healthy', 0) > 0:
        cuisines_available.append('Healthy/Fresh')
    if row.get('mexican', 0) > 0:
        cuisines_available.append('Mexican')
    if row.get('middle_eastern', 0) > 0:
        cuisines_available.append('Middle Eastern')
    if row.get('british', 0) > 0:
        cuisines_available.append('British')
    
    return cuisines_available


def calculate_essential_coverage(cuisines_available):
    """Calculate what percentage of essential cuisines are covered."""
    essential_present = [c for c in cuisines_available if c in ESSENTIAL_CUISINES]
    return len(essential_present) / len(ESSENTIAL_CUISINES) * 100


def get_missing_cuisines(cuisines_available):
    """Get list of missing essential and recommended cuisines."""
    missing_essential = [c for c in ESSENTIAL_CUISINES if c not in cuisines_available]
    missing_recommended = [c for c in RECOMMENDED_CUISINES if c not in cuisines_available]
    return missing_essential, missing_recommended


def calculate_mvp_status(row, config):
    """Calculate MVP status based on criteria."""
    thresholds = config['mvp_criteria']
    
    criteria_met = 0
    
    # Cuisine criterion
    if row['cuisines_count'] >= thresholds['cuisines_min']['value']:
        criteria_met += 1
    
    # Partner criterion
    if row['partners'] >= thresholds['partners_min']['value']:
        criteria_met += 1
    
    # Dish criterion
    if row['total_dishes'] >= thresholds['dishes_min']['value']:
        criteria_met += 1
    
    # Rating criterion (only if we have rating data)
    if pd.notna(row.get('avg_rating')) and row['avg_rating'] >= thresholds['rating_min']['value']:
        criteria_met += 1
    elif pd.isna(row.get('avg_rating')):
        # If no rating data, don't count against MVP
        pass
    
    is_mvp = criteria_met >= 3  # MVP if meets at least 3 of 4 criteria
    
    return is_mvp, criteria_met


def determine_recruitment_priority(row):
    """Determine recruitment priority based on gaps and potential."""
    # High priority: Has orders but missing essential cuisines
    # Medium priority: Has some supply but low coverage
    # Low priority: Early stage or already MVP
    
    if row['is_mvp']:
        return 'Low'
    
    # Parse essential_cuisine_coverage (it's a string like "60%")
    coverage_str = row.get('essential_cuisine_coverage', '0%')
    coverage_pct = float(coverage_str.replace('%', '')) if coverage_str else 0
    
    # High priority if has orders but missing essentials
    if row.get('orders', 0) > 0 and coverage_pct < 60:
        return 'High'
    
    # High priority if has partners but low cuisine diversity
    if row['partners'] >= 3 and row['cuisines_count'] < 4:
        return 'High'
    
    # Medium priority if developing
    if row['partners'] >= 1 and row['total_dishes'] >= 5:
        return 'Medium'
    
    # Low priority if early stage
    return 'Low'


def analyze_all_zones():
    """Main analysis function covering all zones."""
    
    # Load data sources
    anna_zones = load_anna_zone_data()
    orders_df = load_snowflake_orders()
    ratings_df = load_snowflake_ratings()
    config = load_mvp_config()
    
    # Calculate zone-level performance from Snowflake (if available)
    zone_performance = {}
    if orders_df is not None:
        # Aggregate orders by zone
        zone_orders = orders_df.groupby('ZONE_NAME').agg({
            'ORDER_ID': 'count'
        }).reset_index()
        zone_orders.columns = ['zone_name', 'orders']
        zone_performance = dict(zip(zone_orders['zone_name'], zone_orders['orders']))
        logger.info(f"Calculated performance for {len(zone_performance)} zones with orders")
    
    zone_ratings = {}
    if ratings_df is not None:
        # Aggregate ratings by zone (column is RATING_STARS)
        ratings_by_zone = ratings_df.groupby('ZONE_NAME').agg({
            'RATING_STARS': 'mean'
        }).reset_index()
        ratings_by_zone.columns = ['zone_name', 'avg_rating']
        zone_ratings = dict(zip(ratings_by_zone['zone_name'], ratings_by_zone['avg_rating']))
        logger.info(f"Calculated ratings for {len(zone_ratings)} zones")
    
    # Process each zone from Anna's ground truth
    zone_reports = []
    
    for _, row in anna_zones.iterrows():
        zone_name = row['zone_name']
        zone_code = row['zone_code']
        
        # Get cuisines available from Anna's data
        cuisines_available = map_anna_cuisines_to_essential(row)
        essential_coverage = calculate_essential_coverage(cuisines_available)
        missing_essential, missing_recommended = get_missing_cuisines(cuisines_available)
        
        # Build zone report
        zone_report = {
            'zone': zone_name,
            'zone_code': zone_code,
            'region': row.get('region', 'Unknown'),
            'city': row.get('city', ''),
            'large_city': row.get('large_city', ''),
            
            # Supply metrics (from Anna's ground truth)
            'partners': int(row.get('num_brands', 0)),
            'cuisines_count': int(row.get('num_cuisines', 0)),
            'total_dishes': int(row.get('total_dishes', 0)),
            
            # Cuisine breakdown
            'asian_dishes': int(row.get('asian', 0)),
            'italian_dishes': int(row.get('italian', 0)),
            'indian_dishes': int(row.get('indian', 0)),
            'healthy_dishes': int(row.get('healthy', 0)),
            'mexican_dishes': int(row.get('mexican', 0)),
            'middle_eastern_dishes': int(row.get('middle_eastern', 0)),
            'british_dishes': int(row.get('british', 0)),
            
            # Performance metrics (from Snowflake)
            'orders': zone_performance.get(zone_name, 0),
            'avg_rating': zone_ratings.get(zone_name, None),
            
            # Gap analysis
            'cuisines_available': str(cuisines_available),
            'essential_cuisine_coverage': f"{essential_coverage:.0f}%",
            'missing_essential_cuisines': str(missing_essential),
            'missing_recommended_cuisines': str(missing_recommended),
            
            # Dish coverage (simplified - based on total dishes vs threshold)
            'dish_coverage': f"{min(100, row.get('total_dishes', 0) / 21 * 100):.0f}%"
        }
        
        # Calculate MVP status
        is_mvp, criteria_met = calculate_mvp_status(zone_report, config)
        zone_report['is_mvp'] = is_mvp
        zone_report['mvp_criteria_met'] = criteria_met
        
        # Determine recruitment priority
        zone_report['recruitment_priority'] = determine_recruitment_priority(zone_report)
        
        zone_reports.append(zone_report)
    
    # Create DataFrame
    df = pd.DataFrame(zone_reports)
    
    # Sort by orders (zones with activity first), then by partners
    df = df.sort_values(['orders', 'partners'], ascending=[False, False])
    
    return df


def main():
    """Main function to generate comprehensive zone gap report."""
    logger.info("=" * 60)
    logger.info("COMPREHENSIVE ZONE ANALYSIS")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Using Anna's ground truth for ALL 1,306 zones")
    logger.info("")
    
    # Run analysis
    df = analyze_all_zones()
    
    # Save output
    output_path = OUTPUT_DIR / "zone_gap_report.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved: {output_path}")
    
    # Summary statistics
    logger.info("")
    logger.info("=" * 60)
    logger.info("ZONE ANALYSIS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total zones analyzed: {len(df)}")
    logger.info(f"Zones with orders: {len(df[df['orders'] > 0])}")
    logger.info(f"Zones with ratings: {len(df[df['avg_rating'].notna()])}")
    logger.info("")
    
    # MVP status distribution
    mvp_count = len(df[df['is_mvp'] == True])
    near_mvp = len(df[(df['is_mvp'] == False) & (df['mvp_criteria_met'] >= 2)])
    developing = len(df[(df['is_mvp'] == False) & (df['mvp_criteria_met'] == 1)])
    early_stage = len(df[(df['is_mvp'] == False) & (df['mvp_criteria_met'] == 0)])
    
    logger.info("MVP Status Distribution:")
    logger.info(f"  MVP Ready: {mvp_count} ({mvp_count/len(df)*100:.1f}%)")
    logger.info(f"  Near MVP (2 criteria): {near_mvp} ({near_mvp/len(df)*100:.1f}%)")
    logger.info(f"  Developing (1 criterion): {developing} ({developing/len(df)*100:.1f}%)")
    logger.info(f"  Early Stage (0 criteria): {early_stage} ({early_stage/len(df)*100:.1f}%)")
    logger.info("")
    
    # Recruitment priority distribution
    logger.info("Recruitment Priority Distribution:")
    priority_counts = df['recruitment_priority'].value_counts()
    for priority, count in priority_counts.items():
        logger.info(f"  {priority}: {count} ({count/len(df)*100:.1f}%)")
    logger.info("")
    
    # Top zones with gaps (high priority)
    logger.info("Top 10 High Priority Zones (with orders, missing essentials):")
    high_priority = df[(df['recruitment_priority'] == 'High') & (df['orders'] > 0)].head(10)
    for _, zone in high_priority.iterrows():
        logger.info(f"  {zone['zone']}: {zone['orders']} orders, {zone['cuisines_count']} cuisines, missing: {zone['missing_essential_cuisines'][:50]}...")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("ANALYSIS COMPLETE")
    logger.info("=" * 60)
    
    return df


if __name__ == "__main__":
    main()

