#!/usr/bin/env python3
"""
Quality Gate - QC Report Generator
===================================
Generates QC_REPORT.md and MANUAL_REVIEW_QUEUE.csv for pre-readout validation.

Checks:
A. Schema & completeness
B. Source integrity
C. Mapping quality
D. Validation rubric conformance
E. Not-on-Dinneroo handling
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "DATA/3_ANALYSIS"
SOURCE_DIR = BASE_DIR / "DATA/1_SOURCE/anna_slides"
DELIVERABLES_DIR = BASE_DIR / "DELIVERABLES/reports"
DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

# Expected dish types (canonical list)
CANONICAL_DINNEROO = [
    'Pasta', 'Rice Bowl', 'Grain Bowl', 'Noodles', 'South Asian / Indian Curry',
    'East Asian Curry', 'Katsu', 'Biryani', 'Pizza', 'Fried Rice', 'Protein & Veg',
    'Chilli', 'Fajitas', 'Lasagne', 'Shawarma', 'Tacos', 'Burrito / Burrito Bowl',
    'Quesadilla', 'Nachos', 'Pho', 'Poke', "Shepherd's Pie", 'Sushi'
]

CANONICAL_NOT_ON_DINNEROO = [
    'Casserole / Stew', 'Risotto', 'Tagine', 'Paella', 'Pastry Pie',
    'Jacket potato', 'Sausage & mash', 'Fish & chips', 'Roast', 'Peking duck', 'Mezze'
]

def run_qc_checks():
    """Run all QC checks and return results."""
    results = []
    manual_review_queue = []
    
    # Load files
    working_path = ANALYSIS_DIR / "dish_validation_working.csv"
    df = pd.read_csv(working_path)
    
    qa_path = ANALYSIS_DIR / "dish_survey_mapping_qa.csv"
    df_qa = pd.read_csv(qa_path)
    
    row_level_path = ANALYSIS_DIR / "kids_full_and_happy_row_level.csv"
    df_row = pd.read_csv(row_level_path)
    
    # ========================================
    # A. SCHEMA & COMPLETENESS
    # ========================================
    print("Checking A. Schema & completeness...")
    
    required_cols = ['dish_type', 'cuisine', 'current_tier', 'looker_demand_index',
                     'looker_preference_index', 'validation_status', 'validation_confidence']
    missing_cols = [c for c in required_cols if c not in df.columns]
    
    if missing_cols:
        results.append({
            'check': 'A1. Required columns exist',
            'status': 'FAIL',
            'severity': 'HIGH',
            'details': f"Missing: {missing_cols}"
        })
    else:
        results.append({
            'check': 'A1. Required columns exist',
            'status': 'PASS',
            'severity': '-',
            'details': 'All required columns present'
        })
    
    # Check for duplicate dish_type
    dups = df['dish_type'].duplicated().sum()
    if dups > 0:
        results.append({
            'check': 'A2. No duplicate dish_type',
            'status': 'FAIL',
            'severity': 'HIGH',
            'details': f"{dups} duplicates found"
        })
    else:
        results.append({
            'check': 'A2. No duplicate dish_type',
            'status': 'PASS',
            'severity': '-',
            'details': 'No duplicates'
        })
    
    # Check canonical list match
    actual_dinneroo = set(df[df['on_dinneroo'] == True]['dish_type'].tolist())
    expected_dinneroo = set(CANONICAL_DINNEROO)
    missing = expected_dinneroo - actual_dinneroo
    extra = actual_dinneroo - expected_dinneroo
    
    if missing or extra:
        results.append({
            'check': 'A3. Canonical dish list match',
            'status': 'WARN',
            'severity': 'MED',
            'details': f"Missing: {missing if missing else 'None'}; Extra: {extra if extra else 'None'}"
        })
    else:
        results.append({
            'check': 'A3. Canonical dish list match',
            'status': 'PASS',
            'severity': '-',
            'details': 'All canonical dishes present'
        })
    
    # ========================================
    # B. SOURCE INTEGRITY
    # ========================================
    print("Checking B. Source integrity...")
    
    # Check that looker metrics are present for Dinneroo dishes
    dinneroo_df = df[df['on_dinneroo'] == True]
    missing_demand = dinneroo_df['looker_demand_index'].isna().sum()
    missing_pref = dinneroo_df['looker_preference_index'].isna().sum()
    
    if missing_demand > 0 or missing_pref > 0:
        results.append({
            'check': 'B1. Looker metrics populated for Dinneroo dishes',
            'status': 'WARN',
            'severity': 'MED',
            'details': f"Missing demand: {missing_demand}, Missing preference: {missing_pref}"
        })
    else:
        results.append({
            'check': 'B1. Looker metrics populated for Dinneroo dishes',
            'status': 'PASS',
            'severity': '-',
            'details': 'All Looker metrics present'
        })
    
    # ========================================
    # C. MAPPING QUALITY
    # ========================================
    print("Checking C. Mapping quality...")
    
    # Get overall mapping coverage
    overall_row = df_qa[df_qa['dish_type'] == '_OVERALL_']
    if len(overall_row) > 0:
        overall_coverage = overall_row['mapping_coverage_pct'].values[0]
        if overall_coverage < 60:
            results.append({
                'check': 'C1. Overall mapping coverage ≥60%',
                'status': 'FAIL',
                'severity': 'HIGH',
                'details': f"Coverage is {overall_coverage:.1f}%"
            })
        elif overall_coverage < 75:
            results.append({
                'check': 'C1. Overall mapping coverage ≥60%',
                'status': 'WARN',
                'severity': 'MED',
                'details': f"Coverage is {overall_coverage:.1f}% (below 75% target)"
            })
        else:
            results.append({
                'check': 'C1. Overall mapping coverage ≥60%',
                'status': 'PASS',
                'severity': '-',
                'details': f"Coverage is {overall_coverage:.1f}%"
            })
    
    # Check for low-n dishes
    low_n_dishes = df[(df['on_dinneroo'] == True) & 
                       (df['kids_full_and_happy_n'] < 20) & 
                       (df['kids_full_and_happy_n'].notna())]
    
    for idx, row in low_n_dishes.iterrows():
        manual_review_queue.append({
            'area': 'dish_mapping',
            'item_id': row['dish_type'],
            'issue_type': 'low_sample_size',
            'severity': 'MED',
            'recommended_action': f"Review confidence of kids_happy metric (n={int(row['kids_full_and_happy_n'])})",
            'owner': 'Francesca',
            'notes': row['research_notes'][:100] if pd.notna(row['research_notes']) else ''
        })
    
    if len(low_n_dishes) > 0:
        results.append({
            'check': 'C2. Low sample size dishes flagged',
            'status': 'INFO',
            'severity': 'MED',
            'details': f"{len(low_n_dishes)} dishes have n<20 (flagged for manual review)"
        })
    else:
        results.append({
            'check': 'C2. Low sample size dishes flagged',
            'status': 'PASS',
            'severity': '-',
            'details': 'All dishes have adequate sample sizes'
        })
    
    # ========================================
    # D. VALIDATION RUBRIC CONFORMANCE
    # ========================================
    print("Checking D. Validation rubric conformance...")
    
    # Check Query dishes have MED/HIGH confidence
    query_dishes = df[df['validation_status'] == '⚠️ Query']
    low_conf_queries = query_dishes[~query_dishes['validation_confidence'].isin(['HIGH', 'MED'])]
    
    if len(low_conf_queries) > 0:
        for idx, row in low_conf_queries.iterrows():
            manual_review_queue.append({
                'area': 'validation_rubric',
                'item_id': row['dish_type'],
                'issue_type': 'query_low_confidence',
                'severity': 'HIGH',
                'recommended_action': 'Reconsider Query status given LOW confidence',
                'owner': 'Francesca',
                'notes': f"Confidence: {row['validation_confidence']}"
            })
        results.append({
            'check': 'D1. Query dishes have MED/HIGH confidence',
            'status': 'WARN',
            'severity': 'MED',
            'details': f"{len(low_conf_queries)} Query dishes have LOW confidence"
        })
    else:
        results.append({
            'check': 'D1. Query dishes have MED/HIGH confidence',
            'status': 'PASS',
            'severity': '-',
            'details': 'All Query dishes have MED/HIGH confidence'
        })
    
    # Check all dishes have research_notes
    missing_notes = df['research_notes'].isna().sum()
    if missing_notes > 0:
        results.append({
            'check': 'D2. All dishes have research_notes',
            'status': 'WARN',
            'severity': 'LOW',
            'details': f"{missing_notes} dishes missing research notes"
        })
    else:
        results.append({
            'check': 'D2. All dishes have research_notes',
            'status': 'PASS',
            'severity': '-',
            'details': 'All dishes have research notes'
        })
    
    # ========================================
    # E. NOT-ON-DINNEROO HANDLING
    # ========================================
    print("Checking E. Not-on-Dinneroo handling...")
    
    not_dinneroo = df[df['on_dinneroo'] == False]
    has_kids_metrics = not_dinneroo[not_dinneroo['kids_full_and_happy_pct'].notna()]
    
    if len(has_kids_metrics) > 0:
        results.append({
            'check': 'E1. Not-on-Dinneroo dishes have N/A kids metrics',
            'status': 'FAIL',
            'severity': 'HIGH',
            'details': f"{len(has_kids_metrics)} not-on-Dinneroo dishes incorrectly have kids metrics"
        })
    else:
        results.append({
            'check': 'E1. Not-on-Dinneroo dishes have N/A kids metrics',
            'status': 'PASS',
            'severity': '-',
            'details': 'All not-on-Dinneroo dishes correctly have N/A kids metrics'
        })
    
    return results, manual_review_queue

def generate_qc_report(results, manual_review_queue):
    """Generate the QC_REPORT.md file."""
    
    # Count by status
    high_fail = sum(1 for r in results if r['status'] == 'FAIL' and r['severity'] == 'HIGH')
    med_issues = sum(1 for r in results if r['severity'] == 'MED')
    low_issues = sum(1 for r in results if r['severity'] == 'LOW')
    
    # Determine overall status
    if high_fail > 0:
        overall_status = "🛑 STOP - HIGH severity issues found"
        go_decision = "DO NOT PROCEED"
    elif len(manual_review_queue) > 0:
        overall_status = "⏸️ HOLD - Manual review required"
        go_decision = "REVIEW QUEUE BEFORE PROCEEDING"
    else:
        overall_status = "✅ GO - All checks passed"
        go_decision = "PROCEED TO FINAL OUTPUT"
    
    # Build report
    report = f"""# QC Report - Dish Validation

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Overall Status**: {overall_status}
**Decision**: {go_decision}

