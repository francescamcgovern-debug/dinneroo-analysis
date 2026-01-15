#!/usr/bin/env python3
"""
Dinneroo Analysis Pipeline Runner

One-command execution of the full analysis pipeline.

Usage:
    python run_pipeline.py --all           # Full pipeline
    python run_pipeline.py --phase 1       # Just data loading
    python run_pipeline.py --phase 2       # Just analysis
    python run_pipeline.py --phase 3       # Just synthesis
    python run_pipeline.py --dashboards    # Just export for dashboards
    python run_pipeline.py --validate      # Just data validation

The pipeline follows Denis Rothman's methodology:
- Phase 1: Data Preparation (load, extract, validate)
- Phase 2: Analysis (score dishes, analyze zones, segment customers)
- Phase 3: Synthesis (generate reports, export dashboards)
"""

import argparse
import logging
import subprocess
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
SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent

# Pipeline configuration
# Updated 2026-01-06: Now uses v3 scoring (Two-Track) and v2 priority list (with Smart Discovery)
PHASES = {
    1: {
        'name': 'Data Preparation',
        'scripts': [
            'phase1_data/01_load_sources.py',
            'phase1_data/02_extract_survey_scores.py',
            'phase1_data/03_validate_data.py',
            'phase1_data/04_validate_config.py',  # Validates config against actual data - fails early if unfounded recommendations
            'phase1_data/05_extract_performance.py'  # Required for v3 scoring
        ]
    },
    2: {
        'name': 'Analysis',
        'scripts': [
            'phase2_analysis/01_score_dishes_v3.py',  # Two-Track scoring (Track A + Track B)
            'phase2_analysis/02_analyze_zones.py',
            'phase2_analysis/03_segment_customers.py',
            'phase2_analysis/04_smart_discovery.py',   # Smart Discovery dishes
            'phase2_analysis/generate_three_lists.py'  # Segment-specific rankings (Family/Couple/Recruitment)
        ]
    },
    3: {
        'name': 'Synthesis',
        'scripts': [
            'phase3_synthesis/01_generate_priority_list_v2.py',  # Combined priority list
            'phase3_synthesis/02_generate_zone_report.py',
            'phase3_synthesis/03_export_dashboard_data.py',
            'generate_zone_dashboard_data.py',  # Updates zone_analysis.json
            'sync_zone_data.py',  # Syncs zone_analysis.json → zone_data.js (for dashboard)
            'update_master_dashboard.py'  # Updates master dashboard with latest metrics
        ]
    }
}


def run_script(script_path: Path) -> bool:
    """Run a single Python script and return success status."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Running: {script_path.name}")
    logger.info('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✓ {script_path.name} completed successfully")
            return True
        else:
            logger.error(f"✗ {script_path.name} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error running {script_path.name}: {e}")
        return False


def run_phase(phase_num: int) -> bool:
    """Run all scripts in a phase."""
    if phase_num not in PHASES:
        logger.error(f"Invalid phase number: {phase_num}")
        return False
    
    phase = PHASES[phase_num]
    logger.info(f"\n{'#'*60}")
    logger.info(f"PHASE {phase_num}: {phase['name']}")
    logger.info('#'*60)
    
    success = True
    for script in phase['scripts']:
        script_path = SCRIPTS_DIR / script
        if not script_path.exists():
            logger.warning(f"Script not found: {script_path}")
            continue
        
        if not run_script(script_path):
            success = False
            # Continue with other scripts even if one fails
    
    return success


def run_full_pipeline() -> bool:
    """Run the complete pipeline."""
    start_time = datetime.now()
    logger.info(f"\n{'#'*60}")
    logger.info("DINNEROO ANALYSIS PIPELINE")
    logger.info(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info('#'*60)
    
    success = True
    for phase_num in sorted(PHASES.keys()):
        if not run_phase(phase_num):
            success = False
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"\n{'#'*60}")
    logger.info("PIPELINE COMPLETE")
    logger.info(f"Duration: {duration}")
    logger.info(f"Status: {'SUCCESS' if success else 'COMPLETED WITH ERRORS'}")
    logger.info('#'*60)
    
    return success


def run_dashboards_only() -> bool:
    """
    Update dashboard data + sync GitHub Pages outputs.

    Note:
    - Historically this pointed at `phase3_synthesis/03_export_dashboard_data.py`, which is currently a no-op.
    - The real dashboard update flow is:
        1) generate `docs/data/zone_analysis.json` (+ refresh `docs/data/zone_mvp_status.json`)
        2) update embedded metrics inside the master dashboard HTML
        3) sync `zone_data.js` + copy master dashboard → `docs/dashboard.html`
    """
    steps = [
        SCRIPTS_DIR / 'generate_zone_dashboard_data.py',
        SCRIPTS_DIR / 'update_master_dashboard.py',
        SCRIPTS_DIR / 'sync_zone_data.py',
    ]

    success = True
    for script_path in steps:
        if not run_script(script_path):
            success = False
    return success


def run_validation_only() -> bool:
    """Run only the data validation script."""
    script_path = SCRIPTS_DIR / 'phase1_data/03_validate_data.py'
    return run_script(script_path)


def main():
    parser = argparse.ArgumentParser(
        description='Dinneroo Analysis Pipeline Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Run the full pipeline (all phases)'
    )
    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3],
        help='Run a specific phase (1=Data, 2=Analysis, 3=Synthesis)'
    )
    parser.add_argument(
        '--dashboards',
        action='store_true',
        help='Export dashboard data only'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run data validation only'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all scripts in the pipeline'
    )
    
    args = parser.parse_args()
    
    # List scripts if requested
    if args.list:
        print("\nDinneroo Analysis Pipeline Scripts:")
        print("="*50)
        for phase_num, phase in PHASES.items():
            print(f"\nPhase {phase_num}: {phase['name']}")
            for script in phase['scripts']:
                script_path = SCRIPTS_DIR / script
                status = "✓" if script_path.exists() else "✗"
                print(f"  {status} {script}")
        return
    
    # Run appropriate command
    success = True
    
    if args.all:
        success = run_full_pipeline()
    elif args.phase:
        success = run_phase(args.phase)
    elif args.dashboards:
        success = run_dashboards_only()
    elif args.validate:
        success = run_validation_only()
    else:
        # Default: show help
        parser.print_help()
        print("\nExamples:")
        print("  python run_pipeline.py --all        # Full pipeline")
        print("  python run_pipeline.py --phase 1    # Data preparation only")
        print("  python run_pipeline.py --dashboards # Update dashboards")
        return
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

