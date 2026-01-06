"""
Script: 04_consolidate_surveys.py
Phase: 1 - Data Preparation
Purpose: Consolidate survey exports from Alchemer, handling deduplication

This script:
1. Merges new Alchemer exports with existing consolidated files
2. Deduplicates using Response ID
3. Produces clean consolidated files for the pipeline

Usage:
    python scripts/phase1_data/04_consolidate_surveys.py --all
    python scripts/phase1_data/04_consolidate_surveys.py --post-order
    python scripts/phase1_data/04_consolidate_surveys.py --dropoff
"""

import argparse
import logging
import pandas as pd
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
SURVEYS_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE" / "surveys"
LOGS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "logs"


def consolidate_post_order():
    """
    Consolidate Post-Order Survey data.
    
    The post-order survey is ONGOING, so we need to:
    1. Load existing consolidated file
    2. Load new Alchemer export
    3. Merge and deduplicate on Response ID
    4. Save updated consolidated file
    """
    logger.info("=" * 60)
    logger.info("CONSOLIDATING POST-ORDER SURVEY")
    logger.info("=" * 60)
    
    existing_path = SURVEYS_DIR / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    new_path = SURVEYS_DIR / "POST_ORDER_ALCHEMER_2026-01-06.csv"
    
    if not new_path.exists():
        logger.warning(f"New export not found: {new_path}")
        logger.info("Looking for any POST_ORDER_ALCHEMER_*.csv file...")
        alchemer_files = list(SURVEYS_DIR.glob("POST_ORDER_ALCHEMER_*.csv"))
        if alchemer_files:
            new_path = sorted(alchemer_files)[-1]  # Most recent
            logger.info(f"Found: {new_path}")
        else:
            logger.error("No Alchemer export found for post-order survey")
            return None
    
    # Load existing
    if existing_path.exists():
        existing_df = pd.read_csv(existing_path)
        logger.info(f"Existing consolidated: {len(existing_df)} rows")
    else:
        existing_df = pd.DataFrame()
        logger.info("No existing consolidated file - starting fresh")
    
    # Load new export
    new_df = pd.read_csv(new_path)
    logger.info(f"New Alchemer export: {len(new_df)} rows")
    
    # Check for Response ID column
    if 'Response ID' not in new_df.columns:
        logger.error("New export missing 'Response ID' column")
        return None
    
    # Standardize column name in existing if needed
    if len(existing_df) > 0 and 'Response ID' not in existing_df.columns:
        # Try to find similar column
        for col in existing_df.columns:
            if 'response' in col.lower() and 'id' in col.lower():
                existing_df = existing_df.rename(columns={col: 'Response ID'})
                break
    
    # Get date ranges for logging
    if 'Date Submitted' in new_df.columns:
        new_dates = pd.to_datetime(new_df['Date Submitted'], errors='coerce')
        logger.info(f"New export date range: {new_dates.min()} to {new_dates.max()}")
    
    if len(existing_df) > 0 and 'Date Submitted' in existing_df.columns:
        existing_dates = pd.to_datetime(existing_df['Date Submitted'], errors='coerce')
        logger.info(f"Existing date range: {existing_dates.min()} to {existing_dates.max()}")
    
    # Merge and deduplicate
    if len(existing_df) > 0:
        # Combine both dataframes
        combined = pd.concat([existing_df, new_df], ignore_index=True)
        logger.info(f"Combined (before dedup): {len(combined)} rows")
        
        # Deduplicate on Response ID, keeping the most recent (last) occurrence
        # Sort by Date Submitted first so the most recent is kept
        if 'Date Submitted' in combined.columns:
            combined['_sort_date'] = pd.to_datetime(combined['Date Submitted'], errors='coerce')
            combined = combined.sort_values('_sort_date', na_position='first')
            combined = combined.drop(columns=['_sort_date'])
        
        # Drop duplicates keeping last (most recent)
        before_dedup = len(combined)
        combined = combined.drop_duplicates(subset=['Response ID'], keep='last')
        duplicates_removed = before_dedup - len(combined)
        
        logger.info(f"Duplicates removed: {duplicates_removed}")
        logger.info(f"Final consolidated: {len(combined)} rows")
        
        # Calculate net new
        net_new = len(combined) - len(existing_df)
        logger.info(f"Net new responses: {net_new}")
    else:
        combined = new_df
        logger.info(f"Using new export as consolidated: {len(combined)} rows")
    
    # Save consolidated file
    combined.to_csv(existing_path, index=False)
    logger.info(f"Saved to: {existing_path}")
    
    # Log summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'survey': 'post_order',
        'existing_rows': len(existing_df) if len(existing_df) > 0 else 0,
        'new_export_rows': len(new_df),
        'final_rows': len(combined),
        'net_new': len(combined) - (len(existing_df) if len(existing_df) > 0 else 0)
    }
    
    return combined


