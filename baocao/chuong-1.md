> **Tệp bàn giao cho Claude Word — bản rút gọn ngày 17/09/2026.** Toàn báo cáo đã được rút gọn còn khoảng
> 32.000 từ, tính cả chữ trong bảng. Nội dung đã lược bỏ (bản gốc đầy đủ) và khối ghi chú bàn giao trước
> đây nằm ở `baocao/doc.md`.
>
> - Số hiệu mục, hình và bảng giữ nguyên: 21 hình (Hình 1.1 – 1.21), 5 bảng (Bảng 1.1 – 1.5). Đã bỏ mục 1.5.6.
> - Trích dẫn [1]–[4] đã gắn vào mục 1.3; hình còn phải chuẩn bị gồm 4 ảnh chụp khảo sát (1.1 – 1.4),
>   5 sơ đồ khái niệm (1.5 – 1.9) và 12 logo (1.10 – 1.21), yêu cầu chi tiết xem `doc.md`.

---

# TỔNG QUAN ĐỀ TÀI

## Tổng quan đề tài

### Nhu cầu tự động hoá chăm sóc khách hàng trong thương mại điện tử

Chăm sóc khách hàng (CSKH) là khâu tiếp xúc thường xuyên nhất giữa cửa hàng trực tuyến và người mua. Ở các cửa hàng thời trang, khâu này bộc lộ ba điểm nghẽn khi vận hành thủ công. Thứ nhất, phần lớn câu hỏi lặp lại quanh một số chủ đề hữu hạn như giá, kích cỡ, vận chuyển, trạng thái đơn hàng và đổi trả, vốn đã có sẵn câu trả lời trong tài liệu chính sách. Thứ hai, thời gian phản hồi ảnh hưởng trực tiếp tới tỉ lệ chốt đơn, trong khi tin nhắn dồn vào buổi tối và cuối tuần, ngoài giờ làm việc của nhân viên. Thứ ba, chất lượng trả lời không đồng nhất giữa các nhân viên và khó truy vết khi có khiếu nại.

Ba vấn đề này có chung hướng giải quyết là để hệ thống tự động xử lý phần việc lặp lại theo một nguồn tri thức thống nhất, dành con người cho những tình huống cần phán đoán. Xác định đúng ranh giới giữa hai phần việc đó là bài toán kỹ thuật trung tâm của đề tài.

### Khảo sát các giải pháp hiện có

Các giải pháp tự động hoá chăm sóc khách hàng hiện có có thể chia thành bốn nhóm tiêu biểu.

**a) Chatbot theo kịch bản.** Khách chọn các nút bấm theo một cây quyết định dựng sẵn. Luồng xử lý dự đoán được, chi phí thấp và nội dung không sai lệch vì do con người soạn trước; nhưng hệ thống không hiểu ngôn ngữ tự do, cây kịch bản phình rất nhanh theo số tình huống và trải nghiệm cứng nhắc khiến khách thường đòi gặp nhân viên ngay (Hình 1.1).

Hình 1.1. Giao diện chatbot theo kịch bản trên nền tảng nhắn tin

**b) Chatbot NLU truyền thống (Dialogflow, Rasa và các nền tảng tương tự).** Mô hình phân loại ý định được huấn luyện trên tập câu mẫu, kết hợp trích xuất thực thể và điền khe. Hệ thống hiểu được diễn đạt tự do ở mức khá, nhưng phải gán nhãn thủ công nhiều câu mẫu và huấn luyện lại mỗi khi nghiệp vụ thay đổi, một rào cản lớn với cửa hàng nhỏ (Hình 1.2).

Hình 1.2. Giao diện huấn luyện ý định của một nền tảng NLU truyền thống

**c) Trợ lý dựa trên mô hình ngôn ngữ lớn, có hoặc không kèm truy hồi một bước.** Nhóm này triển khai nhanh, hiểu ngôn ngữ tốt và trả lời trôi chảy, nhưng rủi ro nhất: khi tri thức truy hồi yếu, mô hình vẫn có thể bịa ra chính sách, mã giảm giá hay cam kết những hành động hệ thống không làm được, và kiến trúc một bước không có điểm nào để từ chối trả lời có cấu trúc hay chuyển yêu cầu cho con người (Hình 1.3).

