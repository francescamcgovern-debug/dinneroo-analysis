"""
Family Behavior Analysis
========================
Generates data for FAMILY_BEHAVIOR_AGENT:
1. non_dinneroo_cuisine_demand.csv - What families order outside Dinneroo
2. regional_cuisine_preferences.csv - Regional eating patterns
3. price_sensitivity_analysis.csv - Price point analysis

Data source: FULL_ORDER_HISTORY.csv (~800K orders)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_SOURCE = PROJECT_ROOT / "DATA" / "1_SOURCE" / "snowflake"
DATA_ANALYSIS = PROJECT_ROOT / "DATA" / "3_ANALYSIS"

# Region mapping
REGION_MAPPING = {
    # London zones
    'Clapham': 'London', 'Islington': 'London', 'Brixton': 'London', 
    'Camden/Kentish Town': 'London', 'Chiswick': 'London', 'Hackney': 'London',
    'Shoreditch': 'London', 'Peckham': 'London', 'Fulham': 'London',
    'Balham': 'London', 'Putney & Barnes': 'London', 'Battersea': 'London',
    'Hampstead': 'London', 'Notting Hill': 'London', 'Mayfair': 'London',
    'South Kensington': 'London', 'Kensington': 'London', 'Chelsea': 'London',
    'Victoria, Westminster, Pimlico': 'London', 'Euston': 'London',
    'East Central': 'London', 'Finsbury Park / Harringay / Crouch End': 'London',
    'Dalston Stoke Newington': 'London', 'Stratford': 'London',
    'Brockley / Forest Hill': 'London', 'Greenwich': 'London',
    'Canary Wharf': 'London', 'Wapping and Mile End': 'London',
    'Canning Town': 'London', 'Tottenham': 'London', 'Wood Green': 'London',
    'Golders Green / Brent Cross': 'London', 'Belsize Park / St John\'s Wood': 'London',
    'Croydon': 'London', 'Bromley': 'London', 'Richmond / Kew': 'London',
    
    # South East
    'Brighton Central': 'South East', 'Cambridge': 'South East', 'Oxford': 'South East',
    'Reading': 'South East', 'Southampton': 'South East', 'Portsmouth': 'South East',
    'Canterbury': 'South East', 'Guildford': 'South East', 'Chelmsford': 'South East',
    'Colchester': 'South East', 'Basingstoke': 'South East', 'Bournemouth': 'South East',
    'St Albans': 'South East', 'Watford': 'South East', 'Epsom': 'South East',
    
    # South West
    'Bristol': 'South West', 'Bath': 'South West', 'Cheltenham': 'South West',
    'Exeter': 'South West', 'Plymouth': 'South West',
    
    # North
    'Manchester': 'North', 'Leeds': 'North', 'Liverpool': 'North',
    'Sheffield': 'North', 'Newcastle': 'North', 'York': 'North',
    'Hull': 'North', 'Bradford': 'North', 'Harrogate': 'North',
    
    # Midlands
    'Birmingham': 'Midlands', 'Nottingham': 'Midlands', 'Leicester': 'Midlands',
    'Coventry': 'Midlands', 'Derby': 'Midlands', 'West Bridgford': 'Midlands',
    
    # Scotland
    'Edinburgh': 'Scotland', 'Edinburgh North': 'Scotland', 
    'Glasgow': 'Scotland', 'Glasgow West End': 'Scotland',
    
    # Wales
    'Cardiff': 'Wales', 'Cardiff Bay Area': 'Wales', 'Swansea': 'Wales',
    
    # Ireland
    'Dublin City North': 'Ireland', 'Dublin City South': 'Ireland',
}

def get_region(zone_name):
    """Map zone to region, with fallback to 'Other'"""
    # Check exact match first
    if zone_name in REGION_MAPPING:
        return REGION_MAPPING[zone_name]
    
    # Check partial matches
    for zone, region in REGION_MAPPING.items():
        if zone.lower() in zone_name.lower() or zone_name.lower() in zone.lower():
            return region
    
    return 'Other'


def normalize_cuisine(cuisine):
    """Normalize cuisine names for consistent grouping"""
    if pd.isna(cuisine):
        return 'Unknown'
    
    cuisine = str(cuisine).lower().strip()
    
    # Normalize common variations
    mappings = {
        'american': 'American',
        'burgers': 'Burgers',
        'chicken': 'Chicken',
        'chinese': 'Chinese',
        'indian': 'Indian',
        'italian': 'Italian',
        'japanese': 'Japanese',
        'korean': 'Korean',
        'mexican': 'Mexican',
        'thai': 'Thai',
        'vietnamese': 'Vietnamese',
        'greek': 'Greek',
        'mediterranean': 'Mediterranean',
        'caribbean': 'Caribbean',
        'african': 'African',
        'middle eastern': 'Middle Eastern',
        'mezze': 'Middle Eastern',
        'halal': 'Halal',
        'healthy': 'Healthy',
        'salads': 'Healthy',
        'sushi': 'Japanese',
        'pizza': 'Italian',
        'pasta': 'Italian',
        'curry': 'Indian',
        'pho': 'Vietnamese',
        'ramen': 'Japanese',
        'kebab': 'Middle Eastern',
        'fish & chips': 'British',
        'fish and chips': 'British',
        'british': 'British',
        'pies': 'British',
        'breakfast': 'Breakfast',
        'dessert': 'Dessert',
        'desserts': 'Dessert',
        'grocery': 'Grocery',
        'alcohol': 'Alcohol',
        'convenience': 'Convenience',
    }
    
    for key, value in mappings.items():
        if key in cuisine:
            return value
    
    return cuisine.title()


def generate_non_dinneroo_cuisine_demand(df):
    """
    Generate cuisine demand analysis for non-Dinneroo orders.
    Output: non_dinneroo_cuisine_demand.csv
    """
    print("\n=== Generating Non-Dinneroo Cuisine Demand ===")
    
    # Filter to non-Dinneroo orders only
    non_dinneroo = df[df['IS_DINNEROO'] == False].copy()
    print(f"Non-Dinneroo orders: {len(non_dinneroo):,}")
    
    # Normalize cuisine names
    non_dinneroo['cuisine_normalized'] = non_dinneroo['CUISINE'].apply(normalize_cuisine)
    
    # Aggregate by cuisine
    cuisine_demand = non_dinneroo.groupby('cuisine_normalized').agg({
        'ORDER_ID': 'count',
        'CUSTOMER_ID': 'nunique',
        'ORDER_VALUE': 'mean'
    }).reset_index()
    
    cuisine_demand.columns = ['cuisine', 'non_dinneroo_orders', 'unique_customers', 'avg_order_value']
    
    # Check what's on Dinneroo
    dinneroo_cuisines = set(df[df['IS_DINNEROO'] == True]['CUISINE'].apply(normalize_cuisine).unique())
    
    cuisine_demand['dinneroo_available'] = cuisine_demand['cuisine'].apply(
        lambda x: 'Yes' if x in dinneroo_cuisines else 'No'
    )
    
    # Calculate gap signal
    def get_gap_signal(row):
        if row['dinneroo_available'] == 'Yes':
            return 'Available'
        elif row['non_dinneroo_orders'] >= 10000:
            return 'High'
        elif row['non_dinneroo_orders'] >= 5000:
            return 'Medium'
        else:
            return 'Low'
    
    cuisine_demand['gap_signal'] = cuisine_demand.apply(get_gap_signal, axis=1)
    
    # Sort by orders descending
    cuisine_demand = cuisine_demand.sort_values('non_dinneroo_orders', ascending=False)
    
    # Round values
    cuisine_demand['avg_order_value'] = cuisine_demand['avg_order_value'].round(2)
    
    # Save
    output_path = DATA_ANALYSIS / "non_dinneroo_cuisine_demand.csv"
    cuisine_demand.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")
    print(f"Cuisines analyzed: {len(cuisine_demand)}")
    
    # Print top gaps
    gaps = cuisine_demand[cuisine_demand['gap_signal'].isin(['High', 'Medium'])]
    print(f"\nTop cuisine gaps (not on Dinneroo, high demand):")
    for _, row in gaps.head(10).iterrows():
        print(f"  {row['cuisine']}: {row['non_dinneroo_orders']:,} orders ({row['gap_signal']})")
    
    return cuisine_demand


def generate_regional_preferences(df):
    """
    Generate regional cuisine preference analysis.
    Output: regional_cuisine_preferences.csv
    """
    print("\n=== Generating Regional Cuisine Preferences ===")
    
    # Add region column
    df['region'] = df['ZONE_NAME'].apply(get_region)
    
    # Normalize cuisine
    df['cuisine_normalized'] = df['CUISINE'].apply(normalize_cuisine)
    
    # Filter out non-food categories
    food_df = df[~df['cuisine_normalized'].isin(['Grocery', 'Alcohol', 'Convenience', 'Unknown'])]
    
    # Calculate national totals
    national_totals = food_df.groupby('cuisine_normalized')['ORDER_ID'].count()
    national_total = national_totals.sum()
    national_share = (national_totals / national_total * 100).to_dict()
    
    # Calculate regional breakdown
    regional_data = []
    
    for region in df['region'].unique():
        region_df = food_df[food_df['region'] == region]
        region_total = len(region_df)
        
        if region_total < 100:  # Skip regions with too few orders
            continue
            
        cuisine_counts = region_df.groupby('cuisine_normalized')['ORDER_ID'].count()
        
        for cuisine, count in cuisine_counts.items():
            regional_share = count / region_total * 100
            nat_share = national_share.get(cuisine, 0)
            
            # Index vs national (100 = same as national)
            index_vs_national = (regional_share / nat_share * 100) if nat_share > 0 else 0
            
            # Determine regional strength
            if index_vs_national >= 120:
                strength = 'Strong'
            elif index_vs_national >= 80:
                strength = 'Moderate'
            else:
                strength = 'Weak'
            
            regional_data.append({
                'region': region,
                'cuisine': cuisine,
                'order_count': count,
                'order_share': round(regional_share, 2),
                'national_share': round(nat_share, 2),
                'index_vs_national': round(index_vs_national, 1),
                'regional_strength': strength
            })
    
    regional_df = pd.DataFrame(regional_data)
    
    # Sort by region and order share
    regional_df = regional_df.sort_values(['region', 'order_share'], ascending=[True, False])
    
    # Save
    output_path = DATA_ANALYSIS / "regional_cuisine_preferences.csv"
    regional_df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")
    print(f"Regions analyzed: {regional_df['region'].nunique()}")
    
    # Print regional highlights
    print("\nRegional highlights (strong preferences):")
    strong = regional_df[regional_df['regional_strength'] == 'Strong']
    for region in strong['region'].unique():
        region_strong = strong[strong['region'] == region].head(3)
        cuisines = ", ".join(region_strong['cuisine'].tolist())
        print(f"  {region}: {cuisines}")
    
    return regional_df


def generate_price_sensitivity(df):
    """
    Generate price sensitivity analysis.
    Output: price_sensitivity_analysis.csv
    """
    print("\n=== Generating Price Sensitivity Analysis ===")
    
    # Define price bands
    def get_price_band(value):
        if pd.isna(value) or value <= 0:
            return 'Invalid'
        elif value < 15:
            return '£0-15'
        elif value < 20:
            return '£15-20'
        elif value < 25:
            return '£20-25'
        elif value < 30:
            return '£25-30'
        elif value < 40:
            return '£30-40'
        else:
            return '£40+'
    
    df['price_band'] = df['ORDER_VALUE'].apply(get_price_band)
    
    # Filter out invalid
    valid_df = df[df['price_band'] != 'Invalid']
    
    # Separate Dinneroo vs non-Dinneroo
    dinneroo_df = valid_df[valid_df['IS_DINNEROO'] == True]
    non_dinneroo_df = valid_df[valid_df['IS_DINNEROO'] == False]
    
    # Calculate distributions
    price_data = []
    
    price_bands = ['£0-15', '£15-20', '£20-25', '£25-30', '£30-40', '£40+']
    
    dinneroo_total = len(dinneroo_df)
    non_dinneroo_total = len(non_dinneroo_df)
    
    for band in price_bands:
        dinneroo_count = len(dinneroo_df[dinneroo_df['price_band'] == band])
        non_dinneroo_count = len(non_dinneroo_df[non_dinneroo_df['price_band'] == band])
        
        dinneroo_share = (dinneroo_count / dinneroo_total * 100) if dinneroo_total > 0 else 0
        non_dinneroo_share = (non_dinneroo_count / non_dinneroo_total * 100) if non_dinneroo_total > 0 else 0
        
        # Determine if this is a sweet spot (high volume)
        sweet_spot = 'Yes' if non_dinneroo_share >= 20 else 'No'
        
        price_data.append({
            'price_band': band,
            'dinneroo_orders': dinneroo_count,
            'dinneroo_share': round(dinneroo_share, 1),
            'non_dinneroo_orders': non_dinneroo_count,
            'non_dinneroo_share': round(non_dinneroo_share, 1),
            'sweet_spot': sweet_spot
        })
    
    price_df = pd.DataFrame(price_data)
    
    # Add summary stats
    summary = {
        'dinneroo_avg_order': round(dinneroo_df['ORDER_VALUE'].mean(), 2),
        'dinneroo_median_order': round(dinneroo_df['ORDER_VALUE'].median(), 2),
        'non_dinneroo_avg_order': round(non_dinneroo_df['ORDER_VALUE'].mean(), 2),
        'non_dinneroo_median_order': round(non_dinneroo_df['ORDER_VALUE'].median(), 2),
        'dinneroo_total_orders': dinneroo_total,
        'non_dinneroo_total_orders': non_dinneroo_total,
    }
    
    # Save price analysis
    output_path = DATA_ANALYSIS / "price_sensitivity_analysis.csv"
    price_df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")
    
    # Save summary as JSON
    summary_path = DATA_ANALYSIS / "price_sensitivity_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved: {summary_path}")
    
    # Print insights
    print(f"\nPrice insights:")
    print(f"  Dinneroo avg order: £{summary['dinneroo_avg_order']}")
    print(f"  Non-Dinneroo avg order: £{summary['non_dinneroo_avg_order']}")
    print(f"  Dinneroo is {'above' if summary['dinneroo_avg_order'] > summary['non_dinneroo_avg_order'] else 'below'} general Deliveroo average")
    
    sweet_spots = price_df[price_df['sweet_spot'] == 'Yes']['price_band'].tolist()
    print(f"  Sweet spots (high volume): {', '.join(sweet_spots)}")
    
    return price_df, summary


def main():
    """Run all family behavior analyses"""
    print("=" * 60)
    print("FAMILY BEHAVIOR ANALYSIS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load data
    print("\nLoading FULL_ORDER_HISTORY.csv...")
    df = pd.read_csv(DATA_SOURCE / "FULL_ORDER_HISTORY.csv")
    print(f"Loaded {len(df):,} orders")
    
    # Convert IS_DINNEROO to boolean
    df['IS_DINNEROO'] = df['IS_DINNEROO'].astype(str).str.lower() == 'true'
    
    print(f"Dinneroo orders: {df['IS_DINNEROO'].sum():,}")
    print(f"Non-Dinneroo orders: {(~df['IS_DINNEROO']).sum():,}")
    
    # Run analyses
    cuisine_demand = generate_non_dinneroo_cuisine_demand(df)
    regional_prefs = generate_regional_preferences(df)
    price_analysis, price_summary = generate_price_sensitivity(df)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("\nOutput files:")
    print(f"  - {DATA_ANALYSIS / 'non_dinneroo_cuisine_demand.csv'}")
    print(f"  - {DATA_ANALYSIS / 'regional_cuisine_preferences.csv'}")
    print(f"  - {DATA_ANALYSIS / 'price_sensitivity_analysis.csv'}")
    print(f"  - {DATA_ANALYSIS / 'price_sensitivity_summary.json'}")


if __name__ == "__main__":
    main()


