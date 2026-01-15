"""
Latent Demand Extraction
========================
Extracts and combines latent demand signals from all available sources:
1. Open-text REQUEST mentions (dropoff + post-order + ratings) - filtered for requests only
2. OG Survey wishlist percentages
3. Dropoff barrier patterns

Output: Combined latent demand score for each dish type

v2.0 (Jan 2026): Added request pattern filtering to exclude complaints/neutral mentions
"""

import pandas as pd
import numpy as np
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

# Request patterns - only count text that contains these patterns
REQUEST_PATTERNS = [
    r'wish.*had',
    r'would love.*see',
    r'would like.*see',
    r'would like.*more',
    r'please add',
    r'why don\'t you have',
    r'would be great if',
    r'more.*please',
    r'i want',
    r'we want',
    r'need more',
    r'should have',
    r'could you add',
    r'missing.*option',
    r'no.*option for',
    r'like to see',
    r'love to see',
    r'be nice to have',
    r'would order',
    r'looking for',
]

def is_request(text):
    """Check if text contains a request pattern (not just a complaint or neutral mention)."""
    if pd.isna(text) or not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    for pattern in REQUEST_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "DATA"

# Dish type keywords for matching - expanded to 100+ dish types
DISH_KEYWORDS = {
    # === ITALIAN ===
    'Pizza': ['pizza', 'margherita', 'pepperoni'],
    'Pasta': ['pasta', 'spaghetti', 'penne', 'linguine', 'fettuccine', 'carbonara', 'bolognese'],
    'Lasagne': ['lasagne', 'lasagna'],
    'Risotto': ['risotto', 'arborio'],
    'Gnocchi': ['gnocchi'],
    'Filled Pasta': ['ravioli', 'tortellini', 'cannelloni'],
    'Baked Pasta': ['baked pasta', 'pasta bake', 'penne bake'],
    
    # === ASIAN - JAPANESE ===
    'Katsu': ['katsu', 'cutlet', 'tonkatsu'],
    'Sushi': ['sushi', 'maki', 'nigiri', 'sashimi'],
    'Ramen': ['ramen'],
    'Teriyaki': ['teriyaki'],
    'Gyoza': ['gyoza', 'dumpling', 'dumplings', 'potsticker'],
    'Tempura': ['tempura'],
    'Udon': ['udon'],
    
    # === ASIAN - CHINESE ===
    'Fried Rice': ['fried rice', 'egg fried rice'],
    'Noodles': ['noodle', 'noodles', 'lo mein', 'chow mein'],
    'Stir Fry': ['stir fry', 'stir-fry', 'stirfry'],
    'Sweet & Sour': ['sweet and sour', 'sweet & sour'],
    'Spring Rolls': ['spring roll', 'spring rolls', 'egg roll'],
    'Dim Sum': ['dim sum', 'har gow', 'siu mai', 'char siu bao'],
    'Peking Duck': ['peking duck', 'crispy duck', 'duck pancakes'],
    
    # === ASIAN - THAI ===
    'Pad Thai': ['pad thai', 'padthai'],
    'Thai Curry': ['green curry', 'red curry', 'massaman', 'panang'],
    'Tom Yum': ['tom yum', 'tom kha'],
    'Satay': ['satay', 'chicken satay'],
    
    # === ASIAN - VIETNAMESE ===
    'Pho': ['pho', 'vietnamese soup'],
    'Banh Mi': ['banh mi', 'vietnamese sandwich'],
    
    # === ASIAN - KOREAN ===
    'Korean Fried Chicken': ['korean fried chicken', 'kfc korean'],
    'Bibimbap': ['bibimbap'],
    'Bulgogi': ['bulgogi'],
    'Japchae': ['japchae', 'glass noodles'],
    
    # === ASIAN - SOUTHEAST ASIAN ===
    'Laksa': ['laksa'],
    'Nasi Goreng': ['nasi goreng'],
    'Rendang': ['rendang', 'beef rendang'],
    
    # === INDIAN / SOUTH ASIAN ===
    'Curry': ['curry', 'tikka', 'masala', 'vindaloo', 'madras', 'jalfrezi'],
    'Butter Chicken': ['butter chicken'],
    'Tikka Masala': ['tikka masala', 'chicken tikka'],
    'Korma': ['korma'],
    'Biryani': ['biryani', 'biriyani'],
    'Tandoori': ['tandoori'],
    'Daal': ['daal', 'dal', 'dhal', 'lentil curry'],
    'Samosa': ['samosa', 'samosas'],
    
    # === MEXICAN / TEX-MEX ===
    'Fajitas': ['fajita', 'fajitas'],
    'Tacos': ['taco', 'tacos'],
    'Burrito': ['burrito', 'burritos'],
    'Quesadilla': ['quesadilla'],
    'Nachos': ['nachos'],
    'Enchiladas': ['enchilada', 'enchiladas'],
    'Fish Tacos': ['fish taco', 'fish tacos'],
    'Chilli': ['chilli', 'chili', 'con carne'],
    
    # === MIDDLE EASTERN ===
    'Shawarma': ['shawarma', 'kebab', 'doner'],
    'Falafel': ['falafel'],
    'Hummus Plate': ['hummus', 'mezze'],
    'Shakshuka': ['shakshuka'],
    'Lamb Kofta': ['kofta', 'kofte', 'lamb kofta'],
    
    # === GREEK / MEDITERRANEAN ===
    'Gyros': ['gyros', 'gyro'],
    'Souvlaki': ['souvlaki'],
    'Moussaka': ['moussaka'],
    'Spanakopita': ['spanakopita', 'spinach pie'],
    'Dolma': ['dolma', 'dolmades', 'stuffed vine leaves'],
    
    # === BRITISH / COMFORT ===
    'Fish & Chips': ['fish and chips', 'fish & chips', 'fish n chips', 'fish chips'],
    'Roast Dinner': ['roast dinner', 'sunday roast', 'roast chicken', 'roast beef'],
    'Mac & Cheese': ['mac and cheese', 'mac & cheese', 'macaroni cheese', 'mac n cheese'],
    'Burger': ['burger', 'burgers'],
    'Pie': ['pie', 'meat pie', 'chicken pie', 'steak pie'],
    'Bangers & Mash': ['bangers and mash', 'sausage and mash', 'sausage mash'],
    'Shepherd\'s Pie': ['shepherd pie', 'shepherds pie', 'cottage pie'],
    'Jacket Potato': ['jacket potato', 'baked potato'],
    'Casserole': ['casserole', 'stew', 'hotpot'],
    'Pasty': ['pasty', 'cornish pasty'],
    
    # === AMERICAN ===
    'Wings': ['wings', 'chicken wings', 'buffalo wings'],
    'Chicken Nuggets': ['nuggets', 'chicken nuggets', 'chicken strips', 'chicken tenders'],
    'Hot Dog': ['hot dog', 'hotdog'],
    'BBQ Ribs': ['ribs', 'bbq ribs', 'spare ribs'],
    'Pulled Pork': ['pulled pork'],
    
    # === CARIBBEAN / AFRICAN ===
    'Jerk Chicken': ['jerk chicken', 'jerk'],
    'Jollof Rice': ['jollof', 'jollof rice'],
    'Curry Goat': ['curry goat', 'goat curry'],
    'Plantain': ['plantain'],
    'Suya': ['suya'],
    'Oxtail': ['oxtail'],
    
    # === EUROPEAN ===
    'Schnitzel': ['schnitzel', 'wiener schnitzel'],
    'Bratwurst': ['bratwurst', 'wurst'],
    'Pierogi': ['pierogi', 'pierogies'],
    'Stroganoff': ['stroganoff', 'beef stroganoff'],
    'Tagine': ['tagine', 'tajine'],
    'Paella': ['paella'],
    'Cous Cous': ['couscous', 'cous cous'],
    
    # === HEALTHY / BOWLS ===
    'Salad': ['salad', 'caesar', 'greek salad'],
    'Poke Bowl': ['poke', 'poke bowl'],
    'Buddha Bowl': ['buddha bowl'],
    'Grain Bowl': ['grain bowl', 'quinoa bowl'],
    'Rice Bowl': ['rice bowl', 'donburi'],
    'Acai Bowl': ['acai', 'acai bowl'],
    
    # === OTHER ===
    'Soup': ['soup', 'broth'],
    'Sandwich': ['sandwich', 'panini', 'toastie'],
    'Wrap': ['wrap', 'wraps'],
    'Grilled Chicken': ['grilled chicken', 'peri peri', 'piri piri', 'nandos', "nando's"],
    'Rotisserie Chicken': ['rotisserie', 'whole chicken'],
    
    # === CUISINE CATEGORIES (for general mentions) ===
    'Chinese': ['chinese'],
    'Thai': ['thai'],
    'Indian': ['indian'],
    'Japanese': ['japanese'],
    'Mexican': ['mexican'],
    'Mediterranean': ['mediterranean', 'greek'],
    'Vegetarian': ['vegetarian', 'veggie', 'vegan', 'plant-based', 'meat-free'],
    'Healthy': ['healthy', 'balanced', 'nutritious', 'low calorie'],
    'Kids Menu': ['kids', 'children', 'child friendly', 'kid friendly', 'plain', 'mild'],
}

