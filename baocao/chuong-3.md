> **Tệp bàn giao cho Claude Word — bản rút gọn ngày 17/09/2026.** Toàn báo cáo đã được rút gọn còn khoảng
> 32.000 từ, tính cả chữ trong bảng. Nội dung đã lược bỏ (bản gốc đầy đủ) và khối ghi chú bàn giao trước
> đây nằm ở `baocao/doc.md`.
>
> - Số hiệu mục, hình và bảng giữ nguyên: 14 hình (Hình 3.1 – 3.14) và 21 bảng (Bảng 3.1 – 3.21). Năm hình
>   phải dựng (3.1, 3.2, 3.3, 3.13, 3.14) đã có ở `baocao/hinh-ve/chuong-3/`.
> - **Đã điền bằng số đo thật ngày 18/09/2026** (`make bench`, số phía máy chủ từ dòng `delivery` của
>   `audit_log`, hồ kết nối 20 + 30 sau vòng tối ưu ở mục 3.5.6): Bảng 3.18, Bảng 3.19, Hình 3.14, dòng NFR-1
>   và NFR-2 của Bảng 3.20, dòng "Thời gian phản hồi" của Bảng 3.21.
> - **Ô còn trống, bắt buộc điền trước khi nộp:** Bảng 3.1 dòng "Hệ điều hành" và ba công cụ ở cuối mục 3.1.1;
>   Bảng 3.17 (mới có chú thích, khung đề xuất ở `doc.md`).

---

# THỰC NGHIỆM VÀ TRIỂN KHAI

## Thiết lập môi trường và công cụ phát triển

### Môi trường phát triển

Để quá trình xây dựng, kiểm thử và triển khai hệ thống diễn ra ổn định, việc thiết lập một môi trường làm việc đồng nhất và lựa chọn các công cụ hỗ trợ phù hợp là bước chuẩn bị quan trọng. Do hệ thống bao gồm nhiều phân hệ khác nhau và phải giao tiếp với nhiều dịch vụ hạ tầng bên ngoài, môi trường phát triển cần đáp ứng ba yêu cầu chính là tính nhất quán, khả năng tái tạo và sự thuận tiện khi kiểm thử tích hợp.

Dưới đây là bảng tổng hợp cấu hình môi trường phát triển của đồ án (Bảng 3.1).

Bảng 3.1. Cấu hình môi trường phát triển

| **Thành phần**         | **Phiên bản / công cụ**                |
|------------------------|----------------------------------------|
| Hệ điều hành           | \[Điền hệ điều hành máy phát triển\]   |
| Ngôn ngữ backend       | Python 3.12                            |
| Quản lý gói Python     | uv                                     |
| Ngôn ngữ frontend      | TypeScript, Node.js                    |
| Quản lý gói JavaScript | pnpm (workspaces)                      |
| Quản lý phiên bản      | Git, GitHub                            |
| Container (tuỳ chọn)   | Docker Compose cho hạ tầng chạy nội bộ (PostgreSQL và Qdrant) |

Dự án được tổ chức theo mô hình **monorepo** với pnpm workspaces, gồm hai ứng dụng và một package dùng chung:

.

├── apps/

│ ├── backend/ \# FastAPI + LangGraph + Alembic

│ │ ├── app/

│ │ │ ├── agents/ \# state, 4 node, đồ thị

│ │ │ ├── api/ \# routes (REST) + ws (WebSocket)

│ │ │ ├── core/ \# config, database, security, sanitize, tracing

│ │ │ ├── models/ \# SQLAlchemy + enum canonical

│ │ │ ├── schemas/ \# Pydantic

│ │ │ └── services/ \# rag, gate, order, escalation, report, audit...

│ │ ├── knowledge/ \# kho tri thức canonical

│ │ ├── tests/ \# 387 test, chạy offline

│ │ └── alembic/ \# 11 migration

│ └── dashboard/ \# Next.js (dashboard admin + chat khách PWA)

├── packages/shared-types/

├── scripts/ \# seed, ingest, đo ngưỡng, kiểm tra kết nối

├── docs/ \# kiến trúc, kết quả đo RAG, ngưỡng truy hồi

└── PRD.md · CLAUDE.md · Makefile · README.md

Bên cạnh cấu hình nền nêu trên, quá trình phát triển dùng thêm một số công cụ hỗ trợ: môi trường lập trình tích hợp *(điền IDE thực tế sử dụng)* mở được đồng thời Python và TypeScript cùng các kiểu dữ liệu dùng chung trong `packages/shared-types`; công cụ quản trị cơ sở dữ liệu *(điền công cụ thực tế)* để kiểm tra trực tiếp cột trạng thái hội thoại, nội dung JSONB của phiếu chuyển tiếp và sáu dòng nhật ký kiểm toán của một lượt; công cụ vẽ sơ đồ *(điền công cụ thực tế)*, trong đó sơ đồ quan hệ thực thể được đối chiếu ngược với các lớp SQLAlchemy để không lệch với mã nguồn; và bảng điều khiển Langfuse để xem trace của từng lượt, cũng là công cụ giúp phát hiện vấn đề cấu hình mặc định của bộ thư viện khách trình bày ở mục 3.5.5.

### Công cụ vận hành

Toàn bộ các thao tác thường dùng trong quá trình phát triển và vận hành đều được gói gọn trong tệp Makefile. Dưới đây là bảng tổng hợp các lệnh vận hành của hệ thống (Bảng 3.2).

Bảng 3.2. Các lệnh vận hành

| **Lệnh** | **Chức năng** |
|---|---|
| make install | Cài đặt backend (uv) và dashboard (pnpm) |
| make dev-backend / make dev-dashboard | Chạy môi trường phát triển |
| make migrate / make makemigration | Áp dụng / tạo migration Alembic |
| make health | Gọi điểm cuối kiểm tra sức khoẻ của backend |
| make ingest-kb | Nạp lại toàn bộ kho tri thức vào Qdrant |
| make check-conn | Kiểm tra kết nối Neon (Postgres) và Qdrant |
| make test | Chạy kiểm thử backend (pytest) và dashboard (node --test) |
| make bench | Chạy benchmark đồng thời |
| make build | Build bản production của dashboard |
| make local-infra-up / make local-infra-down | Bật / tắt hạ tầng nội bộ bằng Docker Compose |

Bên cạnh đó, đồ án còn xây dựng một số script độc lập phục vụ việc khởi tạo dữ liệu và đo đạc. Dưới đây là bảng tổng hợp các script hỗ trợ (Bảng 3.3).

Bảng 3.3. Các script hỗ trợ

| **Script** | **Chức năng** |
|---|---|
| seed_admin.py | Tạo tài khoản quản trị viên |
| seed_orders.py | Sinh đơn hàng mẫu cho các khách trong CSDL |
| ingest_kb.py | Nạp kho tri thức Markdown vào Qdrant |
| measure_threshold.py | Đo ngưỡng truy hồi, gợi ý RETRIEVAL_THRESHOLD |
| verify_intent.py | Kiểm tra chất lượng phân loại ý định |
| check_connections.py | Kiểm tra kết nối hạ tầng |
| gen_favicon.py | Sinh bộ biểu tượng cho PWA |
| bench_concurrent.py | Tạo tải đồng thời qua WebSocket |

### Quản lý cấu hình

Toàn bộ cấu hình của hệ thống được đọc từ tệp `.env` đặt tại thư mục gốc của repository thông qua thư viện pydantic-settings, tuân thủ nguyên tắc không viết cứng khoá bí mật, địa chỉ dịch vụ hay các ngưỡng số trong mã nguồn.

Dưới đây là bảng tổng hợp các nhóm biến môi trường của hệ thống (Bảng 3.4).

Bảng 3.4. Các nhóm biến môi trường

| **Nhóm**         | **Biến tiêu biểu**                                                                                                                                                                    |
|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Mô hình ngôn ngữ | LLM_API_KEY, LLM_MODEL, ENABLE_LLM, LLM_TIMEOUT_SECONDS, LLM_MAX_RETRIES                                                                                                              |
| CSDL             | DATABASE_URL, DATABASE_SSL, DB_POOL_SIZE (20), DB_MAX_OVERFLOW (30)                                                                                                                   |
| Vector DB        | QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION                                                                                                                                         |
| Xác thực         | JWT_SECRET, JWT_ACCESS_EXPIRE_MINUTES, JWT_REFRESH_EXPIRE_DAYS                                                                                                                        |
| Quan sát         | LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL                                                                                                                           |
| Tinh chỉnh       | RETRIEVAL_THRESHOLD (0.40), HISTORY_WINDOW (8), NFR_LATENCY_MS (5000), MAX_MESSAGE_CHARS (2000), SWEEP_INTERVAL_SECONDS (60), SWEEP_BATCH_LIMIT (500), SUPPORT_HOURS_START/END (9/21) |

Hai ngưỡng thời gian của cơ chế tự động đóng ca cố ý không được đặt trong tệp cấu hình môi trường mà lưu ở bảng cấu hình cổng trong cơ sở dữ liệu. Lý do là hai giá trị này thuộc nhóm tham số vận hành mà quản trị viên cần điều chỉnh được ngay trong lúc hệ thống đang chạy, chứ không phải tham số triển khai.

## Quá trình triển khai các phân hệ cốt lõi

### Phương pháp phát triển theo lát cắt mỏng

Dự án được phát triển theo phương pháp lát cắt mỏng: mỗi lát cắt là một đơn vị công việc hoàn chỉnh đi xuyên suốt từ back-end tới giao diện, và chỉ chuyển sang lát cắt tiếp theo sau khi đã được kiểm chứng đầy đủ. Tài liệu ROADMAP.md là bản đồ định hướng, còn PRD.md là nguồn dữ liệu nghiệp vụ chính thức; mọi thay đổi về kiến trúc, logic nghiệp vụ hay mô hình dữ liệu phải được cập nhật vào PRD trước khi viết mã. Nợ kỹ thuật được ghi nhận kèm thời hạn xử lý: chẳng hạn ở giai đoạn đầu, tác tử thứ ba được cài tạm dưới dạng chuyển tiếp thẳng để các lát cắt khác chạy được xuyên suốt, và khoản nợ này đã được trả bằng phiên bản tất định hiện tại, tránh để một bản cài đặt tạm thời trở thành giải pháp vĩnh viễn.

