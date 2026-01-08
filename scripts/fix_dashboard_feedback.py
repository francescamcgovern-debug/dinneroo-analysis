#!/usr/bin/env python3
"""
Fix Dashboard Feedback Issues
Implements all fixes from the feedback review (ffea1812)
"""

import re

DASHBOARD_PATH = "DELIVERABLES/dashboards/dinneroo_master_dashboard.html"

def fix_dashboard():
    with open(DASHBOARD_PATH, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # =========================================================================
    # CRITICAL FIX #1: Add Zone Count Legend after section header
    # =========================================================================
    
    zone_count_legend = '''
            <!-- Zone Count Legend - ADDED BY FEEDBACK FIX -->
            <div class="methodology-note" style="margin-bottom: 1.5rem; background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3);">
                <strong style="color: var(--accent-blue);">📊 ZONE COUNT GUIDE</strong>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 0.75rem; text-align: center;">
                    <div style="background: var(--bg-card); padding: 0.75rem; border-radius: 0.5rem;">
                        <div style="font-size: 1.5rem; font-weight: 700;">1,306</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">Total Zones</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted);">Anna's full coverage</div>
                    </div>
                    <div style="background: var(--bg-card); padding: 0.75rem; border-radius: 0.5rem;">
                        <div style="font-size: 1.5rem; font-weight: 700;">434</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">With Supply</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted);">Partners configured</div>
                    </div>
                    <div style="background: var(--bg-card); padding: 0.75rem; border-radius: 0.5rem;">
                        <div style="font-size: 1.5rem; font-weight: 700;">201</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">With Orders</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted);">Trial activity</div>
                    </div>
                    <div style="background: var(--bg-card); padding: 0.75rem; border-radius: 0.5rem;">
                        <div style="font-size: 1.5rem; font-weight: 700;">197</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">Analyzed</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted);">Statistical threshold</div>
                    </div>
                </div>
            </div>
            
            <!-- Role-Based Quick Start - ADDED BY FEEDBACK FIX -->
            <div class="step-card" style="margin-bottom: 2rem; border-top: 3px solid var(--accent-purple);">
                <div class="step-header">
                    <div class="step-number" style="background: var(--accent-purple);">🎯</div>
                    <div>
                        <div class="step-title">Quick Start by Role</div>
                        <div class="step-subtitle">Jump to what matters most for your team</div>
                    </div>
                </div>
                <div class="step-content">
                    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem;">
                        <button onclick="showSection('thresholds'); setTimeout(() => document.getElementById('exec-summary')?.scrollIntoView({behavior:'smooth'}), 100);" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--accent-teal)'" onmouseout="this.style.borderColor='var(--border)'">
                            <div style="font-size: 1.5rem;">📊</div>
                            <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Product</div>
                            <div style="font-size: 0.7rem; color: var(--text-muted);">MVP thresholds</div>
                        </button>
                        <button onclick="showSection('zones')" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--accent-teal)'" onmouseout="this.style.borderColor='var(--border)'">
                            <div style="font-size: 1.5rem;">🗺️</div>
                            <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Partner Ops</div>
                            <div style="font-size: 0.7rem; color: var(--text-muted);">Zone priority queue</div>
                        </button>
                        <button onclick="showSection('dishes')" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--accent-teal)'" onmouseout="this.style.borderColor='var(--border)'">
                            <div style="font-size: 1.5rem;">🍽️</div>
                            <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Commercial</div>
                            <div style="font-size: 0.7rem; color: var(--text-muted);">Dish recruitment</div>
                        </button>
                        <button onclick="showSection('gaps')" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--accent-teal)'" onmouseout="this.style.borderColor='var(--border)'">
                            <div style="font-size: 1.5rem;">🎨</div>
                            <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Marketing</div>
                            <div style="font-size: 0.7rem; color: var(--text-muted);">Cuisine positioning</div>
                        </button>
                        <button onclick="showSection('thresholds'); setTimeout(() => document.getElementById('exec-summary')?.scrollIntoView({behavior:'smooth'}), 100);" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--accent-teal)'" onmouseout="this.style.borderColor='var(--border)'">
                            <div style="font-size: 1.5rem;">👔</div>
                            <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Leadership</div>
                            <div style="font-size: 0.7rem; color: var(--text-muted);">Executive summary</div>
                        </button>
                    </div>
                </div>
            </div>
            
'''
    
    # Insert after section description, before Executive Summary
    content = content.replace(
        '            <!-- Executive Summary Panel -->',
        zone_count_legend + '            <!-- Executive Summary Panel -->'
    )
    
    # Add ID to Executive Summary for scrolling
    content = content.replace(
        '<div class="step-card" style="margin-bottom: 2rem; border-top: 3px solid var(--accent-teal);">\n                <div class="step-header">\n                    <div class="step-number" style="background: var(--accent-teal);">📊</div>\n                    <div>\n                        <div class="step-title">Executive Summary</div>',
        '<div id="exec-summary" class="step-card" style="margin-bottom: 2rem; border-top: 3px solid var(--accent-teal);">\n                <div class="step-header">\n                    <div class="step-number" style="background: var(--accent-teal);">📊</div>\n                    <div>\n                        <div class="step-title">Executive Summary</div>'
    )
    
    # =========================================================================
    # CRITICAL FIX #2a: Update MVP Progress Bar (33/50 → 70/50, target exceeded!)
    # =========================================================================
    
    content = content.replace(
        '<span>33/50 zones (66%) <span style="color: var(--success);">+3 this week ▲</span></span>',
        '<span>70/50 zones (140%) <span style="color: var(--success);">🎉 TARGET EXCEEDED!</span></span>'
    )
    
    # Update progress bar width from 66% to 100% (capped)
    content = content.replace(
        'width: 66%; height: 100%; border-radius: 0.5rem;"></div>',
        'width: 100%; height: 100%; border-radius: 0.5rem;"></div>'
    )
    
    # =========================================================================
    # CRITICAL FIX #2b: Update Near MVP Breakdown (48 → 31, correct cuisines)
    # =========================================================================
    
    content = content.replace(
        '<strong>NEAR MVP BREAKDOWN</strong> <span style="color: var(--text-muted);">(48 zones, 1 gap away)</span>\n                        <div style="display: flex; gap: 2rem; margin-top: 0.75rem;">\n                            <div><span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-teal);">32</span> need Indian</div>\n                            <div><span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-purple);">10</span> need Mexican</div>\n                            <div><span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-amber);">6</span> need British</div>\n                        </div>',
        '<strong>NEAR MVP BREAKDOWN</strong> <span style="color: var(--text-muted);">(31 zones, 1 gap away)</span> <span class="evidence-badge validated" style="font-size: 0.65rem;">🟢 zone_mvp_status.json</span>\n                        <div style="display: flex; gap: 2rem; margin-top: 0.75rem;">\n                            <div><span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-teal);">31</span> need Healthy</div>\n                            <div><span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-purple);">25</span> need Indian</div>\n                            <div><span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-amber);">25</span> need Mexican</div>\n                        </div>'
    )
    
    # =========================================================================
    # FIX #4a: Add sample sizes to segment satisfaction insight
    # =========================================================================
    
    content = content.replace(
        '💡 <strong>INSIGHT:</strong> Non-families are 54% of orders and equally/more satisfied (Couples: 87.1% vs Families: 85.6%)',
        '💡 <strong>INSIGHT:</strong> Non-families are 54% of orders and equally/more satisfied (Couples: 87.1% <span style="color: var(--text-muted);">[n=205]</span> vs Families: 85.6% <span style="color: var(--text-muted);">[n=410]</span>)'
    )
    
    # =========================================================================
    # CRITICAL FIX #2c: Update Alerts Panel (48 → 31)
    # =========================================================================
    
    content = content.replace(
        '<strong>48 Near MVP Zones</strong> need only 1 cuisine gap filled\n                                <div style="font-size: 0.8rem; color: var(--text-muted);">32 need Indian, 10 need Mexican, 6 need British</div>',
        '<strong>31 Near MVP Zones</strong> need only 1 cuisine gap filled\n                                <div style="font-size: 0.8rem; color: var(--text-muted);">31 need Healthy, 25 need Indian, 25 need Mexican</div>'
    )
    
    # =========================================================================
    # FIX #4b: Add source attribution to latent demand
    # =========================================================================
    
    content = content.replace(
        '<strong>87 Latent Demand Mentions</strong> for vegetarian options\n                                <div style="font-size: 0.8rem; color: var(--text-muted);">Top barrier after restaurant availability</div>',
        '<strong>87 Latent Demand Mentions</strong> for vegetarian options\n                                <div style="font-size: 0.8rem; color: var(--text-muted);">OG Survey open-text (n=2,796) · Top barrier after restaurant availability</div>'
    )
    
    # =========================================================================
    # CRITICAL FIX #1b: Fix "101 zones" → "201 zones" in Zone section
    # =========================================================================
    
    content = content.replace(
        'Track zone readiness across <strong>101 zones with orders</strong>',
        'Track zone readiness across <strong>201 zones with orders</strong>'
    )
    
    content = content.replace(
        '<span class="source-badge snowflake">101 Zones</span>',
        '<span class="source-badge snowflake">201 Zones</span>'
    )
    
    # =========================================================================
    # CRITICAL FIX #2d: Update Zone KPI card (42 → 70)
    # =========================================================================
    
    content = content.replace(
        '<div class="value" id="mvp-ready-count">42</div>',
        '<div class="value" id="mvp-ready-count">70</div>'
    )
    
    # =========================================================================
    # CRITICAL FIX #2e: Update Zone Progression Funnel
    # =========================================================================
    
    # Update Near MVP in funnel (48 → 31)
    content = content.replace(
        '<span style="font-weight: 600;">Near MVP</span>\n                                <span style="font-weight: 700; font-size: 1.25rem;">48</span>',
        '<span style="font-weight: 600;">Near MVP</span>\n                                <span style="font-weight: 700; font-size: 1.25rem;">31</span>'
    )
    
    # Update At MVP in funnel (33 → 70)
    content = content.replace(
        '<span style="font-weight: 600;">At MVP</span>\n                                <span style="font-weight: 700; font-size: 1.25rem;">33</span>',
        '<span style="font-weight: 600;">At MVP</span>\n                                <span style="font-weight: 700; font-size: 1.25rem;">70</span>'
    )
    
    # Update funnel widths to reflect new proportions
    # At MVP width: was 16% (33/201), now should be ~35% (70/201)
    content = content.replace(
        '<div style="width: 16%; margin-left: 42%; background: rgba(0, 212, 170, 0.4); height: 40px;',
        '<div style="width: 35%; margin-left: 32.5%; background: rgba(0, 212, 170, 0.4); height: 40px;'
    )
    
    # Near MVP width: was 24% (48/201), now should be ~15% (31/201)
    content = content.replace(
        '<div style="width: 24%; margin-left: 38%; background: rgba(245, 158, 11, 0.3); height: 40px;',
        '<div style="width: 15%; margin-left: 42.5%; background: rgba(245, 158, 11, 0.3); height: 40px;'
    )
    
    # =========================================================================
    # CRITICAL FIX #2f: Update threshold evidence text
    # =========================================================================
    
    content = content.replace(
        '<strong>16%</strong> of zones with orders meet all MVP criteria (33 of 201)',
        '<strong>35%</strong> of zones with orders meet all MVP criteria (70 of 201)'
    )
    
    # =========================================================================
    # FIX #5: Expand survivorship bias warning
    # =========================================================================
    
    old_survivorship = '<div class="step-subtitle">What dishes are performing well? (33 dishes with order data) ⚠️ Survivorship bias applies</div>'
    new_survivorship = '''<div class="step-subtitle">What dishes are performing well? (33 dishes with order data)</div>
                    </div>
                </div>
                <div class="step-content">
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 1rem;">
                        <strong style="color: var(--warning);">⚠️ SURVIVORSHIP BIAS NOTE:</strong>
                        <span style="color: var(--text-secondary); font-size: 0.85rem;">
                            Performance data shows what works among dishes we already offer — not what families want most. 
                            Dishes not yet on Dinneroo (e.g., grilled chicken, fish &amp; chips) may have strong unmet demand. 
                            <strong>See Section B: Recruitment Priorities</strong> below for latent demand analysis from open-text surveys (n=2,796).
                        </span>
                    </div>'''
    
    content = content.replace(old_survivorship, new_survivorship)
    
    # Remove the duplicate step-content div that gets created
    content = content.replace(
        '''</div>
                </div>
                <div class="step-content">
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 1rem;">
                        <strong style="color: var(--warning);">⚠️ SURVIVORSHIP BIAS NOTE:</strong>
                        <span style="color: var(--text-secondary); font-size: 0.85rem;">
                            Performance data shows what works among dishes we already offer — not what families want most. 
                            Dishes not yet on Dinneroo (e.g., grilled chicken, fish &amp; chips) may have strong unmet demand. 
                            <strong>See Section B: Recruitment Priorities</strong> below for latent demand analysis from open-text surveys (n=2,796).
                        </span>
                    </div>
                <div class="step-content">''',
        '''</div>
                </div>
                <div class="step-content">
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 1rem;">
                        <strong style="color: var(--warning);">⚠️ SURVIVORSHIP BIAS NOTE:</strong>
                        <span style="color: var(--text-secondary); font-size: 0.85rem;">
                            Performance data shows what works among dishes we already offer — not what families want most. 
                            Dishes not yet on Dinneroo (e.g., grilled chicken, fish &amp; chips) may have strong unmet demand. 
                            <strong>See Section B: Recruitment Priorities</strong> below for latent demand analysis from open-text surveys (n=2,796).
                        </span>
                    </div>'''
    )
    
    # =========================================================================
    # Write the fixed content
    # =========================================================================
    
    with open(DASHBOARD_PATH, 'w') as f:
        f.write(content)
    
    # Count changes
    changes = []
    if 'Zone Count Legend' in content and 'Zone Count Legend' not in original_content:
        changes.append("✅ Added Zone Count Legend panel")
    if 'Quick Start by Role' in content and 'Quick Start by Role' not in original_content:
        changes.append("✅ Added Quick Start by Role panel")
    if '70/50 zones' in content:
        changes.append("✅ Updated MVP Progress: 33 → 70")
    if '31 zones, 1 gap away' in content:
        changes.append("✅ Updated Near MVP: 48 → 31")
    if '31 need Healthy' in content:
        changes.append("✅ Fixed Near MVP breakdown (Healthy, Indian, Mexican)")
    if '[n=205]' in content:
        changes.append("✅ Added sample sizes to segment satisfaction")
    if 'OG Survey open-text (n=2,796)' in content:
        changes.append("✅ Added source attribution to latent demand")
    if '201 zones with orders' in content:
        changes.append("✅ Fixed zone count: 101 → 201")
    if 'id="mvp-ready-count">70' in content:
        changes.append("✅ Updated Zone KPI MVP count: 42 → 70")
    if 'SURVIVORSHIP BIAS NOTE' in content:
        changes.append("✅ Expanded survivorship bias warning")
    if '35%</strong> of zones with orders' in content:
        changes.append("✅ Updated threshold evidence: 16% → 35%")
    
    print("=" * 60)
    print("DASHBOARD FEEDBACK FIXES APPLIED")
    print("=" * 60)
    for change in changes:
        print(change)
    print()
    print(f"Total changes: {len(changes)}")
    print(f"File updated: {DASHBOARD_PATH}")
    print()
    print("Next step: Run 'python3 scripts/sync_zone_data.py' to deploy to docs/")

if __name__ == "__main__":
    fix_dashboard()