def load_dropoff_survey():
    """Load dropoff survey with open-text responses."""
    try:
        df = pd.read_csv(DATA_PATH / "2_ENRICHED" / "DROPOFF_ENRICHED.csv")
        return df
    except Exception as e:
        print(f"Warning: Could not load dropoff survey: {e}")
        return pd.DataFrame()

def load_post_order_survey():
    """Load post-order survey with open-text responses."""
    try:
        df = pd.read_csv(DATA_PATH / "2_ENRICHED" / "post_order_enriched_COMPLETE.csv")
        return df
    except Exception as e:
        print(f"Warning: Could not load post-order survey: {e}")
        return pd.DataFrame()

def load_og_survey():
    """Load OG survey data with wishlist percentages."""
    try:
        with open(DATA_PATH / "3_ANALYSIS" / "extracted_factors_phase1.json", 'r') as f:
            data = json.load(f)
        return data.get('og_survey_dishes', [])
    except Exception as e:
        print(f"Warning: Could not load OG survey: {e}")
        return []

def load_ratings():
    """Load ratings with comments."""
    try:
        df = pd.read_csv(DATA_PATH / "1_SOURCE" / "snowflake" / "DINNEROO_RATINGS.csv")
        return df
    except Exception as e:
        print(f"Warning: Could not load ratings: {e}")
        return pd.DataFrame()

