"""
Partner Recruitment Analysis
============================
Generates data for PARTNER_AGENT:
1. partner_recruitment_priority.csv - Priority partners to recruit

Data sources:
- FULL_ORDER_HISTORY.csv - Partners on Deliveroo
- zone_gap_report.csv - What's missing where
- non_dinneroo_cuisine_demand.csv - Cuisine demand
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

# Partner-to-cuisine mapping (known partners that fill gaps)
PARTNER_CUISINE_MAP = {
    # Grilled Chicken (TOP GAP)
    "Nando's": {'cuisine': 'Grilled Chicken', 'dish_types': ['Grilled Chicken', 'Peri-Peri', 'Wraps'], 'fit_score': 95},
    'Cocotte': {'cuisine': 'Grilled Chicken', 'dish_types': ['Rotisserie Chicken', 'Roast Chicken'], 'fit_score': 85},
    'Roosters': {'cuisine': 'Grilled Chicken', 'dish_types': ['Grilled Chicken', 'Wings'], 'fit_score': 75},
    
    # Greek/Mediterranean (ZERO SUPPLY)
    'The Athenian': {'cuisine': 'Greek', 'dish_types': ['Souvlaki', 'Gyros', 'Mezze'], 'fit_score': 85},
    'Gokyuzu': {'cuisine': 'Turkish/Mediterranean', 'dish_types': ['Kebab', 'Mezze', 'Grilled Meats'], 'fit_score': 80},
    'Comptoir Libanais': {'cuisine': 'Mediterranean', 'dish_types': ['Mezze', 'Shawarma', 'Falafel'], 'fit_score': 75},
    
    # Korean (ZERO SUPPLY)
    'Korean Dinner Party': {'cuisine': 'Korean', 'dish_types': ['Bibimbap', 'Bulgogi', 'Korean Fried Chicken'], 'fit_score': 80},
    'On The Bab': {'cuisine': 'Korean', 'dish_types': ['Korean Street Food', 'Bibimbap'], 'fit_score': 75},
    'Kimchee': {'cuisine': 'Korean', 'dish_types': ['Korean BBQ', 'Bibimbap'], 'fit_score': 70},
    
    # Caribbean (ZERO SUPPLY)
    'Turtle Bay': {'cuisine': 'Caribbean', 'dish_types': ['Jerk Chicken', 'Caribbean Curry', 'Rice & Peas'], 'fit_score': 80},
    'Rudie\'s': {'cuisine': 'Caribbean', 'dish_types': ['Jerk', 'Caribbean'], 'fit_score': 75},
    
    # British Comfort
    'Pieminister': {'cuisine': 'British', 'dish_types': ['Pies', 'Mash', 'Gravy'], 'fit_score': 85},
    'The Chippy': {'cuisine': 'British', 'dish_types': ['Fish & Chips'], 'fit_score': 80},
    
    # Chinese Family (UNDERREPRESENTED)
    'Ping Pong': {'cuisine': 'Chinese', 'dish_types': ['Dim Sum', 'Chinese'], 'fit_score': 75},
    'Busaba': {'cuisine': 'Thai/Asian', 'dish_types': ['Thai', 'Asian'], 'fit_score': 70},
    
    # Portuguese (HIGH DEMAND)
    'Nando\'s': {'cuisine': 'Portuguese', 'dish_types': ['Peri-Peri Chicken'], 'fit_score': 95},  # Also covers Portuguese
    'Casa do Frango': {'cuisine': 'Portuguese', 'dish_types': ['Frango', 'Portuguese Chicken'], 'fit_score': 85},
}

# Gap priorities (from analysis)
GAP_PRIORITIES = {
    'Grilled Chicken': {'priority': 'Critical', 'demand_signal': 'High', 'current_supply': 'Zero'},
    'Greek': {'priority': 'Critical', 'demand_signal': 'Medium', 'current_supply': 'Zero'},
    'Korean': {'priority': 'Critical', 'demand_signal': 'Medium', 'current_supply': 'Zero'},
    'Caribbean': {'priority': 'High', 'demand_signal': 'Low-Medium', 'current_supply': 'Zero'},
    'British': {'priority': 'High', 'demand_signal': 'High', 'current_supply': 'Limited'},
    'Portuguese': {'priority': 'High', 'demand_signal': 'High', 'current_supply': 'Zero'},
    'Turkish': {'priority': 'Medium', 'demand_signal': 'Medium', 'current_supply': 'Limited'},
    'Chinese': {'priority': 'Medium', 'demand_signal': 'High', 'current_supply': 'Underrepresented'},
}


def analyze_deliveroo_partners(df):
    """Analyze which partners are on Deliveroo but not Dinneroo"""
    
    # Get non-Dinneroo partners
    non_dinneroo = df[df['IS_DINNEROO'] == False]
    
    # Aggregate by partner
    partner_stats = non_dinneroo.groupby('PARTNER_NAME').agg({
        'ORDER_ID': 'count',
        'CUSTOMER_ID': 'nunique',
        'ORDER_VALUE': 'mean',
        'CUISINE': 'first',
        'ZONE_NAME': 'nunique'
    }).reset_index()
    
    partner_stats.columns = ['partner_name', 'orders', 'unique_customers', 'avg_order_value', 'cuisine', 'zones_available']
    
    return partner_stats


def generate_partner_recruitment_priority(df):
    """Generate partner recruitment priority list"""
    print("\n=== Generating Partner Recruitment Priority ===")
    
    # Load cuisine demand data
    cuisine_demand = pd.read_csv(DATA_ANALYSIS / "non_dinneroo_cuisine_demand.csv")
    
    # Get partner stats from Deliveroo
    partner_stats = analyze_deliveroo_partners(df)
    
    # Build recruitment priority list
    recruitment_data = []
    
    for partner, info in PARTNER_CUISINE_MAP.items():
        cuisine = info['cuisine']
        gap_info = GAP_PRIORITIES.get(cuisine, {'priority': 'Low', 'demand_signal': 'Unknown', 'current_supply': 'Unknown'})
        
        # Check if partner exists on Deliveroo
        partner_match = partner_stats[partner_stats['partner_name'].str.contains(partner.split()[0], case=False, na=False)]
        
        on_deliveroo = len(partner_match) > 0
        deliveroo_orders = partner_match['orders'].sum() if on_deliveroo else 0
        deliveroo_zones = partner_match['zones_available'].max() if on_deliveroo else 0
        
        # Get cuisine demand
        cuisine_row = cuisine_demand[cuisine_demand['cuisine'].str.lower() == cuisine.lower()]
        demand_orders = cuisine_row['non_dinneroo_orders'].values[0] if len(cuisine_row) > 0 else 0
        
        recruitment_data.append({
            'partner': partner,
            'cuisine_gap': cuisine,
            'dish_types': ', '.join(info['dish_types']),
            'priority': gap_info['priority'],
            'demand_signal': gap_info['demand_signal'],
            'current_dinneroo_supply': gap_info['current_supply'],
            'fit_score': info['fit_score'],
            'on_deliveroo': 'Yes' if on_deliveroo else 'Unknown',
            'deliveroo_orders': deliveroo_orders,
            'deliveroo_zones': deliveroo_zones,
            'cuisine_demand_orders': demand_orders,
            'recommendation': 'Recruit' if gap_info['priority'] in ['Critical', 'High'] else 'Consider'
        })
    
    recruitment_df = pd.DataFrame(recruitment_data)
    
    # Sort by priority and fit score
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    recruitment_df['priority_rank'] = recruitment_df['priority'].map(priority_order)
    recruitment_df = recruitment_df.sort_values(['priority_rank', 'fit_score'], ascending=[True, False])
    recruitment_df = recruitment_df.drop('priority_rank', axis=1)
    
    # Save
    output_path = DATA_ANALYSIS / "partner_recruitment_priority.csv"
    recruitment_df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")
    print(f"Partners analyzed: {len(recruitment_df)}")
    
    # Print top recommendations
    print("\nTop recruitment priorities:")
    critical = recruitment_df[recruitment_df['priority'] == 'Critical']
    for _, row in critical.iterrows():
        print(f"  {row['partner']} ({row['cuisine_gap']}): Fit {row['fit_score']}%, {row['on_deliveroo']} on Deliveroo")
    
    return recruitment_df


def generate_expansion_candidates(df):
    """Identify existing Dinneroo partners that should expand to more zones"""
    print("\n=== Generating Partner Expansion Candidates ===")
    
    # Get Dinneroo partner performance
    dinneroo = df[df['IS_DINNEROO'] == True]
    
    partner_performance = dinneroo.groupby('PARTNER_NAME').agg({
        'ORDER_ID': 'count',
        'CUSTOMER_ID': 'nunique',
        'ORDER_VALUE': 'mean',
        'ZONE_NAME': 'nunique'
    }).reset_index()
    
    partner_performance.columns = ['partner', 'dinneroo_orders', 'unique_customers', 'avg_order_value', 'current_zones']
    
    # Calculate orders per zone (efficiency metric)
    partner_performance['orders_per_zone'] = partner_performance['dinneroo_orders'] / partner_performance['current_zones']
    
    # Identify expansion candidates (high performance, limited zones)
    partner_performance['expansion_potential'] = partner_performance.apply(
        lambda x: 'High' if x['orders_per_zone'] > 200 and x['current_zones'] < 50 else
                  'Medium' if x['orders_per_zone'] > 100 and x['current_zones'] < 80 else
                  'Low',
        axis=1
    )
    
    # Sort by expansion potential and orders
    partner_performance = partner_performance.sort_values(
        ['expansion_potential', 'dinneroo_orders'], 
        ascending=[True, False]
    )
    
    # Save
    output_path = DATA_ANALYSIS / "partner_expansion_candidates.csv"
    partner_performance.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")
    
    # Print top expansion candidates
    print("\nTop expansion candidates:")
    high_potential = partner_performance[partner_performance['expansion_potential'] == 'High'].head(5)
    for _, row in high_potential.iterrows():
        print(f"  {row['partner']}: {row['dinneroo_orders']:,} orders in {row['current_zones']} zones ({row['orders_per_zone']:.0f}/zone)")
    
    return partner_performance


def main():
    """Run partner recruitment analysis"""
    print("=" * 60)
    print("PARTNER RECRUITMENT ANALYSIS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load data
    print("\nLoading FULL_ORDER_HISTORY.csv...")
    df = pd.read_csv(DATA_SOURCE / "FULL_ORDER_HISTORY.csv")
    print(f"Loaded {len(df):,} orders")
    
    # Convert IS_DINNEROO to boolean
    df['IS_DINNEROO'] = df['IS_DINNEROO'].astype(str).str.lower() == 'true'
    
    # Run analyses
    recruitment_priority = generate_partner_recruitment_priority(df)
    expansion_candidates = generate_expansion_candidates(df)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("\nOutput files:")
    print(f"  - {DATA_ANALYSIS / 'partner_recruitment_priority.csv'}")
    print(f"  - {DATA_ANALYSIS / 'partner_expansion_candidates.csv'}")


if __name__ == "__main__":
    main()


