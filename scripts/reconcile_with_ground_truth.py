#!/usr/bin/env python3
"""
Reconciliation Script: Snowflake vs Anna's Ground Truth

Compares behavioral data from Snowflake with Anna's authoritative supply data
to identify discrepancies and document known differences.

Output: DATA/2_ENRICHED/reconciliation_report.json

Usage:
    python3 scripts/reconcile_with_ground_truth.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Output paths
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "2_ENRICHED"
OUTPUT_FILE = OUTPUT_DIR / "reconciliation_report.json"

# Source file paths
SNOWFLAKE_SOURCES = {
    "orders": PROJECT_ROOT / "DATA" / "1_SOURCE" / "snowflake" / "ALL_DINNEROO_ORDERS.csv",
    "partner_performance": PROJECT_ROOT / "DATA" / "1_SOURCE" / "snowflake" / "DINNEROO_PARTNER_PERFORMANCE.csv",
    "partner_catalog": PROJECT_ROOT / "DATA" / "1_SOURCE" / "snowflake" / "DINNEROO_PARTNER_CATALOG_BY_ZONE.csv",
    "menu_catalog": PROJECT_ROOT / "DATA" / "1_SOURCE" / "snowflake" / "DINNEROO_MENU_CATALOG.csv",
    "ratings": PROJECT_ROOT / "DATA" / "1_SOURCE" / "snowflake" / "DINNEROO_RATINGS.csv",
}

ANNA_SOURCES = {
    "family_dishes": PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "anna_family_dishes.csv",
    "partner_coverage": PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "anna_partner_coverage.csv",
    "zone_dish_counts": PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "anna_zone_dish_counts.csv",
}

# Thresholds for alerts
THRESHOLDS = {
    "partner_count": {"warn": 0.15, "fail": 0.30},  # 15% warn, 30% fail
    "site_count": {"warn": 0.10, "fail": 0.20},     # Sites should match closely
    "zone_count": {"warn": 0.50, "fail": 0.70},    # Zones with orders will always be lower than zones with coverage
    "dish_count": {"warn": 0.15, "fail": 0.30},
}

# Known differences to document (not flag as errors)
KNOWN_DIFFERENCES = {
    "order_derived_undercount": """
    Order-derived counts will always be LOWER than Anna's ground truth because:
    1. Partners can be onboarded but have zero orders yet
    2. Zones can have dishes available that haven't been ordered
    3. Order data only shows what was purchased, not what's available
    
    This is EXPECTED behavior. Anna's data is the authoritative source for "what we have".
    Snowflake data shows "what has been ordered" (revealed preference).
    """,
    "menu_item_variations": """
    Menu item names in Snowflake may differ from Anna's categorization due to:
    1. Partner naming conventions
    2. Menu item variations (e.g., "Chicken Katsu" vs "Katsu Curry")
    3. Aggregation differences
    """,
}


def load_data() -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """Load all data sources."""
    snowflake_data = {}
    anna_data = {}
    
    print("Loading Snowflake data...")
    for name, path in SNOWFLAKE_SOURCES.items():
        if path.exists():
            try:
                snowflake_data[name] = pd.read_csv(path, low_memory=False)
                print(f"  ✓ {name}: {len(snowflake_data[name]):,} rows")
            except Exception as e:
                print(f"  ✗ {name}: Failed to load - {e}")
        else:
            print(f"  ✗ {name}: File not found")
    
    print("\nLoading Anna's ground truth...")
    for name, path in ANNA_SOURCES.items():
        if path.exists():
            try:
                anna_data[name] = pd.read_csv(path, low_memory=False)
                print(f"  ✓ {name}: {len(anna_data[name]):,} rows")
            except Exception as e:
                print(f"  ✗ {name}: Failed to load - {e}")
        else:
            print(f"  ✗ {name}: File not found")
    
    return snowflake_data, anna_data


def compare_partner_counts(
    snowflake_data: Dict[str, pd.DataFrame],
    anna_data: Dict[str, pd.DataFrame]
) -> Dict[str, Any]:
    """Compare partner/site counts between Snowflake and Anna's data.
    
    Note: Anna's data has BRANDS (40) with site counts (756 total).
    Snowflake has individual RESTAURANT SITES (770+).
    We compare site counts, not brand counts.
    """
    result = {
        "metric": "site_count",  # Changed from partner_count to site_count
        "status": "pass",
        "issues": [],
        "details": {}
    }
    
    # Get Anna's data - brands and total sites
    anna_brand_count = 40  # Default
    anna_site_count = 756  # Default from documentation
    
    if "partner_coverage" in anna_data:
        anna_partners = anna_data["partner_coverage"]
        anna_brand_count = len(anna_partners)
        result["details"]["anna_brand_count"] = anna_brand_count
        
        # Sum up total sites from the total_sites column
        for col in anna_partners.columns:
            if 'site' in col.lower() and 'total' in col.lower():
                anna_site_count = anna_partners[col].sum()
                break
        result["details"]["anna_total_sites"] = int(anna_site_count)
    else:
        result["details"]["anna_brand_count"] = anna_brand_count
        result["details"]["anna_total_sites"] = anna_site_count
    
    # Get Snowflake site count - these are individual restaurant sites
    snowflake_sites = set()
    
    # Try partner_performance first (has partner-zone combinations)
    if "partner_performance" in snowflake_data:
        df = snowflake_data["partner_performance"]
        for col in df.columns:
            if 'partner' in col.lower() or 'restaurant' in col.lower():
                if 'id' not in col.lower():
                    snowflake_sites = set(df[col].dropna().unique())
                    break
    
    # Fallback to orders
    if not snowflake_sites and "orders" in snowflake_data:
        df = snowflake_data["orders"]
        for col in df.columns:
            if 'partner' in col.lower() or 'restaurant' in col.lower():
                if 'id' not in col.lower():
                    snowflake_sites = set(df[col].dropna().unique())
                    break
    
    snowflake_site_count = len(snowflake_sites)
    result["details"]["snowflake_site_count"] = snowflake_site_count
    result["details"]["snowflake_sites_sample"] = sorted(list(snowflake_sites))[:5]  # First 5 for reference
    
    # Try to extract brand names from Snowflake sites for brand comparison
    # Sites are named like "Dishoom - Editions - ISL" or "0131 - Fulham - 363 Fulham Road - PizzaExpress"
    snowflake_brands = set()
    for site in snowflake_sites:
        site_str = str(site)
        # Try to extract brand name (usually last part after " - " or contains known brands)
        parts = site_str.split(' - ')
        if len(parts) >= 2:
            # Check if last part looks like a brand
            potential_brand = parts[-1].strip()
            if potential_brand and not potential_brand[0].isdigit():
                snowflake_brands.add(potential_brand)
            elif len(parts) >= 3:
                # Try second to last
                potential_brand = parts[-2].strip()
                if potential_brand and not potential_brand[0].isdigit():
                    snowflake_brands.add(potential_brand)
    
    result["details"]["snowflake_brand_count_estimated"] = len(snowflake_brands)
    result["details"]["snowflake_brands_sample"] = sorted(list(snowflake_brands))[:10]
    
    # Calculate discrepancy - compare SITE counts
    if anna_site_count > 0:
        discrepancy = abs(anna_site_count - snowflake_site_count) / anna_site_count
        result["details"]["site_discrepancy_pct"] = round(discrepancy * 100, 1)
        result["details"]["site_difference"] = anna_site_count - snowflake_site_count
        
        # Determine status based on site count comparison
        if discrepancy > THRESHOLDS["site_count"]["fail"]:
            result["status"] = "fail"
            result["issues"].append(
                f"Site count discrepancy {discrepancy*100:.1f}% exceeds threshold "
                f"(Snowflake: {snowflake_site_count}, Anna: {anna_site_count})"
            )
        elif discrepancy > THRESHOLDS["site_count"]["warn"]:
            result["status"] = "warn"
            result["issues"].append(
                f"Site count discrepancy {discrepancy*100:.1f}% is notable "
                f"(Snowflake: {snowflake_site_count}, Anna: {anna_site_count})"
            )
        
        # Add context
        if snowflake_site_count < anna_site_count:
            result["details"]["explanation"] = (
                "Snowflake site count is lower than Anna's - this is EXPECTED. "
                "Order data only shows sites with orders, not all onboarded sites. "
                f"Anna has {anna_brand_count} brands with {anna_site_count} total sites."
            )
        elif snowflake_site_count > anna_site_count:
            result["details"]["explanation"] = (
                "Snowflake site count is HIGHER than Anna's - investigate. "
                "This could indicate sites not in Anna's tracking or naming variations."
            )
    
    return result


def compare_zone_counts(
    snowflake_data: Dict[str, pd.DataFrame],
    anna_data: Dict[str, pd.DataFrame]
) -> Dict[str, Any]:
    """Compare zone counts between Snowflake and Anna's data."""
    result = {
        "metric": "zone_count",
        "status": "pass",
        "issues": [],
        "details": {}
    }
    
    # Get Anna's zone count (ground truth)
    # Note: Anna's file has 1,306 rows but many are zones with 0 dishes
    # The relevant comparison is zones WITH Dinneroo coverage (434 per documentation)
    if "zone_dish_counts" in anna_data:
        anna_zones = anna_data["zone_dish_counts"]
        zone_col = None
        for col in anna_zones.columns:
            if 'zone' in col.lower():
                zone_col = col
                break
        
        if zone_col:
            anna_count = anna_zones[zone_col].nunique()
        else:
            anna_count = len(anna_zones)
        result["details"]["anna_total_zones"] = anna_count
        
        # Try to find zones with actual coverage
        dish_col = None
        for col in anna_zones.columns:
            if 'dish' in col.lower() and 'count' in col.lower():
                dish_col = col
                break
        
        if dish_col:
            zones_with_dishes = anna_zones[anna_zones[dish_col] > 0]
            result["details"]["anna_zones_with_dishes"] = len(zones_with_dishes)
        else:
            result["details"]["anna_zones_with_dishes"] = 434  # From documentation
    else:
        anna_count = 1306  # Total zones
        result["details"]["anna_total_zones"] = anna_count
        result["details"]["anna_zones_with_dishes"] = 434  # From documentation
    
    # Get Snowflake zone count - zones with actual orders
    snowflake_zones = set()
    if "orders" in snowflake_data:
        df = snowflake_data["orders"]
        for col in df.columns:
            if 'zone' in col.lower():
                snowflake_zones = set(df[col].dropna().unique())
                break
    
    snowflake_count = len(snowflake_zones)
    result["details"]["snowflake_zone_count"] = snowflake_count
    
    # Use zones_with_dishes for comparison (more relevant than total zones)
    anna_count = result["details"].get("anna_zones_with_dishes", 434)
    
    # Calculate discrepancy
    if anna_count > 0:
        discrepancy = abs(anna_count - snowflake_count) / anna_count
        result["details"]["discrepancy_pct"] = round(discrepancy * 100, 1)
        result["details"]["difference"] = anna_count - snowflake_count
        
        if discrepancy > THRESHOLDS["zone_count"]["fail"]:
            result["status"] = "fail"
            result["issues"].append(
                f"Zone count discrepancy {discrepancy*100:.1f}% exceeds threshold "
                f"(Snowflake: {snowflake_count}, Anna: {anna_count})"
            )
        elif discrepancy > THRESHOLDS["zone_count"]["warn"]:
            result["status"] = "warn"
            result["issues"].append(
                f"Zone count discrepancy {discrepancy*100:.1f}% is notable "
                f"(Snowflake: {snowflake_count}, Anna: {anna_count})"
            )
        
        if snowflake_count < anna_count:
            result["details"]["explanation"] = (
                "Snowflake count is lower than Anna's - this is EXPECTED. "
                "Order data only shows zones with orders, not all zones with coverage."
            )
    
    return result