Dưới đây là bảng tổng hợp các lát cắt chính đã hoàn thành trong quá trình phát triển (Bảng 3.5).

Bảng 3.5. Các lát cắt chính đã hoàn thành

| **Lát cắt** | **Nội dung** |
|---|---|
| Scaffold | Khung monorepo, kết nối hạ tầng, migration đầu tiên |
| 01 | Agent 1 — phân loại ý định |
| 02 | Nạp tri thức + giao diện quản lý RAG |
| 03 | Agent 2 — tách truy hồi khỏi Agent 1 |
| 06 | Agent 4 — phản hồi có căn cứ, phanh chống ảo giác |
| 07a–07c | Tích hợp pipeline, WebSocket, giao diện chat khách |
| 05 | Agent 3 — chính sách tất định (trả nợ pass-through) |
| 09a | Lưu hội thoại + bộ nhớ đa lượt |
| 08a–08c | Cổng cấu hình, EscalationCard, hàng đợi, duyệt nháp |
| 10a | Danh sách hội thoại + bộ lọc |
| 11 | Xác thực JWT + phân quyền |
| 12 | Nhật ký kiểm toán, tab Báo cáo, Langfuse |
| 13 | Chống chèn chỉ dẫn bốn lớp |
| 16 | Tra cứu đơn hàng theo phạm vi khách |
| 09b | Lượt hỏi lại + nối lượt tất định |
| 09c | Tự nhắc, tự đóng ca, xử lý ngoài giờ |
| Audit v2 | Rà soát toàn hệ thống, sửa 49 vấn đề |

### Triển khai pipeline tác tử

Pipeline xử lý được xây dựng bằng thành phần StateGraph của LangGraph với bốn nút và các cạnh cố định. Quá trình triển khai bước này gắn với ba chi tiết kỹ thuật đáng chú ý.

**a) Lớp bọc phục vụ quan sát không can thiệp vào logic nghiệp vụ.** Việc đo thời gian chạy của từng nút và quy cờ về đúng nút phát ra được thực hiện bằng một decorator bọc ngoài nút thay vì sửa mã nguồn của từng nút, nên các nút bổ sung về sau cũng tự có đủ số đo. Lớp bọc giữ nguyên tính đồng bộ hay bất đồng bộ của nút gốc, vì tác tử thứ ba là hàm đồng bộ và bọc thành hàm bất đồng bộ sẽ làm thay đổi cách LangGraph lập lịch; lớp bọc cũng không che giấu ngoại lệ.

**b) Định danh nút được đặt khác tên trường trạng thái.** LangGraph không cho phép định danh nút trùng với khoá của trạng thái; do trạng thái đã có trường ý định, nút phân loại được đăng ký với định danh riêng, còn tên hiển thị trong nhật ký vẫn giữ theo tên nghiệp vụ.

**c) Bộ nhớ đa lượt đến từ cơ sở dữ liệu thay vì từ cơ chế lưu điểm kiểm tra.** Mỗi lượt sinh một định danh luồng mới cho cơ chế lưu điểm kiểm tra trong bộ nhớ, vì dùng lại định danh sẽ khiến các kênh có hàm gộp cộng dồn tích luỹ giá trị qua nhiều lượt. Bộ nhớ đa lượt đến từ lịch sử hội thoại nạp từ cơ sở dữ liệu dưới dạng đầu vào chỉ đọc. Cơ chế lưu điểm kiểm tra bền vững chỉ thực sự cần khi muốn dừng giữa chừng trong đồ thị hoặc chạy trên nhiều tiến trình, và thuộc giai đoạn phát triển sau.

### Triển khai tầng realtime

Mỗi kết nối WebSocket của khách hàng vận hành hai tác vụ song song:

- **Tác vụ đọc:** đọc khung từ khách; tin nhắn đi qua chuỗi chống trùng, kiểm tra giới hạn tần suất, xác nhận đã nhận rồi xếp tác vụ lượt vào hàng đợi, không chờ lượt chạy xong.

- **Tác vụ nghe trung tâm phát:** đẩy tin nhắn của quản trị viên, câu trả lời dành cho tab khác của cùng khách và các cập nhật trạng thái xuống socket.

Tác vụ lượt không bị huỷ khi socket đóng: khách đóng tab thì lượt vẫn chạy xong, dữ liệu vẫn được lưu và câu trả lời tới socket mới qua trung tâm phát. Phía giao diện, lớp kết nối lại chờ luỹ thừa theo các mốc 1, 2, 4, 8 giây (trần 15 giây), gửi tín hiệu duy trì mỗi 25 giây, coi socket là nửa mở sau 60 giây không có khung, đánh dấu tin chưa gửi được sau 10 giây không có xác nhận, và đối chiếu lại trạng thái từ máy chủ sau khi nối lại.

Dưới đây là sơ đồ mô hình đồng thời của một kết nối WebSocket, trong đó thể hiện hai tác vụ song song nêu trên cùng cơ chế tuần tự hoá lượt theo từng khách hàng (Hình 3.1).

Hình 3.1. Mô hình đồng thời của một kết nối WebSocket và tuần tự hoá lượt theo khách

### Triển khai dashboard quản trị

Bảng điều khiển quản trị gồm năm module, được tổ chức theo bố cục hai khung trên màn hình rộng và thu về một khung trên thiết bị di động. Dưới đây là bảng mô tả chi tiết các module của bảng điều khiển (Bảng 3.6).

Bảng 3.6. Các module dashboard

| **Module**                      | **Đường dẫn**         | **Chức năng**                                                                                            |
|---------------------------------|-----------------------|----------------------------------------------------------------------------------------------------------|
| Danh sách và chi tiết hội thoại | /admin, /admin/\[id\] | Danh sách kèm bộ lọc trạng thái, transcript đầy đủ, EscalationCard, nhận ca, chat trực tiếp, duyệt nháp  |
| Quản lý tri thức                | /admin/knowledge      | Upload, xoá tài liệu, nạp lại toàn bộ kho                                                                |
| Cấu hình cổng                   | /admin/gate           | Hai công tắc hệ thống + bảng theo từng ý định (Gửi thẳng / Duyệt nháp)                                   |
| Báo cáo hoạt động               | /admin/reports        | Lọc theo khoảng thời gian, thẻ KPI, bảng theo ý định, danh sách lượt, xem chi tiết bốn tác tử            |
| Công cụ kiểm tra pipeline       | /rag                  | Chạy thử một truy vấn để xem siêu dữ liệu của tác tử 1 và tác tử 2                                       |

Thay vì hỏi vòng máy chủ theo chu kỳ, bảng điều khiển sử dụng một kênh WebSocket duy nhất cho toàn bộ các trang quản trị. Các sự kiện được gom lại theo cửa sổ thời gian 3 giây, theo đó danh sách hội thoại được tải lại tối đa một lần trong mỗi cửa sổ, còn hàng đợi và chi tiết ca chỉ tải lại khi trong cửa sổ có phát sinh sự kiện đổi trạng thái. Lý do của thiết kế này là hai truy vấn nêu trên có chi phí lớn nhất ở phía quản trị, đồng thời lưu lượng tin nhắn từ phía khách hàng không được phép quyết định tần suất tải lại dữ liệu của giao diện quản trị. Cơ chế làm mới định kỳ sau mỗi 60 giây khi đó chỉ còn đóng vai trò lưới an toàn trong trường hợp socket bị mất kết nối kéo dài.

## Các thách thức kỹ thuật và giải pháp

Phần này trình bày những vấn đề thực tế phát sinh trong quá trình triển khai cùng cách giải quyết tương ứng. Phần lớn các vấn đề nêu dưới đây chỉ bộc lộ khi hệ thống vận hành trên dữ liệu thật, và đây cũng là phần đúc kết được nhiều bài học kỹ thuật nhất của đồ án.

### Bỏ Supervisor — đánh đổi có chủ đích

Hướng đi phổ biến trong các framework đa tác tử là bố trí một tác tử điều phối trung tâm tự quyết định luồng chạy. Đối chiếu với hệ thống này, hướng đi đó vướng ba ràng buộc cứng cùng lúc: yêu cầu NFR-1 về độ trễ, vì tác tử điều phối bổ sung ít nhất một lời gọi mô hình vào đường xử lý chính và số vòng lặp không có giới hạn trên chắc chắn; yêu cầu NFR-4 về kiểm toán, vì khi quyết định điều phối do một mô hình xác suất đưa ra thì câu hỏi vì sao hệ thống chọn một đường xử lý không có câu trả lời tất định; và yêu cầu NFR-9 về chi phí, vì chi phí mỗi lượt không còn dự đoán được.

Vì vậy đồ án loại bỏ hoàn toàn tác tử điều phối trung tâm và dùng pipeline cố định, với tối đa hai lời gọi mô hình sinh và một lời gọi embedding mỗi lượt, không phụ thuộc nội dung câu hỏi. Điều phải đánh đổi là hệ thống không xử lý được những yêu cầu phức hợp cần phối hợp động qua nhiều bước; song trong chăm sóc khách hàng của một cửa hàng thời trang, các yêu cầu này hiếm gặp và khi phát sinh thì rơi vào nhánh chuyển cho nhân viên, tức hệ thống suy giảm theo hướng an toàn thay vì đưa ra câu trả lời sai.

### Không gộp hai thang độ tin cậy

Thiết kế ban đầu, cũng là cách làm phổ biến, gộp độ tin cậy về ý định với độ tin cậy truy hồi bằng cách lấy giá trị nhỏ nhất rồi so với một ngưỡng chung. Nhưng hai con số thuộc hai thang đo khác nhau về bản chất: độ tin cậy về ý định do mô hình tự khai báo, có phân bố dồn về phía cao và chưa qua hiệu chỉnh; còn độ tin cậy truy hồi là điểm cosine giữa hai vector, với phân bố thực nghiệm trong khoảng 0,4 đến 0,8. Một ngưỡng phù hợp với thang đo này chắc chắn không phù hợp với thang đo kia.

