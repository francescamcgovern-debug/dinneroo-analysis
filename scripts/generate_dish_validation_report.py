#!/usr/bin/env python3
"""
Generate Dish Validation Report (Excel Workbook)
==================================================
Creates the final deliverable: dish_validation_report.xlsx

Tabs:
1. Ranking Comparison - Side-by-side rankings with Anna's tiers preserved
2. All Metrics - Full data with Anna's naming for sorting/filtering
3. How Rankings Work - Methodology explanation
4. Data Dictionary - Source, definition, formula, date
5. Mapping QA - Survey mapping quality metrics
6. Drop-off Cuisine Requests - Open-text cuisine mentions (separate; not forced into dish types)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "DATA/3_ANALYSIS"
DELIVERABLES_DIR = BASE_DIR / "DELIVERABLES/reports"
DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

# Drop-off source column (for traceability in Data Dictionary text)
DROPOFF_REQUESTS_SOURCE_COL = "What dishes and cuisines would you like to see more of? (please list as many as you can)"

# Column renaming: internal -> Anna's terminology
COLUMN_RENAME = {
    'dish_type': 'Dish Type',
    'cuisine': 'Cuisine',
    'current_tier': 'Anna Tier',
    'on_dinneroo': 'On Dinneroo',
    'looker_demand_index': 'Demand Strength',
    'looker_preference_index': 'Consumer Preference',
    'family_suitability': 'Family Suitability (Pre-Launch)',
    'kids_full_and_happy_pct': 'Kids Happy % (Post-Order)',
    'kids_full_and_happy_n': 'Kids Happy Sample Size',
    'kids_full_and_happy_numerator': 'Kids Happy Count',
    'kids_full_and_happy_denominator': 'Kids Happy Base',
    'nonfam_satisfied_pct': 'Non-Family Satisfied % (Post-Order)',
    'nonfam_total': 'Non-Family Sample Size',
    'coverage_gap_pct': 'Coverage Gap %',
    'mapping_coverage_pct': 'Mapping Coverage %',
    'dropoff_requests': 'Drop-off Requests',
    'dropoff_demand_signal': 'Drop-off Demand Signal',
    'validation_status': 'Validation',
    'validation_confidence': 'Confidence',
    'research_notes': 'Research Notes'
}

# Note: Anna Rank, Family Rank, Non-Family Rank, Balanced Rank, and Shift columns
# are created during calculation and don't need renaming


def fix_unknown_tier(df):
    """Fix 'Unknown' tier display - use 'Not Tiered' for clarity."""
    df = df.copy()
    df['current_tier'] = df['current_tier'].replace('Unknown', 'Not Tiered')
    return df


def load_nonfamily_satisfaction(df):
    """Load and merge non-family satisfaction data."""
    nonfam_path = ANALYSIS_DIR / "nonfamily_satisfaction.csv"
    if nonfam_path.exists():
        nonfam = pd.read_csv(nonfam_path)
        df = df.merge(nonfam[['dish_type', 'nonfam_satisfied_pct', 'nonfam_total']], 
                      on='dish_type', how='left')
    return df


def load_dropoff_requests(df):
    """Load and merge drop-off open-text request counts mapped to dish types."""
    dropoff_path = ANALYSIS_DIR / "dropoff_dish_requests.csv"
    if dropoff_path.exists():
        dropoff = pd.read_csv(dropoff_path)
        # Keep only the columns we need in the workbook/scoring
        keep = [c for c in ['dish_type', 'dropoff_requests', 'dropoff_demand_signal'] if c in dropoff.columns]
        if keep:
            df = df.merge(dropoff[keep], on='dish_type', how='left')
    # Fill defaults
    if 'dropoff_requests' in df.columns:
        df['dropoff_requests'] = df['dropoff_requests'].fillna(0).astype(int)
    if 'dropoff_demand_signal' in df.columns:
        df['dropoff_demand_signal'] = df['dropoff_demand_signal'].fillna('None')
    return df


def load_dropoff_cuisine_requests():
    """Load Tab: Drop-off Cuisine Requests (cuisine-level mentions)."""
    path = ANALYSIS_DIR / "dropoff_cuisine_requests.csv"
    if path.exists():
        df = pd.read_csv(path)
        # Friendly column names
        df = df.rename(columns={
            'cuisine': 'Cuisine Mention',
            'mentions': 'Mentions (Count)',
            'mention_share': 'Share of Responses'
        })
        return df
    return pd.DataFrame()


def calculate_rankings(df):
    """Calculate Demand Rank, Family Rank, and Balanced Rank."""
    df = df.copy()
    
    # Only rank Dinneroo dishes (exclude Test & Learn)
    on_dinneroo_mask = df['on_dinneroo'] == True
    
    # Demand Rank: Sort by Demand Strength (descending)
    # Higher demand = lower rank number (rank 1 = highest demand)
    df['Demand Rank'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    if 'looker_demand_index' in df.columns:
        df.loc[on_dinneroo_mask, 'Demand Rank'] = df.loc[on_dinneroo_mask, 'looker_demand_index'].rank(
            ascending=False, method='min', na_option='bottom'
        ).astype('Int64')
    
    # Family Score: Combine kids_happy and suitability (normalized)
    # Normalize both to 0-1 scale, then average
    df['_kids_happy_norm'] = np.nan
    df['_suitability_norm'] = np.nan
    
    if 'kids_full_and_happy_pct' in df.columns:
        # Kids happy is already 0-100%, normalize to 0-1
        df['_kids_happy_norm'] = df['kids_full_and_happy_pct'] / 100.0
    
    if 'family_suitability' in df.columns:
        # Suitability is 1-5, normalize to 0-1
        df['_suitability_norm'] = (df['family_suitability'] - 1) / 4.0
    
    # Family Score = average of normalized metrics (handling NaN)
    # For Test & Learn (no kids_happy), this will use suitability alone
    df['_family_score'] = df[['_kids_happy_norm', '_suitability_norm']].mean(axis=1, skipna=True)
    
    # Family Rank: Sort by Family Score (descending) - include ALL dishes with family_suitability
    # This allows Test & Learn dishes to be ranked by suitability alone
    has_family_score = df['_family_score'].notna()
    df['Family Rank'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    df.loc[has_family_score, 'Family Rank'] = df.loc[has_family_score, '_family_score'].rank(
        ascending=False, method='min', na_option='bottom'
    ).astype('Int64')
    
    # Balanced Score: 50% Demand + 50% Family
    # Normalize demand to 0-1 scale first
    if 'looker_demand_index' in df.columns:
        max_demand = df.loc[on_dinneroo_mask, 'looker_demand_index'].max()
        if max_demand > 0:
            df['_demand_norm'] = df['looker_demand_index'] / max_demand
        else:
            df['_demand_norm'] = 0
    else:
        df['_demand_norm'] = np.nan
    
    df['_balanced_score'] = 0.5 * df['_demand_norm'].fillna(0) + 0.5 * df['_family_score'].fillna(0)
    
    # Balanced Rank
    df['Balanced Rank'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    df.loc[on_dinneroo_mask, 'Balanced Rank'] = df.loc[on_dinneroo_mask, '_balanced_score'].rank(
        ascending=False, method='min', na_option='bottom'
    ).astype('Int64')

    # Balanced Score (incl drop-off): 40% Demand + 40% Family + 20% Drop-off requests (normalized)
    df['_dropoff_norm'] = 0.0
    if 'dropoff_requests' in df.columns:
        max_drop = df['dropoff_requests'].max()
        if max_drop and max_drop > 0:
            df['_dropoff_norm'] = df['dropoff_requests'] / max_drop
        else:
            df['_dropoff_norm'] = 0.0

    df['_balanced_incl_dropoff_score'] = (
        0.4 * df['_demand_norm'].fillna(0) +
        0.4 * df['_family_score'].fillna(0) +
        0.2 * df['_dropoff_norm'].fillna(0)
    )

    df['Balanced Rank (incl drop-off)'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    df.loc[on_dinneroo_mask, 'Balanced Rank (incl drop-off)'] = df.loc[on_dinneroo_mask, '_balanced_incl_dropoff_score'].rank(
        ascending=False, method='min', na_option='bottom'
    ).astype('Int64')
    
    # Non-Family Rank: Sort by Non-Family Satisfied % (descending)
    df['Non-Family Rank'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    if 'nonfam_satisfied_pct' in df.columns:
        df.loc[on_dinneroo_mask, 'Non-Family Rank'] = df.loc[on_dinneroo_mask, 'nonfam_satisfied_pct'].rank(
            ascending=False, method='min', na_option='bottom'
        ).astype('Int64')
    
    # Anna Rank: Based on her Demand Strength (her original prioritization)
    # This serves as the baseline for comparison
    df['Anna Rank'] = df['Demand Rank'].copy()  # Her ranking was demand-based
    
    # Calculate shifts from Anna's ranking (positive = research ranks higher than Anna)
    df['Family Shift'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    df['Non-Family Shift'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    df['Balanced Shift'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    df['Balanced Shift (incl drop-off)'] = pd.Series([pd.NA] * len(df), dtype='Int64')
    
    df.loc[on_dinneroo_mask, 'Family Shift'] = (df.loc[on_dinneroo_mask, 'Anna Rank'] - df.loc[on_dinneroo_mask, 'Family Rank']).astype('Int64')
    df.loc[on_dinneroo_mask, 'Non-Family Shift'] = (df.loc[on_dinneroo_mask, 'Anna Rank'] - df.loc[on_dinneroo_mask, 'Non-Family Rank']).astype('Int64')
    df.loc[on_dinneroo_mask, 'Balanced Shift'] = (df.loc[on_dinneroo_mask, 'Anna Rank'] - df.loc[on_dinneroo_mask, 'Balanced Rank']).astype('Int64')
    df.loc[on_dinneroo_mask, 'Balanced Shift (incl drop-off)'] = (df.loc[on_dinneroo_mask, 'Anna Rank'] - df.loc[on_dinneroo_mask, 'Balanced Rank (incl drop-off)']).astype('Int64')
    
    # Clean up temp columns
    df = df.drop(columns=[
        '_kids_happy_norm', '_suitability_norm', '_family_score',
        '_demand_norm', '_balanced_score',
        '_dropoff_norm', '_balanced_incl_dropoff_score'
    ])
    
    return df


def create_ranking_comparison(df):
    """Create Tab 1: Ranking Comparison (Main View)."""
    cols = [
        'Dish Type', 'Cuisine', 'Anna Tier', 'Validation',
        'Anna Rank',
        'Family Rank', 'Family Shift',
        'Non-Family Rank', 'Non-Family Shift', 
        'Balanced Rank', 'Balanced Shift',
        'Balanced Rank (incl drop-off)', 'Balanced Shift (incl drop-off)',
        'Research Notes'
    ]
    cols = [c for c in cols if c in df.columns]
    
    # Sort by Anna Rank for default view (her baseline)
    df_sorted = df[cols].copy()
    if 'Anna Rank' in df_sorted.columns:
        df_sorted = df_sorted.sort_values('Anna Rank', na_position='last')
    
    return df_sorted


def create_all_metrics(df):
    """Create Tab 2: All Metrics (for sorting/filtering)."""
    cols = [
        'Dish Type', 'Cuisine', 'On Dinneroo', 'Anna Tier',
        'Demand Strength', 'Consumer Preference',
        'Family Suitability (Pre-Launch)',
        'Kids Happy % (Post-Order)', 'Kids Happy Count', 'Kids Happy Base', 'Kids Happy Sample Size',
        'Non-Family Satisfied % (Post-Order)', 'Non-Family Sample Size',
        'Coverage Gap %', 'Mapping Coverage %',
        'Drop-off Requests', 'Drop-off Demand Signal',
        'Anna Rank', 
        'Family Rank', 'Family Shift',
        'Non-Family Rank', 'Non-Family Shift',
        'Balanced Rank', 'Balanced Shift',
        'Balanced Rank (incl drop-off)', 'Balanced Shift (incl drop-off)',
        'Validation', 'Confidence', 'Research Notes'
    ]
    cols = [c for c in cols if c in df.columns]
    return df[cols].copy()


def create_methodology():
    """Create Tab 3: How Rankings Work."""
    data = [
        {
            'Ranking': 'ANNA RANK (Baseline)',
            'What It Measures': 'Anna\'s original dish prioritization based on demand data',
            'Formula': 'Sort by Demand Strength (descending)',
            'Source': 'Supply Team Dish Scoring (Dec-25) - Looker data',
            'How to Read Shift': 'This is the baseline (shift = 0). Other ranks compare to this.',
            'Notes': 'Rank 1 = highest priority in Anna\'s framework.'
        },
        {
            'Ranking': 'FAMILY RANK',
            'What It Measures': 'How dishes perform for families (kids + parents)',
            'Formula': '0.5 × (Kids Happy %) + 0.5 × (Family Suitability)',
            'Source': 'Post-order survey (kids reaction) + Pre-launch survey (suitability)',
            'How to Read Shift': '+ve shift = families rate higher than Anna. -ve = families rate lower.',
            'Notes': 'E.g., Shepherd\'s Pie: Anna #17, Family #1, Shift +16 = families love it more than demand suggests.'
        },
        {
            'Ranking': 'NON-FAMILY RANK',
            'What It Measures': 'How dishes perform for couples/singles (no children)',
            'Formula': 'Sort by Non-Family Satisfied % (descending)',
            'Source': 'Post-order survey filtered to households without children (n=574)',
            'How to Read Shift': '+ve shift = non-families rate higher. -ve = non-families rate lower.',
            'Notes': 'Useful if considering pivot away from family focus. E.g., Poke: Anna #19, Non-Family #1.'
        },
        {
            'Ranking': 'BALANCED RANK',
            'What It Measures': 'Combined view: 50% demand + 50% family satisfaction',
            'Formula': '0.5 × (Demand normalized) + 0.5 × (Family Score)',
            'Source': 'Combines Anna\'s Looker data with research survey data',
            'How to Read Shift': '+ve shift = balanced view ranks higher. -ve = balanced view ranks lower.',
            'Notes': 'Middle ground between pure demand and pure family focus.'
        },
        {
            'Ranking': 'BALANCED RANK (INCL DROP-OFF)',
            'What It Measures': 'Combined view: 40% demand + 40% family + 20% drop-off requests',
            'Formula': '0.4 × (Demand normalized) + 0.4 × (Family Score) + 0.2 × (Drop-off Requests normalized)',
            'Source': 'Demand Strength + family metrics + drop-off survey open-text requests',
            'How to Read Shift': '+ve shift = balanced (incl drop-off) ranks higher. -ve = ranks lower.',
            'Notes': 'Drop-off signals are incorporated into this rank. Cuisine-level drop-off requests (e.g., “Chinese”) are summarized separately and are not forced into dish-type scoring.'
        },
        {
            'Ranking': 'SHIFT COLUMNS',
            'What It Measures': 'How much each approach differs from Anna\'s ranking',
            'Formula': 'Anna Rank - [Other Rank]. Positive = that approach ranks the dish HIGHER.',
            'Source': 'Calculated comparison',
            'How to Read Shift': '+16 means "this approach ranks the dish 16 positions higher than Anna"',
            'Notes': 'Large shifts (>5) highlight dishes where approaches meaningfully disagree.'
        }
    ]
    return pd.DataFrame(data)


def create_data_dictionary():
    """Create Tab 4: Data Dictionary with Anna's naming."""
    data = [
        {
            'Column': 'Dish Type',
            'Source': 'Supply Team Dish Scoring (Dec-25)',
            'Definition': 'High-level dish category (e.g., Katsu, Pizza, South Asian / Indian Curry)',
            'Formula/Calculation': 'Direct from source file',
            'Date': 'Dec-25'
        },
        {
            'Column': 'Cuisine',
            'Source': 'Supply Team Item Categorisation (Dec-25)',
            'Definition': 'Core 7 cuisine category (Asian, Italian, Indian, Healthy, Mexican, Middle Eastern, British)',
            'Formula/Calculation': 'Modal cuisine from item to dish mapping',
            'Date': 'Dec-25'
        },
        {
            'Column': 'Anna Tier',
            'Source': 'Supply Team Dish Scoring (Dec-25)',
            'Definition': 'Original tier: Core Driver / Preference Driver / Demand Booster / Deprioritised / Test & Learn',
            'Formula/Calculation': 'PRE-CALCULATED (not re-run) - preserved from source',
            'Date': 'Dec-25'
        },
        {
            'Column': 'Demand Strength',
            'Source': 'Supply Team Dish Scoring (Looker)',
            'Definition': 'Demand strength index (1.0 = average across all dishes)',
            'Formula/Calculation': 'PRE-CALCULATED - Indexed avg of: sales per dish, % zones rank top 3, open-text requests',
            'Date': 'Dec-25'
        },
        {
            'Column': 'Consumer Preference',
            'Source': 'Supply Team Dish Scoring (Looker + Survey)',
            'Definition': 'Preference strength index (1.0 = average across all dishes)',
            'Formula/Calculation': 'PRE-CALCULATED - Indexed avg of: Deliveroo rating, meal satisfaction, repeat intent',
            'Date': 'Dec-25'
        },
        {
            'Column': 'Family Suitability (Pre-Launch)',
            'Source': 'Pre-launch Research Survey',
            'Definition': 'Suitability score /5 based on frequency of consumption, difficulty of home prep, desire to see in-app',
            'Formula/Calculation': 'From Dish Suitability Ratings file, column D',
            'Date': 'Pre-launch'
        },
        {
            'Column': 'Kids Happy % (Post-Order)',
            'Source': 'Post-order Survey (Research)',
            'Definition': '% of mapped family surveys where at least one child reaction is "full and happy"',
            'Formula/Calculation': 'Kids Happy Count / Kids Happy Base x 100',
            'Date': 'Oct-Jan'
        },
        {
            'Column': 'Kids Happy Count',
            'Source': 'Post-order Survey (Research)',
            'Definition': 'Number of surveys where child was "full and happy"',
            'Formula/Calculation': 'Child reactions: "They ate all parts... full and happy" OR "They ate some parts... full and happy"',
            'Date': 'Oct-Jan'
        },
        {
            'Column': 'Kids Happy Base',
            'Source': 'Post-order Survey (Research)',
            'Definition': 'Number of surveys with child reaction data (eligible base)',
            'Formula/Calculation': 'Family survey = has children in household OR child reaction column populated',
            'Date': 'Oct-Jan'
        },
        {
            'Column': 'Coverage Gap %',
            'Source': 'Supply Team Dish Coverage (Dec-25)',
            'Definition': '% of active zones where dish is NOT available',
            'Formula/Calculation': 'From Current Dish Coverage file',
            'Date': 'Dec-25'
        },
        {
            'Column': 'Demand Rank',
            'Source': 'Calculated (Research)',
            'Definition': 'Rank 1-24 if sorted by Demand Strength (descending)',
            'Formula/Calculation': 'RANK(Demand Strength, descending). Rank 1 = highest demand.',
            'Date': '-'
        },
        {
            'Column': 'Family Rank',
            'Source': 'Calculated (Research)',
            'Definition': 'Rank 1-24 if sorted by Family Score (descending)',
            'Formula/Calculation': 'Family Score = 0.5 x (Kids Happy % / 100) + 0.5 x ((Suitability - 1) / 4)',
            'Date': '-'
        },
        {
            'Column': 'Balanced Rank',
            'Source': 'Calculated (Research)',
            'Definition': 'Rank 1-24 if sorted by Balanced Score (descending)',
            'Formula/Calculation': 'Balanced = 0.5 x Demand (normalized) + 0.5 x Family Score',
            'Date': '-'
        },
        {
            'Column': 'Drop-off Requests',
            'Source': 'Drop-off Survey (Open Text)',
            'Definition': 'Count of drop-off responses that explicitly mention this dish type (mapped via keyword rules)',
            'Formula/Calculation': f'Map open-text in \"{DROPOFF_REQUESTS_SOURCE_COL}\" to dish types; count mentions (each dish counted once per response).',
            'Date': 'Oct-Jan'
        },
        {
            'Column': 'Drop-off Demand Signal',
            'Source': 'Drop-off Survey (Open Text)',
            'Definition': 'Categorical strength label based on Drop-off Requests count',
            'Formula/Calculation': 'None=0; Low=1-2; Medium=3-5; High=6+',
            'Date': 'Oct-Jan'
        },
        {
            'Column': 'Balanced Rank (incl drop-off)',
            'Source': 'Calculated (Research)',
            'Definition': 'Rank 1-24 if sorted by Balanced Score that includes drop-off demand (dish-level)',
            'Formula/Calculation': 'Balanced (incl drop-off) = 0.4 x Demand (normalized) + 0.4 x Family Score + 0.2 x Drop-off Requests (normalized)',
            'Date': '-'
        },
        {
            'Column': 'Balanced Shift (incl drop-off)',
            'Source': 'Calculated (Research)',
            'Definition': 'Difference vs Anna baseline for the drop-off-inclusive balanced rank',
            'Formula/Calculation': 'Anna Rank - Balanced Rank (incl drop-off)',
            'Date': '-'
        },
        {
            'Column': 'Validation',
            'Source': 'Research assessment',
            'Definition': 'Confirmed = research supports tier / Opportunity = worth discussing',
            'Formula/Calculation': 'Rubric: 2+ signals align = Confirmed; nuance found = Opportunity',
            'Date': '-'
        },
        {
            'Column': 'Confidence',
            'Source': 'Research assessment',
            'Definition': 'HIGH / MED / LOW based on sample size',
            'Formula/Calculation': 'HIGH (n >= 30), MED (20-29), LOW (<20)',
            'Date': '-'
        }
    ]
    return pd.DataFrame(data)