def extract_dish_mentions(text, dish_keywords, requests_only=False):
    """
    Extract dish type mentions from text.
    
    Args:
        text: The text to analyze
        dish_keywords: Dict mapping dish types to keywords
        requests_only: If True, only count if text contains a request pattern
    
    Returns:
        List of dish types mentioned
    """
    if pd.isna(text) or not isinstance(text, str):
        return []
    
    # If requests_only mode, skip text that doesn't contain a request pattern
    if requests_only and not is_request(text):
        return []
    
    text_lower = text.lower()
    mentions = []
    
    for dish_type, keywords in dish_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                mentions.append(dish_type)
                break  # Only count each dish type once per text
    
    return mentions

def analyze_dropoff_open_text(df, requests_only=True):
    """
    Analyze open-text fields from dropoff survey.
    
    Note: Dropoff survey questions are inherently request-focused 
    ("What would you like to see?"), so we still apply request filtering
    but these questions naturally yield request-style responses.
    """
    mentions = Counter()
    
    # Key open-text columns - these are request-focused questions
    text_columns = [
        'What dishes and cuisines would you like to see more of? (please list as many as you can)',
        'What kid-friendly options would you like to see? (please be as descriptive as possible)',
        'What would you like to customise or add? (please describe as much as you can)',
        'What improvements would you suggest (if any) to the "Family Dinneroo" or "Feed the Family for £25" offering?'
    ]
    
    for col in text_columns:
        if col in df.columns:
            for text in df[col].dropna():
                # For dropoff, questions are request-focused so we're less strict
                # but still filter to ensure dish mentions are in request context
                dish_mentions = extract_dish_mentions(text, DISH_KEYWORDS, requests_only=False)
                mentions.update(dish_mentions)
    
    return dict(mentions)