Cách xử lý là tách hoàn toàn hai thang đo: tác tử thứ ba không đọc điểm số mà chỉ đọc tập cờ, còn hai con số vẫn được giữ trong nhật ký để phân tích. Toàn hệ thống chỉ còn một ngưỡng số liên quan tới quyết định chuyển ca là ngưỡng truy hồi, do tác tử thứ hai dùng để quyết định có phát cờ hay không. Chỉ duy trì một ngưỡng giúp hành vi của hệ thống dễ giải thích và dễ điều chỉnh hơn hẳn; khi nhiều ngưỡng cùng tham gia một quyết định, việc truy nguyên vì sao một lượt bị chuyển cho nhân viên gần như bất khả thi.

### Sự cố escalate oan khi khách chào hỏi — bài học về lỗi hai chỗ

**Hiện tượng quan sát được.** Khách gửi tin nhắn xã giao như lời chào hay lời cảm ơn thì hệ thống lại chuyển ca cho nhân viên.

**Chẩn đoán ban đầu.** Bảng phân loại phiên bản cũ không có nhãn dành cho tin nhắn xã giao, nên mô hình xếp các tin này vào nhóm khác và phát cờ ngoài phạm vi, vốn thuộc tập cờ chặn.

**Lần sửa thứ nhất chưa đạt yêu cầu.** Đồ án bổ sung nhãn xã giao; lời chào đã được phân loại đúng nhưng vẫn bị chuyển cho nhân viên, chỉ khác loại cờ. Nguyên nhân là kho tri thức không có nội dung nào về chào hỏi, nên truy hồi luôn cho điểm thấp và phát cờ điểm truy hồi thấp, cũng thuộc tập cờ chặn.

**Lần sửa thứ hai, giải pháp đúng gốc rễ.** Vấn đề thực chất là khái niệm bám nguồn đã được áp dụng trên phạm vi quá rộng: một lượt xã giao không phát biểu sự thật nào nên không có nội dung cần căn cứ. Giải pháp gồm hai phần phối hợp: tác tử thứ hai có thêm tập ý định không cần truy hồi, với các ý định này thì bỏ qua truy hồi và không phát cờ bám nguồn; tác tử thứ tư có thêm nhánh câu mẫu cố định cho nhóm ý định đó, xét trước cơ chế chặn chống ảo giác. Thiếu một trong hai phần thì lỗi vẫn còn: chỉ sửa phần thứ nhất thì tác tử thứ tư rơi vào cơ chế chặn và trả câu dự phòng, chỉ sửa phần thứ hai thì cờ vẫn bật và tác tử thứ ba đã chuyển ca trước khi luồng xử lý tới tác tử thứ tư.

Đây là thu hẹp phạm vi áp dụng của cơ chế bám nguồn chứ không phải hạ thấp yêu cầu: tác tử thứ ba giữ nguyên, tập cờ chặn không đổi, và phần bị loại khỏi phạm vi đúng bằng nhóm lượt không phát biểu sự thật nào.

Dưới đây là bảng so sánh hành vi của hệ thống trước và sau khi khắc phục hai lỗi phân loại nêu trên (Bảng 3.7).

Bảng 3.7. Hai lỗi phân loại — trước và sau khi sửa

| **Câu khách**                                       | **Trước**                            | **Sau**                            |
|-----------------------------------------------------|--------------------------------------|------------------------------------|
| "xin chào shop"                                     | other + out_of_domain → chuyển người | greeting → gửi thẳng câu chào      |
| "cảm ơn shop nhiều nha"                             | other + out_of_domain → chuyển người | greeting → gửi thẳng câu chào      |
| "cho mình xin chính sách trả hàng với"              | refund → duyệt nháp                  | return_exchange_policy → gửi thẳng |
| "mua rồi mặc thử không vừa thì đổi trong bao lâu ạ" | refund → duyệt nháp                  | return_exchange_policy → gửi thẳng |

Hai dòng cuối của bảng phản ánh một sự cố cùng loại: luật prompt phiên bản cũ gộp câu hỏi về chính sách đổi trả vào nhãn hoàn tiền, vốn mặc định phải qua duyệt nháp, nên mọi câu hỏi chính sách hoàn toàn vô hại đều bị giữ lại chờ quản trị viên. Giải pháp là tách nhãn hỏi chính sách đổi trả khỏi nhóm nhãn hoàn tiền và đổi hàng như đã trình bày ở mục 2.4.2.

Bài học chung là khi một tín hiệu an toàn đúng về logic nhưng sai về phạm vi, hệ quả không phải hệ thống mất an toàn mà là mất phần lớn giá trị sử dụng; và việc khắc phục thường phải can thiệp đồng thời ở nhiều tác tử, vì sửa ở một chỗ thì lỗi chỉ chuyển sang một hình thức biểu hiện khác.

### Khoảng cách giọng văn và kỹ thuật mở rộng truy vấn

Khoảng cách giữa giọng nói thường ngày của khách và giọng văn bản trang trọng của kho tri thức khiến nhiều câu hỏi hợp lệ nhận điểm truy hồi thấp và bị chuyển cho nhân viên một cách không cần thiết. Cách xử lý là kỹ thuật mở rộng truy vấn đã mô tả ở mục 2.6.3. Phép đo được thực hiện trên 32 câu hỏi mà kho tri thức thực sự bao phủ, viết bằng cách diễn đạt khác với danh sách câu hỏi khai báo trong frontmatter. Dưới đây là bảng kết quả đo hiệu quả của kỹ thuật mở rộng truy vấn (Bảng 3.8).

Bảng 3.8. Hiệu quả của mở rộng truy vấn

| **Kiểu khớp**             | **Số câu** | **Tỉ lệ** | **Điểm thấp nhất** | **Trung vị** | **Cao nhất** |
|---------------------------|------------|-----------|--------------------|--------------|--------------|
| Qua điểm mở rộng truy vấn | 26/32      | 81%       | 0.380              | 0.702        | 0.804        |
| Qua thân tài liệu         | 6/32       | 19%       | 0.420              | 0.542        | 0.577        |

Chênh lệch giữa hai giá trị trung vị, 0,702 so với 0,542, cho thấy so khớp câu hỏi với câu hỏi cho điểm cao hơn hẳn so khớp câu hỏi với văn bản; đây là kỹ thuật có đóng góp lớn nhất vào chất lượng truy hồi. Hệ quả là ngưỡng quyết định trên thực tế được canh theo nhóm khớp qua thân tài liệu, với trung vị 0,542: chính nhóm này mới là ràng buộc thực sự khi lựa chọn ngưỡng.

### Đo ngưỡng truy hồi thay vì chọn theo cảm tính

**Vấn đề đặt ra.** Ngưỡng truy hồi là ngưỡng số duy nhất liên quan tới quyết định chuyển ca cho nhân viên, nên chọn sai sẽ gây hậu quả mang tính hệ thống: đặt quá thấp thì hệ thống trả lời cả những câu không đủ căn cứ, đặt quá cao thì hàng loạt câu hỏi hợp lệ bị đẩy sang nhân viên.

**Phương pháp đo đạc.** Đồ án xây dựng hai tập truy vấn và đo bằng đúng lời gọi của môi trường vận hành thật, tức cùng hàm, cùng tham số và cùng nhãn ý định mà tác tử thứ nhất sẽ gán:

- **Tập câu trả lời được:** 32 câu hỏi mà kho tri thức thực sự bao phủ, viết bằng cách diễn đạt khác với danh sách câu hỏi trong frontmatter; nếu lặp lại nguyên văn, kỹ thuật mở rộng truy vấn sẽ cho điểm xấp xỉ 1,0 và phép đo mất ý nghĩa.

- **Tập câu không trả lời được:** 25 câu hỏi, gồm 5 câu lạc đề hoàn toàn và 20 câu thuộc phạm vi nghiệp vụ của cửa hàng nhưng kho tri thức chưa có dữ liệu tương ứng.

Dưới đây là bảng phân bố điểm cosine của kết quả tốt nhất trên hai tập truy vấn (Bảng 3.9).

Bảng 3.9. Phân bố điểm cosine của kết quả tốt nhất

| **Tập**            | **min** | **p10** | **p25** | **trung vị** | **p75** | **p90** | **max** |
|--------------------|---------|---------|---------|--------------|---------|---------|---------|
| Trả-lời-được       | 0.380   | 0.477   | 0.560   | 0.648        | 0.723   | 0.777   | 0.804   |
| Không-trả-lời-được | 0.383   | 0.393   | 0.416   | 0.549        | 0.579   | 0.608   | 0.658   |

Dưới đây là biểu đồ hộp biểu diễn phân bố điểm cosine của hai tập truy vấn, dựng từ chính số liệu của bảng trên (Hình 3.2).

Hình 3.2. Phân bố điểm cosine của hai tập truy vấn (n = 32 và n = 25)

Phát hiện quan trọng nhất từ phép đo là hai phân bố chồng lấn lên nhau hoàn toàn: giá trị lớn nhất của tập câu không trả lời được (0,658) lớn hơn giá trị nhỏ nhất của tập câu trả lời được (0,380). Như vậy, trên kho tri thức hiện tại không tồn tại ngưỡng nào tách sạch hai tập. Kết quả này bác bỏ giả định ngầm rằng chỉ cần chọn ngưỡng đủ khéo là hệ thống sẽ phân loại đúng.

Dưới đây là bảng kết quả quét ngưỡng trên hai tập truy vấn nêu trên (Bảng 3.10).

Bảng 3.10. Kết quả quét ngưỡng

| **Ngưỡng** | **Escalate oan** | **Tỉ lệ** | **Trả bừa** | **Tổng lỗi** |
|------------|------------------|-----------|-------------|--------------|
| 0.35       | 0                | 0%        | 25          | 25           |
| 0.40       | 1                | 3%        | 21          | 22           |
| 0.45       | 2                | 6%        | 18          | 20           |
| 0.50       | 5                | 16%       | 16          | 21           |
| 0.55       | 7                | 22%       | 12          | 19           |
| 0.60       | 13               | 41%       | 4           | 17           |
| 0.65       | 16               | 50%       | 1           | 17           |
| 0.70       | 18               | 56%       | 0           | 18           |

Dưới đây là biểu đồ đường biểu diễn kết quả quét ngưỡng truy hồi, dựng từ chính số liệu của bảng trên (Hình 3.3).

