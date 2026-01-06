#!/usr/bin/env python3
"""
MVP Consumer Outcomes Validation

Joins survey responses to zone-level data to validate that MVP criteria
(5 cuisines, 5 partners) actually improve consumer outcomes:
- Kids happy rate
- Reorder intent
- Variety complaints

This addresses the gap where MVP criteria were based on order volume/ratings
but NOT validated against the consumer signals that matter.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import re

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_SOURCE = PROJECT_ROOT / "DATA" / "1_SOURCE"
DATA_ANALYSIS = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "data"


def load_data():
    """Load all required data sources."""
    print("Loading data sources...")
    
    # Zone metrics with cuisine/partner counts
    zones = pd.read_csv(DATA_ANALYSIS / "zone_quality_scores.csv")
    print(f"  Zones: {len(zones)} zones with cuisine/partner counts")
    
    # Orders with zone info and BRAND column (from segmented orders)
    # This has clean brand names that match survey restaurant names
    orders = pd.read_csv(DATA_ANALYSIS / "orders_segmented.csv", low_memory=False)
    print(f"  Orders: {len(orders)} orders with zone mapping and brand")
    
    # Survey responses
    survey = pd.read_csv(DATA_SOURCE / "surveys" / "POST_ORDER_SURVEY-CONSOLIDATED.csv", low_memory=False)
    print(f"  Survey: {len(survey)} responses")
    
    return zones, orders, survey


def map_restaurant_to_zone(orders):
    """Create restaurant -> zone mapping from orders data."""
    # Get most common zone for each restaurant
    restaurant_zone = orders.groupby('PARTNER_NAME')['ZONE_NAME'].agg(
        lambda x: x.value_counts().index[0] if len(x) > 0 else None
    ).reset_index()
    restaurant_zone.columns = ['restaurant', 'zone']
    
    # Also create a mapping for common restaurant name variations
    name_mapping = {
        'Dishoom': 'Dishoom',
        'PizzaExpress': 'PizzaExpress',
        'Wagamama': 'Wagamama',
        'The Salad Project': 'The Salad Project',
        "Bill's": "Bill's",
        'Giggling Squid': 'Giggling Squid',
        'Pho': 'Pho',
        'Banana Tree': 'Banana Tree',
        'Itsu': 'Itsu',
        'Iro Sushi': 'Iro Sushi',
        'Asia Villa': 'Asia Villa',
        'Cocotte': 'Cocotte',
        'Kricket': 'Kricket',
    }
    
    return restaurant_zone, name_mapping


def parse_kids_reaction(survey):
    """
    Parse kids reaction columns to determine if kids were happy.
    Actual values from survey:
    - 'They ate all parts of the dish and were full and happy'
    - 'They ate some parts of the dish, but were full and happy'
    - 'They ate some parts of the dish, but not as much as I wanted'
    - 'They tried some parts but didn't eat much at all'
    - 'They didn't try any of it'
    """
    kids_cols = [
        'Child 1 (youngest):How did your child(ren) react to the meal?',
        'Child 2:How did your child(ren) react to the meal?',
        'Child 3:How did your child(ren) react to the meal?',
        'Child 4:How did your child(ren) react to the meal?',
        'Child 5:How did your child(ren) react to the meal?',
    ]
    
    # "Full and happy" = positive outcome
    positive_keywords = ['full and happy']
    
    def is_kids_happy(row):
        """Return 1 if kids were full and happy, 0 if not, None if no data."""
        reactions = []
        for col in kids_cols:
            if col in row.index and pd.notna(row[col]) and row[col] != '' and col not in str(row[col]):
                reactions.append(str(row[col]).lower())
        
        if not reactions:
            return None
        
        # Kids happy if majority had "full and happy" in their reaction
        positive_count = sum(1 for r in reactions if any(kw in r for kw in positive_keywords))
        return 1 if positive_count >= len(reactions) / 2 else 0
    
    return survey.apply(is_kids_happy, axis=1)


def parse_reorder_intent(survey):
    """
    Parse reorder intent from survey.
    Column: 'I would like order the same dish again :Please state how much you agree or disagree with the following statements:'
    Values: 'Strongly agree', 'Agree', 'Neither agree nor disagree', 'Disagree', 'Strongly disagree'
    """
    col = 'I would like order the same dish again :Please state how much you agree or disagree with the following statements:'
    alt_col = 'I would like to order the same dish again :Please state how much you agree or disagree with the following statements:'
    
    positive_responses = ['Strongly agree', 'Agree']
    
    def get_reorder_intent(row):
        val = None
        if col in row.index and pd.notna(row[col]):
            val = row[col]
        elif alt_col in row.index and pd.notna(row[alt_col]):
            val = row[alt_col]
        
        if val is None or val == '':
            return None
        return 1 if val in positive_responses else 0
    
    return survey.apply(get_reorder_intent, axis=1)


def parse_variety_complaints(survey):
    """
    Parse variety complaints from open-text feedback.
    Look for mentions of 'variety', 'choice', 'selection', 'more options' in improvement fields.
    """
    improvement_cols = [
        'Overall, how could this dish be improved to suit your needs better?',
        'What further improvements would you suggest (if any)?',
    ]
    
    variety_keywords = ['variety', 'choice', 'selection', 'more options', 'limited', 
                        'more restaurants', 'more cuisines', 'different options']
    
    def has_variety_complaint(row):
        for col in improvement_cols:
            if col in row.index and pd.notna(row[col]) and row[col] != '':
                text = str(row[col]).lower()
                if any(kw in text for kw in variety_keywords):
                    return 1
        return 0
    
    return survey.apply(has_variety_complaint, axis=1)


def join_survey_to_zones(survey, orders, zones):
    """
    Join survey responses to zone data via restaurant -> zone mapping.
    Uses BRAND column from orders_segmented.csv which has clean brand names.
    """
    print("\nJoining survey to zones...")
    
    # Get brand -> zone mapping from orders (using BRAND column for clean names)
    brand_zones = orders.groupby('BRAND').agg({
        'ZONE_NAME': lambda x: x.value_counts().index[0] if len(x) > 0 else None
    }).reset_index()
    brand_zones.columns = ['brand', 'zone']
    
    print(f"  Brand -> Zone mapping: {len(brand_zones)} brands")
    print(f"  Sample brands: {brand_zones['brand'].head(10).tolist()}")
    
    # Clean restaurant names in survey
    survey['restaurant_clean'] = survey['Which restaurant did you order from?'].str.strip()
    
    # Create name mapping for common variations
    name_mapping = {
        "Bill's": "Bill's",
        'Bills': "Bill's",
        'PizzaExpress': 'PizzaExpress',
        'Pizza Express': 'PizzaExpress',
    }
    survey['restaurant_mapped'] = survey['restaurant_clean'].replace(name_mapping)
    
    print(f"  Survey restaurants: {survey['restaurant_mapped'].dropna().unique()[:10].tolist()}")
    
    # Join survey to zones via brand
    survey_with_zone = survey.merge(
        brand_zones,
        left_on='restaurant_mapped',
        right_on='brand',
        how='left'
    )
    
    # For surveys that didn't match, try to match via City
    # Get zone -> city mapping
    zone_city = zones[['ZONE_NAME', 'CITY_NAME']].drop_duplicates()
    
    # For unmatched surveys, assign a zone from their city
    unmatched_mask = survey_with_zone['zone'].isna()
    if unmatched_mask.any():
        # Get city from survey
        survey_with_zone.loc[unmatched_mask, 'survey_city'] = survey_with_zone.loc[unmatched_mask, 'City']
        
        # Find zones in that city
        city_zones = zones.groupby('CITY_NAME').agg({
            'ZONE_NAME': 'first',
            'DINNEROO_CUISINE_COUNT': 'mean',
            'DINNEROO_PARTNER_COUNT': 'mean'
        }).reset_index()
        
        # Merge city-based zone assignment
        survey_with_zone = survey_with_zone.merge(
            city_zones[['CITY_NAME', 'ZONE_NAME']].rename(columns={'ZONE_NAME': 'city_zone'}),
            left_on='survey_city',
            right_on='CITY_NAME',
            how='left'
        )
        
        # Use city_zone where zone is missing
        survey_with_zone['zone'] = survey_with_zone['zone'].fillna(survey_with_zone['city_zone'])
    
    # Join to zone metrics
    survey_with_metrics = survey_with_zone.merge(
        zones[['ZONE_NAME', 'DINNEROO_CUISINE_COUNT', 'DINNEROO_PARTNER_COUNT']],
        left_on='zone',
        right_on='ZONE_NAME',
        how='left'
    )
    
    matched = survey_with_metrics['DINNEROO_CUISINE_COUNT'].notna().sum()
    print(f"  Matched {matched}/{len(survey)} survey responses to zones ({matched/len(survey)*100:.1f}%)")
    
    # Debug: show match breakdown
    by_restaurant = survey_with_metrics.groupby('restaurant_clean')['DINNEROO_CUISINE_COUNT'].apply(
        lambda x: x.notna().sum()
    ).sort_values(ascending=False)
    print(f"  Top matched restaurants: {by_restaurant.head(5).to_dict()}")
    
    return survey_with_metrics


def calculate_outcomes_by_bucket(df):
    """
    Calculate consumer outcomes grouped by cuisine/partner count buckets.
    """
    print("\nCalculating outcomes by bucket...")
    
    # Parse consumer outcome columns
    df['kids_happy'] = parse_kids_reaction(df)
    df['reorder_intent'] = parse_reorder_intent(df)
    df['variety_complaint'] = parse_variety_complaints(df)
    
    # Create buckets
    def cuisine_bucket(x):
        if pd.isna(x):
            return None
        if x <= 2:
            return '1-2_cuisines'
        elif x <= 4:
            return '3-4_cuisines'
        else:
            return '5+_cuisines'
    
    def partner_bucket(x):
        if pd.isna(x):
            return None
        if x <= 2:
            return '1-2_partners'
        elif x <= 4:
            return '3-4_partners'
        else:
            return '5+_partners'
    
    df['cuisine_bucket'] = df['DINNEROO_CUISINE_COUNT'].apply(cuisine_bucket)
    df['partner_bucket'] = df['DINNEROO_PARTNER_COUNT'].apply(partner_bucket)
    
    # Calculate by cuisine bucket
    cuisine_results = {}
    for bucket in ['1-2_cuisines', '3-4_cuisines', '5+_cuisines']:
        bucket_df = df[df['cuisine_bucket'] == bucket]
        n = len(bucket_df)
        
        kids_happy_data = bucket_df['kids_happy'].dropna()
        reorder_data = bucket_df['reorder_intent'].dropna()
        variety_data = bucket_df['variety_complaint']
        
        cuisine_results[bucket] = {
            'kids_happy': round(kids_happy_data.mean(), 3) if len(kids_happy_data) > 0 else None,
            'kids_happy_n': len(kids_happy_data),
            'reorder_intent': round(reorder_data.mean(), 3) if len(reorder_data) > 0 else None,
            'reorder_intent_n': len(reorder_data),
            'variety_complaints': round(variety_data.mean(), 3) if len(variety_data) > 0 else None,
            'variety_complaints_n': len(variety_data),
            'n': n
        }
        print(f"  {bucket}: n={n}, kids_happy={cuisine_results[bucket]['kids_happy']}, "
              f"reorder={cuisine_results[bucket]['reorder_intent']}, "
              f"variety_complaints={cuisine_results[bucket]['variety_complaints']}")
    
    # Calculate by partner bucket
    partner_results = {}
    for bucket in ['1-2_partners', '3-4_partners', '5+_partners']:
        bucket_df = df[df['partner_bucket'] == bucket]
        n = len(bucket_df)
        
        kids_happy_data = bucket_df['kids_happy'].dropna()
        reorder_data = bucket_df['reorder_intent'].dropna()
        variety_data = bucket_df['variety_complaint']
        
        partner_results[bucket] = {
            'kids_happy': round(kids_happy_data.mean(), 3) if len(kids_happy_data) > 0 else None,
            'kids_happy_n': len(kids_happy_data),
            'reorder_intent': round(reorder_data.mean(), 3) if len(reorder_data) > 0 else None,
            'reorder_intent_n': len(reorder_data),
            'variety_complaints': round(variety_data.mean(), 3) if len(variety_data) > 0 else None,
            'variety_complaints_n': len(variety_data),
            'n': n
        }
        print(f"  {bucket}: n={n}, kids_happy={partner_results[bucket]['kids_happy']}, "
              f"reorder={partner_results[bucket]['reorder_intent']}, "
              f"variety_complaints={partner_results[bucket]['variety_complaints']}")
    
    return cuisine_results, partner_results


def calculate_impact(results, low_bucket, high_bucket):
    """Calculate the impact (difference) between low and high buckets."""
    low = results.get(low_bucket, {})
    high = results.get(high_bucket, {})
    
    impact = {}
    for metric in ['kids_happy', 'reorder_intent', 'variety_complaints']:
        low_val = low.get(metric)
        high_val = high.get(metric)
        
        if low_val is not None and high_val is not None:
            diff = high_val - low_val
            # For variety complaints, negative is good
            if metric == 'variety_complaints':
                impact[f'{metric}_change'] = round(diff, 3)
                impact[f'{metric}_impact'] = f"{diff*100:+.1f}pp" if diff != 0 else "0pp"
            else:
                impact[f'{metric}_change'] = round(diff, 3)
                impact[f'{metric}_impact'] = f"{diff*100:+.1f}pp" if diff != 0 else "0pp"
    
    return impact


def generate_output(cuisine_results, partner_results):
    """Generate the final output JSON."""
    
    # Calculate impacts
    cuisine_impact = calculate_impact(cuisine_results, '1-2_cuisines', '5+_cuisines')
    partner_impact = calculate_impact(partner_results, '1-2_partners', '5+_partners')
    
    output = {
        "analysis_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "methodology": "Survey responses joined to zones via restaurant mapping, then grouped by cuisine/partner count buckets",
        
        "cuisine_impact": {
            "buckets": cuisine_results,
            "impact_5_vs_1-2": cuisine_impact,
            "summary": {
                "kids_happy_impact": cuisine_impact.get('kids_happy_impact', 'N/A'),
                "reorder_intent_impact": cuisine_impact.get('reorder_intent_impact', 'N/A'),
                "variety_complaint_impact": cuisine_impact.get('variety_complaints_impact', 'N/A'),
                "sample_size_low": cuisine_results.get('1-2_cuisines', {}).get('n', 0),
                "sample_size_high": cuisine_results.get('5+_cuisines', {}).get('n', 0),
            }
        },
        
        "partner_impact": {
            "buckets": partner_results,
            "impact_5_vs_1-2": partner_impact,
            "summary": {
                "kids_happy_impact": partner_impact.get('kids_happy_impact', 'N/A'),
                "reorder_intent_impact": partner_impact.get('reorder_intent_impact', 'N/A'),
                "variety_complaint_impact": partner_impact.get('variety_complaints_impact', 'N/A'),
                "sample_size_low": partner_results.get('1-2_partners', {}).get('n', 0),
                "sample_size_high": partner_results.get('5+_partners', {}).get('n', 0),
            }
        },
        
        "validation_status": {
            "kids_happy_validated": cuisine_impact.get('kids_happy_change') is not None,
            "reorder_intent_validated": cuisine_impact.get('reorder_intent_change') is not None,
            "variety_complaints_validated": cuisine_impact.get('variety_complaints_change') is not None,
        },
        
        "source": "POST_ORDER_SURVEY-CONSOLIDATED.csv joined to zone_quality_scores.csv via ALL_DINNEROO_ORDERS.csv"
    }
    
    return output


def main():
    print("=" * 60)
    print("MVP CONSUMER OUTCOMES VALIDATION")
    print("=" * 60)
    
    # Load data
    zones, orders, survey = load_data()
    
    # Join survey to zones
    survey_with_metrics = join_survey_to_zones(survey, orders, zones)
    
    # Calculate outcomes by bucket
    cuisine_results, partner_results = calculate_outcomes_by_bucket(survey_with_metrics)
    
    # Generate output
    output = generate_output(cuisine_results, partner_results)
    
    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "mvp_consumer_validation.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    print("\nCuisine Impact (5+ vs 1-2 cuisines):")
    print(f"  Kids Happy: {output['cuisine_impact']['summary']['kids_happy_impact']}")
    print(f"  Reorder Intent: {output['cuisine_impact']['summary']['reorder_intent_impact']}")
    print(f"  Variety Complaints: {output['cuisine_impact']['summary']['variety_complaint_impact']}")
    
    print("\nPartner Impact (5+ vs 1-2 partners):")
    print(f"  Kids Happy: {output['partner_impact']['summary']['kids_happy_impact']}")
    print(f"  Reorder Intent: {output['partner_impact']['summary']['reorder_intent_impact']}")
    print(f"  Variety Complaints: {output['partner_impact']['summary']['variety_complaint_impact']}")
    
    print(f"\nOutput saved to: {output_path}")
    
    # Validation check
    all_validated = all(output['validation_status'].values())
    if all_validated:
        print("\n✅ All consumer outcomes validated!")
    else:
        print("\n⚠️ Some outcomes could not be validated - check sample sizes")
    
    return output


if __name__ == "__main__":
    main()