Hình 1.3. Trợ lý dựa trên mô hình ngôn ngữ lớn kết hợp truy hồi một bước

**d) Hệ đa tác tử có tác tử điều phối trung tâm (Supervisor).** Tác tử điều phối tự quyết định tại thời điểm chạy sẽ gọi tác tử nào, theo thứ tự nào và lặp bao nhiêu vòng. Kiến trúc linh hoạt tối đa nhưng mất tính dự đoán: cùng một câu hỏi có thể đi hai đường khác nhau, số lời gọi mô hình không có trần, và rất khó truy nguyên khi hệ thống hành xử sai (Hình 1.4).

Hình 1.4. Kiến trúc điều phối động có tác tử Supervisor

Dưới đây là bảng so sánh bốn nhóm giải pháp với hệ thống đề xuất theo bảy tiêu chí (Bảng 1.1).

Bảng 1.1. So sánh các nhóm giải pháp tự động hoá CSKH

| **Tiêu chí**                              | **Kịch bản** | **NLU truyền thống** | **LLM/RAG một bước** | **Đa tác tử có Supervisor** | **Hệ thống đề xuất**                                  |
|-------------------------------------------|--------------|----------------------|----------------------|-----------------------------|-------------------------------------------------------|
| Hiểu ngôn ngữ tự do                       | Không        | Trung bình           | Tốt                  | Tốt                         | Tốt                                                   |
| Dự đoán được luồng chạy                   | Cao          | Cao                  | Trung bình           | Thấp                        | Cao                                                   |
| Khả năng kiểm toán                        | Cao          | Trung bình           | Thấp                 | Thấp                        | Cao                                                   |
| Chống trả lời sai chính sách              | Cao          | Cao                  | Thấp                 | Thấp                        | Cao                                                   |
| Cơ chế chuyển người có cấu trúc           | Thô sơ       | Thô sơ               | Không có             | Không tất định              | Có, tất định                                          |
| Chi phí/độ trễ một lượt                   | Rất thấp     | Thấp                 | Thấp                 | Không có trần               | Có trần cứng (≤ 2 lời gọi LLM + 1 embedding mỗi lượt) |
| Công sức soạn và bảo trì nội dung trả lời | Rất cao      | Cao                  | Thấp                 | Thấp                        | Thấp                                                  |

Như vậy, chưa có nhóm giải pháp nào vừa hiểu được ngôn ngữ tự nhiên, vừa giữ được tính dự đoán và khả năng kiểm toán cho một hệ thống đối thoại trực tiếp với khách hàng. Đề tài nhắm vào đúng khoảng trống này: giữ năng lực ngôn ngữ của mô hình ở tầng tác tử nhưng rút quyền tự trị khỏi tầng điều phối (Hình 1.5).

Hình 1.5. Bản đồ định vị các nhóm giải pháp tự động hoá CSKH và khoảng trống của đề tài

## Bài toán đặt ra và phạm vi đề tài

### Bài toán đặt ra

Bài toán đặt ra là xây dựng một hệ thống chăm sóc khách hàng cho cửa hàng thời trang trực tuyến, trong đó nhiều tác tử AI chuyên biệt phối hợp trong một pipeline cố định để tiếp nhận, hiểu, tra cứu tri thức và trả lời khách; con người chỉ can thiệp ở các ca quan trọng hoặc khi hệ thống không đủ căn cứ. Bài toán được cụ thể hoá thành sáu mục tiêu:

- **M1.** Phân loại ý định và trích xuất thực thể từ tin nhắn tiếng Việt tự do.

- **M2.** Truy hồi tri thức từ tài liệu chính sách, câu hỏi thường gặp và thông tin sản phẩm để câu trả lời luôn có căn cứ.

- **M3.** Đánh giá rủi ro và quyết định trả lời tự động hay chuyển cho nhân viên theo một chính sách tất định, kiểm toán được.

