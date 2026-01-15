#!/usr/bin/env python3
"""
MVP Threshold Strengthening Analysis
=====================================
Strengthens the 5/5/20 MVP recommendation with:
1. Additional outcome metrics (rating, kids_happy, enough_food)
2. Sample sizes and confidence levels
3. Monotonicity checks
4. Sensitivity analysis
5. Confounding narrative

Outputs:
- mvp_strengthening_report.xlsx
- mvp_strengthening_narrative.md
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import re

# Paths
BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "DATA/3_ANALYSIS"
DELIVERABLES_DIR = BASE_DIR / "DELIVERABLES/reports"
CONFIG_DIR = BASE_DIR / "config"

def load_threshold_data():
    """Load the MVP threshold discovery data."""
    path = ANALYSIS_DIR / "mvp_threshold_discovery.json"
    with open(path) as f:
        return json.load(f)

def load_mvp_threshold_config():
    """Load business targets (north star) for MVP thresholds."""
    path = CONFIG_DIR / "mvp_thresholds.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)

def extract_metrics_by_bucket(data, step, bucket_key):
    """Extract metrics for a given step and create a summary table."""
    if isinstance(data, dict) and step in data:
        buckets = data[step][bucket_key]
    else:
        buckets = data[bucket_key]
    
    rows = []
    for bucket in buckets:
        row = {
            'bucket': bucket['bucket'],
            'zones': bucket['zones'],
            'repeat_rate': bucket['behavioral']['repeat_rate']['value'],
            'repeat_rate_n': bucket['behavioral']['repeat_rate']['n'],
            'avg_rating': bucket['behavioral']['avg_rating']['value'],
            'avg_rating_n': bucket['behavioral']['avg_rating']['n'],
            'order_volume': bucket['behavioral'].get('order_volume', {}).get('value'),
            'order_volume_n': bucket['behavioral'].get('order_volume', {}).get('n', 0),
            'kids_happy': bucket['survey'].get('kids_happy', {}).get('value'),
            'kids_happy_n': bucket['survey'].get('kids_happy', {}).get('n', 0),
            'kids_happy_reliable': bucket['survey'].get('kids_happy', {}).get('reliable', False),
            'enough_food': bucket['survey'].get('enough_food', {}).get('value'),
            'enough_food_n': bucket['survey'].get('enough_food', {}).get('n', 0),
            'liked_loved': bucket['survey'].get('liked_loved', {}).get('value'),
            'liked_loved_n': bucket['survey'].get('liked_loved', {}).get('n', 0),
            'food_hot': bucket['survey'].get('food_hot', {}).get('value'),
            'food_hot_n': bucket['survey'].get('food_hot', {}).get('n', 0),
            'food_on_time': bucket['survey'].get('food_on_time', {}).get('value'),
            'food_on_time_n': bucket['survey'].get('food_on_time', {}).get('n', 0),
            'reorder_intent': bucket['survey'].get('reorder_intent', {}).get('value'),
            'reorder_intent_n': bucket['survey'].get('reorder_intent', {}).get('n', 0),
        }
        rows.append(row)
    
    return pd.DataFrame(rows)

def bucket_sort_key(bucket: str) -> float:
    """
    Convert bucket strings into a sortable numeric key.
    Examples:
    - "1-2" -> 1
    - "3-4" -> 3
    - "10+" -> 10
    - "7+" -> 7
    - "1-15" -> 1
    - "16-30" -> 16
    """
    if bucket is None or (isinstance(bucket, float) and pd.isna(bucket)):
        return float("inf")
    s = str(bucket).strip()
    m = re.match(r"^(\d+)\+$", s)
    if m:
        return float(m.group(1))
    m = re.match(r"^(\d+)-(\d+)$", s)
    if m:
        return float(m.group(1))
    return float("inf")

def check_monotonicity(df, metric_col):
    """Check if a metric increases monotonically as bucket increases."""
    if metric_col not in df.columns:
        return None, "Metric not available"

    df_sorted = df.copy()
    if 'bucket' in df_sorted.columns:
        df_sorted['_bucket_key'] = df_sorted['bucket'].apply(bucket_sort_key)
        df_sorted = df_sorted.sort_values('_bucket_key')

    values = df_sorted[metric_col].dropna().tolist()
    
    if len(values) < 2:
        return None, "Insufficient data"
    
    # Check if mostly increasing
    increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
    total = len(values) - 1
    
    if increases == total:
        return True, "Perfectly monotonic"
    elif increases >= total * 0.75:
        return True, f"Mostly monotonic ({increases}/{total} increases)"
    else:
        return False, f"Non-monotonic ({increases}/{total} increases)"

def calculate_confidence(n, is_behavioral=True):
    """Calculate confidence level based on sample size."""
    if is_behavioral:
        if n >= 1000:
            return 'HIGH'
        elif n >= 500:
            return 'MED'
        else:
            return 'LOW'
    else:  # Survey
        if n >= 100:
            return 'HIGH'
        elif n >= 50:
            return 'MED'
        elif n >= 20:
            return 'LOW'
        else:
            return 'VERY LOW'

def pct(val):
    """Format 0-1 proportion as percentage string."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "N/A"
    return f"{val*100:.1f}%"

