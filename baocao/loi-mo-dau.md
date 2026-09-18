> **Tệp bàn giao cho Claude Word — PHẦN ĐẦU BÁO CÁO.** Nội dung dưới đây đã đối chiếu với mã nguồn tại
> nhánh `main`, commit `b01b145` ("chore(infra): gỡ Redis khỏi dự án"), ngày 15/09/2026. Đây là **tệp MỚI**,
> bổ sung sau khi đối chiếu phần đầu của báo cáo mẫu CT060102 — gồm LỜI CAM ĐOAN, DANH MỤC TỪ VIẾT TẮT,
> DANH MỤC HÌNH VẼ, DANH MỤC BẢNG, LỜI CẢM ƠN và LỜI MỞ ĐẦU — trong khi bộ năm tệp bàn giao cũ chỉ có thân bài.

## ĐÃ BỔ SUNG (so sánh với báo cáo mẫu CT060102)

| # | Vị trí | Nội dung thêm |
|---|---|---|
| 1 | **LỜI MỞ ĐẦU** (trước Chương 1) | Mẫu có mục này và dành cho nó bốn đoạn: bối cảnh, khoảng trống của các giải pháp hiện có, lý do chọn đề tài kèm mục tiêu, và danh sách các chương. Bộ bàn giao cũ **không có** mục này. Nội dung đã soạn đầy đủ dưới đây theo đúng khuôn bốn đoạn của mẫu |
| 2 | **DANH MỤC TỪ VIẾT TẮT** (đặt sau LỜI CAM ĐOAN và trước DANH MỤC HÌNH VẼ, đúng vị trí mẫu dùng) | Báo cáo mẫu CT060102 **có** mục này, dưới dạng bảng ba cột "Ký hiệu viết tắt / Từ đầy đủ / Ý nghĩa"; bộ bàn giao cũ **không có**. Mục này càng cần thiết vì báo cáo dùng rất nhiều viết tắt chuyên ngành (RAG, LLM, HITL, CAS, JWT, RBAC, JSONB, NFR, FR…), nhiều viết tắt xuất hiện lần đầu ở Chương 2 hoặc Chương 3 mà không được giải nghĩa lại, nên một danh mục tra cứu ở đầu báo cáo giúp hội đồng đọc thuận hơn |

## VIỆC CẦN KIỂM TRA TRONG BẢN .docx

- Bản .docx đã có **LỜI CAM ĐOAN**, **LỜI CẢM ƠN** và **LỜI MỞ ĐẦU** chưa. Cả ba mục này đều
  có trong mẫu CT060102; LỜI MỞ ĐẦU đã soạn ở tệp này, còn LỜI CAM ĐOAN và LỜI CẢM ƠN phải do
  người viết tự đặt bút.
- **DANH MỤC TỪ VIẾT TẮT** đã có trong bản .docx chưa, và có đặt ngay sau LỜI CAM ĐOAN, trước
  DANH MỤC HÌNH VẼ như mẫu CT060102 không.
- **DANH MỤC HÌNH VẼ** đã cập nhật thành **51 dòng** chưa (21 hình Chương 1 + 16 hình Chương 2
  + 14 hình Chương 3).
- **DANH MỤC BẢNG** đã cập nhật thành **48 dòng** chưa (5 bảng Chương 1 + 22 bảng Chương 2
  + 21 bảng Chương 3).
- Hình và bảng của **Phụ lục** đánh theo hệ riêng **PL.x** (Hình PL.1 – PL.6, Bảng PL.1 – PL.9)
  và **KHÔNG** liệt kê vào hai danh mục nói trên.

---

# LỜI MỞ ĐẦU

