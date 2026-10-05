# Kịch bản thuyết trình bảo vệ đồ án

Dùng với `mau/cskh-a-hoc-thuat.html` (18 slide). Lời nói khoảng 1.900 tiếng, tức khoảng 13 phút 20 giây ở nhịp
150 tiếng/phút, chừa gần 2 phút dự phòng trong 15 phút.

- **Mốc đồng hồ:** hết slide 5 ≈ 2:45 · hết slide 9 ≈ 6:30 · hết slide 15 ≈ 12:00. Trễ quá 30 giây so với mốc thì
  các slide còn lại chỉ nói câu in đậm.
- **Câu in đậm** là ý bắt buộc phải nói. Phần còn lại nói theo ý, không cần thuộc từng chữ; riêng số liệu nói đúng
  như trên slide.
- Không đọc lại chữ trên slide. Hội đồng hỏi chi tiết thì chỉ sang số mục báo cáo ở chân slide.

---

## 1 · Bìa — 0:20 (mốc 0:20)

Em chào thầy cô trong hội đồng. Em là Bùi Anh Tuấn, CT060144. Em xin trình bày đồ án “Xây dựng hệ thống chăm sóc
khách hàng tự trị sử dụng Multi-Agent AI”, do ThS. Vũ Thị Hòa và ThS. Cao Thanh Vinh hướng dẫn.

## 2 · Nội dung trình bày — 0:15 (mốc 0:35)

Bài trình bày đi theo bốn phần của báo cáo. Chân mỗi slide em ghi số mục trong báo cáo để thầy cô tiện tra chi tiết.

## 3 · Bài toán — 0:50 (mốc 1:25)

Ở một shop thời trang online, phần lớn tin nhắn hỏi đi hỏi lại về giá, size, phí ship, đơn hàng, đổi trả; câu trả
lời đã nằm sẵn trong tài liệu. Vậy mà nhân viên vẫn phải trả lời tay, tin dồn vào buổi tối, mỗi người trả lời một
kiểu.

LLM giải quyết được phần hiểu câu hỏi. Nhưng để nó trả lời thẳng thì nó có thể bịa chính sách, bịa mã giảm giá rất
tự tin. Còn thêm một Supervisor tự chọn bước thì cùng một câu hỏi có thể đi nhiều đường, chi phí không có trần, lỗi
khó truy.

Nên câu hỏi em đặt ra là: **việc nào giao cho AI, việc nào phải giữ bằng luật cố định.**

## 4 · Khoảng trống — 0:40 (mốc 2:05)

Em khảo sát bốn nhóm giải pháp và đặt lên hai trục. Chatbot kịch bản và NLU truyền thống dự đoán được, nhưng không
hiểu câu nói tự do. LLM một bước và đa tác tử có Supervisor thì ngược lại: hiểu tốt nhưng mất kiểm soát luồng.

Đồ án nhắm vào góc còn trống: **giữ năng lực ngôn ngữ ở từng tác tử, nhưng rút quyền tự quyết khỏi tầng điều
phối.** Nhờ vậy mỗi lượt có trần chi phí: tối đa hai lời gọi LLM và một lời gọi embedding.

## 5 · Mục tiêu — 0:40 (mốc 2:45)

Từ đó đồ án có sáu mục tiêu, đi từ hiểu câu hỏi, tìm căn cứ, quyết định an toàn, sinh phản hồi, tới dashboard và
khả năng kiểm soát. Chỉ tiêu đo được là: tự trả lời từ 70% trở lên, chuyển nhầm cho nhân viên không quá 5%, thời
gian phản hồi P95 không quá 5 giây.

Nguyên tắc xuyên suốt: **không đủ chắc chắn thì chuyển nhân viên.** Phạm vi là chat web với đơn hàng mô phỏng; hệ
thống không tự huỷ đơn hay hoàn tiền.

## 6 · Pipeline — 0:55 (mốc 3:40)

Đây là kiến trúc lõi. Mỗi tin nhắn đi qua bốn tác tử theo một thứ tự cố định.

Tác tử một dùng LLM phân loại vào 15 ý định và trích thực thể; mã đơn được bắt thêm bằng biểu thức chính quy để
không mất khi LLM lỗi. Tác tử hai tìm tri thức trong Qdrant và tra đơn hàng. Tác tử ba quyết định hướng đi, và
**nó không gọi LLM**. Tác tử bốn là nơi duy nhất được nói với khách.

Đầu ra chỉ có ba kết cục: gửi thẳng, giữ nháp chờ duyệt, hoặc chuyển người; riêng câu hỏi về đơn mà thiếu mã thì
hệ thống hỏi lại khách.

Điểm mấu chốt: **tác tử chỉ quyết nội dung, không tác tử nào được chọn bước tiếp theo.**

