#!/usr/bin/env python3
"""
Generate Three Lists Script
===========================
Generates segment-specific dish rankings by reading weights from config.

Three Output Lists:
1. Family Performers - Best dishes for families with children (Anna 24 taxonomy)
2. Couple Performers - Best dishes for couples/adults without children (Anna 24 taxonomy)
3. Recruitment Priorities - Dishes NOT on Dinneroo with highest potential

Weights are read from config/scoring_framework_v3.json, so changing weights
and re-running this script will update the rankings.

Usage:
    python generate_three_lists.py
"""

import pandas as pd
import numpy as np
import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "DATA"
CONFIG_PATH = BASE_PATH / "config"
OUTPUT_PATH = DATA_PATH / "3_ANALYSIS"
DELIVERABLES_PATH = BASE_PATH / "DELIVERABLES" / "reports"

# Anna's 24 high-level dish types (source of truth)
ANNA_24_DISHES = [
    "Rice Bowl", "Pasta", "Grain Bowl", "Noodles", "South Asian / Indian Curry",
    "East Asian Curry", "Katsu", "Biryani", "Pizza", "Fried Rice", "Protein & Veg",
    "Chilli", "Fajitas", "Lasagne", "Shawarma", "Tacos", "Burrito / Burrito Bowl",
    "Quesadilla", "Nachos", "Pho", "Poke", "Shepherd's Pie", "Sushi", "Other"
]


def load_config():
    """Load the scoring framework configuration."""
    config_path = CONFIG_PATH / "scoring_framework_v3.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(f"✓ Loaded config v{config.get('version', 'unknown')}")
    return config


def load_data():
    """Load all required data sources."""
    data = {}
    
    # 1. Dish type rollup (Anna 24 taxonomy with granular types and partners)
    rollup_path = OUTPUT_PATH / "dish_type_rollup.csv"
    if rollup_path.exists():
        data['rollup'] = pd.read_csv(rollup_path)
        print(f"  ✓ dish_type_rollup.csv: {len(data['rollup'])} dish types")
    else:
        print(f"  ✗ Missing: dish_type_rollup.csv")
        
    # 2. Dish performance (survey data: kids_happy, adult_satisfaction, portions)
    perf_path = OUTPUT_PATH / "dish_performance.csv"
    if perf_path.exists():
        data['performance'] = pd.read_csv(perf_path)
        print(f"  ✓ dish_performance.csv: {len(data['performance'])} dishes")
    else:
        print(f"  ✗ Missing: dish_performance.csv")
    
    # 3. Dish opportunity scores (fussy_eater, adult_appeal, framework_score, etc.)
    opp_path = OUTPUT_PATH / "dish_opportunity_scores.csv"
    if opp_path.exists():
        data['opportunity'] = pd.read_csv(opp_path)
        print(f"  ✓ dish_opportunity_scores.csv: {len(data['opportunity'])} dishes")
    else:
        print(f"  ✗ Missing: dish_opportunity_scores.csv")
    
    # 4. Latent demand scores
    latent_path = OUTPUT_PATH / "latent_demand_scores.csv"
    if latent_path.exists():
        data['latent_demand'] = pd.read_csv(latent_path)
        print(f"  ✓ latent_demand_scores.csv: {len(data['latent_demand'])} dishes")
    else:
        print(f"  ✗ Missing: latent_demand_scores.csv")
    
    return data


def map_dish_type_to_anna24(dish_type: str) -> str:
    """Map various dish type names to Anna's 24-dish taxonomy."""
    # Direct matches
    if dish_type in ANNA_24_DISHES:
        return dish_type
    
    # Common mappings
    mappings = {
        'Curry': 'South Asian / Indian Curry',
        'Indian Curry': 'South Asian / Indian Curry',
        'Thai Curry': 'East Asian Curry',
        'Massaman': 'East Asian Curry',
        'Thai Green Curry': 'East Asian Curry',
        'Burrito': 'Burrito / Burrito Bowl',
        'Burrito Bowl': 'Burrito / Burrito Bowl',
        'Indian': 'South Asian / Indian Curry',
        'Satay': 'Other',
        'Wings': 'Other',
        'Chicken Wings': 'Other',
        'Mezze': 'Other',
        'Teriyaki': 'Rice Bowl',  # Teriyaki rice bowls
        'Pad Thai': 'Noodles',
        'Ramen': 'Noodles',
        'Chow Mein': 'Noodles',
    }
    
    return mappings.get(dish_type, dish_type)


