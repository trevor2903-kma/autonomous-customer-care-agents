> **Tệp bàn giao cho Claude Word — PHỤ LỤC, bản rút gọn ngày 17/09/2026.** Toàn báo cáo đã được rút gọn còn
> khoảng 32.000 từ, tính cả chữ trong bảng. Nội dung đã lược bỏ (bản gốc đầy đủ) và khối ghi chú bàn giao
> trước đây nằm ở `baocao/doc.md`.
>
> - Tám mục A – H, 9 bảng (Bảng PL.1 – PL.9) và 6 hình (Hình PL.1 – PL.6), số hiệu giữ nguyên, **không** liệt
>   kê vào DANH MỤC HÌNH VẼ hay DANH MỤC BẢNG. Đã bỏ mục I.
> - Sáu bảng đặc tả use case theo đúng khuôn 8 dòng của mẫu CT060102; dòng "Ghi chú thiết kế" đã chuyển sang `doc.md`.

---

# PHỤ LỤC

## A. Đặc tả chi tiết các Use Case còn lại

Phần này đặc tả sáu use case đã được liệt kê ở mục 2.3.1 nhưng chưa được đặc tả trong thân bài. Dưới đây lần lượt là các bảng đặc tả chi tiết của từng use case (Bảng PL.1 đến Bảng PL.6).

Bảng PL.1. Đặc tả UC-04 — Cung cấp mã đơn khi được hỏi lại

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Cung cấp mã đơn khi được hỏi lại (UC-04) |
| Mô tả | Khách gửi mã đơn ở lượt kế tiếp sau khi hệ thống hỏi lại; hệ thống khôi phục ý định của lượt trước mà khách không cần nhắc lại câu hỏi |
| Tác nhân | Khách hàng |
| Tiền điều kiện | Hội thoại ở trạng thái chờ khách trả lời, ý định của lượt trước đã được lưu |
| Hậu điều kiện | Ý định gốc được khôi phục, mã đơn được ghi vào thực thể, lượt chạy tiếp như bình thường và ghi đủ sáu dòng nhật ký kiểm toán |
| Luồng sự kiện chính | 1. Khách gửi tin nhắn chỉ chứa mã đơn. 2. Hệ thống nạp trạng thái và ý định của lượt trước. 3. Tác tử 1 nhận ra ngữ cảnh nối lượt, khôi phục tất định ý định gốc và mã đơn, không gọi mô hình. 4. Tác tử 2 truy hồi bằng câu hỏi gốc trong lịch sử và tra đơn trong phạm vi tài khoản đang đăng nhập. 5. Pipeline chạy tiếp và trả kết quả cho khách |
| Luồng thay thế | 1a. Tin nhắn là một câu hỏi mới → xử lý như lượt mới. 4a. Tra đơn không ra kết quả → trả câu thông báo cố định không tìm thấy đơn. 4b. Đã hỏi lại một lần mà vẫn không có mã dùng được → chuyển cho nhân viên |
| Luồng sự kiện ngoại lệ | 4c. Cơ sở dữ liệu lỗi khi tra đơn → phát cờ chưa xử lý được đơn và chuyển người, không báo "không tìm thấy đơn". 3a. Mô hình hết thời gian chờ → chuyển người, nhưng mã đơn vẫn được giữ nhờ biểu thức chính quy |

Bảng PL.2. Đặc tả UC-06 — Yêu cầu gặp nhân viên

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Yêu cầu gặp nhân viên (UC-06) |
| Mô tả | Khách chủ động yêu cầu nói chuyện với người thật, bất kể hệ thống có đủ căn cứ trả lời hay không |
| Tác nhân | Khách hàng |
| Tiền điều kiện | Hội thoại đang ở phía tác tử, chưa có nhân viên tiếp quản |
| Hậu điều kiện | Hội thoại vào hàng đợi người kèm phiếu chuyển tiếp; khách nhận thông báo chuyển tiếp |
| Luồng sự kiện chính | 1. Khách gửi tin nhắn muốn gặp người thật. 2. Tác tử 1 phát cờ yêu cầu gặp người. 3. Tác tử 3 thấy cờ chặn nên quyết định chuyển người, không qua cổng cấu hình. 4. Tác tử 4 phát thông báo chuyển tiếp cố định. 5. Hệ thống ghi trạng thái và phiếu chuyển tiếp trong một giao dịch rồi mới báo khách |
| Luồng thay thế | 4a. Ngoài giờ hỗ trợ → dùng thông báo bản ngoài giờ |
| Luồng sự kiện ngoại lệ | 5a. Ghi cơ sở dữ liệu thất bại sau một lần thử lại → khách nhận câu không kèm cam kết thay cho thông báo chuyển tiếp |