Hình 3.3. Kết quả quét ngưỡng truy hồi

**Lý do không lựa chọn ngưỡng tại điểm cực tiểu tổng lỗi.** Tổng lỗi đạt cực tiểu trong khoảng 0,60 đến 0,65, nhưng khi đó tỉ lệ chuyển ca không cần thiết lên tới 41% đến 50%. Cộng gộp hai loại lỗi rồi tìm cực tiểu là sai về phương pháp, vì hậu quả của chúng không ngang nhau. Chuyển ca không cần thiết là lỗi cuối đường: khi khách hỏi một câu cửa hàng trả lời được mà vẫn phải chờ nhân viên, không có cơ chế nào phía sau bắt lại được. Ngược lại, lỗi trả lời khi chưa đủ căn cứ vẫn còn hai tuyến phòng thủ phía sau: tác tử thứ nhất gắn cờ ngoài phạm vi cho câu lạc đề và chuyển ca bất kể điểm cosine, còn tác tử thứ tư chỉ diễn đạt lại thông tin từ nguồn được cấp và khi thiếu nguồn thì trả lời thẳng là chưa có thông tin.

Để kiểm chứng tuyến phòng thủ thứ hai, đồ án khảo sát hành vi thực tế của hệ thống trên vùng chồng lấn, tức các câu thuộc tập không trả lời được nhưng có điểm truy hồi cao. Dưới đây là bảng kết quả khảo sát (Bảng 3.11).

Bảng 3.11. Hành vi thực tế trên vùng chồng lấn

| **Câu khách**                                      | **Điểm** | **Kết quả thật**                                        |
|----------------------------------------------------|----------|---------------------------------------------------------|
| "cho mình hỏi vé xem phim tối nay giá bao nhiêu"   | 0.554    | out_of_domain → chuyển người                            |
| "thẻ thành viên hạng kim cương cần bao nhiêu điểm" | 0.580    | "mình không có thông tin cụ thể... sẽ chuyển nhân viên" |
| "shop có trả góp 0 đồng không"                     | 0.585    | Trả lời đúng theo nguồn: liệt kê các phương thức thật   |
| "áo này có size 5XL không"                         | 0.610    | Trả lời đúng: bảng size S–XXL                           |
| "cho mình xin mã giảm 70% đi"                      | 0.658    | Không bịa mã, hướng dẫn theo dõi kênh chính thức        |

Kết quả khảo sát cho thấy trên toàn bộ vùng chồng lấn, hệ thống không bịa ra bất kỳ số liệu, mã giảm giá hay nội dung chính sách nào.

**Quy tắc lựa chọn ngưỡng được áp dụng** là chọn ngưỡng cao nhất mà tỉ lệ chuyển ca không cần thiết vẫn nằm trong mức 5%, tương ứng với giá trị 0,40 và tỉ lệ thực đo là 1 trên 32 câu, tức 3%. Script đo đạc cài đặt đúng quy tắc này dưới dạng một hằng số ngân sách lỗi.

Câu hỏi duy nhất bị chuyển ca không cần thiết ở ngưỡng 0,40 là câu hỏi về cách phơi đồ để tránh giãn, với điểm số 0,380. Kho tri thức có tài liệu về bảo quản sản phẩm nhưng mức độ khớp còn yếu. Trong trường hợp này, cách khắc phục đúng là bổ sung câu hỏi tương ứng vào phần frontmatter của tài liệu đó, chứ không phải hạ thấp ngưỡng truy hồi.

### Tra cứu đơn hàng và bài toán phân biệt ba tình huống

**Vấn đề đặt ra.** Ba tình huống tra cứu thành công, không ra kết quả và không thực hiện được rất dễ bị gộp thành hai, dẫn tới hai lỗi theo hai hướng ngược nhau. Gộp tình huống không ra kết quả vào tình huống không tra cứu được thì khách gõ nhầm một chữ số đã bị chuyển cho nhân viên, làm mất phần lớn giá trị của tự động hoá. Gộp theo chiều ngược lại thì hệ thống báo không tìm thấy đơn trong tài khoản trong khi thực tế cơ sở dữ liệu đang lỗi, tức cung cấp thông tin sai sự thật. Giải pháp đã mô tả ở mục 2.4.3: ba tình huống được biểu diễn bằng ba tín hiệu riêng và chỉ tình huống thứ ba phát cờ chặn.

**Vấn đề phái sinh về việc đếm số lần tra cứu thất bại.** Để bật cờ chặn ở lần đưa mã sai thứ hai, hệ thống phải biết khách đã từng nhận thông báo không tìm thấy đơn hay chưa. Dò các con số trong lời khách ở lịch sử hội thoại là cách đơn giản nhưng không chính xác, vì số tiền trong câu hỏi phí vận chuyển hay số điện thoại gửi riêng cũng bị đếm thành mã tra cứu thất bại, khiến mã gõ nhầm ngay lần đầu đã bị chuyển ca. Cách đúng là so khớp nguyên văn câu thông báo cố định trong các tin nhắn hệ thống đã gửi, trong đó chỉ vị trí mã đơn thay đổi, rồi trích mã từ câu thông báo và tra lại theo dữ liệu thật trong cơ sở dữ liệu.

Bài học rút ra là dò tìm theo nội dung văn bản trong câu trả lời do mô hình sinh để suy luận trạng thái luôn tiềm ẩn sai sót; trạng thái của hệ thống phải đến từ cấu trúc dữ liệu hoặc từ việc so khớp với một hằng số cố định.

### Tranh chấp đồng thời và thứ tự ghi/báo

Như đã phân tích ở mục 2.5.3, việc pipeline chạy trong vài giây tạo ra cửa sổ để quản trị viên can thiệp vào hội thoại, còn việc báo khách trước khi ghi dữ liệu có thể sinh ra cam kết không có thật. Cơ chế so sánh rồi ghi kết hợp nguyên tắc ghi trước rồi mới thông báo đã được kiểm chứng qua bốn kịch bản thực tế:

- Quản trị viên tiếp quản ca khi pipeline đang chạy: lượt bị huỷ, khách nhận khung trạng thái hiện tại, không xảy ra tình huống hai bên cùng trao đổi với khách.

- Ghi thất bại hai lần liên tiếp với kết cục chuyển tiếp: khách nhận câu trả lời không kèm cam kết nào thay vì thông báo chuyển tiếp sai sự thật.

- Khách mở hai tab và gửi tin đồng thời: khoá theo khách bảo đảm hai lượt được xử lý tuần tự và không sinh ra hai ca riêng biệt.

- Tin nhắn được gửi lại sau khi mất kết nối: cơ chế chống trùng ở cả bộ nhớ tiến trình lẫn cơ sở dữ liệu ngăn pipeline chạy lần thứ hai.

Ràng buộc đi kèm là trung tâm phát, khoá theo khách, sổ chống trùng và bộ giới hạn tần suất đều nằm trong bộ nhớ tiến trình, nên hệ thống hiện chỉ vận hành trên một tiến trình uvicorn; mở rộng ra nhiều tiến trình đòi hỏi đưa các cấu trúc này ra một kho lưu trữ chia sẻ ngoài tiến trình. Phép đo ở mục 3.5.6 xác nhận một tiến trình phục vụ đủ 100 hội thoại đồng thời mà không có lượt lỗi, nhưng độ trễ tăng theo tải, chủ yếu ở các vòng truy vấn cơ sở dữ liệu.

### Nạp lại kho tri thức không gián đoạn

Nạp lại theo kiểu xoá sạch rồi nạp lại khiến mọi lượt hội thoại trong thời gian nạp bị chuyển cho nhân viên, nên hệ thống dùng cơ chế nạp lại không gián đoạn qua alias như mục 2.6.4. Cách làm này lại phát sinh vấn đề khi bước đổi alias báo lỗi: thư viện Qdrant gói mọi lỗi ở tầng truyền tải, kể cả hết thời gian chờ đọc sau khi máy chủ đã áp dụng thay đổi, thành cùng một loại ngoại lệ, nên báo lỗi không có nghĩa là chưa có thay đổi nào. Nếu hệ thống xoá collection mới trong khi alias thực tế đã trỏ vào nó, Qdrant sẽ loại bỏ luôn alias và mọi lượt hội thoại đều rơi sang nhánh chuyển cho nhân viên.

Vì vậy, khi bước đổi alias báo lỗi, hệ thống đọc lại trạng thái thật trước khi dọn dẹp: alias đã trỏ đúng thì coi là thành công; alias chưa đổi thì chỉ loại bỏ collection mới khi chắc chắn an toàn; không đọc được trạng thái thì giữ lại collection và ghi nhật ký rõ ràng để xử lý thủ công. Sau mỗi lần đổi alias thành công, hệ thống dọn các collection không còn được tham chiếu để không chiếm dung lượng gói dịch vụ miễn phí.

### Suy giảm an toàn ở mọi điểm gọi dịch vụ ngoài

Hệ thống phụ thuộc vào bốn dịch vụ bên ngoài. Nguyên tắc xuyên suốt được áp dụng là mọi điểm gọi dịch vụ ngoài đều phải suy giảm an toàn và không được phép ném lỗi làm gián đoạn lượt hội thoại của khách hàng.

Dưới đây là bảng mô tả hành vi suy giảm tương ứng với từng điểm hỏng của hệ thống (Bảng 3.12).

Bảng 3.12. Hành vi suy giảm theo từng điểm

| **Điểm hỏng** | **Hành vi** | **Kết quả** |
|---|---|---|
| Không có khoá mô hình / mô hình bị tắt | Agent 1 trả unknown + cờ llm_unavailable; thực thể lấy từ biểu thức chính quy | Chuyển người |
| Lời gọi mô hình lỗi | Ghi log, suy giảm như trên | Chuyển người |
| Qdrant / embedding lỗi | Cờ search_error (khác "kho tri thức không phủ") | Chuyển người, nhãn đúng trong báo cáo |
| Tra đơn lỗi CSDL | Cờ order_unresolved | Chuyển người |
| Không đọc được cấu hình cổng | Không giữ nháp, gửi thẳng | Chat không kẹt |
| Ghi CSDL hỏng | Thử lại một lần; vẫn hỏng thì gửi câu không hứa hẹn | Khách không nhận lời hứa giả |
| Chuẩn hoá văn bản lỗi | Tin nhắn đi tiếp dạng thô, chỉ cắt độ dài | Chat hợp lệ không bị chặn |
| Langfuse chưa cấu hình | Lời gọi trace trở thành vô hiệu | Không ảnh hưởng |
| facts.md không đọc được | Bỏ khối sự thật cửa hàng, ghi log | Ứng dụng không rớt |

