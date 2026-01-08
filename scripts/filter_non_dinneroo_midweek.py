#!/usr/bin/env python3
"""
Filter Non-Dinneroo Orders to Midweek Dinner Time

This script filters FULL_ORDER_HISTORY.csv to create non_dinneroo_cuisine_demand_midweek.csv
with orders filtered to:
- Non-Dinneroo orders only (IS_DINNEROO = False)
- Monday-Thursday only (DAY_OF_WEEK = 1,2,3,4)
- Dinner time only (16:30 - 21:00)

CRITICAL: This filtered data should be used for ALL non-Dinneroo benchmarks.
The raw unfiltered data creates apples-to-oranges comparisons because Dinneroo is 98% midweek.

Usage:
    python3 scripts/filter_non_dinneroo_midweek.py

Output:
    DATA/3_ANALYSIS/non_dinneroo_cuisine_demand_midweek.csv
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
INPUT_FILE = PROJECT_ROOT / "DATA" / "1_SOURCE" / "snowflake" / "FULL_ORDER_HISTORY.csv"
OUTPUT_FILE = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "non_dinneroo_cuisine_demand_midweek.csv"
RAW_OUTPUT_FILE = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "non_dinneroo_cuisine_demand.csv"

# Filter constants
MIDWEEK_DAYS = [1, 2, 3, 4]  # Mon=1, Tue=2, Wed=3, Thu=4
DINNER_START_HOUR = 16
DINNER_START_MINUTE = 30
DINNER_END_HOUR = 21
DINNER_END_MINUTE = 0


def load_order_history():
    """Load the full order history file."""
    logger.info(f"Loading order history from {INPUT_FILE}")
    
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Order history file not found: {INPUT_FILE}")
    
    df = pd.read_csv(INPUT_FILE, low_memory=False)
    logger.info(f"Loaded {len(df):,} total orders")
    return df


def filter_non_dinneroo(df):
    """Filter to non-Dinneroo orders only."""
    # Handle various boolean representations
    if df['IS_DINNEROO'].dtype == bool:
        non_dinneroo = df[~df['IS_DINNEROO']]
    else:
        non_dinneroo = df[df['IS_DINNEROO'].astype(str).str.lower().isin(['false', '0', 'no'])]
    
    logger.info(f"After non-Dinneroo filter: {len(non_dinneroo):,} orders ({len(non_dinneroo)/len(df)*100:.1f}%)")
    return non_dinneroo


def filter_midweek(df):
    """Filter to Monday-Thursday only."""
    midweek = df[df['DAY_OF_WEEK'].isin(MIDWEEK_DAYS)]
    logger.info(f"After midweek filter (Mon-Thu): {len(midweek):,} orders ({len(midweek)/len(df)*100:.1f}%)")
    return midweek


def filter_dinner_time(df):
    """Filter to dinner time only (16:30-21:00)."""
    # Parse timestamp and extract hour/minute
    df = df.copy()
    df['ORDER_TIMESTAMP'] = pd.to_datetime(df['ORDER_TIMESTAMP'])
    df['hour'] = df['ORDER_TIMESTAMP'].dt.hour
    df['minute'] = df['ORDER_TIMESTAMP'].dt.minute
    
    # Filter to dinner time: 16:30 - 21:00
    dinner_time = df[
        ((df['hour'] == DINNER_START_HOUR) & (df['minute'] >= DINNER_START_MINUTE)) |
        ((df['hour'] > DINNER_START_HOUR) & (df['hour'] < DINNER_END_HOUR)) |
        ((df['hour'] == DINNER_END_HOUR) & (df['minute'] == 0))
    ]
    
    logger.info(f"After dinner time filter (16:30-21:00): {len(dinner_time):,} orders ({len(dinner_time)/len(df)*100:.1f}%)")
    return dinner_time


def aggregate_by_cuisine(df, label=""):
    """Aggregate orders by cuisine."""
    logger.info(f"Aggregating by cuisine{' (' + label + ')' if label else ''}")
    
    cuisine_agg = df.groupby('CUISINE').agg(
        non_dinneroo_orders=('ORDER_ID', 'count'),
        unique_customers=('CUSTOMER_ID', 'nunique'),
        avg_order_value=('ORDER_VALUE', 'mean')
    ).reset_index()
    
    cuisine_agg.columns = ['cuisine', 'non_dinneroo_orders', 'unique_customers', 'avg_order_value']
    cuisine_agg = cuisine_agg.sort_values('non_dinneroo_orders', ascending=False)
    cuisine_agg['avg_order_value'] = cuisine_agg['avg_order_value'].round(2)
    
    # Add Dinneroo availability flag (simplified - will need manual verification)
    dinneroo_available_cuisines = [
        'Burgers', 'Italian', 'Japanese', 'Chicken', 'Indian', 'Chinese',
        'Healthy', 'Asian', 'Vietnamese', 'Thai', 'Halal', 'Sandwiches',
        'Middle Eastern', 'Breakfast', 'Lebanese', 'Unknown', 'Mexican',
        'Vegan Friendly', 'Burritos', 'Tacos', 'Mediterranean', 'Vegetarian',
        'Meal Deals', 'Gluten Free', 'Kosher', 'Wraps', 'Asian Fusion',
        'Movie Night Restaurants', 'Featured Restaurants', 'Shawarma',
        'Christmas Specials', 'Roasteries', 'Organic', 'Veganuary',
        'Exclusive offers, from our exclusive restaurants', 'Plus offers Oct 2024',
        'Only on Deliveroo', 'Family favourites'
    ]
    
    cuisine_agg['dinneroo_available'] = cuisine_agg['cuisine'].apply(
        lambda x: 'Yes' if x in dinneroo_available_cuisines else 'No'
    )
    
    # Add gap signal
    def get_gap_signal(row):
        if row['dinneroo_available'] == 'Yes':
            return 'Available'
        elif row['non_dinneroo_orders'] >= 5000:
            return 'High'
        elif row['non_dinneroo_orders'] >= 2000:
            return 'Medium'
        else:
            return 'Low'
    
    cuisine_agg['gap_signal'] = cuisine_agg.apply(get_gap_signal, axis=1)
    
    return cuisine_agg


def generate_comparison_stats(raw_df, filtered_df):
    """Generate statistics comparing raw vs filtered data."""
    raw_agg = aggregate_by_cuisine(raw_df, "raw")
    filtered_agg = aggregate_by_cuisine(filtered_df, "filtered")
    
    # Merge to compare
    comparison = raw_agg.merge(
        filtered_agg[['cuisine', 'non_dinneroo_orders']],
        on='cuisine',
        suffixes=('', '_filtered'),
        how='left'
    )
    comparison['non_dinneroo_orders_filtered'] = comparison['non_dinneroo_orders_filtered'].fillna(0).astype(int)
    comparison['filter_ratio'] = (comparison['non_dinneroo_orders_filtered'] / comparison['non_dinneroo_orders']).round(3)
    
    # Log top cuisines with highest change
    logger.info("\nTop cuisines by filter impact:")
    logger.info("-" * 60)
    for _, row in comparison.head(15).iterrows():
        logger.info(f"  {row['cuisine']}: {row['non_dinneroo_orders']:,} → {row['non_dinneroo_orders_filtered']:,} ({row['filter_ratio']:.0%} retained)")
    
    return comparison


def main():
    """Main execution."""
    logger.info("=" * 60)
    logger.info("NON-DINNEROO MIDWEEK DINNER FILTER")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Filtering criteria:")
    logger.info(f"  - Non-Dinneroo orders only (IS_DINNEROO = False)")
    logger.info(f"  - Days: Monday-Thursday (DAY_OF_WEEK = {MIDWEEK_DAYS})")
    logger.info(f"  - Time: {DINNER_START_HOUR}:{DINNER_START_MINUTE:02d} - {DINNER_END_HOUR}:{DINNER_END_MINUTE:02d}")
    logger.info("")
    
    # Load data
    df = load_order_history()
    
    # Step 1: Filter to non-Dinneroo
    non_dinneroo_df = filter_non_dinneroo(df)
    
    # Save raw non-Dinneroo aggregation (for reference only)
    logger.info("\nGenerating raw (unfiltered) aggregation...")
    raw_agg = aggregate_by_cuisine(non_dinneroo_df, "unfiltered")
    raw_agg.to_csv(RAW_OUTPUT_FILE, index=False)
    logger.info(f"Saved raw aggregation to {RAW_OUTPUT_FILE}")
    
    # Step 2: Apply midweek filter
    midweek_df = filter_midweek(non_dinneroo_df)
    
    # Step 3: Apply dinner time filter
    filtered_df = filter_dinner_time(midweek_df)
    
    # Generate filtered aggregation
    logger.info("\nGenerating filtered (midweek dinner) aggregation...")
    filtered_agg = aggregate_by_cuisine(filtered_df, "midweek dinner")
    
    # Add metadata columns
    filtered_agg['filter_applied'] = 'Mon-Thu 16:30-21:00'
    filtered_agg['filter_rationale'] = 'Dinneroo is 98% midweek dinner orders'
    
    # Save filtered output
    filtered_agg.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"\nSaved filtered aggregation to {OUTPUT_FILE}")
    
    # Generate comparison stats
    logger.info("\n" + "=" * 60)
    logger.info("FILTER IMPACT ANALYSIS")
    logger.info("=" * 60)
    generate_comparison_stats(non_dinneroo_df, filtered_df)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total orders in history: {len(df):,}")
    logger.info(f"Non-Dinneroo orders: {len(non_dinneroo_df):,}")
    logger.info(f"After midweek filter: {len(midweek_df):,}")
    logger.info(f"After dinner time filter: {len(filtered_df):,}")
    logger.info(f"Retention rate: {len(filtered_df)/len(non_dinneroo_df)*100:.1f}%")
    logger.info(f"")
    logger.info(f"Cuisines in output: {len(filtered_agg)}")
    logger.info(f"")
    logger.info("CRITICAL: Use {OUTPUT_FILE.name} for benchmarks, NOT {RAW_OUTPUT_FILE.name}")
    
    return filtered_agg


if __name__ == "__main__":
    result = main()
    print(f"\nTop 20 cuisines by midweek dinner demand:")
    print(result.head(20).to_string(index=False))