Bảng PL.3. Đặc tả UC-13 — Duyệt hoặc từ chối nháp phản hồi

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Duyệt hoặc từ chối nháp phản hồi (UC-13) |
| Mô tả | Quản trị viên xem nháp do tác tử sinh cho ý định nhạy cảm rồi gửi nguyên văn, sửa trước khi gửi hoặc từ chối |
| Tác nhân | Quản trị viên |
| Tiền điều kiện | Đã đăng nhập với vai trò quản trị; có hội thoại chờ duyệt kèm nháp |
| Hậu điều kiện | Duyệt: nháp thành tin nhắn gửi khách, hội thoại về trạng thái đã trả lời. Từ chối: hội thoại vào hàng đợi người. Hành động được ghi nhật ký |
| Luồng sự kiện chính | 1. Mở hội thoại chờ duyệt. 2. Xem phiếu chuyển tiếp, nháp và các nguồn tri thức đã dùng. 3. Bấm Duyệt. 4. Hệ thống kiểm tra trạng thái vẫn như lúc đọc, ghi tin nhắn và trạng thái trong một giao dịch. 5. Khách nhận phản hồi |
| Luồng thay thế | 3a. Sửa nháp rồi duyệt → gửi nội dung đã sửa. 3b. Từ chối → hội thoại vào hàng đợi người, khách không nhận nội dung nào của nháp. 4a. Ca đã bị người khác xử lý → lỗi xung đột, giao diện tải lại |
| Luồng sự kiện ngoại lệ | 4b. Nháp đã thay đổi kể từ lúc mở màn hình → lỗi xung đột "nháp đã cũ", tránh duyệt một nội dung khác với nội dung vừa đọc. 3c. Quản trị viên bị hạ quyền giữa phiên → thao tác bị từ chối |

Bảng PL.4. Đặc tả UC-19 — Cấu hình cổng theo từng ý định

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Cấu hình cổng theo từng ý định (UC-19) |
| Mô tả | Quản trị viên quyết định với từng ý định rằng phản hồi được gửi thẳng hay phải qua duyệt nháp |
| Tác nhân | Quản trị viên |
| Tiền điều kiện | Đã đăng nhập với vai trò quản trị |
| Hậu điều kiện | Quy tắc mới có hiệu lực từ lượt kế tiếp; thay đổi được ghi nhật ký kiểm toán |
| Luồng sự kiện chính | 1. Mở màn hình cấu hình cổng. 2. Xem hai công tắc mức hệ thống và bảng quy tắc theo ý định. 3. Bật hoặc tắt chế độ gửi thẳng cho một ý định. 4. Hệ thống lưu và xác nhận |
| Luồng thay thế | 3a. Tắt công tắc trả lời tự động mức hệ thống → mọi ý định chuyển sang duyệt nháp |
| Luồng sự kiện ngoại lệ | 4a. Lượt kế tiếp không đọc được cấu hình do lỗi cơ sở dữ liệu → gửi thẳng câu trả lời thay vì giữ nháp |

Hai use case cuối thuộc nhóm xác thực, nền tảng của ràng buộc tra cứu đơn hàng theo phạm vi tài khoản (Bảng PL.5 và Bảng PL.6).

Bảng PL.5. Đặc tả UC-01 — Đăng ký tài khoản

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Đăng ký tài khoản (UC-01) |
| Mô tả | Người chưa có tài khoản tự tạo tài khoản khách hàng; tài khoản quản trị chỉ được tạo bằng script, không qua đăng ký |
| Tác nhân | Khách hàng |
| Tiền điều kiện | Chưa đăng nhập; email chưa gắn với tài khoản nào |
| Hậu điều kiện | Có bản ghi người dùng vai trò khách hàng với mật khẩu đã băm; phiên được mở ngay qua cookie; trả mã 201 |
| Luồng sự kiện chính | 1. Nhập email và mật khẩu. 2. Kiểm tra giới hạn tần suất theo IP (5 lần mỗi 60 giây). 3. Chuẩn hoá email. 4. Kiểm tra email chưa tồn tại. 5. Băm mật khẩu bằng bcrypt trong threadpool. 6. Tạo người dùng vai trò khách hàng. 7. Ghi mã truy cập và mã làm mới vào hai cookie httpOnly, trả mã 201 |
| Luồng thay thế | 4a. Email đã tồn tại → báo trùng email, không tiết lộ thông tin nào khác về tài khoản đó |
| Luồng sự kiện ngoại lệ | 2a. Vượt giới hạn tần suất → mã 429 kèm tiêu đề `Retry-After`. 6a. Cơ sở dữ liệu lỗi → huỷ giao dịch, không tạo tài khoản dở và không ghi cookie |

