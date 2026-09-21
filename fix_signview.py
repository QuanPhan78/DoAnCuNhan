import os

path = r'd:\DoAnCuNhan\RentalSystem\Views\Cart\SignContract.cshtml'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the contract info display
old_info = '''                <p><strong>Tổng tiền:</strong> <span class="text-danger fw-bold">@Model.TongTien.ToString("N0") đ</span></p>
                <p><strong>Tiền đã cọc:</strong> <span class="text-success fw-bold">@Model.TienDaCoc.ToString("N0") đ</span></p>'''

new_info = '''                <p><strong>Tổng tiền:</strong> <span class="text-danger fw-bold">@Model.TongTien.ToString("N0") đ</span></p>
                <p><strong>Yêu cầu đặt cọc:</strong> <span class="text-warning fw-bold">@(((decimal?)ViewBag.TienCocYeuCau ?? 0).ToString("N0")) đ</span> <small class="text-muted">(Thanh toán khi nhận máy)</small></p>
                <p><strong>Tiền đã cọc:</strong> <span class="text-success fw-bold">@Model.TienDaCoc.ToString("N0") đ</span></p>'''
content = content.replace(old_info, new_info)

# 2. Add the dropdown inside the form
old_form = '''        <form asp-action="SignContract" method="post" enctype="multipart/form-data" id="signForm">
            @Html.AntiForgeryToken()
            <input type="hidden" name="id" value="@Model.MaHopDong" />'''

new_form = '''        <form asp-action="SignContract" method="post" enctype="multipart/form-data" id="signForm">
            @Html.AntiForgeryToken()
            <input type="hidden" name="id" value="@Model.MaHopDong" />
            
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
                    <h5 class="fw-bold text-brand"><i class="fas fa-hand-holding-usd me-2"></i> Lựa chọn Thanh toán</h5>
                </div>
                <div class="card-body">
                    <label class="form-label fw-bold">Số kỳ trả góp (Tùy chọn)</label>
                    <select name="soKyHan" class="form-select border-dark shadow-none w-50">
                        <option value="1">Trả 1 lần (Toàn bộ)</option>
                        <option value="2">Trả góp 2 đợt</option>
                        <option value="3">Trả góp 3 đợt</option>
                        <option value="4">Trả góp 4 đợt</option>
                        <option value="6">Trả góp 6 đợt</option>
                    </select>
                    <small class="text-muted d-block mt-2"><i class="fas fa-info-circle"></i> Tiền thuê sẽ được chia đều cho số kỳ hạn bạn chọn. Thanh toán định kỳ mỗi tháng/tuần tùy theo độ dài hợp đồng.</small>
                </div>
            </div>'''
content = content.replace(old_form, new_form)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
