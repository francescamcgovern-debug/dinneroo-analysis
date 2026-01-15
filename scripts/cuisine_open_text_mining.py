#!/usr/bin/env python3
"""
Cuisine Open-Text Mining
========================
Parses open-text survey responses to identify explicit cuisine/dish requests.

Protocol (from plan):
- Request-only rule: Count a row only if it includes (a) target keyword AND (b) request-intent phrase
- Manual review workflow: Create audit sheet for human review
- Cap: Review first N=200 flagged rows

Outputs:
- cuisine_open_text_review_sheet.csv (for manual review)
- cuisine_demand_signals.csv (summary by cuisine/dish)
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
SOURCE_DIR = BASE_DIR / "DATA/1_SOURCE/surveys"
ANALYSIS_DIR = BASE_DIR / "DATA/3_ANALYSIS"
DELIVERABLES_DIR = BASE_DIR / "DELIVERABLES/reports"

# Target keywords for mining
CUISINE_KEYWORDS = {
    # Chinese specific
    'chinese': 'Chinese',
    'sweet and sour': 'Chinese',
    'chow mein': 'Chinese',
    'dim sum': 'Chinese',
    'peking': 'Chinese',
    'cantonese': 'Chinese',
    'szechuan': 'Chinese',
    'sichuan': 'Chinese',
    'spring roll': 'Chinese',
    'egg fried rice': 'Chinese',
    # Other Asian sub-cuisines
    'japanese': 'Japanese',
    'korean': 'Korean',
    'vietnamese': 'Vietnamese',
    'thai': 'Thai',
    # Non-Asian requests
    'nando': 'Nando\'s (Peri-Peri)',
    'peri peri': 'Nando\'s (Peri-Peri)',
    'roast': 'British',
    'fish and chips': 'British',
    'fish & chips': 'British',
    'kebab': 'Middle Eastern',
    'greek': 'Greek',
    'spanish': 'Spanish',
    'american': 'American',
    'burger': 'American',
}

# Request-intent phrases (must also appear for a row to count as "request")
# REFINED: Explicit forward-looking requests, including softer expressions of demand
REQUEST_INTENTS = [
    'would like more', 'need more', 'want more', 'more options for',
    'add more', 'include more', 'should have more', 'bring back',
    'love to see', 'why no', 'please add', 'wish there were',
    'where is', 'hoping for more', 'expand to include',
    'no .* options',  # e.g., "no burger options"
    'definitely',  # "Chinese food definitely"
    'more .* restaurants',  # "more Chinese restaurants"
    'include other cuisines',  # "include other cuisines as well"
    'perhaps more',  # softer request
    'more food choices',  # general expansion request
]

# Exclusion phrases - if these appear, it's NOT a request
EXCLUSION_PHRASES = [
    'ordered', 'had the', 'we got', 'i got', 'chose the',
    'was good', 'was great', 'was lovely', 'was fantastic',
    'was disappointing', 'was not', 'wasn\'t', 'could be improved',
    'portion', 'dry', 'crispy', 'sauce', 'chicken was', 'too much',
    'not enough', 'seemed to be', 'most seems to be',  # "most seems to be Chinese" = not a request
    'awful experience', 'terrible', 'complaint', 'refund',
]

# Negative intent - these indicate NOT wanting more
NEGATIVE_INTENTS = [
    'too much', 'too many', 'most seems to be', 'already have',
    'enough of', 'less', 'not more',
]

def find_open_text_columns(df):
    """Find columns that contain open-text responses."""
    open_text_cols = []
    
    # Look for improvement/suggestion columns
    for col in df.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in ['improve', 'suggest', 'further', 'other', 'comment', 'feedback']):
            open_text_cols.append(col)
    
    return open_text_cols

def parse_open_text(text, keywords, intents):
    """Parse text for keyword + intent matches with stricter filtering."""
    if pd.isna(text) or not isinstance(text, str):
        return []
    
    text_lower = text.lower()
    matches = []
    
    # Check for exclusion phrases first - if present, likely dish feedback not demand
    has_exclusion = any(excl in text_lower for excl in EXCLUSION_PHRASES)
    
    # Check for negative intent - means they DON'T want more
    has_negative = any(neg in text_lower for neg in NEGATIVE_INTENTS)
    
    for keyword, cuisine in keywords.items():
        if keyword in text_lower:
            # Check if any intent phrase also present
            has_intent = any(intent in text_lower for intent in intents)
            
            # Find the intent phrase that matched
            matched_intent = None
            for intent in intents:
                if intent in text_lower:
                    matched_intent = intent
                    break
            
            # Determine classification with stricter rules
            if has_negative:
                classification = 'Negative (don\'t want more)'
            elif has_exclusion and not has_intent:
                classification = 'Dish Feedback (exclude)'
            elif has_intent and not has_exclusion:
                classification = 'Request'
            elif has_intent and has_exclusion:
                classification = 'Ambiguous (needs review)'
            else:
                classification = 'Mention (no intent)'
            
            matches.append({
                'keyword': keyword,
                'cuisine_group': cuisine,
                'has_intent': has_intent,
                'has_exclusion': has_exclusion,
                'has_negative': has_negative,
                'matched_intent': matched_intent,
                'classification': classification
            })
    
    return matches

def process_surveys():
    """Process both post-order and dropoff surveys."""
    print("Processing surveys for open-text mining...")
    
    all_flagged = []
    
    # Process post-order survey
    post_order_path = SOURCE_DIR / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    if post_order_path.exists():
        df_post = pd.read_csv(post_order_path)
        print(f"  Loaded {len(df_post)} post-order responses")
        
        open_text_cols = find_open_text_columns(df_post)
        print(f"  Found {len(open_text_cols)} open-text columns")
        
        for idx, row in df_post.iterrows():
            response_id = row.get('Response ID', idx)
            
            for col in open_text_cols:
                text = row.get(col)
                matches = parse_open_text(text, CUISINE_KEYWORDS, REQUEST_INTENTS)
                
                for match in matches:
                    all_flagged.append({
                        'source_file': 'POST_ORDER_SURVEY-CONSOLIDATED.csv',
                        'response_id': response_id,
                        'column': col,
                        'raw_text': text[:500] if text else '',  # Truncate long text
                        'matched_keyword': match['keyword'],
                        'matched_intent_phrase': match['matched_intent'],
                        'cuisine_group': match['cuisine_group'],
                        'auto_classification': match['classification'],
                        'is_valid_request': match['classification'] == 'Request',
                        'classification': '',  # For manual review
                        'reviewer': '',
                        'notes': ''
                    })
    
    # Process dropoff survey
    dropoff_path = SOURCE_DIR / "DROPOFF_SURVEY-CONSOLIDATED.csv"
    if dropoff_path.exists():
        df_drop = pd.read_csv(dropoff_path)
        print(f"  Loaded {len(df_drop)} dropoff responses")
        
        open_text_cols = find_open_text_columns(df_drop)
        
        for idx, row in df_drop.iterrows():
            response_id = row.get('Response ID', idx)
            
            for col in open_text_cols:
                text = row.get(col)
                matches = parse_open_text(text, CUISINE_KEYWORDS, REQUEST_INTENTS)
                
                for match in matches:
                    all_flagged.append({
                        'source_file': 'DROPOFF_SURVEY-CONSOLIDATED.csv',
                        'response_id': response_id,
                        'column': col,
                        'raw_text': text[:500] if text else '',
                        'matched_keyword': match['keyword'],
                        'matched_intent_phrase': match['matched_intent'],
                        'cuisine_group': match['cuisine_group'],
                        'auto_classification': match['classification'],
                        'is_valid_request': match['classification'] == 'Request',
                        'classification': '',
                        'reviewer': '',
                        'notes': ''
                    })
    
    return pd.DataFrame(all_flagged)

def create_review_sheet(df_flagged, cap=200):
    """Create the manual review sheet (capped at N rows)."""
    print(f"\nCreating manual review sheet (cap={cap})...")
    
    # Prioritize Requests over Mentions
    df_sorted = df_flagged.sort_values(
        by=['auto_classification', 'cuisine_group'],
        ascending=[True, True]  # Requests first (alphabetically before "Mention")
    )
    
    # Cap at N rows
    df_capped = df_sorted.head(cap)
    
    # Add review instructions
    review_path = ANALYSIS_DIR / "cuisine_open_text_review_sheet.csv"
    df_capped.to_csv(review_path, index=False)
    
    print(f"  Saved review sheet to: {review_path}")
    print(f"  Total flagged: {len(df_flagged)}, Included in review: {len(df_capped)}")
    
    return df_capped

def calculate_demand_signals(df_flagged):
    """Calculate demand signals by cuisine/keyword."""
    print("\nCalculating demand signals...")
    
    # Filter to valid Requests only (stricter classification)
    df_requests = df_flagged[df_flagged['is_valid_request'] == True]
    
    # Also filter out duplicates (same response_id + cuisine_group)
    df_requests = df_requests.drop_duplicates(subset=['response_id', 'cuisine_group'])
    
    # Group by cuisine
    cuisine_counts = df_requests.groupby('cuisine_group').agg(
        request_count=('response_id', 'count'),
        unique_responses=('response_id', 'nunique'),
        keywords_matched=('matched_keyword', lambda x: ', '.join(x.unique()))
    ).reset_index()
    
    # Group by keyword
    keyword_counts = df_requests.groupby('matched_keyword').agg(
        request_count=('response_id', 'count'),
        cuisine_group=('cuisine_group', 'first')
    ).reset_index()
    
    # Save signals
    cuisine_path = ANALYSIS_DIR / "cuisine_demand_signals.csv"
    cuisine_counts.to_csv(cuisine_path, index=False)
    
    keyword_path = ANALYSIS_DIR / "keyword_demand_signals.csv"
    keyword_counts.to_csv(keyword_path, index=False)
    
    print(f"  Saved cuisine signals to: {cuisine_path}")
    print(f"  Saved keyword signals to: {keyword_path}")
    
    return cuisine_counts, keyword_counts

def main():
    """Main execution."""
    print("=" * 60)
    print("CUISINE OPEN-TEXT MINING")
    print("=" * 60)
    
    # Process surveys
    df_flagged = process_surveys()
    
    if len(df_flagged) == 0:
        print("\nNo matches found in open-text fields.")
        return
    
    # Create review sheet
    df_review = create_review_sheet(df_flagged, cap=200)
    
    # Calculate demand signals
    cuisine_counts, keyword_counts = calculate_demand_signals(df_flagged)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total open-text matches: {len(df_flagged)}")
    print(f"  - Requests (with intent): {len(df_flagged[df_flagged['auto_classification'] == 'Request'])}")
    print(f"  - Mentions (no intent): {len(df_flagged[df_flagged['auto_classification'] == 'Mention'])}")
    
    print("\nDemand signals by cuisine (Requests only):")
    print(cuisine_counts.to_string(index=False))
    
    print("\nTop keywords:")
    print(keyword_counts.head(15).to_string(index=False))
    
    return df_flagged

if __name__ == "__main__":
    main()