- **M4.** Sinh phản hồi cuối cùng cho khách sau cổng kiểm soát của quản trị viên.

- **M5.** Cung cấp dashboard giám sát thời gian thực, hàng đợi chuyển tiếp và công cụ duyệt nháp.

- **M6.** Bảo đảm tính kiểm soát: nhật ký kiểm toán, người trong vòng lặp, cổng cấu hình và quản lý tri thức.

Chỉ tiêu nghiệp vụ là tự động xử lý từ 70% số lượt hội thoại trở lên với thời gian phản hồi dưới 5 giây. Nguyên tắc xuyên suốt là khi không đủ chắc chắn thì chuyển cho nhân viên: một hệ thống trả lời mọi câu nhưng sai chính sách ở 5% số lượt gây thiệt hại lớn hơn nhiều so với một hệ thống chỉ trả lời 80% số lượt và chuyển phần còn lại.

### Đối tượng sử dụng

Hệ thống phục vụ hai nhóm người dùng trên cùng một ứng dụng web:

- **Khách hàng:** truy cập cổng chat, đăng nhập để tra cứu đơn hàng của chính mình và xem lại lịch sử hội thoại; cần được trả lời nhanh, chính xác và được chuyển tới nhân viên thật khi hệ thống không trả lời được.

- **Quản trị viên (nhân viên chăm sóc khách hàng):** bắt buộc đăng nhập; tiếp nhận các ca chuyển tiếp, duyệt nháp phản hồi, trao đổi trực tiếp với khách, quản lý kho tri thức, cấu hình cổng tự động và xem báo cáo, kể cả trên điện thoại qua ứng dụng web tiến bộ (PWA).

### Phạm vi và giới hạn hệ thống

**Phạm vi hệ thống:**

- Chat văn bản trên web theo thời gian thực qua WebSocket.

- Pipeline bốn tác tử chạy theo thứ tự cố định, không có tác tử điều phối trung tâm.

- Kho tri thức Markdown trong repository nạp vào cơ sở dữ liệu vector, kèm chức năng tải tài liệu bổ sung qua giao diện.

- Tra cứu trạng thái đơn hàng mô phỏng trong phạm vi tài khoản đang đăng nhập.

- Hàng đợi chuyển tiếp kèm phiếu ngữ cảnh, tiếp quản ca, duyệt nháp và cổng cấu hình theo ý định.

- Xác thực JWT, phân quyền theo vai trò và bốn lớp chống chèn chỉ dẫn.

- Nhật ký kiểm toán, tab báo cáo, tự nhắc và tự đóng hội thoại khi khách không hoạt động.

**Giới hạn của hệ thống:**

- Chưa có bộ nhớ xuyên hội thoại, hồ sơ khách hàng và gợi ý sản phẩm.

- Không thực hiện thao tác làm thay đổi đơn hàng như huỷ đơn, hoàn tiền hay đổi đơn.

- Chưa tích hợp kênh thoại, hình ảnh hay mạng xã hội; vòng học bán tự động mới được dự trù trong thiết kế.

- Không vận hành theo mô hình đa tác tử tự trị hoàn toàn — đây là lựa chọn có chủ đích để đổi lấy độ tin cậy và khả năng kiểm toán, không phải giới hạn kỹ thuật.

## Cơ sở lý thuyết liên quan

### Mô hình ngôn ngữ lớn và ứng dụng trong CSKH

Mô hình ngôn ngữ lớn (Large Language Model - LLM) là mạng nơ-ron theo kiến trúc Transformer [1], được huấn luyện trên khối văn bản rất lớn để dự đoán token tiếp theo, nhờ đó thực hiện được nhiều tác vụ ngôn ngữ chỉ bằng cách mô tả tác vụ trong prompt mà không cần huấn luyện lại. Đề tài khai thác hai đặc tính của LLM. Thứ nhất là khả năng phân loại zero-shot và few-shot: bộ phân loại ý định được mô tả bằng danh sách nhãn kèm ví dụ ngay trong prompt, loại bỏ nhu cầu gán nhãn và huấn luyện lại. Thứ hai là khả năng sinh văn bản có ràng buộc nguồn, tức chỉ diễn đạt lại thông tin từ các đoạn được cấp. Đặc tính thứ hai chỉ là xu hướng hành vi chứ không phải bảo đảm kỹ thuật, nên Chương 2 thiết kế thêm các cơ chế cưỡng chế bám nguồn. Tác vụ phân loại dùng chế độ trả về JSON có ràng buộc với nhiệt độ bằng 0 để kết quả ổn định giữa các lần chạy.