def percentile_score(series: pd.Series, reverse: bool = False) -> pd.Series:
    """Convert values to 1-5 percentile-based scores."""
    if reverse:
        series = -series
    
    ranks = series.rank(pct=True, na_option='bottom')
    scores = pd.cut(
        ranks,
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[1, 2, 3, 4, 5],
        include_lowest=True
    )
    return scores.astype(float)


def generate_family_list(data: dict, config: dict) -> pd.DataFrame:
    """Generate Family Performers list using config weights."""
    print("\n📊 Generating Family Performers list...")
    
    weights = config['lists']['family_performers']['factors']
    
    # Start with rollup as base (Anna 24 taxonomy)
    df = data['rollup'].copy()
    df = df.rename(columns={'high_level_dish': 'dish_type'})
    
    # Merge performance data
    if 'performance' in data:
        perf = data['performance'].copy()
        perf['dish_type_mapped'] = perf['dish_type'].apply(map_dish_type_to_anna24)
        
        # Aggregate by Anna 24 type
        perf_agg = perf.groupby('dish_type_mapped').agg({
            'kids_happy_rate': 'mean',
            'adult_satisfaction_rate': 'mean',
            'portions_adequate_rate': 'mean',
            'n': 'sum'
        }).reset_index()
        perf_agg = perf_agg.rename(columns={'dish_type_mapped': 'dish_type'})
        
        df = df.merge(perf_agg, on='dish_type', how='left')
    
    # Merge opportunity data for fussy_eater_friendly
    if 'opportunity' in data:
        opp = data['opportunity'].copy()
        opp['dish_type_mapped'] = opp['dish_type'].apply(map_dish_type_to_anna24)
        
        opp_agg = opp.groupby('dish_type_mapped').agg({
            'fussy_eater_friendly': 'mean',
            'order_volume': 'sum',
            'adult_appeal': 'mean'
        }).reset_index()
        opp_agg = opp_agg.rename(columns={'dish_type_mapped': 'dish_type'})
        
        df = df.merge(opp_agg, on='dish_type', how='left')
    
    # Calculate percentile scores for each factor
    df['kids_happy_score'] = percentile_score(df['kids_happy_rate'].fillna(0))
    df['fussy_eater_score'] = percentile_score(df['fussy_eater_friendly'].fillna(3))
    df['orders_score'] = percentile_score(df['order_volume'].fillna(0))
    df['adult_sat_score'] = percentile_score(df['adult_satisfaction_rate'].fillna(0))
    df['portions_score'] = percentile_score(df['portions_adequate_rate'].fillna(0))
    
    # Calculate weighted family score
    df['family_score'] = (
        df['kids_happy_score'] * weights['kids_happy']['weight'] +
        df['fussy_eater_score'] * weights['fussy_eater_friendly']['weight'] +
        df['orders_score'] * weights['orders_per_zone']['weight'] +
        df['adult_sat_score'] * weights['adult_satisfaction']['weight'] +
        df['portions_score'] * weights['portions_adequate']['weight']
    )
    
    # Rank by family score
    df = df.sort_values('family_score', ascending=False)
    df['family_rank'] = range(1, len(df) + 1)
    
    # Handle ties - assign same rank
    df['family_rank'] = df['family_score'].rank(ascending=False, method='min').astype(int)
    
    # Select output columns
    output_cols = [
        'dish_type', 'family_rank', 'family_score',
        'kids_happy_rate', 'fussy_eater_friendly', 'order_volume',
        'adult_satisfaction_rate', 'portions_adequate_rate',
        'item_count', 'partners', 'granular_types'
    ]
    
    # Rename for output
    result = df[['dish_type', 'family_rank', 'family_score',
                 'kids_happy_rate', 'fussy_eater_friendly', 'order_volume',
                 'adult_satisfaction_rate', 'portions_adequate_rate',
                 'item_count', 'partners', 'granular_types']].copy()
    
    result = result.rename(columns={
        'dish_type': 'high_level_dish',
        'kids_happy_rate': 'kids_happy',
        'adult_satisfaction_rate': 'adult_satisfaction',
        'portions_adequate_rate': 'portions_adequate',
        'order_volume': 'total_orders'
    })
    
    result = result.sort_values('family_rank')
    
    print(f"  ✓ Generated {len(result)} dishes")
    print(f"  Top 5: {list(result.head()['high_level_dish'])}")
    
    return result


