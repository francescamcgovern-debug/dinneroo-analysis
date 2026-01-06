"""
Script: 01_load_sources.py
Phase: 1 - Data
Purpose: Load and validate all data sources, create unified data catalog
Inputs: DATA/1_SOURCE/* (all raw data files)
Outputs: DATA/2_ENRICHED/data_catalog.json (inventory of available data)

This script scans all source data and creates a catalog that subsequent
scripts can use to understand what data is available.
"""

import logging
import json
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
SOURCE_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE"
ENRICHED_DIR = PROJECT_ROOT / "DATA" / "2_ENRICHED"
OUTPUT_FILE = ENRICHED_DIR / "data_catalog.json"


def scan_csv_file(filepath: Path) -> dict:
    """Scan a CSV file and return metadata."""
    try:
        df = pd.read_csv(filepath, nrows=5)  # Just peek at first 5 rows
        full_df = pd.read_csv(filepath)
        return {
            "path": str(filepath.relative_to(PROJECT_ROOT)),
            "rows": len(full_df),
            "columns": list(df.columns),
            "column_count": len(df.columns),
            "file_size_kb": filepath.stat().st_size / 1024,
            "status": "valid"
        }
    except Exception as e:
        return {
            "path": str(filepath.relative_to(PROJECT_ROOT)),
            "status": "error",
            "error": str(e)
        }


def load_snowflake_sources() -> dict:
    """Load all Snowflake data sources."""
    snowflake_dir = SOURCE_DIR / "snowflake"
    sources = {}
    
    expected_files = [
        "DINNEROO_ORDERS.csv",
        "DINNEROO_RATINGS.csv", 
        "DINNEROO_MENU_CATALOG.csv",
        "FULL_ORDER_HISTORY.csv"
    ]
    
    for filename in expected_files:
        filepath = snowflake_dir / filename
        if filepath.exists():
            sources[filename] = scan_csv_file(filepath)
            logger.info(f"✓ Loaded {filename}: {sources[filename].get('rows', 'N/A')} rows")
        else:
            sources[filename] = {"status": "missing", "path": str(filepath)}
            logger.warning(f"✗ Missing: {filename}")
    
    return sources


def load_survey_sources() -> dict:
    """Load all survey data sources."""
    survey_dir = SOURCE_DIR / "surveys"
    sources = {}
    
    expected_files = [
        "OG_SURVEY.csv",
        "DROPOFF_SURVEY.csv",
        "POST_ORDER_SURVEY-CONSOLIDATED.csv",
        "PULSE_SURVEY.csv"
    ]
    
    for filename in expected_files:
        filepath = survey_dir / filename
        if filepath.exists():
            sources[filename] = scan_csv_file(filepath)
            logger.info(f"✓ Loaded {filename}: {sources[filename].get('rows', 'N/A')} rows")
        else:
            sources[filename] = {"status": "missing", "path": str(filepath)}
            logger.warning(f"✗ Missing: {filename}")
    
    # Also scan for any other CSV files
    if survey_dir.exists():
        for filepath in survey_dir.glob("*.csv"):
            if filepath.name not in expected_files:
                sources[filepath.name] = scan_csv_file(filepath)
                logger.info(f"✓ Found additional: {filepath.name}")
    
    return sources


def load_qualitative_sources() -> dict:
    """Load qualitative data sources (transcripts, etc.)."""
    qual_dir = SOURCE_DIR / "qualitative"
    sources = {}
    
    if qual_dir.exists():
        for filepath in qual_dir.glob("*.csv"):
            sources[filepath.name] = scan_csv_file(filepath)
            logger.info(f"✓ Loaded qualitative: {filepath.name}")
        
        for filepath in qual_dir.glob("*.txt"):
            sources[filepath.name] = {
                "path": str(filepath.relative_to(PROJECT_ROOT)),
                "file_size_kb": filepath.stat().st_size / 1024,
                "status": "valid",
                "type": "text"
            }
            logger.info(f"✓ Found text file: {filepath.name}")
    
    return sources


def load_reference_sources() -> dict:
    """Load reference data (zones, partners, etc.)."""
    ref_dir = SOURCE_DIR / "reference"
    sources = {}
    
    if ref_dir.exists():
        for filepath in ref_dir.glob("*.csv"):
            sources[filepath.name] = scan_csv_file(filepath)
            logger.info(f"✓ Loaded reference: {filepath.name}")
    
    return sources


def create_data_summary(catalog: dict) -> dict:
    """Create a summary of available data."""
    summary = {
        "total_sources": 0,
        "valid_sources": 0,
        "missing_sources": 0,
        "total_rows": 0,
        "by_category": {}
    }
    
    for category, sources in catalog["sources"].items():
        category_stats = {"valid": 0, "missing": 0, "rows": 0}
        for name, info in sources.items():
            summary["total_sources"] += 1
            if info.get("status") == "valid":
                summary["valid_sources"] += 1
                category_stats["valid"] += 1
                category_stats["rows"] += info.get("rows", 0)
                summary["total_rows"] += info.get("rows", 0)
            elif info.get("status") == "missing":
                summary["missing_sources"] += 1
                category_stats["missing"] += 1
        summary["by_category"][category] = category_stats
    
    return summary


def main():
    """Main function to load all data sources."""
    logger.info("=" * 60)
    logger.info("PHASE 1: Loading Data Sources")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build catalog
    catalog = {
        "generated_at": datetime.now().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "sources": {}
    }
    
    # Load each category
    logger.info("\n--- Snowflake Sources ---")
    catalog["sources"]["snowflake"] = load_snowflake_sources()
    
    logger.info("\n--- Survey Sources ---")
    catalog["sources"]["surveys"] = load_survey_sources()
    
    logger.info("\n--- Qualitative Sources ---")
    catalog["sources"]["qualitative"] = load_qualitative_sources()
    
    logger.info("\n--- Reference Sources ---")
    catalog["sources"]["reference"] = load_reference_sources()
    
    # Create summary
    catalog["summary"] = create_data_summary(catalog)
    
    # Save catalog
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    logger.info("\n" + "=" * 60)
    logger.info("DATA CATALOG SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total sources: {catalog['summary']['total_sources']}")
    logger.info(f"Valid sources: {catalog['summary']['valid_sources']}")
    logger.info(f"Missing sources: {catalog['summary']['missing_sources']}")
    logger.info(f"Total rows: {catalog['summary']['total_rows']:,}")
    logger.info(f"\nCatalog saved to: {OUTPUT_FILE}")
    
    # Validation
    assert catalog['summary']['valid_sources'] > 0, "No valid data sources found!"
    
    return catalog


if __name__ == "__main__":
    main()

