# Kết quả refactor RAG/Knowledge — số liệu trước/sau

> Đo ngày **2026-07-23** · KB `apps/backend/knowledge/` (15 tài liệu → **95 point** Qdrant) ·
> `ENABLE_LLM=true`, embeddings `text-embedding-3-small`, `retrieval_threshold=0.40`.
> Ngưỡng đo riêng ở [`retrieval-threshold.md`](./retrieval-threshold.md).

## 1. Hai lỗi đặt hàng — trước/sau

Cột "trước" **suy từ mã cũ** (tất định, không phải đo lại): taxonomy cũ map chào hỏi → `other`, và
`other` → cờ `out_of_domain` ∈ `BLOCKING_FLAGS` → `human_handoff`; luật prompt cũ map "hỏi chính sách
đổi trả" → `refund`, mà `refund` có `send_directly=false` → giữ nháp chờ duyệt.

| Câu khách | Trước | Sau (đo) |
| --- | --- | --- |
| "xin chào shop" | `other` + `out_of_domain` → **chuyển người** | `greeting` → **gửi thẳng** câu chào |
| "cảm ơn shop nhiều nha" | `other` + `out_of_domain` → **chuyển người** | `greeting` → **gửi thẳng** câu chào |
| "cho mình xin chính sách trả hàng với" | `refund` → **duyệt nháp** | `return_exchange_policy` → **gửi thẳng** |
| "mua rồi mặc thử không vừa thì đổi trong bao lâu ạ" | `refund` → **duyệt nháp** | `return_exchange_policy` → **gửi thẳng** |

Sửa `greeting` cần **hai** chỗ, không phải một: đổi nhãn ở Agent 1 mới chỉ chuyển cờ chặn từ
`out_of_domain` sang `low_retrieval_score` (KB không có nội dung chào hỏi nên retrieve luôn yếu). Phải
thêm `NO_RETRIEVAL_INTENTS` ở Agent 2 — lượt xã giao không phát biểu sự thật nào nên **không có gì để
"không grounded"** — và cho nhánh câu-chào-mẫu ở Agent 4 chạy **trước** phanh `rag_contexts` rỗng →
FALLBACK.

## 2. Phân bố kết cục trên bộ 20 câu khách

Bộ 20 câu trộn đủ nhóm (xã giao, tra cứu, giao dịch, lạc đề). Kết cục giao theo PRD §9.

| Kết cục | Số câu | Tỉ lệ |
| --- | --- | --- |
| Gửi thẳng | 16/20 | **80%** |
| Duyệt nháp (`refund`/`exchange`/`complaint`) | 3/20 | 15% |
| Chuyển người (`out_of_domain`) | 1/20 | 5% |
| **FALLBACK oan** | **0/20** | **0%** |
| Trả lời được nội dung thật | 19/20 | 95% |

Câu duy nhất chuyển người là "cho mình hỏi vé xem phim tối nay" — **đúng** (ngoài phạm vi shop). Ba câu
duyệt nháp đều là ca giao dịch nhạy cảm — **đúng**, gate không bị nới nhầm khi thêm 5 intent mới.

## 3. Chất lượng truy hồi

Trên tập 32 câu trả-lời-được (giọng khác `questions[]` trong KB):

| Chỉ số | Giá trị |
| --- | --- |
| Điểm cosine top-1 (median) | 0.648 |
| Câu khớp qua query-expansion | 26/32 (81%) |
| Câu khớp thân tài liệu | 6/32 (19%) |
| Câu dưới ngưỡng 0.40 (escalate oan) | 1/32 (3%) |

**Query-expansion là thứ kéo chất lượng lên**: khách hỏi bằng giọng nói thường, KB viết bằng giọng văn
bản; embed câu-hỏi-với-câu-hỏi ăn điểm hơn hẳn câu-hỏi-với-văn-bản (median 0.702 so với 0.542).

## 4. Bám quy trình & grounding hành động

| Câu khách | Hành vi đo được |
| --- | --- |
| "em đặt mấy hôm rồi chưa thấy hàng" | contexts `[case, faq, faq, case]` → bot **hỏi mã đơn trước**, đúng bước 1 của `## Bot Diagnostic Flow` |
| "đơn 6578 hàng bị lỗi, cho em hoàn tiền" | hỏi lý do + *"sẽ chuyển thông tin tới nhân viên hỗ trợ"* — **không** nói đã hoàn tiền |
| "ship về Đà Nẵng hết bao nhiêu" | *"30.000đ… từ 500.000đ trở lên được miễn phí"* — số liệu thật |
| "thẻ thành viên hạng kim cương cần bao nhiêu điểm" | *"không có thông tin cụ thể… sẽ chuyển nhân viên"* — không bịa |

4 file `case/*.md` có section `## Internal Note (cho CSKH)` chứa quy trình nội bộ (vd *"xử lý hoàn tiền
theo phương thức thanh toán ban đầu"*). Section này **bị loại khỏi index** — kiểm chứng: không point nào
trong 95 point chứa chuỗi `Internal Note`.

## 5. Việc còn lại (ngoài phạm vi slice)

- **Sàn điểm từng-context** — hiện chỉ lọc theo top-1; chunk yếu vẫn lọt vào prompt Agent 4.
- **Xếp hạng giữa các doc CÙNG intent** — lọc theo intent không phân giải được (vd `faq/theo-doi-don-hang`
  0.6876 so với `case/don-giao-cham` 0.6853 cho cùng một câu).
- Hai câu trả lời **quá lời theo hướng khẳng định KHÔNG có** ("chưa hỗ trợ giao đi Mỹ", "không có địa chỉ
  tại Huế") trong khi KB chỉ im lặng chứ không phủ định.
- `docs/retrieval-threshold.md` §5 — đo lại ngưỡng mỗi khi KB đổi đáng kể.
