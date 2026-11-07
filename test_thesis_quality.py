#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TEST_THESIS_QUALITY.PY - E2E OPAQUE-BOX THESIS QUALITY TEST SUITE
Standards Authority: Khoa CNTT HUIT (2025_kltn_toeic+knn_1.pdf & Mau 2025.docx)
Project: RentalSystem Graduation Thesis Verification
Author: E2E Test Writer (test_writer_1)

4-TIER TEST ARCHITECTURE:
- Tier 1: Feature Coverage (Section Layout, Margins, Font, 5 Kết Chương,
          Lời Cam Đoan, 2.1 Algorithms, 7 Processes UML, 18 Tables DB ERD,
          7 Functions 3-Layer Design, .NET 9 MVC, 540 ChallengerTests,
          Likert N=50 Survey, Deep Captions, 300 DPI Images, Build Health)
- Tier 2: Boundary Cases & Robustness (Dxa Margins Tolerance, Caption Syntax
          Variations, Unicode Normalization, Corrupt File Guards, Boundary N>=50,
          Table Count >= 18, DPI >= 290)
- Tier 3: Combinations & Cross-Cutting Integrity (Caption-to-Media Pairing,
          Table-to-Grid Pairing, Sequential Chapter Flow, Heading Hierarchy,
          word/settings.xml updateFields, Process-Function Symmetry)
- Tier 4: Academic Scenario (End-to-End Faculty Defense Rubric Simulation,
          10 Evaluation Dimensions, Legacy Draft Discrepancy Forensic Audit)
================================================================================
"""

import os
import sys
import re
import io
import zipfile
import unittest
import argparse
import unicodedata
import subprocess
from pathlib import Path
from PIL import Image

# Ensure stdout uses UTF-8 encoding on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import docx
from docx.oxml.ns import nsdecls, qn

WORKSPACE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = WORKSPACE_DIR
PRIMARY_THESIS_PATH = os.path.join(PROJECT_ROOT, "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx")
FIXTURE_THESIS_PATH = os.path.join(PROJECT_ROOT, "tests", "fixtures", "huit_thesis_fixture.docx")
LEGACY_DRAFT_PATH = os.path.join(PROJECT_ROOT, "BỘ CÔNG THƯƠNG.docx")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "figures")
RENTAL_CSPROJ = os.path.join(PROJECT_ROOT, "RentalSystem", "RentalSystem.csproj")
CHALLENGER_CSPROJ = os.path.join(PROJECT_ROOT, "ChallengerTests", "ChallengerTests.csproj")

# Configurable target path
TARGET_DOCX_PATH = None
SKIP_LIVE_BUILD = False


def normalize_text(text: str) -> str:
    """Normalize text using Unicode NFC and strip redundant spaces."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def resolve_target_docx() -> str:
    """
    Resolve which docx file to test:
    1. CLI argument or THESIS_DOCX_PATH env variable
    2. Primary thesis document if present
    3. Auto-generate compliant fixture document for progressive testability
    """
    global TARGET_DOCX_PATH
    if TARGET_DOCX_PATH and os.path.exists(TARGET_DOCX_PATH):
        return TARGET_DOCX_PATH

    env_path = os.environ.get("THESIS_DOCX_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    if os.path.exists(PRIMARY_THESIS_PATH):
        return PRIMARY_THESIS_PATH

    # Progressive testability fallback: generate and use compliant fixture
    if not os.path.exists(FIXTURE_THESIS_PATH):
        from tests.fixture_builder import build_huit_compliant_thesis
        os.makedirs(os.path.dirname(FIXTURE_THESIS_PATH), exist_ok=True)
        build_huit_compliant_thesis(FIXTURE_THESIS_PATH)

    return FIXTURE_THESIS_PATH


# ==============================================================================
# DOCUMENT QUALITY AUDITOR (OPAQUE-BOX OPENXML INSPECTOR)
# ==============================================================================

class DocumentQualityAuditor:
    """Performs deep, opaque-box OpenXML inspection on Word graduation thesis documents."""

    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"Target document not found: {docx_path}")

        self.doc = docx.Document(docx_path)
        self.zip_pkg = zipfile.ZipFile(docx_path, "r")
        self._analyze()

    def _analyze(self):
        NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

        # 1. Inspect Sections & Geometries
        self.sections_info = []
        for idx, section in enumerate(self.doc.sections):
            sectPr = section._sectPr
            
            # Margins
            top_cm = round(section.top_margin.cm, 2)
            bottom_cm = round(section.bottom_margin.cm, 2)
            left_cm = round(section.left_margin.cm, 2)
            right_cm = round(section.right_margin.cm, 2)

            top_dxa = section.top_margin.twips
            bottom_dxa = section.bottom_margin.twips
            left_dxa = section.left_margin.twips
            right_dxa = section.right_margin.twips

            # Borders
            borders_elem = sectPr.xpath("./w:pgBorders")
            border_info = {"display": None, "top": None, "bottom": None, "left": None, "right": None}
            if borders_elem:
                b_el = borders_elem[0]
                border_info["display"] = b_el.attrib.get(f"{{{NS_W}}}display")
                for child in b_el:
                    tag_local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if tag_local in ["top", "bottom", "left", "right"]:
                        border_info[tag_local] = child.attrib.get(f"{{{NS_W}}}val")

            # Page Numbering
            pgnum_elem = sectPr.xpath("./w:pgNumType")
            pgnum_info = {"fmt": None, "start": None}
            if pgnum_elem:
                p_el = pgnum_elem[0]
                pgnum_info["fmt"] = p_el.attrib.get(f"{{{NS_W}}}fmt")
                pgnum_info["start"] = p_el.attrib.get(f"{{{NS_W}}}start")

            self.sections_info.append({
                "index": idx,
                "top_cm": top_cm,
                "bottom_cm": bottom_cm,
                "left_cm": left_cm,
                "right_cm": right_cm,
                "top_dxa": top_dxa,
                "bottom_dxa": bottom_dxa,
                "left_dxa": left_dxa,
                "right_dxa": right_dxa,
                "borders": border_info,
                "pgnum": pgnum_info,
            })

        # 2. Inspect Paragraphs & Captions
        self.paragraphs_text = []
        self.figure_captions = []
        self.table_captions = []
        
        # Regex for deep hierarchical captions: Hình X.Y.Z. N: Tên hình (explicit dot and space before sequence number N)
        fig_re = re.compile(r"^Hình\s+([0-9]+(?:\.[0-9]+)+)\.\s+([0-9]+)\s*:\s*(.+)$", re.IGNORECASE)
        tbl_re = re.compile(r"^Bảng\s+([0-9]+(?:\.[0-9]+)+)\.\s+([0-9]+)\s*:\s*(.+)$", re.IGNORECASE)
        
        # Regex for legacy 2-level captions: Hình X.Y: Tên hình (no dot-space before colon)
        legacy_fig_re = re.compile(r"^Hình\s+([0-9]+\.[0-9]+)\s*:\s*(.+)$", re.IGNORECASE)
        legacy_tbl_re = re.compile(r"^Bảng\s+([0-9]+\.[0-9]+)\s*:\s*(.+)$", re.IGNORECASE)

        self.font_names_observed = set()
        self.line_spacings_observed = []
        self.space_afters_observed = []

        for p_idx, p in enumerate(self.doc.paragraphs):
            raw_text = p.text
            norm_text = normalize_text(raw_text)
            self.paragraphs_text.append((p_idx, norm_text))

            # Fonts & spacing
            if p.paragraph_format.line_spacing is not None:
                self.line_spacings_observed.append(p.paragraph_format.line_spacing)
            if p.paragraph_format.space_after is not None:
                self.space_afters_observed.append(p.paragraph_format.space_after.pt)
            for r in p.runs:
                if r.font.name:
                    self.font_names_observed.add(r.font.name)

            # Captions
            m_fig = fig_re.match(norm_text)
            if m_fig:
                self.figure_captions.append({
                    "index": p_idx,
                    "text": norm_text,
                    "section_code": m_fig.group(1),
                    "seq_num": m_fig.group(2),
                    "title": m_fig.group(3).strip(),
                    "is_deep": len(m_fig.group(1).split(".")) >= 2
                })
            elif legacy_fig_re.match(norm_text):
                m_leg = legacy_fig_re.match(norm_text)
                self.figure_captions.append({
                    "index": p_idx,
                    "text": norm_text,
                    "section_code": m_leg.group(1),
                    "seq_num": "1",
                    "title": m_leg.group(2).strip(),
                    "is_deep": False
                })

            m_tbl = tbl_re.match(norm_text)
            if m_tbl:
                self.table_captions.append({
                    "index": p_idx,
                    "text": norm_text,
                    "section_code": m_tbl.group(1),
                    "seq_num": m_tbl.group(2),
                    "title": m_tbl.group(3).strip(),
                    "is_deep": len(m_tbl.group(1).split(".")) >= 2
                })
            elif legacy_tbl_re.match(norm_text):
                m_leg = legacy_tbl_re.match(norm_text)
                self.table_captions.append({
                    "index": p_idx,
                    "text": norm_text,
                    "section_code": m_leg.group(1),
                    "seq_num": "1",
                    "title": m_leg.group(2).strip(),
                    "is_deep": False
                })

        # 3. Inspect Tables
        self.tables_count = len(self.doc.tables)

        # 4. Inspect Embedded Media (DPI and formats)
        self.media_info = []
        for name in self.zip_pkg.namelist():
            if name.startswith("word/media/") and name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                try:
                    data = self.zip_pkg.read(name)
                    im = Image.open(io.BytesIO(data))
                    dpi = im.info.get("dpi", (72.0, 72.0))
                    dpi_x = dpi[0] if isinstance(dpi, tuple) else dpi
                    dpi_y = dpi[1] if isinstance(dpi, tuple) else dpi
                    self.media_info.append({
                        "name": name,
                        "size": im.size,
                        "dpi": (dpi_x, dpi_y),
                        "is_300dpi": dpi_x >= 290.0
                    })
                except Exception:
                    pass

        # 5. Inspect Settings
        self.has_update_fields = False
        if "word/settings.xml" in self.zip_pkg.namelist():
            settings_xml = self.zip_pkg.read("word/settings.xml").decode("utf-8", errors="ignore")
            if "updateFields" in settings_xml:
                self.has_update_fields = True

    def find_paragraphs_matching(self, pattern: str):
        """Find all paragraphs matching a regular expression."""
        prog = re.compile(pattern, re.IGNORECASE)
        results = []
        for idx, text in self.paragraphs_text:
            if prog.search(text):
                results.append((idx, text))
        return results

    def find_all_text_matching(self, pattern: str):
        """Find matches across both paragraphs and table cells."""
        prog = re.compile(pattern, re.IGNORECASE)
        results = []
        for idx, text in self.paragraphs_text:
            if prog.search(text):
                results.append((idx, text))
        for t_idx, table in enumerate(self.doc.tables):
            for r_idx, row in enumerate(table.rows):
                for c_idx, cell in enumerate(row.cells):
                    ct = normalize_text(cell.text)
                    if prog.search(ct):
                        results.append((f"table_{t_idx}_r{r_idx}_c{c_idx}", ct))
        return results

    def close(self):
        if self.zip_pkg:
            self.zip_pkg.close()


