---
intent: complaint
title: Hàng lỗi hoặc giao sai
applies_when: khách nhận hàng và phản ánh lỗi nhà sản xuất, giao sai sản phẩm/size, hoặc khác mô tả
questions:
  - "áo bị lỗi đường may"
  - "giao sai size"
  - "giao sai sản phẩm"
  - "hàng bị lỗi"
---
# Hàng lỗi hoặc giao sai

## Triệu chứng
Khách đã nhận hàng và phản ánh: **lỗi nhà sản xuất**, **giao sai** sản phẩm/size, hoặc **khác mô tả**.

## Bot Diagnostic Flow
1. Xin lỗi khách và hỏi **mã đơn**.
2. Đề nghị khách gửi **ảnh/video** cho thấy lỗi hoặc điểm sai.
3. Phân loại:
   - **Lỗi nhà sản xuất** (đường may, phai màu bất thường, lỗi vải…) → được đổi/trả (trong 6 tháng, có bằng chứng) → **chuyển nhân viên**.
   - **Giao sai sản phẩm/size** hoặc **khác mô tả** → thuộc diện đổi/trả → **chuyển nhân viên**.
4. **Không** tự khẳng định được/không được hoàn tiền — nhân viên xác minh ảnh và quyết định.

## Internal Note
Đối chiếu ảnh với sản phẩm/đơn; lỗi NSX áp dụng đổi/trả 6 tháng; giao sai thì đổi đúng sản phẩm hoặc hoàn tiền.
