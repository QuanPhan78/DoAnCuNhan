#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/adversarial_scanner.py
Empirical Adversarial Scanner for Graduation Thesis Verification.
Tests KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx and tools/build_master_thesis.py:
  1. Forbidden AI fluff phrases
  2. Forbidden roles & Canonical Role Consistency (Admin, KinhDoanh, KyThuat, KhachHang)
  3. Automatic TOC & Heading outline levels
  4. C# Consistency & Technical Assertions
  5. ChallengerTests execution (dotnet test)
"""

import os
import re
import sys
import zipfile
import subprocess
import unicodedata
import docx

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCX_PATH = os.path.join(PROJECT_ROOT, "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx")
SCRIPT_PATH = os.path.join(PROJECT_ROOT, "tools", "build_master_thesis.py")
CHALLENGER_CSPROJ = os.path.join(PROJECT_ROOT, "ChallengerTests", "ChallengerTests.csproj")

FORBIDDEN_AI_PHRASES = [
    "bức tranh toàn cảnh",
    "tiền đề vững chắc",
    "bước tiến vượt bậc",
    "hoàn thành một cách trọn vẹn",
    "đóng vai trò như một trái tim của hệ thống",
    "vận hành vững chắc",
    "độc nhất",
]

FORBIDDEN_ROLES = [
    "Thủ quỹ",
    "Kế toán tài chính",
    "Ban Giám đốc",
    "Trưởng phòng Kỹ thuật",
    "Quản lý kỹ thuật",
]

# Additional phrases to probe
EXTENDED_AI_PHRASES = [
    "bước đột phá vượt bậc",
    "trái tim của hệ thống",
    "nền tảng vững chắc",
    "hoàn toàn không có sai sót",
    "vận hành hoàn hảo",
]

CANONICAL_ROLES = ["Admin", "KinhDoanh", "KyThuat", "KhachHang"]


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_docx_all_texts(docx_path):
    """Extract all text items with context: paragraphs, table cells, headers, footers."""
    doc = docx.Document(docx_path)
    items = []

    # Paragraphs
    for p_idx, p in enumerate(doc.paragraphs):
        t = normalize_text(p.text)
        if t:
            items.append((f"p[{p_idx}] (style={p.style.name if p.style else 'None'})", t))

    # Tables
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                t = normalize_text(cell.text)
                if t:
                    items.append((f"table[{t_idx}].r[{r_idx}].c[{c_idx}]", t))

    # Headers and Footers
    for s_idx, sec in enumerate(doc.sections):
        for hp_idx, p in enumerate(sec.header.paragraphs):
            t = normalize_text(p.text)
            if t:
                items.append((f"sec[{s_idx}].header.p[{hp_idx}]", t))
        for fp_idx, p in enumerate(sec.footer.paragraphs):
            t = normalize_text(p.text)
            if t:
                items.append((f"sec[{s_idx}].footer.p[{fp_idx}]", t))

    return items


def scan_file_text(text_content, phrases, label):
    """Search for literal or regex matches in text content."""
    matches = {}
    for phrase in phrases:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        found = pattern.findall(text_content)
        if found:
            matches[phrase] = len(found)
    return matches


def scan_docx_items(items, phrases):
    """Scan structured items in docx."""
    results = {}
    for phrase in phrases:
        pat = re.compile(re.escape(phrase), re.IGNORECASE)
        matched_locs = []
        for loc, text in items:
            if pat.search(text):
                matched_locs.append((loc, text))
        if matched_locs:
            results[phrase] = matched_locs
    return results


def check_role_ketoan(items, script_content):
    """
    Specifically audit 'Kế toán'.
    Verify whether any system actor or role assignment uses 'Kế toán'.
    """
    findings = {"docx": [], "script": []}
    pat_ketoan = re.compile(r"kế\s+toán", re.IGNORECASE)

    # In docx
    for loc, text in items:
        if pat_ketoan.search(text):
            # Check context: is it referring to legacy process, or a role/actor in RentalSystem?
            findings["docx"].append((loc, text))

    # In script
    for line_no, line in enumerate(script_content.splitlines(), start=1):
        if pat_ketoan.search(line):
            findings["script"].append((line_no, line.strip()))

    return findings


def check_openxml_toc_and_headings(docx_path):
    """Verify TOC field instruction and Heading outlineLvl in OpenXML."""
    results = {
        "has_toc_field": False,
        "toc_instruction": None,
        "has_update_fields": False,
        "heading_styles_outline": {},
    }

    with zipfile.ZipFile(docx_path, "r") as z:
        # Check document.xml for TOC
        doc_xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
        toc_fld_match = re.search(r'<w:fldSimple[^>]*w:instr="([^"]*TOC[^"]*)"', doc_xml)
        if toc_fld_match:
            results["has_toc_field"] = True
            results["toc_instruction"] = toc_fld_match.group(1)
        else:
            # Also check w:instrText inside fldChar
            instr_match = re.search(r'<w:instrText[^>]*>([^<]*TOC[^<]*)</w:instrText>', doc_xml)
            if instr_match:
                results["has_toc_field"] = True
                results["toc_instruction"] = instr_match.group(1)

        # Check word/settings.xml for updateFields
        if "word/settings.xml" in z.namelist():
            settings_xml = z.read("word/settings.xml").decode("utf-8", errors="ignore")
            if "updateFields" in settings_xml:
                results["has_update_fields"] = True

        # Check styles.xml for Heading 1..4 outline levels
        if "word/styles.xml" in z.namelist():
            styles_xml = z.read("word/styles.xml").decode("utf-8", errors="ignore")
            for h_level in [1, 2, 3, 4]:
                style_id = f"Heading{h_level}"
                # check style definition
                m_style = re.search(rf'<w:style[^>]*w:styleId="{style_id}"[^>]*>(.*?)</w:style>', styles_xml, re.DOTALL)
                if m_style:
                    content = m_style.group(1)
                    has_outline = "w:outlineLvl" in content
                    val_match = re.search(r'<w:outlineLvl\s+w:val="(\d+)"', content)
                    lvl_val = val_match.group(1) if val_match else None
                    results["heading_styles_outline"][style_id] = {
                        "present": True,
                        "has_outlineLvl": has_outline,
                        "outline_val": lvl_val,
                    }
                else:
                    results["heading_styles_outline"][style_id] = {"present": False}

    return results


def run_challenger_tests():
    """Run dotnet run --project ChallengerTests and capture output."""
    cmd = ["dotnet", "run", "--project", CHALLENGER_CSPROJ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=PROJECT_ROOT,
            timeout=120,
        )
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
        }
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


def main():
    print("================================================================================")
    print("EMPIRICAL ADVERSARIAL SCANNER: THESIS VERIFICATION")
    print("================================================================================")
    print(f"Target Docx: {DOCX_PATH}")
    print(f"Target Script: {SCRIPT_PATH}")

    # Read build_master_thesis.py
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        script_content = f.read()

    # Read docx items
    docx_items = extract_docx_all_texts(DOCX_PATH)
    docx_full_text = " ".join([t for _, t in docx_items])

    print(f"Loaded docx with {len(docx_items)} textual units (paragraphs + table cells).")

    # TEST 1: FORBIDDEN AI FLUFF PHRASES
    print("\n--- TEST 1: FORBIDDEN AI FLUFF PHRASES ---")
    script_ai_hits = scan_file_text(script_content, FORBIDDEN_AI_PHRASES, "build_master_thesis.py")
    docx_ai_hits = scan_docx_items(docx_items, FORBIDDEN_AI_PHRASES)

    print(f"[build_master_thesis.py] AI Fluff hits: {len(script_ai_hits)}")
    for phrase, count in script_ai_hits.items():
        print(f"  ❌ HIT: '{phrase}' (count={count})")

    print(f"[DOCX] AI Fluff hits: {len(docx_ai_hits)}")
    for phrase, locs in docx_ai_hits.items():
        print(f"  ❌ HIT: '{phrase}' (found in {len(locs)} places)")
        for loc, snippet in locs[:3]:
            print(f"     at {loc}: {snippet[:100]}...")

    # Extended AI phrases
    print("\n--- TEST 1b: EXTENDED AI FLUFF PROBE ---")
    script_ext_hits = scan_file_text(script_content, EXTENDED_AI_PHRASES, "build_master_thesis.py")
    docx_ext_hits = scan_docx_items(docx_items, EXTENDED_AI_PHRASES)
    print(f"[build_master_thesis.py] Extended AI hits: {len(script_ext_hits)}")
    for p, c in script_ext_hits.items():
        print(f"  ⚠️ Hit: '{p}' ({c})")
    print(f"[DOCX] Extended AI hits: {len(docx_ext_hits)}")
    for p, locs in docx_ext_hits.items():
        print(f"  ⚠️ Hit: '{p}' ({len(locs)})")

    # TEST 2: FORBIDDEN ROLES
    print("\n--- TEST 2: FORBIDDEN ROLES ---")
    script_role_hits = scan_file_text(script_content, FORBIDDEN_ROLES, "build_master_thesis.py")
    docx_role_hits = scan_docx_items(docx_items, FORBIDDEN_ROLES)

    print(f"[build_master_thesis.py] Forbidden role hits: {len(script_role_hits)}")
    for role, count in script_role_hits.items():
        print(f"  ❌ HIT: '{role}' (count={count})")

    print(f"[DOCX] Forbidden role hits: {len(docx_role_hits)}")
    for role, locs in docx_role_hits.items():
        print(f"  ❌ HIT: '{role}' (found in {len(locs)} places)")
        for loc, snippet in locs[:3]:
            print(f"     at {loc}: {snippet[:100]}...")

    # TEST 2b: AUDIT KẾ TOÁN
    print("\n--- TEST 2b: AUDIT 'KẾ TOÁN' OCCURRENCES ---")
    ketoan_findings = check_role_ketoan(docx_items, script_content)
    print(f"[build_master_thesis.py] 'Kế toán' line occurrences: {len(ketoan_findings['script'])}")
    for line_no, line in ketoan_findings["script"]:
        print(f"  Line {line_no}: {line[:120]}")

    print(f"[DOCX] 'Kế toán' item occurrences: {len(ketoan_findings['docx'])}")
    for loc, snippet in ketoan_findings["docx"]:
        print(f"  Location {loc}: {snippet[:120]}")

    # TEST 3: TOC & HEADING OUTLINE LEVELS
    print("\n--- TEST 3: AUTOMATIC TOC & HEADING OUTLINE LEVELS ---")
    toc_results = check_openxml_toc_and_headings(DOCX_PATH)
    print(f"Has TOC field: {toc_results['has_toc_field']} (instr='{toc_results['toc_instruction']}')")
    print(f"Has updateFields in settings.xml: {toc_results['has_update_fields']}")
    for h_style, h_info in toc_results["heading_styles_outline"].items():
        print(f"  {h_style}: present={h_info['present']}, outlineLvl={h_info.get('outline_val')}")

    # TEST 4: CANONICAL ROLE & C# CONSISTENCY AUDIT
    print("\n--- TEST 4: CANONICAL ROLES & C# ARCHITECTURE CONSISTENCY ---")
    for r in CANONICAL_ROLES:
        count_doc = len(re.findall(re.escape(r), docx_full_text))
        count_scr = len(re.findall(re.escape(r), script_content))
        print(f"  Canonical Role '{r}': docx occurrences = {count_doc}, script occurrences = {count_scr}")

    # Key mechanisms check
    mech_checks = {
        "SemaphoreSlim": "SemaphoreSlim",
        "VietQR / NAPAS 247": r"VietQR|NAPAS",
        "BankingWebhook": r"BankingWebhook|PaymentController",
        "Canvas HTML5 / CCCD": r"Canvas|CCCD",
        "Debt Aging (4 groups)": r"4\s*nhóm|tuổi\s*nợ|Current|1-30",
        "ClosedXML": "ClosedXML",
    }
    for label, pat in mech_checks.items():
        m_count = len(re.findall(pat, docx_full_text, re.IGNORECASE))
        print(f"  Mechanism '{label}': {m_count} matches in docx")

    # TEST 5: RUN CHALLENGER TESTS
    print("\n--- TEST 5: RUN CHALLENGERTESTS SUITE ---")
    test_res = run_challenger_tests()
    print(f"Return code: {test_res['returncode']}")
    # Extract test summary
    summary_match = re.search(r"TEST RESULTS SUMMARY:\s*(\d+)\s*PASSED,\s*(\d+)\s*FAILED", test_res["stdout"])
    if summary_match:
        passed, failed = summary_match.groups()
        total = str(int(passed) + int(failed))
        skipped = "0"
    else:
        summary_match = re.search(r"Passed:\s*(\d+),\s*Failed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)", test_res["stdout"])
        if not summary_match:
            summary_match = re.search(r"Total tests:\s*(\d+)\.\s*Passed:\s*(\d+)\.\s*Failed:\s*(\d+)\.\s*Skipped:\s*(\d+)", test_res["stdout"])
            if summary_match:
                total, passed, failed, skipped = summary_match.groups()
            else:
                passed = failed = skipped = total = "N/A"
        else:
            passed, failed, skipped, total = summary_match.groups()

    print(f"Test Execution Summary: Total={total}, Passed={passed}, Failed={failed}, Skipped={skipped}")
    if int(failed) if failed.isdigit() else 1 > 0:
        print("❌ FAILURES DETECTED in ChallengerTests:")
        for line in test_res["stdout"].splitlines():
            if "Failed" in line or "Error" in line:
                print(f"   {line}")
    else:
        print("✅ ALL TESTS PASSED.")

    # OVERALL VERDICT
    print("\n================================================================================")
    print("VERDICT CALCULATION")
    print("================================================================================")
    fail_reasons = []
    if script_ai_hits:
        fail_reasons.append(f"build_master_thesis.py contains forbidden AI fluff: {list(script_ai_hits.keys())}")
    if docx_ai_hits:
        fail_reasons.append(f"DOCX contains forbidden AI fluff: {list(docx_ai_hits.keys())}")
    if script_role_hits:
        fail_reasons.append(f"build_master_thesis.py contains forbidden roles: {list(script_role_hits.keys())}")
    if docx_role_hits:
        fail_reasons.append(f"DOCX contains forbidden roles: {list(docx_role_hits.keys())}")
    if len(ketoan_findings["docx"]) > 0:
        # Check if ketoan is in non-canonical context
        fail_reasons.append(f"DOCX contains {len(ketoan_findings['docx'])} occurrences of 'Kế toán'")
    if len(ketoan_findings["script"]) > 0:
        fail_reasons.append(f"build_master_thesis.py contains {len(ketoan_findings['script'])} occurrences of 'Kế toán'")
    if not toc_results["has_toc_field"]:
        fail_reasons.append("DOCX is missing w:fldSimple TOC field")
    if not toc_results["has_update_fields"]:
        fail_reasons.append("DOCX is missing updateFields in settings.xml")
    if failed != "0" or test_res["returncode"] != 0:
        fail_reasons.append(f"ChallengerTests failed: returncode={test_res['returncode']}, failed={failed}")

    if fail_reasons:
        print("OVERALL VERDICT: REJECT ❌")
        for r in fail_reasons:
            print(f"  - {r}")
    else:
        print("OVERALL VERDICT: APPROVE ✅")
    print("================================================================================")


if __name__ == "__main__":
    main()
