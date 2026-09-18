> **Tệp bàn giao cho Claude Word — số liệu đo lại của Bảng 3.14 và các chỗ dùng lại số liệu đó.**
>
> - **Việc cần làm:** trong bản .docx, tìm từng vị trí theo tiêu đề mục và câu mốc được nêu ở mỗi phần dưới đây,
>   rồi thay đúng nội dung được chỉ định. Không sửa nội dung nào khác ngoài các chỗ được nêu.
> - Giữ nguyên dòng chú thích bảng, tiêu đề cột và kiểu định dạng bảng đang có. Số thập phân dùng dấu phẩy; tỉ lệ
>   phần trăm viết liền như "90%".
> - **Nguồn số liệu:** đo thật ngày 18/09/2026 trên hệ thống đang chạy. Bộ 20 câu là danh sách `CASES` trong
>   `scripts/verify_intent.py`. Mỗi câu được gửi từ một tài khoản khách mới qua kênh WebSocket `/ws/chat`, nên mỗi
>   câu là lượt đầu tiên của một hội thoại riêng. Kết cục từng lượt được tính bằng hàm `group_turns` của tab Báo cáo
>   từ bảng `audit_log`. Cấu hình lúc đo: `gpt-4o-mini`, `text-embedding-3-small`, ngưỡng truy hồi 0.40, kho tri
>   thức 15 tài liệu tương ứng 95 điểm vector, cổng cấu hình mặc định. Số liệu thô:
>   `baocao/so-lieu/do-lai-bang-3-14-2026-09-18.json`. Dữ liệu thử đã được xoá khỏi cơ sở dữ liệu sau khi đo.
> - **Vì sao phải đo lại:** số cũ của bảng được đo ngày 23/07/2026, trước khi hệ thống có luồng hỏi lại mã đơn
>   (mục 2.7.3). Với mã nguồn hiện tại, yêu cầu hoàn tiền hoặc đổi hàng không kèm mã đơn được hỏi mã trước, không
>   còn vào thẳng luồng duyệt nháp; bảng cũ không có dòng nào cho kết cục này.

---

## 1. Đoạn dẫn trước Bảng 3.14 — mục "Đánh giá chất lượng xử lý trên bộ câu hỏi thực tế"

*Đoạn đang kết thúc bằng câu: «Bộ câu hỏi này được chạy trên hệ thống thật với kho tri thức đầy đủ gồm 15 tài liệu
tương ứng 95 điểm vector trong Qdrant, mô hình được bật và ngưỡng truy hồi đặt ở mức 0.40.»*

**Thao tác:** thêm câu sau vào **cuối** đoạn đó, cùng đoạn, không xuống dòng:

Lần đo ngày 18/09/2026 gửi mỗi câu từ một tài khoản khách mới, tức mỗi câu là lượt đầu tiên của một hội thoại riêng, qua kênh WebSocket như khách thật; kết cục của từng lượt được tính bằng đúng hàm mà tab Báo cáo dùng để tính các chỉ số KPI.

---

## 2. Bảng 3.14 — cùng mục

*Nằm sau: «Dưới đây là bảng thống kê phân bố kết cục xử lý thu được trên bộ 20 câu hỏi nói trên (Bảng 3.14).»*

**Thao tác:** bảng hiện có 5 dòng dữ liệu. Thay toàn bộ phần dữ liệu bằng **6 dòng** dưới đây:

- sửa số liệu dòng "Gửi thẳng";
- **thêm hai dòng con** ngay dưới dòng "Gửi thẳng" ("– Trả lời ngay" và "– Hỏi lại mã đơn, chờ khách"), ô đầu thụt
  vào một mức so với dòng "Gửi thẳng" nếu định dạng bảng cho phép;
- đổi nhãn và số liệu dòng "Duyệt nháp";
- giữ nguyên dòng "Chuyển người" và dòng "Phản hồi dự phòng oan";
- **xoá** dòng "Trả lời được nội dung thật".

Bảng 3.14. Phân bố kết cục xử lý trên bộ 20 câu hỏi

| **Kết cục** | **Số câu** | **Tỉ lệ** | **Mục tiêu KPI** | **Đánh giá** |
|---|---|---|---|---|
| Gửi thẳng | 18/20 | 90% | ≥ 70% | Đạt |
| – Trả lời ngay | 15/20 | 75% | — | — |
| – Hỏi lại mã đơn, chờ khách | 3/20 | 15% | — | Đúng thiết kế |
| Duyệt nháp (complaint) | 1/20 | 5% | — | Đúng thiết kế |
| Chuyển người (out_of_domain) | 1/20 | 5% | < 30% | Đạt |
| Phản hồi dự phòng oan | 0/20 | 0% | → 0% | Đạt |

---

## 3. Phần phân tích ngay dưới Bảng 3.14 — cùng mục

*Nằm sau câu: «Kết quả trên có thể phân tích chi tiết như sau:»*

**Thao tác:** câu dẫn này giữ nguyên. Danh sách gạch đầu dòng ngay sau nó hiện có **3 ý** (bắt đầu lần lượt bằng
"Câu hỏi duy nhất bị chuyển…", "Ba câu hỏi được đưa vào luồng duyệt nháp…", "Không có câu hỏi nào rơi vào…");
thay **cả 3 ý** bằng **6 ý** dưới đây, giữ kiểu gạch đầu dòng đang dùng:

