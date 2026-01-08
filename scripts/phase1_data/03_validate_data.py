"""
Script: 03_validate_data.py
Phase: 1 - Data
Purpose: Validate data quality and generate quality report
Inputs: DATA/2_ENRICHED/data_catalog.json, all source files
Outputs: DATA/2_ENRICHED/data_quality_report.json

This script performs quality checks on all data sources and generates
a report that can be used to understand data limitations.
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
ENRICHED_DIR = PROJECT_ROOT / "DATA" / "2_ENRICHED"
ANALYSIS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
CONFIG_DIR = PROJECT_ROOT / "config"


def load_evidence_standards():
    """Load evidence standards configuration."""
    config_path = CONFIG_DIR / "evidence_standards.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def check_required_columns(df: pd.DataFrame, required: list, source_name: str) -> dict:
    """Check if required columns exist."""
    missing = [col for col in required if col not in df.columns]
    present = [col for col in required if col in df.columns]
    
    return {
        "source": source_name,
        "required_columns": required,
        "present": present,
        "missing": missing,
        "status": "pass" if not missing else "fail"
    }


def check_null_rates(df: pd.DataFrame, source_name: str) -> dict:
    """Check null rates for all columns."""
    null_rates = {}
    high_null_cols = []
    
    for col in df.columns:
        null_rate = df[col].isna().mean()
        null_rates[col] = round(null_rate, 3)
        if null_rate > 0.5:
            high_null_cols.append(col)
    
    return {
        "source": source_name,
        "null_rates": null_rates,
        "high_null_columns": high_null_cols,
        "status": "warning" if high_null_cols else "pass"
    }


def check_sample_sizes(df: pd.DataFrame, source_name: str, standards: dict) -> dict:
    """Check if sample sizes meet standards."""
    row_count = len(df)
    
    min_required = standards.get("sample_size_requirements", {})
    
    checks = {
        "source": source_name,
        "row_count": row_count,
        "meets_dish_recommendation": row_count >= min_required.get("dish_recommendation", {}).get("min_orders", 50),
        "meets_zone_assessment": row_count >= min_required.get("zone_assessment", {}).get("min_orders", 100),
        "status": "pass" if row_count >= 50 else "warning"
    }
    
    return checks


def check_date_range(df: pd.DataFrame, source_name: str) -> dict:
    """Check date range of data."""
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    
    date_info = {"source": source_name, "date_columns": []}
    
    for col in date_cols:
        try:
            dates = pd.to_datetime(df[col], errors='coerce')
            valid_dates = dates.dropna()
            if len(valid_dates) > 0:
                date_info["date_columns"].append({
                    "column": col,
                    "min_date": str(valid_dates.min()),
                    "max_date": str(valid_dates.max()),
                    "valid_count": len(valid_dates),
                    "invalid_count": len(dates) - len(valid_dates)
                })
        except Exception:
            pass
    
    return date_info


def check_regional_distribution(df: pd.DataFrame, source_name: str) -> dict:
    """Check regional distribution for bias."""
    region_cols = [col for col in df.columns if 'region' in col.lower() or 'zone' in col.lower() or 'area' in col.lower()]
    
    distribution = {"source": source_name, "regional_checks": []}
    
    for col in region_cols:
        if col in df.columns:
            value_counts = df[col].value_counts()
            top_region = value_counts.index[0] if len(value_counts) > 0 else None
            top_pct = value_counts.iloc[0] / len(df) if len(value_counts) > 0 else 0
            
            distribution["regional_checks"].append({
                "column": col,
                "unique_values": len(value_counts),
                "top_value": top_region,
                "top_percentage": round(top_pct, 3),
                "bias_warning": top_pct > 0.5
            })
    
    return distribution


def validate_orders_data() -> dict:
    """Validate Dinneroo orders data."""
    orders_path = SOURCE_DIR / "snowflake" / "DINNEROO_ORDERS.csv"
    
    if not orders_path.exists():
        return {"source": "DINNEROO_ORDERS", "status": "missing"}
    
    df = pd.read_csv(orders_path)
    standards = load_evidence_standards()
    
    return {
        "source": "DINNEROO_ORDERS",
        "row_count": len(df),
        "columns": check_required_columns(df, ['order_id', 'customer_id', 'zone_name', 'partner_name'], "DINNEROO_ORDERS"),
        "nulls": check_null_rates(df, "DINNEROO_ORDERS"),
        "sample_sizes": check_sample_sizes(df, "DINNEROO_ORDERS", standards),
        "dates": check_date_range(df, "DINNEROO_ORDERS"),
        "regional": check_regional_distribution(df, "DINNEROO_ORDERS"),
        "status": "valid"
    }


def validate_ratings_data() -> dict:
    """Validate ratings data."""
    ratings_path = SOURCE_DIR / "snowflake" / "DINNEROO_RATINGS.csv"
    
    if not ratings_path.exists():
        return {"source": "DINNEROO_RATINGS", "status": "missing"}
    
    df = pd.read_csv(ratings_path)
    
    # Check rating distribution
    rating_col = None
    for col in ['rating', 'star_rating', 'score']:
        if col in df.columns:
            rating_col = col
            break
    
    rating_stats = {}
    if rating_col:
        rating_stats = {
            "mean": round(df[rating_col].mean(), 2),
            "median": round(df[rating_col].median(), 2),
            "std": round(df[rating_col].std(), 2),
            "min": df[rating_col].min(),
            "max": df[rating_col].max()
        }
    
    return {
        "source": "DINNEROO_RATINGS",
        "row_count": len(df),
        "rating_stats": rating_stats,
        "nulls": check_null_rates(df, "DINNEROO_RATINGS"),
        "status": "valid"
    }


def validate_menu_catalog() -> dict:
    """Validate menu catalog data."""
    menu_path = SOURCE_DIR / "snowflake" / "DINNEROO_MENU_CATALOG.csv"
    
    if not menu_path.exists():
        return {"source": "DINNEROO_MENU_CATALOG", "status": "missing"}
    
    df = pd.read_csv(menu_path)
    
    # Check cuisine distribution
    cuisine_col = None
    for col in ['cuisine', 'cuisine_type', 'category']:
        if col in df.columns:
            cuisine_col = col
            break
    
    cuisine_dist = {}
    if cuisine_col:
        cuisine_dist = df[cuisine_col].value_counts().to_dict()
    
    return {
        "source": "DINNEROO_MENU_CATALOG",
        "row_count": len(df),
        "cuisine_distribution": cuisine_dist,
        "unique_partners": df['partner_name'].nunique() if 'partner_name' in df.columns else None,
        "unique_dishes": df['dish_name'].nunique() if 'dish_name' in df.columns else None,
        "status": "valid"
    }


def validate_survey_data() -> dict:
    """Validate survey data."""
    survey_path = SOURCE_DIR / "surveys" / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    
    if not survey_path.exists():
        return {"source": "POST_ORDER_SURVEY", "status": "missing"}
    
    df = pd.read_csv(survey_path)
    
    return {
        "source": "POST_ORDER_SURVEY",
        "row_count": len(df),
        "column_count": len(df.columns),
        "nulls": check_null_rates(df, "POST_ORDER_SURVEY"),
        "regional": check_regional_distribution(df, "POST_ORDER_SURVEY"),
        "status": "valid"
    }


def generate_quality_summary(validations: list) -> dict:
    """Generate overall quality summary."""
    valid_count = sum(1 for v in validations if v.get("status") == "valid")
    missing_count = sum(1 for v in validations if v.get("status") == "missing")
    
    issues = []
    
    for v in validations:
        if v.get("status") == "missing":
            issues.append(f"Missing source: {v.get('source')}")
        if v.get("nulls", {}).get("status") == "warning":
            issues.append(f"High null rates in: {v.get('source')}")
        if v.get("regional", {}).get("regional_checks"):
            for check in v["regional"]["regional_checks"]:
                if check.get("bias_warning"):
                    issues.append(f"Regional bias in {v.get('source')}: {check.get('top_value')} = {check.get('top_percentage')*100:.0f}%")
    
    return {
        "total_sources": len(validations),
        "valid_sources": valid_count,
        "missing_sources": missing_count,
        "issues": issues,
        "overall_status": "pass" if not issues else "warning"
    }


def main():
    """Main function to validate all data."""
    logger.info("=" * 60)
    logger.info("PHASE 1: Data Validation")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    
    validations = []
    
    # Validate each source
    logger.info("\n--- Validating Orders Data ---")
    validations.append(validate_orders_data())
    
    logger.info("\n--- Validating Ratings Data ---")
    validations.append(validate_ratings_data())
    
    logger.info("\n--- Validating Menu Catalog ---")
    validations.append(validate_menu_catalog())
    
    logger.info("\n--- Validating Survey Data ---")
    validations.append(validate_survey_data())
    
    # Generate summary
    summary = generate_quality_summary(validations)
    
    # Build report
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "validations": validations
    }
    
    # Save report
    output_path = ENRICHED_DIR / "data_quality_report.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info("\n" + "=" * 60)
    logger.info("DATA QUALITY SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Valid sources: {summary['valid_sources']}/{summary['total_sources']}")
    logger.info(f"Overall status: {summary['overall_status']}")
    
    if summary['issues']:
        logger.info("\nIssues found:")
        for issue in summary['issues']:
            logger.warning(f"  ⚠ {issue}")
    
    logger.info(f"\nReport saved to: {output_path}")
    
    return report


if __name__ == "__main__":
    main()




