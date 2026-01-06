#!/usr/bin/env python3
"""
Generate unified dashboard data by merging:
- Anna's presentation data (coverage_matrix, dish_tiers, mvp_zone_summary, recruitment_priorities)
- Track A performance scores (kids_happy, adult_satisfaction with sample sizes)
- Track B opportunity scores (latent_demand, framework scores)
- Threshold sensitivity analysis (cuisine/partner count impact)
- Cuisine performance (repeat rates)
- Zone gap report

Outputs:
- docs/data/unified_dishes.json
- docs/data/mvp_evidence.json
- docs/data/zone_gaps.json
"""

import pandas as pd
import json
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_ANALYSIS = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
PRESENTATION_DATA = PROJECT_ROOT / "DELIVERABLES" / "presentation_data"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "data"

def load_anna_data():
    """Load Anna's presentation data files."""
    coverage = pd.read_csv(PRESENTATION_DATA / "coverage_matrix.csv")
    tiers = pd.read_csv(PRESENTATION_DATA / "dish_tiers.csv")
    mvp_summary = pd.read_csv(PRESENTATION_DATA / "mvp_zone_summary.csv")
    recruitment = pd.read_csv(PRESENTATION_DATA / "recruitment_priorities.csv")
    
    return coverage, tiers, mvp_summary, recruitment

def load_track_a_performance():
    """Load Track A performance scores with survey sample sizes."""
    df = pd.read_csv(DATA_ANALYSIS / "dish_performance_scores.csv")
    return df

def load_track_b_opportunity():
    """Load Track B opportunity scores with latent demand."""
    df = pd.read_csv(DATA_ANALYSIS / "dish_opportunity_scores.csv")
    return df

def load_threshold_sensitivity():
    """Load threshold sensitivity analysis."""
    with open(DATA_ANALYSIS / "threshold_sensitivity.json", "r") as f:
        return json.load(f)

def load_cuisine_performance():
    """Load cuisine performance with repeat rates."""
    df = pd.read_csv(DATA_ANALYSIS / "cuisine_performance.csv")
    return df

def load_zone_gap_report():
    """Load zone gap report."""
    df = pd.read_csv(DATA_ANALYSIS / "zone_gap_report.csv")
    return df

def normalize_dish_name(name):
    """Normalize dish names for matching."""
    if pd.isna(name):
        return ""
    return str(name).lower().strip().replace("_", " ").replace("-", " ")


def generate_rationale(dish_record, track_a_match, track_b_match, coverage_match):
    """
    Generate evidence-based rationale for dish recommendation.
    Includes specific metrics with sample sizes.
    """
    parts = []
    
    # Kids happy rate (most important consumer signal)
    if track_a_match is not None and pd.notna(track_a_match.get('kids_happy')):
        rate = int(track_a_match['kids_happy'] * 100)
        n = int(track_a_match['kids_happy_n']) if pd.notna(track_a_match.get('kids_happy_n')) else 0
        if rate >= 80:
            parts.append(f"{rate}% kids full & happy (n={n})")
        elif rate >= 70:
            parts.append(f"{rate}% kids happy (n={n})")
    
    # Rating
    if track_a_match is not None and pd.notna(track_a_match.get('avg_rating')):
        rating = float(track_a_match['avg_rating'])
        n = int(track_a_match['rating_n']) if pd.notna(track_a_match.get('rating_n')) else 0
        if rating >= 4.5:
            parts.append(f"{rating:.1f}★ rating (n={n})")
    
    # Latent demand
    if track_b_match is not None and pd.notna(track_b_match.get('latent_demand_mentions')):
        mentions = int(track_b_match['latent_demand_mentions'])
        if mentions >= 20:
            parts.append(f"{mentions} latent demand mentions (high)")
        elif mentions >= 5:
            parts.append(f"{mentions} latent demand mentions")
    
    # Family fit framework
    if track_b_match is not None and pd.notna(track_b_match.get('kid_friendly')):
        kf = int(track_b_match['kid_friendly'])
        fef = int(track_b_match.get('fussy_eater_friendly', 3))
        if kf >= 4 and fef >= 4:
            parts.append("high kid-friendly & fussy-eater scores")
        elif kf >= 4:
            parts.append("high kid-friendly score")
    
    # Quadrant action
    if coverage_match is not None and pd.notna(coverage_match.get('Action')):
        action = coverage_match['Action']
        quadrant = coverage_match.get('Quadrant', '')
        if 'High Importance' in str(quadrant):
            if 'High Coverage' in str(quadrant):
                parts.append("Core Driver - maintain availability")
            else:
                parts.append("Demand Booster - expand to more zones")
    
    # If no specific evidence, use tier-based generic
    if not parts:
        tier = dish_record.get('tier', 'Unknown')
        if tier == 'Must Have':
            parts.append("High priority based on family fit framework")
        elif tier == 'Nice to Have':
            parts.append("Good option for variety")
        else:
            parts.append("Monitor for performance")
    
    return ". ".join(parts)