def generate_couple_list(data: dict, config: dict) -> pd.DataFrame:
    """Generate Couple Performers list using config weights."""
    print("\n📊 Generating Couple Performers list...")
    
    weights = config['lists']['couple_performers']['factors']
    
    # Start with rollup as base
    df = data['rollup'].copy()
    df = df.rename(columns={'high_level_dish': 'dish_type'})
    
    # Merge performance data
    if 'performance' in data:
        perf = data['performance'].copy()
        perf['dish_type_mapped'] = perf['dish_type'].apply(map_dish_type_to_anna24)
        
        perf_agg = perf.groupby('dish_type_mapped').agg({
            'adult_satisfaction_rate': 'mean',
            'n': 'sum'
        }).reset_index()
        perf_agg = perf_agg.rename(columns={'dish_type_mapped': 'dish_type'})
        
        df = df.merge(perf_agg, on='dish_type', how='left')
    
    # Merge opportunity data
    if 'opportunity' in data:
        opp = data['opportunity'].copy()
        opp['dish_type_mapped'] = opp['dish_type'].apply(map_dish_type_to_anna24)
        
        opp_agg = opp.groupby('dish_type_mapped').agg({
            'adult_appeal': 'mean',
            'order_volume': 'sum'
        }).reset_index()
        opp_agg = opp_agg.rename(columns={'dish_type_mapped': 'dish_type'})
        
        df = df.merge(opp_agg, on='dish_type', how='left')
    
    # Calculate percentile scores
    df['adult_sat_score'] = percentile_score(df['adult_satisfaction_rate'].fillna(0))
    df['rating_score'] = percentile_score(df['adult_satisfaction_rate'].fillna(0))  # Using adult_sat as proxy
    df['orders_score'] = percentile_score(df['order_volume'].fillna(0))
    df['adult_appeal_score'] = percentile_score(df['adult_appeal'].fillna(3))
    
    # Calculate weighted couple score
    df['couple_score'] = (
        df['adult_sat_score'] * weights['adult_satisfaction']['weight'] +
        df['rating_score'] * weights['rating']['weight'] +
        df['orders_score'] * weights['orders_per_zone']['weight'] +
        df['adult_appeal_score'] * weights['adult_appeal']['weight']
    )
    
    # Rank
    df = df.sort_values('couple_score', ascending=False)
    df['couple_rank'] = df['couple_score'].rank(ascending=False, method='min').astype(int)
    
    # Select output columns
    result = df[['dish_type', 'couple_rank', 'couple_score',
                 'adult_satisfaction_rate', 'adult_appeal', 'order_volume',
                 'item_count', 'partners']].copy()
    
    result = result.rename(columns={
        'dish_type': 'high_level_dish',
        'adult_satisfaction_rate': 'adult_satisfaction',
        'order_volume': 'total_orders'
    })
    
    result = result.sort_values('couple_rank')
    
    print(f"  ✓ Generated {len(result)} dishes")
    print(f"  Top 5: {list(result.head()['high_level_dish'])}")
    
    return result


def generate_recruitment_list(data: dict, config: dict) -> pd.DataFrame:
    """Generate Recruitment Priorities list using config weights."""
    print("\n📊 Generating Recruitment Priorities list...")
    
    weights = config['lists']['recruitment_priorities']['factors']
    
    # Use opportunity data as base (includes dishes not on Dinneroo)
    if 'opportunity' not in data:
        print("  ✗ Cannot generate recruitment list without opportunity data")
        return pd.DataFrame()
    
    df = data['opportunity'].copy()
    
    # Filter to dishes with supply gaps or not on Dinneroo
    df = df[
        (df['on_dinneroo'] == False) | 
        (df['gap_type'].isin(['Supply Gap', 'Quality Gap']))
    ].copy()
    
    # Merge latent demand
    if 'latent_demand' in data:
        latent = data['latent_demand'][['dish_type', 'open_text_requests', 'latent_demand_score']].copy()
        df = df.merge(latent, on='dish_type', how='left')
        df['open_text_requests'] = df['open_text_requests'].fillna(0)
    else:
        df['open_text_requests'] = 0
        df['latent_demand_score'] = 1
    
    # Calculate percentile scores
    df['latent_score'] = percentile_score(df['open_text_requests'].fillna(0))
    df['framework_score_pct'] = percentile_score(df['framework_score'].fillna(3))
    df['fussy_score'] = percentile_score(df['fussy_eater_friendly'].fillna(3))
    df['gap_score_pct'] = percentile_score(df['gap_score'].fillna(1))
    df['partner_score'] = percentile_score(df['partner_capability'].fillna(2))
    
    # Calculate weighted recruitment score
    df['recruitment_score'] = (
        df['latent_score'] * weights['latent_demand_mentions']['weight'] +
        df['framework_score_pct'] * weights['framework_score']['weight'] +
        df['fussy_score'] * weights['fussy_eater_friendly']['weight'] +
        df['gap_score_pct'] * weights['gap_score']['weight'] +
        df['partner_score'] * weights['partner_capability']['weight']
    )
    
    # Rank
    df = df.sort_values('recruitment_score', ascending=False)
    df['recruitment_rank'] = df['recruitment_score'].rank(ascending=False, method='min').astype(int)
    
    # Select output columns
    result = df[['dish_type', 'recruitment_rank', 'recruitment_score',
                 'open_text_requests', 'fussy_eater_friendly', 'gap_score',
                 'cuisine', 'potential_partners', 'gap_type']].copy()
    
    result = result.rename(columns={
        'open_text_requests': 'latent_demand_mentions'
    })
    
    result = result.sort_values('recruitment_rank')
    
    print(f"  ✓ Generated {len(result)} dishes")
    print(f"  Top 5: {list(result.head()['dish_type'])}")
    
    return result


