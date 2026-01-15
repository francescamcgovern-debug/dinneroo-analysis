#!/usr/bin/env python3
"""
Dish Research Enrichment
=========================
Adds research data (kids_full_and_happy metrics) to the dish validation working file.

Uses Anna's survey→dish mapping and post-order survey child reaction data.

Outputs:
- Updated dish_validation_working.csv with research metrics
- dish_survey_mapping_qa.csv (mapping QA)
- kids_full_and_happy_row_level.csv (traceability audit)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import re

# Paths
BASE_DIR = Path(__file__).parent.parent
SOURCE_DIR = BASE_DIR / "DATA/1_SOURCE"
ANNA_DIR = SOURCE_DIR / "anna_slides"
SURVEY_DIR = SOURCE_DIR / "surveys"
ANALYSIS_DIR = BASE_DIR / "DATA/3_ANALYSIS"

# Full & happy child reaction categories (exact strings from survey)
FULL_AND_HAPPY_CATEGORIES = [
    "They ate all parts of the dish and were full and happy",
    "They ate some parts of the dish, but were full and happy"
]

def load_anna_mapping():
    """Load Anna's dish→dish_type mapping from Survey_ Dish Matching.csv."""
    print("Loading Anna's survey→dish mapping...")
    
    df = pd.read_csv(ANNA_DIR / "Dish Analysis Dec-25 - Survey_ Dish Matching.csv", header=None)
    
    # Columns: 2 = "Menu Items Simplified" (survey response text), 6 = "UPDATED DISH" (dish_type)
    mapping = {}
    for idx in range(5, len(df)):  # Skip header rows
        row = df.iloc[idx]
        survey_text = str(row[2]).strip().lower() if pd.notna(row[2]) else None
        dish_type = str(row[6]).strip() if pd.notna(row[6]) else None
        
        if survey_text and dish_type and survey_text not in ['', 'nan'] and dish_type not in ['', 'nan']:
            mapping[survey_text] = dish_type
    
    print(f"  Loaded {len(mapping)} survey→dish mappings")
    return mapping

def build_keyword_mapping():
    """Build fallback keyword→dish_type mapping for unmapped responses."""
    return {
        # Asian
        'katsu': 'Katsu',
        'pad thai': 'Noodles',
        'pho': 'Pho',
        'noodle': 'Noodles',
        'ramen': 'Pho',
        'sushi': 'Sushi',
        'rice bowl': 'Rice Bowl',
        'fried rice': 'Fried Rice',
        'teriyaki': 'Rice Bowl',
        # Indian
        'curry': 'South Asian / Indian Curry',
        'biryani': 'Biryani',
        'tikka': 'South Asian / Indian Curry',
        'korma': 'South Asian / Indian Curry',
        'masala': 'South Asian / Indian Curry',
        'ruby': 'South Asian / Indian Curry',
        # Italian
        'pizza': 'Pizza',
        'pasta': 'Pasta',
        'lasagne': 'Lasagne',
        'lasagna': 'Lasagne',
        # Mexican
        'fajita': 'Fajitas',
        'burrito': 'Burrito / Burrito Bowl',
        'taco': 'Tacos',
        'quesadilla': 'Quesadilla',
        'chilli': 'Chilli',
        'chili': 'Chilli',
        # Other
        'shepherd': "Shepherd's Pie",
        'shawarma': 'Shawarma',
        'grain bowl': 'Grain Bowl',
        'salad': 'Grain Bowl',
        'poke': 'Poke',
    }

def map_dish_text_to_type(dish_text, anna_mapping, keyword_mapping):
    """Map a survey dish text response to a dish_type."""
    if not dish_text or pd.isna(dish_text):
        return None, None
    
    dish_text_clean = str(dish_text).strip().lower()
    
    # Skip "don't remember" or empty
    if dish_text_clean in ['don\'t remember', 'dont remember', '', 'nan', 'n/a']:
        return None, 'excluded'
    
    # Try Anna's mapping first
    if dish_text_clean in anna_mapping:
        return anna_mapping[dish_text_clean], 'anna_map'
    
    # Try keyword matching
    for keyword, dish_type in keyword_mapping.items():
        if keyword in dish_text_clean:
            return dish_type, 'keyword'
    
    # Unmapped
    return None, 'unmapped'

def is_family_survey(row, child_cols):
    """Check if a survey response is from a family with children."""
    # Check if "My child/children" is selected in household
    has_children_household = pd.notna(row.get('My child/children:Who currently lives in your home with you? (Please select all that apply)'))
    
    # Check if any child reaction column is populated
    has_child_reaction = any(pd.notna(row.get(col)) for col in child_cols if col in row.index)
    
    return has_children_household or has_child_reaction

def is_full_and_happy(row, child_cols):
    """Check if at least one child reaction indicates full and happy."""
    for col in child_cols:
        if col in row.index:
            reaction = row.get(col)
            if pd.notna(reaction) and reaction in FULL_AND_HAPPY_CATEGORIES:
                return True
    return False

