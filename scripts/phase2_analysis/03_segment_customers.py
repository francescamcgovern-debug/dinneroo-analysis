"""
Script: 03_segment_customers.py
Phase: 2 - Analysis
Purpose: Segment customers by family type, region, and subscription status
Inputs:
    - DATA/1_SOURCE/snowflake/DINNEROO_ORDERS.csv
    - DATA/1_SOURCE/snowflake/FULL_ORDER_HISTORY.csv
    - DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv
Outputs: DATA/3_ANALYSIS/customer_segments.csv

This script analyzes customer behavior patterns across different segments
to understand family meal preferences.
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


def load_dinneroo_orders():
    """Load Dinneroo orders."""
    orders_path = SOURCE_DIR / "snowflake" / "DINNEROO_ORDERS.csv"
    if orders_path.exists():
        return pd.read_csv(orders_path)
    logger.warning("Dinneroo orders not found")
    return pd.DataFrame()


def load_full_order_history():
    """Load full Deliveroo order history (including non-Dinneroo)."""
    history_path = SOURCE_DIR / "snowflake" / "FULL_ORDER_HISTORY.csv"
    if history_path.exists():
        return pd.read_csv(history_path)
    logger.warning("Full order history not found")
    return pd.DataFrame()


def load_survey_data():
    """Load post-order survey for family indicators."""
    survey_path = SOURCE_DIR / "surveys" / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    if survey_path.exists():
        return pd.read_csv(survey_path)
    logger.warning("Survey data not found")
    return pd.DataFrame()


def identify_family_customers(orders_df: pd.DataFrame, survey_df: pd.DataFrame) -> set:
    """Identify customers who are likely families based on survey responses."""
    family_customers = set()
    
    if survey_df.empty:
        return family_customers
    
    # Find customer ID column
    customer_col = None
    for col in ['customer_id', 'user_id', 'customer']:
        if col in survey_df.columns:
            customer_col = col
            break
    
    if not customer_col:
        return family_customers
    
    # Look for family indicators in survey
    child_cols = [c for c in survey_df.columns if 'child' in c.lower()]
    family_cols = [c for c in survey_df.columns if 'family' in c.lower() or 'household' in c.lower()]
    
    for col in child_cols + family_cols:
        # Customers who have non-null responses about children
        has_response = survey_df[survey_df[col].notna()][customer_col]
        family_customers.update(has_response.unique())
    
    logger.info(f"Identified {len(family_customers)} family customers from survey")
    return family_customers


def segment_by_region(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Segment orders by region."""
    
    # Find zone column
    zone_col = None
    for col in ['zone_name', 'zone', 'area', 'region']:
        if col in orders_df.columns:
            zone_col = col
            break
    
    if not zone_col:
        logger.warning("No zone column found")
        return pd.DataFrame()
    
    # Map zones to regions
    def map_to_region(zone):
        zone_lower = str(zone).lower()
        if 'london' in zone_lower or 'westminster' in zone_lower or 'camden' in zone_lower:
            return 'London'
        elif 'manchester' in zone_lower or 'liverpool' in zone_lower or 'leeds' in zone_lower:
            return 'North'
        elif 'birmingham' in zone_lower or 'nottingham' in zone_lower or 'leicester' in zone_lower:
            return 'Midlands'
        elif 'bristol' in zone_lower or 'bath' in zone_lower or 'exeter' in zone_lower:
            return 'South West'
        elif 'brighton' in zone_lower or 'southampton' in zone_lower or 'reading' in zone_lower:
            return 'South East'
        elif 'edinburgh' in zone_lower or 'glasgow' in zone_lower:
            return 'Scotland'
        elif 'cardiff' in zone_lower or 'swansea' in zone_lower:
            return 'Wales'
        else:
            return 'Other'
    
    orders_df['region'] = orders_df[zone_col].apply(map_to_region)
    
    # Calculate metrics by region
    cuisine_col = None
    for col in ['cuisine', 'cuisine_type', 'category']:
        if col in orders_df.columns:
            cuisine_col = col
            break
    
    regional_metrics = []
    for region in orders_df['region'].unique():
        region_orders = orders_df[orders_df['region'] == region]
        
        metrics = {
            'region': region,
            'order_count': len(region_orders),
            'customer_count': region_orders['customer_id'].nunique() if 'customer_id' in region_orders.columns else 0,
            'avg_order_value': region_orders['order_value'].mean() if 'order_value' in region_orders.columns else None
        }
        
        if cuisine_col:
            top_cuisines = region_orders[cuisine_col].value_counts().head(5).to_dict()
            metrics['top_cuisines'] = json.dumps(top_cuisines)
        
        regional_metrics.append(metrics)
    
    return pd.DataFrame(regional_metrics)


