#!/usr/bin/env python3
"""
Extract Drop-off Dish/Cuisine Requests (Open Text)
==================================================
Purpose:
- Parse explicit dish/cuisine requests from the drop-off survey enriched file
- Map mentions to Anna's 24 dish types (for dish workbook integration)
- Summarize cuisine-level mentions separately (do NOT force into dish types)

Inputs:
- DATA/2_ENRICHED/DROPOFF_ENRICHED.csv
  Column: "What dishes and cuisines would you like to see more of? (please list as many as you can)"

Outputs:
- DATA/3_ANALYSIS/dropoff_dish_requests.csv
- DATA/3_ANALYSIS/dropoff_cuisine_requests.csv
- DATA/3_ANALYSIS/dropoff_requests_row_level.csv (audit)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

BASE_DIR = Path(__file__).parent.parent
ENRICHED_PATH = BASE_DIR / "DATA/2_ENRICHED/DROPOFF_ENRICHED.csv"
OUT_DIR = BASE_DIR / "DATA/3_ANALYSIS"

REQUESTS_COL = "What dishes and cuisines would you like to see more of? (please list as many as you can)"


def _norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _match_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(p, text) for p in patterns)


def _dedupe_preserve_order(xs: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def dish_type_patterns() -> Dict[str, List[str]]:
    """
    Conservative keyword patterns for Anna's 24 dish types.
    Notes:
    - This is intentionally conservative: it maps explicit dish mentions only.
    - Cuisine-only mentions (e.g., "Chinese") are handled separately.
    """
    return {
        "Rice Bowl": [r"\brice\s*bowl(s)?\b"],
        "Pasta": [r"\bpasta\b", r"\bspaghetti\b", r"\bpenne\b", r"\blinguine\b"],
        "Grain Bowl": [r"\bgrain\s*bowl(s)?\b", r"\bgrain\bowl\b"],
        "Noodles": [r"\bnoodle(s)?\b", r"\bramen\b", r"\budon\b", r"\byaki\s*soba\b"],
        "South Asian / Indian Curry": [r"\bcurry('?s)?\b", r"\btikka\b", r"\bmasala\b", r"\bkorma\b", r"\bvindaloo\b", r"\bmadras\b", r"\bjalfrezi\b"],
        "East Asian Curry": [r"\bthai\s*curry\b", r"\bgreen\s*curry\b", r"\bred\s*curry\b", r"\bmassaman\b", r"\bpanang\b", r"\braisu\b", r"\braisu\s*curry\b"],
        "Katsu": [r"\bkatsu\b"],
        "Biryani": [r"\bbiryani\b", r"\bbiriyani\b", r"\bbiriani\b"],
        "Pizza": [r"\bpizza\b"],
        "Fried Rice": [r"\bfried\s*rice\b", r"\begg\s*fried\s*rice\b"],
        "Protein & Veg": [r"\bprotein\s*&\s*veg\b", r"\bprotein\b", r"\bgrilled\s*chicken\b", r"\bchicken,\s*rice\s*and\s*veg\b"],
        "Chilli": [r"\bchilli\b", r"\bchili\b", r"\bcon\s*carne\b"],
        "Fajitas": [r"\bfajita(s)?\b"],
        "Lasagne": [r"\blasagn(e|a)\b"],
        "Shawarma": [r"\bshawarma\b", r"\bkebab\b", r"\bdoner\b"],
        "Tacos": [r"\btaco(s)?\b"],
        "Burrito / Burrito Bowl": [r"\bburrito(s)?\b", r"\bburrito\s*bowl(s)?\b"],
        "Quesadilla": [r"\bquesadilla(s)?\b"],
        "Nachos": [r"\bnacho(s)?\b"],
        "Pho": [r"\bpho\b"],
        "Poke": [r"\bpoke\b"],
        "Shepherd's Pie": [r"shepherd'?s\s*pie", r"\bcottage\s*pie\b"],
        "Sushi": [r"\bsushi\b", r"\bmaki\b", r"\bnigiri\b"],
        "Other": [],
    }


def cuisine_patterns() -> Dict[str, List[str]]:
    """
    Cuisine-level mentions for separate reporting.
    This includes both Core 7 and notable sub-cuisine signals (e.g., Chinese).
    """
    return {
        "Chinese": [r"\bchinese\b", r"\bdim\s*sum\b"],
        "Indian": [r"\bindian\b", r"\bcurry\b", r"\bbiryani\b", r"\btikka\b"],
        "Italian": [r"\bitalian\b", r"\bpasta\b", r"\blasagn(e|a)\b", r"\bpizza\b", r"\bspaghetti\b"],
        "Mexican": [r"\bmexican\b", r"\btaco(s)?\b", r"\bfajita(s)?\b", r"\bburrito(s)?\b", r"\bwahaca\b"],
        "Middle Eastern": [r"\bmiddle\s*eastern\b", r"\bturkish\b", r"\blebanese\b", r"\bkebab\b", r"\bshawarma\b"],
        "British": [r"\bbritish\b", r"\bfish\s*&?\s*chips\b", r"\broast\b", r"\bcottage\s*pie\b", r"shepherd'?s\s*pie"],
        "Asian (general)": [r"\basian\b", r"\bthai\b", r"\bjapanese\b", r"\bkorean\b", r"\bvietnamese\b", r"\bmalaysian\b"],
        "Thai": [r"\bthai\b", r"\bpad\s*thai\b"],
        "Japanese": [r"\bjapanese\b", r"\bsushi\b", r"\bkatsu\b"],
        "Korean": [r"\bkorean\b"],
        "Vietnamese": [r"\bvietnamese\b", r"\bpho\b", r"\bbanh\s*mi\b"],
        "Malaysian": [r"\bmalaysian\b", r"\blaksa\b"],
        "Burgers / Chicken": [r"\bburger(s)?\b", r"\bwings\b", r"\bkfc\b", r"nando'?s"],
        "Healthy / Veg": [r"\bhealthy\b", r"\bsalad(s)?\b", r"\bvegetarian\b", r"\bvegan\b"],
        "Caribbean / African": [r"\bcaribbean\b", r"\bafrican\b"],
    }


def signal_from_count(count: int) -> str:
    if count <= 0:
        return "None"
    if count <= 2:
        return "Low"
    if count <= 5:
        return "Medium"
    return "High"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ENRICHED_PATH, low_memory=False)
    if REQUESTS_COL not in df.columns:
        raise ValueError(f"Column not found: {REQUESTS_COL!r} in {ENRICHED_PATH}")

    responses = df[REQUESTS_COL].dropna().astype(str).tolist()
    total = len(responses)

    dish_pats = dish_type_patterns()
    cuisine_pats = cuisine_patterns()

    dish_counts = {k: 0 for k in dish_pats.keys()}
    cuisine_counts = {k: 0 for k in cuisine_pats.keys()}

    audit_rows: List[dict] = []

    for raw in responses:
        text = _norm_text(raw)

        matched_dishes: List[str] = []
        for dish_type, pats in dish_pats.items():
            if not pats:
                continue
            if _match_any(text, pats):
                matched_dishes.append(dish_type)

        matched_cuisines: List[str] = []
        for cuisine, pats in cuisine_pats.items():
            if _match_any(text, pats):
                matched_cuisines.append(cuisine)

        matched_dishes = _dedupe_preserve_order(matched_dishes)
        matched_cuisines = _dedupe_preserve_order(matched_cuisines)

        for d in matched_dishes:
            dish_counts[d] += 1
        for c in matched_cuisines:
            cuisine_counts[c] += 1

        audit_rows.append(
            {
                "response_text": raw,
                "matched_dish_types": "; ".join(matched_dishes) if matched_dishes else "",
                "matched_cuisines": "; ".join(matched_cuisines) if matched_cuisines else "",
                "is_cuisine_only": bool(matched_cuisines) and not bool(matched_dishes),
                "is_unmapped": (not matched_cuisines) and (not matched_dishes),
            }
        )

    # Dish-level summary
    dish_df = (
        pd.DataFrame(
            [
                {
                    "dish_type": k,
                    "dropoff_requests": int(v),
                    "dropoff_request_share": (v / total) if total else 0.0,
                    "dropoff_demand_signal": signal_from_count(int(v)),
                }
                for k, v in dish_counts.items()
            ]
        )
        .sort_values(["dropoff_requests", "dish_type"], ascending=[False, True])
        .reset_index(drop=True)
    )

    cuisine_df = (
        pd.DataFrame(
            [
                {
                    "cuisine": k,
                    "mentions": int(v),
                    "mention_share": (v / total) if total else 0.0,
                }
                for k, v in cuisine_counts.items()
            ]
        )
        .sort_values(["mentions", "cuisine"], ascending=[False, True])
        .reset_index(drop=True)
    )

    audit_df = pd.DataFrame(audit_rows)

    dish_df.to_csv(OUT_DIR / "dropoff_dish_requests.csv", index=False)
    cuisine_df.to_csv(OUT_DIR / "dropoff_cuisine_requests.csv", index=False)
    audit_df.to_csv(OUT_DIR / "dropoff_requests_row_level.csv", index=False)

    print(f"Drop-off responses parsed: {total}")
    print(f"Wrote: {OUT_DIR / 'dropoff_dish_requests.csv'}")
    print(f"Wrote: {OUT_DIR / 'dropoff_cuisine_requests.csv'}")
    print(f"Wrote: {OUT_DIR / 'dropoff_requests_row_level.csv'}")


if __name__ == "__main__":
    main()