### Sinh có tăng cường truy hồi (RAG)

Sinh có tăng cường truy hồi (Retrieval-Augmented Generation - RAG) ghép một bước truy hồi thông tin vào trước bước sinh văn bản [2]: hệ thống tìm các đoạn tài liệu liên quan nhất với câu hỏi rồi đưa vào prompt làm căn cứ cho câu trả lời. Quy trình gồm hai pha. Ở pha nạp, tài liệu được chia thành đoạn, chuyển thành vector bằng mô hình embedding và lưu vào cơ sở dữ liệu vector kèm siêu dữ liệu. Ở pha truy hồi, câu hỏi cũng được vector hoá để tìm k đoạn gần nhất theo độ đo cosine (Hình 1.6).

Hình 1.6. Hai pha của kỹ thuật sinh có tăng cường truy hồi

Khi áp dụng vào chăm sóc khách hàng, RAG đặt ra ba vấn đề. Chia đoạn theo số ký tự cố định phá vỡ cấu trúc nội dung như bảng kích cỡ hay các bước quy trình, nên đề tài chia theo từng mục của tài liệu Markdown. Giọng nói thường ngày của khách khác xa giọng văn trang trọng của tài liệu chính sách, nên vector của hai cách diễn đạt có thể cách xa nhau dù cùng một nội dung. Cuối cùng, ngưỡng phân biệt tri thức đủ liên quan phải được đo trên chính kho tri thức thật chứ không chọn theo cảm tính.

### Kiến trúc đa tác tử và LangGraph

Kiến trúc đa tác tử (multi-agent) chia một tác vụ phức tạp thành nhiều tác tử chuyên biệt trao đổi qua một trạng thái dùng chung, cho phép tối ưu, kiểm thử và quan sát từng bước độc lập. Có hai trường phái điều phối. Ở điều phối động, một tác tử trung tâm (Supervisor) quyết định luồng chạy ngay tại thời điểm vận hành. Ở điều phối tĩnh, thứ tự xử lý được định nghĩa trước dưới dạng đồ thị, các điểm rẽ nhánh nằm trong mã tất định, còn tác tử chỉ quyết định nội dung xử lý chứ không quyết định luồng đi (Hình 1.7).

Hình 1.7. So sánh điều phối động có Supervisor và điều phối tĩnh theo pipeline cố định

Đề tài chọn điều phối tĩnh, chấp nhận hy sinh tính linh hoạt ở tầng điều phối để đổi lấy độ tin cậy, khả năng kiểm toán và một trần chi phí xác định cho mỗi lượt. Công cụ hiện thực là LangGraph, thư viện xây dựng ứng dụng mô hình ngôn ngữ dưới dạng đồ thị có trạng thái [4], với năm khái niệm nền tảng: trạng thái (State) kiểu TypedDict chứa toàn bộ thông tin của một lượt; nút (Node) là hàm nhận trạng thái và trả về phần cần cập nhật; cạnh (Edge) định nghĩa thứ tự chạy; hàm gộp (Reducer) quy định cách gộp khi nhiều nút ghi cùng một trường, trong đó đề tài dùng hàm gộp cộng dồn cho cờ bất định và nhật ký trace để quy mỗi cờ về đúng tác tử; và cơ chế lưu điểm kiểm tra (Checkpointer) để dừng rồi chạy tiếp đồ thị.

### Grounding và vấn đề ảo giác