Thương mại điện tử Việt Nam những năm gần đây tăng trưởng nhanh, và bán lẻ thời trang trực tuyến là một trong những ngành hàng sôi động nhất: phần lớn giao dịch bắt đầu từ một cuộc hội thoại trên trang bán hàng hoặc mạng xã hội chứ không phải từ một lần bấm mua im lặng. Vì vậy chăm sóc khách hàng trở thành khâu tiếp xúc thường xuyên nhất giữa cửa hàng và người mua, nhưng ở phần lớn cửa hàng vừa và nhỏ, khâu này vẫn đang vận hành hoàn toàn thủ công. Cách làm thủ công bộc lộ ba điểm nghẽn. Thứ nhất, phần lớn câu hỏi lặp lại quanh một số chủ đề hữu hạn — giá, bảng size, phí và thời gian vận chuyển, điều kiện đổi trả, tình trạng đơn hàng — nên nhân viên phải soạn lại cùng một câu trả lời nhiều lần mỗi ngày. Thứ hai, thời gian phản hồi ảnh hưởng trực tiếp tới tỉ lệ chốt đơn: khách hỏi khi đang cân nhắc, và một câu trả lời đến muộn thường đồng nghĩa với một đơn đã mất. Thứ ba, chất lượng trả lời không đồng nhất giữa các nhân viên và giữa các thời điểm, đồng thời không truy vết được — khi phát sinh tranh chấp về điều kiện đổi trả hay về cam kết thời gian giao hàng, cửa hàng không có cách nào tái hiện lại hệ thống đã nói gì với khách và dựa trên căn cứ nào.

Thị trường hiện có nhiều giải pháp tự động hoá cho khâu này, nhưng mỗi nhóm đều vướng một hạn chế khiến chúng chưa phù hợp với bài toán vừa nêu. Chatbot theo kịch bản chỉ khớp được những mẫu câu định trước nên không hiểu ngôn ngữ tự do, trong khi khách hàng thật hỏi bằng câu nói thường ngày, viết sai chính tả, viết tắt và gộp nhiều ý trong một tin nhắn. Các nền tảng hiểu ngôn ngữ tự nhiên truyền thống xử lý được ngôn ngữ tự do hơn, nhưng đòi hỏi gán nhãn dữ liệu và huấn luyện lại mỗi khi thêm một ý định hoặc thay đổi chính sách bán hàng — một chi phí vận hành mà cửa hàng nhỏ khó duy trì. Các trợ lý dựng trên mô hình ngôn ngữ lớn theo lối gọi một bước thì cho câu trả lời trôi chảy và hiểu ngôn ngữ tự do rất tốt, nhưng lại có thể trả lời sai chính sách của cửa hàng và cam kết những việc hệ thống không làm được, bởi mô hình sinh văn bản theo xác suất chứ không theo một nguồn tri thức được kiểm soát. Cuối cùng, các hệ đa tác tử có tác tử điều phối trung tâm tự quyết định gọi tác tử nào thì linh hoạt, nhưng đánh mất tính dự đoán được: cùng một câu hỏi có thể đi qua những đường xử lý khác nhau, số lời gọi mô hình cho mỗi lượt không có trần chi phí, và khi có sự cố thì rất khó tái hiện lại đường đi để tìm nguyên nhân.

Từ khoảng trống đó, em chọn đề tài xây dựng một hệ thống chăm sóc khách hàng tự trị dùng kiến trúc đa tác tử AI cho cửa hàng thời trang trực tuyến. Mục tiêu của đề tài không phải thay thế con người, mà là tự động hoá phần việc lặp lại dựa trên một nguồn tri thức thống nhất và có thể kiểm chứng, nhờ đó dành thời gian của nhân viên cho những tình huống thật sự cần phán đoán: khiếu nại, ngoại lệ chính sách, và những yêu cầu mà hệ thống không đủ căn cứ để xử lý. Nguyên tắc xuyên suốt toàn bộ thiết kế là: **khi không đủ căn cứ thì chuyển yêu cầu cho nhân viên**, chứ không đoán — một câu trả lời sai chính sách gây thiệt hại lớn hơn nhiều so với một lần chuyển tiếp không cần thiết. Hai chỉ tiêu định lượng đặt ra cho hệ thống là tự động xử lý được từ 70% số lượt hội thoại trở lên, và giữ độ trễ phản hồi ở phân vị 95 không vượt quá 5 giây.

