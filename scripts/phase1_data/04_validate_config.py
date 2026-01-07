"""
Script: 04_validate_config.py
Phase: 1 - Data Preparation
Purpose: Validate mvp_thresholds.json config against actual performance data

This script ensures that all cuisine/dish recommendations in the config are
evidence-based and not assumptions. It will FAIL the pipeline if:
1. Any recommendation is missing a 'source' field
2. Any recommended cuisine has repeat rate below threshold
3. Any recommended cuisine has rating below minimum

This prevents unfounded recommendations from being added to the config.

Inputs:
    - config/mvp_thresholds.json
    - DATA/3_ANALYSIS/cuisine_performance.csv
    - docs/data/priority_dishes.json

Outputs:
    - DATA/2_ENRICHED/config_validation_report.json
    - Console output with validation results
"""

import logging
import json
import pandas as pd
import sys
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
CONFIG_DIR = PROJECT_ROOT / "config"
ANALYSIS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
ENRICHED_DIR = PROJECT_ROOT / "DATA" / "2_ENRICHED"
DOCS_DIR = PROJECT_ROOT / "docs" / "data"

# Validation thresholds
MIN_REPEAT_RATE_REQUIRED = 0.15  # Required cuisines must have at least 15% repeat rate
MIN_REPEAT_RATE_RECOMMENDED = 0.15  # Recommended cuisines must have at least 15% repeat rate
MIN_RATING = 4.0  # All cuisines must have at least 4.0 rating
WARN_REPEAT_RATE = 0.18  # Warn if below this but above minimum


def load_config():
    """Load the MVP thresholds config."""
    config_path = CONFIG_DIR / "mvp_thresholds.json"
    if not config_path.exists():
        logger.error(f"Config not found: {config_path}")
        return None
    
    with open(config_path) as f:
        return json.load(f)


def load_cuisine_performance():
    """Load cuisine performance data."""
    perf_path = ANALYSIS_DIR / "cuisine_performance.csv"
    if not perf_path.exists():
        logger.warning(f"Cuisine performance not found: {perf_path}")
        return None
    
    return pd.read_csv(perf_path)


def load_dish_rankings():
    """Load dish priority rankings."""
    dishes_path = DOCS_DIR / "priority_dishes.json"
    if not dishes_path.exists():
        logger.warning(f"Priority dishes not found: {dishes_path}")
        return None
    
    with open(dishes_path) as f:
        return json.load(f)


def find_cuisine_in_data(cuisine_name: str, perf_df: pd.DataFrame) -> dict:
    """Find cuisine in performance data, handling name variations."""
    if perf_df is None:
        return None
    
    # Try exact match first (case-insensitive)
    cuisine_lower = cuisine_name.lower()
    
    # Handle common variations
    search_terms = [cuisine_lower]
    if 'japanese' in cuisine_lower or 'asian' in cuisine_lower:
        search_terms.extend(['japanese', 'asian'])
    if 'thai' in cuisine_lower or 'vietnamese' in cuisine_lower:
        search_terms.extend(['thai', 'vietnamese', 'pho'])
    if 'mediterranean' in cuisine_lower or 'healthy' in cuisine_lower:
        search_terms.extend(['mediterranean', 'healthy', 'salads'])
    if 'chicken' in cuisine_lower:
        search_terms.extend(['chicken'])
    if 'mexican' in cuisine_lower or 'latin' in cuisine_lower:
        search_terms.extend(['mexican'])
    if 'salad' in cuisine_lower or 'fresh' in cuisine_lower:
        search_terms.extend(['salads', 'healthy'])
    
    # Search for matches
    for term in search_terms:
        matches = perf_df[perf_df['CUISINE'].str.lower().str.contains(term, na=False)]
        if len(matches) > 0:
            # Return best match (highest order count)
            best = matches.loc[matches['order_count'].idxmax()]
            return {
                'cuisine': best['CUISINE'],
                'order_count': int(best['order_count']),
                'repeat_rate': float(best['repeat_rate']),
                'avg_rating': float(best['avg_rating'])
            }
    
    return None