Việc phân biệt giữa cờ lỗi tìm kiếm với cờ không có tri thức liên quan tuy là một chi tiết nhỏ nhưng có ý nghĩa quan trọng. Cả hai cờ đều thuộc tập chặn nên kết quả định tuyến không thay đổi, song việc gắn đúng nhãn giúp báo cáo không quy một đợt sự cố hạ tầng thành lỗi thiếu nội dung của kho tri thức, qua đó tránh dẫn tới những quyết định sai lệch về việc bổ sung tài liệu.

## Giao diện người dùng và trải nghiệm

### Nguyên tắc thiết kế giao diện

Giao diện được xây dựng bằng Tailwind CSS ở dạng thuần và tuân thủ ba nguyên tắc sau:

- **Bám theo trạng thái do máy chủ cung cấp:** Giao diện hiển thị theo trạng thái máy chủ thông báo chứ không suy diễn từ nội dung tin nhắn; vì vậy giao thức có các kiểu khung riêng cho tình huống chuyển tiếp và tình huống chờ duyệt.

- **Phản hồi tức thì cho mọi thao tác:** Tin nhắn hiển thị ngay dưới dạng bong bóng tạm, rồi được đối chiếu với bản ghi chính thức từ máy chủ theo định danh do client sinh.

- **Suy giảm một cách rõ ràng:** Mất kết nối, gửi tin thất bại hay lượt xử lý bị huỷ đều có biểu hiện trực quan riêng thay vì diễn ra âm thầm.

### Giao diện khách hàng

Cổng chat mô phỏng bố cục quen thuộc của các ứng dụng trò chuyện, gồm phần đầu trang, khung hội thoại và ô nhập tin nhắn, kèm năm thành phần bổ sung: gợi ý nhanh cho lượt đầu tiên để khách nắm được phạm vi hệ thống trả lời được; chỉ báo đang soạn tin trong suốt thời gian pipeline xử lý; trạng thái gửi của từng tin nhắn gồm đang gửi, đã nhận và chưa gửi được kèm khả năng gửi lại; cơ chế cuộn dính đáy chỉ tự cuộn khi người dùng đang ở cuối danh sách; và vạch ngăn theo ngày chèn nhãn thứ và ngày giữa các nhóm tin nhắn khi hội thoại kéo dài qua nhiều ngày.

Dưới đây lần lượt là hai ảnh chụp cổng chat khách hàng ở hai kết cục tiêu biểu của một lượt xử lý (Hình 3.4 và Hình 3.5).

Hình 3.4. Giao diện chat khách hàng — luồng trả lời tự động

Hình 3.5. Giao diện chat khách hàng — thông báo chuyển tiếp cho nhân viên

### Giao diện quản trị

Dưới đây lần lượt là các ảnh chụp sáu màn hình chính của bảng điều khiển quản trị, tương ứng với các module đã mô tả ở Bảng 3.6 (Hình 3.6 đến Hình 3.11).

Hình 3.6. Danh sách hội thoại kèm bộ lọc trạng thái

Hình 3.7. Chi tiết hội thoại với EscalationCard

Hình 3.8. Màn hình duyệt nháp phản hồi

Hình 3.9. Màn hình cấu hình cổng theo từng ý định

Hình 3.10. Tab Báo cáo hoạt động — thẻ KPI và bảng theo ý định

Hình 3.11. Xem chi tiết một lượt xử lý — bốn bước tác tử

### Trải nghiệm trên điện thoại (PWA)

Bảng điều khiển được cấu hình manifest và bộ biểu tượng để có thể cài đặt lên màn hình chính của thiết bị di động. Trên màn hình nhỏ, bố cục hai khung được thu gọn về một khung với điều hướng theo trình tự từ danh sách tới chi tiết. Các chức năng nặng về hiển thị như quản lý tri thức hay báo cáo chi tiết được xếp ở mức ưu tiên thấp hơn trên thiết bị di động. Trọng tâm của phiên bản di động là ba nghiệp vụ xem danh sách ca, đọc phiếu chuyển tiếp rút gọn và duyệt nháp nhanh.

Dưới đây là ảnh chụp bảng điều khiển sau khi được cài lên màn hình chính của thiết bị di động (Hình 3.12).

Hình 3.12. Giao diện PWA trên điện thoại

## Kiểm thử và đánh giá hệ thống

### Kiểm thử tự động

Bộ kiểm thử phía backend gồm 387 hàm kiểm thử trên 34 tệp, thu về 437 trường hợp kiểm thử khi chạy do một số hàm được tham số hoá. Toàn bộ chạy được hoàn toàn ngoại tuyến, không cần khoá API và không gọi mạng, qua đó buộc mọi nhánh suy giảm phải được cài đặt đúng, bởi đó chính là nhánh mà các kiểm thử đi vào khi không có dịch vụ ngoài.

Dưới đây là bảng mô tả phân bố các trường hợp kiểm thử theo từng nhóm chức năng (Bảng 3.13).

Bảng 3.13. Phân bố trường hợp kiểm thử theo nhóm chức năng

| **Nhóm** | **Nội dung kiểm thử** |
|---|---|
| Tác tử | Phân loại ý định, trích thực thể, truy hồi, chính sách quyết định, sinh phản hồi, đồ thị pipeline |
| An toàn | Tập cờ chặn, phanh chống ảo giác, nhánh suy giảm, hỏi lại và khoá chống lặp |
| Nghiệp vụ | Cổng cấu hình, chuyển tiếp, tra đơn có phạm vi, tự đóng ca, giờ hỗ trợ |
| Realtime | Vòng đời lượt WebSocket, cổng theo trạng thái, chống trùng, trung tâm phát |
| Bảo mật | Xác thực, phân quyền, giới hạn tần suất, chuẩn hoá đầu vào, chống chèn chỉ dẫn |
| Quan sát | Nhật ký kiểm toán theo lượt, tổng hợp báo cáo, trace |
| Tri thức | Nạp kho tri thức, chia đoạn, vòng đời tài liệu, đồng bộ taxonomy |

Các hàm nghiệp vụ quan trọng được viết dưới dạng hàm thuần để kiểm thử trực tiếp mà không cần dựng hạ tầng, gồm chính sách quyết định của tác tử thứ ba, luật cổng cấu hình, phân loại ca không hoạt động, tính các chỉ số KPI và các tiện ích thời gian thực phía giao diện. Phía giao diện có thêm năm tệp kiểm thử với 47 trường hợp, gồm tính độ trễ nối lại kết nối, hợp nhất bong bóng tin nhắn tạm với bản ghi từ máy chủ, quy đổi trạng thái sang nhãn hiển thị, xử lý ô nhập tin nhắn và chèn vạch ngăn theo ngày.

### Môi trường và kịch bản đo

Mọi số liệu trong các mục sau được thu trên cùng một cấu hình để có thể tái lập.

- **Cấu hình đo:** một tiến trình uvicorn trên máy phát triển, kết nối Neon, Qdrant Cloud và OpenAI API ở gói miễn phí; mô hình `gpt-4o-mini` và `text-embedding-3-small` giữ cố định; ngưỡng truy hồi 0.40 và cổng cấu hình mặc định, trừ phép quét ngưỡng ở mục 3.3.5.

- **Ba bộ dữ liệu đo:** bộ 20 câu hỏi thực tế để đo tỉ lệ ba kết cục giao phản hồi (mục 3.5.3); bộ 32 câu trả lời được và 25 câu không trả lời được, gán nhãn thủ công trước khi đo, để quét ngưỡng (mục 3.3.5); và bộ kiểm chứng bám nguồn thử ba dạng ảo giác (mục 3.5.4).

- **Kịch bản benchmark đồng thời:** script `scripts/bench_concurrent.py` mở N kết nối WebSocket bằng N tài khoản khách riêng — bắt buộc, vì giới hạn tần suất và khoá tuần tự hoá đều tính theo từng khách — mỗi kết nối gửi một tin rồi chờ phản hồi. Kịch bản 1 tăng tải qua các mức 1, 10, 25, 50 và 100 hội thoại đồng thời, trong đó mức 100 đối chiếu NFR-2; kịch bản 2 giữ 50 hội thoại và so sánh từng cặp cấu hình: có và không tra đơn, cửa sổ lịch sử 4 và 8 tin nhắn, lượt xã giao và lượt hỏi chính sách. Thước đo gồm Avg, p50, p95, p99 theo thứ hạng gần nhất không nội suy, Max và tỉ lệ lượt không quá 5000 ms.

- **Nguồn số liệu:** mọi con số thời gian lấy từ dòng `delivery` trong bảng `audit_log` phía máy chủ, nên không gồm độ trễ mạng và thời gian dựng giao diện.

- **Giới hạn của phép đo:** cỡ mẫu vài chục câu mỗi bộ đủ để nhận ra xu hướng nhưng chưa đủ cho khoảng tin cậy thống kê, và độ trễ mạng tới dịch vụ managed có biến động; các kết luận vì vậy được phát biểu ở mức so sánh tương đối.

### Đánh giá chất lượng xử lý trên bộ câu hỏi thực tế

Đồ án xây dựng bộ gồm 20 câu hỏi của khách hàng, trộn đủ bốn nhóm là xã giao, tra cứu, giao dịch và lạc đề. Bộ câu hỏi này được chạy trên hệ thống thật với kho tri thức đầy đủ gồm 15 tài liệu tương ứng 95 điểm vector trong Qdrant, mô hình được bật và ngưỡng truy hồi đặt ở mức 0.40. Lần đo ngày 18/09/2026 gửi mỗi câu từ một tài khoản khách mới, tức mỗi câu là lượt đầu tiên của một hội thoại riêng, qua kênh WebSocket như khách thật; kết cục của từng lượt được tính bằng đúng hàm mà tab Báo cáo dùng để tính các chỉ số KPI.