Ảo giác (hallucination) là hiện tượng mô hình sinh ra thông tin không có căn cứ trong nguồn được cấp, với độ trôi chảy và tự tin không khác gì thông tin đúng [3]; bám nguồn (grounding) là các kỹ thuật buộc câu trả lời phải dựa trên nguồn đã được kiểm soát. Qua quan sát hành vi thực tế của hệ thống, đề tài phân biệt ba dạng ảo giác, mỗi dạng cần một cơ chế phòng chống riêng (Hình 1.8).

Hình 1.8. Ba dạng ảo giác trong ngữ cảnh chăm sóc khách hàng và cơ chế chống tương ứng

**a) Bịa ra thông tin không tồn tại.** Mô hình đưa ra một chính sách, con số hay mã giảm giá không có thật. Cơ chế chống là chỉ cấp nguồn đã kiểm soát và cấm dùng tri thức ngoài nguồn.

**b) Suy diễn phủ định từ chỗ nguồn im lặng.** Tài liệu không nhắc tới giao hàng quốc tế, mô hình lại khẳng định cửa hàng không giao hàng đi nước ngoài — về logic, đây cũng là bịa ra một chính sách. Cơ chế chống là quy tắc tường minh phân biệt "chưa có thông tin" với "không tồn tại", kết hợp quy tắc coi mọi danh sách trong nguồn là danh sách mở trừ khi nguồn dùng từ "chỉ" hoặc "duy nhất".

**c) Bịa ra hành động.** Mô hình khẳng định đã hoàn tiền hay đang kết nối nhân viên, dạng nguy hiểm nhất vì tạo cam kết giả với khách. Cơ chế chống là giới hạn hành động trong prompt, kết hợp một bất biến kiến trúc: tác tử sinh phản hồi không có quyền chuyển ca, nên mọi lời hứa chuyển tiếp do nó tự đưa ra đều bị cấm.

Ngoài ra, khi không truy hồi được nguồn nào, hệ thống không gọi mô hình sinh phản hồi, nên không thể phát sinh nội dung bịa đặt.

### Human-in-the-loop và nguyên tắc tự trị có giới hạn

Có người trong vòng lặp (Human-in-the-loop - HITL) là mô hình vận hành trong đó hệ thống tự động xử lý phần lớn công việc nhưng dành các điểm quyết định quan trọng cho con người. Đề tài hiện thực mô hình này bằng một thang phản hồi ba mức: **gửi thẳng** khi hệ thống đủ tự tin, có căn cứ và ý định được phép trả lời tự động; **duyệt nháp** khi hệ thống đủ tự tin nhưng ý định thuộc nhóm nhạy cảm như hoàn tiền, đổi hàng, khiếu nại, và câu trả lời chỉ được gửi sau khi quản trị viên duyệt; **chuyển cho nhân viên** khi hệ thống gặp giới hạn như không có tri thức, câu hỏi ngoài phạm vi hoặc khách yêu cầu gặp người thật (Hình 1.9).

Hình 1.9. Thang phản hồi phân cấp ba mức và ranh giới giữa an toàn với cấu hình

Mức thứ ba do cơ chế an toàn quyết định và không bao giờ bị cấu hình ghi đè; cổng cấu hình chỉ can thiệp vào ranh giới giữa mức thứ nhất và mức thứ hai.

## Tổng quan yêu cầu hệ thống

### Yêu cầu chức năng

Dưới đây là bảng yêu cầu chức năng của hệ thống, gom theo bảy nhóm (Bảng 1.2).

Bảng 1.2. Yêu cầu chức năng của hệ thống

