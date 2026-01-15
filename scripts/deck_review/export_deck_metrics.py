#!/usr/bin/env python3
"""
Export a small set of deck-oriented metrics with explicit denominators.

Purpose:
  The colleague deck includes "% of active zones meeting X threshold" claims without a
  traceable export. This script produces a canonical export computed from established
  per-zone fields (docs/data/zone_mvp_status.json) WITHOUT recalculating MVP status.

Output:
  - DELIVERABLES/presentation_data/deck_metrics_zone_threshold_coverage.csv
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _zone_sets(zones: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Return standard denominators used in this repo (explicit zone-count types)."""
    total = zones
    supply = [z for z in zones if z.get("mvp_status") in {"Supply Only", "MVP Ready", "Near MVP", "Progressing", "Developing"}]
    live = [z for z in zones if (z.get("orders") or z.get("order_count") or 0) > 0]
    analysis = [z for z in live if z.get("health_score") is not None]  # best-effort proxy; not guaranteed
    return {
        "total_zones": total,
        "supply_zones": supply,
        "live_zones_with_orders": live,
        "analysis_zones_best_effort": analysis,
    }


def _coverage(zones: List[Dict[str, Any]], partners_min: int, cuisines_min: int, dishes_min: int) -> Dict[str, float]:
    denom = len(zones)
    if denom == 0:
        return {
            "denominator": 0,
            "pct_partners_min": 0.0,
            "pct_cuisines_min": 0.0,
            "pct_dishes_min": 0.0,
            "pct_all3": 0.0,
        }
    partners_ok = [z for z in zones if (z.get("partners") or 0) >= partners_min]
    cuisines_ok = [z for z in zones if (z.get("core_7_count") or 0) >= cuisines_min]
    dishes_ok = [z for z in zones if (z.get("total_dishes") or 0) >= dishes_min]
    all3_ok = [z for z in zones if (z.get("partners") or 0) >= partners_min and (z.get("core_7_count") or 0) >= cuisines_min and (z.get("total_dishes") or 0) >= dishes_min]
    return {
        "denominator": denom,
        "pct_partners_min": round(100 * len(partners_ok) / denom, 1),
        "pct_cuisines_min": round(100 * len(cuisines_ok) / denom, 1),
        "pct_dishes_min": round(100 * len(dishes_ok) / denom, 1),
        "pct_all3": round(100 * len(all3_ok) / denom, 1),
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    zones = _read_json(project_root / "docs" / "data" / "zone_mvp_status.json")
    thresholds = _read_json(project_root / "config" / "mvp_thresholds.json")

    crit = thresholds.get("mvp_criteria", {})
    partners_min = int(crit.get("partners_min", {}).get("value", 5))
    cuisines_min = int(crit.get("cuisines_min", {}).get("value", 5))
    dishes_min = int(crit.get("dishes_min", {}).get("value", 21))

    sets = _zone_sets(zones)
    out_path = project_root / "DELIVERABLES" / "presentation_data" / "deck_metrics_zone_threshold_coverage.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "zone_denominator_type",
                "denominator",
                "partners_min",
                "cuisines_min_core7",
                "dishes_min",
                "pct_partners_min",
                "pct_cuisines_min",
                "pct_dishes_min",
                "pct_all3",
                "source",
                "notes",
            ],
        )
        w.writeheader()
        for denom_type, zset in sets.items():
            cov = _coverage(zset, partners_min, cuisines_min, dishes_min)
            w.writerow(
                {
                    "zone_denominator_type": denom_type,
                    "denominator": cov["denominator"],
                    "partners_min": partners_min,
                    "cuisines_min_core7": cuisines_min,
                    "dishes_min": dishes_min,
                    "pct_partners_min": cov["pct_partners_min"],
                    "pct_cuisines_min": cov["pct_cuisines_min"],
                    "pct_dishes_min": cov["pct_dishes_min"],
                    "pct_all3": cov["pct_all3"],
                    "source": "docs/data/zone_mvp_status.json + config/mvp_thresholds.json",
                    "notes": "Computed from established per-zone fields; MVP status labels not recalculated.",
                }
            )

    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

