#!/usr/bin/env python3
"""
Prepare Dashboard Data Script

Aggregates all data sources and prepares a unified JSON file for the
Consumer Insight Dashboard.

Output: docs/data/dashboard_data.json

Usage:
    python3 scripts/prepare_dashboard_data.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Output paths
OUTPUT_DIR = PROJECT_ROOT / "docs" / "data"
OUTPUT_FILE = OUTPUT_DIR / "dashboard_data.json"


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if pd.isna(obj):
            return None
        return super().default(obj)


def load_csv_safe(path: Path, comment: str = '#') -> Optional[pd.DataFrame]:
    """Safely load a CSV file, handling errors gracefully."""
    if not path.exists():
        print(f"  ⚠ File not found: {path.name}")
        return None
    try:
        df = pd.read_csv(path, low_memory=False, comment=comment)
        print(f"  ✓ Loaded {path.name}: {len(df):,} rows")
        return df
    except Exception as e:
        print(f"  ✗ Failed to load {path.name}: {e}")
        return None


def load_json_safe(path: Path) -> Optional[Dict]:
    """Safely load a JSON file, handling errors gracefully."""
    if not path.exists():
        print(f"  ⚠ File not found: {path.name}")
        return None
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        print(f"  ✓ Loaded {path.name}")
        return data
    except Exception as e:
        print(f"  ✗ Failed to load {path.name}: {e}")
        return None


def prepare_metadata() -> Dict[str, Any]:
    """Prepare metadata about data sources."""
    return {
        "generated": datetime.now().isoformat(),
        "version": "2.0",
        "sources": {
            "postOrder": {
                "name": "Post-Order Survey",
                "type": "survey",
                "description": "Feedback from customers after placing a Dinneroo order",
                "n": 1599,
                "lastUpdated": "2026-01-06",
                "file": "DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv",
                "strengths": ["Actual customer experience", "Satisfaction data", "Open-text feedback"],
                "limitations": ["Only orderers (survivorship bias)", "May skew to extremes"],
                "useFor": ["Satisfaction by dish/partner", "Customer feedback", "What's working"]
            },
            "dropoff": {
                "name": "Dropoff Survey",
                "type": "survey",
                "description": "Feedback from people who browsed but didn't order",
                "n": 838,
                "lastUpdated": "2026-01-06",
                "file": "DATA/1_SOURCE/surveys/dropoff_LATEST.csv",
                "strengths": ["Unmet demand", "Barriers", "What people wanted but couldn't find"],
                "limitations": ["Self-selection", "Recall may be inaccurate"],
                "useFor": ["Discovering dishes/cuisines people wanted but we don't have"]
            },
            "orders": {
                "name": "Snowflake Orders",
                "type": "behavioral",
                "description": "Actual Dinneroo orders (revealed preference)",
                "n": 82350,
                "lastUpdated": "2026-01-06",
                "file": "DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv",
                "strengths": ["Revealed preference (actual behavior)", "Large sample", "Real transactions"],
                "limitations": ["Only what we offer (can't show unmet demand)", "No 'why' context"],
                "useFor": ["What actually sells", "Zone performance", "Partner performance"]
            },
            "ratings": {
                "name": "Snowflake Ratings",
                "type": "behavioral",
                "description": "Customer ratings and comments",
                "n": 10713,
                "lastUpdated": "2026-01-06",
                "file": "DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv",
                "strengths": ["Quality signal", "Customer sentiment", "Verified orders only"],
                "limitations": ["~13% of orders leave ratings", "May skew to extremes"],
                "useFor": ["Quality assessment", "Partner comparison", "Sentiment analysis"]
            },
            "annaGroundTruth": {
                "name": "Anna's Ground Truth",
                "type": "supply",
                "description": "Authoritative supply data (what we have)",
                "dishes": 155,
                "partners": 40,
                "sites": 756,
                "lastUpdated": "2025-12-01",
                "file": "DATA/1_SOURCE/anna_slides/anna_*.csv",
                "strengths": ["Verified supply counts", "Authoritative source", "Zone-level detail"],
                "limitations": ["Point-in-time snapshot", "May not reflect recent changes"],
                "useFor": ["Supply metrics", "Zone coverage", "Partner counts"]
            },
            "transcripts": {
                "name": "Customer Transcripts",
                "type": "qualitative",
                "description": "88 customer interview transcripts",
                "n": 88,
                "lastUpdated": "2025-12-15",
                "file": "DATA/1_SOURCE/qual_research/transcripts/customer_interviews/",
                "strengths": ["Deep 'why' context", "Verbatim quotes", "Unprompted dish mentions"],
                "limitations": ["Small sample", "Recruited participants"],
                "useFor": ["Discovering dishes mentioned organically", "Understanding family needs"]
            },
            "ogSurvey": {
                "name": "OG Survey",
                "type": "historical",
                "description": "Pre-launch survey (stated preference)",
                "n": 400,
                "lastUpdated": "2025-06-01",
                "file": "DATA/1_SOURCE/historical_surveys/OG_SURVEY.csv",
                "biasWarning": True,
                "warning": "Pre-launch stated preference - validate with behavioral data",
                "strengths": ["Large sample", "Broad dish coverage"],
                "limitations": ["Stated preference only", "Pre-launch (no real experience)", "Hypothetical choices"],
                "useFor": ["Triangulation only - never as sole source"]
            },
            "pulse": {
                "name": "Pulse Survey",
                "type": "survey",
                "description": "Loyalty-focused survey",
                "n": 250,
                "lastUpdated": "2025-11-01",
                "file": "DATA/1_SOURCE/external/Pulse_Survey_Loyalty_Nov2025.csv",
                "strengths": ["Frequency and loyalty context", "Repeat behavior drivers"],
                "limitations": ["Specific focus on loyalty"],
                "useFor": ["Understanding repeat behavior drivers"]
            }
        }
    }


def prepare_data_sources_registry() -> Dict[str, Any]:
    """Prepare comprehensive DATA_SOURCES registry for metric provenance."""
    return {
        # KPI Metrics
        "avgRating": {
            "name": "Average Rating",
            "source": "ratings",
            "sourceFile": "DINNEROO_RATINGS.csv",
            "n": 10713,
            "methodology": "Mean of 1-5 star ratings from verified orders",
            "calculation": "AVG(RATING_STARS) WHERE RATING_STARS IS NOT NULL",
            "benchmark": {"good": 4.2, "average": 3.5, "poor": 3.0},
            "benchmarkSource": "Deliveroo platform average",
            "caveats": ["Only ~13% of orders leave ratings", "May skew to extremes (very happy/unhappy)"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["ratingDistribution", "partnerRating"]
        },
        "totalOrders": {
            "name": "Total Orders",
            "source": "orders",
            "sourceFile": "ALL_DINNEROO_ORDERS.csv",
            "n": 82350,
            "methodology": "Count of all Dinneroo orders in the dataset",
            "calculation": "COUNT(*) FROM ALL_DINNEROO_ORDERS",
            "benchmark": None,
            "caveats": ["Represents orders, not unique customers"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["uniqueCustomers", "ordersPerZone"]
        },
        "surveyResponses": {
            "name": "Survey Responses",
            "source": "postOrder",
            "sourceFile": "POST_ORDER_SURVEY-CONSOLIDATED.csv",
            "n": 1599,
            "methodology": "Count of completed post-order survey responses",
            "calculation": "COUNT(*) FROM POST_ORDER_SURVEY",
            "benchmark": None,
            "caveats": ["Survivorship bias - only completed orders", "Self-selected respondents"],
            "evidenceLevel": "corroborated",
            "relatedMetrics": ["satisfaction", "repeatIntent"]
        },
        "dishesScored": {
            "name": "Dishes Scored",
            "source": "annaGroundTruth",
            "sourceFile": "MASTER_DISH_LIST_WITH_WORKINGS.csv",
            "n": 32,
            "methodology": "Count of dish types in master scoring framework",
            "calculation": "COUNT(DISTINCT dish_type)",
            "benchmark": None,
            "caveats": ["23 on platform, 9 prospects"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["dishRanking", "strategicPriority"]
        },
        "zonesAnalyzed": {
            "name": "Zones Analyzed",
            "source": "ground_truth",
            "sourceFile": "anna_zone_dish_counts.csv",
            "n": 1306,
            "methodology": "All zones from Anna's ground truth supply data",
            "calculation": "COUNT(*) FROM anna_zone_dish_counts",
            "benchmark": None,
            "caveats": ["201 zones have orders", "1,105 zones have no order activity yet"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["mvpZones", "zoneOrders"]
        },
        "mvpZones": {
            "name": "MVP Zones",
            "source": "orders",
            "sourceFile": "zone_gap_report.csv",
            "n": 100,
            "methodology": "Zones meeting MVP criteria: 5+ partners, 5+ cuisines, 20+ dishes",
            "calculation": "COUNT(*) WHERE partners >= 5 AND cuisines >= 5 AND dishes >= 20",
            "benchmark": {"good": 50, "average": 25, "poor": 10},
            "benchmarkSource": "Internal target",
            "caveats": ["MVP criteria may change", "Based on current thresholds"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["zonesAnalyzed", "partnerCount"]
        },
        
        # Dish Metrics
        "avgSalesPerDish": {
            "name": "Avg Sales Per Dish",
            "source": "orders",
            "sourceFile": "ALL_DINNEROO_ORDERS.csv",
            "methodology": "Average order count per dish type across all zones",
            "calculation": "AVG(order_count) GROUP BY dish_type",
            "benchmark": {"good": 100, "average": 50, "poor": 20},
            "benchmarkSource": "Top quartile performers",
            "caveats": ["Varies significantly by zone", "Affected by partner availability"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["pctZonesTop5", "deliverooRating"]
        },
        "deliverooRating": {
            "name": "Dish Rating",
            "source": "ratings",
            "sourceFile": "DINNEROO_RATINGS.csv",
            "methodology": "Mean rating for orders containing this dish type",
            "calculation": "AVG(RATING_STARS) WHERE dish_type = X",
            "benchmark": {"good": 4.5, "average": 4.0, "poor": 3.5},
            "benchmarkSource": "Deliveroo platform average by dish",
            "caveats": ["Sample size varies by dish", "Rating may reflect partner not dish"],
            "evidenceLevel": "corroborated",
            "relatedMetrics": ["mealSatisfaction", "repeatIntent"]
        },
        "mealSatisfaction": {
            "name": "Meal Satisfaction",
            "source": "postOrder",
            "sourceFile": "POST_ORDER_SURVEY-CONSOLIDATED.csv",
            "methodology": "% of respondents satisfied or very satisfied with meal",
            "calculation": "(COUNT(satisfaction IN ('Satisfied', 'Very Satisfied')) / COUNT(*)) * 100",
            "benchmark": {"good": 85, "average": 70, "poor": 60},
            "benchmarkSource": "Industry standard",
            "caveats": ["Self-reported", "Survivorship bias"],
            "evidenceLevel": "corroborated",
            "relatedMetrics": ["deliverooRating", "repeatIntent"]
        },
        "repeatIntent": {
            "name": "Repeat Intent",
            "source": "postOrder",
            "sourceFile": "POST_ORDER_SURVEY-CONSOLIDATED.csv",
            "methodology": "% of respondents who would order again",
            "calculation": "(COUNT(reorder_intent IN ('Agree', 'Strongly Agree')) / COUNT(*)) * 100",
            "benchmark": {"good": 80, "average": 65, "poor": 50},
            "benchmarkSource": "Industry standard",
            "caveats": ["Stated intent vs actual behavior", "May overstate"],
            "evidenceLevel": "single",
            "relatedMetrics": ["mealSatisfaction", "deliverooRating"]
        },
        "dishSuitability": {
            "name": "Dish Suitability",
            "source": "ogSurvey",
            "sourceFile": "OG_SURVEY.csv",
            "methodology": "1-5 scale rating of dish suitability for family meals",
            "calculation": "AVG(suitability_score) WHERE dish_type = X",
            "benchmark": {"good": 4.0, "average": 3.0, "poor": 2.0},
            "benchmarkSource": "Survey scale midpoint",
            "caveats": ["Stated preference only", "Pre-launch data - validate with behavioral"],
            "evidenceLevel": "single",
            "biasWarning": True,
            "relatedMetrics": ["openTextRequests", "wishlistPct"]
        },
        "openTextRequests": {
            "name": "Open-Text Requests",
            "source": "postOrder",
            "sourceFile": "POST_ORDER_SURVEY-CONSOLIDATED.csv",
            "methodology": "Count of unprompted mentions in open-text fields",
            "calculation": "COUNT(*) WHERE open_text CONTAINS dish_type",
            "benchmark": {"good": 20, "average": 10, "poor": 5},
            "benchmarkSource": "Relative to other dishes",
            "caveats": ["Manual/LLM extraction", "May miss variations in spelling"],
            "evidenceLevel": "corroborated",
            "relatedMetrics": ["wishlistPct", "demandStrength"]
        },
        "wishlistPct": {
            "name": "Wishlist %",
            "source": "ogSurvey",
            "sourceFile": "OG_SURVEY.csv",
            "methodology": "% of respondents who added dish to wishlist",
            "calculation": "(COUNT(wishlist CONTAINS dish_type) / COUNT(*)) * 100",
            "benchmark": {"good": 10, "average": 5, "poor": 2},
            "benchmarkSource": "Survey response distribution",
            "caveats": ["Stated preference only", "Pre-launch data"],
            "evidenceLevel": "single",
            "biasWarning": True,
            "relatedMetrics": ["openTextRequests", "dishSuitability"]
        },
        "demandStrength": {
            "name": "Demand Strength",
            "source": "orders",
            "sourceFile": "ALL_DINNEROO_ORDERS.csv",
            "methodology": "Composite score based on order volume and growth",
            "calculation": "Normalized score combining order count and trend",
            "benchmark": {"good": 3.0, "average": 2.0, "poor": 1.0},
            "benchmarkSource": "Distribution quartiles",
            "caveats": ["Only measures existing demand", "Cannot capture unmet demand"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["avgSalesPerDish", "consumerPreference"]
        },
        "consumerPreference": {
            "name": "Consumer Preference",
            "source": "postOrder",
            "sourceFile": "POST_ORDER_SURVEY-CONSOLIDATED.csv",
            "methodology": "Composite score from satisfaction and intent metrics",
            "calculation": "Weighted average of satisfaction and repeat intent",
            "benchmark": {"good": 1.2, "average": 1.0, "poor": 0.8},
            "benchmarkSource": "Normalized to 1.0 average",
            "caveats": ["Survey-based", "May not reflect actual behavior"],
            "evidenceLevel": "corroborated",
            "relatedMetrics": ["mealSatisfaction", "repeatIntent"]
        },
        "coverageGap": {
            "name": "Coverage Gap",
            "source": "annaGroundTruth",
            "sourceFile": "anna_zone_dish_counts.csv",
            "methodology": "% of zones where dish is not available",
            "calculation": "(COUNT(zones WHERE dish NOT available) / COUNT(zones)) * 100",
            "benchmark": {"good": 30, "average": 50, "poor": 70},
            "benchmarkSource": "Internal target",
            "caveats": ["Based on supply data", "May lag actual availability"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["demandStrength", "zonesAnalyzed"]
        },
        
        # Zone Metrics
        "zoneOrders": {
            "name": "Zone Orders",
            "source": "orders",
            "sourceFile": "ALL_DINNEROO_ORDERS.csv",
            "methodology": "Total order count per zone",
            "calculation": "COUNT(*) GROUP BY zone",
            "benchmark": {"good": 1000, "average": 500, "poor": 100},
            "benchmarkSource": "Distribution quartiles",
            "caveats": ["Varies by zone population", "Affected by partner availability"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["zonePartners", "zoneCuisines"]
        },
        "zonePartners": {
            "name": "Zone Partners",
            "source": "annaGroundTruth",
            "sourceFile": "anna_zone_dish_counts.csv",
            "methodology": "Count of unique partners in zone",
            "calculation": "COUNT(DISTINCT partner) WHERE zone = X",
            "benchmark": {"good": 10, "average": 5, "poor": 3},
            "benchmarkSource": "MVP threshold",
            "caveats": ["Point-in-time count", "May include inactive partners"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["zoneCuisines", "mvpZones"]
        },
        "zoneCuisines": {
            "name": "Zone Cuisines",
            "source": "annaGroundTruth",
            "sourceFile": "anna_zone_dish_counts.csv",
            "methodology": "Count of unique cuisine types in zone",
            "calculation": "COUNT(DISTINCT cuisine) WHERE zone = X",
            "benchmark": {"good": 8, "average": 5, "poor": 3},
            "benchmarkSource": "MVP threshold",
            "caveats": ["Based on partner classification", "May vary by definition"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["zonePartners", "mvpZones"]
        },
        "zoneRating": {
            "name": "Zone Rating",
            "source": "ratings",
            "sourceFile": "DINNEROO_RATINGS.csv",
            "methodology": "Average rating for orders in zone",
            "calculation": "AVG(RATING_STARS) WHERE zone = X",
            "benchmark": {"good": 4.2, "average": 3.8, "poor": 3.5},
            "benchmarkSource": "Platform average",
            "caveats": ["Sample size varies by zone", "May be skewed by few partners"],
            "evidenceLevel": "corroborated",
            "relatedMetrics": ["zoneOrders", "zonePartners"]
        },
        
        # Cuisine Gap Metrics
        "cuisineSupplyGap": {
            "name": "Cuisine Supply Gap",
            "source": "annaGroundTruth",
            "sourceFile": "anna_zone_dish_counts.csv",
            "methodology": "Zones where cuisine supply is below average",
            "calculation": "item_count < AVG(item_count)",
            "benchmark": None,
            "caveats": ["Relative measure", "Average may shift"],
            "evidenceLevel": "validated",
            "relatedMetrics": ["cuisineQualityGap", "cuisineOrders"]
        },
        "cuisineQualityGap": {
            "name": "Cuisine Quality Gap",
            "source": "ratings",
            "sourceFile": "DINNEROO_RATINGS.csv",
            "methodology": "Cuisines where rating is below benchmark (4.0)",
            "calculation": "AVG(RATING_STARS) < 4.0",
            "benchmark": {"good": 4.0, "average": 3.8, "poor": 3.5},
            "benchmarkSource": "Platform target",
            "caveats": ["May be affected by partner mix", "Sample size varies"],
            "evidenceLevel": "corroborated",
            "relatedMetrics": ["cuisineSupplyGap", "cuisineOrders"]
        }
    }


def prepare_evidence_standards() -> Dict[str, Any]:
    """Prepare evidence standards reference."""
    return {
        "levels": {
            "single": {
                "symbol": "🔵",
                "name": "Single Source",
                "definition": "One data source only",
                "useFor": "Exploratory findings, hypothesis generation",
                "color": "#3b82f6"
            },
            "corroborated": {
                "symbol": "🟡",
                "name": "Corroborated",
                "definition": "2 independent sources",
                "useFor": "Working hypotheses, internal analysis",
                "color": "#f59e0b"
            },
            "validated": {
                "symbol": "🟢",
                "name": "Validated",
                "definition": "3+ sources OR quant+qual",
                "useFor": "Strategic recommendations, stakeholder presentations",
                "color": "#22c55e"
            }
        },
        "sampleSizeThresholds": {
            "unreliable": {"max": 20, "label": "Unreliable", "action": "Do not report"},
            "directional": {"min": 20, "max": 50, "label": "Directional", "action": "Report with caveat"},
            "moderate": {"min": 50, "max": 100, "label": "Moderate", "action": "Report as finding"},
            "strong": {"min": 100, "label": "Strong", "action": "Report confidently"}
        },
        "triangulationRules": {
            "canTriangulate": [
                {"sourceA": "Post-Order Survey", "sourceB": "Snowflake Orders", "reason": "Survey vs behavioral"},
                {"sourceA": "Dropoff Survey", "sourceB": "Post-Order Survey", "reason": "Different populations"},
                {"sourceA": "Any Quantitative", "sourceB": "Any Qualitative", "reason": "Different methods"},
                {"sourceA": "Snowflake Orders", "sourceB": "Transcripts", "reason": "Behavioral vs exploratory"}
            ],
            "cannotTriangulate": [
                {"sourceA": "Two questions from same survey", "sourceB": "Same survey", "reason": "Same respondents"},
                {"sourceA": "Post-Order + Dropoff (same metric)", "sourceB": "Both surveys", "reason": "Method overlap"}
            ]
        }
    }


def prepare_metric_definitions() -> Dict[str, Any]:
    """Prepare metric definitions for the glossary."""
    return {
        "satisfaction": {
            "name": "Satisfaction Rate",
            "definition": "% of respondents who are 'Very Satisfied' OR 'Satisfied'",
            "formula": "satisfied.mean() * 100",
            "interpretation": {
                "good": ">85%",
                "average": "70-85%",
                "poor": "<70%"
            }
        },
        "lovedItRate": {
            "name": "Loved It Rate",
            "definition": "% who selected 'Loved it' (highest rating only)",
            "formula": "(df['DISH_SENTIMENT'] == 'Loved it').mean() * 100",
            "interpretation": {
                "good": ">40%",
                "average": "25-40%",
                "poor": "<25%"
            }
        },
        "strongAdvocate": {
            "name": "Strong Advocate",
            "definition": "Customers meeting ALL THREE: Loved it + Very Satisfied + Would reorder",
            "formula": "(DISH_SENTIMENT == 'Loved it') & (SATISFACTION == 'Very Satisfied') & (REORDER_INTENT in ['Agree', 'Strongly agree'])",
            "interpretation": {
                "good": ">20%",
                "average": "10-20%",
                "poor": "<10%"
            }
        },
        "frequencyCategory": {
            "name": "Customer Frequency",
            "definition": "Based on days since last order",
            "categories": {
                "Very High": "<7 days (Daily / few times a week)",
                "High": "7-14 days (About once a week)",
                "Medium": "14-30 days (Once a month)",
                "Low": "30-90 days (Less than once a month)",
                "Very Low": ">90 days (Dormant / churned)"
            }
        }
    }


def prepare_dishes(project_root: Path) -> List[Dict[str, Any]]:
    """Prepare dish data from master dish list."""
    path = project_root / "DELIVERABLES" / "reports" / "MASTER_DISH_LIST_WITH_WORKINGS.csv"
    df = load_csv_safe(path)
    
    if df is None:
        return []
    
    dishes = []
    for _, row in df.iterrows():
        dish = {
            "rank": int(row.get("rank", 0)) if pd.notna(row.get("rank")) else None,
            "dishType": row.get("dish_type", ""),
            "cuisine": row.get("cuisine", ""),
            "onDinneroo": str(row.get("on_dinneroo", "")).upper() == "TRUE",
            "strategicPriority": row.get("strategic_priority", ""),
            "performance": {
                "avgSalesPerDish": float(row.get("avg_sales_per_dish")) if pd.notna(row.get("avg_sales_per_dish")) else None,
                "pctZonesTop5": row.get("pct_zones_top_5", ""),
                "deliverooRating": float(row.get("deliveroo_rating")) if pd.notna(row.get("deliveroo_rating")) else None,
                "mealSatisfaction": row.get("meal_satisfaction", ""),
                "repeatIntent": row.get("repeat_intent", "")
            },
            "opportunity": {
                "dishSuitability": float(row.get("dish_suitability")) if pd.notna(row.get("dish_suitability")) else None,
                "openTextRequests": int(row.get("open_text_requests")) if pd.notna(row.get("open_text_requests")) else None,
                "wishlistPct": row.get("wishlist_pct", "")
            },
            "context": {
                "demandStrength": float(row.get("demand_strength")) if pd.notna(row.get("demand_strength")) else None,
                "consumerPreference": float(row.get("consumer_preference")) if pd.notna(row.get("consumer_preference")) else None,
                "coverageGap": row.get("coverage_gap", "")
            }
        }
        dishes.append(dish)
    
    return dishes


def prepare_zones(project_root: Path) -> List[Dict[str, Any]]:
    """Prepare zone data from zone gap report."""
    path = project_root / "DATA" / "3_ANALYSIS" / "zone_gap_report.csv"
    df = load_csv_safe(path)
    
    if df is None:
        return []
    
    zones = []
    for _, row in df.iterrows():
        zone = {
            "zone": row.get("zone", ""),
            "region": row.get("region", ""),
            "orders": int(row.get("orders", 0)) if pd.notna(row.get("orders")) else 0,
            "partners": int(row.get("partners", 0)) if pd.notna(row.get("partners")) else 0,
            "cuisinesCount": int(row.get("cuisines_count", 0)) if pd.notna(row.get("cuisines_count")) else 0,
            "avgRating": float(row.get("avg_rating", 0)) if pd.notna(row.get("avg_rating")) else None,
            "isMvp": str(row.get("is_mvp", "")).lower() == "true",
            "mvpCriteriaMet": int(row.get("mvp_criteria_met", 0)) if pd.notna(row.get("mvp_criteria_met")) else 0,
            "cuisinesAvailable": row.get("cuisines_available", ""),
            "essentialCuisineCoverage": row.get("essential_cuisine_coverage", ""),
            "missingEssentialCuisines": row.get("missing_essential_cuisines", ""),
            "missingRecommendedCuisines": row.get("missing_recommended_cuisines", ""),
            "dishCoverage": row.get("dish_coverage", ""),
            "presentDishTypes": row.get("present_dish_types", ""),
            "missingDishTypes": row.get("missing_dish_types", ""),
            "recruitmentPriority": row.get("recruitment_priority", "")
        }
        zones.append(zone)
    
    return zones


def prepare_cuisine_gaps(project_root: Path) -> List[Dict[str, Any]]:
    """Prepare cuisine gap analysis data."""
    path = project_root / "DATA" / "3_ANALYSIS" / "cuisine_gap_analysis.csv"
    df = load_csv_safe(path)
    
    if df is None:
        return []
    
    gaps = []
    for _, row in df.iterrows():
        gap = {
            "cuisine": row.get("cuisine", ""),
            "itemCount": int(row.get("item_count", 0)) if pd.notna(row.get("item_count")) else 0,
            "brandCount": int(row.get("brand_count", 0)) if pd.notna(row.get("brand_count")) else 0,
            "avgRating": float(row.get("avg_rating", 0)) if pd.notna(row.get("avg_rating")) else None,
            "ratingCount": int(row.get("rating_count", 0)) if pd.notna(row.get("rating_count")) else 0,
            "orderCount": int(row.get("order_count", 0)) if pd.notna(row.get("order_count")) else 0,
            "gapType": row.get("gap_type", ""),
            "supplyVsAvg": float(row.get("supply_vs_avg", 0)) if pd.notna(row.get("supply_vs_avg")) else None,
            "ratingVsBenchmark": float(row.get("rating_vs_benchmark", 0)) if pd.notna(row.get("rating_vs_benchmark")) else None
        }
        gaps.append(gap)
    
    return gaps


def prepare_latent_demand(project_root: Path) -> Dict[str, Any]:
    """Prepare latent demand summary."""
    path = project_root / "DATA" / "3_ANALYSIS" / "latent_demand_summary.json"
    data = load_json_safe(path)
    
    if data is None:
        return {}
    
    return data


def prepare_survey_signals(project_root: Path) -> Dict[str, Any]:
    """Aggregate survey signals from multiple sources."""
    signals = {
        "postOrder": {},
        "dropoff": {},
        "combined": {}
    }
    
    # Load post-order survey
    post_order_path = project_root / "DATA" / "2_ENRICHED" / "post_order_enriched_COMPLETE.csv"
    post_order = load_csv_safe(post_order_path)
    
    if post_order is not None:
        signals["postOrder"] = {
            "totalResponses": len(post_order),
            "satisfactionDistribution": {},
            "topRestaurants": [],
            "topDishes": []
        }
        
        # Get satisfaction distribution if available
        for col in post_order.columns:
            if 'satisfaction' in col.lower() or 'feel about the meal' in col.lower():
                dist = post_order[col].value_counts().to_dict()
                signals["postOrder"]["satisfactionDistribution"] = {str(k): int(v) for k, v in dist.items() if pd.notna(k)}
                break
    
    # Load dropoff survey
    dropoff_path = project_root / "DATA" / "2_ENRICHED" / "DROPOFF_ENRICHED.csv"
    dropoff = load_csv_safe(dropoff_path)
    
    if dropoff is not None:
        signals["dropoff"] = {
            "totalResponses": len(dropoff),
            "barriers": {},
            "wishlistDishes": []
        }
    
    # Combined stats
    signals["combined"] = {
        "totalSurveyResponses": signals["postOrder"].get("totalResponses", 0) + signals["dropoff"].get("totalResponses", 0)
    }
    
    return signals


def prepare_behavioral_data(project_root: Path) -> Dict[str, Any]:
    """Prepare behavioral data summary from Snowflake."""
    behavioral = {
        "orders": {},
        "ratings": {},
        "partners": {}
    }
    
    # Load orders
    orders_path = project_root / "DATA" / "1_SOURCE" / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
    orders = load_csv_safe(orders_path)
    
    if orders is not None:
        behavioral["orders"] = {
            "totalOrders": len(orders),
            "uniqueCustomers": orders["CUSTOMER_ID"].nunique() if "CUSTOMER_ID" in orders.columns else 0,
            "uniquePartners": orders["PARTNER_NAME"].nunique() if "PARTNER_NAME" in orders.columns else 0,
            "uniqueZones": orders["ZONE_NAME"].nunique() if "ZONE_NAME" in orders.columns else 0
        }
        
        # Top zones by orders
        if "ZONE_NAME" in orders.columns:
            top_zones = orders["ZONE_NAME"].value_counts().head(10).to_dict()
            behavioral["orders"]["topZones"] = [{"zone": k, "orders": int(v)} for k, v in top_zones.items()]
        
        # Top partners by orders
        if "PARTNER_NAME" in orders.columns:
            top_partners = orders["PARTNER_NAME"].value_counts().head(10).to_dict()
            behavioral["orders"]["topPartners"] = [{"partner": k, "orders": int(v)} for k, v in top_partners.items()]
    
    # Load ratings
    ratings_path = project_root / "DATA" / "1_SOURCE" / "snowflake" / "DINNEROO_RATINGS.csv"
    ratings = load_csv_safe(ratings_path)
    
    if ratings is not None:
        behavioral["ratings"] = {
            "totalRatings": len(ratings),
            "avgRating": float(ratings["RATING_STARS"].mean()) if "RATING_STARS" in ratings.columns else None,
            "ratingDistribution": {}
        }
        
        if "RATING_STARS" in ratings.columns:
            dist = ratings["RATING_STARS"].value_counts().sort_index().to_dict()
            behavioral["ratings"]["ratingDistribution"] = {str(int(k)): int(v) for k, v in dist.items() if pd.notna(k)}
    
    return behavioral


def prepare_ground_truth(project_root: Path) -> Dict[str, Any]:
    """Prepare Anna's ground truth data."""
    ground_truth = {
        "partners": [],
        "zones": {},
        "dishes": {}
    }
    
    # Load partner coverage
    partners_path = project_root / "DATA" / "3_ANALYSIS" / "anna_partner_coverage.csv"
    partners = load_csv_safe(partners_path)
    
    if partners is not None:
        ground_truth["partners"] = partners.to_dict(orient="records")
        ground_truth["summary"] = {
            "totalBrands": len(partners),
            "totalSites": int(partners["total_sites"].sum()) if "total_sites" in partners.columns else 0
        }
    
    # Load zone dish counts
    zones_path = project_root / "DATA" / "3_ANALYSIS" / "anna_zone_dish_counts.csv"
    zones = load_csv_safe(zones_path)
    
    if zones is not None:
        # Find the total_dishes column
        total_dishes_col = None
        for col in zones.columns:
            if 'total' in col.lower() and 'dish' in col.lower():
                total_dishes_col = col
                break
        
        zones_with_dishes = 0
        if total_dishes_col:
            zones_with_dishes = len(zones[pd.to_numeric(zones[total_dishes_col], errors='coerce') > 0])
        
        ground_truth["zones"] = {
            "totalZones": len(zones),
            "zonesWithDishes": zones_with_dishes
        }
    
    return ground_truth