| **Mã**     | **Nhóm**    | **Mô tả**                                                                 |
|------------|-------------|---------------------------------------------------------------------------|
| FR-PIPE-1  | Pipeline    | Mỗi hội thoại có state độc lập, nhiều hội thoại xử lý song song           |
| FR-PIPE-2  | Pipeline    | Thứ tự tác tử cố định intent → knowledge → decision → response            |
| FR-PIPE-3  | Pipeline    | Tác tử ghi độ tin cậy và cờ bất định; định tuyến dựa trên cờ              |
| FR-PIPE-4  | Pipeline    | Mọi bước tác tử được ghi nhật ký kiểm toán                                |
| FR-PIPE-5  | Pipeline    | Phản hồi tự động phải có căn cứ; thiếu căn cứ thì chuyển người            |
| FR-RAG-1   | Tri thức    | Nạp tài liệu → chia đoạn → embedding → vector database                    |
| FR-RAG-2   | Tri thức    | Truy hồi theo ý định, trả về các đoạn kèm điểm                            |
| FR-RAG-3   | Tri thức    | Nạp lại, quản lý siêu dữ liệu, xoá tài liệu                               |
| FR-GATE-1  | Cổng        | Cổng lưu trong CSDL, đặt được theo từng ý định                            |
| FR-GATE-2  | Cổng        | Cổng chỉ can thiệp ca auto_reply, không tác động ca chuyển người          |
| FR-GATE-3  | Cổng        | Mặc định bật tự trả lời, tắt cho nhóm nhạy cảm                            |
| FR-ESC-1   | HITL        | Mọi ca chuyển người kèm EscalationCard                                    |
| FR-ESC-4   | HITL        | Nhận ca, chat trực tiếp, đóng ca; duyệt hoặc sửa nháp                     |
| FR-ESC-5   | HITL        | Mọi hành động của quản trị viên được ghi nhật ký                          |
| FR-ASYNC-1 | Bất đồng bộ | Pipeline chạy đồng bộ theo tin nhắn, P95 ≤ 5 giây                         |
| FR-ASYNC-2 | Bất đồng bộ | Thiếu thông tin thì hỏi lại tối đa một lần                                |
| FR-ASYNC-3 | Bất đồng bộ | Chuyển người thì tạm dừng AI cho hội thoại đó                             |
| FR-ASYNC-4 | Bất đồng bộ | Ngoài giờ hỗ trợ: giữ ca trong hàng đợi, không tự đóng                    |
| FR-ASYNC-7 | Bất đồng bộ | Realtime bằng WebSocket, không polling                                    |
| FR-ADMIN-  | Quản trị    | Hội thoại và bộ lọc, chat, hàng đợi, duyệt nháp, tri thức, cổng, báo cáo  |
| FR-CUST-   | Khách hàng  | Tạo hội thoại, nhận phản hồi thời gian thực, xem lịch sử                  |

### Yêu cầu phi chức năng

Dưới đây là bảng tổng hợp các yêu cầu phi chức năng cùng chỉ tiêu tương ứng của từng yêu cầu (Bảng 1.3).

Bảng 1.3. Yêu cầu phi chức năng

| **Mã** | **Yêu cầu**                | **Chỉ tiêu**                                                                  |
|--------|----------------------------|-------------------------------------------------------------------------------|
| NFR-1  | Thời gian phản hồi tự động | P95 ≤ 5 giây                                                                  |
| NFR-2  | Đồng thời                  | ≥ 100 người dùng; một ca chuyển người không nghẽn ca khác                     |
| NFR-3  | Khả dụng                   | Uptime ≥ 99%                                                                  |
| NFR-4  | Kiểm toán                  | 100% hành động tác tử và quyết định quản trị viên được ghi log, truy vết được |
| NFR-5  | Bảo mật                    | JWT, phân quyền theo vai trò, HTTPS/WSS                                       |
| NFR-6  | An toàn dữ liệu            | Dữ liệu demo là dữ liệu mô phỏng; có phương án chạy nội bộ                    |
| NFR-7  | Chống lạm dụng             | Chống chèn chỉ dẫn từ tin nhắn khách và tài liệu tri thức                     |
| NFR-8  | Quan sát                   | Giám sát chi phí token, độ trễ, tỉ lệ lỗi                                     |
| NFR-9  | Chi phí                    | Ưu tiên dịch vụ managed gói miễn phí                                          |
| NFR-10 | Cấu hình                   | Ngưỡng, cổng, mốc thời gian, cửa sổ ngữ cảnh đều cấu hình được                |
| NFR-11 | An toàn nội dung           | Phản hồi phải có căn cứ; cấm trả lời sai chính sách                           |

### Các chỉ số đánh giá (KPI)

