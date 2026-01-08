"""
Generate Slides Data v3.0
=========================
Generates slides_data.csv from the unified scoring output.

Uses:
- priority_100_unified.csv as single source of truth
- Performance/Opportunity terminology
- Action-oriented quadrant names (Core Drivers, Preference Drivers, etc.)

Output format follows the slide-tagged row structure:
- SUMMARY: Key metrics
- CORE_DRIVERS: High perf + high opp dishes
- PREFERENCE_DRIVERS: High opp, lower perf
- DEMAND_BOOSTERS: High perf, lower opp
- COVERAGE_ACTION: Gaps to address
- PROSPECTS: Not on Dinneroo opportunities
- PERFORMANCE: Detailed metrics per dish
- INSIGHTS: Key findings
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "DATA" / "3_ANALYSIS"
OUTPUT_PATH = BASE_PATH / "DELIVERABLES" / "presentation_data"

def load_unified_data():
    """Load the unified scoring output."""
    csv_path = DATA_PATH / "priority_100_unified.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        print(f"Loaded priority_100_unified.csv: {len(df)} dishes")
        return df
    else:
        print("ERROR: priority_100_unified.csv not found")
        return pd.DataFrame()


def load_performance_data():
    """Load additional performance metrics."""
    perf_path = DATA_PATH / "dish_performance.csv"
    if perf_path.exists():
        return pd.read_csv(perf_path)
    return pd.DataFrame()


def generate_slides_data(df, perf_df):
    """Generate slide-tagged data rows."""
    rows = []
    
    # Header
    rows.append({
        'sheet_name': '# SLIDES DATA - Generated from priority_100_unified.csv',
        'metric': '',
        'value': '',
        'notes': ''
    })
    rows.append({
        'sheet_name': f'# Generated: {datetime.now().strftime("%Y-%m-%d")}',
        'metric': '',
        'value': '',
        'notes': ''
    })
    rows.append({
        'sheet_name': '# Framework: 6-Factor, 60/40 Performance/Opportunity Split',
        'metric': '',
        'value': '',
        'notes': ''
    })
    
    # SUMMARY METRICS
    on_dinneroo = df[df['on_dinneroo'] == True]
    off_dinneroo = df[df['on_dinneroo'] == False]
    
    core_drivers = df[df['quadrant'] == 'Core Drivers']
    preference_drivers = df[df['quadrant'] == 'Preference Drivers']
    demand_boosters = df[df['quadrant'] == 'Demand Boosters']
    deprioritised = df[df['quadrant'] == 'Deprioritised']
    
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# SLIDE 1: SUMMARY METRICS', 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    
    rows.append({
        'sheet_name': 'SUMMARY',
        'metric': 'Dish Types Analysed',
        'value': str(len(df)),
        'notes': f'{len(on_dinneroo)} on Dinneroo + {len(off_dinneroo)} prospects'
    })
    rows.append({
        'sheet_name': 'SUMMARY',
        'metric': 'On Dinneroo',
        'value': str(len(on_dinneroo)),
        'notes': 'Currently available on platform'
    })
    rows.append({
        'sheet_name': 'SUMMARY',
        'metric': 'Prospects',
        'value': str(len(off_dinneroo)),
        'notes': 'Not yet on platform - recruitment opportunities'
    })
    rows.append({
        'sheet_name': 'SUMMARY',
        'metric': 'Core Drivers',
        'value': str(len(core_drivers)),
        'notes': 'High performance + high opportunity'
    })
    rows.append({
        'sheet_name': 'SUMMARY',
        'metric': 'Preference Drivers',
        'value': str(len(preference_drivers)),
        'notes': 'High opportunity, build demand'
    })
    rows.append({
        'sheet_name': 'SUMMARY',
        'metric': 'Demand Boosters',
        'value': str(len(demand_boosters)),
        'notes': 'High performance, improve quality'
    })
    rows.append({
        'sheet_name': 'SUMMARY',
        'metric': 'Deprioritised',
        'value': str(len(deprioritised)),
        'notes': 'Low performance and opportunity'
    })
    
    # 2x2 MATRIX DATA
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# SLIDE 2: 2x2 MATRIX DATA (Performance vs Opportunity)', 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# X = performance_score | Y = opportunity_score | Quadrant = action', 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    
    for _, dish in df.iterrows():
        perf = dish.get('performance_score', 0) or 0
        opp = dish.get('opportunity_score', 0) or 0
        quadrant = dish.get('quadrant', 'Unknown')
        
        rows.append({
            'sheet_name': 'MATRIX_2X2',
            'metric': dish['dish_type'],
            'value': f"{perf:.1f}|{opp:.1f}",
            'notes': f"{quadrant} - rank #{dish.get('rank', 'N/A')}"
        })
    
    # CORE DRIVERS
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# SLIDE 3: CORE DRIVERS - Protect and expand', 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    
    for _, dish in core_drivers.iterrows():
        # Build metrics string
        metrics = []
        if pd.notna(dish.get('order_volume')):
            metrics.append(f"{int(dish['order_volume'])} orders")
        if pd.notna(dish.get('orders_per_zone')):
            metrics.append(f"{dish['orders_per_zone']:.1f} per zone")
        if pd.notna(dish.get('avg_rating')):
            metrics.append(f"{dish['avg_rating']:.1f} rating")
        if pd.notna(dish.get('kids_happy')):
            kids = dish['kids_happy']
            if kids <= 1:
                kids = kids * 100
            metrics.append(f"{kids:.0f}% kids happy")
        
        rows.append({
            'sheet_name': 'CORE_DRIVERS',
            'metric': dish['dish_type'],
            'value': '|'.join(metrics) if metrics else 'No data',
            'notes': f"{dish.get('cuisine', 'Unknown')} - score {dish.get('unified_score', 0):.2f}"
        })
    
    # PREFERENCE DRIVERS
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# SLIDE 4: PREFERENCE DRIVERS - Build demand', 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    
    for _, dish in preference_drivers.iterrows():
        rows.append({
            'sheet_name': 'PREFERENCE_DRIVERS',
            'metric': dish['dish_type'],
            'value': f"Opp: {dish.get('opportunity_score', 0):.1f}|Perf: {dish.get('performance_score', 'N/A')}",
            'notes': f"{dish.get('cuisine', 'Unknown')} - high potential, needs volume"
        })
    
    # DEMAND BOOSTERS
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# SLIDE 5: DEMAND BOOSTERS - Improve quality', 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    
    for _, dish in demand_boosters.head(15).iterrows():
        metrics = []
        if pd.notna(dish.get('order_volume')):
            metrics.append(f"{int(dish['order_volume'])} orders")
        if pd.notna(dish.get('avg_rating')):
            metrics.append(f"{dish['avg_rating']:.1f} rating")
        
        rows.append({
            'sheet_name': 'DEMAND_BOOSTERS',
            'metric': dish['dish_type'],
            'value': '|'.join(metrics) if metrics else f"Score: {dish.get('unified_score', 0):.2f}",
            'notes': f"{dish.get('cuisine', 'Unknown')} - volume exists, improve satisfaction"
        })
    
    # PROSPECTS (not on Dinneroo)
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# SLIDE 6: PROSPECTS - Recruitment opportunities', 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    
    for _, dish in off_dinneroo.head(15).iterrows():
        opp_score = dish.get('opportunity_score', 0)
        latent = dish.get('latent_demand_score', 0)
        
        rows.append({
            'sheet_name': 'PROSPECTS',
            'metric': dish['dish_type'],
            'value': f"Opportunity: {opp_score:.1f}|Latent: {latent}",
            'notes': f"{dish.get('cuisine', 'Unknown')} - not on Dinneroo"
        })
    
    # KEY INSIGHTS
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# SLIDE 7: KEY INSIGHTS', 'metric': '', 'value': '', 'notes': ''})
    rows.append({'sheet_name': '# ' + '─' * 60, 'metric': '', 'value': '', 'notes': ''})
    
    # Top performer
    if len(df) > 0:
        top = df.iloc[0]
        rows.append({
            'sheet_name': 'INSIGHTS',
            'metric': 'Top Performer',
            'value': top['dish_type'],
            'notes': f"Score: {top.get('unified_score', 0):.2f}"
        })
    
    # Most Core Drivers
    if len(core_drivers) > 0:
        rows.append({
            'sheet_name': 'INSIGHTS',
            'metric': 'Core Drivers Count',
            'value': str(len(core_drivers)),
            'notes': 'Protect and expand these dishes'
        })
    
    # Framework summary
    rows.append({
        'sheet_name': 'INSIGHTS',
        'metric': 'Framework',
        'value': '60/40 Performance/Opportunity',
        'notes': '6 factors: Orders/Zone, Zone Ranking, Rating, Kids Happy, Latent Demand, Non-Dinneroo'
    })
    
    return pd.DataFrame(rows)


def generate_dish_tiers(df):
    """Generate dish_tiers.csv from unified data."""
    tiers = []
    
    for _, dish in df.iterrows():
        tier_label = dish.get('tier', 'Monitor')
        if 'Must-Have' in tier_label:
            tier = 'Must Have'
        elif 'Should-Have' in tier_label:
            tier = 'Should Have'
        elif 'Nice-to-Have' in tier_label:
            tier = 'Nice to Have'
        else:
            tier = 'Monitor'
        
        tiers.append({
            'Rank': dish.get('rank'),
            'Dish': dish.get('dish_type'),
            'Tier': tier,
            'Unified Score': dish.get('unified_score'),
            'Performance Score': dish.get('performance_score'),
            'Opportunity Score': dish.get('opportunity_score'),
            'Quadrant': dish.get('quadrant'),
            'Cuisine': dish.get('cuisine'),
            'On Dinneroo': dish.get('on_dinneroo'),
            'Order Volume': dish.get('order_volume'),
            'Orders per Zone': dish.get('orders_per_zone')
        })
    
    return pd.DataFrame(tiers)


def main():
    """Generate all presentation data files."""
    print("=" * 60)
    print("GENERATE SLIDES DATA v3.0")
    print("From priority_100_unified.csv")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading data...")
    df = load_unified_data()
    perf_df = load_performance_data()
    
    if len(df) == 0:
        print("ERROR: No data to process")
        return
    
    # Generate slides_data.csv
    print("\n2. Generating slides_data.csv...")
    slides_df = generate_slides_data(df, perf_df)
    
    slides_path = OUTPUT_PATH / "slides_data.csv"
    slides_df.to_csv(slides_path, index=False)
    print(f"   Saved: {slides_path}")
    
    # Generate dish_tiers.csv
    print("\n3. Generating dish_tiers.csv...")
    tiers_df = generate_dish_tiers(df)
    
    tiers_path = OUTPUT_PATH / "dish_tiers.csv"
    tiers_df.to_csv(tiers_path, index=False)
    print(f"   Saved: {tiers_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    quadrant_counts = df['quadrant'].value_counts()
    print("\nQuadrant Distribution:")
    for quad, count in quadrant_counts.items():
        print(f"  {quad}: {count}")
    
    tier_counts = tiers_df['Tier'].value_counts()
    print("\nTier Distribution:")
    for tier, count in tier_counts.items():
        print(f"  {tier}: {count}")
    
    print("\n✓ Presentation data generated!")


if __name__ == "__main__":
    main()


