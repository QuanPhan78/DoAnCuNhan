# -*- coding: utf-8 -*-
with open('tools/build_master_thesis.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'add_heading_3(doc, "2.3.3. Thiết kế kiến trúc Backend RESTful API chuẩn OpenAPI / Swagger")\n    add_p(doc, "Nhằm tạo nền tảng backend vững chắc và sẵn sàng tích hợp với các ứng dụng máy khách di động trong tương lai, hệ thống thiết lập kiến trúc Backend RESTful API chuẩn mực. Các máy khách (Client Apps) trao đổi dữ liệu JSON hai chiều thông qua giao thức HTTPS bảo mật, xác thực qua cơ chế JWT Token (JSON Web Token) và tuân thủ các mã phản hồi HTTP tiêu chuẩn:")'

replacement = 'add_heading_3(doc, "2.3.3. Thiết kế kiến trúc Backend RESTful API theo đặc tả OpenAPI / Swagger")\n    add_p(doc, "Để hỗ trợ trao đổi dữ liệu với các ứng dụng máy khách và mở rộng tích hợp trong tương lai, hệ thống thiết lập các dịch vụ Backend RESTful API. Các ứng dụng máy khách (Client Apps) trao đổi dữ liệu định dạng JSON thông qua giao thức HTTPS bảo mật, xác thực bằng cơ chế JWT Token (JSON Web Token) và sử dụng các mã phản hồi HTTP tiêu chuẩn:")'

has_crlf = '\r\n' in text
text = text.replace('\r\n', '\n')

if target in text:
    text = text.replace(target, replacement)
    if has_crlf:
        text = text.replace('\n', '\r\n')
    with open('tools/build_master_thesis.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('SUCCESS')
else:
    print('TARGET NOT FOUND')