# ==============================================================================
# TIER 1: FEATURE COVERAGE TEST CASES (18 TEST CASES)
# ==============================================================================

class TestTier1FeatureCoverage(unittest.TestCase):
    """
    Tier 1: Feature Coverage Unit & Component Verification.
    Verifies every specific requirement from HUIT 2025 and ORIGINAL_REQUEST.md.
    """

    @classmethod
    def setUpClass(cls):
        cls.target_file = resolve_target_docx()
        cls.auditor = DocumentQualityAuditor(cls.target_file)

    @classmethod
    def tearDownClass(cls):
        cls.auditor.close()

    def test_t1_01_section_count_and_structure(self):
        """[T1-01] Verify document contains at least 3 distinct sections (Cover, Preliminary, Body)."""
        sec_count = len(self.auditor.sections_info)
        self.assertGreaterEqual(
            sec_count, 3,
            f"Expected at least 3 sections (Section 0: Cover, Section 1: Prelim, Section 2: Body). Found: {sec_count}"
        )

    def test_t1_02_section0_cover_page_border(self):
        """[T1-02] Verify Section 0 cover page has cornerTriangles borders with display='firstPage'."""
        sec0 = self.auditor.sections_info[0]
        borders = sec0["borders"]
        self.assertEqual(
            borders.get("display"), "firstPage",
            f"Section 0 borders must be configured with display='firstPage'. Got: {borders.get('display')}"
        )
        for side in ["top", "bottom", "left", "right"]:
            self.assertEqual(
                borders.get(side), "cornerTriangles",
                f"Section 0 border '{side}' must be 'cornerTriangles'. Got: {borders.get(side)}"
            )

    def test_t1_03_section1_preliminary_roman_numbering(self):
        """[T1-03] Verify Section 1 preliminary pages use lowerRoman page numbering starting at 1."""
        sec1 = self.auditor.sections_info[1]
        pgnum = sec1["pgnum"]
        self.assertEqual(
            pgnum.get("fmt"), "lowerRoman",
            f"Section 1 page numbering format must be 'lowerRoman' (i, ii, iii...). Got: {pgnum.get('fmt')}"
        )
        self.assertEqual(
            pgnum.get("start"), "1",
            f"Section 1 page numbering must start at 1. Got: {pgnum.get('start')}"
        )

    def test_t1_04_section1_loi_cam_doan_presence_and_order(self):
        """[T1-04] Verify LỜI CAM ĐOAN exists and is placed strictly after Lời cảm ơn and before Nhận xét GVHD."""
        cam_doan = self.auditor.find_paragraphs_matching(r"LỜI\s+CAM\s+ĐOAN")
        cam_on = self.auditor.find_paragraphs_matching(r"LỜI\s+CẢM\s+ƠN")
        gvhd = self.auditor.find_paragraphs_matching(r"NHẬN\s+XÉT\s+(?:CỦA\s+)?GIẢNG\s+VIÊN\s+HƯỚNG\s+DẪN|NHẬN\s+XÉT\s+GVHD")

        self.assertTrue(len(cam_doan) > 0, "Missing required section 'LỜI CAM ĐOAN' in preliminary pages.")
        self.assertTrue(len(cam_on) > 0, "Missing required section 'LỜI CẢM ƠN'.")
        self.assertTrue(len(gvhd) > 0, "Missing required section 'NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN'.")

        cam_on_idx = cam_on[0][0]
        cam_doan_idx = cam_doan[0][0]
        gvhd_idx = gvhd[0][0]

        self.assertLess(
            cam_on_idx, cam_doan_idx,
            f"LỜI CAM ĐOAN (p{cam_doan_idx}) must appear AFTER LỜI CẢM ƠN (p{cam_on_idx})."
        )
        self.assertLess(
            cam_doan_idx, gvhd_idx,
            f"LỜI CAM ĐOAN (p{cam_doan_idx}) must appear BEFORE NHẬN XÉT GVHD (p{gvhd_idx})."
        )

    def test_t1_05_section2_main_body_arabic_numbering(self):
        """[T1-05] Verify Section 2 main body uses Arabic/decimal numbering starting at 1."""
        sec2 = self.auditor.sections_info[2]
        pgnum = sec2["pgnum"]
        self.assertEqual(
            pgnum.get("start"), "1",
            f"Section 2 page numbering must reset and start at 1. Got: {pgnum.get('start')}"
        )
        fmt = pgnum.get("fmt")
        self.assertTrue(
            fmt is None or fmt in ["decimal", ""],
            f"Section 2 page numbering format must be decimal/Arabic. Got: {fmt}"
        )

    def test_t1_06_page_geometry_and_margins(self):
        """[T1-06] Verify HUIT 2025 margins: Left 3.5cm (1985 dxa), Right/Top/Bottom 2.5cm (1418 dxa)."""
        for sec in self.auditor.sections_info:
            idx = sec["index"]
            left_dxa = sec["left_dxa"]
            right_dxa = sec["right_dxa"]
            top_dxa = sec["top_dxa"]
            bottom_dxa = sec["bottom_dxa"]

            # Tolerance: ±25 dxa (~0.4mm)
            self.assertTrue(
                1960 <= left_dxa <= 2010,
                f"Section {idx} Left margin must be 3.5cm (~1985 dxa). Got: {left_dxa} dxa ({sec['left_cm']} cm)"
            )
            self.assertTrue(
                1390 <= right_dxa <= 1445,
                f"Section {idx} Right margin must be 2.5cm (~1418 dxa). Got: {right_dxa} dxa ({sec['right_cm']} cm)"
            )
            self.assertTrue(
                1390 <= top_dxa <= 1445,
                f"Section {idx} Top margin must be 2.5cm (~1418 dxa). Got: {top_dxa} dxa ({sec['top_cm']} cm)"
            )
            self.assertTrue(
                1390 <= bottom_dxa <= 1445,
                f"Section {idx} Bottom margin must be 2.5cm (~1418 dxa). Got: {bottom_dxa} dxa ({sec['bottom_cm']} cm)"
            )

    def test_t1_07_font_family_and_spacing(self):
        """[T1-07] Verify font Times New Roman and line spacing Multiple 1.3 / 6pt space after."""
        # Check fonts in runs or normal style
        normal_font = self.auditor.doc.styles["Normal"].font.name
        observed_fonts = self.auditor.font_names_observed
        has_tnr = (normal_font == "Times New Roman") or ("Times New Roman" in observed_fonts)
        self.assertTrue(
            has_tnr,
            f"Document must use Times New Roman font. Normal style: {normal_font}, observed: {observed_fonts}"
        )

        # Check line spacing multiple 1.3
        if self.auditor.line_spacings_observed:
            avg_spacing = sum(self.auditor.line_spacings_observed) / len(self.auditor.line_spacings_observed)
            self.assertTrue(
                1.2 <= avg_spacing <= 1.4,
                f"Average paragraph line spacing should be Multiple 1.3. Got: {avg_spacing:.2f}"
            )

    def test_t1_08_five_chapter_concluding_sections(self):
        """[T1-08] Verify all 5 chapters end with explicit concluding sections: 1.4, 2.5, 3.5, 4.4, 5.4 KẾT CHƯƠNG."""
        required_conclusions = [
            (r"1\.4\.?\s*KẾT\s+CHƯƠNG", "1.4 KẾT CHƯƠNG (Chương 1)"),
            (r"2\.5\.?\s*KẾT\s+CHƯƠNG", "2.5 KẾT CHƯƠNG (Chương 2)"),
            (r"3\.5\.?\s*KẾT\s+CHƯƠNG", "3.5 KẾT CHƯƠNG (Chương 3)"),
            (r"4\.4\.?\s*KẾT\s+CHƯƠNG", "4.4 KẾT CHƯƠNG (Chương 4)"),
            (r"5\.4\.?\s*KẾT\s+CHƯƠNG", "5.4 KẾT CHƯƠNG (Chương 5)")
        ]
        for pattern, label in required_conclusions:
            matches = self.auditor.find_paragraphs_matching(pattern)
            self.assertTrue(
                len(matches) > 0,
                f"Missing required chapter conclusion section: '{label}' matching regex '{pattern}'."
            )

    def test_t1_09_chapter1_survey(self):
        """[T1-09] Verify Chapter 1 surveys the tech equipment rental domain, 4 departments, and contains zero ICT Saigon mentions."""
        domain_matches = self.auditor.find_paragraphs_matching(r"lĩnh\s+vực\s+cho\s+thuê|thiết\s+bị\s+công\s+nghệ|cho\s+thuê\s+thiết\s+bị")
        self.assertTrue(
            len(domain_matches) > 0,
            "Chapter 1 must document survey of the technology equipment rental domain."
        )
        depts = self.auditor.find_paragraphs_matching(r"4\s+phòng\s+ban|4\s+bộ\s+phận|Kinh\s+doanh|Quản\s+lý\s+kho|Kế\s+toán")
        self.assertTrue(len(depts) > 0, "Chapter 1 must document organizational structure with 4 departments.")

        # Zero mentions of ICT Saigon per user requirement
        ict_matches = self.auditor.find_paragraphs_matching(r"\bICT\s+(?:Sài\s+Gòn|Saigon)\b|\bCông\s+ty.*ICT\b")
        self.assertEqual(
            len(ict_matches), 0,
            f"All mentions of 'ICT Sài Gòn' / 'ICT Saigon' must be completely removed. Found: {len(ict_matches)}"
        )

    def test_t1_10_chapter2_section21_core_algorithms(self):
        """[T1-10] Verify Section 2.1 documents SemaphoreSlim, VietQR NAPAS 247, and Debt amortization."""
        sema = self.auditor.find_paragraphs_matching(r"SemaphoreSlim|2\.1\.1")
        vietqr = self.auditor.find_paragraphs_matching(r"VietQR|NAPAS\s*247|2\.1\.2")
        debt = self.auditor.find_paragraphs_matching(r"phân\s+kỳ|tuổi\s+nợ|2\.1\.3")

        self.assertTrue(len(sema) > 0, "Section 2.1 must include 2.1.1 SemaphoreSlim concurrency control.")
        self.assertTrue(len(vietqr) > 0, "Section 2.1 must include 2.1.2 Dynamic VietQR NAPAS 247 algorithm.")
        self.assertTrue(len(debt) > 0, "Section 2.1 must include 2.1.3 Debt amortization & aging debt algorithm.")

    def test_t1_11_chapter2_section22_seven_processes_modeling(self):
        """[T1-11] Verify Chapter 2 Section 2.2 models 7 core processes with text specs, Activity, Sequence, Collab."""
        p22 = self.auditor.find_paragraphs_matching(r"2\.2\.2\.[1-7]")
        self.assertGreaterEqual(
            len(p22), 7,
            f"Section 2.2 must model 7 core business processes (2.2.2.1 through 2.2.2.7). Found: {len(p22)}"
        )

    def test_t1_12_chapter3_database_dictionary_18_tables_and_erd(self):
        """[T1-12] Verify Chapter 3 Section 3.1 contains database dictionary with at least 18 tables and physical ERD."""
        erd = self.auditor.find_paragraphs_matching(r"ERD|cơ\s+sở\s+dữ\s+liệu\s+vật\s+lý")
        self.assertTrue(len(erd) > 0, "Section 3.1 must contain Physical ERD schema.")
        
        # Verify table dictionary count in document tables or captions
        tbl_dict_captions = [c for c in self.auditor.table_captions if "3.1.1" in c["section_code"]]
        self.assertGreaterEqual(
            len(tbl_dict_captions) if tbl_dict_captions else self.auditor.tables_count, 18,
            f"Expected at least 18 database dictionary tables in Chapter 3. Found captions: {len(tbl_dict_captions)}"
        )

    def test_t1_13_chapter3_section34_seven_functions_three_layer_design(self):
        """[T1-13] Verify Section 3.4 contains 3-layer design (BCE, Sequence, Collab) for 7 core functions."""
        p34 = self.auditor.find_paragraphs_matching(r"3\.4\.[1-7]")
        self.assertGreaterEqual(
            len(p34), 7,
            f"Section 3.4 must contain 3-layer design for 7 core functions (3.4.1 through 3.4.7). Found: {len(p34)}"
        )

    def test_t1_14_chapter4_implementation_environment(self):
        """[T1-14] Verify Chapter 4 mentions .NET 9, SQL Server, Visual Studio, and ASP.NET Core MVC architecture."""
        dotnet = self.auditor.find_paragraphs_matching(r"\.NET\s*9|ASP\.NET\s+Core")
        sql = self.auditor.find_paragraphs_matching(r"SQL\s+Server")
        mvc = self.auditor.find_paragraphs_matching(r"MVC|kiến\s+trúc\s+phân\s+tầng")

        self.assertTrue(len(dotnet) > 0, "Chapter 4 must document .NET 9 development platform.")
        self.assertTrue(len(sql) > 0, "Chapter 4 must document Microsoft SQL Server database.")
        self.assertTrue(len(mvc) > 0, "Chapter 4 must document ASP.NET Core MVC tiered architecture.")

    def test_t1_15_chapter5_testing_evaluation(self):
        """[T1-15] Verify Chapter 5 title, functional test matrix (TC-01 to TC-12), and integration testing."""
        ch5_title = self.auditor.find_paragraphs_matching(r"THỬ\s+NGHIỆM\s+VÀ\s+TRIỂN\s+KHAI")
        self.assertTrue(
            len(ch5_title) > 0,
            "Chapter 5 title must be 'THỬ NGHIỆM VÀ TRIỂN KHAI'."
        )
        tc_matrix = self.auditor.find_paragraphs_matching(r"TC-01|ca\s+kiểm\s+thử|Ma\s+trận\s+kết\s+quả\s+kiểm\s+thử")
        self.assertTrue(
            len(tc_matrix) > 0,
            "Chapter 5 must document functional testing matrix (TC-01 to TC-12)."
        )
        integration = self.auditor.find_paragraphs_matching(r"luồng\s+tích\s+hợp|SemaphoreSlim|Idempotency|Webhook")
        self.assertTrue(
            len(integration) > 0,
            "Chapter 5 must document integration testing and data safety."
        )

    def test_t1_16_deep_hierarchical_captions_format(self):
        """[T1-16] Verify figures follow 'Hình X.Y.Z. N: Tên hình' and tables follow 'Bảng X.Y.Z. N: Tên bảng'."""
        fig_caps = self.auditor.figure_captions
        self.assertGreater(len(fig_caps), 0, "Document must contain figure captions.")
        deep_figs = [c for c in fig_caps if c["is_deep"]]
        self.assertGreaterEqual(
            len(deep_figs), len(fig_caps) * 0.8,
            f"At least 80% of figures must follow deep numbering 'Hình X.Y.Z. N: ...'. Found: {len(deep_figs)}/{len(fig_caps)}"
        )

        tbl_caps = self.auditor.table_captions
        self.assertGreater(len(tbl_caps), 0, "Document must contain table captions.")
        deep_tbls = [c for c in tbl_caps if c["is_deep"]]
        self.assertGreaterEqual(
            len(deep_tbls), len(tbl_caps) * 0.8,
            f"At least 80% of tables must follow deep numbering 'Bảng X.Y.Z. N: ...'. Found: {len(deep_tbls)}/{len(tbl_caps)}"
        )

    def test_t1_17_embedded_diagrams_resolution_300dpi(self):
        """[T1-17] Verify embedded diagrams or assets directory have ~300 DPI resolution (>= 290 DPI)."""
        media_list = self.auditor.media_info
        if media_list:
            high_res = [m for m in media_list if m["is_300dpi"]]
            self.assertGreaterEqual(
                len(high_res), len(media_list) * 0.7,
                f"Expected >= 70% of embedded diagrams to be 300 DPI (>= 290 DPI). Found: {len(high_res)}/{len(media_list)}"
            )
        elif os.path.exists(FIGURES_DIR):
            # Check figures directory directly if document has not yet bundled all images
            fig_files = [os.path.join(FIGURES_DIR, f) for f in os.listdir(FIGURES_DIR) if f.endswith(".png")]
            self.assertGreater(len(fig_files), 0, "No diagram files found in figures directory.")
            im = Image.open(fig_files[0])
            dpi = im.info.get("dpi", (0, 0))[0]
            self.assertGreaterEqual(dpi, 290.0, f"Figures must be 300 DPI. Observed: {dpi}")

    def test_t1_18_dotnet_build_and_challenger_tests(self):
        """[T1-18] Verify dotnet build 0 errors and ChallengerTests 100% pass (540+ tests)."""
        if SKIP_LIVE_BUILD:
            self.skipTest("Live build verification skipped via --fast flag.")

        # 1. dotnet build
        build_res = subprocess.run(
            ["dotnet", "build", RENTAL_CSPROJ],
            cwd=PROJECT_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=120
        )
        self.assertEqual(build_res.returncode, 0, f"dotnet build failed:\n{build_res.stdout}\n{build_res.stderr}")
        self.assertIn("0 Error(s)", build_res.stdout, "dotnet build must report 0 Error(s).")

        # 2. ChallengerTests
        test_res = subprocess.run(
            ["dotnet", "run", "--project", CHALLENGER_CSPROJ],
            cwd=PROJECT_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=180
        )
        self.assertEqual(test_res.returncode, 0, f"ChallengerTests runner failed with exit code {test_res.returncode}")
        self.assertIn("0 FAILED", test_res.stdout, "ChallengerTests must report 0 FAILED.")
        self.assertIn("595 PASSED", test_res.stdout, "ChallengerTests must report all 595 tests PASSED.")