def consolidate_dropoff():
    """
    Consolidate Dropoff Survey data.
    
    The dropoff survey is CLOSED, so we:
    1. Compare new export with existing
    2. If new has more/equal rows, replace entirely
    3. Log any discrepancies
    """
    logger.info("=" * 60)
    logger.info("CONSOLIDATING DROPOFF SURVEY")
    logger.info("=" * 60)
    
    existing_path = SURVEYS_DIR / "DROPOFF_SURVEY-CONSOLIDATED.csv"
    new_path = SURVEYS_DIR / "DROPOFF_ALCHEMER_2026-01-06.csv"
    
    if not new_path.exists():
        logger.warning(f"New export not found: {new_path}")
        logger.info("Looking for any DROPOFF_ALCHEMER_*.csv file...")
        alchemer_files = list(SURVEYS_DIR.glob("DROPOFF_ALCHEMER_*.csv"))
        if alchemer_files:
            new_path = sorted(alchemer_files)[-1]
            logger.info(f"Found: {new_path}")
        else:
            logger.error("No Alchemer export found for dropoff survey")
            return None
    
    # Load existing
    if existing_path.exists():
        existing_df = pd.read_csv(existing_path)
        logger.info(f"Existing consolidated: {len(existing_df)} rows")
    else:
        existing_df = pd.DataFrame()
        logger.info("No existing consolidated file")
    
    # Load new export
    new_df = pd.read_csv(new_path)
    logger.info(f"New Alchemer export: {len(new_df)} rows")
    
    # For dropoff (closed survey), just use the new export if it has more data
    if len(new_df) >= len(existing_df):
        logger.info(f"New export has {len(new_df) - len(existing_df)} more rows - using new export")
        new_df.to_csv(existing_path, index=False)
        logger.info(f"Saved to: {existing_path}")
        return new_df
    else:
        logger.warning(f"New export has FEWER rows ({len(new_df)}) than existing ({len(existing_df)})")
        logger.warning("Keeping existing file - please verify the Alchemer export")
        return existing_df


def main():
    parser = argparse.ArgumentParser(description='Consolidate survey exports from Alchemer')
    parser.add_argument('--all', action='store_true', help='Consolidate all surveys')
    parser.add_argument('--post-order', action='store_true', help='Consolidate post-order survey only')
    parser.add_argument('--dropoff', action='store_true', help='Consolidate dropoff survey only')
    
    args = parser.parse_args()
    
    # Default to all if no specific survey selected
    if not any([args.all, args.post_order, args.dropoff]):
        args.all = True
    
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    if args.all or args.post_order:
        results['post_order'] = consolidate_post_order()
    
    if args.all or args.dropoff:
        results['dropoff'] = consolidate_dropoff()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("CONSOLIDATION COMPLETE")
    logger.info("=" * 60)
    
    for survey, df in results.items():
        if df is not None:
            logger.info(f"{survey}: {len(df)} rows")
        else:
            logger.info(f"{survey}: FAILED")
    
    return results


if __name__ == "__main__":
    main()

