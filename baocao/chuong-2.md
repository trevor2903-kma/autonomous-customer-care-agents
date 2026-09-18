> **Tệp bàn giao cho Claude Word — bản rút gọn ngày 17/09/2026.** Toàn báo cáo đã được rút gọn còn khoảng
> 32.000 từ, tính cả chữ trong bảng. Nội dung đã lược bỏ (bản gốc đầy đủ) và khối ghi chú bàn giao trước
> đây nằm ở `baocao/doc.md`.
>
> - Số hiệu mục, hình và bảng giữ nguyên: 16 hình (Hình 2.1 – 2.16, ảnh dựng sẵn trong `hinh-ve/chuong-2/`,
>   vị trí chèn theo `hinh-ve/README.md` vẫn đúng) và 22 bảng (Bảng 2.1 – 2.22).
> - Một số dòng của bảng CSDL (2.15 – 2.20) đã được gộp các thuộc tính cùng kiểu cho gọn; bảng đầy đủ từng cột
>   nằm trong `doc.md`.
> - Hình 2.3, 2.6, 2.15 và 2.16 đã được vẽ lại bằng `hinh-ve/so-do.py`; Hình 2.14 có thêm mã DBML
>   (`hinh-ve/chuong-2/hinh-2-14-erd.dbml`) để dựng trên dbdiagram.io. Khi vẽ lại Hình 2.4, xem cảnh báo đối
>   chiếu mã nguồn trong phần ghi chú cũ ở `doc.md`.

---

# PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

## Xác định Actor

Trong hệ thống đề xuất, các tác nhân được xác định dựa trên vai trò tương tác và mức độ đặc quyền đối với dữ liệu. Hệ thống phân tách rõ ràng giữa nhóm người dùng cuối và nhóm nhân sự vận hành nhằm bảo đảm tính khách quan và an toàn dữ liệu. Ngoài hai tác nhân người dùng, hệ thống còn có một tác nhân hệ thống đảm nhiệm các tác vụ chạy nền theo chu kỳ.

Dưới đây là bảng mô tả chi tiết các tác nhân của hệ thống cùng quyền hạn tương ứng (Bảng 2.1).

Bảng 2.1. Danh sách actor

| **Actor**                              | **Đăng nhập** | **Quyền hạn chính**                                                                                                                                                                                                                                     |
|----------------------------------------|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Khách hàng (Customer)                  | Tuỳ chọn      | Mở hội thoại mới; gửi tin nhắn và nhận phản hồi thời gian thực; nhận thông báo khi ca được chuyển cho nhân viên; xem lại lịch sử hội thoại của mình (khi đã đăng nhập); được tra cứu đơn hàng của chính mình                                            |
| Quản trị viên (Admin / nhân viên CSKH) | Bắt buộc      | Xem và lọc danh sách hội thoại; chat trực tiếp với khách; nhận và xử lý hàng đợi chuyển tiếp kèm EscalationCard; duyệt hoặc sửa nháp phản hồi; quản lý kho tri thức; bật/tắt cổng cấu hình theo từng ý định; xem báo cáo hoạt động và nhật ký kiểm toán |
| Tác vụ nền (System sweeper)            | —             | Quét định kỳ các hội thoại không hoạt động để nhắc và tự đóng theo cấu hình                                                                                                                                                                             |

Về ranh giới quyền hạn, khách hàng chỉ tra cứu được những đơn hàng thuộc tài khoản đang đăng nhập. Mọi truy vấn đơn hàng đều mang theo định danh của chủ đơn, và khi không có định danh này, hệ thống sẽ không trả về bất kỳ đơn hàng nào. Đây được xác định là hành vi an toàn mặc định của hệ thống.

Dưới đây là sơ đồ mô tả các tác nhân và ranh giới của hệ thống (Hình 2.1).

Hình 2.1. Sơ đồ actor và ranh giới hệ thống

## Tổng quan thiết kế hệ thống

### Bốn trụ cột thiết kế

Toàn bộ thiết kế của hệ thống được xây dựng trên bốn nguyên tắc nền tảng, chi phối mọi quyết định kỹ thuật ở các phần sau của chương.

**Trụ cột thứ nhất: luồng xử lý cố định để bảo đảm tính dự đoán và khả năng kiểm toán.**

Thứ tự các tác tử do đồ thị quy định trước, còn việc rẽ nhánh do nút phát ngôn duy nhất thực hiện dựa trên tập cờ và quyết định của tác tử thứ ba; không tác tử nào tự chọn đường đi tại thời điểm chạy, nên hệ thống không sử dụng tác tử điều phối trung tâm. Đây là đánh đổi có chủ đích: từ bỏ quyền tự trị ở tầng điều phối để đổi lấy độ tin cậy, khả năng kiểm toán và một trần chi phí xác định. Mỗi lượt hội thoại tiêu tốn tối đa hai lời gọi mô hình sinh và một lời gọi embedding, không phụ thuộc nội dung câu hỏi; lượt xã giao và lượt chuyển cho nhân viên còn tốn ít hơn vì dùng câu mẫu cố định ở bước sinh phản hồi.

**Trụ cột thứ hai: tự trị có giới hạn ở tầng tác tử.**

Bên trong mỗi nút, tác tử vẫn có không gian quyết định riêng: tác tử phân loại chọn nhãn ý định và trích xuất thực thể, tác tử tri thức chọn truy hồi theo ý định hay trên phạm vi rộng, tác tử phản hồi chọn cách diễn đạt câu trả lời. Các quyết định này đều bị giới hạn về số bước và không tác động được tới luồng điều phối chung.

**Trụ cột thứ ba: an toàn trước các tình huống ngoài dự kiến.**

Mỗi tác tử trả về kèm độ tin cậy và tập cờ bất định. Khi gặp giới hạn năng lực, hệ thống chuyển yêu cầu cho nhân viên thay vì cố gắng trả lời; đặc biệt, khi không có tri thức làm căn cứ, hệ thống bắt buộc chuyển ca và tuyệt đối không tự sinh câu trả lời.

**Trụ cột thứ tư: cải thiện dần dưới sự phê duyệt của con người.**

Hệ thống phát hiện các mẫu lặp lại từ nhật ký kiểm toán, như những ý định thường bị chuyển tiếp, chủ đề có độ tin cậy thấp hay câu hỏi chưa có tri thức, để đề xuất bổ sung tri thức. Đề xuất chỉ được áp dụng sau khi quản trị viên phê duyệt; các tác tử không được tự thay đổi luồng điều khiển hay tự chỉnh sửa kho tri thức. Giai đoạn hiện tại mới triển khai phần thu thập dữ liệu qua tab Báo cáo, còn phần sinh đề xuất tự động thuộc giai đoạn phát triển tiếp theo.

### Kiến trúc tổng thể

Hệ thống được tổ chức theo kiến trúc phân lớp gồm bốn lớp:

- **Lớp giao diện:** Một ứng dụng Next.js duy nhất phục vụ cả cổng chat của khách hàng và bảng điều khiển của quản trị viên; trên thiết bị di động, ứng dụng được cài dưới dạng ứng dụng web tiến bộ.

- **Lớp giao tiếp:** REST API cho thao tác quản trị và tra cứu, cùng ba kênh WebSocket hai chiều: `/ws/chat` cho khách hàng, `/ws/admin-inbox` cho thông báo hàng đợi và `/ws/admin/{conversation_id}` cho quản trị viên đang mở một ca cụ thể.

- **Lớp xử lý:** Pipeline bốn tác tử trên nền LangGraph, các dịch vụ nghiệp vụ về hội thoại, cổng cấu hình, tri thức, đơn hàng, chuyển tiếp, kiểm toán và báo cáo, cùng một tác vụ nền quét các hội thoại không hoạt động.

- **Lớp lưu trữ:** PostgreSQL lưu dữ liệu nghiệp vụ và nhật ký kiểm toán, Qdrant lưu vector tri thức, không có kho lưu trữ trung gian nào khác. Bộ nhớ đa lượt được đọc từ PostgreSQL ở đầu mỗi lượt, còn trung tâm phát thời gian thực và bộ giới hạn tần suất nằm trong bộ nhớ tiến trình.

Dưới đây là sơ đồ kiến trúc tổng thể của hệ thống (Hình 2.2).

Hình 2.2. Kiến trúc tổng thể hệ thống

Trong kiến trúc trên, có hai bất biến cần được nhấn mạnh vì chúng chi phối toàn bộ phần thiết kế còn lại:

- **Định tuyến dựa trên cờ thay vì dựa trên nội dung văn bản:** Quyết định chuyển ca cho nhân viên do tác tử thứ ba đưa ra dựa trên tập cờ chặn. Không có bất kỳ vị trí nào trong hệ thống thực hiện dò tìm chuỗi ký tự trong câu trả lời của mô hình để suy ra trạng thái xử lý.

- **Điểm phát ngôn duy nhất:** Mọi tin nhắn mà hệ thống gửi tới khách hàng đều phát ra từ tác tử thứ tư, không một nút nào khác được phép ghi tin nhắn của hệ thống. Nhờ đó, toàn bộ nội dung đi ra khỏi hệ thống đều đi qua đúng một vị trí duy nhất để kiểm soát.

### Vai trò các phân hệ chính

Dưới đây là bảng mô tả vai trò và trách nhiệm của từng phân hệ trong mã nguồn, kèm thư mục tương ứng (Bảng 2.2).

Bảng 2.2. Vai trò các phân hệ