def prepare_selection_gaps() -> List[Dict[str, Any]]:
    """Prepare selection gaps summary for stakeholder presentation."""
    # These are the key selection problems identified from WBR and analysis
    return [
        {
            "gap": "No Fish & Chips",
            "evidence": "63% families eat regularly (OG Survey n=404), 0 supply, 5 open-text requests",
            "evidenceSources": ["OG Survey", "Supply Data", "Open-text"],
            "impact": "Missing high-demand dish - #11 most eaten by families",
            "action": "Partner recruitment",
            "priority": "High",
            "eatenPct": 63,
            "supplyCount": 0,
            "openTextMentions": 5
        },
        {
            "gap": "Limited Mexican",
            "evidence": "60% eat regularly, only Las Iguanas, 31 open-text requests",
            "evidenceSources": ["OG Survey", "Supply Data", "Open-text"],
            "impact": "Under-served cuisine with high demand",
            "action": "Expand partners",
            "priority": "High",
            "eatenPct": 60,
            "supplyCount": 1,
            "openTextMentions": 31
        },
        {
            "gap": "No Roasts",
            "evidence": "78% eat regularly - 2nd highest after burgers, ~0% supply",
            "evidenceSources": ["OG Survey", "Supply Data"],
            "impact": "Highest latent demand - families don't expect on delivery",
            "action": "Investigate feasibility",
            "priority": "Medium",
            "eatenPct": 78,
            "supplyCount": 0,
            "openTextMentions": 1
        },
        {
            "gap": "Chinese under-represented",
            "evidence": "68% eat regularly, 0.07% of orders, 34 open-text requests",
            "evidenceSources": ["OG Survey", "Snowflake Orders", "Open-text"],
            "impact": "Largest stated/revealed gap",
            "action": "Menu expansion",
            "priority": "High",
            "eatenPct": 68,
            "orderPct": 0.07,
            "openTextMentions": 34
        },
        {
            "gap": "More Pies",
            "evidence": "49% eat regularly, highest suitability score (4.4), 75-89% scratch cook",
            "evidenceSources": ["OG Survey", "Suitability Scoring"],
            "impact": "High effort dish families would outsource",
            "action": "Partner recruitment",
            "priority": "Medium",
            "eatenPct": 49,
            "suitabilityScore": 4.4,
            "openTextMentions": 6
        },
        {
            "gap": "Burgers (guilt-free)",
            "evidence": "70% eat regularly - highest consumption, 17 open-text requests",
            "evidenceSources": ["OG Survey", "Open-text"],
            "impact": "High demand, need healthier options",
            "action": "Partner recruitment (chicken/gourmet/veggie)",
            "priority": "Medium",
            "eatenPct": 70,
            "openTextMentions": 17
        }
    ]