Dưới đây là các chỉ số đánh giá cùng mục tiêu; kết quả đo đối chiếu được trình bày ở mục 3.5.7 (Bảng 1.4).

Bảng 1.4. Chỉ số đánh giá hệ thống

| **Chỉ số**                                                   | **Mục tiêu** |
|--------------------------------------------------------------|--------------|
| Tỉ lệ tự trả lời (Auto Reply Rate)                           | ≥ 70%        |
| Thời gian phản hồi trung bình                                | \< 5 giây    |
| Tỉ lệ chuyển người (Escalation Rate)                         | \< 30%       |
| Tỉ lệ escalate oan (câu trả lời được nhưng vẫn chuyển người) | ≤ 5%         |
| Tỉ lệ phản hồi dự phòng oan (FALLBACK)                       | → 0%         |

## Công nghệ và các công cụ sử dụng

Bộ công nghệ được chọn theo ba ràng buộc đã nêu ở mục 1.4: độ trễ P95 dưới 5 giây (NFR-1), chi phí nằm trong gói miễn phí của dịch vụ managed (NFR-9) và mọi tham số cấu hình được qua biến môi trường (NFR-10), với nguyên tắc ưu tiên công cụ có sẵn cơ chế cần dùng thay vì tự xây dựng.

### Backend

- **Python 3.12 và FastAPI 0.115** [8] (Hình 1.10): phần lớn thư viện điều phối tác tử và bộ thư viện khách của các nhà cung cấp mô hình ưu tiên Python; FastAPI là framework bất đồng bộ, hỗ trợ WebSocket ngay trong lõi và xác thực dữ liệu tại biên bằng Pydantic. Vì một lượt xử lý chủ yếu là chờ nhập xuất (gọi mô hình, tạo embedding, truy vấn Qdrant và PostgreSQL), hàng trăm hội thoại chạy xen kẽ được trên một tiến trình.

Hình 1.10. Logo Python và FastAPI

- **LangGraph 0.2** [4] (Hình 1.11): cho phép định nghĩa đồ thị tĩnh với các cạnh cố định, đúng lựa chọn ở mục 1.3.3, và cung cấp sẵn cơ chế gộp trạng thái.

Hình 1.11. Logo LangGraph

- **SQLAlchemy 2.0 và Alembic 1.13** [9] (Hình 1.12): truy cập PostgreSQL bất đồng bộ qua `asyncpg` với ranh giới giao dịch tường minh; Alembic phiên bản hoá lược đồ bằng các tệp migration.

Hình 1.12. Logo SQLAlchemy và Alembic

- **Pydantic 2.9 và pydantic-settings 2.5** (Hình 1.13): xác thực schema và đọc cấu hình từ biến môi trường ngay khi khởi động, hiện thực NFR-10 — không viết cứng khoá bí mật, địa chỉ dịch vụ hay ngưỡng số trong mã nguồn.

Hình 1.13. Logo Pydantic

- **Công cụ bổ sung:** uv quản lý gói Python; bcrypt (từ phiên bản 4.1) băm mật khẩu; PyJWT 2.9 xử lý mã thông báo; python-frontmatter, pypdf và python-docx đọc tài liệu tri thức.

### Mô hình ngôn ngữ và embedding

Hệ thống dùng hai mô hình của OpenAI qua bộ thư viện khách chính thức phiên bản 1.40 (Hình 1.14): `gpt-4o-mini` cho hai lời gọi mỗi lượt, gồm phân loại ý định với chế độ trả về JSON có cấu trúc [6] và sinh phản hồi; `text-embedding-3-small` sinh vector 1536 chiều cho đoạn tri thức và câu hỏi [5]. Mô hình cỡ nhỏ là đủ vì phần khó đã được chuyển sang kiến trúc: bảng phân loại nằm sẵn trong prompt, tri thức được truy hồi sẵn và quyết định an toàn do mã tất định đảm nhiệm. Thời gian chờ và số lần thử lại được đặt tường minh qua biến môi trường (mục 3.5.5).

Hình 1.14. Logo OpenAI

### Lưu trữ và hạ tầng