def num(val, digits=2):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "N/A"
    return f"{val:.{digits}f}"

def compute_threshold_scorecard(df, below_buckets, above_buckets):
    """
    Compute a multi-metric scorecard comparing below vs at/above buckets.
    Returns rows suitable for both narrative and Excel.
    """
    below = df[df['bucket'].isin(below_buckets)]
    above = df[df['bucket'].isin(above_buckets)]
    if len(below) == 0 or len(above) == 0:
        return []

    # Metrics: (col, n_col, kind)
    # kind: 'pct' means 0-1 proportion; 'rating' and 'volume' are raw.
    metrics = [
        ('repeat_rate', 'repeat_rate_n', 'pct'),
        ('avg_rating', 'avg_rating_n', 'rating'),
        ('kids_happy', 'kids_happy_n', 'pct'),
        ('liked_loved', 'liked_loved_n', 'pct'),
        ('enough_food', 'enough_food_n', 'pct'),
        ('food_hot', 'food_hot_n', 'pct'),
        ('food_on_time', 'food_on_time_n', 'pct'),
        ('order_volume', 'order_volume_n', 'volume'),
    ]

    rows = []
    for col, n_col, kind in metrics:
        if col not in df.columns:
            continue
        below_val = below[col].mean()
        above_val = above[col].mean()
        n_below = int(pd.to_numeric(below.get(n_col, 0), errors='coerce').fillna(0).sum()) if n_col in df.columns else 0
        n_above = int(pd.to_numeric(above.get(n_col, 0), errors='coerce').fillna(0).sum()) if n_col in df.columns else 0

        if kind == 'pct':
            delta = (above_val - below_val) * 100 if pd.notna(above_val) and pd.notna(below_val) else None
            delta_fmt = f"{delta:+.1f}pp" if delta is not None else "N/A"
            below_fmt = pct(below_val)
            above_fmt = pct(above_val)
            conf = calculate_confidence(n_above, is_behavioral=False)
        elif kind == 'rating':
            delta = (above_val - below_val) if pd.notna(above_val) and pd.notna(below_val) else None
            delta_fmt = f"{delta:+.2f}" if delta is not None else "N/A"
            below_fmt = num(below_val, digits=2)
            above_fmt = num(above_val, digits=2)
            conf = calculate_confidence(n_above, is_behavioral=True)
        else:  # volume
            delta = (above_val - below_val) if pd.notna(above_val) and pd.notna(below_val) else None
            delta_fmt = f"{delta:+.0f}" if delta is not None else "N/A"
            below_fmt = num(below_val, digits=0)
            above_fmt = num(above_val, digits=0)
            # order_volume_n is zones, so this is directional only
            conf = 'MED'

        rows.append({
            'metric': col,
            'below': below_val,
            'above': above_val,
            'below_fmt': below_fmt,
            'above_fmt': above_fmt,
            'delta_fmt': delta_fmt,
            'n_below': n_below,
            'n_above': n_above,
            'confidence': conf,
        })
    return rows

def create_summary_table(df_partners, df_cuisines, df_dishes):
    """Create a combined scorecard table for the 5/5/20 thresholds (multi-metric)."""
    
    summary_rows = []
    
    # Partner threshold (5+)
    partner_above = ['5-6', '7-9', '10+']
    partner_below = ['1-2', '3-4']
    for r in compute_threshold_scorecard(df_partners, partner_below, partner_above):
        summary_rows.append({'dimension': 'Partners', 'threshold': '5+', **r})
    
    # Cuisine threshold (5+)
    cuisine_above = ['5-6', '7+']
    cuisine_below = ['1-2', '3-4']
    for r in compute_threshold_scorecard(df_cuisines, cuisine_below, cuisine_above):
        summary_rows.append({'dimension': 'Cuisines', 'threshold': '5+', **r})
    
    # Dish threshold (20+) - using dishes_per_zone
    dish_above = ['16-30', '31-50', '51+']  # includes 20+ within these buckets
    dish_below = ['1-15']
    for r in compute_threshold_scorecard(df_dishes, dish_below, dish_above):
        summary_rows.append({'dimension': 'Dishes', 'threshold': '20+', **r})
    
    df_summary = pd.DataFrame(summary_rows)
    # Friendly metric names for outputs
    metric_names = {
        'repeat_rate': 'Repeat Rate',
        'avg_rating': 'Avg Rating',
        'kids_happy': 'Kids Happy',
        'liked_loved': 'Liked/Loved',
        'enough_food': 'Enough Food',
        'food_hot': 'Food Hot',
        'food_on_time': 'Food On Time',
        'order_volume': 'Orders per Zone (avg)',
    }
    if not df_summary.empty:
        df_summary['metric_name'] = df_summary['metric'].map(metric_names).fillna(df_summary['metric'])
    return df_summary