def prepare_og_survey_comparison(project_root: Path) -> Dict[str, Any]:
    """Prepare OG Survey data for validation comparison."""
    path = project_root / "DATA" / "3_ANALYSIS" / "extracted_factors_phase1.json"
    data = load_json_safe(path)
    
    if data is None:
        return {"dishes": [], "dishMapping": {}}
    
    og_dishes = data.get("og_survey_dishes", [])
    
    # Create ranked list with parsed percentages
    ranked_dishes = []
    for i, dish in enumerate(og_dishes):
        eaten_pct = dish.get("eaten_pct", "0%")
        if isinstance(eaten_pct, str):
            eaten_pct = float(eaten_pct.replace("%", ""))
        
        wishlist_pct = dish.get("wishlist_pct", "0%")
        if isinstance(wishlist_pct, str):
            wishlist_pct = float(wishlist_pct.replace("%", ""))
        
        ranked_dishes.append({
            "rank": i + 1,
            "dish": dish.get("dish", ""),
            "cuisine": dish.get("cuisine", ""),
            "eatenPct": eaten_pct,
            "wishlistPct": wishlist_pct,
            "shareable": dish.get("shareable", ""),
            "customisable": dish.get("customisable", ""),
            "healthy": dish.get("healthy", ""),
            "prepTime": dish.get("prep_time", 0)
        })
    
    # Mapping from OG Survey terms to Master List terms
    dish_mapping = {
        "Curry Rice": ["Indian Curry", "Biryani", "East Asian Curry"],
        "Stir fry Noodles": ["Noodles", "Fried Rice"],
        "Fajitas Burritos": ["Fajitas", "Burrito Bowl", "Tacos"],
        "Mash pie": ["Shepherd's Pie"],
        "Fish Chips": ["Fish & Chips"],
        "Burger Chips": ["Burgers"],
        "Meat veg": ["Protein & Veg"],
        "Boiled Pasta": ["Pasta"],
        "Baked Pasta": ["Lasagne"],
        "Katsu Curry": ["Katsu"],
        "Thai Curry": ["East Asian Curry"],
        "Rice bowl fried rice": ["Rice Bowl", "Fried Rice"],
        "Jacket potato": ["Jacket Potato"],
        "Casserole Stew": ["Casserole / Stew"],
        "Pastry Pie": ["Pastry Pie"],
        "Sausage mash": ["Sausage & Mash"]
    }
    
    return {
        "dishes": ranked_dishes,
        "dishMapping": dish_mapping,
        "sampleSize": 404,
        "surveyDate": "2025-06-01",
        "biasWarning": "Pre-launch stated preference - validate with behavioral data"
    }


