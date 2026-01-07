#!/usr/bin/env python3
"""
Segment Comparison Analysis
===========================
Compares family vs couple vs single segments to understand behavioral differences.

Purpose: Determine if families behave differently enough to justify family-specific
scoring factors in the dish scoring framework and MVP thresholds.

Outputs:
- DATA/3_ANALYSIS/segment_comparison.csv
- DATA/3_ANALYSIS/segment_comparison_detailed.json
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_SOURCE = PROJECT_ROOT / "DATA" / "1_SOURCE" / "surveys"
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"

def load_post_order_survey():
    """Load and parse post-order survey data."""
    filepath = DATA_SOURCE / "POST_ORDER_ALCHEMER_2026-01-06.csv"
    df = pd.read_csv(filepath)
    print(f"Loaded post-order survey: {len(df)} responses")
    return df

def load_dropoff_survey():
    """Load and parse dropoff survey data."""
    filepath = DATA_SOURCE / "DROPOFF_ALCHEMER_2026-01-06.csv"
    df = pd.read_csv(filepath)
    print(f"Loaded dropoff survey: {len(df)} responses")
    return df

def classify_segment(row, survey_type='post_order'):
    """
    Classify a respondent into a segment based on household composition.
    
    Segments:
    - Family: Has children in household
    - Couple: Has partner but no children
    - Single: Lives alone
    - Other: Friends, other adults, etc.
    """
    # Column names vary slightly between surveys
    if survey_type == 'post_order':
        live_alone_col = "I live alone:Who currently lives in your home with you? (Please select all that apply)"
        partner_col = "Partner:Who currently lives in your home with you? (Please select all that apply)"
        children_col = "My child/children:Who currently lives in your home with you? (Please select all that apply)"
        friends_col = "Friend(s):Who currently lives in your home with you? (Please select all that apply)"
    else:  # dropoff
        live_alone_col = "I live alone:Who currently lives in your home with you? (Please select all that apply)"
        partner_col = "Partner:Who currently lives in your home with you? (Please select all that apply)"
        children_col = "My child/children:Who currently lives in your home with you? (Please select all that apply)"
        friends_col = "Friend(s):Who currently lives in your home with you? (Please select all that apply)"
    
    has_children = pd.notna(row.get(children_col)) and str(row.get(children_col)).strip() != ''
    has_partner = pd.notna(row.get(partner_col)) and str(row.get(partner_col)).strip() != ''
    lives_alone = pd.notna(row.get(live_alone_col)) and str(row.get(live_alone_col)).strip() != ''
    has_friends = pd.notna(row.get(friends_col)) and str(row.get(friends_col)).strip() != ''
    
    if has_children:
        return 'Family'
    elif has_partner and not has_children:
        return 'Couple'
    elif lives_alone:
        return 'Single'
    elif has_friends:
        return 'Friends/Sharers'
    else:
        return 'Other'

def analyze_post_order_by_segment(df):
    """Analyze post-order survey responses by segment."""
    
    # Classify each respondent
    df['segment'] = df.apply(lambda row: classify_segment(row, 'post_order'), axis=1)
    
    results = {}
    
    # Count by segment
    segment_counts = df['segment'].value_counts().to_dict()
    results['segment_counts'] = segment_counts
    print(f"\nSegment distribution:")
    for seg, count in segment_counts.items():
        print(f"  {seg}: {count}")
    
    # Analyze by segment
    segment_analysis = {}
    
    for segment in ['Family', 'Couple', 'Single', 'Friends/Sharers', 'Other']:
        seg_df = df[df['segment'] == segment]
        if len(seg_df) < 3:
            continue
            
        analysis = {
            'n': len(seg_df),
            'metrics': {}
        }
        
        # 1. Satisfaction - "How did you feel about the meal?"
        satisfaction_col = "How did you feel about the meal?"
        if satisfaction_col in seg_df.columns:
            sat_dist = seg_df[satisfaction_col].value_counts(normalize=True).to_dict()
            loved_liked = sat_dist.get('Loved it', 0) + sat_dist.get('Liked it', 0)
            analysis['metrics']['satisfaction'] = {
                'loved_liked_pct': round(loved_liked * 100, 1),
                'distribution': {k: round(v * 100, 1) for k, v in sat_dist.items() if pd.notna(k)}
            }
        
        # 2. Repeat Intent - "I would like to order the same dish again"
        repeat_col = "I would like to order the same dish again :Please state how much you agree or disagree with the following statements:"
        if repeat_col in seg_df.columns:
            repeat_dist = seg_df[repeat_col].value_counts(normalize=True).to_dict()
            agree_pct = repeat_dist.get('Strongly agree', 0) + repeat_dist.get('Agree', 0)
            analysis['metrics']['repeat_intent'] = {
                'agree_pct': round(agree_pct * 100, 1),
                'distribution': {k: round(v * 100, 1) for k, v in repeat_dist.items() if pd.notna(k)}
            }
        
        # 3. Dish Choice Reasons
        dish_choice_cols = [col for col in seg_df.columns if 'Why did you choose this dish?' in col]
        if dish_choice_cols:
            reasons = {}
            for col in dish_choice_cols:
                # Extract reason name from column
                reason_match = re.search(r'^([^:]+):', col)
                if reason_match:
                    reason = reason_match.group(1)
                    # Count non-empty responses
                    selected = seg_df[col].notna() & (seg_df[col] != '')
                    reasons[reason] = round(selected.sum() / len(seg_df) * 100, 1)
            analysis['metrics']['dish_choice_reasons'] = reasons
        
        # 4. Restaurant Choice
        restaurant_col = "Which restaurant did you order from?"
        if restaurant_col in seg_df.columns:
            top_restaurants = seg_df[restaurant_col].value_counts().head(5).to_dict()
            analysis['metrics']['top_restaurants'] = top_restaurants
        
        # 5. Overall Rating
        rating_col = "Overall, how would you rate your Family Dinneroo experience?"
        if rating_col in seg_df.columns:
            rating_dist = seg_df[rating_col].value_counts(normalize=True).to_dict()
            satisfied_pct = rating_dist.get('Very Satisfied', 0) + rating_dist.get('Satisfied', 0)
            analysis['metrics']['overall_rating'] = {
                'satisfied_pct': round(satisfied_pct * 100, 1),
                'distribution': {k: round(v * 100, 1) for k, v in rating_dist.items() if pd.notna(k)}
            }
        
        # 6. Food Adequacy - "There was enough food for everyone"
        adequacy_col = "There was enough food for everyone:Please rate how much you agree or disagree with the following statements:"
        if adequacy_col in seg_df.columns:
            adequacy_dist = seg_df[adequacy_col].value_counts(normalize=True).to_dict()
            agree_pct = adequacy_dist.get('Strongly agree', 0) + adequacy_dist.get('Agree', 0)
            analysis['metrics']['food_adequacy'] = {
                'agree_pct': round(agree_pct * 100, 1),
                'distribution': {k: round(v * 100, 1) for k, v in adequacy_dist.items() if pd.notna(k)}
            }
        
        segment_analysis[segment] = analysis
    
    results['segment_analysis'] = segment_analysis
    return results

def analyze_dropoff_by_segment(df):
    """Analyze dropoff survey responses by segment."""
    
    # Classify each respondent
    df['segment'] = df.apply(lambda row: classify_segment(row, 'dropoff'), axis=1)
    
    results = {}
    
    # Count by segment
    segment_counts = df['segment'].value_counts().to_dict()
    results['segment_counts'] = segment_counts
    print(f"\nDropoff segment distribution:")
    for seg, count in segment_counts.items():
        print(f"  {seg}: {count}")
    
    segment_analysis = {}
    
    for segment in ['Family', 'Couple', 'Single', 'Friends/Sharers', 'Other']:
        seg_df = df[df['segment'] == segment]
        if len(seg_df) < 3:
            continue
            
        analysis = {
            'n': len(seg_df),
            'metrics': {}
        }
        
        # 1. Appeal Rating
        appeal_col = "Overall, how appealing did Family Dinneroo seem when you looked at it?"
        if appeal_col in seg_df.columns:
            appeal_dist = seg_df[appeal_col].value_counts(normalize=True).to_dict()
            appealing_pct = appeal_dist.get('Very appealing', 0) + appeal_dist.get('Somewhat appealing', 0)
            analysis['metrics']['appeal'] = {
                'appealing_pct': round(appealing_pct * 100, 1),
                'distribution': {k: round(v * 100, 1) for k, v in appeal_dist.items() if pd.notna(k)}
            }
        
        # 2. Barriers - Why didn't they order?
        barrier_cols = [col for col in seg_df.columns if "Which of these best describe why it didn't work for you?" in col]
        if barrier_cols:
            barriers = {}
            for col in barrier_cols:
                # Extract barrier name from column
                barrier_match = re.search(r'^([^:]+):', col)
                if barrier_match:
                    barrier = barrier_match.group(1)
                    # Count non-empty responses
                    selected = seg_df[col].notna() & (seg_df[col] != '')
                    barriers[barrier] = round(selected.sum() / len(seg_df) * 100, 1)
            analysis['metrics']['barriers'] = barriers
        
        # 3. What would help - improvements
        improvement_cols = [col for col in seg_df.columns if "Which of the following would have made you more likely" in col]
        if improvement_cols:
            improvements = {}
            for col in improvement_cols:
                # Extract improvement name from column
                imp_match = re.search(r'^([^:]+):', col)
                if imp_match:
                    improvement = imp_match.group(1)
                    # Count non-empty responses
                    selected = seg_df[col].notna() & (seg_df[col] != '')
                    improvements[improvement] = round(selected.sum() / len(seg_df) * 100, 1)
            analysis['metrics']['improvements_wanted'] = improvements
        
        # 4. Appealing aspects
        appeal_aspect_cols = [col for col in seg_df.columns if "What are the most appealing aspects" in col]
        if appeal_aspect_cols:
            aspects = {}
            for col in appeal_aspect_cols:
                aspect_match = re.search(r'^([^:]+):', col)
                if aspect_match:
                    aspect = aspect_match.group(1)
                    selected = seg_df[col].notna() & (seg_df[col] != '')
                    aspects[aspect] = round(selected.sum() / len(seg_df) * 100, 1)
            analysis['metrics']['appealing_aspects'] = aspects
        
        segment_analysis[segment] = analysis
    
    results['segment_analysis'] = segment_analysis
    return results

def compute_segment_differences(post_order_results, dropoff_results):
    """Compute key differences between segments."""
    
    differences = []
    
    # Get family baseline from post-order
    po_analysis = post_order_results.get('segment_analysis', {})
    family_data = po_analysis.get('Family', {})
    
    if not family_data:
        print("Warning: No family data found in post-order survey")
        return differences
    
    family_n = family_data.get('n', 0)
    family_metrics = family_data.get('metrics', {})
    
    # Compare each segment to families
    for segment in ['Couple', 'Single', 'Friends/Sharers']:
        seg_data = po_analysis.get(segment, {})
        if not seg_data:
            continue
            
        seg_n = seg_data.get('n', 0)
        seg_metrics = seg_data.get('metrics', {})
        
        # Compare satisfaction
        if 'satisfaction' in family_metrics and 'satisfaction' in seg_metrics:
            family_sat = family_metrics['satisfaction'].get('loved_liked_pct', 0)
            seg_sat = seg_metrics['satisfaction'].get('loved_liked_pct', 0)
            diff = seg_sat - family_sat
            differences.append({
                'metric': 'Satisfaction (Loved/Liked %)',
                'segment': segment,
                'segment_n': seg_n,
                'family_value': family_sat,
                'segment_value': seg_sat,
                'difference': round(diff, 1),
                'index_vs_family': round(seg_sat / family_sat * 100, 0) if family_sat > 0 else None,
                'significant': abs(diff) > 10
            })
        
        # Compare repeat intent
        if 'repeat_intent' in family_metrics and 'repeat_intent' in seg_metrics:
            family_repeat = family_metrics['repeat_intent'].get('agree_pct', 0)
            seg_repeat = seg_metrics['repeat_intent'].get('agree_pct', 0)
            diff = seg_repeat - family_repeat
            differences.append({
                'metric': 'Repeat Intent (Agree %)',
                'segment': segment,
                'segment_n': seg_n,
                'family_value': family_repeat,
                'segment_value': seg_repeat,
                'difference': round(diff, 1),
                'index_vs_family': round(seg_repeat / family_repeat * 100, 0) if family_repeat > 0 else None,
                'significant': abs(diff) > 10
            })
        
        # Compare overall rating
        if 'overall_rating' in family_metrics and 'overall_rating' in seg_metrics:
            family_rating = family_metrics['overall_rating'].get('satisfied_pct', 0)
            seg_rating = seg_metrics['overall_rating'].get('satisfied_pct', 0)
            diff = seg_rating - family_rating
            differences.append({
                'metric': 'Overall Satisfied %',
                'segment': segment,
                'segment_n': seg_n,
                'family_value': family_rating,
                'segment_value': seg_rating,
                'difference': round(diff, 1),
                'index_vs_family': round(seg_rating / family_rating * 100, 0) if family_rating > 0 else None,
                'significant': abs(diff) > 10
            })
        
        # Compare food adequacy
        if 'food_adequacy' in family_metrics and 'food_adequacy' in seg_metrics:
            family_adequacy = family_metrics['food_adequacy'].get('agree_pct', 0)
            seg_adequacy = seg_metrics['food_adequacy'].get('agree_pct', 0)
            diff = seg_adequacy - family_adequacy
            differences.append({
                'metric': 'Food Adequacy (Agree %)',
                'segment': segment,
                'segment_n': seg_n,
                'family_value': family_adequacy,
                'segment_value': seg_adequacy,
                'difference': round(diff, 1),
                'index_vs_family': round(seg_adequacy / family_adequacy * 100, 0) if family_adequacy > 0 else None,
                'significant': abs(diff) > 10
            })
        
        # Compare dish choice reasons - specifically "child appeal"
        if 'dish_choice_reasons' in family_metrics and 'dish_choice_reasons' in seg_metrics:
            family_reasons = family_metrics['dish_choice_reasons']
            seg_reasons = seg_metrics['dish_choice_reasons']
            
            child_appeal_family = family_reasons.get('Sounded appealing to my children', 0)
            child_appeal_seg = seg_reasons.get('Sounded appealing to my children', 0)
            diff = child_appeal_seg - child_appeal_family
            differences.append({
                'metric': '"Child Appeal" Cited %',
                'segment': segment,
                'segment_n': seg_n,
                'family_value': child_appeal_family,
                'segment_value': child_appeal_seg,
                'difference': round(diff, 1),
                'index_vs_family': round(child_appeal_seg / child_appeal_family * 100, 0) if child_appeal_family > 0 else None,
                'significant': abs(diff) > 15
            })
            
            # Adult appeal
            adult_appeal_family = family_reasons.get('Sounded appealing to adults', 0)
            adult_appeal_seg = seg_reasons.get('Sounded appealing to adults', 0)
            diff = adult_appeal_seg - adult_appeal_family
            differences.append({
                'metric': '"Adult Appeal" Cited %',
                'segment': segment,
                'segment_n': seg_n,
                'family_value': adult_appeal_family,
                'segment_value': adult_appeal_seg,
                'difference': round(diff, 1),
                'index_vs_family': round(adult_appeal_seg / adult_appeal_family * 100, 0) if adult_appeal_family > 0 else None,
                'significant': abs(diff) > 15
            })
            
            # Value for money
            value_family = family_reasons.get('Good value for money', 0)
            value_seg = seg_reasons.get('Good value for money', 0)
            diff = value_seg - value_family
            differences.append({
                'metric': '"Good Value" Cited %',
                'segment': segment,
                'segment_n': seg_n,
                'family_value': value_family,
                'segment_value': value_seg,
                'difference': round(diff, 1),
                'index_vs_family': round(value_seg / value_family * 100, 0) if value_family > 0 else None,
                'significant': abs(diff) > 15
            })
    
    return differences

def generate_summary_csv(differences, output_path):
    """Generate summary CSV of segment differences."""
    df = pd.DataFrame(differences)
    df.to_csv(output_path, index=False)
    print(f"\nSaved segment comparison to: {output_path}")
    return df

def main():
    print("=" * 60)
    print("SEGMENT COMPARISON ANALYSIS")
    print("Comparing Family vs Couple vs Single behaviors")
    print("=" * 60)
    
    # Load data
    post_order_df = load_post_order_survey()
    dropoff_df = load_dropoff_survey()
    
    # Analyze by segment
    print("\n--- POST-ORDER SURVEY ANALYSIS ---")
    post_order_results = analyze_post_order_by_segment(post_order_df)
    
    print("\n--- DROPOFF SURVEY ANALYSIS ---")
    dropoff_results = analyze_dropoff_by_segment(dropoff_df)
    
    # Compute differences
    print("\n--- COMPUTING SEGMENT DIFFERENCES ---")
    differences = compute_segment_differences(post_order_results, dropoff_results)
    
    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save CSV summary
    csv_path = OUTPUT_DIR / "segment_comparison.csv"
    summary_df = generate_summary_csv(differences, csv_path)
    
    # Save detailed JSON
    detailed_results = {
        'generated_at': datetime.now().isoformat(),
        'post_order_analysis': post_order_results,
        'dropoff_analysis': dropoff_results,
        'segment_differences': differences,
        'summary': {
            'total_post_order_responses': len(post_order_df),
            'total_dropoff_responses': len(dropoff_df),
            'segments_analyzed': list(post_order_results.get('segment_analysis', {}).keys()),
            'significant_differences_found': sum(1 for d in differences if d.get('significant', False))
        }
    }
    
    json_path = OUTPUT_DIR / "segment_comparison_detailed.json"
    with open(json_path, 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    print(f"Saved detailed results to: {json_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    
    # Print segment counts
    print("\nSample Sizes:")
    for segment, data in post_order_results.get('segment_analysis', {}).items():
        print(f"  {segment}: n={data.get('n', 0)}")
    
    # Print significant differences
    sig_diffs = [d for d in differences if d.get('significant', False)]
    if sig_diffs:
        print(f"\nSignificant Differences Found: {len(sig_diffs)}")
        for d in sig_diffs:
            direction = "higher" if d['difference'] > 0 else "lower"
            print(f"  • {d['segment']} {direction} on '{d['metric']}': {d['segment_value']}% vs Family {d['family_value']}% (Δ{d['difference']:+.1f})")
    else:
        print("\nNo significant differences found between segments.")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    return detailed_results

if __name__ == "__main__":
    main()