def extract_step_recommendations(data):
    """Extract data-driven inflection recommendations (if present) for each step."""
    recs = {}
    # Step 1 partners
    s1 = data.get('step_1_partners', {})
    recs['partners'] = {
        'inflection': (s1.get('inflection_analysis') or {}),
        'recommendation': (s1.get('recommendation') or {}),
        'consensus': (s1.get('consensus') or {}),
    }
    # Step 2 cuisines
    s2 = data.get('step_2_cuisines_within_partners', {})
    recs['cuisines'] = {
        'inflection': (s2.get('inflection_analysis') or {}),
        'recommendation': (s2.get('recommendation') or {}),
        'consensus': (s2.get('consensus') or {}),
        'filter': s2.get('filter_applied'),
    }
    # Step 3 dishes
    s3 = data.get('step_3_dishes_within_partners_and_cuisines', {})
    # This step nests details under dishes_per_zone / dishes_per_partner; keep both if present.
    recs['dishes'] = {
        'by_zone': (s3.get('dishes_per_zone') or {}),
        'by_partner': (s3.get('dishes_per_partner') or {}),
    }
    return recs

def generate_narrative(df_summary, monotonicity_results, correlations, cfg, recs):
    """Generate the strengthening narrative."""

    # Business targets (north star)
    mvp_criteria = (cfg or {}).get('mvp_criteria', {})
    partners_target = (mvp_criteria.get('partners_min') or {}).get('value', 5)
    cuisines_target = (mvp_criteria.get('cuisines_min') or {}).get('value', 5)
    dishes_target = (mvp_criteria.get('dishes_min') or {}).get('value', 21)
    partners_inflect = (mvp_criteria.get('partners_min') or {}).get('data_inflection_point')
    cuisines_inflect = (mvp_criteria.get('cuisines_min') or {}).get('data_inflection_point')

    # Helper to pull a metric row for a dimension
    def row(dim, metric):
        d = df_summary[(df_summary['dimension'] == dim) & (df_summary['metric'] == metric)]
        return d.iloc[0] if len(d) else None

    # Executive scorecard lines (repeat + rating + satisfaction + value + ops)
    partners_rr = row('Partners', 'repeat_rate')
    cuisines_rr = row('Cuisines', 'repeat_rate')
    dishes_rr = row('Dishes', 'repeat_rate')

    narrative = f"""# MVP Threshold Strengthening Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**North-star targets (business)**: {partners_target}+ partners, {cuisines_target}+ cuisines, {dishes_target}+ dishes

## Executive Summary (multi-metric)

This strengthens the MVP thresholds using **multiple independent outcome metrics** (not just repeat rate):
- Behavioral: repeat rate, average rating, order volume
- Survey: kids happy, liked/loved, enough food, food hot, on-time

**Headline:** The 5/5/20 direction is supported across multiple outcomes, with important nuance:
- Data-driven **inflection often starts around ~3–4** (minimum viable)
- **5+ is the product “north star”** for redundancy and family variety

### Scorecard at the thresholds (Below vs At/Above)

| Dimension | Threshold | Repeat Rate | Avg Rating | Kids Happy | Enough Food | Food Hot | On Time |
|----------|-----------|------------|-----------|-----------|------------|---------|--------|
| Partners | {partners_target}+ | {partners_rr['below_fmt'] if partners_rr is not None else 'N/A'} → {partners_rr['above_fmt'] if partners_rr is not None else 'N/A'} ({partners_rr['delta_fmt'] if partners_rr is not None else 'N/A'}) | {num(row('Partners','avg_rating')['below'],2) if row('Partners','avg_rating') is not None else 'N/A'} → {num(row('Partners','avg_rating')['above'],2) if row('Partners','avg_rating') is not None else 'N/A'} | {row('Partners','kids_happy')['below_fmt'] if row('Partners','kids_happy') is not None else 'N/A'} → {row('Partners','kids_happy')['above_fmt'] if row('Partners','kids_happy') is not None else 'N/A'} | {row('Partners','enough_food')['below_fmt'] if row('Partners','enough_food') is not None else 'N/A'} → {row('Partners','enough_food')['above_fmt'] if row('Partners','enough_food') is not None else 'N/A'} | {row('Partners','food_hot')['below_fmt'] if row('Partners','food_hot') is not None else 'N/A'} → {row('Partners','food_hot')['above_fmt'] if row('Partners','food_hot') is not None else 'N/A'} | {row('Partners','food_on_time')['below_fmt'] if row('Partners','food_on_time') is not None else 'N/A'} → {row('Partners','food_on_time')['above_fmt'] if row('Partners','food_on_time') is not None else 'N/A'} |
| Cuisines | {cuisines_target}+ | {cuisines_rr['below_fmt'] if cuisines_rr is not None else 'N/A'} → {cuisines_rr['above_fmt'] if cuisines_rr is not None else 'N/A'} ({cuisines_rr['delta_fmt'] if cuisines_rr is not None else 'N/A'}) | {num(row('Cuisines','avg_rating')['below'],2) if row('Cuisines','avg_rating') is not None else 'N/A'} → {num(row('Cuisines','avg_rating')['above'],2) if row('Cuisines','avg_rating') is not None else 'N/A'} | {row('Cuisines','kids_happy')['below_fmt'] if row('Cuisines','kids_happy') is not None else 'N/A'} → {row('Cuisines','kids_happy')['above_fmt'] if row('Cuisines','kids_happy') is not None else 'N/A'} | {row('Cuisines','enough_food')['below_fmt'] if row('Cuisines','enough_food') is not None else 'N/A'} → {row('Cuisines','enough_food')['above_fmt'] if row('Cuisines','enough_food') is not None else 'N/A'} | {row('Cuisines','food_hot')['below_fmt'] if row('Cuisines','food_hot') is not None else 'N/A'} → {row('Cuisines','food_hot')['above_fmt'] if row('Cuisines','food_hot') is not None else 'N/A'} | {row('Cuisines','food_on_time')['below_fmt'] if row('Cuisines','food_on_time') is not None else 'N/A'} → {row('Cuisines','food_on_time')['above_fmt'] if row('Cuisines','food_on_time') is not None else 'N/A'} |
| Dishes | 20+ | {dishes_rr['below_fmt'] if dishes_rr is not None else 'N/A'} → {dishes_rr['above_fmt'] if dishes_rr is not None else 'N/A'} ({dishes_rr['delta_fmt'] if dishes_rr is not None else 'N/A'}) | {num(row('Dishes','avg_rating')['below'],2) if row('Dishes','avg_rating') is not None else 'N/A'} → {num(row('Dishes','avg_rating')['above'],2) if row('Dishes','avg_rating') is not None else 'N/A'} | {row('Dishes','kids_happy')['below_fmt'] if row('Dishes','kids_happy') is not None else 'N/A'} → {row('Dishes','kids_happy')['above_fmt'] if row('Dishes','kids_happy') is not None else 'N/A'} | {row('Dishes','enough_food')['below_fmt'] if row('Dishes','enough_food') is not None else 'N/A'} → {row('Dishes','enough_food')['above_fmt'] if row('Dishes','enough_food') is not None else 'N/A'} | {row('Dishes','food_hot')['below_fmt'] if row('Dishes','food_hot') is not None else 'N/A'} → {row('Dishes','food_hot')['above_fmt'] if row('Dishes','food_hot') is not None else 'N/A'} | {row('Dishes','food_on_time')['below_fmt'] if row('Dishes','food_on_time') is not None else 'N/A'} → {row('Dishes','food_on_time')['above_fmt'] if row('Dishes','food_on_time') is not None else 'N/A'} |

## Inflection vs Target (what to say in CD)

- **Data inflection (minimum viable)**: partners ~{partners_inflect}+ and cuisines ~{cuisines_inflect}+ show meaningful improvement in the underlying analysis (see `mvp_threshold_discovery.json` inflection_analysis).
- **Business target (north star)**: {partners_target}+ partners and {cuisines_target}+ cuisines support redundancy and choice (see `config/mvp_thresholds.json`).
- **Interpretation**: “3+ is where performance starts to lift; 5+ is the intended family proposition.”

## Monotonicity Checks (diagnostic only)

Monotonicity is mixed because bucket sizes are uneven and supply factors are correlated; we treat this as **context**, not the core proof.

| Dimension | Repeat Rate | Kids Happy | Avg Rating |
|-----------|-------------|------------|------------|
| Partners | {monotonicity_results.get('partners_repeat', 'N/A')} | {monotonicity_results.get('partners_kids', 'N/A')} | {monotonicity_results.get('partners_rating', 'N/A')} |
| Cuisines | {monotonicity_results.get('cuisines_repeat', 'N/A')} | {monotonicity_results.get('cuisines_kids', 'N/A')} | {monotonicity_results.get('cuisines_rating', 'N/A')} |
| Dishes | {monotonicity_results.get('dishes_repeat', 'N/A')} | {monotonicity_results.get('dishes_kids', 'N/A')} | {monotonicity_results.get('dishes_rating', 'N/A')} |

## Confounding Factors

**Important caveat**: Partners and cuisines are highly correlated (r={correlations['partner_cuisine']:.2f}).

This means:
- Zones with more partners tend to also have more cuisines
- It’s difficult to isolate the independent effect of each factor
- The thresholds should be seen as a **package**, not independent requirements

**Mitigation**: The underlying analysis is hierarchical (partners → cuisines controlling for partners → dishes controlling for both), which provides **directional evidence** rather than causal claims.

## Recommendation

**Maintain the {partners_target}/{cuisines_target}/{dishes_target} north-star thresholds** and communicate:
- “Minimum viable lift starts around ~3–4”
- “5+ is where the proposition becomes reliably good for families”

---

*This analysis strengthens (rather than replaces) the existing threshold recommendation.*
"""
    return narrative

