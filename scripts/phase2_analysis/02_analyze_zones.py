"""
Script: 02_analyze_zones.py
Phase: 2 - Analysis
Purpose: Analyze zones for MVP status and identify gaps
Inputs:
    - DATA/1_SOURCE/snowflake/DINNEROO_ORDERS.csv
    - DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv
    - DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv
    - config/mvp_thresholds.json
Outputs: DATA/3_ANALYSIS/zone_analysis.csv

This script evaluates each zone against MVP criteria and identifies
supply and quality gaps.
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
SOURCE_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE"
ANALYSIS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
CONFIG_DIR = PROJECT_ROOT / "config"


def load_mvp_config():
    """Load MVP thresholds configuration."""
    config_path = CONFIG_DIR / "mvp_thresholds.json"
    with open(config_path) as f:
        return json.load(f)


def load_orders():
    """Load orders data."""
    orders_path = SOURCE_DIR / "snowflake" / "DINNEROO_ORDERS.csv"
    if orders_path.exists():
        return pd.read_csv(orders_path)
    logger.warning("Orders data not found")
    return pd.DataFrame()


def load_ratings():
    """Load ratings data."""
    ratings_path = SOURCE_DIR / "snowflake" / "DINNEROO_RATINGS.csv"
    if ratings_path.exists():
        return pd.read_csv(ratings_path)
    logger.warning("Ratings data not found")
    return pd.DataFrame()


def load_menu_catalog():
    """Load menu catalog."""
    menu_path = SOURCE_DIR / "snowflake" / "DINNEROO_MENU_CATALOG.csv"
    if menu_path.exists():
        return pd.read_csv(menu_path)
    logger.warning("Menu catalog not found")
    return pd.DataFrame()


def calculate_zone_metrics(orders_df: pd.DataFrame, ratings_df: pd.DataFrame, menu_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate key metrics for each zone."""
    
    if orders_df.empty:
        logger.warning("No orders data available")
        return pd.DataFrame()
    
    # Find zone column
    zone_col = None
    for col in ['zone_name', 'zone', 'area', 'region']:
        if col in orders_df.columns:
            zone_col = col
            break
    
    if not zone_col:
        logger.warning("No zone column found in orders")
        return pd.DataFrame()
    
    # Find partner column
    partner_col = None
    for col in ['partner_name', 'restaurant_name', 'partner']:
        if col in orders_df.columns:
            partner_col = col
            break
    
    # Find cuisine column
    cuisine_col = None
    for col in ['cuisine', 'cuisine_type', 'category']:
        if col in orders_df.columns:
            cuisine_col = col
            break
    
    # Find dish column
    dish_col = None
    for col in ['dish_name', 'item_name', 'menu_item']:
        if col in orders_df.columns:
            dish_col = col
            break
    
    # Calculate metrics per zone
    zone_metrics = []
    
    for zone in orders_df[zone_col].unique():
        zone_orders = orders_df[orders_df[zone_col] == zone]
        
        metrics = {
            'zone_name': zone,
            'order_count': len(zone_orders),
            'partner_count': zone_orders[partner_col].nunique() if partner_col else 0,
            'dish_count': zone_orders[dish_col].nunique() if dish_col else 0,
            'cuisine_count': zone_orders[cuisine_col].nunique() if cuisine_col else 0
        }
        
        # Add ratings if available
        if not ratings_df.empty and zone_col in ratings_df.columns:
            zone_ratings = ratings_df[ratings_df[zone_col] == zone]
            rating_col = None
            for col in ['rating', 'star_rating', 'score']:
                if col in zone_ratings.columns:
                    rating_col = col
                    break
            if rating_col:
                metrics['avg_rating'] = round(zone_ratings[rating_col].mean(), 2)
                metrics['rating_count'] = len(zone_ratings)
            else:
                metrics['avg_rating'] = None
                metrics['rating_count'] = 0
        else:
            metrics['avg_rating'] = None
            metrics['rating_count'] = 0
        
        # Get cuisine breakdown
        if cuisine_col:
            cuisine_counts = zone_orders[cuisine_col].value_counts().to_dict()
            metrics['cuisine_breakdown'] = json.dumps(cuisine_counts)
        
        zone_metrics.append(metrics)
    
    return pd.DataFrame(zone_metrics)