def analyze_post_order_open_text(df, requests_only=True):
    """
    Analyze open-text fields from post-order survey.
    
    IMPORTANT: These questions can include complaints ("the curry was cold")
    or neutral mentions ("the lasagne was ok"). We filter to only count
    text that contains request patterns ("wish you had", "would love to see").
    """
    mentions = Counter()
    requests_found = 0
    total_responses = 0
    
    # Key open-text columns - these may contain complaints, so filter strictly
    text_columns = [
        'Overall, how could this dish be improved to suit your needs better?',
        'What further improvements would you suggest (if any)?'
    ]
    
    for col in text_columns:
        if col in df.columns:
            for text in df[col].dropna():
                total_responses += 1
                # Apply strict request filtering for post-order
                dish_mentions = extract_dish_mentions(text, DISH_KEYWORDS, requests_only=requests_only)
                if dish_mentions:
                    requests_found += 1
                mentions.update(dish_mentions)
    
    print(f"      Post-order: {requests_found}/{total_responses} responses contained request patterns")
    return dict(mentions)

def analyze_ratings_comments(df, requests_only=True):
    """
    Analyze rating comments for dish mentions.
    
    IMPORTANT: Rating comments are general feedback and often contain
    complaints or neutral mentions. We filter strictly for request patterns.
    """
    mentions = Counter()
    requests_found = 0
    total_comments = 0
    
    if 'RATING_COMMENT' in df.columns:
        for text in df['RATING_COMMENT'].dropna():
            total_comments += 1
            # Apply strict request filtering for ratings
            dish_mentions = extract_dish_mentions(text, DISH_KEYWORDS, requests_only=requests_only)
            if dish_mentions:
                requests_found += 1
            mentions.update(dish_mentions)
    
    print(f"      Ratings: {requests_found}/{total_comments} comments contained request patterns")
    return dict(mentions)

def analyze_og_survey_wishlist(og_data):
    """Extract wishlist percentages from OG survey."""
    wishlist = {}
    
    for item in og_data:
        dish = item.get('dish', '')
        wishlist_pct = item.get('wishlist_pct', '0%')
        
        # Parse percentage
        try:
            pct = float(wishlist_pct.replace('%', ''))
        except:
            pct = 0
        
        # Map to our dish types
        dish_lower = dish.lower()
        
        # Direct mappings from OG survey dish names to our dish types
        mappings = {
            # Italian
            'pizza': 'Pizza',
            'boiled pasta': 'Pasta',
            'baked pasta': 'Baked Pasta',
            'filled pasta': 'Filled Pasta',
            'lasagne': 'Lasagne',
            'risotto': 'Risotto',
            'gnocchi': 'Gnocchi',
            # Asian
            'curry rice': 'Curry',
            'thai curry': 'Thai Curry',
            'katsu curry': 'Katsu',
            'stir fry noodles': 'Noodles',
            'thai noodles': 'Noodles',
            'ramen': 'Ramen',
            'rice bowl fried rice': 'Rice Bowl',
            # Mexican
            'fajitas burritos': 'Fajitas',
            'tacos': 'Tacos',
            'chilli': 'Chilli',
            # British
            'burger chips': 'Burger',
            'fish chips': 'Fish & Chips',
            'mash pie': 'Pie',
            'pastry pie': 'Pie',
            'meat veg': 'Roast Dinner',
            'sausage mash': 'Bangers & Mash',
            'jacket potato': 'Jacket Potato',
            'casserole stew': 'Casserole',
            'sandwich toastie': 'Sandwich',
            'meat chips': 'Burger',
            # Other
            'piri': 'Grilled Chicken',
            'cajun chicken': 'Grilled Chicken',
            'jerk chicken': 'Jerk Chicken',
            'chicken': 'Grilled Chicken',
            'soup': 'Soup',
            'salad': 'Salad',
            'cous cous': 'Cous Cous',
            'paella': 'Paella',
            'stroganoff': 'Stroganoff',
            'tagine': 'Tagine',
        }
        
        for key, dish_type in mappings.items():
            if key in dish_lower:
                if dish_type not in wishlist or pct > wishlist[dish_type]:
                    wishlist[dish_type] = pct
                break
    
    return wishlist