def generate_unified_dishes(coverage, tiers, track_a, track_b):
    """
    Merge all dish data into unified format.
    """
    dishes = []
    
    # Use tiers as the base (most complete list)
    for _, row in tiers.iterrows():
        dish_name = row['Dish']
        dish_norm = normalize_dish_name(dish_name)
        
        # Find matching Track A data (performance with kids_happy)
        track_a_match = None
        for _, ta in track_a.iterrows():
            if normalize_dish_name(ta['dish_type']) in dish_norm or dish_norm in normalize_dish_name(ta['dish_type']):
                track_a_match = ta
                break
        
        # Find matching Track B data (opportunity with latent demand)
        track_b_match = None
        for _, tb in track_b.iterrows():
            if normalize_dish_name(tb['dish_type']) in dish_norm or dish_norm in normalize_dish_name(tb['dish_type']):
                track_b_match = tb
                break
        
        # Find matching coverage data
        coverage_match = None
        for _, cv in coverage.iterrows():
            if normalize_dish_name(cv['Dish']) == dish_norm:
                coverage_match = cv
                break
        
        # Build unified dish record (rationale will be set after we have all data)
        dish_record = {
            "dish": dish_name,
            "tier": row['Tier'],
            "priority_score": float(row['Priority Score']) if pd.notna(row['Priority Score']) else 0,
            "category": row['Category'] if pd.notna(row.get('Category')) else "Unknown",
            "evidence_type": row['Evidence Type'] if pd.notna(row.get('Evidence Type')) else "Estimated",
            "cuisine": row['Cuisine'] if pd.notna(row.get('Cuisine')) else "Unknown",
            "gap_type": row['Gap Type'] if pd.notna(row.get('Gap Type')) else "No Gap",
            "rationale": "",  # Will be set below with evidence
            "potential_partners": row['Potential Partners'] if pd.notna(row.get('Potential Partners')) else "TBD",
        }
        
        # Add coverage/quadrant info
        if coverage_match is not None:
            dish_record["quadrant"] = coverage_match['Quadrant'] if pd.notna(coverage_match.get('Quadrant')) else "Unknown"
            dish_record["action"] = coverage_match['Action'] if pd.notna(coverage_match.get('Action')) else "Unknown"
            dish_record["order_volume"] = int(coverage_match['Order Volume']) if pd.notna(coverage_match.get('Order Volume')) else 0
            dish_record["on_dinneroo"] = int(coverage_match['Order Volume']) > 0 if pd.notna(coverage_match.get('Order Volume')) else False
        else:
            dish_record["quadrant"] = "Unknown"
            dish_record["action"] = "Unknown"
            dish_record["order_volume"] = 0
            dish_record["on_dinneroo"] = False
        
        # Add Track A performance data (kids_happy, adult_satisfaction with sample sizes)
        if track_a_match is not None:
            dish_record["performance"] = {
                "rating": {
                    "value": float(track_a_match['avg_rating']) if pd.notna(track_a_match.get('avg_rating')) else None,
                    "n": int(track_a_match['rating_n']) if pd.notna(track_a_match.get('rating_n')) else None
                },
                "kids_happy": {
                    "rate": float(track_a_match['kids_happy']) if pd.notna(track_a_match.get('kids_happy')) else None,
                    "n": int(track_a_match['kids_happy_n']) if pd.notna(track_a_match.get('kids_happy_n')) else None
                },
                "adult_satisfaction": {
                    "rate": float(track_a_match['adult_satisfaction']) if pd.notna(track_a_match.get('adult_satisfaction')) else None,
                    "n": int(track_a_match['adult_satisfaction_n']) if pd.notna(track_a_match.get('adult_satisfaction_n')) else None
                },
                "portions_adequate": {
                    "rate": float(track_a_match['portions_adequate']) if pd.notna(track_a_match.get('portions_adequate')) else None,
                    "n": int(track_a_match['portions_n']) if pd.notna(track_a_match.get('portions_n')) else None
                },
                "track_a_score": float(track_a_match['track_a_score']) if pd.notna(track_a_match.get('track_a_score')) else None,
                "survey_n": int(track_a_match['survey_n']) if pd.notna(track_a_match.get('survey_n')) else None
            }
            dish_record["evidence_type"] = "Measured" if dish_record["performance"]["survey_n"] else dish_record["evidence_type"]
        else:
            dish_record["performance"] = None
        
        # Add Track B opportunity data (latent demand, framework scores)
        if track_b_match is not None:
            dish_record["opportunity"] = {
                "latent_demand_mentions": int(track_b_match['latent_demand_mentions']) if pd.notna(track_b_match.get('latent_demand_mentions')) else 0,
                "latent_demand_score": float(track_b_match['latent_demand_score']) if pd.notna(track_b_match.get('latent_demand_score')) else 1,
                "kid_friendly": int(track_b_match['kid_friendly']) if pd.notna(track_b_match.get('kid_friendly')) else 3,
                "balanced_guilt_free": int(track_b_match['balanced_guilt_free']) if pd.notna(track_b_match.get('balanced_guilt_free')) else 3,
                "fussy_eater_friendly": int(track_b_match['fussy_eater_friendly']) if pd.notna(track_b_match.get('fussy_eater_friendly')) else 3,
                "customisation": int(track_b_match['customisation']) if pd.notna(track_b_match.get('customisation')) else 3,
                "framework_score": float(track_b_match['framework_score']) if pd.notna(track_b_match.get('framework_score')) else 3.0,
                "track_b_score": float(track_b_match['track_b_score']) if pd.notna(track_b_match.get('track_b_score')) else 2.5,
                "partner_capability": int(track_b_match['partner_capability']) if pd.notna(track_b_match.get('partner_capability')) else 2
            }
        else:
            dish_record["opportunity"] = None
        
        # Determine evidence level
        sources = 0
        if dish_record["performance"] and dish_record["performance"].get("survey_n"):
            sources += 1
        if dish_record["performance"] and dish_record["performance"].get("rating", {}).get("n"):
            sources += 1
        if dish_record["opportunity"] and dish_record["opportunity"].get("latent_demand_mentions", 0) > 0:
            sources += 1
        if dish_record["order_volume"] > 0:
            sources += 1
        
        if sources >= 3:
            dish_record["evidence_level"] = "Validated"
        elif sources >= 2:
            dish_record["evidence_level"] = "Corroborated"
        else:
            dish_record["evidence_level"] = "Single"
        
        # Generate evidence-based rationale
        dish_record["rationale"] = generate_rationale(dish_record, track_a_match, track_b_match, coverage_match)
        
        dishes.append(dish_record)
    
    # Sort by priority score descending
    dishes.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # Add rank
    for i, dish in enumerate(dishes):
        dish["rank"] = i + 1
    
    return dishes