def prepare_normalization_metadata() -> Dict[str, Any]:
    """Prepare metadata explaining supply normalization."""
    return {
        "explanation": "Sales metrics are normalized for supply differences to ensure fair comparison across dishes with different availability.",
        "formula": "Normalized Sales = Total Orders / (Zones Available × Days Listed)",
        "example": "A dish in 10 zones with 1000 orders scores the same as a dish in 100 zones with 10,000 orders",
        "metricsNormalized": [
            {
                "metric": "avgSalesPerDish",
                "name": "Avg Sales Per Dish",
                "normalization": "Divided by zones available",
                "badge": "Supply-Normalized"
            },
            {
                "metric": "pctZonesTop5",
                "name": "% Zones in Top 5",
                "normalization": "Inherently normalized (percentage)",
                "badge": "Zone-Relative"
            },
            {
                "metric": "demandStrength",
                "name": "Demand Strength",
                "normalization": "Composite of normalized metrics",
                "badge": "Supply-Normalized"
            }
        ],
        "metricsNotNormalized": [
            {
                "metric": "deliverooRating",
                "name": "Deliveroo Rating",
                "reason": "Per-order average, not affected by zone count"
            },
            {
                "metric": "mealSatisfaction",
                "name": "Meal Satisfaction",
                "reason": "Survey percentage, not volume-based"
            },
            {
                "metric": "repeatIntent",
                "name": "Repeat Intent",
                "reason": "Survey percentage, not volume-based"
            }
        ]
    }


