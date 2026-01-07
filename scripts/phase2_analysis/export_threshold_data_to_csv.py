#!/usr/bin/env python3
"""
Export MVP threshold discovery data to CSV files for charting in slides.
"""

import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_FILE = BASE_DIR / "DATA" / "3_ANALYSIS" / "mvp_threshold_discovery.json"
OUTPUT_DIR = BASE_DIR / "DELIVERABLES" / "presentation_data"

def load_data():
    with open(INPUT_FILE, 'r') as f:
        return json.load(f)

def export_partners_table(data):
    """Export partner count analysis to CSV."""
    rows = []
    for bucket in data['step_1_partners']['by_partner_count']:
        rows.append({
            'partners': bucket['bucket'],
            'zones': bucket['zones'],
            'repeat_rate': round(bucket['behavioral']['repeat_rate']['value'] * 100, 1) if bucket['behavioral']['repeat_rate']['value'] else None,
            'repeat_rate_n': bucket['behavioral']['repeat_rate']['n'],
            'avg_rating': round(bucket['behavioral']['avg_rating']['value'], 2) if bucket['behavioral']['avg_rating']['value'] else None,
            'avg_rating_n': bucket['behavioral']['avg_rating']['n'],
            'kids_happy_pct': round(bucket['survey']['kids_happy']['value'] * 100, 1) if bucket['survey']['kids_happy']['value'] else None,
            'kids_happy_n': bucket['survey']['kids_happy']['n'],
            'liked_loved_pct': round(bucket['survey']['liked_loved']['value'] * 100, 1) if bucket['survey']['liked_loved']['value'] else None,
            'liked_loved_n': bucket['survey']['liked_loved']['n'],
            'enough_food_pct': round(bucket['survey']['enough_food']['value'] * 100, 1) if bucket['survey']['enough_food']['value'] else None,
            'enough_food_n': bucket['survey']['enough_food']['n'],
            'food_hot_pct': round(bucket['survey']['food_hot']['value'] * 100, 1) if bucket['survey']['food_hot']['value'] else None,
            'food_hot_n': bucket['survey']['food_hot']['n'],
            'food_on_time_pct': round(bucket['survey']['food_on_time']['value'] * 100, 1) if bucket['survey']['food_on_time']['value'] else None,
            'food_on_time_n': bucket['survey']['food_on_time']['n'],
        })
    
    df = pd.DataFrame(rows)
    # Sort by partner count
    sort_order = {'1-2': 1, '3-4': 2, '5-6': 3, '7-9': 4, '10+': 5}
    df['sort_key'] = df['partners'].map(sort_order)
    df = df.sort_values('sort_key').drop('sort_key', axis=1)
    
    return df

def export_cuisines_table(data):
    """Export cuisine count analysis to CSV."""
    rows = []
    for bucket in data['step_2_cuisines_within_partners']['by_cuisine_count']:
        rows.append({
            'cuisines': bucket['bucket'],
            'zones': bucket['zones'],
            'repeat_rate': round(bucket['behavioral']['repeat_rate']['value'] * 100, 1) if bucket['behavioral']['repeat_rate']['value'] else None,
            'repeat_rate_n': bucket['behavioral']['repeat_rate']['n'],
            'avg_rating': round(bucket['behavioral']['avg_rating']['value'], 2) if bucket['behavioral']['avg_rating']['value'] else None,
            'avg_rating_n': bucket['behavioral']['avg_rating']['n'],
            'kids_happy_pct': round(bucket['survey']['kids_happy']['value'] * 100, 1) if bucket['survey']['kids_happy']['value'] else None,
            'kids_happy_n': bucket['survey']['kids_happy']['n'],
            'liked_loved_pct': round(bucket['survey']['liked_loved']['value'] * 100, 1) if bucket['survey']['liked_loved']['value'] else None,
            'liked_loved_n': bucket['survey']['liked_loved']['n'],
            'enough_food_pct': round(bucket['survey']['enough_food']['value'] * 100, 1) if bucket['survey']['enough_food']['value'] else None,
            'enough_food_n': bucket['survey']['enough_food']['n'],
            'food_hot_pct': round(bucket['survey']['food_hot']['value'] * 100, 1) if bucket['survey']['food_hot']['value'] else None,
            'food_hot_n': bucket['survey']['food_hot']['n'],
            'food_on_time_pct': round(bucket['survey']['food_on_time']['value'] * 100, 1) if bucket['survey']['food_on_time']['value'] else None,
            'food_on_time_n': bucket['survey']['food_on_time']['n'],
        })
    
    df = pd.DataFrame(rows)
    # Sort by cuisine count
    sort_order = {'1-2': 1, '3-4': 2, '5-6': 3, '7+': 4}
    df['sort_key'] = df['cuisines'].map(sort_order)
    df = df.sort_values('sort_key').drop('sort_key', axis=1)
    
    return df