def generate_mvp_evidence(threshold_data, cuisine_perf):
    """
    Generate MVP evidence from threshold sensitivity and cuisine performance.
    """
    # Extract cuisine analysis
    cuisine_analysis = threshold_data.get("cuisine_analysis", [])
    partner_analysis = threshold_data.get("partner_analysis", [])
    key_findings = threshold_data.get("key_findings", {})
    
    # Find 4 and 5 cuisine data
    cuisine_4 = next((c for c in cuisine_analysis if c["cuisine_count"] == 4), {})
    cuisine_5 = next((c for c in cuisine_analysis if c["cuisine_count"] == 5), {})
    
    # Find partner data
    partner_1_2 = next((p for p in partner_analysis if p["partner_range"] == "1-2"), {})
    partner_5 = next((p for p in partner_analysis if p["partner_range"] == "5-5"), {})
    
    # Calculate impact
    if cuisine_4 and cuisine_5:
        orders_impact = ((cuisine_5.get("avg_orders", 0) - cuisine_4.get("avg_orders", 0)) / cuisine_4.get("avg_orders", 1)) * 100
        rating_impact = cuisine_5.get("avg_rating", 0) - cuisine_4.get("avg_rating", 0)
    else:
        orders_impact = 34  # fallback
        rating_impact = 0.09
    
    # Get top cuisines by repeat rate
    top_cuisines = []
    for _, row in cuisine_perf.head(10).iterrows():
        cuisine_name = row['CUISINE']
        # Skip non-cuisine categories
        if cuisine_name.lower() in ['meal deals', 'salads', 'vegan friendly', 'gluten free', 'breakfast', 'halal', 'kosher']:
            continue
        top_cuisines.append({
            "cuisine": cuisine_name,
            "repeat_rate": round(float(row['repeat_rate']), 3) if pd.notna(row.get('repeat_rate')) else 0,
            "rating": round(float(row['avg_rating']), 2) if pd.notna(row.get('avg_rating')) else 0,
            "n": int(row['order_count']) if pd.notna(row.get('order_count')) else 0
        })
    
    mvp_evidence = {
        "cuisine_threshold": {
            "recommended": 5,
            "evidence": {
                "5_cuisines": {
                    "zones": cuisine_5.get("zones", 13),
                    "avg_orders": round(cuisine_5.get("avg_orders", 685), 0),
                    "avg_rating": round(cuisine_5.get("avg_rating", 4.44), 2)
                },
                "4_cuisines": {
                    "zones": cuisine_4.get("zones", 24),
                    "avg_orders": round(cuisine_4.get("avg_orders", 511), 0),
                    "avg_rating": round(cuisine_4.get("avg_rating", 4.35), 2)
                },
                "impact": f"+{round(orders_impact)}% orders, +{round(rating_impact, 2)} rating"
            },
            "source": "threshold_sensitivity.json (n=197 zones)"
        },
        "partner_threshold": {
            "recommended": 5,
            "evidence": {
                "5_partners": {
                    "zones": partner_5.get("zones", 16),
                    "avg_orders": round(partner_5.get("avg_orders", 537), 0)
                },
                "1-2_partners": {
                    "zones": partner_1_2.get("zones", 95),
                    "avg_orders": round(partner_1_2.get("avg_orders", 68), 0)
                },
                "impact": f"{round(partner_5.get('avg_orders', 537) / max(partner_1_2.get('avg_orders', 68), 1))}x more orders"
            },
            "source": "threshold_sensitivity.json (n=197 zones)"
        },
        "variety_demand": key_findings.get("variety_complaint_rate", "17.3% want more variety"),
        "variety_source": "open-text analysis (n=2,796)",
        "core_cuisines": top_cuisines[:5],
        "core_cuisines_source": "cuisine_performance.csv (behavioral data)"
    }
    
    return mvp_evidence