def segment_by_subscription(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Segment by Plus subscriber vs PAYG."""
    
    # Find subscription column
    sub_col = None
    for col in ['is_plus', 'subscription', 'plus_subscriber', 'customer_type']:
        if col in orders_df.columns:
            sub_col = col
            break
    
    if not sub_col:
        logger.warning("No subscription column found")
        return pd.DataFrame()
    
    # Calculate metrics by subscription status
    sub_metrics = []
    for status in orders_df[sub_col].unique():
        sub_orders = orders_df[orders_df[sub_col] == status]
        
        metrics = {
            'subscription_status': status,
            'order_count': len(sub_orders),
            'customer_count': sub_orders['customer_id'].nunique() if 'customer_id' in sub_orders.columns else 0,
            'avg_order_value': sub_orders['order_value'].mean() if 'order_value' in sub_orders.columns else None,
            'repeat_rate': None  # Would need customer-level analysis
        }
        
        sub_metrics.append(metrics)
    
    return pd.DataFrame(sub_metrics)


def analyze_cannibalization(dinneroo_df: pd.DataFrame, full_history_df: pd.DataFrame) -> dict:
    """
    Analyze cannibalization risk by comparing Dinneroo vs non-Dinneroo orders.
    Key insight: Dinneroo should create NEW occasions, not replace weekend orders.
    """
    
    results = {
        'dinneroo_day_distribution': {},
        'non_dinneroo_day_distribution': {},
        'cannibalization_risk': 'Unknown'
    }
    
    if dinneroo_df.empty or full_history_df.empty:
        return results
    
    # Find date column
    date_col = None
    for col in ['order_date', 'created_at', 'date', 'order_time']:
        if col in dinneroo_df.columns:
            date_col = col
            break
    
    if not date_col:
        return results
    
    # Parse dates and get day of week
    try:
        dinneroo_df['day_of_week'] = pd.to_datetime(dinneroo_df[date_col]).dt.day_name()
        full_history_df['day_of_week'] = pd.to_datetime(full_history_df[date_col]).dt.day_name()
    except Exception as e:
        logger.error(f"Error parsing dates: {e}")
        return results
    
    # Calculate day distribution
    dinneroo_days = dinneroo_df['day_of_week'].value_counts(normalize=True).to_dict()
    results['dinneroo_day_distribution'] = {k: round(v, 3) for k, v in dinneroo_days.items()}
    
    # Non-Dinneroo orders (from full history, excluding Dinneroo)
    if 'is_dinneroo' in full_history_df.columns:
        non_dinneroo = full_history_df[full_history_df['is_dinneroo'] == False]
    else:
        non_dinneroo = full_history_df  # Assume all are non-Dinneroo if no flag
    
    non_dinneroo_days = non_dinneroo['day_of_week'].value_counts(normalize=True).to_dict()
    results['non_dinneroo_day_distribution'] = {k: round(v, 3) for k, v in non_dinneroo_days.items()}
    
    # Assess cannibalization risk
    # If Dinneroo is mostly midweek and non-Dinneroo is mostly weekend, low risk
    midweek_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
    weekend_days = ['Friday', 'Saturday', 'Sunday']
    
    dinneroo_midweek = sum(dinneroo_days.get(d, 0) for d in midweek_days)
    non_dinneroo_weekend = sum(non_dinneroo_days.get(d, 0) for d in weekend_days)
    
    if dinneroo_midweek > 0.7 and non_dinneroo_weekend > 0.5:
        results['cannibalization_risk'] = 'Low - Dinneroo creates new midweek occasion'
    elif dinneroo_midweek > 0.5:
        results['cannibalization_risk'] = 'Medium - Some overlap but mostly differentiated'
    else:
        results['cannibalization_risk'] = 'High - Significant overlap with existing orders'
    
    results['dinneroo_midweek_pct'] = round(dinneroo_midweek, 3)
    results['non_dinneroo_weekend_pct'] = round(non_dinneroo_weekend, 3)
    
    return results


def main():
    """Main function to segment customers."""
    logger.info("=" * 60)
    logger.info("PHASE 2: Segmenting Customers")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    dinneroo_orders = load_dinneroo_orders()
    full_history = load_full_order_history()
    survey_data = load_survey_data()
    
    logger.info(f"Loaded Dinneroo orders: {len(dinneroo_orders)}")
    logger.info(f"Loaded full history: {len(full_history)}")
    logger.info(f"Loaded survey data: {len(survey_data)}")
    
    # Identify family customers
    family_customers = identify_family_customers(dinneroo_orders, survey_data)
    
    # Regional segmentation
    logger.info("\nAnalyzing regional segments...")
    regional_segments = segment_by_region(dinneroo_orders)
    
    # Subscription segmentation
    logger.info("\nAnalyzing subscription segments...")
    subscription_segments = segment_by_subscription(dinneroo_orders)
    
    # Cannibalization analysis
    logger.info("\nAnalyzing cannibalization risk...")
    cannibalization = analyze_cannibalization(dinneroo_orders, full_history)
    
    # Compile results
    results = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_dinneroo_orders': len(dinneroo_orders),
            'total_full_history_orders': len(full_history),
            'identified_family_customers': len(family_customers),
            'regions_analyzed': len(regional_segments) if not regional_segments.empty else 0
        },
        'cannibalization_analysis': cannibalization
    }
    
    # Save regional segments
    if not regional_segments.empty:
        regional_segments.to_csv(ANALYSIS_DIR / "regional_segments.csv", index=False)
        logger.info(f"Saved regional segments: {len(regional_segments)} regions")
    
    # Save subscription segments
    if not subscription_segments.empty:
        subscription_segments.to_csv(ANALYSIS_DIR / "subscription_segments.csv", index=False)
        logger.info(f"Saved subscription segments: {len(subscription_segments)} statuses")
    
    # Save full results
    with open(ANALYSIS_DIR / "customer_segments.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("\n" + "=" * 60)
    logger.info("CUSTOMER SEGMENTATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Dinneroo orders: {results['summary']['total_dinneroo_orders']}")
    logger.info(f"Identified family customers: {results['summary']['identified_family_customers']}")
    logger.info(f"\nCannibalization Risk: {cannibalization.get('cannibalization_risk', 'Unknown')}")
    logger.info(f"Dinneroo midweek %: {cannibalization.get('dinneroo_midweek_pct', 'N/A')}")
    
    if not regional_segments.empty:
        logger.info(f"\nRegional distribution:")
        logger.info(regional_segments[['region', 'order_count']].to_string())
    
    logger.info(f"\nResults saved to: {ANALYSIS_DIR}")
    
    return results


if __name__ == "__main__":
    main()