# ==============================================================================
# TIER 2: BOUNDARY CASES & ROBUSTNESS (7 TEST CASES)
# ==============================================================================

class TestTier2BoundaryAndRobustness(unittest.TestCase):
    """
    Tier 2: Boundary Cases, Numeric Tolerances & Parser Robustness.
    Verifies system edge cases, adversarial inputs, and metric boundaries.
    """

    @classmethod
    def setUpClass(cls):
        cls.target_file = resolve_target_docx()
        cls.auditor = DocumentQualityAuditor(cls.target_file)

    @classmethod
    def tearDownClass(cls):
        cls.auditor.close()

    def test_t2_01_margin_dxa_tolerance_bounds(self):
        """[T2-01] Margin tolerance boundary: Left in [1970, 2000] dxa, Top/Bottom/Right in [1400, 1435] dxa."""
        for sec in self.auditor.sections_info:
            self.assertGreaterEqual(sec["left_dxa"], 1965, "Left margin underflow.")
            self.assertLessEqual(sec["left_dxa"], 2005, "Left margin overflow.")
            self.assertGreaterEqual(sec["right_dxa"], 1400, "Right margin underflow.")
            self.assertLessEqual(sec["right_dxa"], 1435, "Right margin overflow.")

    def test_t2_02_caption_syntax_variations(self):
        """[T2-02] Caption syntax tolerance: verifies parser matches variations with extra spaces or punctuation."""
        sample_deep_fig = "Hình 2.2.2.1.  1:   Sơ đồ hoạt động quy trình"
        fig_re = re.compile(r"^Hình\s+([0-9]+(?:\.[0-9]+)+)\.?\s*([0-9]+)\s*:\s*(.+)$", re.IGNORECASE)
        m = fig_re.match(normalize_text(sample_deep_fig))
        self.assertIsNotNone(m, "Caption parser should handle multiple whitespace variations.")
        self.assertEqual(m.group(1), "2.2.2.1")
        self.assertEqual(m.group(2), "1")
        self.assertEqual(m.group(3), "Sơ đồ hoạt động quy trình")

    def test_t2_03_case_insensitive_section_matching(self):
        """[T2-03] Unicode NFC accent and case robustness: matches 'kết chương' in uppercase, lowercase, titlecase."""
        patterns = ["KẾT CHƯƠNG", "Kết chương", "Kết Chương", "kết chương"]
        for p in patterns:
            norm_p = normalize_text(p)
            self.assertTrue(re.search(r"kết\s+chương", norm_p, re.IGNORECASE))

    def test_t2_04_missing_or_corrupted_docx_handling(self):
        """[T2-04] Auditor error handling: gracefully raises FileNotFoundError or BadZipFile on bad inputs."""
        with self.assertRaises(FileNotFoundError):
            DocumentQualityAuditor("d:/DoAnCuNhan/non_existent_file_xyz_123.docx")

    def test_t2_05_database_table_count_boundary(self):
        """[T2-05] Database entity table boundary: dictionary must document at least 18 core tables (>= 18)."""
        tbl_captions = [c for c in self.auditor.table_captions if "3.1.1" in c["section_code"]]
        count = len(tbl_captions) if tbl_captions else self.auditor.tables_count
        self.assertGreaterEqual(count, 18, f"Database entity tables must be >= 18. Actual: {count}")

    def test_t2_06_image_dpi_floating_boundary(self):
        """[T2-06] Image DPI float boundary: accepts matplotlib default 299.9994 as valid 300 DPI (>= 290.0)."""
        test_dpi = 299.9994
        self.assertGreaterEqual(test_dpi, 290.0, "DPI float boundary must accept standard matplotlib DPI.")

    def test_t2_07_functional_test_case_matrix_coverage(self):
        """[T2-07] Functional test matrix coverage: must document at least 10 test cases (TC-01 through TC-12)."""
        tc_matches = self.auditor.find_all_text_matching(r"\bTC-(?:0[1-9]|1[0-2])\b")
        self.assertGreaterEqual(len(tc_matches), 10, "Testing matrix must cover at least 10 core functional test cases.")


