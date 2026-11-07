#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/test_assets_empirical_v2.py
================================================================================
UPGRADED EMPIRICAL ASSET VERIFICATION HARNESS — 72 FIGURES
Project: RentalSystem HUIT 2025 Thesis
Challenger: Empirical Image Asset Re-Challenger (challenger_image_eval_2)

Evaluation Criteria:
1. Aspect Ratio Parity (< 2.0% divergence between PNG and SVG viewBox).
2. Metadata & DPI Verification:
   - PIL/Pillow reports DPI == (300, 300).
   - File size > 0 bytes for all 72 PNGs and 72 SVGs.
3. Grayscale Color Verification:
   - 61 technical diagrams in Academic Grayscale (zero or near-zero saturation).
   - 11 UI screenshots conform to Executive Deep Navy (#0f2b5c, Slate, Pure White,
     no prohibited neon colors).
================================================================================
"""

import os
import sys
import json
import re
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

# Import MASTER_FIGURES_REGISTRY from render_master_diagrams
sys.path.insert(0, str(BASE_DIR / "tools"))
from render_master_diagrams import MASTER_FIGURES_REGISTRY


def parse_svg_dimensions(svg_path: Path):
    """
    Parse SVG viewBox or width/height attributes to extract vector canvas dimensions.
    Returns: (width, height, aspect_ratio, raw_viewbox, parse_error)
    """
    if not svg_path.exists():
        return None, None, None, None, "File not found"

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()

        # Check svg tag
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if tag.lower() != "svg":
            return None, None, None, None, f"Root element is '{root.tag}', expected '<svg>'"

        vb = root.attrib.get("viewBox")
        w_attr = root.attrib.get("width")
        h_attr = root.attrib.get("height")

        svg_w = None
        svg_h = None

        if vb:
            tokens = [float(t) for t in re.split(r"[\s,]+", vb.strip()) if t]
            if len(tokens) >= 4:
                # tokens: min-x, min-y, width, height
                svg_w = tokens[2]
                svg_h = tokens[3]

        if (svg_w is None or svg_h is None) and w_attr and h_attr:
            # Parse width and height attributes (stripping units like pt, px)
            def clean_dim(val):
                cleaned = re.sub(r"[a-zA-Z%]+", "", str(val)).strip()
                return float(cleaned) if cleaned else None

            svg_w = clean_dim(w_attr)
            svg_h = clean_dim(h_attr)

        if svg_w is None or svg_h is None or svg_w <= 0 or svg_h <= 0:
            return None, None, None, vb, f"Could not determine positive width/height from SVG (w={svg_w}, h={svg_h})"

        ar = svg_w / svg_h
        return svg_w, svg_h, ar, vb, None

    except Exception as e:
        return None, None, None, None, f"SVG parse exception: {str(e)}"


def analyze_grayscale(img: Image.Image, w: int, h: int):
    """
    Empirically analyze RGB image for Academic Grayscale conformance.
    Returns: (mean_rgb_diff, max_rgb_diff, mean_saturation, max_saturation, is_grayscale)
    """
    if img.mode in ("L", "1"):
        return 0.0, 0.0, 0.0, 0.0, True

    # Subsample if large to optimize CPU/RAM
    step = 1
    if w > 3000 or h > 3000:
        step = 4
    elif w > 1500 or h > 1500:
        step = 2

    rgb = img.convert("RGB")
    arr = np.asarray(rgb)[::step, ::step].astype(np.float32)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # Mean absolute difference between channels
    diff = (np.abs(r - g) + np.abs(g - b) + np.abs(b - r)) / 3.0
    mean_diff = float(np.mean(diff))
    max_diff = float(np.max(diff))

    # Saturation in HSV: (max - min) / max (for max > 0)
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin
    sat = np.zeros_like(delta)
    nonzero_mask = cmax > 0
    sat[nonzero_mask] = delta[nonzero_mask] / cmax[nonzero_mask]

    mean_sat = float(np.mean(sat))
    max_sat = float(np.max(sat))

    # Grayscale condition: delta == 0 or mean_diff < 0.01 and mean_sat < 0.005
    is_grayscale = (mean_diff < 0.01) and (mean_sat < 0.005)

    return round(mean_diff, 5), round(max_diff, 2), round(mean_sat, 5), round(max_sat, 4), is_grayscale


def analyze_executive_navy(img: Image.Image, w: int, h: int):
    """
    Empirically verify UI screenshot conformance to Executive Navy design system:
    - Primary Deep Navy: #0f2b5c (RGB ~ 15, 43, 92)
    - Royal Blue Accent: #1e3a8a (RGB ~ 30, 58, 138)
    - Pure White & Slate surfaces: #ffffff, #f8fafc, #e2e8f0
    - Absence of prohibited jarring neon colors (neon cyan, neon yellow, bright lime).
    """
    step = 1
    if w > 2000 or h > 2000:
        step = 2

    rgb = img.convert("RGB")
    arr = np.asarray(rgb)[::step, ::step].astype(np.int16)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    total_pixels = r.size

    # 1. Check for Deep Navy / Slate Navy presence
    # Deep Navy criteria: Dark blue where B is prominent, R is low, G is low-moderate
    # e.g., #0f2b5c -> R=15, G=43, B=92; #1e3a8a -> R=30, G=58, B=138
    navy_mask = (r < 65) & (g < 100) & (b > 60) & (b > r + 20)
    navy_pixels = int(np.sum(navy_mask))
    navy_pct = round((navy_pixels / total_pixels) * 100.0, 2)

    # 2. Check for Neutral/White/Slate canvas & surfaces (R ~ G ~ B, high luminance)
    # Neutral slate/white: difference between channels < 20
    neutral_mask = (np.abs(r - g) < 20) & (np.abs(g - b) < 20) & (np.abs(b - r) < 20)
    neutral_pixels = int(np.sum(neutral_mask))
    neutral_pct = round((neutral_pixels / total_pixels) * 100.0, 2)

    # 3. Check for Prohibited Jarring Neon Colors:
    # - Neon Cyan: G > 220, B > 220, R < 80
    # - Neon Yellow: R > 220, G > 220, B < 80
    # - Bright Lime: G > 220, R < 80, B < 80
    neon_cyan = (g > 220) & (b > 220) & (r < 80)
    neon_yellow = (r > 220) & (g > 220) & (b < 80)
    neon_lime = (g > 220) & (r < 80) & (b < 80)
    neon_mask = neon_cyan | neon_yellow | neon_lime
    neon_pixels = int(np.sum(neon_mask))
    neon_pct = round((neon_pixels / total_pixels) * 100.0, 4)

    # Conformance criteria:
    # - Must contain Navy elements or Slate/White professional UI elements (> 80% corporate neutral + navy)
    # - Must NOT contain bright neon clashing colors (neon_pct < 0.1%)
    conforms = (neon_pct < 0.05) and ((navy_pct > 0.5) or (neutral_pct > 80.0))

    return {
        "navy_pixel_pct": navy_pct,
        "neutral_surface_pct": neutral_pct,
        "prohibited_neon_pct": neon_pct,
        "prohibited_neon_pixels": neon_pixels,
        "conforms_executive_navy": conforms
    }


def run_comprehensive_evaluation():
    print("=" * 80, flush=True)
    print("UPGRADED EMPIRICAL RE-CHALLENGER HARNESS (72 FIGURES)", flush=True)
    print("Verifying Aspect Ratio Parity (< 2%), 300 DPI, Grayscale, and Executive Navy", flush=True)
    print("=" * 80, flush=True)

    items = MASTER_FIGURES_REGISTRY
    total_count = len(items)

    metrics = {
        "total_evaluated": total_count,
        "png_exists_and_nonzero": 0,
        "svg_exists_and_nonzero": 0,
        "dpi_300_exact": 0,
        "aspect_ratio_parity_pass": 0,
        "grayscale_61_pass": 0,
        "ui_navy_11_pass": 0,
        "all_criteria_pass": 0,
        "ar_divergences": [],
        "max_ar_divergence": 0.0,
        "min_ar_divergence": 100.0,
        "mean_ar_divergence": 0.0,
        "worst_parity_figure": None,
        "best_parity_figure": None,
        "failures": []
    }

    results = []

    for item in items:
        stt = item["stt"]
        fig_num = item["fig_num"]
        title = item["title"]
        engine = item["engine"]
        target_png = item["target_png"]
        target_svg = item["target_svg"]
        is_ui = (engine == "ui_screenshot") or ("ui_" in target_png)

        png_p = FIGURES_DIR / target_png
        svg_p = FIGURES_DIR / target_svg

        record = {
            "stt": stt,
            "fig_num": fig_num,
            "title": title,
            "engine": engine,
            "is_ui": is_ui,
            "png_file": target_png,
            "svg_file": target_svg,
            "png_exists": False,
            "png_size_bytes": 0,
            "svg_exists": False,
            "svg_size_bytes": 0,
            "dpi_raw": None,
            "dpi_pass": False,
            "png_dims": (0, 0),
            "svg_dims": (0, 0),
            "png_ar": 0.0,
            "svg_ar": 0.0,
            "ar_divergence_pct": 0.0,
            "ar_parity_pass": False,
            "grayscale_pass": False,
            "grayscale_metrics": {},
            "ui_navy_pass": False,
            "ui_navy_metrics": {},
            "figure_overall_pass": False,
            "error_reasons": []
        }

        # 1. Check PNG File & DPI
        if png_p.exists():
            record["png_exists"] = True
            record["png_size_bytes"] = png_p.stat().st_size
            if record["png_size_bytes"] > 0:
                metrics["png_exists_and_nonzero"] += 1
            else:
                record["error_reasons"].append("PNG size is 0 bytes")
        else:
            record["error_reasons"].append("PNG file not found")

        # 2. Check SVG File
        if svg_p.exists():
            record["svg_exists"] = True
            record["svg_size_bytes"] = svg_p.stat().st_size
            if record["svg_size_bytes"] > 0:
                metrics["svg_exists_and_nonzero"] += 1
            else:
                record["error_reasons"].append("SVG size is 0 bytes")
        else:
            record["error_reasons"].append("SVG file not found")

        # 3. Aspect Ratio & Dimensions
        svg_w, svg_h, svg_ar, svg_vb, svg_err = parse_svg_dimensions(svg_p)
        if svg_err:
            record["error_reasons"].append(svg_err)
        else:
            record["svg_dims"] = (svg_w, svg_h)
            record["svg_ar"] = round(svg_ar, 6)

        if record["png_exists"] and record["png_size_bytes"] > 0:
            try:
                with Image.open(png_p) as img:
                    pw, ph = img.size
                    record["png_dims"] = (pw, ph)
                    png_ar = pw / ph
                    record["png_ar"] = round(png_ar, 6)

                    # DPI Check
                    dpi = img.info.get("dpi")
                    record["dpi_raw"] = dpi
                    if dpi is not None:
                        rx, ry = dpi
                        if (round(rx) == 300 and round(ry) == 300) or (abs(rx - 300) < 1.0 and abs(ry - 300) < 1.0):
                            record["dpi_pass"] = True
                            metrics["dpi_300_exact"] += 1
                        else:
                            record["error_reasons"].append(f"DPI is {dpi}, expected (300, 300)")
                    else:
                        record["error_reasons"].append("DPI metadata missing in PNG")

                    # Color / Grayscale analysis
                    if not is_ui:
                        mean_diff, max_diff, mean_sat, max_sat, is_gray = analyze_grayscale(img, pw, ph)
                        record["grayscale_metrics"] = {
                            "mean_rgb_diff": mean_diff,
                            "max_rgb_diff": max_diff,
                            "mean_saturation": mean_sat,
                            "max_saturation": max_sat
                        }
                        record["grayscale_pass"] = is_gray
                        if is_gray:
                            metrics["grayscale_61_pass"] += 1
                        else:
                            record["error_reasons"].append(f"Grayscale violation: mean_diff={mean_diff}, mean_sat={mean_sat}")
                    else:
                        ui_info = analyze_executive_navy(img, pw, ph)
                        record["ui_navy_metrics"] = ui_info
                        record["ui_navy_pass"] = ui_info["conforms_executive_navy"]
                        if ui_info["conforms_executive_navy"]:
                            metrics["ui_navy_11_pass"] += 1
                        else:
                            record["error_reasons"].append(f"Executive Navy violation: {ui_info}")

            except Exception as e:
                record["error_reasons"].append(f"PNG open exception: {str(e)}")

        # Parity calculation
        if record["png_ar"] > 0 and record["svg_ar"] > 0:
            divergence = abs(record["png_ar"] - record["svg_ar"]) / record["svg_ar"] * 100.0
            record["ar_divergence_pct"] = round(divergence, 4)
            metrics["ar_divergences"].append(divergence)

            if divergence < 2.0:
                record["ar_parity_pass"] = True
                metrics["aspect_ratio_parity_pass"] += 1
            else:
                record["error_reasons"].append(f"Aspect ratio divergence {divergence:.2f}% >= 2.0% threshold")

            if divergence > metrics["max_ar_divergence"]:
                metrics["max_ar_divergence"] = divergence
                metrics["worst_parity_figure"] = {
                    "stt": stt,
                    "fig_num": fig_num,
                    "target_png": target_png,
                    "png_ar": record["png_ar"],
                    "svg_ar": record["svg_ar"],
                    "divergence_pct": record["ar_divergence_pct"]
                }
            if divergence < metrics["min_ar_divergence"]:
                metrics["min_ar_divergence"] = divergence
                metrics["best_parity_figure"] = {
                    "stt": stt,
                    "fig_num": fig_num,
                    "target_png": target_png,
                    "divergence_pct": record["ar_divergence_pct"]
                }

        # Overall figure pass
        color_ok = record["ui_navy_pass"] if is_ui else record["grayscale_pass"]
        overall_ok = (
            record["png_exists"] and record["png_size_bytes"] > 0 and
            record["svg_exists"] and record["svg_size_bytes"] > 0 and
            record["dpi_pass"] and record["ar_parity_pass"] and color_ok
        )
        record["figure_overall_pass"] = overall_ok

        if overall_ok:
            metrics["all_criteria_pass"] += 1
            status_tag = "PASS"
        else:
            metrics["failures"].append(record)
            status_tag = "FAIL"

        color_str = f"Navy={record['ui_navy_pass']}" if is_ui else f"Gray={record['grayscale_pass']}"
        print(f"[{stt:02d}/72] {fig_num:14s} | {target_png:45s} | AR Div: {record['ar_divergence_pct']:6.4f}% | DPI: {record['dpi_pass']} | {color_str} -> {status_tag}", flush=True)
        results.append(record)

    if metrics["ar_divergences"]:
        metrics["mean_ar_divergence"] = round(float(np.mean(metrics["ar_divergences"])), 4)
        metrics["max_ar_divergence"] = round(float(metrics["max_ar_divergence"]), 4)
        metrics["min_ar_divergence"] = round(float(metrics["min_ar_divergence"]), 4)

    # Print Quantitative Summary
    print("\n" + "=" * 80, flush=True)
    print("UPGRADED EMPIRICAL VERIFICATION SUMMARY METRICS", flush=True)
    print("=" * 80, flush=True)
    print(f"Total Figures Evaluated:                  {metrics['total_evaluated']} / 72", flush=True)
    print(f"PNG File Exists & Size > 0:                {metrics['png_exists_and_nonzero']} / 72 ({metrics['png_exists_and_nonzero']/total_count*100:.1f}%)", flush=True)
    print(f"SVG File Exists & Size > 0:                {metrics['svg_exists_and_nonzero']} / 72 ({metrics['svg_exists_and_nonzero']/total_count*100:.1f}%)", flush=True)
    print(f"PNG Metadata 300 DPI Reported:            {metrics['dpi_300_exact']} / 72 ({metrics['dpi_300_exact']/total_count*100:.1f}%)", flush=True)
    print(f"Aspect Ratio Parity (< 2% Div):           {metrics['aspect_ratio_parity_pass']} / 72 ({metrics['aspect_ratio_parity_pass']/total_count*100:.1f}%)", flush=True)
    print(f"Academic Grayscale (61 Technical Diags):  {metrics['grayscale_61_pass']} / 61 ({metrics['grayscale_61_pass']/61*100:.1f}%)", flush=True)
    print(f"Executive Navy Conformance (11 UI Screens): {metrics['ui_navy_11_pass']} / 11 ({metrics['ui_navy_11_pass']/11*100:.1f}%)", flush=True)
    print("-" * 80, flush=True)
    print(f"Min Aspect Ratio Divergence:              {metrics['min_ar_divergence']:.4f}%", flush=True)
    print(f"Mean Aspect Ratio Divergence:             {metrics['mean_ar_divergence']:.4f}%", flush=True)
    print(f"Max Aspect Ratio Divergence:              {metrics['max_ar_divergence']:.4f}%", flush=True)
    print(f"Worst Parity Figure:                      {metrics['worst_parity_figure']}", flush=True)
    print("-" * 80, flush=True)
    print(f"OVERALL ALL-CRITERIA PASS:                {metrics['all_criteria_pass']} / 72 ({metrics['all_criteria_pass']/total_count*100:.1f}%)", flush=True)
    print("=" * 80, flush=True)

    if metrics["failures"]:
        print(f"\n[FAILURES DETECTED: {len(metrics['failures'])} item(s)]:", flush=True)
        for fail in metrics["failures"]:
            print(f"  - STT {fail['stt']:02d} ({fail['fig_num']}): {fail['error_reasons']}", flush=True)
    else:
        print("\nALL 72 FIGURES EMPIRICALLY SATISFY 100% OF UPGRADED CHALLENGER CRITERIA!", flush=True)

    # Save detailed JSON output
    out_json = BASE_DIR / "tools" / "test_assets_empirical_v2_result.json"
    clean_metrics = {k: v for k, v in metrics.items() if k != "ar_divergences"}
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"summary": clean_metrics, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"Detailed JSON results written to: {out_json}", flush=True)

    return metrics, results


if __name__ == "__main__":
    run_comprehensive_evaluation()
