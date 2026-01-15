#!/usr/bin/env python3
"""
Asian Sub-Demand Analysis
==========================
Creates supplementary analysis showing demand signals within Asian cuisine category.

From plan:
- Show which Asian dishes drive the most demand (Pho, Katsu, Noodles, etc.)
- Highlight that "Chinese-style" dishes may be underrepresented vs Japanese-style
- Frame as recruitment insight, not changing 7-cuisine MVP

Outputs:
- asian_subdomain_analysis.csv
- Summary narrative for presentation
"""

import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "DATA/3_ANALYSIS"
ANNA_DIR = BASE_DIR / "DATA/1_SOURCE/anna_slides"
DELIVERABLES_DIR = BASE_DIR / "DELIVERABLES/reports"

# Asian dish types from Anna's framework
ASIAN_DISHES = {
    'Pho': 'Vietnamese',
    'Katsu': 'Japanese',
    'Noodles': 'Mixed (Thai/Chinese/Japanese)',
    'Rice Bowl': 'Mixed (Japanese/Korean/Chinese)',
    'Fried Rice': 'Chinese',
    'East Asian Curry': 'Thai/Japanese',
    'Sushi': 'Japanese',
    'Poke': 'Hawaiian/Japanese'
}

def load_dish_data():
    """Load dish performance data."""
    working_path = ANALYSIS_DIR / "dish_validation_working.csv"
    df = pd.read_csv(working_path)
    return df

def analyze_asian_dishes(df):
    """Analyze demand within Asian dishes."""
    print("Analyzing Asian sub-demand signals...")
    
    # Filter to Asian cuisine dishes
    asian_df = df[df['cuisine'] == 'Asian'].copy()
    
    # Add sub-cuisine category
    asian_df['sub_cuisine'] = asian_df['dish_type'].map(ASIAN_DISHES)
    
    # Calculate metrics
    analysis = []
    for idx, row in asian_df.iterrows():
        dish = row['dish_type']
        
        analysis.append({
            'dish_type': dish,
            'sub_cuisine': ASIAN_DISHES.get(dish, 'Unknown'),
            'current_tier': row['current_tier'],
            'looker_demand_index': row['looker_demand_index'],
            'looker_preference_index': row['looker_preference_index'],
            'kids_full_and_happy_pct': row['kids_full_and_happy_pct'],
            'kids_n': row['kids_full_and_happy_n'],
            'family_suitability': row['family_suitability'],
            'coverage_gap_pct': row['coverage_gap_pct'],
            'validation_status': row['validation_status']
        })
    
    return pd.DataFrame(analysis)

def calculate_subcuisine_summary(df_asian):
    """Summarize by sub-cuisine category."""
    # Group by sub-cuisine origin
    sub_groups = {
        'Japanese': ['Katsu', 'Sushi', 'Poke'],
        'Vietnamese': ['Pho'],
        'Chinese': ['Fried Rice'],
        'Thai': ['East Asian Curry'],
        'Mixed': ['Noodles', 'Rice Bowl']
    }
    
    summary = []
    for origin, dishes in sub_groups.items():
        df_sub = df_asian[df_asian['dish_type'].isin(dishes)]
        if len(df_sub) > 0:
            summary.append({
                'sub_cuisine_origin': origin,
                'dishes_included': ', '.join(dishes),
                'avg_demand_index': df_sub['looker_demand_index'].mean(),
                'avg_kids_happy_pct': df_sub['kids_full_and_happy_pct'].mean(),
                'total_kids_n': df_sub['kids_n'].sum(),
                'dish_count': len(df_sub)
            })
    
    return pd.DataFrame(summary)

