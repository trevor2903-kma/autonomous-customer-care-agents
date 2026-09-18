# Hình vẽ báo cáo ĐATN

Mã nguồn cho các sơ đồ và biểu đồ của báo cáo, kèm ảnh PNG đã dựng sẵn nằm cạnh từng tệp.
Kiểu hình bám báo cáo mẫu CT060102: use case, tuần tự (khung `alt` / `opt` / `loop` / `group`), ERD, sơ đồ lớp.

- **Sơ đồ** — PlantUML (`.puml`), style dùng chung ở `_style.puml`.
- **Biểu đồ số liệu** — `bieu-do.py` (matplotlib), dựng **chỉ** từ số liệu các bảng trong báo cáo;
  ảnh xuất đúng khổ in rộng 16 cm, 300 dpi.
- **Sơ đồ vẽ theo toạ độ** — `so-do.py` (matplotlib) cho Hình 2.2 (kiến trúc tổng thể), Hình 2.3 (use case),
  Hình 2.6 (máy trạng thái), Hình 2.15 (sơ đồ lớp), Hình 2.16 (bốn lớp phòng thủ),
  Hình 3.1 (mô hình đồng thời WebSocket) và Hình PL.1, PL.2 (use case phân rã):
  kiểu báo cáo mẫu (khung có nhãn tab, nét đen, đường thẳng, nhãn giữa đường), vì PlantUML luôn bẻ gãy đường ở
  mép khung và tại vị trí nhãn; khổ in rộng 16 cm, 300 dpi.

## Dựng lại ảnh

```powershell
.\baocao\hinh-ve\render.ps1              # tất cả
.\baocao\hinh-ve\render.ps1 chuong-2     # một chương
```

Cần Java (cho PlantUML) và `uv` (cho biểu đồ số liệu và sơ đồ vẽ theo toạ độ). Lần đầu script tự tải `plantuml.jar` vào `.tools/`
(không commit); `uv` tự tạo môi trường tạm có matplotlib, không cài gì vào dự án.

**Chèn vào Word:** Insert → Pictures, đặt chiều rộng bằng lề trang (khoảng 16 cm). Các hình rất rộng
(2.14, 3.13) nên đặt trên trang xoay ngang nếu chữ bị nhỏ.

**Hình 2.14 trên dbdiagram.io:** dán nội dung `chuong-2/hinh-2-14-erd.dbml` vào https://dbdiagram.io rồi xuất PNG.
Mã DBML đã đối chiếu với metadata SQLAlchemy (8 bảng, đủ cột, NOT NULL, 3 khoá ngoại kèm `ON DELETE`). Hai tham
chiếu mềm `audit_log` → `conversation` / `message` được vẽ bằng nét xám nhưng **không có khoá ngoại thật**, nên
chỉ dùng tệp để vẽ hình, không dùng bản xuất SQL của dbdiagram làm schema; `assigned_admin_id` để ở dạng chú thích.

## Chương 1 — 5 hình vẽ

| Hình | Tệp | Vị trí chèn |
|---|---|---|
| 1.5 Bản đồ định vị các nhóm giải pháp và khoảng trống của đề tài | `chuong-1/hinh-1-05-ban-do-dinh-vi` (biểu đồ) | Mục 1.1.2, sau Bảng 1.1 |
| 1.6 Hai pha của kỹ thuật sinh có tăng cường truy hồi | `chuong-1/hinh-1-06-hai-pha-rag` | Mục 1.3.2 |
| 1.7 So sánh điều phối động và điều phối tĩnh | `chuong-1/hinh-1-07-dieu-phoi-dong-va-tinh` | Mục 1.3.3 |
| 1.8 Ba dạng ảo giác và cơ chế chống tương ứng | `chuong-1/hinh-1-08-ba-dang-ao-giac` | Mục 1.3.4, trước tiểu mục a/b/c |
| 1.9 Thang phản hồi ba mức và ranh giới an toàn / cấu hình | `chuong-1/hinh-1-09-thang-phan-hoi-ba-muc` | Mục 1.3.5 |

