#!/usr/bin/env python3
"""
Data Quality Validation Script

Validates all data sources for the Consumer Insight Dashboard.
Checks: row counts, freshness, null rates, and expected ranges.

Output: DATA/2_ENRICHED/data_quality_report.json

Usage:
    python3 scripts/validate_data_quality.py
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Output paths
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "2_ENRICHED"
OUTPUT_FILE = OUTPUT_DIR / "data_quality_report.json"

# Data source configurations
DATA_SOURCES = {
    # Snowflake sources (behavioral data)
    "snowflake_orders": {
        "path": "DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv",
        "type": "behavioral",
        "min_rows": 50000,
        "expected_rows": 70000,
        "key_columns": ["ORDER_ID", "CUSTOMER_ID", "PARTNER_NAME", "ZONE_NAME", "ORDER_TIMESTAMP"],
        "max_null_rate": 0.1,
        "freshness_days": 7,
        "critical": True
    },
    "snowflake_customers": {
        "path": "DATA/1_SOURCE/snowflake/ALL_DINNEROO_CUSTOMERS.csv",
        "type": "behavioral",
        "min_rows": 10000,
        "expected_rows": 50000,
        "key_columns": ["CUSTOMER_ID", "TOTAL_ORDERS"],
        "max_null_rate": 0.1,
        "freshness_days": 7,
        "critical": True
    },
    "snowflake_ratings": {
        "path": "DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv",
        "type": "behavioral",
        "min_rows": 5000,
        "expected_rows": 10000,
        "key_columns": ["ORDER_ID", "RATING_STARS"],
        "max_null_rate": 0.5,  # Rating comments often null
        "freshness_days": 7,
        "critical": False
    },
    "snowflake_partner_performance": {
        "path": "DATA/1_SOURCE/snowflake/DINNEROO_PARTNER_PERFORMANCE.csv",
        "type": "behavioral",
        "min_rows": 100,
        "expected_rows": 500,
        "key_columns": ["PARTNER_NAME", "ZONE_NAME", "TOTAL_ORDERS"],
        "max_null_rate": 0.1,
        "freshness_days": 7,
        "critical": True
    },
    "snowflake_menu_catalog": {
        "path": "DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv",
        "type": "behavioral",
        "min_rows": 10000,
        "expected_rows": 60000,
        "key_columns": ["PARTNER_NAME", "MENU_ITEM"],
        "max_null_rate": 0.1,
        "freshness_days": 7,
        "critical": False
    },
    
    # Anna's ground truth (supply data)
    "anna_family_dishes": {
        "path": "DATA/3_ANALYSIS/anna_family_dishes.csv",
        "type": "ground_truth",
        "min_rows": 100,
        "expected_rows": 142,
        "key_columns": [],
        "max_null_rate": 0.2,
        "freshness_days": 30,
        "critical": True
    },
    "anna_partner_coverage": {
        "path": "DATA/3_ANALYSIS/anna_partner_coverage.csv",
        "type": "ground_truth",
        "min_rows": 30,
        "expected_rows": 40,
        "key_columns": [],
        "max_null_rate": 0.2,
        "freshness_days": 30,
        "critical": True
    },
    "anna_zone_dish_counts": {
        "path": "DATA/3_ANALYSIS/anna_zone_dish_counts.csv",
        "type": "ground_truth",
        "min_rows": 400,
        "expected_rows": 1306,
        "key_columns": [],
        "max_null_rate": 0.2,
        "freshness_days": 30,
        "critical": True
    },
    
    # Survey data
    "post_order_survey": {
        "path": "DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv",
        "type": "survey",
        "min_rows": 1000,
        "expected_rows": 1500,
        "key_columns": ["Response ID"],
        "max_null_rate": 0.5,  # Surveys have many optional fields
        "freshness_days": 30,
        "critical": True
    },
    "dropoff_survey": {
        "path": "DATA/1_SOURCE/surveys/dropoff_LATEST.csv",
        "type": "survey",
        "min_rows": 500,
        "expected_rows": 800,
        "key_columns": [],
        "max_null_rate": 0.5,
        "freshness_days": 30,
        "critical": True
    },
    "post_order_enriched": {
        "path": "DATA/2_ENRICHED/post_order_enriched_COMPLETE.csv",
        "type": "enriched",
        "min_rows": 1000,
        "expected_rows": 1500,
        "key_columns": [],
        "max_null_rate": 0.5,
        "freshness_days": 14,
        "critical": False
    },
    "dropoff_enriched": {
        "path": "DATA/2_ENRICHED/DROPOFF_ENRICHED.csv",
        "type": "enriched",
        "min_rows": 500,
        "expected_rows": 800,
        "key_columns": [],
        "max_null_rate": 0.5,
        "freshness_days": 14,
        "critical": False
    },
    
    # Analysis outputs
    "zone_gap_report": {
        "path": "DATA/3_ANALYSIS/zone_gap_report.csv",
        "type": "analysis",
        "min_rows": 50,
        "expected_rows": 101,
        "key_columns": ["zone"],
        "max_null_rate": 0.3,
        "freshness_days": 14,
        "critical": False
    },
    "cuisine_gap_analysis": {
        "path": "DATA/3_ANALYSIS/cuisine_gap_analysis.csv",
        "type": "analysis",
        "min_rows": 10,
        "expected_rows": 15,
        "key_columns": ["cuisine"],
        "max_null_rate": 0.2,
        "freshness_days": 14,
        "critical": False
    },
    "latent_demand_summary": {
        "path": "DATA/3_ANALYSIS/latent_demand_summary.json",
        "type": "analysis",
        "min_rows": 1,  # JSON file
        "expected_rows": 1,
        "key_columns": [],
        "max_null_rate": 0.0,
        "freshness_days": 14,
        "critical": False
    },
    "master_dish_list": {
        "path": "DELIVERABLES/reports/MASTER_DISH_LIST_WITH_WORKINGS.csv",
        "type": "analysis",
        "min_rows": 20,
        "expected_rows": 32,
        "key_columns": ["dish_type"],
        "max_null_rate": 0.3,
        "freshness_days": 14,
        "critical": True
    }
}


def get_file_freshness(file_path: Path) -> Dict[str, Any]:
    """Get file modification time and freshness status."""
    if not file_path.exists():
        return {"exists": False, "modified": None, "age_days": None}
    
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age_days = (datetime.now() - mtime).days
    
    return {
        "exists": True,
        "modified": mtime.isoformat(),
        "age_days": age_days
    }


def validate_csv(file_path: Path, config: Dict) -> Dict[str, Any]:
    """Validate a CSV file against configuration."""
    result = {
        "source": file_path.name,
        "path": str(file_path),
        "type": config["type"],
        "status": "valid",
        "issues": [],
        "warnings": []
    }
    
    # Check file exists
    freshness = get_file_freshness(file_path)
    result["freshness"] = freshness
    
    if not freshness["exists"]:
        result["status"] = "missing"
        result["issues"].append(f"File not found: {file_path}")
        return result
    
    # Check freshness
    if freshness["age_days"] > config["freshness_days"]:
        result["warnings"].append(
            f"Data is {freshness['age_days']} days old (threshold: {config['freshness_days']})"
        )
    
    # Load and validate data
    try:
        # Try reading with comment handling for files with # comments
        df = pd.read_csv(file_path, low_memory=False, comment='#')
        result["row_count"] = len(df)
        result["column_count"] = len(df.columns)
        result["columns"] = list(df.columns)
        
        # Check row count
        if len(df) < config["min_rows"]:
            result["status"] = "error"
            result["issues"].append(
                f"Row count {len(df)} below minimum {config['min_rows']}"
            )
        elif len(df) < config["expected_rows"] * 0.8:
            result["warnings"].append(
                f"Row count {len(df)} below expected {config['expected_rows']}"
            )
        
        # Check key columns exist
        for col in config["key_columns"]:
            if col not in df.columns:
                result["status"] = "error"
                result["issues"].append(f"Missing key column: {col}")
        
        # Check null rates for key columns
        null_rates = {}
        high_null_columns = []
        for col in df.columns:
            null_rate = df[col].isna().mean()
            null_rates[col] = round(null_rate, 3)
            if null_rate > config["max_null_rate"] and col in config["key_columns"]:
                high_null_columns.append(col)
        
        result["null_rates"] = null_rates
        if high_null_columns:
            result["warnings"].append(
                f"High null rates in key columns: {high_null_columns}"
            )
        
        # Sample values for key columns
        sample_values = {}
        for col in config["key_columns"]:
            if col in df.columns:
                sample_values[col] = df[col].dropna().head(3).tolist()
        result["sample_values"] = sample_values
        
    except Exception as e:
        result["status"] = "error"
        result["issues"].append(f"Failed to read file: {str(e)}")
    
    # Determine final status
    if result["issues"]:
        result["status"] = "error" if config["critical"] else "warning"
    elif result["warnings"]:
        result["status"] = "warning"
    
    return result


def validate_json(file_path: Path, config: Dict) -> Dict[str, Any]:
    """Validate a JSON file against configuration."""
    result = {
        "source": file_path.name,
        "path": str(file_path),
        "type": config["type"],
        "status": "valid",
        "issues": [],
        "warnings": []
    }
    
    # Check file exists
    freshness = get_file_freshness(file_path)
    result["freshness"] = freshness
    
    if not freshness["exists"]:
        result["status"] = "missing"
        result["issues"].append(f"File not found: {file_path}")
        return result
    
    # Check freshness
    if freshness["age_days"] > config["freshness_days"]:
        result["warnings"].append(
            f"Data is {freshness['age_days']} days old (threshold: {config['freshness_days']})"
        )
    
    # Load and validate JSON
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        result["row_count"] = 1  # JSON counts as 1
        if isinstance(data, dict):
            result["keys"] = list(data.keys())
        elif isinstance(data, list):
            result["row_count"] = len(data)
            
    except Exception as e:
        result["status"] = "error"
        result["issues"].append(f"Failed to read JSON: {str(e)}")
    
    return result


def run_validation() -> Dict[str, Any]:
    """Run full validation on all data sources."""
    print("=" * 60)
    print("DATA QUALITY VALIDATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "summary": {
            "total_sources": len(DATA_SOURCES),
            "valid": 0,
            "warning": 0,
            "error": 0,
            "missing": 0
        },
        "by_type": {
            "behavioral": {"valid": 0, "warning": 0, "error": 0, "missing": 0},
            "ground_truth": {"valid": 0, "warning": 0, "error": 0, "missing": 0},
            "survey": {"valid": 0, "warning": 0, "error": 0, "missing": 0},
            "enriched": {"valid": 0, "warning": 0, "error": 0, "missing": 0},
            "analysis": {"valid": 0, "warning": 0, "error": 0, "missing": 0}
        },
        "validations": [],
        "blocking_issues": [],
        "warnings": [],
        "overall_status": "ready"
    }
    
    for source_name, config in DATA_SOURCES.items():
        file_path = PROJECT_ROOT / config["path"]
        print(f"Validating {source_name}...")
        
        # Choose validator based on file type
        if config["path"].endswith(".json"):
            result = validate_json(file_path, config)
        else:
            result = validate_csv(file_path, config)
        
        result["source_name"] = source_name
        result["critical"] = config["critical"]
        report["validations"].append(result)
        
        # Update summary
        status = result["status"]
        report["summary"][status] = report["summary"].get(status, 0) + 1
        report["by_type"][config["type"]][status] += 1
        
        # Track blocking issues
        if status == "error" and config["critical"]:
            report["blocking_issues"].append({
                "source": source_name,
                "issues": result["issues"]
            })
        
        # Track warnings
        if result["warnings"]:
            report["warnings"].extend([
                {"source": source_name, "warning": w} for w in result["warnings"]
            ])
        
        # Print status
        status_icon = {"valid": "✓", "warning": "⚠", "error": "✗", "missing": "✗"}
        print(f"  {status_icon.get(status, '?')} {status.upper()}")
        if result.get("row_count"):
            print(f"    Rows: {result['row_count']:,}")
        for issue in result.get("issues", []):
            print(f"    Issue: {issue}")
        for warning in result.get("warnings", []):
            print(f"    Warning: {warning}")
        print()
    
    # Determine overall status
    if report["blocking_issues"]:
        report["overall_status"] = "blocked"
    elif report["summary"]["error"] > 0:
        report["overall_status"] = "not_ready"
    elif report["summary"]["warning"] > 3:
        report["overall_status"] = "needs_review"
    else:
        report["overall_status"] = "ready"
    
    # Print summary
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total sources: {report['summary']['total_sources']}")
    print(f"  ✓ Valid:   {report['summary']['valid']}")
    print(f"  ⚠ Warning: {report['summary']['warning']}")
    print(f"  ✗ Error:   {report['summary']['error']}")
    print(f"  ✗ Missing: {report['summary']['missing']}")
    print()
    print(f"Overall Status: {report['overall_status'].upper()}")
    
    if report["blocking_issues"]:
        print()
        print("BLOCKING ISSUES:")
        for issue in report["blocking_issues"]:
            print(f"  - {issue['source']}: {issue['issues']}")
    
    print()
    
    return report


def save_report(report: Dict[str, Any]) -> None:
    """Save validation report to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Report saved to: {OUTPUT_FILE}")


def main():
    """Main entry point."""
    report = run_validation()
    save_report(report)
    
    # Exit with appropriate code
    if report["overall_status"] == "blocked":
        print("\n❌ VALIDATION FAILED - Blocking issues found")
        sys.exit(1)
    elif report["overall_status"] == "not_ready":
        print("\n⚠️ VALIDATION WARNING - Non-critical errors found")
        sys.exit(0)
    else:
        print("\n✅ VALIDATION PASSED - Ready for dashboard build")
        sys.exit(0)


if __name__ == "__main__":
    main()