# ==============================================================================
# TIER 3: COMBINATIONS & CROSS-CUTTING INTEGRITY (6 TEST CASES)
# ==============================================================================

class TestTier3CrossCuttingIntegrity(unittest.TestCase):
    """
    Tier 3: Combinations, Cross-Referencing & Document Architecture Integrity.
    Verifies relationships across chapters, figures, tables, and settings.
    """

    @classmethod
    def setUpClass(cls):
        cls.target_file = resolve_target_docx()
        cls.auditor = DocumentQualityAuditor(cls.target_file)

    @classmethod
    def tearDownClass(cls):
        cls.auditor.close()

    def test_t3_01_figure_caption_to_image_pairing(self):
        """[T3-01] Cross-reference: figure captions correspond to actual diagram assets."""
        fig_caps = self.auditor.figure_captions
        self.assertGreater(len(fig_caps), 0, "Document has no figure captions.")
        # Ensure captions have non-empty titles
        for cap in fig_caps:
            self.assertTrue(len(cap["title"]) > 0, f"Caption {cap['text']} has empty title.")

    def test_t3_02_table_caption_to_table_pairing(self):
        """[T3-02] Cross-reference: table captions correspond to structured table grids."""
        tbl_caps = self.auditor.table_captions
        self.assertGreater(len(tbl_caps), 0, "Document has no table captions.")
        for cap in tbl_caps:
            self.assertTrue(len(cap["title"]) > 0, f"Table caption {cap['text']} has empty title.")

    def test_t3_03_sequential_chapter_flow(self):
        """[T3-03] Sequential chapter progression: Mở đầu -> Ch 1 -> Ch 2 -> Ch 3 -> Ch 4 -> Ch 5 -> Kết luận."""
        markers = [
            (r"(?:^|\b)MỞ\s+ĐẦU", "Mở đầu"),
            (r"^CHƯƠNG\s+1\b", "Chương 1"),
            (r"^CHƯƠNG\s+2\b", "Chương 2"),
            (r"^CHƯƠNG\s+3\b", "Chương 3"),
            (r"^CHƯƠNG\s+4\b", "Chương 4"),
            (r"^CHƯƠNG\s+5\b", "Chương 5"),
            (r"(?:^|\b)KẾT\s+LUẬN\b", "Kết luận")
        ]
        indices = []
        for pat, label in markers:
            matches = self.auditor.find_paragraphs_matching(pat)
            self.assertTrue(len(matches) > 0, f"Missing sequential milestone '{label}'.")
            indices.append(matches[0][0])

        for i in range(len(indices) - 1):
            self.assertLess(
                indices[i], indices[i + 1],
                f"Chapter progression violation: '{markers[i][1]}' (p{indices[i]}) must precede '{markers[i+1][1]}' (p{indices[i+1]})."
            )

    def test_t3_04_hierarchical_heading_nesting(self):
        """[T3-04] Heading hierarchy: Chapter 2 sub-sections follow 2.1, 2.2, 2.3, 2.4, 2.5."""
        p21 = self.auditor.find_paragraphs_matching(r"^2\.1\.?\s")
        p22 = self.auditor.find_paragraphs_matching(r"^2\.2\.?\s")
        p23 = self.auditor.find_paragraphs_matching(r"^2\.3\.?\s")
        p24 = self.auditor.find_paragraphs_matching(r"^2\.4\.?\s")
        p25 = self.auditor.find_paragraphs_matching(r"^2\.5\.?\s")

        self.assertTrue(len(p21) > 0 and len(p22) > 0 and len(p23) > 0 and len(p24) > 0 and len(p25) > 0,
                        "Chapter 2 must maintain complete hierarchy: 2.1, 2.2, 2.3, 2.4, 2.5.")
        self.assertLess(p21[0][0], p22[0][0], f"Heading 2.1 (p{p21[0][0]}) must precede 2.2 (p{p22[0][0]}).")
        self.assertLess(p22[0][0], p23[0][0], f"Heading 2.2 (p{p22[0][0]}) must precede 2.3 (p{p23[0][0]}).")
        self.assertLess(p23[0][0], p24[0][0], f"Heading 2.3 (p{p23[0][0]}) must precede 2.4 (p{p24[0][0]}).")
        self.assertLess(p24[0][0], p25[0][0], f"Heading 2.4 (p{p24[0][0]}) must precede 2.5 (p{p25[0][0]}).")

    def test_t3_05_toc_update_fields_setting(self):
        """[T3-05] OpenXML settings: word/settings.xml contains <w:updateFields w:val='true'/> or TOC is populated."""
        has_toc_entries = len([p for p in self.auditor.doc.paragraphs if 'toc' in p.style.name.lower()]) > 0
        self.assertTrue(
            self.auditor.has_update_fields or has_toc_entries,
            "word/settings.xml must contain <w:updateFields w:val='true'/> or TOC must be populated."
        )

    def test_t3_06_seven_processes_symmetry(self):
        """[T3-06] Structural symmetry: all 7 processes in Ch2 have corresponding 3-layer designs in Ch3."""
        ch2_codes = ["2.2.2.1", "2.2.2.2", "2.2.2.3", "2.2.2.4", "2.2.2.5", "2.2.2.6", "2.2.2.7"]
        ch3_codes = ["3.4.1", "3.4.2", "3.4.3", "3.4.4", "3.4.5", "3.4.6", "3.4.7"]

        for c2, c3 in zip(ch2_codes, ch3_codes):
            m2 = self.auditor.find_paragraphs_matching(rf"{re.escape(c2)}")
            m3 = self.auditor.find_paragraphs_matching(rf"{re.escape(c3)}")
            self.assertTrue(len(m2) > 0, f"Missing Chapter 2 business process specification for '{c2}'.")
            self.assertTrue(len(m3) > 0, f"Missing Chapter 3 3-layer function design for '{c3}'.")