def evaluate_mvp_status(zone_metrics: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Evaluate each zone against MVP criteria."""
    
    thresholds = config['mvp_criteria']
    
    # Check each criterion
    zone_metrics['meets_cuisines'] = zone_metrics['cuisine_count'] >= thresholds['cuisines_min']['value']
    zone_metrics['meets_partners'] = zone_metrics['partner_count'] >= thresholds['partners_min']['value']
    zone_metrics['meets_dishes'] = zone_metrics['dish_count'] >= thresholds['dishes_min']['value']
    zone_metrics['meets_rating'] = zone_metrics['avg_rating'] >= thresholds['rating_min']['value']
    
    # Count how many criteria met
    criteria_cols = ['meets_cuisines', 'meets_partners', 'meets_dishes', 'meets_rating']
    zone_metrics['criteria_met'] = zone_metrics[criteria_cols].sum(axis=1)
    
    # Determine MVP status
    def get_mvp_status(row):
        if row['criteria_met'] == 4:
            return 'MVP Ready'
        elif row['criteria_met'] >= 3:
            return 'Near MVP'
        elif row['criteria_met'] >= 1:
            return 'Developing'
        else:
            return 'Early Stage'
    
    zone_metrics['mvp_status'] = zone_metrics.apply(get_mvp_status, axis=1)
    
    return zone_metrics


def calculate_zone_quality_score(zone_metrics: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Calculate composite quality score for each zone."""
    
    score_config = config['zone_quality_score']['components']
    
    def calc_score(row):
        score = 0
        
        # Cuisine coverage (25%)
        cuisine_score = min(row['cuisine_count'] / 8, 1.0) * score_config['cuisine_coverage']['weight']
        
        # Partner density (20%)
        partner_score = min(row['partner_count'] / 10, 1.0) * score_config['partner_density']['weight']
        
        # Dish variety (20%)
        dish_score = min(row['dish_count'] / 50, 1.0) * score_config['dish_variety']['weight']
        
        # Quality score (20%)
        quality_score = (row['avg_rating'] / 5.0 if pd.notna(row['avg_rating']) else 0.5) * score_config['quality_score']['weight']
        
        # Volume (15%)
        volume_score = min(row['order_count'] / 1000, 1.0) * score_config['volume']['weight']
        
        return round(cuisine_score + partner_score + dish_score + quality_score + volume_score, 3)
    
    zone_metrics['quality_score'] = zone_metrics.apply(calc_score, axis=1)
    
    return zone_metrics


def identify_gaps(zone_metrics: pd.DataFrame, orders_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Identify supply and quality gaps for each zone."""
    
    gap_config = config['gap_classification']
    
    # Find zone and cuisine columns
    zone_col = None
    for col in ['zone_name', 'zone', 'area', 'region']:
        if col in orders_df.columns:
            zone_col = col
            break
    
    cuisine_col = None
    for col in ['cuisine', 'cuisine_type', 'category']:
        if col in orders_df.columns:
            cuisine_col = col
            break
    
    partner_col = None
    for col in ['partner_name', 'restaurant_name', 'partner']:
        if col in orders_df.columns:
            partner_col = col
            break
    
    # Target cuisines (based on family meal factors analysis)
    target_cuisines = ['Italian', 'Chinese', 'Indian', 'Mexican', 'Japanese', 'Thai', 'Mediterranean', 'British']
    
    gaps = []
    
    for _, zone in zone_metrics.iterrows():
        zone_name = zone['zone_name']
        zone_orders = orders_df[orders_df[zone_col] == zone_name] if zone_col else pd.DataFrame()
        
        zone_gaps = {
            'zone_name': zone_name,
            'supply_gaps': [],
            'quality_gaps': []
        }
        
        if cuisine_col and partner_col and not zone_orders.empty:
            for cuisine in target_cuisines:
                cuisine_orders = zone_orders[zone_orders[cuisine_col].str.lower() == cuisine.lower()]
                
                if len(cuisine_orders) == 0:
                    zone_gaps['supply_gaps'].append(cuisine)
                else:
                    partner_count = cuisine_orders[partner_col].nunique()
                    if partner_count < 2:
                        zone_gaps['supply_gaps'].append(f"{cuisine} (only {partner_count} partner)")
        
        zone_gaps['supply_gaps_str'] = ', '.join(zone_gaps['supply_gaps']) if zone_gaps['supply_gaps'] else 'None'
        zone_gaps['quality_gaps_str'] = ', '.join(zone_gaps['quality_gaps']) if zone_gaps['quality_gaps'] else 'None'
        zone_gaps['gap_count'] = len(zone_gaps['supply_gaps']) + len(zone_gaps['quality_gaps'])
        
        gaps.append(zone_gaps)
    
    gaps_df = pd.DataFrame(gaps)
    
    # Merge with zone metrics
    zone_metrics = zone_metrics.merge(
        gaps_df[['zone_name', 'supply_gaps_str', 'quality_gaps_str', 'gap_count']],
        on='zone_name',
        how='left'
    )
    
    return zone_metrics


def main():
    """Main function to analyze zones."""
    logger.info("=" * 60)
    logger.info("PHASE 2: Analyzing Zones")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    config = load_mvp_config()
    orders_df = load_orders()
    ratings_df = load_ratings()
    menu_df = load_menu_catalog()
    
    logger.info(f"Loaded orders: {len(orders_df)} records")
    logger.info(f"Loaded ratings: {len(ratings_df)} records")
    logger.info(f"Loaded menu: {len(menu_df)} items")
    
    # Calculate metrics
    logger.info("\nCalculating zone metrics...")
    zone_metrics = calculate_zone_metrics(orders_df, ratings_df, menu_df)
    
    if zone_metrics.empty:
        logger.error("No zone metrics calculated")
        return pd.DataFrame()
    
    logger.info(f"Analyzed {len(zone_metrics)} zones")
    
    # Evaluate MVP status
    logger.info("\nEvaluating MVP status...")
    zone_metrics = evaluate_mvp_status(zone_metrics, config)
    
    # Calculate quality scores
    logger.info("\nCalculating quality scores...")
    zone_metrics = calculate_zone_quality_score(zone_metrics, config)
    
    # Identify gaps
    logger.info("\nIdentifying gaps...")
    zone_metrics = identify_gaps(zone_metrics, orders_df, config)
    
    # Sort by quality score
    zone_metrics = zone_metrics.sort_values('quality_score', ascending=False)
    zone_metrics['rank'] = range(1, len(zone_metrics) + 1)
    
    # Reorder columns
    priority_cols = ['rank', 'zone_name', 'mvp_status', 'quality_score', 'criteria_met']
    metric_cols = ['order_count', 'partner_count', 'cuisine_count', 'dish_count', 'avg_rating']
    criteria_cols = ['meets_cuisines', 'meets_partners', 'meets_dishes', 'meets_rating']
    gap_cols = ['supply_gaps_str', 'quality_gaps_str', 'gap_count']
    other_cols = [c for c in zone_metrics.columns if c not in priority_cols + metric_cols + criteria_cols + gap_cols]
    
    zone_metrics = zone_metrics[priority_cols + metric_cols + criteria_cols + gap_cols + other_cols]
    
    # Save
    output_path = ANALYSIS_DIR / "zone_analysis.csv"
    zone_metrics.to_csv(output_path, index=False)
    
    logger.info("\n" + "=" * 60)
    logger.info("ZONE ANALYSIS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total zones analyzed: {len(zone_metrics)}")
    logger.info(f"\nMVP Status distribution:")
    logger.info(zone_metrics['mvp_status'].value_counts().to_string())
    logger.info(f"\nTop 10 zones by quality score:")
    logger.info(zone_metrics[['rank', 'zone_name', 'quality_score', 'mvp_status']].head(10).to_string())
    logger.info(f"\nSaved to: {output_path}")
    
    return zone_metrics


if __name__ == "__main__":
    main()

