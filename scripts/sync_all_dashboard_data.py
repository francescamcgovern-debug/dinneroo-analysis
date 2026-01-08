#!/usr/bin/env python3
"""
Master Dashboard Data Sync Script

Runs all data sync scripts to update dashboard with latest analysis.
This ensures dish and zone data stay in sync with dashboard.

Usage:
    python3 scripts/sync_all_dashboard_data.py

Run this after:
    - Any analysis script (phase2 or phase3)
    - regenerate_dish_scores_v3_1.py
    - generate_zone_dashboard_data.py
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def run_sync(script_name: str, description: str) -> bool:
    """Run a sync script and return success status."""
    script_path = PROJECT_ROOT / "scripts" / script_name
    
    if not script_path.exists():
        print(f"  ✗ Script not found: {script_name}")
        return False
    
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        capture_output=False
    )
    
    return result.returncode == 0


def main():
    print("=" * 60)
    print("DASHBOARD DATA SYNC - ALL")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    syncs = [
        ("sync_zone_data.py", "Zone Data Sync"),
        ("sync_dish_data.py", "Dish Data Sync"),
    ]
    
    results = []
    for script, description in syncs:
        success = run_sync(script, description)
        results.append((script, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("SYNC SUMMARY")
    print("=" * 60)
    
    all_success = True
    for script, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {script}")
        if not success:
            all_success = False
    
    print()
    if all_success:
        print("✓ All dashboard data synced successfully!")
        print()
        print("Next steps:")
        print("  1. Open docs/dashboard.html in browser to verify")
        print("  2. Commit changes if everything looks good")
    else:
        print("✗ Some syncs failed - check output above")
    
    return all_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