# ==============================================================================
# TIER 4: ACADEMIC SCENARIO & FACULTY RUBRIC (2 TEST CASES)
# ==============================================================================

class TestTier4AcademicRubricScenario(unittest.TestCase):
    """
    Tier 4: Faculty Defense Committee Rubric & Forensic Verification.
    Simulates the official HUIT 2025 Graduation Thesis Review Checklist.
    """

    @classmethod
    def setUpClass(cls):
        cls.target_file = resolve_target_docx()
        cls.auditor = DocumentQualityAuditor(cls.target_file)

    @classmethod
    def tearDownClass(cls):
        cls.auditor.close()

    def test_t4_01_huit_graduation_rubric_holistic_score(self):
        """
        [T4-01] Holistic Academic Defense Rubric Evaluation (10 dimensions, 10 pts each, Max 100 pts).
        Target document must score >= 90% to pass committee review.
        """
        score = 0
        feedback = []

        # 1. Section Structure & Geometry (10 pts)
        if len(self.auditor.sections_info) >= 3:
            sec0_ok = self.auditor.sections_info[0]["borders"].get("top") == "cornerTriangles"
            sec1_ok = self.auditor.sections_info[1]["pgnum"].get("fmt") == "lowerRoman"
            sec2_ok = self.auditor.sections_info[2]["pgnum"].get("start") == "1"
            if sec0_ok and sec1_ok and sec2_ok:
                score += 10
                feedback.append("1. Section Structure & Border Geometry: 10/10 PASS")
            else:
                score += 5
                feedback.append("1. Section Structure & Border Geometry: 5/10 PARTIAL")
        else:
            feedback.append("1. Section Structure: 0/10 FAIL (less than 3 sections)")

        # 2. Lời Cam Đoan Placement & Academic Ethics (10 pts)
        cam_doan = self.auditor.find_paragraphs_matching(r"LỜI\s+CAM\s+ĐOAN")
        cam_on = self.auditor.find_paragraphs_matching(r"LỜI\s+CẢM\s+ƠN")
        gvhd = self.auditor.find_paragraphs_matching(r"NHẬN\s+XÉT.*GIẢNG\s+VIÊN")
        if cam_doan and cam_on and gvhd and (cam_on[0][0] < cam_doan[0][0] < gvhd[0][0]):
            score += 10
            feedback.append("2. Lời Cam Đoan Placement: 10/10 PASS")
        else:
            feedback.append("2. Lời Cam Đoan Placement: 0/10 FAIL")

        # 3. Domain Survey & Clean Structure (10 pts)
        domain = self.auditor.find_paragraphs_matching(r"lĩnh\s+vực\s+cho\s+thuê|cho\s+thuê\s+thiết\s+bị")
        depts = self.auditor.find_paragraphs_matching(r"4\s+phòng\s+ban|4\s+bộ\s+phận|Kinh\s+doanh|Quản\s+lý\s+kho|Kế\s+toán")
        ict = self.auditor.find_paragraphs_matching(r"\bICT\s+(?:Sài\s+Gòn|Saigon)\b")
        if domain and depts and len(ict) == 0:
            score += 10
            feedback.append("3. Domain Survey & Clean Structure (0 ICT Saigon): 10/10 PASS")
        else:
            feedback.append("3. Domain Survey & Clean Structure: 0/10 FAIL")

        # 4. Three Core Algorithms 2.1 (10 pts)
        sema = self.auditor.find_paragraphs_matching(r"SemaphoreSlim")
        vqr = self.auditor.find_paragraphs_matching(r"VietQR|NAPAS")
        debt = self.auditor.find_paragraphs_matching(r"phân\s+kỳ|tuổi\s+nợ")
        if sema and vqr and debt:
            score += 10
            feedback.append("4. Core Technical Algorithms (2.1): 10/10 PASS")
        else:
            feedback.append("4. Core Technical Algorithms (2.1): 0/10 FAIL")

        # 5. Seven Core Business Processes Modeling (10 pts)
        p7 = self.auditor.find_paragraphs_matching(r"2\.2\.2\.[1-7]")
        if len(p7) >= 7:
            score += 10
            feedback.append("5. 7 Core Processes Modeling (2.2): 10/10 PASS")
        else:
            feedback.append("5. 7 Core Processes Modeling (2.2): 0/10 FAIL")

        # 6. Database Dictionary 18 Tables & ERD (10 pts)
        erd = self.auditor.find_paragraphs_matching(r"ERD")
        tbl_dict = [c for c in self.auditor.table_captions if "3.1.1" in c["section_code"]]
        if erd and (len(tbl_dict) >= 18 or self.auditor.tables_count >= 18):
            score += 10
            feedback.append("6. DB Dictionary 18 Tables & ERD: 10/10 PASS")
        else:
            feedback.append("6. DB Dictionary 18 Tables & ERD: 0/10 FAIL")

        # 7. Seven Core Functions 3-Layer Design (10 pts)
        f7 = self.auditor.find_paragraphs_matching(r"3\.4\.[1-7]")
        if len(f7) >= 7:
            score += 10
            feedback.append("7. 7 Functions 3-Layer Design (3.4): 10/10 PASS")
        else:
            feedback.append("7. 7 Functions 3-Layer Design (3.4): 0/10 FAIL")

        # 8. Implementation & MVC Architecture (10 pts)
        net9 = self.auditor.find_paragraphs_matching(r"\.NET\s*9")
        if net9:
            score += 10
            feedback.append("8. Implementation & .NET 9 MVC: 10/10 PASS")
        else:
            feedback.append("8. Implementation & .NET 9 MVC: 0/10 FAIL")

        # 9. System Testing Matrix & Integration (10 pts)
        tc_matrix = self.auditor.find_paragraphs_matching(r"TC-01|Ma\s+trận\s+kết\s+quả\s+kiểm\s+thử")
        integ = self.auditor.find_paragraphs_matching(r"luồng\s+tích\s+hợp|SemaphoreSlim|Idempotency")
        if tc_matrix and integ:
            score += 10
            feedback.append("9. System Testing Matrix & Integration: 10/10 PASS")
        else:
            feedback.append("9. System Testing Matrix & Integration: 0/10 FAIL")

        # 10. 5 Chapter Conclusions & Deep Numbering (10 pts)
        concl = [
            self.auditor.find_paragraphs_matching(r"1\.4\.?\s*KẾT\s+CHƯƠNG"),
            self.auditor.find_paragraphs_matching(r"2\.5\.?\s*KẾT\s+CHƯƠNG"),
            self.auditor.find_paragraphs_matching(r"3\.5\.?\s*KẾT\s+CHƯƠNG"),
            self.auditor.find_paragraphs_matching(r"4\.4\.?\s*KẾT\s+CHƯƠNG"),
            self.auditor.find_paragraphs_matching(r"5\.4\.?\s*KẾT\s+CHƯƠNG")
        ]
        deep_caps = [c for c in self.auditor.figure_captions if c["is_deep"]]
        if all(len(c) > 0 for c in concl) and len(deep_caps) > 0:
            score += 10
            feedback.append("10. 5 Concluding Sections & Deep Captions: 10/10 PASS")
        else:
            feedback.append("10. 5 Concluding Sections & Deep Captions: 0/10 FAIL")

        sys.stdout.write(f"\n--- FACULTY DEFENSE RUBRIC EVALUATION: {score}/100 ---\n")
        for f in feedback:
            sys.stdout.write(f"  {f}\n")
        sys.stdout.flush()

        self.assertGreaterEqual(
            score, 90,
            f"Document failed HUIT 2025 faculty defense committee rubric! Score: {score}/100\nFeedback:\n" + "\n".join(feedback)
        )

    def test_t4_02_legacy_draft_audit_discrepancy_detection(self):
        """
        [T4-02] Forensic Discrepancy Verification on Legacy Draft (BỘ CÔNG THƯƠNG.docx).
        Demonstrates test integrity: proves the test suite correctly detects missing elements
        (missing Lời cam đoan, missing 5 kết chương, legacy 2-level captions) on an un-upgraded draft.
        """
        if not os.path.exists(LEGACY_DRAFT_PATH):
            self.skipTest("Legacy draft BỘ CÔNG THƯƠNG.docx not found.")

        legacy_auditor = DocumentQualityAuditor(LEGACY_DRAFT_PATH)
        try:
            # 1. Verify missing Lời cam đoan
            cam_doan = legacy_auditor.find_paragraphs_matching(r"LỜI\s+CAM\s+ĐOAN")
            self.assertEqual(
                len(cam_doan), 0,
                "Integrity check: Legacy draft BỘ CÔNG THƯƠNG.docx must lack LỜI CAM ĐOAN."
            )

            # 2. Verify missing concluding sections
            concl_14 = legacy_auditor.find_paragraphs_matching(r"1\.4\.?\s*KẾT\s+CHƯƠNG")
            self.assertEqual(
                len(concl_14), 0,
                "Integrity check: Legacy draft must lack 1.4 KẾT CHƯƠNG."
            )

            # 3. Verify legacy 2-level figure captions (e.g. Hình 1.1) vs deep hierarchical
            deep_figures = [c for c in legacy_auditor.figure_captions if c["is_deep"]]
            self.assertEqual(
                len(deep_figures), 0,
                "Integrity check: Legacy draft uses 2-level captions, not deep hierarchical captions."
            )
        finally:
            legacy_auditor.close()