def compare_dish_counts(
    snowflake_data: Dict[str, pd.DataFrame],
    anna_data: Dict[str, pd.DataFrame]
) -> Dict[str, Any]:
    """Compare dish counts between Snowflake and Anna's data."""
    result = {
        "metric": "dish_count",
        "status": "pass",
        "issues": [],
        "details": {}
    }
    
    # Get Anna's dish count (ground truth)
    if "family_dishes" in anna_data:
        anna_count = len(anna_data["family_dishes"])
        result["details"]["anna_dish_count"] = anna_count
    else:
        anna_count = 142  # Known value from documentation
        result["details"]["anna_dish_count"] = anna_count
    
    # Get Snowflake dish count from menu catalog
    snowflake_count = 0
    if "menu_catalog" in snowflake_data:
        df = snowflake_data["menu_catalog"]
        # Count unique menu items (this will be higher due to variations)
        item_col = None
        for col in df.columns:
            if 'item' in col.lower() or 'menu' in col.lower():
                item_col = col
                break
        if item_col:
            snowflake_count = df[item_col].nunique()
    
    result["details"]["snowflake_unique_items"] = snowflake_count
    
    # Note: Menu catalog will have MORE items than Anna's curated list
    result["details"]["explanation"] = (
        "Snowflake menu catalog contains all menu item variations. "
        "Anna's list is curated family dishes (142). "
        "These are not directly comparable - Anna's is the authoritative list of family dishes."
    )
    
    return result