def prepare_methodology_summary() -> Dict[str, Any]:
    """Prepare methodology summary for stakeholder presentation."""
    return {
        "title": "Our Methodology Response",
        "principles": [
            {
                "name": "Triangulated Scoring",
                "description": "No single source > 50% weight",
                "detail": "Combines behavioral (orders, ratings) with survey (satisfaction, intent) and qualitative (open-text) data"
            },
            {
                "name": "Behavioral Validation",
                "description": "OG Survey claims checked against actual orders",
                "detail": "Stated preference from pre-launch survey is validated with revealed preference from Snowflake"
            },
            {
                "name": "Supply Normalization",
                "description": "Sales adjusted for zone availability",
                "detail": "Prevents dishes in more zones from unfairly outranking limited-availability dishes"
            },
            {
                "name": "Gap Analysis",
                "description": "Coverage gaps prioritized by demand evidence",
                "detail": "High coverage gap alone doesn't mean opportunity - must have demand signal"
            },
            {
                "name": "Family Signals",
                "description": "Kids Full & Happy (7.5%), Fussy Eater Friendly (5.5%)",
                "detail": "Family-specific metrics weighted into scoring to reflect Dinneroo's target audience"
            }
        ],
        "weightingFramework": {
            "performance": {
                "weight": 0.50,
                "components": {
                    "normalizedSales": 0.10,
                    "zoneRankingStrength": 0.10,
                    "deliverooRating": 0.10,
                    "repeatIntent": 0.05,
                    "kidsFullHappy": 0.075,
                    "likedLovedIt": 0.075
                }
            },
            "opportunity": {
                "weight": 0.50,
                "components": {
                    "latentDemand": 0.25,
                    "adultAppeal": 0.1025,
                    "balancedGuiltFree": 0.0925,
                    "fussyEaterFriendly": 0.055
                }
            }
        }
    }


