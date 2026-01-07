#!/usr/bin/env python3
"""
Generate Dashboard Script

Creates a self-contained HTML dashboard with embedded data.

Output: docs/dashboards/consumer_insight_tracker.html

Usage:
    python3 scripts/generate_dashboard.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
DATA_FILE = PROJECT_ROOT / "docs" / "data" / "dashboard_data.json"
TEMPLATE_FILE = PROJECT_ROOT / "DELIVERABLES" / "dashboards" / "consumer_insight_tracker.html"
OUTPUT_FILE = PROJECT_ROOT / "docs" / "dashboards" / "consumer_insight_tracker.html"


def load_data():
    """Load dashboard data."""
    if not DATA_FILE.exists():
        print(f"Error: Data file not found: {DATA_FILE}")
        print("Run 'python3 scripts/prepare_dashboard_data.py' first.")
        sys.exit(1)
    
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def load_template():
    """Load HTML template."""
    if not TEMPLATE_FILE.exists():
        print(f"Error: Template file not found: {TEMPLATE_FILE}")
        sys.exit(1)
    
    with open(TEMPLATE_FILE, 'r') as f:
        return f.read()


def embed_data(html: str, data: dict) -> str:
    """Embed JSON data directly into HTML."""
    # Find the script section and inject data
    data_script = f"""
    <script>
        // Embedded Dashboard Data
        const EMBEDDED_DATA = {json.dumps(data, indent=2)};
    </script>
    """
    
    # Insert before the main script
    html = html.replace(
        '<script>\n        // Dashboard Data - Will be populated from JSON',
        data_script + '\n    <script>\n        // Dashboard Data - Will be populated from JSON'
    )
    
    # Update the loadData function to use embedded data
    old_load = """async function loadData() {
            try {
                const response = await fetch('../data/dashboard_data.json');
                DASHBOARD_DATA = await response.json();
                initializeDashboard();
            } catch (error) {
                console.error('Failed to load data:', error);
                // Use embedded fallback data
                initializeWithFallback();
            }
        }"""
    
    new_load = """async function loadData() {
            // Use embedded data for offline functionality
            if (typeof EMBEDDED_DATA !== 'undefined') {
                DASHBOARD_DATA = EMBEDDED_DATA;
                initializeDashboard();
                return;
            }
            
            // Fallback to fetch if embedded data not available
            try {
                const response = await fetch('../data/dashboard_data.json');
                DASHBOARD_DATA = await response.json();
                initializeDashboard();
            } catch (error) {
                console.error('Failed to load data:', error);
                initializeWithFallback();
            }
        }"""
    
    html = html.replace(old_load, new_load)
    
    return html


def main():
    """Main entry point."""
    print("=" * 60)
    print("GENERATING DASHBOARD")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Load data
    print("Loading data...")
    data = load_data()
    print(f"  Dishes: {len(data.get('dishes', []))}")
    print(f"  Zones: {len(data.get('zones', []))}")
    print(f"  Cuisine gaps: {len(data.get('cuisineGaps', []))}")
    print()
    
    # Load template
    print("Loading template...")
    html = load_template()
    print(f"  Template size: {len(html):,} bytes")
    print()
    
    # Embed data
    print("Embedding data...")
    html = embed_data(html, data)
    print(f"  Final size: {len(html):,} bytes")
    print()
    
    # Save output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)
    
    print("=" * 60)
    print("DASHBOARD GENERATED")
    print("=" * 60)
    print(f"Output: {OUTPUT_FILE}")
    print()
    print("The dashboard is self-contained and works offline.")
    print("Share the HTML file directly or host it on any web server.")
    print()
    
    return True


if __name__ == "__main__":
    main()