**Không vẽ — cần chụp hoặc tải:** Hình 1.1 – 1.4 (ảnh chụp giải pháp hiện có, ghi rõ nguồn và thời điểm truy cập)
và Hình 1.10 – 1.21 (logo công nghệ, lấy từ trang thương hiệu chính thức).

## Chương 2 — 16 hình

| Hình | Tệp | Vị trí chèn |
|---|---|---|
| 2.1 Sơ đồ actor và ranh giới hệ thống | `chuong-2/hinh-2-01-actor-ranh-gioi` | Mục 2.1, cuối mục |
| 2.2 Kiến trúc tổng thể hệ thống | `chuong-2/hinh-2-02-kien-truc-tong-the` (vẽ bằng `so-do.py`) | Mục 2.2.2 |
| 2.3 Biểu đồ use case tổng quát | `chuong-2/hinh-2-03-use-case-tong-quat` (vẽ bằng `so-do.py`) | Mục 2.3.1 |
| 2.4 Pipeline bốn tác tử cố định trên LangGraph | `chuong-2/hinh-2-04-pipeline-bon-tac-tu` | Đầu mục 2.4 |
| 2.5 Cây quyết định từ tập cờ tới ba kết cục | `chuong-2/hinh-2-05-cay-quyet-dinh` | Mục 2.5.1, sau Bảng 2.9 |
| 2.6 Máy trạng thái vòng đời hội thoại | `chuong-2/hinh-2-06-may-trang-thai` (vẽ bằng `so-do.py`) | Mục 2.5.2, sau Bảng 2.10 |
| 2.7 Hai đường nạp kho tri thức | `chuong-2/hinh-2-07-hai-duong-nap-tri-thuc` | Cuối mục 2.6.1 |
| 2.8 Nạp lại kho tri thức theo blue/green | `chuong-2/hinh-2-08-blue-green-reindex` | Cuối mục 2.6.4 |
| 2.9 Tuần tự — Trả lời tự động | `chuong-2/hinh-2-09-tuan-tu-tra-loi-tu-dong` | Mục 2.7.1 |
| 2.10 Tuần tự — Chuyển tiếp cho nhân viên | `chuong-2/hinh-2-10-tuan-tu-chuyen-tiep` | Mục 2.7.2 |
| 2.11 Tuần tự — Hỏi lại mã đơn và nối lượt | `chuong-2/hinh-2-11-tuan-tu-hoi-ma-don` | Mục 2.7.3 |
| 2.12 Tuần tự — Duyệt nháp | `chuong-2/hinh-2-12-tuan-tu-duyet-nhap` | Mục 2.7.4 |
| 2.13 Tuần tự — Tác vụ nền tự nhắc và đóng ca | `chuong-2/hinh-2-13-tuan-tu-tu-nhac-dong-ca` | Mục 2.7.5 |
| 2.14 Sơ đồ quan hệ thực thể (ERD) | `chuong-2/hinh-2-14-erd` (kèm `.dbml` cho dbdiagram.io) | Mục 2.8.1 |
| 2.15 Sơ đồ lớp miền dữ liệu | `chuong-2/hinh-2-15-so-do-lop-mien-du-lieu` (vẽ bằng `so-do.py`) | Mục 2.8.3 |
| 2.16 Bốn lớp phòng thủ chống chèn chỉ dẫn | `chuong-2/hinh-2-16-bon-lop-phong-thu` (vẽ bằng `so-do.py`) | Mục 2.9.3, trước Bảng 2.22 |

## Chương 3 — 5 hình vẽ

