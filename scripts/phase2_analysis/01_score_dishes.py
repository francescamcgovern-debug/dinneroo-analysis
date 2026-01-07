"""
Unified Dish Scoring Script v2.0
================================
Scores dishes using the two-track approach:
- Performance Track (50%): Behavioral data from Snowflake + surveys
- Opportunity Track (50%): Latent demand + validated fit factors

Hybrid scoring: Uses survey data where available, LLM estimation as fallback.

Output: Master list of 100 dish types with unified scores.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "DATA"
CONFIG_PATH = BASE_PATH / "config"
DELIVERABLES_PATH = BASE_PATH / "DELIVERABLES"

def load_config():
    """Load the unified scoring configuration."""
    with open(CONFIG_PATH / "dish_scoring_unified.json", 'r') as f:
        return json.load(f)

def load_master_dish_types():
    """Load master list of dish types with LLM-estimated factors."""
    try:
        with open(CONFIG_PATH / "dish_types_master.json", 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data['dishes'])
    except Exception as e:
        print(f"Warning: Could not load master dish types: {e}")
        return pd.DataFrame()

def load_performance_data():
    """Load performance data from existing analysis."""
    try:
        df = pd.read_csv(DATA_PATH / "3_ANALYSIS" / "dish_performance_scores.csv")
        return df
    except Exception as e:
        print(f"Warning: Could not load performance scores: {e}")
        return pd.DataFrame()

def load_opportunity_data():
    """Load opportunity scores from existing analysis."""
    try:
        df = pd.read_csv(DATA_PATH / "3_ANALYSIS" / "dish_opportunity_scores.csv")
        return df
    except Exception as e:
        print(f"Warning: Could not load opportunity scores: {e}")
        return pd.DataFrame()

def load_latent_demand():
    """Load latent demand scores."""
    try:
        df = pd.read_csv(DATA_PATH / "3_ANALYSIS" / "latent_demand_scores.csv")
        return df
    except Exception as e:
        print(f"Warning: Could not load latent demand scores: {e}")
        return pd.DataFrame()

def calculate_performance_score(row, config):
    """Calculate performance track score for a dish."""
    perf_config = config['tracks']['performance']['components']
    
    # Check if we have enough data
    has_orders = pd.notna(row.get('order_volume')) and row.get('order_volume', 0) >= 50
    has_rating = pd.notna(row.get('avg_rating'))
    
    if not has_orders:
        return None, 'no_data'
    
    scores = {}
    weights = {}
    
    # Normalized sales (using order volume as proxy)
    if pd.notna(row.get('order_volume')):
        vol = row['order_volume']
        if vol >= 5000:
            scores['normalized_sales'] = 5
        elif vol >= 2000:
            scores['normalized_sales'] = 4
        elif vol >= 500:
            scores['normalized_sales'] = 3
        elif vol >= 100:
            scores['normalized_sales'] = 2
        else:
            scores['normalized_sales'] = 1
        weights['normalized_sales'] = perf_config['normalized_sales']['effective_weight']
    
    # Zone ranking strength (using volume as proxy for now)
    if pd.notna(row.get('order_volume')):
        vol = row['order_volume']
        if vol >= 5000:
            scores['zone_ranking'] = 5
        elif vol >= 2000:
            scores['zone_ranking'] = 4
        elif vol >= 500:
            scores['zone_ranking'] = 3
        elif vol >= 100:
            scores['zone_ranking'] = 2
        else:
            scores['zone_ranking'] = 1
        weights['zone_ranking'] = perf_config['zone_ranking_strength']['effective_weight']
    
    # Deliveroo rating
    if pd.notna(row.get('avg_rating')):
        rating = row['avg_rating']
        if rating >= 4.5:
            scores['rating'] = 5
        elif rating >= 4.3:
            scores['rating'] = 4
        elif rating >= 4.0:
            scores['rating'] = 3
        elif rating >= 3.5:
            scores['rating'] = 2
        else:
            scores['rating'] = 1
        weights['rating'] = perf_config['deliveroo_rating']['effective_weight']
    
    # Survey-based metrics
    if pd.notna(row.get('adult_satisfaction')):
        sat = row['adult_satisfaction']
        if sat >= 0.9:
            scores['liked_loved'] = 5
        elif sat >= 0.8:
            scores['liked_loved'] = 4
        elif sat >= 0.7:
            scores['liked_loved'] = 3
        elif sat >= 0.6:
            scores['liked_loved'] = 2
        else:
            scores['liked_loved'] = 1
        weights['liked_loved'] = perf_config['liked_loved_it']['effective_weight']
    
    if pd.notna(row.get('kids_happy')):
        kids = row['kids_happy']
        if kids >= 0.85:
            scores['kids_happy'] = 5
        elif kids >= 0.75:
            scores['kids_happy'] = 4
        elif kids >= 0.65:
            scores['kids_happy'] = 3
        elif kids >= 0.55:
            scores['kids_happy'] = 2
        else:
            scores['kids_happy'] = 1
        weights['kids_happy'] = perf_config['kids_full_happy']['effective_weight']
    
    # Calculate weighted score
    if not scores:
        return None, 'no_data'
    
    total_weight = sum(weights.values())
    if total_weight == 0:
        return None, 'no_data'
    
    # Calculate weighted average (scores are 1-5, result is 1-5)
    weighted_score = sum(scores[k] * weights[k] for k in scores) / total_weight
    
    evidence = 'validated' if len(scores) >= 4 else 'corroborated'
    
    return weighted_score, evidence

def calculate_opportunity_score(row, latent_demand_df, config):
    """Calculate opportunity track score for a dish."""
    opp_config = config['tracks']['opportunity']['components']
    
    dish_type = row.get('dish_type', '')
    
    scores = {}
    weights = {}
    evidence_flags = []
    
    # Latent demand score
    latent_row = latent_demand_df[latent_demand_df['dish_type'] == dish_type]
    if len(latent_row) > 0:
        scores['latent_demand'] = latent_row.iloc[0]['latent_demand_score']
        evidence_flags.append('measured')
    else:
        scores['latent_demand'] = 2  # Default low score
        evidence_flags.append('estimated')
    weights['latent_demand'] = opp_config['latent_demand']['effective_weight']
    
    # Validated fit factors
    fit_config = opp_config['validated_fit_factors']['factors']
    
    # Adult appeal
    if pd.notna(row.get('adult_appeal')):
        scores['adult_appeal'] = row['adult_appeal']
        evidence_flags.append('measured')
    else:
        # LLM estimation fallback - use heuristics for now
        scores['adult_appeal'] = estimate_adult_appeal(dish_type)
        evidence_flags.append('estimated')
    weights['adult_appeal'] = fit_config['adult_appeal']['effective_weight']
    
    # Balanced/guilt-free
    if pd.notna(row.get('balanced_guilt_free')):
        scores['balanced'] = row['balanced_guilt_free']
        evidence_flags.append('measured')
    else:
        scores['balanced'] = estimate_balanced(dish_type)
        evidence_flags.append('estimated')
    weights['balanced'] = fit_config['balanced_guilt_free']['effective_weight']
    
    # Fussy eater friendly
    if pd.notna(row.get('fussy_eater_friendly')):
        scores['fussy_eater'] = row['fussy_eater_friendly']
        evidence_flags.append('measured')
    else:
        scores['fussy_eater'] = estimate_fussy_eater(dish_type)
        evidence_flags.append('estimated')
    weights['fussy_eater'] = fit_config['fussy_eater_friendly']['effective_weight']
    
    # Calculate weighted score (scores are 1-5, result is 1-5)
    total_weight = sum(weights.values())
    weighted_score = sum(scores[k] * weights[k] for k in scores) / total_weight
    
    # Determine evidence level
    measured_count = evidence_flags.count('measured')
    if measured_count >= 3:
        evidence = 'validated'
    elif measured_count >= 1:
        evidence = 'corroborated'
    else:
        evidence = 'estimated'
    
    return weighted_score, evidence, scores

def estimate_adult_appeal(dish_type):
    """Estimate adult appeal based on dish type characteristics."""
    high_appeal = ['Pho', 'Ramen', 'Sushi', 'Thai', 'Curry', 'Shawarma', 'Biryani', 
                   'Pad Thai', 'Korean Fried Chicken', 'Greek Mezze']
    medium_appeal = ['Katsu', 'Rice Bowl', 'Noodles', 'Fajitas', 'Burrito', 'Salad',
                     'Grilled Chicken', 'Teriyaki', 'Stir Fry']
    low_appeal = ['Pizza', 'Mac & Cheese', 'Pasta', 'Fish & Chips', 'Burger']
    
    dish_lower = dish_type.lower()
    
    for d in high_appeal:
        if d.lower() in dish_lower:
            return 5
    for d in medium_appeal:
        if d.lower() in dish_lower:
            return 4
    for d in low_appeal:
        if d.lower() in dish_lower:
            return 3
    
    return 3  # Default

def estimate_balanced(dish_type):
    """Estimate balanced/guilt-free score based on dish type."""
    very_balanced = ['Salad', 'Grilled Chicken', 'Poke Bowl', 'Buddha Bowl', 'Grain Bowl',
                     'Rice Bowl', 'Pho', 'Stir Fry']
    balanced = ['Katsu', 'Teriyaki', 'Fajitas', 'Shawarma', 'Curry', 'Noodles']
    neutral = ['Pad Thai', 'Ramen', 'Biryani', 'Sushi', 'Tacos']
    indulgent = ['Pizza', 'Burger', 'Mac & Cheese', 'Fish & Chips', 'Lasagne']
    
    dish_lower = dish_type.lower()
    
    for d in very_balanced:
        if d.lower() in dish_lower:
            return 5
    for d in balanced:
        if d.lower() in dish_lower:
            return 4
    for d in neutral:
        if d.lower() in dish_lower:
            return 3
    for d in indulgent:
        if d.lower() in dish_lower:
            return 2
    
    return 3  # Default

def estimate_fussy_eater(dish_type):
    """Estimate fussy eater friendliness based on dish type."""
    very_friendly = ['Pizza', 'Pasta', 'Mac & Cheese', 'Chicken', 'Fish & Chips',
                     'Burger', 'Fajitas', 'Katsu']
    friendly = ['Rice Bowl', 'Noodles', 'Teriyaki', 'Fried Rice', 'Grilled Chicken']
    neutral = ['Curry', 'Lasagne', 'Stir Fry', 'Shawarma']
    challenging = ['Pho', 'Ramen', 'Sushi', 'Thai', 'Biryani', 'Korean']
    
    dish_lower = dish_type.lower()
    
    for d in very_friendly:
        if d.lower() in dish_lower:
            return 5
    for d in friendly:
        if d.lower() in dish_lower:
            return 4
    for d in neutral:
        if d.lower() in dish_lower:
            return 3
    for d in challenging:
        if d.lower() in dish_lower:
            return 2
    
    return 3  # Default

def calculate_unified_score(perf_score, opp_score, config):
    """Calculate the unified score combining both tracks."""
    perf_weight = config['tracks']['performance']['weight']
    opp_weight = config['tracks']['opportunity']['weight']
    
    if perf_score is None:
        # No performance data - use opportunity only (already on 1-5 scale)
        return opp_score, 'opportunity_only'
    
    # Both scores are on 1-5 scale, weighted average stays on 1-5 scale
    unified = (perf_score * perf_weight + opp_score * opp_weight)
    return unified, 'full'

def assign_tier(score, config):
    """Assign tier based on score."""
    tiers = config['tier_classification']
    
    if score >= tiers['tier_1_must_have']['threshold']:
        return 'Tier 1: Must-Have'
    elif score >= tiers['tier_2_should_have']['threshold']:
        return 'Tier 2: Should-Have'
    elif score >= tiers['tier_3_nice_to_have']['threshold']:
        return 'Tier 3: Nice-to-Have'
    else:
        return 'Tier 4: Monitor'

def assign_quadrant(perf_score, opp_score, has_performance_data=True, on_dinneroo=True):
    """Assign quadrant based on performance and opportunity scores.
    
    Action-oriented naming:
    - Priority: High performance + High opportunity - Expand aggressively
    - Protect: High performance + Low opportunity - Maintain, don't over-invest
    - Develop: Low performance + High opportunity - Fix issues, improve quality
    - Monitor: Low performance + Low opportunity - Watch, deprioritize
    - Prospect: NOT on Dinneroo + High opportunity - Expansion opportunity
    
    Key logic:
    - Prospect is ONLY for dishes NOT on Dinneroo (true expansion opportunities)
    - Dishes ON Dinneroo without performance data go to Develop (need to track)
    """
    perf_threshold = 3.5
    opp_threshold = 3.0
    
    # For dishes NOT on Dinneroo, use opportunity-only logic
    if not on_dinneroo:
        if opp_score >= opp_threshold:
            return 'Prospect'  # High opportunity, not on platform yet
        else:
            return 'Monitor'
    
    # For dishes ON Dinneroo without performance data, treat as Develop/Monitor
    # (we have them but need to track performance)
    if perf_score is None or not has_performance_data:
        if opp_score >= opp_threshold:
            return 'Develop'  # On platform, high opportunity, need to improve tracking
        else:
            return 'Monitor'
    
    # Standard 2x2 for dishes with performance data
    if perf_score >= perf_threshold and opp_score >= opp_threshold:
        return 'Priority'
    elif perf_score < perf_threshold and opp_score >= opp_threshold:
        return 'Develop'
    elif perf_score >= perf_threshold and opp_score < opp_threshold:
        return 'Protect'
    else:
        return 'Monitor'

def main():
    """Run the unified dish scoring."""
    print("=" * 60)
    print("UNIFIED DISH SCORING v2.0")
    print("=" * 60)
    
    # Load config
    print("\n1. Loading configuration...")
    config = load_config()
    print(f"   Framework version: {config['version']}")
    
    # Load data
    print("\n2. Loading data...")
    perf_df = load_performance_data()
    print(f"   Performance data: {len(perf_df)} dishes")
    
    opp_df = load_opportunity_data()
    print(f"   Opportunity data: {len(opp_df)} dishes")
    
    latent_df = load_latent_demand()
    print(f"   Latent demand data: {len(latent_df)} dishes")
    
    master_df = load_master_dish_types()
    print(f"   Master dish types: {len(master_df)} dishes")
    
    # Merge data
    print("\n3. Merging data sources...")
    
    # Start with master dish types as base to ensure we get all 100
    if len(master_df) > 0:
        merged = master_df.copy()
    elif len(opp_df) > 0:
        merged = opp_df.copy()
    else:
        merged = pd.DataFrame()
    
    # Merge opportunity data (Anna's work is source of truth for on_dinneroo)
    if len(opp_df) > 0 and len(merged) > 0:
        opp_cols = ['dish_type', 'on_dinneroo', 'order_volume', 'latent_demand_score', 'kid_friendly', 
                    'balanced_guilt_free', 'adult_appeal', 'fussy_eater_friendly',
                    'gap_type', 'gap_score', 'potential_partners']
        opp_cols = [c for c in opp_cols if c in opp_df.columns]
        merged = pd.merge(
            merged,
            opp_df[opp_cols],
            on='dish_type',
            how='left',
            suffixes=('', '_opp')
        )
        # Use Anna's on_dinneroo status as source of truth (override master list)
        if 'on_dinneroo_opp' in merged.columns:
            merged['on_dinneroo'] = merged['on_dinneroo_opp'].fillna(merged['on_dinneroo'])
            merged = merged.drop(columns=['on_dinneroo_opp'])
        # Use opportunity data values where master doesn't have them
        for col in ['balanced_guilt_free', 'adult_appeal', 'fussy_eater_friendly']:
            if f'{col}_opp' in merged.columns:
                merged[col] = merged[col].fillna(merged[f'{col}_opp'])
                merged = merged.drop(columns=[f'{col}_opp'])
    
    # Merge performance data
    if len(perf_df) > 0 and len(merged) > 0:
        perf_cols = ['dish_type', 'order_volume', 'avg_rating', 'adult_satisfaction', 
                     'kids_happy', 'portions_adequate', 'survey_n']
        perf_cols = [c for c in perf_cols if c in perf_df.columns]
        merged = pd.merge(
            merged, 
            perf_df[perf_cols],
            on='dish_type',
            how='left',
            suffixes=('', '_perf')
        )
        # Use performance order_volume if available
        if 'order_volume_perf' in merged.columns:
            merged['order_volume'] = merged['order_volume_perf'].fillna(merged.get('order_volume', 0))
            merged = merged.drop(columns=['order_volume_perf'])
    
    print(f"   Merged dataset: {len(merged)} dishes")
    
    # Calculate scores
    print("\n4. Calculating scores...")
    results = []
    
    for idx, row in merged.iterrows():
        dish_type = row['dish_type']
        
        # Performance score
        perf_score, perf_evidence = calculate_performance_score(row, config)
        
        # Opportunity score
        opp_score, opp_evidence, opp_components = calculate_opportunity_score(row, latent_df, config)
        
        # Unified score
        unified_score, score_type = calculate_unified_score(perf_score, opp_score, config)
        
        # Tier and quadrant
        tier = assign_tier(unified_score, config)
        has_perf_data = perf_score is not None and perf_evidence != 'no_data'
        is_on_dinneroo = row.get('on_dinneroo', True)
        quadrant = assign_quadrant(perf_score, opp_score, has_performance_data=has_perf_data, on_dinneroo=is_on_dinneroo)
        
        # Determine overall evidence level
        if perf_evidence == 'validated' or opp_evidence == 'validated':
            evidence_level = 'Validated'
        elif perf_evidence == 'corroborated' or opp_evidence == 'corroborated':
            evidence_level = 'Corroborated'
        else:
            evidence_level = 'Estimated'
        
        results.append({
            'rank': 0,  # Will be set after sorting
            'dish_type': dish_type,
            'cuisine': row.get('cuisine', ''),
            'on_dinneroo': row.get('on_dinneroo', True),
            
            # Scores
            'performance_score': round(perf_score, 2) if perf_score else None,
            'opportunity_score': round(opp_score, 2),
            'unified_score': round(unified_score, 2),
            
            # Classification
            'tier': tier,
            'quadrant': quadrant,
            'evidence_level': evidence_level,
            
            # Performance components
            'order_volume': row.get('order_volume'),
            'avg_rating': row.get('avg_rating'),
            'adult_satisfaction': row.get('adult_satisfaction'),
            'kids_happy': row.get('kids_happy'),
            
            # Opportunity components
            'latent_demand_score': opp_components.get('latent_demand'),
            'adult_appeal': opp_components.get('adult_appeal'),
            'balanced_guilt_free': opp_components.get('balanced'),
            'fussy_eater_friendly': opp_components.get('fussy_eater'),
        })
    
    # Create DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('unified_score', ascending=False).reset_index(drop=True)
    results_df['rank'] = results_df.index + 1
    
    # Reorder columns
    col_order = ['rank', 'dish_type', 'cuisine', 'on_dinneroo', 'unified_score', 
                 'performance_score', 'opportunity_score', 'tier', 'quadrant', 
                 'evidence_level', 'order_volume', 'avg_rating', 'adult_satisfaction',
                 'kids_happy', 'latent_demand_score', 'adult_appeal', 
                 'balanced_guilt_free', 'fussy_eater_friendly']
    results_df = results_df[[c for c in col_order if c in results_df.columns]]
    
    # Limit to top 100
    results_df = results_df.head(100)
    
    print(f"   Scored {len(results_df)} dishes")
    
    # Save outputs
    print("\n5. Saving outputs...")
    
    # CSV
    csv_path = DATA_PATH / "3_ANALYSIS" / "priority_100_unified.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"   Saved CSV: {csv_path}")
    
    # JSON for dashboards
    json_path = BASE_PATH / "docs" / "data" / "priority_100_unified.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    json_data = {
        'generated': datetime.now().isoformat(),
        'framework_version': config['version'],
        'total_dishes': len(results_df),
        'tier_distribution': results_df['tier'].value_counts().to_dict(),
        'quadrant_distribution': results_df['quadrant'].value_counts().to_dict(),
        'dishes': results_df.to_dict('records')
    }
    
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"   Saved JSON: {json_path}")
    
    # 2x2 Matrix CSV
    matrix_df = results_df[['dish_type', 'performance_score', 'opportunity_score', 'quadrant', 'unified_score']].copy()
    matrix_path = DATA_PATH / "3_ANALYSIS" / "dish_2x2_unified.csv"
    matrix_df.to_csv(matrix_path, index=False)
    print(f"   Saved 2x2 matrix: {matrix_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print("\nTier Distribution:")
    for tier, count in results_df['tier'].value_counts().items():
        print(f"  {tier}: {count}")
    
    print("\nQuadrant Distribution:")
    for quad, count in results_df['quadrant'].value_counts().items():
        print(f"  {quad}: {count}")
    
    print("\nEvidence Level Distribution:")
    for level, count in results_df['evidence_level'].value_counts().items():
        print(f"  {level}: {count}")
    
    print("\nTop 15 Dishes:")
    print(results_df[['rank', 'dish_type', 'unified_score', 'tier', 'on_dinneroo']].head(15).to_string(index=False))
    
    print("\n✓ Unified dish scoring complete!")
    
    return results_df

if __name__ == "__main__":
    main()
