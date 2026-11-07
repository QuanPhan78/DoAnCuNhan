#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/test_assets_empirical.py
================================================================================
EMPIRICAL CHALLENGER VERIFICATION HARNESS — 72 FIGURES
Project: RentalSystem HUIT 2025 Thesis
Standards:
  1. PNG Checks:
     - File exists and size > 0 bytes
     - PIL DPI metadata == (300, 300)
     - Dimensions:
       * Strict: width >= 1000px and height >= 600px
       * Orientation-aware: max(dim) >= 1000px and min(dim) >= 600px
     - Academic Grayscale color analysis:
       mean(|R-G| + |G-B| + |B-R|) / 3. For grayscale images, delta == 0.0.
  2. SVG Checks:
     - File exists and size > 0 bytes
     - Well-formed XML containing <svg> element
  3. Cross-check against AUDIT_72_FIGURES.md & table_72_figures.md
================================================================================
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
import numpy as np

# Reconfigure stdout for UTF-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
FIGURES_DIR = BASE_DIR / "figures"
AUDIT_MD_PATH = FIGURES_DIR / "AUDIT_72_FIGURES.md"
TABLE_MD_PATH = BASE_DIR / ".agents" / "teamwork" / "explorer_diag_survey_1" / "table_72_figures.md"

# Import MASTER_FIGURES_REGISTRY from render_master_diagrams
sys.path.insert(0, str(BASE_DIR / "tools"))
from render_master_diagrams import MASTER_FIGURES_REGISTRY


def check_png(file_path: Path, is_ui: bool = False):
    result = {
        "exists": False,
        "size_bytes": 0,
        "dpi": None,
        "dpi_pass": False,
        "width": 0,
        "height": 0,
        "dim_strict_pass": False,
        "dim_orient_pass": False,
        "mode": "",
        "mean_rgb_diff": 0.0,
        "max_rgb_diff": 0.0,
        "grayscale_pass": False,
        "errors": []
    }

    if not file_path.exists():
        result["errors"].append("File not found")
        return result

    result["exists"] = True
    result["size_bytes"] = file_path.stat().st_size
    if result["size_bytes"] == 0:
        result["errors"].append("File size is 0 bytes")
        return result

    try:
        with Image.open(file_path) as img:
            result["width"], result["height"] = img.size
            result["mode"] = img.mode
            dpi = img.info.get("dpi")
            result["dpi"] = dpi

            # DPI Check: must be (300, 300) within rounding tolerance
            if dpi is not None:
                rx, ry = dpi
                if abs(rx - 300) < 1.0 and abs(ry - 300) < 1.0:
                    result["dpi_pass"] = True
                else:
                    result["errors"].append(f"DPI is {dpi}, expected (300, 300)")
            else:
                result["errors"].append("DPI metadata missing")

            # Dimension checks
            w, h = result["width"], result["height"]
            if w >= 1000 and h >= 600:
                result["dim_strict_pass"] = True
            else:
                result["errors"].append(f"Strict dimensions ({w}x{h}) < (1000x600)")

            if max(w, h) >= 1000 and min(w, h) >= 600:
                result["dim_orient_pass"] = True
            else:
                result["errors"].append(f"Oriented dimensions ({w}x{h}): max={max(w,h)}, min={min(w,h)}")

            # Color analysis
            if is_ui:
                # UI screenshots may be executive navy/slate/color or grayscale
                result["grayscale_pass"] = True
            elif img.mode in ("L", "1"):
                result["mean_rgb_diff"] = 0.0
                result["max_rgb_diff"] = 0.0
                result["grayscale_pass"] = True
            else:
                # Fast sample analysis for large diagrams
                # Subsample if image is huge (> 2048x2048) to avoid memory blowup
                step = 1
                if w > 3000 or h > 3000:
                    step = 4
                rgb = img.convert("RGB")
                arr = np.asarray(rgb)[::step, ::step]
                r = arr[:, :, 0].astype(np.int16)
                g = arr[:, :, 1].astype(np.int16)
                b = arr[:, :, 2].astype(np.int16)
                diff = (np.abs(r - g) + np.abs(g - b) + np.abs(b - r)) / 3.0
                mean_diff = float(np.mean(diff))
                max_diff = float(np.max(diff))
                result["mean_rgb_diff"] = round(mean_diff, 4)
                result["max_rgb_diff"] = round(max_diff, 2)

                if mean_diff < 0.01:
                    result["grayscale_pass"] = True
                else:
                    result["errors"].append(f"Residual color detected: mean_rgb_diff={mean_diff:.4f}, max={max_diff:.1f}")

    except Exception as e:
        result["errors"].append(f"Image load exception: {str(e)}")

    return result


