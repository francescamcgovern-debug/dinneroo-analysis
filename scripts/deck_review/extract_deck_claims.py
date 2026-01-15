#!/usr/bin/env python3
"""
Extract slide text and basic visual inventory from a PPTX into JSON.

Outputs:
  - DELIVERABLES/reports/deck_claims_raw.json

Notes:
  - This extracts selectable text (a:t nodes) and notes (if present).
  - It also records counts of embedded images/charts per slide so we can
    identify slides that may contain non-extractable numeric claims.
"""

from __future__ import annotations

import json
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
}


@dataclass
class SlideExtraction:
    slide_index: int
    slide_path: str
    text_runs: List[str]
    text_joined: str
    notes_joined: str
    visuals: Dict[str, int]


def _get_text_runs(xml_bytes: bytes) -> List[str]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    runs = []
    for node in root.findall(".//a:t", NS):
        if node.text:
            s = node.text.strip()
            if s:
                runs.append(s)
    return runs


def _count_visuals(xml_bytes: bytes) -> Dict[str, int]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return {"images_blip": 0, "pics": 0, "charts": 0, "graphic_frames": 0}
    blips = root.findall(".//a:blip", NS)
    pics = root.findall(".//p:pic", NS)
    charts = root.findall(".//c:chart", NS)
    graphic_frames = root.findall(".//p:graphicFrame", NS)
    return {
        "images_blip": len(blips),
        "pics": len(pics),
        "charts": len(charts),
        "graphic_frames": len(graphic_frames),
    }


def _slide_targets_in_order(z: zipfile.ZipFile) -> List[str]:
    """
    Return slide XML paths in presentation order using ppt/presentation.xml.
    Fallback: sort by slideN.
    """
    try:
        pres_xml = z.read("ppt/presentation.xml")
        pres_root = ET.fromstring(pres_xml)
        rels_xml = z.read("ppt/_rels/presentation.xml.rels")
        rels_root = ET.fromstring(rels_xml)
    except KeyError:
        pres_root = None
        rels_root = None

    rid_to_target: Dict[str, str] = {}
    if rels_root is not None:
        for rel in rels_root.findall("pkgrel:Relationship", NS):
            rid = rel.attrib.get("Id")
            target = rel.attrib.get("Target")
            if rid and target:
                rid_to_target[rid] = target

    slide_targets: List[str] = []
    if pres_root is not None:
        sldIdLst = pres_root.find("p:sldIdLst", NS)
        if sldIdLst is not None:
            for sldId in sldIdLst.findall("p:sldId", NS):
                rid = sldId.attrib.get(f"{{{NS['r']}}}id")
                target = rid_to_target.get(rid or "")
                if target:
                    slide_targets.append("ppt/" + target.lstrip("/"))

    if slide_targets:
        return slide_targets

    # Fallback order: slide1.xml, slide2.xml, ...
    def slide_num(name: str) -> int:
        stem = Path(name).stem
        digits = "".join([c for c in stem if c.isdigit()])
        return int(digits) if digits else 0

    slides = [n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
    return sorted(slides, key=slide_num)


def extract_pptx(pptx_path: Path) -> List[SlideExtraction]:
    with zipfile.ZipFile(pptx_path) as z:
        slide_paths = _slide_targets_in_order(z)
        slides: List[SlideExtraction] = []
        for idx, slide_path in enumerate(slide_paths, start=1):
            slide_xml = z.read(slide_path)
            text_runs = _get_text_runs(slide_xml)
            visuals = _count_visuals(slide_xml)

            notes_joined = ""
            notes_path = f"ppt/notesSlides/notesSlide{idx}.xml"
            if notes_path in z.namelist():
                notes_runs = _get_text_runs(z.read(notes_path))
                notes_joined = " | ".join(notes_runs)

            slides.append(
                SlideExtraction(
                    slide_index=idx,
                    slide_path=slide_path,
                    text_runs=text_runs,
                    text_joined=" | ".join(text_runs),
                    notes_joined=notes_joined,
                    visuals=visuals,
                )
            )
        return slides


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    pptx_path = project_root / "DELIVERABLES" / "incoming" / "dish_analysis_colleague.pptx"
    out_path = project_root / "DELIVERABLES" / "reports" / "deck_claims_raw.json"

    if not pptx_path.exists():
        raise FileNotFoundError(f"Deck not found at {pptx_path}")

    slides = extract_pptx(pptx_path)
    payload: Dict[str, Any] = {
        "deck": {
            "filename": pptx_path.name,
            "path": str(pptx_path.relative_to(project_root)),
        },
        "slide_count": len(slides),
        "slides": [asdict(s) for s in slides],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