Bảng PL.6. Đặc tả UC-08 — Đăng nhập và duy trì phiên làm việc

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Đăng nhập và duy trì phiên làm việc (UC-08) |
| Mô tả | Người dùng mở phiên và giữ phiên liên tục tới khi mã làm mới hết hạn; dùng chung cho khách hàng và quản trị viên, vai trò đọc từ cơ sở dữ liệu quyết định màn hình được vào |
| Tác nhân | Khách hàng, Quản trị viên |
| Tiền điều kiện | Tài khoản đã tồn tại |
| Hậu điều kiện | Hai mã thông báo nằm trong cookie; giao diện điều hướng theo vai trò; phiên tự gia hạn ở nền |
| Luồng sự kiện chính | 1. Gửi email và mật khẩu. 2. Kiểm tra giới hạn tần suất theo IP (10 lần mỗi 60 giây) và theo email (5 lần mỗi 60 giây). 3. Tra người dùng theo email đã chuẩn hoá. 4. Xác minh mật khẩu bằng bcrypt trong threadpool. 5. Phát mã truy cập hạn 30 phút và mã làm mới hạn 7 ngày vào hai cookie httpOnly có thuộc tính suy dẫn theo môi trường. 6. Giao diện tải hồ sơ và điều hướng theo vai trò |
| Luồng thay thế | 6a. Mã truy cập hết hạn giữa phiên → yêu cầu nhận mã 401, giao diện tự gọi làm mới, hệ thống phát lại cả hai mã và yêu cầu được chạy lại một lần. 6b. Nhiều yêu cầu cùng nhận mã 401 → chỉ thực hiện một lần làm mới |
| Luồng sự kiện ngoại lệ | 6c. Mã làm mới hết hạn hoặc sai → mã 401, về trang đăng nhập. 3a. Email không tồn tại → vẫn băm một hash giả để thời gian phản hồi không lộ email. 2a. Vượt giới hạn tần suất → mã 429 kèm `Retry-After`. 6d. Kết nối WebSocket với vai trò đã bị hạ → đóng mã 4401; cơ sở dữ liệu lỗi khi xác minh → đóng mã 1011 để giao diện nối lại |

## B. Biểu đồ use case phân rã

Hai biểu đồ dưới đây phân rã biểu đồ use case tổng quát ở Hình 2.3 theo từng nhóm tác nhân.

### Phân rã use case nhóm khách hàng

Nhóm khách hàng lấy UC-02 (mở hội thoại và gửi tin nhắn) làm gốc: UC-03 là kết quả thường gặp nhất; UC-04 mở rộng UC-03 theo quan hệ **extend** khi hệ thống thiếu thực thể bắt buộc; UC-05 bao gồm bước xác thực danh tính theo quan hệ **include**; UC-06 là đường thoát luôn khả dụng; UC-07 chỉ yêu cầu đã đăng nhập (Hình PL.1).

Hình PL.1. Biểu đồ use case phân rã — nhóm khách hàng

### Phân rã use case nhóm quản trị viên

Nhóm quản trị viên được đọc theo vòng đời một ca: UC-09 và UC-10 xem và lọc hàng đợi; UC-11 (nhận ca) là điểm vào, kéo theo UC-12 (chat trực tiếp) và UC-16 (đóng ca); UC-13 đến UC-15 là ba kết cục loại trừ nhau của duyệt nháp; UC-17 đến UC-20 nằm ngoài vòng đời ca. Mọi use case của nhóm đều cần đăng nhập với vai trò quản trị (Hình PL.2).

Hình PL.2. Biểu đồ use case phân rã — nhóm quản trị viên

## C. Biểu đồ tuần tự bổ sung

Hai biểu đồ dưới đây bổ sung luồng xác thực và luồng tiếp quản ca, hai luồng nằm ngoài pipeline nhưng quyết định tính đúng đắn của hệ thống.

### Luồng đăng nhập và làm mới phiên

