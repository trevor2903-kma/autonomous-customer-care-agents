---
intent: refund
title: Yêu cầu hoàn tiền / trả hàng
applies_when: khách yêu cầu hoàn tiền hoặc trả hàng cho một đơn cụ thể
questions:
  - "cho tôi hoàn tiền"
  - "trả hàng lấy lại tiền"
  - "không thích nữa trả được không"
  - "muốn được refund"
---
# Yêu cầu hoàn tiền / trả hàng

## Triệu chứng
Khách yêu cầu **hoàn tiền / trả hàng** cho một đơn cụ thể.

## Bot Diagnostic Flow
1. Hỏi **mã đơn**, **sản phẩm** muốn trả và **lý do**.
2. **Đối chiếu sản phẩm với đơn**: sản phẩm khách muốn trả phải có trong đơn. **Không có** → **dừng** ở đây: nêu
   đơn gồm những sản phẩm nào và hỏi khách sản phẩm đó thuộc đơn khác (xin mã đơn đó) hay muốn trả một sản phẩm
   trong đơn này; **không** phân loại lý do, **không** nhắc điều kiện hoàn tiền.
3. Phân loại lý do:
   - **Hàng lỗi / giao sai / khác mô tả** → thuộc diện hoàn tiền → **chuyển nhân viên**.
   - **Đổi ý / không vừa** với hàng đúng mô tả → vẫn được trả trong **30 ngày** nếu hàng **chưa dùng/giặt, còn nguyên tag** → kiểm tra điều kiện rồi **chuyển nhân viên**.
4. Nhắc điều kiện: trong **30 ngày** kể từ khi nhận, hàng nguyên trạng, có mã đơn; đồ lót/đồ bơi đã mở niêm phong không áp dụng.
5. **Tuyệt đối không xác nhận đã hoàn tiền** — việc hoàn do nhân viên thực hiện sau khi duyệt.

## Internal Note
Hoàn về đúng kênh thanh toán ban đầu; phí vận chuyển (nếu có) không hoàn; lỗi NSX áp dụng trong 6 tháng.
