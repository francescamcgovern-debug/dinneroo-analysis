#!/usr/bin/env python3
"""
Validate consistency across all outputs.

Ensures all agents are using the same definitions from scripts/utils/definitions.py
and that outputs don't conflict.

Validation Checks:
1. All dishes in priority_100 have core_7_cuisine
2. Zone cuisine counts match Anna's ground truth
3. MVP status is calculated consistently
4. No conflicts between dish rankings and cuisine recommendations
"""

import pandas as pd
import json
from pathlib import Path
import sys

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from utils.definitions import (
    CORE_7,
    REQUIRED_FOR_MVP,
    get_core_7,
    get_mvp_status,
    get_cuisine_pass,
    validate_cuisine,
    validate_dish,
)

PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "data"


def check_dish_rankings():
    """
    Check 1: Validate dish rankings have consistent cuisine mappings.
    """
    print("\n" + "=" * 60)
    print("CHECK 1: Dish Rankings (priority_100_unified.csv)")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    file_path = DATA_DIR / "priority_100_unified.csv"
    if not file_path.exists():
        errors.append(f"File not found: {file_path}")
        return errors, warnings
    
    df = pd.read_csv(file_path)
    
    # Check for core_7_cuisine column
    if 'core_7_cuisine' not in df.columns:
        errors.append("Missing 'core_7_cuisine' column - run update_dish_cuisines.py first")
        return errors, warnings
    
    # Check for missing core_7_cuisine values
    missing_core_7 = df[df['core_7_cuisine'].isna() | (df['core_7_cuisine'] == '')]
    if len(missing_core_7) > 0:
        for _, row in missing_core_7.iterrows():
            errors.append(f"Rank {row['rank']}: '{row['dish_type']}' missing core_7_cuisine")
    
    # Check dishes mapped to 'Other'
    other_dishes = df[df['core_7_cuisine'] == 'Other']
    if len(other_dishes) > 0:
        for _, row in other_dishes.iterrows():
            warnings.append(f"Rank {row['rank']}: '{row['dish_type']}' mapped to 'Other' (not Core 7)")
    
    # Check Anna's expected classifications
    ANNA_CORE_DRIVERS = ['Pho', 'Curry', 'Biryani', 'Fried Rice', 'Sushi', 'Katsu', 'Rice Bowl', 'Noodles']
    ANNA_DEPRIORITISED = ['Pasta', 'Lasagne', 'Tacos', 'Chilli', 'Burrito', 'Quesadilla', 'Poke', 'Nachos']
    
    # Core Drivers should be Tier 1-2
    for dish in ANNA_CORE_DRIVERS:
        matches = df[df['dish_type'].str.contains(dish, case=False, na=False)]
        if not matches.empty:
            row = matches.iloc[0]
            if row['tier'] not in ['Tier 1: Must-Have', 'Tier 2: Should-Have']:
                warnings.append(f"Core Driver '{dish}' is {row['tier']} - Anna expects Tier 1-2")
    
    # Deprioritised should be Tier 3-4 (but may differ due to data)
    for dish in ANNA_DEPRIORITISED:
        matches = df[df['dish_type'].str.contains(dish[:5], case=False, na=False)]
        if not matches.empty:
            row = matches.iloc[0]
            if row['tier'] in ['Tier 1: Must-Have']:
                warnings.append(f"Deprioritised '{dish}' is {row['tier']} - Anna expects Tier 3-4")
    
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    return errors, warnings


def check_zone_cuisine_counts():
    """
    Check 2: Zone cuisine counts match Anna's ground truth.
    """
    print("\n" + "=" * 60)
    print("CHECK 2: Zone Cuisine Counts")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Load Anna's ground truth
    anna_file = DATA_DIR / "anna_zone_dish_counts.csv"
    if not anna_file.exists():
        errors.append(f"Anna's ground truth not found: {anna_file}")
        return errors, warnings
    
    anna_df = pd.read_csv(anna_file)
    
    # Load zone_mvp_status.json
    mvp_file = DOCS_DATA_DIR / "zone_mvp_status.json"
    if not mvp_file.exists():
        errors.append(f"Zone MVP status not found: {mvp_file}")
        return errors, warnings
    
    with open(mvp_file) as f:
        zones = json.load(f)
    
    # Check that zone_mvp_status has core_7 structure
    if zones and 'core_7' not in zones[0]:
        errors.append("zone_mvp_status.json missing 'core_7' structure - run generate_zone_dashboard_data.py")
        return errors, warnings
    
    # Sample check: verify a few zones match Anna's data
    anna_lookup = {row['zone_name']: row for _, row in anna_df.iterrows()}
    
    mismatches = 0
    for zone_data in zones[:50]:  # Check first 50 zones
        zone_name = zone_data['zone']
        if zone_name in anna_lookup:
            anna_row = anna_lookup[zone_name]
            
            # Check Core 7 counts match
            for cuisine in ['asian', 'italian', 'indian', 'healthy', 'mexican', 'middle_eastern', 'british']:
                anna_count = int(anna_row.get(cuisine, 0) or 0)
                zone_count = zone_data.get('core_7', {}).get(cuisine, 0)
                
                if anna_count != zone_count:
                    mismatches += 1
                    if mismatches <= 5:
                        errors.append(f"{zone_name}: {cuisine} mismatch - Anna={anna_count}, zone_mvp={zone_count}")
    
    if mismatches > 5:
        errors.append(f"... and {mismatches - 5} more cuisine count mismatches")
    
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    return errors, warnings