| **Phân hệ**          | **Thư mục**                  | **Trách nhiệm**                                                                                    |
|----------------------|------------------------------|----------------------------------------------------------------------------------------------------|
| Pipeline tác tử      | app/agents/                  | Định nghĩa state, bốn node xử lý, đồ thị điều phối                                                 |
| Tầng API             | app/api/routes/, app/api/ws/ | REST endpoint và các kênh WebSocket                                                                |
| Tầng service         | app/services/                | Logic nghiệp vụ tái sử dụng được: RAG, cổng, đơn hàng, chuyển tiếp, kiểm toán, báo cáo, tự đóng ca |
| Tầng mô hình dữ liệu | app/models/                  | Thực thể SQLAlchemy và các enum canonical                                                          |
| Tầng lõi             | app/core/                    | Cấu hình, kết nối CSDL/Qdrant/OpenAI, bảo mật, chuẩn hoá đầu vào, giới hạn tần suất, trace          |
| Kho tri thức         | knowledge/                   | Tài liệu Markdown canonical nằm trong repository                                                   |
| Giao diện            | apps/dashboard/              | Ứng dụng Next.js hai vai                                                                           |
| Kiểu dùng chung      | packages/shared-types/       | Enum và kiểu TypeScript đồng bộ với backend                                                        |

Nguyên tắc phân tách trách nhiệm được tuân thủ nghiêm ngặt, trong đó toàn bộ logic truy hồi nằm ở tầng dịch vụ chứ không được cài đặt trực tiếp trong các nút xử lý. Nhờ vậy, tác tử thứ hai sử dụng lại đúng hàm truy hồi mà script đo ngưỡng gọi tới, qua đó bảo đảm số liệu đo đạc phản ánh chính xác hành vi của hệ thống khi vận hành thật.

## Biểu đồ Use Case

### Biểu đồ Use Case tổng quát

Dưới đây là biểu đồ use case tổng quát của hệ thống, trình bày toàn bộ các use case thuộc hai nhóm tác nhân (Hình 2.3).

Hình 2.3. Biểu đồ use case tổng quát

**Use case của Khách hàng:**

- UC-01: Đăng ký tài khoản

- UC-02: Mở hội thoại và gửi tin nhắn

- UC-03: Nhận phản hồi tự động

- UC-04: Cung cấp thông tin bổ sung khi hệ thống hỏi lại (mã đơn hàng)

- UC-05: Tra cứu trạng thái đơn hàng của mình

- UC-06: Yêu cầu gặp nhân viên

- UC-07: Xem lịch sử hội thoại của mình

**Use case của Quản trị viên:**

- UC-08: Đăng nhập và duy trì phiên làm việc (dùng chung cho cả khách hàng và quản trị viên)

- UC-09: Xem và lọc danh sách hội thoại

- UC-10: Xem chi tiết một hội thoại kèm nhật ký tác tử

- UC-11: Nhận ca từ hàng đợi chuyển tiếp (takeover)

- UC-12: Chat trực tiếp với khách hàng

- UC-13: Duyệt nháp phản hồi

- UC-14: Sửa nháp rồi gửi

- UC-15: Từ chối nháp và tự xử lý

- UC-16: Đóng ca (resolve)

- UC-17: Upload / xoá tài liệu tri thức

- UC-18: Nạp lại toàn bộ kho tri thức (reindex)

- UC-19: Cấu hình cổng tự động theo từng ý định

- UC-20: Xem báo cáo hoạt động và chi tiết một lượt xử lý

### Đặc tả một số Use Case tiêu biểu

Phần này đặc tả hai use case tiêu biểu, có nhiều luồng thay thế và gắn trực tiếp với các cơ chế an toàn của hệ thống; sáu use case UC-01, UC-04, UC-06, UC-08, UC-13 và UC-19 được đặc tả ở phần Phụ lục.

Dưới đây là bảng đặc tả use case UC-03, use case đi qua cả bốn tác tử và cả ba kết cục giao phản hồi (Bảng 2.3).

Bảng 2.3. Đặc tả UC-03 — Nhận phản hồi tự động

| **Mục** | **Nội dung** |
|---|---|
| Tên use case | Nhận phản hồi tự động (UC-03) |
| Mô tả | Khách nhận câu trả lời do hệ thống sinh khi đủ căn cứ và ý định được phép trả lời thẳng; nếu không, use case rẽ sang chờ duyệt hoặc chuyển cho nhân viên |
| Tác nhân | Khách hàng |
| Tiền điều kiện | Hội thoại đang ở phía AI, không có nhân viên đang xử lý |
| Luồng chính | 1. Khách gửi tin nhắn qua WebSocket. 2. Hệ thống chuẩn hoá, chống trùng, kiểm tra giới hạn tần suất và xác nhận đã nhận. 3. Lưu tin khách và phát cho các phiên đang mở. 4. Pipeline chạy bốn tác tử. 5. Tác tử 3 quyết định auto_reply, cổng cho phép gửi thẳng. 6. Tác tử 4 sinh phản hồi có căn cứ. 7. Ghi trạng thái và tin nhắn AI trong một giao dịch, commit xong mới gửi. 8. Khách nhận phản hồi |
| Luồng thay thế 5a | Cổng tắt cho ý định → nháp vào hàng đợi duyệt, khách nhận tín hiệu chờ |
| Luồng thay thế 5b | Có cờ chặn → chuyển người, khách nhận thông báo chuyển tiếp |
| Luồng thay thế 7a | Nhân viên tiếp quản khi pipeline đang chạy → lượt bị huỷ, khách nhận trạng thái hiện tại |
| Hậu điều kiện | Trạng thái hội thoại được cập nhật; sáu dòng nhật ký kiểm toán được ghi cùng khoá lượt |
| Luồng sự kiện ngoại lệ | E1. Ghi CSDL thất bại sau một lần thử lại → khách nhận câu không kèm cam kết. E2. Lỗi Qdrant hoặc embedding → cờ `search_error`, chuyển người. E3. Mô hình quá 20 giây → cờ `llm_unavailable`, chuyển người. E4. Quá 20 tin trong 60 giây → khung lỗi `rate_limited`, không chạy pipeline |

Dưới đây là bảng đặc tả use case UC-11, use case thể hiện rõ nhất cơ chế so sánh rồi ghi khi hai quản trị viên cùng nhận một ca (Bảng 2.4).

Bảng 2.4. Đặc tả UC-11 — Nhận ca từ hàng đợi chuyển tiếp

| **Mục** | **Nội dung** |
|---|---|
| Tên use case | Nhận ca từ hàng đợi chuyển tiếp (UC-11) |
| Mô tả | Quản trị viên tiếp quản hội thoại trong hàng đợi người; sau đó tác tử ngừng can thiệp và tin nhắn của khách đi thẳng tới quản trị viên cho tới khi đóng ca |
| Tác nhân | Quản trị viên |
| Tiền điều kiện | Đã đăng nhập với vai trò admin; có ca đang chờ nhận |
| Luồng chính | 1. Mở hàng đợi, sắp theo mức ưu tiên giảm dần. 2. Chọn ca, xem EscalationCard. 3. Bấm Nhận ca. 4. Hệ thống kiểm tra trạng thái vẫn như lúc đọc rồi chuyển sang đang xử lý và gán quản trị viên. 5. AI tạm dừng, tin nhắn của khách đi thẳng tới quản trị viên |
| Luồng thay thế 4a | Ca đã bị người khác nhận hoặc đã đóng → lỗi xung đột, giao diện tải lại trạng thái |
| Hậu điều kiện | Hành động được ghi vào nhật ký kiểm toán |
| Luồng sự kiện ngoại lệ | E1. Quản trị viên bị hạ quyền giữa phiên → kênh quản trị trả khung `not_assigned`. E2. CSDL lỗi khi xác minh quyền → đóng kết nối mã 1011, giao diện tự nối lại |

## Thiết kế pipeline bốn tác tử

Pipeline của hệ thống là một đồ thị LangGraph tuyến tính hoàn toàn, trong đó bốn nút xử lý nối tiếp nhau theo đúng một thứ tự cố định từ điểm bắt đầu tới điểm kết thúc. Đồ thị không khai báo bất kỳ cạnh điều kiện nào và cũng không có nút riêng cho nghiệp vụ chuyển ca: việc rẽ nhánh nằm bên trong nút phát ngôn cuối cùng, còn phần việc kèm theo của chuyển tiếp do tầng dịch vụ đảm nhiệm bên ngoài đồ thị.

Dưới đây là sơ đồ pipeline bốn tác tử cố định vận hành trên nền LangGraph (Hình 2.4).

Hình 2.4. Pipeline bốn tác tử cố định trên LangGraph

### Trạng thái điều phối (ConversationState)

Toàn bộ thông tin của một lượt xử lý được lưu trong một cấu trúc dữ liệu duy nhất mà các nút trong đồ thị cùng đọc và ghi. Thiết kế của cấu trúc này có ảnh hưởng quyết định tới tính đúng đắn của hệ thống, bởi mọi tín hiệu an toàn và mọi dữ liệu nghiệp vụ đều đi qua đây.

Dưới đây là bảng mô tả các trường chính của cấu trúc trạng thái điều phối (Bảng 2.5).

Bảng 2.5. Các trường chính của ConversationState