def validate_cuisine(cuisine_config: dict, perf_df: pd.DataFrame, 
                     min_repeat_rate: float, cuisine_type: str) -> dict:
    """Validate a single cuisine recommendation."""
    result = {
        'cuisine': cuisine_config.get('cuisine'),
        'type': cuisine_type,
        'status': 'UNKNOWN',
        'issues': [],
        'warnings': []
    }
    
    # Check for source citation
    if 'source' not in cuisine_config:
        result['issues'].append("Missing 'source' field - no evidence citation")
    
    if 'evidence' not in cuisine_config:
        result['issues'].append("Missing 'evidence' field - no performance data")
    
    if 'validated' not in cuisine_config:
        result['warnings'].append("Missing 'validated' field - unknown validation date")
    
    # Check against actual data
    actual_data = find_cuisine_in_data(cuisine_config.get('cuisine', ''), perf_df)
    
    if actual_data:
        result['actual_data'] = actual_data
        
        # Check repeat rate
        if actual_data['repeat_rate'] < min_repeat_rate:
            result['issues'].append(
                f"Repeat rate {actual_data['repeat_rate']:.1%} below threshold {min_repeat_rate:.1%}"
            )
        elif actual_data['repeat_rate'] < WARN_REPEAT_RATE:
            result['warnings'].append(
                f"Repeat rate {actual_data['repeat_rate']:.1%} is marginal (threshold: {min_repeat_rate:.1%})"
            )
        
        # Check rating
        if actual_data['avg_rating'] < MIN_RATING:
            result['issues'].append(
                f"Rating {actual_data['avg_rating']:.2f} below minimum {MIN_RATING}"
            )
        
        # Verify evidence matches actual data (within tolerance)
        if 'evidence' in cuisine_config:
            config_repeat = cuisine_config['evidence'].get('repeat_rate', 0)
            if abs(config_repeat - actual_data['repeat_rate']) > 0.05:
                result['warnings'].append(
                    f"Config repeat_rate ({config_repeat:.1%}) differs from actual ({actual_data['repeat_rate']:.1%})"
                )
    else:
        result['warnings'].append("Could not find cuisine in performance data")
    
    # Determine status
    if result['issues']:
        result['status'] = 'FAIL'
    elif result['warnings']:
        result['status'] = 'WARN'
    else:
        result['status'] = 'PASS'
    
    return result


def validate_not_recommended(not_rec_config: dict, perf_df: pd.DataFrame) -> dict:
    """Validate that 'not_recommended' cuisines are correctly flagged."""
    result = {
        'cuisine': not_rec_config.get('cuisine'),
        'type': 'not_recommended',
        'status': 'PASS',
        'issues': [],
        'warnings': []
    }
    
    # Check for evidence
    if 'source' not in not_rec_config:
        result['warnings'].append("Missing 'source' field")
    
    if 'evidence' not in not_rec_config:
        result['warnings'].append("Missing 'evidence' field")
    
    # Verify the cuisine actually underperforms
    actual_data = find_cuisine_in_data(not_rec_config.get('cuisine', ''), perf_df)
    
    if actual_data:
        result['actual_data'] = actual_data
        
        # If it's flagged as not recommended but actually performs well, that's a warning
        if actual_data['repeat_rate'] >= 0.20:
            result['warnings'].append(
                f"Cuisine has good repeat rate ({actual_data['repeat_rate']:.1%}) - verify exclusion is justified"
            )
    
    if result['warnings']:
        result['status'] = 'WARN'
    
    return result


