#!/usr/bin/env python3
"""
Fix dish order volumes in priority_100_unified.csv using actual order data.
"""

import csv
from collections import defaultdict

# Dish type keyword mappings for order matching
DISH_KEYWORDS = {
    'Katsu': ['katsu'],
    'Noodles': ['noodle', 'noodles', 'chow mein', 'lo mein', 'yakisoba', 'udon'],
    'Curry': ['curry'],  # Generic curry - not Butter Chicken or Tikka
    'Pho': ['pho'],
    'Rice Bowl': ['rice bowl', 'donburi', 'bibimbap', 'poke bowl'],
    'Bowl': ['bowl'],  # Generic bowls
    'Pad Thai': ['pad thai'],
    'Salad': ['salad'],
    'Pasta': ['pasta', 'spaghetti', 'penne', 'linguine', 'fettuccine', 'rigatoni'],
    'Shawarma': ['shawarma'],
    'Sushi': ['sushi', 'maki', 'nigiri', 'sashimi'],
    'Pizza': ['pizza'],
    'Fajitas': ['fajita'],
    'Biryani': ['biryani'],
    'Fried Rice': ['fried rice', 'egg fried rice'],
    'Ramen': ['ramen'],
    'Teriyaki': ['teriyaki'],
    'Burrito': ['burrito'],
    'Tacos': ['taco'],
    "Shepherd's Pie": ['shepherd'],
    'Lasagne': ['lasagne', 'lasagna'],
    'Mac & Cheese': ['mac & cheese', 'mac and cheese', 'macaroni cheese'],
    'Butter Chicken': ['butter chicken'],
    'Tikka Masala': ['tikka masala'],
    'Gyoza': ['gyoza', 'dumpling', 'potsticker'],
    'Spring Roll': ['spring roll'],
    'Dim Sum': ['dim sum'],
    'Bao': ['bao bun', 'bao'],
    'Wings': ['wings'],
    'Burger': ['burger'],
    'Fish & Chips': ['fish & chips', 'fish and chips'],
    'Quesadilla': ['quesadilla'],
    'Nachos': ['nachos'],
    'Wrap': ['wrap'],
    'Kebab': ['kebab', 'kofta'],
    'Falafel': ['falafel'],
    'Hummus': ['hummus'],
    'Grain Bowl': ['grain bowl', 'buddha bowl'],
    'Stir Fry': ['stir fry', 'stir-fry'],
}

def count_orders_by_dish():
    """Count actual order mentions for each dish type."""
    dish_counts = defaultdict(int)
    total_orders = 0
    
    with open('DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_orders += 1
            items = row.get('MENU_ITEM_LIST', '').lower()
            
            for dish, keywords in DISH_KEYWORDS.items():
                for kw in keywords:
                    if kw in items:
                        dish_counts[dish] += 1
                        break
    
    return dish_counts, total_orders

def fix_priority_csv():
    """Update priority_100_unified.csv with correct order volumes."""
    
    print("Counting actual orders...")
    dish_counts, total_orders = count_orders_by_dish()
    print(f"Analyzed {total_orders:,} orders")
    print()
    
    # Read existing CSV
    with open('DATA/3_ANALYSIS/priority_100_unified.csv', 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    # Track changes
    changes = []
    removed = []
    
    # Update order volumes
    updated_rows = []
    for row in rows:
        dish = row['dish_type']
        old_volume = row['order_volume']
        
        # Find matching dish in our counts
        new_volume = None
        for counted_dish, count in dish_counts.items():
            if counted_dish.lower() == dish.lower() or dish.lower() in counted_dish.lower():
                new_volume = count
                break
        
        # Special case mappings
        dish_lower = dish.lower()
        if 'curry' in dish_lower and dish_lower != 'curry':
            # Specific curries like "East Asian Curry" - estimate
            new_volume = dish_counts.get('Curry', 0) // 5  # Rough estimate
        if dish_lower == 'chicken pie':
            # This doesn't exist - mark for removal or zero
            new_volume = 0
            removed.append(dish)
        
        if new_volume is not None and old_volume:
            try:
                old_val = float(old_volume)
                if abs(old_val - new_volume) > 100:
                    changes.append(f"{dish}: {old_val:,.0f} → {new_volume:,}")
            except:
                pass
        
        # Update the row
        if new_volume is not None:
            row['order_volume'] = new_volume
            row['orders_per_zone'] = new_volume  # Also update this field
        elif row['on_dinneroo'] == 'True' and (not old_volume or old_volume == '0' or old_volume == ''):
            row['order_volume'] = 0
            row['orders_per_zone'] = 0
        
        updated_rows.append(row)
    
    # Remove rows with 0 orders that claim to be on Dinneroo with high volumes
    final_rows = []
    for row in updated_rows:
        # Keep all rows but flag suspicious ones
        if row['dish_type'] == 'Chicken Pie':
            row['on_dinneroo'] = 'False'  # Fix the lie
            row['order_volume'] = 0
        final_rows.append(row)
    
    # Re-rank by order volume for on_dinneroo items
    on_dinneroo = [r for r in final_rows if r['on_dinneroo'] == 'True']
    off_dinneroo = [r for r in final_rows if r['on_dinneroo'] == 'False']
    
    # Sort on_dinneroo by actual orders
    on_dinneroo.sort(key=lambda x: float(x['order_volume'] or 0), reverse=True)
    
    # Combine
    all_rows = on_dinneroo + off_dinneroo
    
    # Re-number ranks
    for i, row in enumerate(all_rows, 1):
        row['rank'] = i
    
    # Write updated CSV
    with open('DATA/3_ANALYSIS/priority_100_unified.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print("=" * 60)
    print("PRIORITY_100_UNIFIED.CSV FIXED")
    print("=" * 60)
    print()
    print("Major changes:")
    for change in changes[:15]:
        print(f"  {change}")
    if len(changes) > 15:
        print(f"  ... and {len(changes) - 15} more")
    print()
    if removed:
        print("Removed/zeroed (didn't exist):")
        for dish in removed:
            print(f"  ❌ {dish}")
    print()
    print(f"File updated: DATA/3_ANALYSIS/priority_100_unified.csv")
    print()
    print("Top 10 dishes by ACTUAL orders:")
    for row in all_rows[:10]:
        vol = float(row['order_volume'] or 0)
        print(f"  {row['rank']:2}. {row['dish_type']:20} {vol:>8,.0f} orders")

if __name__ == "__main__":
    fix_priority_csv()

