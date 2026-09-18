> **Tệp bàn giao cho Claude Word — bản rút gọn ngày 17/09/2026.** Toàn báo cáo đã được rút gọn còn khoảng
> 32.000 từ, tính cả chữ trong bảng. Nội dung đã lược bỏ (bản gốc đầy đủ) và khối ghi chú bàn giao trước
> đây nằm ở `baocao/doc.md`.
>
> - **Việc còn tồn về trích dẫn:** [1]–[10] và [14] đã có trong thân bài Chương 1; [11], [12] (nên gắn ở mục
>   2.9.3) và [13] (mục 2.2.2) chưa được trích. Bốn bài báo [1], [2], [3], [12] cần tra lại tác giả, năm, nơi
>   công bố; tài liệu trực tuyến cần ghi ngày truy cập thật.

---

# TỔNG KẾT

## Kết quả đạt được

Đồ án đã xây dựng hoàn chỉnh một hệ thống chăm sóc khách hàng tự trị cho cửa hàng thời trang trực tuyến trên kiến trúc pipeline bốn tác tử cố định, vận hành thông suốt trên hạ tầng thật và có đủ công cụ giám sát. Dưới đây là bảng đối chiếu kết quả với sáu mục tiêu đã đặt ra ở Chương 1.

| **Mục tiêu** | **Kết quả** |
|---|---|
| M1 — Phân loại ý định và trích thực thể | Đạt. Taxonomy 15 ý định nằm trong prompt, không cần huấn luyện; trích thực thể hai đường bảo đảm không mất mã đơn |
| M2 — Truy hồi tri thức để trả lời có căn cứ | Đạt. Kho tri thức canonical, chia đoạn theo section, mở rộng truy vấn, nạp lại blue/green |
| M3 — Đánh giá rủi ro và ra quyết định | Đạt. Tác tử quyết định tất định trên tám cờ chặn, không gọi mô hình, không gộp hai thang độ tin cậy |
| M4 — Sinh phản hồi sau cổng kiểm soát | Đạt. Điểm phát ngôn duy nhất, ba nguồn căn cứ, phanh cứng chống ảo giác |
| M5 — Dashboard giám sát và hàng đợi | Đạt. Năm module, realtime không polling, EscalationCard, duyệt nháp, cổng theo ý định |
| M6 — Bảo đảm tính kiểm soát | Đạt. Sáu dòng nhật ký mỗi lượt, HITL ba mức, cổng cấu hình, bốn lớp chống chèn chỉ dẫn |

Về định lượng, hệ thống vượt các chỉ tiêu KPI về chất lượng xử lý: 90% số lượt được gửi thẳng, trong đó 75% là câu trả lời ngay và 15% là câu hỏi lại mã đơn (mục tiêu ≥ 70%), 5% phải chuyển cho nhân viên (mục tiêu < 30%), 3% chuyển ca không cần thiết (ngân sách ≤ 5%) và 0% phản hồi dự phòng không cần thiết. Riêng chỉ tiêu thời gian phản hồi mới chỉ sát mục tiêu ở tải thấp, với trung bình 5,1 giây ở 10 hội thoại đồng thời và 5,0 giây ở 25, rồi tăng lên 9,0 giây ở 100 hội thoại (mục 3.5.6). Về kỹ thuật, hệ thống gồm khoảng 7.900 dòng Python, gần 6.800 dòng kiểm thử với 387 hàm kiểm thử chạy ngoại tuyến, khoảng 5.500 dòng TypeScript, 11 migration và 15 tài liệu tri thức gốc.

## Những đóng góp đáng chú ý của đồ án

Bên cạnh các mục tiêu chức năng, đồ án có bốn đóng góp về mặt thiết kế:

- **Loại bỏ tác tử điều phối trung tâm một cách có chủ đích:** với ràng buộc chặt về độ trễ, chi phí và kiểm toán, một pipeline tĩnh đủ đáp ứng bài toán, có trần chi phí xác định và một đường chạy duy nhất để kiểm toán; các yêu cầu phức hợp được hấp thụ an toàn qua nhánh chuyển cho nhân viên.

- **Phân loại ba dạng ảo giác cùng cơ chế chống tương ứng:** ngoài bịa ra thông tin, đồ án chỉ ra hai dạng ít được đề cập là suy diễn phủ định từ chỗ nguồn im lặng và bịa ra hành động; dạng thứ ba được chặn bằng một bất biến kiến trúc chứ không chỉ bằng prompt.