def analyze_dropoff_barriers(df):
    """Analyze structured barrier responses for implicit demand."""
    barrier_signals = Counter()
    
    # Barrier columns that indicate unmet demand
    barrier_columns = {
        "There wasn't an option that suited everyone:Which of these best describe why it didn't work for you? (select all that apply)": ['Variety', 'Kids Menu'],
        "The meals didn't look appealing to my children:Which of these best describe why it didn't work for you? (select all that apply)": ['Kids Menu'],
        "I wasn't sure if the food fitted dietary needs:Which of these best describe why it didn't work for you? (select all that apply)": ['Vegetarian', 'Healthy'],
    }
    
    for col, dish_types in barrier_columns.items():
        if col in df.columns:
            count = df[col].notna().sum()
            for dish_type in dish_types:
                barrier_signals[dish_type] += count
    
    return dict(barrier_signals)

def calculate_latent_demand_scores(dropoff_mentions, post_order_mentions, ratings_mentions, 
                                   og_wishlist, barrier_signals):
    """Combine all signals into a latent demand score."""
    
    # Get all dish types
    all_dishes = set()
    all_dishes.update(dropoff_mentions.keys())
    all_dishes.update(post_order_mentions.keys())
    all_dishes.update(ratings_mentions.keys())
    all_dishes.update(og_wishlist.keys())
    all_dishes.update(barrier_signals.keys())
    
    # Also include dishes from opportunity scores
    try:
        opp_df = pd.read_csv(DATA_PATH / "3_ANALYSIS" / "dish_opportunity_scores.csv")
        all_dishes.update(opp_df['dish_type'].tolist())
    except:
        pass
    
    results = []
    
    for dish in all_dishes:
        # Get counts from each source
        dropoff_count = dropoff_mentions.get(dish, 0)
        post_order_count = post_order_mentions.get(dish, 0)
        ratings_count = ratings_mentions.get(dish, 0)
        wishlist_pct = og_wishlist.get(dish, 0)
        barrier_count = barrier_signals.get(dish, 0)
        
        # Total mentions
        total_mentions = dropoff_count + post_order_count + ratings_count
        
        # Weighted score (following plan weights)
        # Open-text: 35%, Wishlist: 20%, Barriers: 20% (transcripts 25% not available programmatically)
        # Normalize and combine
        
        # Normalize mentions (assume 50+ is max)
        mentions_score = min(total_mentions / 50, 1.0) * 5
        
        # Normalize wishlist (assume 20% is max)
        wishlist_score = min(wishlist_pct / 20, 1.0) * 5
        
        # Normalize barriers (assume 100+ is max)
        barrier_score = min(barrier_count / 100, 1.0) * 5
        
        # Weighted combination
        latent_demand_score = (
            mentions_score * 0.45 +  # Open-text (35%) + some transcript proxy
            wishlist_score * 0.30 +   # OG Survey wishlist (20% + buffer)
            barrier_score * 0.25      # Barriers (20%)
        )
        
        # Convert to 1-5 scale
        final_score = max(1, min(5, round(latent_demand_score + 1)))
        
        results.append({
            'dish_type': dish,
            'dropoff_requests': dropoff_count,
            'post_order_requests': post_order_count,
            'ratings_requests': ratings_count,
            'open_text_requests': total_mentions,  # Renamed for clarity
            'og_wishlist_pct': wishlist_pct,
            'barrier_signals': barrier_count,
            'latent_demand_raw': round(latent_demand_score, 2),
            'latent_demand_score': final_score
        })
    
    return pd.DataFrame(results)