| Hình | Tệp | Vị trí chèn |
|---|---|---|
| 3.1 Mô hình đồng thời của kết nối WebSocket | `chuong-3/hinh-3-01-mo-hinh-dong-thoi-websocket` (vẽ bằng `so-do.py`) | Mục 3.2.3, cuối mục |
| 3.2 Phân bố điểm cosine của hai tập truy vấn | `chuong-3/hinh-3-02-phan-bo-cosine` (biểu đồ, Bảng 3.9) | Mục 3.3.5, sau Bảng 3.9 |
| 3.3 Kết quả quét ngưỡng truy hồi | `chuong-3/hinh-3-03-quet-nguong` (biểu đồ, Bảng 3.10) | Mục 3.3.5, sau Bảng 3.10 |
| 3.13 Phân rã thời gian một lượt và phạm vi NFR-1 | `chuong-3/hinh-3-13-phan-ra-thoi-gian-mot-luot` | Mục 3.5.5, sau Bảng 3.16 |
| 3.14 Độ trễ p95 theo số hội thoại đồng thời | `chuong-3/hinh-3-14-p95-theo-tai` (biểu đồ, Bảng 3.18) | Mục 3.5.6, cuối mục |

**Hình 3.14:** dựng từ cột p95 của Bảng 3.18 (số phía máy chủ, đo 18/09/2026). Đo lại thì điền số mới vào
`BANG_3_18_P95_MS` trong `bieu-do.py` rồi chạy `render.ps1 chuong-3`.

**Không vẽ — cần chụp:** Hình 3.4 – 3.12 (ảnh chụp giao diện).

## Phụ lục — 2 hình vẽ

| Hình | Tệp | Vị trí chèn |
|---|---|---|
| PL.1 Biểu đồ use case phân rã — nhóm khách hàng | `phu-luc/hinh-pl-1-use-case-khach-hang` (vẽ bằng `so-do.py`) | Phụ lục B, mục "Phân rã use case nhóm khách hàng" |
| PL.2 Biểu đồ use case phân rã — nhóm quản trị viên | `phu-luc/hinh-pl-2-use-case-quan-tri` (vẽ bằng `so-do.py`) | Phụ lục B, mục "Phân rã use case nhóm quản trị viên" |

## Đối chiếu với mã nguồn

Các hình vẽ theo code thật; những chỗ tài liệu đang lệch với code:

- **2.2 — điểm phát ngôn duy nhất chỉ đúng TRONG pipeline.** Tác vụ nền (`services/auto_resolve.py`, hàm `_act`)
  tự chèn và phát hai câu cố định tới khách (nhắc, báo đóng ca) mà không qua tác tử response. Vì vậy ghi chú của
  Hình 2.2 viết "trong pipeline, chỉ tác tử response phát tin nhắn tới khách hàng"; câu ở mục 2.2.2 ("Mọi tin nhắn
  mà hệ thống gửi tới khách hàng đều phát ra từ tác tử thứ tư") rộng hơn code.

- **2.6, 2.12 — từ chối nháp đưa ca về `IN_HUMAN_QUEUE`** (`api/routes/admin.py`), khớp Bảng PL.3.
  PRD §15 vẫn ghi `HUMAN_HANDLING`.
- **2.6:** `RESPONDING` không được dùng ở đâu; `CLOSED` chỉ dùng để lọc khi đọc; `NEW` chỉ là giá trị mặc định cột.
  Mỗi lượt AI ghi **thẳng** từ trạng thái đọc ở đầu lượt (`ACTIVE_AI` / `REPLIED` / `AWAITING_CUSTOMER`) sang
  trạng thái kết quả (`api/ws/chat.py`, CAS `allowed_from = {prior_status}`) — không quay về `ACTIVE_AI` trước.
  PRD §15 vẫn vẽ vòng `REPLIED → CLASSIFYING`.
- **3.13 — lần phát hub thứ nhất nằm TRONG con số NFR-1.** `total_ms` tính từ `received` tới `t_sent`
  (`api/ws/chat.py`), mà lần phát tin khách cho quản trị viên xảy ra trước pipeline. Chỉ lần phát thứ hai
  (sau khi gửi câu trả lời) nằm ngoài. Bảng 3.16 đang ghi `fanout_ms` "không tính vào độ trễ" — đúng một nửa.