| **Nhóm**  | **Trường**                                | **Ý nghĩa**                                                              |
|-----------|-------------------------------------------|--------------------------------------------------------------------------|
| Lõi       | conversation_id, turn_id, input           | Định danh ca, khoá gom một lượt cho kiểm toán, tin nhắn khách            |
| Lõi       | customer_id                               | Định danh khách đã đăng nhập — khoá phạm vi của tra cứu đơn hàng         |
| Lõi       | history                                   | Lịch sử các lượt trước, nạp từ CSDL. Chỉ đọc, không có reducer           |
| Lõi       | messages, trace                           | Danh sách cộng dồn (reducer add) — tin nhắn sinh ra và nhật ký từng bước |
| Lõi       | status                                    | Trạng thái hội thoại mà nút vừa ghi                                      |
| Lõi       | result                                    | Kết quả của lượt: nhánh đã đi, câu trả lời, lý do chuyển tiếp — đây là trường mà tầng WebSocket đọc để gửi cho khách |
| An toàn   | intent_confidence, retrieval_confidence   | Hai độ tin cậy tách biệt, cố ý không gộp                                 |
| An toàn   | confidence                                | Độ tin cậy chung của lượt                                                |
| An toàn   | uncertainty_flags                         | Danh sách cộng dồn các cờ bất định                                       |
| An toàn   | escalation_reason, require_human_handoff  | Lý do và cờ chuyển người                                                 |
| Nghiệp vụ | intent, entities, rag_contexts            | Ý định, thực thể, các đoạn tri thức truy hồi được                        |
| Nghiệp vụ | order_context                             | Dữ liệu đơn hàng tra được — nguồn grounding thứ ba                       |
| Nghiệp vụ | order_not_found                           | Mã đơn khách đưa mà tra không ra — tín hiệu, không phải cờ chặn          |
| Nghiệp vụ | action, priority, severity                | Quyết định của tác tử 3                                                  |
| Nối lượt  | prior_status, prior_intent, clarify_field | Trạng thái và ý định của lượt trước, phục vụ cơ chế hỏi lại              |

Cấu trúc trạng thái nêu trên gắn với ba quyết định thiết kế đáng chú ý.

**a) Trường lịch sử không dùng hàm gộp và được tách riêng khỏi trường tin nhắn.** Lịch sử là đầu vào chỉ đọc nạp từ cơ sở dữ liệu, còn trường tin nhắn là đầu ra của lượt hiện tại. Gộp hai trường sẽ nhân đôi bộ nhớ đa lượt và vô tình biến lịch sử thành một nguồn bám căn cứ, điều bị cấm tuyệt đối vì dữ liệu ở các lượt trước có thể đã thay đổi.

**b) Hàm gộp cộng dồn chỉ tiếp nhận các cờ mới phát sinh.** Mỗi nút chỉ trả về những cờ do chính nó phát ra, nhờ đó từng cờ quy được về đúng tác tử đã sinh ra nó. Đây là điều kiện để tab báo cáo phân tích được nguyên nhân khiến một lượt bị chuyển cho nhân viên.

**c) Trường định danh lượt chỉ phục vụ quan sát.** Không nút nào được đọc trường này để ra quyết định, để việc bổ sung khả năng quan sát không làm thay đổi hành vi của hệ thống.

### Agent 1 — Intent Classifier

**Đầu vào:** tin nhắn khách + lịch sử hội thoại + trạng thái/ý định lượt trước.

**Đầu ra:** {intent, category, entities, confidence, uncertainty_flags}.

**Bảng phân loại mười lăm ý định.** Danh sách ý định là một tập đóng, nhúng thẳng vào prompt kèm mô tả và ví dụ cho từng nhãn thay vì huấn luyện một bộ phân loại riêng; tác tử thứ nhất không thực hiện truy hồi. Dưới đây là bảng phân loại cùng nhóm và thực thể cần trích của từng ý định (Bảng 2.6).

Bảng 2.6. Taxonomy ý định

| **Nhóm**      | **Ý định**             | **Category** | **Thực thể trích**    |
|---------------|------------------------|--------------|-----------------------|
| Trước bán     | product_price          | pre_sale     | product_name, color   |
| Trước bán     | product_information    | pre_sale     | product_name, color   |
| Trước bán     | size_consulting        | pre_sale     | height, weight, size  |
| Trước bán     | promotion              | pre_sale     | promo_code            |
| Tra cứu chung | shipping               | general      | destination, order_id |
| Tra cứu chung | payment                | general      | order_id              |
| Tra cứu chung | membership             | general      | —                     |
| Tra cứu chung | store_information      | general      | —                     |
| Tra cứu chung | return_exchange_policy | general      | —                     |
| Sau bán       | order_status           | after_sale   | order_id              |
| Sau bán       | refund                 | after_sale   | order_id              |
| Sau bán       | exchange               | after_sale   | order_id              |
| Sau bán       | complaint              | after_sale   | order_id              |
| Xã giao       | greeting               | general      | —                     |
| Ngoài phạm vi | other                  | general      | —                     |

Nhãn hỏi chính sách đổi trả được tách khỏi nhóm yêu cầu hoàn tiền và đổi hàng: hỏi chính sách chỉ là tra cứu nên được trả lời thẳng, còn yêu cầu trả một đơn cụ thể là giao dịch phải qua duyệt nháp; nếu gộp lại, mọi câu hỏi chính sách đều bị giữ chờ duyệt.

**Trích xuất thực thể theo hai đường.** Thực thể được trích đồng thời bằng mô hình và bằng biểu thức chính quy rồi hợp nhất, ưu tiên kết quả của mô hình. Biểu thức chính quy chạy ở mọi nhánh, kể cả khi mô hình không khả dụng, nên mã đơn không bao giờ bị mất; chuỗi số chỉ xuất hiện trong ngữ cảnh số tiền bị loại khỏi trường mã đơn.

**Các cờ do tác tử thứ nhất phát ra** gồm ý định mơ hồ (`ambiguous_intent`), nhiều ý định (`multi_intent`), ngoài phạm vi (`out_of_domain`), khách yêu cầu gặp nhân viên (`human_requested`) và mô hình không khả dụng (`llm_unavailable`). Cờ yêu cầu gặp nhân viên được phát hiện bằng luật tất định neo theo động từ liên hệ đứng trước danh từ chỉ người, vì mô hình hay xếp các câu xin gặp nhân viên vào nhóm xã giao; luật chạy cả khi mô hình không khả dụng và không nhận nhầm những câu than phiền về nhân viên.

**Cơ chế suy giảm an toàn.** Khi thiếu khoá API, mô hình bị tắt hoặc lời gọi lỗi, tác tử trả về ý định không xác định, độ tin cậy bằng 0 kèm cờ `llm_unavailable`, thực thể vẫn lấy từ biểu thức chính quy và không ném ngoại lệ, nhờ đó bộ kiểm thử chạy được ngoại tuyến.

### Agent 2 — Knowledge Agent (RAG + tra cứu đơn hàng)

**Đầu vào:** ý định + thực thể + câu hỏi gốc + định danh khách.

**Đầu ra:** {rag_contexts, retrieval_confidence, order_context, order_not_found, uncertainty_flags}.

Tác tử thứ hai vận hành hai nhánh bổ trợ nhau: kho tri thức trả lời về chính sách, cơ sở dữ liệu đơn hàng trả lời về một đơn cụ thể. Việc tách hai nhánh xuất phát từ một lỗi thực tế: khách hỏi trạng thái đơn nhưng truy hồi trúng tài liệu chính sách vận chuyển với điểm đủ cao, khiến lượt được trả lời tự động dù không có dữ liệu đơn nào làm căn cứ.

**Nhánh truy hồi tri thức.** Ý định xã giao được bỏ qua truy hồi và không phát cờ bám nguồn, vì lượt xã giao không phát biểu sự thật nào cần căn cứ. Với các ý định còn lại, hệ thống truy vấn k kết quả gần nhất trên Qdrant (mặc định k = 4), ưu tiên đoạn cùng ý định; nếu không đủ kết quả hoặc điểm cao nhất dưới ngưỡng thì chạy thêm một lượt không lọc rồi gộp, để một nhãn ý định sai không làm bỏ sót tri thức đúng. Điểm cosine tốt nhất nằm dưới ngưỡng truy hồi thì phát cờ điểm truy hồi thấp.

**Nhánh tra cứu đơn hàng** chỉ chạy với các ý định gắn với đơn (order_status, shipping, refund, exchange, complaint) khi có mã đơn, luôn kèm định danh chủ đơn, và phân biệt ba tình huống. Tra được thì dữ liệu đơn trở thành nguồn căn cứ thứ ba cho tác tử thứ tư. Không ra kết quả thì chỉ ghi tín hiệu không tìm thấy đơn, không chặn, vì phần lớn trường hợp là khách gõ nhầm mã. Không tra được do lỗi cơ sở dữ liệu hoặc thiếu định danh khách thì phát cờ chưa xử lý được đơn và chuyển người, vì báo không tìm thấy đơn khi thực tế chưa tra được là cung cấp thông tin sai. Cờ này cũng được bật khi khách đưa mã sai lần thứ hai, đếm bằng cách so khớp nguyên văn câu thông báo cố định trong lịch sử. Khi tra được đơn, các cờ bám nguồn được miễn nhưng vẫn được ghi vào nhật ký để kiểm toán.

**Các cờ do tác tử thứ hai phát ra** gồm không có tri thức liên quan, điểm truy hồi thấp, lỗi tìm kiếm (sự cố Qdrant hoặc dịch vụ embedding, khác với việc kho tri thức chưa bao phủ nội dung) và chưa xử lý được đơn hàng.

### Agent 3 — Decision Engine

Tác tử thứ ba là nút ra quyết định của pipeline, đồng thời là nơi hội tụ toàn bộ các tín hiệu an toàn do những tác tử trước phát ra.