def main():
    """Run the latent demand extraction."""
    print("=" * 60)
    print("LATENT DEMAND EXTRACTION")
    print("=" * 60)
    
    # Load data sources
    print("\n1. Loading data sources...")
    dropoff_df = load_dropoff_survey()
    print(f"   Dropoff survey: {len(dropoff_df)} responses")
    
    post_order_df = load_post_order_survey()
    print(f"   Post-order survey: {len(post_order_df)} responses")
    
    og_data = load_og_survey()
    print(f"   OG survey dishes: {len(og_data)} dishes")
    
    ratings_df = load_ratings()
    print(f"   Ratings: {len(ratings_df)} ratings")
    
    # Extract mentions from each source (with request filtering)
    print("\n2. Extracting dish REQUEST mentions (filtered)...")
    print("   Filtering for patterns: 'wish', 'would love', 'please add', etc.")
    
    dropoff_mentions = analyze_dropoff_open_text(dropoff_df, requests_only=True) if len(dropoff_df) > 0 else {}
    print(f"   Dropoff open-text: {sum(dropoff_mentions.values())} request mentions across {len(dropoff_mentions)} dish types")
    
    post_order_mentions = analyze_post_order_open_text(post_order_df, requests_only=True) if len(post_order_df) > 0 else {}
    print(f"   Post-order open-text: {sum(post_order_mentions.values())} request mentions across {len(post_order_mentions)} dish types")
    
    ratings_mentions = analyze_ratings_comments(ratings_df, requests_only=True) if len(ratings_df) > 0 else {}
    print(f"   Ratings comments: {sum(ratings_mentions.values())} request mentions across {len(ratings_mentions)} dish types")
    
    # Extract OG survey wishlist
    print("\n3. Extracting OG survey wishlist...")
    og_wishlist = analyze_og_survey_wishlist(og_data)
    print(f"   Wishlist data for {len(og_wishlist)} dish types")
    
    # Analyze barriers
    print("\n4. Analyzing barrier signals...")
    barrier_signals = analyze_dropoff_barriers(dropoff_df) if len(dropoff_df) > 0 else {}
    print(f"   Barrier signals for {len(barrier_signals)} categories")
    
    # Calculate combined scores
    print("\n5. Calculating latent demand scores...")
    results_df = calculate_latent_demand_scores(
        dropoff_mentions, post_order_mentions, ratings_mentions,
        og_wishlist, barrier_signals
    )
    print(f"   Scored {len(results_df)} dish types")
    
    # Sort by score
    results_df = results_df.sort_values('latent_demand_score', ascending=False)
    
    # Save output
    output_path = DATA_PATH / "3_ANALYSIS" / "latent_demand_scores.csv"
    results_df.to_csv(output_path, index=False)
    print(f"\n6. Saved to: {output_path}")
    
    # Print top dishes
    print("\n" + "=" * 60)
    print("TOP 15 DISHES BY LATENT DEMAND (REQUEST-FILTERED)")
    print("=" * 60)
    print(results_df[['dish_type', 'open_text_requests', 'og_wishlist_pct', 'latent_demand_score']].head(15).to_string(index=False))
    
    # Save summary JSON
    summary = {
        'generated': datetime.now().isoformat(),
        'sources': {
            'dropoff_responses': len(dropoff_df),
            'post_order_responses': len(post_order_df),
            'ratings': len(ratings_df),
            'og_survey_dishes': len(og_data)
        },
        'total_dish_types_scored': len(results_df),
        'top_10_by_latent_demand': results_df.head(10)[['dish_type', 'latent_demand_score']].to_dict('records')
    }
    
    summary_path = DATA_PATH / "3_ANALYSIS" / "latent_demand_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary to: {summary_path}")
    
    print("\n✓ Latent demand extraction complete!")
    
    return results_df

if __name__ == "__main__":
    main()