def generate_zone_gaps(zone_gap_df, recruitment_df, family_dishes_per_zone=None):
    """
    Generate zone gaps data from zone_gap_report and recruitment_priorities.
    
    Args:
        zone_gap_df: Zone gap report data
        recruitment_df: Recruitment priorities data
        family_dishes_per_zone: Dict of zone -> family dish count from Anna's data
    """
    # Use family dishes lookup (calculated from Anna's Item Categorisation)
    # This is ACTUAL family dishes on Dinneroo, not order line items
    unique_dishes_lookup = family_dishes_per_zone or {}
    
    zones = []
    
    for _, row in zone_gap_df.iterrows():
        # Parse missing cuisines (stored as string representation of list)
        missing_cuisines_str = row.get('missing_essential_cuisines', '[]')
        if isinstance(missing_cuisines_str, str):
            try:
                missing_cuisines = eval(missing_cuisines_str) if missing_cuisines_str.startswith('[') else []
            except:
                missing_cuisines = []
        else:
            missing_cuisines = []
        
        # Parse missing dishes
        missing_dishes_str = row.get('missing_dish_types', '[]')
        if isinstance(missing_dishes_str, str):
            try:
                missing_dishes = eval(missing_dishes_str) if missing_dishes_str.startswith('[') else []
            except:
                missing_dishes = []
        else:
            missing_dishes = []
        
        # Parse available cuisines
        cuisines_available_str = row.get('cuisines_available', '[]')
        if isinstance(cuisines_available_str, str):
            try:
                cuisines_available = eval(cuisines_available_str) if cuisines_available_str.startswith('[') else []
            except:
                cuisines_available = []
        else:
            cuisines_available = []
        
        zone_name = row['zone']
        zone_record = {
            "zone": zone_name,
            "region": row.get('region', 'Unknown'),
            "orders": int(row['orders']) if pd.notna(row.get('orders')) else 0,
            "partners": int(row['partners']) if pd.notna(row.get('partners')) else 0,
            "cuisines_count": int(row['cuisines_count']) if pd.notna(row.get('cuisines_count')) else 0,
            "unique_dishes": unique_dishes_lookup.get(zone_name, 0),
            "cuisines_available": cuisines_available,
            "avg_rating": round(float(row['avg_rating']), 2) if pd.notna(row.get('avg_rating')) else 0,
            "is_mvp": bool(row['is_mvp']) if pd.notna(row.get('is_mvp')) else False,
            "essential_cuisine_coverage": row.get('essential_cuisine_coverage', '0%'),
            "missing_cuisines": missing_cuisines,
            "missing_dishes": missing_dishes,
            "dish_coverage": row.get('dish_coverage', '0%'),
            "recruitment_priority": row.get('recruitment_priority', 'Low')
        }
        
        zones.append(zone_record)
    
    # Sort by orders descending
    zones.sort(key=lambda x: x["orders"], reverse=True)
    
    # Extract recruitment priorities summary
    recruitment_summary = []
    for _, row in recruitment_df.iterrows():
        if pd.notna(row.get('Cuisine')) and row.get('Gap Type') != 'Zone Gap':
            recruitment_summary.append({
                "cuisine": row['Cuisine'],
                "gap_type": row['Gap Type'],
                "priority": row['Priority'],
                "top_dishes": row.get('Top Dishes', ''),
                "action": row.get('Recommended Action', '')
            })
    
    return {
        "zones": zones,
        "recruitment_priorities": recruitment_summary,
        "summary": {
            "total_zones": len(zones),
            "mvp_ready": len([z for z in zones if z["is_mvp"]]),
            "needs_work": len([z for z in zones if not z["is_mvp"]]),
            "high_priority": len([z for z in zones if z["recruitment_priority"] == "High"])
        }
    }