def save_outputs(family_df: pd.DataFrame, couple_df: pd.DataFrame, 
                 recruitment_df: pd.DataFrame, config: dict):
    """Save all outputs to DATA/3_ANALYSIS and copy to DELIVERABLES."""
    print("\n💾 Saving outputs...")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Family list
    family_path = OUTPUT_PATH / "dish_family_performers.csv"
    family_df.to_csv(family_path, index=False)
    print(f"  ✓ {family_path.name}")
    
    # Couple list
    couple_path = OUTPUT_PATH / "dish_couple_performers.csv"
    couple_df.to_csv(couple_path, index=False)
    print(f"  ✓ {couple_path.name}")
    
    # Recruitment list
    recruitment_path = OUTPUT_PATH / "dish_recruitment_priorities.csv"
    recruitment_df.to_csv(recruitment_path, index=False)
    print(f"  ✓ {recruitment_path.name}")
    
    # Copy to DELIVERABLES with additional metadata
    print("\n📁 Copying to DELIVERABLES...")
    
    # Family deliverable
    family_deliv = family_df.copy()
    family_deliv_path = DELIVERABLES_PATH / "DISH_FAMILY_RANKINGS.csv"
    family_deliv.to_csv(family_deliv_path, index=False)
    print(f"  ✓ {family_deliv_path.name}")
    
    # Couple deliverable
    couple_deliv = couple_df.copy()
    couple_deliv_path = DELIVERABLES_PATH / "DISH_COUPLE_RANKINGS.csv"
    couple_deliv.to_csv(couple_deliv_path, index=False)
    print(f"  ✓ {couple_deliv_path.name}")
    
    # Recruitment deliverable
    recruitment_deliv = recruitment_df.copy()
    recruitment_deliv_path = DELIVERABLES_PATH / "DISH_RECRUITMENT_PRIORITIES.csv"
    recruitment_deliv.to_csv(recruitment_deliv_path, index=False)
    print(f"  ✓ {recruitment_deliv_path.name}")
    
    # Also create combined rollup
    rollup_path = DELIVERABLES_PATH / "DISH_RANKINGS_WITH_ROLLUP.csv"
    combined = family_df.merge(
        couple_df[['high_level_dish', 'couple_rank', 'couple_score']],
        on='high_level_dish',
        how='left'
    )
    combined.to_csv(rollup_path, index=False)
    print(f"  ✓ {rollup_path.name}")


def print_weight_summary(config: dict):
    """Print current weight configuration for verification."""
    print("\n📋 Current Weight Configuration:")
    print("=" * 60)
    
    for list_name, list_config in config['lists'].items():
        print(f"\n{list_name.upper().replace('_', ' ')}:")
        for factor, factor_config in list_config['factors'].items():
            weight_pct = int(factor_config['weight'] * 100)
            print(f"  • {factor}: {weight_pct}%")


def main():
    """Main execution."""
    print("=" * 60)
    print("GENERATE THREE LISTS")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load config
    config = load_config()
    print_weight_summary(config)
    
    # Load data
    print("\n📂 Loading data sources...")
    data = load_data()
    
    if not data.get('rollup') is not None:
        print("\n❌ Error: dish_type_rollup.csv is required")
        return
    
    # Generate lists
    family_df = generate_family_list(data, config)
    couple_df = generate_couple_list(data, config)
    recruitment_df = generate_recruitment_list(data, config)
    
    # Save outputs
    save_outputs(family_df, couple_df, recruitment_df, config)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)
    print(f"Family Performers: {len(family_df)} dishes")
    print(f"Couple Performers: {len(couple_df)} dishes")
    print(f"Recruitment Priorities: {len(recruitment_df)} dishes")
    print("\nTo update rankings, edit config/scoring_framework_v3.json")
    print("and re-run this script.")


if __name__ == "__main__":
    main()


