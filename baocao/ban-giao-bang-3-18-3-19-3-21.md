> **Tệp bàn giao cho Claude Word — số liệu đo của Bảng 3.18, Bảng 3.19 và Bảng 3.21 (Chương 3).**
>
> - **Việc cần làm:** trong Chương 3 của bản .docx, tìm từng bảng theo dòng chú thích, rồi điền đúng số liệu
>   dưới đây vào bảng đang có sẵn. Giữ nguyên dòng chú thích, câu dẫn phía trên, tiêu đề cột và kiểu định dạng bảng.
> - **Không** thêm, bớt hay đổi thứ tự cột. **Không** sửa nội dung nào khác ngoài các ô được nêu ở từng mục.
> - Giữ nguyên cách viết số như dưới đây: số mili giây viết liền, không chèn dấu phân cách hàng nghìn; số thập
>   phân trong cột "Ghi chú" dùng dấu phẩy.
> - **Nguồn số liệu:** đo thật ngày 18/09/2026 bằng `scripts/bench_concurrent.py` (`make bench`) trên hệ thống
>   đang chạy, lấy số **phía máy chủ** từ dòng `delivery` của bảng `audit_log`. Phân vị tính theo thứ hạng gần
>   nhất, không nội suy. Cấu hình đo: một tiến trình uvicorn, hồ kết nối cơ sở dữ liệu 20 + 30
>   (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`). Số liệu thô: `baocao/so-lieu/benchmark-2026-09-18-pool-20-30.json`.
> - **Lưu ý:** đây là số **sau** vòng tối ưu hồ kết nối. Bộ số đo đầu tiên (hồ mặc định 5 + 10) không điền vào
>   bảng mà chỉ dùng để so sánh trong thân bài mục 3.5.6; số thô của nó ở
>   `baocao/so-lieu/benchmark-2026-09-18-pool-5-10.json`.

---

## 1. Bảng 3.18 — Mục 3.5.6 "Benchmark đồng thời và phân tích điểm nghẽn"

*Nằm sau: «Dưới đây là bảng kết quả benchmark theo số hội thoại đồng thời, tương ứng với kịch bản 1 đã mô tả ở mục 3.5.2 (Bảng 3.18).»*

**Thao tác:** bảng hiện có 5 dòng dữ liệu (1, 10, 25, 50, 100) với mọi ô số liệu để trống. Điền các ô theo bảng dưới.

Bảng 3.18. Kết quả benchmark theo số hội thoại đồng thời

| **Số hội thoại đồng thời** | **Tổng số lượt** | **Avg (ms)** | **p50 (ms)** | **p95 (ms)** | **p99 (ms)** | **Max (ms)** | **Tỉ lệ ≤ NFR-1 (%)** |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 5860 | 5860 | 5860 | 5860 | 5860 | 0 |
| 10 | 10 | 5131 | 5035 | 5648 | 5648 | 5648 | 40 |
| 25 | 25 | 5048 | 5042 | 5481 | 5941 | 5941 | 48 |
| 50 | 50 | 6246 | 6323 | 6598 | 6706 | 6706 | 0 |
| 100 | 100 | 8998 | 9068 | 9705 | 10408 | 10753 | 0 |

---

## 2. Bảng 3.19 — Mục 3.5.6 "Benchmark đồng thời và phân tích điểm nghẽn"

*Nằm sau: «Tương tự, dưới đây là bảng kết quả benchmark theo cấu hình xử lý ở mức tải cố định 50 hội thoại đồng thời, tương ứng với kịch bản 2 (Bảng 3.19).»*

**Thao tác:**

- Bảng hiện có 6 dòng dữ liệu với mọi ô từ cột "Tổng số lượt" tới cột "Ghi chú" để trống. Điền các ô theo bảng dưới.
- **Đổi nhãn hai dòng cuối** ở cột "Cấu hình":
  - "Cửa sổ lịch sử 4 lượt" → "Cửa sổ lịch sử 4 tin nhắn (HISTORY_WINDOW = 4)"
  - "Cửa sổ lịch sử 8 lượt" → "Cửa sổ lịch sử 8 tin nhắn (HISTORY_WINDOW = 8)"

  Lý do: biến `HISTORY_WINDOW` đếm số **tin nhắn** nạp vào ngữ cảnh, không đếm số lượt.

Bảng 3.19. Kết quả benchmark theo cấu hình xử lý ở mức 50 hội thoại đồng thời

| **Cấu hình** | **Tổng số lượt** | **Avg (ms)** | **p95 (ms)** | **Thành phần chiếm tỉ trọng lớn nhất** | **Ghi chú** |
|---|---|---|---|---|---|
| Lượt xã giao (không truy hồi, không gọi mô hình sinh) | 50 | 3822 | 4407 | persist_ms — 37% (pipeline_ms 34%) | Chỉ một lời gọi mô hình (tác tử 1, 1,11 s); tác tử 2 bỏ qua truy hồi; 50/50 gửi thẳng và **toàn bộ** nằm trong 5 giây |
| Lượt hỏi chính sách (2 lời gọi mô hình + 1 embedding) | 50 | 6246 | 6598 | pipeline_ms — 54% | Mức 50 của Bảng 3.18; tác tử 1: 1,08 s, tác tử 2: 1,10 s, tác tử 4: 1,17 s |
| Lượt có tra cứu đơn hàng | 50 | 6791 | 7552 | pipeline_ms — 64% | Mỗi khách hỏi một đơn đang giao của chính mình, 50/50 tra thấy; tác tử 2 mất 1,73 s, trong đó tra đơn 0,44 s |
| Lượt không tra cứu đơn hàng | 50 | 6184 | 6604 | pipeline_ms — 55% | Câu hỏi thời gian giao hàng, không kèm mã đơn; nhanh hơn dòng trên 607 ms Avg |
| Cửa sổ lịch sử 4 tin nhắn (HISTORY_WINDOW = 4) | 50 | 6210 | 6973 | pipeline_ms — 59% | Hội thoại đã có 4 lượt (8 tin nhắn) trước lượt đo; tác tử 4: 1,21 s |
| Cửa sổ lịch sử 8 tin nhắn (HISTORY_WINDOW = 8) | 50 | 6133 | 6867 | pipeline_ms — 60% | So với cửa sổ 4 tin nhắn: −77 ms Avg, −106 ms p95; tác tử 4: 1,30 s |

---

## 3. Bảng 3.21 — Mục 3.5.7 "Đánh giá đối chiếu yêu cầu"

*Nằm sau: «Tương tự, dưới đây là bảng đối chiếu các chỉ số KPI giữa mục tiêu đề ra và kết quả đo được (Bảng 3.21).»*

**Thao tác:** **chỉ sửa dòng cuối** "Thời gian phản hồi". Hai ô "Đo được" và "Đánh giá" của dòng này hiện là
"[điền số liệu đo]" và "[đánh giá]"; thay bằng nội dung ở bảng dưới. Bốn dòng phía trên chỉ chép lại để đối chiếu
vị trí. Riêng dòng "Tỉ lệ tự trả lời" đã đổi từ 80% thành 90% sau lần đo lại Bảng 3.14 ngày 18/09/2026; thao tác
sửa ô đó nằm trong `ban-giao-bang-3-14.md`.

Bảng 3.21. Đối chiếu chỉ số KPI

| **Chỉ số** | **Mục tiêu** | **Đo được** | **Đánh giá** |
|---|---|---|---|
| Tỉ lệ tự trả lời | ≥ 70% | 90% (bộ 20 câu) | Đạt |
| Tỉ lệ chuyển người | < 30% | 5% (bộ 20 câu) | Đạt |
| Tỉ lệ escalate oan | ≤ 5% | 3% (1/32 câu) | Đạt |
| Tỉ lệ dự phòng oan | → 0% | 0% | Đạt |
| Thời gian phản hồi | < 5 giây | Avg 5,1 s ở 10 hội thoại; 5,0 s ở 25; 6,2 s ở 50; 9,0 s ở 100 (Bảng 3.18); lượt xã giao 3,8 s (Bảng 3.19) | Sát mục tiêu ở tải thấp, chưa đạt từ 50 hội thoại |

*Ghi chú cho người biên tập:* chỉ số này ở Bảng 1.4 là **thời gian phản hồi trung bình**, nên cột "Đo được" dùng
giá trị Avg của Bảng 3.18 (không dùng p95).