- **Ranh giới bất khả xâm phạm giữa an toàn và cấu hình:** việc có đủ căn cứ để trả lời hay không do mã tất định quyết định, còn việc có được trả lời tự động hay không do con người cấu hình, nên thao tác cấu hình không thể vô tình vô hiệu hoá cơ chế an toàn.

- **Chọn ngưỡng theo ngân sách lỗi không cân xứng:** khi hai phân bố điểm truy hồi chồng lấn, ngưỡng được chọn theo ngân sách của loại lỗi không khắc phục được thay vì theo cực tiểu tổng lỗi — cách làm áp dụng được cho các hệ thống RAG có cơ chế chuyển tiếp cho con người.

## Hạn chế

Các hạn chế đã nêu chi tiết ở mục 3.5.8 gồm ba nhóm. Về xử lý ngôn ngữ, hệ thống chưa có sàn điểm theo đoạn, chưa xếp hạng lại kết quả, chưa ngữ cảnh hoá câu hỏi nối tiếp, chưa xử lý nhiều ý định trong một tin nhắn và còn hiện tượng quá lời theo hướng phủ định. Về kiến trúc, hệ thống chạy trên một tiến trình, cơ chế lưu điểm kiểm tra chưa bền vững, chưa phát hiện được quản trị viên trực tuyến, và độ trễ chưa đạt yêu cầu NFR-1 khi tải tăng: ngay sau vòng tối ưu hồ kết nối, p95 vẫn là 9,7 giây ở 100 hội thoại đồng thời và trung bình 5,0 giây ở 25 hội thoại, trong đó phần tăng theo tải đã chuyển từ các vòng truy vấn cơ sở dữ liệu sang hai lời gọi ra ngoài là embedding và truy vấn Qdrant. Về chức năng, vòng học bán tự động và thao tác trên đơn hàng chưa được xây dựng, độ trễ phía người dùng chưa được đo.

## Hướng phát triển

Hướng phát triển được chia thành ba giai đoạn; với mỗi hướng, yêu cầu xuyên suốt là giữ nguyên các bất biến an toàn đã xây dựng.

**Trong ngắn hạn:**

- **Sàn điểm theo đoạn và bước xếp hạng lại** ở khâu hậu xử lý truy hồi; sàn điểm chỉ lọc nội dung đưa vào prompt, không trở thành ngưỡng định tuyến thứ hai.

- **Ngữ cảnh hoá truy vấn** bằng bước viết lại câu hỏi nối tiếp trước khi tạo embedding, chỉ chạy khi phát hiện câu hỏi nối tiếp để giữ trần chi phí và ràng buộc NFR-1.

- **Kho chia sẻ ngoài tiến trình và checkpointer bền vững** để chạy nhiều tiến trình, trong khi vẫn giữ cơ chế so sánh rồi ghi trên bản ghi hội thoại, thứ tự ghi trước rồi mới báo khách và chỉ mục chống trùng trên bảng `message`.

- **Xử lý nhiều ý định trong một tin nhắn** bằng cách tách yêu cầu con; mỗi yêu cầu đi trọn pipeline và chịu đúng cổng cấu hình của ý định, kết quả của lượt là kết quả nghiêm ngặt nhất.

- **Phát hiện cảm xúc của khách** chỉ để nâng mức ưu tiên trong hàng đợi, không đưa vào tập cờ chặn.

- **Giảm độ trễ dưới tải.** Vòng tối ưu hồ kết nối ở mục 3.5.6 đã đưa p95 ở 100 hội thoại đồng thời từ 13,1 giây xuống 9,7 giây và đẩy điểm nghẽn sang các lời gọi ra ngoài; bước tiếp theo là đặt backend cùng vùng với cơ sở dữ liệu, chuyển cụm Qdrant về vùng gần và gộp bớt các vòng truy vấn trước pipeline, rồi đo lại cùng kịch bản; đồng thời đo độ trễ phía người dùng cuối.

**Trong trung hạn**, đồ án hướng tới vòng học bán tự động: tổng hợp các mẫu lặp lại trong nhật ký kiểm toán thành đề xuất bổ sung tài liệu hoặc câu hỏi — như trường hợp câu hỏi về cách phơi đồ tránh giãn chỉ khớp ở mức 0,380 — kèm bằng chứng truy vết được; tác tử chỉ đề xuất, con người phê duyệt.

**Trong dài hạn**, hệ thống có thể mở rộng theo bốn hướng:

- **Tích hợp hệ thống quản lý đơn hàng thật** để thao tác được trên đơn. Đây là hướng rủi ro nhất vì phá bỏ bất biến đang chặn dạng ảo giác thứ ba, nên phải bù bằng xác nhận nhiều bước, nhật ký từng thao tác và bắt buộc qua cổng duyệt của con người.