Tác tử này hoạt động hoàn toàn tất định và không gọi mô hình ngôn ngữ: việc có đủ căn cứ để trả lời hay không đã được các tác tử trước mã hoá thành tập cờ, và thêm một lời gọi mô hình vào đường xử lý chính sẽ làm hỏng NFR-1. Tác tử cũng không gộp hai thang độ tin cậy — độ tin cậy ý định do mô hình tự khai báo, còn độ tin cậy truy hồi là điểm cosine — mà giữ cả hai trong nhật ký và chỉ định tuyến dựa trên tập cờ.

Dưới đây là bảng mô tả tập cờ chặn của hệ thống cùng nguồn phát và lý do chặn tương ứng (Bảng 2.7).

Bảng 2.7. Tập cờ chặn (BLOCKING_FLAGS)

| **Cờ**                | **Nguồn** | **Vì sao chặn**                                                     |
|-----------------------|-----------|---------------------------------------------------------------------|
| multi_intent          | Agent 1   | Khách hỏi hai việc khác nhau; trả lời một việc là thiếu             |
| out_of_domain         | Agent 1   | Câu thật sự ngoài phạm vi cửa hàng                                  |
| human_requested       | Agent 1   | Khách xin gặp người rõ ràng — đừng bắt khách nói đi nói lại với bot |
| llm_unavailable       | Agent 1   | Không phân loại được                                                |
| no_relevant_knowledge | Agent 2   | Không có tri thức để bám                                            |
| low_retrieval_score   | Agent 2   | Tri thức truy hồi được quá yếu                                      |
| search_error          | Agent 2   | Sự cố hạ tầng truy hồi                                              |
| order_unresolved      | Agent 2   | Tra đơn hỏng, hoặc mã sai lần thứ hai                               |

Hai cờ cố ý không thuộc tập chặn. Cờ ý định mơ hồ chỉ mang tính thông tin, vì hệ thống chuyển ca khi không trả lời được chứ không phải khi nhãn chưa rõ, và khi căn cứ yếu thì các cờ bám nguồn đã đảm nhiệm việc chặn. Cờ rủi ro ảo giác do tác tử thứ tư phát ra sau bước quyết định, nên chính tác tử thứ tư tự chuyển ca khi phát cờ này.

**Mức ưu tiên và mức nghiêm trọng** được gán theo một bảng tra tất định dựa trên ý định (khiếu nại cao nhất, tiếp theo là hoàn tiền, rồi đổi hàng và tra cứu đơn, các ý định còn lại ở mức thấp) và chỉ dùng để sắp xếp hàng đợi.

**Nhánh hỏi lại thông tin.** Khi ý định gắn với đơn hàng nhưng thiếu mã đơn và không có cờ chặn nào, tác tử thứ ba định tuyến sang nhánh hỏi lại để tác tử thứ tư hỏi mã đơn, hội thoại chuyển sang trạng thái chờ khách. Khoá chống lặp bảo đảm chỉ hỏi một lần: lượt sau vẫn thiếu thông tin thì chuyển thẳng cho nhân viên.

**Cơ chế an toàn luôn được ưu tiên trên nhánh hỏi lại**, theo đó nhánh hỏi lại chỉ được xét tới khi cổng an toàn không chặn lượt xử lý.

### Agent 4 — Response Generator

Tác tử thứ tư là điểm phát ngôn duy nhất của hệ thống tới khách hàng, sử dụng ba nguồn căn cứ: tệp sự thật lõi của cửa hàng (giờ hỗ trợ, phí vận chuyển, thanh toán, đổi trả, bảng kích cỡ, chương trình thành viên) được nạp thẳng vào prompt ở mọi lượt; các đoạn tri thức truy hồi được, mỗi đoạn kèm một trong năm nhãn quy trình xử lý, tài liệu tra cứu, câu hỏi thường gặp, khuyến mãi hoặc tài liệu tải lên; và dữ liệu đơn hàng của chính khách khi tra cứu thành công.

**Năm nhánh xử lý được xét theo thứ tự:** câu hỏi làm rõ mã đơn (câu cố định, không gọi mô hình, chuyển hội thoại sang chờ khách); thông báo chuyển tiếp (không gọi mô hình, có bản trong và ngoài giờ hỗ trợ); câu mẫu cố định cho ý định xã giao (xét trước cơ chế chặn chống ảo giác); thông báo không tìm thấy đơn (câu cố định, dùng chung cho mã không tồn tại và mã thuộc người khác để không lộ đơn hàng của khách khác); và sinh phản hồi có căn cứ cho mọi trường hợp còn lại.

**Cơ chế chặn cứng chống ảo giác.** Khi không có nguồn căn cứ nào hoặc không gọi được mô hình, hệ thống không sinh phản hồi mà trả câu dự phòng kèm cờ rủi ro ảo giác. Câu dự phòng không được gửi tới khách; cờ này khiến chính tác tử thứ tư chuyển ca sang hàng đợi nhân viên kèm lý do đúng định dạng.

**Các quy tắc bám nguồn trong prompt hệ thống** là phần được đúc kết trực tiếp từ những lỗi quan sát được trong quá trình vận hành thực tế. Dưới đây là bảng tổng hợp các quy tắc này cùng dạng lỗi mà mỗi quy tắc hướng tới phòng chống (Bảng 2.8).

Bảng 2.8. Các quy tắc grounding của Agent 4

| **Quy tắc** | **Nội dung** | **Chống dạng lỗi nào** |
|---|---|---|
| Chỉ dùng nguồn được cấp | Không nói gì ngoài facts.md, rag_contexts, order_context | Bịa ra cái "có" |
| Không suy diễn vắng mặt | Nguồn im lặng không có nghĩa là không tồn tại; phải nói "em chưa có thông tin về X" | Bịa ra cái "không có" |
| Danh sách trong nguồn là danh sách MỞ | Không có chữ "chỉ"/"duy nhất" thì không coi là danh sách đóng | Bịa ra cái "không có" |
| Giới hạn hành động | Chỉ tra cứu được trạng thái đơn; không nói đã hoàn tiền, huỷ/đổi đơn hay tạo yêu cầu | Bịa ra hành động |
| Không tự hứa chuyển người | Việc chuyển ca do hệ thống quyết định; tác tử 4 hứa chuyển nhân viên là nói sai | Bịa ra hành động |
| Bám quy trình | Làm đúng thứ tự các bước của đoạn "Quy trình xử lý", mỗi lượt chỉ hỏi 1–2 điều | Nhảy tới kết luận |
| Lịch sử không phải dữ liệu đơn | Trạng thái đơn chỉ lấy từ dữ liệu đơn của lượt hiện tại | Dữ liệu cũ |
| Văn xuôi thuần | Khung chat không render markdown; cấm ký hiệu định dạng | Lỗi hiển thị |

## Thiết kế cơ chế an toàn và kiểm soát

### Cổng cấu hình và ba kết cục giao phản hồi

Cổng cấu hình cho phép quản trị viên lựa chọn mức độ tự động mà hệ thống được phép thực hiện, đồng thời bảo đảm thao tác cấu hình này không tác động tới logic an toàn của hệ thống.

Dưới đây là bảng mô tả ba kết cục giao phản hồi cùng điều kiện và trạng thái tương ứng (Bảng 2.9).

Bảng 2.9. Ba kết cục giao phản hồi

| **Kết cục**  | **Điều kiện**                                    | **Ai gửi cho khách**           | **Trạng thái**   |
|--------------|--------------------------------------------------|--------------------------------|------------------|
| Gửi thẳng    | auto_reply + không cờ chặn + cổng bật cho ý định | AI                             | REPLIED          |
| Duyệt nháp   | auto_reply + không cờ chặn + cổng tắt cho ý định | Quản trị viên (duyệt/sửa nháp) | PENDING_APPROVAL |
| Chuyển người | Có cờ chặn                                       | Quản trị viên (xử lý từ đầu)   | IN_HUMAN_QUEUE   |

Dưới đây là cây quyết định dẫn từ tập cờ tới ba kết cục giao phản hồi nêu trên (Hình 2.5).

Hình 2.5. Cây quyết định từ tập cờ tới ba kết cục giao phản hồi

**Bất biến FR-GATE-2.** Cổng cấu hình chỉ can thiệp vào những ca tác tử thứ ba đã quyết định trả lời tự động; ca thuộc diện chuyển người luôn vào hàng đợi người bất kể cấu hình. Ranh giới này tách hai loại quyết định: có đủ căn cứ để trả lời hay không thuộc phạm vi an toàn, do mã tất định quyết định; loại yêu cầu này có được trả lời tự động hay không thuộc chính sách kinh doanh, do con người cấu hình.

Mặc định, cổng trả lời tự động được bật nhưng tắt cho hoàn tiền, đổi hàng và khiếu nại. Cấu hình gồm một bản ghi toàn cục và một bảng luật theo ý định, kèm bộ đệm có thời gian sống ngắn. Cổng cố ý không chứa ngưỡng truy hồi: ngưỡng là giá trị đo trên kho tri thức thật, đọc từ biến môi trường `RETRIEVAL_THRESHOLD`. Khi không đọc được cấu hình do lỗi cơ sở dữ liệu, hệ thống gửi thẳng câu trả lời vì câu trả lời đó đã có căn cứ và đã qua cổng an toàn.

### Vòng đời hội thoại

Dưới đây là bảng liệt kê tập trạng thái canonical của hội thoại, phân theo nhóm cùng ý nghĩa của từng trạng thái (Bảng 2.10).

Bảng 2.10. Tập trạng thái hội thoại (canonical, dùng chung backend và frontend)

