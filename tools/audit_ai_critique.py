# -*- coding: utf-8 -*-
import docx, re, sys, os

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docx_path = os.path.join(PROJECT_ROOT, 'KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx')
doc = docx.Document(docx_path)
full_text = '\n'.join([p.text for p in doc.paragraphs])

# Also check tables
table_text = []
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            table_text.append(cell.text)
full_doc_text = full_text + '\n' + '\n'.join(table_text)

print('=== 1. KIỂM TRA SỐ LIỆU CHƯƠNG 5 TRONG FILE WORD ===')
print('Matches for 540:', re.findall(r'540', full_doc_text))
print('Matches for 595:', re.findall(r'595', full_doc_text))
print('Matches for 100 luồng / 100 Tasks:', re.findall(r'100\s*(?:luồng|Tasks|task)', full_doc_text, re.I))
print('Matches for 61 lỗi:', re.findall(r'61\s*lỗi', full_doc_text, re.I))
print('Matches for 12 ca sử dụng:', len(re.findall(r'12\s*ca\s+sử\s+dụng', full_doc_text, re.I)))
print('Matches for 13 ca sử dụng:', len(re.findall(r'13\s*ca\s+sử\s+dụng', full_doc_text, re.I)))
print('Matches for 12 ca kiểm thử:', len(re.findall(r'12\s*ca\s+kiểm\s+thử', full_doc_text, re.I)))
print('Matches for 14 ca kiểm thử:', len(re.findall(r'14\s*ca\s+kiểm\s+thử', full_doc_text, re.I)))

print('\n=== 2. KIỂM TRA LỌT TỪ KHÓA ĐỀ CƯƠNG / MÔN HỌC ===')
for kw in ['CLO3', 'CLO6', 'CLO', 'Đề cương chi tiết', 'CNTT-KLCN058', 'Doanh nghiệp']:
    matches = re.findall(rf'{re.escape(kw)}', full_doc_text, re.I)
    print(f'Keyword "{kw}": {len(matches)} matches')

print('\n=== 3. KIỂM TRA TỪ NGỮ NÓI QUÁ ===')
for kw in ['triệt để', 'tuyệt đối', 'nghiêm ngặt', 'toàn diện', 'vững chắc']:
    matches = re.findall(rf'{kw}', full_doc_text, re.I)
    print(f'Word "{kw}": {len(matches)} matches')

print('\n=== 4. KIỂM TRA PLACEHOLDER & TIÊU ĐỀ ===')
print('Matches for Update Field / Nhấn chuột phải:', len(re.findall(r'update\s*field|nhấn\s*chuột\s*phải', full_doc_text, re.I)))
print('Matches for Cán bộ phản biện:', re.findall(r'phản\s+biện.*', full_doc_text, re.I))
print('Matches for Mojibake (¡¢£¤¥):', len(re.findall(r'[¡¢£¤¥]', full_doc_text)))

print('\n=== 5. KIỂM TRA TRÍCH DẪN [n] TRONG THÂN BÀI ===')
citations = re.findall(r'\[\d+\]', full_text)
print('In-text citations found in paragraphs:', len(citations), set(citations[:10]))


print('\n=== 6. KIỂM TRA REVIEW 2 (BẢN NHÁP CŨ) ===')
terms = ['¡', '¢', '£', '¤', '¥', 'TinhTrangBanGia', 'SỐ ĐỒ LỚP', 'NOCCHECK', 'aspxnet', 'Bang dac ta', 'Cau truc tir dien', 'tuan tq']
for term in terms:
    print(f'Term "{term}": {full_doc_text.count(term)} occurrences')
