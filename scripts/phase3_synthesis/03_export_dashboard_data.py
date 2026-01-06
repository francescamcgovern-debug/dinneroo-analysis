"""
Script: 03_export_dashboard_data.py
Phase: 3 - Synthesis
Purpose: Export data as JSON for dynamic GitHub Pages dashboards
Inputs:
    - DATA/3_ANALYSIS/priority_100_dishes.csv
    - DATA/3_ANALYSIS/zone_analysis.csv
    - DATA/3_ANALYSIS/cuisine_priorities.csv
    - config/factor_weights.json
    - config/mvp_thresholds.json
Outputs:
    - docs/data/priority_dishes.json
    - docs/data/zone_data.json
    - docs/data/config.json

This script exports analysis results as JSON files that can be loaded
by the GitHub Pages dashboards for dynamic, interactive visualizations.
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
ANALYSIS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DATA_DIR = DOCS_DIR / "data"


def load_analysis_data():
    """Load all analysis outputs."""
    data = {}
    
    # Priority dishes
    dishes_path = ANALYSIS_DIR / "priority_100_dishes.csv"
    if dishes_path.exists():
        data['priority_dishes'] = pd.read_csv(dishes_path)
        logger.info(f"Loaded {len(data['priority_dishes'])} priority dishes")
    
    # Zone analysis
    zones_path = ANALYSIS_DIR / "zone_analysis.csv"
    if zones_path.exists():
        data['zones'] = pd.read_csv(zones_path)
        logger.info(f"Loaded {len(data['zones'])} zones")
    
    # Cuisine priorities
    cuisine_path = ANALYSIS_DIR / "cuisine_priorities.csv"
    if cuisine_path.exists():
        data['cuisines'] = pd.read_csv(cuisine_path)
        logger.info(f"Loaded {len(data['cuisines'])} cuisines")
    
    return data


def load_configs():
    """Load all configuration files."""
    configs = {}
    
    for config_file in ['factor_weights.json', 'mvp_thresholds.json', 'evidence_standards.json']:
        config_path = CONFIG_DIR / config_file
        if config_path.exists():
            with open(config_path) as f:
                configs[config_file.replace('.json', '')] = json.load(f)
    
    return configs


def prepare_dishes_json(dishes_df: pd.DataFrame, config: dict) -> dict:
    """Prepare priority dishes data for JSON export."""
    
    # Get factor columns from config
    factor_names = list(config.get('factor_weights', {}).get('factors', {}).keys())
    
    dishes_list = []
    for _, row in dishes_df.iterrows():
        dish = {
            'rank': int(row.get('priority_rank', row.get('rank', 0))),
            'name': row['dish_name'],
            'cuisine': row.get('cuisine', 'Other'),
            'composite_score': round(float(row['composite_score']), 2),
            'evidence_type': row.get('evidence_type', 'Estimated'),
            'ideal_presentation': row.get('ideal_presentation', ''),
            'positioning_guidance': row.get('positioning_guidance', ''),
            'factors': {}
        }
        
        # Add individual factor scores
        for factor in factor_names:
            if factor in row.index:
                dish['factors'][factor] = int(row[factor]) if pd.notna(row[factor]) else 3
        
        # Add on-menu status
        dish['on_menu'] = row.get('on_dinneroo_menu', 3) >= 3
        
        dishes_list.append(dish)
    
    return {
        'generated_at': datetime.now().isoformat(),
        'total_dishes': len(dishes_list),
        'dishes': dishes_list
    }


def prepare_zones_json(zones_df: pd.DataFrame, config: dict) -> dict:
    """Prepare zone data for JSON export."""
    
    zones_list = []
    for _, row in zones_df.iterrows():
        zone = {
            'rank': int(row.get('rank', 0)),
            'name': row['zone_name'],
            'mvp_status': row.get('mvp_status', 'Unknown'),
            'quality_score': round(float(row.get('quality_score', 0)), 3),
            'metrics': {
                'order_count': int(row.get('order_count', 0)),
                'partner_count': int(row.get('partner_count', 0)),
                'cuisine_count': int(row.get('cuisine_count', 0)),
                'dish_count': int(row.get('dish_count', 0)),
                'avg_rating': round(float(row.get('avg_rating', 0)), 2) if pd.notna(row.get('avg_rating')) else None
            },
            'criteria': {
                'meets_cuisines': bool(row.get('meets_cuisines', False)),
                'meets_partners': bool(row.get('meets_partners', False)),
                'meets_dishes': bool(row.get('meets_dishes', False)),
                'meets_rating': bool(row.get('meets_rating', False))
            },
            'gaps': {
                'supply': row.get('supply_gaps_str', 'None'),
                'quality': row.get('quality_gaps_str', 'None')
            }
        }
        zones_list.append(zone)
    
    # Calculate summary stats
    status_counts = zones_df['mvp_status'].value_counts().to_dict() if 'mvp_status' in zones_df.columns else {}
    
    return {
        'generated_at': datetime.now().isoformat(),
        'total_zones': len(zones_list),
        'summary': {
            'mvp_ready': status_counts.get('MVP Ready', 0),
            'near_mvp': status_counts.get('Near MVP', 0),
            'developing': status_counts.get('Developing', 0),
            'early_stage': status_counts.get('Early Stage', 0)
        },
        'zones': zones_list
    }


def prepare_config_json(configs: dict) -> dict:
    """Prepare configuration data for dashboard use."""
    
    # Extract factor weights for sliders
    factor_weights = {}
    if 'factor_weights' in configs:
        for name, info in configs['factor_weights'].get('factors', {}).items():
            factor_weights[name] = {
                'weight': info.get('weight', 0.1),
                'description': info.get('description', ''),
                'source': info.get('source', 'estimated')
            }
    
    # Extract MVP thresholds
    mvp_thresholds = {}
    if 'mvp_thresholds' in configs:
        for name, info in configs['mvp_thresholds'].get('mvp_criteria', {}).items():
            mvp_thresholds[name] = {
                'value': info.get('value'),
                'justification': info.get('justification', '')
            }
    
    return {
        'generated_at': datetime.now().isoformat(),
        'factor_weights': factor_weights,
        'mvp_thresholds': mvp_thresholds,
        'evidence_types': configs.get('factor_weights', {}).get('evidence_types', {}),
        'score_conversion': configs.get('factor_weights', {}).get('score_conversion', {})
    }


def main():
    """Main function to export dashboard data."""
    logger.info("=" * 60)
    logger.info("PHASE 3: Exporting Dashboard Data")
    logger.info("=" * 60)
    
    # Ensure output directories exist
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    analysis_data = load_analysis_data()
    configs = load_configs()
    
    # Prepare and export priority dishes
    if 'priority_dishes' in analysis_data:
        dishes_json = prepare_dishes_json(analysis_data['priority_dishes'], configs)
        dishes_path = DOCS_DATA_DIR / "priority_dishes.json"
        with open(dishes_path, 'w') as f:
            json.dump(dishes_json, f, indent=2)
        logger.info(f"Exported priority dishes to: {dishes_path}")
    
    # Prepare and export zones
    if 'zones' in analysis_data:
        zones_json = prepare_zones_json(analysis_data['zones'], configs)
        zones_path = DOCS_DATA_DIR / "zone_data.json"
        with open(zones_path, 'w') as f:
            json.dump(zones_json, f, indent=2)
        logger.info(f"Exported zone data to: {zones_path}")
    
    # Export config
    config_json = prepare_config_json(configs)
    config_path = DOCS_DATA_DIR / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config_json, f, indent=2)
    logger.info(f"Exported config to: {config_path}")
    
    # Create a manifest file
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'files': [
            {'name': 'priority_dishes.json', 'description': 'Priority 100 dishes with scores'},
            {'name': 'zone_data.json', 'description': 'Zone MVP status and metrics'},
            {'name': 'config.json', 'description': 'Factor weights and thresholds'}
        ]
    }
    manifest_path = DOCS_DATA_DIR / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info("\n" + "=" * 60)
    logger.info("DASHBOARD DATA EXPORT COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Files exported to: {DOCS_DATA_DIR}")
    logger.info("Dashboards can now load data dynamically from these JSON files")
    
    return manifest


if __name__ == "__main__":
    main()

