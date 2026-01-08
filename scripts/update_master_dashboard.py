#!/usr/bin/env python3
"""
Update Master Dashboard Script

Reads data from source files and updates the embedded JSON in the master dashboard.
This ensures the dashboard stays in sync with the latest analysis.

Output: DELIVERABLES/dashboards/dinneroo_master_dashboard.html (updated in place)

Usage:
    python3 scripts/update_master_dashboard.py

Data Sources:
    - DATA/3_ANALYSIS/mvp_threshold_discovery.json (MVP inflection points)
    - docs/data/zone_mvp_status.json (Zone MVP calculations - 201 live zones)
    - config/mvp_thresholds.json (Business MVP requirements)
    - config/dashboard_metrics.json (Reconciled metrics)
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DASHBOARD_FILE = PROJECT_ROOT / "DELIVERABLES" / "dashboards" / "dinneroo_master_dashboard.html"

# Data sources
DATA_SOURCES = {
    "mvp_threshold_discovery": PROJECT_ROOT / "DATA" / "3_ANALYSIS" / "mvp_threshold_discovery.json",
    "zone_mvp_status": PROJECT_ROOT / "docs" / "data" / "zone_mvp_status.json",
    "mvp_thresholds": PROJECT_ROOT / "config" / "mvp_thresholds.json",
    "dashboard_metrics": PROJECT_ROOT / "config" / "dashboard_metrics.json",
}


def load_json_safe(path: Path) -> Optional[Dict]:
    """Safely load a JSON file."""
    if not path.exists():
        print(f"  ⚠ File not found: {path}")
        return None
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        print(f"  ✓ Loaded {path.name}")
        return data
    except Exception as e:
        print(f"  ✗ Failed to load {path.name}: {e}")
        return None


def extract_zone_metrics(zone_mvp_status: list) -> Dict[str, Any]:
    """Extract key metrics from zone MVP status data."""
    if not zone_mvp_status:
        return {}
    
    total_zones = len(zone_mvp_status)
    mvp_ready = sum(1 for z in zone_mvp_status if z.get("mvp_status") == "MVP Ready")
    near_mvp = sum(1 for z in zone_mvp_status if z.get("mvp_status") == "Near MVP")
    developing = sum(1 for z in zone_mvp_status if z.get("mvp_status") == "Developing")
    
    total_orders = sum(z.get("order_count", 0) for z in zone_mvp_status)
    total_customers = sum(z.get("customer_count", 0) for z in zone_mvp_status)
    
    # Calculate average metrics
    ratings = [z.get("avg_rating") for z in zone_mvp_status if z.get("avg_rating") is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    repeat_rates = [z.get("repeat_rate", 0) for z in zone_mvp_status]
    avg_repeat_rate = sum(repeat_rates) / len(repeat_rates) if repeat_rates else 0
    
    return {
        "live_zones": total_zones,
        "mvp_ready": mvp_ready,
        "near_mvp": near_mvp,
        "developing": developing,
        "mvp_ready_pct": round(mvp_ready / total_zones * 100, 1) if total_zones > 0 else 0,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "avg_rating": round(avg_rating, 2),
        "avg_repeat_rate": round(avg_repeat_rate * 100, 1),
    }


def extract_threshold_metrics(mvp_discovery: Dict) -> Dict[str, Any]:
    """Extract threshold metrics from MVP discovery data."""
    if not mvp_discovery:
        return {}
    
    metrics = {
        "zones_analyzed": mvp_discovery.get("step_1_partners", {}).get("total_zones_analyzed", 197),
        "methodology": mvp_discovery.get("methodology", ""),
        "generated": mvp_discovery.get("generated", ""),
    }
    
    # Extract partner inflection data
    partners_data = mvp_discovery.get("step_1_partners", {}).get("by_partner_count", [])
    metrics["partners_by_count"] = partners_data
    
    # Extract cuisine inflection data
    cuisines_data = mvp_discovery.get("step_2_cuisines_within_partners", {}).get("by_cuisine_count", [])
    metrics["cuisines_by_count"] = cuisines_data
    
    # Extract dishes per partner data
    dishes_data = mvp_discovery.get("step_3_dishes_within_partners_and_cuisines", {}).get("by_dishes_per_partner", [])
    metrics["dishes_per_partner"] = dishes_data
    
    return metrics


def generate_data_freshness_html(metrics: Dict) -> str:
    """Generate the data freshness indicator HTML."""
    now = datetime.now()
    return f'<div>Last updated: {now.strftime("%Y-%m-%d %H:%M")}</div>'


def update_dashboard_metrics(html: str, zone_metrics: Dict, threshold_metrics: Dict, dashboard_metrics: Dict) -> str:
    """Update specific metrics in the dashboard HTML."""
    
    # Update live zones count
    if zone_metrics.get("live_zones"):
        # Pattern to match "Trial period: XXX zones"
        html = re.sub(
            r'Trial period: \d+ zones',
            f'Trial period: {zone_metrics["live_zones"]} zones',
            html
        )
    
    # Update order count from dashboard_metrics
    order_count = dashboard_metrics.get("order_metrics", {}).get("total_orders", {}).get("value", 82350)
    html = re.sub(
        r'Trial period: (\d+) zones · [\d,]+ orders',
        f'Trial period: \\1 zones · {order_count:,} orders',
        html
    )
    
    # Update MVP Ready percentage
    if zone_metrics.get("mvp_ready") and zone_metrics.get("live_zones"):
        mvp_pct = round(zone_metrics["mvp_ready"] / zone_metrics["live_zones"] * 100)
        html = re.sub(
            r'<strong>\d+%</strong> of zones with orders meet all MVP criteria \(\d+ of \d+\)',
            f'<strong>{mvp_pct}%</strong> of zones with orders meet all MVP criteria ({zone_metrics["mvp_ready"]} of {zone_metrics["live_zones"]})',
            html
        )
    
    # Update zones analyzed count
    if threshold_metrics.get("zones_analyzed"):
        html = re.sub(
            r'Based on <strong>\d+ zones</strong> with orders',
            f'Based on <strong>{threshold_metrics["zones_analyzed"]} zones</strong> with orders',
            html
        )
    
    return html


def main():
    """Main entry point."""
    print("=" * 60)
    print("UPDATING MASTER DASHBOARD")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Check dashboard exists
    if not DASHBOARD_FILE.exists():
        print(f"✗ Dashboard not found: {DASHBOARD_FILE}")
        sys.exit(1)
    
    print("Loading data sources...")
    
    # Load all data sources
    mvp_discovery = load_json_safe(DATA_SOURCES["mvp_threshold_discovery"])
    zone_mvp_status = load_json_safe(DATA_SOURCES["zone_mvp_status"])
    mvp_thresholds = load_json_safe(DATA_SOURCES["mvp_thresholds"])
    dashboard_metrics = load_json_safe(DATA_SOURCES["dashboard_metrics"])
    
    print()
    
    # Extract metrics
    print("Extracting metrics...")
    zone_metrics = extract_zone_metrics(zone_mvp_status) if zone_mvp_status else {}
    threshold_metrics = extract_threshold_metrics(mvp_discovery) if mvp_discovery else {}
    
    if zone_metrics:
        print(f"  ✓ Zone metrics: {zone_metrics['live_zones']} live zones, {zone_metrics['mvp_ready']} MVP Ready")
    if threshold_metrics:
        print(f"  ✓ Threshold metrics: {threshold_metrics.get('zones_analyzed', 0)} zones analyzed")
    
    print()
    
    # Read current dashboard
    print("Reading dashboard...")
    with open(DASHBOARD_FILE, 'r') as f:
        html = f.read()
    print(f"  ✓ Dashboard loaded: {len(html):,} characters")
    
    # Update metrics in dashboard
    print("Updating metrics...")
    updated_html = update_dashboard_metrics(html, zone_metrics, threshold_metrics, dashboard_metrics or {})
    
    # Check if changes were made
    if updated_html != html:
        # Backup original
        backup_file = DASHBOARD_FILE.with_suffix('.html.bak')
        with open(backup_file, 'w') as f:
            f.write(html)
        print(f"  ✓ Backup created: {backup_file.name}")
        
        # Write updated dashboard
        with open(DASHBOARD_FILE, 'w') as f:
            f.write(updated_html)
        print(f"  ✓ Dashboard updated: {DASHBOARD_FILE.name}")
    else:
        print("  ℹ No changes needed - dashboard already up to date")
    
    print()
    print("=" * 60)
    print("DASHBOARD UPDATE COMPLETE")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  • Live zones: {zone_metrics.get('live_zones', 'N/A')}")
    print(f"  • MVP Ready: {zone_metrics.get('mvp_ready', 'N/A')} ({zone_metrics.get('mvp_ready_pct', 'N/A')}%)")
    print(f"  • Near MVP: {zone_metrics.get('near_mvp', 'N/A')}")
    print(f"  • Developing: {zone_metrics.get('developing', 'N/A')}")
    print(f"  • Avg Rating: {zone_metrics.get('avg_rating', 'N/A')}")
    print(f"  • Avg Repeat Rate: {zone_metrics.get('avg_repeat_rate', 'N/A')}%")
    print()


if __name__ == "__main__":
    main()


