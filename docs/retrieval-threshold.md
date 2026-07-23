# Đo `retrieval_threshold` trên KB thật

> Đo ngày **2026-07-23** · KB `apps/backend/knowledge/` (15 tài liệu → 95 point) ·
> embeddings `text-embedding-3-small` · Qdrant cosine · script `scripts/measure_threshold.py`.
> Chạy lại: `cd apps/backend && uv run python ../../scripts/measure_threshold.py`

## 1. Ngưỡng này là gì

`retrieval_threshold` là **ngưỡng số DUY NHẤT** liên quan escalation trong hệ thống. Agent 2 lấy điểm
cosine của hit top-1; dưới ngưỡng thì gắn cờ `low_retrieval_score`. Agent 3 (tất định) thấy cờ đó trong
`BLOCKING_FLAGS` → `human_handoff`. Agent 3 **không** đọc điểm số, **không** blend confidence.

Câu hỏi mà ngưỡng phải trả lời: *"có tri thức nào đủ liên quan để trả lời không?"*

## 2. Phương pháp

Hai tập truy vấn, chạy **đúng lời gọi production** `rag_service.search(query, top_k=4, intent=...)` với
intent như Agent 1 sẽ gán:

| Tập | Số câu | Nội dung |
| --- | --- | --- |
| **Trả-lời-được** | 32 | câu KB thật sự phủ, viết bằng **giọng khác** `questions[]` trong KB |
| **Không-trả-lời-được** | 25 | 5 câu lạc đề hoàn toàn + 20 câu trong phạm vi shop nhưng KB không có dữ liệu |

Viết giọng khác là bắt buộc: lặp lại nguyên văn `questions[]` thì query-expansion cho ~1.0 và phép đo
thành vô nghĩa.

## 3. Kết quả

### Phân bố điểm top-1

| Tập | min | p10 | p25 | median | p75 | p90 | max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Trả-lời-được | 0.380 | 0.477 | 0.560 | **0.648** | 0.723 | 0.777 | 0.804 |
| Không-trả-lời-được | 0.383 | 0.393 | 0.416 | **0.549** | 0.579 | 0.608 | 0.658 |

**Hai phân bố chồng nhau hoàn toàn.** `max(không-trả-lời-được) = 0.658` **>** `min(trả-lời-được) = 0.380`
→ **khe rỗng**: không tồn tại ngưỡng nào tách sạch hai tập trên KB này.

Tách theo kiểu hit trong tập trả-lời-được (26 câu khớp qua query-expansion, 6 câu khớp thân tài liệu):

| Kiểu hit | min | median | max |
| --- | --- | --- | --- |
| query-expansion | 0.380 | 0.702 | 0.804 |
| thân tài liệu | 0.420 | 0.542 | 0.577 |

Đúng như plan §2.7 dự đoán: query-expansion đẩy điểm lên cao, nên ngưỡng thực chất canh cho **hit thân**
(median 0.542) — nhóm này mới là ràng buộc.

### Quét ngưỡng

| Ngưỡng | Escalate oan | Tỉ lệ | Trả bừa | Tổng lỗi |
| --- | --- | --- | --- | --- |
| 0.35 | 0 | 0% | 25 | 25 |
| **0.40** | **1** | **3%** | **21** | **22** |
| 0.45 | 2 | 6% | 18 | 20 |
| 0.50 | 5 | 16% | 16 | 21 |
| 0.55 | 7 | 22% | 12 | 19 |
| 0.60 | 13 | 41% | 4 | 17 |
| 0.65 | 16 | 50% | 1 | 17 |
| 0.70 | 18 | 56% | 0 | 18 |

## 4. Chọn 0.40 — vì sao không phải cực tiểu tổng lỗi

Cực tiểu **tổng** lỗi rơi vào 0.60–0.65, nhưng phải trả bằng **41–50% escalate oan**. Cộng hai loại lỗi
rồi tìm cực tiểu là sai, vì chúng **không ngang giá**:

- **Escalate oan là lỗi CUỐI.** Khách hỏi câu shop trả lời được mà vẫn phải chờ người → mất đúng thứ hệ
  thống sinh ra để làm. Không tuyến nào bắt lại được.
- **Trả bừa còn HAI tuyến sau nó:**
  1. **Agent 1** gắn `out_of_domain` cho câu lạc đề → `human_handoff` **bất kể điểm cosine**.
  2. **Agent 4** chỉ nói từ `facts.md` + `rag_contexts`, thiếu thì bảo sẽ chuyển nhân viên.

Kiểm chứng tuyến 2 trên chính vùng chồng lấn (câu không-trả-lời-được nhưng điểm cao):

| Câu | Điểm | Kết quả thật |
| --- | --- | --- |
| "cho mình hỏi vé xem phim tối nay giá bao nhiêu" | 0.554 | `out_of_domain` → **human_handoff** |
| "thẻ thành viên hạng kim cương cần bao nhiêu điểm" | 0.580 | *"mình không có thông tin cụ thể… sẽ chuyển nhân viên"* |
| "shop có trả góp 0 đồng không" | 0.585 | trả lời đúng theo nguồn: không có trả góp, liệt kê phương thức thật |
| "áo này có size 5XL không" | 0.610 | trả lời đúng: không có, bảng size S–XXL |
| "cho mình xin mã giảm 70% đi" | 0.658 | **không bịa mã**, hướng dẫn theo dõi web/Fanpage |

Không có số liệu, mã giảm giá hay chính sách nào bị bịa. Hai câu trả lời hơi **quá lời theo hướng khẳng
định KHÔNG có** ("chưa hỗ trợ giao đi Mỹ", "không có địa chỉ tại Huế") trong khi KB chỉ im lặng chứ không
phủ định — nhẹ, ghi nhận để theo dõi.

Quy tắc chọn: **ngưỡng cao nhất mà tỉ lệ escalate oan còn ≤ 5%** → **0.40** (1/32 câu). Script dùng đúng
quy tắc này (`FALSE_ESCALATION_BUDGET`).

Câu duy nhất bị escalate oan ở 0.40: *"phơi đồ kiểu gì cho khỏi giãn"* (0.380) — KB có
`reference/bao-quan-san-pham.md` nhưng khớp yếu. Cách sửa đúng là **thêm `questions[]` cho doc đó**, không
phải hạ ngưỡng.

## 5. Kết luận & việc tiếp theo

- `retrieval_threshold = 0.40` (mặc định ở `app/core/config.py`; override bằng `RETRIEVAL_THRESHOLD` trong
  `.env` nếu cần).
- Ngưỡng này chỉnh theo **recall**, **không** dùng để chặn câu ngoài KB — việc đó do `out_of_domain` +
  grounding lo. Đừng nâng nó lên để "an toàn hơn": đổi lại là hàng loạt câu hợp lệ bị đẩy sang người.
- Muốn giảm "trả bừa" thật sự thì phải làm **sàn điểm từng-context** (lọc từng chunk thay vì chỉ nhìn
  top-1) — plan §5 xếp ngoài phạm vi slice này.
- **Đo lại khi KB đổi đáng kể** (thêm/bớt tài liệu, đổi `questions[]`, đổi embedding model).
