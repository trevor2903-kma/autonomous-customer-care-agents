# Tài liệu phân loại Intent — Shop Quần áo (seed để test RAG)

> **Mục đích:** seed cho Qdrant để Intent Classifier (PRD §7.1) phân loại intent của khách theo RAG.
> **Quy ước chunk:** mỗi mục `## <intent_id>` = MỘT chunk (embed riêng). Payload lưu: `intent`, `category`,
> `text`, `source`. Phần "Ví dụ câu khách" là thứ quyết định độ chính xác truy hồi — viết càng sát giọng
> khách thật càng tốt.
> **Đây là tài liệu TEST tối giản** — KHÔNG phải nguồn chân lý (PRD.md mới là). Tập intent theo PRD §7.1.

---

## product_price
- category: pre_sale
- Mô tả: Khách hỏi GIÁ của sản phẩm — bao nhiêu tiền, giá niêm yết, giá sỉ/lẻ, giá theo màu/size.
- Ví dụ câu khách:
  - "Áo này bao nhiêu tiền vậy shop?"
  - "Cho mình xin giá cái váy hoa ở hình 2"
  - "Quần jean ống rộng giá nhiêu ạ?"
  - "Set đồ này tổng bao nhiêu tiền?"
  - "Mua 3 cái có giá sỉ không shop?"
  - "Giá áo khoác dạ là bao nhiêu thế?"

## product_information
- category: pre_sale
- Mô tả: Khách hỏi THÔNG TIN sản phẩm (không phải giá) — chất liệu, màu sắc, còn hàng không, form dáng, xuất xứ.
- Ví dụ câu khách:
  - "Áo này còn màu trắng không shop?"
  - "Chất vải cái đầm này là gì vậy?"
  - "Quần này form rộng hay ôm ạ?"
  - "Áo thun này còn hàng không?"
  - "Váy này dài tới đâu vậy shop?"
  - "Cái áo len này có bị xù lông không?"

## size_consulting
- category: pre_sale
- Mô tả: Khách nhờ TƯ VẤN CHỌN SIZE dựa trên cân nặng/chiều cao/số đo; hỏi size nào vừa.
- Ví dụ câu khách:
  - "Mình cao 1m60 nặng 50kg thì mặc size gì shop?"
  - "Áo này size M vừa người 55kg không ạ?"
  - "Vòng eo 68 thì chọn size mấy?"
  - "Tư vấn giúp em size với, em 1m70 65kg"
  - "Size L có rộng quá với người 48kg không?"
  - "Bảng size của cái quần này thế nào ạ?"

## shipping
- category: general
- Mô tả: Khách hỏi VẬN CHUYỂN — phí ship, thời gian giao, giao tỉnh, ship COD, đơn vị vận chuyển.
- Ví dụ câu khách:
  - "Ship về Đà Nẵng bao nhiêu tiền shop?"
  - "Mấy ngày thì hàng tới nơi vậy ạ?"
  - "Shop có giao hàng thu tiền tận nơi (COD) không?"
  - "Phí ship nội thành bao nhiêu thế?"
  - "Đặt hôm nay thì bao giờ nhận được?"
  - "Có freeship cho đơn trên 500k không ạ?"

## order_status
- category: after_sale
- Mô tả: Khách hỏi TRẠNG THÁI ĐƠN đã đặt — đơn tới đâu rồi, đã giao chưa, mã vận đơn, khi nào nhận.
- Ví dụ câu khách:
  - "Đơn 1234 của mình tới đâu rồi shop?"
  - "Em đặt hàng 3 ngày rồi mà chưa thấy giao"
  - "Cho mình xin mã vận đơn với ạ"
  - "Đơn hàng của mình đã gửi đi chưa?"
  - "Bao giờ thì đơn ABC123 giao tới?"
  - "Kiểm tra giúp mình đơn đặt hôm qua với"

## refund
- category: after_sale
- Mô tả: Khách muốn TRẢ HÀNG / HOÀN TIỀN — chính sách hoàn tiền, điều kiện trả, hoàn tiền về đâu.
- Ví dụ câu khách:
  - "Mình muốn trả lại cái áo này và lấy lại tiền"
  - "Sản phẩm bị lỗi, cho em hoàn tiền được không?"
  - "Chính sách hoàn tiền của shop thế nào ạ?"
  - "Không vừa thì trả hàng hoàn tiền được không?"
  - "Bao lâu thì được hoàn tiền sau khi trả hàng?"
  - "Đơn 1234 mình muốn yêu cầu hoàn tiền"

## exchange
- category: after_sale
- Mô tả: Khách muốn ĐỔI HÀNG — đổi size, đổi màu, đổi mẫu khác; điều kiện & thời hạn đổi.
- Ví dụ câu khách:
  - "Cho mình đổi sang size L được không shop?"
  - "Áo bị chật, em muốn đổi cái to hơn"
  - "Đổi màu khác có được không ạ?"
  - "Muốn đổi mẫu khác thì làm sao shop?"
  - "Thời hạn đổi hàng là mấy ngày vậy?"
  - "Đổi hàng có mất phí ship không ạ?"

## complaint
- category: after_sale
- Mô tả: Khách KHIẾU NẠI / PHÀN NÀN — hàng lỗi/sai, thái độ phục vụ, giao chậm, bức xúc, đòi gặp quản lý.
- Ví dụ câu khách:
  - "Shop giao sai màu cho mình rồi, xử lý sao đây?"
  - "Áo bị rách chỉ ngay khi vừa nhận, quá tệ"
  - "Mình đặt 1 tuần rồi mà chưa giao, thất vọng thật sự"
  - "Nhân viên tư vấn thái độ quá, tôi muốn gặp quản lý"
  - "Hàng không giống hình, shop lừa đảo à?"
  - "Đây là lần cuối tôi mua ở đây, dịch vụ quá kém"

## promotion
- category: pre_sale
- Mô tả: Khách hỏi KHUYẾN MÃI — mã giảm giá, chương trình sale, ưu đãi thành viên, quà tặng kèm.
- Ví dụ câu khách:
  - "Shop đang có chương trình giảm giá nào không ạ?"
  - "Có mã giảm giá cho khách mới không shop?"
  - "Mua 2 tặng 1 còn áp dụng không vậy?"
  - "Sale mấy phần trăm thế shop?"
  - "Thành viên có được ưu đãi gì không ạ?"
  - "Nhập mã nào để được freeship vậy shop?"

## other
- category: general
- Mô tả: Câu KHÔNG thuộc các nhóm trên hoặc ngoài phạm vi shop — chào hỏi, cảm ơn, hỏi lan man, spam.
- Ví dụ câu khách:
  - "Alo shop ơi"
  - "Cảm ơn shop nhiều nha"
  - "Shop mở cửa mấy giờ vậy?"
  - "Địa chỉ cửa hàng ở đâu ạ?"
  - "Hôm nay trời đẹp ha"
  - "abcxyz test test"