Người dùng gửi email và mật khẩu; back-end kiểm tra giới hạn tần suất, xác minh mật khẩu bằng bcrypt rồi ghi mã thông báo truy cập và mã thông báo làm mới vào hai cookie httpOnly. Khi một yêu cầu nhận mã 401, giao diện gọi điểm cuối làm mới; back-end kiểm tra đúng loại mã, phát lại cả hai mã, và giao diện chạy lại yêu cầu một lần — nhiều yêu cầu cùng lúc chỉ chờ chung một lần làm mới. Ở bước bắt tay WebSocket, back-end đọc cookie trước và đọc vai trò từ cơ sở dữ liệu trước khi chấp nhận kết nối (Hình PL.3).

Hình PL.3. Biểu đồ tuần tự — Đăng nhập và làm mới phiên qua httpOnly cookie

### Luồng tiếp quản ca và chat trực tiếp với khách hàng

Quản trị viên nhận ca bằng một cập nhật có điều kiện: hệ thống chỉ ghi khi trạng thái hội thoại vẫn như lúc đọc, ngược lại trả mã 409, nên hai người bấm nhận cùng lúc thì chỉ một người thành công. Sau khi ca được nhận, pipeline tự động dừng trên hội thoại đó, tin nhắn của khách đi thẳng tới người giữ ca qua trung tâm phát, và khung tin gửi tới khách không mang định danh nhân viên. Thao tác đóng ca cũng đi qua cập nhật có điều kiện và ghi một dòng nhật ký kiểm toán (Hình PL.4).

Hình PL.4. Biểu đồ tuần tự — Tiếp quản ca và chat trực tiếp với khách hàng

## D. Sơ đồ lớp theo từng miền dữ liệu

Hai sơ đồ dưới đây tách sơ đồ lớp tổng ở Hình 2.15 theo miền dữ liệu, mỗi sơ đồ bốn lớp.

### Miền hội thoại

Miền hội thoại gồm `User`, `Conversation`, `Message` và `Order`: một `User` có nhiều `Conversation` và nhiều `Order`, một `Conversation` có nhiều `Message`; khoá chủ đơn `customer_id` của `Order` là cơ sở kỹ thuật của tra cứu đơn hàng theo phạm vi khách hàng (Hình PL.5).

Hình PL.5. Sơ đồ lớp miền hội thoại

### Miền cấu hình và hỗ trợ

Miền cấu hình và hỗ trợ gồm `GateConfig`, `GateIntentRule`, `AuditLog` và `KnowledgeDocument`. Hai lớp cấu hình dùng khoá mang ý nghĩa nghiệp vụ thay vì UUID; hai lớp hỗ trợ cố ý không có khoá ngoại cứng, nên bốn lớp không liên kết trực tiếp với nhau (Hình PL.6).

Hình PL.6. Sơ đồ lớp miền cấu hình và hỗ trợ

## E. Cấu trúc một tài liệu tri thức canonical

Mỗi tài liệu trong thư mục `knowledge/` là một tệp Markdown có phần frontmatter dùng để khai báo siêu dữ liệu. Dưới đây là phần đầu của tệp `knowledge/faq/gia-san-pham.md` được trích dẫn làm ví dụ minh hoạ.

```yaml
---
intent: product_price
title: Giá sản phẩm
questions:
  - "cái này giá bao nhiêu"
  - "giá sản phẩm xem ở đâu"
  - "giá online và cửa hàng có giống nhau không"
  - "sản phẩm này bao nhiêu tiền"
---
# Giá sản phẩm

Giá của mỗi sản phẩm được **niêm yết trực tiếp** trên trang sản phẩm...
```

Trường `intent` gắn tài liệu với một nhãn ý định, `title` là tên hiển thị, còn `questions` liệt kê các cách hỏi tự nhiên của khách, mỗi câu sinh một điểm vector phục vụ mở rộng truy vấn (mục 2.6.3). Trường `type` được suy ra từ thư mục chứa tệp; hai tệp `facts.md` và `README.md` ở thư mục gốc không được nạp vào cơ sở dữ liệu vector.

## F. Cấu trúc phiếu chuyển tiếp (EscalationCard)

Phiếu chuyển tiếp được lưu dưới dạng JSONB trong bảng `conversation`, gồm các trường sau (Bảng PL.7).

Bảng PL.7. Các trường của phiếu chuyển tiếp