def export_dishes_per_zone_table(data):
    """Export dishes per zone analysis to CSV."""
    rows = []
    for bucket in data['step_3_dishes_within_partners_and_cuisines']['dishes_per_zone']['buckets']:
        rows.append({
            'dishes_per_zone': bucket['bucket'],
            'zones': bucket['zones'],
            'repeat_rate': round(bucket['behavioral']['repeat_rate']['value'] * 100, 1) if bucket['behavioral']['repeat_rate']['value'] else None,
            'repeat_rate_n': bucket['behavioral']['repeat_rate']['n'],
            'avg_rating': round(bucket['behavioral']['avg_rating']['value'], 2) if bucket['behavioral']['avg_rating']['value'] else None,
            'avg_rating_n': bucket['behavioral']['avg_rating']['n'],
            'kids_happy_pct': round(bucket['survey']['kids_happy']['value'] * 100, 1) if bucket['survey']['kids_happy']['value'] else None,
            'kids_happy_n': bucket['survey']['kids_happy']['n'],
            'liked_loved_pct': round(bucket['survey']['liked_loved']['value'] * 100, 1) if bucket['survey']['liked_loved']['value'] else None,
            'liked_loved_n': bucket['survey']['liked_loved']['n'],
            'enough_food_pct': round(bucket['survey']['enough_food']['value'] * 100, 1) if bucket['survey']['enough_food']['value'] else None,
            'enough_food_n': bucket['survey']['enough_food']['n'],
        })
    
    df = pd.DataFrame(rows)
    # Sort by dish count
    sort_order = {'1-15': 1, '16-30': 2, '31-50': 3, '51+': 4}
    df['sort_key'] = df['dishes_per_zone'].map(sort_order)
    df = df.sort_values('sort_key').drop('sort_key', axis=1)
    
    return df

def export_dishes_per_partner_table(data):
    """Export dishes per partner analysis to CSV."""
    rows = []
    for bucket in data['step_3_dishes_within_partners_and_cuisines']['dishes_per_partner']['buckets']:
        rows.append({
            'dishes_per_partner': bucket['bucket'],
            'zones': bucket['zones'],
            'repeat_rate': round(bucket['behavioral']['repeat_rate']['value'] * 100, 1) if bucket['behavioral']['repeat_rate']['value'] else None,
            'repeat_rate_n': bucket['behavioral']['repeat_rate']['n'],
            'avg_rating': round(bucket['behavioral']['avg_rating']['value'], 2) if bucket['behavioral']['avg_rating']['value'] else None,
            'avg_rating_n': bucket['behavioral']['avg_rating']['n'],
            'kids_happy_pct': round(bucket['survey']['kids_happy']['value'] * 100, 1) if bucket['survey']['kids_happy']['value'] else None,
            'kids_happy_n': bucket['survey']['kids_happy']['n'],
            'liked_loved_pct': round(bucket['survey']['liked_loved']['value'] * 100, 1) if bucket['survey']['liked_loved']['value'] else None,
            'liked_loved_n': bucket['survey']['liked_loved']['n'],
            'enough_food_pct': round(bucket['survey']['enough_food']['value'] * 100, 1) if bucket['survey']['enough_food']['value'] else None,
            'enough_food_n': bucket['survey']['enough_food']['n'],
            'food_hot_pct': round(bucket['survey']['food_hot']['value'] * 100, 1) if bucket['survey']['food_hot']['value'] else None,
            'food_hot_n': bucket['survey']['food_hot']['n'],
        })
    
    df = pd.DataFrame(rows)
    # Sort by dish count
    sort_order = {'3-4': 1, '4-5': 2, '5-6': 3, '6+': 4}
    df['sort_key'] = df['dishes_per_partner'].map(sort_order)
    df = df.sort_values('sort_key').drop('sort_key', axis=1)
    
    return df

