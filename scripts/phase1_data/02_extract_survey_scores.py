"""
Script: 02_extract_survey_scores.py
Phase: 1 - Data
Purpose: Extract survey-backed scores for dishes from all survey sources
Inputs: 
    - DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv
    - DATA/1_SOURCE/surveys/OG_SURVEY.csv
    - DATA/1_SOURCE/surveys/DROPOFF_SURVEY.csv
Outputs: DATA/3_ANALYSIS/survey_backed_scores.csv

This script extracts direct measurements from surveys to inform the
10-factor Family Meal scoring. Survey data takes precedence over estimates.
"""

import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE"
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
CONFIG_DIR = PROJECT_ROOT / "config"


def load_config():
    """Load factor weights configuration."""
    config_path = CONFIG_DIR / "factor_weights.json"
    with open(config_path) as f:
        return json.load(f)


def rate_to_score(rate: float) -> int:
    """Convert a success rate (0-1) to a 1-5 score."""
    if rate >= 0.90:
        return 5
    elif rate >= 0.75:
        return 4
    elif rate >= 0.60:
        return 3
    elif rate >= 0.40:
        return 2
    else:
        return 1


def extract_kid_friendly_scores(post_order_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract kid-friendly scores from Post-Order Survey.
    Uses 'Child 1 (youngest):How did your child(ren) react to the meal?' column.
    Success = 'full and happy' responses.
    """
    logger.info("Extracting kid-friendly scores...")
    
    # Find the child reaction column
    child_cols = [c for c in post_order_df.columns if 'child' in c.lower() and 'react' in c.lower()]
    
    if not child_cols:
        logger.warning("No child reaction column found")
        return pd.DataFrame()
    
    child_col = child_cols[0]
    dish_col = None
    
    # Find dish column
    for col in ['dish_name', 'Dish', 'dish', 'menu_item', 'item_name']:
        if col in post_order_df.columns:
            dish_col = col
            break
    
    if not dish_col:
        logger.warning("No dish column found in post-order survey")
        return pd.DataFrame()
    
    # Calculate success rate per dish
    df = post_order_df[[dish_col, child_col]].dropna()
    df['is_success'] = df[child_col].str.lower().str.contains('full|happy', na=False)
    
    scores = df.groupby(dish_col).agg(
        kid_friendly_rate=('is_success', 'mean'),
        kid_friendly_n=('is_success', 'count')
    ).reset_index()
    
    scores['kid_friendly_score'] = scores['kid_friendly_rate'].apply(rate_to_score)
    scores = scores.rename(columns={dish_col: 'dish_name'})
    
    logger.info(f"  Extracted kid-friendly scores for {len(scores)} dishes")
    return scores


def extract_adult_appeal_scores(post_order_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract adult appeal scores from Post-Order Survey.
    Uses 'How did you feel about the meal?' column.
    Success = 'Loved it' or 'Liked it' responses.
    """
    logger.info("Extracting adult appeal scores...")
    
    adult_cols = [c for c in post_order_df.columns if 'how did you feel' in c.lower()]
    
    if not adult_cols:
        logger.warning("No adult reaction column found")
        return pd.DataFrame()
    
    adult_col = adult_cols[0]
    dish_col = None
    
    for col in ['dish_name', 'Dish', 'dish', 'menu_item', 'item_name']:
        if col in post_order_df.columns:
            dish_col = col
            break
    
    if not dish_col:
        return pd.DataFrame()
    
    df = post_order_df[[dish_col, adult_col]].dropna()
    df['is_success'] = df[adult_col].str.lower().str.contains('loved|liked', na=False)
    
    scores = df.groupby(dish_col).agg(
        adult_appeal_rate=('is_success', 'mean'),
        adult_appeal_n=('is_success', 'count')
    ).reset_index()
    
    scores['adult_appeal_score'] = scores['adult_appeal_rate'].apply(rate_to_score)
    scores = scores.rename(columns={dish_col: 'dish_name'})
    
    logger.info(f"  Extracted adult appeal scores for {len(scores)} dishes")
    return scores


def extract_portion_scores(post_order_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract portion flexibility scores from Post-Order Survey.
    Uses 'There was enough food for everyone' agreement column.
    """
    logger.info("Extracting portion scores...")
    
    portion_cols = [c for c in post_order_df.columns if 'enough food' in c.lower()]
    
    if not portion_cols:
        logger.warning("No portion column found")
        return pd.DataFrame()
    
    portion_col = portion_cols[0]
    dish_col = None
    
    for col in ['dish_name', 'Dish', 'dish', 'menu_item', 'item_name']:
        if col in post_order_df.columns:
            dish_col = col
            break
    
    if not dish_col:
        return pd.DataFrame()
    
    df = post_order_df[[dish_col, portion_col]].dropna()
    df['is_success'] = df[portion_col].str.lower().str.contains('agree|strongly', na=False)
    
    scores = df.groupby(dish_col).agg(
        portion_rate=('is_success', 'mean'),
        portion_n=('is_success', 'count')
    ).reset_index()
    
    scores['portion_flexibility_score'] = scores['portion_rate'].apply(rate_to_score)
    scores = scores.rename(columns={dish_col: 'dish_name'})
    
    logger.info(f"  Extracted portion scores for {len(scores)} dishes")
    return scores


def extract_value_scores(post_order_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract value scores from Post-Order Survey.
    Uses 'Good value for money' selection.
    """
    logger.info("Extracting value scores...")
    
    value_cols = [c for c in post_order_df.columns if 'value' in c.lower() and 'money' in c.lower()]
    
    if not value_cols:
        # Try alternative: why did you choose
        choice_cols = [c for c in post_order_df.columns if 'why did you choose' in c.lower()]
        if choice_cols:
            value_col = choice_cols[0]
        else:
            logger.warning("No value column found")
            return pd.DataFrame()
    else:
        value_col = value_cols[0]
    
    dish_col = None
    for col in ['dish_name', 'Dish', 'dish', 'menu_item', 'item_name']:
        if col in post_order_df.columns:
            dish_col = col
            break
    
    if not dish_col:
        return pd.DataFrame()
    
    df = post_order_df[[dish_col, value_col]].dropna()
    df['is_success'] = df[value_col].str.lower().str.contains('value', na=False)
    
    scores = df.groupby(dish_col).agg(
        value_rate=('is_success', 'mean'),
        value_n=('is_success', 'count')
    ).reset_index()
    
    scores['value_at_25_score'] = scores['value_rate'].apply(rate_to_score)
    scores = scores.rename(columns={dish_col: 'dish_name'})
    
    logger.info(f"  Extracted value scores for {len(scores)} dishes")
    return scores


def extract_healthy_scores(post_order_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract balanced/guilt-free scores from Post-Order Survey.
    Uses 'Healthy option' selection in why did you choose.
    """
    logger.info("Extracting healthy/balanced scores...")
    
    choice_cols = [c for c in post_order_df.columns if 'why did you choose' in c.lower()]
    
    if not choice_cols:
        logger.warning("No choice column found")
        return pd.DataFrame()
    
    choice_col = choice_cols[0]
    dish_col = None
    
    for col in ['dish_name', 'Dish', 'dish', 'menu_item', 'item_name']:
        if col in post_order_df.columns:
            dish_col = col
            break
    
    if not dish_col:
        return pd.DataFrame()
    
    df = post_order_df[[dish_col, choice_col]].dropna()
    df['is_healthy'] = df[choice_col].str.lower().str.contains('healthy', na=False)
    
    scores = df.groupby(dish_col).agg(
        healthy_rate=('is_healthy', 'mean'),
        healthy_n=('is_healthy', 'count')
    ).reset_index()
    
    scores['balanced_guilt_free_score'] = scores['healthy_rate'].apply(rate_to_score)
    scores = scores.rename(columns={dish_col: 'dish_name'})
    
    logger.info(f"  Extracted healthy scores for {len(scores)} dishes")
    return scores


def extract_og_survey_scores(og_survey_path: Path) -> pd.DataFrame:
    """
    Extract shareability and other scores from OG Survey.
    """
    logger.info("Extracting OG Survey scores...")
    
    if not og_survey_path.exists():
        logger.warning("OG Survey not found")
        return pd.DataFrame()
    
    try:
        og_df = pd.read_csv(og_survey_path)
        
        # Look for dish-level ratings
        dish_col = None
        for col in ['dish_name', 'Dish', 'dish', 'DishName']:
            if col in og_df.columns:
                dish_col = col
                break
        
        if not dish_col:
            logger.warning("No dish column in OG Survey")
            return pd.DataFrame()
        
        # Look for shareable column
        share_cols = [c for c in og_df.columns if 'share' in c.lower()]
        
        scores = og_df[[dish_col]].copy()
        scores = scores.rename(columns={dish_col: 'dish_name'})
        
        if share_cols:
            scores['shareability_score'] = og_df[share_cols[0]].apply(
                lambda x: 5 if str(x).lower() == 'high' else (3 if str(x).lower() == 'medium' else 2)
            )
        
        logger.info(f"  Extracted OG Survey scores for {len(scores)} dishes")
        return scores.drop_duplicates(subset=['dish_name'])
        
    except Exception as e:
        logger.error(f"Error processing OG Survey: {e}")
        return pd.DataFrame()


def merge_all_scores(score_dfs: list) -> pd.DataFrame:
    """Merge all score dataframes on dish_name."""
    if not score_dfs:
        return pd.DataFrame()
    
    # Start with first non-empty dataframe
    merged = None
    for df in score_dfs:
        if df is not None and len(df) > 0:
            if merged is None:
                merged = df
            else:
                merged = merged.merge(df, on='dish_name', how='outer')
    
    return merged if merged is not None else pd.DataFrame()


def calculate_evidence_type(row: pd.Series) -> str:
    """
    Determine evidence type based on how many factors have survey data.
    Measured: 3+ factors have survey data
    Blended: 1-2 factors have survey data
    Estimated: No survey data
    """
    score_cols = [c for c in row.index if c.endswith('_score') and not c.startswith('overall')]
    n_cols = [c for c in row.index if c.endswith('_n')]
    
    measured_count = 0
    for n_col in n_cols:
        if pd.notna(row.get(n_col)) and row.get(n_col, 0) >= 5:
            measured_count += 1
    
    if measured_count >= 3:
        return "Measured"
    elif measured_count >= 1:
        return "Blended"
    else:
        return "Estimated"


def main():
    """Main function to extract all survey-backed scores."""
    logger.info("=" * 60)
    logger.info("PHASE 1: Extracting Survey-Backed Scores")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load Post-Order Survey
    post_order_path = SOURCE_DIR / "surveys" / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    og_survey_path = SOURCE_DIR / "surveys" / "OG_SURVEY.csv"
    
    score_dfs = []
    
    if post_order_path.exists():
        post_order_df = pd.read_csv(post_order_path)
        logger.info(f"Loaded Post-Order Survey: {len(post_order_df)} rows")
        
        # Extract scores from Post-Order Survey
        score_dfs.append(extract_kid_friendly_scores(post_order_df))
        score_dfs.append(extract_adult_appeal_scores(post_order_df))
        score_dfs.append(extract_portion_scores(post_order_df))
        score_dfs.append(extract_value_scores(post_order_df))
        score_dfs.append(extract_healthy_scores(post_order_df))
    else:
        logger.warning(f"Post-Order Survey not found at {post_order_path}")
    
    # Extract from OG Survey
    score_dfs.append(extract_og_survey_scores(og_survey_path))
    
    # Merge all scores
    merged_scores = merge_all_scores([df for df in score_dfs if df is not None and len(df) > 0])
    
    if len(merged_scores) > 0:
        # Calculate evidence type
        merged_scores['evidence_type'] = merged_scores.apply(calculate_evidence_type, axis=1)
        
        # Calculate total sample size
        n_cols = [c for c in merged_scores.columns if c.endswith('_n')]
        merged_scores['total_survey_n'] = merged_scores[n_cols].sum(axis=1)
        
        # Save
        output_path = OUTPUT_DIR / "survey_backed_scores.csv"
        merged_scores.to_csv(output_path, index=False)
        
        logger.info("\n" + "=" * 60)
        logger.info("SURVEY EXTRACTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total dishes with survey data: {len(merged_scores)}")
        logger.info(f"Evidence type distribution:")
        logger.info(merged_scores['evidence_type'].value_counts().to_string())
        logger.info(f"\nSaved to: {output_path}")
    else:
        logger.warning("No survey scores extracted")
    
    return merged_scores


if __name__ == "__main__":
    main()