## 7 · Quyết định bằng luật — 1:00 (mốc 4:40)

Tác tử ba chỉ đọc cờ. Có tám cờ chặn: bốn cờ từ tác tử một, như câu ngoài phạm vi hay khách xin gặp người; bốn cờ
từ tác tử hai, như không có tri thức, điểm truy hồi thấp hay lỗi tìm kiếm. Chỉ cần một cờ là chuyển người.

Em cố ý không cộng độ tự tin của LLM với điểm truy hồi, vì hai con số này khác bản chất. Ngưỡng số duy nhất là
ngưỡng truy hồi, và em chọn nó bằng đo đạc ở phần sau.

Bên phải là ranh giới em coi là quan trọng nhất. Lớp an toàn trả lời câu “có đủ căn cứ không”, Admin không chỉnh
được. Lớp cấu hình chỉ chọn “gửi ngay hay chờ duyệt” cho ca đã an toàn. Nên **Admin cấu hình thế nào cũng không
biến được ca rủi ro thành ca tự trả lời.**

## 8 · Chống ảo giác — 0:55 (mốc 5:35)

Tác tử bốn chống ba dạng ảo giác. Dạng thứ nhất là bịa ra cái có, như mã giảm giá; em chặn bằng cách chỉ cho dùng
ba nguồn. Dạng thứ hai ít được nhắc hơn: **bịa ra cái không có**. Tài liệu không nhắc giao quốc tế, mô hình lại kết
luận shop không giao; quy tắc ở đây là “chưa có thông tin” khác với “không tồn tại”. Dạng thứ ba là bịa hành động,
kiểu “em đã hoàn tiền”; tác tử bốn chỉ được tra cứu và không được tự hứa chuyển nhân viên.

Thêm một phanh cứng: không có nguồn hoặc không gọi được LLM thì không sinh câu trả lời, chuyển thẳng cho người. Các
thông báo quan trọng đều là câu cố định, không qua LLM.

## 9 · Độ bền và bảo mật — 0:55 (mốc 6:30)

Ngoài nội dung, hệ thống còn phải đúng trong ba tình huống khó. Khi đồng thời: một lượt AI mất vài giây, Admin có
thể nhận ca giữa chừng; nhờ so-sánh-rồi-ghi, lượt AI đó bị huỷ, không có cảnh AI và người cùng trả lời. Dữ liệu
luôn ghi xong mới báo khách.

Khi dịch vụ ngoài lỗi: mỗi điểm lỗi có cờ riêng và lối thoát an toàn; ví dụ Qdrant lỗi được ghi đúng là lỗi hạ
tầng, không bị hiểu nhầm là kho thiếu nội dung.

Khi bị tấn công: ngoài bốn lớp chống prompt injection, điều quan trọng hơn là **giới hạn quyền**: kể cả khi LLM bị
dẫn dắt, nó cũng không xem được đơn của người khác và không có đường nào để tự chuyển ca.

## 10 · Truy hồi — 0:55 (mốc 7:25)

Sang phần thực nghiệm. Vấn đề đầu tiên là giọng văn: khách hỏi kiểu đời thường, tài liệu viết trang trọng, nên cùng
ý mà điểm vẫn thấp. Em thêm câu hỏi mẫu vào đầu mỗi tài liệu để so câu hỏi với câu hỏi: 26 trên 32 câu khớp qua
đường này, trung vị 0,70, so với 0,54 khi chỉ khớp được với thân tài liệu.

Nhưng khi đo 32 câu trả lời được và 25 câu không trả lời được, hai phân bố vẫn chồng lấn trong khoảng 0,38 đến 0,66.
Nghĩa là **không có ngưỡng nào tách sạch hai tập.**

## 11 · Chọn ngưỡng — 1:00 (mốc 8:25)

Vậy chọn ngưỡng thế nào? Nếu lấy tổng lỗi nhỏ nhất thì rơi vào 0,60 đến 0,65, nhưng khi đó 41 đến 50% câu trả lời
được bị chuyển oan.

Em cho rằng hai loại lỗi không ngang giá. Chuyển oan thì không còn bước nào sửa lại, khách phải chờ người. Còn tài
liệu yếu lọt qua thì phía sau vẫn còn lớp kiểm tra ngoài phạm vi và quy tắc bám nguồn.

Nên quy tắc là: **chọn ngưỡng cao nhất mà chuyển oan không quá 5%.** Kết quả là 0,40, chỉ 1 trên 32 câu bị chuyển
oan. Em cũng kiểm tra riêng các câu nằm trong vùng chồng lấn: hệ thống không bịa số liệu, mã giảm giá hay chính
sách nào.

## 12 · Bài học — 0:55 (mốc 9:20)