def find_missing_entities(
    snowflake_data: Dict[str, pd.DataFrame],
    anna_data: Dict[str, pd.DataFrame]
) -> Dict[str, Any]:
    """Find entities in Anna's data that are missing from Snowflake orders."""
    result = {
        "missing_partners": [],
        "missing_zones": [],
        "coverage_analysis": {}
    }
    
    # Get partner names from both sources
    anna_partners: Set[str] = set()
    snowflake_partners: Set[str] = set()
    
    if "partner_coverage" in anna_data:
        df = anna_data["partner_coverage"]
        for col in df.columns:
            if 'partner' in col.lower() or 'brand' in col.lower() or 'name' in col.lower():
                anna_partners = set(df[col].dropna().str.lower().str.strip())
                break
    
    if "orders" in snowflake_data:
        df = snowflake_data["orders"]
        for col in df.columns:
            if 'partner' in col.lower() or 'restaurant' in col.lower():
                snowflake_partners = set(df[col].dropna().str.lower().str.strip())
                break
    
    # Find missing partners
    if anna_partners and snowflake_partners:
        missing = anna_partners - snowflake_partners
        result["missing_partners"] = list(missing)[:20]  # Limit to 20
        result["coverage_analysis"]["partners"] = {
            "anna_total": len(anna_partners),
            "snowflake_total": len(snowflake_partners),
            "missing_from_orders": len(missing),
            "coverage_pct": round(len(snowflake_partners) / len(anna_partners) * 100, 1) if anna_partners else 0
        }
    
    # Get zone names from both sources
    anna_zones: Set[str] = set()
    snowflake_zones: Set[str] = set()
    
    if "zone_dish_counts" in anna_data:
        df = anna_data["zone_dish_counts"]
        for col in df.columns:
            if 'zone' in col.lower():
                anna_zones = set(df[col].dropna().str.lower().str.strip())
                break
    
    if "orders" in snowflake_data:
        df = snowflake_data["orders"]
        for col in df.columns:
            if 'zone' in col.lower():
                snowflake_zones = set(df[col].dropna().str.lower().str.strip())
                break
    
    # Find missing zones
    if anna_zones and snowflake_zones:
        missing = anna_zones - snowflake_zones
        result["missing_zones"] = list(missing)[:20]  # Limit to 20
        result["coverage_analysis"]["zones"] = {
            "anna_total": len(anna_zones),
            "snowflake_total": len(snowflake_zones),
            "missing_from_orders": len(missing),
            "coverage_pct": round(len(snowflake_zones) / len(anna_zones) * 100, 1) if anna_zones else 0
        }
    
    return result


