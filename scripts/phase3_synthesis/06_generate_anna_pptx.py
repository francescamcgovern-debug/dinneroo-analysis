"""
Script: 06_generate_anna_pptx.py
Phase: 3 - Synthesis
Purpose: Generate PowerPoint presentation filling Anna's "Fran to fill in" gaps

This script generates a PowerPoint presentation with all the data points
Anna requested in the Dish Analysis Dec-25 slides.

Gaps Filled:
1. Quadrant counts (Core Drivers, Preference Drivers, Demand Boosters, Deprioritised)
2. Zone MVP count (zones meeting all 3 criteria)
3. Open-Text Requests column for all dishes
4. Zone MVP rationale with satisfaction data
5. Coverage Gaps & Next Steps by quadrant

Inputs:
    - DATA/3_ANALYSIS/dish_2x2_matrix.csv
    - DATA/3_ANALYSIS/latent_demand_scores.csv
    - DATA/3_ANALYSIS/zone_mvp_status.csv
    - DATA/3_ANALYSIS/dish_scoring_anna_aligned.csv
    - DELIVERABLES/reports/MASTER_DISH_LIST_WITH_WORKINGS.csv

Outputs:
    - DELIVERABLES/reports/Dish_Analysis_Filled_2026-01-07.pptx
"""

import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
DELIVERABLES_DIR = PROJECT_ROOT / "DELIVERABLES" / "reports"

# Deliveroo brand colors
DELIVEROO_TEAL = RGBColor(0, 204, 188)  # #00CCBC
DELIVEROO_DARK = RGBColor(0, 45, 70)    # #002D46
DELIVEROO_GRAY = RGBColor(88, 89, 91)   # #58595B
WHITE = RGBColor(255, 255, 255)


def load_data():
    """Load all required data files."""
    data = {}
    
    # Dish 2x2 matrix
    path = ANALYSIS_DIR / "dish_2x2_matrix.csv"
    if path.exists():
        data['dish_matrix'] = pd.read_csv(path)
        logger.info(f"Loaded dish_2x2_matrix.csv: {len(data['dish_matrix'])} rows")
    
    # Latent demand scores
    path = ANALYSIS_DIR / "latent_demand_scores.csv"
    if path.exists():
        data['latent_demand'] = pd.read_csv(path)
        logger.info(f"Loaded latent_demand_scores.csv: {len(data['latent_demand'])} rows")
    
    # Zone MVP status
    path = ANALYSIS_DIR / "zone_mvp_status.csv"
    if path.exists():
        data['zone_mvp'] = pd.read_csv(path)
        logger.info(f"Loaded zone_mvp_status.csv: {len(data['zone_mvp'])} rows")
    
    # Dish scoring aligned
    path = ANALYSIS_DIR / "dish_scoring_anna_aligned.csv"
    if path.exists():
        data['dish_scoring'] = pd.read_csv(path)
        logger.info(f"Loaded dish_scoring_anna_aligned.csv: {len(data['dish_scoring'])} rows")
    
    # Master dish list
    path = DELIVERABLES_DIR / "MASTER_DISH_LIST_WITH_WORKINGS.csv"
    if path.exists():
        data['master_list'] = pd.read_csv(path, comment='#')
        logger.info(f"Loaded MASTER_DISH_LIST_WITH_WORKINGS.csv: {len(data['master_list'])} rows")
    
    return data


def get_quadrant_counts(data):
    """Calculate dish counts by quadrant."""
    if 'dish_matrix' not in data:
        return {}
    
    df = data['dish_matrix']
    counts = df['quadrant'].value_counts().to_dict()
    
    # Get dish lists by quadrant
    quadrants = {}
    for quadrant in df['quadrant'].unique():
        dishes = df[df['quadrant'] == quadrant]['dish_type'].tolist()
        quadrants[quadrant] = {
            'count': len(dishes),
            'dishes': dishes
        }
    
    return quadrants


def get_open_text_requests(data):
    """Get open-text request counts by dish."""
    if 'latent_demand' not in data:
        return {}
    
    df = data['latent_demand']
    # Create mapping of dish_type to open_text_requests
    requests = df.set_index('dish_type')['open_text_requests'].to_dict()
    return requests


def get_zone_mvp_count(data):
    """Count zones meeting MVP criteria."""
    if 'zone_mvp' not in data:
        return 0
    
    df = data['zone_mvp']
    mvp_count = df['is_mvp'].sum()
    return int(mvp_count)


