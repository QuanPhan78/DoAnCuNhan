#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/sync_thesis_documents.py
================================================================================
RentalSystem Thesis Word Document Synchronization & OpenXML Media Replacement
Milestone 3 (M3) — Requirement R4

Synchronizes 78 300-DPI technical diagrams and real web UI browser screenshots
from figures/ into BOTH Word thesis documents:
  1. d:\\DoAnCuNhan\\KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx
  2. d:\\DoAnCuNhan\\BaoCao_KLCN058_Final.docx

Core Operations:
  1. Clean backup of both documents (.bak) before modifying.
  2. Byte-for-byte replacement of word/media/image1.png to image78.png with figures/*.png.
  3. Dynamic parsing of word/_rels/document.xml.rels and DrawingML inline shapes (<wp:inline>).
  4. Precise proportional extent recalculation (<wp:extent> and <a:ext>) preserving natural aspect ratio:
     - 3.50 cm (1,260,000 EMUs) for cover logo (image1.png).
     - 15.00 cm (5,400,000 EMUs) for wide ERD and Class diagrams (image32, image33, image47).
     - 14.50 cm (5,220,000 EMUs) default width for all other 74 technical diagrams and UI screenshots.
     - Proportionate height: int(target_cx * (img_height / img_width)).
  5. In word/settings.xml, ensure <w:updateFields w:val="true"/> is present (especially for Document 2).
  6. 100% preservation of all captions (<w:pStyle w:val="Caption"/>), text paragraphs, tables, and styles.
  7. Atomic zip packaging with CRC-32 validation and post-sync integrity verification.
================================================================================
"""

import os
import sys
import shutil
import hashlib
import zipfile
from pathlib import Path
from PIL import Image
import lxml.etree as ET

# Ensure stdout uses UTF-8 encoding on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_ROOT / "figures"

DOCUMENTS = [
    PROJECT_ROOT / "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx",
    PROJECT_ROOT / "BaoCao_KLCN058_Final.docx",
]

# OpenXML Namespaces
NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

EMUS_PER_CM = 360000

# Canonical Mapping: media filename -> source file in figures/
CANONICAL_MEDIA_MAP = {
    "image1.png": "logo_huit.png",
    "image2.png": "hinh_1_1_quy_trinh_truyen_thong.png",
    "image3.png": "hinh_1_2_quy_trinh_tong_the_de_xuat.png",
    "image4.png": "hinh_2_1_1_1_semaphore_concurrency.png",
    "image5.png": "hinh_2_1_2_1_vietqr_napas247_structure.png",
    "image6.png": "hinh_2_1_3_1_debt_aging_algorithm.png",
    "image7.png": "hinh_2_1_use_case_tong_quat.png",
    "image8.png": "hinh_2_2_2_1_1_activity_dang_ky_xac_thuc.png",
    "image9.png": "hinh_2_2_2_1_2_sequence_dang_ky_xac_thuc.png",
    "image10.png": "hinh_2_2_2_1_3_collaboration_dang_ky_xac_thuc.png",
    "image11.png": "hinh_2_2_2_2_1_activity_dat_thue_inventory.png",
    "image12.png": "hinh_2_2_2_2_2_sequence_dat_thue_inventory.png",
    "image13.png": "hinh_2_2_2_2_3_collaboration_dat_thue_inventory.png",
    "image14.png": "hinh_2_2_2_3_1_activity_thanh_toan_vietqr.png",
    "image15.png": "hinh_2_2_2_3_2_sequence_thanh_toan_vietqr.png",
    "image16.png": "hinh_2_2_2_3_3_collaboration_thanh_toan_vietqr.png",
    "image17.png": "hinh_2_2_2_4_1_activity_ban_giao_ky_so.png",
    "image18.png": "hinh_2_2_2_4_2_sequence_ban_giao_ky_so.png",
    "image19.png": "hinh_2_2_2_4_3_collaboration_ban_giao_ky_so.png",
    "image20.png": "hinh_2_2_2_5_1_activity_bao_tri_su_co.png",
    "image21.png": "hinh_2_2_2_5_2_sequence_bao_tri_su_co.png",
    "image22.png": "hinh_2_2_2_5_3_collaboration_bao_tri_su_co.png",
    "image23.png": "hinh_2_2_2_6_1_activity_gia_han_cong_no.png",
    "image24.png": "hinh_2_2_2_6_2_sequence_gia_han_cong_no.png",
    "image25.png": "hinh_2_2_2_6_3_collaboration_gia_han_cong_no.png",
    "image26.png": "hinh_2_2_2_7_1_activity_tra_may_hoan_coc.png",
    "image27.png": "hinh_2_2_2_7_2_sequence_tra_may_hoan_coc.png",
    "image28.png": "hinh_2_2_2_7_3_collaboration_tra_may_hoan_coc.png",
    "image29.png": "hinh_2_2_use_case_khach_hang.png",
    "image30.png": "hinh_2_3_use_case_admin.png",
    "image31.png": "hinh_2_4_use_case_bao_tri.png",
    "image32.png": "hinh_2_4_1_analysis_class_diagram.png",
    "image33.png": "hinh_3_3_erd_vat_ly_chi_tiet.png",
    "image34.png": "hinh_3_10_ui_trang_chu.png",
    "image35.png": "hinh_3_11_ui_chi_tiet_san_pham.png",
    "image36.png": "hinh_3_12_ui_checkout.png",
    "image37.png": "hinh_3_13_ui_ky_hop_dong.png",
    "image38.png": "hinh_3_14_ui_hop_dong_khach_hang.png",
    "image39.png": "hinh_3_15_ui_cong_no_khach_hang.png",
    "image40.png": "hinh_3_16_ui_phieu_bao_tri.png",
    "image41.png": "hinh_3_17_ui_admin_dashboard.png",
    "image42.png": "hinh_3_18_ui_admin_cong_no.png",
    "image43.png": "hinh_3_19_ui_admin_bao_tri.png",
    "image44.png": "hinh_3_20_ui_in_hop_dong.png",
    "image45.png": "hinh_3_8_dieu_huong_khach_hang.png",
    "image46.png": "hinh_3_9_dieu_huong_admin.png",
    "image47.png": "hinh_3_3_1_design_class_diagram.png",
    "image48.png": "hinh_3_4_1_1_bce_dang_ky_xac_thuc.png",
    "image49.png": "hinh_3_4_1_2_sequence_3lop_dang_ky_xac_thuc.png",
    "image50.png": "hinh_3_4_1_3_collab_3lop_dang_ky_xac_thuc.png",
    "image51.png": "hinh_3_4_2_1_bce_dat_thue_inventory.png",
    "image52.png": "hinh_3_4_2_2_sequence_3lop_dat_thue_inventory.png",
    "image53.png": "hinh_3_4_2_3_collab_3lop_dat_thue_inventory.png",
    "image54.png": "hinh_3_4_3_1_bce_thanh_toan_vietqr.png",
    "image55.png": "hinh_3_4_3_2_sequence_3lop_thanh_toan_vietqr.png",
    "image56.png": "hinh_3_4_3_3_collab_3lop_thanh_toan_vietqr.png",
    "image57.png": "hinh_3_4_4_1_bce_ban_giao_ky_so.png",
    "image58.png": "hinh_3_4_4_2_sequence_3lop_ban_giao_ky_so.png",
    "image59.png": "hinh_3_4_4_3_collab_3lop_ban_giao_ky_so.png",
    "image60.png": "hinh_3_4_5_1_bce_bao_tri_su_co.png",
    "image61.png": "hinh_3_4_5_2_sequence_3lop_bao_tri_su_co.png",
    "image62.png": "hinh_3_4_5_3_collab_3lop_bao_tri_su_co.png",
    "image63.png": "hinh_3_4_6_1_bce_gia_han_cong_no.png",
    "image64.png": "hinh_3_4_6_2_sequence_3lop_gia_han_cong_no.png",
    "image65.png": "hinh_3_4_6_3_collab_3lop_gia_han_cong_no.png",
    "image66.png": "hinh_3_4_7_1_bce_tra_may_hoan_coc.png",
    "image67.png": "hinh_3_4_7_2_sequence_3lop_tra_may_hoan_coc.png",
    "image68.png": "hinh_3_4_7_3_collab_3lop_tra_may_hoan_coc.png",
    "image69.png": "hinh_3_1_kien_truc_he_thong.png",
    "image70.png": "hinh_3_2_luong_http_request.png",
    "image71.png": "hinh_4_1_cau_truc_ma_nguon.png",
    "image72.png": "hinh_4_2_state_thiet_bi.png",
    "image73.png": "hinh_4_3_state_phieu_bao_tri.png",
    "image74.png": "hinh_4_4_migration_timeline.png",
    "image75.png": "hinh_5_3_ty_le_khac_phuc_rui_ro.png",
    "image76.png": "hinh_5_1_ket_qua_kiem_thu_challenger.png",
    "image77.png": "hinh_5_2_2_load_test_semaphore.png",
    "image78.png": "hinh_5_4_console_test_runner.png",
}

# Width specifications in cm
WIDE_DIAGRAMS = {"image32.png", "image33.png", "image47.png"}
COVER_LOGOS = {"image1.png"}


def get_target_width_cm(media_filename: str) -> float:
    """Determine target display width in cm for a media file."""
    if media_filename in COVER_LOGOS:
        return 3.50
    elif media_filename in WIDE_DIAGRAMS:
        return 15.00
    else:
        return 14.50


def verify_figures_directory():
    """Verify that all 78 target images exist and are valid in figures/."""
    print("=" * 80)
    print("STEP 1: VERIFYING SOURCE ASSETS IN figures/")
    print("=" * 80)
    if not FIGURES_DIR.exists():
        raise FileNotFoundError(f"Figures directory not found: {FIGURES_DIR}")

    missing = []
    invalid = []
    figure_metadata = {}

    for media_name, fig_name in sorted(
        CANONICAL_MEDIA_MAP.items(),
        key=lambda x: int(x[0].replace("image", "").replace(".png", "")),
    ):
        fig_path = FIGURES_DIR / fig_name
        if not fig_path.exists():
            missing.append((media_name, fig_name))
            continue

        try:
            with Image.open(fig_path) as im:
                im.verify()
            with Image.open(fig_path) as im:
                w, h = im.size
                dpi = im.info.get("dpi", (72.0, 72.0))
                dpi_x = dpi[0] if isinstance(dpi, tuple) else dpi
                figure_metadata[media_name] = {
                    "path": fig_path,
                    "filename": fig_name,
                    "width_px": w,
                    "height_px": h,
                    "dpi_x": dpi_x,
                    "size_bytes": fig_path.stat().st_size,
                }
        except Exception as e:
            invalid.append((fig_name, str(e)))

    if missing:
        print(f"FATAL: Missing {len(missing)} files in figures/:")
        for m, f in missing:
            print(f"  - {m} -> figures/{f}")
        raise RuntimeError(f"Missing {len(missing)} source images in figures/")

    if invalid:
        print(f"FATAL: Found {len(invalid)} corrupt images in figures/:")
        for f, err in invalid:
            print(f"  - {f}: {err}")
        raise RuntimeError(f"Corrupt source images detected: {invalid}")

    print(f"SUCCESS: All {len(figure_metadata)} source figures verified in {FIGURES_DIR}")
    return figure_metadata


def backup_document(doc_path: Path):
    """Create a pristine .bak backup if not already present."""
    bak_path = doc_path.with_suffix(".docx.bak")
    if not bak_path.exists():
        shutil.copy2(doc_path, bak_path)
        print(f"  [BACKUP] Created backup: {bak_path.name} ({bak_path.stat().st_size:,} bytes)")
    else:
        print(f"  [BACKUP] Existing backup preserved: {bak_path.name}")


def synchronize_document(doc_path: Path, figure_metadata: dict):
    """
    Perform in-place OpenXML synchronization for a single docx file:
    1. Replace bytes in word/media/imageXX.png
    2. Recalculate DrawingML extents in word/document.xml
    3. Ensure updateFields in word/settings.xml
    4. Validate and write atomically
    """
    print(f"\n--- Synchronizing Document: {doc_path.name} ---")
    if not doc_path.exists():
        raise FileNotFoundError(f"Document not found: {doc_path}")

    backup_document(doc_path)

    # 1. Inspect existing zip package
    with zipfile.ZipFile(doc_path, "r") as zin:
        namelist = set(zin.namelist())
        doc_xml_bytes = zin.read("word/document.xml")
        rels_xml_bytes = zin.read("word/_rels/document.xml.rels")
        settings_xml_bytes = (
            zin.read("word/settings.xml") if "word/settings.xml" in namelist else None
        )

        # Map rId -> media target filename (e.g. "rId13" -> "image2.png")
        rels_tree = ET.fromstring(rels_xml_bytes)
        rid_to_media = {}
        for r in rels_tree.findall(f"{{{NAMESPACES['pr']}}}Relationship"):
            rid = r.attrib.get("Id")
            target = r.attrib.get("Target", "")
            if "image" in target.lower():
                media_file = Path(target).name.lower()
                rid_to_media[rid] = media_file

        print(f"  Loaded {len(rid_to_media)} image relationship mappings from document.xml.rels.")

        # 2. Recalculate DrawingML inline shape extents in document.xml
        doc_tree = ET.fromstring(doc_xml_bytes)
        inlines = doc_tree.findall(f".//{{{NAMESPACES['wp']}}}inline")
        print(f"  Identified {len(inlines)} DrawingML <wp:inline> shapes in word/document.xml.")

        updated_drawings = 0
        for inline_idx, inline in enumerate(inlines, start=1):
            blip = inline.find(f".//{{{NAMESPACES['a']}}}blip")
            if blip is None:
                continue

            embed_id = blip.attrib.get(f"{{{NAMESPACES['r']}}}embed")
            if not embed_id or embed_id not in rid_to_media:
                continue

            media_file = rid_to_media[embed_id]
            if media_file not in figure_metadata:
                continue

            meta = figure_metadata[media_file]
            target_w_cm = get_target_width_cm(media_file)
            target_cx = int(target_w_cm * EMUS_PER_CM)
            target_cy = int(target_cx * (meta["height_px"] / meta["width_px"]))

            # Update <wp:extent cx="..." cy="..."/>
            extent = inline.find(f"{{{NAMESPACES['wp']}}}extent")
            if extent is not None:
                extent.attrib["cx"] = str(target_cx)
                extent.attrib["cy"] = str(target_cy)

            # Update all <a:ext cx="..." cy="..."/> inside <a:xfrm>
            for ext in inline.findall(f".//{{{NAMESPACES['a']}}}xfrm/{{{NAMESPACES['a']}}}ext"):
                ext.attrib["cx"] = str(target_cx)
                ext.attrib["cy"] = str(target_cy)

            # Update picture name in <pic:cNvPr>
            cnvpr = inline.find(f".//{{{NAMESPACES['pic']}}}cNvPr")
            if cnvpr is not None:
                cnvpr.attrib["name"] = meta["filename"]

            updated_drawings += 1

        print(f"  Successfully recalculated extents for {updated_drawings} inline drawings.")

        # Serialize updated document.xml
        updated_doc_xml = ET.tostring(
            doc_tree, xml_declaration=True, encoding="UTF-8", standalone="yes"
        )

        # 3. Update word/settings.xml (<w:updateFields w:val="true"/>)
        updated_settings_xml = None
        if settings_xml_bytes is not None:
            settings_tree = ET.fromstring(settings_xml_bytes)
            update_elem = settings_tree.find(f"{{{NAMESPACES['w']}}}updateFields")
            if update_elem is None:
                ET.SubElement(
                    settings_tree,
                    f"{{{NAMESPACES['w']}}}updateFields",
                    attrib={f"{{{NAMESPACES['w']}}}val": "true"},
                )
                print("  Injected <w:updateFields w:val='true'/> into word/settings.xml.")
            else:
                update_elem.attrib[f"{{{NAMESPACES['w']}}}val"] = "true"
                print("  Verified <w:updateFields w:val='true'/> in word/settings.xml.")
            updated_settings_xml = ET.tostring(
                settings_tree, xml_declaration=True, encoding="UTF-8", standalone="yes"
            )

        # 4. Atomically build new zip archive
        temp_doc_path = doc_path.with_suffix(".docx.tmp")
        replaced_media_count = 0

        with zipfile.ZipFile(
            temp_doc_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as zout:
            for item in zin.infolist():
                fname = item.filename
                if fname == "word/document.xml":
                    zout.writestr(fname, updated_doc_xml)
                elif fname == "word/settings.xml" and updated_settings_xml is not None:
                    zout.writestr(fname, updated_settings_xml)
                elif fname.startswith("word/media/"):
                    media_base = Path(fname).name.lower()
                    if media_base in figure_metadata:
                        fig_file_path = figure_metadata[media_base]["path"]
                        with open(fig_file_path, "rb") as f_img:
                            new_bytes = f_img.read()
                        zout.writestr(fname, new_bytes)
                        replaced_media_count += 1
                    else:
                        zout.writestr(fname, zin.read(fname))
                else:
                    zout.writestr(fname, zin.read(fname))

    # Verify temp archive before replacing
    with zipfile.ZipFile(temp_doc_path, "r") as zchk:
        bad_file = zchk.testzip()
        if bad_file is not None:
            temp_doc_path.unlink(missing_ok=True)
            raise RuntimeError(f"Corrupt zip part detected in {temp_doc_path}: {bad_file}")

    # Atomic replace
    shutil.move(temp_doc_path, doc_path)
    print(f"  SUCCESS: Synchronized {doc_path.name}")
    print(f"    - Media files replaced: {replaced_media_count}/78")
    print(f"    - Drawings updated: {updated_drawings}/81")
    print(f"    - Package size: {doc_path.stat().st_size:,} bytes")


def verify_sha256_equality():
    """Verify that all 78 media files in both documents match SHA256 of figures/."""
    print("\n" + "=" * 80)
    print("STEP 3: POST-SYNC SHA256 MEDIA EQUALITY VERIFICATION")
    print("=" * 80)

    for doc_path in DOCUMENTS:
        print(f"\nChecking document: {doc_path.name}")
        with zipfile.ZipFile(doc_path, "r") as zf:
            zip_media = {
                Path(name).name.lower(): zf.read(name)
                for name in zf.namelist()
                if name.startswith("word/media/")
            }

        mismatches = []
        for media_name, fig_name in sorted(
            CANONICAL_MEDIA_MAP.items(),
            key=lambda x: int(x[0].replace("image", "").replace(".png", "")),
        ):
            if media_name not in zip_media:
                mismatches.append((media_name, "Missing in zip package"))
                continue

            fig_path = FIGURES_DIR / fig_name
            with open(fig_path, "rb") as f:
                fig_bytes = f.read()

            fig_hash = hashlib.sha256(fig_bytes).hexdigest()
            zip_hash = hashlib.sha256(zip_media[media_name]).hexdigest()

            if fig_hash != zip_hash:
                mismatches.append(
                    (media_name, f"Hash mismatch: fig={fig_hash[:8]} zip={zip_hash[:8]}")
                )

        if mismatches:
            print(f"  FAIL: Found {len(mismatches)} media hash mismatches in {doc_path.name}:")
            for m, err in mismatches:
                print(f"    - {m}: {err}")
            raise RuntimeError(f"SHA256 verification failed for {doc_path.name}")
        else:
            print(f"  PASS: All 78 media files in {doc_path.name} have 100% SHA256 match to figures/.")


def verify_structure_and_captions():
    """Verify that captions and table counts are preserved 100%."""
    print("\n" + "=" * 80)
    print("STEP 4: CAPTION & DOCUMENT STRUCTURE INTEGRITY VERIFICATION")
    print("=" * 80)

    for doc_path in DOCUMENTS:
        with zipfile.ZipFile(doc_path, "r") as zf:
            doc_xml = zf.read("word/document.xml")
        root = ET.fromstring(doc_xml)

        # Captions count: <w:pStyle w:val="Caption"/>
        caption_styles = root.findall(f".//{{{NAMESPACES['w']}}}pStyle[@{{{NAMESPACES['w']}}}val='Caption']")
        tbl_elements = root.findall(f".//{{{NAMESPACES['w']}}}tbl")
        drawing_elements = root.findall(f".//{{{NAMESPACES['wp']}}}inline")

        print(f"Document: {doc_path.name}")
        print(f"  - Total Caption-styled paragraphs: {len(caption_styles)} (Expected: 126)")
        print(f"  - Total Tables: {len(tbl_elements)} (Expected: 47)")
        print(f"  - Total DrawingML inline shapes: {len(drawing_elements)} (Expected: 81)")

        if len(caption_styles) < 126:
            raise RuntimeError(f"Caption count dropped in {doc_path.name}: {len(caption_styles)} < 126")
        if len(tbl_elements) != 47:
            raise RuntimeError(f"Table count changed in {doc_path.name}: {len(tbl_elements)} != 47")
        if len(drawing_elements) != 81:
            raise RuntimeError(f"DrawingML count changed in {doc_path.name}: {len(drawing_elements)} != 81")

    print("\nPASS: Captions, tables, and drawing elements 100% preserved.")


def main():
    print("=" * 80)
    print("RENTALSYSTEM MASTER THESIS DUAL-DOCUMENT SYNCHRONIZATION")
    print("=" * 80)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Figures dir:  {FIGURES_DIR}")
    print(f"Target docs:  {[d.name for d in DOCUMENTS]}")
    print("=" * 80)

    # Step 1: Verify source figures in figures/
    figure_metadata = verify_figures_directory()

    # Step 2: Synchronize both documents
    print("\n" + "=" * 80)
    print("STEP 2: SYNCHRONIZING BOTH WORD DOCUMENTS")
    print("=" * 80)
    for doc_path in DOCUMENTS:
        synchronize_document(doc_path, figure_metadata)

    # Step 3: Verify SHA256 equality
    verify_sha256_equality()

    # Step 4: Verify captions and document structure
    verify_structure_and_captions()

    print("\n" + "=" * 80)
    print("ALL SYNCHRONIZATION STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