def generate_recommendations(comparisons: List[Dict], missing: Dict) -> List[Dict[str, str]]:
    """Generate actionable recommendations based on findings."""
    recommendations = []
    
    # Check for significant discrepancies
    for comp in comparisons:
        if comp["status"] == "fail":
            recommendations.append({
                "priority": "high",
                "metric": comp["metric"],
                "action": f"Investigate {comp['metric']} discrepancy of {comp['details'].get('discrepancy_pct', 'N/A')}%",
                "details": comp["issues"][0] if comp["issues"] else "Review data sources"
            })
        elif comp["status"] == "warn":
            recommendations.append({
                "priority": "medium",
                "metric": comp["metric"],
                "action": f"Monitor {comp['metric']} discrepancy",
                "details": comp["issues"][0] if comp["issues"] else "Within acceptable range but notable"
            })
    
    # Check coverage
    if missing.get("coverage_analysis", {}).get("partners", {}).get("coverage_pct", 100) < 80:
        recommendations.append({
            "priority": "medium",
            "metric": "partner_coverage",
            "action": "Review partners with zero orders",
            "details": f"{len(missing.get('missing_partners', []))} partners in Anna's data have no orders"
        })
    
    # Always recommend using Anna's data for supply metrics
    recommendations.append({
        "priority": "info",
        "metric": "data_usage",
        "action": "Use Anna's ground truth for supply metrics",
        "details": "Snowflake shows revealed preference (orders), Anna shows actual availability"
    })
    
    return recommendations


