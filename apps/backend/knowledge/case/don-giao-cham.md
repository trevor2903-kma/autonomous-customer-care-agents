---
intent: order_status
title: Đơn giao chậm / chưa nhận được
applies_when: khách đã đặt nhưng lâu chưa nhận (nhắc số ngày, "chưa thấy hàng", "sao lâu vậy")
questions:
  - "đặt mấy hôm rồi chưa nhận được"
  - "đơn giao lâu quá"
  - "sao ship lâu thế"
---
# Đơn giao chậm / chưa nhận được

## Triệu chứng
Khách báo đã đặt một số ngày nhưng chưa nhận được hàng.

## Bot Diagnostic Flow
1. Hỏi **mã đơn** (nếu khách chưa cung cấp).
2. Hỏi **ngày đặt** và **khu vực nhận** (toàn quốc hay đảo/vùng đặc biệt).
3. Đối chiếu thời gian dự kiến (2–5 ngày toàn quốc; đảo/vùng đặc biệt 8–14 ngày):
   - Nếu **còn trong thời gian dự kiến** → trấn an, nêu mốc giao dự kiến, nhắc khách theo dõi qua mã vận đơn (email).
   - Nếu **đã quá thời gian dự kiến** → xin lỗi, báo sẽ kiểm tra với đơn vị vận chuyển và **chuyển nhân viên** xử lý.
4. Lưu ý đơn được giao lại tối đa 3 lần; nếu nghi thất bại giao hàng, xác minh trước.
5. **Không** tự hứa hoàn tiền/đền bù — do nhân viên quyết sau khi kiểm tra.

## Internal Note (cho CSKH)
Kiểm tra trạng thái vận đơn với đơn vị giao; nếu thất lạc/hoàn kho, xử lý hoàn tiền theo phương thức thanh toán ban đầu.
