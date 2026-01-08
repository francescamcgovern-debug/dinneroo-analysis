# Dashboard Feedback Fix Plan

**Plan ID:** ffea1812-fixes  
**Date:** January 8, 2026  
**Target:** `DELIVERABLES/dashboards/dinneroo_master_dashboard.html`

---

## Authoritative Data (from `docs/data/zone_mvp_status.json`)

### Zone Counts
| Type | Count | Description |
|------|-------|-------------|
| **Total Zones** | 1,306 | All configured zones (Anna's data) |
| **Supply Zones** | 434 | Zones with partners configured (235 Supply Only + 199 with activity) |
| **Zones with Orders** | 201 | Zones that generated orders during trial |
| **Statistical Analysis** | 197 | Zones with sufficient data for threshold analysis |

### MVP Status Distribution
| Status | Count | Description |
|--------|-------|-------------|
| **MVP Ready** | 70 | Meet all criteria (5+ partners, 5+ cuisines, 4.0+ rating) |
| **Near MVP** | 31 | Missing 1 cuisine gap |
| **Progressing** | 36 | 3-4 cuisines |
| **Developing** | 62 | 1-2 cuisines |
| **Supply Only** | 235 | Partners configured, no orders yet |
| **Not Started** | 872 | No Dinneroo partners |

### Near MVP Breakdown (What's Missing)
| Cuisine | Zones Needing |
|---------|---------------|
| Healthy | 31 |
| Indian | 25 |
| Mexican | 25 |
| Middle Eastern | 6 |
| British | 6 |

---

## Fix Implementation Plan

### 🔴 Critical Fix #1: Zone Count Legend

**Location:** After MVP Thresholds section header (line ~1010)

**Add this panel:**
```html
<!-- Zone Count Legend -->
<div class="methodology-note" style="margin-bottom: 1.5rem; background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3);">
    <strong style="color: var(--accent-blue);">📊 ZONE COUNT GUIDE</strong>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 0.75rem; text-align: center;">
        <div style="background: var(--bg-card); padding: 0.75rem; border-radius: 0.5rem;">
            <div style="font-size: 1.5rem; font-weight: 700;">1,306</div>
            <div style="font-size: 0.75rem; color: var(--text-secondary);">Total Zones</div>
            <div style="font-size: 0.65rem; color: var(--text-muted);">Anna's data</div>
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
```

**Also update these inconsistent references:**
- Line ~1520: Change "101 zones with orders" → "201 zones with orders"
- Line ~1635: Change source badge "101 Zones" → "201 Zones"

---

### 🔴 Critical Fix #2: MVP Progress Bar & Counts

**Updates needed:**

1. **Executive Summary MVP Progress** (line ~1025):
   - Change: `33/50 zones (66%)` → `70/50 zones (140%)`
   - Note: Target exceeded! Adjust messaging.

2. **Near MVP Breakdown** (line ~1041):
   - Change: `48 zones, 1 gap away` → `31 zones, 1 gap away`
   - Change breakdown: `32 need Indian, 10 need Mexican, 6 need British` 
   - To: `31 need Healthy, 25 need Indian, 25 need Mexican`

3. **Alerts Panel** (line ~1099):
   - Change: `48 Near MVP Zones` → `31 Near MVP Zones`
   - Update breakdown accordingly

4. **Zone KPI Card** (line ~1581):
   - Change: `id="mvp-ready-count">42` → `id="mvp-ready-count">70`

5. **Zone Progression Funnel** (lines ~1560-1570):
   - Update Near MVP: `48` → `31`
   - Update At MVP: `33` → `70`

6. **Threshold evidence** (line ~1586):
   - Change: `16% of zones with orders meet all MVP criteria (33 of 201)`
   - To: `35% of zones with orders meet all MVP criteria (70 of 201)`

---

### 🟡 Warning Fix #3: Role-Based Quick Start

**Location:** Add after header, before MVP Thresholds section

**Add this panel:**
```html
<!-- Role-Based Quick Start -->
<div class="step-card" style="margin-bottom: 2rem; border-top: 3px solid var(--accent-purple);">
    <div class="step-header">
        <div class="step-number" style="background: var(--accent-purple);">🎯</div>
        <div>
            <div class="step-title">Quick Start</div>
            <div class="step-subtitle">Jump to what matters for your role</div>
        </div>
    </div>
    <div class="step-content">
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem;">
            <button onclick="showSection('thresholds')" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center;">
                <div style="font-size: 1.5rem;">📊</div>
                <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Product</div>
                <div style="font-size: 0.7rem; color: var(--text-muted);">MVP thresholds & segments</div>
            </button>
            <button onclick="showSection('zones')" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center;">
                <div style="font-size: 1.5rem;">🗺️</div>
                <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Partner Ops</div>
                <div style="font-size: 0.7rem; color: var(--text-muted);">Zone priority queue</div>
            </button>
            <button onclick="showSection('dishes')" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center;">
                <div style="font-size: 1.5rem;">🍽️</div>
                <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Commercial</div>
                <div style="font-size: 0.7rem; color: var(--text-muted);">Dish recruitment</div>
            </button>
            <button onclick="showSection('gaps')" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center;">
                <div style="font-size: 1.5rem;">🎨</div>
                <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Marketing</div>
                <div style="font-size: 0.7rem; color: var(--text-muted);">Cuisine positioning</div>
            </button>
            <button onclick="scrollToExecutiveSummary()" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; cursor: pointer; text-align: center;">
                <div style="font-size: 1.5rem;">👔</div>
                <div style="font-weight: 600; color: var(--text-primary); margin-top: 0.25rem;">Leadership</div>
                <div style="font-size: 0.7rem; color: var(--text-muted);">Executive summary</div>
            </button>
        </div>
    </div>
</div>
```

**Also add JavaScript function:**
```javascript
function scrollToExecutiveSummary() {
    document.querySelector('.step-title:contains("Executive Summary")').scrollIntoView({behavior: 'smooth'});
}
```

---

### 🟡 Warning Fix #4: Add Missing Sample Sizes

**Updates needed:**

1. **Segment satisfaction** (Executive Summary, line ~1080):
   - Add to insight: `(Couples: 87.1% [n=205] vs Families: 85.6% [n=410])`

2. **Latent Demand Alert** (line ~1105):
   - Change: `87 Latent Demand Mentions for vegetarian options`
   - To: `87 Latent Demand Mentions for vegetarian options (OG Survey open-text, n=2,796)`

3. **Near MVP breakdown** (line ~1041):
   - Add evidence level: `🟢 VALIDATED (zone_mvp_status.json, Jan 2026)`

---

### 🟡 Warning Fix #5: Expand Survivorship Bias Warning

**Location:** Line ~1767 (Dishes section)

**Change from:**
```html
<div class="step-subtitle">What dishes are performing well? (33 dishes with order data) ⚠️ Survivorship bias applies</div>
```

**To:**
```html
<div class="step-subtitle">What dishes are performing well? (33 dishes with order data)</div>
</div>
</div>
<div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 1rem;">
    <strong style="color: var(--warning);">⚠️ SURVIVORSHIP BIAS NOTE:</strong>
    <span style="color: var(--text-secondary); font-size: 0.85rem;">
        Performance data shows what works among dishes we already offer — not what families want most. 
        Dishes not yet on Dinneroo (e.g., grilled chicken, fish & chips) may have strong unmet demand. 
        <strong>See Section B: Recruitment Priorities</strong> for latent demand analysis from open-text surveys.
    </span>
</div>
```

---

## Implementation Order

1. ✅ Read current dashboard HTML
2. 🔄 Apply Critical Fix #1 (Zone Count Legend)
3. 🔄 Apply Critical Fix #2 (MVP counts alignment)
4. 🔄 Apply Warning Fix #3 (Quick Start panel)
5. 🔄 Apply Warning Fix #4 (Sample sizes)
6. 🔄 Apply Warning Fix #5 (Survivorship warning)
7. 🔄 Run sync script to deploy

---

## Validation Checklist

After fixes, verify:
- [ ] Zone counts consistent (201 for "with orders" throughout)
- [ ] MVP Ready shows 70 everywhere
- [ ] Near MVP shows 31 everywhere
- [ ] Near MVP breakdown: Healthy 31, Indian 25, Mexican 25
- [ ] Quick Start panel visible at top
- [ ] Sample sizes on segment satisfaction
- [ ] Latent demand has source attribution
- [ ] Survivorship bias has full explanation

---

*Plan ready for implementation.*