def main():
    """Main validation function."""
    logger.info("=" * 60)
    logger.info("CONFIG VALIDATION: Checking recommendations against data")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    config = load_config()
    if not config:
        logger.error("Failed to load config")
        sys.exit(1)
    
    perf_df = load_cuisine_performance()
    
    # Validation results
    results = {
        'validation_date': datetime.now().isoformat(),
        'config_version': config.get('version'),
        'cuisines': [],
        'summary': {
            'total': 0,
            'passed': 0,
            'warnings': 0,
            'failed': 0
        }
    }
    
    # Validate required cuisines
    logger.info("\n--- Validating REQUIRED cuisines ---")
    required = config.get('mvp_selection_requirements', {}).get('core_cuisines', {}).get('required', [])
    
    for cuisine in required:
        result = validate_cuisine(cuisine, perf_df, MIN_REPEAT_RATE_REQUIRED, 'required')
        results['cuisines'].append(result)
        results['summary']['total'] += 1
        
        if result['status'] == 'PASS':
            results['summary']['passed'] += 1
            logger.info(f"  PASS: {result['cuisine']}")
        elif result['status'] == 'WARN':
            results['summary']['warnings'] += 1
            logger.warning(f"  WARN: {result['cuisine']}")
            for w in result['warnings']:
                logger.warning(f"        - {w}")
        else:
            results['summary']['failed'] += 1
            logger.error(f"  FAIL: {result['cuisine']}")
            for i in result['issues']:
                logger.error(f"        - {i}")
    
    # Validate recommended cuisines
    logger.info("\n--- Validating RECOMMENDED cuisines ---")
    recommended = config.get('mvp_selection_requirements', {}).get('core_cuisines', {}).get('recommended', [])
    
    for cuisine in recommended:
        result = validate_cuisine(cuisine, perf_df, MIN_REPEAT_RATE_RECOMMENDED, 'recommended')
        results['cuisines'].append(result)
        results['summary']['total'] += 1
        
        if result['status'] == 'PASS':
            results['summary']['passed'] += 1
            logger.info(f"  PASS: {result['cuisine']}")
        elif result['status'] == 'WARN':
            results['summary']['warnings'] += 1
            logger.warning(f"  WARN: {result['cuisine']}")
            for w in result['warnings']:
                logger.warning(f"        - {w}")
        else:
            results['summary']['failed'] += 1
            logger.error(f"  FAIL: {result['cuisine']}")
            for i in result['issues']:
                logger.error(f"        - {i}")
    
    # Validate not_recommended cuisines
    logger.info("\n--- Validating NOT_RECOMMENDED cuisines ---")
    not_recommended = config.get('mvp_selection_requirements', {}).get('core_cuisines', {}).get('not_recommended', [])
    
    for cuisine in not_recommended:
        result = validate_not_recommended(cuisine, perf_df)
        results['cuisines'].append(result)
        results['summary']['total'] += 1
        
        if result['status'] == 'PASS':
            results['summary']['passed'] += 1
            logger.info(f"  PASS: {result['cuisine']} correctly flagged as not recommended")
        else:
            results['summary']['warnings'] += 1
            logger.warning(f"  WARN: {result['cuisine']}")
            for w in result['warnings']:
                logger.warning(f"        - {w}")
    
    # Save validation report
    report_path = ENRICHED_DIR / "config_validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"\nValidation report saved to: {report_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total cuisines checked: {results['summary']['total']}")
    logger.info(f"  PASSED: {results['summary']['passed']}")
    logger.info(f"  WARNINGS: {results['summary']['warnings']}")
    logger.info(f"  FAILED: {results['summary']['failed']}")
    
    # Exit with error if any failures
    if results['summary']['failed'] > 0:
        logger.error("\n❌ CONFIG VALIDATION FAILED")
        logger.error("Fix the issues above before running the pipeline.")
        logger.error("Every recommendation must have evidence from actual data.")
        sys.exit(1)
    elif results['summary']['warnings'] > 0:
        logger.warning("\n⚠️  CONFIG VALIDATION PASSED WITH WARNINGS")
        logger.warning("Review warnings above to ensure recommendations are valid.")
    else:
        logger.info("\n✅ CONFIG VALIDATION PASSED")
        logger.info("All recommendations are evidence-based.")
    
    return results


if __name__ == "__main__":
    main()