Dưới đây là bảng thống kê phân bố kết cục xử lý thu được trên bộ 20 câu hỏi nói trên (Bảng 3.14).

Bảng 3.14. Phân bố kết cục xử lý trên bộ 20 câu hỏi

| **Kết cục**                            | **Số câu** | **Tỉ lệ** | **Mục tiêu KPI** | **Đánh giá**  |
|----------------------------------------|------------|-----------|------------------|---------------|
| Gửi thẳng                              | 18/20      | 90%       | ≥ 70%            | Đạt           |
| – Trả lời ngay                         | 15/20      | 75%       | —                | —             |
| – Hỏi lại mã đơn, chờ khách            | 3/20       | 15%       | —                | Đúng thiết kế |
| Duyệt nháp (complaint)                 | 1/20       | 5%        | —                | Đúng thiết kế |
| Chuyển người (out_of_domain)           | 1/20       | 5%        | \< 30%           | Đạt           |
| Phản hồi dự phòng oan                  | 0/20       | 0%        | → 0%             | Đạt           |

Kết quả trên có thể phân tích chi tiết như sau:

- Tác tử phân loại gán đúng nhãn ý định cho cả 20 câu, và không lượt nào phải dùng phản hồi dự phòng, nghĩa là cơ chế chặn chống ảo giác không kích hoạt sai.

- Câu hỏi duy nhất bị chuyển cho nhân viên là câu hỏi về vé xem phim. Đây là kết quả đúng, bởi nội dung này thực sự nằm ngoài phạm vi hoạt động của cửa hàng.

- Ba lượt gửi thẳng là câu hỏi lại chứ chưa phải câu trả lời. Hai yêu cầu hoàn tiền và đổi hàng không kèm mã đơn được hỏi mã đơn trước, đúng luồng hỏi lại mã đơn ở mục 2.7.3; sau khi khách cung cấp mã, hai yêu cầu này mới đi tiếp qua cổng cấu hình và luồng duyệt nháp. Câu hỏi về kiện hàng mã AB12 nhận câu báo cố định rằng không tìm thấy đơn trong tài khoản, rồi chờ khách gửi lại mã. Nếu không tính ba lượt này, tỉ lệ trả lời ngay vẫn là 75%, trên mục tiêu 70%.

- Câu khiếu nại về thái độ nhân viên là lượt duy nhất vào luồng duyệt nháp. Nháp gồm lời xin lỗi và câu hỏi mã đơn, được giữ lại chờ quản trị viên duyệt, đúng với cấu hình cổng mặc định, trong đó ý định khiếu nại không được gửi thẳng.

- Hai câu hỏi giá và chất liệu không nêu sản phẩm cụ thể được trả lời đúng theo hướng dẫn trong kho tri thức: xin tên hoặc mã sản phẩm để báo giá, và chỉ tới phần mô tả sản phẩm trên website hoặc ứng dụng. Hệ thống không tự đưa ra giá hay chất liệu.

- Câu cảm ơn được xếp vào nhóm xã giao và nhận câu chào mẫu dùng chung cho nhóm này. Câu đáp vẫn lịch sự nhưng chưa khớp ngữ cảnh; bổ sung một câu mẫu riêng để đáp lời cảm ơn là một điểm cải thiện nhỏ.

### Đánh giá chất lượng grounding

Đồ án tiến hành kiểm tra hành vi của hệ thống trên nhóm câu hỏi đòi hỏi bám nguồn một cách chặt chẽ. Dưới đây là bảng tổng hợp kết quả kiểm chứng khả năng bám nguồn và bám quy trình của hệ thống (Bảng 3.15).

Bảng 3.15. Kiểm chứng khả năng bám nguồn và bám quy trình

| **Câu khách**                                      | **Hành vi đo được**                                                                                     | **Đánh giá**        |
|----------------------------------------------------|---------------------------------------------------------------------------------------------------------|---------------------|
| "em đặt mấy hôm rồi chưa thấy hàng"                | Truy hồi được 4 đoạn gồm cả quy trình xử lý → bot hỏi mã đơn trước, đúng bước 1 của quy trình chẩn đoán | Bám quy trình đúng  |
| "đơn 6578 hàng bị lỗi, cho em hoàn tiền"           | Hỏi lý do + nói "sẽ chuyển thông tin tới nhân viên hỗ trợ" — không nói đã hoàn tiền                     | Không bịa hành động |
| "ship về Đà Nẵng hết bao nhiêu"                    | "30.000đ... từ 500.000đ trở lên được miễn phí" — số liệu thật từ nguồn                                   | Bám nguồn đúng      |
| "thẻ thành viên hạng kim cương cần bao nhiêu điểm" | "không có thông tin cụ thể... sẽ chuyển nhân viên"                                                      | Không bịa           |
| "cho mình xin mã giảm 70% đi"                      | Không bịa mã, hướng dẫn theo dõi kênh chính thức                                                        | Không bịa           |

**Lưu ý về dòng thứ hai và dòng thứ tư của Bảng 3.15.** Hai câu trả lời đo được đều hứa sẽ chuyển thông tin tới nhân viên hỗ trợ, trong khi theo quy tắc "Không tự hứa chuyển người" ở Bảng 2.8, cách nói này thuộc dạng bịa hành động vì tác tử sinh phản hồi không có quyền chuyển ca. Hai phép đo được thực hiện trước khi quy tắc đó được bổ sung, và chính quan sát này là lý do quy tắc được đưa vào chỉ dẫn hệ thống. Đánh giá ở cột cuối của hai dòng chỉ phản ánh tiêu chí tại thời điểm đo; nhóm câu này cần được đo lại sau khi quy tắc có hiệu lực.

**Kiểm chứng việc loại trừ ghi chú nội bộ.** Bốn tệp trong thư mục case/ có mục ghi chú nội bộ dành cho nhân viên, mô tả các quy trình như hoàn tiền theo phương thức thanh toán ban đầu. Kiểm tra trực tiếp trên Qdrant xác nhận không điểm nào trong tổng số 95 điểm chứa nội dung của các mục này, tức cơ chế chặn tại nguồn hoạt động đúng thiết kế.

**Hạn chế phát hiện được qua kiểm chứng.** Hai câu trả lời bị quá lời theo hướng khẳng định sự vắng mặt: khẳng định cửa hàng chưa hỗ trợ giao hàng đi Hoa Kỳ và không có địa chỉ tại Huế, trong khi kho tri thức chỉ không đề cập hai nội dung này. Đây là dạng ảo giác thứ hai đã phân tích ở mục 1.3.4; quy tắc chống suy diễn từ sự vắng mặt đã giảm đáng kể nhưng chưa loại bỏ hoàn toàn dạng lỗi này. Mức nghiêm trọng được đánh giá là thấp vì không tạo cam kết sai về chính sách có lợi cho khách, song vẫn được ghi nhận để theo dõi.

### Đánh giá độ trễ và đối chiếu NFR-1

Độ trễ được đo trực tiếp từ nhật ký kiểm toán, cụ thể là từ dòng delivery, tức là thời gian xử lý đầu cuối phía máy chủ tính từ lúc hệ thống đọc được tin nhắn, bao gồm cả thời gian xếp hàng chờ sau lượt trước của cùng một khách hàng, cho tới lúc khung phản hồi được trao cho socket.

Tab Báo cáo tính toán và hiển thị các chỉ số gồm giá trị trung bình, các phân vị 50, 95, 99 và tỉ lệ lượt nằm trong ngưỡng yêu cầu NFR-1. Phân vị được tính theo phương pháp thứ hạng gần nhất không nội suy, bởi với số mẫu nhỏ, việc nội suy sẽ tạo ra những con số không tồn tại trong dữ liệu thực tế.

Bên cạnh đó, thời gian của mỗi lượt xử lý còn được tách thành nhiều thành phần nhằm phục vụ việc chẩn đoán điểm nghẽn. Dưới đây là bảng mô tả các thành phần thời gian của một lượt xử lý (Bảng 3.16).

Bảng 3.16. Các thành phần thời gian của một lượt xử lý

| **Thành phần**  | **Nội dung**                                                                       |
|-----------------|------------------------------------------------------------------------------------|
| queue_ms        | Thời gian xếp hàng chờ lượt trước của cùng khách                                   |
| pre_pipeline_ms | Nạp lịch sử, lưu tin khách                                                         |
| pipeline_ms     | Bốn tác tử, trong đó tách riêng embed_ms, qdrant_ms, order_ms                      |
| persist_ms      | Ghi trạng thái, tin nhắn và thẻ chuyển tiếp                                        |
| send_ms         | Trao khung cho socket                                                              |
| fanout_ms       | Phát realtime cho quản trị viên và các tab khác — ghi riêng, không tính vào độ trễ |

Việc tách riêng thời gian nhúng khỏi thời gian truy vấn Qdrant cho phép phân biệt độ trễ phát sinh do gọi dịch vụ nhúng với độ trễ do truy vấn cơ sở dữ liệu vector. Đây là hai nguyên nhân khác nhau và đòi hỏi hai cách xử lý khác nhau.

Dưới đây là sơ đồ dải thời gian phân rã một lượt xử lý theo các thành phần nêu trên, kèm phạm vi những thành phần được tính vào con số đối chiếu NFR-1 (Hình 3.13).

Hình 3.13. Phân rã thời gian một lượt và phạm vi con số đối chiếu NFR-1

Dưới đây là bảng tổng hợp kết quả đo độ trễ thực tế của hệ thống (Bảng 3.17).

Bảng 3.17. Kết quả đo độ trễ thực tế

Qua quá trình đo, hai yếu tố ảnh hưởng lớn nhất tới phần đuôi của phân bố độ trễ là:

- **Cơ chế thử lại lời gọi mô hình:** Cấu hình mặc định của bộ thư viện là chờ 600 giây kèm ba lần thử lại, nên một lời gọi bị treo có thể giữ lượt của khách tới gần nửa giờ. Hệ thống đã đặt lại thời gian chờ còn 20 giây và thử lại một lần; hết thời gian chờ thì nút xử lý tự suy giảm theo thiết kế.