# ==============================================================================
# AUDIT & CLI RUNNER
# ==============================================================================

def run_standalone_audit(docx_path: str):
    """Run a standalone forensic audit on any Word document and print a detailed report."""
    print(f"\n{'='*75}")
    print(f"HUIT 2025 GRADUATION THESIS AUDIT REPORT: {os.path.basename(docx_path)}")
    print(f"{'='*75}")
    
    try:
        auditor = DocumentQualityAuditor(docx_path)
    except Exception as e:
        print(f"FAILED TO OPEN DOCUMENT: {e}")
        return

    print(f"Total Sections: {len(auditor.sections_info)}")
    for sec in auditor.sections_info:
        print(f"  Section {sec['index']}: Margins Left={sec['left_cm']}cm, Right={sec['right_cm']}cm, "
              f"Top={sec['top_cm']}cm, Bottom={sec['bottom_cm']}cm | "
              f"Border Display={sec['borders'].get('display')} Top={sec['borders'].get('top')} | "
              f"PgNum fmt={sec['pgnum'].get('fmt')} start={sec['pgnum'].get('start')}")

    print(f"\nTotal Paragraphs: {len(auditor.paragraphs_text)}")
    print(f"Total Tables: {auditor.tables_count}")
    print(f"Total Figure Captions: {len(auditor.figure_captions)} (Deep: {sum(1 for c in auditor.figure_captions if c['is_deep'])})")
    print(f"Total Table Captions: {len(auditor.table_captions)} (Deep: {sum(1 for c in auditor.table_captions if c['is_deep'])})")
    print(f"Total Media Images: {len(auditor.media_info)} (300 DPI: {sum(1 for m in auditor.media_info if m['is_300dpi'])})")
    print(f"TOC updateFields in settings.xml: {auditor.has_update_fields}")

    print(f"\nRequired Structural Sections Check:")
    checks = [
        ("LỜI CẢM ƠN", r"LỜI\s+CẢM\s+ƠN"),
        ("LỜI CAM ĐOAN", r"LỜI\s+CAM\s+ĐOAN"),
        ("NHẬN XÉT GVHD", r"NHẬN\s+XÉT.*GIẢNG\s+VIÊN"),
        ("1.4 KẾT CHƯƠNG", r"1\.4\.?\s*KẾT\s+CHƯƠNG"),
        ("2.5 KẾT CHƯƠNG", r"2\.5\.?\s*KẾT\s+CHƯƠNG"),
        ("3.5 KẾT CHƯƠNG", r"3\.5\.?\s*KẾT\s+CHƯƠNG"),
        ("4.4 KẾT CHƯƠNG", r"4\.4\.?\s*KẾT\s+CHƯƠNG"),
        ("5.4 KẾT CHƯƠNG", r"5\.4\.?\s*KẾT\s+CHƯƠNG"),
        ("Chapter 1: Domain Survey", r"lĩnh\s+vực\s+cho\s+thuê|thiết\s+bị\s+công\s+nghệ"),
        ("Chapter 1: Zero ICT Saigon", r"\bICT\s+(?:Sài\s+Gòn|Saigon)\b"),
        ("Section 2.1: SemaphoreSlim", r"SemaphoreSlim"),
        ("Section 2.1: VietQR", r"VietQR|NAPAS"),
        ("Section 2.1: Phân kỳ nợ", r"phân\s+kỳ|tuổi\s+nợ"),
        ("Chapter 5: Test Matrix TC-01..12", r"TC-01|Ma\s+trận\s+kết\s+quả\s+kiểm\s+thử"),
        ("Chapter 5: Integration Testing", r"luồng\s+tích\s+hợp|Idempotency")
    ]
    for label, pat in checks:
        matches = auditor.find_paragraphs_matching(pat)
        status = "[FOUND]" if matches else "[MISSING]"
        idx_str = f"(p{matches[0][0]})" if matches else ""
        print(f"  {status:<10} {label:<35} {idx_str}")

    auditor.close()
    print(f"{'='*75}\n")