Hai bài học khi chạy trên dữ liệu thật. Thứ nhất: khách chỉ nói “xin chào shop” mà bị chuyển cho nhân viên, vì chưa
có nhãn xã giao và tác tử hai vẫn đòi tài liệu làm căn cứ; phải sửa cả hai tác tử mới hết. Tương tự, câu hỏi chính
sách đổi trả bị gộp vào hoàn tiền nên bị giữ chờ duyệt; em tách thành nhãn riêng. Bài học là **luật an toàn đúng
nhưng phạm vi quá rộng thì mất giá trị tự động**, và em không nới tập cờ chặn.

Thứ hai: trạng thái phải đến từ cấu trúc, không từ câu chữ. Tra đơn có ba tín hiệu riêng, nên khách gõ sai mã chỉ
bị hỏi lại chứ không bị chuyển oan.

## 13 · Giao diện — 0:35 (mốc 9:55)

Đây là giao diện, một ứng dụng web cho hai vai. Bên trái là cổng chat: câu trả lời lấy đúng phí ship trong chính
sách. Ở giữa là EscalationCard nhân viên nhận khi ca được chuyển: lý do, ý định, nguồn tri thức kèm điểm, nên
**nhân viên không phải đọc lại hội thoại từ đầu.** Bên phải là màn cấu hình cổng theo từng ý định. Mọi thứ cập nhật
qua WebSocket và cài được lên điện thoại.

## 14 · Chất lượng xử lý — 1:00 (mốc 10:55)

Về chất lượng: trên bộ 20 câu chạy trên hệ thống thật, **90% được xử lý mà không cần nhân viên ngay**: 75% trả lời
luôn, 15% là hỏi lại mã đơn đúng thiết kế. Một câu khiếu nại chờ duyệt, một câu ngoài phạm vi chuyển người. Chuyển
oan 3%, không có phản hồi dự phòng oan. Bốn KPI chất lượng đều đạt.

Về bám nguồn: phí ship trả đúng số trong chính sách, xin mã giảm 70% thì không bịa mã, đòi hoàn tiền thì không nói
đã hoàn. Hạn chế em ghi nhận thẳng là còn hai ca mô hình suy diễn “không có” khi tài liệu không nhắc tới.

Phần lõi có 437 trường hợp kiểm thử tự động, chạy ngoại tuyến.

## 15 · Độ trễ — 1:00 (mốc 11:55)

**Chỉ tiêu chưa đạt là độ trễ.** Ở 25 hội thoại đồng thời p95 là 5,5 giây, vượt ngưỡng không nhiều; lên 100 hội
thoại thì 9,7 giây. Tuy vậy 100 trên 100 lượt đều không lỗi, nên yêu cầu phục vụ 100 người dùng đồng thời vẫn đạt.

Nhờ nhật ký tách thời gian từng bước, em xác định được nguyên nhân: ba bước nối tiếp là LLM, embedding cộng Qdrant,
rồi LLM, mỗi bước khoảng 1,1 giây. Bằng chứng là lượt chào hỏi chỉ một lời gọi LLM thì p95 còn 4,4 giây. Hướng xử
lý là đặt các dịch vụ gần nhau và bớt truy vấn thừa.

## 16 · Đóng góp — 0:40 (mốc 12:35)

Tóm lại, đồ án có bốn đóng góp. Một: chủ động bỏ Supervisor để mỗi lượt dự đoán được và có trần chi phí. Hai: tách
ảo giác thành ba dạng, mỗi dạng một cơ chế chống. Ba: tách lớp an toàn khỏi cấu hình nghiệp vụ, để cấu hình không vô
tình tắt được bảo vệ. Bốn: chọn ngưỡng truy hồi theo chi phí từng loại lỗi, trên dữ liệu đo được.

Điều em rút ra lớn nhất: **AI làm phần hiểu và diễn đạt; những quyết định có rủi ro phải giữ bằng luật.**

## 17 · Hạn chế và hướng phát triển — 0:35 (mốc 13:10)

Về hạn chế: độ trễ chưa đạt khi tải cao; truy hồi còn có thể cải thiện bằng lọc và xếp hạng lại; tin nhiều ý định
vẫn chuyển người; và hệ thống mới chạy an toàn trên một tiến trình. Ngắn hạn em xử lý các điểm này. Xa hơn là
**vòng học bán tự động: hệ thống đề xuất, con người quyết định**, và tích hợp hệ thống đơn hàng thật, với thao tác
nhạy cảm do người duyệt.

## 18 · Cảm ơn — 0:10 (mốc 13:20)

Em xin cảm ơn thầy cô đã lắng nghe, và rất mong nhận được câu hỏi, góp ý của hội đồng.
