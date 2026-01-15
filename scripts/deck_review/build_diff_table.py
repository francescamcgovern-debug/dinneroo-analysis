#!/usr/bin/env python3
"""
Build a unified diff table comparing deck claims to Cursor source-of-truth.

Inputs:
  - DELIVERABLES/reports/deck_claims_normalized.json
  - config/mvp_thresholds.json
  - config/scoring_framework_v3.json
  - docs/data/zone_mvp_status.json (established; do not recompute MVP status)

Outputs:
  - DELIVERABLES/reports/deck_vs_cursor_diff_table.csv
  - DELIVERABLES/reports/deck_vs_cursor_gate_summary.md
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


AREA_A = "A_MVP"
AREA_B = "B_SCORING"


@dataclass
class DiffRow:
    area: str
    gate: str  # A or B
    slide_index: int
    claim_id: str
    claim_type: str
    deck_metric: str
    deck_value: Optional[float]
    deck_unit: Optional[str]
    deck_text: str
    cursor_value: Optional[str]
    cursor_unit: Optional[str]
    cursor_source: str
    status: str  # MATCH | DRIFT | UNVERIFIABLE | NOT_APPLICABLE
    recommendation: str
    notes: str


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _get_mvp_criteria(mvp_thresholds: Dict[str, Any]) -> Dict[str, float]:
    c = mvp_thresholds.get("mvp_criteria", {})
    return {
        "partners_min": float(c.get("partners_min", {}).get("value")),
        "cuisines_min": float(c.get("cuisines_min", {}).get("value")),
        "dishes_min": float(c.get("dishes_min", {}).get("value")),
        "rating_min": float(c.get("rating_min", {}).get("value")),
        "repeat_rate_min": float(c.get("repeat_rate_min", {}).get("value")),
    }


def _zone_mvp_status_counts(zone_mvp_status: List[Dict[str, Any]]) -> Dict[str, int]:
    # Summarize *existing* status labels; do not recompute status.
    counts: Dict[str, int] = {}
    for z in zone_mvp_status:
        s = z.get("mvp_status", "UNKNOWN")
        counts[s] = counts.get(s, 0) + 1
    return counts


def evaluate_gate_a(
    claims: List[Dict[str, Any]],
    mvp_thresholds: Dict[str, Any],
    zone_mvp_status: List[Dict[str, Any]],
) -> Tuple[List[DiffRow], str]:
    criteria = _get_mvp_criteria(mvp_thresholds)
    status_counts = _zone_mvp_status_counts(zone_mvp_status)

    rows: List[DiffRow] = []
    needs_fix = False

    for c in claims:
        if c.get("area") != AREA_A:
            continue
        metric = c.get("metric")
        ctype = c.get("claim_type")

        # Focus Gate A on MVP definition thresholds + coverage percentages.
        if metric not in {
            "partners_min",
            "cuisines_min",
            "dishes_min",
            "coverage_percent_partners_threshold",
            "coverage_percent_cuisines_threshold",
            "coverage_percent_dishes_threshold",
            "coverage_percent_all3_thresholds",
            "zone_mvp_definition",
            "zone_mvp_proposed_thresholds",
        }:
            continue

        deck_value = c.get("value")
        deck_unit = c.get("unit")
        cursor_value: Optional[str] = None
        cursor_unit: Optional[str] = None
        cursor_source = ""
        status = "UNVERIFIABLE"
        recommendation = ""
        notes = ""

        if metric in {"partners_min", "cuisines_min", "dishes_min"} and deck_value is not None:
            # Only treat these as MVP definition checks on the explicit MVP definition slides.
            # (Avoid misclassifying unrelated statements like "9+ dishes average per cuisine".)
            if int(c.get("slide_index", 0)) not in {7, 9}:
                continue
            truth = criteria.get(metric)
            cursor_value = str(int(truth)) if truth is not None and float(truth).is_integer() else str(truth)
            cursor_unit = deck_unit
            cursor_source = f"config/mvp_thresholds.json:mvp_criteria.{metric}.value"
            if truth is not None and float(deck_value) == float(truth):
                status = "MATCH"
                recommendation = "No change needed."
            else:
                status = "DRIFT"
                needs_fix = True
                recommendation = f"Update deck to use {metric}={cursor_value}{deck_unit or ''} (Cursor target)."
                # Add nuance for cuisines_min = 4 (Near MVP tier) vs MVP target = 5.
                if metric == "cuisines_min" and float(deck_value) == 4.0:
                    notes = "Note: 4 cuisines corresponds to 'Near MVP' tier in config, but MVP target cuisines_min is 5."

        elif metric.startswith("coverage_percent_"):
            # These are headline percentages in the deck. We do not currently map these to an established exported metric.
            cursor_source = "N/A (no established Cursor export found for this exact percentage claim)"
            status = "UNVERIFIABLE"
            recommendation = (
                "Specify denominator (zone count type: total/supply/live) and recompute from established "
                "Cursor outputs, or remove/label as deck-calculated."
            )
            notes = (
                f"Deck uses MVP thresholds partners>=5, cuisines>=4, dishes>=10; Cursor MVP targets are "
                f"partners>=5, cuisines>=5, dishes>=21 (so these %s likely need re-derivation). "
                f"Zone status tiers in Cursor are in docs/data/zone_mvp_status.json (counts by status: {status_counts})."
            )

        elif metric in {"zone_mvp_definition", "zone_mvp_proposed_thresholds"}:
            cursor_source = "config/mvp_thresholds.json + docs/data/zone_mvp_status.json (established status tiers)"
            status = "UNVERIFIABLE"
            recommendation = (
                "Ensure the deck's definition of zone MVP matches config/mvp_thresholds.json, and reference "
                "docs/data/zone_mvp_status.json for established status labels."
            )

        rows.append(
            DiffRow(
                area=AREA_A,
                gate="A",
                slide_index=int(c.get("slide_index", 0)),
                claim_id=str(c.get("claim_id")),
                claim_type=str(ctype),
                deck_metric=str(metric),
                deck_value=deck_value,
                deck_unit=deck_unit,
                deck_text=str(c.get("text", "")),
                cursor_value=cursor_value,
                cursor_unit=cursor_unit,
                cursor_source=cursor_source,
                status=status,
                recommendation=recommendation,
                notes=notes,
            )
        )

    verdict = "PASS" if not needs_fix else "NEEDS FIX"
    return rows, verdict


def _canonical_dish_groups_from_mvp_thresholds(mvp_thresholds: Dict[str, Any]) -> Dict[str, List[str]]:
    dt = (mvp_thresholds.get("dish_types") or {})
    return {
        "core_drivers": list((dt.get("core_drivers") or {}).get("dishes", [])),
        "preference_drivers": list((dt.get("preference_drivers") or {}).get("dishes", [])),
        "demand_boosters": list((dt.get("demand_boosters") or {}).get("dishes", [])),
        "deprioritised": list((dt.get("deprioritised") or {}).get("dishes", [])),
        "all_dish_types": list(dt.get("all_dish_types", [])),
    }


def _map_deck_dish_to_canonical(dish: str) -> str:
    # Small synonym map to align deck labels to canonical Anna taxonomy.
    # (This is for comparison only; do not change the underlying taxonomy.)
    d = dish.strip()
    mapping = {
        "Indian curry": "South Asian / Indian Curry",
        "Curry": "South Asian / Indian Curry",
        "Burritos": "Burrito / Burrito Bowl",
        "Burrito": "Burrito / Burrito Bowl",
        "Quesadillas": "Quesadilla",
    }
    return mapping.get(d, d)


def _canonical_group_for_dish(canonical_groups: Dict[str, List[str]], dish: str) -> Optional[str]:
    for group in ["core_drivers", "preference_drivers", "demand_boosters", "deprioritised"]:
        if dish in canonical_groups.get(group, []):
            return group
    if dish in canonical_groups.get("all_dish_types", []):
        return "other"
    return None


def evaluate_gate_b(
    claims: List[Dict[str, Any]],
    mvp_thresholds: Dict[str, Any],
    scoring_framework: Dict[str, Any],
) -> Tuple[List[DiffRow], str]:
    canonical_groups = _canonical_dish_groups_from_mvp_thresholds(mvp_thresholds)
    scoring_type = (scoring_framework.get("scoring_method") or {}).get("type")

    rows: List[DiffRow] = []
    needs_fix = False

    # 1) Core methodology drift check
    for c in claims:
        if c.get("metric") == "scoring_method_index_to_1_mean":
            status = "DRIFT" if scoring_type != "index_to_1_mean" else "MATCH"
            if status == "DRIFT":
                needs_fix = True
            rows.append(
                DiffRow(
                    area=AREA_B,
                    gate="B",
                    slide_index=int(c.get("slide_index", 0)),
                    claim_id=str(c.get("claim_id")),
                    claim_type=str(c.get("claim_type")),
                    deck_metric=str(c.get("metric")),
                    deck_value=c.get("value"),
                    deck_unit=c.get("unit"),
                    deck_text=str(c.get("text", "")),
                    cursor_value=str(scoring_type),
                    cursor_unit=None,
                    cursor_source="config/scoring_framework_v3.json:scoring_method.type",
                    status=status,
                    recommendation=(
                        "If the deck should reflect Cursor scoring, replace the indexing/mean method description with "
                        "percentile-based 1–5 scoring and list-specific weighted factors."
                        if status == "DRIFT"
                        else "No change needed."
                    ),
                    notes="",
                )
            )

    # 1b) Inputs/factors drift check
    for c in claims:
        if c.get("metric") != "scoring_inputs_list":
            continue
        needs_fix = True
        # Summarize the Cursor scoring factors across lists for comparison.
        lists = scoring_framework.get("lists") or {}
        factor_sets = {}
        for list_name, spec in lists.items():
            factors = (spec.get("factors") or {}).keys()
            factor_sets[list_name] = sorted(list(factors))
        rows.append(
            DiffRow(
                area=AREA_B,
                gate="B",
                slide_index=int(c.get("slide_index", 0)),
                claim_id=str(c.get("claim_id")),
                claim_type=str(c.get("claim_type")),
                deck_metric="scoring_inputs_list",
                deck_value=None,
                deck_unit=None,
                deck_text=str(c.get("text", "")),
                cursor_value=json.dumps(factor_sets, ensure_ascii=False),
                cursor_unit=None,
                cursor_source="config/scoring_framework_v3.json:lists.*.factors",
                status="DRIFT",
                recommendation=(
                    "If the deck should reflect Cursor scoring, replace the stated inputs with the segment-specific "
                    "factor sets and cite where each factor is sourced (survey/orders/latent demand)."
                ),
                notes="Deck describes a unified demand/preference indicator set; Cursor uses a three-list, segment-specific weighted framework.",
            )
        )

    # 2) Dish grouping alignment check (deck groups vs canonical dish_types in config/mvp_thresholds.json)
    deck_group_claims = [c for c in claims if str(c.get("metric", "")).endswith(".dishes") and "dish_group_" in str(c.get("metric", ""))]
    for c in deck_group_claims:
        deck_group_metric = str(c.get("metric"))
        deck_group_name = deck_group_metric.split(".", 1)[0].replace("dish_group_", "")
        deck_dishes_raw = str(c.get("text", "")).strip()
        deck_dishes = [d.strip() for d in deck_dishes_raw.split(",") if d.strip()]

        mismatches: List[str] = []
        unknowns: List[str] = []
        matches: List[str] = []

        for dd in deck_dishes:
            canonical = _map_deck_dish_to_canonical(dd)
            canonical_group = _canonical_group_for_dish(canonical_groups, canonical)
            if canonical_group is None:
                unknowns.append(dd)
                continue
            # Map deck group to an approximate canonical expectation (best-effort):
            deck_to_canonical = {
                "core_drivers": "core_drivers",
                "demand_boosters": "demand_boosters",
                "preference_drivers": "preference_drivers",
                "deprioritised": "deprioritised",
                "test_and_learn": None,  # not a canonical category in config/mvp_thresholds.json
            }.get(deck_group_name)
            if deck_to_canonical is None:
                unknowns.append(dd)
            elif canonical_group == deck_to_canonical:
                matches.append(dd)
            else:
                mismatches.append(f"{dd} (deck:{deck_group_name} vs canonical:{canonical_group})")

        if mismatches:
            needs_fix = True
            status = "DRIFT"
            rec = "Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy)."
        else:
            status = "UNVERIFIABLE" if unknowns else "MATCH"
            rec = (
                "No change needed."
                if status == "MATCH"
                else "Confirm taxonomy mapping for non-canonical dishes (or add mapping) before using these groupings in deck."
            )

        notes_parts = []
        if mismatches:
            notes_parts.append("Mismatches: " + "; ".join(mismatches))
        if unknowns:
            notes_parts.append("Not in canonical dish_types list: " + ", ".join(unknowns))

        rows.append(
            DiffRow(
                area=AREA_B,
                gate="B",
                slide_index=int(c.get("slide_index", 0)),
                claim_id=str(c.get("claim_id")),
                claim_type=str(c.get("claim_type")),
                deck_metric=deck_group_metric,
                deck_value=None,
                deck_unit=None,
                deck_text=deck_dishes_raw,
                cursor_value="See config/mvp_thresholds.json:dish_types.*",
                cursor_unit=None,
                cursor_source="config/mvp_thresholds.json:dish_types",
                status=status,
                recommendation=rec,
                notes=" | ".join(notes_parts),
            )
        )

    # 3) Dish-group coverage targets (deck introduces targets; Cursor config does not define these as a standard)
    coverage_claims = [c for c in claims if str(c.get("metric", "")).endswith(".coverage_target_percent")]
    for c in coverage_claims:
        rows.append(
            DiffRow(
                area=AREA_B,
                gate="B",
                slide_index=int(c.get("slide_index", 0)),
                claim_id=str(c.get("claim_id")),
                claim_type=str(c.get("claim_type")),
                deck_metric=str(c.get("metric")),
                deck_value=c.get("value"),
                deck_unit=c.get("unit"),
                deck_text=str(c.get("text", "")),
                cursor_value=None,
                cursor_unit=None,
                cursor_source="N/A (no standard Cursor config for dish group coverage targets)",
                status="UNVERIFIABLE",
                recommendation="If keeping these targets, add explicit justification + data linkage; otherwise remove or label as deck-specific targets.",
                notes="Cursor has MVP zone criteria and dish taxonomy groupings; it does not define % coverage targets per dish-group as a canonical standard.",
            )
        )

    verdict = "PASS" if not needs_fix else "NEEDS FIX"
    return rows, verdict


def write_csv(path: Path, rows: List[DiffRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))


def write_summary_md(path: Path, verdict_a: str, verdict_b: str, rows_a: List[DiffRow], rows_b: List[DiffRow]) -> None:
    def _count(rows: List[DiffRow], status: str) -> int:
        return sum(1 for r in rows if r.status == status)

    lines = []
    lines.append("# Deck vs Cursor Gate Summary")
    lines.append("")
    lines.append(f"- Deck: `DELIVERABLES/incoming/dish_analysis_colleague.pptx`")
    lines.append("")
    lines.append("## Gate A (MVP thresholds/status)")
    lines.append(f"- Verdict: **{verdict_a}**")
    lines.append(f"- MATCH: {_count(rows_a, 'MATCH')}, DRIFT: {_count(rows_a, 'DRIFT')}, UNVERIFIABLE: {_count(rows_a, 'UNVERIFIABLE')}")
    lines.append("")
    lines.append("## Gate B (dish scoring approach)")
    lines.append(f"- Verdict: **{verdict_b}**")
    lines.append(f"- MATCH: {_count(rows_b, 'MATCH')}, DRIFT: {_count(rows_b, 'DRIFT')}, UNVERIFIABLE: {_count(rows_b, 'UNVERIFIABLE')}")
    lines.append("")
    lines.append("## Output")
    lines.append("- Diff table: `DELIVERABLES/reports/deck_vs_cursor_diff_table.csv`")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]

    claims_path = project_root / "DELIVERABLES" / "reports" / "deck_claims_normalized.json"
    mvp_thresholds_path = project_root / "config" / "mvp_thresholds.json"
    scoring_framework_path = project_root / "config" / "scoring_framework_v3.json"
    zone_mvp_status_path = project_root / "docs" / "data" / "zone_mvp_status.json"

    out_csv = project_root / "DELIVERABLES" / "reports" / "deck_vs_cursor_diff_table.csv"
    out_md = project_root / "DELIVERABLES" / "reports" / "deck_vs_cursor_gate_summary.md"

    claims = load_json(claims_path)
    mvp_thresholds = load_json(mvp_thresholds_path)
    scoring_framework = load_json(scoring_framework_path)
    zone_mvp_status = load_json(zone_mvp_status_path)

    rows_a, verdict_a = evaluate_gate_a(claims, mvp_thresholds, zone_mvp_status)
    rows_b, verdict_b = evaluate_gate_b(claims, mvp_thresholds, scoring_framework)

    rows = rows_a + rows_b
    if not rows:
        raise RuntimeError("No diff rows produced; check claim extraction and filters.")

    write_csv(out_csv, rows)
    write_summary_md(out_md, verdict_a, verdict_b, rows_a, rows_b)

    print(f"Wrote: {out_csv}")
    print(f"Wrote: {out_md}")
    print(f"Gate A verdict: {verdict_a} (rows={len(rows_a)})")
    print(f"Gate B verdict: {verdict_b} (rows={len(rows_b)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