def generate_narrative(df_asian, df_summary):
    """Generate narrative for presentation."""
    
    # Find top performers
    top_demand = df_asian.nlargest(3, 'looker_demand_index')[['dish_type', 'looker_demand_index', 'sub_cuisine']].to_dict('records')
    top_happy = df_asian.dropna(subset=['kids_full_and_happy_pct']).nlargest(3, 'kids_full_and_happy_pct')[['dish_type', 'kids_full_and_happy_pct', 'sub_cuisine']].to_dict('records')
    
    # Chinese representation
    chinese_dishes = df_asian[df_asian['sub_cuisine'].str.contains('Chinese', na=False)]
    japanese_dishes = df_asian[df_asian['sub_cuisine'].str.contains('Japanese', na=False)]
    
    narrative = f"""# Asian Sub-Demand Analysis

## Key Finding

While Asian remains a single category for MVP tracking (to align with internal tagging), 
recruitment should prioritise specific sub-types based on demand and family satisfaction.

## Demand Leaders (Looker Index)

1. **{top_demand[0]['dish_type']}** ({top_demand[0]['sub_cuisine']}) - Demand Index: {top_demand[0]['looker_demand_index']}
2. **{top_demand[1]['dish_type']}** ({top_demand[1]['sub_cuisine']}) - Demand Index: {top_demand[1]['looker_demand_index']}
3. **{top_demand[2]['dish_type']}** ({top_demand[2]['sub_cuisine']}) - Demand Index: {top_demand[2]['looker_demand_index']}

## Family Satisfaction Leaders (Kids Full & Happy)

1. **{top_happy[0]['dish_type']}** ({top_happy[0]['sub_cuisine']}) - {top_happy[0]['kids_full_and_happy_pct']:.0f}%
2. **{top_happy[1]['dish_type']}** ({top_happy[1]['sub_cuisine']}) - {top_happy[1]['kids_full_and_happy_pct']:.0f}%
3. **{top_happy[2]['dish_type']}** ({top_happy[2]['sub_cuisine']}) - {top_happy[2]['kids_full_and_happy_pct']:.0f}%

## Sub-Cuisine Representation

| Origin | Dish Count | Notes |
|--------|------------|-------|
| Japanese-style | {len(japanese_dishes)} | Strong representation (Katsu, Sushi, Poke) |
| Chinese-style | {len(chinese_dishes)} | Currently only Fried Rice explicitly categorised as Chinese |
| Vietnamese | 1 | Pho - high performer |
| Thai | 1 | East Asian Curry |
| Mixed | 2 | Noodles, Rice Bowl span multiple origins |

## Insight: Chinese Demand May Be Masked

The open-text mining found explicit requests for:
- Chinese cuisine (2 requests)
- Spring rolls (1 request)
- Egg fried rice (1 request)

However, Chinese-style dishes may be ordered under generic categories like "Fried Rice" or "Noodles" 
rather than being tagged as Chinese specifically. This suggests:

1. **Actual Chinese demand may be higher than visible** in cuisine-level reporting
2. **Recruitment opportunity**: Partners offering distinctly Chinese dishes (sweet & sour, chow mein, dim sum) 
   could fill a gap that isn't visible in current framework

## Recommendation

"While Asian remains a single category for MVP tracking, recruitment should prioritise:
1. Vietnamese (Pho) - highest demand + excellent family satisfaction
2. Japanese (Katsu, Sushi) - strong demand, good family fit
3. Chinese-style options - potential unmet demand, consider testing with partners that offer 
   clearly Chinese dishes (sweet & sour, chow mein) to assess true appetite"

---

*Note: This analysis supplements rather than replaces the 7-cuisine MVP framework.*
"""
    
    return narrative

def main():
    """Main execution."""
    print("=" * 60)
    print("ASIAN SUB-DEMAND ANALYSIS")
    print("=" * 60)
    
    # Load data
    df = load_dish_data()
    
    # Analyze Asian dishes
    df_asian = analyze_asian_dishes(df)
    
    # Summary by sub-cuisine
    df_summary = calculate_subcuisine_summary(df_asian)
    
    # Generate narrative
    narrative = generate_narrative(df_asian, df_summary)
    
    # Save outputs
    asian_path = ANALYSIS_DIR / "asian_subdomain_analysis.csv"
    df_asian.to_csv(asian_path, index=False)
    print(f"\nSaved Asian dish analysis to: {asian_path}")
    
    summary_path = ANALYSIS_DIR / "asian_subcuisine_summary.csv"
    df_summary.to_csv(summary_path, index=False)
    print(f"Saved sub-cuisine summary to: {summary_path}")
    
    narrative_path = DELIVERABLES_DIR / "asian_subdomain_narrative.md"
    with open(narrative_path, 'w') as f:
        f.write(narrative)
    print(f"Saved narrative to: {narrative_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("ASIAN DISH PERFORMANCE")
    print("=" * 60)
    print(df_asian[['dish_type', 'sub_cuisine', 'current_tier', 'looker_demand_index', 
                     'kids_full_and_happy_pct']].to_string(index=False))
    
    print("\n" + "=" * 60)
    print("SUB-CUISINE SUMMARY")
    print("=" * 60)
    print(df_summary.to_string(index=False))
    
    return df_asian, df_summary

if __name__ == "__main__":
    main()