## Summary

| Severity | Count |
|----------|-------|
| HIGH     | {high_fail} |
| MED      | {med_issues} |
| LOW      | {low_issues} |

## Check Results

| Check | Status | Severity | Details |
|-------|--------|----------|---------|
"""
    
    for r in results:
        emoji = "✅" if r['status'] == 'PASS' else ("❌" if r['status'] == 'FAIL' else "⚠️")
        report += f"| {r['check']} | {emoji} {r['status']} | {r['severity']} | {r['details']} |\n"
    
    report += f"""

## Manual Review Queue

{len(manual_review_queue)} items require manual review before final output.

See `MANUAL_REVIEW_QUEUE.csv` for details.

## Files Checked

| File | Path |
|------|------|
| Working data | DATA/3_ANALYSIS/dish_validation_working.csv |
| Mapping QA | DATA/3_ANALYSIS/dish_survey_mapping_qa.csv |
| Row-level audit | DATA/3_ANALYSIS/kids_full_and_happy_row_level.csv |

## Stop/Go Rules

- **STOP**: Any HIGH severity failure exists → Fix before proceeding
- **HOLD**: Only MED/LOW issues exist → Present QC report + manual review queue; require signoff
- **GO**: QC passes with no HIGH issues and manual review resolved

---

*Report generated by QC Gate script*
"""
    
    # Save report
    report_path = DELIVERABLES_DIR / "QC_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Saved QC report to: {report_path}")
    
    # Save manual review queue
    if manual_review_queue:
        queue_df = pd.DataFrame(manual_review_queue)
        queue_path = DELIVERABLES_DIR / "MANUAL_REVIEW_QUEUE.csv"
        queue_df.to_csv(queue_path, index=False)
        print(f"Saved manual review queue to: {queue_path}")
    
    return overall_status

def main():
    """Main execution."""
    print("=" * 60)
    print("QUALITY GATE - QC CHECK")
    print("=" * 60)
    
    results, manual_review_queue = run_qc_checks()
    
    print("\n" + "=" * 60)
    print("GENERATING QC REPORT")
    print("=" * 60)
    
    overall_status = generate_qc_report(results, manual_review_queue)
    
    print("\n" + "=" * 60)
    print(f"OVERALL STATUS: {overall_status}")
    print("=" * 60)
    
    if manual_review_queue:
        print(f"\n⚠️  {len(manual_review_queue)} items in manual review queue")
    
    return results, manual_review_queue

if __name__ == "__main__":
    main()
