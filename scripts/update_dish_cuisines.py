#!/usr/bin/env python3
"""
Update priority_100_unified.csv with core_7_cuisine and sub_cuisine columns.

Uses canonical definitions from scripts/utils/definitions.py to ensure
consistency across all agents.
"""

import pandas as pd
from pathlib import Path
import sys

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from utils.definitions import (
    CORE_7,
    get_core_7,
    get_sub_cuisine,
    get_core_7_for_dish,
    DISH_TO_CORE,
    DISH_TO_SUB,
)

PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"


def main():
    print("=" * 60)
    print("UPDATE DISH CUISINES (Unified Definitions)")
    print("=" * 60)
    print()
    
    # Load priority_100_unified.csv
    input_file = DATA_DIR / "priority_100_unified.csv"
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} dishes from {input_file}")
    print()
    
    # Track updates
    updated_count = 0
    unmapped_dishes = []
    
    # Add core_7_cuisine and sub_cuisine columns
    core_7_cuisines = []
    sub_cuisines = []
    
    for _, row in df.iterrows():
        dish_type = row['dish_type']
        existing_cuisine = row.get('cuisine', '')
        
        # First try to get core_7 from dish type
        core_7 = get_core_7_for_dish(dish_type)
        sub = get_sub_cuisine(dish_type)
        
        # If dish not found, try from existing cuisine column
        if core_7 == 'Other' or core_7 is None:
            if existing_cuisine and str(existing_cuisine) not in ['nan', '', 'None']:
                mapped_core_7 = get_core_7(str(existing_cuisine))
                if mapped_core_7 and mapped_core_7 != 'Other':
                    core_7 = mapped_core_7
                    # Use existing cuisine as sub-cuisine if it's different from core
                    if existing_cuisine.lower().strip() not in [c.lower() for c in CORE_7]:
                        sub = existing_cuisine.title()
        
        # Track unmapped dishes
        if core_7 == 'Other' or core_7 is None:
            unmapped_dishes.append({
                'dish': dish_type,
                'original_cuisine': existing_cuisine,
                'rank': row['rank']
            })
        else:
            updated_count += 1
        
        core_7_cuisines.append(core_7 or 'Other')
        sub_cuisines.append(sub)
    
    # Add new columns
    df['core_7_cuisine'] = core_7_cuisines
    df['sub_cuisine'] = sub_cuisines
    
    # Reorder columns to put new ones after cuisine
    cols = list(df.columns)
    cuisine_idx = cols.index('cuisine')
    cols.remove('core_7_cuisine')
    cols.remove('sub_cuisine')
    cols.insert(cuisine_idx + 1, 'core_7_cuisine')
    cols.insert(cuisine_idx + 2, 'sub_cuisine')
    df = df[cols]
    
    # Save updated file
    df.to_csv(input_file, index=False)
    print(f"Updated {input_file}")
    print(f"  - Added core_7_cuisine column")
    print(f"  - Added sub_cuisine column")
    print(f"  - Mapped {updated_count} dishes to Core 7")
    
    # Report unmapped dishes
    if unmapped_dishes:
        print(f"\nUnmapped dishes ({len(unmapped_dishes)}):")
        for d in unmapped_dishes[:10]:
            print(f"  - Rank {d['rank']}: {d['dish']} (original: {d['original_cuisine']})")
        if len(unmapped_dishes) > 10:
            print(f"  ... and {len(unmapped_dishes) - 10} more")
    
    # Print summary by Core 7
    print(f"\nDishes by Core 7 Cuisine:")
    for cuisine in CORE_7 + ['Other']:
        count = len(df[df['core_7_cuisine'] == cuisine])
        print(f"  {cuisine:<18} {count:>3} dishes")


if __name__ == "__main__":
    main()