| **Nhóm**   | **Trạng thái**                                | **Ý nghĩa**                           |
|------------|-----------------------------------------------|---------------------------------------|
| Khởi tạo   | NEW, ACTIVE_AI                                | Ca vừa tạo / đang ở phía AI           |
| Đang xử lý | CLASSIFYING, RETRIEVING, DECIDING, RESPONDING | Trạng thái trung gian của bốn tác tử  |
| Phía AI    | REPLIED                                       | Đã trả lời tự động                    |
| Phía AI    | AWAITING_CUSTOMER                             | Đang chờ khách bổ sung thông tin      |
| Chờ người  | PENDING_APPROVAL                              | Nháp chờ quản trị viên duyệt          |
| Chờ người  | IN_HUMAN_QUEUE                                | Trong hàng đợi chuyển tiếp            |
| Chờ người  | HUMAN_HANDLING                                | Quản trị viên đang xử lý, AI tạm dừng |
| Kết thúc   | RESOLVED, CLOSED                              | Ca đã đóng                            |

Dưới đây là máy trạng thái mô tả các phép chuyển trạng thái hợp lệ trong vòng đời một hội thoại (Hình 2.6).

Hình 2.6. Máy trạng thái vòng đời hội thoại

Trên bảng điều khiển quản trị, các trạng thái được nhóm lại thành ba nhóm hiển thị gồm nhóm đang xử lý, nhóm chờ quản trị viên và nhóm đã kết thúc. Khi phát sinh lỗi kỹ thuật, ca cũng được chuyển vào hàng đợi người nhưng có gắn thêm nhãn \[error\] để phân biệt với những ca thực sự cần tới sự can thiệp của con người.

### Cơ chế so-sánh-rồi-ghi (CAS) và thứ tự ghi/báo

Tại tầng điều phối lượt xử lý, hệ thống phải giải quyết ba vấn đề về tính đúng đắn của dữ liệu.

**a) Tranh chấp trạng thái.** Một lượt pipeline mất vài giây, trong lúc đó quản trị viên có thể tiếp quản hoặc đóng ca; nếu lượt tự động vẫn ghi kết quả đè lên trạng thái mới, sẽ có hai bên cùng trao đổi với khách hàng. Vì vậy mọi thay đổi trạng thái đều dùng cơ chế so sánh rồi ghi: trạng thái chỉ được ghi nếu giá trị hiện tại vẫn đúng bằng giá trị đã đọc ở đầu lượt. Nếu không khớp, cả lượt bị huỷ: hệ thống không lưu và không gửi nội dung nào, khách chỉ nhận khung trạng thái hiện tại để giao diện gỡ chỉ báo đang soạn tin. Lượt bị huỷ vẫn được ghi nhật ký với dấu hiệu riêng để tab báo cáo không nhầm với ca chuyển cho nhân viên thật sự.

**b) Thứ tự giữa thao tác ghi và thao tác thông báo.** Nếu hệ thống báo khách rằng yêu cầu đã được chuyển tới nhân viên rồi mới ghi cơ sở dữ liệu, và bước ghi gặp lỗi, khách sẽ nhận một cam kết về một ca không tồn tại trong hàng đợi. Vì vậy hệ thống ghi trước, thông báo sau: trạng thái, tin nhắn phản hồi và phiếu chuyển tiếp được ghi trong cùng một giao dịch, và chỉ khi giao dịch commit thành công mới gửi thông báo cho khách. Bước ghi được bảo vệ để không bị huỷ giữa chừng và được thử lại một lần; nếu vẫn thất bại, khách nhận một câu trả lời không kèm bất kỳ cam kết nào.

**c) Xử lý tuần tự theo từng khách hàng.** Các lượt của cùng một khách, kể cả khi khách mở nhiều tab, được xử lý tuần tự dưới một khoá theo thứ tự đến, nên hai tin nhắn gửi liên tiếp không chạy chồng lên nhau và không tạo ra hai ca riêng biệt.

### Human-in-the-loop và EscalationCard

Phiếu chuyển tiếp là thẻ ngữ cảnh được đính kèm mỗi ca chuyển tiếp, dựng lên từ trạng thái cuối cùng của pipeline. Mục tiêu của thiết kế này là giúp quản trị viên khi nhận ca có ngay toàn bộ thông tin cần thiết để xử lý, thay vì phải đọc lại từ đầu toàn bộ nội dung hội thoại.

Dưới đây là bảng mô tả các thành phần của phiếu chuyển tiếp (Bảng 2.11).

Bảng 2.11. Thành phần EscalationCard

| **Trường**         | **Nội dung**                                                                 |
|--------------------|------------------------------------------------------------------------------|
| summary            | Tin nhắn khách kích hoạt việc chuyển tiếp                                    |
| intent, entities   | Ý định và thực thể đã nhận diện                                              |
| rag_context        | Tối đa 3 nguồn tri thức hàng đầu, kèm điểm và trích đoạn ngắn                |
| escalation_reason  | Lý do cụ thể (danh sách cờ chặn, hoặc clarify_unresolved...)                 |
| priority, severity | Mức ưu tiên và nghiêm trọng                                                  |
| suggested_reply    | Nháp gợi ý — rỗng với ca chuyển người, là nháp của tác tử 4 với ca chờ duyệt |

Hàng đợi được sắp xếp theo mức ưu tiên giảm dần, sau đó tới thời điểm của tin nhắn cuối cùng mới nhất. Do mức ưu tiên được lưu dưới dạng chuỗi ký tự, việc sắp xếp phải sử dụng biểu thức ánh xạ sang giá trị số ngay trong câu truy vấn, bởi nếu sắp xếp theo thứ tự bảng chữ cái thì kết quả sẽ không phản ánh đúng mức độ ưu tiên thực tế.

**Cổng chặn theo trạng thái hội thoại.** Khi hội thoại đang ở một trong các trạng thái có nhân viên xử lý, pipeline tự động sẽ không được kích hoạt. Toàn bộ tin nhắn của khách hàng khi đó được định tuyến thẳng tới quản trị viên thông qua kênh thời gian thực.

### Tự động nhắc và đóng hội thoại

Hệ thống bố trí một tác vụ nền chạy theo chu kỳ để quét các hội thoại đang ở phía xử lý tự động mà khách hàng đã im lặng quá lâu. Phần logic phân loại được cài đặt dưới dạng một hàm thuần, tách biệt hoàn toàn khỏi phần nhập xuất, và xử lý ba tình huống:

- Hội thoại chưa được nhắc và thời gian im lặng đã vượt ngưỡng thứ nhất thì hệ thống gửi một tin nhắc duy nhất, sử dụng câu mẫu cố định và không gọi mô hình.

- Hội thoại đã được nhắc, khách hàng vẫn chưa phản hồi và thời gian kể từ lúc nhắc đã vượt ngưỡng thứ hai thì hệ thống tiến hành đóng ca.

- Các trạng thái còn lại không phát sinh hành động nào.

Câu lệnh cập nhật có điều kiện sẽ kiểm tra lại trạng thái ngay tại thời điểm ghi, nhờ đó nếu quản trị viên vừa tiếp quản hoặc khách hàng vừa nhắn lại trong khoảng giữa hai lần quét thì ca sẽ không bị đóng nhầm. Bên cạnh đó, các ca đang chờ nhân viên xử lý không bao giờ bị tự động đóng, đúng theo yêu cầu FR-ASYNC-4.

## Thiết kế kho tri thức và cơ chế RAG

### Kho tri thức canonical trong repository

Thay vì quản lý tri thức qua chức năng tải tài liệu lên như cách làm phổ biến, đề tài tổ chức kho tri thức dưới dạng các tệp Markdown nằm trong repository, phiên bản hoá bằng Git; cơ sở dữ liệu vector chỉ là bản phái sinh, dựng lại được hoàn toàn bằng một lệnh. Lý do là tri thức là một phần cấu thành sản phẩm nên cần được rà soát và theo dõi lịch sử như mã nguồn, còn cơ chế xoá sạch rồi nạp lại loại bỏ triệt để bài toán đồng bộ trạng thái giữa kho tệp và cơ sở dữ liệu vector. Chức năng tải tài liệu lên qua giao diện vẫn được giữ nhưng chỉ là bổ sung tạm thời: tài liệu tải lên theo đường này bị xoá ở lần nạp lại toàn bộ kế tiếp, và đây là hành vi đúng đã được ghi rõ trong tài liệu thiết kế.

Dưới đây là bảng mô tả cấu trúc kho tri thức của hệ thống (Bảng 2.12).

Bảng 2.12. Cấu trúc kho tri thức

| **Thư mục**          | **Loại**  | **Nội dung**                                                                                            | **Số tài liệu** |
|----------------------|-----------|---------------------------------------------------------------------------------------------------------|-----------------|
| knowledge/facts.md   | facts     | Sự thật lõi cửa hàng, nạp thẳng vào prompt, không vào vector database                                   | 1               |
| knowledge/faq/       | faq       | Câu hỏi thường gặp: giá, đặt hàng, thanh toán, thành viên, theo dõi đơn, khuyến mãi, thông tin cửa hàng | 7               |
| knowledge/reference/ | reference | Tài liệu tra cứu: chính sách đổi trả, chính sách vận chuyển, hướng dẫn chọn size, bảo quản sản phẩm     | 4               |
| knowledge/case/      | case      | Quy trình xử lý tình huống: hàng lỗi, đơn giao chậm, đổi size, yêu cầu hoàn tiền                        | 4               |
| knowledge/promotion/ | promotion | Chương trình khuyến mãi theo đợt — thư mục đã dựng sẵn, giai đoạn này chưa có tài liệu                  | 0               |

