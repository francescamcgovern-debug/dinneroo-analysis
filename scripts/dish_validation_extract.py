#!/usr/bin/env python3
"""
Dish Validation Data Extraction
================================
Extracts dish metrics from Anna's source files into a clean working file.

Sources:
- Dish Analysis Dec-25 - Dish Scoring.csv (demand, preference, tier, coverage)
- Dish Analysis Dec-25 - Dish Suitability Ratings.csv (family suitability)
- Dish Analysis Dec-25 - Item Categorisation.csv (cuisine assignment)

Output:
- DATA/3_ANALYSIS/dish_validation_working.csv
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
SOURCE_DIR = BASE_DIR / "DATA/1_SOURCE/anna_slides"
OUTPUT_DIR = BASE_DIR / "DATA/3_ANALYSIS"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_dish_scores():
    """Extract demand, preference, and coverage from Dish Scoring CSV."""
    print("Extracting dish scores from Dish Scoring CSV...")
    
    # Read the raw CSV
    df_raw = pd.read_csv(SOURCE_DIR / "Dish Analysis Dec-25 - Dish Scoring.csv", header=None)
    
    # Column indices (0-indexed):
    # 2: dish_name
    # 10: suitability rating
    # 12: demand strength
    # 13: consumer preference
    # 17: coverage gap %
    
    # Extract Dinneroo dishes (rows 7-29, 0-indexed: 6-28)
    dinneroo_dishes = []
    for idx in range(6, 29):  # rows 7-29
        row = df_raw.iloc[idx]
        dish_name = str(row[2]).strip() if pd.notna(row[2]) else None
        if dish_name and dish_name not in ['', 'nan']:
            demand = row[12] if pd.notna(row[12]) else None
            preference = row[13] if pd.notna(row[13]) else None
            coverage_gap = row[17] if pd.notna(row[17]) else None
            suitability = row[10] if pd.notna(row[10]) else None
            
            # Clean coverage gap (remove %)
            if coverage_gap and isinstance(coverage_gap, str):
                coverage_gap = coverage_gap.replace('%', '')
                try:
                    coverage_gap = float(coverage_gap) / 100
                except:
                    coverage_gap = None
            
            # Convert demand/preference to float if string
            try:
                demand = float(demand) if demand else None
            except:
                demand = None
            try:
                preference = float(preference) if preference else None
            except:
                preference = None
            
            dinneroo_dishes.append({
                'dish_type': dish_name,
                'on_dinneroo': True,
                'looker_demand_index': demand,
                'looker_preference_index': preference,
                'coverage_gap_pct': coverage_gap,
                'family_suitability_raw': suitability
            })
    
    # Extract not-on-Dinneroo candidates (rows 30-40, 0-indexed: 29-39)
    not_on_dinneroo = []
    for idx in range(29, 40):
        row = df_raw.iloc[idx]
        dish_name = str(row[2]).strip() if pd.notna(row[2]) else None
        if dish_name and dish_name not in ['', 'nan']:
            suitability = row[10] if pd.notna(row[10]) else None
            coverage_gap = row[17] if pd.notna(row[17]) else None
            
            # Clean coverage gap
            if coverage_gap and isinstance(coverage_gap, str):
                coverage_gap = coverage_gap.replace('%', '')
                try:
                    coverage_gap = float(coverage_gap) / 100
                except:
                    coverage_gap = None
            
            not_on_dinneroo.append({
                'dish_type': dish_name,
                'on_dinneroo': False,
                'looker_demand_index': None,  # N/A for not-on-Dinneroo
                'looker_preference_index': None,  # N/A
                'coverage_gap_pct': coverage_gap,
                'family_suitability_raw': suitability
            })
    
    print(f"  Extracted {len(dinneroo_dishes)} Dinneroo dishes")
    print(f"  Extracted {len(not_on_dinneroo)} not-on-Dinneroo candidates")
    return dinneroo_dishes + not_on_dinneroo

def extract_tier_classifications():
    """Extract tier classifications from Dish Scoring CSV (rows 89-112)."""
    print("Extracting tier classifications...")
    
    df_raw = pd.read_csv(SOURCE_DIR / "Dish Analysis Dec-25 - Dish Scoring.csv", header=None)
    
    tier_map = {}
    current_tier = None
    
    # Rows 88-112 (0-indexed: 87-111)
    for idx in range(87, 113):
        row = df_raw.iloc[idx]
        
        # Check if this row defines a tier
        tier_cell = str(row[1]).strip() if pd.notna(row[1]) else ''
        if tier_cell in ['Core Drivers', 'Preference Drivers', 'Demand Boosters', 'Deprioritised']:
            current_tier = tier_cell
        
        # Get dish name from column 2
        dish_name = str(row[2]).strip() if pd.notna(row[2]) else None
        if dish_name and dish_name not in ['', 'nan', 'Dish Coverage and Next Steps']:
            if current_tier:
                tier_map[dish_name] = current_tier
    
    return tier_map

def extract_suitability_scores():
    """Extract family suitability scores from Suitability Ratings CSV."""
    print("Extracting suitability scores...")
    
    df_raw = pd.read_csv(SOURCE_DIR / "Dish Analysis Dec-25 - Dish Suitability Ratings.csv", header=None)
    
    suitability_map = {}
    
    # Rows with suitability scores start around row 8, iterate up to file length
    max_row = min(len(df_raw), 50)
    for idx in range(7, max_row):
        row = df_raw.iloc[idx]
        dish_name = str(row[2]).strip() if pd.notna(row[2]) else None
        suitability = row[3] if pd.notna(row[3]) else None
        
        if dish_name and suitability and dish_name not in ['', 'nan']:
            try:
                suitability_map[dish_name] = float(suitability)
            except:
                pass
    
    print(f"  Found {len(suitability_map)} suitability scores")
    return suitability_map

def extract_cuisine_assignments():
    """Extract cuisine assignments from Item Categorisation CSV."""
    print("Extracting cuisine assignments...")
    
    df = pd.read_csv(SOURCE_DIR / "Dish Analysis Dec-25 - Item Categorisation.csv", header=None, skiprows=8)
    
    # Column D (index 3) is Cuisine, Column E (index 4) is High-Level Dish
    cuisine_counts = {}
    
    for idx, row in df.iterrows():
        try:
            include = row[0]
            cuisine = str(row[3]).strip() if pd.notna(row[3]) else None
            dish_type = str(row[4]).strip() if pd.notna(row[4]) else None
            
            if include == 1 and cuisine and dish_type and dish_type not in ['', 'nan']:
                if dish_type not in cuisine_counts:
                    cuisine_counts[dish_type] = {}
                if cuisine not in cuisine_counts[dish_type]:
                    cuisine_counts[dish_type][cuisine] = 0
                cuisine_counts[dish_type][cuisine] += 1
        except Exception as e:
            continue
    
    # Get modal cuisine for each dish type
    cuisine_map = {}
    for dish_type, cuisines in cuisine_counts.items():
        modal_cuisine = max(cuisines, key=cuisines.get)
        cuisine_map[dish_type] = modal_cuisine
    
    print(f"  Found cuisine assignments for {len(cuisine_map)} dish types")
    return cuisine_map

def build_working_file():
    """Build the consolidated working file."""
    
    # Extract all data
    dishes = extract_dish_scores()
    tiers = extract_tier_classifications()
    suitability = extract_suitability_scores()
    cuisines = extract_cuisine_assignments()
    
    # Map dish names for suitability lookup (handle naming variations)
    suitability_lookup = {
        'South Asian / Indian Curry': suitability.get("Curry & Rice (e.g. Tikka, korma, butter chicken)", None),
        'East Asian Curry': suitability.get("Thai Curry (e.g. Red, Green, Massaman)", None),
        'Katsu': suitability.get("Katsu Curry", None),
        'Fajitas': suitability.get("Fajitas / Burritos", None),
        'Shepherd\'s Pie': suitability.get("Cottage/Shepherd's/Fish Pie", None),
        'Chilli': suitability.get("Chilli & Rice (e.g. Con Carne, 3-Bean)", None),
        'Tacos': suitability.get("Tacos / Enchiladas / Quesadillas", None),
        'Noodles': suitability.get("Stir fry / Noodles", None),
        'Pasta': suitability.get("Baked Pasta (e.g. Chicken, Tuna, Tomato)", None),
        'Rice Bowl': suitability.get("Rice bowl / fried rice", None),
        'Protein & Veg': suitability.get("Meat & vegetables (e.g. Roast, Grilled, Breaded)", None),
        'Pho': suitability.get("Ramen", None),  # Closest match
        'Pizza': suitability.get("Pizza", None),
        'Lasagne': suitability.get("Lasagne", None),
        'Fish & chips': suitability.get("Fish & chips", None),
        'Sausage & mash': suitability.get("Sausage & mash", None),
        'Jacket potato': suitability.get("Jacket potato", None),
        'Casserole / Stew': suitability.get("Casserole / Stew", None),
        'Risotto': suitability.get("Risotto", None),
        'Tagine': suitability.get("Tagine", None),
        'Paella': suitability.get("Paella", None),
        'Pastry Pie': suitability.get("Pastry Pie (e.g. Chicken, Steak, Beef, Veggie)", None),
        'Roast': suitability.get("Meat & vegetables (e.g. Roast, Grilled, Breaded)", None),
    }
    
    # Build consolidated data
    consolidated = []
    for dish in dishes:
        dish_type = dish['dish_type']
        
        # Get tier
        current_tier = tiers.get(dish_type, 'Test & Learn' if not dish['on_dinneroo'] else 'Unknown')
        
        # Get cuisine
        cuisine = cuisines.get(dish_type, 'Unknown')
        
        # Get suitability (prefer lookup, then raw value)
        family_suit = suitability_lookup.get(dish_type)
        if family_suit is None:
            family_suit = dish.get('family_suitability_raw')
            if family_suit and isinstance(family_suit, str):
                try:
                    family_suit = float(family_suit)
                except:
                    family_suit = None
        
        consolidated.append({
            'dish_type': dish_type,
            'cuisine': cuisine,
            'on_dinneroo': dish['on_dinneroo'],
            'current_tier': current_tier,
            'looker_demand_index': dish['looker_demand_index'],
            'looker_preference_index': dish['looker_preference_index'],
            'family_suitability': family_suit,
            'coverage_gap_pct': dish['coverage_gap_pct'],
            # Placeholder columns for research data (to be filled by next step)
            'kids_full_and_happy_pct': None,
            'kids_full_and_happy_numerator': None,
            'kids_full_and_happy_denominator': None,
            'mapping_coverage_pct': None,
            'validation_status': None,
            'validation_confidence': None,
            'research_notes': None
        })
    
    # Create DataFrame
    df = pd.DataFrame(consolidated)
    
    # Save to working file
    output_path = OUTPUT_DIR / "dish_validation_working.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved working file to: {output_path}")
    print(f"Total dishes: {len(df)}")
    print(f"  - On Dinneroo: {df['on_dinneroo'].sum()}")
    print(f"  - Not on Dinneroo: {(~df['on_dinneroo']).sum()}")
    
    # Also save extraction metadata
    metadata = {
        'extraction_timestamp': datetime.now().isoformat(),
        'source_files': [
            'Dish Analysis Dec-25 - Dish Scoring.csv',
            'Dish Analysis Dec-25 - Dish Suitability Ratings.csv',
            'Dish Analysis Dec-25 - Item Categorisation.csv'
        ],
        'dish_count': len(df),
        'dinneroo_count': int(df['on_dinneroo'].sum()),
        'not_dinneroo_count': int((~df['on_dinneroo']).sum()),
        'tiers_found': list(df['current_tier'].unique()),
        'cuisines_found': list(df['cuisine'].unique())
    }
    
    metadata_path = OUTPUT_DIR / "dish_validation_extraction_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to: {metadata_path}")
    
    return df

if __name__ == "__main__":
    df = build_working_file()
    print("\n=== Extraction Summary ===")
    print(df[['dish_type', 'cuisine', 'current_tier', 'looker_demand_index', 'looker_preference_index', 'family_suitability']].to_string())