- Tác tử phân loại gán đúng nhãn ý định cho cả 20 câu, và không lượt nào phải dùng phản hồi dự phòng, nghĩa là cơ chế chặn chống ảo giác không kích hoạt sai.
- Câu hỏi duy nhất bị chuyển cho nhân viên là câu hỏi về vé xem phim. Đây là kết quả đúng, bởi nội dung này thực sự nằm ngoài phạm vi hoạt động của cửa hàng.
- Ba lượt gửi thẳng là câu hỏi lại chứ chưa phải câu trả lời. Hai yêu cầu hoàn tiền và đổi hàng không kèm mã đơn được hỏi mã đơn trước, đúng luồng hỏi lại mã đơn ở mục 2.7.3; sau khi khách cung cấp mã, hai yêu cầu này mới đi tiếp qua cổng cấu hình và luồng duyệt nháp. Câu hỏi về kiện hàng mã AB12 nhận câu báo cố định rằng không tìm thấy đơn trong tài khoản, rồi chờ khách gửi lại mã. Nếu không tính ba lượt này, tỉ lệ trả lời ngay vẫn là 75%, trên mục tiêu 70%.
- Câu khiếu nại về thái độ nhân viên là lượt duy nhất vào luồng duyệt nháp. Nháp gồm lời xin lỗi và câu hỏi mã đơn, được giữ lại chờ quản trị viên duyệt, đúng với cấu hình cổng mặc định, trong đó ý định khiếu nại không được gửi thẳng.
- Hai câu hỏi giá và chất liệu không nêu sản phẩm cụ thể được trả lời đúng theo hướng dẫn trong kho tri thức: xin tên hoặc mã sản phẩm để báo giá, và chỉ tới phần mô tả sản phẩm trên website hoặc ứng dụng. Hệ thống không tự đưa ra giá hay chất liệu.
- Câu cảm ơn được xếp vào nhóm xã giao và nhận câu chào mẫu dùng chung cho nhóm này. Câu đáp vẫn lịch sự nhưng chưa khớp ngữ cảnh; bổ sung một câu mẫu riêng để đáp lời cảm ơn là một điểm cải thiện nhỏ.

---

## 4. Bảng 3.21 — mục "Đánh giá đối chiếu yêu cầu"

*Nằm sau: «Tương tự, dưới đây là bảng đối chiếu các chỉ số KPI giữa mục tiêu đề ra và kết quả đo được (Bảng 3.21).»*

**Thao tác:** chỉ sửa **một ô**: ở dòng "Tỉ lệ tự trả lời", cột "Đo được", thay "80% (bộ 20 câu)" bằng
**"90% (bộ 20 câu)"**. Các ô và các dòng khác giữ nguyên. Dòng "Tỉ lệ chuyển người" vẫn là 5% (không đổi).

---

## 5. Đoạn tổng kết Chương 3 — mục "Tổng kết chương" cuối Chương 3

*Đoạn bắt đầu bằng: «Về thực nghiệm, hai phân bố điểm truy hồi chồng lấn hoàn toàn…»*

**Thao tác:** trong đoạn này, thay câu

«Với ngưỡng 0.40, hệ thống đạt 80% gửi thẳng, 3% chuyển ca không cần thiết và 0% phản hồi dự phòng không cần thiết, vượt các chỉ tiêu KPI về chất lượng xử lý.»

bằng câu

«Với ngưỡng 0.40, hệ thống đạt 90% gửi thẳng, trong đó 75% là câu trả lời ngay, cùng 3% chuyển ca không cần thiết và 0% phản hồi dự phòng không cần thiết, vượt các chỉ tiêu KPI về chất lượng xử lý.»

Các câu khác của đoạn giữ nguyên.

---

## 6. Phần Tổng kết — hai chỗ

**6a. Mục "Kết quả đạt được"** — đoạn bắt đầu bằng «Về định lượng, hệ thống vượt các chỉ tiêu KPI về chất lượng
xử lý:». **Thao tác:** thay cụm

«80% số lượt được gửi thẳng (mục tiêu ≥ 70%)»

bằng cụm

«90% số lượt được gửi thẳng, trong đó 75% là câu trả lời ngay và 15% là câu hỏi lại mã đơn (mục tiêu ≥ 70%)»

Phần còn lại của câu và của đoạn giữ nguyên.

**6b. Mục "Kết luận chung"** — đoạn bắt đầu bằng «Bài học quan trọng nhất không nằm ở kỹ thuật ghép nối…».
**Thao tác:** thay cụm «đạt mức tự động hoá 80%» bằng **«đạt mức tự động hoá 90%»**. Phần còn lại giữ nguyên.

---

*Ghi chú cho người biên tập:* "Gửi thẳng" ở đây khớp cách tab Báo cáo của hệ thống tính tỉ lệ tự trả lời: mọi lượt
được gửi tới khách ngay, không qua người, kể cả câu hỏi lại mã đơn. Vì vậy Bảng 3.14 tách riêng hai dòng con để
người đọc thấy cả hai con số: 90% gửi thẳng và 75% trả lời ngay. Cả hai đều vượt mục tiêu 70%.