- **Bộ nhớ xuyên hội thoại và hồ sơ khách hàng**, chỉ dùng để cá nhân hoá cách diễn đạt, không dùng làm căn cứ cho chính sách hay trạng thái đơn hàng.

- **Mở rộng sang các nền tảng nhắn tin và mạng xã hội** bằng tầng chuyển đổi ở biên, giữ nguyên pipeline lõi để không phải kiểm chứng lại các bảo đảm an toàn cho từng kênh.

- **Hỗ trợ đa ngôn ngữ** với kho tri thức nhân bản theo từng ngôn ngữ, vì kỹ thuật mở rộng truy vấn dựa vào sự tương đồng cách diễn đạt trong cùng một ngôn ngữ.

## Kết luận chung

Đồ án đã xây dựng thành công một hệ thống chăm sóc khách hàng tự trị dựa trên kiến trúc đa tác tử AI, đạt toàn bộ sáu mục tiêu chức năng và vượt các chỉ tiêu KPI về chất lượng xử lý; riêng chỉ tiêu thời gian phản hồi chưa đạt khi tải tăng, nguyên nhân và hướng xử lý đã được chỉ ra bằng số đo ở mục 3.5.6.

Bài học quan trọng nhất không nằm ở kỹ thuật ghép nối các thành phần AI, mà ở việc xác định ranh giới giữa những quyết định nên giao cho mô hình ngôn ngữ và những quyết định bắt buộc do mã tất định đảm nhiệm. Mô hình làm rất tốt việc hiểu câu hỏi và diễn đạt câu trả lời, nhưng không đủ tin cậy để quyết định có nên trả lời khách hay không và được phép cam kết những gì. Nguyên tắc chuyển ca cho nhân viên mỗi khi không đủ căn cứ thoạt nhìn có vẻ khiêm tốn, nhưng chính nó cho phép hệ thống đạt mức tự động hoá 90% mà vẫn kiểm soát được sai sót — một đánh đổi xứng đáng với hệ thống trao đổi trực tiếp với khách hàng.

# TÀI LIỆU THAM KHẢO

| \[1\]  | A. Vaswani và cộng sự, "Attention Is All You Need," Advances in Neural Information Processing Systems 30, 2017.                                                                                                                          |
|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| \[2\]  | P. Lewis và cộng sự, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," Advances in Neural Information Processing Systems 33, 2020.                                                                                     |
| \[3\]  | Z. Ji và cộng sự, "Survey of Hallucination in Natural Language Generation," ACM Computing Surveys, vol. 55, no. 12, 2023.                                                                                                                |
| \[4\]  | LangChain, "LangGraph Documentation," \[Trực tuyến\]. Truy cập: https://langchain-ai.github.io/langgraph/                                                                                                                                |
| \[5\]  | OpenAI, "Embeddings — OpenAI API Documentation," \[Trực tuyến\]. Truy cập: https://platform.openai.com/docs/guides/embeddings                                                                                                            |
| \[6\]  | OpenAI, "Structured Outputs / JSON mode," \[Trực tuyến\]. Truy cập: https://platform.openai.com/docs/guides/structured-outputs                                                                                                           |
| \[7\]  | Qdrant, "Qdrant Documentation — Collections, Aliases and Filtering," \[Trực tuyến\]. Truy cập: https://qdrant.tech/documentation/                                                                                                        |
| \[8\]  | S. Ramírez, "FastAPI Documentation," \[Trực tuyến\]. Truy cập: https://fastapi.tiangolo.com/                                                                                                                                             |
| \[9\]  | SQLAlchemy, "SQLAlchemy 2.0 Documentation — asyncio support," \[Trực tuyến\]. Truy cập: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html                                                                                    |
| \[10\] | Vercel, "Next.js App Router Documentation," \[Trực tuyến\]. Truy cập: https://nextjs.org/docs/app                                                                                                                                        |
| \[11\] | OWASP Foundation, "OWASP Top 10 for Large Language Model Applications — LLM01: Prompt Injection," 2025. \[Trực tuyến\]. Truy cập: https://owasp.org/www-project-top-10-for-large-language-model-applications/                            |
| \[12\] | K. Greshake và cộng sự, "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection," Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (AISec), 2023. |
| \[13\] | I. Fette và A. Melnikov, "The WebSocket Protocol," RFC 6455, IETF, 2011.                                                                                                                                                                 |
| \[14\] | Langfuse, "Langfuse Documentation — Tracing for LLM Applications," \[Trực tuyến\]. Truy cập: https://langfuse.com/docs                                                                                                                   |