Mỗi tài liệu đều có phần frontmatter khai báo ba trường gồm tiêu đề, nhãn ý định và một danh sách các câu hỏi, trong đó danh sách câu hỏi ghi nhận những cách diễn đạt mà khách hàng có thể dùng để hỏi về nội dung của tài liệu.

Dưới đây là sơ đồ mô tả hai đường nạp tri thức vào hệ thống, gồm đường chính thức đi từ repository và đường tải tài liệu lên tạm thời từ giao diện quản trị (Hình 2.7).

Hình 2.7. Hai đường nạp kho tri thức: canonical và ad-hoc

### Chia đoạn theo section

Hệ thống chia đoạn theo từng mục của tài liệu Markdown: mỗi mục được giữ nguyên văn kể cả bảng và danh sách đánh số; chỉ mục quá dài mới cắt theo cửa sổ câu; mục đánh dấu nguyên khối luôn được giữ nguyên để không mất thứ tự các bước chẩn đoán. Mục ghi chú nội bộ dành cho nhân viên, vốn chứa những hành động hệ thống không được cam kết với khách như quy trình hoàn tiền, bị loại khỏi chỉ mục ngay tại nguồn.

### Mở rộng truy vấn (query-expansion)

Mở rộng truy vấn là kỹ thuật có đóng góp lớn nhất vào chất lượng truy hồi của hệ thống.

**Vấn đề đặt ra.** Khách hàng hỏi bằng giọng nói thường ngày, còn kho tri thức được viết bằng giọng văn bản trang trọng của tài liệu chính sách, nên vector biểu diễn của hai cách diễn đạt cách khá xa nhau dù cùng đề cập một nội dung.

**Giải pháp áp dụng.** Ngoài các điểm vector của thân tài liệu, hệ thống tạo thêm một điểm vector cho mỗi câu hỏi khai báo trong frontmatter: vector của điểm là vector của câu hỏi, còn nội dung trả về vẫn là thân tài liệu đầy đủ. Phép so khớp khi đó chuyển từ câu hỏi với văn bản sang câu hỏi với câu hỏi và cho điểm cao hơn hẳn; số liệu đo được trình bày ở mục 3.3.4.

**Cơ chế định danh điểm ổn định.** Định danh của mỗi điểm được sinh tất định từ đường dẫn tài liệu và chỉ số đoạn, nên thao tác nạp lại mang tính luỹ đẳng và việc chỉnh sửa một tệp không ảnh hưởng tới các tệp khác trong kho.

### Nạp lại theo cơ chế blue/green

Phương án nạp lại theo kiểu xoá collection rồi nạp lại từ đầu có một hạn chế nghiêm trọng: trong suốt thời gian nạp, mọi thao tác truy hồi rơi vào một collection rỗng hoặc nạp dở, nên toàn bộ lượt hội thoại trong khoảng thời gian đó đều bị chuyển cho nhân viên.

**Giải pháp áp dụng.** Tên collection phục vụ truy vấn là một alias trỏ tới một collection vật lý có hậu tố thời gian. Quy trình nạp lại gồm bốn bước:

- Tạo một collection vật lý mới.

- Nạp toàn bộ kho tri thức vào collection mới, trong khi khách hàng vẫn được phục vụ bằng bản dữ liệu cũ.

- Đổi hướng alias bằng một lời gọi duy nhất, tận dụng thao tác nguyên tử mà Qdrant cung cấp.

- Xoá collection cũ và dọn các collection không còn được tham chiếu.

Nếu quá trình nạp gặp lỗi giữa chừng, bản dựng dở bị loại bỏ, alias được giữ nguyên và lỗi được ném lên tầng trên, nên tầng truy hồi không bao giờ gặp collection rỗng.

Dưới đây là sơ đồ mô tả bốn bước của quy trình nạp lại kho tri thức theo cơ chế blue/green (Hình 2.8).

Hình 2.8. Quy trình nạp lại kho tri thức theo cơ chế blue/green

## Các biểu đồ tuần tự

### Luồng trả lời tự động

Dưới đây là biểu đồ tuần tự mô tả luồng trả lời tự động, tức nhánh gửi thẳng câu trả lời cho khách hàng (Hình 2.9).

Hình 2.9. Biểu đồ tuần tự — Luồng trả lời tự động

### Luồng chuyển tiếp cho nhân viên

Dưới đây là biểu đồ tuần tự mô tả luồng chuyển ca cho nhân viên khi xuất hiện cờ chặn (Hình 2.10).

Hình 2.10. Biểu đồ tuần tự — Luồng chuyển tiếp cho nhân viên

### Luồng hỏi lại mã đơn và nối lượt

Đây là luồng xử lý phức tạp nhất của hệ thống xét về mặt quản lý trạng thái. Dưới đây là biểu đồ tuần tự mô tả luồng hỏi lại mã đơn và nối lượt (Hình 2.11).

Hình 2.11. Biểu đồ tuần tự — Luồng hỏi lại mã đơn và nối lượt

Luồng này có hai chi tiết kỹ thuật được bổ sung để khắc phục hai lỗi phát sinh trong vận hành thực tế.

**Lỗi thứ nhất: dãy số đứng một mình bị phân loại nhầm vào nhóm ngoài phạm vi.** Khi khách chỉ gõ một dãy số là mã đơn, mô hình có xu hướng xếp tin nhắn vào nhãn ngoài phạm vi, phát cờ chặn và chuyển ca cho nhân viên dù khách vừa trả lời đúng yêu cầu. Giải pháp là nhận diện ngữ cảnh nối lượt và khôi phục ý định gốc một cách tất định, bỏ qua lời gọi mô hình ở bước này.

**Lỗi thứ hai: truy hồi bằng dãy số cho điểm rất thấp.** Độ tương tự cosine giữa một dãy số mã đơn với toàn bộ tài liệu trong kho chỉ khoảng 0,253, khiến hệ thống phát cờ điểm truy hồi thấp và lại chuyển ca không cần thiết. Giải pháp là ở lượt nối, tác tử thứ hai truy hồi bằng chính câu hỏi gốc của khách, tức tin nhắn gần nhất không phải dãy số đơn thuần.

Giữ đúng ý định gốc cũng là yêu cầu nghiệp vụ: khi khách đặt vấn đề hoàn đơn, lượt nối vẫn phải giữ ý định hoàn tiền để tiếp tục đi qua bước duyệt nháp, không được hạ xuống thành ý định tra cứu trạng thái đơn hàng.

### Luồng duyệt nháp

Dưới đây là biểu đồ tuần tự mô tả luồng giữ nháp phản hồi để quản trị viên duyệt trước khi gửi (Hình 2.12).

Hình 2.12. Biểu đồ tuần tự — Luồng duyệt nháp

Khi nháp phản hồi bị giữ lại, khách hàng chỉ nhận được một tín hiệu chờ chứ không nhận bất kỳ phần nội dung nào của nháp. Nội dung chỉ rời khỏi hệ thống sau khi đã có người phê duyệt, đúng theo nguyên tắc điểm phát ngôn duy nhất đã trình bày ở mục 2.2.2.

### Luồng tự động nhắc và đóng ca

Dưới đây là biểu đồ tuần tự mô tả hoạt động của tác vụ nền quét các hội thoại im lặng để nhắc và tự đóng ca (Hình 2.13).

Hình 2.13. Biểu đồ tuần tự — Tác vụ nền tự nhắc và đóng ca

## Thiết kế cơ sở dữ liệu

### Sơ đồ quan hệ thực thể

Dưới đây là sơ đồ quan hệ thực thể của cơ sở dữ liệu, thể hiện tám bảng cùng các liên kết giữa chúng (Hình 2.14).

Hình 2.14. Sơ đồ quan hệ thực thể (ERD)

### Chi tiết các bảng

Các thực thể đều dựng trên những lớp nền dùng chung cung cấp sẵn khoá chính và các mốc thời gian, nên phần mô tả từng bảng phía sau chỉ liệt kê các thuộc tính riêng của bảng đó.

Dưới đây là bảng mô tả cấu trúc dữ liệu chung do các lớp nền cung cấp (Bảng 2.13).

Bảng 2.13. Cấu trúc dữ liệu chung (lớp nền Base, UUIDMixin và TimestampMixin)

| **Thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc** | **Mô tả** |
|---|---|---|---|
| id | UUID | Khoá chính, sinh phía ứng dụng bằng `uuid4` | Do `UUIDMixin` cấp; biết trước định danh trước khi commit để gắn vào nhật ký của lượt |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() | Do `TimestampMixin` cấp; thời điểm tạo |
| updated_at | TIMESTAMPTZ | NOT NULL, server_default now(), onupdate now() | Do `TimestampMixin` cấp; thời điểm cập nhật gần nhất |

`UUIDMixin` được dùng cho sáu lớp thực thể, `TimestampMixin` chỉ `Conversation` dùng; hai bảng cấu hình cổng dùng khoá mang ý nghĩa nghiệp vụ thay vì UUID.

Dưới đây là bảng mô tả các thuộc tính riêng của bảng tài khoản người dùng (Bảng 2.14).

Bảng 2.14. Bảng user

| **Tên thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc**                  | **Mô tả**                                 |
|---------------|------------------|--------------------------------|-------------------------------------------|
| id            | UUID             | Khoá chính                     | Định danh                                 |
| email         | VARCHAR(255)     | NOT NULL, UNIQUE, index        | Định danh đăng nhập, chuẩn hoá chữ thường |
| password_hash | VARCHAR(255)     | NOT NULL                       | Băm bcrypt                                |
| role          | VARCHAR(16)      | NOT NULL                       | admin hoặc customer                       |
| display_name  | VARCHAR(255)     | nullable                       | Tên hiển thị                              |
| created_at    | TIMESTAMPTZ      | NOT NULL, server_default now() | Thời điểm tạo                             |

