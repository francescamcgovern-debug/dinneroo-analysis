#!/usr/bin/env python3
"""
Hierarchical MVP Threshold Discovery

Discovers data-driven thresholds for MVP zone criteria by:
1. Starting with partner count (most controllable lever)
2. Then cuisine count WITHIN partner buckets (controlling for partners)
3. Then dish count WITHIN partner × cuisine buckets (controlling for both)

This approach avoids spurious correlations where "more cuisines = better" 
might just be a proxy for "more partners = better".

Metrics used:
- Tier 1 (Core Success): repeat_rate, kids_happy, liked_loved
- Tier 2 (Supporting): avg_rating, reorder_intent, enough_food
- Tier 3 (Diagnostic): order_volume, food_hot, food_on_time
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "DATA"
OUTPUT_DIR = DATA_DIR / "3_ANALYSIS"

# Input files
ORDERS_FILE = DATA_DIR / "1_SOURCE" / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
RATINGS_FILE = DATA_DIR / "1_SOURCE" / "snowflake" / "DINNEROO_RATINGS.csv"
SURVEY_FILE = DATA_DIR / "2_ENRICHED" / "post_order_enriched_COMPLETE.csv"
ZONE_STATS_FILE = DATA_DIR / "3_ANALYSIS" / "zone_quality_scores.csv"
ANNA_ZONE_DISHES_FILE = DATA_DIR / "3_ANALYSIS" / "anna_zone_dish_counts.csv"  # Curated Dinneroo dishes

# Minimum sample sizes for reliable metrics
MIN_BEHAVIORAL_SAMPLE = 30  # Orders/ratings for behavioral metrics
MIN_SURVEY_SAMPLE = 20      # Survey responses for survey metrics

def load_data():
    """Load all required data files."""
    print("Loading data files...")
    
    # Zone stats with partner/cuisine/dish counts
    zone_stats = pd.read_csv(ZONE_STATS_FILE)
    print(f"  Zone stats: {len(zone_stats)} zones")
    
    # Anna's curated Dinneroo dish counts per zone
    anna_dishes = pd.read_csv(ANNA_ZONE_DISHES_FILE)
    print(f"  Anna zone dishes: {len(anna_dishes)} zones")
    
    # Orders for repeat rate calculation
    orders = pd.read_csv(ORDERS_FILE)
    print(f"  Orders: {len(orders)} orders")
    
    # Ratings
    ratings = pd.read_csv(RATINGS_FILE)
    print(f"  Ratings: {len(ratings)} ratings")
    
    # Survey responses
    survey = pd.read_csv(SURVEY_FILE, low_memory=False)
    print(f"  Survey responses: {len(survey)} responses")
    
    return zone_stats, anna_dishes, orders, ratings, survey


def calculate_repeat_rate_by_zone(orders):
    """Calculate repeat rate (% customers with 2+ orders) per zone."""
    # Count orders per customer per zone
    customer_orders = orders.groupby(['ZONE_NAME', 'CUSTOMER_ID']).size().reset_index(name='order_count')
    
    # For each zone, calculate % of customers with 2+ orders
    zone_repeat = customer_orders.groupby('ZONE_NAME').agg(
        total_customers=('CUSTOMER_ID', 'nunique'),
        repeat_customers=('order_count', lambda x: (x >= 2).sum())
    ).reset_index()
    
    zone_repeat['repeat_rate'] = zone_repeat['repeat_customers'] / zone_repeat['total_customers']
    
    return zone_repeat[['ZONE_NAME', 'repeat_rate', 'total_customers']]


def calculate_rating_by_zone(ratings):
    """Calculate average rating per zone."""
    zone_ratings = ratings.groupby('ZONE_NAME').agg(
        avg_rating=('RATING_STARS', 'mean'),
        rating_count=('RATING_STARS', 'count')
    ).reset_index()
    
    return zone_ratings


def calculate_survey_metrics_by_zone(survey):
    """Calculate survey-based metrics per zone."""
    # Filter to completed surveys with zone linkage
    valid_survey = survey[
        (survey['Status'] == 'Complete') & 
        (survey['ZONE_NAME'].notna()) &
        (survey['LINKAGE_METHOD'] != 'unmatched')
    ].copy()
    
    print(f"  Valid linked survey responses: {len(valid_survey)}")
    
    # Kids happy metric - only for family orders
    # Column: "Child 1 (youngest):How did your child(ren) react to the meal?"
    # Values: "They ate all parts of the dish and were full and happy", 
    #         "They ate some parts of the dish, but were full and happy", etc.
    child_col = "Child 1 (youngest):How did your child(ren) react to the meal?"
    if child_col in valid_survey.columns:
        valid_survey['kids_happy'] = valid_survey[child_col].apply(
            lambda x: 1 if pd.notna(x) and 'full and happy' in str(x).lower() else 
                     (0 if pd.notna(x) and x != '' else np.nan)
        )
    else:
        valid_survey['kids_happy'] = np.nan
    
    # Liked/Loved metric
    # Column: "How did you feel about the meal?"
    # Values: "Loved it", "Liked it", "Neutral", "Did not enjoy it"
    meal_col = "How did you feel about the meal?"
    if meal_col in valid_survey.columns:
        valid_survey['liked_loved'] = valid_survey[meal_col].apply(
            lambda x: 1 if pd.notna(x) and str(x).lower() in ['loved it', 'liked it'] else 
                     (0 if pd.notna(x) and x != '' else np.nan)
        )
    else:
        valid_survey['liked_loved'] = np.nan
    
    # Reorder intent
    # Column pattern: "I would like order the same dish again" or similar
    reorder_cols = [c for c in valid_survey.columns if 'order the same dish again' in c.lower() or 
                    'order the same dish again' in c.lower()]
    if reorder_cols:
        reorder_col = reorder_cols[0]
        valid_survey['reorder_intent'] = valid_survey[reorder_col].apply(
            lambda x: 1 if pd.notna(x) and str(x).lower() in ['strongly agree', 'agree'] else 
                     (0 if pd.notna(x) and x != '' else np.nan)
        )
    else:
        valid_survey['reorder_intent'] = np.nan
    
    # Enough food metric
    enough_col = "There was enough food for everyone:Please rate how much you agree or disagree with the following statements:"
    if enough_col in valid_survey.columns:
        valid_survey['enough_food'] = valid_survey[enough_col].apply(
            lambda x: 1 if pd.notna(x) and str(x).lower() in ['strongly agree', 'agree'] else 
                     (0 if pd.notna(x) and x != '' else np.nan)
        )
    else:
        valid_survey['enough_food'] = np.nan
    
    # Food hot metric
    hot_col = "The food arrived hot:Please rate how much you agree or disagree with the following statements:"
    if hot_col in valid_survey.columns:
        valid_survey['food_hot'] = valid_survey[hot_col].apply(
            lambda x: 1 if pd.notna(x) and str(x).lower() in ['strongly agree', 'agree'] else 
                     (0 if pd.notna(x) and x != '' else np.nan)
        )
    else:
        valid_survey['food_hot'] = np.nan
    
    # Food on time metric
    time_col = "The food arrived on time:Please rate how much you agree or disagree with the following statements:"
    if time_col in valid_survey.columns:
        valid_survey['food_on_time'] = valid_survey[time_col].apply(
            lambda x: 1 if pd.notna(x) and str(x).lower() in ['strongly agree', 'agree'] else 
                     (0 if pd.notna(x) and x != '' else np.nan)
        )
    else:
        valid_survey['food_on_time'] = np.nan
    
    # Aggregate by zone
    zone_survey = valid_survey.groupby('ZONE_NAME').agg(
        kids_happy=('kids_happy', 'mean'),
        kids_happy_n=('kids_happy', lambda x: x.notna().sum()),
        liked_loved=('liked_loved', 'mean'),
        liked_loved_n=('liked_loved', lambda x: x.notna().sum()),
        reorder_intent=('reorder_intent', 'mean'),
        reorder_intent_n=('reorder_intent', lambda x: x.notna().sum()),
        enough_food=('enough_food', 'mean'),
        enough_food_n=('enough_food', lambda x: x.notna().sum()),
        food_hot=('food_hot', 'mean'),
        food_hot_n=('food_hot', lambda x: x.notna().sum()),
        food_on_time=('food_on_time', 'mean'),
        food_on_time_n=('food_on_time', lambda x: x.notna().sum()),
        survey_count=('ZONE_NAME', 'count')
    ).reset_index()
    
    return zone_survey


def merge_zone_data(zone_stats, anna_dishes, repeat_rates, ratings, survey_metrics):
    """Merge all zone-level data into single dataframe."""
    # Start with zone stats
    df = zone_stats[['ZONE_NAME', 'DINNEROO_PARTNER_COUNT', 'DINNEROO_CUISINE_COUNT', 
                     'TOTAL_DINNEROO_ORDERS']].copy()
    
    # Rename for clarity
    df = df.rename(columns={
        'DINNEROO_PARTNER_COUNT': 'partners',
        'DINNEROO_CUISINE_COUNT': 'cuisines',
        'TOTAL_DINNEROO_ORDERS': 'orders'
    })
    
    # Merge Anna's curated Dinneroo dish counts
    # Anna's data uses 'zone_name' column
    anna_dish_counts = anna_dishes[['zone_name', 'total_dishes', 'num_cuisines', 'num_brands']].copy()
    anna_dish_counts = anna_dish_counts.rename(columns={
        'zone_name': 'ZONE_NAME',
        'total_dishes': 'dinneroo_dishes',  # Curated Dinneroo dishes (not all menu items)
        'num_cuisines': 'anna_cuisines',
        'num_brands': 'anna_partners'
    })
    df = df.merge(anna_dish_counts, on='ZONE_NAME', how='left')
    
    # Use Anna's dish count as primary, fall back to 0 if not available
    df['dishes'] = df['dinneroo_dishes'].fillna(0).astype(int)
    
    # Merge repeat rates
    df = df.merge(repeat_rates, on='ZONE_NAME', how='left')
    
    # Merge ratings
    df = df.merge(ratings, on='ZONE_NAME', how='left')
    
    # Merge survey metrics
    df = df.merge(survey_metrics, on='ZONE_NAME', how='left')
    
    print(f"\nMerged zone data: {len(df)} zones")
    print(f"  With repeat rate: {df['repeat_rate'].notna().sum()}")
    print(f"  With ratings: {df['avg_rating'].notna().sum()}")
    print(f"  With survey data: {df['survey_count'].notna().sum()}")
    print(f"  With Dinneroo dish data: {(df['dishes'] > 0).sum()}")
    print(f"  Dish count range: {df['dishes'].min()} - {df['dishes'].max()}")
    
    return df


def create_buckets(df, column, bucket_config):
    """Create buckets for a given column based on configuration."""
    df = df.copy()
    bucket_col = f'{column}_bucket'
    
    conditions = []
    labels = []
    
    for label, (low, high) in bucket_config.items():
        if high is None:
            conditions.append(df[column] >= low)
        else:
            conditions.append((df[column] >= low) & (df[column] <= high))
        labels.append(label)
    
    df[bucket_col] = np.select(conditions, labels, default='Unknown')
    
    return df


def calculate_bucket_metrics(df, bucket_col):
    """Calculate all metrics for each bucket."""
    results = []
    
    for bucket in df[bucket_col].unique():
        bucket_df = df[df[bucket_col] == bucket]
        
        # Behavioral metrics
        behavioral = {
            'repeat_rate': {
                'value': bucket_df['repeat_rate'].mean() if bucket_df['repeat_rate'].notna().any() else None,
                'n': int(bucket_df['total_customers'].sum()) if 'total_customers' in bucket_df.columns else len(bucket_df),
                'reliable': bucket_df['total_customers'].sum() >= MIN_BEHAVIORAL_SAMPLE if 'total_customers' in bucket_df.columns else len(bucket_df) >= MIN_BEHAVIORAL_SAMPLE
            },
            'avg_rating': {
                'value': bucket_df['avg_rating'].mean() if bucket_df['avg_rating'].notna().any() else None,
                'n': int(bucket_df['rating_count'].sum()) if 'rating_count' in bucket_df.columns else len(bucket_df),
                'reliable': bucket_df['rating_count'].sum() >= MIN_BEHAVIORAL_SAMPLE if 'rating_count' in bucket_df.columns else len(bucket_df) >= MIN_BEHAVIORAL_SAMPLE
            },
            'order_volume': {
                'value': bucket_df['orders'].mean() if 'orders' in bucket_df.columns else None,
                'n': len(bucket_df),
                'reliable': True
            }
        }
        
        # Survey metrics
        survey = {}
        for metric in ['kids_happy', 'liked_loved', 'reorder_intent', 'enough_food', 'food_hot', 'food_on_time']:
            n_col = f'{metric}_n'
            if metric in bucket_df.columns:
                total_n = int(bucket_df[n_col].sum()) if n_col in bucket_df.columns else 0
                survey[metric] = {
                    'value': bucket_df[metric].mean() if bucket_df[metric].notna().any() else None,
                    'n': total_n,
                    'reliable': total_n >= MIN_SURVEY_SAMPLE
                }
            else:
                survey[metric] = {'value': None, 'n': 0, 'reliable': False}
        
        results.append({
            'bucket': bucket,
            'zones': len(bucket_df),
            'behavioral': behavioral,
            'survey': survey
        })
    
    return results


def bucket_sort_key(bucket_name):
    """Extract numeric value for sorting buckets like '1-2', '3-4', '5-6', '7-9', '10+'."""
    # Handle "Unknown" bucket
    if bucket_name == 'Unknown':
        return 9999  # Sort to end
    # Handle formats: "1-2", "10+", "5-6", "3.5-4.5" etc.
    if '+' in bucket_name:
        try:
            return float(bucket_name.replace('+', ''))
        except ValueError:
            return 9999
    elif '-' in bucket_name:
        try:
            return float(bucket_name.split('-')[0])
        except ValueError:
            return 9999
    else:
        try:
            return float(bucket_name)
        except ValueError:
            return 9999


def find_inflection_point(bucket_metrics, metric_name, is_survey=False):
    """Find the biggest CONSECUTIVE improvement between buckets for a metric."""
    # Sort buckets by their numeric order
    sorted_buckets = sorted(bucket_metrics, key=lambda x: bucket_sort_key(x['bucket']))
    
    max_delta = 0
    inflection = None
    all_transitions = []
    
    for i in range(len(sorted_buckets) - 1):
        current = sorted_buckets[i]
        next_bucket = sorted_buckets[i + 1]
        
        if is_survey:
            current_val = current['survey'].get(metric_name, {}).get('value')
            next_val = next_bucket['survey'].get(metric_name, {}).get('value')
            current_reliable = current['survey'].get(metric_name, {}).get('reliable', False)
            next_reliable = next_bucket['survey'].get(metric_name, {}).get('reliable', False)
        else:
            current_val = current['behavioral'].get(metric_name, {}).get('value')
            next_val = next_bucket['behavioral'].get(metric_name, {}).get('value')
            current_reliable = current['behavioral'].get(metric_name, {}).get('reliable', False)
            next_reliable = next_bucket['behavioral'].get(metric_name, {}).get('reliable', False)
        
        if current_val is not None and next_val is not None:
            delta = next_val - current_val
            transition = {
                'from': current['bucket'],
                'to': next_bucket['bucket'],
                'delta': round(delta, 4),
                'delta_pct': f"+{round(delta * 100, 1)}pp" if delta > 0 else f"{round(delta * 100, 1)}pp",
                'reliable': current_reliable and next_reliable
            }
            all_transitions.append(transition)
            
            # Only consider positive improvements for threshold recommendation
            if delta > max_delta:
                max_delta = delta
                inflection = transition
    
    # Return the inflection (without embedding all_transitions to avoid circular reference)
    return inflection


def analyze_partners(df):
    """Step 1: Analyze partner count impact on success metrics."""
    print("\n" + "="*60)
    print("STEP 1: Partner Count Analysis")
    print("="*60)
    
    # Define partner buckets
    partner_buckets = {
        '1-2': (1, 2),
        '3-4': (3, 4),
        '5-6': (5, 6),
        '7-9': (7, 9),
        '10+': (10, None)
    }
    
    df_bucketed = create_buckets(df, 'partners', partner_buckets)
    bucket_metrics = calculate_bucket_metrics(df_bucketed, 'partners_bucket')
    
    # Find inflection points for each metric
    inflections = {
        'repeat_rate': find_inflection_point(bucket_metrics, 'repeat_rate', is_survey=False),
        'avg_rating': find_inflection_point(bucket_metrics, 'avg_rating', is_survey=False),
        'kids_happy': find_inflection_point(bucket_metrics, 'kids_happy', is_survey=True),
        'liked_loved': find_inflection_point(bucket_metrics, 'liked_loved', is_survey=True),
        'reorder_intent': find_inflection_point(bucket_metrics, 'reorder_intent', is_survey=True)
    }
    
    # Determine consensus threshold
    threshold_votes = defaultdict(int)
    for metric, inflection in inflections.items():
        if inflection and inflection.get('reliable', False):
            threshold_votes[inflection['to']] += 1
    
    recommended_threshold = max(threshold_votes, key=threshold_votes.get) if threshold_votes else '5-6'
    
    # Print summary
    for bucket in sorted(bucket_metrics, key=lambda x: x['bucket']):
        print(f"\n  {bucket['bucket']} partners ({bucket['zones']} zones):")
        print(f"    Repeat rate: {bucket['behavioral']['repeat_rate']['value']:.1%}" if bucket['behavioral']['repeat_rate']['value'] else "    Repeat rate: N/A")
        print(f"    Avg rating: {bucket['behavioral']['avg_rating']['value']:.2f}" if bucket['behavioral']['avg_rating']['value'] else "    Avg rating: N/A")
        print(f"    Kids happy: {bucket['survey']['kids_happy']['value']:.1%} (n={bucket['survey']['kids_happy']['n']})" if bucket['survey']['kids_happy']['value'] else "    Kids happy: N/A")
        print(f"    Liked/Loved: {bucket['survey']['liked_loved']['value']:.1%} (n={bucket['survey']['liked_loved']['n']})" if bucket['survey']['liked_loved']['value'] else "    Liked/Loved: N/A")
    
    return {
        'total_zones_analyzed': len(df),
        'by_partner_count': bucket_metrics,
        'inflection_analysis': inflections,
        'consensus': dict(threshold_votes),
        'recommendation': {
            'threshold': recommended_threshold,
            'confidence': 'HIGH' if threshold_votes[recommended_threshold] >= 3 else 'MEDIUM' if threshold_votes[recommended_threshold] >= 2 else 'LOW',
            'rationale': f"{threshold_votes[recommended_threshold]} of {len([i for i in inflections.values() if i])} metrics show inflection at {recommended_threshold}"
        }
    }


def analyze_cuisines_within_partners(df, partner_threshold):
    """Step 2: Analyze cuisine count impact, controlling for partner count."""
    print("\n" + "="*60)
    print(f"STEP 2: Cuisine Count Analysis (within {partner_threshold}+ partners)")
    print("="*60)
    
    # Parse partner threshold
    if partner_threshold.endswith('+'):
        min_partners = int(partner_threshold[:-1])
    else:
        min_partners = int(partner_threshold.split('-')[0])
    
    # Filter to zones meeting partner threshold
    df_filtered = df[df['partners'] >= min_partners].copy()
    print(f"  Zones meeting partner threshold: {len(df_filtered)}")
    
    # Define cuisine buckets
    cuisine_buckets = {
        '1-2': (1, 2),
        '3-4': (3, 4),
        '5-6': (5, 6),
        '7+': (7, None)
    }
    
    df_bucketed = create_buckets(df_filtered, 'cuisines', cuisine_buckets)
    bucket_metrics = calculate_bucket_metrics(df_bucketed, 'cuisines_bucket')
    
    # Find inflection points
    inflections = {
        'repeat_rate': find_inflection_point(bucket_metrics, 'repeat_rate', is_survey=False),
        'avg_rating': find_inflection_point(bucket_metrics, 'avg_rating', is_survey=False),
        'kids_happy': find_inflection_point(bucket_metrics, 'kids_happy', is_survey=True),
        'liked_loved': find_inflection_point(bucket_metrics, 'liked_loved', is_survey=True),
        'reorder_intent': find_inflection_point(bucket_metrics, 'reorder_intent', is_survey=True)
    }
    
    # Check if cuisines add independent value
    significant_inflections = [i for i in inflections.values() if i and i.get('reliable', False) and i.get('delta', 0) > 0.02]
    adds_value = len(significant_inflections) >= 2
    
    # Determine threshold
    threshold_votes = defaultdict(int)
    for metric, inflection in inflections.items():
        if inflection and inflection.get('reliable', False):
            threshold_votes[inflection['to']] += 1
    
    recommended_threshold = max(threshold_votes, key=threshold_votes.get) if threshold_votes else None
    
    # Print summary
    for bucket in sorted(bucket_metrics, key=lambda x: x['bucket']):
        print(f"\n  {bucket['bucket']} cuisines ({bucket['zones']} zones):")
        print(f"    Repeat rate: {bucket['behavioral']['repeat_rate']['value']:.1%}" if bucket['behavioral']['repeat_rate']['value'] else "    Repeat rate: N/A")
        print(f"    Avg rating: {bucket['behavioral']['avg_rating']['value']:.2f}" if bucket['behavioral']['avg_rating']['value'] else "    Avg rating: N/A")
    
    return {
        'filter_applied': f"Only zones with {min_partners}+ partners",
        'zones_after_filter': len(df_filtered),
        'by_cuisine_count': bucket_metrics,
        'inflection_analysis': inflections,
        'adds_independent_value': adds_value,
        'recommendation': {
            'threshold': recommended_threshold if adds_value else 'N/A - driven by partners',
            'confidence': 'HIGH' if adds_value and threshold_votes.get(recommended_threshold, 0) >= 2 else 'LOW',
            'rationale': f"{'Cuisines add value beyond partners' if adds_value else 'Cuisine effect appears driven by partner count'}"
        }
    }


def analyze_dishes_within_partners_and_cuisines(df, partner_threshold, cuisine_threshold):
    """Step 3: Analyze Dinneroo dish count impact, controlling for partners and cuisines.
    
    Analyzes BOTH:
    - Dishes per zone (total supply breadth)
    - Dishes per partner (menu depth per partner)
    """
    print("\n" + "="*60)
    print(f"STEP 3: Dinneroo Dish Count Analysis (within {partner_threshold}+ partners, {cuisine_threshold}+ cuisines)")
    print("="*60)
    
    # Parse thresholds
    if partner_threshold.endswith('+'):
        min_partners = int(partner_threshold[:-1])
    else:
        min_partners = int(partner_threshold.split('-')[0])
    
    if cuisine_threshold and cuisine_threshold != 'N/A - driven by partners':
        if cuisine_threshold.endswith('+'):
            min_cuisines = int(cuisine_threshold[:-1])
        else:
            min_cuisines = int(cuisine_threshold.split('-')[0])
    else:
        min_cuisines = 0  # No cuisine filter if not applicable
    
    # Filter to zones meeting both thresholds AND having Dinneroo dishes
    df_filtered = df[
        (df['partners'] >= min_partners) & 
        (df['cuisines'] >= min_cuisines) &
        (df['dishes'] > 0)  # Only zones with actual Dinneroo dishes
    ].copy()
    
    # Calculate dishes per partner
    df_filtered['dishes_per_partner'] = df_filtered['dishes'] / df_filtered['partners']
    
    print(f"  Zones meeting thresholds with Dinneroo dishes: {len(df_filtered)}")
    print(f"  Dishes per ZONE range: {df_filtered['dishes'].min()} - {df_filtered['dishes'].max()}")
    print(f"  Dishes per PARTNER range: {df_filtered['dishes_per_partner'].min():.1f} - {df_filtered['dishes_per_partner'].max():.1f}")
    
    if len(df_filtered) < 10:
        print("  WARNING: Too few zones for reliable analysis")
        return {
            'filter_applied': f"Only zones with {min_partners}+ partners AND {min_cuisines}+ cuisines AND Dinneroo dishes",
            'zones_after_filter': len(df_filtered),
            'dishes_per_zone': {},
            'dishes_per_partner': {},
            'adds_independent_value': False,
            'recommendation': {
                'threshold': 'N/A - insufficient data',
                'confidence': 'LOW',
                'rationale': 'Too few zones for reliable analysis'
            }
        }
    
    # ========================================
    # ANALYSIS A: Dishes per ZONE (total supply breadth)
    # ========================================
    print("\n  --- A: Dishes per ZONE (total supply breadth) ---")
    
    zone_dish_buckets = {
        '1-15': (1, 15),
        '16-30': (16, 30),
        '31-50': (31, 50),
        '51+': (51, None)
    }
    
    df_zone_bucketed = create_buckets(df_filtered, 'dishes', zone_dish_buckets)
    zone_bucket_metrics = calculate_bucket_metrics(df_zone_bucketed, 'dishes_bucket')
    
    zone_inflections = {
        'repeat_rate': find_inflection_point(zone_bucket_metrics, 'repeat_rate', is_survey=False),
        'avg_rating': find_inflection_point(zone_bucket_metrics, 'avg_rating', is_survey=False),
        'kids_happy': find_inflection_point(zone_bucket_metrics, 'kids_happy', is_survey=True),
        'liked_loved': find_inflection_point(zone_bucket_metrics, 'liked_loved', is_survey=True)
    }
    
    for bucket in sorted(zone_bucket_metrics, key=lambda x: bucket_sort_key(x['bucket'])):
        rr = bucket['behavioral']['repeat_rate']['value']
        kh = bucket['survey']['kids_happy']['value']
        kh_n = bucket['survey']['kids_happy']['n']
        print(f"    {bucket['bucket']} dishes/zone ({bucket['zones']} zones): ", end="")
        print(f"Repeat={rr:.1%}" if rr else "Repeat=N/A", end="")
        print(f", Kids Happy={kh:.1%} (n={kh_n})" if kh else "")
    
    # ========================================
    # ANALYSIS B: Dishes per PARTNER (menu depth)
    # ========================================
    print("\n  --- B: Dishes per PARTNER (menu depth) ---")
    
    # Dishes per partner typically ranges from 3-10 based on Anna's data (mean ~4.5)
    partner_dish_buckets = {
        '3-4': (3, 4),
        '4-5': (4.01, 5),
        '5-6': (5.01, 6),
        '6+': (6.01, None)
    }
    
    df_partner_bucketed = create_buckets(df_filtered, 'dishes_per_partner', partner_dish_buckets)
    partner_bucket_metrics = calculate_bucket_metrics(df_partner_bucketed, 'dishes_per_partner_bucket')
    
    partner_inflections = {
        'repeat_rate': find_inflection_point(partner_bucket_metrics, 'repeat_rate', is_survey=False),
        'avg_rating': find_inflection_point(partner_bucket_metrics, 'avg_rating', is_survey=False),
        'kids_happy': find_inflection_point(partner_bucket_metrics, 'kids_happy', is_survey=True),
        'liked_loved': find_inflection_point(partner_bucket_metrics, 'liked_loved', is_survey=True)
    }
    
    for bucket in sorted(partner_bucket_metrics, key=lambda x: bucket_sort_key(x['bucket'])):
        rr = bucket['behavioral']['repeat_rate']['value']
        kh = bucket['survey']['kids_happy']['value']
        kh_n = bucket['survey']['kids_happy']['n']
        print(f"    {bucket['bucket']} dishes/partner ({bucket['zones']} zones): ", end="")
        print(f"Repeat={rr:.1%}" if rr else "Repeat=N/A", end="")
        print(f", Kids Happy={kh:.1%} (n={kh_n})" if kh else "")
    
    # Check if either approach shows independent value
    zone_significant = [i for i in zone_inflections.values() if i and i.get('reliable', False) and i.get('delta', 0) > 0.02]
    partner_significant = [i for i in partner_inflections.values() if i and i.get('reliable', False) and i.get('delta', 0) > 0.02]
    
    adds_value = len(zone_significant) >= 2 or len(partner_significant) >= 2
    
    # Determine which approach is stronger
    zone_strength = len(zone_significant)
    partner_strength = len(partner_significant)
    
    if partner_strength > zone_strength:
        preferred_approach = "dishes_per_partner"
        preferred_rationale = "Dishes per partner shows stronger independent effect"
    elif zone_strength > partner_strength:
        preferred_approach = "dishes_per_zone"
        preferred_rationale = "Total dishes per zone shows stronger independent effect"
    else:
        preferred_approach = "either"
        preferred_rationale = "Both approaches show similar effects"
    
    print(f"\n  Preferred approach: {preferred_approach}")
    print(f"  Rationale: {preferred_rationale}")
    
    return {
        'filter_applied': f"Only zones with {min_partners}+ partners AND {min_cuisines}+ cuisines AND Dinneroo dishes",
        'zones_after_filter': len(df_filtered),
        'dishes_per_zone': {
            'buckets': zone_bucket_metrics,
            'inflection_analysis': zone_inflections,
            'significant_inflections': zone_strength
        },
        'dishes_per_partner': {
            'buckets': partner_bucket_metrics,
            'inflection_analysis': partner_inflections,
            'significant_inflections': partner_strength
        },
        'preferred_approach': preferred_approach,
        'adds_independent_value': adds_value,
        'recommendation': {
            'threshold': 'TBD based on inflection' if adds_value else 'N/A - driven by partners/cuisines',
            'confidence': 'MEDIUM' if adds_value else 'LOW',
            'rationale': preferred_rationale if adds_value else 'Dish effect appears driven by partner/cuisine count'
        }
    }


def calculate_correlations(df):
    """Calculate correlations between partners, cuisines, and dishes."""
    corr_matrix = df[['partners', 'cuisines', 'dishes']].corr()
    
    return {
        'partner_cuisine': round(corr_matrix.loc['partners', 'cuisines'], 3),
        'partner_dish': round(corr_matrix.loc['partners', 'dishes'], 3),
        'cuisine_dish': round(corr_matrix.loc['cuisines', 'dishes'], 3),
        'warnings': [
            f"High correlation ({corr_matrix.loc['partners', 'cuisines']:.2f}) between partners and cuisines - interpret with caution"
            if corr_matrix.loc['partners', 'cuisines'] > 0.7 else None,
            f"High correlation ({corr_matrix.loc['partners', 'dishes']:.2f}) between partners and dishes - interpret with caution"
            if corr_matrix.loc['partners', 'dishes'] > 0.7 else None
        ]
    }


def generate_final_recommendations(partner_result, cuisine_result, dish_result, correlations):
    """Synthesize findings into final recommendations."""
    recommendations = []
    
    # Partner recommendation (always primary)
    recommendations.append({
        'criterion': 'partners',
        'threshold': partner_result['recommendation']['threshold'],
        'confidence': partner_result['recommendation']['confidence'],
        'is_primary': True,
        'evidence_summary': partner_result['recommendation']['rationale']
    })
    
    # Cuisine recommendation
    if cuisine_result['adds_independent_value']:
        recommendations.append({
            'criterion': 'cuisines',
            'threshold': cuisine_result['recommendation']['threshold'],
            'confidence': cuisine_result['recommendation']['confidence'],
            'is_primary': False,
            'adds_value_beyond_partners': True,
            'evidence_summary': cuisine_result['recommendation']['rationale']
        })
    else:
        recommendations.append({
            'criterion': 'cuisines',
            'threshold': 'REMOVE - driven by partners',
            'confidence': 'HIGH',
            'is_primary': False,
            'adds_value_beyond_partners': False,
            'evidence_summary': 'Cuisine effect is a proxy for partner count'
        })
    
    # Dish recommendation
    if dish_result['adds_independent_value']:
        recommendations.append({
            'criterion': 'dishes',
            'threshold': dish_result['recommendation']['threshold'],
            'confidence': dish_result['recommendation']['confidence'],
            'is_primary': False,
            'adds_value_beyond_above': True,
            'evidence_summary': dish_result['recommendation']['rationale']
        })
    else:
        recommendations.append({
            'criterion': 'dishes',
            'threshold': 'REMOVE - driven by partners/cuisines',
            'confidence': 'HIGH',
            'is_primary': False,
            'adds_value_beyond_above': False,
            'evidence_summary': 'Dish effect is a proxy for partner/cuisine count'
        })
    
    # Check if simplification is possible
    simplification_possible = not cuisine_result['adds_independent_value'] or not dish_result['adds_independent_value']
    
    return {
        'mvp_criteria': recommendations,
        'simplification_possible': simplification_possible,
        'simplification_note': 'MVP may be simplified to just partner count' if simplification_possible else 'All three criteria add independent value'
    }


def main():
    """Run the hierarchical threshold discovery analysis."""
    print("="*60)
    print("HIERARCHICAL MVP THRESHOLD DISCOVERY")
    print("="*60)
    print(f"Run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    zone_stats, anna_dishes, orders, ratings, survey = load_data()
    
    # Calculate zone-level metrics
    print("\nCalculating zone-level metrics...")
    repeat_rates = calculate_repeat_rate_by_zone(orders)
    zone_ratings = calculate_rating_by_zone(ratings)
    survey_metrics = calculate_survey_metrics_by_zone(survey)
    
    # Merge all data (now including Anna's curated Dinneroo dish counts)
    df = merge_zone_data(zone_stats, anna_dishes, repeat_rates, zone_ratings, survey_metrics)
    
    # Calculate correlations
    correlations = calculate_correlations(df)
    print(f"\nCorrelations:")
    print(f"  Partners ↔ Cuisines: {correlations['partner_cuisine']}")
    print(f"  Partners ↔ Dishes: {correlations['partner_dish']}")
    print(f"  Cuisines ↔ Dishes: {correlations['cuisine_dish']}")
    
    # Step 1: Partner analysis
    partner_result = analyze_partners(df)
    partner_threshold = partner_result['recommendation']['threshold']
    
    # Step 2: Cuisine analysis (controlling for partners)
    cuisine_result = analyze_cuisines_within_partners(df, partner_threshold)
    cuisine_threshold = cuisine_result['recommendation']['threshold']
    
    # Step 3: Dish analysis (controlling for partners and cuisines)
    dish_result = analyze_dishes_within_partners_and_cuisines(df, partner_threshold, cuisine_threshold)
    
    # Generate final recommendations
    final_recommendations = generate_final_recommendations(
        partner_result, cuisine_result, dish_result, correlations
    )
    
    # Compile output
    output = {
        'generated': datetime.now().strftime('%Y-%m-%d'),
        'methodology': 'Hierarchical analysis - partners first, then cuisines controlling for partners, then dishes controlling for both',
        'metrics': {
            'tier_1_core': {
                'repeat_rate': {'source': 'Snowflake', 'definition': '% customers with 2+ orders'},
                'kids_happy': {'source': 'Survey', 'definition': '% Full and happy (families only)'},
                'liked_loved': {'source': 'Survey', 'definition': '% Loved it or Liked it'}
            },
            'tier_2_supporting': {
                'avg_rating': {'source': 'Snowflake', 'definition': 'Mean star rating'},
                'reorder_intent': {'source': 'Survey', 'definition': '% Agree/Strongly agree to reorder'},
                'enough_food': {'source': 'Survey', 'definition': '% Agree/Strongly agree portions adequate'}
            },
            'tier_3_diagnostic': {
                'order_volume': {'source': 'Snowflake', 'definition': 'Total orders'},
                'food_hot': {'source': 'Survey', 'definition': '% Agree/Strongly agree food hot'},
                'food_on_time': {'source': 'Survey', 'definition': '% Agree/Strongly agree on time'}
            }
        },
        'step_1_partners': partner_result,
        'step_2_cuisines_within_partners': cuisine_result,
        'step_3_dishes_within_partners_and_cuisines': dish_result,
        'correlations': correlations,
        'final_recommendations': final_recommendations,
        'data_quality_notes': {
            'zones_analyzed': len(df),
            'zones_with_repeat_rate': int(df['repeat_rate'].notna().sum()),
            'zones_with_ratings': int(df['avg_rating'].notna().sum()),
            'zones_with_survey': int(df['survey_count'].notna().sum()),
            'min_behavioral_sample': MIN_BEHAVIORAL_SAMPLE,
            'min_survey_sample': MIN_SURVEY_SAMPLE,
            'limitations': [
                'Survey sample sizes are small in some buckets',
                'Behavioral and survey data may not perfectly align',
                'Correlations between factors make independent effects hard to isolate'
            ]
        }
    }
    
    # Save output
    output_file = OUTPUT_DIR / 'mvp_threshold_discovery.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("FINAL RECOMMENDATIONS")
    print("="*60)
    for rec in final_recommendations['mvp_criteria']:
        print(f"\n  {rec['criterion'].upper()}:")
        print(f"    Threshold: {rec['threshold']}")
        print(f"    Confidence: {rec['confidence']}")
        print(f"    Evidence: {rec['evidence_summary']}")
    
    print(f"\n  Simplification possible: {final_recommendations['simplification_possible']}")
    print(f"  Note: {final_recommendations['simplification_note']}")
    
    print(f"\n\nOutput saved to: {output_file}")
    
    return output


if __name__ == '__main__':
    main()

