with open(r'D:/DoAnCuNhan/Rose_Diagrams/RentalSystem_Master.mdl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("All lines with 'UC-KH01':")
for i, l in enumerate(lines, 1):
    if 'UC-KH01' in l:
        print(f"{i:5d}: {l.strip()}")

print("\nAll lines with 'UC-AD01':")
for i, l in enumerate(lines, 1):
    if 'UC-AD01' in l:
        print(f"{i:5d}: {l.strip()}")