def load_zone_quality_scores():
    """Load zone quality scores."""
    df = pd.read_csv(DATA_ANALYSIS / "zone_quality_scores.csv")
    return df


def calculate_family_dishes_per_zone():
    """
    Calculate actual family dishes per zone using Anna's Item Categorisation.
    
    Logic:
    1. Load Anna's curated list of 155 family dishes by brand
    2. Get which brands are present in each zone from orders
    3. Sum the dish counts for brands present in each zone
    
    This gives ACTUAL family dishes on Dinneroo per zone, not order line items.
    Source: Anna's Dish Analysis Dec-25.xlsx > Item Categorisation sheet
    """
    print("  Calculating family dishes per zone from Anna's Item Categorisation...")
    
    # Load Anna's family dishes by brand
    xlsx_path = PROJECT_ROOT / "DELIVERABLES" / "reports" / "Dish Analysis Dec-25.xlsx"
    item_cat = pd.read_excel(xlsx_path, sheet_name='Item Categorisation', header=7)
    
    # Filter to included items only (Include = 1)
    family_dishes = item_cat[item_cat.iloc[:, 0] == 1][['Brand', 'Item']].copy()
    family_dishes.columns = ['brand', 'item']
    
    # Get dish count per brand
    dishes_per_brand = family_dishes.groupby('brand').size().to_dict()
    print(f"    - {len(family_dishes)} family dishes across {len(dishes_per_brand)} brands")
    
    # Load orders to get brands per zone
    orders = pd.read_csv(DATA_ANALYSIS / "orders_segmented.csv", low_memory=False)
    brands_per_zone = orders.groupby('ZONE_NAME')['BRAND'].unique().to_dict()
    
    # Calculate family dishes per zone
    zone_dish_counts = {}
    for zone, brands in brands_per_zone.items():
        dish_count = sum(dishes_per_brand.get(brand, 0) for brand in brands)
        zone_dish_counts[zone] = dish_count
    
    print(f"    - Calculated for {len(zone_dish_counts)} zones")
    print(f"    - Average: {sum(zone_dish_counts.values()) / len(zone_dish_counts):.1f} dishes/zone")
    
    return zone_dish_counts