- **PostgreSQL trên Neon** (Hình 1.15): lưu toàn bộ dữ liệu nghiệp vụ và nhật ký kiểm toán; được chọn vì giao dịch ACID (ghi trạng thái, tin nhắn và phiếu chuyển tiếp cùng lúc), kiểu JSONB và câu lệnh cập nhật có điều kiện làm nền cho cơ chế so sánh rồi ghi.

Hình 1.15. Logo PostgreSQL và Neon

- **Qdrant Cloud** [7] (Hình 1.16): cơ sở dữ liệu vector tìm theo độ đo cosine, lọc theo payload ngay trong truy vấn và hỗ trợ alias cho collection để nạp lại kho tri thức không gián đoạn (mục 2.6.4).

Hình 1.16. Logo Qdrant

- **Langfuse** [14] (Hình 1.17): trace từng lời gọi mô hình kèm số token và chi phí; tích hợp tuỳ chọn, không cấu hình thì tự vô hiệu.

Hình 1.17. Logo Langfuse

Dưới đây là bảng tổng hợp hạ tầng; cả ba dịch vụ đều dùng gói miễn phí, phù hợp ràng buộc NFR-9 (Bảng 1.5).

Bảng 1.5. Hạ tầng sử dụng

| **Thành phần** | **Công nghệ** | **Vai trò** |
|----------------|---------------|-------------|
| CSDL quan hệ | PostgreSQL (Neon, managed) | Hội thoại, tin nhắn, đơn hàng, tài khoản, cấu hình cổng, nhật ký kiểm toán |
| Vector database | Qdrant Cloud (độ đo cosine) | Lưu embedding các đoạn tri thức |
| Quan sát LLM | Langfuse | Trace lời gọi mô hình, token, chi phí; không cấu hình thì tự vô hiệu |

### Frontend

- **TypeScript, React 18 và Next.js 14 (App Router)** [10] (Hình 1.18): một ứng dụng duy nhất phục vụ cổng chat khách hàng (`/chat`) và bảng điều khiển quản trị (`/admin`), dùng chung giao thức, tập trạng thái và thành phần hiển thị; cài được lên điện thoại dưới dạng PWA thay cho ứng dụng di động riêng.

Hình 1.18. Logo Next.js và React

- **Tailwind CSS** (Hình 1.19): dùng ở dạng thuần, không kèm thư viện thành phần, vì giao diện có nhiều trạng thái hiển thị đặc thù.

Hình 1.19. Logo Tailwind CSS

- **TanStack Query** (Hình 1.20): quản lý bộ đệm dữ liệu phía máy chủ, làm mới theo sự kiện WebSocket thay vì hỏi vòng định kỳ.

Hình 1.20. Logo TanStack Query

### Tổ chức mã nguồn và kiểm thử

- **pnpm workspaces** (Hình 1.21): monorepo gồm `apps/backend`, `apps/dashboard` và `packages/shared-types`, để tập trạng thái hội thoại chỉ có một nguồn khai báo duy nhất.

Hình 1.21. Logo pnpm

- **Kiểm thử và tự động hoá:** pytest cho back-end (chạy ngoại tuyến, không cần khoá API) và trình kiểm thử tích hợp của Node.js cho giao diện; Makefile gói các thao tác thường dùng; Git và GitHub theo mô hình nhánh tính năng.

## Tổng kết chương

Chương 1 đã khảo sát bài toán chăm sóc khách hàng của cửa hàng thời trang trực tuyến và bốn nhóm giải pháp tự động hoá hiện có, từ đó xác định khoảng trống mà đề tài nhắm tới: chưa có giải pháp nào vừa hiểu ngôn ngữ tự nhiên, vừa giữ được tính dự đoán và khả năng kiểm toán. Chương cũng trình bày cơ sở lý thuyết về LLM, RAG, kiến trúc đa tác tử và ba dạng ảo giác, cùng mục tiêu, phạm vi, yêu cầu, chỉ số đánh giá và bộ công nghệ của hệ thống. Trên nền tảng đó, Chương 2 trình bày phân tích và thiết kế chi tiết.