Dưới đây là bảng mô tả các thuộc tính riêng của bảng hội thoại (Bảng 2.15).

Bảng 2.15. Bảng conversation

| **Tên thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc** | **Mô tả** |
|---|---|---|---|
| id | UUID | Khoá chính | Định danh |
| customer_id | UUID | nullable, FK → user.id, ON DELETE SET NULL, index | Khách sở hữu; NULL với khách vãng lai |
| customer_identifier | VARCHAR(255) | nullable | Nhãn nhận dạng khách vãng lai |
| status | VARCHAR(32) | NOT NULL, default NEW, index | Trạng thái canonical |
| current_intent | VARCHAR(64) | nullable | Ý định hiện tại |
| entities, uncertainty_flags | JSONB | NOT NULL, default rỗng | Thực thể tích luỹ, các cờ bất định |
| confidence | FLOAT | nullable | Độ tin cậy |
| escalation_reason | TEXT | nullable | Lý do chuyển tiếp |
| priority, severity | VARCHAR(16) | nullable | Mức ưu tiên và nghiêm trọng |
| escalation_card | JSONB | nullable | Thẻ ngữ cảnh chuyển tiếp |
| assigned_admin_id | UUID | nullable, không khoá ngoại cứng | Quản trị viên đang xử lý |
| last_message_at, auto_resolve_reminded_at | TIMESTAMPTZ | nullable | Thời điểm tin cuối; mốc đã gửi tin nhắc |
| created_at, updated_at | TIMESTAMPTZ | NOT NULL, server_default now() | Do `TimestampMixin` cấp |

Dưới đây là bảng mô tả các thuộc tính riêng của bảng tin nhắn (Bảng 2.16).

Bảng 2.16. Bảng message

| **Tên thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc** | **Mô tả** |
|---|---|---|---|
| id | UUID | Khoá chính | Định danh |
| conversation_id | UUID | NOT NULL, FK → conversation.id, ON DELETE CASCADE, index | Hội thoại chứa tin |
| sender | VARCHAR(16) | NOT NULL | customer / ai / admin |
| content | TEXT | NOT NULL | Nội dung |
| intent, confidence | VARCHAR(64), FLOAT | nullable | Siêu dữ liệu phân loại |
| client_msg_id | VARCHAR(64) | nullable; chỉ mục duy nhất từng phần cùng conversation_id | Định danh do client sinh, chống trùng khi gửi lại |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() | Thời điểm |

Vi phạm chỉ mục duy nhất trên cặp (conversation_id, client_msg_id) là tín hiệu tin nhắn được gửi lại, tạo thành lớp chống trùng bền vững ở tầng cơ sở dữ liệu.

Dưới đây là bảng mô tả các thuộc tính riêng của bảng đơn hàng (Bảng 2.17).

Bảng 2.17. Bảng order

| **Tên thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc** | **Mô tả** |
|---|---|---|---|
| id | UUID | Khoá chính | Định danh |
| order_code | VARCHAR(32) | NOT NULL, UNIQUE, index | Mã đơn, chỉ gồm chữ số |
| customer_id | UUID | NOT NULL, FK → user.id, ON DELETE CASCADE, index | Chủ đơn — khoá phạm vi tra cứu |
| status | VARCHAR(16) | NOT NULL | Trạng thái đơn |
| items_summary, region | VARCHAR(255), VARCHAR(64) | NOT NULL | Tóm tắt sản phẩm, khu vực giao |
| ordered_at, shipped_at, delivered_at, cancelled_at | TIMESTAMPTZ | ordered_at NOT NULL; còn lại nullable | Các mốc theo trạng thái |
| estimated_delivery, tracking_code | TIMESTAMPTZ, VARCHAR(64) | nullable | Ngày dự kiến giao, mã vận đơn |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() | Thời điểm tạo bản ghi |

Mã đơn chỉ gồm chữ số để biểu thức chính quy luôn trích được kể cả khi mô hình không khả dụng; các mốc thời gian tách thành cột riêng để hệ thống nêu đúng ngày giao thực tế thay vì ngày dự kiến.

Dưới đây là bảng mô tả các thuộc tính riêng của bảng nhật ký kiểm toán (Bảng 2.18).

Bảng 2.18. Bảng audit_log

| **Tên thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc** | **Mô tả** |
|---|---|---|---|
| id | UUID | Khoá chính | Định danh |
| conversation_id, message_id | UUID | nullable, không khoá ngoại cứng, index trên conversation_id | Nhật ký bền cả khi hội thoại bị xoá |
| turn_id | UUID | nullable, index | Khoá gom các dòng của một lượt |
| duration_ms | INTEGER | nullable | Thời gian, ý nghĩa theo loại dòng |
| node, action | VARCHAR(32), VARCHAR(64) | nullable | Loại dòng (customer / intent / knowledge / decision / response / delivery / admin) và hành động |
| confidence | FLOAT | nullable | Độ tin cậy của bước |
| uncertainty_flags, detail | JSONB | NOT NULL, default rỗng | Cờ và chi tiết của bước |
| escalation_reason | TEXT | nullable | Lý do |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now(), index | Mọi truy vấn báo cáo lọc theo thời gian |

Mỗi lượt khách sinh sáu dòng nhật ký cùng khoá lượt: tiếp nhận tin nhắn, bốn nút pipeline và kết cục giao phản hồi. Với dòng của nút, `duration_ms` là thời gian chạy của nút; với dòng kết cục, đó là thời gian đầu cuối phía máy chủ, từ lúc đọc được tin nhắn tới lúc trao khung phản hồi cho socket — con số dùng để đối chiếu NFR-1.

Dưới đây là bảng mô tả các thuộc tính riêng của bảng sổ tài liệu tri thức (Bảng 2.19).

Bảng 2.19. Bảng knowledge_document

| **Tên thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc** | **Mô tả** |
|---|---|---|---|
| id | UUID | Khoá chính | Định danh |
| title | VARCHAR(255) | NOT NULL | Tên hiển thị |
| source_type | VARCHAR(16) | nullable | Định dạng gốc: pdf / docx / txt / md |
| file_ref | VARCHAR(512) | UNIQUE, nullable | Khoá ổn định, trùng payload.source trên Qdrant |
| doc_type, intent | VARCHAR(16), VARCHAR(64) | nullable | Thư mục kho tri thức hoặc upload; nhãn ý định trong frontmatter |
| chunks | INTEGER | NOT NULL, default 0 | Số điểm vector đã ghi |
| metadata | JSONB | NOT NULL, default rỗng | Siêu dữ liệu bổ sung |
| status | VARCHAR(16) | NOT NULL, default pending | indexed / pending |
| embedding_ref | VARCHAR(255) | nullable | Tham chiếu Qdrant |
| created_at, indexed_at | TIMESTAMPTZ | created_at NOT NULL; indexed_at nullable | Thời điểm tạo và thời điểm index xong |

Bảng này chỉ là sổ hiển thị cho màn hình Quản lý tri thức, được dựng lại sau mỗi lần nạp toàn bộ; nguồn chính thức vẫn là thư mục `knowledge/` và dữ liệu trên Qdrant.

Cấu hình cổng được lưu trong hai bảng: một bảng toàn cục chỉ có một dòng và một bảng luật mỗi ý định một dòng (Bảng 2.20).

Bảng 2.20. Bảng cấu hình cổng

| **Bảng** | **Tên thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc** | **Mô tả** |
|---|---|---|---|---|
| gate_config | id | INTEGER | Khoá chính, luôn bằng 1 | Bảng chỉ có một dòng |
| gate_config | auto_reply_enabled, auto_resolve_enabled | BOOLEAN | NOT NULL, default true | Công tắc trả lời tự động và tự đóng ca |
| gate_config | auto_resolve_minutes | INTEGER | NOT NULL, default 30 | Ngưỡng im lặng thứ nhất (phút) — gửi tin nhắc |
| gate_config | auto_resolve_grace_minutes | INTEGER | NOT NULL, default 15 | Ngưỡng thứ hai kể từ lúc nhắc (phút) — đóng ca |
| gate_intent_rule | intent | VARCHAR(64) | Khoá chính | Tên ý định |
| gate_intent_rule | label | VARCHAR(64) | NOT NULL | Nhãn hiển thị |
| gate_intent_rule | sensitive | BOOLEAN | NOT NULL, default false | Chỉ dùng để hiển thị nhãn |
| gate_intent_rule | send_directly | BOOLEAN | NOT NULL, default true | true là gửi thẳng, false là giữ nháp chờ duyệt |

### Sơ đồ lớp miền dữ liệu

Các bảng ở mục 2.8.2 tồn tại trong mã nguồn dưới dạng lớp SQLAlchemy 2 khai báo, dựng trên ba lớp nền ở Bảng 2.13; khoá UUID được sinh phía ứng dụng để biết định danh tin nhắn trước khi commit. Tám lớp thực thể chia thành ba nhóm: nhóm hội thoại gồm `User`, `Conversation`, `Message` liên kết một nhiều và `Order` gắn với `User` qua khoá chủ đơn; nhóm cấu hình gồm `GateConfig` và `GateIntentRule`; nhóm hỗ trợ gồm `AuditLog` và `KnowledgeDocument`, cố ý không có khoá ngoại cứng (Hình 2.15).

Hình 2.15. Sơ đồ lớp miền dữ liệu