Nội dung báo cáo được trình bày qua ba chương và kết luận:

- **Chương 1: Tổng quan đề tài** — khảo sát các nhóm giải pháp tự động hoá chăm sóc khách hàng hiện có, xác định bài toán và phạm vi của đề tài, trình bày cơ sở lý thuyết và bộ công nghệ được lựa chọn.
- **Chương 2: Phân tích và thiết kế hệ thống** — trình bày bốn trụ cột thiết kế, pipeline bốn tác tử, các cơ chế an toàn và kiểm soát, thiết kế kho tri thức, cơ sở dữ liệu và bảo mật.
- **Chương 3: Thực nghiệm và triển khai** — trình bày môi trường và công cụ, quá trình triển khai các phân hệ, các thách thức kỹ thuật thực tế đã gặp, giao diện người dùng và kết quả đo đạc.
- **Kết luận** — đánh giá kết quả đạt được, những đóng góp về mặt thiết kế, hạn chế còn tồn tại và hướng phát triển tiếp theo.

# DANH MỤC TỪ VIẾT TẮT

| **Viết tắt** | **Dạng đầy đủ** | **Nghĩa tiếng Việt** |
|---|---|---|
| ACID | Atomicity, Consistency, Isolation, Durability | Nguyên tử — nhất quán — cô lập — bền vững; bốn thuộc tính của một giao dịch cơ sở dữ liệu |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| CAS | Compare-And-Set | So sánh rồi ghi; chỉ ghi khi giá trị hiện tại đúng như kỳ vọng |
| CSDL | Cơ sở dữ liệu | Cơ sở dữ liệu (database) |
| CSKH | Chăm sóc khách hàng | Chăm sóc khách hàng (customer support) |
| ERD | Entity Relationship Diagram | Sơ đồ quan hệ thực thể |
| FR | Functional Requirement | Yêu cầu chức năng |
| HITL | Human-In-The-Loop | Có người trong vòng lặp; con người tham gia vào luồng xử lý tự động |
| HS256 | HMAC using SHA-256 | Thuật toán chữ ký đối xứng dựa trên SHA-256, dùng để ký JWT |
| HTTPS | HyperText Transfer Protocol Secure | Giao thức truyền siêu văn bản có mã hoá |
| JSON | JavaScript Object Notation | Định dạng dữ liệu dạng văn bản theo cặp khoá — giá trị |
| JSONB | JSON Binary | Kiểu dữ liệu JSON lưu dạng nhị phân của PostgreSQL, truy vấn và lập chỉ mục được |
| JWT | JSON Web Token | Thẻ xác thực dạng JSON có chữ ký |
| KPI | Key Performance Indicator | Chỉ số hiệu quả trọng yếu |
| LLM | Large Language Model | Mô hình ngôn ngữ lớn |
| NFR | Non-Functional Requirement | Yêu cầu phi chức năng |
| NLU | Natural Language Understanding | Hiểu ngôn ngữ tự nhiên |
| PWA | Progressive Web App | Ứng dụng web tiến bộ; web cài được lên màn hình chính của điện thoại |
| RAG | Retrieval-Augmented Generation | Sinh có tăng cường truy hồi |
| RBAC | Role-Based Access Control | Phân quyền theo vai trò |
| REST | Representational State Transfer | Kiến trúc giao tiếp chuyển trạng thái đại diện qua HTTP |
| SQL | Structured Query Language | Ngôn ngữ truy vấn có cấu trúc |
| UUID | Universally Unique Identifier | Định danh duy nhất toàn cục |
| WSS | WebSocket Secure | Giao thức WebSocket có mã hoá |

**Lưu ý biên tập:** báo cáo mẫu CT060102 có mục tương ứng và đặt nó ngay sau LỜI CAM ĐOAN, trước
DANH MỤC HÌNH VẼ, nên bản .docx nên giữ mục này và đặt đúng vị trí đó. Nếu khoa không yêu cầu danh
mục từ viết tắt thì có thể bỏ toàn bộ mục này mà không ảnh hưởng tới thân bài.