def get_child_reaction_values(row, child_cols):
    """Get all non-null child reaction values as a list."""
    reactions = []
    for col in child_cols:
        if col in row.index:
            reaction = row.get(col)
            if pd.notna(reaction):
                reactions.append(str(reaction))
    return reactions

def process_surveys():
    """Process post-order surveys to extract kids_full_and_happy metrics."""
    print("\nProcessing post-order surveys...")
    
    # Load survey data
    survey_path = SURVEY_DIR / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    df_survey = pd.read_csv(survey_path)
    print(f"  Loaded {len(df_survey)} survey responses")
    
    # Identify child reaction columns
    child_cols = [col for col in df_survey.columns if col.startswith('Child ') and 'react' in col.lower()]
    print(f"  Found {len(child_cols)} child reaction columns: {child_cols[:3]}...")
    
    # Load mappings
    anna_mapping = load_anna_mapping()
    keyword_mapping = build_keyword_mapping()
    
    # Dish text column
    dish_col = 'What dish(es) did you order?'
    
    # Process each row
    row_level_data = []
    
    for idx, row in df_survey.iterrows():
        response_id = row.get('Response ID', idx)
        dish_text = row.get(dish_col)
        
        # Map dish text to dish_type
        dish_type, mapping_method = map_dish_text_to_type(dish_text, anna_mapping, keyword_mapping)
        
        # Check if family survey
        is_family = is_family_survey(row, child_cols)
        
        # Check if any child reaction present (for denominator)
        child_reactions = get_child_reaction_values(row, child_cols)
        has_child_reaction = len(child_reactions) > 0
        
        # Check full and happy
        full_happy = is_full_and_happy(row, child_cols)
        
        # Determine if included in denominator
        # Denominator = mapped family survey with at least one child reaction
        included_in_denom = dish_type is not None and is_family and has_child_reaction
        
        row_level_data.append({
            'response_id': response_id,
            'source_file': 'POST_ORDER_SURVEY-CONSOLIDATED.csv',
            'dish_text_raw': dish_text,
            'mapped_dish_type': dish_type,
            'mapping_method': mapping_method,
            'is_family_survey': is_family,
            'child_reaction_values': '|'.join(child_reactions) if child_reactions else None,
            'is_full_and_happy': 1 if full_happy else 0,
            'included_in_denominator': 1 if included_in_denom else 0
        })
    
    df_row_level = pd.DataFrame(row_level_data)
    
    # Save row-level audit
    row_level_path = ANALYSIS_DIR / "kids_full_and_happy_row_level.csv"
    df_row_level.to_csv(row_level_path, index=False)
    print(f"\n  Saved row-level audit to: {row_level_path}")
    
    return df_row_level

def calculate_dish_metrics(df_row_level):
    """Calculate kids_full_and_happy metrics per dish_type."""
    print("\nCalculating dish-level metrics...")
    
    # Filter to rows included in denominator
    df_denom = df_row_level[df_row_level['included_in_denominator'] == 1]
    
    # Group by dish_type
    dish_metrics = []
    for dish_type in df_denom['mapped_dish_type'].unique():
        df_dish = df_denom[df_denom['mapped_dish_type'] == dish_type]
        
        denominator = len(df_dish)
        numerator = df_dish['is_full_and_happy'].sum()
        pct = (numerator / denominator * 100) if denominator > 0 else None
        
        dish_metrics.append({
            'dish_type': dish_type,
            'kids_full_and_happy_numerator': int(numerator),
            'kids_full_and_happy_denominator': int(denominator),
            'kids_full_and_happy_n': int(denominator),
            'kids_full_and_happy_pct': round(pct, 1) if pct else None
        })
    
    df_metrics = pd.DataFrame(dish_metrics)
    print(f"  Calculated metrics for {len(df_metrics)} dish types")
    
    return df_metrics

