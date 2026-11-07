#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empirical Adversarial Verification Suite for Thesis OpenXML Layout & Compliance.
Standards: HUIT 2025 Thesis Guidelines & ORIGINAL_REQUEST.md.
Target: KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx
"""

import os
import sys
import re
import zipfile
from lxml import etree

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_MAP = {"w": W_NS}
ATTR_W = f"{{{W_NS}}}"


class ThesisAdversarialAuditor:
    def __init__(self, docx_path: str):
        self.docx_path = os.path.abspath(docx_path)
        if not os.path.exists(self.docx_path):
            raise FileNotFoundError(f"Target document not found: {self.docx_path}")

        self.zip_file = zipfile.ZipFile(self.docx_path, "r")
        self.doc_xml = self.zip_file.read("word/document.xml")
        self.root = etree.fromstring(self.doc_xml)

        self.settings_xml = ""
        if "word/settings.xml" in self.zip_file.namelist():
            self.settings_xml = self.zip_file.read("word/settings.xml").decode("utf-8", errors="ignore")

        self.results = {}

    def audit_toc_field(self):
        """Verify presence of <w:fldSimple w:instr='TOC ...'> and updateFields in settings."""
        fld_simples = self.root.xpath("//w:fldSimple", namespaces=NS_MAP)
        toc_instrs = []
        for f in fld_simples:
            instr = f.attrib.get(f"{ATTR_W}instr", "")
            if "TOC" in instr:
                toc_instrs.append(instr)

        has_target_toc = any(
            re.search(r'TOC\s+\\o\s+["\']1-3["\']\s+\\h\s+\\z\s+\\u', instr)
            for instr in toc_instrs
        )

        has_update_fields = "<w:updateFields w:val=\"true\"/>" in self.settings_xml or "updateFields" in self.settings_xml

        # Check auxiliary TOCs (Figures and Tables)
        instr_texts = self.root.xpath("//w:instrText", namespaces=NS_MAP)
        aux_tocs = [it.text.strip() for it in instr_texts if it.text and "TOC" in it.text]

        passed = has_target_toc and has_update_fields
        self.results["TOC"] = {
            "passed": passed,
            "has_target_toc_fldSimple": has_target_toc,
            "toc_instructions": toc_instrs,
            "has_update_fields": has_update_fields,
            "auxiliary_tocs": aux_tocs,
        }
        return passed

    def audit_headings(self):
        """
        Verify all 82 headings (Heading 1, 2, 3, 4):
        - Have explicit <w:outlineLvl w:val="X"/>
        - Have explicit <w:keepNext/>
        - Zero headings have orphan status
        - Outline levels match heading style numbers
        """
        paras = self.root.xpath("//w:p", namespaces=NS_MAP)
        headings = []

        for idx, p in enumerate(paras):
            style_elem = p.xpath("./w:pPr/w:pStyle", namespaces=NS_MAP)
            style_val = style_elem[0].attrib.get(f"{ATTR_W}val") if style_elem else None

            outline_elem = p.xpath("./w:pPr/w:outlineLvl", namespaces=NS_MAP)
            outline_val = outline_elem[0].attrib.get(f"{ATTR_W}val") if outline_elem else None

            has_keep_next = len(p.xpath("./w:pPr/w:keepNext", namespaces=NS_MAP)) > 0
            text = "".join(p.xpath(".//w:t/text()", namespaces=NS_MAP)).strip()

            is_heading_style = bool(
                style_val and re.match(r"^heading\s*[1-4]$", style_val, re.IGNORECASE)
            )

            if is_heading_style or outline_val is not None:
                headings.append({
                    "idx": idx,
                    "text": text,
                    "style": style_val,
                    "outlineLvl": outline_val,
                    "keepNext": has_keep_next,
                })

        count = len(headings)
        missing_outline = [h for h in headings if h["outlineLvl"] is None]
        missing_keep_next = [h for h in headings if not h["keepNext"]]

        style_counts = {}
        hierarchy_mismatches = []
        for h in headings:
            st = h["style"] or "Unknown"
            style_counts[st] = style_counts.get(st, 0) + 1
            if h["style"] and re.match(r"^Heading([1-4])$", h["style"]):
                num = int(re.match(r"^Heading([1-4])$", h["style"]).group(1))
                expected_outline = str(num - 1)
                if h["outlineLvl"] != expected_outline:
                    hierarchy_mismatches.append(h)

        passed = (
            count == 82
            and len(missing_outline) == 0
            and len(missing_keep_next) == 0
            and len(hierarchy_mismatches) == 0
        )

        self.results["Headings"] = {
            "passed": passed,
            "total_count": count,
            "expected_count": 82,
            "breakdown": style_counts,
            "missing_outline_count": len(missing_outline),
            "missing_keep_next_count": len(missing_keep_next),
            "hierarchy_mismatch_count": len(hierarchy_mismatches),
            "orphan_risk_count": len(missing_keep_next),
        }
        return passed

    def audit_tables(self):
        """
        Verify all 47 tables:
        - Table width <= 8504 dxa (15.0cm)
        - <w:tblHeader/> on row 0
        - <w:cantSplit/> on all rows
        """
        tables = self.root.xpath("//w:tbl", namespaces=NS_MAP)
        table_count = len(tables)

        width_violations = []
        missing_header_tables = []
        rows_missing_cantsplit = []
        total_rows_inspected = 0

        for t_idx, tbl in enumerate(tables):
            # Check width
            tblW_elem = tbl.xpath("./w:tblPr/w:tblW", namespaces=NS_MAP)
            tbl_w_val = tblW_elem[0].attrib.get(f"{ATTR_W}w") if tblW_elem else None
            tbl_w_type = tblW_elem[0].attrib.get(f"{ATTR_W}type") if tblW_elem else None

            grid_cols = tbl.xpath("./w:tblGrid/w:gridCol", namespaces=NS_MAP)
            grid_w_sum = sum(int(c.attrib.get(f"{ATTR_W}w", 0)) for c in grid_cols) if grid_cols else 0

            effective_w = int(tbl_w_val) if (tbl_w_val and tbl_w_type == "dxa") else grid_w_sum
            if effective_w > 8504:
                width_violations.append({
                    "table_index": t_idx,
                    "width_dxa": effective_w,
                    "width_cm": round(effective_w / 567.0, 2),
                })

            # Check rows
            rows = tbl.xpath("./w:tr", namespaces=NS_MAP)
            if not rows:
                continue

            # Header row (row 0)
            has_tbl_header = len(rows[0].xpath("./w:trPr/w:tblHeader", namespaces=NS_MAP)) > 0
            if not has_tbl_header:
                missing_header_tables.append(t_idx)

            # All rows cantSplit
            for r_idx, r in enumerate(rows):
                total_rows_inspected += 1
                has_cant_split = len(r.xpath("./w:trPr/w:cantSplit", namespaces=NS_MAP)) > 0
                if not has_cant_split:
                    rows_missing_cantsplit.append((t_idx, r_idx))

        passed = (
            table_count == 47
            and len(width_violations) == 0
            and len(missing_header_tables) == 0
            and len(rows_missing_cantsplit) == 0
        )

        self.results["Tables"] = {
            "passed": passed,
            "total_tables": table_count,
            "expected_tables": 47,
            "width_violations_count": len(width_violations),
            "width_violations": width_violations,
            "missing_tblHeader_count": len(missing_header_tables),
            "total_rows_inspected": total_rows_inspected,
            "rows_missing_cantSplit_count": len(rows_missing_cantsplit),
        }
        return passed

    def audit_captions_and_figures(self):
        """
        Verify:
        - All 47 table captions immediately preceding a table have keepNext=True
        - All 81 figure images (paragraphs with w:drawing) have keepNext=True
        """
        paras = self.root.xpath("//w:p", namespaces=NS_MAP)

        tbl_captions_above_tables = []
        fig_images = []

        for idx, p in enumerate(paras):
            text = "".join(p.xpath(".//w:t/text()", namespaces=NS_MAP)).strip()
            keep_next = len(p.xpath("./w:pPr/w:keepNext", namespaces=NS_MAP)) > 0
            drawings = p.xpath(".//w:drawing", namespaces=NS_MAP)

            if drawings:
                fig_images.append({
                    "idx": idx,
                    "drawing_count": len(drawings),
                    "keepNext": keep_next,
                    "text": text[:40],
                })

            if re.match(r"^Bảng\s+\d", text):
                next_elem = p.getnext()
                if next_elem is not None and next_elem.tag.endswith("tbl"):
                    tbl_captions_above_tables.append({
                        "idx": idx,
                        "text": text[:60],
                        "keepNext": keep_next,
                    })

        missing_tbl_caption_keepnext = [c for c in tbl_captions_above_tables if not c["keepNext"]]
        missing_fig_img_keepnext = [f for f in fig_images if not f["keepNext"]]

        passed = (
            len(tbl_captions_above_tables) == 47
            and len(missing_tbl_caption_keepnext) == 0
            and len(fig_images) == 81
            and len(missing_fig_img_keepnext) == 0
        )

        self.results["CaptionsAndFigures"] = {
            "passed": passed,
            "table_captions_count": len(tbl_captions_above_tables),
            "expected_table_captions": 47,
            "table_captions_missing_keepnext": len(missing_tbl_caption_keepnext),
            "figure_images_count": len(fig_images),
            "expected_figure_images": 81,
            "figure_images_missing_keepnext": len(missing_fig_img_keepnext),
        }
        return passed

    def audit_margins(self):
        """
        Check margins across all sections:
        Left 3.5cm (or 3.0cm), Right 2.0-2.5cm, Top 2.0-2.5cm, Bottom 2.0-2.5cm.
        """
        sectPrs = self.root.xpath("//w:sectPr", namespaces=NS_MAP)
        section_details = []
        all_margins_valid = True

        for idx, sp in enumerate(sectPrs):
            pgMar = sp.xpath("./w:pgMar", namespaces=NS_MAP)
            if pgMar:
                m = pgMar[0]
                top = int(m.attrib.get(f"{ATTR_W}top", 0))
                bottom = int(m.attrib.get(f"{ATTR_W}bottom", 0))
                left = int(m.attrib.get(f"{ATTR_W}left", 0))
                right = int(m.attrib.get(f"{ATTR_W}right", 0))

                top_cm = round(top / 567.0, 2)
                bottom_cm = round(bottom / 567.0, 2)
                left_cm = round(left / 567.0, 2)
                right_cm = round(right / 567.0, 2)

                left_ok = 2.95 <= left_cm <= 3.55
                right_ok = 1.95 <= right_cm <= 2.55
                top_ok = 1.95 <= top_cm <= 2.55
                bottom_ok = 1.95 <= bottom_cm <= 2.55

                sec_valid = left_ok and right_ok and top_ok and bottom_ok
                if not sec_valid:
                    all_margins_valid = False

                section_details.append({
                    "section_index": idx,
                    "left_cm": left_cm,
                    "right_cm": right_cm,
                    "top_cm": top_cm,
                    "bottom_cm": bottom_cm,
                    "valid": sec_valid,
                })

        passed = len(sectPrs) >= 3 and all_margins_valid
        self.results["Margins"] = {
            "passed": passed,
            "sections_count": len(sectPrs),
            "section_details": section_details,
        }
        return passed

    def run_all(self):
        p1 = self.audit_toc_field()
        p2 = self.audit_headings()
        p3 = self.audit_tables()
        p4 = self.audit_captions_and_figures()
        p5 = self.audit_margins()

        verdict = "APPROVE" if (p1 and p2 and p3 and p4 and p5) else "REJECT"
        self.results["VERDICT"] = verdict
        return verdict


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx"
    print(f"=== EMPIRICAL ADVERSARIAL INSPECTION: {target} ===")

    auditor = ThesisAdversarialAuditor(target)
    verdict = auditor.run_all()

    for k, v in auditor.results.items():
        if k == "VERDICT":
            continue
        status = "[PASS]" if v.get("passed") else "[FAIL]"
        print(f"{status} {k}: {v}")

    print(f"\n=======================================================")
    print(f"FINAL ADVERSARIAL VERDICT: {verdict}")
    print(f"=======================================================")

    sys.exit(0 if verdict == "APPROVE" else 1)


if __name__ == "__main__":
    main()
