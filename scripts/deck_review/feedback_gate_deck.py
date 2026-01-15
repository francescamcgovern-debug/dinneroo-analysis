#!/usr/bin/env python3
"""
Generate a FEEDBACK_AGENT-style QA report for a PPTX deck vs Cursor truth.

Inputs:
  - DELIVERABLES/incoming/dish_analysis_colleague.pptx
  - DELIVERABLES/reports/deck_claims_raw.json
  - DELIVERABLES/reports/deck_vs_cursor_diff_table.csv
  - config/dashboard_metrics.json (for canonical counts & denominators)

Outputs:
  - DELIVERABLES/reports/deck_review_qa_report.md

This is an automated, best-effort QA pass. It is intentionally conservative:
anything we can't trace to an explicit source is flagged for review.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Issue:
    category: str
    severity: str  # Critical | Warning | Info
    slide: Optional[int]
    summary: str
    evidence: str
    recommendation: str


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _group_by(rows: List[Dict[str, str]], key: str) -> Dict[str, List[Dict[str, str]]]:
    out: Dict[str, List[Dict[str, str]]] = {}
    for r in rows:
        out.setdefault(r.get(key, ""), []).append(r)
    return out


def build_issues(
    diff_rows: List[Dict[str, str]],
    deck_raw: Dict[str, Any],
    dashboard_metrics: Dict[str, Any],
) -> List[Issue]:
    issues: List[Issue] = []

    # --- Data Accuracy (Critical): any DRIFT in diff table
    for r in diff_rows:
        if r.get("status") != "DRIFT":
            continue
        issues.append(
            Issue(
                category="Data Accuracy",
                severity="Critical",
                slide=int(r["slide_index"]) if r.get("slide_index") else None,
                summary=f"Deck claim drifts from Cursor truth: {r.get('deck_metric')}",
                evidence=f"Deck: {r.get('deck_text')} ({r.get('deck_value')}{r.get('deck_unit')}) vs Cursor: {r.get('cursor_value')} ({r.get('cursor_source')})",
                recommendation=r.get("recommendation") or "Update deck to match canonical values.",
            )
        )

    # --- Evidence Standards (Warning): percentages with no denominator/source
    for r in diff_rows:
        if r.get("status") != "UNVERIFIABLE":
            continue
        if (r.get("deck_unit") or "").strip() != "%":
            continue
        issues.append(
            Issue(
                category="Evidence Standards",
                severity="Warning",
                slide=int(r["slide_index"]) if r.get("slide_index") else None,
                summary="Percent claim lacks a clear denominator + traceable source export",
                evidence=f"Claim: {r.get('deck_text')} = {r.get('deck_value')}% (no established Cursor export linked).",
                recommendation=(
                    "Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance "
                    "to an exported file (or label as deck-calculated)."
                ),
            )
        )

    # --- Methodology Drift (Info): any DRIFT in methodology/scoring method
    for r in diff_rows:
        if r.get("status") != "DRIFT":
            continue
        if r.get("area") != "B_SCORING":
            continue
        issues.append(
            Issue(
                category="Methodology Drift",
                severity="Info",
                slide=int(r["slide_index"]) if r.get("slide_index") else None,
                summary="Scoring methodology described in deck differs from Cursor scoring config",
                evidence=f"Deck metric: {r.get('deck_metric')}; Cursor source: {r.get('cursor_source')}",
                recommendation=r.get("recommendation") or "Align deck methodology to config.",
            )
        )

    # --- Data Source Misuse (Warning): OG survey used as primary without triangulation cues
    # Best-effort: scan slide texts for "pre-launch" / "OG Survey" mentions.
    raw_slides = deck_raw.get("slides", [])
    for s in raw_slides:
        idx = int(s.get("slide_index", 0))
        text = (s.get("text_joined") or "").lower()
        if "pre-launch" in text or "og" in text and "survey" in text:
            issues.append(
                Issue(
                    category="Triangulation Violations",
                    severity="Warning",
                    slide=idx,
                    summary="Deck references pre-launch stated-preference signals; triangulation requirements must be explicit",
                    evidence="Deck mentions pre-launch research / suitability. Cursor rules require triangulation with behavioral data.",
                    recommendation="Add explicit triangulation note + avoid using OG/pre-launch as sole basis for recommendations.",
                )
            )

    # --- Conflicting Stories (Critical): multiple MVP definitions inside deck (heuristic)
    # Look for multiple distinct threshold triplets in the deck text.
    mvp_defs = []
    for s in raw_slides:
        t = s.get("text_joined") or ""
        if "zone mvp" in t.lower():
            mvp_defs.append((int(s.get("slide_index", 0)), t))
    # If there are multiple MVP-defining slides, flag to ensure consistent definition.
    if len(mvp_defs) >= 2:
        issues.append(
            Issue(
                category="Conflicting Stories",
                severity="Critical",
                slide=None,
                summary="Multiple slides define/describe Zone MVP; must ensure one consistent definition aligned to config",
                evidence="Zone MVP appears on multiple slides (e.g., summary slide and threshold slide).",
                recommendation="Pick the canonical definition from config/mvp_thresholds.json and ensure all slides use it consistently.",
            )
        )

    # --- Anti-Replication (Info): any deck slide with "As at" dates but no link to run date
    for s in raw_slides:
        idx = int(s.get("slide_index", 0))
        t = s.get("text_joined") or ""
        if "As at" in t:
            issues.append(
                Issue(
                    category="Anti-Replication",
                    severity="Info",
                    slide=idx,
                    summary="Deck uses an 'As at' date; ensure it matches data freshness and exported run date",
                    evidence=f"Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.",
                    recommendation="Add a footnote or appendix line citing data extract date and source file(s).",
                )
            )

    # Add a helpful note from dashboard_metrics about zone denominators
    zone_metrics = (dashboard_metrics.get("zone_metrics") or {})
    behavioral_zones = zone_metrics.get("behavioral_zones_with_orders", {}).get("value")
    supply_zones = zone_metrics.get("supply_zones_with_partners", {}).get("value")
    total_zones = zone_metrics.get("total_zones_in_system", {}).get("value")
    issues.append(
        Issue(
            category="Evidence Standards",
            severity="Info",
            slide=None,
            summary="Zone denominators must be explicit in any % statements",
            evidence=f"Canonical counts (dashboard_metrics.json): total={total_zones}, supply_with_partners={supply_zones}, live_with_orders={behavioral_zones}.",
            recommendation="For any % zone metric in the deck, explicitly state which denominator is used.",
        )
    )

    return issues


def write_report(path: Path, deck_path: str, issues: List[Issue]) -> None:
    # Summarize by category
    def status_for(sev: str) -> str:
        return "❌" if sev == "Critical" else ("⚠️" if sev == "Warning" else "ℹ️")

    categories = [
        ("Data Accuracy", "Critical"),
        ("Conflicting Stories", "Critical"),
        ("Evidence Standards", "Warning"),
        ("Triangulation Violations", "Warning"),
        ("Data Source Misuse", "Warning"),
        ("Survivorship Bias", "Warning"),
        ("Stated vs Revealed", "Warning"),
        ("Anti-Replication", "Info"),
        ("Methodology Drift", "Info"),
    ]

    # Count issues per category (presence-based)
    cat_counts: Dict[str, int] = {}
    for i in issues:
        cat_counts[i.category] = cat_counts.get(i.category, 0) + 1

    overall = "PASS"
    if any(i.severity == "Critical" for i in issues):
        overall = "CRITICAL ISSUES"
    elif any(i.severity == "Warning" for i in issues):
        overall = "NEEDS ATTENTION"

    lines: List[str] = []
    lines.append("# Feedback Report")
    lines.append("")
    lines.append(f"**Deliverable:** {deck_path}")
    lines.append(f"**Reviewed:** {date.today().isoformat()}")
    lines.append(f"**Overall Status:** {overall}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Category | Status | Issues |")
    lines.append("|----------|--------|--------|")
    for cat, sev in categories:
        n = cat_counts.get(cat, 0)
        s = status_for("Critical" if sev == "Critical" and n > 0 else ("Warning" if sev == "Warning" and n > 0 else "Info" if sev == "Info" and n > 0 else ""))
        status = "❌" if (sev in {"Critical", "Warning"} and n > 0) else "✅"
        lines.append(f"| {cat} | {status} | {n} |")

    lines.append("")
    lines.append("## Issues")
    lines.append("")

    # Order issues by severity then slide
    sev_rank = {"Critical": 0, "Warning": 1, "Info": 2}
    issues_sorted = sorted(issues, key=lambda x: (sev_rank.get(x.severity, 9), x.slide is None, x.slide or 0))
    for idx, issue in enumerate(issues_sorted, start=1):
        slide_str = f"Slide {issue.slide}" if issue.slide is not None else "All slides"
        lines.append(f"{idx}. **{issue.severity} — {issue.category}** ({slide_str}): {issue.summary}")
        lines.append(f"   - Evidence: {issue.evidence}")
        lines.append(f"   - Recommendation: {issue.recommendation}")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    deck_path = project_root / "DELIVERABLES" / "incoming" / "dish_analysis_colleague.pptx"
    deck_raw_path = project_root / "DELIVERABLES" / "reports" / "deck_claims_raw.json"
    diff_path = project_root / "DELIVERABLES" / "reports" / "deck_vs_cursor_diff_table.csv"
    dashboard_metrics_path = project_root / "config" / "dashboard_metrics.json"
    out_path = project_root / "DELIVERABLES" / "reports" / "deck_review_qa_report.md"

    deck_raw = _read_json(deck_raw_path)
    diff_rows = _read_csv(diff_path)
    dashboard_metrics = _read_json(dashboard_metrics_path)

    issues = build_issues(diff_rows, deck_raw, dashboard_metrics)
    write_report(out_path, str(deck_path.relative_to(project_root)), issues)
    print(f"Wrote: {out_path}")
    print(f"Issues: {len(issues)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