def main():
    """Main entry point."""
    print("=" * 60)
    print("PREPARING DASHBOARD DATA")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Initialize dashboard data
    dashboard_data = {
        "metadata": prepare_metadata()
    }
    
    print("Loading data sources...")
    print()
    
    # Prepare each data section
    print("1. Preparing dish data...")
    dashboard_data["dishes"] = prepare_dishes(PROJECT_ROOT)
    print()
    
    print("2. Preparing zone data...")
    dashboard_data["zones"] = prepare_zones(PROJECT_ROOT)
    print()
    
    print("3. Preparing cuisine gap data...")
    dashboard_data["cuisineGaps"] = prepare_cuisine_gaps(PROJECT_ROOT)
    print()
    
    print("4. Preparing latent demand data...")
    dashboard_data["latentDemand"] = prepare_latent_demand(PROJECT_ROOT)
    print()
    
    print("5. Preparing survey signals...")
    dashboard_data["surveySignals"] = prepare_survey_signals(PROJECT_ROOT)
    print()
    
    print("6. Preparing behavioral data...")
    dashboard_data["behavioral"] = prepare_behavioral_data(PROJECT_ROOT)
    print()
    
    print("7. Preparing ground truth data...")
    dashboard_data["groundTruth"] = prepare_ground_truth(PROJECT_ROOT)
    print()
    
    print("8. Preparing data sources registry...")
    dashboard_data["dataSourcesRegistry"] = prepare_data_sources_registry()
    print(f"  ✓ {len(dashboard_data['dataSourcesRegistry'])} metrics registered")
    print()
    
    print("9. Preparing evidence standards...")
    dashboard_data["evidenceStandards"] = prepare_evidence_standards()
    print("  ✓ Evidence levels and thresholds loaded")
    print()
    
    print("10. Preparing metric definitions...")
    dashboard_data["metricDefinitions"] = prepare_metric_definitions()
    print(f"  ✓ {len(dashboard_data['metricDefinitions'])} definitions loaded")
    print()
    
    print("11. Preparing selection gaps...")
    dashboard_data["selectionGaps"] = prepare_selection_gaps()
    print(f"  ✓ {len(dashboard_data['selectionGaps'])} selection gaps identified")
    print()
    
    print("12. Preparing OG Survey comparison...")
    dashboard_data["ogSurveyComparison"] = prepare_og_survey_comparison(PROJECT_ROOT)
    print(f"  ✓ {len(dashboard_data['ogSurveyComparison'].get('dishes', []))} OG Survey dishes loaded")
    print()
    
    print("13. Preparing normalization metadata...")
    dashboard_data["normalizationMetadata"] = prepare_normalization_metadata()
    print("  ✓ Normalization explanations loaded")
    print()
    
    print("14. Preparing methodology summary...")
    dashboard_data["methodologySummary"] = prepare_methodology_summary()
    print("  ✓ Methodology summary loaded")
    print()
    
    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(dashboard_data, f, indent=2, cls=NumpyEncoder)
    
    print("=" * 60)
    print("DASHBOARD DATA PREPARED")
    print("=" * 60)
    print(f"Output: {OUTPUT_FILE}")
    print(f"Dishes: {len(dashboard_data['dishes'])}")
    print(f"Zones: {len(dashboard_data['zones'])}")
    print(f"Cuisine gaps: {len(dashboard_data['cuisineGaps'])}")
    print(f"Metrics registered: {len(dashboard_data['dataSourcesRegistry'])}")
    print()
    
    return dashboard_data


if __name__ == "__main__":
    main()

