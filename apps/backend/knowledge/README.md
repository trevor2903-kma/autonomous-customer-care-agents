# Kho tri thức (Knowledge Base) — ThriftYourStyle (thời trang hàng mới)

Thư mục này là **nguồn chân lý (canonical)** cho RAG. File `.md` ở đây được script `ingest_kb.py`
duyệt → tách frontmatter → chunk theo section → embed vào Qdrant (**Reset-and-reingest**). Sửa nội dung
ở đây rồi chạy lại ingest là bot áp dụng bản mới.

## Quy ước
- **Thư mục = `type`**: `faq/`, `case/`, `reference/`. Ingest suy `type` từ tên thư mục (không cần ghi `type`).
- **`facts.md`**: sự thật lõi LUÔN nạp vào prompt Agent 4, **KHÔNG** đưa vào Qdrant.
- **Khuyến mãi có giới hạn / một lần** KHÔNG để ở đây → upload ad-hoc qua UI (non-canonical, mất khi rebuild toàn bộ).
  Chỉ KM **tái diễn/định kỳ** mới cho vào `promotion/`.

## Frontmatter theo loại
- faq:       `intent`, `title`, `questions: [...]`
- case:      `intent`, `title`, `applies_when`, `questions: [...]`  + thân có `## Bot Diagnostic Flow`
- reference: `intent` (bỏ nếu đa-intent), `title`
- facts.md:  chỉ `title`

## Tập intent (khớp 1-1 với enum `Intent` trong code — CODE là nguồn chuẩn)
Thông tin — không nhạy cảm → tự trả lời:
  `product_price` · `product_information` · `size_consulting` · `shipping` · `order_status` ·
  `promotion` · `payment` · `membership` · `return_exchange_policy` · `store_information` · `greeting`
Giao dịch — nhạy cảm → qua gate / duyệt nháp:
  `refund` · `exchange` · `complaint`
Ngoài phạm vi:
  `other`

> So với bản 10 intent cũ, thêm: `greeting` (sửa lỗi "xin chào"→out_of_domain), `return_exchange_policy`
> (HỎI chính sách — sửa lỗi bị dán `refund` rồi bắt duyệt), `payment`, `membership` (hợp với shop kiểu Uniqlo),
> `store_information` (giờ mở cửa/địa chỉ/hotline — cùng lỗi escalate oan như "xin chào").
> `greeting` KHÔNG có file KB — Agent 4 trả câu chào mẫu.

## ⚠️ Giá trị đang là MẪU — thay theo shop của bạn
Trong `facts.md` và `reference/`: phí ship, ngưỡng freeship (500.000đ), thời gian giao, cửa sổ đổi/trả
(30 ngày), bảng size, hotline, giờ làm việc, kênh thanh toán, chương trình thành viên. Chỉnh theo thực tế.