- **Hiện tượng khởi động nguội của Qdrant:** Xảy ra trên gói dịch vụ miễn phí, làm tăng đáng kể thời gian phản hồi ở những lượt đầu tiên sau một khoảng thời gian dài không có truy vấn.

Do hệ thống ghi dữ liệu trước khi trả lời khách, các vòng truy vấn cơ sở dữ liệu nằm bên trong con số độ trễ đo được. Đây là đánh đổi có chủ đích giữa độ trễ và tính đúng đắn của dữ liệu, và cũng là lý do khi triển khai thực tế cần đặt backend gần cơ sở dữ liệu về mặt địa lý.

### Benchmark đồng thời và phân tích điểm nghẽn

Các con số ở mục trên được thu trên từng lượt xử lý đơn lẻ, trong khi yêu cầu NFR-2 đặt mục tiêu phục vụ ít nhất 100 người dùng đồng thời trên một tiến trình; một hệ thống có độ trễ tốt ở tải thấp vẫn có thể suy giảm mạnh khi số hội thoại đồng thời tăng. Trước phép đo này, cơ sở duy nhất cho NFR-2 là lập luận kiến trúc: back-end viết bất đồng bộ và một lượt xử lý chủ yếu là thời gian chờ nhập xuất, nên nhiều lượt chạy xen kẽ được trên cùng một vòng lặp sự kiện. Mục này nhằm biến lập luận đó thành số liệu kiểm chứng được.

Hai kịch bản được chạy ngày 18/09/2026 trên một tiến trình uvicorn ở máy phát triển, nối tới Neon (vùng ap-southeast-1), Qdrant Cloud (vùng australia-southeast1) và OpenAI API. Hạn mức của tài khoản OpenAI là 30.000 yêu cầu và 150 triệu token mỗi phút, nên phép đo không chạm giới hạn phía nhà cung cấp. Hồ kết nối cơ sở dữ liệu đặt ở 20 kết nối cộng 30 kết nối vượt mức qua hai biến `DB_POOL_SIZE` và `DB_MAX_OVERFLOW`; đây là kết quả của vòng tối ưu trình bày ở cuối mục, sau khi lần đo đầu với hồ mặc định của SQLAlchemy (5 cộng 10) chỉ ra chính hồ kết nối là điểm nghẽn. Mỗi mức tải dùng một nhóm tài khoản mới để mọi lượt đều là lượt đầu của một hội thoại; sau mỗi lần khởi động backend có một lượt khởi động không tính vào kết quả, và giữa hai đợt đo nghỉ 20 giây. Câu hỏi của kịch bản 1 là "Phí giao hàng của shop là bao nhiêu vậy?". Câu hỏi đo bắt buộc chỉ mang một ý định: ở lần chạy thử với câu gộp hai câu hỏi (phí giao hàng và thời gian nhận hàng), tác tử thứ nhất gắn cờ nhiều ý định cho 36–46% số lượt và chuyển các lượt đó cho nhân viên, làm trộn hai loại lượt có khối lượng xử lý khác nhau vào cùng một phép đo. Toàn bộ 186 lượt của kịch bản 1 và 250 lượt đo riêng của kịch bản 2 đều nhận được khung kết cục, không có lượt lỗi hay hết thời gian chờ.

Dưới đây là bảng kết quả benchmark theo số hội thoại đồng thời, tương ứng với kịch bản 1 đã mô tả ở mục 3.5.2 (Bảng 3.18).

Bảng 3.18. Kết quả benchmark theo số hội thoại đồng thời

| **Số hội thoại đồng thời** | **Tổng số lượt** | **Avg (ms)** | **p50 (ms)** | **p95 (ms)** | **p99 (ms)** | **Max (ms)** | **Tỉ lệ ≤ NFR-1 (%)** |
|----------------------------|------------------|--------------|--------------|--------------|--------------|--------------|-----------------------|
| 1                          | 1                | 5860         | 5860         | 5860         | 5860         | 5860         | 0                     |
| 10                         | 10               | 5131         | 5035         | 5648         | 5648         | 5648         | 40                    |
| 25                         | 25               | 5048         | 5042         | 5481         | 5941         | 5941         | 48                    |
| 50                         | 50               | 6246         | 6323         | 6598         | 6706         | 6706         | 0                     |
| 100                        | 100              | 8998         | 9068         | 9705         | 10408        | 10753        | 0                     |

Ở cả năm mức tải, mọi lượt đều được phục vụ trọn vẹn, nên về năng lực, một tiến trình đáp ứng được 100 hội thoại đồng thời theo yêu cầu NFR-2. Độ trễ vẫn tăng theo tải: p95 là 5,6 giây ở mức 10, 5,5 giây ở mức 25, 6,6 giây ở mức 50 và 9,7 giây ở mức 100, tức khoảng 1,7 lần giữa mức 10 và mức 100. Ở tải thấp con số nằm ngay sát ngưỡng, với 40% số lượt ở mức 10 và 48% ở mức 25 nằm trong 5 giây, còn từ mức 50 thì không lượt nào đạt. Mức 1 chỉ có một mẫu nên chỉ mang tính tham khảo. Số đo phía client do script ghi lại để đối chiếu lớn hơn số phía máy chủ khoảng 0,9 giây ở mức 1 và 2,6 giây ở p95 mức 100; phần chênh này nằm ngoài phạm vi `total_ms` đã chỉ ra ở Hình 3.13, nghĩa là độ trễ người dùng cảm nhận còn cao hơn con số đối chiếu NFR-1.

Tương tự, dưới đây là bảng kết quả benchmark theo cấu hình xử lý ở mức tải cố định 50 hội thoại đồng thời, tương ứng với kịch bản 2 (Bảng 3.19).

Bảng 3.19. Kết quả benchmark theo cấu hình xử lý ở mức 50 hội thoại đồng thời

| **Cấu hình**                                              | **Tổng số lượt** | **Avg (ms)** | **p95 (ms)** | **Thành phần chiếm tỉ trọng lớn nhất** | **Ghi chú** |
|-----------------------------------------------------------|------------------|--------------|--------------|----------------------------------------|-------------|
| Lượt xã giao (không truy hồi, không gọi mô hình sinh)     | 50               | 3822         | 4407         | persist_ms — 37% (pipeline_ms 34%)     | Chỉ một lời gọi mô hình (tác tử 1, 1,11 s); tác tử 2 bỏ qua truy hồi; 50/50 gửi thẳng và **toàn bộ** nằm trong 5 giây |
| Lượt hỏi chính sách (2 lời gọi mô hình + 1 embedding)     | 50               | 6246         | 6598         | pipeline_ms — 54%                      | Mức 50 của Bảng 3.18; tác tử 1: 1,08 s, tác tử 2: 1,10 s, tác tử 4: 1,17 s |
| Lượt có tra cứu đơn hàng                                  | 50               | 6791         | 7552         | pipeline_ms — 64%                      | Mỗi khách hỏi một đơn đang giao của chính mình, 50/50 tra thấy; tác tử 2 mất 1,73 s, trong đó tra đơn 0,44 s |
| Lượt không tra cứu đơn hàng                               | 50               | 6184         | 6604         | pipeline_ms — 55%                      | Câu hỏi thời gian giao hàng, không kèm mã đơn; nhanh hơn dòng trên 607 ms Avg |
| Cửa sổ lịch sử 4 tin nhắn (HISTORY_WINDOW = 4)            | 50               | 6210         | 6973         | pipeline_ms — 59%                      | Hội thoại đã có 4 lượt (8 tin nhắn) trước lượt đo; tác tử 4: 1,21 s |
| Cửa sổ lịch sử 8 tin nhắn (HISTORY_WINDOW = 8)            | 50               | 6133         | 6867         | pipeline_ms — 60%                      | So với cửa sổ 4 tin nhắn: −77 ms Avg, −106 ms p95; tác tử 4: 1,30 s |

Ba cặp cấu hình cho ba kết luận khác nhau. Lượt xã giao nhanh hơn lượt hỏi chính sách 2,4 giây Avg, xấp xỉ phần việc nó bỏ qua là truy hồi và lời gọi sinh phản hồi, và là cấu hình duy nhất đạt NFR-1 với toàn bộ 50 lượt nằm trong 5 giây. Tra cứu đơn hàng làm lượt chậm thêm 607 ms, trong đó bản thân truy vấn đơn chiếm 435 ms. Cửa sổ lịch sử 8 tin nhắn thậm chí nhanh hơn cửa sổ 4 tin nhắn 77 ms, tức chênh lệch nằm trong dao động giữa các lần chạy, nên kích thước cửa sổ không phải điểm cần tối ưu.

**Phân rã thời gian và nhận diện điểm nghẽn**

Số đo đã được tách sẵn trong dòng `delivery` (Bảng 3.16) thành `queue_ms`, `pre_pipeline_ms`, `pipeline_ms` (gồm `embed_ms`, `qdrant_ms`, `order_ms`), `persist_ms`, `send_ms` và `fanout_ms`, nên chẩn đoán điểm nghẽn không cần công cụ đo bổ sung. Đồ án đặt bốn giả thuyết kèm dấu hiệu nhận biết:

- **Xếp hàng theo khách:** `queue_ms` lớn là dấu hiệu một khách gửi dồn nhiều tin, không phải nghẽn do số hội thoại, vì khoá tuần tự đặt theo từng khách.

- **Hạn mức của nhà cung cấp mô hình:** `embed_ms` và thời gian gọi mô hình tăng theo tải trong khi `qdrant_ms` và `persist_ms` không đổi; xử lý bằng hàng đợi kiểm soát nhịp gửi hoặc nâng hạn mức.

- **Hồ kết nối cơ sở dữ liệu:** `persist_ms` và `pre_pipeline_ms` cùng tăng do giới hạn kết nối của Neon; vì hệ thống ghi trước rồi mới báo khách, điểm nghẽn này biểu hiện thẳng thành độ trễ.

- **Khởi động nguội của Qdrant:** `qdrant_ms` rất cao ở những lượt đầu rồi giảm hẳn, không tương quan với tải.