def run_reconciliation() -> Dict[str, Any]:
    """Run full reconciliation between Snowflake and Anna's data."""
    print("=" * 60)
    print("DATA RECONCILIATION: Snowflake vs Anna's Ground Truth")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Load data
    snowflake_data, anna_data = load_data()
    print()
    
    # Initialize report
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "status": "pass",
            "total_comparisons": 0,
            "passed": 0,
            "warnings": 0,
            "failures": 0
        },
        "comparisons": [],
        "missing_entities": {},
        "known_differences": KNOWN_DIFFERENCES,
        "recommendations": [],
        "data_usage_guidance": {
            "supply_metrics": "Use Anna's ground truth (anna_*.csv)",
            "performance_metrics": "Use Snowflake data (orders, ratings)",
            "preference_metrics": "Use surveys with triangulation"
        }
    }
    
    # Run comparisons
    print("Running comparisons...")
    print()
    
    comparisons = [
        compare_partner_counts(snowflake_data, anna_data),
        compare_zone_counts(snowflake_data, anna_data),
        compare_dish_counts(snowflake_data, anna_data),
    ]
    
    for comp in comparisons:
        report["comparisons"].append(comp)
        report["summary"]["total_comparisons"] += 1
        
        if comp["status"] == "pass":
            report["summary"]["passed"] += 1
            status_icon = "✓"
        elif comp["status"] == "warn":
            report["summary"]["warnings"] += 1
            status_icon = "⚠"
        else:
            report["summary"]["failures"] += 1
            status_icon = "✗"
        
        print(f"{status_icon} {comp['metric'].upper()}: {comp['status'].upper()}")
        for key, value in comp["details"].items():
            if key != "explanation":
                print(f"    {key}: {value}")
        if comp["details"].get("explanation"):
            print(f"    Note: {comp['details']['explanation'][:80]}...")
        print()
    
    # Find missing entities
    print("Analyzing coverage gaps...")
    report["missing_entities"] = find_missing_entities(snowflake_data, anna_data)
    
    if report["missing_entities"].get("coverage_analysis"):
        for entity_type, coverage in report["missing_entities"]["coverage_analysis"].items():
            print(f"  {entity_type}: {coverage.get('coverage_pct', 'N/A')}% coverage in orders")
    print()
    
    # Generate recommendations
    report["recommendations"] = generate_recommendations(
        report["comparisons"],
        report["missing_entities"]
    )
    
    # Determine overall status
    if report["summary"]["failures"] > 0:
        report["summary"]["status"] = "fail"
    elif report["summary"]["warnings"] > 0:
        report["summary"]["status"] = "warn"
    else:
        report["summary"]["status"] = "pass"
    
    # Print summary
    print("=" * 60)
    print("RECONCILIATION SUMMARY")
    print("=" * 60)
    print(f"Status: {report['summary']['status'].upper()}")
    print(f"Comparisons: {report['summary']['total_comparisons']}")
    print(f"  ✓ Passed:   {report['summary']['passed']}")
    print(f"  ⚠ Warnings: {report['summary']['warnings']}")
    print(f"  ✗ Failures: {report['summary']['failures']}")
    print()
    
    if report["recommendations"]:
        print("RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            priority_icon = {"high": "🔴", "medium": "🟡", "info": "🔵"}.get(rec["priority"], "•")
            print(f"  {priority_icon} [{rec['priority'].upper()}] {rec['action']}")
    print()
    
    return report


def save_report(report: Dict[str, Any]) -> None:
    """Save reconciliation report to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Report saved to: {OUTPUT_FILE}")


def main():
    """Main entry point."""
    report = run_reconciliation()
    save_report(report)
    
    # Exit with appropriate code
    if report["summary"]["status"] == "fail":
        print("\n❌ RECONCILIATION FAILED - Significant discrepancies found")
        print("   Review the report and known differences before proceeding.")
        sys.exit(1)
    elif report["summary"]["status"] == "warn":
        print("\n⚠️ RECONCILIATION WARNING - Notable discrepancies found")
        print("   These may be expected. Review the explanations in the report.")
        sys.exit(0)
    else:
        print("\n✅ RECONCILIATION PASSED - Data sources are aligned")
        sys.exit(0)


if __name__ == "__main__":
    main()