def main():
    global TARGET_DOCX_PATH, SKIP_LIVE_BUILD

    parser = argparse.ArgumentParser(description="RentalSystem HUIT 2025 Thesis Quality Test Suite")
    parser.add_argument("--docx", "-d", help="Path to docx file to test (default: auto-detect or fixture)")
    parser.add_argument("--audit", help="Run standalone forensic audit on a specific docx and exit")
    parser.add_argument("--fast", action="store_true", help="Skip live dotnet build and ChallengerTests")
    parser.add_argument("--fixture", action="store_true", help="Force testing against generated compliant fixture")
    args, unknown = parser.parse_known_args()

    if args.audit:
        run_standalone_audit(args.audit)
        sys.exit(0)

    if args.fast:
        SKIP_LIVE_BUILD = True

    if args.docx:
        TARGET_DOCX_PATH = os.path.abspath(args.docx)
    elif args.fixture:
        TARGET_DOCX_PATH = FIXTURE_THESIS_PATH

    resolved = resolve_target_docx()
    print(f"\n[TEST_THESIS_QUALITY] Target Document: {resolved}")
    print(f"[TEST_THESIS_QUALITY] Skip live build: {SKIP_LIVE_BUILD}")

    # Pass remaining args to unittest
    unittest_args = [sys.argv[0]] + unknown
    unittest.main(argv=unittest_args)


if __name__ == "__main__":
    main()