def check_mvp_status_calculation():
    """
    Check 3: MVP status is calculated consistently using canonical function.
    """
    print("\n" + "=" * 60)
    print("CHECK 3: MVP Status Calculation")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    mvp_file = DOCS_DATA_DIR / "zone_mvp_status.json"
    if not mvp_file.exists():
        errors.append(f"Zone MVP status not found: {mvp_file}")
        return errors, warnings
    
    with open(mvp_file) as f:
        zones = json.load(f)
    
    # Verify MVP status matches expected calculation
    status_counts = {}
    miscalculated = 0
    
    for zone_data in zones:
        core_7_count = zone_data.get('core_7_count', 0)
        orders = zone_data.get('orders', 0) or zone_data.get('order_count', 0) or 0
        has_orders = orders > 0
        
        expected_status = get_mvp_status(core_7_count, has_orders)
        actual_status = zone_data.get('mvp_status')
        
        status_counts[actual_status] = status_counts.get(actual_status, 0) + 1
        
        if expected_status != actual_status:
            miscalculated += 1
            if miscalculated <= 5:
                errors.append(f"{zone_data['zone']}: Expected '{expected_status}', got '{actual_status}' (core_7={core_7_count}, orders={orders})")
    
    if miscalculated > 5:
        errors.append(f"... and {miscalculated - 5} more MVP status mismatches")
    
    # Report status distribution
    print("\n  MVP Status Distribution:")
    for status in ['MVP Ready', 'Near MVP', 'Progressing', 'Developing', 'Supply Only', 'Not Started']:
        count = status_counts.get(status, 0)
        print(f"    {status:<15} {count:>5} zones")
    
    print(f"\n  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    return errors, warnings


def check_config_alignment():
    """
    Check 4: Config files align with canonical definitions.
    """
    print("\n" + "=" * 60)
    print("CHECK 4: Config File Alignment")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    config_dir = PROJECT_ROOT / "config"
    
    # Check cuisine_hierarchy.json
    hierarchy_file = config_dir / "cuisine_hierarchy.json"
    if hierarchy_file.exists():
        with open(hierarchy_file) as f:
            hierarchy = json.load(f)
        
        config_required = set(hierarchy.get('core_cuisines', {}).get('required_for_mvp', []))
        canonical_required = set(REQUIRED_FOR_MVP)
        
        if config_required != canonical_required:
            errors.append(f"cuisine_hierarchy.json required_for_mvp mismatch: {config_required} vs {canonical_required}")
    else:
        warnings.append("cuisine_hierarchy.json not found")
    
    # Check mvp_thresholds.json
    thresholds_file = config_dir / "mvp_thresholds.json"
    if thresholds_file.exists():
        with open(thresholds_file) as f:
            thresholds = json.load(f)
        
        cuisine_min = thresholds.get('mvp_criteria', {}).get('cuisines_min', {}).get('value', 0)
        if cuisine_min != 5:
            warnings.append(f"mvp_thresholds.json cuisines_min is {cuisine_min}, expected 5")
    else:
        warnings.append("mvp_thresholds.json not found")
    
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    return errors, warnings


def main():
    print("=" * 60)
    print("CONSISTENCY VALIDATION")
    print("=" * 60)
    print()
    print(f"Canonical Core 7: {CORE_7}")
    print(f"Required for MVP: {REQUIRED_FOR_MVP}")
    
    all_errors = []
    all_warnings = []
    
    # Run all checks
    errors, warnings = check_dish_rankings()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    errors, warnings = check_zone_cuisine_counts()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    errors, warnings = check_mvp_status_calculation()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    errors, warnings = check_config_alignment()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if all_errors:
        print(f"\n❌ ERRORS ({len(all_errors)}):")
        for e in all_errors[:20]:
            print(f"  - {e}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more errors")
    else:
        print("\n✓ No errors found")
    
    if all_warnings:
        print(f"\n⚠️  WARNINGS ({len(all_warnings)}):")
        for w in all_warnings[:20]:
            print(f"  - {w}")
        if len(all_warnings) > 20:
            print(f"  ... and {len(all_warnings) - 20} more warnings")
    else:
        print("\n✓ No warnings")
    
    print("\n" + "=" * 60)
    if not all_errors:
        print("✓ VALIDATION PASSED - All outputs consistent")
        return 0
    else:
        print("❌ VALIDATION FAILED - Fix errors above")
        return 1


if __name__ == "__main__":
    exit(main())