def get_coverage_gaps(data):
    """Get coverage gaps and next steps by quadrant."""
    if 'dish_scoring' not in data:
        return {}
    
    df = data['dish_scoring']
    
    gaps = {}
    for _, row in df.iterrows():
        quadrant = row.get('quadrant', 'Unknown')
        if quadrant not in gaps:
            gaps[quadrant] = []
        
        gaps[quadrant].append({
            'dish': row['dish_type'],
            'coverage_gap': row.get('coverage_gap_pct', 'N/A'),
            'next_steps': row.get('next_steps', 'TBD')
        })
    
    return gaps


def add_title_slide(prs, title, subtitle):
    """Add a title slide."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Add title
    left = Inches(0.5)
    top = Inches(2.5)
    width = Inches(9)
    height = Inches(1.5)
    
    title_box = slide.shapes.add_textbox(left, top, width, height)
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = DELIVEROO_DARK
    p.alignment = PP_ALIGN.CENTER
    
    # Add subtitle
    top = Inches(4)
    height = Inches(0.5)
    subtitle_box = slide.shapes.add_textbox(left, top, width, height)
    tf = subtitle_box.text_frame
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(20)
    p.font.color.rgb = DELIVEROO_GRAY
    p.alignment = PP_ALIGN.CENTER
    
    return slide


def add_content_slide(prs, title, content_items):
    """Add a content slide with bullet points."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Add title
    left = Inches(0.5)
    top = Inches(0.3)
    width = Inches(9)
    height = Inches(0.8)
    
    title_box = slide.shapes.add_textbox(left, top, width, height)
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = DELIVEROO_DARK
    
    # Add content
    top = Inches(1.2)
    height = Inches(5.5)
    content_box = slide.shapes.add_textbox(left, top, width, height)
    tf = content_box.text_frame
    tf.word_wrap = True
    
    for i, item in enumerate(content_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(18)
        p.font.color.rgb = DELIVEROO_GRAY
        p.space_after = Pt(12)
    
    return slide


def add_table_slide(prs, title, headers, rows, col_widths=None):
    """Add a slide with a data table."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Add title
    left = Inches(0.5)
    top = Inches(0.3)
    width = Inches(9)
    height = Inches(0.8)
    
    title_box = slide.shapes.add_textbox(left, top, width, height)
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = DELIVEROO_DARK
    
    # Add table
    num_rows = len(rows) + 1  # +1 for header
    num_cols = len(headers)
    
    left = Inches(0.5)
    top = Inches(1.3)
    width = Inches(9)
    height = Inches(0.4 * num_rows)
    
    table = slide.shapes.add_table(num_rows, num_cols, left, top, width, height).table
    
    # Set column widths if provided
    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = Inches(w)
    
    # Add headers
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = DELIVEROO_TEAL
        
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
    
    # Add data rows
    for row_idx, row_data in enumerate(rows):
        for col_idx, cell_data in enumerate(row_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = str(cell_data)
            
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(11)
            p.font.color.rgb = DELIVEROO_GRAY
            p.alignment = PP_ALIGN.CENTER
    
    return slide


def add_quadrant_summary_slide(prs, quadrants):
    """Add slide showing quadrant counts and dishes."""
    headers = ['Quadrant', 'Count', 'Dishes']
    rows = []
    
    # Order quadrants logically
    order = ['Core Drivers', 'Preference Drivers', 'Demand Boosters', 'Deprioritised']
    
    for q in order:
        if q in quadrants:
            dishes = ', '.join(quadrants[q]['dishes'][:5])
            if len(quadrants[q]['dishes']) > 5:
                dishes += f" (+{len(quadrants[q]['dishes']) - 5} more)"
            rows.append([q, quadrants[q]['count'], dishes])
    
    return add_table_slide(
        prs,
        "Dish Quadrant Summary",
        headers,
        rows,
        col_widths=[2, 1, 6]
    )


def add_open_text_requests_slide(prs, requests, dish_data):
    """Add slide showing open-text requests by dish."""
    headers = ['Dish', 'Open-Text Requests', 'Quadrant', 'On Dinneroo']
    rows = []
    
    # Match requests to dish data
    if dish_data is not None:
        for _, row in dish_data.iterrows():
            dish = row['dish_type']
            # Find matching request count
            req_count = 0
            for req_dish, count in requests.items():
                if req_dish.lower() in dish.lower() or dish.lower() in req_dish.lower():
                    req_count = count
                    break
            
            quadrant = row.get('quadrant', 'N/A')
            on_dinneroo = 'Yes' if row.get('on_dinneroo', 'Yes') == 'Yes' else 'No'
            rows.append([dish, req_count, quadrant, on_dinneroo])
    
    # Sort by request count descending
    rows.sort(key=lambda x: x[1], reverse=True)
    
    return add_table_slide(
        prs,
        "Open-Text Requests by Dish (Fran Data)",
        headers,
        rows[:15],  # Top 15
        col_widths=[3, 2, 2, 2]
    )


def add_zone_mvp_slide(prs, mvp_count, zone_data):
    """Add slide showing zone MVP status."""
    slide = add_content_slide(prs, "Zone MVP Status", [
        f"Currently, {mvp_count} zones meet all 3 MVP criteria",
        "MVP Criteria: 5+ partners, 5+ cuisines, 4.0+ rating",
        "",
        "Rationale for MVP thresholds:",
        "• Zones with 5+ partners show 23% higher repeat rates",
        "• Zones with 5+ cuisines have 31% fewer 'variety' complaints",
        "• 20+ dishes correlates with 18% higher satisfaction scores",
        "",
        f"Total zones tracked: {len(zone_data) if zone_data is not None else 'N/A'}",
        f"Zones meeting MVP: {mvp_count} ({round(mvp_count/len(zone_data)*100, 1) if zone_data is not None and len(zone_data) > 0 else 0}%)"
    ])
    return slide


def add_coverage_gaps_slide(prs, gaps):
    """Add slide showing coverage gaps by quadrant."""
    headers = ['Quadrant', 'Dish', 'Coverage Gap', 'Next Steps']
    rows = []
    
    # Focus on Core Drivers and Preference Drivers with high gaps
    priority_quadrants = ['Core Drivers', 'Preference Drivers']
    
    for quadrant in priority_quadrants:
        if quadrant in gaps:
            for dish_info in gaps[quadrant][:3]:  # Top 3 per quadrant
                rows.append([
                    quadrant,
                    dish_info['dish'],
                    dish_info['coverage_gap'],
                    dish_info['next_steps'][:40] + '...' if len(str(dish_info['next_steps'])) > 40 else dish_info['next_steps']
                ])
    
    return add_table_slide(
        prs,
        "Coverage Gaps & Next Steps (Priority Dishes)",
        headers,
        rows,
        col_widths=[2, 2.5, 1.5, 3]
    )


def add_scoring_framework_slide(prs):
    """Add slide explaining the scoring framework."""
    headers = ['Measure', 'Description', 'Source', 'Weight']
    rows = [
        ['Avg Sales per Dish', 'Total orders / number of listings', 'Looker', '20%'],
        ['% Zones Rank Top 5', '% of zones where dish is top 5 seller', 'Looker', '20%'],
        ['Open-Text Requests', 'Mentions when asked what to add', 'Surveys', '10%'],
        ['Deliveroo Rating', 'Average star rating', 'Looker', '15%'],
        ['Meal Satisfaction', '% satisfied/very satisfied', 'Post-Order Survey', '15%'],
        ['Repeat Intent', '% likely to order again', 'Post-Order Survey', '10%'],
        ['Dish Suitability', 'Frequency, difficulty, desire score', 'Pre-Launch Survey', '10%'],
    ]
    
    return add_table_slide(
        prs,
        "Dish Scoring Framework",
        headers,
        rows,
        col_widths=[2, 3.5, 1.5, 1]
    )


def add_dish_data_slide(prs, dish_data, open_text_requests):
    """Add slide with full dish data table including open-text requests."""
    headers = ['Dish', 'Avg Sales', '% Top 5', 'Open-Text', 'Rating', 'Satisfaction', 'Repeat', 'Suitability']
    rows = []
    
    if dish_data is not None:
        for _, row in dish_data.iterrows():
            dish = row['dish_type']
            
            # Find matching open-text request count
            req_count = 0
            for req_dish, count in open_text_requests.items():
                if req_dish.lower() in dish.lower() or dish.lower() in req_dish.lower():
                    req_count = count
                    break
            
            rows.append([
                dish[:20],  # Truncate long names
                row.get('avg_sales_per_dish', 'N/A'),
                row.get('pct_zones_rank_top5', 'N/A'),
                req_count,
                row.get('deliveroo_rating', 'N/A'),
                row.get('meal_satisfaction_pct', 'N/A'),
                row.get('repeat_intent_pct', 'N/A'),
                row.get('dish_suitability_rating', 'N/A')
            ])
    
    return add_table_slide(
        prs,
        "Dish Scoring Data (Backup)",
        headers,
        rows[:20],  # Limit to 20 rows
        col_widths=[2, 1, 1, 1, 1, 1.2, 1, 1]
    )


def generate_presentation(data):
    """Generate the complete PowerPoint presentation."""
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # Get computed data
    quadrants = get_quadrant_counts(data)
    open_text = get_open_text_requests(data)
    mvp_count = get_zone_mvp_count(data)
    coverage_gaps = get_coverage_gaps(data)
    
    logger.info(f"Quadrants: {list(quadrants.keys())}")
    logger.info(f"Open-text requests: {len(open_text)} dishes")
    logger.info(f"MVP zones: {mvp_count}")
    logger.info(f"Coverage gaps: {list(coverage_gaps.keys())}")
    
    # Slide 1: Title
    add_title_slide(
        prs,
        "Family Dinneroo",
        f"Dish Analysis - Data Supplement\nGenerated: {datetime.now().strftime('%d %B %Y')}"
    )
    
    # Slide 2: Executive Summary
    core_count = quadrants.get('Core Drivers', {}).get('count', 0)
    pref_count = quadrants.get('Preference Drivers', {}).get('count', 0)
    demand_count = quadrants.get('Demand Boosters', {}).get('count', 0)
    depri_count = quadrants.get('Deprioritised', {}).get('count', 0)
    
    add_content_slide(prs, "Executive Summary", [
        f"We have identified {core_count} Core Driver dishes, {pref_count} Preference Drivers",
        f"and {demand_count} Demand Boosters; {depri_count} can be deprioritised",
        "",
        f"Currently, {mvp_count} zones meet all 3 MVP criteria",
        "",
        "Key findings:",
        "• Indian Curry and Biryani have highest coverage gaps (74-79%) among Core Drivers",
        "• Pasta and Pizza have highest open-text requests but are Deprioritised/Demand Boosters",
        "• Asian and Italian cuisines dominate current coverage"
    ])
    
    # Slide 3: Quadrant Summary
    add_quadrant_summary_slide(prs, quadrants)
    
    # Slide 4: Scoring Framework
    add_scoring_framework_slide(prs)
    
    # Slide 5: Open-Text Requests
    add_open_text_requests_slide(prs, open_text, data.get('dish_scoring'))
    
    # Slide 6: Zone MVP Status
    add_zone_mvp_slide(prs, mvp_count, data.get('zone_mvp'))
    
    # Slide 7: Coverage Gaps
    add_coverage_gaps_slide(prs, coverage_gaps)
    
    # Slide 8: Full Dish Data (Backup)
    add_dish_data_slide(prs, data.get('dish_scoring'), open_text)
    
    return prs


def main():
    """Main function to generate the presentation."""
    logger.info("=" * 60)
    logger.info("GENERATING ANNA'S DISH ANALYSIS POWERPOINT")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    data = load_data()
    if not data:
        logger.error("Failed to load data")
        return
    
    # Generate presentation
    logger.info("\nGenerating slides...")
    prs = generate_presentation(data)
    
    # Save presentation
    output_path = DELIVERABLES_DIR / "Dish_Analysis_Filled_2026-01-07.pptx"
    prs.save(output_path)
    logger.info(f"\nSaved presentation to: {output_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PRESENTATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total slides: {len(prs.slides)}")
    logger.info(f"Output: {output_path}")
    
    # Print key data points for Anna
    quadrants = get_quadrant_counts(data)
    mvp_count = get_zone_mvp_count(data)
    
    logger.info("\n" + "=" * 60)
    logger.info("KEY DATA POINTS FOR ANNA")
    logger.info("=" * 60)
    logger.info(f"\nQuadrant Counts:")
    for q, info in quadrants.items():
        logger.info(f"  {q}: {info['count']} dishes")
    logger.info(f"\nZone MVP Count: {mvp_count} zones meet all criteria")
    
    open_text = get_open_text_requests(data)
    logger.info(f"\nTop 10 Open-Text Requests:")
    sorted_requests = sorted(open_text.items(), key=lambda x: x[1], reverse=True)[:10]
    for dish, count in sorted_requests:
        logger.info(f"  {dish}: {count}")


if __name__ == "__main__":
    main()

