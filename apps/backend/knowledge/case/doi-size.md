---
intent: exchange
title: Đổi size / đổi màu
applies_when: khách đã mua và muốn đổi sang size hoặc màu khác (không phải do lỗi)
questions:
  - "cho đổi size khác được không"
  - "áo rộng quá đổi size nhỏ hơn được không"
  - "muốn đổi sang màu khác"
---
# Đổi size / đổi màu

## Triệu chứng
Khách đã mua và muốn đổi sang **size/màu khác** (không phải do hàng lỗi).

## Bot Diagnostic Flow
1. Hỏi **mã đơn**, **size/màu hiện tại** và **size/màu muốn đổi**.
2. Kiểm tra điều kiện đổi: trong **30 ngày** kể từ khi nhận, hàng **chưa sử dụng/giặt, còn nguyên tag & nhãn**,
   không thuộc nhóm đồ lót/đồ bơi đã mở niêm phong.
3. Hướng xử lý:
   - Nếu size/màu muốn đổi **còn hàng** → **chuyển nhân viên** để xử lý đổi.
   - Nếu **hết hàng** → nêu phương án (chờ về hàng hoặc trả hàng để hoàn tiền) và **chuyển nhân viên**.
4. **Không** tự xác nhận đã đổi/đã hoàn — nhân viên thực hiện.

## Internal Note
Đơn online: đổi size/màu theo tồn kho; nếu không đủ điều kiện đổi, xử lý theo chính sách trả hàng 30 ngày.
