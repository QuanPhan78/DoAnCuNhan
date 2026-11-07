# -*- coding: utf-8 -*-
import sys, os, win32com.client

sys.stdout.reconfigure(encoding='utf-8')

word_path = os.path.abspath('KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx')

print(f"Opening Word document: {word_path}")
word = win32com.client.Dispatch("Word.Application")
word.Visible = False

try:
    doc = word.Documents.Open(word_path, ReadOnly=True)
    
    # Force pagination
    doc.Repaginate()
    total_pages = doc.ComputeStatistics(2) # 2 = wdStatisticPages
    print(f"Total pages computed by Word COM: {total_pages}")
    
    # Find all occurrences of "Hình 1.2. 1" and their page numbers
    print("\n--- Searching for 'Hình 1.2. 1' in Document ---")
    rng = doc.Content
    find = rng.Find
    find.Text = "Hình 1.2. 1"
    while find.Execute():
        page_num = rng.Information(1) # 1 = wdActiveEndPageNumber
        section_num = rng.Information(2) # 2 = wdActiveEndSectionNumber
        print(f"Found 'Hình 1.2. 1': Page {page_num}, Section {section_num}, text='{rng.Text.strip()}'")
    
    # Check what is on Page 98
    print(f"\n--- Inspecting Page 98 ---")
    if total_pages >= 98:
        # Go to page 98
        p98_rng = doc.GoTo(What=1, Which=1, Count=98) # wdGoToPage = 1, wdGoToAbsolute = 1
        p98_rng.End = doc.GoTo(What=1, Which=1, Count=99).Start if total_pages >= 99 else doc.Content.End
        text_p98 = p98_rng.Text
        print(f"Page 98 length: {len(text_p98)} chars")
        print("Page 98 text preview (first 300 chars):")
        print(repr(text_p98[:300]))
        print("\nHas InlineShapes on Page 98:", p98_rng.InlineShapes.Count)
        print("Has Shapes on Page 98:", p98_rng.Shapes.Count)

finally:
    doc.Close(False)
    word.Quit()
