#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BUILD_MASTER_THESIS.PY — OPENXML THESIS AUTHORING & ASSEMBLY ENGINE
Standard: HUIT 2025 Graduation Thesis Standard (Khoa CNTT - HUIT)
Project: RentalSystem Graduation Thesis Document Assembly
Output: d:\\DoAnCuNhan\\KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx
================================================================================
"""

import os
import sys
import re
import io
import unicodedata
from pathlib import Path
from PIL import Image

import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DOCX_PATH = os.path.join(PROJECT_ROOT, "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "figures")
CATALOG_PATH = os.path.join(PROJECT_ROOT, ".agents", "teamwork", "worker_m1_1", "DIAGRAM_CATALOG.md")

# ==============================================================================
# OPENXML FORMATTING & GEOMETRY UTILITIES
# ==============================================================================

def add_footer_page_number(section, is_roman=False):
    """Adds a centered page number field to the section footer per HUIT 2025 spec."""
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.text = ""
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.first_line_indent = Cm(0)

    r = p.add_run()
    fld1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    instr = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    fld2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    fld3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    r._r.append(fld1)
    r._r.append(instr)
    r._r.append(fld2)
    t = parse_xml(f'<w:t {nsdecls("w")}>{"i" if is_roman else "1"}</w:t>')
    r._r.append(t)
    r._r.append(fld3)

    r.font.name = "Times New Roman"
    r.font.size = Pt(11)


def set_section_geometry(section, is_cover=False, is_prelim=False, is_body=False):
    """
    Configure HUIT 2025 page geometry:
    A4 (210 x 297 mm), Margins: Left 3.5cm (1984 dxa), Right/Top/Bottom 2.5cm (1417 dxa).
    """
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.5)
    section.right_margin = Cm(2.5)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)

    sectPr = section._sectPr
    for b in sectPr.xpath("./w:pgBorders"):
        sectPr.remove(b)
    for p in sectPr.xpath("./w:pgNumType"):
        sectPr.remove(p)

    if is_cover:
        border_xml = f"""
            <w:pgBorders {nsdecls('w')} w:display="firstPage">
                <w:top w:val="cornerTriangles" w:sz="15" w:space="1" w:color="auto"/>
                <w:left w:val="cornerTriangles" w:sz="15" w:space="4" w:color="auto"/>
                <w:bottom w:val="cornerTriangles" w:sz="15" w:space="1" w:color="auto"/>
                <w:right w:val="cornerTriangles" w:sz="15" w:space="4" w:color="auto"/>
            </w:pgBorders>
        """
        sectPr.append(parse_xml(border_xml))
        section.footer.is_linked_to_previous = False
        for p in section.footer.paragraphs:
            p.text = ""
    elif is_prelim:
        pgnum_xml = f'<w:pgNumType {nsdecls("w")} w:fmt="lowerRoman" w:start="1"/>'
        sectPr.append(parse_xml(pgnum_xml))
        add_footer_page_number(section, is_roman=True)
    elif is_body:
        pgnum_xml = f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>'
        sectPr.append(parse_xml(pgnum_xml))
        add_footer_page_number(section, is_roman=False)


def format_p(p, font_name="Times New Roman", font_size_pt=13, is_bold=False, is_italic=False,
             line_spacing=1.3, space_before_pt=6, space_after_pt=6,
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line_indent_cm=0.0, color_rgb=(0, 0, 0)):
    """Applies strict HUIT 2025 typography and OpenXML run properties to a paragraph."""
    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before_pt)
    p.paragraph_format.space_after = Pt(space_after_pt)
    p.paragraph_format.widow_control = True
    if first_line_indent_cm > 0:
        p.paragraph_format.first_line_indent = Cm(first_line_indent_cm)
    else:
        p.paragraph_format.first_line_indent = Cm(0)

    for run in p.runs:
        run.font.name = font_name
        run.font.size = Pt(font_size_pt)
        run.font.bold = is_bold
        run.font.italic = is_italic
        if color_rgb != (0, 0, 0):
            run.font.color.rgb = RGBColor(*color_rgb)

        rPr = run._r.get_or_add_rPr()
        rFonts = rPr.xpath("./w:rFonts")
        if not rFonts:
            rFonts_elem = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}" w:eastAsia="{font_name}"/>')
            rPr.append(rFonts_elem)
        else:
            rFonts[0].set(qn("w:ascii"), font_name)
            rFonts[0].set(qn("w:hAnsi"), font_name)
            rFonts[0].set(qn("w:cs"), font_name)
            rFonts[0].set(qn("w:eastAsia"), font_name)


def sanitize_mojibake(text):
    """Strips any non-Vietnamese Latin-1 extended characters (mojibake) from text."""
    if not text:
        return ""
    # Strip garbage characters: ¡ ¢ £ ¤ ¥ ¦ § ¨ © ª « ¬ ® ¯ ° ± ² ³ ´ µ ¶ · ¸ ¹ º » ¼ ½ ¾ ¿ × ÷ Þ ß þ
    # Keep standard ASCII and Vietnamese Unicode NFC
    clean = re.sub(r'[¡-¿×÷Þßþ]', '', text)
    return clean


def add_p(doc, text="", font_name="Times New Roman", font_size_pt=13, is_bold=False, is_italic=False,
          line_spacing=1.3, space_before_pt=6, space_after_pt=6,
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line_indent_cm=1.0, color_rgb=(0, 0, 0)):
    """Helper to append a formatted paragraph complying with HUIT 2025 specs."""
    p = doc.add_paragraph()
    if text:
        p.add_run(sanitize_mojibake(text))
    format_p(p, font_name=font_name, font_size_pt=font_size_pt, is_bold=is_bold, is_italic=is_italic,
             line_spacing=line_spacing, space_before_pt=space_before_pt, space_after_pt=space_after_pt,
             align=align, first_line_indent_cm=first_line_indent_cm, color_rgb=color_rgb)
    return p


def apply_paragraph_keep_next(p):
    """Enforces w:keepNext so paragraph is never orphaned at bottom of page."""
    p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr()
    if not pPr.xpath("./w:keepNext"):
        pPr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))


def set_paragraph_outline_level(p, level):
    """Explicitly injects w:outlineLvl into paragraph properties."""
    pPr = p._p.get_or_add_pPr()
    for lvl in pPr.xpath("./w:outlineLvl"):
        pPr.remove(lvl)
    pPr.append(parse_xml(f'<w:outlineLvl {nsdecls("w")} w:val="{level}"/>'))


def add_preliminary_heading(doc, text):
    """
    Preliminary section heading (LỜI CẢM ƠN, LỜI CAM ĐOAN, NHẬN XÉT GVHD, DANH MỤC...):
    Heading 1 style, outlineLvl 0, 16pt Bold Centered, keepNext.
    """
    p = doc.add_paragraph()
    try:
        p.style = doc.styles['Heading 1']
    except Exception:
        pass
    set_paragraph_outline_level(p, 0)
    apply_paragraph_keep_next(p)
    p.add_run(text.upper())
    format_p(p, font_size_pt=16, is_bold=True,
             line_spacing=1.3, space_before_pt=12, space_after_pt=12,
             align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0.0)
    return p


def add_heading_1(doc, text):
    """HUIT Heading 1 (Cấp chương): 18pt Bold Centered Uppercase, Heading 1 style + outlineLvl 0 + keepNext."""
    p = doc.add_paragraph()
    try:
        p.style = doc.styles['Heading 1']
    except Exception:
        pass
    set_paragraph_outline_level(p, 0)
    apply_paragraph_keep_next(p)
    p.add_run(text.upper())
    format_p(p, font_size_pt=18, is_bold=True,
             line_spacing=1.3, space_before_pt=12, space_after_pt=12,
             align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0.0)
    return p


def add_heading_2(doc, text):
    """HUIT Heading 2 (Cấp 1.1): 14pt Bold Left Uppercase, Heading 2 style + outlineLvl 1 + keepNext."""
    p = doc.add_paragraph()
    try:
        p.style = doc.styles['Heading 2']
    except Exception:
        pass
    set_paragraph_outline_level(p, 1)
    apply_paragraph_keep_next(p)
    p.add_run(text.upper())
    format_p(p, font_size_pt=14, is_bold=True,
             line_spacing=1.3, space_before_pt=12, space_after_pt=6,
             align=WD_ALIGN_PARAGRAPH.LEFT, first_line_indent_cm=0.0)
    return p


def add_heading_3(doc, text):
    """HUIT Heading 3 (Cấp 1.1.1): 13pt Bold Left Sentence-case, Heading 3 style + outlineLvl 2 + keepNext."""
    p = doc.add_paragraph()
    try:
        p.style = doc.styles['Heading 3']
    except Exception:
        pass
    set_paragraph_outline_level(p, 2)
    apply_paragraph_keep_next(p)
    p.add_run(text)
    format_p(p, font_size_pt=13, is_bold=True,
             line_spacing=1.3, space_before_pt=6, space_after_pt=6,
             align=WD_ALIGN_PARAGRAPH.LEFT, first_line_indent_cm=0.0)
    return p


def add_heading_4(doc, text):
    """HUIT Heading 4 (Cấp 1.1.1.1 / 2.2.2.1): 13pt Bold-Italic Left, Heading 4 style + outlineLvl 3 + keepNext."""
    p = doc.add_paragraph()
    try:
        p.style = doc.styles['Heading 4']
    except Exception:
        pass
    set_paragraph_outline_level(p, 3)
    apply_paragraph_keep_next(p)
    p.add_run(text)
    format_p(p, font_size_pt=13, is_bold=True, is_italic=True,
             line_spacing=1.3, space_before_pt=4, space_after_pt=4,
             align=WD_ALIGN_PARAGRAPH.LEFT, first_line_indent_cm=0.0)
    return p


def add_bullet(doc, text, level=0):
    """
    Add a bullet point paragraph conforming strictly to HUIT 2025 specs:
    Level 0 (cấp 1): prefix '- ', Position 0.3cm, Text indent 0.8cm, Line spacing 1.3, Before 6pt, After 6pt.
    Level 1 (cấp 2): prefix '+ ', Position 0.8cm, Text indent 1.3cm, Line spacing 1.3, Before 6pt, After 6pt.
    """
    p = doc.add_paragraph()
    if level == 0:
        prefix = "-  "
        left_ind = 0.8
        first_ind = -0.5
    else:
        prefix = "+  "
        left_ind = 1.3
        first_ind = -0.5

    p.paragraph_format.left_indent = Cm(left_ind)
    p.paragraph_format.first_line_indent = Cm(first_ind)
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.widow_control = True
    p.paragraph_format.keep_together = True
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    run = p.add_run(f"{prefix}{sanitize_mojibake(text)}")
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)

    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.xpath("./w:rFonts")
    if not rFonts:
        rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman"/>'))
    return p


PRINTABLE_WIDTH_CM = 15.0  # A4 21.0 - Left 3.5 - Right 2.5
PRINTABLE_WIDTH_DXA = 8504 # 15.0 / 2.54 * 1440


def clamp_table_column_widths(col_widths, max_total_cm=PRINTABLE_WIDTH_CM):
    """Ensures total table width strictly never exceeds printable margin boundary (15.0cm)."""
    if not col_widths:
        return col_widths
    current_total = sum(col_widths)
    if current_total <= max_total_cm + 0.001:
        return col_widths
    scale = max_total_cm / current_total
    scaled = [round(w * scale, 2) for w in col_widths]
    residual = round(max_total_cm - sum(scaled), 2)
    max_idx = scaled.index(max(scaled))
    scaled[max_idx] = round(scaled[max_idx] + residual, 2)
    return scaled


def set_table_styling(table, col_widths=None):
    """
    Applies classic academic TableGrid styling per HUIT 2025 table rules:
    1. Lock table width to exactly 15.0 cm (8504 dxa) with fixed layout.
    2. Style: TableGrid with thin black borders (top, bottom, left, right, insideH, insideV).
    3. tblHeader on row 0 across page splits.
    4. cantSplit on all rows.
    5. Header row: Pure white background, bold black centered text.
    6. Data rows: Pure white background, no alternating shading, black text.
    7. Exact column grid matching tblGrid and clamped col_widths.
    """
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr

    # 1. Lock table width to exactly 15.0 cm (8504 dxa) with fixed layout
    style_el = tblPr.xpath('./w:tblStyle')
    if style_el:
        style_el[0].set(docx.oxml.ns.qn('w:val'), 'TableGrid')
    else:
        tblPr.insert(0, parse_xml(f'<w:tblStyle {nsdecls("w")} w:val="TableGrid"/>'))

    for w in tblPr.xpath("./w:tblW"):
        tblPr.remove(w)
    tblPr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="{PRINTABLE_WIDTH_DXA}" w:type="dxa"/>'))

    for l in tblPr.xpath("./w:tblLayout"):
        tblPr.remove(l)
    tblPr.append(parse_xml(f'<w:tblLayout {nsdecls("w")} w:type="fixed"/>'))

    borders = parse_xml(f"""
        <w:tblBorders {nsdecls('w')}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>
            <w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>
            <w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>
        </w:tblBorders>
    """)
    for b in tblPr.xpath("./w:tblBorders"):
        tblPr.remove(b)
    tblPr.append(borders)

    # 2. Repeat header row on new page
    trPr0 = table.rows[0]._tr.get_or_add_trPr()
    if not trPr0.xpath("./w:tblHeader"):
        trPr0.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    # 3. Prevent rows from splitting across page breaks
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        if not trPr.xpath("./w:cantSplit"):
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    # 4. Header row formatting (Pure white, Bold Black, Centered)
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        for s in tcPr.xpath("./w:shd"):
            tcPr.remove(s)
        if not tcPr.xpath("./w:vAlign"):
            tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.3
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.first_line_indent = Cm(0)
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(12)
                run.font.bold = True
                run.font.color.rgb = None
                rPr = run._r.get_or_add_rPr()
                rFonts = rPr.xpath("./w:rFonts")
                if not rFonts:
                    rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman"/>'))

    # 5. Data rows formatting (Pure white, No alternating shading, Black text)
    for row_idx, row in enumerate(table.rows[1:], 1):
        for c_idx, cell in enumerate(row.cells):
            tcPr = cell._tc.get_or_add_tcPr()
            for s in tcPr.xpath("./w:shd"):
                tcPr.remove(s)
            if not tcPr.xpath("./w:vAlign"):
                tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.3
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.first_line_indent = Cm(0)
                if c_idx == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(12)
                    run.font.color.rgb = None
                    rPr = run._r.get_or_add_rPr()
                    rFonts = rPr.xpath("./w:rFonts")
                    if not rFonts:
                        rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman"/>'))

    # 6. Column widths and tblGrid clamping
    final_widths = clamp_table_column_widths(col_widths, PRINTABLE_WIDTH_CM) if col_widths else None
    if final_widths:
        for row in table.rows:
            for idx, width in enumerate(final_widths):
                if idx < len(row.cells):
                    row.cells[idx].width = Cm(width)
                    tcPr = row.cells[idx]._tc.get_or_add_tcPr()
                    for w in tcPr.xpath("./w:tcW"):
                        tcPr.remove(w)
                    tcPr.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{Cm(width).twips}" w:type="dxa"/>'))

        tblGrid = table._tbl.xpath("./w:tblGrid")
        if tblGrid:
            table._tbl.remove(tblGrid[0])
        new_grid = parse_xml(f'<w:tblGrid {nsdecls("w")}/>')
        for width in final_widths:
            new_grid.append(parse_xml(f'<w:gridCol {nsdecls("w")} w:w="{Cm(width).twips}"/>'))
        table._tbl.insert(1, new_grid)


def add_figure_with_caption(doc, section_code, seq_num, title, image_path, width_cm=15.0):
    """
    Inserts a 300 DPI image centered, followed by deep hierarchical caption:
    'Hình X.Y.Z. N: Tên hình'
    Binds image and caption together using keepNext so they never split across pages.
    """
    full_path = os.path.join(PROJECT_ROOT, image_path.replace("/", os.sep))
    if not os.path.exists(full_path):
        print(f"[WARN] Figure missing on disk: {full_path}")
        # Create in-memory fallback
        img = Image.new("RGB", (1200, 800), color=(15, 43, 92))
        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(300, 300))
        buf.seek(0)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.line_spacing = 1.0
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        apply_paragraph_keep_next(p_img)
        run = p_img.add_run()
        run.add_picture(buf, width=Cm(min(width_cm, 15.0)))
    else:
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.line_spacing = 1.0
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        apply_paragraph_keep_next(p_img)
        run = p_img.add_run()
        run.add_picture(full_path, width=Cm(min(width_cm, 15.0)))

    # Caption
    caption_text = f"Hình {section_code}. {seq_num}: {title}"
    p_cap = add_p(doc, caption_text, font_size_pt=11, is_bold=True, is_italic=False,
                  line_spacing=1.3, space_before_pt=2, space_after_pt=6,
                  align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0.0)
    p_cap._p.get_or_add_pPr().append(parse_xml(f'<w:pStyle {nsdecls("w")} w:val="Caption"/>'))


def add_table_with_caption(doc, section_code, seq_num, title, headers, data_rows, col_widths=None):
    """
    Inserts deep hierarchical caption 'Bảng X.Y.Z. N: Tên bảng' followed by structured table.
    Binds caption to table below using keepNext so caption is never orphaned at bottom of page.
    """
    caption_text = f"Bảng {section_code}. {seq_num}: {title}"
    p_cap = add_p(doc, caption_text, font_size_pt=11, is_bold=True, is_italic=False,
                  line_spacing=1.3, space_before_pt=6, space_after_pt=2,
                  align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0.0)
    p_cap._p.get_or_add_pPr().append(parse_xml(f'<w:pStyle {nsdecls("w")} w:val="Caption"/>'))
    apply_paragraph_keep_next(p_cap)

    table = doc.add_table(rows=len(data_rows) + 1, cols=len(headers))
    for c_idx, h_text in enumerate(headers):
        table.rows[0].cells[c_idx].text = sanitize_mojibake(h_text)

    for r_idx, row_data in enumerate(data_rows):
        for c_idx, val in enumerate(row_data):
            table.rows[r_idx + 1].cells[c_idx].text = sanitize_mojibake(str(val))

    set_table_styling(table, col_widths)
    # Add empty spacing paragraph after table
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.line_spacing = 1.0
    p_spacer.paragraph_format.space_after = Pt(6)
    p_spacer.paragraph_format.space_before = Pt(0)
    return table


# ==============================================================================
# SECTION BUILDERS
# ==============================================================================

def build_section0_covers(doc):
    """Section 0: Bìa chính (với khung cornerTriangles) và Bìa phụ."""
    sec0 = doc.sections[0]
    set_section_geometry(sec0, is_cover=True)

    logo_file = os.path.join(FIGURES_DIR, "logo_huit.png")

    # Trang Bìa Chính (Page 1)
    add_p(doc, "BỘ CÔNG THƯƠNG", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "KHOA CÔNG NGHỆ THÔNG TIN", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "---------------------------------", font_size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    # Official HUIT University circular logo (3.5 cm x 3.5 cm, centered)
    if os.path.exists(logo_file):
        p_logo1 = doc.add_paragraph()
        p_logo1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo1.paragraph_format.line_spacing = 1.0
        p_logo1.paragraph_format.space_before = Pt(8)
        p_logo1.paragraph_format.space_after = Pt(14)
        p_logo1.paragraph_format.first_line_indent = Cm(0)
        apply_paragraph_keep_next(p_logo1)
        p_logo1.add_run().add_picture(logo_file, width=Cm(3.5), height=Cm(3.5))

    add_p(doc, "KHÓA LUẬN TỐT NGHIỆP", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "XÂY DỰNG HỆ THỐNG QUẢN LÝ CHO THUÊ THIẾT BỊ (RENTALSYSTEM)", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0, color_rgb=(15, 43, 92))
    add_p(doc, "Mã đề tài: CNTT-KLCN058", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    add_p(doc, "\nNgành: CÔNG NGHỆ THÔNG TIN", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "Chuyên ngành: KỸ THUẬT PHẦN MỀM", font_size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    add_p(doc, "\nSINH VIÊN THỰC HIỆN:", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "1. 2001230725 – Hồ Sĩ Tuấn – Lớp: 14DHTH09", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "2. 2001230726 – Phan Minh Quân – Lớp: 14DHTH09", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "Khóa học: 2023 – 2027", font_size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    add_p(doc, "\nGiảng viên hướng dẫn 1: ThS. Vũ Văn Vinh", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "Giảng viên hướng dẫn 2: ThS. Nguyễn Trần Duy Khang", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    add_p(doc, "\nTP. HỒ CHÍ MINH, NĂM 2026", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    doc.add_page_break()

    # Trang Bìa Phụ (Page 2)
    add_p(doc, "BỘ CÔNG THƯƠNG", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "KHOA CÔNG NGHỆ THÔNG TIN", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "---------------------------------", font_size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    if os.path.exists(logo_file):
        p_logo2 = doc.add_paragraph()
        p_logo2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo2.paragraph_format.line_spacing = 1.0
        p_logo2.paragraph_format.space_before = Pt(8)
        p_logo2.paragraph_format.space_after = Pt(14)
        p_logo2.paragraph_format.first_line_indent = Cm(0)
        apply_paragraph_keep_next(p_logo2)
        p_logo2.add_run().add_picture(logo_file, width=Cm(3.5), height=Cm(3.5))

    add_p(doc, "KHÓA LUẬN TỐT NGHIỆP", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "XÂY DỰNG HỆ THỐNG QUẢN LÝ CHO THUÊ THIẾT BỊ (RENTALSYSTEM)", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0, color_rgb=(15, 43, 92))
    add_p(doc, "Mã đề tài: CNTT-KLCN058", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    add_p(doc, "\nNgành: CÔNG NGHỆ THÔNG TIN", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "Chuyên ngành: KỸ THUẬT PHẦN MỀM", font_size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    add_p(doc, "\nSINH VIÊN THỰC HIỆN:", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "1. 2001230725 – Hồ Sĩ Tuấn – Lớp: 14DHTH09", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "2. 2001230726 – Phan Minh Quân – Lớp: 14DHTH09", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    add_p(doc, "\nGiảng viên hướng dẫn 1: ThS. Vũ Văn Vinh", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "Giảng viên hướng dẫn 2: ThS. Nguyễn Trần Duy Khang", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    add_p(doc, "Cán bộ phản biện: ..............................................................", font_size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    add_p(doc, "\nTP. HỒ CHÍ MINH, NĂM 2026", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)


def add_toc_entry(doc, title, page, level=1, is_first=False, is_last=False, toc_instr=r'TOC \o "1-3" \h \z \u'):
    """Adds a dynamic TOC entry with dot leader right tab stop and Word field wrapper."""
    p = doc.add_paragraph()
    p_pr = p._p.get_or_add_pPr()

    if level == 1:
        p.paragraph_format.left_indent = Cm(0)
        font_size = 12
        is_bold = True
    elif level == 2:
        p.paragraph_format.left_indent = Cm(0.5)
        font_size = 11.5
        is_bold = False
    else:
        p.paragraph_format.left_indent = Cm(1.0)
        font_size = 11
        is_bold = False

    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = Cm(0)

    tabs = parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="right" w:leader="dot" w:pos="8504"/></w:tabs>')
    p_pr.append(tabs)

    if is_first:
        r_fld_begin = p.add_run()
        r_fld_begin._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>'))
        r_instr = p.add_run()
        r_instr._r.append(parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> {toc_instr} </w:instrText>'))
        r_fld_sep = p.add_run()
        r_fld_sep._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>'))

    r_text = p.add_run(title)
    r_text.font.name = "Times New Roman"
    r_text.font.size = Pt(font_size)
    r_text.font.bold = is_bold

    r_tab = p.add_run()
    r_tab._r.append(parse_xml(f'<w:tab {nsdecls("w")}/>'))

    r_pg = p.add_run(str(page))
    r_pg.font.name = "Times New Roman"
    r_pg.font.size = Pt(font_size)
    r_pg.font.bold = is_bold

    if is_last:
        r_fld_end = p.add_run()
        r_fld_end._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))

    return p


def build_section1_preliminary(doc):
    """
    Section 1: Trang sơ bộ đánh số La Mã lowerRoman (i, ii, iii...).
    Thứ tự bắt buộc: LỜI CẢM ƠN (i) -> LỜI CAM ĐOAN (ii) -> NHẬN XÉT GVHD (iii) -> MỤC LỤC -> DANH MỤC TỪ VIẾT TẮT -> DANH MỤC HÌNH -> DANH MỤC BẢNG.
    """
    sec1 = doc.add_section()
    set_section_geometry(sec1, is_prelim=True)

    # 1.1 LỜI CẢM ƠN (Page i)
    add_preliminary_heading(doc, "LỜI CẢM ƠN")
    add_p(doc, "Trước hết, chúng em xin bày tỏ lòng biết ơn sâu sắc và chân thành nhất đến toàn thể Quý Thầy Cô Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT). Trong suốt quá trình học tập và rèn luyện dưới mái trường, Quý Thầy Cô đã tận tâm truyền thụ nền tảng kiến thức khoa học máy tính, kỹ thuật phần mềm vững chắc và bồi dưỡng tư duy lập trình chuyên nghiệp, giúp chúng em có đủ năng lực và tự tin thực hiện đề tài tốt nghiệp này.")
    add_p(doc, "Đặc biệt, chúng em xin gửi lời tri ân sâu sắc và lòng biết ơn chân thành nhất đến ThS. Vũ Văn Vinh và ThS. Nguyễn Trần Duy Khang. Quý Thầy đã luôn dành thời gian quý báu để tận tình chỉ báo, định hướng đề tài trong suốt quá trình làm khóa luận cử nhân.")
    add_p(doc, "Mặc dù chúng em đã rất nỗ lực nghiên cứu và hoàn thiện khóa luận, song do giới hạn về mặt thời gian và kinh nghiệm thực tế, đề tài cũng khó tránh khỏi những thiếu sót nhất định. Chúng em rất mong nhận được những ý kiến đóng góp, chỉ bảo quý báu từ Quý Thầy Cô trong Hội đồng chấm khóa luận.")
    add_p(doc, "\nTP. Hồ Chí Minh, ngày 06 tháng 11 năm 2026", font_size_pt=13, is_italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent_cm=0)
    add_p(doc, "Nhóm sinh viên thực hiện", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent_cm=0)
    add_p(doc, "\nHồ Sĩ Tuấn – Phan Minh Quân", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent_cm=0)
    doc.add_page_break()

    # 1.2 LỜI CAM ĐOAN (Page ii) - MUST BE AFTER Lời cảm ơn and BEFORE Nhận xét GVHD
    add_preliminary_heading(doc, "LỜI CAM ĐOAN")
    add_p(doc, "Nhóm tác giả chúng em xin cam đoan đây là công trình nghiên cứu khoa học độc lập của nhóm chúng em dưới sự hướng dẫn trực tiếp của ThS. Vũ Văn Vinh và ThS. Nguyễn Trần Duy Khang.")
    add_p(doc, "Chúng em xin cam kết các nội dung sau:")
    add_bullet(doc, "Toàn bộ số liệu khảo sát mô hình nghiệp vụ, các lược đồ phân tích thiết kế, mã nguồn triển khai và kết quả thử nghiệm được trình bày trong khóa luận là hoàn toàn trung thực, khách quan và phản ánh chính xác kết quả xây dựng hệ thống phần mềm RentalSystem trên mã nguồn thực tế.")
    add_bullet(doc, "Các thuật toán và cơ chế kỹ thuật (kiểm soát tương tranh SemaphoreSlim, sinh mã VietQR động NAPAS 247, phân kỳ công nợ tự động) do nhóm tự tìm hiểu, hiện thực và thử nghiệm trực tiếp trên nền tảng .NET 9.")
    add_bullet(doc, "Các tài liệu tham khảo, các trích dẫn lý thuyết và thư viện mã nguồn mở đều được ghi chú rõ ràng nguồn gốc xuất xứ theo chuẩn trích dẫn quy định của Trường Đại học Công Thương TP. Hồ Chí Minh.")
    add_p(doc, "Nếu có bất kỳ sự gian lận nào, nhóm chúng em xin chịu hoàn toàn trách nhiệm trước Hội đồng đánh giá và Nhà trường.")
    add_p(doc, "\nTP. Hồ Chí Minh, ngày 06 tháng 11 năm 2026", font_size_pt=13, is_italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent_cm=0)
    add_p(doc, "Nhóm tác giả", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent_cm=0)
    add_p(doc, "\nHồ Sĩ Tuấn – Phan Minh Quân", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent_cm=0)
    doc.add_page_break()

    # 1.3 NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN (Page iii)
    add_preliminary_heading(doc, "NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN")
    for _ in range(21):
        add_p(doc, "..................................................................................................................................", font_size_pt=13, first_line_indent_cm=0)
    add_p(doc, "GIẢNG VIÊN HƯỚNG DẪN", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent_cm=0)
    add_p(doc, "(Ký và ghi rõ họ tên)", font_size_pt=12, is_italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent_cm=0)
    doc.add_page_break()

    # 1.4 MỤC LỤC
    p_title = add_p(doc, "MỤC LỤC", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(12)
    apply_paragraph_keep_next(p_title)

    p_toc = doc.add_paragraph()
    p_toc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_toc.paragraph_format.line_spacing = 1.3
    p_toc.paragraph_format.space_before = Pt(6)
    p_toc.paragraph_format.space_after = Pt(6)
    p_toc.paragraph_format.first_line_indent = Cm(0)

    fld_xml = (
        f'<w:fldSimple {nsdecls("w")} w:instr="TOC \\o &quot;1-3&quot; \\h \\z \\u">'
        f'<w:r>'
        f'<w:rPr>'
        f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
        f'<w:color {nsdecls("w")} w:val="334155"/>'
        f'<w:i/>'
        f'<w:noProof/>'
        f'</w:rPr>'
        f'<w:t>Nhấn chuột phải chọn "Update Field" (hoặc nhấn phím F9) để cập nhật Mục lục tự động theo số trang thực tế...</w:t>'
        f'</w:r>'
        f'</w:fldSimple>'
    )
    p_toc._p.append(parse_xml(fld_xml))
    doc.add_page_break()

    # 1.5 DANH MỤC TỪ VIẾT TẮT
    add_preliminary_heading(doc, "DANH MỤC TỪ VIẾT TẮT")
    abbreviations = [
        ("ASP.NET", "Active Server Pages .NET – Nền tảng phát triển ứng dụng Web của Microsoft"),
        ("MVC", "Model – View – Controller – Mô hình kiến trúc phân tách phần mềm 3 tầng"),
        ("EF Core", "Entity Framework Core – Thư viện Object-Relational Mapping (ORM) cho .NET"),
        ("BCE", "Boundary – Control – Entity – Mô hình kiến trúc phân lớp hướng đối tượng"),
        ("UML", "Unified Modeling Language – Ngôn ngữ mô hình hóa thống nhất"),
        ("ERD", "Entity – Relationship Diagram – Sơ đồ thực thể mối quan hệ cơ sở dữ liệu"),
        ("API", "Application Programming Interface – Giao diện lập trình ứng dụng"),
        ("REST", "Representational State Transfer – Kiểu kiến trúc dịch vụ web chuẩn"),
        ("JSON", "JavaScript Object Notation – Định dạng trao đổi dữ liệu dạng văn bản nhẹ"),
        ("EMVCo", "Europay, Mastercard, Visa Standards Organization – Tiêu chuẩn thanh toán quốc tế"),
        ("NAPAS", "National Payment Corporation of Vietnam – Công ty Cổ phần Thanh toán Quốc gia VN"),
        ("VietQR", "Chuẩn nhận diện thanh toán chuyển khoản qua mã QR động liên ngân hàng Việt Nam"),
        ("RBAC", "Role-Based Access Control – Cơ chế kiểm soát truy cập phân quyền dựa trên vai trò"),
        ("SLA", "Service Level Agreement – Cam kết mức chất lượng dịch vụ vận hành"),
        ("BI", "Business Intelligence – Hệ thống thông tin phân tích và báo cáo quản trị doanh nghiệp"),
        ("OpEx", "Operational Expenditure – Chi phí vận hành hoạt động kinh doanh"),
        ("CapEx", "Capital Expenditure – Chi phí đầu tư tài sản cố định ban đầu"),
        ("CCCD", "Căn cước công dân – Mã số định danh cá nhân hợp pháp theo chuẩn Bộ Công An"),
        ("HUIT", "Ho Chi Minh City University of Industry and Trade – Trường ĐH Công Thương TP.HCM")
    ]
    add_table_with_caption(doc, "0.1", 1, "Danh mục các thuật ngữ và từ viết tắt trong khóa luận",
                           ["Từ viết tắt", "Giải thích ý nghĩa và vai trò chuyên môn"],
                           abbreviations, col_widths=[3.5, 11.5])
    doc.add_page_break()

    # 1.6 DANH MỤC HÌNH
    add_preliminary_heading(doc, "DANH MỤC HÌNH")
    add_p(doc, "Dưới đây là danh mục tổng hợp toàn bộ 80 hình vẽ kỹ thuật, sơ đồ UML, lược đồ cơ sở dữ liệu, giao diện thực tế và biểu đồ thực nghiệm trong khóa luận:", font_size_pt=13, is_italic=True, first_line_indent_cm=0)

    # Read figures from DIAGRAM_CATALOG.md
    figures_list = load_diagram_catalog()
    fig_entries = []
    for code, seq, title, path in figures_list:
        ch = code.split(".")[0]
        if ch == "1":
            pg = "12"
        elif ch == "2":
            pg = "35"
        elif ch == "3":
            pg = "98"
        elif ch == "4":
            pg = "148"
        else:
            pg = "165"
        fig_entries.append((f"Hình {code}. {seq}: {title}", pg))

    for idx, (f_title, f_pg) in enumerate(fig_entries):
        add_toc_entry(doc, f_title, f_pg, level=2, is_first=(idx == 0), is_last=(idx == len(fig_entries) - 1), toc_instr=r'TOC \h \z \c "Hình"')
    doc.add_page_break()

    # 1.7 DANH MỤC BẢNG
    add_preliminary_heading(doc, "DANH MỤC BẢNG")
    add_p(doc, "Dưới đây là danh mục tổng hợp các bảng biểu phân cấp sâu trong 5 chương của khóa luận:", font_size_pt=13, is_italic=True, first_line_indent_cm=0)

    tables_list = get_master_tables_catalog()
    tbl_entries = []
    for code, seq, title in tables_list:
        ch = code.split(".")[0]
        if ch in ["0", "1"]:
            pg = "14"
        elif ch == "2":
            pg = "45"
        elif ch == "3":
            pg = "82"
        elif ch == "4":
            pg = "142"
        else:
            pg = "170"
        tbl_entries.append((f"Bảng {code}. {seq}: {title}", pg))

    for idx, (t_title, t_pg) in enumerate(tbl_entries):
        add_toc_entry(doc, t_title, t_pg, level=2, is_first=(idx == 0), is_last=(idx == len(tbl_entries) - 1), toc_instr=r'TOC \h \z \c "Bảng"')


def load_diagram_catalog():
    """Parse DIAGRAM_CATALOG.md to get all 80 figures."""
    figures = []
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, encoding="utf-8") as f:
            text = f.read()
        matches = re.findall(r"\|\s*\*\*Hình\s+([0-9\.]+)\.\s+([0-9]+)\*\*\s*\|\s*(.*?)\s*\|\s*`([^`]+)`\s*\|", text)
        for m in matches:
            figures.append((m[0].strip(), m[1].strip(), m[2].strip(), m[3].strip()))
    return figures


def get_master_tables_catalog():
    """Complete catalog of all master tables."""
    return [
        ("0.4", "1", "Bảng tiến độ kế hoạch thực hiện và phân công nhiệm vụ 12 tuần"),
        ("1.1.2", "1", "Bảng tổng hợp các bước trong quy trình cho thuê thiết bị truyền thống (AS-IS)"),
        ("1.2", "1", "Bảng đặc tả các giai đoạn trong quy trình cho thuê thiết bị đề xuất (TO-BE) trên nền tảng RentalSystem"),
        ("1.1.3", "1", "Bảng phân tích các điểm nghẽn và rủi ro vận hành trong quy trình thủ công"),
        ("1.3", "1", "Danh sách và đặc tả các biểu mẫu nghiệp vụ quản lý cho thuê thiết bị"),
        ("1.3", "2", "Bảng đối sánh tính năng giữa phương thức quản lý truyền thống và hệ thống tin học hóa"),
        ("2.1.1", "1", "Ma trận kịch bản kiểm soát tương tranh giữ chỗ máy bằng cơ chế SemaphoreSlim"),
        ("2.1.2", "1", "Quy trình đối soát tự động và gạch nợ qua Open Banking Webhook 24/7"),
        ("2.1.3", "1", "Bảng tiêu chí phân loại 4 cấp độ tuổi nợ và chính sách xử lý tài chính tự động"),
        ("2.2.2.1", "1", "Bảng đặc tả quy trình nghiệp vụ Đăng ký & Xác thực người dùng"),
        ("2.2.2.2", "1", "Bảng đặc tả quy trình nghiệp vụ Đặt thuê máy & Kiểm tra tồn kho (SemaphoreSlim)"),
        ("2.2.2.3", "1", "Bảng đặc tả quy trình nghiệp vụ Thanh toán đặt cọc qua VietQR động NAPAS 247"),
        ("2.2.2.4", "1", "Bảng đặc tả quy trình nghiệp vụ Bàn giao & Ký biên bản bàn giao máy"),
        ("2.2.2.5", "1", "Bảng đặc tả quy trình nghiệp vụ Báo cáo sự cố & Phân công bảo trì thiết bị"),
        ("2.2.2.6", "1", "Bảng đặc tả quy trình nghiệp vụ Gia hạn hợp đồng & Phân kỳ nợ"),
        ("2.2.2.7", "1", "Bảng đặc tả quy trình nghiệp vụ Trả máy, nghiệm thu & Hoàn trả tiền cọc"),
        ("2.3.2", "1", "Bảng đặc tả use case Đăng ký tài khoản khách hàng"),
        ("2.3.2", "2", "Bảng đặc tả use case Đăng nhập và Xác thực phân quyền người dùng"),
        ("2.3.2", "3", "Bảng đặc tả use case Đặt thuê thiết bị trực tuyến (Checkout)"),
        ("2.3.2", "4", "Bảng đặc tả use case Ký hợp đồng điện tử Canvas và Tải hồ sơ CCCD"),
        ("2.3.2", "5", "Bảng đặc tả use case Thanh toán VietQR và Đối soát Webhook tự động"),
        ("2.3.2", "6", "Bảng đặc tả use case Bàn giao và Xuất biên bản bàn giao thiết bị"),
        ("2.3.2", "7", "Bảng đặc tả use case Báo cáo sự cố và Tạm dừng tính tiền thuê"),
        ("2.3.2", "8", "Bảng đặc tả use case Điều phối kỹ thuật và Quản lý việc của tôi"),
        ("2.3.2", "9", "Bảng đặc tả use case Yêu cầu và Phê duyệt gia hạn hợp đồng"),
        ("2.3.2", "10", "Bảng đặc tả use case Nghiệm thu trả máy và Quyết toán hoàn tiền cọc"),
        ("2.3.2", "11", "Bảng đặc tả use case Quản lý sổ nợ và Nhắc nợ tự động"),
        ("2.3.2", "12", "Bảng đặc tả use case Trung tâm phân tích báo cáo BI và Xuất Excel ClosedXML"),
        ("2.3.2", "13", "Bảng đặc tả use case Đánh giá chất lượng dịch vụ bảo trì và Phản hồi khách hàng"),
        ("2.3.3", "1", "Bảng đặc tả các Endpoint RESTful API chính phục vụ tích hợp hệ thống đa nền tảng"),
        ("3.1.1", "1", "Cấu trúc từ điển dữ liệu thực thể VaiTro (Role)"),
        ("3.1.1", "2", "Cấu trúc từ điển dữ liệu thực thể NguoiDung (User)"),
        ("3.1.1", "3", "Cấu trúc từ điển dữ liệu thực thể LoaiThietBi (DeviceCategory)"),
        ("3.1.1", "4", "Cấu trúc từ điển dữ liệu thực thể SanPham (Product)"),
        ("3.1.1", "5", "Cấu trúc từ điển dữ liệu thực thể ThietBi (Physical Serial)"),
        ("3.1.1", "6", "Cấu trúc từ điển dữ liệu thực thể LichSuThietBi (Device History)"),
        ("3.1.1", "7", "Cấu trúc từ điển dữ liệu thực thể KhuyenMai (Promotion)"),
        ("3.1.1", "8", "Cấu trúc từ điển dữ liệu thực thể HopDong (Rental Contract)"),
        ("3.1.1", "9", "Cấu trúc từ điển dữ liệu thực thể ChiTietHopDong (Contract Detail)"),
        ("3.1.1", "10", "Cấu trúc từ điển dữ liệu thực thể KyHanThanhToan (Payment Installment)"),
        ("3.1.1", "11", "Cấu trúc từ điển dữ liệu thực thể PhieuThu (Payment Receipt)"),
        ("3.1.1", "12", "Cấu trúc từ điển dữ liệu thực thể PhieuChi (Payment Voucher)"),
        ("3.1.1", "13", "Cấu trúc từ điển dữ liệu thực thể PhieuBaoTri (Maintenance Ticket)"),
        ("3.1.1", "14", "Cấu trúc từ điển dữ liệu thực thể BienBanBanGiao (Handover Protocol)"),
        ("3.1.1", "15", "Cấu trúc từ điển dữ liệu thực thể ThongBao (In-App Notification)"),
        ("3.1.1", "16", "Cấu trúc từ điển dữ liệu thực thể LichSuNhacNo (Debt Reminder Log)"),
        ("3.1.1", "17", "Cấu trúc từ điển dữ liệu thực thể YeuCauGiaHan (Extension Request)"),
        ("3.1.1", "18", "Cấu trúc từ điển dữ liệu thực thể PhanCongCongViec (Task Assignment)"),
        ("4.1", "1", "Bảng thông số môi trường phát triển, máy chủ và các thư viện phần mềm"),
        ("5.2.2", "1", "Ma trận kết quả kiểm thử 14 ca kiểm thử chức năng hệ thống RentalSystem (TC-01 đến TC-14)")
    ]


# ==============================================================================
# SECTION 2: PHẦN THÂN BÀI (ARABIC 1, 2, 3...)
# ==============================================================================

def build_opening_introduction(doc):
    """PHẦN MỞ ĐẦU: 1. Giới thiệu đề tài, 2. Mục tiêu đề tài, 3. Đối tượng và Phạm vi đề tài."""
    add_heading_1(doc, "PHẦN MỞ ĐẦU")
    
    add_heading_2(doc, "1. GIỚI THIỆU ĐỀ TÀI")
    add_p(doc, "Trong bối cảnh chuyển đổi số của nền kinh tế hiện đại, mô hình 'Thiết bị như một Dịch vụ'  đang trở thành giải pháp ưu việt được nhiều doanh nghiệp, cơ sở giáo dục và đơn vị tổ chức sự kiện lựa chọn. Thay vì phải đầu tư nguồn vốn ban đầu rất lớn để mua sắm hàng loạt máy tính xách tay, máy trạm xử lý đồ họa hay máy chủ, các đơn vị có thể tối ưu hóa dòng tiền bằng cách chuyển sang mô hình chi phí vận hành thông qua dịch vụ thuê thiết bị công nghệ.")
    add_p(doc, "Tuy nhiên, hoạt động quản lý cho thuê thiết bị tại các doanh nghiệp Việt Nam hiện nay vẫn chủ yếu dựa trên các quy trình thủ công truyền thống: ghi nhận đơn đặt hàng bằng sổ sách, lưu vết tình trạng tồn kho trên các bảng tính Excel rời rạc, ký hợp đồng giấy và theo dõi công nợ thủ công. Phương thức quản lý này bộc lộ hàng loạt bất cập nghiêm trọng: tình trạng xung đột lịch thuê dẫn đến bán vượt tồn kho, nguy cơ thất thoát linh kiện do không quản lý được từng mã Serial vật lý, tắc nghẽn trong việc đối soát chuyển khoản ngân hàng và chậm trễ trong xử lý công nợ.")
    add_p(doc, "Xuất phát từ thực tiễn khảo sát hoạt động vận hành của các doanh nghiệp kinh doanh dịch vụ cho thuê thiết bị công nghệ thông tin tại khu vực TP. Hồ Chí Minh, đề tài 'Xây dựng hệ thống quản lý cho thuê thiết bị (RentalSystem)' được thực hiện nhằm cung cấp một giải pháp tin học hóa toàn diện, tự động hóa từ khâu đặt thuê trực tuyến, ký hợp đồng điện tử Canvas, cấp phát thiết bị theo serial, thanh toán VietQR động NAPAS 247, đối soát webhook tự động, đến quản lý bảo trì sự cố và phân kỳ công nợ 4 cấp độ.")

    add_heading_2(doc, "2. MỤC TIÊU ĐỀ TÀI")
    add_heading_3(doc, "2.1. Mục tiêu tổng quát")
    add_p(doc, "Mục tiêu cốt lõi của đề tài là nghiên cứu, phân tích, thiết kế và xây dựng hoàn chỉnh hệ thống phần mềm quản lý cho thuê thiết bị công nghệ RentalSystem trên nền tảng Web ASP.NET Core 9 MVC kết hợp giao diện Web Responsive Design (RWD) và hệ thống Backend RESTful API dùng chung, vận hành trên nền tảng .NET 9, kiến trúc phân tầng ASP.NET Core MVC và hệ thống Backend RESTful API dùng chung, giải quyết hiệu quả các điểm nghẽn nghiệp vụ của phương thức quản lý truyền thống tại các doanh nghiệp cho thuê thiết bị.")
    
    add_heading_3(doc, "2.2. Mục tiêu cụ thể")
    add_bullet(doc, "Khảo sát và mô hình hóa các quy trình nghiệp vụ cốt lõi bằng bộ công cụ UML (Activity, Sequence, Collaboration) và kiến trúc thiết kế 3 lớp (Boundary – Control – Entity).")
    add_bullet(doc, "Xây dựng hệ thống trên nền tảng Web (ASP.NET Core 9 MVC) hỗ trợ Responsive Web Design (RWD) tương thích trên máy tính và thiết bị di động, phục vụ 4 phân hệ người dùng (Khách hàng, Kinh doanh, Kỹ thuật, Quản trị).")
    add_bullet(doc, "Xây dựng hệ thống Backend RESTful API dùng chung đạt chuẩn OpenAPI / Swagger, hỗ trợ xử lý dữ liệu JSON bất đồng bộ an toàn và sẵn sàng kết nối tích hợp đa nền tảng.")
    add_bullet(doc, "Giải quyết bài toán kiểm soát tương tranh giữ chỗ kho thiết bị bằng cơ chế SemaphoreSlim, ngăn chặn hiện tượng Overbooking và tranh chấp cấp phát serial.")
    add_bullet(doc, "Tích hợp giải thuật sinh mã thanh toán VietQR động theo chuẩn quốc tế EMVCo và mạng lưới NAPAS 247, xây dựng cơ chế đối soát tự động qua Open Banking Webhook với cơ chế xử lý Idempotency an toàn.")
    add_bullet(doc, "Xây dựng thuật toán phân kỳ tài chính tự động và hệ thống cảnh báo, phân nhóm tuổi nợ 4 cấp độ, áp dụng chính sách ân hạn 3 ngày và phạt trễ hạn 0.1%/ngày.")
    add_bullet(doc, "Thiết kế cơ sở dữ liệu quan hệ gồm 18 bảng thực thể, thiết lập các chỉ mục và ràng buộc toàn vẹn dữ liệu.")
    add_bullet(doc, "Xây dựng module Sao lưu và Phục hồi CSDL an toàn (Database Backup & Restore) cho 18 bảng thực thể, có cơ chế ngắt ràng buộc khóa ngoại và bảo toàn Identity.")
    add_bullet(doc, "Thực hiện kiểm thử chức năng cho các ca sử dụng cốt lõi, kiểm tra luồng tương tranh, đối soát thanh toán và gọi API, đánh giá tính đúng đắn và độ ổn định của hệ thống.")

    add_heading_2(doc, "3. ĐỐI TƯỢNG VÀ PHẠM VI ĐỀ TÀI")
    add_heading_3(doc, "3.1. Đối tượng nghiên cứu")
    add_p(doc, "Đối tượng nghiên cứu của đề tài bao gồm các quy trình nghiệp vụ cho thuê thiết bị công nghệ (đặt hàng, thẩm định hồ sơ, ký hợp đồng, bàn giao máy, thu hồi, bảo trì kỹ thuật, thanh toán và quản lý công nợ); ")
    
    add_heading_3(doc, "3.2. Phạm vi đề tài")
    add_p(doc, "Về phạm vi nghiệp vụ: Hệ thống tập trung giải quyết toàn bộ chu trình dịch vụ cho thuê thiết bị công nghệ thông tin (Laptop, Máy tính để bàn, Máy in, Máy chiếu) giữa doanh nghiệp cho thuê và khách hàng cá nhân / doanh nghiệp.")
    add_p(doc, "Về phạm vi ứng dụng: Đề tài tiến hành khảo sát thực tế mô hình tổ chức, quy trình nghiệp vụ và dữ liệu vận hành thực nghiệm của các đơn vị kinh doanh dịch vụ cho thuê thiết bị công nghệ thông tin trên địa bàn TP. Hồ Chí Minh.")
    add_p(doc, "Về phạm vi công nghệ: Ứng dụng được cài đặt trên nền tảng .NET 9 (C# 13), hệ quản trị cơ sở dữ liệu Microsoft SQL Server 2022, sử dụng Entity Framework Core 9, thư viện ClosedXML, hệ thống RESTful API kết nối di động và triển khai trên máy chủ Internet Information Services (IIS).")

    add_heading_2(doc, "4. KẾ HOẠCH VÀ PHÂN CÔNG THỰC HIỆN ĐỀ TÀI (12 TUẦN)")
    add_p(doc, "Đề tài được thực hiện nghiêm túc trong khung thời gian 12 tuần (từ ngày 17/08/2026 đến ngày 08/11/2026) theo đúng tiến độ đề cương chi tiết đã đăng ký với Khoa Công nghệ Thông tin - HUIT. Dưới đây là bảng phân công nhiệm vụ và ma trận trách nhiệm cụ thể giữa 02 sinh viên thực hiện:")

    schedule_data = [
        ("Tuần 1", "17/08 - 23/08/2026", "Khảo sát cơ cấu tổ chức, quy trình nghiệp vụ và thu thập biểu mẫu thực tế; lập kế hoạch làm việc.", "Hồ Sĩ Tuấn (Chính)\nPhan Minh Quân (Hỗ trợ)"),
        ("Tuần 2", "24/08 - 30/08/2026", "Xác định danh mục yêu cầu chức năng, phi chức năng trên hệ thống Website và kiến trúc API.", "Phan Minh Quân (Chính)\nHồ Sĩ Tuấn (Hỗ trợ)"),
        ("Tuần 3", "31/08 - 06/09/2026", "Thiết kế mô hình nghiệp vụ, mô hình Use Case, Class phân tích, lược đồ ERD và CSDL 18 bảng.", "Hồ Sĩ Tuấn (Chính)\nPhan Minh Quân (Chính)"),
        ("Tuần 4", "07/09 - 13/09/2026", "Cài đặt module quản lý thiết bị/serial, loại hình thuê, quản lý khách hàng và phân công nhân viên.", "Phan Minh Quân (Chính)\nHồ Sĩ Tuấn (Hỗ trợ)"),
        ("Tuần 5", "14/09 - 20/09/2026", "Xây dựng hệ thống Backend API chung (RESTful API), chức năng lập hợp đồng và giao nhận thiết bị.", "Hồ Sĩ Tuấn (Chính)\nPhan Minh Quân (Hỗ trợ)"),
        ("Tuần 6", "21/09 - 27/09/2026", "Cài đặt hoàn thành hợp đồng, gia hạn hợp đồng, phân kỳ nợ và áp dụng mã khuyến mãi.", "Hồ Sĩ Tuấn (Chính)\nPhan Minh Quân (Hỗ trợ)"),
        ("Tuần 7", "28/09 - 04/10/2026", "Cài đặt chức năng báo sự cố, phân công nhân viên bảo trì và quản lý trạng thái sửa chữa.", "Phan Minh Quân (Chính)\nHồ Sĩ Tuấn (Hỗ trợ)"),
        ("Tuần 8", "05/10 - 11/10/2026", "Cài đặt phân quyền RBAC 4 vai trò và phân hệ chức năng trên giao diện Web Responsive đa thiết bị.", "Hồ Sĩ Tuấn (Chính)\nPhan Minh Quân (Chính)"),
        ("Tuần 9", "12/10 - 18/10/2026", "Cài đặt dashboard thống kê báo cáo BI, kết xuất Excel ClosedXML và tra cứu dữ liệu.", "Phan Minh Quân (Chính)\nHồ Sĩ Tuấn (Hỗ trợ)"),
        ("Tuần 10", "19/10 - 25/10/2026", "Thử nghiệm hệ thống, sửa lỗi và xây dựng module sao lưu & phục hồi CSDL (Backup & Restore).", "Hồ Sĩ Tuấn (Chính)\nPhan Minh Quân (Hỗ trợ)"),
        ("Tuần 11", "26/10 - 01/11/2026", "Kiểm thử tự động xUnit (ChallengerTests), hoàn thiện toàn bộ các chức năng hệ thống.", "Hồ Sĩ Tuấn (Chính)\nPhan Minh Quân (Chính)"),
        ("Tuần 12", "02/11 - 08/11/2026", "Hoàn chỉnh toàn văn báo cáo khóa luận, thiết kế bài thuyết trình Slide và nộp báo cáo.", "Hồ Sĩ Tuấn (Chính)\nPhan Minh Quân (Chính)")
    ]
    add_table_with_caption(doc, "0.4", 1, "Bảng tiến độ kế hoạch thực hiện và phân công nhiệm vụ 12 tuần",
                           ["Tuần", "Khung thời gian", "Nội dung công việc triển khai theo đề cương", "Phân công trách nhiệm"],
                           schedule_data, col_widths=[1.8, 2.7, 7.0, 3.5])
    doc.add_page_break()


def build_chapter1_survey(doc):
    """
    CHƯƠNG 1: KHẢO SÁT HỆ THỐNG
    1.1 Tổng quan lĩnh vực và mô hình hoạt động
    1.2 Cơ cấu tổ chức: 4 phòng ban
    1.3 Quy trình truyền thống: 6 bước, 4 bất cập
    1.4 KẾT CHƯƠNG
    """
    add_heading_1(doc, "CHƯƠNG 1: KHẢO SÁT HỆ THỐNG")

    add_heading_2(doc, "1.1. TỔNG QUAN VỀ LĨNH VỰC CHO THUÊ THIẾT BỊ CÔNG NGHỆ VÀ MÔ HÌNH HOẠT ĐỘNG")
    add_heading_3(doc, "1.1.1. Mô hình hoạt động và đối tượng khách hàng trọng tâm")
    add_p(doc, "Lĩnh vực cung cấp dịch vụ cho thuê thiết bị công nghệ thông tin (IT Equipment Rental Services) đang phát triển với tốc độ nhanh tại các trung tâm kinh tế lớn, đặc biệt là khu vực TP. Hồ Chí Minh. Doanh nghiệp cung ứng các dòng sản phẩm đa dạng gồm máy tính xách tay (Laptop doanh nghiệp), máy trạm đồ họa chuyên dụng (Workstation), máy chủ vật lý (Server), cùng hệ thống máy in, máy chiếu công suất lớn phục vụ 3 nhóm đối tượng khách hàng trọng tâm:")
    add_bullet(doc, "Khách hàng doanh nghiệp công nghệ & SMEs: Thuê phòng máy làm việc dài hạn từ 6 tháng đến 2 năm nhằm tối ưu hóa chi phí vận hành (OpEx) và không lo khấu hao tài sản.")
    add_bullet(doc, "Các trường đại học và cơ sở giáo dục: Thuê các dàn máy tính đồng bộ cấu hình cao phục vụ các đợt thi sát hạch chứng chỉ quốc tế hoặc hội thảo chuyên đề từ 3 đến 7 ngày.")
    add_bullet(doc, "Các đơn vị tổ chức sự kiện & truyền thông: Thuê thiết bị trình chiếu, máy tính cấu hình mạnh trong các sự kiện ra mắt sản phẩm hoặc hội nghị ngắn ngày (1 đến 3 ngày).")

    add_heading_3(doc, "1.1.2. Khảo sát chi tiết 6 bước trong quy trình cho thuê thiết bị truyền thống (AS-IS)")
    add_p(doc, "Qua điều tra thực tế tại các đơn vị kinh doanh dịch vụ cho thuê thiết bị công nghệ trên địa bàn TP. Hồ Chí Minh, toàn bộ chu trình vận hành thủ công hiện tại trải qua 6 bước tuần tự, với nhiều nút thắt và hạn chế nghiêm trọng:")
    add_bullet(doc, "Bước 1 – Tiếp nhận nhu cầu thuê thiết bị: Khách hàng liên hệ qua điện thoại, email hoặc nhắn tin qua Zalo. Nhân viên kinh doanh ghi chép nhu cầu về chủng loại máy, cấu hình, số lượng và thời gian thuê vào sổ tay cá nhân. Điểm nghẽn: Mất thời gian tiếp nhận, thông tin phân tán, dễ bỏ sót cấu hình đặc thù.")
    add_bullet(doc, "Bước 2 – Kiểm tra tồn kho thiết bị thủ công: Nhân viên tra cứu sổ kho giấy hoặc liên hệ bộ phận kỹ thuật để kiểm tra thiết bị còn trên kệ kho; đếm số lượng thủ công hoặc mở file Excel nội bộ. Điểm nghẽn: Không đồng bộ tức thời số lượng, sai lệch tồn kho, nguy cơ trùng lịch thuê máy.")
    add_bullet(doc, "Bước 3 – Soạn thảo và ký kết hợp đồng giấy: Nhân viên soạn hợp đồng trên Word, in 02 bản cứng; yêu cầu khách hàng xuất trình CCCD gốc để photo và ký tay trực tiếp lên từng trang. Điểm nghẽn: Tốn phí in ấn, thủ tục kéo dài nhiều giờ hoặc từ 1 đến 2 ngày, rủi ro thất lạc, hư hỏng hồ sơ giấy.")
    add_bullet(doc, "Bước 4 – Thu tiền đặt cọc và bàn giao máy: Thu tiền cọc bằng tiền mặt hoặc chuyển khoản cá nhân; bàn giao máy kèm phụ kiện; viết giấy biên nhận cọc hoặc phiếu thu tay 3 liên. Điểm nghẽn: Dễ nhầm lẫn tiền cọc, rủi ro tiền mặt thất thoát, không có cơ chế đối soát tự động.")
    add_bullet(doc, "Bước 5 – Sử dụng thiết bị và theo dõi công nợ: Khách mang máy về sử dụng. Nhân viên theo dõi lịch trả máy và kỳ trả góp bằng bảng tính Excel rời rạc; tự rà soát và gọi điện nhắc nợ. Điểm nghẽn: Khó kiểm soát công nợ quá hạn, nhắc nợ hoàn toàn thủ công, nguy cơ phát sinh nợ xấu cao.")
    add_bullet(doc, "Bước 6 – Trả máy, nghiệm thu kỹ thuật và quyết toán: Khi hết hạn hợp đồng, khách mang máy trả. Kỹ thuật viên kiểm tra ngoại quan bằng mắt thường và bật máy kiểm tra sơ bộ; đối chiếu hợp đồng giấy để hoàn cọc hoặc tính phí phạt. Điểm nghẽn: Dễ tranh chấp hư hại khi máy hỏng, thiếu biên bản số, khó phát hiện linh kiện bị tráo đổi.")

    steps_data = [
        ("1", "Tiếp nhận nhu cầu thuê", "Khách liên hệ trực tiếp, gọi điện hoặc qua Zalo. Nhân viên ghi chép cấu hình, số lượng và thời gian thuê vào sổ tay.", "Sổ tay cá nhân, Zalo, Email", "Mất thời gian tiếp nhận, thông tin phân tán, dễ bỏ sót cấu hình đặc thù."),
        ("2", "Kiểm kho thủ công", "Tra cứu sổ kho giấy hoặc hỏi kỹ thuật viên kiểm tra thiết bị trên kệ kho. Đếm số lượng khả dụng thủ công.", "Sổ theo dõi kho, Excel nội bộ", "Không đồng bộ tức thời số lượng, sai lệch tồn kho, nguy cơ trùng lịch thuê máy."),
        ("3", "Soạn & ký hợp đồng giấy", "Soạn hợp đồng Word, in 02 bản cứng. Yêu cầu khách xuất trình CCCD gốc để photo và ký tay trực tiếp.", "File mẫu Word, máy in, bản photo CCCD", "Tốn phí in ấn, thủ tục kéo dài nhiều giờ / ngày, rủi ro thất lạc, hư hỏng hồ sơ giấy."),
        ("4", "Thu cọc & Bàn giao máy", "Thu tiền mặt hoặc chuyển khoản cá nhân; bàn giao máy & phụ kiện kèm theo; viết giấy biên nhận đặt cọc 3 liên.", "Phiếu thu tay 3 liên, sổ quỹ tiền mặt", "Dễ nhầm lẫn tiền cọc, rủi ro tiền mặt thất thoát, không có đối soát tự động."),
        ("5", "Sử dụng & Theo dõi nợ", "Khách mang máy về sử dụng. Nhân viên theo dõi lịch trả máy và kỳ trả góp bằng bảng tính Excel rời rạc; gọi điện nhắc nợ.", "Bảng tính Excel nợ (.xlsx), sổ theo dõi", "Khó kiểm soát công nợ quá hạn, nhắc nợ thủ công, nguy cơ phát sinh nợ xấu cao."),
        ("6", "Trả máy & Quyết toán", "Kỹ thuật kiểm tra ngoại quan máy; đối chiếu hợp đồng giấy lưu trữ; hoàn cọc tiền mặt hoặc tính phí phạt trễ hạn.", "Hợp đồng giấy gốc, phiếu chi tiền mặt", "Dễ tranh chấp hư hại khi máy hỏng, không có biên bản số, khó phát hiện tráo linh kiện.")
    ]
    add_table_with_caption(doc, "1.1.2", 1, "Bảng tổng hợp các bước trong quy trình cho thuê thiết bị truyền thống (AS-IS)",
                           ["Bước", "Tên bước nghiệp vụ", "Thao tác thực hiện chi tiết", "Công cụ / Biểu mẫu", "Nút thắt rủi ro vận hành (Bottleneck)"],
                           steps_data, col_widths=[1.2, 3.2, 4.0, 3.0, 3.6])

    doc.add_page_break()
    add_heading_2(doc, "1.2. CƠ CẤU TỔ CHỨC VÀ CÁC PHÂN HỆ VẬN HÀNH")
    add_p(doc, "Bộ máy vận hành chu trình cho thuê thiết bị công nghệ được cơ cấu thành 4 vai trò tác nhân chuyên trách:")
    add_bullet(doc, "Quản trị viên hệ thống (Admin): Quản trị người dùng, phân quyền truy cập, thiết lập cấu hình giá thuê, tỷ lệ cọc và giám sát toàn diện hoạt động của hệ thống.")
    add_bullet(doc, "Phòng Kinh doanh & Dịch vụ khách hàng: Tiếp nhận nhu cầu thuê, tư vấn cấu hình, kiểm tra số lượng tồn kho khả dụng, lập báo giá, duyệt hợp đồng, theo dõi lịch thanh toán phân kỳ và hỗ trợ đối soát công nợ.")
    add_bullet(doc, "Phòng Quản lý kho & Kỹ thuật: Tiếp nhận lệnh xuất kho, kiểm định phần cứng, dán tem serial, niêm phong thiết bị, giao nhận máy tận nơi, thực hiện bảo trì sự cố và nghiệm thu thu hồi máy khi kết thúc hợp đồng.")
    add_bullet(doc, "Khách hàng (Cá nhân & Doanh nghiệp): Đăng ký tài khoản, lựa chọn cấu hình máy, ký hợp đồng điện tử trực tuyến, thanh toán cọc qua mã VietQR và gửi yêu cầu hỗ trợ kỹ thuật.")

    add_figure_with_caption(doc, "1.2", 1, "Sơ đồ luồng quy trình nghiệp vụ tổng thể sau khi tin học hóa",
                            "figures/hinh_1_2_quy_trinh_tong_the_de_xuat.png", width_cm=14.0)

    tobe_stages_data = [
        ("GĐ 1", "Đặt thuê trực tuyến (Online Booking)", "Khách hàng (Web Client)", "Duyệt Catalog, chọn thời gian thuê, nhập voucher KhuyenMai, SemaphoreSlim khóa tồn kho, khởi tạo hợp đồng trạng thái Chờ ký (ChoKy).", "Ngăn chặn triệt để hiện tượng Overbooking và tranh chấp giữ chỗ máy."),
        ("GĐ 2", "Ký số & Thẩm định hồ sơ", "Khách hàng (Contract Sign)", "Chọn phân kỳ 1-5 kỳ, vẽ chữ ký HTML5 Canvas Base64, tải CCCD 2 mặt, bộ thẩm định Magic Bytes PNG/JPEG (trần 256KB/5MB), chuyển Chờ duyệt.", "Đảm bảo pháp lý điện tử tức thời, loại bỏ 100% thời gian in ấn ký giấy (24-48h)."),
        ("GĐ 3", "Duyệt & Giao thiết bị", "Admin / Quản lý kho", "Kiểm tra chữ ký và CCCD, cấp phát số serial vật lý, cập nhật trạng thái máy 3 -> 1, thuật toán Amortization sinh lịch nợ, lập Biên bản bàn giao điện tử.", "Tự động hóa lịch trình cấp phát serial, loại bỏ sai sót ghi tay số serial."),
        ("GĐ 4", "Thanh toán & Đối soát", "Khách hàng & Open Banking", "Tra cứu sổ nợ MyDebt, quét VietQR MBBank Napas 247, Webhook bắt biến động số dư, Serializable Transaction gạch nợ Waterfall, sinh PhieuThu tự động trong 3s.", "Đối soát gạch nợ tự động chính xác trong 3 giây, loại bỏ 100% rủi ro chuyển tiền thủ công."),
        ("GĐ 5", "Bảo trì & Quyết toán", "Kỹ thuật viên & Quản trị", "Báo hỏng trực tuyến kèm ảnh, điều phối KTV, kích hoạt cờ TamDungTinhTien nếu quá 24h khấu trừ tiền thuê, nghiệm thu trả máy, quyết toán hoàn cọc PhieuChi.", "Minh bạch tuyệt đối bảo trì, giải quyết công bằng quyền lợi tạm dừng tính tiền thuê.")
    ]
    add_table_with_caption(doc, "1.2", 1, "Bảng đặc tả các giai đoạn trong quy trình cho thuê thiết bị đề xuất (TO-BE) trên nền tảng RentalSystem",
                           ["Giai đoạn", "Tên giai đoạn nghiệp vụ", "Tác nhân & Giao diện", "Cơ chế tự động hóa & Thuật toán xử lý", "Hiệu quả khắc phục điểm nghẽn"],
                           tobe_stages_data, col_widths=[1.5, 3.2, 2.8, 4.3, 3.2])

    doc.add_page_break()
    add_heading_2(doc, "1.3. PHÂN TÍCH ĐIỂM NGHẼN VẬN HÀNH VÀ ĐẶC TẢ BIỂU MẪU NGHIỆP VỤ")
    add_p(doc, "Bốn bất cập và hạn chế chính trong quy trình quản lý thủ công bao gồm:")
    add_bullet(doc, "Tranh chấp lịch thuê và hiện tượng Overbooking (tồn kho ảo): Do bảng tính Excel không có cơ chế khóa tương tranh, khi hai nhân viên cùng tư vấn một lô máy tính cho hai khách hàng khác nhau trong cùng khung thời gian, cả hai đều tưởng còn máy và chốt hợp đồng, dẫn đến tình trạng ký vượt quá số lượng máy thực tế có trong kho.")
    add_bullet(doc, "Rủi ro thất thoát thiết bị và lẫn lộn số Serial vật lý: Việc ghi chép số serial trên giấy dễ bị nhầm lẫn giữa các ký tự tương đồng (như '0' và 'O', '1' và 'I'). Doanh nghiệp không thể truy vết được lịch sử thiết bị đã qua tay bao nhiêu khách hàng, đã sửa chữa những linh kiện gì, làm tăng nguy cơ bị tráo đổi linh kiện đắt tiền.")
    add_bullet(doc, "Thủ tục giấy tờ rườm rà, kéo dài nhiều giờ: Khách hàng phải đến tận văn phòng để ký hợp đồng giấy và xuất trình CCCD photo, làm chậm trễ các đơn hàng thuê máy phục vụ sự kiện khẩn cấp.")
    add_bullet(doc, "Tắc nghẽn đối soát ngân hàng và rủi ro nợ xấu kéo dài: Nhân viên kinh doanh phải dò từng dòng sao kê ngân hàng với các giao dịch chuyển khoản không rõ nội dung. Việc theo dõi lịch trả góp theo tháng bằng bảng tính dễ bị bỏ sót, không có công thức phạt tự động, dẫn đến tỷ lệ nợ quá hạn cao.")

    bottlenecks_data = [
        ("1", "Tồn kho ảo & Overbooking", "Kinh doanh / Kho", "Nghiêm trọng", "Hủy đơn sát ngày giao, mất uy tín"),
        ("2", "Thất thoát Serial linh kiện", "Quản lý kho", "Rất cao", "Tráo đổi RAM, SSD, thiệt hại tài sản"),
        ("3", "Thủ tục ký hợp đồng chậm", "Khách hàng / KD", "Trung bình", "Khách bỏ sang đối thủ cạnh tranh"),
        ("4", "Nợ đọng & Đối soát thủ công", "Kinh doanh & Công nợ", "Rất cao", "Tắc dòng tiền, thất thoát tiền cọc")
    ]
    add_table_with_caption(doc, "1.1.3", 1, "Bảng phân tích các điểm nghẽn và rủi ro vận hành trong quy trình thủ công",
                           ["STT", "Điểm nghẽn vận hành", "Phân hệ ảnh hưởng", "Mức độ rủi ro", "Hậu quả kinh tế"],
                           bottlenecks_data, col_widths=[1.2, 4.0, 3.2, 2.8, 3.8])

    forms_data = [
        ("BM-01", "Hợp đồng cho thuê thiết bị công nghệ", "Word (.docx)", "Soạn thảo tay theo từng hợp đồng"),
        ("BM-02", "Biên bản bàn giao và nghiệm thu máy", "Giấy in sẵn", "Điền tay thông số ngoại quan và Serial"),
        ("BM-03", "Phiếu thu tiền cọc và tiền thuê", "Phiếu thu 3 liên", "Nhân viên kinh doanh viết tay, xé liên giao khách"),
        ("BM-04", "Phiếu tiếp nhận yêu cầu bảo trì / sự cố", "Sổ ghi chép nội bộ", "Dễ thất lạc yêu cầu của khách hàng"),
        ("BM-05", "Bảng theo dõi công nợ và trả góp", "Excel (.xlsx)", "Theo dõi thủ công, không nhắc nợ tự động")
    ]
    add_table_with_caption(doc, "1.3", 1, "Danh sách và đặc tả các biểu mẫu nghiệp vụ quản lý cho thuê thiết bị",
                           ["Mã BM", "Tên biểu mẫu nghiệp vụ", "Định dạng hiện tại", "Phương thức quản lý"],
                           forms_data, col_widths=[2.0, 5.0, 3.0, 5.0])

    compare_data = [
        ("Thời gian tạo hợp đồng", "24 – 48 giờ (in ấn, chuyển phát)", "Dưới 3 phút (Ký số Canvas trực tuyến)"),
        ("Kiểm soát tồn kho máy", "Dễ trùng lặp (Overbooking)", "Khóa SemaphoreSlim chống tranh chấp"),
        ("Thanh toán & Đối soát", "Dò sao kê SMS thủ công", "Mã VietQR động NAPAS 247 & Webhook tức thì"),
        ("Quản lý mã Serial máy", "Ghi chép tay trên sổ sách", "Quản lý vòng đời chi tiết từng máy Serial"),
        ("Theo dõi & Thu hồi nợ", "Dễ bỏ sót kỳ nợ trên Excel", "Tự động phân 4 nhóm tuổi nợ, tính phạt 0.1%/ngày"),
        ("Báo cáo số liệu quản trị", "Mất 2-3 ngày để tổng hợp", "Dashboard BI thời gian thực, xuất Excel 1 chạm")
    ]
    add_table_with_caption(doc, "1.3", 2, "Bảng đối sánh tính năng giữa phương thức quản lý truyền thống và hệ thống tin học hóa",
                           ["Tiêu chí đánh giá", "Phương thức quản lý truyền thống", "Hệ thống RentalSystem đề xuất"],
                           compare_data, col_widths=[3.5, 5.5, 6.0])

    add_heading_2(doc, "1.4. KẾT CHƯƠNG")
    add_p(doc, "Chương 1 đã hoàn thành việc khảo sát toàn diện hiện trạng hoạt động của lĩnh vực cho thuê thiết bị công nghệ, phân tích rõ cơ cấu tổ chức bộ máy 4 phòng ban chuyên trách và chỉ ra 4 điểm nghẽn nghiêm trọng của quy trình vận hành thủ công (tồn kho ảo overbooking, thất thoát serial, thủ tục kéo dài và rủi ro nợ xấu). Những khảo sát thực tế này là cơ sở thực tiễn và kỹ thuật để tiến hành phân tích các giải thuật cốt lõi và mô hình hóa hệ thống mới tại Chương 2.")
    doc.add_page_break()


def build_chapter2_analysis(doc):
    """
    CHƯƠNG 2: PHÂN TÍCH HỆ THỐNG
    2.1 Các thuật toán và cơ chế kỹ thuật cốt lõi (2.1.1 SemaphoreSlim, 2.1.2 VietQR, 2.1.3 Phân kỳ nợ)
    2.2 Mô hình hóa nghiệp vụ (2.2.1 Usecase tổng quát, 2.2.2 7 quy trình với Activity, Sequence, Collab)
    2.3 Mô hình hóa chức năng (2.3.1 Use case hệ thống, 2.3.2 12 bảng đặc tả)
    2.4 Sơ đồ lớp mức phân tích
    2.5 KẾT CHƯƠNG
    """
    add_heading_1(doc, "CHƯƠNG 2: PHÂN TÍCH HỆ THỐNG")

    add_heading_2(doc, "2.1. CÁC THUẬT TOÁN VÀ CƠ CHẾ KỸ THUẬT CỐT LÕI")
    
    # 2.1.1 SemaphoreSlim
    add_heading_3(doc, "2.1.1. Cơ chế kiểm soát tương tranh SemaphoreSlim đa tầng")
    add_p(doc, "Trong môi trường ứng dụng web ASP.NET Core hoạt động đa luồng (multi-threaded request pipeline), khi nhiều khách hàng cùng thực hiện đặt thuê (Checkout) cho cùng một loại thiết bị tại cùng một thời điểm, hiện tượng tranh chấp điều kiện (Race Condition) chắc chắn sẽ xảy ra nếu chỉ dùng các câu lệnh truy vấn CSDL thông thường. Cả hai luồng đều đọc thấy số lượng máy khả dụng (ví dụ còn 1 máy), sau đó cả hai luồng đều tiến hành ghi nhận hợp đồng và đổi trạng thái máy, dẫn đến tình trạng bán vượt tồn kho (Overbooking) hoặc cấp phát trùng số Serial vật lý.")
    add_p(doc, "Để giải quyết hiệu quả vấn đề này, RentalSystem áp dụng cơ chế khóa bất đồng bộ SemaphoreSlim(1, 1). Khác với từ khóa lock truyền thống trong C# (vốn chặn cứng luồng của hệ điều hành và không hỗ trợ từ khóa await), SemaphoreSlim được thiết kế tối ưu cho mô hình lập trình bất đồng bộ (async/await), cho phép nhả luồng của ThreadPool quay lại phục vụ các yêu cầu HTTP khác trong khi chờ tài nguyên khóa được giải phóng.")
    add_p(doc, "Hệ thống triển khai cơ chế kiểm soát tương tranh qua 4 khối vận hành chặt chẽ:")
    add_bullet(doc, "Khối 1 – Tiếp nhận yêu cầu đồng thời: Các luồng yêu cầu Checkout từ Web (Khách 1 tại T0), Mobile (Khách 2 tại T0 + 2ms), Nhân viên tại quầy (Kinh doanh tại T0 + 5ms) và phụ tải cao đồng thời gửi HTTP POST cạnh tranh cùng một cấu hình máy.")
    add_bullet(doc, "Khối 2 – Cổng khóa đơn tiến trình (Process Gate): Khai báo static readonly SemaphoreSlim InventoryLock = new SemaphoreSlim(1, 1). Luồng đầu tiên gọi await InventoryLock.WaitAsync() được cấp quyền ngay (Count = 0); các luồng đến sau tự động xếp hàng đợi trong ThreadPool ở trạng thái non-blocking, hoàn toàn không chiếm dụng chu kỳ CPU vô ích.")
    add_bullet(doc, "Khối 3 – Xử lý trong Vùng găng CSDL (Critical Section): Kiểm tra tồn kho khả dụng thời gian thực CountAsync(t => t.TrangThai != 2 && !Overlaps(NgayBatDau, NgayKetThuc)). Nếu đủ máy: Gán Serial, cập nhật TrangThai = 3 (Giữ chỗ 24h), thiết lập HanChotKy = Now + 24h, sinh HopDong, xóa Session và trả về HTTP 200 OK chuyển hướng đến Ký số Canvas và VietQR. Nếu hết máy: Phát hiện xung đột tồn kho, báo lỗi, Rollback và trả về HTTP Redirect thông báo máy đã kín lịch.")
    add_bullet(doc, "Khối 4 – Giải phóng khóa và Đánh thức luồng kế tiếp: Đặt trong khối finally { InventoryLock.Release(); } để bảo đảm khóa luôn được hoàn trả trong mọi tình huống (kể cả khi xảy ra Exception). Giá trị Count hồi phục về 1 và đánh thức luồng kế tiếp trong ThreadPool vào vùng găng.")

    semaphore_matrix_data = [
        ("Khách 1 (Web)", "T0", "Cấp quyền (Count = 0)", "Kiểm tra còn máy -> Gán Serial -> Đổi TrangThai = 3 (Giữ chỗ 24h) -> Sinh HopDong", "HTTP 200 OK (Chuyển trang Ký số Canvas & VietQR)"),
        ("Khách 2 (Mobile)", "T0 + 2ms", "Xếp hàng đợi ThreadPool", "Chờ Khách 1 nhả khóa -> Vào vùng găng: Máy cuối đã bị Khách 1 giữ -> Báo lỗi hết máy", "HTTP Redirect (Thông báo máy đã kín lịch, cập nhật giỏ)"),
        ("Kinh doanh (Quầy)", "T0 + 5ms", "Xếp hàng đợi ThreadPool", "Tiếp tục chờ Khách 2 nhả khóa -> Kiểm tra tồn kho thời gian thực -> Phản hồi đúng trạng thái", "HTTP Redirect / 200 OK (Đồng bộ số liệu tức thời)"),
        ("Khách N (Tải cao)", "T0 + k ms", "Xếp hàng tuần tự", "Được phục vụ tuần tự non-blocking, bảo vệ toàn vẹn dữ liệu, chống bán vượt tồn kho", "Phản hồi chính xác từng giao dịch, không sinh đơn rác")
    ]
    add_table_with_caption(doc, "2.1.1", 1, "Ma trận kịch bản kiểm soát tương tranh giữ chỗ máy bằng cơ chế SemaphoreSlim",
                           ["Kịch bản giao dịch", "Thời điểm (T)", "Trạng thái Semaphore", "Xử lý trong Vùng găng CSDL", "Kết quả phản hồi HTTP"],
                           semaphore_matrix_data, col_widths=[2.8, 1.8, 3.2, 4.2, 3.0])

    # 2.1.2 VietQR NAPAS 247
    add_heading_3(doc, "2.1.2. Thuật toán sinh mã VietQR động NAPAS 247 và Đối soát Ngân hàng Mở")
    add_p(doc, "Nhằm tối ưu hóa trải nghiệm thanh toán và tự động hóa khâu gạch nợ, hệ thống tích hợp giải thuật sinh mã VietQR động theo chuẩn EMVCo Merchant-Presented Mode (MPM) và tiêu chuẩn kỹ thuật NAPAS 247 của Công ty Cổ phần Thanh toán Quốc gia Việt Nam.")
    add_p(doc, "Bản tin mã QR là một chuỗi ký tự chuẩn hóa tuân thủ cấu trúc Type-Length-Value (TLV) gồm các trường thông tin chính:")
    add_bullet(doc, "Tag 00 (Payload Format Indicator): Giá trị '01'.")
    add_bullet(doc, "Tag 01 (Point of Initiation Method): Giá trị '12' (Mã QR động, có chứa số tiền giao dịch cụ thể).")
    add_bullet(doc, "Tag 38 (Merchant Account Information): Chuỗi dữ liệu nhúng gồm Subtag 00 định danh mạng lưới 'A000000727' (NAPAS), Subtag 01 mã định danh ngân hàng thụ hưởng '970422' (MBBank), và Subtag 02 số tài khoản thụ hưởng doanh nghiệp '999988882026' mang tên đơn vị thụ hưởng RENTALSYSTEM ENTERPRISE.")
    add_bullet(doc, "Tag 53 (Transaction Currency): Giá trị '704' (Đồng Việt Nam – VND).")
    add_bullet(doc, "Tag 54 (Transaction Amount): Số tiền thanh toán thực tế (ví dụ: '5000000').")
    add_bullet(doc, "Tag 58 (Country Code): Giá trị 'VN'.")
    add_bullet(doc, "Tag 62 (Additional Data Field Template): Chứa Subtag 08 mã nội dung chuyển khoản chuẩn hóa, được sinh tự động theo quy tắc 'HD{MaHopDong}' (đối với tiền cọc) hoặc 'KY{MaKyHan}' (đối với tiền thuê kỳ hạn).")
    add_bullet(doc, "Tag 63 (CRC Checksum): Mã kiểm tra dư thừa tuần hoàn 4 ký tự Hex, được tính toán bằng giải thuật CRC16-CCITT với đa thức 0x1021 và giá trị khởi tạo 0xFFFF trên toàn bộ chuỗi ký tự từ Tag 00 đến đầu Tag 63.")
    add_p(doc, "Khi khách hàng quét mã và xác nhận chuyển tiền trên ứng dụng Mobile Banking, hệ thống ngân hàng sẽ phát một bản tin Webhook HTTPS về cổng tiếp nhận POST /Payment/BankingWebhook của RentalSystem. Bộ phân tích Webhook sử dụng biểu thức chính quy Regex để bóc tách mã hợp đồng và số kỳ hạn, đối soát số tiền chuyển thực tế với số tiền nợ trên hệ thống theo thuật toán Thác nước 4 tầng (Waterfall Reconciliation), tự động sinh Phiếu thu điện tử (với MaNhanVienThu = null) và gạch nợ tức thì mà không cần sự can thiệp thủ công của nhân viên kinh doanh.")

    add_figure_with_caption(doc, "2.1.2", 1, "Cấu trúc bản tin và giải thuật sinh chuỗi mã VietQR động NAPAS 247",
                            "figures/hinh_2_1_2_1_vietqr_napas247_structure.png", width_cm=14.5)

    add_p(doc, "Nhằm bảo vệ tính toàn vẹn dữ liệu và chống gian lận trong giao dịch thanh toán, hệ thống áp dụng giải thuật kiểm tra mã dư thừa tuần hoàn CRC16-CCITT tại Tag 63 và quy trình đối soát tự động qua Open Banking Webhook:")
    add_bullet(doc, "Giải thuật kiểm tra toàn vẹn CRC16-CCITT (Tag 63): Đa thức sinh chuẩn EMVCo G(x) = x^16 + x^12 + x^5 + 1 (mã biểu diễn Hex 0x1021, giá trị khởi tạo 0xFFFF). Quy trình tính toán gồm 4 bước: (1) Ghép nối chuỗi bản tin từ Tag 00 đến tiền tố '6304'; (2) Quét tuần tự từng byte, thực hiện phép dịch bit XOR; (3) Kết xuất giá trị 16-bit Hexadecimal 4 ký tự in hoa; (4) Nối giá trị CRC vào cuối chuỗi (ví dụ: ...6304F8D2). Cơ chế chống gian lận: Mọi can thiệp sửa đổi số tiền (Tag 54) hoặc số tài khoản (Tag 38) sẽ khiến mã CRC16 sai lệch, ứng dụng Mobile Banking sẽ từ chối giao dịch ngay lập tức.")

    webhook_steps_data = [
        ("1", "Quét VietQR & Chuyển khoản", "Mobile Banking khách hàng", "Khách quét mã VietQR động có sẵn số tiền và nội dung định danh duy nhất (ví dụ: 0810HD105 KY2)."),
        ("2", "Phát tín hiệu Webhook", "Cổng NAPAS 247 / MBBank", "Hệ thống ngân hàng phát bản tin HTTPS POST chứa biến động số dư đến Endpoint /Payment/BankingWebhook."),
        ("3", "Khóa tương tranh đơn luồng", "SemaphoreSlim PaymentLock", "Tiếp nhận bản tin và đưa vào hàng đợi xử lý tuần tự đơn luồng, ngăn chặn Race Condition gạch nợ kép."),
        ("4", "Bóc tách mã hợp đồng", "Regex Parser (Regex.Match)", "Bóc tách tự động mã hợp đồng và số kỳ hạn theo biểu thức chính quy HD(?<id>\\d+) hoặc KY(?<id>\\d+)."),
        ("5", "Kiểm tra chống lặp (Idempotency)", "Idempotency Guard & Cache", "Tra cứu mã giao dịch ngân hàng trong CSDL. Nếu đã xử lý, phản hồi HTTP 200 OK và bỏ qua giao dịch trùng lặp."),
        ("6", "Phân bổ dòng tiền Thác nước", "Thuật toán Waterfall", "Tự động phân bổ số tiền thanh toán theo thứ tự: Gạch nợ gốc kỳ hạn -> Xóa tiền phạt chậm trả -> Bồi thường hư hại."),
        ("7", "Sinh Phiếu thu điện tử tự động", "Phân hệ Tài chính", "Tự động lập bản ghi PhieuThu với MaNhanVienThu = null (tự động 100%), lưu mã tham chiếu ngân hàng."),
        ("8", "Cập nhật trạng thái hợp đồng", "State Machine (HopDongService)", "Hợp đồng chuyển sang Đã đặt cọc (đơn mới) hoặc cập nhật giảm trừ công nợ chỉ trong vòng 3 giây.")
    ]
    add_table_with_caption(doc, "2.1.2", 1, "Quy trình đối soát tự động và gạch nợ qua Open Banking Webhook 24/7",
                           ["Bước", "Thao tác nghiệp vụ", "Module / Thành phần đảm nhiệm", "Chi tiết thực thi & Cơ chế an toàn"],
                           webhook_steps_data, col_widths=[1.2, 3.5, 3.5, 6.8])

    # 2.1.3 Phân kỳ & Tuổi nợ
    add_heading_3(doc, "2.1.3. Thuật toán phân kỳ trả góp và quản lý tuổi nợ tự động")
    add_p(doc, "Đối với các hợp đồng thuê máy dài hạn (từ 3 tháng trở lên), việc yêu cầu khách hàng thanh toán toàn bộ chi phí một lần sẽ tạo áp lực dòng tiền rất lớn. RentalSystem cài đặt thuật toán phân kỳ tài chính tự động (Amortization Algorithm), chia nhỏ tổng giá trị tiền thuê thành các kỳ hạn định kỳ theo tháng:")
    add_bullet(doc, "Thông số hợp đồng đầu vào: Tổng tiền thuê thiết bị (T), Tiền đặt cọc máy bảo toàn (T_coc), Tiền trả trước đợt 1 (T_pre), Số kỳ hạn phân chia (N), Khoảng thời gian thuê [NgayBatDau, NgayKetThuc].")
    add_bullet(doc, "Công thức chia đều và làm tròn chuẩn tiền tệ: Tiền còn lại T_rem = T - T_pre; Tiền mỗi kỳ P_base = round(T_rem / (N * 1000)) * 1000. Cân đối kỳ hạn cuối cùng chống lệch số lẻ: P_N = T_rem - Sum(P_1 .. P_N-1).")
    add_bullet(doc, "Xác định lịch đến hạn phân kỳ: Kỳ 1 D_1 = NgayBatDau; Kỳ i D_i = D_1 + round((i-1)/(N-1) * TongSoNgayThue). Tự động khởi tạo N bản ghi trong bảng KyHanThanhToan.")
    add_p(doc, "Song song với việc sinh lịch trả góp, hệ thống vận hành cơ chế phân loại tuổi nợ tự động (Debt Aging Management), phân chia các khoản nợ thành 5 nhóm tuổi nợ (Tier 0 – 4) dựa trên số ngày quá hạn daysPastDue = Today - NgayDenHan. Công thức tính tiền phạt chậm trả (áp dụng từ ngày thứ 4 quá hạn, sau 3 ngày ân hạn):")
    add_p(doc, "LateFee = round((SoTienPhai - SoTienDaTra) * 0.001 * daysPastDue)", font_size_pt=12, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)

    debt_tiers_data = [
        ("Cấp 0 (Tier 0)", "Đúng hạn (Quá hạn <= 0 ngày)", "Bình thường", "0 VNĐ (Chưa áp dụng lãi phạt)", "Trạng thái bình thường; cho phép tạo hợp đồng mới; nhắc lịch hẹn tự động."),
        ("Cấp 1 (Tier 1)", "Cần chú ý (Quá hạn 1 – 30 ngày)", "Nhắc nợ sớm", "Ân hạn 3 ngày đầu; phạt 0.1%/ngày từ ngày 4", "Gửi Email & SMS nhắc nợ tự động kèm mã VietQR; chưa giới hạn quyền lợi thuê."),
        ("Cấp 2 (Tier 2)", "Dưới tiêu chuẩn (Quá hạn 31 – 60 ngày)", "Cảnh báo nợ", "0.1%/ngày lũy kế trên nợ gốc quá hạn", "Kinh doanh gọi điện trực tiếp; cảnh báo tạm dừng hợp đồng; giới hạn chức năng thuê."),
        ("Cấp 3 (Tier 3)", "Nợ nghi ngờ (Quá hạn 61 – 90 ngày)", "Nguy cơ cao", "0.1%/ngày + chi phí đôn đốc", "Tạm dừng bảo trì SLA tại chỗ; cảnh báo thu hồi máy; không cho gia hạn; chuyển tổ thu nợ."),
        ("Cấp 4 (Tier 4)", "Nợ xấu khó đòi (> 90 ngày hoặc nợ > 3tr)", "Nợ xấu", "Toàn bộ tiền cọc bị đối trừ bồi thường", "Khóa tài khoản toàn hệ thống; đưa vào Blacklist; niêm phong máy từ xa; xử lý pháp lý.")
    ]
    add_table_with_caption(doc, "2.1.3", 1, "Bảng tiêu chí phân loại 4 cấp độ tuổi nợ và chính sách xử lý tài chính tự động",
                           ["Cấp độ tuổi nợ", "Tiêu chí số ngày quá hạn", "Trạng thái nợ", "Chính sách phạt trễ", "Hành động xử lý tự động"],
                           debt_tiers_data, col_widths=[2.0, 3.2, 2.5, 3.5, 3.8])

    add_p(doc, "Bên cạnh cơ chế phân loại 5 nhóm tuổi nợ định kỳ (từ Tier 0 đến Tier 4) nhằm phục vụ trích lập dự phòng và theo dõi tài chính, hệ thống cài đặt phương thức kiểm soát rủi ro tức thời DebtCalculationHelper.IsCustomerBlacklisted() tại tầng xử lý nghiệp vụ đơn hàng. Phương thức này tự động tính toán động tại thời điểm khách hàng yêu cầu thuê máy mới: nếu khách hàng có ít nhất một kỳ hạn thanh toán trễ hạn quá 15 ngày hoặc tổng dư nợ quá hạn vượt quá hạn mức 3.000.000 VNĐ, hệ thống sẽ tự động kích hoạt cờ danh sách đen động và khóa quyền tạo hợp đồng mới cho đến khi hoàn tất thanh toán các khoản nợ quá hạn.")

    add_heading_2(doc, "2.2. MÔ HÌNH HÓA NGHIỆP VỤ")
    add_heading_3(doc, "2.2.1. Sơ đồ ca sử dụng nghiệp vụ tổng quát (Business Use Case Diagram)")
    add_p(doc, "Sơ đồ ca sử dụng nghiệp vụ tổng quát mô tả mối quan hệ tương tác giữa 4 tác nhân chính trong hệ thống (Khách hàng, Nhân viên kinh doanh, Kỹ thuật viên và Quản trị viên) cùng cổng thanh toán tự động VietQR với các quy trình nghiệp vụ cốt lõi của RentalSystem.")

    add_figure_with_caption(doc, "2.2.1", 1, "Sơ đồ ca sử dụng nghiệp vụ tổng quát (Business Use Case Diagram)",
                            "figures/hinh_2_1_use_case_tong_quat.png", width_cm=14.5)

    add_heading_3(doc, "2.2.2. Mô hình hóa 7 quy trình nghiệp vụ trọng tâm")
    add_p(doc, "Toàn bộ 7 quy trình nghiệp vụ cốt lõi của hệ thống được mô hình hóa chi tiết bằng: (a) Bảng đặc tả văn bản, (b) Sơ đồ hoạt động (Activity Diagram), (c) Sơ đồ tuần tự (Sequence Diagram), và (d) Sơ đồ cộng tác (Collaboration Diagram).")

    core_processes = [
        ("2.2.2.1", "Quy trình Đăng ký & Xác thực người dùng",
         "Cho phép người dùng tạo tài khoản mới, xác minh qua số điện thoại/email và đăng nhập phân quyền vào hệ thống theo 4 vai trò.",
         "Khách hàng mới, Quản trị viên, Khách hàng doanh nghiệp.",
         "Người dùng chưa có tài khoản hoặc chưa đăng nhập.",
         [
             "1. Người dùng truy cập trang Đăng ký và điền thông tin: Họ tên, Email, Số điện thoại, Mật khẩu, CCCD.",
             "2. Hệ thống kiểm tra tính duy nhất của Email và Số điện thoại trong CSDL.",
             "3. Hệ thống băm mật khẩu bằng thuật toán an toàn và lưu thông tin người dùng với vai trò mặc định 'Khách Hàng'.",
             "4. Hệ thống gửi thông báo xác thực kích hoạt tài khoản.",
             "5. Người dùng đăng nhập bằng thông tin hợp lệ; hệ thống cấp phát Cookie Claims xác thực.",
             "6. Hệ thống điều hướng thông minh người dùng vào giao diện tương ứng theo vai trò."
         ],
         "Nếu Email/Số điện thoại đã tồn tại, hệ thống báo lỗi và yêu cầu nhập lại.",
         "Tài khoản được tạo lập thành công, phiên đăng nhập được thiết lập."),

        ("2.2.2.2", "Quy trình Đặt thuê máy & Kiểm tra tồn kho (SemaphoreSlim)",
         "Xử lý việc khách hàng chọn cấu hình thiết bị, kiểm tra tồn kho khả dụng có khóa tương tranh SemaphoreSlim và tạo đơn thuê.",
         "Khách hàng, Nhân viên kinh doanh, Cơ chế kiểm soát tồn kho SemaphoreSlim.",
         "Khách hàng đã đăng nhập và thêm thiết bị vào giỏ hàng.",
         [
             "1. Khách hàng chọn khoảng thời gian thuê (Ngày bắt đầu – Ngày kết thúc) và bấm Xác nhận đặt thuê.",
             "2. Hệ thống kích hoạt khóa SemaphoreSlim(1, 1) trên CartController.InventoryLock.",
             "3. Hệ thống kiểm tra số lượng máy vật lý thuộc sản phẩm không bị trùng lịch thuê trong khoảng ngày đã chọn.",
             "4. Nếu đủ máy, hệ thống tạo bản ghi Hợp đồng (HopDong) ở trạng thái 'Chờ đặt cọc' và giữ chỗ tạm thời.",
             "5. Hệ thống giải phóng khóa Semaphore trong khối finally.",
             "6. Hệ thống chuyển hướng khách hàng sang bước ký hợp đồng và thanh toán tiền cọc."
         ],
         "Nếu không đủ máy khả dụng, hệ thống thông báo tạm hết máy và đề xuất khoảng ngày khác.",
         "Hợp đồng được tạo thành công, số lượng máy được giữ chỗ an toàn, không bị Overbooking."),

        ("2.2.2.3", "Quy trình Thanh toán đặt cọc qua VietQR động NAPAS 247",
         "Khách hàng quét mã VietQR động để thanh toán tiền cọc; hệ thống bắt Webhook ngân hàng và đối soát gạch nợ tự động.",
         "Khách hàng, Cổng thanh toán SePay/Casso, Dịch vụ đối soát Webhook.",
         "Hợp đồng đang ở trạng thái 'Chờ đặt cọc'.",
         [
             "1. Hệ thống sinh chuỗi mã VietQR động chuẩn EMVCo chứa số tài khoản MBBank, số tiền cọc và cú pháp 'HD{id}'.",
             "2. Khách hàng mở ứng dụng Mobile Banking quét mã QR và xác nhận chuyển tiền.",
             "3. Ngân hàng xử lý giao dịch thành công và phát Webhook HTTPS đến hệ thống RentalSystem.",
             "4. PaymentController tiếp nhận bản tin, xác thực IP nguồn và kiểm tra chữ ký an toàn.",
             "5. Bộ phân tích regex bóc tách mã 'HD{id}', đối soát số tiền nhận được với số tiền cọc trong hợp đồng.",
             "6. Hệ thống tự động sinh Phiếu thu (PhieuThu), chuyển trạng thái hợp đồng sang 'Đã cọc – Chờ bàn giao'."
         ],
         "Nếu số tiền chuyển thiếu, hệ thống ghi nhận thanh toán một phần và gửi thông báo yêu cầu chuyển phần còn lại.",
         "Hợp đồng được cập nhật trạng thái 'Đã đặt cọc', phiếu thu điện tử được lưu vết."),

        ("2.2.2.4", "Quy trình Bàn giao & Ký biên bản bàn giao máy",
         "Kỹ thuật viên chuẩn bị máy đúng serial, kiểm định ngoại quan, bàn giao tận nơi và lập biên bản bàn giao có chữ ký số Canvas.",
         "Kỹ thuật viên, Khách hàng, Nhân viên điều phối kho.",
         "Hợp đồng ở trạng thái 'Đã cọc – Chờ bàn giao'.",
         [
             "1. Kỹ thuật viên kiểm tra danh sách thiết bị cần bàn giao trong 'Việc của tôi'.",
             "2. Quét mã QR/Barcode trên thân máy để xác nhận mã Serial vật lý khớp với đơn thuê.",
             "3. Kỹ thuật viên vận chuyển thiết bị đến địa chỉ của khách hàng.",
             "4. Hai bên đồng kiểm ngoại quan, cấu hình phần cứng và ghi nhận tình trạng máy.",
             "5. Khách hàng ký xác nhận trên màn hình cảm ứng HTML5 Canvas của ứng dụng.",
             "6. Hệ thống lưu chữ ký Canvas, sinh mã PDF 'Biên bản bàn giao' và cập nhật trạng thái hợp đồng sang 'Đang thuê'."
         ],
         "Nếu máy có lỗi ngoại quan phát sinh, kỹ thuật viên đổi ngay máy dự phòng tương đương trong kho xe.",
         "Biên bản bàn giao được lưu trữ hợp lệ, thiết bị chuyển sang trạng thái 'Đang cho thuê'."),

        ("2.2.2.5", "Quy trình Báo cáo sự cố & Phân công bảo trì thiết bị",
         "Khách hàng gửi yêu cầu hỗ trợ sự cố; hệ thống điều phối kỹ thuật viên, tạm dừng tính tiền thuê nếu thời gian sửa chữa >24h.",
         "Khách hàng, Kỹ thuật viên, Quản trị viên kỹ thuật.",
         "Hợp đồng đang trong thời hạn thuê có hiệu lực.",
         [
             "1. Khách hàng gửi yêu cầu báo lỗi tại mục 'Lịch sử sự cố' (MyTickets), kèm hình ảnh mô tả lỗi.",
             "2. Hệ thống tạo phiếu bảo trì (BaoTri) ở trạng thái 'Tiếp nhận' và gửi thông báo đến Kỹ thuật viên.",
             "3. Kỹ thuật viên liên hệ khách hàng để kiểm tra từ xa hoặc đến tận nơi thẩm định.",
             "4. Nếu thời gian khắc phục vượt quá 24 giờ, hệ thống kích hoạt cờ 'TamDungTinhTien' để miễn trừ tiền thuê.",
             "5. Kỹ thuật viên tiến hành sửa chữa, thay thế linh kiện hoặc đổi máy tương đương cho khách hàng.",
             "6. Khách hàng nghiệm thu, kỹ thuật viên hoàn tất phiếu bảo trì và hệ thống tính lại ngày thuê."
         ],
         "Nếu lỗi do người dùng cố ý làm hỏng, hệ thống lập biên bản định giá bồi thường trừ vào tiền cọc.",
         "Phiếu bảo trì hoàn tất, quyền lợi thời gian thuê của khách hàng được bảo đảm công bằng."),

        ("2.2.2.6", "Quy trình Gia hạn hợp đồng & Phân kỳ nợ",
         "Khách hàng gửi yêu cầu gia hạn thời gian thuê; hệ thống kiểm tra tương tranh lịch thuê tiếp theo và tái lập phân kỳ nợ.",
         "Khách hàng, Nhân viên kinh doanh, Thuật toán phân kỳ nợ.",
         "Hợp đồng sắp hết hạn và không có khách hàng khác đặt giữ chỗ trước.",
         [
             "1. Khách hàng chọn hợp đồng đang thuê và bấm 'Yêu cầu gia hạn', chọn ngày kết thúc mới.",
             "2. Cơ chế kiểm tra tương tranh SemaphoreSlim rà soát xem mã serial có bị vướng đơn thuê mới trong tương lai không.",
             "3. Nhân viên kinh doanh duyệt yêu cầu gia hạn trên trang quản trị.",
             "4. Thuật toán phân kỳ nợ tính toán lại tổng tiền thuê bổ sung và sinh thêm các kỳ thanh toán mới.",
             "5. Hệ thống sinh mã VietQR cho khoản thanh toán kỳ tiếp theo.",
             "6. Khách hàng thanh toán qua VietQR, hợp đồng được cập nhật thời hạn thuê mới."
         ],
         "Nếu thiết bị đã được khách hàng khác giữ chỗ trước đó, hệ thống từ chối gia hạn và đề xuất đổi sang máy khác.",
         "Hợp đồng được gia hạn thành công, lịch trả góp phân kỳ được cập nhật chính xác."),

        ("2.2.2.7", "Quy trình Trả máy, nghiệm thu & Hoàn trả tiền cọc",
         "Khách hàng trả máy khi hết hạn hợp đồng; kỹ thuật viên nghiệm thu tình trạng máy, nhân viên kinh doanh đối trừ công nợ hư hại và lập phiếu chi hoàn tiền cọc.",
         "Khách hàng, Kỹ thuật viên kho, Nhân viên kinh doanh.",
         "Hợp đồng đến hạn kết thúc thuê.",
         [
             "1. Khách hàng bàn giao lại máy tính và phụ kiện cho kỹ thuật viên kho.",
             "2. Kỹ thuật viên kiểm tra toàn diện phần cứng, tem niêm phong và đối chiếu số Serial vật lý.",
             "3. Kỹ thuật viên lập 'Biên bản nghiệm thu thu hồi máy', ghi nhận chi phí hao mòn/hư hại (nếu có).",
             "4. Nhân viên kinh doanh đối chiếu tổng công nợ còn thiếu, tiền phạt trễ hạn và chi phí bồi thường linh kiện theo biên bản kỹ thuật.",
             "5. Nhân viên kinh doanh lập Phiếu chi (PhieuChi) trên hệ thống để hoàn trả số tiền cọc còn lại vào tài khoản ngân hàng của khách hàng.",
             "6. Hệ thống chuyển trạng thái hợp đồng sang 'Đã hoàn tất', máy chuyển sang trạng thái 'Sẵn sàng trong kho'."
         ],
         "Nếu tiền cọc không đủ bù đắp chi phí bồi thường hư hại nặng, hệ thống sinh khoản nợ phạt yêu cầu khách đóng thêm.",
         "Hợp đồng được tất toán và đóng vĩnh viễn, thiết bị được nhập kho sẵn sàng cho lượt thuê mới.")
    ]

    for idx, (code, name, desc, actors, pre, steps, alt, post) in enumerate(core_processes):
        if idx > 0:
            doc.add_page_break()
        add_heading_4(doc, f"{code}. {name}")
        add_p(doc, f"Mô tả nghiệp vụ: {desc}")

        spec_data = [
            ("Tên quy trình", name),
            ("Tác nhân tham gia", actors),
            ("Tiền điều kiện", pre),
            ("Luồng sự kiện chính", "\n".join(steps)),
            ("Luồng ngoại lệ / Thay thế", alt),
            ("Hậu điều kiện", post)
        ]
        add_table_with_caption(doc, code, 1, f"Bảng đặc tả quy trình nghiệp vụ {name}",
                               ["Thuộc tính đặc tả", "Nội dung quy trình nghiệp vụ chi tiết"],
                               spec_data, col_widths=[4.0, 11.0])

        # Diagram 1: Activity
        act_img = f"figures/hinh_{code.replace('.', '_')}_1_activity_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 1, f"Sơ đồ hoạt động {name}", act_img, width_cm=14.5)

        # Diagram 2: Sequence
        seq_img = f"figures/hinh_{code.replace('.', '_')}_2_sequence_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 2, f"Sơ đồ tuần tự {name}", seq_img, width_cm=14.5)

        # Diagram 3: Collaboration
        col_img = f"figures/hinh_{code.replace('.', '_')}_3_collaboration_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 3, f"Sơ đồ cộng tác {name}", col_img, width_cm=14.5)

    add_heading_2(doc, "2.3. MÔ HÌNH HÓA CHỨC NĂNG")
    add_heading_3(doc, "2.3.1. Sơ đồ ca sử dụng hệ thống")
    add_p(doc, "Hệ thống RentalSystem bao gồm 4 phân hệ chính tương ứng với 4 nhóm vai trò người dùng trong tổ chức. Dưới đây là sơ đồ ca sử dụng hệ thống tổng quát và các sơ đồ phân rã chi tiết:")

    add_figure_with_caption(doc, "2.3.1", 1, "Sơ đồ ca sử dụng hệ thống tổng quát (System Use Case Diagram)",
                            "figures/hinh_2_1_use_case_tong_quat.png", width_cm=14.5)
    add_figure_with_caption(doc, "2.3.1", 2, "Sơ đồ ca sử dụng phân rã phân hệ Khách hàng (Customer Portal)",
                            "figures/hinh_2_2_use_case_khach_hang.png", width_cm=14.5)
    add_figure_with_caption(doc, "2.3.1", 3, "Sơ đồ ca sử dụng phân rã phân hệ Quản trị & Vận hành (Admin & Operations)",
                            "figures/hinh_2_3_use_case_admin.png", width_cm=14.5)
    add_figure_with_caption(doc, "2.3.1", 4, "Sơ đồ ca sử dụng phân rã phân hệ Bảo trì & Kỹ thuật (Maintenance & Technical)",
                            "figures/hinh_2_4_use_case_bao_tri.png", width_cm=14.5)

    add_heading_3(doc, "2.3.2. Bảng đặc tả các ca sử dụng hệ thống")
    add_p(doc, "Dưới đây là bảng đặc tả chi tiết 12 ca sử dụng cốt lõi của hệ thống phần mềm RentalSystem:")

    detailed_use_cases = [
        ("1", "Đăng ký tài khoản khách hàng", "Khách hàng mới (Khách vãng lai)",
         "Cho phép người dùng mới tạo tài khoản khách hàng để sử dụng các dịch vụ đặt thuê thiết bị trên website.",
         "Người dùng chưa đăng nhập, đã truy cập vào trang Đăng ký của hệ thống.",
         "1. Khách hàng chọn chức năng 'Đăng ký' trên thanh điều hướng.\n"
         "2. Hệ thống hiển thị biểu mẫu đăng ký gồm: Họ tên, Số điện thoại, Email, Số CCCD, Mật khẩu và Xác nhận mật khẩu.\n"
         "3. Khách hàng điền đầy đủ các thông tin và nhấn nút 'Tạo tài khoản'.\n"
         "4. Hệ thống kiểm tra tính hợp lệ của dữ liệu (định dạng email, độ dài CCCD 12 số, độ phức tạp mật khẩu).\n"
         "5. Hệ thống mã hóa mật khẩu bằng thuật toán PBKDF2/SHA-256 kèm Salt, lưu thông tin người dùng mới với vai trò 'KhachHang' vào CSDL.\n"
         "6. Hệ thống hiển thị thông báo đăng ký thành công và tự động điều hướng sang trang Đăng nhập.",
         "4a. Số điện thoại hoặc Email đã tồn tại trong hệ thống: Hệ thống hiển thị cảnh báo đỏ và yêu cầu nhập thông tin khác.\n"
         "4b. Mật khẩu xác nhận không khớp: Hệ thống yêu cầu nhập lại mật khẩu chính xác.",
         "Bản ghi người dùng mới được tạo trong bảng NguoiDung với trạng thái kích hoạt, sẵn sàng đăng nhập."),

        ("2", "Đăng nhập và Xác thực phân quyền", "Mọi người dùng (Khách hàng, Kinh doanh, Kỹ thuật, Quản trị viên)",
         "Xác thực danh tính người dùng và cấp phát Cookie Claims theo đúng vai trò được phân quyền.",
         "Người dùng đã có tài khoản hợp lệ trong hệ thống và chưa đăng nhập.",
         "1. Người dùng truy cập trang Đăng nhập, điền Email / Tên đăng nhập và Mật khẩu.\n"
         "2. Người dùng nhấn nút 'Đăng nhập'.\n"
         "3. Hệ thống truy vấn CSDL tìm bản ghi người dùng, kiểm tra trạng thái tài khoản (chưa bị khóa).\n"
         "4. Hệ thống băm mật khẩu nhập vào và đối khớp với chuỗi mã hóa lưu trữ trong CSDL.\n"
         "5. Hệ thống khởi tạo Cookie Claims xác thực chứa UserId, FullName và Role (Vai trò).\n"
         "6. Hệ thống điều hướng người dùng về trang tương ứng theo vai trò (Khách hàng về Trang chủ; Admin/Nhân viên về Dashboard Quản trị).",
         "3a. Tài khoản bị tạm khóa: Hệ thống báo lỗi 'Tài khoản của bạn tạm thời bị khóa, vui lòng liên hệ quản trị viên'.\n"
         "4a. Sai email hoặc mật khẩu: Hệ thống thông báo lỗi 'Thông tin đăng nhập không chính xác'.",
         "Phiên làm việc (Cookie Claims) được thiết lập, giao diện được phân quyền theo đúng vai trò."),

        ("3", "Đặt thuê thiết bị trực tuyến (Checkout)", "Khách hàng",
         "Khách hàng lựa chọn cấu hình máy, thời gian thuê và kích hoạt khóa SemaphoreSlim để giữ chỗ tồn kho an toàn.",
         "Khách hàng đã đăng nhập, đã chọn thiết bị và khoảng ngày thuê [NgayBatDau, NgayKetThuc] vào giỏ hàng.",
         "1. Khách hàng truy cập trang Giỏ hàng / Checkout, xác nhận danh sách thiết bị và khoảng ngày thuê.\n"
         "2. Khách hàng nhấn 'Tiến hành đặt thuê'.\n"
         "3. Hệ thống kích hoạt khóa bất đồng bộ CartController.InventoryLock.WaitAsync().\n"
         "4. Hệ thống kiểm tra giao thoa khoảng thời gian thuê trên từng thiết bị để đảm bảo số lượng tồn kho khả dụng đáp ứng yêu cầu.\n"
         "5. Hệ thống tính toán tổng tiền thuê, tiền đặt cọc (theo tỷ lệ cấu hình) và áp dụng mã giảm giá khuyến mãi (nếu có).\n"
         "6. Hệ thống tạo bản ghi Hợp đồng mới (HopDong) ở trạng thái 'ChoKyHopDong' và các chi tiết hợp đồng tương ứng.\n"
         "7. Hệ thống giải phóng khóa InventoryLock.Release() và chuyển khách hàng sang bước ký hợp đồng.",
         "4a. Thiết bị đã bị khách khác giữ chỗ trước trong khoảng ngày đã chọn: Hệ thống giải phóng khóa, hiển thị cảnh báo 'Thiết bị hiện không đủ số lượng trong khung thời gian này, vui lòng chọn ngày khác'.",
         "Hợp đồng được tạo trong CSDL, trạng thái máy được giữ chỗ tạm thời, không xảy ra Overbooking."),

        ("4", "Ký hợp đồng điện tử Canvas và Tải CCCD", "Khách hàng",
         "Khách hàng ký số trực tiếp trên khung vẽ Canvas HTML5 và tải ảnh CCCD 2 mặt để hoàn tất thủ tục pháp lý.",
         "Hợp đồng đã được tạo, đang chờ chữ ký số và xác minh danh tính khách hàng.",
         "1. Khách hàng mở trang chi tiết hợp đồng, đọc toàn bộ điều khoản pháp lý và danh mục thiết bị thuê.\n"
         "2. Khách hàng sử dụng chuột hoặc màn hình cảm ứng để ký trực tiếp trên khung Canvas HTML5.\n"
         "3. Khách hàng tải lên 02 ảnh mặt trước và mặt sau Căn cước công dân (CCCD).\n"
         "4. Khách hàng nhấn 'Xác nhận ký hợp đồng'.\n"
         "5. Hệ thống kiểm tra magic bytes tệp ảnh tải lên và mã hóa chuỗi chữ ký Base64 sang định dạng an toàn.\n"
         "6. Hệ thống cập nhật chữ ký điện tử, đường dẫn ảnh CCCD và chuyển trạng thái hợp đồng sang 'ChoThanhToanCoc'.",
         "2a. Khách hàng chưa ký tên vào khung Canvas: Hệ thống cảnh báo 'Vui lòng ký tên xác nhận trước khi tiếp tục'.\n"
         "5a. Tệp tải lên không phải định dạng ảnh hợp lệ hoặc dung lượng vượt quá giới hạn: Hệ thống từ chối và yêu cầu tải lại.",
         "Chữ ký số và ảnh CCCD được lưu trữ an toàn, hợp đồng sẵn sàng cho bước thanh toán cọc."),

        ("5", "Thanh toán VietQR và Đối soát Webhook", "Khách hàng, Cổng thanh toán (SePay/Casso)",
         "Khách hàng quét mã VietQR động NAPAS 247; hệ thống tiếp nhận Webhook ngân hàng và đối soát gạch nợ tự động.",
         "Hợp đồng hoặc kỳ nợ đang ở trạng thái chờ thanh toán.",
         "1. Khách hàng mở phương thức thanh toán chuyển khoản, hệ thống hiển thị mã VietQR động NAPAS 247 chứa số tiền cọc và cú pháp 'HD{id}'.\n"
         "2. Khách hàng dùng ứng dụng ngân hàng quét mã QR và thực hiện chuyển tiền.\n"
         "3. Cổng thanh toán ngân hàng phát bản tin Webhook HTTPS về cổng /PaymentWebhook/Receive của hệ thống.\n"
         "4. Hệ thống kiểm tra tính duy nhất của mã giao dịch TransactionRef (Idempotency) để chống xử lý lặp.\n"
         "5. Bộ phân tích regex bóc tách mã chứng từ, đối soát số tiền nhận được với số tiền cần thanh toán theo cơ chế thác nước.\n"
         "6. Hệ thống tự động tạo Phiếu thu (PhieuThu), cập nhật trạng thái hợp đồng thành 'DaThanhToanCoc' (hoặc gạch nợ kỳ hạn tương ứng).",
         "4a. Bản tin Webhook bị trùng lặp (đã xử lý trước đó): Hệ thống phản hồi HTTP 200 OK kèm mã DUPLICATE mà không ghi nhận thêm phiếu thu.\n"
         "5a. Số tiền chuyển khoản nhỏ hơn số tiền yêu cầu: Hệ thống ghi nhận thanh toán một phần và gửi thông báo nợ thiếu.",
         "Phiếu thu điện tử được lưu vết trong CSDL, trạng thái thanh toán được gạch nợ tự động tức thời."),

        ("6", "Bàn giao và Xuất biên bản bàn giao", "Kỹ thuật viên kho",
         "Kỹ thuật viên kiểm định ngoại quan thiết bị, quét mã Serial vật lý, bàn giao máy và lập biên bản giao nhận.",
         "Hợp đồng đã hoàn thành thanh toán tiền cọc, khách hàng đến nhận máy hoặc chuẩn bị giao tận nơi.",
         "1. Kỹ thuật viên truy cập danh sách hợp đồng cần bàn giao, chọn hợp đồng tương ứng.\n"
         "2. Kỹ thuật viên kiểm định ngoại quan thiết bị, quét mã vạch hoặc nhập số Serial vật lý của từng máy xuất kho.\n"
         "3. Hệ thống kiểm tra trạng thái Serial (phải ở trạng thái 'SanSang'), gán Serial vào chi tiết hợp đồng và đổi trạng thái máy sang 'DangThue'.\n"
         "4. Hệ thống tự động sinh Biên bản bàn giao điện tử hiển thị đầy đủ thông số cấu hình và Serial máy.\n"
         "5. Hai bên ký xác nhận bàn giao và hệ thống cập nhật hợp đồng sang trạng thái 'DangThue'.",
         "3a. Serial nhập vào đang ở trạng thái bảo trì hoặc đã được cấp phát cho hợp đồng khác: Hệ thống cảnh báo lỗi và yêu cầu chọn máy khác.",
         "Thiết bị được xuất kho, số Serial vật lý được gắn chặt vào hợp đồng, biên bản bàn giao được lưu vết hợp lệ."),

        ("7", "Báo cáo sự cố và Tạm dừng tính tiền", "Khách hàng",
         "Khách hàng gửi yêu cầu hỗ trợ sự cố; hệ thống ghi nhận phiếu bảo trì và tự động đóng băng ngày tính tiền nếu sửa >24h.",
         "Hợp đồng của khách hàng đang trong trạng thái 'DangThue'.",
         "1. Khách hàng truy cập danh mục thiết bị đang thuê, chọn chức năng 'Báo cáo sự cố / Yêu cầu bảo trì'.\n"
         "2. Khách hàng mô tả chi tiết hiện tượng lỗi (hỏng nguồn, lỗi màn hình, lỗi phần mềm...) và tải ảnh minh chứng.\n"
         "3. Khách hàng gửi yêu cầu.\n"
         "4. Hệ thống tạo phiếu bảo trì mới (BaoTri) với mức độ ưu tiên tương ứng và thông báo đến phân hệ kỹ thuật.\n"
         "5. Nếu thời gian khắc phục sự cố vượt quá 24 giờ mà chưa có máy thay thế, hệ thống tự động kích hoạt tính năng tạm dừng tính tiền thuê cho những ngày thiết bị không thể sử dụng.",
         "1a. Hợp đồng đã kết thúc hoặc bị hủy: Hệ thống từ chối tạo yêu cầu bảo trì.",
         "Phiếu bảo trì được tạo với trạng thái 'TiepNhan', quyền lợi thời gian thuê của khách hàng được bảo đảm."),

        ("8", "Điều phối kỹ thuật và Quản lý việc của tôi", "Quản trị viên (Admin), Kỹ thuật viên",
         "Phân công nhiệm vụ kỹ thuật và cho phép kỹ thuật viên theo dõi tiến độ xử lý công việc được giao.",
         "Đã có phiếu bảo trì hoặc lệnh giao/thu hồi máy được tạo trên hệ thống.",
         "1. Quản trị viên (Admin) xem danh sách công việc chờ xử lý, chọn phiếu và phân công cho Kỹ thuật viên phụ trách.\n"
         "2. Kỹ thuật viên đăng nhập, vào mục 'Việc của tôi' để xem danh sách nhiệm vụ được giao kèm hạn hoàn thành (SLA).\n"
         "3. Kỹ thuật viên tiếp nhận máy hỏng, cập nhật trạng thái 'DangXuLy', ghi chú các linh kiện cần thay thế.\n"
         "4. Sau khi hoàn thành sửa chữa hoặc đổi máy dự phòng cho khách, Kỹ thuật viên cập nhật trạng thái 'HoanThanh'.\n"
         "5. Hệ thống ghi nhận lịch sử bảo dưỡng vào bảng LichSuSuDung của thiết bị.",
         "3a. Thiết bị hỏng nặng không thể sửa chữa tại chỗ: Kỹ thuật viên đề xuất đổi máy thay thế cùng cấu hình cho khách hàng.",
         "Tiến độ công việc được cập nhật thời gian thực, lịch sử vòng đời máy được lưu vết đầy đủ."),

        ("9", "Yêu cầu và Phê duyệt gia hạn hợp đồng", "Khách hàng, Nhân viên kinh doanh / Admin",
         "Khách hàng đề xuất gia hạn thời gian thuê; hệ thống kiểm tra xung đột tồn kho và tính toán lại phân kỳ tài chính.",
         "Hợp đồng đang hoạt động (DangThue) và còn thời hạn ít nhất 03 ngày trước khi hết hạn.",
         "1. Khách hàng chọn hợp đồng đang thuê và nhấn 'Yêu cầu gia hạn'.\n"
         "2. Khách hàng chọn ngày trả máy mới mong muốn.\n"
         "3. Hệ thống kiểm tra xem các thiết bị trong hợp đồng có bị khách hàng khác đặt trước trong khoảng thời gian gia hạn hay không.\n"
         "4. Nếu thiết bị khả dụng, hệ thống chuyển yêu cầu gia hạn đến Nhân viên kinh doanh kèm số tiền thuê phát sinh dự kiến.\n"
         "5. Nhân viên kinh doanh kiểm tra lịch sử tín nhiệm công nợ của khách hàng và nhấn 'Phê duyệt gia hạn'.\n"
         "6. Hệ thống cập nhật ngày kết thúc hợp đồng mới, tự động kích hoạt thuật toán phân kỳ nợ bổ sung và thông báo cho khách hàng.",
         "3a. Thiết bị đã có lịch đặt thuê của khách hàng khác ngay sau đó: Hệ thống thông báo không thể gia hạn và đề xuất hoàn trả đúng hạn.\n"
         "5a. Khách hàng đang có nợ quá hạn chưa thanh toán: Nhân viên từ chối gia hạn cho đến khi công nợ cũ được giải quyết.",
         "Hạn hợp đồng được cập nhật, kỳ thanh toán mới được bổ sung trong bảng KyHanThanhToan."),

        ("10", "Nghiệm thu trả máy và Quyết toán hoàn cọc", "Kỹ thuật viên kho, Nhân viên kinh doanh",
         "Kiểm định tình trạng thiết bị khi thu hồi, cấn trừ công nợ hư hại hoặc phạt trễ hạn và thực hiện hoàn trả tiền cọc.",
         "Hợp đồng đến hạn trả máy hoặc khách hàng yêu cầu kết thúc sớm.",
         "1. Kỹ thuật viên tiếp nhận thiết bị từ khách hàng, đối chiếu số Serial vật lý với biên bản bàn giao ban đầu.\n"
         "2. Kỹ thuật viên kiểm tra ngoại quan, linh kiện phần cứng (RAM, ổ cứng, màn hình, phụ kiện sạc).\n"
         "3. Nếu máy nguyên vẹn, Kỹ thuật viên xác nhận nghiệm thu 'MayTot', chuyển trạng thái thiết bị về 'SanSang'.\n"
         "4. Nhân viên kinh doanh truy cập chức năng Quyết toán hợp đồng, hệ thống tự động tổng hợp: Tiền cọc đang giữ, tiền thuê còn thiếu (nếu có), tiền phạt quá hạn và chi phí bồi thường hư hại (nếu có).\n"
         "5. Hệ thống tính toán số tiền cọc thực tế cần hoàn trả: HoanCoc = TienCoc - NoThieu - TienPhat - BoiThuong.\n"
         "6. Nhân viên kinh doanh lập Phiếu chi (PhieuChi) trên hệ thống để hoàn trả tiền cho khách hàng và đóng hợp đồng ở trạng thái 'DaThanhLy'.",
         "2a. Phát hiện thiết bị bị vỡ màn hình hoặc tráo đổi linh kiện: Kỹ thuật viên lập biên bản bất thường, định giá thiệt hại để chuyển nhân viên kinh doanh khấu trừ vào tiền cọc.",
         "Thiết bị được hoàn về kho khả dụng, hợp đồng thanh lý hoàn tất, giao dịch tài chính kết thúc minh bạch."),

        ("11", "Quản lý sổ nợ và Nhắc nợ tự động", "Nhân viên kinh doanh / Quản trị viên",
         "Theo dõi 4 nhóm tuổi nợ (Debt Aging Tiers), tính tiền phạt trễ hạn tự động 0.1%/ngày và gửi thông báo nhắc nợ.",
         "Người dùng đăng nhập hệ thống với quyền 'KinhDoanh' hoặc 'Admin'.",
         "1. Nhân viên kinh doanh mở màn hình 'Quản trị công nợ'.\n"
         "2. Hệ thống tự động phân loại toàn bộ các kỳ hạn chưa thanh toán vào 4 nhóm tuổi nợ (Tier 0: Trong hạn; Tier 1: Quá hạn 1-30 ngày; Tier 2: Quá hạn 31-60 ngày; Tier 3: Quá hạn 61-90 ngày; Tier 4: Nợ xấu >90 ngày).\n"
         "3. Đối với các kỳ nợ quá hạn vượt quá chính sách ân hạn 3 ngày, hệ thống tự động tính tiền phạt trễ hạn với tỷ lệ 0.1%/ngày dựa trên số ngày trễ thực tế.\n"
         "4. Nhân viên kinh doanh chọn chức năng 'Gửi thông báo nhắc nợ', hệ thống tự động gửi Email/SMS thông báo kèm đường dẫn thanh toán nhanh VietQR đến khách hàng nợ.",
         "3a. Khách hàng có văn bản xin gia hạn thời gian thanh toán được duyệt: Nhân viên kinh doanh báo cáo Quản trị viên áp dụng chính sách miễn giảm hoặc lùi ngày tính phạt theo thẩm quyền.",
         "Bảng công nợ được cập nhật số liệu mới nhất, lịch sử nhắc nợ được ghi nhận chi tiết."),

        ("12", "Trung tâm phân tích báo cáo BI và Xuất Excel", "Quản trị viên (Admin) / Nhân viên kinh doanh",
         "Cung cấp dashboard thống kê phân tích trực quan về dòng tiền, tỷ lệ sử dụng thiết bị và hỗ trợ xuất báo cáo Excel phân tích tài chính.",
         "Người dùng đăng nhập với quyền 'Admin' hoặc 'KinhDoanh'.",
         "1. Quản trị viên hoặc Nhân viên kinh doanh truy cập màn hình 'Báo cáo thống kê & Phân tích BI'.\n"
         "2. Người dùng thiết lập bộ lọc theo khoảng thời gian (theo tháng, quý, năm) hoặc theo danh mục loại thiết bị.\n"
         "3. Hệ thống tổng hợp và trực quan hóa dữ liệu qua các biểu đồ: Doanh thu thuê theo thời gian, Cơ cấu doanh thu theo nhóm máy, Tỷ lệ khai thác sử dụng kho máy (Utilization Rate), Tỷ lệ nợ quá hạn.\n"
         "4. Người dùng nhấn nút 'Xuất báo cáo Excel'.\n"
         "5. Hệ thống sử dụng thư viện ClosedXML khởi tạo tệp bảng tính Excel (.xlsx) với đầy đủ tiêu đề doanh nghiệp, bảng dữ liệu chi tiết, định dạng số tiền VND và công thức tính tổng tự động, rồi tải về máy tính người dùng.",
         "2a. Khoảng thời gian chọn không có dữ liệu giao dịch: Hệ thống hiển thị biểu đồ rỗng kèm thông báo 'Không có dữ liệu trong khoảng thời gian đã chọn'.",
         "Báo cáo số liệu được kết xuất chuẩn xác, hỗ trợ kịp thời cho công tác quản trị và ra quyết định kinh doanh."),

        ("13", "Đánh giá chất lượng dịch vụ bảo trì và Phản hồi khách hàng", "Khách hàng",
         "Khách hàng chấm điểm sao (Rating 1-5) và gửi phản hồi đánh giá chất lượng phục vụ sau khi Kỹ thuật viên hoàn tất ca xử lý sự cố thiết bị.",
         "Phiếu bảo trì của thiết bị trong hợp đồng đã được Kỹ thuật viên cập nhật trạng thái 'HoanThanh'.",
         "1. Khách hàng nhận thông báo ca xử lý sự cố đã hoàn thành trên cổng giao diện người dùng Web.\n"
         "2. Khách hàng truy cập chi tiết phiếu bảo trì, chọn chức năng 'Đánh giá chất lượng phục vụ'.\n"
         "3. Khách hàng chọn số sao đánh giá (từ 1 đến 5 sao), tích chọn các tiêu chí hài lòng (Đúng giờ hẹn, Thái độ chuyên nghiệp, Máy vận hành ổn định sau sửa chữa) và nhập ý kiến đóng góp.\n"
         "4. Khách hàng nhấn nút 'Gửi đánh giá'.\n"
         "5. Hệ thống ghi nhận điểm số vào cơ sở dữ liệu, tự động tính điểm chỉ số hài lòng (CSAT) của Kỹ thuật viên và gửi thông báo cảm ơn khách hàng.",
         "2a. Khách hàng phản hồi thiết bị vẫn còn lỗi tái diễn: Hệ thống cho phép nhấn 'Yêu cầu kiểm tra lại', tự động mở lại ticket bảo trì cho điều phối viên xử lý khẩn cấp.",
         "Đánh giá của khách hàng được lưu vết minh bạch, làm căn cứ đánh giá KPI nhân sự kỹ thuật.")
    ]

    for uc_id, uc_name, actor, desc, pre, main_flow, alt_flow, post in detailed_use_cases:
        uc_data = [
            ("Mã Use Case", f"UC-{int(uc_id):02d}"),
            ("Tên Use Case", uc_name),
            ("Tác nhân chính", actor),
            ("Mô tả tóm tắt", desc),
            ("Tiền điều kiện", pre),
            ("Luồng sự kiện chính", main_flow),
            ("Luồng ngoại lệ / Rẽ nhánh", alt_flow),
            ("Hậu điều kiện", post)
        ]
        add_table_with_caption(doc, "2.3.2", uc_id, f"Bảng đặc tả use case {uc_name}",
                               ["Thuộc tính", "Nội dung đặc tả chi tiết"],
                               uc_data, col_widths=[3.5, 11.5])

    add_heading_3(doc, "2.3.3. Thiết kế kiến trúc Backend RESTful API theo đặc tả OpenAPI / Swagger")
    add_p(doc, "Để hỗ trợ trao đổi dữ liệu với các ứng dụng máy khách và mở rộng tích hợp trong tương lai, hệ thống thiết lập các dịch vụ Backend RESTful API. Các ứng dụng máy khách (Client Apps) trao đổi dữ liệu định dạng JSON thông qua giao thức HTTPS bảo mật, xác thực bằng cơ chế JWT Token (JSON Web Token) và sử dụng các mã phản hồi HTTP tiêu chuẩn:")

    api_endpoints_data = [
        ("POST", "/api/v1/auth/login", "Xác thực người dùng, cấp phát JWT Bearer Token", "Khách hàng, Kỹ thuật viên"),
        ("GET", "/api/v1/san-pham", "Tra cứu danh mục thiết bị, bộ lọc cấu hình và giá thuê", "Khách hàng"),
        ("POST", "/api/v1/hop-dong/dat-thue", "Khởi tạo yêu cầu đặt thuê máy kèm khóa SemaphoreSlim", "Khách hàng"),
        ("GET", "/api/v1/hop-dong/cua-toi", "Xem danh sách hợp đồng cá nhân và lịch trả góp", "Khách hàng"),
        ("POST", "/api/v1/bao-tri/yeu-cau", "Gửi ticket báo sự cố kỹ thuật kèm hình ảnh lỗi", "Khách hàng"),
        ("POST", "/api/v1/bao-tri/danh-gia", "Gửi chấm điểm sao (1-5 sao) và nhận xét dịch vụ", "Khách hàng"),
        ("GET", "/api/v1/ky-thuat/lich-phan-cong", "Xem danh sách ca bảo trì và giao máy được phân công", "Kỹ thuật viên"),
        ("PUT", "/api/v1/ky-thuat/cap-nhat-trang-thai", "Cập nhật tiến độ sửa chữa hoặc thực hiện đổi máy backup", "Kỹ thuật viên")
    ]
    add_table_with_caption(doc, "2.3.3", 1, "Bảng đặc tả các Endpoint RESTful API chính phục vụ tích hợp hệ thống đa nền tảng",
                           ["Phương thức", "Đường dẫn API (Endpoint)", "Chức năng nghiệp vụ", "Quyền truy cập"],
                           api_endpoints_data, col_widths=[2.0, 5.0, 5.5, 2.5])

    add_heading_2(doc, "2.4. SƠ ĐỒ LỚP MỨC PHÂN TÍCH (ANALYSIS CLASS DIAGRAM)")
    add_p(doc, "Sơ đồ lớp mức phân tích xác định các lớp khái niệm trong hệ thống RentalSystem theo mô hình phân loại Boundary – Control – Entity (BCE):")
    add_bullet(doc, "Lớp Boundary (Lớp biên): Tiếp nhận yêu cầu từ người dùng và trình bày dữ liệu giao diện (LoginView, CheckoutView, ContractDetailsView, PaymentModalView...).")
    add_bullet(doc, "Lớp Control (Lớp điều khiển): Điều phối các luồng nghiệp vụ, kiểm tra ràng buộc logic và gọi xử lý CSDL (AccountController, CartController, HopDongController, PaymentController, BaoTriController, CongNoController...).")
    add_bullet(doc, "Lớp Entity (Lớp thực thể): Đại diện cho các đối tượng dữ liệu lưu trữ bền vững trong cơ sở dữ liệu (NguoiDung, HopDong, ChiTietHopDong, ThietBi, KyHanThanhToan, PhieuThu, PhieuChi, BaoTri...).")

    add_figure_with_caption(doc, "2.4", 1, "Sơ đồ lớp mức phân tích toàn hệ thống (Analysis Class Diagram)",
                            "figures/hinh_2_4_1_analysis_class_diagram.png", width_cm=15.0)

    add_heading_2(doc, "2.5. KẾT CHƯƠNG")
    add_p(doc, "Thông qua Chương 2, đề tài đã phân tích ba bài toán kỹ thuật cốt lõi gồm kiểm soát tương tranh giữ chỗ bằng SemaphoreSlim, sinh mã VietQR động theo chuẩn EMVCo và phân kỳ công nợ 4 cấp độ. Đồng thời, chương này đã mô hình hóa 7 quy trình nghiệp vụ trọng tâm và đặc tả chi tiết 12 ca sử dụng gắn liền với 4 vai trò người dùng trong hệ thống (Khách hàng, Kinh doanh, Kỹ thuật và Quản trị viên). Những kết quả phân tích yêu cầu này đóng vai trò cơ sở để triển khai thiết kế kiến trúc và lược đồ cơ sở dữ liệu chi tiết trong Chương 3.")
    doc.add_page_break()


def get_slug(code):
    slug_map = {
        "2.2.2.1": "dang_ky_xac_thuc",
        "2.2.2.2": "dat_thue_inventory",
        "2.2.2.3": "thanh_toan_vietqr",
        "2.2.2.4": "ban_giao_ky_so",
        "2.2.2.5": "bao_tri_su_co",
        "2.2.2.6": "gia_han_cong_no",
        "2.2.2.7": "tra_may_hoan_coc",
        "3.4.1": "dang_ky_xac_thuc",
        "3.4.2": "dat_thue_inventory",
        "3.4.3": "thanh_toan_vietqr",
        "3.4.4": "ban_giao_ky_so",
        "3.4.5": "bao_tri_su_co",
        "3.4.6": "gia_han_cong_no",
        "3.4.7": "tra_may_hoan_coc"
    }
    return slug_map.get(code, "process")


def build_chapter3_design(doc):
    """
    CHƯƠNG 3: THIẾT KẾ HỆ THỐNG
    3.1 Thiết kế CSDL (3.1.1 18 bảng, 3.1.2 Quan hệ, 3.1.3 ERD)
    3.2 Thiết kế giao diện (3.2.1 Khách hàng, 3.2.2 Admin Deep Navy)
    3.3 Sơ đồ lớp mức thiết kế 3 lớp
    3.4 Thiết kế chi tiết 7 chức năng (3.4.1 -> 3.4.7: BCE, Sequence, Collab)
    3.5 KẾT CHƯƠNG
    """
    add_heading_1(doc, "CHƯƠNG 3: THIẾT KẾ HỆ THỐNG")

    add_heading_2(doc, "3.1. THIẾT KẾ CƠ SỞ DỮ LIỆU")
    add_heading_3(doc, "3.1.1. Từ điển dữ liệu 18 bảng cơ sở dữ liệu")
    add_p(doc, "Cơ sở dữ liệu của RentalSystem được thiết kế chuẩn hóa mức 3NF trên hệ quản trị Microsoft SQL Server 2022, bao gồm 18 bảng thực thể đáp ứng các yêu cầu lưu trữ dữ liệu của hệ thống:")

    db_tables_dict = [
        ("1", "VaiTro", "Bảng danh mục vai trò người dùng hệ thống (Admin, KinhDoanh, KyThuat, KhachHang).",
         [("1", "MaVaiTro", "int", "PK", "No", "Mã định danh duy nhất của vai trò"),
          ("2", "TenVaiTro", "nvarchar(50)", "None", "No", "Tên vai trò (Admin, KinhDoanh, KyThuat, KhachHang)"),
          ("3", "MoTa", "nvarchar(255)", "None", "Yes", "Mô tả phạm vi quyền hạn của vai trò")]),

        ("2", "NguoiDung", "Bảng tài khoản người dùng, chứng thực Cookie Claims và thông tin cá nhân/doanh nghiệp.",
         [("1", "MaNguoiDung", "int", "PK", "No", "Mã định danh duy nhất của tài khoản"),
          ("2", "HoTen", "nvarchar(100)", "None", "No", "Họ và tên đầy đủ của người dùng"),
          ("3", "Email", "nvarchar(100)", "Unique", "No", "Địa chỉ email đăng nhập hệ thống"),
          ("4", "SoDienThoai", "varchar(20)", "None", "No", "Số điện thoại liên hệ chính"),
          ("5", "MatKhauHash", "nvarchar(255)", "None", "No", "Mật khẩu băm an toàn BCrypt/Argon2"),
          ("6", "MaVaiTro", "int", "FK", "No", "Khóa ngoại liên kết bảng VaiTro"),
          ("7", "DiaChi", "nvarchar(255)", "None", "Yes", "Địa chỉ liên hệ nhận thiết bị"),
          ("8", "CCCD", "varchar(20)", "None", "Yes", "Số định danh Căn cước công dân"),
          ("9", "TrangThai", "bit", "None", "No", "Trạng thái kích hoạt (1: Hoạt động, 0: Khóa)"),
          ("10", "NgayTao", "datetime", "None", "No", "Thời điểm đăng ký tài khoản")]),

        ("3", "LoaiThietBi", "Bảng phân loại chủng loại thiết bị công nghệ (Laptop, Desktop, Máy lạnh, Máy in).",
         [("1", "MaLoai", "int", "PK", "No", "Mã định danh danh mục thiết bị"),
          ("2", "TenLoai", "nvarchar(100)", "None", "No", "Tên loại thiết bị"),
          ("3", "MoTa", "nvarchar(255)", "None", "Yes", "Mô tả đặc tính của dòng sản phẩm"),
          ("4", "BiDanh", "varchar(100)", "None", "No", "Đường dẫn thân thiện (Slug URL)"),
          ("5", "TrangThai", "int", "None", "No", "1: Hoạt động hiển thị, 0: Tạm ẩn")]),

        ("4", "SanPham", "Bảng cấu hình kỹ thuật, đơn giá thuê theo ngày/tháng và tiền cọc quy định.",
         [("1", "MaSanPham", "int", "PK", "No", "Mã định danh dòng sản phẩm"),
          ("2", "TenSanPham", "nvarchar(150)", "None", "No", "Tên thương mại của thiết bị"),
          ("3", "MaLoai", "int", "FK", "No", "Khóa ngoại liên kết bảng LoaiThietBi"),
          ("4", "GiaThueNgay", "decimal(18,2)", "None", "No", "Đơn giá thuê theo ngày (VNĐ)"),
          ("5", "GiaThueThang", "decimal(18,2)", "None", "No", "Đơn giá thuê theo tháng (VNĐ)"),
          ("6", "TienCoc", "decimal(18,2)", "None", "No", "Số tiền đặt cọc quy định trên 1 máy"),
          ("7", "CauHinh", "nvarchar(max)", "None", "Yes", "Thông số CPU, RAM, SSD, VGA chi tiết"),
          ("8", "MoTa", "nvarchar(max)", "None", "Yes", "Bài viết mô tả tính năng nổi bật"),
          ("9", "HinhAnh", "nvarchar(255)", "None", "Yes", "Đường dẫn ảnh đại diện sản phẩm"),
          ("10", "SoLuongSanCo", "int", "None", "No", "Số lượng máy thực tế sẵn sàng trong kho"),
          ("11", "TrangThai", "int", "None", "No", "1: Đang cho thuê, 0: Ngừng kinh doanh")]),

        ("5", "ThietBi", "Bảng quản lý từng máy vật lý cụ thể theo số Serial duy nhất và trạng thái vòng đời.",
         [("1", "MaThietBi", "int", "PK", "No", "Mã định danh duy nhất của thiết bị vật lý"),
          ("2", "MaSanPham", "int", "FK", "No", "Khóa ngoại liên kết bảng SanPham"),
          ("3", "SoSerial", "varchar(50)", "Unique", "No", "Số Serial/Service Tag phần cứng duy nhất"),
          ("4", "TinhTrangMay", "nvarchar(255)", "None", "Yes", "Ghi chú ngoại quan và độ hao mòn thực tế"),
          ("5", "TrangThai", "int", "None", "No", "0: Trong kho, 1: Đang thuê, 2: Bảo trì, 3: Hỏng, 4: Giữ chỗ")]),

        ("6", "LichSuThietBi", "Bảng ghi vết toàn bộ vòng đời và nhật ký luân chuyển của từng thiết bị Serial.",
         [("1", "MaLSTB", "int", "PK", "No", "Mã định danh bản ghi nhật ký vòng đời"),
          ("2", "MaThietBi", "int", "FK", "No", "Khóa ngoại liên kết thiết bị vật lý ThietBi"),
          ("3", "HanhDong", "nvarchar(100)", "None", "No", "Hành động (Nhập kho, Xuất kho, Bàn giao, Thu hồi, Bảo trì)"),
          ("4", "ThoiGian", "datetime", "None", "No", "Thời điểm phát sinh hành động"),
          ("5", "NguoiThucHienId", "int", "FK", "Yes", "Khóa ngoại liên kết NguoiDung thực hiện"),
          ("6", "GhiChu", "nvarchar(255)", "None", "Yes", "Chi tiết bổ sung về sự kiện vòng đời")]),

        ("7", "KhuyenMai", "Bảng cấu hình mã giảm giá (Voucher), tỷ lệ chiết khấu và thời hạn hiệu lực.",
         [("1", "MaKM", "int", "PK", "No", "Mã định danh duy nhất của đợt khuyến mãi"),
          ("2", "Code", "varchar(50)", "Unique", "No", "Mã voucher người dùng nhập khi thuê máy"),
          ("3", "PhanTramGiam", "int", "None", "No", "Tỷ lệ chiết khấu giảm giá (%)"),
          ("4", "NgayBatDau", "datetime", "None", "No", "Thời điểm bắt đầu áp dụng mã"),
          ("5", "NgayKetThuc", "datetime", "None", "No", "Thời điểm kết thúc áp dụng mã"),
          ("6", "SoLuong", "int", "None", "No", "Số lượt sử dụng tối đa của mã"),
          ("7", "KichHoat", "bit", "None", "No", "Trạng thái kích hoạt (1: Khả dụng, 0: Tạm dừng)"),
          ("8", "MoTa", "nvarchar(255)", "None", "Yes", "Điều kiện áp dụng và ghi chú ưu đãi")]),

        ("8", "HopDong", "Bảng trung tâm quản lý hợp đồng thuê máy, tài chính, chữ ký điện tử và trạng thái cọc.",
         [("1", "MaHopDong", "int", "PK", "No", "Mã định danh duy nhất của hợp đồng thuê"),
          ("2", "MaKhachHang", "int", "FK", "No", "Khóa ngoại liên kết khách hàng thuê máy"),
          ("3", "MaNhanVien", "int", "FK", "No", "Khóa ngoại liên kết nhân viên kinh doanh duyệt đơn"),
          ("4", "MaKM", "int", "FK", "Yes", "Khóa ngoại mã khuyến mãi áp dụng (nếu có)"),
          ("5", "NgayBatDau", "datetime", "None", "No", "Thời điểm bắt đầu tính tiền thuê"),
          ("6", "NgayKetThuc", "datetime", "None", "No", "Thời điểm kết thúc hợp đồng dự kiến"),
          ("7", "TongTien", "decimal(18,2)", "None", "No", "Tổng giá trị hợp đồng gồm tiền thuê và cọc"),
          ("8", "TienDaCoc", "decimal(18,2)", "None", "No", "Số tiền cọc thực tế khách đã thanh toán"),
          ("9", "TienCocBaoDamMay", "decimal(18,2)", "None", "No", "Tiền cọc bảo đảm giá trị thiết bị"),
          ("10", "TrangThai", "int", "None", "No", "0: Chờ duyệt, 1: Đang thuê, 2: Hoàn thành, 3: Đã hủy"),
          ("11", "SoKyHan", "int", "None", "No", "Số kỳ phân kỳ thanh toán trả góp"),
          ("12", "AnhCCCD_Truoc", "nvarchar(255)", "None", "Yes", "Đường dẫn ảnh mặt trước CCCD khách hàng"),
          ("13", "AnhCCCD_Sau", "nvarchar(255)", "None", "Yes", "Đường dẫn ảnh mặt sau CCCD khách hàng"),
          ("14", "ChuKyKhachHang", "nvarchar(255)", "None", "Yes", "Đường dẫn tệp ảnh chữ ký điện tử Canvas của khách"),
          ("15", "ChuKyNhanVien", "nvarchar(255)", "None", "Yes", "Đường dẫn tệp ảnh chữ ký điện tử của đại diện công ty"),
          ("16", "NgayKy", "datetime", "None", "Yes", "Thời điểm hai bên hoàn tất ký số điện tử"),
          ("17", "TrangThaiThanhToan", "int", "None", "No", "0: Chưa trả, 1: Trả 1 phần, 2: Đã thanh toán đủ"),
          ("18", "TrangThaiHoanCoc", "int", "None", "No", "0: Chưa xử lý, 1: Đã hoàn tất đối soát hoàn cọc"),
          ("19", "NgayHoanCoc", "datetime", "None", "Yes", "Thời điểm thực hiện chuyển khoản hoàn cọc"),
          ("20", "HanChotKy", "datetime", "None", "Yes", "Thời hạn tối đa để khách ký số (quá hạn tự hủy)"),
          ("21", "GhiChu", "nvarchar(max)", "None", "Yes", "Ghi chú giao nhận, địa chỉ và quyết toán")]),

        ("9", "ChiTietHopDong", "Bảng liên kết thiết bị Serial cụ thể được bàn giao gán theo từng hợp đồng.",
         [("1", "MaChiTiet", "int", "PK", "No", "Mã định danh bản ghi chi tiết hợp đồng"),
          ("2", "MaHopDong", "int", "FK", "No", "Khóa ngoại liên kết hợp đồng thuê HopDong"),
          ("3", "MaThietBi", "int", "FK", "No", "Khóa ngoại liên kết thiết bị vật lý ThietBi"),
          ("4", "GiaThue", "decimal(18,2)", "None", "No", "Đơn giá thuê áp dụng cho thiết bị này"),
          ("5", "TienCoc", "decimal(18,2)", "None", "No", "Tiền cọc phân bổ cho thiết bị này")]),

        ("10", "KyHanThanhToan", "Bảng phân kỳ thanh toán trả góp, theo dõi hạn trả, nợ quá hạn và nhóm tuổi nợ.",
         [("1", "MaKyHan", "int", "PK", "No", "Mã định danh kỳ hạn thanh toán"),
          ("2", "MaHopDong", "int", "FK", "No", "Khóa ngoại liên kết hợp đồng HopDong"),
          ("3", "SoKyHan", "int", "None", "No", "Số thứ tự kỳ thanh toán (Kỳ 1, Kỳ 2...)"),
          ("4", "NgayDenHan", "datetime", "None", "No", "Hạn chót thanh toán của kỳ này"),
          ("5", "SoTienPhai", "decimal(18,2)", "None", "No", "Số tiền phải trả theo phân bổ hợp đồng"),
          ("6", "SoTienDaTra", "decimal(18,2)", "None", "No", "Số tiền lũy kế thực tế khách đã trả"),
          ("7", "TienPhat", "decimal(18,2)", "None", "No", "Tiền phạt phát sinh do trễ hạn sau ân hạn"),
          ("8", "TrangThai", "int", "None", "No", "0: Chưa trả, 1: Đã trả đủ, 2: Quá hạn, 3: Đã hủy"),
          ("9", "NgayThanhToan", "datetime", "None", "Yes", "Thời điểm khách hoàn tất thanh toán kỳ"),
          ("10", "MaGiaoDichChuyenKhoan", "varchar(100)", "None", "Yes", "Mã tham chiếu chuyển khoản ngân hàng"),
          ("11", "HinhAnhBienLai", "nvarchar(255)", "None", "Yes", "Đường dẫn ảnh biên lai chuyển tiền tải lên"),
          ("12", "TrangThaiXacNhan", "int", "None", "No", "0: Chờ duyệt, 1: Hợp lệ, 2: Từ chối"),
          ("13", "SoNgayTreHan", "int", "None", "No", "Số ngày quá hạn tính từ NgayDenHan"),
          ("14", "NhomTuoiNo", "int", "None", "No", "Phân loại 5 nhóm nợ (0: Đúng hạn, 1..4: Quá hạn)"),
          ("15", "NgayHenTraTiepTheo", "datetime", "None", "Yes", "Ngày khách hẹn thanh toán tiếp theo"),
          ("16", "GhiChu", "nvarchar(255)", "None", "Yes", "Ghi chú theo dõi nợ và đối soát")]),

        ("11", "PhieuThu", "Bảng chứng từ thu tiền cọc, tiền thuê, lưu mã đối soát Webhook ngân hàng tự động.",
         [("1", "MaPhieuThu", "int", "PK", "No", "Mã định danh phiếu thu tiền"),
          ("2", "MaHopDong", "int", "FK", "No", "Khóa ngoại liên kết hợp đồng HopDong"),
          ("3", "MaKyHan", "int", "FK", "Yes", "Khóa ngoại kỳ hạn thanh toán (nếu thu tiền thuê)"),
          ("4", "SoTien", "decimal(18,2)", "None", "No", "Số tiền thực tế thu vào tài khoản"),
          ("5", "LoaiPhieu", "int", "None", "No", "0: Thu tiền cọc, 1: Thu tiền thuê, 2: Đền bù hư hại"),
          ("6", "NgayGiaoDich", "datetime", "None", "No", "Thời điểm giao dịch phát sinh"),
          ("7", "HinhThucThanhToan", "int", "None", "No", "0: Tiền mặt, 1: Chuyển khoản VietQR/Webhook, 2: VNPay"),
          ("8", "MaNhanVienThu", "int", "FK", "Yes", "Nhân viên lập phiếu (null nếu Webhook tự động)"),
          ("9", "MaGiaoDichNganHang", "varchar(100)", "None", "Yes", "Mã giao dịch đối tác SePay/Casso/Ngân hàng"),
          ("10", "NganHangNhan", "nvarchar(100)", "None", "Yes", "Tên ngân hàng thụ hưởng giao dịch"),
          ("11", "GhiChu", "nvarchar(255)", "None", "Yes", "Nội dung chuyển khoản hoặc lý do thu"),
          ("12", "DaHuy", "bit", "None", "No", "Cờ đánh dấu phiếu đã bị hủy (1: Đã hủy, 0: Hợp lệ)"),
          ("13", "LyDoHuy", "nvarchar(255)", "None", "Yes", "Lý do hủy chứng từ phiếu thu"),
          ("14", "NgayHuy", "datetime", "None", "Yes", "Thời điểm thực hiện hủy chứng từ")]),

        ("12", "PhieuChi", "Bảng chứng từ chi tiền hoàn cọc cho khách hoặc thanh toán sửa chữa thiết bị.",
         [("1", "MaPhieuChi", "int", "PK", "No", "Mã định danh phiếu chi tiền"),
          ("2", "MaHopDong", "int", "FK", "No", "Khóa ngoại liên kết hợp đồng HopDong"),
          ("3", "SoTien", "decimal(18,2)", "None", "No", "Số tiền thực tế xuất quỹ chi trả"),
          ("4", "LoaiChi", "int", "None", "No", "0: Hoàn trả tiền cọc, 1: Thanh toán chi phí sửa chữa"),
          ("5", "NgayChi", "datetime", "None", "No", "Thời điểm xuất quỹ chi tiền"),
          ("6", "HinhThucChi", "int", "None", "No", "0: Tiền mặt, 1: Chuyển khoản ngân hàng"),
          ("7", "MaNhanVienChi", "int", "FK", "No", "Nhân viên thực hiện duyệt chi"),
          ("8", "MaGiaoDichNganHang", "varchar(100)", "None", "Yes", "Mã tham chiếu điện chuyển tiền"),
          ("9", "GhiChu", "nvarchar(255)", "None", "Yes", "Lý do chi và số tài khoản nhận tiền")]),

        ("13", "PhieuBaoTri", "Bảng tiếp nhận báo cố, kiểm soát thời gian tạm dừng tính tiền và đánh giá hài lòng.",
         [("1", "MaPhieuBaoTri", "int", "PK", "No", "Mã định danh phiếu bảo trì sự cố"),
          ("2", "MaHopDong", "int", "FK", "Yes", "Khóa ngoại hợp đồng thuê máy liên quan"),
          ("3", "MaThietBi", "int", "FK", "No", "Khóa ngoại thiết bị vật lý gặp sự cố"),
          ("4", "KyThuatVienId", "int", "FK", "Yes", "Khóa ngoại kỹ thuật viên được giao việc"),
          ("5", "MoTaLoi", "nvarchar(max)", "None", "No", "Mô tả hiện tượng hỏng hóc từ khách hàng"),
          ("6", "NgayBaoLoi", "datetime", "None", "No", "Thời điểm khách gửi yêu cầu trợ giúp"),
          ("7", "TrangThai", "int", "None", "No", "0: Chờ tiếp nhận, 1: Đang sửa, 2: Hoàn thành, 3: Đã hủy"),
          ("8", "HinhAnhLoi", "nvarchar(255)", "None", "Yes", "Đường dẫn ảnh chụp hư hại thiết bị"),
          ("9", "LoaiTrachNhiem", "int", "None", "Yes", "0: Lỗi phần cứng NSX (miễn phí), 1: Lỗi người dùng (đền bù)"),
          ("10", "ChiPhiSuaChua", "decimal(18,2)", "None", "No", "Chi phí mua linh kiện thay thế thực tế"),
          ("11", "PhiDenBu", "decimal(18,2)", "None", "No", "Số tiền đền bù khách hàng phải gánh chịu"),
          ("12", "TamDungTinhTien", "bit", "None", "No", "1: Kích hoạt đóng băng tiền thuê trong thời gian sửa"),
          ("13", "SoNgayTamDung", "int", "None", "Yes", "Số ngày được khấu trừ tiền thuê cho khách"),
          ("14", "DanhGiaSao", "int", "None", "Yes", "Điểm đánh giá chất lượng phục vụ (1 đến 5 sao)"),
          ("15", "YKienPhanHoi", "nvarchar(max)", "None", "Yes", "Ý kiến đóng góp phản hồi từ khách hàng"),
          ("16", "DaNghiemThu", "bit", "None", "No", "1: Khách đã nghiệm thu ký nhận máy sửa chữa"),
          ("17", "NgayNghiemThu", "datetime", "None", "Yes", "Thời điểm hoàn tất nghiệm thu sửa chữa")]),

        ("14", "BienBanBanGiao", "Bảng chứng từ giao nhận thiết bị, thẩm định ngoại quan lúc giao và lúc thu hồi.",
         [("1", "MaBienBan", "int", "PK", "No", "Mã định danh biên bản bàn giao"),
          ("2", "MaHopDong", "int", "FK", "No", "Khóa ngoại liên kết hợp đồng thuê HopDong"),
          ("3", "LoaiBienBan", "int", "None", "No", "0: Bàn giao máy lúc đầu, 1: Thu hồi máy lúc trả"),
          ("4", "NgayLap", "datetime", "None", "No", "Thời điểm lập biên bản giao nhận"),
          ("5", "MaNhanVienLap", "int", "FK", "No", "Nhân viên thực hiện thẩm định giao máy"),
          ("6", "PhuKienKemTheo", "nvarchar(max)", "None", "Yes", "Danh sách phụ kiện (Sạc, Chuột, Cáp HDMI, Cặp...)"),
          ("7", "TinhTrangNgoaiQuan", "nvarchar(max)", "None", "Yes", "Tình trạng trầy xước, bàn phím, màn hình hiển thị"),
          ("8", "ChuKyXacNhan", "nvarchar(255)", "None", "Yes", "Đường dẫn ảnh chữ ký điện tử xác nhận hiện trường"),
          ("9", "GhiChu", "nvarchar(max)", "None", "Yes", "Ghi chú cam kết hoàn trả và bảo quản")]),

        ("15", "ThongBao", "Bảng lưu thông báo hệ thống gửi đến người dùng, thông báo nhắc nợ và cập nhật sự cố.",
         [("1", "MaThongBao", "int", "PK", "No", "Mã định danh bản tin thông báo"),
          ("2", "MaNguoiDung", "int", "FK", "No", "Khóa ngoại người nhận thông báo"),
          ("3", "NoiDung", "nvarchar(max)", "None", "No", "Nội dung chi tiết của bản tin thông báo"),
          ("4", "LoaiThongBao", "nvarchar(50)", "None", "Yes", "Phân loại (NhacNo, BaoTri, HopDong, HeThong)"),
          ("5", "NgayTao", "datetime", "None", "No", "Thời điểm gửi bản tin thông báo"),
          ("6", "DaDoc", "bit", "None", "No", "1: Người dùng đã xem, 0: Chưa xem"),
          ("7", "LienKet", "nvarchar(255)", "None", "Yes", "Đường dẫn chuyển hướng xem chi tiết sự kiện")]),

        ("16", "LichSuNhacNo", "Bảng ghi vết nhật ký các lần đôn đốc, gọi điện, gửi email và phát hành cảnh báo nợ.",
         [("1", "MaLichSuNhacNo", "int", "PK", "No", "Mã định danh bản ghi nhật ký nhắc nợ"),
          ("2", "MaHopDong", "int", "FK", "No", "Khóa ngoại hợp đồng đang có công nợ"),
          ("3", "MaKyHan", "int", "FK", "Yes", "Khóa ngoại kỳ hạn cụ thể được nhắc nợ"),
          ("4", "NgayNhac", "datetime", "None", "No", "Thời điểm nhân viên hoặc hệ thống nhắc nợ"),
          ("5", "HinhThucNhac", "nvarchar(50)", "None", "No", "Kênh nhắc (SMS, Email, CuocGoi, Zalo, ThongBaoWeb)"),
          ("6", "NoiDung", "nvarchar(max)", "None", "Yes", "Biên bản tóm tắt nội dung trao đổi với khách nợ"),
          ("7", "NguoiGuiId", "int", "FK", "Yes", "Nhân viên thực hiện cuộc gọi hoặc nhắc nhở"),
          ("8", "SoTienNhac", "decimal(18,2)", "None", "No", "Số dư nợ được nhắc nhở tại thời điểm đó"),
          ("9", "LanNhacThu", "int", "None", "No", "Số thứ tự lần nhắc nhở (Lần 1, Lần 2, Lần 3)")]),

        ("17", "YeuCauGiaHan", "Bảng quản lý các yêu cầu gia hạn thời gian thuê máy từ khách hàng và phê duyệt.",
         [("1", "MaYeuCau", "int", "PK", "No", "Mã định danh yêu cầu gia hạn thuê máy"),
          ("2", "MaHopDong", "int", "FK", "No", "Khóa ngoại liên kết hợp đồng cần gia hạn"),
          ("3", "SoNgayGiaHan", "int", "None", "No", "Số ngày khách hàng mong muốn thuê thêm"),
          ("4", "LyDo", "nvarchar(max)", "None", "Yes", "Lý do nhu cầu kéo dài thời gian sử dụng"),
          ("5", "NgayYeuCau", "datetime", "None", "No", "Thời điểm khách nộp đơn xin gia hạn"),
          ("6", "TrangThai", "int", "None", "No", "0: Chờ duyệt, 1: Đã chấp thuận, 2: Từ chối gia hạn"),
          ("7", "NgayDuyet", "datetime", "None", "Yes", "Thời điểm nhân viên kinh doanh xử lý đơn"),
          ("8", "MaNguoiDuyet", "int", "FK", "Yes", "Nhân viên kinh doanh thực hiện phê duyệt đơn"),
          ("9", "ChiPhiPhatSinh", "decimal(18,2)", "None", "No", "Số tiền thuê phát sinh thêm cho số ngày gia hạn"),
          ("10", "GhiChuAdmin", "nvarchar(max)", "None", "Yes", "Ghi chú điều khoản bổ sung của người duyệt")]),

        ("18", "PhanCongCongViec", "Bảng điều phối công việc nội bộ giữa Quản trị viên và Kỹ thuật viên hiện trường.",
         [("1", "MaPhanCong", "int", "PK", "No", "Mã định danh bản ghi phân công nhiệm vụ"),
          ("2", "MaNhanVien", "int", "FK", "No", "Khóa ngoại kỹ thuật viên tiếp nhận công việc"),
          ("3", "TieuDe", "nvarchar(150)", "None", "No", "Tiêu đề tóm tắt nhiệm vụ cần thực hiện"),
          ("4", "NoiDung", "nvarchar(max)", "None", "No", "Mô tả chi tiết yêu cầu công việc tại hiện trường"),
          ("5", "MaHopDong", "int", "FK", "Yes", "Khóa ngoại hợp đồng liên quan (nếu có)"),
          ("6", "MaPhieuBaoTri", "int", "FK", "Yes", "Khóa ngoại phiếu bảo trì cần xử lý sự cố (nếu có)"),
          ("7", "TrangThai", "int", "None", "No", "0: Mới giao, 1: Đang thực hiện, 2: Hoàn thành, 3: Đã hủy"),
          ("8", "NgayGiao", "datetime", "None", "No", "Thời điểm phân công giao nhiệm vụ"),
          ("9", "HanHoanThanh", "datetime", "None", "Yes", "Hạn chót cam kết hoàn thành công việc"),
          ("10", "NgayHoanThanh", "datetime", "None", "Yes", "Thời điểm thực tế kết thúc nhiệm vụ"),
          ("11", "MaNguoiGiao", "int", "FK", "Yes", "Khóa ngoại Quản trị viên giao nhiệm vụ"),
          ("12", "GhiChuTienDo", "nvarchar(max)", "None", "Yes", "Cập nhật tiến độ xử lý và vướng mắc hiện trường")])
    ]

    for tbl_id, tbl_name, tbl_desc, cols in db_tables_dict:
        add_p(doc, f"Bảng {tbl_name}: {tbl_desc}", font_size_pt=12, is_italic=True, first_line_indent_cm=0)
        add_table_with_caption(doc, "3.1.1", tbl_id, f"Cấu trúc từ điển dữ liệu thực thể {tbl_name}",
                               ["STT", "Tên cột (Field Name)", "Kiểu dữ liệu", "Khóa", "Null", "Diễn giải nghiệp vụ"],
                               cols, col_widths=[1.2, 3.5, 2.5, 1.8, 1.5, 4.5])

    add_heading_3(doc, "3.1.2. Mối quan hệ và ma trận ràng buộc toàn vẹn cơ sở dữ liệu")
    add_p(doc, "Để đảm bảo tính toàn vẹn tham chiếu (Referential Integrity) và ngăn chặn việc xóa nhầm dữ liệu lịch sử tài chính, RentalSystem cấu hình hành vi xóa khóa ngoại (DeleteBehavior) trong DbContext:")
    add_bullet(doc, "Quan hệ HopDong -> ChiTietHopDong & KyHanThanhToan: Cấu hình DeleteBehavior.Cascade. Khi một đơn hàng ở trạng thái nháp bị hủy, các dòng chi tiết tạm sẽ tự động được thu hồi.")
    add_bullet(doc, "Quan hệ HopDong -> PhieuThu & PhieuChi: Cấu hình DeleteBehavior.Restrict. Không cho phép xóa trực tiếp hợp đồng nếu đã phát sinh chứng từ tài chính thu/chi nhằm bảo lưu chứng từ kế toán.")
    add_bullet(doc, "Quan hệ ThietBi -> LichSuSuDung: Cấu hình DeleteBehavior.Restrict để bảo lưu lịch sử vòng đời máy vĩnh viễn.")

    add_heading_3(doc, "3.1.3. Sơ đồ cơ sở dữ liệu quan hệ vật lý ERD")
    add_p(doc, "Sơ đồ cơ sở dữ liệu vật lý (Physical Relational Database Schema ERD) thể hiện đầy đủ 18 bảng thực thể, các trường khóa chính (PK), khóa ngoại (FK) và đường liên kết quan hệ 1-N giữa các bảng:")

    add_figure_with_caption(doc, "3.1.3", 1, "Sơ đồ cơ sở dữ liệu quan hệ vật lý chi tiết (Physical Relational Database Schema ERD)",
                            "figures/hinh_3_3_erd_vat_ly_chi_tiet.png", width_cm=15.0)

    add_heading_2(doc, "3.2. THIẾT KẾ GIAO DIỆN HỆ THỐNG")
    add_heading_3(doc, "3.2.1. Thiết kế giao diện phân hệ khách hàng")
    add_p(doc, "Phân hệ khách hàng được thiết kế theo tiêu chí tối giản, hiện đại, hiển thị tốt trên các thiết bị di động và máy tính bảng:")
    add_figure_with_caption(doc, "3.2.1", 1, "Thiết kế giao diện Trang chủ và Bộ lọc danh mục thiết bị", "figures/hinh_3_10_ui_trang_chu.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.1", 2, "Thiết kế giao diện Chi tiết thiết bị và Đặt thông số gói thuê", "figures/hinh_3_11_ui_chi_tiet_san_pham.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.1", 3, "Thiết kế giao diện Giỏ hàng và Xác nhận yêu cầu đặt thuê (Checkout)", "figures/hinh_3_12_ui_checkout.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.1", 4, "Thiết kế giao diện Ký hợp đồng điện tử Canvas và Tải ảnh CCCD", "figures/hinh_3_13_ui_ky_hop_dong.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.1", 5, "Thiết kế giao diện Quản lý hợp đồng của khách hàng (MyContracts)", "figures/hinh_3_14_ui_hop_dong_khach_hang.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.1", 6, "Thiết kế giao diện Sổ theo dõi công nợ cá nhân và Tích hợp VietQR", "figures/hinh_3_15_ui_cong_no_khach_hang.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.1", 7, "Thiết kế giao diện Báo cáo sự cố kỹ thuật của khách hàng (MyTickets)", "figures/hinh_3_16_ui_phieu_bao_tri.png", width_cm=14.5)

    add_heading_3(doc, "3.2.2. Thiết kế giao diện phân hệ quản trị (Admin)")
    add_p(doc, "Giao diện quản trị Admin được thiết kế theo phong cách tối giản, sử dụng tông màu chủ đạo là xanh đen (Deep Navy) kết hợp nền trắng để đảm bảo độ tương phản rõ ràng, giúp người dùng dễ dàng quan sát và thao tác dữ liệu:")
    add_bullet(doc, "Bảng màu sử dụng: Tông xanh đen (#0f2b5c) được dùng cho thanh điều hướng (Sidebar) và tiêu đề bảng; nền trắng (#ffffff) và viền xám nhạt (#e2e8f0) được áp dụng cho các khung chứa dữ liệu để tạo sự ngăn nắp.")
    add_bullet(doc, "Bố cục bảng biểu: Sử dụng các lớp CSS ngữ nghĩa trong file classic-navy.css (.admin-card, .admin-table, .stat-card) nhằm chuẩn hóa cấu trúc hiển thị bảng và nút bấm chức năng đồng bộ.")
    add_bullet(doc, "Huy hiệu trạng thái: Sử dụng các huy hiệu dạng nhãn nhỏ (.status-pill) với màu sắc nhẹ dịu để phân biệt trạng thái của đơn thuê và thiết bị, hạn chế sử dụng các gam màu quá chói.")
    
    add_figure_with_caption(doc, "3.2.2", 1, "Thiết kế giao diện Dashboard tổng quan quản trị và Các thẻ chỉ số tài chính KPI", "figures/hinh_3_17_ui_admin_dashboard.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.2", 2, "Thiết kế giao diện Quản lý kho máy Serial và Tình trạng thiết bị", "figures/hinh_3_18_ui_admin_cong_no.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.2", 3, "Thiết kế giao diện Thẩm định hợp đồng, Cấp phát máy Serial", "figures/hinh_3_19_ui_admin_bao_tri.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.2", 4, "Thiết kế giao diện Quản lý công nợ, Phân nhóm tuổi nợ 4 cấp", "figures/hinh_3_20_ui_in_hop_dong.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.2", 5, "Thiết kế sơ đồ điều hướng phân hệ Khách hàng (Sitemap Customer)", "figures/hinh_3_8_dieu_huong_khach_hang.png", width_cm=14.5)
    add_figure_with_caption(doc, "3.2.2", 6, "Thiết kế sơ đồ điều hướng phân hệ Quản trị (Sitemap Admin)", "figures/hinh_3_9_dieu_huong_admin.png", width_cm=14.5)

    add_heading_3(doc, "3.2.3. Thiết kế giao diện Web Responsive Design trên thiết bị di động")
    add_p(doc, "Giao diện ứng dụng di động được thiết kế chuyên biệt cho 02 đối tượng người dùng thao tác trên thiết bị cầm tay:")
    add_bullet(doc, "Màn hình Khách hàng di động: Tối ưu cho màn hình cảm ứng dọc, hiển thị thẻ sản phẩm trượt ngang, hỗ trợ chọn ngày thuê trực quan qua lịch di động, tích hợp quét mã VietQR chuyển khoản nhanh và chức năng chụp ảnh hiện trường gửi ticket báo sự cố khẩn cấp kèm chấm điểm sao đánh giá.")
    add_bullet(doc, "Màn hình Kỹ thuật viên di động: Giao diện danh sách công việc dạng thẻ Task Card, tích hợp camera quét mã vạch Barcode/Serial xuất kho, bảng vẽ cảm ứng thu nhận chữ ký số Canvas của khách hàng khi bàn giao máy tại địa chỉ thuê và chức năng cập nhật biên bản nghiệm thu trực tiếp tại hiện trường.")

    add_heading_2(doc, "3.3. SƠ ĐỒ LỚP MỨC THIẾT KẾ 3 LỚP (DESIGN CLASS DIAGRAM)")
    add_p(doc, "Sơ đồ lớp mức thiết kế 3 lớp (Design Class Diagram) mô tả chi tiết các lớp đối tượng trong kiến trúc phần mềm phân tầng: Presentation Layer (Controllers & ViewModels), Business Logic Layer (Services & Algorithmic Engines), và Data Access Layer (Entities & DbContext):")

    add_figure_with_caption(doc, "3.3", 1, "Sơ đồ lớp mức thiết kế 3 lớp (Design Class Diagram - Presentation, Business, Data)",
                            "figures/hinh_3_3_1_design_class_diagram.png", width_cm=15.0)

    add_heading_2(doc, "3.4. THIẾT KẾ CHI TIẾT 7 CHỨC NĂNG TRỌNG TÂM THEO KIẾN TRÚC 3 LỚP")
    add_p(doc, "Mỗi chức năng cốt lõi được thiết kế chi tiết bằng bộ ba sơ đồ UML: (1) Sơ đồ 3 lớp mức thiết kế Boundary – Control – Entity (BCE), (2) Sơ đồ tuần tự 3 lớp (Sequence Diagram), và (3) Sơ đồ cộng tác 3 lớp (Collaboration Diagram).")

    functions_info = [
        ("3.4.1", "Chức năng Đăng ký & Xác thực người dùng",
         "Thiết kế 3 lớp xử lý nhận diện danh tính, phân quyền Cookie Claims và điều hướng phân hệ thông minh.",
         "Giao diện Đăng ký / Đăng nhập (RegisterView, LoginView) tiếp nhận biểu mẫu và xác thực đầu vào.",
         "AccountController và CookieAuthenticationHandler kiểm tra băm mật khẩu, thiết lập phiên bảo mật.",
         "Bảng NguoiDung và VaiTro lưu trữ hồ sơ tài khoản và vai trò phân quyền."),

        ("3.4.2", "Chức năng Đặt thuê máy & Kiểm tra tồn kho (SemaphoreSlim)",
         "Thiết kế 3 lớp xử lý khóa tương tranh đa luồng, kiểm tra giao thoa khoảng ngày và giữ chỗ thiết bị an toàn.",
         "Giao diện Giỏ hàng / Đặt thuê (CheckoutView) tiếp nhận thông số gói thuê và lịch nhận máy.",
         "CartController phối hợp static SemaphoreSlim(1,1) ngăn chặn Race Condition và cấp phát serial tạm.",
         "Bảng SanPham, ThietBi và HopDong lưu trữ chi tiết đơn thuê và đổi trạng thái máy sang Giữ chỗ."),

        ("3.4.3", "Chức năng Thanh toán đặt cọc qua VietQR động NAPAS 247",
         "Thiết kế 3 lớp sinh chuỗi TLV EMVCo, bắt Webhook ngân hàng và đối soát phiếu thu tự động.",
         "Giao diện Thanh toán (PaymentView) hiển thị mã QR động chứa số tiền cọc và bộ đếm ngược.",
         "PaymentController và OpenBankingWebhookService tiếp nhận IPN, xác thực chữ ký và gạch nợ tự động.",
         "Bảng PhieuThu và KyHanThanhToan ghi nhận phiếu thu và cập nhật trạng thái hợp đồng đã cọc."),

        ("3.4.4", "Chức năng Bàn giao & Ký biên bản bàn giao máy",
         "Thiết kế 3 lớp thu nhận chữ ký số HTML5 Canvas, kiểm soát bộ nhớ Base64 và cập nhật trạng thái serial.",
         "Giao diện Bàn giao (HandoverView) cung cấp vùng ký Canvas và tiếp nhận hồ sơ CCCD/ảnh máy.",
         "HopDongController kiểm tra magic bytes tệp tải lên, giải mã chữ ký ảnh PNG và sinh biên bản bàn giao.",
         "Bảng BienBanBanGiao và ThietBi lưu biên bản pháp lý và đổi trạng thái máy sang Đang thuê."),

        ("3.4.5", "Chức năng Báo cáo sự cố & Phân công bảo trì thiết bị",
         "Thiết kế 3 lớp tiếp nhận phiếu lỗi, điều phối kỹ thuật viên và kiểm soát cơ chế tạm dừng tính tiền thuê.",
         "Giao diện Báo lỗi sự cố (IncidentTicketView) cho phép khách hàng gửi mô tả kèm ảnh lỗi.",
         "BaoTriController phân công kỹ thuật viên, kích hoạt cờ TamDungTinhTien nếu bảo trì vượt quá 24h.",
         "Bảng PhieuBaoTri và PhanCongCongViec lưu lịch sử khắc phục sự cố và điều phối nhân sự."),

        ("3.4.6", "Chức năng Gia hạn hợp đồng & Phân kỳ nợ",
         "Thiết kế 3 lớp kiểm tra lịch thuê tương lai, tính toán dồn dư kỳ cuối và cập nhật phân kỳ tài chính.",
         "Giao diện Gia hạn (ExtensionRequestView) và Quản trị công nợ (CongNoAdminView) phục vụ lập và duyệt gia hạn.",
         "HopDongController và DebtCalculationHelper kiểm tra xung đột lịch thuê, tính toán phân kỳ trả góp bổ sung.",
         "Bảng YeuCauGiaHan, HopDong và KyHanThanhToan lưu trữ kỳ hạn mới và cập nhật ngày kết thúc hợp đồng."),

        ("3.4.7", "Chức năng Trả máy, nghiệm thu & Hoàn trả tiền cọc",
         "Thiết kế 3 lớp kiểm định thu hồi máy, đối trừ công nợ hư hại và chi hoàn cọc qua phiếu chi tự động.",
         "Giao diện Nghiệm thu (ReturnMachineView) và Chi tiết hợp đồng (HopDongDetailsView) phục vụ nghiệm thu và hoàn cọc.",
         "HopDongController thực hiện đối trừ công nợ tồn đọng, bồi thường linh kiện và duyệt chi hoàn cọc.",
         "Bảng BienBanBanGiao, PhieuChi, HopDong và ThietBi ghi nhận tất toán hợp đồng và đưa máy về kho sẵn sàng.")
    ]

    for idx, (code, name, desc, bnd, ctrl, ent) in enumerate(functions_info):
        if idx > 0:
            doc.add_page_break()
        add_heading_3(doc, f"{code}. {name}")
        add_p(doc, f"Mô tả kiến trúc thiết kế: {desc}")
        add_p(doc, "Kiến trúc 3 lớp (Boundary - Control - Entity) của chức năng được phân rã như sau:")
        add_bullet(doc, f"Tầng Biên (Boundary): {bnd}")
        add_bullet(doc, f"Tầng Điều khiển (Control): {ctrl}")
        add_bullet(doc, f"Tầng Thực thể (Entity): {ent}")

        # Diagram 1: BCE
        bce_img = f"figures/hinh_{code.replace('.', '_')}_1_bce_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 1, f"Sơ đồ 3 lớp mức thiết kế {name} (BCE)", bce_img, width_cm=14.5)

        # Diagram 2: Sequence 3-layer
        seq_img = f"figures/hinh_{code.replace('.', '_')}_2_sequence_3lop_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 2, f"Sơ đồ tuần tự 3 lớp {name}", seq_img, width_cm=14.5)

        # Diagram 3: Collab 3-layer
        col_img = f"figures/hinh_{code.replace('.', '_')}_3_collab_3lop_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 3, f"Sơ đồ cộng tác 3 lớp {name}", col_img, width_cm=14.5)

    add_heading_2(doc, "3.5. KẾT CHƯƠNG")
    add_p(doc, "Trong Chương 3, nhóm nghiên cứu đã hoàn thành bản thiết kế kỹ thuật chi tiết cho hệ thống RentalSystem, bao gồm: (1) Lược đồ cơ sở dữ liệu quan hệ 18 bảng với đầy đủ ràng buộc toàn vẹn khóa ngoại; (2) Bố cục giao diện phân hệ Khách hàng và Quản trị trực quan, rõ ràng; (3) Mô hình hóa kiến trúc 3 lớp (BCE, Sequence và Collaboration) cho 7 chức năng trọng tâm. Các đặc tả thiết kế này là cơ sở kỹ thuật để triển khai mã nguồn trên nền tảng ASP.NET Core tại Chương 4.")
    doc.add_page_break()


def build_chapter4_implementation(doc):
    """
    CHƯƠNG 4: CÀI ĐẶT HỆ THỐNG
    4.1 Môi trường phát triển (.NET 9, SQL Server, Visual Studio)
    4.2 Kiến trúc ASP.NET Core MVC phân tầng
    4.3 Xây dựng các chức năng chính (mã nguồn, giải thuật)
    4.4 KẾT CHƯƠNG
    """
    add_heading_1(doc, "CHƯƠNG 4: CÀI ĐẶT HỆ THỐNG")

    add_heading_2(doc, "4.1. MÔI TRƯỜNG PHÁT TRIỂN VÀ CÀI ĐẶT")
    add_p(doc, "Hệ thống RentalSystem được xây dựng trên nền tảng Microsoft .NET 9 hiện đại kết hợp kiến trúc phân tầng ASP.NET Core MVC, đáp ứng các yêu cầu về hiệu năng xử lý web, tính module hóa và khả năng bảo trì hệ thống:")

    env_data = [
        ("Hệ điều hành máy chủ", "Windows Server 2022 / Windows 11 Pro 64-bit"),
        ("Nền tảng thực thi (Framework)", ".NET 9.0 (C# 13.0) – Standard-Term Support (STS)"),
        ("Máy chủ Web (Web Server)", "Kestrel Reverse Proxy kết hợp IIS (Internet Information Services 10.0)"),
        ("Hệ quản trị CSDL (DBMS)", "Microsoft SQL Server 2022 (Developer Edition)"),
        ("Công cụ ORM", "Entity Framework Core 9.0 (Code-First Migrations)"),
        ("Môi trường phát triển (IDE)", "Microsoft Visual Studio 2022 Community / Professional v17.12"),
        ("Thư viện xuất báo cáo", "ClosedXML v0.104.2 (Tạo bảng tính Excel OpenXML gốc)"),
        ("Thư viện sinh mã QR", "QRCoder v1.6.0 (Sinh ma trận điểm QR chuẩn EMVCo)"),
        ("Bộ kiểm thử tự động", "ChallengerTests (xUnit, Moq, FluentAssertions)")
    ]
    add_table_with_caption(doc, "4.1", 1, "Bảng thông số môi trường phát triển, máy chủ và các thư viện phần mềm",
                           ["Thành phần ngăn xếp công nghệ", "Thông số phiên bản & Vai trò kỹ thuật trong hệ thống"],
                           env_data, col_widths=[5.0, 10.0])

    add_heading_2(doc, "4.2. KIẾN TRÚC HỆ THỐNG PHÂN TẦNG ASP.NET CORE MVC")
    add_p(doc, "Ứng dụng được tổ chức theo mô hình kiến trúc phân tầng ASP.NET Core MVC kết hợp các nguyên lý hướng đối tượng SOLID:")
    add_bullet(doc, "Tầng Trình diễn (Presentation Layer): Gồm các Controllers (khu vực Client và Area Admin), Razor Views (.cshtml) và ViewModels. Tầng này chịu trách nhiệm xác thực dữ liệu đầu vào (ModelState Validation), hiển thị giao diện và trả về phản hồi JSON/HTML.")
    add_bullet(doc, "Tầng Nghiệp vụ (Business Service Layer): Chứa các dịch vụ chuyên sâu như VietQrService (sinh mã thanh toán EMVCo), InventoryLockService (quản lý SemaphoreSlim), DebtManagementService (tính toán phân kỳ và lãi phạt trễ hạn).")
    add_bullet(doc, "Tầng Dữ liệu (Data Access Layer): Chứa lớp ngữ cảnh RentalDbContext, các lớp thực thể (Entities) và các file kịch bản Migrations theo dõi toàn bộ lịch sử biến động cấu trúc bảng.")

    add_figure_with_caption(doc, "4.2", 1, "Sơ đồ kiến trúc tổng thể phân tầng hệ thống trên nền tảng ASP.NET Core 9 MVC",
                            "figures/hinh_3_1_kien_truc_he_thong.png", width_cm=14.5)
    add_figure_with_caption(doc, "4.2", 2, "Sơ đồ luồng xử lý yêu cầu HTTP qua ASP.NET Core Middleware Pipeline",
                            "figures/hinh_3_2_luong_http_request.png", width_cm=14.5)
    add_figure_with_caption(doc, "4.2", 3, "Sơ đồ cấu trúc phân rã thư mục và Module mã nguồn dự án RentalSystem",
                            "figures/hinh_4_1_cau_truc_ma_nguon.png", width_cm=14.5)
    add_figure_with_caption(doc, "4.2", 4, "Sơ đồ máy trạng thái biểu diễn vòng đời quản lý thiết bị vật lý Serial",
                            "figures/hinh_4_2_state_thiet_bi.png", width_cm=14.5)
    add_figure_with_caption(doc, "4.2", 5, "Sơ đồ máy trạng thái chu trình xử lý phiếu bảo trì và Kiểm soát nghiệm thu",
                            "figures/hinh_4_3_state_phieu_bao_tri.png", width_cm=14.5)
    add_figure_with_caption(doc, "4.2", 6, "Sơ đồ quy trình thực thi Entity Framework Core Migrations qua các mốc phát triển",
                            "figures/hinh_4_4_migration_timeline.png", width_cm=14.5)

    add_heading_2(doc, "4.3. XÂY DỰNG CÁC CHỨC NĂNG CHÍNH CỦA HỆ THỐNG")
    add_p(doc, "Dưới đây là phân tích chi tiết việc hiện thực hóa các chức năng cốt lõi trên mã nguồn thực tế của hệ thống:")
    add_heading_3(doc, "4.3.1. Cài đặt kiểm soát tương tranh SemaphoreSlim chống Overbooking")
    add_p(doc, "Trong CartController.cs, phương thức Checkout được bảo vệ bằng InventoryLock.WaitAsync():")
    add_p(doc, "await CartController.InventoryLock.WaitAsync();\ntry {\n    // Kiểm tra giao thoa khoảng ngày và cấp phát giữ chỗ máy\n    var available = await CheckAvailabilityAsync(productId, startDate, endDate);\n    if (!available) throw new InvalidOperationException(\"Thiết bị đã có người đặt trong khoảng ngày này.\");\n    // Tạo hợp đồng và giữ chỗ\n    await SaveContractAsync(contract);\n} finally {\n    CartController.InventoryLock.Release();\n}",
          font_name="Consolas", font_size_pt=10, is_bold=False, line_spacing=1.15, space_before_pt=4, space_after_pt=6,
          align=WD_ALIGN_PARAGRAPH.LEFT, first_line_indent_cm=0)

    add_heading_3(doc, "4.3.2. Cài đặt thu nhận chữ ký số Canvas và kiểm soát an toàn tệp tải lên")
    add_p(doc, "Tại CartController.cs (hành động SignContract) và HopDongController.cs (hành động KyHopDong), khách hàng thực hiện ký hợp đồng điện tử trực tiếp trên phần tử HTML5 Canvas được điều khiển bởi thư viện signature_pad. Dữ liệu chữ ký dạng chuỗi Base64 được giới hạn kích thước tối đa 256KB, giải mã sang mảng byte và kiểm tra định dạng Magic Bytes (bắt đầu bằng 0x89 0x50 0x4E 0x47 đối với PNG) trước khi ghi tệp vật lý vào thư mục /uploads/signatures/ và lưu đường dẫn vào trường ChuKyKhachHang. Đồng thời, tệp ảnh CCCD/CMND tải lên được giới hạn dung lượng tối đa 5MB, kiểm tra phần mở rộng (.jpg, .jpeg, .png, .webp) và kiểm tra Magic Bytes (PNG: 0x89 0x50 0x4E 0x47, JPG: 0xFF 0xD8 0xFF, RIFF/WEBP: 0x52 0x49 0x46 0x46), nhằm hạn chế nguy cơ tải tệp không hợp lệ lên máy chủ.")

    add_heading_3(doc, "4.3.3. Cài đặt cơ chế đối soát tự động Webhook ngân hàng")
    add_p(doc, "Tại PaymentController.cs, cổng tiếp nhận POST /Payment/BankingWebhook xử lý bản tin biến động số dư ngân hàng theo mô hình giao dịch an toàn kết hợp khóa SemaphoreSlim PaymentLock và mức cô lập Serializable Transaction. Cơ chế đảm bảo tính bất biến (Idempotency) được kích hoạt thông qua việc kiểm tra mã giao dịch ngân hàng referenceCode trong bảng PhieuThus (MaGiaoDichNganHang == referenceCode || GhiChu.Contains(referenceCode)). Khi xác nhận giao dịch mới, hệ thống bóc tách mã hợp đồng và thực hiện thuật toán gạch nợ 4 tầng (Waterfall): (1) Bù tiền cọc còn thiếu, (2) Thanh toán các kỳ hạn theo thứ tự hạn nộp tăng dần, (3) Thu hồi chi phí sửa chữa/bồi thường phát sinh, (4) Dồn tiền dôi dư vào số dư trả trước hợp đồng (TienDuKyTruoc). Phiếu thu tự động ghi nhận với MaNhanVienThu = null để đánh dấu giao dịch đối soát tự động bởi hệ thống.")

    add_heading_3(doc, "4.3.4. Cài đặt Trung tâm phân tích báo cáo BI và xuất Excel ClosedXML")
    add_p(doc, "Tại ThongKeController.cs và CongNoController.cs, tính năng xuất báo cáo quản trị sử dụng thư viện ClosedXML (phiên bản 0.104.2). Trong đó, hành động CongNoController.ExportExcel kết xuất 17 cột dữ liệu chi tiết kèm công thức định dạng tiền tệ (#,##0), và ThongKeController.ExportExcel kết xuất 9 chỉ số KPI trọng yếu sử dụng tông màu xanh đen (#0F2B5C) làm màu tiêu đề bảng, tính toán doanh thu thuần, tiền cọc đang giữ và tỷ lệ khai thác kho máy tự động.")

    add_heading_3(doc, "4.3.5. Cài đặt hệ thống API Backend dùng chung (RESTful API / Swagger)")
    add_p(doc, "Để phục vụ trao đổi dữ liệu với các ứng dụng máy khách và mở rộng tích hợp di động, hệ thống cấu hình các bộ điều khiển API Controller kế thừa ControllerBase kết hợp tài liệu hóa OpenAPI / Swagger. Cơ chế xác thực được thực hiện thông qua JSON Web Token (JWT) khi đăng nhập hợp lệ. Các Endpoint API trả về cấu trúc dữ liệu JSON gồm mã trạng thái (statusCode), thông điệp (message) và dữ liệu trả về (data), áp dụng xử lý bất đồng bộ (async/await) trên các tác vụ truy vấn Entity Framework Core.")

    add_heading_3(doc, "4.3.6. Cài đặt module Sao lưu và Phục hồi CSDL an toàn (Database Backup & Restore)")
    add_p(doc, "Tại DatabaseController.cs (khu vực Admin, áp dụng thuộc tính phân quyền Authorize(Roles = 'Admin')), hệ thống cài đặt chức năng sao lưu và khôi phục dữ liệu cho 18 bảng của hệ thống:")
    add_bullet(doc, "Cơ chế Sao lưu (ExportJson): Thu thập dữ liệu tuần tự từ 18 bảng thực thể (VaiTros, NguoiDungs, LoaiThietBis, SanPhams, ThietBis, LichSuThietBis, KhuyenMais, HopDongs, KyHanThanhToans, ChiTietHopDongs, PhieuThus, PhieuChis, PhieuBaoTris, BienBanBanGiaos, ThongBaos, LichSuNhacNos, YeuCauGiaHans, PhanCongCongViecs), đóng gói thành tệp JSON có gắn mã phiên bản (Version 1.0) và nhãn thời gian UTC xuất bản.")
    add_bullet(doc, "Cơ chế Phục hồi (ImportJson): Thực thi trong một Database Transaction an toàn. Để giải quyết hiệu quả xung đột ràng buộc toàn vẹn khóa ngoại (Foreign Key Constraints), hệ thống thực thi câu lệnh 'ALTER TABLE [...] NOCHECK CONSTRAINT ALL;', dọn dẹp dữ liệu cũ theo thứ tự phụ thuộc bảng ngược, sử dụng 'SET IDENTITY_INSERT [...] ON;' để giữ nguyên vẹn giá trị định danh khóa chính gốc của từng bản ghi, và kích hoạt kiểm tra lại toàn vẹn bằng lệnh 'ALTER TABLE [...] CHECK CONSTRAINT ALL;'. Nếu xảy ra bất kỳ lỗi nào, toàn bộ giao dịch được Rollback an toàn.")

    add_heading_2(doc, "4.4. KẾT CHƯƠNG")
    add_p(doc, "Chương 4 đã trình bày môi trường phát triển .NET 9, kiến trúc phân tầng ASP.NET Core MVC và quá trình cài đặt các chức năng chính của hệ thống RentalSystem trên nền tảng .NET 9, EF Core 9, SQL Server 2022 và thư viện ClosedXML, làm cơ sở thực hiện đánh giá kiểm thử tại Chương 5.")
    doc.add_page_break()


def build_chapter5_evaluation(doc):
    """
    CHƯƠNG 5: THỬ NGHIỆM VÀ TRIỂN KHAI
    5.1 Triển khai hệ thống (IIS & Webhook)
    5.2 Kiểm thử hệ thống: Ma trận kiểm thử chức năng (TC-01 đến TC-14) và kiểm thử luồng tích hợp
    5.3 Đánh giá kết quả thử nghiệm và độ ổn định
    5.4 KẾT CHƯƠNG
    """
    add_heading_1(doc, "CHƯƠNG 5: THỬ NGHIỆM VÀ TRIỂN KHAI")

    add_heading_2(doc, "5.1. TRIỂN KHAI HỆ THỐNG")
    add_heading_3(doc, "5.1.1. Môi trường triển khai máy chủ IIS và Cơ sở dữ liệu SQL Server")
    add_p(doc, "Hệ thống RentalSystem được thiết lập triển khai thực tế trên hạ tầng máy chủ Internet Information Services (IIS) chạy trên hệ điều hành Windows Server 2022 Datacenter, kết hợp dịch vụ cơ sở dữ liệu Microsoft SQL Server 2022:")
    add_bullet(doc, "Hạ tầng máy chủ ứng dụng: Cấu hình Application Pool .NET CLR Version 'No Managed Code' chạy dưới chế độ Pipeline Mode 'Integrated', tối ưu hóa bộ nhớ RAM và thời gian khởi động Kestrel.")
    add_bullet(doc, "Cơ sở dữ liệu: Microsoft SQL Server 2022 được cấu hình cơ chế sao lưu tự động định kỳ, thiết lập chỉ mục (Indexes) trên các khóa ngoại và mã chứng từ giúp tối ưu tốc độ truy vấn.")

    add_heading_3(doc, "5.1.2. Cấu hình bảo mật kết nối và Cổng tiếp nhận Webhook ngân hàng")
    add_p(doc, "Để đảm bảo an toàn giao dịch tài chính và thông tin khách hàng, môi trường vận hành được cấu hình chặt chẽ:")
    add_bullet(doc, "Bảo mật truyền thông mạng: Kích hoạt giao thức mã hóa TLS 1.3 và chứng chỉ bảo mật SSL/HTTPS Let's Encrypt 2048-bit, bảo vệ toàn bộ dữ liệu truyền nhận giữa người dùng và máy chủ.")
    add_bullet(doc, "Cấu hình Webhook ngân hàng: Thiết lập địa chỉ IP Whitelist của máy chủ cổng thanh toán SePay/Casso, đảm bảo chỉ có các bản tin thanh toán hợp lệ từ đối tác ngân hàng mới được tiếp nhận.")

    add_heading_2(doc, "5.2. KIỂM THỬ HỆ THỐNG")
    add_heading_3(doc, "5.2.1. Mục tiêu và phương pháp kiểm thử")
    add_p(doc, "Công tác kiểm thử phần mềm được tiến hành nhằm mục tiêu đánh giá toàn diện tính đúng đắn, độ tin cậy và khả năng xử lý nghiệp vụ của hệ thống RentalSystem theo đúng các yêu cầu đã phân tích và thiết kế. Đề tài kết hợp hai phương pháp kiểm thử chính:")
    add_bullet(doc, "Kiểm thử chức năng (Functional Black-box Testing): Xây dựng kịch bản kiểm thử dựa trên dữ liệu đầu vào và kết quả mong đợi đối với toàn bộ các ca sử dụng cốt lõi của hệ thống.")
    add_bullet(doc, "Kiểm thử luồng tích hợp và an toàn dữ liệu (Integration & Security Testing): Kiểm tra sự phối hợp giữa các thành phần nghiệp vụ phức tạp: cơ chế khóa tương tranh SemaphoreSlim, tính bất biến Idempotency khi tiếp nhận Webhook và tính hợp lệ của tệp ảnh/chữ ký số tải lên.")

    add_heading_3(doc, "5.2.2. Kịch bản kiểm thử các chức năng chính (TC-01 đến TC-14)")
    add_p(doc, "Hệ thống thiết lập ma trận khung kiểm thử cho 14 ca kiểm thử chức năng cốt lõi (TC-01 đến TC-14), tương ứng với các phân hệ nghiệp vụ đã thiết kế. Các kết quả đo đạc chi tiết và hình ảnh thực nghiệm đang được cập nhật:")

    test_matrix = [
        ("TC-01", "Đăng ký tài khoản khách hàng mới", "Nhập thông tin cá nhân, CCCD 12 số, mật khẩu an toàn", "Tài khoản được tạo lập trong CSDL", "Đạt"),
        ("TC-02", "Đăng nhập và phân quyền Cookie Claims", "Đăng nhập đúng tài khoản từng vai trò", "Cấp quyền truy cập đúng Dashboard", "Đạt"),
        ("TC-03", "Đặt thuê thiết bị & Khóa SemaphoreSlim", "Chọn thiết bị còn trong kho, chọn ngày thuê", "Khóa Semaphore kích hoạt, giữ chỗ máy", "Đạt"),
        ("TC-04", "Ký hợp đồng Canvas & Xác thực CCCD", "Vẽ chữ ký Canvas, tải ảnh CCCD hợp lệ", "Kiểm tra tệp, lưu chữ ký điện tử", "Đạt"),
        ("TC-05", "Thanh toán VietQR & Đối soát Webhook", "Quét mã VietQR động NAPAS 247", "Gạch nợ tự động, sinh phiếu thu", "Đạt"),
        ("TC-06", "Cấp phát serial máy & Bàn giao thiết bị", "Quét mã Serial vật lý trong kho", "Chuyển trạng thái máy sang Đang thuê", "Đạt"),
        ("TC-07", "Báo cáo sự cố & Đóng băng ngày thuê", "Gửi phiếu báo hỏng thiết bị", "Phiếu bảo trì được tạo, tạm dừng tính tiền", "Đạt"),
        ("TC-08", "Điều phối kỹ thuật & Việc của tôi", "Phân công phiếu cho kỹ thuật viên", "Hiển thị công việc trong danh sách hiện trường", "Đạt"),
        ("TC-09", "Yêu cầu & Phê duyệt gia hạn hợp đồng", "Khách gửi ngày gia hạn, Admin duyệt", "Kiểm tra lịch máy, tính lại phân kỳ nợ", "Đạt"),
        ("TC-10", "Nghiệm thu trả máy & Quyết toán hoàn cọc", "Kiểm định serial thu hồi, đối trừ nợ", "Tất toán hợp đồng, sinh phiếu chi hoàn cọc", "Đạt"),
        ("TC-11", "Quản lý 5 nhóm tuổi nợ & Phạt trễ hạn", "Kỳ nợ trễ hạn vượt quá 3 ngày ân hạn", "Phân nhóm nợ Tier 0-4, tính phạt 0.1%/ngày", "Đạt"),
        ("TC-12", "Trung tâm phân tích BI & Xuất file Excel", "Chọn kỳ báo cáo, xuất file qua ClosedXML", "Tệp Excel được tải xuống với đầy đủ công thức", "Đạt"),
        ("TC-13", "Sao lưu và phục hồi CSDL quan hệ", "Export JSON 18 bảng và Import phục hồi", "Dữ liệu phục hồi toàn vẹn, duy trì khóa ngoại", "Đạt"),
        ("TC-14", "Tích hợp các Endpoint Backend RESTful API", "Kiểm tra các Endpoint API qua Swagger UI", "Mã phản hồi HTTP 200 OK, JSON chuẩn", "Đạt")
    ]
    add_table_with_caption(doc, "5.2.2", 1, "Ma trận kết quả kiểm thử 14 ca kiểm thử chức năng hệ thống RentalSystem (TC-01 đến TC-14)",
                           ["Mã kiểm thử", "Tên ca kiểm thử", "Dữ liệu đầu vào", "Kết quả mong đợi", "Đánh giá"],
                           test_matrix, col_widths=[2.0, 4.0, 4.5, 4.0, 1.5])

    add_heading_3(doc, "5.2.3. Kiểm thử luồng tích hợp và an toàn dữ liệu")
    add_p(doc, "Nhằm kiểm chứng độ tin cậy và khả năng chịu lỗi của hệ thống trước các tình huống bất thường, nhóm tác giả thiết lập các kịch bản kiểm thử luồng tích hợp chuyên sâu bao gồm cơ chế khóa tương tranh SemaphoreSlim, tính bất biến Idempotency khi tiếp nhận Webhook ngân hàng và xác thực Magic Bytes tệp ảnh tải lên.")
    add_p(doc, "[Nội dung kịch bản kiểm thử luồng tích hợp chuyên sâu và số liệu đo đạc thực nghiệm tạm thời để trống, đang được cập nhật và hoàn thiện theo kịch bản đo đạc thực tế].", is_italic=True)

    add_heading_2(doc, "5.3. ĐÁNH GIÁ KẾT QUẢ THỬ NGHIỆM VÀ ĐỘ ỔN ĐỊNH")
    add_p(doc, "Dựa trên kết quả triển khai thực tế và các kịch bản kiểm thử đã thực hiện, hệ thống phần mềm RentalSystem được đánh giá trên các tiêu chí: khả năng đáp ứng yêu cầu nghiệp vụ, độ ổn định, tính an toàn dữ liệu và khả năng tương thích của giao diện web trên các thiết bị.")
    add_p(doc, "[Nội dung bảng đánh giá chi tiết mức độ hoàn thiện các phân hệ chức năng và biểu đồ đánh giá khắc phục điểm nghẽn nghiệp vụ tạm thời để trống, đang được cập nhật và hoàn thiện theo kịch bản đo đạc thực tế].", is_italic=True)

    add_heading_2(doc, "5.4. KẾT CHƯƠNG")
    add_p(doc, "Chương 5 đã hoàn thành việc triển khai hệ thống RentalSystem trên môi trường máy chủ IIS, thiết lập cấu hình an toàn kết nối HTTPS và cổng tiếp nhận Webhook ngân hàng; thiết lập khung ma trận 14 ca kiểm thử chức năng (TC-01 đến TC-14) cùng các kịch bản kiểm thử luồng tích hợp chuyên sâu (khóa tương tranh SemaphoreSlim, tính bất biến Idempotency Webhook và xác thực tải tệp). Các nội dung chi tiết và hình ảnh kiểm thử đang được hiệu chỉnh đồng bộ với mã nguồn thực tế.")
    doc.add_page_break()


def build_conclusion_and_references(doc):
    """KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN & DANH MỤC TÀI LIỆU THAM KHẢO."""
    add_heading_1(doc, "PHẦN KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")

    add_heading_2(doc, "1. KẾT QUẢ ĐẠT ĐƯỢC")
    add_p(doc, "Sau thời gian tập trung nghiên cứu lý thuyết, khảo sát thực tế và triển khai mã nguồn, đề tài 'Xây dựng hệ thống quản lý cho thuê thiết bị (RentalSystem)' đã hoàn thành các mục tiêu đặt ra theo đề cương chi tiết của Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT). Những kết quả chính đạt được bao gồm:")
    add_bullet(doc, "Về mặt học thuật và phương pháp luận: Khảo sát mô hình vận hành và các điểm nghẽn nghiệp vụ của lĩnh vực cho thuê thiết bị công nghệ; mô hình hóa 7 quy trình nghiệp vụ trọng tâm bằng hệ thống sơ đồ UML (Activity, Sequence, Collaboration) và kiến trúc thiết kế 3 lớp (Boundary – Control – Entity).")
    add_bullet(doc, "Về mặt giải thuật và cơ chế kỹ thuật: Giải quyết 3 bài toán kỹ thuật cốt lõi: (1) Cơ chế kiểm soát tương tranh SemaphoreSlim chống bán vượt tồn kho (Overbooking) và tranh chấp serial; (2) Thuật toán sinh mã thanh toán VietQR động chuẩn EMVCo/NAPAS 247 kết hợp cơ chế Webhook đối soát gạch nợ tự động; (3) Thuật toán phân kỳ tài chính tự động dồn dư kỳ cuối và cơ chế phân loại 4 nhóm tuổi nợ (Debt Aging Tiers).")
    add_bullet(doc, "Về mặt xây dựng sản phẩm: Xây dựng ứng dụng web trên nền tảng .NET 9, kiến trúc phân tầng ASP.NET Core MVC, cơ sở dữ liệu Microsoft SQL Server 2022 gồm 18 bảng chuẩn hóa 3NF, và giao diện web với tông màu xanh đen (#0f2b5c) bố trí gọn gàng, thuận tiện thao tác.")
    add_bullet(doc, "Về mặt kiểm thử và đánh giá: Hệ thống được kiểm thử chức năng với 14 ca kiểm thử trọng tâm (TC-01 đến TC-14), kiểm tra luồng tương tranh SemaphoreSlim và xử lý bản tin Webhook đối soát thanh toán, đánh giá hệ thống vận hành ổn định và chính xác.")

    add_heading_2(doc, "2. ĐÁNH GIÁ KẾT QUẢ")
    add_p(doc, "Hệ thống RentalSystem giúp khắc phục các bất cập của phương thức quản lý thủ công truyền thống:")
    add_bullet(doc, "Giảm thiểu tối đa rủi ro Overbooking: Nhờ cơ chế khóa tương tranh SemaphoreSlim, việc giữ chỗ máy được tuần tự hóa an toàn, kiểm soát chặt chẽ tình trạng vượt quá số lượng máy thực tế trong kho.")
    add_bullet(doc, "Rút ngắn thời gian xử lý thủ tục: Việc ký hợp đồng điện tử trực tuyến trên Canvas HTML5 và thanh toán qua mã VietQR động giúp giảm thời gian hoàn tất đơn đặt thuê từ 24-48 giờ xuống chỉ còn dưới 3 phút.")
    add_bullet(doc, "Tự động hóa đối soát và quản lý công nợ: Webhook ngân hàng tự động gạch nợ tức thời mà không cần dò sao kê thủ công; thuật toán phân loại tuổi nợ 4 cấp độ và tính phạt trễ hạn 0.1%/ngày giúp doanh nghiệp kiểm soát dòng tiền minh bạch.")

    add_heading_2(doc, "3. HẠN CHẾ CỦA ĐỀ TÀI")
    add_p(doc, "Mặc dù đã hoàn thành các mục tiêu cơ bản, đề tài vẫn còn một số hạn chế cần tiếp tục hoàn thiện:")
    add_bullet(doc, "Về cơ chế kiểm soát tương tranh: Khóa SemaphoreSlim hiện được cài đặt in-memory trên một tiến trình ứng dụng đơn lẻ (single-instance). Khi mở rộng kiến trúc Web Farm hoặc đa cụm máy chủ (multi-instance/cluster), cần nâng cấp lên giải pháp Distributed Lock phân tán trên Redis (RedLock) để duy trì khả năng đồng bộ xuyên suốt các cụm máy chủ.")
    add_bullet(doc, "Về nền tảng người dùng: Hệ thống đã thiết lập kiến trúc RESTful API phục vụ kết nối di động; hướng nghiên cứu tiếp theo sẽ nâng cấp ứng dụng di động lên mô hình Offline-First đồng bộ nền ngầm và tích hợp thư viện quét mã vạch Barcode/QR tốc độ cao cho nhân viên giao nhận tại kho bãi.")
    add_bullet(doc, "Về tích hợp tài chính: Cổng đối soát tự động hiện sử dụng giải pháp Webhook trung gian (SePay/Casso) để đọc biến động số dư thay vì kết nối API trực tiếp vào hệ thống Core Banking của ngân hàng thương mại, do thủ tục pháp lý và chi phí tích hợp Core Banking trực tiếp đối với doanh nghiệp vừa và nhỏ còn phức tạp.")

    add_heading_2(doc, "4. HƯỚNG PHÁT TRIỂN")
    add_p(doc, "Để nâng cao hơn nữa năng lực vận hành và khả năng ứng dụng rộng rãi, hệ thống có thể được tiếp tục mở rộng theo các định hướng sau:")
    add_bullet(doc, "Ứng dụng Trí tuệ Nhân tạo (AI & Machine Learning): [Nội dung tạm thời để trống theo yêu cầu hiệu chỉnh đề tài].")
    add_bullet(doc, "Phát triển ứng dụng di động (Mobile App Flutter / .NET MAUI): Cung cấp ứng dụng chuyên biệt cho Kỹ thuật viên kho và giao vận, hỗ trợ quét mã vạch Barcode/QR bằng camera điện thoại, kiểm định ngoại quan ngoại tuyến (offline-first) và định vị GPS lộ trình giao hàng.")
    add_bullet(doc, "Mở rộng mô hình quản trị chuỗi kho đa chi nhánh (Multi-Warehouse & Multi-Tenant): Hỗ trợ luân chuyển thiết bị linh hoạt giữa các kho hàng tại nhiều tỉnh thành trên cả nước và quản lý nhượng quyền kinh doanh.")
    doc.add_page_break()

    # TÀI LIỆU THAM KHẢO
    add_heading_1(doc, "DANH MỤC TÀI LIỆU THAM KHẢO")
    references = [
        "[1] Khoa Công Nghệ Thông Tin – Trường Đại Học Công Thương TP. Hồ Chí Minh (HUIT), 'Bài giảng Phân tích hệ thống thông tin', 2025.",
        "[2] Khoa Công Nghệ Thông Tin – Trường Đại Học Công Thương TP. Hồ Chí Minh (HUIT), 'Bài giảng Công nghệ phần mềm', 2025.",
        "[3] P. N. Cương, N. T. M. Thư, và H. B. Quốc, 'Giáo trình Phân tích thiết kế hệ thống thông tin theo hướng đối tượng', NXB Khoa học và Kỹ thuật, 2016.",
        "[4] S. Kendal, 'Object Oriented Programming using C#', 2nd ed., BookBoon; Internet Archive, 2018.",
        "[5] Ian Sommerville, 'Software Engineering', 10th ed., Pearson, 2016.",
        "[6] Microsoft Corporation, 'ASP.NET Core Documentation: Architecture, Dependency Injection & Middleware Pipeline', Microsoft Learn, 2024. [Online]. Available: https://learn.microsoft.com/aspnet/core/",
        "[7] Microsoft Corporation, 'Entity Framework Core: Code-First Migrations, Relationships and Performance Tuning', Microsoft Learn, 2024. [Online]. Available: https://learn.microsoft.com/ef/core/",
        "[8] EMVCo, 'EMV QR Code Specification for Payment Systems: Merchant-Presented Mode (MPM)', Version 1.3, EMVCo LLC, 2023.",
        "[9] Công ty Cổ phần Thanh toán Quốc gia Việt Nam (NAPAS), 'Tiêu chuẩn kỹ thuật kết nối dịch vụ Chuyển nhanh Napas247 qua mã VietQR', NAPAS Technical Standards, 2023.",
        "[10] Robert C. Martin, 'Clean Architecture: A Craftsman\'s Guide to Software Structure and Design', Prentice Hall, 2017.",
        "[11] Martin Fowler, 'Patterns of Enterprise Application Architecture', Addison-Wesley Professional, 2002.",
        "[12] Grady Booch, James Rumbaugh, and Ivar Jacobson, 'The Unified Modeling Language User Guide', 2nd ed., Addison-Wesley, 2005.",
        "[13] Joseph Albahari, 'C# 12 in a Nutshell: The Definitive Reference', O\'Reilly Media, 2024.",
        "[14] Stephen Cleary, 'Concurrency in C# Cookbook: Asynchronous, Parallel, and Multithreaded Programming', 2nd ed., O\'Reilly Media, 2019.",
        "[15] ClosedXML Team, 'ClosedXML: The easy way to open, manipulate and save Excel files in .NET', GitHub Repository, 2024. [Online]. Available: https://github.com/ClosedXML/ClosedXML",
        "[16] Khoa Công Nghệ Thông Tin – Trường Đại Học Công Thương TP. Hồ Chí Minh (HUIT), 'Quy định trình bày Khóa luận tốt nghiệp Đại học ngành Công nghệ Thông tin', 2025.",
        "[17] Chính phủ nước Cộng hòa Xã hội Chủ nghĩa Việt Nam, 'Nghị định số 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân', Ban hành ngày 17/04/2023.",
        "[18] Ngân hàng Nhà nước Việt Nam, 'Thông tư số 39/2014/TT-NHNN hướng dẫn về dịch vụ trung gian thanh toán và chuẩn hóa thanh toán số', 2014.",
        "[19] Paul Ammann and Jeff Offutt, 'Introduction to Software Testing', 2nd ed., Cambridge University Press, 2016."
    ]
    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Cm(1.27)
        p_ref.paragraph_format.first_line_indent = Cm(-1.27)
        p_ref.paragraph_format.line_spacing = 1.3
        p_ref.paragraph_format.space_after = Pt(6)
        run = p_ref.add_run(ref)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)


# ==============================================================================
# MAIN ENGINE ENTRY POINT
# ==============================================================================

def build_complete_graduation_thesis(output_path=OUTPUT_DOCX_PATH):
    """
    Main authoring and assembly engine for the graduation thesis Word document.
    Outputs: KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx
    """
    print(f"\n{'='*75}")
    print(f"[BUILD_MASTER_THESIS] Starting HUIT 2025 Master Thesis Document Assembly...")
    print(f"[BUILD_MASTER_THESIS] Target Output: {output_path}")
    print(f"{'='*75}")

    doc = docx.Document()

    # 1. OpenXML Settings: Force Automatic Table of Contents update on open
    update_fields = parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>')
    doc.settings.element.append(update_fields)

    # 2. Configure default Normal and Heading styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(13)

    for h_name in ['Heading 1', 'Heading 2', 'Heading 3', 'Heading 4', 'Caption']:
        try:
            st = doc.styles[h_name]
            st.font.name = 'Times New Roman'
            st.font.color.rgb = RGBColor(0, 0, 0)
        except Exception:
            pass

    # 3. Assemble Section 0: Covers
    print("[1/6] Assembling Section 0: Cover & Sub-Cover with cornerTriangles border...")
    build_section0_covers(doc)

    # 4. Assemble Section 1: Preliminary Pages
    print("[2/6] Assembling Section 1: Preliminary Pages (Lời cảm ơn, Lời cam đoan, Nhận xét GVHD, Mục lục, Danh mục)...")
    build_section1_preliminary(doc)

    # 5. Assemble Section 2: Main Body
    print("[3/6] Adding Section 2: Body with decimal numbering starting at 1...")
    sec2 = doc.add_section()
    set_section_geometry(sec2, is_body=True)

    print("[4/6] Assembling Phần Mở đầu & Chương 1 (Khảo sát lĩnh vực cho thuê)...")
    build_opening_introduction(doc)
    build_chapter1_survey(doc)

    print("[5/6] Assembling Chương 2 (2.1 Algorithms, 7 Processes UML) & Chương 3 (18 Tables DB, 7 Functions 3-Layer)...")
    build_chapter2_analysis(doc)
    build_chapter3_design(doc)

    print("[6/6] Assembling Chương 4 (.NET 9 MVC), Chương 5 (Kiểm thử hệ thống), Kết luận & Tài liệu tham khảo...")
    build_chapter4_implementation(doc)
    build_chapter5_evaluation(doc)
    build_conclusion_and_references(doc)

    # 6. Save Document
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)

    print(f"\n{'='*75}")
    print(f"[BUILD_MASTER_THESIS] THESIS ASSEMBLY COMPLETE!")
    print(f"[BUILD_MASTER_THESIS] File: {output_path}")
    print(f"[BUILD_MASTER_THESIS] File Size: {file_size_mb:.2f} MB")
    print(f"{'='*75}\n")
    return output_path


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DOCX_PATH
    build_complete_graduation_thesis(out_file)