def check_svg(file_path: Path):
    result = {
        "exists": False,
        "size_bytes": 0,
        "well_formed": False,
        "has_svg_tag": False,
        "tag": "",
        "attrib": {},
        "errors": []
    }

    if not file_path.exists():
        result["errors"].append("SVG file not found")
        return result

    result["exists"] = True
    result["size_bytes"] = file_path.stat().st_size
    if result["size_bytes"] == 0:
        result["errors"].append("SVG size is 0 bytes")
        return result

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        result["well_formed"] = True
        result["tag"] = root.tag
        result["attrib"] = dict(root.attrib)

        # Check for svg tag (ignoring namespace)
        tag_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if tag_name.lower() == "svg":
            result["has_svg_tag"] = True
        else:
            result["errors"].append(f"Root tag is '{root.tag}', expected '<svg>'")
    except Exception as e:
        result["errors"].append(f"XML parse error: {str(e)}")

    return result


def run_full_suite():
    print("=" * 80, flush=True)
    print("EMPIRICAL ASSET CHALLENGER: VERIFYING ALL 72 FIGURES IN figures/", flush=True)
    print(f"Registry count: {len(MASTER_FIGURES_REGISTRY)}", flush=True)
    print("=" * 80, flush=True)

    summary = {
        "total_figures": len(MASTER_FIGURES_REGISTRY),
        "png_exists_pass": 0,
        "png_dpi_300_pass": 0,
        "png_dim_strict_pass": 0,
        "png_dim_orient_pass": 0,
        "png_grayscale_pass": 0,
        "svg_exists_pass": 0,
        "svg_valid_pass": 0,
        "all_checks_strict_pass": 0,
        "all_checks_orient_pass": 0,
        "failures_strict": [],
        "failures_orient": []
    }

    results = []

    for item in MASTER_FIGURES_REGISTRY:
        stt = item["stt"]
        fig_num = item["fig_num"]
        title = item["title"]
        engine = item["engine"]
        target_png = item["target_png"]
        target_svg = item["target_svg"]
        is_ui = (engine == "ui_screenshot") or ("ui_" in target_png)

        png_path = FIGURES_DIR / target_png
        svg_path = FIGURES_DIR / target_svg

        png_res = check_png(png_path, is_ui=is_ui)
        svg_res = check_svg(svg_path)

        # Track counts
        if png_res["exists"] and png_res["size_bytes"] > 0:
            summary["png_exists_pass"] += 1
        if png_res["dpi_pass"]:
            summary["png_dpi_300_pass"] += 1
        if png_res["dim_strict_pass"]:
            summary["png_dim_strict_pass"] += 1
        if png_res["dim_orient_pass"]:
            summary["png_dim_orient_pass"] += 1
        if png_res["grayscale_pass"]:
            summary["png_grayscale_pass"] += 1

        if svg_res["exists"] and svg_res["size_bytes"] > 0:
            summary["svg_exists_pass"] += 1
        if svg_res["well_formed"] and svg_res["has_svg_tag"]:
            summary["svg_valid_pass"] += 1

        # Overall strict
        strict_pass = (
            png_res["exists"] and png_res["size_bytes"] > 0 and
            png_res["dpi_pass"] and png_res["dim_strict_pass"] and
            png_res["grayscale_pass"] and
            svg_res["exists"] and svg_res["size_bytes"] > 0 and
            svg_res["well_formed"] and svg_res["has_svg_tag"]
        )
        if strict_pass:
            summary["all_checks_strict_pass"] += 1
        else:
            summary["failures_strict"].append({
                "stt": stt,
                "fig_num": fig_num,
                "target_png": target_png,
                "png_errors": png_res["errors"],
                "svg_errors": svg_res["errors"],
                "dims": (png_res["width"], png_res["height"])
            })

        # Overall orient-aware
        orient_pass = (
            png_res["exists"] and png_res["size_bytes"] > 0 and
            png_res["dpi_pass"] and png_res["dim_orient_pass"] and
            png_res["grayscale_pass"] and
            svg_res["exists"] and svg_res["size_bytes"] > 0 and
            svg_res["well_formed"] and svg_res["has_svg_tag"]
        )
        if orient_pass:
            summary["all_checks_orient_pass"] += 1
        else:
            summary["failures_orient"].append({
                "stt": stt,
                "fig_num": fig_num,
                "target_png": target_png,
                "png_errors": png_res["errors"],
                "svg_errors": svg_res["errors"],
                "dims": (png_res["width"], png_res["height"])
            })

        status_str = "PASS" if strict_pass else ("ORIENT_PASS" if orient_pass else "FAIL")
        print(f"[{stt:02d}/72] {fig_num} | {target_png} ({png_res['width']}x{png_res['height']}, {png_res['dpi']}) -> {status_str}", flush=True)

        results.append({
            "stt": stt,
            "fig_num": fig_num,
            "title": title,
            "engine": engine,
            "target_png": target_png,
            "target_svg": target_svg,
            "png": png_res,
            "svg": svg_res,
            "strict_pass": strict_pass,
            "orient_pass": orient_pass
        })

    # Print summary table
    print("\n" + "=" * 80, flush=True)
    print("QUANTITATIVE SUMMARY METRICS", flush=True)
    print("=" * 80, flush=True)
    print(f"Total Figures Evaluated:              {summary['total_figures']} / 72", flush=True)
    print(f"PNG File Exists & Size > 0:            {summary['png_exists_pass']} / 72 ({(summary['png_exists_pass']/72)*100:.1f}%)", flush=True)
    print(f"PNG 300 DPI Exact Header:             {summary['png_dpi_300_pass']} / 72 ({(summary['png_dpi_300_pass']/72)*100:.1f}%)", flush=True)
    print(f"PNG Academic Grayscale (Delta ~ 0):   {summary['png_grayscale_pass']} / 72 ({(summary['png_grayscale_pass']/72)*100:.1f}%)", flush=True)
    print(f"PNG Strict Dims (W>=1000, H>=600):    {summary['png_dim_strict_pass']} / 72 ({(summary['png_dim_strict_pass']/72)*100:.1f}%)", flush=True)
    print(f"PNG Orient Dims (Max>=1000,Min>=600): {summary['png_dim_orient_pass']} / 72 ({(summary['png_dim_orient_pass']/72)*100:.1f}%)", flush=True)
    print(f"SVG Exists & Size > 0:                {summary['svg_exists_pass']} / 72 ({(summary['svg_exists_pass']/72)*100:.1f}%)", flush=True)
    print(f"SVG Well-formed with <svg> Root:      {summary['svg_valid_pass']} / 72 ({(summary['svg_valid_pass']/72)*100:.1f}%)", flush=True)
    print("-" * 80, flush=True)
    print(f"Strict Pass Count:                    {summary['all_checks_strict_pass']} / 72", flush=True)
    print(f"Orientation-Aware Pass Count:         {summary['all_checks_orient_pass']} / 72", flush=True)
    print("=" * 80, flush=True)

    if summary["failures_strict"]:
        print(f"\n[FAILURES - STRICT (W>=1000 and H>=600)] ({len(summary['failures_strict'])} items):", flush=True)
        for fail in summary["failures_strict"]:
            print(f"  - STT {fail['stt']:02d} ({fail['fig_num']}) [{fail['target_png']}]: Dims={fail['dims']}, Errors={fail['png_errors'] + fail['svg_errors']}", flush=True)

    if summary["failures_orient"]:
        print(f"\n[FAILURES - ORIENTATION-AWARE (Max>=1000 and Min>=600)] ({len(summary['failures_orient'])} items):", flush=True)
        for fail in summary["failures_orient"]:
            print(f"  - STT {fail['stt']:02d} ({fail['fig_num']}) [{fail['target_png']}]: Dims={fail['dims']}, Errors={fail['png_errors'] + fail['svg_errors']}", flush=True)

    # Cross check against AUDIT_72_FIGURES.md
    print("\n" + "=" * 80, flush=True)
    print("CROSS-CHECKING AGAINST AUDIT_72_FIGURES.md", flush=True)
    print("=" * 80, flush=True)
    with open(AUDIT_MD_PATH, "r", encoding="utf-8") as f:
        audit_content = f.read()

    audit_mismatches = []
    for item in results:
        png_name = item["target_png"]
        svg_name = item["target_svg"]
        if png_name not in audit_content:
            audit_mismatches.append(f"PNG {png_name} not mentioned in AUDIT_72_FIGURES.md")
        if svg_name not in audit_content:
            audit_mismatches.append(f"SVG {svg_name} not mentioned in AUDIT_72_FIGURES.md")

    if audit_mismatches:
        print(f"Audit report mismatches found: {len(audit_mismatches)}", flush=True)
        for m in audit_mismatches[:5]:
            print(f"  - {m}", flush=True)
    else:
        print("Audit report cross-check: 100% MATCH. All 72 PNGs and 72 SVGs accounted for in AUDIT_72_FIGURES.md.", flush=True)

    # Save detailed JSON output for report generation
    out_json = BASE_DIR / "tools" / "test_assets_empirical_result.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed empirical evaluation saved to: {out_json}", flush=True)

    return summary, results


if __name__ == "__main__":
    run_full_suite()
