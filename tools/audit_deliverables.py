import docx, re, sys

sys.stdout.reconfigure(encoding='utf-8')

for fname in ['KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx', 'BaoCao_KLCN058_Final.docx']:
    print(f'=== AUDITING: {fname} ===')
    doc = docx.Document(fname)
    
    all_text = ' '.join([p.text for p in doc.paragraphs])
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                all_text += ' ' + cell.text
                
    # Check 1: ICT mentions
    ict_matches = re.findall(r'\bICT\b|\bICT\s+Sài\s+Gòn\b|\bICT\s+Saigon\b|\bNguyễn\s+Đình\s+Chiểu\b|\b0906\b', all_text, re.IGNORECASE)
    print(f'1. ICT / Company mentions: {len(ict_matches)} (Expected: 0)')
    
    # Check 2: Personal account
    acc_matches = re.findall(r'0783406516|PHAN\s+MINH\s+QUAN', all_text, re.IGNORECASE)
    print(f'2. Personal MBBank Account: {len(acc_matches)} (Expected: 0)')
    
    # Check 3: 'động cơ' translation
    dc_matches = re.findall(r'\bđộng\s+cơ\b', all_text, re.IGNORECASE)
    print(f'3. "Động cơ" machine translation: {len(dc_matches)} (Expected: 0)')
    
    # Check 4: Fabricated test claims (540 / 595 / Likert)
    fake_matches = re.findall(r'\b540\b|\b595\b|\bLikert\b', all_text, re.IGNORECASE)
    print(f'4. Fabricated 540/595/Likert testing claims: {len(fake_matches)} (Expected: 0)')
    
    # Check 5: 12 Use Case tables (UC-01 to UC-12)
    uc_count = len(re.findall(r'\bUC-(?:0[1-9]|1[0-2])\b', all_text))
    print(f'5. Distinct Use Case specifications: {uc_count} (Expected >= 12)')
    
    # Check 6: C# syntax check in docx
    has_cs_fix = '"Thiết bị đã có người đặt trong khoảng ngày này."' in all_text
    has_cs_bug = "'Thiết bị đã có người đặt trong khoảng ngày này.'" in all_text
    print(f'6. C# Syntax: Fixed double quotes = {has_cs_fix}, Bug single quotes = {has_cs_bug}')
    
    # Check 7: Hạn chế của đề tài
    has_han_che = '3. HẠN CHẾ CỦA ĐỀ TÀI' in all_text or 'Hạn chế của đề tài' in all_text
    print(f'7. Mandatory "Hạn chế của đề tài" section: {has_han_che}')
    
    # Check 8: Nhận xét GVHD
    has_blank_lines = '..................................................' in all_text
    has_fake_praise = 'Đồng ý cho sinh viên được bảo vệ' in all_text
    print(f'8. GVHD blank lines = {has_blank_lines}, Pre-filled fake praise = {has_fake_praise}')
    
    # Check 9: References check
    has_toeic_ref = 'TOEIC' in all_text
    has_ict_ref = 'Hồ sơ năng lực và Quy trình vận hành cho thuê' in all_text
    has_nd13_ref = 'Nghị định số 13/2023/NĐ-CP' in all_text
    print(f'9. Bad TOEIC sample ref = {has_toeic_ref}, Bad ICT ref = {has_ict_ref}, Decree 13 ref = {has_nd13_ref}')
    
    # Check 10: Automatic TOC setting
    import zipfile
    with zipfile.ZipFile(fname) as z:
        has_update = "updateFields" in z.read("word/settings.xml").decode("utf-8", errors="ignore")
    print(f'10. Automatic TOC updateFields = {has_update}')
    print(f'    Total paragraphs: {len(doc.paragraphs)}, Total tables: {len(doc.tables)}')
    print()