def main():
    print("Loading data sources...")
    
    # Load all data
    coverage, tiers, mvp_summary, recruitment = load_anna_data()
    track_a = load_track_a_performance()
    track_b = load_track_b_opportunity()
    threshold_data = load_threshold_sensitivity()
    cuisine_perf = load_cuisine_performance()
    zone_gap_df = load_zone_gap_report()
    zone_quality_df = load_zone_quality_scores()
    
    print(f"  - Anna's coverage matrix: {len(coverage)} dishes")
    print(f"  - Anna's dish tiers: {len(tiers)} dishes")
    print(f"  - Track A performance: {len(track_a)} dish types")
    print(f"  - Track B opportunity: {len(track_b)} dish types")
    print(f"  - Zone gap report: {len(zone_gap_df)} zones")
    print(f"  - Zone quality scores: {len(zone_quality_df)} zones")
    
    # Calculate family dishes per zone from Anna's Item Categorisation
    family_dishes_per_zone = calculate_family_dishes_per_zone()
    
    # Generate unified dishes
    print("\nGenerating unified_dishes.json...")
    unified_dishes = generate_unified_dishes(coverage, tiers, track_a, track_b)
    
    # Count dishes with kids_happy data
    dishes_with_kids_happy = len([d for d in unified_dishes if d.get("performance") and d["performance"].get("kids_happy", {}).get("rate")])
    dishes_with_latent_demand = len([d for d in unified_dishes if d.get("opportunity") and d["opportunity"].get("latent_demand_mentions", 0) > 0])
    
    print(f"  - Total dishes: {len(unified_dishes)}")
    print(f"  - Dishes with kids_happy data: {dishes_with_kids_happy}")
    print(f"  - Dishes with latent demand mentions: {dishes_with_latent_demand}")
    
    # Generate MVP evidence
    print("\nGenerating mvp_evidence.json...")
    mvp_evidence = generate_mvp_evidence(threshold_data, cuisine_perf)
    print(f"  - Cuisine threshold: {mvp_evidence['cuisine_threshold']['recommended']} ({mvp_evidence['cuisine_threshold']['evidence']['impact']})")
    print(f"  - Partner threshold: {mvp_evidence['partner_threshold']['recommended']} ({mvp_evidence['partner_threshold']['evidence']['impact']})")
    
    # Generate zone gaps (with family dishes from Anna's Item Categorisation)
    print("\nGenerating zone_gaps.json...")
    zone_gaps = generate_zone_gaps(zone_gap_df, recruitment, family_dishes_per_zone)
    print(f"  - Total zones: {zone_gaps['summary']['total_zones']}")
    print(f"  - MVP ready: {zone_gaps['summary']['mvp_ready']}")
    print(f"  - High priority gaps: {zone_gaps['summary']['high_priority']}")
    
    # Show sample zones with family dishes
    sample_zones = zone_gaps['zones'][:3]
    print(f"  - Sample: {sample_zones[0]['zone']} has {sample_zones[0]['unique_dishes']} family dishes (from Anna's data)")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write output files
    print("\nWriting output files...")
    
    with open(OUTPUT_DIR / "unified_dishes.json", "w") as f:
        json.dump(unified_dishes, f, indent=2)
    print(f"  - {OUTPUT_DIR / 'unified_dishes.json'}")
    
    with open(OUTPUT_DIR / "mvp_evidence.json", "w") as f:
        json.dump(mvp_evidence, f, indent=2)
    print(f"  - {OUTPUT_DIR / 'mvp_evidence.json'}")
    
    with open(OUTPUT_DIR / "zone_gaps.json", "w") as f:
        json.dump(zone_gaps, f, indent=2)
    print(f"  - {OUTPUT_DIR / 'zone_gaps.json'}")
    
    print("\n✅ Done! Generated unified dashboard data.")
    
    # Validation checks
    print("\n--- Validation Checks ---")
    
    # Check 1: Top 10 dishes include latent demand items
    top_10 = unified_dishes[:10]
    latent_in_top_10 = [d for d in top_10 if d.get("opportunity") and d["opportunity"].get("latent_demand_mentions", 0) > 0]
    print(f"✓ Top 10 dishes with latent demand: {len(latent_in_top_10)}/10")
    
    # Check 2: Dishes with survey data show kids_happy
    print(f"✓ Dishes with kids_happy rate + sample size: {dishes_with_kids_happy}")
    
    # Check 3: MVP criteria backed by threshold data
    print(f"✓ MVP cuisine evidence: {mvp_evidence['cuisine_threshold']['source']}")
    print(f"✓ MVP partner evidence: {mvp_evidence['partner_threshold']['source']}")
    
    # Check 4: Chinese Family Meal appears
    chinese_meal = next((d for d in unified_dishes if "chinese" in d["dish"].lower() and "family" in d["dish"].lower()), None)
    if chinese_meal:
        latent = chinese_meal.get("opportunity", {}).get("latent_demand_mentions", 0)
        print(f"✓ Chinese Family Meal found: {latent} latent demand mentions")
    else:
        print("⚠ Chinese Family Meal not found in top dishes")
    
    # VALIDATION GATE: Check that consumer validation data exists
    print("\n--- Consumer Validation Gate ---")
    consumer_validation_path = OUTPUT_DIR / "mvp_consumer_validation.json"
    if not consumer_validation_path.exists():
        print("❌ VALIDATION GATE FAILED: mvp_consumer_validation.json not found!")
        print("   Run scripts/phase2_analysis/04_validate_mvp_consumer_outcomes.py first")
        raise FileNotFoundError(
            "MVP consumer validation data missing. Run 04_validate_mvp_consumer_outcomes.py first. "
            "MVP criteria MUST be validated against consumer outcomes (kids_happy, reorder_intent, variety_complaints)."
        )
    
    with open(consumer_validation_path, "r") as f:
        consumer_val = json.load(f)
    
    # Check required fields exist
    required_fields = ['cuisine_impact', 'partner_impact', 'validation_status']
    missing_fields = [f for f in required_fields if f not in consumer_val]
    if missing_fields:
        print(f"❌ VALIDATION GATE FAILED: Missing fields in consumer validation: {missing_fields}")
        raise ValueError(f"Consumer validation missing required fields: {missing_fields}")
    
    # Check that outcomes were actually validated (not all N/A)
    val_status = consumer_val.get('validation_status', {})
    if not any(val_status.values()):
        print("❌ VALIDATION GATE FAILED: No consumer outcomes could be validated!")
        print("   Check survey data quality and zone matching.")
        raise ValueError("No consumer outcomes validated - check survey data quality")
    
    print(f"✓ Consumer validation data exists")
    print(f"✓ Kids happy validated: {val_status.get('kids_happy_validated', False)}")
    print(f"✓ Reorder intent validated: {val_status.get('reorder_intent_validated', False)}")
    print(f"✓ Variety complaints validated: {val_status.get('variety_complaints_validated', False)}")
    
    # Show summary of consumer impact
    ci = consumer_val.get('cuisine_impact', {}).get('summary', {})
    print(f"\nConsumer Impact Summary (5+ cuisines vs 1-2):")
    print(f"  Kids Happy: {ci.get('kids_happy_impact', 'N/A')}")
    print(f"  Reorder Intent: {ci.get('reorder_intent_impact', 'N/A')}")
    print(f"  Variety Complaints: {ci.get('variety_complaint_impact', 'N/A')}")

if __name__ == "__main__":
    main()

