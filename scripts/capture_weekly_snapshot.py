#!/usr/bin/env python3
"""
Capture Weekly Snapshot
=======================
Saves a timestamped snapshot of key metrics for week-over-week comparison.

Run weekly (e.g., every Monday) to track progress over time:
    python scripts/capture_weekly_snapshot.py

Snapshots are saved to DATA/4_SNAPSHOTS/ with timestamps.
The dashboard will read these to show week-over-week deltas.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_PATH = Path(__file__).parent.parent
DATA_PATH = BASE_PATH / "DATA"
SNAPSHOTS_PATH = DATA_PATH / "4_SNAPSHOTS"
DOCS_DATA_PATH = BASE_PATH / "docs" / "data"

def load_json(path):
    """Load JSON file."""
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return None

def capture_snapshot():
    """Capture current state of key metrics."""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    week_num = datetime.now().strftime('%Y-W%W')
    
    print(f"📸 Capturing snapshot for {timestamp} (Week {week_num})")
    print("=" * 60)
    
    # Create snapshots directory if it doesn't exist
    SNAPSHOTS_PATH.mkdir(parents=True, exist_ok=True)
    
    # Load current data
    zone_priority = load_json(DOCS_DATA_PATH / "zone_priority_queue.json")
    segment_insights = load_json(DOCS_DATA_PATH / "segment_insights.json")
    
    if not zone_priority:
        print("❌ Error: zone_priority_queue.json not found")
        return
    
    # Extract key metrics
    snapshot = {
        "captured_at": datetime.now().isoformat(),
        "week": week_num,
        "date": timestamp,
        "metrics": {
            "zones": {
                "total": zone_priority["summary"]["total_zones"],
                "mvp_ready": zone_priority["summary"]["mvp_ready"],
                "near_mvp": zone_priority["summary"]["near_mvp"],
                "needs_work": zone_priority["summary"]["needs_work"]
            },
            "near_mvp_breakdown": zone_priority.get("near_mvp_breakdown", {}),
            "segments": {}
        }
    }
    
    # Add segment metrics if available
    if segment_insights:
        for seg in segment_insights.get("segments", []):
            snapshot["metrics"]["segments"][seg["name"]] = {
                "n": seg["n"],
                "pct": seg["pct"],
                "satisfaction": seg["satisfaction"]
            }
    
    # Save snapshot
    snapshot_file = SNAPSHOTS_PATH / f"snapshot_{timestamp}.json"
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    print(f"✓ Saved: {snapshot_file.name}")
    
    # Update latest snapshot pointer
    latest_file = SNAPSHOTS_PATH / "latest.json"
    with open(latest_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    print(f"✓ Updated: latest.json")
    
    # Calculate deltas if previous snapshot exists
    calculate_deltas(snapshot)
    
    print("\n" + "=" * 60)
    print("✅ Snapshot captured successfully")
    print(f"   MVP Ready: {snapshot['metrics']['zones']['mvp_ready']}")
    print(f"   Near MVP: {snapshot['metrics']['zones']['near_mvp']}")
    print("=" * 60)

def calculate_deltas(current_snapshot):
    """Calculate week-over-week deltas and save to deltas.json."""
    # Find previous snapshot
    snapshots = sorted(SNAPSHOTS_PATH.glob("snapshot_*.json"))
    
    if len(snapshots) < 2:
        print("ℹ️  Not enough snapshots for delta calculation (need at least 2)")
        return
    
    # Load previous snapshot (second to last)
    prev_file = snapshots[-2]
    with open(prev_file, 'r') as f:
        prev_snapshot = json.load(f)
    
    print(f"\n📊 Calculating deltas vs {prev_snapshot['date']}")
    
    # Calculate deltas
    current_zones = current_snapshot["metrics"]["zones"]
    prev_zones = prev_snapshot["metrics"]["zones"]
    
    deltas = {
        "calculated_at": datetime.now().isoformat(),
        "current_date": current_snapshot["date"],
        "previous_date": prev_snapshot["date"],
        "zones": {
            "mvp_ready": {
                "current": current_zones["mvp_ready"],
                "previous": prev_zones["mvp_ready"],
                "delta": current_zones["mvp_ready"] - prev_zones["mvp_ready"]
            },
            "near_mvp": {
                "current": current_zones["near_mvp"],
                "previous": prev_zones["near_mvp"],
                "delta": current_zones["near_mvp"] - prev_zones["near_mvp"]
            }
        }
    }
    
    # Save deltas
    deltas_file = SNAPSHOTS_PATH / "deltas.json"
    with open(deltas_file, 'w') as f:
        json.dump(deltas, f, indent=2)
    print(f"✓ Saved: deltas.json")
    
    # Also copy to docs/data for dashboard access
    deltas_dashboard_file = DOCS_DATA_PATH / "weekly_deltas.json"
    with open(deltas_dashboard_file, 'w') as f:
        json.dump(deltas, f, indent=2)
    print(f"✓ Copied to: docs/data/weekly_deltas.json")
    
    # Print deltas
    mvp_delta = deltas["zones"]["mvp_ready"]["delta"]
    near_delta = deltas["zones"]["near_mvp"]["delta"]
    
    mvp_sign = "+" if mvp_delta >= 0 else ""
    near_sign = "+" if near_delta >= 0 else ""
    
    print(f"\n   MVP Ready: {current_zones['mvp_ready']} ({mvp_sign}{mvp_delta} vs last week)")
    print(f"   Near MVP: {current_zones['near_mvp']} ({near_sign}{near_delta} vs last week)")

def main():
    capture_snapshot()

if __name__ == "__main__":
    main()


