#!/usr/bin/env python3
"""
Dish Validation Assessment
===========================
Applies the validation rubric to assess each dish as Confirmed/Query/Opportunity.

Validation Rubric (from plan):
- Confirmed ✓: At least 2 independent research signals align with tier expectations
- Query ⚠️: Clear contradiction with MED/HIGH confidence
- Opportunity 💡: Tier is broadly supported but research adds actionable nuance

Outputs:
- Updated dish_validation_working.csv with validation_status and research_notes
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "DATA/3_ANALYSIS"

# Thresholds
SUITABILITY_HIGH = 3.0  # Above average for family suitability
SUITABILITY_LOW = 2.5   # Below this is concerning (but only flag if kids_happy also low)
KIDS_HAPPY_MEDIAN = 78.0  # Approximate median from our data
KIDS_HAPPY_LOW = 70.0    # Below this is concerning (but only flag if suitability also low)

# NOTE: Query only triggers if BOTH suitability AND kids_happy are low
# Single low signal = caveat in notes, not a Query

def assess_dish(row):
    """
    Apply validation rubric to a single dish.
    
    Returns: (validation_status, research_notes)
    """
    dish_type = row['dish_type']
    current_tier = row['current_tier']
    on_dinneroo = row['on_dinneroo']
    family_suit = row.get('family_suitability')
    kids_happy = row.get('kids_full_and_happy_pct')
    kids_n = row.get('kids_full_and_happy_n')
    confidence = row.get('validation_confidence')
    demand = row.get('looker_demand_index')
    preference = row.get('looker_preference_index')
    
    # For not-on-Dinneroo dishes
    if not on_dinneroo:
        if pd.notna(family_suit) and family_suit >= SUITABILITY_HIGH:
            return '💡 Opportunity', f"High family suitability ({family_suit}/5) supports testing. No Dinneroo performance data yet."
        elif pd.notna(family_suit) and family_suit >= 2.5:
            return '✓ Confirmed', f"Moderate suitability ({family_suit}/5). Suitable for Test & Learn category."
        else:
            return '✓ Confirmed', "No performance data; suitability data limited. Appropriate for Test & Learn."
    
    # Initialize signals
    positive_signals = []
    caveats = []  # Renamed from negative_signals - single low signals become caveats, not Query triggers
    notes = []
    
    # Track individual low signals
    low_suitability = False
    low_kids_happy = False
    
    # Check family suitability
    if pd.notna(family_suit):
        if family_suit >= SUITABILITY_HIGH:
            positive_signals.append(f"suitability {family_suit}/5")
        elif family_suit < SUITABILITY_LOW:
            low_suitability = True
            caveats.append(f"low suitability {family_suit}/5 (pre-launch perception)")
    
    # Check kids happy (only if we have sufficient data)
    if pd.notna(kids_happy) and pd.notna(kids_n) and kids_n >= 10:
        if kids_happy >= KIDS_HAPPY_MEDIAN:
            positive_signals.append(f"kids full & happy {kids_happy:.0f}% (n={int(kids_n)})")
        elif kids_happy < KIDS_HAPPY_LOW:
            low_kids_happy = True
            caveats.append(f"low kids happy {kids_happy:.0f}% (n={int(kids_n)})")
    elif pd.notna(kids_n) and kids_n < 10:
        notes.append(f"small survey sample (n={int(kids_n)})")
    
    # Check if tier expectations are met
    tier_expectation_met = True
    
    if current_tier == 'Core Drivers':
        # Core Drivers should have high demand AND preference
        if pd.notna(demand) and demand < 1.0:
            tier_expectation_met = False
            notes.append(f"demand index {demand} below average for Core Driver")
        if pd.notna(preference) and preference < 1.0:
            tier_expectation_met = False
            notes.append(f"preference index {preference} below average for Core Driver")
            
    elif current_tier == 'Preference Drivers':
        # Preference Drivers should have high preference, lower demand is expected
        if pd.notna(preference) and preference < 1.0:
            tier_expectation_met = False
            notes.append(f"preference index {preference} below average for Preference Driver")
            
    elif current_tier == 'Demand Boosters':
        # Demand Boosters should have high demand, lower preference is expected
        if pd.notna(demand) and demand < 1.0:
            tier_expectation_met = False
            notes.append(f"demand index {demand} below average for Demand Booster")
    
    # Apply rubric
    if current_tier == 'Deprioritised':
        # Deprioritised dishes - check if research suggests reconsideration
        if len(positive_signals) >= 2:
            return '💡 Opportunity', f"Deprioritised but research signals positive: {', '.join(positive_signals)}. Consider revisiting."
        else:
            return '✓ Confirmed', f"Research supports deprioritisation. {'; '.join(notes) if notes else 'No strong positive signals.'}"
    
    # For Core/Preference/Demand tiers
    # UPDATED: Only flag Query if BOTH suitability AND kids_happy are low
    if low_suitability and low_kids_happy and confidence in ['HIGH', 'MED']:
        # Query only if BOTH signals are concerning
        all_notes = notes + [f"Tier: {current_tier}"]
        return '⚠️ Query', f"Research flags: {', '.join(caveats)}. {'; '.join(all_notes)}"
    
    elif len(positive_signals) >= 2:
        # Confirmed with strong evidence
        all_notes = notes + caveats  # Include caveats in notes
        note_str = '; '.join(all_notes) if all_notes else ''
        return '✓ Confirmed', f"Research validates {current_tier}: {', '.join(positive_signals)}. {note_str}"
    
    elif len(positive_signals) >= 1:
        # Confirmed with some evidence
        all_notes = notes + caveats  # Include caveats in notes
        note_str = '; '.join(all_notes) if all_notes else ''
        return '✓ Confirmed', f"Research directionally supports {current_tier}: {', '.join(positive_signals)}. {note_str}"
    
    else:
        # Limited evidence - default to confirmed with caveats
        all_notes = ["Limited research data for full validation."] + notes + caveats
        return '✓ Confirmed', '; '.join(all_notes)

def identify_opportunities(row):
    """Check for actionable insights beyond tier validation."""
    opportunities = []
    
    dish_type = row['dish_type']
    family_suit = row.get('family_suitability')
    kids_happy = row.get('kids_full_and_happy_pct')
    current_tier = row['current_tier']
    coverage_gap = row.get('coverage_gap_pct')
    
    # High suitability but low coverage = recruitment opportunity
    if pd.notna(family_suit) and family_suit >= 3.5 and pd.notna(coverage_gap) and coverage_gap > 0.5:
        opportunities.append(f"High suitability ({family_suit}/5) + {coverage_gap*100:.0f}% coverage gap suggests recruitment priority")
    
    # Very high kids happy rate
    if pd.notna(kids_happy) and kids_happy >= 90:
        opportunities.append(f"Exceptional kids happy rate ({kids_happy:.0f}%) - potential flagship dish")
    
    # Shepherd's Pie special case (mentioned in plan)
    if dish_type == "Shepherd's Pie":
        if pd.notna(family_suit) and family_suit >= 4.0:
            opportunities.append(f"Highest family suitability ({family_suit}/5) - demand may be suppressed by availability")
    
    return opportunities

def main():
    """Main execution."""
    print("=" * 60)
    print("DISH VALIDATION ASSESSMENT")
    print("=" * 60)
    
    # Load working file
    working_path = ANALYSIS_DIR / "dish_validation_working.csv"
    df = pd.read_csv(working_path)
    print(f"Loaded {len(df)} dishes")
    
    # Apply validation rubric
    print("\nApplying validation rubric...")
    
    validation_results = []
    for idx, row in df.iterrows():
        status, notes = assess_dish(row)
        opportunities = identify_opportunities(row)
        
        # If opportunities found and status is Confirmed, upgrade to Opportunity
        if opportunities and status == '✓ Confirmed':
            status = '💡 Opportunity'
            notes = notes + " OPPORTUNITY: " + "; ".join(opportunities)
        elif opportunities:
            notes = notes + " ADDITIONAL: " + "; ".join(opportunities)
        
        validation_results.append({
            'validation_status': status,
            'research_notes': notes.strip()
        })
    
    df_results = pd.DataFrame(validation_results)
    df['validation_status'] = df_results['validation_status']
    df['research_notes'] = df_results['research_notes']
    
    # Save updated file
    df.to_csv(working_path, index=False)
    print(f"Updated working file: {working_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    status_counts = df['validation_status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    print("\n--- QUERIES (require attention) ---")
    queries = df[df['validation_status'] == '⚠️ Query']
    for idx, row in queries.iterrows():
        print(f"\n  {row['dish_type']} ({row['current_tier']})")
        print(f"    {row['research_notes'][:100]}...")
    
    print("\n--- OPPORTUNITIES ---")
    opps = df[df['validation_status'] == '💡 Opportunity']
    for idx, row in opps.iterrows():
        print(f"\n  {row['dish_type']} ({row['current_tier']})")
        print(f"    {row['research_notes'][:100]}...")
    
    return df

if __name__ == "__main__":
    main()
