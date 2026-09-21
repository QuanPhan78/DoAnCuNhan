import os

path = r'd:\DoAnCuNhan\RentalSystem\Models\DbInitializer.cs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace PC images
content = content.replace(
    'HinhAnh = "https://cdn.tgdd.vn/Products/Images/5706/325421/dell-optiplex-7010-mff-plus-i5-71010928-600x600.jpg"',
    'HinhAnh = "/images/sanpham/may-tinh.png"'
)
content = content.replace(
    'HinhAnh = "https://cdn.tgdd.vn/Products/Images/5706/310971/hp-prodesk-400-g9-i7-72k73pa-600x600.jpg"',
    'HinhAnh = "/images/sanpham/may-tinh.png"'
)

# Replace AC images
content = content.replace(
    'HinhAnh = "https://cdn.tgdd.vn/Products/Images/2002/235800/daikin-ftkz35vvmv-1-600x600.jpg"',
    'HinhAnh = "/images/sanpham/may-lanh.png"'
)
content = content.replace(
    'HinhAnh = "https://cdn.tgdd.vn/Products/Images/2002/220137/lg-apnq48gt3e4-600x600.jpg"',
    'HinhAnh = "/images/sanpham/may-lanh.png"'
)

# Replace Printer images
content = content.replace(
    'HinhAnh = "https://cdn.tgdd.vn/Products/Images/5765/229753/hp-laserjet-pro-m404dn-w1a53a-600x600.jpg"',
    'HinhAnh = "/images/sanpham/may-in.png"'
)
content = content.replace(
    'HinhAnh = "https://cdn.tgdd.vn/Products/Images/5765/236025/canon-pixma-g3020-600x600.jpg"',
    'HinhAnh = "/images/sanpham/may-in.png"'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