| **Trường** | **Ý nghĩa** |
|---|---|
| `summary` | Nguyên văn tin nhắn kích hoạt việc chuyển tiếp |
| `intent` | Nhãn ý định do tác tử 1 gán |
| `entities` | Các thực thể đã trích, ví dụ mã đơn hoặc kích cỡ |
| `rag_context` | Tối đa ba nguồn tri thức hàng đầu kèm điểm cosine và trích đoạn ngắn |
| `escalation_reason` | Lý do chuyển tiếp, ghi rõ cờ đã kích hoạt |
| `priority` / `severity` | Mức ưu tiên và mức nghiêm trọng, dùng để sắp xếp hàng đợi |
| `suggested_reply` | Nháp phản hồi: rỗng với ca chuyển người, là nháp của tác tử 4 với ca chờ duyệt |

## G. Cấu trúc payload của một điểm vector trên Qdrant

Dưới đây là bảng mô tả các trường payload đi kèm mỗi điểm vector được lưu trên Qdrant (Bảng PL.8).

Bảng PL.8. Các trường payload của một điểm vector

| **Trường** | **Ý nghĩa** |
|---|---|
| `source` | Khoá ổn định của tài liệu, ví dụ `faq/gia-san-pham.md`, dùng để xoá hoặc thay toàn bộ điểm của tài liệu |
| `text` | Nội dung thân đoạn, phần được đưa vào prompt của tác tử 4 |
| `chunk_index` | Chỉ số đoạn; cùng `source` tạo định danh tất định để việc nạp lại mang tính luỹ đẳng |
| `title` | Tên hiển thị của tài liệu |
| `intent` | Nhãn ý định trong frontmatter; rỗng với tài liệu tải lên |
| `type` | Loại tài liệu suy từ thư mục: faq, reference, case, promotion hoặc upload |
| `question` | Rỗng với điểm thân; chứa câu hỏi tương ứng với điểm mở rộng truy vấn |
| `upload_version` | Chỉ có ở tài liệu tải lên; tải lại cùng tên thì thay bản cũ |

## H. Danh sách biến môi trường

Dưới đây là bảng liệt kê các biến môi trường được sử dụng để cấu hình hệ thống (Bảng PL.9).

Bảng PL.9. Biến môi trường của hệ thống

| **Nhóm** | **Biến** | **Ghi chú** |
|---|---|---|
| Ứng dụng | `ENV` (`development` hoặc `production`), `LOG_LEVEL`, `BACKEND_CORS_ORIGINS` | `ENV` quyết định cả quy tắc CORS và thuộc tính cookie |
| Mô hình ngôn ngữ | `LLM_API_KEY`, `LLM_MODEL`, `ENABLE_LLM`, `LLM_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES` | `ENABLE_LLM=false` chạy không gọi mô hình |
| Cơ sở dữ liệu | `DATABASE_URL`, `DATABASE_SSL`, `DB_POOL_SIZE` (20), `DB_MAX_OVERFLOW` (30) | Hồ kết nối phải tỉ lệ với số hội thoại đồng thời — xem mục 3.5.6 |
| Vector database | `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION` | `QDRANT_COLLECTION` là tên alias |
| Xác thực | `JWT_SECRET`, `JWT_ACCESS_EXPIRE_MINUTES` (30), `JWT_REFRESH_EXPIRE_DAYS` (7), `JWT_EXPIRE_MINUTES` (10080) | `JWT_EXPIRE_MINUTES` giữ để tương thích bản cũ |
| Cookie xác thực | `COOKIE_SECURE` (false), `COOKIE_SAMESITE` (`lax`), `COOKIE_DOMAIN` | Ở `production`, SameSite tự chuyển `none` và Secure bắt buộc bật |
| Mô hình nhúng | `EMBEDDING_MODEL` (`text-embedding-3-small`) | |
| Giới hạn tần suất | `RATE_LIMIT_WINDOW_SECONDS` (60), `LOGIN_RATE_PER_IP` (10), `LOGIN_RATE_PER_EMAIL` (5), `REGISTER_RATE_PER_IP` (5), `CHAT_RATE_PER_CUSTOMER` (20) | Đặt về 0 là tắt bộ đếm |
| Quan sát | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` | Không đặt thì tự vô hiệu |
| Tinh chỉnh | `RETRIEVAL_THRESHOLD` (0.40), `HISTORY_WINDOW` (8), `NFR_LATENCY_MS` (5000), `MAX_MESSAGE_CHARS` (2000), `SWEEP_INTERVAL_SECONDS` (60), `SWEEP_BATCH_LIMIT` (500), `SUPPORT_HOURS_START` / `SUPPORT_HOURS_END` (9/21), `SUPPORT_TIMEZONE` (`Asia/Ho_Chi_Minh`), `REPORTS_TZ_OFFSET_HOURS` (7) | Hai ngưỡng tự đóng ca lưu ở bảng `gate_config`, không ở đây |