def calculate_mapping_qa(df_row_level):
    """Calculate mapping QA metrics."""
    print("\nCalculating mapping QA metrics...")
    
    qa_data = []
    
    # Overall stats
    total_rows = len(df_row_level)
    mapped_rows = df_row_level['mapped_dish_type'].notna().sum()
    unmapped_rows = total_rows - mapped_rows
    overall_coverage = (mapped_rows / total_rows * 100) if total_rows > 0 else 0
    
    # Get top unmapped strings
    unmapped_df = df_row_level[df_row_level['mapping_method'] == 'unmapped']
    top_unmapped = unmapped_df['dish_text_raw'].value_counts().head(20).to_dict()
    
    # Per-dish stats
    for dish_type in df_row_level['mapped_dish_type'].dropna().unique():
        df_dish = df_row_level[df_row_level['mapped_dish_type'] == dish_type]
        
        # Count by mapping method
        anna_count = (df_dish['mapping_method'] == 'anna_map').sum()
        keyword_count = (df_dish['mapping_method'] == 'keyword').sum()
        
        qa_data.append({
            'dish_type': dish_type,
            'mapped_rows': len(df_dish),
            'anna_map_rows': int(anna_count),
            'keyword_rows': int(keyword_count),
            'unmapped_rows': 0,  # By definition, these are mapped
            'mapping_coverage_pct': 100.0,  # Within dish, all are mapped
            'notes': ''
        })
    
    df_qa = pd.DataFrame(qa_data)
    
    # Add overall summary row
    summary_row = {
        'dish_type': '_OVERALL_',
        'mapped_rows': int(mapped_rows),
        'anna_map_rows': int((df_row_level['mapping_method'] == 'anna_map').sum()),
        'keyword_rows': int((df_row_level['mapping_method'] == 'keyword').sum()),
        'unmapped_rows': int(unmapped_rows),
        'mapping_coverage_pct': round(overall_coverage, 1),
        'notes': f"Top unmapped: {list(top_unmapped.keys())[:5]}"
    }
    df_qa = pd.concat([pd.DataFrame([summary_row]), df_qa], ignore_index=True)
    
    # Save QA
    qa_path = ANALYSIS_DIR / "dish_survey_mapping_qa.csv"
    df_qa.to_csv(qa_path, index=False)
    print(f"  Saved mapping QA to: {qa_path}")
    print(f"  Overall mapping coverage: {overall_coverage:.1f}%")
    
    return df_qa, overall_coverage

def assign_confidence(row):
    """Assign confidence level based on sample size and mapping coverage."""
    n = row.get('kids_full_and_happy_n', 0)
    mapping_cov = row.get('mapping_coverage_pct', 0)
    
    if pd.isna(n) or n == 0:
        return 'N/A'
    
    n = int(n)
    
    if n >= 30:
        return 'HIGH'
    elif n >= 20:
        return 'MED'
    else:
        return 'LOW'

def update_working_file(df_metrics, df_qa):
    """Update the dish validation working file with research metrics."""
    print("\nUpdating working file with research metrics...")
    
    # Load current working file
    working_path = ANALYSIS_DIR / "dish_validation_working.csv"
    df_working = pd.read_csv(working_path)
    
    # Merge metrics
    df_working = df_working.merge(
        df_metrics[['dish_type', 'kids_full_and_happy_numerator', 'kids_full_and_happy_denominator', 
                    'kids_full_and_happy_n', 'kids_full_and_happy_pct']],
        on='dish_type',
        how='left',
        suffixes=('_old', '')
    )
    
    # Drop old columns if they exist
    for col in ['kids_full_and_happy_pct_old', 'kids_full_and_happy_numerator_old', 
                'kids_full_and_happy_denominator_old', 'kids_full_and_happy_n_old']:
        if col in df_working.columns:
            df_working = df_working.drop(columns=[col])
    
    # Add mapping coverage per dish
    df_qa_dish = df_qa[df_qa['dish_type'] != '_OVERALL_'][['dish_type', 'mapping_coverage_pct', 'mapped_rows']]
    df_working = df_working.merge(df_qa_dish, on='dish_type', how='left', suffixes=('_old', ''))
    
    # Rename and clean
    if 'mapping_coverage_pct_old' in df_working.columns:
        df_working = df_working.drop(columns=['mapping_coverage_pct_old'])
    
    # Assign confidence
    df_working['validation_confidence'] = df_working.apply(assign_confidence, axis=1)
    
    # For not-on-Dinneroo dishes, set kids metrics to N/A
    df_working.loc[df_working['on_dinneroo'] == False, 'kids_full_and_happy_pct'] = None
    df_working.loc[df_working['on_dinneroo'] == False, 'kids_full_and_happy_numerator'] = None
    df_working.loc[df_working['on_dinneroo'] == False, 'kids_full_and_happy_denominator'] = None
    df_working.loc[df_working['on_dinneroo'] == False, 'kids_full_and_happy_n'] = None
    df_working.loc[df_working['on_dinneroo'] == False, 'validation_confidence'] = 'N/A (not on Dinneroo)'
    
    # Save updated working file
    df_working.to_csv(working_path, index=False)
    print(f"  Updated working file: {working_path}")
    
    return df_working

def main():
    """Main execution."""
    print("=" * 60)
    print("DISH RESEARCH ENRICHMENT")
    print("=" * 60)
    
    # Process surveys
    df_row_level = process_surveys()
    
    # Calculate metrics
    df_metrics = calculate_dish_metrics(df_row_level)
    
    # Calculate QA
    df_qa, overall_coverage = calculate_mapping_qa(df_row_level)
    
    # Update working file
    df_working = update_working_file(df_metrics, df_qa)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total survey responses processed: {len(df_row_level)}")
    print(f"Responses included in kids metrics: {df_row_level['included_in_denominator'].sum()}")
    print(f"Overall mapping coverage: {overall_coverage:.1f}%")
    print(f"\nDish metrics calculated for {len(df_metrics)} dish types:")
    print(df_metrics[['dish_type', 'kids_full_and_happy_pct', 'kids_full_and_happy_n']].to_string())
    
    return df_working

if __name__ == "__main__":
    main()