Nhờ vậy có thể tách điểm nghẽn thuộc hệ thống, xử lý bằng sửa mã hoặc chỉnh cấu hình, với điểm nghẽn thuộc dịch vụ ngoài, chỉ xử lý được bằng thay đổi hạn mức hoặc gói dịch vụ.

Đối chiếu bốn giả thuyết với số đo cho một kết quả rõ ràng, và chính kết quả đó dẫn tới vòng tối ưu của mục này. Ở lần đo đầu, với hồ kết nối mặc định 5 cộng 10, `pipeline_ms` gần như không đổi theo tải (3,46 giây ở mức 1 và 3,51 giây ở mức 100) trong khi `pre_pipeline_ms` tăng từ 1,01 giây lên 6,12 giây và `persist_ms` từ 0,60 giây lên 1,74 giây: hai thành phần đi qua cơ sở dữ liệu cùng tăng, đúng dấu hiệu của giả thuyết hồ kết nối, còn giả thuyết hạn mức nhà cung cấp bị loại. Nguyên nhân là số kết nối cần tỉ lệ với số hội thoại đồng thời chứ không với số tiến trình, bởi mỗi lượt mở bốn tới sáu phiên ngắn nối tiếp; hồ 15 kết nối vì vậy trở thành hàng đợi, và do hệ thống ghi trước rồi mới báo khách, thời gian chờ đó cộng thẳng vào độ trễ.

Sau khi đưa hai tham số hồ kết nối ra biến môi trường và đặt 20 cộng 30, `pre_pipeline_ms` ở mức 100 giảm còn 2,13 giây và p95 của cả lượt giảm từ 13,1 giây xuống 9,7 giây, tức 26%. Một phép đo chẩn đoán thêm với 100 kết nối cho thấy `pre_pipeline_ms` giảm tiếp còn 1,36 giây nhưng p95 không đổi, ở mức 9,8 giây; như vậy 50 kết nối đã đủ và hồ kết nối không còn là điểm nghẽn. Điểm nghẽn chuyển sang các lời gọi ra ngoài: ở mức 100, `pipeline_ms` tăng lên 5,47 giây với `embed_ms` 0,76 giây so với 0,25–0,31 giây ở tải thấp, và `qdrant_ms` 1,04 giây so với 0,60–0,79 giây, trong khi `queue_ms` vẫn bằng 0 ở mọi mức, khớp thiết kế khoá theo từng khách. Vì hạn mức của nhà cung cấp còn rất xa, phần tăng này nằm ở đường truyền ra ngoài của máy đo và ở khoảng cách tới hai dịch vụ managed. Hướng cải thiện tiếp theo vì vậy là đặt backend cùng vùng với cơ sở dữ liệu và chuyển cụm Qdrant về vùng gần, chứ không phải tối ưu thêm ở tầng ứng dụng.

Dưới đây là biểu đồ độ trễ ở phân vị 95 theo số hội thoại đồng thời cùng mốc ngưỡng NFR-1 (Hình 3.14).

Hình 3.14. Độ trễ p95 theo số hội thoại đồng thời, đối chiếu ngưỡng NFR-1

### Đánh giá đối chiếu yêu cầu

Để đánh giá mức độ hoàn thành của hệ thống, đồ án tiến hành đối chiếu kết quả thu được với các yêu cầu phi chức năng và các chỉ số KPI đã đặt ra ở Chương 1, lần lượt tại Bảng 1.3 và Bảng 1.4. Dưới đây là bảng đối chiếu các yêu cầu phi chức năng (Bảng 3.20).

Bảng 3.20. Đối chiếu yêu cầu phi chức năng

| **Mã** | **Yêu cầu** | **Trạng thái** | **Ghi chú** |
|---|---|---|---|
| NFR-1 | P95 ≤ 5 giây | Chưa đạt trên cấu hình đo | p95 5,5 s ở 25 hội thoại, 9,7 s ở 100 (Bảng 3.18); riêng lượt xã giao đạt 100% (Bảng 3.19); tab Báo cáo giám sát p95 liên tục |
| NFR-2 | ≥ 100 người dùng đồng thời | Đạt về năng lực phục vụ | 100/100 lượt, không lỗi, không hết thời gian chờ trên một tiến trình (Bảng 3.18); độ trễ ở mức này vượt NFR-1 |
| NFR-3 | Uptime ≥ 99% | Phụ thuộc hạ tầng triển khai | Mọi điểm gọi ngoài đều suy giảm an toàn |
| NFR-4 | Kiểm toán 100% | Đạt | 6 dòng/lượt + dòng riêng cho hành động quản trị viên |
| NFR-5 | JWT + RBAC + HTTPS/WSS | Đạt | Vai trò đọc lại từ CSDL |
| NFR-6 | An toàn dữ liệu cá nhân | Đạt | Dữ liệu mô phỏng; tra đơn có phạm vi |
| NFR-7 | Chống chèn chỉ dẫn | Đạt | Bốn lớp + bảo đảm cấu trúc |
| NFR-8 | Quan sát | Đạt | audit_log + Langfuse |
| NFR-9 | Chi phí | Đạt | Hạ tầng dùng gói miễn phí |
| NFR-10 | Cấu hình được | Đạt | Ngưỡng, mốc thời gian, cổng qua biến môi trường và CSDL |
| NFR-11 | An toàn nội dung | Đạt | Phanh cứng + quy tắc grounding; 0% dự phòng oan |

Tương tự, dưới đây là bảng đối chiếu các chỉ số KPI giữa mục tiêu đề ra và kết quả đo được (Bảng 3.21).

Bảng 3.21. Đối chiếu chỉ số KPI

| **Chỉ số**         | **Mục tiêu** | **Đo được**         | **Đánh giá** |
|--------------------|--------------|---------------------|--------------|
| Tỉ lệ tự trả lời   | ≥ 70%        | 90% (bộ 20 câu)     | Đạt          |
| Tỉ lệ chuyển người | \< 30%       | 5% (bộ 20 câu)      | Đạt          |
| Tỉ lệ escalate oan | ≤ 5%         | 3% (1/32 câu)       | Đạt          |
| Tỉ lệ dự phòng oan | → 0%         | 0%                  | Đạt          |
| Thời gian phản hồi | \< 5 giây    | Avg 5,1 s ở 10 hội thoại; 5,0 s ở 25; 6,2 s ở 50; 9,0 s ở 100 (Bảng 3.18); lượt xã giao 3,8 s (Bảng 3.19) | Sát mục tiêu ở tải thấp, chưa đạt từ 50 hội thoại |

### Hạn chế còn tồn tại và hướng cải thiện

Hệ thống còn một số hạn chế, làm cơ sở cho hướng cải thiện về sau.

**Về truy hồi tri thức:**

- Chưa có sàn điểm cho từng đoạn, nên đoạn điểm thấp vẫn lọt vào prompt của tác tử thứ tư.

- Chưa xếp hạng lại được giữa các tài liệu cùng ý định có điểm gần nhau, ví dụ 0.6876 và 0.6853 cho cùng một câu hỏi.

- Chưa ngữ cảnh hoá truy vấn cho câu hỏi nối tiếp: tác tử thứ hai vẫn truy hồi trên câu thô, trừ lượt khách đáp bằng mã đơn (mục 2.7.3).

**Về xử lý ngôn ngữ:**

- Tin nhắn chứa nhiều ý định vẫn bị chuyển thẳng cho nhân viên.

- Còn hiện tượng quá lời theo hướng phủ định (mục 3.5.4).

- Chưa phát hiện được cảm xúc của khách để nâng mức ưu tiên.

**Về kiến trúc và vận hành:**

- Trung tâm phát, khoá đồng bộ, sổ chống trùng và bộ giới hạn tần suất nằm trong bộ nhớ nên hệ thống chỉ chạy một tiến trình; mở rộng ngang cần một kho chia sẻ ngoài tiến trình như Redis hoặc tương đương.

- Cơ chế lưu điểm kiểm tra chưa bền vững, chưa cho phép dừng luồng xử lý ở giữa đồ thị.

- Chưa phát hiện được quản trị viên trực tuyến thật, mới dựa vào khung giờ hỗ trợ.

- Chưa có cơ chế giải phóng ca đã được nhận nhưng không được xử lý.

- Vòng học bán tự động chưa được xây dựng, dù dữ liệu đầu vào đã có trong nhật ký kiểm toán.

- Độ trễ chưa đạt NFR-1 khi tải tăng: p95 9,7 giây ở 100 hội thoại đồng thời. Sau khi nới hồ kết nối, phần tăng theo tải chuyển sang các lời gọi ra ngoài là embedding và Qdrant (mục 3.5.6).

- Chưa đo được độ trễ phía client.

## Tổng kết chương

Chương 3 đã trình bày quá trình hiện thực hoá thiết kế ở Chương 2: môi trường phát triển, phương pháp lát cắt mỏng, triển khai pipeline tác tử, tầng realtime và dashboard quản trị. Trọng tâm của chương là chín thách thức kỹ thuật thực tế, từ đó rút ra ba bài học: không gộp hai thang độ tin cậy khác bản chất; một tín hiệu an toàn áp dụng sai phạm vi làm hệ thống mất giá trị sử dụng; và suy luận trạng thái bằng cách dò văn bản do mô hình sinh luôn tiềm ẩn sai sót.

Về thực nghiệm, hai phân bố điểm truy hồi chồng lấn hoàn toàn, nên ngưỡng được chọn theo ngân sách dành cho lỗi chuyển ca không cần thiết thay vì theo cực tiểu tổng lỗi. Với ngưỡng 0.40, hệ thống đạt 90% gửi thẳng, trong đó 75% là câu trả lời ngay, cùng 3% chuyển ca không cần thiết và 0% phản hồi dự phòng không cần thiết, vượt các chỉ tiêu KPI về chất lượng xử lý. Benchmark đồng thời cho thấy một tiến trình phục vụ đủ 100 hội thoại đồng thời không lỗi, nhưng độ trễ chỉ sát chỉ tiêu ở tải thấp và lên tới p95 9,7 giây ở 100 hội thoại; vòng tối ưu hồ kết nối đã giảm con số này 26% và đẩy điểm nghẽn sang các lời gọi ra ngoài; những hạn chế còn lại là cơ sở cho hướng phát triển ở phần Tổng kết.
