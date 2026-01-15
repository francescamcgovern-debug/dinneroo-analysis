#!/usr/bin/env python3
"""
Normalize raw deck slide text into a structured claim list tagged to:
  - A_MVP (thresholds/status/definitions)
  - B_SCORING (dish grouping/scoring methodology)

Outputs:
  - DELIVERABLES/reports/deck_claims_normalized.json
  - DELIVERABLES/reports/deck_claims_normalized.csv
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


AREA_A = "A_MVP"
AREA_B = "B_SCORING"


@dataclass
class Claim:
    claim_id: str
    slide_index: int
    area: str
    claim_type: str  # threshold | percent | definition | methodology | classification | narrative | metric
    metric: str
    value: Optional[float]
    unit: Optional[str]
    entity: Optional[str]
    text: str
    needs_visual_review: bool
    confidence: str  # high | medium | low


_RE_THRESHOLD = re.compile(r"\b(?P<value>\d+)\+\s*(?P<unit>px|partners?|cuisines?|dishes?)\b", re.IGNORECASE)
_RE_PERCENT = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*%")


def _slide_needs_visual_review(slide: Dict[str, Any]) -> bool:
    v = slide.get("visuals") or {}
    return (v.get("images_blip", 0) or 0) > 0 or (v.get("pics", 0) or 0) > 0


def _canonicalize_threshold_unit(unit: str) -> str:
    u = unit.lower()
    if u == "px":
        return "partners_min"
    if u.startswith("partner"):
        return "partners_min"
    if u.startswith("cuisine"):
        return "cuisines_min"
    if u.startswith("dish"):
        return "dishes_min"
    return u


_RE_FLAG_EMOJI = re.compile(r"[\U0001F1E6-\U0001F1FF]")  # regional indicator symbols (flags)


def _clean_dish_name(s: str) -> str:
    s = _RE_FLAG_EMOJI.sub("", s)
    s = s.replace("\u2019", "'")  # curly apostrophe
    return " ".join(s.strip().strip(".").split())


def _split_dish_list(s: str) -> List[str]:
    # Take content up to first sentence-ending period to avoid narrative tails.
    head = s.split(".", 1)[0]
    parts = [_clean_dish_name(p) for p in head.split(",")]
    return [p for p in parts if p]


def _infer_area(text: str) -> str:
    t = text.lower()
    if "mvp" in t and ("zone" in t or "partners" in t or "cuisines" in t or "dishes" in t):
        return AREA_A
    if "we propose a zone mvp" in t or "define family dinneroo mvp" in t:
        return AREA_A
    if "demand strength" in t or "cx preference" in t:
        return AREA_B
    if "dish prioritisation" in t or "prioritised dishes" in t or "prioritized dishes" in t:
        return AREA_B
    if "core drivers" in t or "demand boosters" in t or "preference drivers" in t or "test & learn" in t or "depriorit" in t:
        return AREA_B
    # Default: narrative around coverage/gaps is primarily used to motivate scoring/recruitment
    return AREA_B


def _claims_from_text(slide_index: int, slide_text: str, needs_visual_review: bool) -> List[Claim]:
    claims: List[Claim] = []
    area = _infer_area(slide_text)

    # Threshold patterns: "5+ partners", "4+ cuisines", "10+ dishes"
    for m in _RE_THRESHOLD.finditer(slide_text):
        v = float(m.group("value"))
        unit = m.group("unit")
        metric = _canonicalize_threshold_unit(unit)

        claims.append(
            Claim(
                claim_id=f"s{slide_index:02d}_threshold_{len(claims)+1}",
                slide_index=slide_index,
                area=AREA_A if metric in {"partners_min", "cuisines_min", "dishes_min"} else area,
                claim_type="threshold",
                metric=metric,
                value=v,
                unit="+",
                entity=None,
                text=m.group(0),
                needs_visual_review=needs_visual_review,
                confidence="high",
            )
        )

    # Percent patterns (note: many percentages are contextual; capture as raw)
    for m in _RE_PERCENT.finditer(slide_text):
        v = float(m.group("value"))
        snippet = m.group(0)
        inferred_metric = "percent_claim"
        if "repeat" in slide_text.lower() and "rate" in slide_text.lower():
            inferred_metric = "repeat_rate_percent"
        claims.append(
            Claim(
                claim_id=f"s{slide_index:02d}_percent_{len(claims)+1}",
                slide_index=slide_index,
                area=area,
                claim_type="percent",
                metric=inferred_metric,
                value=v,
                unit="%",
                entity=None,
                text=snippet,
                needs_visual_review=needs_visual_review,
                confidence="low",
            )
        )

    # High-signal slide-specific claims we know we care about (methodology text)
    t = slide_text.lower()
    if slide_index == 9 and "meet all 3" in t and "threshold" in t:
        # Slide 9 in this deck contains:
        # - a narrative "% meet all 3" and
        # - a 3-number block aligned to the 3 criteria (partners/cuisines/unique dishes)
        # - and then another "% meet all 3 thresholds" label.
        #
        # We interpret the last 4 percentages as:
        #   partners%, cuisines%, dishes%, all3%
        pct_vals = [float(x) for x in _RE_PERCENT.findall(slide_text)]
        if len(pct_vals) >= 4:
            partners_pct, cuisines_pct, dishes_pct = pct_vals[-4], pct_vals[-3], pct_vals[-2]
            all3_pct = pct_vals[-1]
            claims.extend(
                [
                    Claim(
                        claim_id=f"s{slide_index:02d}_coverage_partners_pct",
                        slide_index=slide_index,
                        area=AREA_A,
                        claim_type="percent",
                        metric="coverage_percent_partners_threshold",
                        value=partners_pct,
                        unit="%",
                        entity="zone",
                        text="Deck: % of active zones meeting partners threshold",
                        needs_visual_review=needs_visual_review,
                        confidence="medium",
                    ),
                    Claim(
                        claim_id=f"s{slide_index:02d}_coverage_cuisines_pct",
                        slide_index=slide_index,
                        area=AREA_A,
                        claim_type="percent",
                        metric="coverage_percent_cuisines_threshold",
                        value=cuisines_pct,
                        unit="%",
                        entity="zone",
                        text="Deck: % of active zones meeting cuisines threshold",
                        needs_visual_review=needs_visual_review,
                        confidence="medium",
                    ),
                    Claim(
                        claim_id=f"s{slide_index:02d}_coverage_dishes_pct",
                        slide_index=slide_index,
                        area=AREA_A,
                        claim_type="percent",
                        metric="coverage_percent_dishes_threshold",
                        value=dishes_pct,
                        unit="%",
                        entity="zone",
                        text="Deck: % of active zones meeting dishes threshold",
                        needs_visual_review=needs_visual_review,
                        confidence="medium",
                    ),
                    Claim(
                        claim_id=f"s{slide_index:02d}_coverage_all3_pct",
                        slide_index=slide_index,
                        area=AREA_A,
                        claim_type="percent",
                        metric="coverage_percent_all3_thresholds",
                        value=all3_pct,
                        unit="%",
                        entity="zone",
                        text="Deck: % of active zones meeting all 3 thresholds",
                        needs_visual_review=needs_visual_review,
                        confidence="medium",
                    ),
                ]
            )
    if "demand strength is calculated" in t and "indexed" in t and "average of 1" in t:
        claims.append(
            Claim(
                claim_id=f"s{slide_index:02d}_methodology_indexing",
                slide_index=slide_index,
                area=AREA_B,
                claim_type="methodology",
                metric="scoring_method_index_to_1_mean",
                value=None,
                unit=None,
                entity=None,
                text="Demand strength calculated by indexing metrics to avg=1 and taking mean; same for Cx preference (deck footnote).",
                needs_visual_review=needs_visual_review,
                confidence="medium",
            )
        )

    if "we define family dinneroo mvp" in t and "zone level" in t:
        claims.append(
            Claim(
                claim_id=f"s{slide_index:02d}_definition_zone_mvp",
                slide_index=slide_index,
                area=AREA_A,
                claim_type="definition",
                metric="zone_mvp_definition",
                value=None,
                unit=None,
                entity="zone",
                text="Deck defines zone MVP in terms of partners/cuisines/dishes thresholds.",
                needs_visual_review=needs_visual_review,
                confidence="high",
            )
        )

    if "we propose a zone mvp" in t:
        claims.append(
            Claim(
                claim_id=f"s{slide_index:02d}_proposal_zone_mvp",
                slide_index=slide_index,
                area=AREA_A,
                claim_type="definition",
                metric="zone_mvp_proposed_thresholds",
                value=None,
                unit=None,
                entity="zone",
                text="Deck proposes zone MVP thresholds (partners/cuisines/dishes).",
                needs_visual_review=needs_visual_review,
                confidence="high",
            )
        )

    if "we have prioritised dishes" in t and "demand signals" in t and "preference" in t:
        claims.append(
            Claim(
                claim_id=f"s{slide_index:02d}_definition_scoring_inputs",
                slide_index=slide_index,
                area=AREA_B,
                claim_type="definition",
                metric="scoring_inputs_list",
                value=None,
                unit=None,
                entity="dish",
                text="Deck lists demand indicators (avg sales per dish, % zones top3, open-text requests) and preference indicators (rating, meal satisfaction, repeat intent, family suitability).",
                needs_visual_review=needs_visual_review,
                confidence="high",
            )
        )

    return claims


def _extract_group_claims_from_runs(
    slide_index: int, text_runs: List[str], needs_visual_review: bool
) -> List[Claim]:
    """
    Best-effort extraction of dish group definitions + lists + coverage targets for slides
    that contain the group table (notably slide 7 and 10 in this deck).
    """
    claims: List[Claim] = []

    joined = " | ".join(text_runs)
    t = joined.lower()
    if "core drivers" not in t or "demand boosters" not in t:
        return claims

    # Slide 7: "Core Drivers (MVP = 100% coverage): Noodles..., Indian curry..."
    if slide_index == 7:
        # Find the run after the label, then parse dish list.
        labels = [
            ("Core Drivers", "dish_group_core_drivers", 100.0),
            ("Demand Boosters", "dish_group_demand_boosters", 75.0),
            ("Preference Drivers", "dish_group_preference_drivers", 50.0),
        ]
        for label, metric_prefix, cov in labels:
            try:
                i = next(i for i, r in enumerate(text_runs) if r.strip().startswith(label))
            except StopIteration:
                continue
            dish_run = text_runs[i + 1] if i + 1 < len(text_runs) else ""
            dishes = _split_dish_list(dish_run) if dish_run else []
            if dishes:
                claims.append(
                    Claim(
                        claim_id=f"s{slide_index:02d}_{metric_prefix}_dishes",
                        slide_index=slide_index,
                        area=AREA_B,
                        claim_type="classification",
                        metric=f"{metric_prefix}.dishes",
                        value=None,
                        unit=None,
                        entity="dish_type",
                        text=", ".join(dishes),
                        needs_visual_review=needs_visual_review,
                        confidence="medium",
                    )
                )
            claims.append(
                Claim(
                    claim_id=f"s{slide_index:02d}_{metric_prefix}_coverage_target",
                    slide_index=slide_index,
                    area=AREA_B,
                    claim_type="threshold",
                    metric=f"{metric_prefix}.coverage_target_percent",
                    value=cov,
                    unit="%",
                    entity="coverage",
                    text=f"{label} coverage target",
                    needs_visual_review=needs_visual_review,
                    confidence="high",
                )
            )
        return claims

    # Slide 10: table rows (use anchor keywords to find dish list runs)
    if slide_index == 10:
        anchors = [
            ("dish_group_core_drivers", "Noodles", 100.0),
            ("dish_group_demand_boosters", "Katsu", 75.0),
            ("dish_group_preference_drivers", "Shepherd", 50.0),
            ("dish_group_test_and_learn", "Pastry Pie", 0.0),
            ("dish_group_deprioritised", "Poke", None),
        ]
        for metric_prefix, anchor, cov in anchors:
            dish_run = ""
            for r in text_runs:
                if anchor.lower() in r.lower():
                    dish_run = r
                    break
            dishes = _split_dish_list(dish_run) if dish_run else []
            if dishes:
                claims.append(
                    Claim(
                        claim_id=f"s{slide_index:02d}_{metric_prefix}_dishes",
                        slide_index=slide_index,
                        area=AREA_B,
                        claim_type="classification",
                        metric=f"{metric_prefix}.dishes",
                        value=None,
                        unit=None,
                        entity="dish_type",
                        text=", ".join(dishes),
                        needs_visual_review=needs_visual_review,
                        confidence="medium",
                    )
                )
            if cov is not None:
                claims.append(
                    Claim(
                        claim_id=f"s{slide_index:02d}_{metric_prefix}_coverage_target",
                        slide_index=slide_index,
                        area=AREA_B,
                        claim_type="threshold",
                        metric=f"{metric_prefix}.coverage_target_percent",
                        value=float(cov),
                        unit="%",
                        entity="coverage",
                        text=f"{anchor} group coverage target",
                        needs_visual_review=needs_visual_review,
                        confidence="high",
                    )
                )

    return claims


def normalize(raw: Dict[str, Any]) -> List[Claim]:
    out: List[Claim] = []
    for slide in raw.get("slides", []):
        slide_index = int(slide["slide_index"])
        slide_text = slide.get("text_joined") or ""
        text_runs = slide.get("text_runs") or []
        needs_visual_review = _slide_needs_visual_review(slide)
        out.extend(_claims_from_text(slide_index, slide_text, needs_visual_review))
        out.extend(_extract_group_claims_from_runs(slide_index, text_runs, needs_visual_review))
    return out


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    raw_path = project_root / "DELIVERABLES" / "reports" / "deck_claims_raw.json"
    out_json = project_root / "DELIVERABLES" / "reports" / "deck_claims_normalized.json"
    out_csv = project_root / "DELIVERABLES" / "reports" / "deck_claims_normalized.csv"

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    claims = normalize(raw)

    out_json.write_text(json.dumps([asdict(c) for c in claims], indent=2), encoding="utf-8")

    fieldnames = list(asdict(claims[0]).keys()) if claims else [
        "claim_id",
        "slide_index",
        "area",
        "claim_type",
        "metric",
        "value",
        "unit",
        "entity",
        "text",
        "needs_visual_review",
        "confidence",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for c in claims:
            w.writerow(asdict(c))

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_csv}")
    print(f"Claims: {len(claims)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