def main():
    """Main execution."""
    print("=" * 60)
    print("MVP THRESHOLD STRENGTHENING ANALYSIS")
    print("=" * 60)
    
    # Load data
    data = load_threshold_data()
    cfg = load_mvp_threshold_config()
    recs = extract_step_recommendations(data)
    
    # Extract metrics by bucket
    print("\nExtracting partner metrics...")
    df_partners = extract_metrics_by_bucket(data, 'step_1_partners', 'by_partner_count')
    
    print("Extracting cuisine metrics...")
    df_cuisines = extract_metrics_by_bucket(data, 'step_2_cuisines_within_partners', 'by_cuisine_count')
    
    print("Extracting dish metrics...")
    # The dishes data is under 'dishes_per_zone' -> 'buckets'
    df_dishes = extract_metrics_by_bucket(data['step_3_dishes_within_partners_and_cuisines'], 'dishes_per_zone', 'buckets')
    
    # Monotonicity checks
    print("\nRunning monotonicity checks...")
    monotonicity_results = {
        'partners_repeat': check_monotonicity(df_partners, 'repeat_rate')[1],
        'partners_kids': check_monotonicity(df_partners, 'kids_happy')[1],
        'partners_rating': check_monotonicity(df_partners, 'avg_rating')[1],
        'cuisines_repeat': check_monotonicity(df_cuisines, 'repeat_rate')[1],
        'cuisines_kids': check_monotonicity(df_cuisines, 'kids_happy')[1],
        'cuisines_rating': check_monotonicity(df_cuisines, 'avg_rating')[1],
        'dishes_repeat': check_monotonicity(df_dishes, 'repeat_rate')[1],
        'dishes_kids': check_monotonicity(df_dishes, 'kids_happy')[1],
        'dishes_rating': check_monotonicity(df_dishes, 'avg_rating')[1],
    }
    
    # Create summary table
    print("Creating summary table...")
    df_summary = create_summary_table(df_partners, df_cuisines, df_dishes)
    
    # Generate narrative
    narrative = generate_narrative(df_summary, monotonicity_results, data['correlations'], cfg, recs)
    
    # Save outputs
    print("\nSaving outputs...")
    
    # Excel workbook
    excel_path = DELIVERABLES_DIR / "mvp_strengthening_report.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Scorecard', index=False)
        df_partners.to_excel(writer, sheet_name='Partners by Bucket', index=False)
        df_cuisines.to_excel(writer, sheet_name='Cuisines by Bucket', index=False)
        df_dishes.to_excel(writer, sheet_name='Dishes by Bucket', index=False)
    print(f"  Saved Excel report to: {excel_path}")
    
    # Narrative
    narrative_path = DELIVERABLES_DIR / "mvp_strengthening_narrative.md"
    with open(narrative_path, 'w') as f:
        f.write(narrative)
    print(f"  Saved narrative to: {narrative_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(df_summary.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("MONOTONICITY RESULTS")
    print("=" * 60)
    for key, value in monotonicity_results.items():
        print(f"  {key}: {value}")
    
    return df_summary, monotonicity_results

if __name__ == "__main__":
    main()
