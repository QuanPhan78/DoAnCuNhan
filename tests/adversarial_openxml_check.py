#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adversarial OpenXML Package Verifier & Stress Tester
Author: Challenger 1 (critic, specialist)
Target: d:\\DoAnCuNhan\\KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx
"""

import os
import sys
import io
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image

DOCX_PATH = sys.argv[1] if len(sys.argv) > 1 else r"d:\DoAnCuNhan\KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx"

NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

def register_namespaces():
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)

def run_adversarial_checks():
    print("=" * 80)
    print("ADVERSARIAL OPENXML AUDIT & STRESS TESTING")
    print(f"Target: {DOCX_PATH}")
    print("=" * 80)

    if not os.path.exists(DOCX_PATH):
        print(f"FATAL: Document not found at {DOCX_PATH}")
        return False

    failures = []
    warnings = []

    # 1. ZIP INTEGRITY & CRC-32 CHECKSUM TEST
    print("\n[CHALLENGE 1] Zip Archive & CRC-32 Checksum Integrity")
    try:
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            corrupt_file = zf.testzip()
            if corrupt_file is not None:
                failures.append(f"CRC-32 checksum failure on zip entry: {corrupt_file}")
                print(f"  FAIL: Corrupt file detected in archive: {corrupt_file}")
            else:
                namelist = zf.namelist()
                print(f"  PASS: All {len(namelist)} zip entries passed CRC-32 checksums.")
    except Exception as e:
        failures.append(f"Zip extraction error: {e}")
        print(f"  FAIL: Zip extraction error: {e}")
        return False

    with zipfile.ZipFile(DOCX_PATH, "r") as zf:
        namelist = set(zf.namelist())

        # 2. [Content_Types].xml INSPECTION
        print("\n[CHALLENGE 2] [Content_Types].xml Schema & Completeness")
        if "[Content_Types].xml" not in namelist:
            failures.append("Missing [Content_Types].xml in zip package")
            print("  FAIL: [Content_Types].xml not found.")
        else:
            try:
                ct_bytes = zf.read("[Content_Types].xml")
                ct_root = ET.fromstring(ct_bytes)
                defaults = {d.attrib.get("Extension"): d.attrib.get("ContentType") for d in ct_root.findall(f"{{{NAMESPACES['ct']}}}Default")}
                overrides = {o.attrib.get("PartName"): o.attrib.get("ContentType") for o in ct_root.findall(f"{{{NAMESPACES['ct']}}}Override")}
                
                print(f"  Found {len(defaults)} default extensions, {len(overrides)} part overrides.")
                # Verify critical defaults
                for ext in ["rels", "xml"]:
                    if ext not in defaults:
                        failures.append(f"[Content_Types].xml missing default for extension '{ext}'")
                        print(f"  FAIL: Missing default extension: {ext}")
                    else:
                        print(f"  PASS: Default extension '{ext}' -> {defaults[ext]}")
                
                # Verify critical parts
                for part in ["/word/document.xml", "/word/settings.xml"]:
                    if part not in overrides:
                        failures.append(f"[Content_Types].xml missing override for '{part}'")
                        print(f"  FAIL: Missing override for: {part}")
                    else:
                        print(f"  PASS: Override '{part}' -> {overrides[part]}")
            except Exception as e:
                failures.append(f"[Content_Types].xml parsing error: {e}")
                print(f"  FAIL: [Content_Types].xml parsing error: {e}")

        # 3. word/settings.xml & <w:updateFields>
        print("\n[CHALLENGE 3] word/settings.xml & Table of Contents updateFields")
        if "word/settings.xml" not in namelist:
            failures.append("Missing word/settings.xml")
            print("  FAIL: word/settings.xml missing")
        else:
            try:
                settings_bytes = zf.read("word/settings.xml")
                settings_root = ET.fromstring(settings_bytes)
                update_fields_elems = settings_root.findall(f"{{{NAMESPACES['w']}}}updateFields")
                if not update_fields_elems:
                    failures.append("Missing <w:updateFields> element in word/settings.xml")
                    print("  FAIL: No <w:updateFields> element found in word/settings.xml")
                else:
                    uf_val = update_fields_elems[0].attrib.get(f"{{{NAMESPACES['w']}}}val")
                    if uf_val not in ["true", "1"]:
                        failures.append(f"<w:updateFields> val attribute is '{uf_val}' (expected 'true' or '1')")
                        print(f"  FAIL: <w:updateFields> val='{uf_val}'")
                    else:
                        print(f"  PASS: <w:updateFields w:val='{uf_val}'/> verified in word/settings.xml.")
            except Exception as e:
                failures.append(f"word/settings.xml parsing error: {e}")
                print(f"  FAIL: word/settings.xml parsing error: {e}")

        # 4. RELATIONSHIPS INTEGRITY (_rels/.rels and word/_rels/document.xml.rels)
        print("\n[CHALLENGE 4] Package & Document Relationships Integrity")
        rel_targets = {}
        if "word/_rels/document.xml.rels" not in namelist:
            failures.append("Missing word/_rels/document.xml.rels")
            print("  FAIL: word/_rels/document.xml.rels missing")
        else:
            try:
                rels_bytes = zf.read("word/_rels/document.xml.rels")
                rels_root = ET.fromstring(rels_bytes)
                for r_elem in rels_root.findall(f"{{{NAMESPACES['pr']}}}Relationship"):
                    r_id = r_elem.attrib.get("Id")
                    r_target = r_elem.attrib.get("Target")
                    r_type = r_elem.attrib.get("Type")
                    rel_targets[r_id] = (r_target, r_type)

                print(f"  Found {len(rel_targets)} relationships in document.xml.rels.")
                
                # Check target existence for internal targets
                broken_rels = []
                for r_id, (target, r_type) in rel_targets.items():
                    if not target.startswith("http://") and not target.startswith("https://"):
                        # Target is relative to word/
                        full_target = f"word/{target}" if not target.startswith("word/") else target
                        # Normalize path
                        full_target = os.path.normpath(full_target).replace("\\", "/")
                        if full_target not in namelist:
                            broken_rels.append((r_id, target, full_target))

                if broken_rels:
                    for b in broken_rels:
                        failures.append(f"Broken relationship target: {b[0]} -> {b[1]} ({b[2]} missing in zip)")
                        print(f"  FAIL: Broken relationship: {b[0]} -> {b[2]}")
                else:
                    print(f"  PASS: All {len(rel_targets)} internal relationships resolve to existing zip parts.")
            except Exception as e:
                failures.append(f"Relationship parsing error: {e}")
                print(f"  FAIL: Relationship parsing error: {e}")

        # 5. word/document.xml SECTION PROPERTIES, MARGINS & PAGE NUMBERING
        print("\n[CHALLENGE 5] word/document.xml Section Geometry & Pagination")
        if "word/document.xml" not in namelist:
            failures.append("Missing word/document.xml")
            print("  FAIL: word/document.xml missing")
        else:
            try:
                doc_bytes = zf.read("word/document.xml")
                doc_root = ET.fromstring(doc_bytes)
                print(f"  PASS: word/document.xml is well-formed XML ({len(doc_bytes):,} bytes).")

                # Find all sectPr elements (in paragraphs pPr/sectPr, and body/sectPr)
                sect_elements = []
                body = doc_root.find(f"{{{NAMESPACES['w']}}}body")
                for p in body.findall(f"{{{NAMESPACES['w']}}}p"):
                    pPr = p.find(f"{{{NAMESPACES['w']}}}pPr")
                    if pPr is not None:
                        sectPr = pPr.find(f"{{{NAMESPACES['w']}}}sectPr")
                        if sectPr is not None:
                            sect_elements.append(sectPr)
                body_sectPr = body.find(f"{{{NAMESPACES['w']}}}sectPr")
                if body_sectPr is not None:
                    sect_elements.append(body_sectPr)

                print(f"  Found {len(sect_elements)} sections in document.xml.")
                if len(sect_elements) < 3:
                    failures.append(f"Expected at least 3 sections, found {len(sect_elements)}")
                    print(f"  FAIL: Found only {len(sect_elements)} sections (expected >= 3).")
                else:
                    print(f"  PASS: Exactly {len(sect_elements)} sections found.")

                for idx, sectPr in enumerate(sect_elements):
                    print(f"\n  --- Auditing Section {idx} ---")
                    
                    # 5.1 Margins
                    pgMar = sectPr.find(f"{{{NAMESPACES['w']}}}pgMar")
                    if pgMar is None:
                        failures.append(f"Section {idx} missing <w:pgMar>")
                        print(f"    FAIL: Missing <w:pgMar>")
                    else:
                        top = int(pgMar.attrib.get(f"{{{NAMESPACES['w']}}}top", "0"))
                        bottom = int(pgMar.attrib.get(f"{{{NAMESPACES['w']}}}bottom", "0"))
                        left = int(pgMar.attrib.get(f"{{{NAMESPACES['w']}}}left", "0"))
                        right = int(pgMar.attrib.get(f"{{{NAMESPACES['w']}}}right", "0"))

                        # Expected: Left = 1985 (3.5 cm), Right = 1418 (2.5 cm), Top = 1418 (2.5 cm), Bottom = 1418 (2.5 cm)
                        # Tolerance ±25 dxa
                        left_ok = (1960 <= left <= 2010)
                        right_ok = (1390 <= right <= 1445)
                        top_ok = (1390 <= top <= 1445)
                        bottom_ok = (1390 <= bottom <= 1445)

                        print(f"    Margins (dxa): Left={left} (ok={left_ok}), Right={right} (ok={right_ok}), Top={top} (ok={top_ok}), Bottom={bottom} (ok={bottom_ok})")
                        if not (left_ok and right_ok and top_ok and bottom_ok):
                            failures.append(f"Section {idx} margins outside HUIT standard: Left={left}, Right={right}, Top={top}, Bottom={bottom}")
                            print(f"    FAIL: Section {idx} margins non-compliant.")
                        else:
                            print(f"    PASS: Section {idx} margins compliant with HUIT standard (3.5cm / 2.5cm / 2.5cm / 2.5cm).")

                    # 5.2 Borders
                    pgBorders = sectPr.find(f"{{{NAMESPACES['w']}}}pgBorders")
                    if idx == 0:
                        if pgBorders is None:
                            failures.append("Section 0 (Cover) missing <w:pgBorders>")
                            print("    FAIL: Section 0 missing <w:pgBorders>")
                        else:
                            disp = pgBorders.attrib.get(f"{{{NAMESPACES['w']}}}display")
                            print(f"    Section 0 border display='{disp}'")
                            if disp != "firstPage":
                                failures.append(f"Section 0 border display='{disp}', expected 'firstPage'")
                                print(f"    FAIL: Expected display='firstPage', got '{disp}'")
                            
                            sides = ["top", "bottom", "left", "right"]
                            for s in sides:
                                s_el = pgBorders.find(f"{{{NAMESPACES['w']}}}{s}")
                                if s_el is None:
                                    failures.append(f"Section 0 missing border for side '{s}'")
                                    print(f"    FAIL: Missing border for side '{s}'")
                                else:
                                    val = s_el.attrib.get(f"{{{NAMESPACES['w']}}}val")
                                    if val != "cornerTriangles":
                                        failures.append(f"Section 0 border '{s}' val='{val}', expected 'cornerTriangles'")
                                        print(f"    FAIL: Border '{s}' val='{val}' != 'cornerTriangles'")
                                    else:
                                        print(f"    PASS: Border '{s}' is 'cornerTriangles'.")

                    # 5.3 Page Numbering
                    pgNumType = sectPr.find(f"{{{NAMESPACES['w']}}}pgNumType")
                    if idx == 1:
                        # Prelim: lowerRoman, start 1
                        if pgNumType is None:
                            failures.append("Section 1 (Prelim) missing <w:pgNumType>")
                            print("    FAIL: Section 1 missing <w:pgNumType>")
                        else:
                            fmt = pgNumType.attrib.get(f"{{{NAMESPACES['w']}}}fmt")
                            start = pgNumType.attrib.get(f"{{{NAMESPACES['w']}}}start")
                            print(f"    Section 1 pagination: fmt='{fmt}', start='{start}'")
                            if fmt != "lowerRoman" or start != "1":
                                failures.append(f"Section 1 pagination: expected fmt='lowerRoman', start='1'. Got fmt='{fmt}', start='{start}'")
                                print(f"    FAIL: Section 1 pagination incorrect.")
                            else:
                                print(f"    PASS: Section 1 correctly resets page numbering to 1 in lowerRoman (i, ii, iii...).")
                    elif idx == 2:
                        # Body: decimal, start 1
                        if pgNumType is None:
                            failures.append("Section 2 (Body) missing <w:pgNumType>")
                            print("    FAIL: Section 2 missing <w:pgNumType>")
                        else:
                            fmt = pgNumType.attrib.get(f"{{{NAMESPACES['w']}}}fmt")
                            start = pgNumType.attrib.get(f"{{{NAMESPACES['w']}}}start")
                            print(f"    Section 2 pagination: fmt='{fmt}', start='{start}'")
                            if start != "1" or (fmt is not None and fmt not in ["decimal", ""]):
                                failures.append(f"Section 2 pagination: expected start='1', fmt in [None, 'decimal']. Got fmt='{fmt}', start='{start}'")
                                print(f"    FAIL: Section 2 pagination incorrect.")
                            else:
                                print(f"    PASS: Section 2 correctly resets page numbering to 1 in decimal (1, 2, 3...).")

                # 5.4 Check embedded drawing blip references in document.xml
                print("\n  --- Checking DrawingML Image Embeds in document.xml ---")
                blip_embeds = []
                for blip in doc_root.iter(f"{{{NAMESPACES['a']}}}blip"):
                    embed_id = blip.attrib.get(f"{{{NAMESPACES['r']}}}embed")
                    if embed_id:
                        blip_embeds.append(embed_id)
                print(f"  Found {len(blip_embeds)} DrawingML <a:blip> embed references.")
                missing_blips = [b for b in blip_embeds if b not in rel_targets]
                if missing_blips:
                    failures.append(f"Found {len(missing_blips)} unresolvable <a:blip> embed IDs: {missing_blips[:5]}")
                    print(f"  FAIL: Unresolvable blip IDs found: {missing_blips}")
                else:
                    print(f"  PASS: 100% of <a:blip> embed IDs resolve to valid relationship targets.")

            except Exception as e:
                failures.append(f"word/document.xml parsing error: {e}")
                print(f"  FAIL: word/document.xml parsing error: {e}")

        # 6. MEDIA ASSETS STRESS-TEST & CORRUPTION CHECK
        print("\n[CHALLENGE 6] Media Assets Deep Integrity & DPI Stress Test (word/media/*)")
        media_files = [n for n in namelist if n.startswith("word/media/")]
        print(f"  Found {len(media_files)} files in word/media/")
        if len(media_files) < 78:
            failures.append(f"Expected at least 78 media files in word/media/, found {len(media_files)}")
            print(f"  FAIL: Media count {len(media_files)} < 78.")
        else:
            print(f"  PASS: Media count {len(media_files)} >= 78.")

        corrupt_images = []
        low_dpi_images = []
        zero_byte_images = []
        image_formats = set()

        for m_name in media_files:
            m_data = zf.read(m_name)
            if len(m_data) == 0:
                zero_byte_images.append(m_name)
                continue
            
            # Magic bytes check
            if m_name.lower().endswith(".png"):
                if not m_data.startswith(b"\x89PNG\r\n\x1a\n"):
                    corrupt_images.append((m_name, "Invalid PNG magic bytes"))
                    continue
            elif m_name.lower().endswith((".jpg", ".jpeg")):
                if not m_data.startswith(b"\xff\xd8\xff"):
                    corrupt_images.append((m_name, "Invalid JPEG magic bytes"))
                    continue

            # Pillow deep decode
            try:
                # 1. verify() checks headers and structural markers
                bio1 = io.BytesIO(m_data)
                im1 = Image.open(bio1)
                im1.verify()
                image_formats.add(im1.format)

                # 2. Re-open and load() decompresses every single scanline/tile
                bio2 = io.BytesIO(m_data)
                im2 = Image.open(bio2)
                im2.load()
                
                dpi = im2.info.get("dpi", (72.0, 72.0))
                dpi_x = dpi[0] if isinstance(dpi, tuple) else dpi
                dpi_y = dpi[1] if isinstance(dpi, tuple) else dpi
                
                # Check for 300 DPI compliance (tolerance >= 290 DPI)
                if dpi_x < 290.0 or dpi_y < 290.0:
                    low_dpi_images.append((m_name, (dpi_x, dpi_y)))

            except Exception as ex:
                corrupt_images.append((m_name, str(ex)))

        if zero_byte_images:
            failures.append(f"Found {len(zero_byte_images)} zero-byte media files: {zero_byte_images}")
            print(f"  FAIL: Zero byte media files: {zero_byte_images}")
        else:
            print(f"  PASS: Zero 0-byte media files detected.")

        if corrupt_images:
            failures.append(f"Found {len(corrupt_images)} corrupt images in word/media/: {corrupt_images}")
            print(f"  FAIL: Corrupt images detected: {corrupt_images}")
        else:
            print(f"  PASS: 100% of {len(media_files)} images successfully opened, verified, and pixel-decoded without error.")

        if low_dpi_images:
            warnings.append(f"{len(low_dpi_images)} images have DPI < 290: {low_dpi_images[:5]}")
            print(f"  WARN: {len(low_dpi_images)} images with DPI < 290.")
        else:
            print(f"  PASS: 100% of media images have 300 DPI (>= 290 DPI).")

        print(f"  Image formats detected: {image_formats}")

    # SUMMARY & FINAL VERDICT
    print("\n" + "=" * 80)
    print("ADVERSARIAL VERDICT")
    print("=" * 80)
    if failures:
        print(f"VERDICT: CHALLENGE_FAILED ({len(failures)} failures)")
        for idx, f in enumerate(failures, 1):
            print(f"  [{idx}] {f}")
        return False
    else:
        print("VERDICT: APPROVE (100% of OpenXML adversarial challenges PASSED)")
        if warnings:
            print(f"Warnings ({len(warnings)}):")
            for w in warnings:
                print(f"  - {w}")
        return True

if __name__ == "__main__":
    success = run_adversarial_checks()
    sys.exit(0 if success else 1)
