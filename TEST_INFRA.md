# TEST INFRASTRUCTURE SPECIFICATION (TEST_INFRA.md)

**Project**: RentalSystem Graduation Thesis (HUIT 2025 Standard)  
**Agent**: E2E Test Writer (`test_writer_1`)  
**Date**: 2026-10-24  
**Authoritative Standards**: `2025_kltn_toeic+knn_1.pdf` & `Mau bao cao_Do an_Khoa luan_2025.docx` (Khoa CNTT - HUIT)

---

## 1. Test Harness Overview

The E2E test suite `test_thesis_quality.py` provides automated, opaque-box, deep OpenXML inspection and system-level validation for the RentalSystem Graduation Thesis Word document. The harness operates independently of word processors, parsing raw OpenXML packaging (`word/document.xml`, `word/settings.xml`, `word/media/`, `word/styles.xml`) and verifying physical geometries, formatting rules, structural requirements, technical modeling depth, empirical metrics, and live software health.

### Runtime Environment
- **Language**: Python 3.14.0 (Standard library `unittest`)
- **OpenXML Engine**: `python-docx` 1.2.0, `lxml` 6.1.2
- **Image Inspection Engine**: `Pillow` 13.0.0
- **Live System Probes**: `dotnet build` (C# 13 / .NET 9.0 SDK), `ChallengerTests.csproj` runner
- **OS / Platform**: Windows 11 (PowerShell / cmd compatible with UTF-8 console support)

---

## 2. Directory Layout & Test Artifacts

```
d:\DoAnCuNhan\
├── test_thesis_quality.py                         # Master E2E Test Suite (CLI runnable)
├── TEST_INFRA.md                                  # Test Infrastructure Specification
├── TEST_READY.md                                  # Test Readiness & Coverage Matrix
├── tests\
│   ├── fixture_builder.py                         # HUIT 2025 Compliant Fixture Generator
│   └── fixtures\
│       └── huit_thesis_fixture.docx               # Reference compliant test fixture
├── figures\                                       # 300 DPI UML & UI diagram assets (40+ PNGs)
├── ChallengerTests\                               # Live automated regression test project (595 tests)
├── RentalSystem\                                  # Core ASP.NET Core MVC application
├── KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx # Master target graduation thesis (M3 output)
└── BỘ CÔNG THƯƠNG.docx                            # Pre-existing draft (used for discrepancy detection)
```

---

## 3. 4-Tier Test Architecture

The test suite organizes 33 comprehensive test cases across four distinct tiers:

```
+--------------------------------------------------------------------------+
|            TIER 4: ACADEMIC SCENARIO & FACULTY RUBRIC (2 Tests)          |
|  - Holistic 10-Dimension Review Simulation (Score >= 90%, 100% on gold) |
|  - Forensic Discrepancy Detection on Legacy Draft (BỘ CÔNG THƯƠNG.docx)  |
+--------------------------------------------------------------------------+
                                     ^
+--------------------------------------------------------------------------+
|         TIER 3: COMBINATIONS & CROSS-CUTTING INTEGRITY (6 Tests)         |
|  - Caption-to-Media Pairing          - Table-to-Grid Structure           |
|  - Sequential Chapter Progression    - Heading Hierarchy Nesting         |
|  - TOC Auto-Update Setting           - 7 Processes / Functions Symmetry  |
+--------------------------------------------------------------------------+
                                     ^
+--------------------------------------------------------------------------+
|            TIER 2: BOUNDARY CASES & ROBUSTNESS (7 Tests)                 |
|  - Margin Dxa Tolerance Bounds       - Caption Syntax Variations         |
|  - Unicode NFC Normalization         - Corrupt/Missing File Handling     |
|  - Database Table Count >= 18        - DPI Float Boundary >= 290.0       |
|  - Likert Survey Sample N >= 50                                          |
+--------------------------------------------------------------------------+
                                     ^
+--------------------------------------------------------------------------+
|              TIER 1: FEATURE COVERAGE (18 Tests)                         |
|  - Section 0/1/2 Count & Setup       - cornerTriangles Border on Cover   |
|  - lowerRoman Prelim Numbering       - Lời Cam Đoan Position & Order     |
|  - Arabic Main Body Numbering        - Margins 3.5/2.5/2.5/2.5 cm        |
|  - Times New Roman 13pt / 1.3 / 6pt  - 5 Concluding Sections (1.4-5.4)   |
|  - Chapter 1 ICT Saigon Survey       - Section 2.1 Core 3 Algorithms     |
|  - Section 2.2 7 Processes UML       - Section 3.1 18 Tables DB ERD      |
|  - Section 3.4 7 Functions 3-Layer   - Chapter 4 .NET 9 MVC Impl         |
|  - Chapter 5 540 Tests & Likert      - Deep Captions (Hình/Bảng X.Y.Z. N)|
|  - 300 DPI Embedded Graphics         - Live dotnet build & Tests Health  |
+--------------------------------------------------------------------------+
```

---

## 4. Opaque-Box Inspection Engine: `DocumentQualityAuditor`

`DocumentQualityAuditor` inspects any Word `.docx` file using binary ZIP extraction and low-level DOM navigation:

1. **Section Geometry Probe**:
   - Reads `w:sectPr` across all sections.
   - Converts `w:pgMar` twips to exact cm and verifies tolerance windows.
   - Extracts `w:pgBorders` ensuring `w:display="firstPage"` with `cornerTriangles` attributes on all 4 borders.
   - Extracts `w:pgNumType` ensuring `fmt="lowerRoman"` on Section 1 and decimal on Section 2.

2. **Heading & Semantic Paragraph Probe**:
   - Normalizes text with `unicodedata.normalize("NFC", text)` to ensure robust Vietnamese diacritics comparison.
   - Identifies structural headings (`LỜI CẢM ƠN`, `LỜI CAM ĐOAN`, `NHẬN XÉT GVHD`, chapter headings, and all 5 `KẾT CHƯƠNG` sections).
   - Validates ordinal order `index(Lời cảm ơn) < index(Lời cam đoan) < index(Nhận xét GVHD)`.

3. **Deep Hierarchical Caption Parser**:
   - Regex: `^Hình\s+([0-9]+(?:\.[0-9]+)+)\.\s+([0-9]+)\s*:\s*(.+)$`
   - Regex: `^Bảng\s+([0-9]+(?:\.[0-9]+)+)\.\s+([0-9]+)\s*:\s*(.+)$`
   - Differentiates deep captions (requiring dot-space before sequence number `N`) from legacy 2-level captions (`Hình X.Y:`).

4. **Media & Resolution Probe**:
   - Extracts all binary streams in `word/media/`.
   - Uses Pillow to probe horizontal and vertical DPI (`dpi_x >= 290.0`).
   - Cross-references against vector-generated figures in `figures/`.

5. **Settings & Field Code Probe**:
   - Inspects `word/settings.xml` for `<w:updateFields w:val="true"/>`.

---

## 5. Execution Modes & CLI Reference

### A. Full Test Execution (Including Live Build and ChallengerTests)
```powershell
python test_thesis_quality.py
```
*Auto-detects `KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx` or uses reference fixture, runs all 33 tests, verifies `dotnet build` and `ChallengerTests`.*

### B. Fast Document-Only Verification (Skip Live Build)
```powershell
python test_thesis_quality.py --fast
```
*Executes all 32 document formatting, section geometry, and rubric tests in < 0.5s.*

### C. Test Specific Document Target
```powershell
python test_thesis_quality.py --docx "d:\DoAnCuNhan\KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx"
```

### D. Standalone Forensic Audit Mode
```powershell
python test_thesis_quality.py --audit "d:\DoAnCuNhan\BỘ CÔNG THƯƠNG.docx"
```
*Outputs a complete diagnostic audit table comparing the document against all HUIT 2025 requirements.*

### E. Standard `unittest` Discovery
```powershell
python -m unittest test_thesis_quality.py -v
```