Tầng xử lý không được mô hình hoá bằng lớp: bốn tác tử là các hàm bất đồng bộ nhận và trả cấu trúc trạng thái kiểu `TypedDict`, tầng dịch vụ là các hàm không giữ trạng thái, nên quan hệ giữa chúng được biểu diễn bằng sơ đồ luồng ở Hình 2.4. Sơ đồ lớp tách theo từng miền nằm ở Phụ lục (Hình PL.5 và Hình PL.6).

## Thiết kế bảo mật

### Xác thực và phân quyền

**Xác thực.** Mật khẩu được băm bằng bcrypt dùng trực tiếp (không qua lớp bọc đã ngừng bảo trì), cắt ở tầng byte trước khi băm để băm và xác minh luôn nhất quán. Khi email không tồn tại, hệ thống vẫn thực hiện một phép băm giả để thời gian phản hồi không làm lộ tài khoản; bcrypt chạy trong nhóm luồng phụ để không chặn vòng lặp sự kiện.

**Mã thông báo.** Hệ thống dùng JWT ký HS256, gồm mã truy cập hạn 30 phút (định danh, vai trò, loại mã, thời điểm phát hành và hết hạn) và mã làm mới hạn 7 ngày (định danh, loại mã, thời điểm phát hành và hết hạn); thời hạn đọc từ cấu hình. Hàm giải mã kiểm tra trường loại để mã làm mới không dùng thay được mã truy cập, và trả về giá trị rỗng thay vì ném ngoại lệ.

**Lưu mã trong httpOnly cookie.** Hai mã nằm trong cookie `access_token` và `refresh_token` thay vì bộ nhớ cục bộ của trình duyệt, nên mã JavaScript trên trang không đọc được. Thuộc tính cookie được cấu hình qua `COOKIE_SECURE`, `COOKIE_SAMESITE` và `COOKIE_DOMAIN`; ở môi trường triển khai, `SameSite` tự chuyển từ `lax` sang `none` và `Secure` bắt buộc bật, nên cùng một mã nguồn chạy đúng cả trên máy phát triển lẫn khi triển khai khác tên miền.

**Làm mới phiên.** Bốn điểm cuối `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh` và `POST /api/auth/logout` phục vụ vòng đời phiên. Điểm cuối làm mới đọc mã từ cookie, phát lại và luân chuyển cả hai mã. Phía giao diện, lớp bọc gọi mạng gặp lỗi 401 thì tự làm mới rồi chạy lại yêu cầu một lần; nhiều yêu cầu cùng lúc chỉ kích hoạt một lần làm mới.

**Phân quyền.** Vai trò được kiểm tra ở tầng dependency của FastAPI và được đọc lại từ cơ sở dữ liệu ở mỗi kết nối WebSocket, riêng kênh quản trị đọc lại ở mỗi tin nhắn để việc thu hồi quyền có hiệu lực ngay. Mã không hợp lệ thì kết nối bị đóng với mã 4401 và giao diện về trang đăng nhập; cơ sở dữ liệu lỗi khi xác minh thì đóng với mã 1011 để giao diện nối lại thay vì đăng xuất oan. Định danh tài khoản nhân viên không bao giờ được gửi xuống phía khách.

Đặc tả use case đăng ký, đăng nhập và biểu đồ tuần tự của luồng làm mới phiên nằm ở phần Phụ lục (Bảng PL.5, Bảng PL.6 và Hình PL.3).

### Giới hạn tần suất

Dưới đây là bảng tổng hợp các giới hạn tần suất của hệ thống cùng lý do đặt ra từng giới hạn (Bảng 2.21).

Bảng 2.21. Các giới hạn tần suất

| **Đối tượng**              | **Giới hạn mặc định** | **Lý do**                                                                                      |
|----------------------------|-----------------------|------------------------------------------------------------------------------------------------|
| Chat theo khách            | 20 tin / 60 giây      | Mỗi tin tốn 2 lời gọi mô hình + 1 embedding                                                    |
| Đăng nhập theo IP          | 10 lần / 60 giây      | Chống dò mật khẩu                                                                              |
| Đăng nhập theo email       | 5 lần / 60 giây       | Chống dò theo tài khoản cụ thể                                                                 |
| Đăng ký theo IP            | 5 lần / 60 giây       | Chống tạo tài khoản hàng loạt                                                                  |
| Kích thước khung WebSocket | 64 KiB                | Chống khung quá lớn làm nghẽn worker. Đặt ở cờ khởi động uvicorn, không phải trong mã ứng dụng |
| Độ dài tin nhắn            | 2000 ký tự            | Giới hạn đầu vào prompt                                                                        |

### Bốn lớp phòng thủ chống chèn chỉ dẫn (prompt injection)

Hệ thống phải chống hai hướng tấn công: trực tiếp khi khách gõ chỉ dẫn vào tin nhắn, và gián tiếp khi chỉ dẫn được giấu trong tài liệu tri thức tải lên.

**Lớp A: chuẩn hoá tại biên.** Mọi văn bản không tin cậy được chuẩn hoá Unicode dạng NFKC, loại ký tự điều khiển và ký tự vô hình (giữ lại xuống dòng và tab), gộp khoảng trắng và cắt độ dài. Lớp này cố ý không phải bộ phát hiện tấn công: không phát cờ, không đếm và không chặn tin nhắn.

**Lớp B: ranh giới giữa dữ liệu và chỉ dẫn.** Tin nhắn khách và từng đoạn tri thức được bọc trong thẻ dữ liệu riêng, kèm quy tắc rằng nội dung trong thẻ chỉ để đọc; mọi thẻ ranh giới giả mạo trong văn bản không tin cậy bị vô hiệu hoá bằng cách bỏ dấu ngoặc nhọn.

**Lớp C: quy tắc trong prompt hệ thống.** Tác tử thứ nhất và thứ tư có khối quy tắc tường minh: nội dung trong thẻ, kể cả lịch sử hội thoại và dữ liệu đơn, chỉ là dữ liệu; không tiết lộ hay nhắc lại prompt hệ thống; không đổi vai trò theo yêu cầu người dùng; bỏ qua câu ra lệnh nằm trong đoạn tri thức; chỉ thực hiện nhiệm vụ chăm sóc khách hàng.

**Lớp D: làm sạch tài liệu tải lên.** Câu mang tính ra lệnh rõ ràng được thay bằng một dấu vết thay vì xoá âm thầm; bộ mẫu cố ý hẹp và thao tác cắt theo từng câu để không làm mất tri thức hợp lệ.

Dưới đây là sơ đồ tổng hợp bốn lớp phòng thủ cùng hai hướng tấn công mà hệ thống phải đối mặt (Hình 2.16).

Hình 2.16. Bốn lớp phòng thủ chống chèn chỉ dẫn và hai hướng tấn công

Dưới đây là bảng tổng hợp bốn lớp phòng thủ cùng vị trí áp dụng và hướng tấn công mà mỗi lớp hướng tới ngăn chặn (Bảng 2.22).

Bảng 2.22. Tổng hợp bốn lớp phòng thủ

| **Lớp**               | **Vị trí**                       | **Chống hướng tấn công**            |
|-----------------------|----------------------------------|-------------------------------------|
| A — Chuẩn hoá         | Biên WebSocket, biên upload      | Che giấu bằng ký tự lạ/vô hình      |
| B — Ranh giới dữ liệu | Dựng prompt                      | Chỉ dẫn trực tiếp trong tin khách   |
| C — Quy tắc prompt    | Prompt hệ thống Agent 1, Agent 4 | Đổi vai, lộ prompt, chuyển mục đích |
| D — Làm sạch tài liệu | Đường upload                     | Chèn gián tiếp qua tài liệu         |

Bốn lớp trên mới là phần bề mặt; năng lực phòng thủ quyết định nằm ở cấu trúc hệ thống. Kể cả khi mô hình bị thao túng hoàn toàn, tác tử thứ ba vẫn định tuyến trên tập cờ, tra cứu đơn vẫn giới hạn theo khách đang đăng nhập và tác tử thứ tư vẫn không có đường nào để tự chuyển ca, nên kẻ tấn công không giành thêm được đặc quyền nào ở tầng hệ thống.

## Tổng kết chương

Chương 2 đã trình bày toàn bộ thiết kế của hệ thống trên nền bốn trụ cột: luồng xử lý cố định để bảo đảm tính dự đoán và khả năng kiểm toán, tự trị có giới hạn ở tầng tác tử, an toàn trước các tình huống ngoài dự kiến, và cải thiện dần dưới sự phê duyệt của con người.

Chương đã đặc tả bốn tác tử cùng cấu trúc trạng thái điều phối dùng chung, với ba quyết định thiết kế chi phối phần còn lại của hệ thống: tác tử ra quyết định hoạt động hoàn toàn tất định và định tuyến trên tập cờ thay vì gộp hai thang độ tin cậy; mọi tin nhắn gửi tới khách hàng phát ra từ một điểm duy nhất; và cổng cấu hình của con người không có đường nào ghi đè lên logic an toàn. Bên cạnh đó là thiết kế kho tri thức trong repository với kỹ thuật mở rộng truy vấn và cơ chế nạp lại không gián đoạn, các biểu đồ tuần tự cho năm luồng nghiệp vụ chính, cơ sở dữ liệu tám bảng và thiết kế bảo mật với bốn lớp phòng thủ chống chèn chỉ dẫn.

Chương 3 sẽ trình bày quá trình hiện thực hoá các thiết kế này, các thách thức kỹ thuật thực tế cùng giải pháp tương ứng, giao diện người dùng và kết quả đo đạc trên hệ thống chạy thật.