def load_mapping_qa():
    """Load Tab 5: Mapping QA."""
    qa_path = ANALYSIS_DIR / "dish_survey_mapping_qa.csv"
    if qa_path.exists():
        return pd.read_csv(qa_path)
    return pd.DataFrame()


def main():
    """Generate the Excel workbook."""
    print("=" * 60)
    print("GENERATING DISH VALIDATION REPORT")
    print("=" * 60)
    
    # Load working file
    working_path = ANALYSIS_DIR / "dish_validation_working.csv"
    df = pd.read_csv(working_path)
    print(f"Loaded {len(df)} dishes")
    
    # Fix Unknown tier
    print("Fixing 'Unknown' tier display...")
    df = fix_unknown_tier(df)
    
    # Load non-family satisfaction data
    print("Loading non-family satisfaction data...")
    df = load_nonfamily_satisfaction(df)

    # Load drop-off request data (dish-type mapping)
    print("Loading drop-off request data...")
    df = load_dropoff_requests(df)
    
    # Calculate rankings
    print("Calculating rankings (Demand, Family, Non-Family, Balanced)...")
    df = calculate_rankings(df)
    
    # Rename columns to Anna's terminology
    print("Renaming columns to Anna's terminology...")
    df = df.rename(columns=COLUMN_RENAME)
    
    # Create tabs
    print("Creating workbook tabs...")
    df_ranking = create_ranking_comparison(df)
    df_all = create_all_metrics(df)
    df_methodology = create_methodology()
    df_dict = create_data_dictionary()
    df_qa = load_mapping_qa()
    df_dropoff_cuisines = load_dropoff_cuisine_requests()
    
    # Write to Excel
    output_path = DELIVERABLES_DIR / "dish_validation_report.xlsx"
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_ranking.to_excel(writer, sheet_name='Ranking Comparison', index=False)
        df_all.to_excel(writer, sheet_name='All Metrics', index=False)
        df_methodology.to_excel(writer, sheet_name='How Rankings Work', index=False)
        df_dict.to_excel(writer, sheet_name='Data Dictionary', index=False)
        df_qa.to_excel(writer, sheet_name='Mapping QA', index=False)
        if len(df_dropoff_cuisines) > 0:
            df_dropoff_cuisines.to_excel(writer, sheet_name='Drop-off Cuisine Requests', index=False)
    
    print(f"\nSaved Excel workbook to: {output_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("WORKBOOK CONTENTS")
    print("=" * 60)
    print(f"  Tab 1 - Ranking Comparison: {len(df_ranking)} rows")
    print(f"  Tab 2 - All Metrics: {len(df_all)} rows")
    print(f"  Tab 3 - How Rankings Work: {len(df_methodology)} rows")
    print(f"  Tab 4 - Data Dictionary: {len(df_dict)} rows")
    print(f"  Tab 5 - Mapping QA: {len(df_qa)} rows")
    if len(df_dropoff_cuisines) > 0:
        print(f"  Tab 6 - Drop-off Cuisine Requests: {len(df_dropoff_cuisines)} rows")
    
    # Show ranking examples
    print("\n" + "=" * 60)
    print("RANKING PREVIEW (Top 5 by Balanced Rank)")
    print("=" * 60)
    preview_cols = ['Dish Type', 'Anna Tier', 'Demand Rank', 'Family Rank', 'Non-Family Rank', 'Balanced Rank', 'Balanced Rank (incl drop-off)']
    preview_cols = [c for c in preview_cols if c in df_ranking.columns]
    print(df_ranking[preview_cols].head(5).to_string(index=False))
    
    return output_path


if __name__ == "__main__":
    main()
