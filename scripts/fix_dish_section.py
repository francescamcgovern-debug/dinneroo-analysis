#!/usr/bin/env python3
"""
Fix Dish Section - Tell a clearer story
"""

DASHBOARD_PATH = "DELIVERABLES/dashboards/dinneroo_master_dashboard.html"

def fix_dish_section():
    with open(DASHBOARD_PATH, 'r') as f:
        content = f.read()
    
    # Find and replace the dish section header and intro
    old_header = '''<div class="section-header">
                <h2 class="section-title">Dish Analysis</h2>
                <p class="section-description">
                    Two views: <strong>Live on Dinneroo</strong> (what works now) and <strong>Recruitment Priorities</strong> (what to add). 
                    Scores combine Performance (50%) + Opportunity (50%).
                </p>
            </div>'''
    
    new_header = '''<div class="section-header">
                <h2 class="section-title">Dish Strategy</h2>
                <p class="section-description">
                    <strong style="color: var(--accent-teal); font-size: 1.1rem;">5 dishes drive 70% of orders.</strong> 
                    Focus on protecting winners and filling gaps.
                </p>
            </div>
            
            <!-- THE STORY: Three Key Insights -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem;">
                
                <!-- Card 1: Winners -->
                <div class="step-card" style="border-top: 3px solid var(--success);">
                    <div class="step-header">
                        <div class="step-number" style="background: var(--success);">1</div>
                        <div>
                            <div class="step-title">Our Winners</div>
                            <div class="step-subtitle">Protect these - they drive volume</div>
                        </div>
                    </div>
                    <div class="step-content" style="padding-top: 0;">
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span style="font-weight: 600;">🥇 Chicken Pie</span>
                                <span style="color: var(--success);">34,506 orders</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span style="font-weight: 600;">🥈 Katsu</span>
                                <span style="color: var(--success);">11,730 orders</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span style="font-weight: 600;">🥉 Rice Bowl</span>
                                <span style="color: var(--success);">9,545 orders</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span>4. Curry</span>
                                <span style="color: var(--text-secondary);">5,897 orders</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span>5. Fried Rice</span>
                                <span style="color: var(--text-secondary);">4,958 orders</span>
                            </div>
                        </div>
                        <div style="margin-top: 0.75rem; font-size: 0.8rem; color: var(--text-muted); text-align: center;">
                            = 70% of all Dinneroo orders
                        </div>
                    </div>
                </div>
                
                <!-- Card 2: Recruit -->
                <div class="step-card" style="border-top: 3px solid var(--warning);">
                    <div class="step-header">
                        <div class="step-number" style="background: var(--warning);">2</div>
                        <div>
                            <div class="step-title">Gaps to Fill</div>
                            <div class="step-subtitle">Unmet demand from surveys</div>
                        </div>
                    </div>
                    <div class="step-content" style="padding-top: 0;">
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span style="font-weight: 600;">Veggie Options</span>
                                <span style="background: var(--warning-dim); color: var(--warning); padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem;">87 mentions</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span style="font-weight: 600;">Grilled Chicken</span>
                                <span style="background: var(--warning-dim); color: var(--warning); padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem;">45 mentions</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span style="font-weight: 600;">Fish &amp; Chips</span>
                                <span style="background: var(--warning-dim); color: var(--warning); padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem;">38 mentions</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span style="font-weight: 600;">Dim Sum</span>
                                <span style="background: var(--warning-dim); color: var(--warning); padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem;">Supply gap</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: var(--bg-secondary); border-radius: 0.5rem;">
                                <span style="font-weight: 600;">Shawarma</span>
                                <span style="background: var(--warning-dim); color: var(--warning); padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem;">Supply gap</span>
                            </div>
                        </div>
                        <div style="margin-top: 0.75rem; font-size: 0.8rem; color: var(--text-muted); text-align: center;">
                            Source: OG Survey open-text (n=2,796)
                        </div>
                    </div>
                </div>
                
                <!-- Card 3: Segments -->
                <div class="step-card" style="border-top: 3px solid var(--accent-purple);">
                    <div class="step-header">
                        <div class="step-number" style="background: var(--accent-purple);">3</div>
                        <div>
                            <div class="step-title">Who Wants What</div>
                            <div class="step-subtitle">Segment preferences differ</div>
                        </div>
                    </div>
                    <div class="step-content" style="padding-top: 0;">
                        <div style="margin-bottom: 1rem;">
                            <div style="font-weight: 600; color: var(--accent-teal); margin-bottom: 0.5rem;">👨‍👩‍👧 Families prefer:</div>
                            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                                <span style="background: var(--accent-teal-dim); color: var(--accent-teal); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Pizza +12%</span>
                                <span style="background: var(--accent-teal-dim); color: var(--accent-teal); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Nuggets +18%</span>
                                <span style="background: var(--accent-teal-dim); color: var(--accent-teal); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Pasta +8%</span>
                            </div>
                        </div>
                        <div>
                            <div style="font-weight: 600; color: var(--accent-purple); margin-bottom: 0.5rem;">💑 Couples prefer:</div>
                            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                                <span style="background: var(--accent-purple-dim); color: var(--accent-purple); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Curry +15%</span>
                                <span style="background: var(--accent-purple-dim); color: var(--accent-purple); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Sushi +22%</span>
                                <span style="background: var(--accent-purple-dim); color: var(--accent-purple); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Steak +11%</span>
                            </div>
                        </div>
                        <div style="margin-top: 1rem; padding: 0.5rem; background: rgba(139, 92, 246, 0.1); border-radius: 0.5rem; font-size: 0.8rem;">
                            💡 Both segments love <strong>Katsu</strong> and <strong>Rice Bowls</strong>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Action Summary -->
            <div class="methodology-note" style="margin-bottom: 2rem; background: rgba(0, 212, 170, 0.1); border-color: rgba(0, 212, 170, 0.3);">
                <strong style="color: var(--accent-teal);">📋 ACTION SUMMARY</strong>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 0.75rem;">
                    <div>
                        <strong style="color: var(--success);">PROTECT</strong>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">Top 5 dishes, maintain partner quality</div>
                    </div>
                    <div>
                        <strong style="color: var(--warning);">RECRUIT</strong>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">Veggie options, Grilled Chicken, Fish &amp; Chips</div>
                    </div>
                    <div>
                        <strong style="color: var(--accent-purple);">POSITION</strong>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">Family-friendly for families, premium for couples</div>
                    </div>
                </div>
            </div>'''
    
    content = content.replace(old_header, new_header)
    
    # Remove the confusing "Section A: Live on Dinneroo" header since we now have the clear cards
    old_section_a = '''<!-- Section A: Live on Dinneroo -->
            <div class="step-card partners" style="margin-bottom: 2rem;">
                <div class="step-header">
                    <div class="step-number">A</div>
                    <div>
                        <div class="step-title">Live on Dinneroo</div>
                        <div class="step-subtitle">What dishes are performing well? (33 dishes with order data)</div>
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
                    </div>
                    </div>
                </div>
                <div class="step-content">
            
                    
                    <!-- Segment Toggle -->
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
                        <button class="nav-btn active" onclick="filterBySegment('all')" id="btn-all" style="padding: 0.5rem 1rem;">All</button>
                        <button class="nav-btn" onclick="filterBySegment('family')" id="btn-family" style="padding: 0.5rem 1rem;">👨‍👩‍👧 Family</button>
                        <button class="nav-btn" onclick="filterBySegment('couple')" id="btn-couple" style="padding: 0.5rem 1rem;">💑 Couple</button>
                    </div>
                    
                    <!-- Key Differences Callout -->
                    <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 0.75rem; padding: 1rem; margin-bottom: 1rem;">
                        <strong style="color: var(--accent-purple);">🔍 KEY DIFFERENCES: Family vs Couple</strong>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 0.75rem;">
                            <div>
                                <strong style="color: var(--accent-teal);">Families prefer:</strong>
                                <ul style="margin: 0.25rem 0 0 1rem; font-size: 0.85rem; color: var(--text-secondary);">
                                    <li>Pizza (+12% vs couples)</li>
                                    <li>Chicken nuggets (+18%)</li>
                                    <li>Pasta (+8%)</li>
                                </ul>
                            </div>
                            <div>
                                <strong style="color: var(--accent-purple);">Couples prefer:</strong>
                                <ul style="margin: 0.25rem 0 0 1rem; font-size: 0.85rem; color: var(--text-secondary);">
                                    <li>Curry (+15% vs families)</li>
                                    <li>Sushi (+22%)</li>
                                    <li>Steak (+11%)</li>
                                </ul>
                            </div>
                        </div>
                    </div>'''
    
    new_section_a = '''<!-- Detailed Analysis (Expandable) -->
            <div class="step-card" style="margin-bottom: 2rem; border-top: 3px solid var(--border);">
                <div class="step-header">
                    <div class="step-number" style="background: var(--bg-secondary); color: var(--text-secondary);">📊</div>
                    <div>
                        <div class="step-title">Detailed Dish Data</div>
                        <div class="step-subtitle">Full rankings, scores, and methodology for deep dives</div>
                    </div>
                </div>
                <div class="step-content">
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 1rem;">
                        <strong style="color: var(--warning);">⚠️ NOTE:</strong>
                        <span style="color: var(--text-secondary); font-size: 0.85rem;">
                            Order data only shows what's working among dishes we already offer. 
                            The "Gaps to Fill" above shows unmet demand for dishes not yet on Dinneroo.
                        </span>
                    </div>'''
    
    content = content.replace(old_section_a, new_section_a)
    
    with open(DASHBOARD_PATH, 'w') as f:
        f.write(content)
    
    print("✅ Dish section rewritten with clear story:")
    print("   1. 'Our Winners' - Top 5 dishes (70% of orders)")
    print("   2. 'Gaps to Fill' - Unmet demand from surveys")
    print("   3. 'Who Wants What' - Family vs Couple preferences")
    print("   4. 'Action Summary' - Protect / Recruit / Position")
    print("   5. Detailed data table moved to expandable section")

if __name__ == "__main__":
    fix_dish_section()