def export_summary_table():
    """Export the minimum vs target summary table."""
    rows = [
        {
            'criterion': 'Partners',
            'minimum_threshold': 3,
            'target_threshold': 5,
            'minimum_evidence': '+4.5pp repeat rate at 3 partners',
            'target_evidence': '+9.4pp kids happy at 5 partners',
            'below_minimum_repeat_rate': 13.9,
            'at_minimum_repeat_rate': 18.4,
            'at_target_repeat_rate': 21.6,
            'below_minimum_kids_happy': 65.1,
            'at_minimum_kids_happy': 70.0,
            'at_target_kids_happy': 79.5,
        },
        {
            'criterion': 'Cuisines',
            'minimum_threshold': 3,
            'target_threshold': 5,
            'minimum_evidence': '+13.6pp liked/loved at 3 cuisines',
            'target_evidence': '+4.2pp repeat rate at 5 cuisines',
            'below_minimum_repeat_rate': 18.3,
            'at_minimum_repeat_rate': 19.1,
            'at_target_repeat_rate': 23.3,
            'below_minimum_kids_happy': 67.4,
            'at_minimum_kids_happy': 76.2,
            'at_target_kids_happy': 66.9,
        },
        {
            'criterion': 'Dishes per Partner',
            'minimum_threshold': 4,
            'target_threshold': 5,
            'minimum_evidence': 'Baseline performance',
            'target_evidence': 'Peak repeat rate (22.3%)',
            'below_minimum_repeat_rate': 20.9,
            'at_minimum_repeat_rate': 21.6,
            'at_target_repeat_rate': 22.3,
            'below_minimum_kids_happy': 84.0,
            'at_minimum_kids_happy': 61.3,
            'at_target_kids_happy': 67.3,
        },
    ]
    return pd.DataFrame(rows)

def export_zone_health_note():
    """Export zone health indicator data."""
    rows = [
        {'total_dishes_per_zone': '1-15', 'repeat_rate': 16.8, 'note': 'Below minimum'},
        {'total_dishes_per_zone': '16-30', 'repeat_rate': 19.5, 'note': 'Minimum'},
        {'total_dishes_per_zone': '31-50', 'repeat_rate': 22.4, 'note': 'Target'},
        {'total_dishes_per_zone': '51+', 'repeat_rate': 21.2, 'note': 'Diminishing returns'},
    ]
    return pd.DataFrame(rows)

def main():
    print("Exporting MVP threshold data to CSV files...")
    
    # Load data
    data = load_data()
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Export each table
    tables = {
        'mvp_partners_by_count.csv': export_partners_table(data),
        'mvp_cuisines_by_count.csv': export_cuisines_table(data),
        'mvp_dishes_per_zone.csv': export_dishes_per_zone_table(data),
        'mvp_dishes_per_partner.csv': export_dishes_per_partner_table(data),
        'mvp_summary_min_vs_target.csv': export_summary_table(),
        'mvp_zone_health_indicator.csv': export_zone_health_note(),
    }
    
    for filename, df in tables.items():
        filepath = OUTPUT_DIR / filename
        df.to_csv(filepath, index=False)
        print(f"  Exported: {filepath}")
        print(f"    Columns: {list(df.columns)}")
        print(f"    Rows: {len(df)}")
        print()
    
    print(f"\nAll files exported to: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()

