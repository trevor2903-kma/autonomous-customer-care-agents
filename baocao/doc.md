# NỘI DUNG ĐÃ LƯỢC BỎ KHỎI BÁO CÁO

> Tệp này lưu nguyên văn mọi nội dung đã được đưa ra khỏi `chuong-1.md`, `chuong-2.md`, `chuong-3.md`,
> `tong-ket.md` và `phu-luc.md` qua hai lượt rút gọn ngày 17/09/2026. Sau khi rút gọn, toàn báo cáo (kể cả
> `loi-mo-dau.md`) còn khoảng 32.000 từ, **tính cả chữ trong bảng**.
>
> - **Phần 1** gồm các vùng đã bỏ hoặc đã viết gọn trong thân bài, xếp theo tệp và theo mục. Nhãn *Đã lược bỏ*
>   nghĩa là vùng đó không còn trong thân bài; nhãn *Đã rút gọn* nghĩa là thân bài giữ một bản ngắn hơn (kể cả
>   bảng đã thu gọn ô), còn dưới đây luôn là **bản gốc đầy đủ** trước khi rút gọn. Dòng "Nằm sau" trích câu mở
>   đầu của đoạn đứng ngay trước trong bản gốc, để định vị khi cần khôi phục.
> - **Phần 2** gồm khối ghi chú bàn giao cho Claude Word ở đầu mỗi tệp trước khi rút gọn.
> - Toàn bộ mục, hình và bảng của báo cáo vẫn được giữ, số hiệu không đổi; riêng mục 1.5.6 và mục I của Phụ lục
>   đã bỏ hẳn (đều là mục cuối nên không làm lệch số hiệu).
> - Tiêu đề nằm bên trong nội dung trích đã được hạ hai cấp (thêm `##`) để không lẫn với cấu trúc của tệp này.

## Phần 1. Nội dung lược bỏ khỏi thân báo cáo

### Chương 1 — Tổng quan đề tài (`chuong-1.md`)

#### Mục 1.1.1 — Nhu cầu tự động hoá chăm sóc khách hàng trong thương mại điện tử · Đã rút gọn

*Nằm sau: «Nhu cầu tự động hoá chăm sóc khách hàng trong thương mại điện tử …»*

Chăm sóc khách hàng (CSKH) là khâu tiếp xúc trực tiếp và thường xuyên nhất giữa một cửa hàng trực tuyến với người mua. Trong mô hình bán lẻ thời trang trực tuyến, công tác này bộc lộ ba đặc thù rõ nét, đồng thời cũng chính là ba điểm nghẽn của quy trình vận hành thủ công hiện nay.

Thứ nhất là tỉ lệ câu hỏi lặp lại rất cao. Qua khảo sát nội dung hội thoại thực tế của các cửa hàng thời trang trên những nền tảng nhắn tin phổ biến, phần lớn tin nhắn của khách hàng tập trung vào một số nhóm hữu hạn: hỏi giá, hỏi thông tin sản phẩm (chất liệu, màu sắc, tình trạng còn hàng), nhờ tư vấn chọn kích cỡ, hỏi phí và thời gian vận chuyển, tra trạng thái đơn hàng, hỏi hình thức thanh toán, hỏi chính sách đổi trả và hỏi chương trình khuyến mãi. Câu trả lời cho những nhóm câu hỏi này đều đã tồn tại sẵn trong tài liệu chính sách của cửa hàng; phần việc còn lại của nhân viên chỉ là đọc tài liệu và diễn đạt lại cho khách, một thao tác mang tính lặp lại và tiêu tốn đáng kể quỹ thời gian.

Thứ hai, thời gian phản hồi có ảnh hưởng trực tiếp tới tỉ lệ chốt đơn. Một khách hàng đang cân nhắc mua hàng nhưng phải chờ tới mười lăm phút mới biết sản phẩm còn kích cỡ phù hợp hay không thì khả năng rời đi là rất cao. Trong khi đó, đội ngũ nhân viên CSKH thường chỉ làm việc trong giờ hành chính, còn lưu lượng tin nhắn của khách lại dồn vào buổi tối và các ngày cuối tuần, tạo ra độ lệch đáng kể giữa nhu cầu của người mua và năng lực phục vụ của cửa hàng.

Thứ ba, chất lượng phản hồi và khả năng giám sát đều ở mức thấp. Mỗi nhân viên trả lời theo trí nhớ và cách hiểu riêng về chính sách, nên không có cơ chế nào bảo đảm hai nhân viên cùng trả lời một câu hỏi sẽ đưa ra cùng một nội dung chính sách. Khi phát sinh khiếu nại, việc truy lại xem nhân viên nào đã trao đổi những gì với khách và dựa trên căn cứ nào gần như không thể thực hiện được.

Về mặt nguyên lý, ba vấn đề nêu trên có chung một hướng giải quyết là chuyển phần công việc lặp lại cho hệ thống tự động xử lý theo một nguồn tri thức thống nhất, qua đó dành thời gian của con người cho những tình huống thực sự cần tới phán đoán. Tuy nhiên, ranh giới giữa hai phần công việc này không cố định và cũng không hiển nhiên. Việc xác định chính xác ranh giới đó chính là bài toán kỹ thuật trung tâm mà đề tài hướng tới giải quyết.

#### Mục 1.1.2 — Khảo sát các giải pháp hiện có · Đã rút gọn

*Nằm sau: «Khảo sát các giải pháp hiện có …»*

Để tự động hoá công tác chăm sóc khách hàng, trên thị trường hiện nay đã xuất hiện nhiều nhóm giải pháp khác nhau. Khi đối chiếu với yêu cầu thực tiễn của một cửa hàng thời trang trực tuyến, có thể phân tích mức độ phù hợp của các giải pháp này thông qua bốn nhóm tiêu biểu sau.

**a) Chatbot theo kịch bản (rule-based / decision tree).** Đây là nhóm phổ biến nhất tại Việt Nam, thường được tích hợp sẵn trên các nền tảng nhắn tin. Hệ thống đưa ra các nút bấm và khách hàng lựa chọn theo một cây quyết định do người vận hành dựng sẵn.

- *Ưu điểm:* Luồng xử lý hoàn toàn dự đoán được, chi phí triển khai gần như bằng không và nội dung phản hồi không bao giờ sai lệch do mọi câu trả lời đều do con người biên soạn trước.

- *Nhược điểm:* Hệ thống không có khả năng hiểu ngôn ngữ tự nhiên. Khi khách hàng diễn đạt tự do, chẳng hạn hỏi về kích cỡ phù hợp với cân nặng của mình, hệ thống không khớp được với bất kỳ nút bấm nào. Bên cạnh đó, cây kịch bản mở rộng rất nhanh theo số lượng tình huống và sớm vượt quá khả năng bảo trì. Trải nghiệm sử dụng vì vậy khá cứng nhắc, khiến khách hàng thường bỏ qua để yêu cầu gặp nhân viên ngay từ đầu.

Dưới đây là ảnh chụp một chatbot theo kịch bản đang hoạt động trên nền tảng nhắn tin, trong đó khách hàng chỉ chọn được các nút bấm dựng sẵn và không có chỗ nào để diễn đạt câu hỏi bằng ngôn ngữ tự do (Hình 1.1).

Hình 1.1. Giao diện chatbot theo kịch bản trên nền tảng nhắn tin

**b) Chatbot NLU truyền thống (Dialogflow, Rasa và các nền tảng tương tự).** Nhóm này sử dụng mô hình phân loại ý định được huấn luyện trên tập câu mẫu, kết hợp với trích xuất thực thể và quản lý hội thoại theo cơ chế điền khe (slot-filling).

- *Ưu điểm:* Hệ thống hiểu được các diễn đạt tự do ở mức khá, đồng thời vẫn giữ được khả năng kiểm soát luồng hội thoại.

- *Nhược điểm:* Phương pháp này đòi hỏi gán nhãn thủ công một lượng lớn câu mẫu cho mỗi ý định và phải huấn luyện lại mỗi khi nghiệp vụ thay đổi. Câu trả lời vẫn dựa trên các khuôn mẫu cố định nên không xử lý được những câu hỏi mang tính tổng hợp. Đối với một cửa hàng quy mô nhỏ, chi phí xây dựng và duy trì tập huấn luyện là một rào cản đáng kể.

Dưới đây là ảnh chụp giao diện huấn luyện ý định của một nền tảng NLU truyền thống, trong đó thấy rõ danh sách câu mẫu phải gán nhãn thủ công cho một ý định duy nhất — chính là khối lượng công việc làm nên chi phí xây dựng tập huấn luyện (Hình 1.2).

Hình 1.2. Giao diện huấn luyện ý định của một nền tảng NLU truyền thống

**c) Trợ lý dựa trên mô hình ngôn ngữ lớn thuần hoặc kết hợp truy hồi một bước.** Nhóm này gửi thẳng câu hỏi của khách hàng tới một mô hình ngôn ngữ lớn, có thể kèm theo một bước truy hồi tài liệu liên quan để mô hình bám vào khi sinh câu trả lời.

- *Ưu điểm:* Thời gian triển khai rất nhanh, khả năng hiểu ngôn ngữ tự nhiên tốt và câu trả lời có độ trôi chảy cao.

- *Nhược điểm:* Đây là nhóm giải pháp tiềm ẩn rủi ro lớn nhất trong ngữ cảnh chăm sóc khách hàng. Khi tri thức truy hồi được yếu hoặc không liên quan, mô hình vẫn sinh ra câu trả lời, và câu trả lời đó có thể chứa một chính sách đổi trả, một mã giảm giá hay một mốc thời gian không hề tồn tại. Nghiêm trọng hơn, mô hình có xu hướng cam kết những hành động mà hệ thống không có khả năng thực hiện, chẳng hạn khẳng định đã hoàn tiền hoặc đã chuyển yêu cầu cho nhân viên, qua đó tạo ra cam kết giả với khách hàng. Ngoài ra, kiến trúc một bước không có điểm nào để hệ thống từ chối trả lời một cách có cấu trúc, đồng thời cũng không có cơ chế chuyển tiếp yêu cầu cho con người.

Dưới đây là ảnh chụp một trợ lý dựa trên mô hình ngôn ngữ lớn kết hợp truy hồi một bước, trong đó cần thấy câu trả lời rất trôi chảy nhưng không kèm trích dẫn nguồn và giao diện không có lối nào để chuyển yêu cầu cho nhân viên thật (Hình 1.3).

Hình 1.3. Trợ lý dựa trên mô hình ngôn ngữ lớn kết hợp truy hồi một bước

**d) Hệ đa tác tử có tác tử điều phối trung tâm (Supervisor).** Đây là kiến trúc đang được nhiều framework quảng bá, trong đó một tác tử điều phối trung tâm đọc yêu cầu rồi tự quyết định tại thời điểm chạy sẽ gọi tác tử chuyên biệt nào, theo thứ tự nào và lặp lại bao nhiêu vòng.

- *Ưu điểm:* Kiến trúc có độ linh hoạt tối đa, xử lý được cả những yêu cầu phức hợp không lường trước.

- *Nhược điểm:* Chính sự linh hoạt này lại phá vỡ khả năng dự đoán của hệ thống. Cùng một câu hỏi có thể đi qua hai đường xử lý khác nhau ở hai lần chạy khác nhau; số lời gọi mô hình, và kéo theo đó là chi phí cùng độ trễ, không có giới hạn trên chắc chắn. Khi hệ thống hành xử sai, việc truy nguyên nguyên nhân cũng rất khó khăn do bản thân quyết định điều phối cũng được đưa ra bởi một mô hình xác suất. Đối với một hệ thống đối thoại trực tiếp với khách hàng và có ràng buộc chặt về độ trễ, đây là cái giá quá đắt.

Dưới đây là ảnh chụp sơ đồ kiến trúc điều phối động của một framework đa tác tử, trong đó cần thấy tác tử Supervisor nằm ở vị trí trung tâm cùng các cạnh quay vòng trở lại nó — biểu thị việc số lời gọi mô hình trong một lượt không có giới hạn trên xác định (Hình 1.4).

Hình 1.4. Kiến trúc điều phối động có tác tử Supervisor

Dưới đây là bảng so sánh bốn nhóm giải pháp vừa khảo sát với hệ thống mà đề tài đề xuất, theo bảy tiêu chí gắn với yêu cầu thực tiễn của một cửa hàng thời trang trực tuyến (Bảng 1.1).

#### Mục 1.1.2 — Khảo sát các giải pháp hiện có · Đã rút gọn

*Nằm sau: «Công sức soạn và bảo trì nội dung trả lời Rất cao Cao Thấp …»*

Từ kết quả khảo sát trên có thể rút ra một khoảng trống đáng chú ý: chưa có nhóm giải pháp nào vừa hiểu được ngôn ngữ tự nhiên, vừa giữ được tính dự đoán và khả năng kiểm toán ở mức chấp nhận được đối với một hệ thống đối thoại trực tiếp với khách hàng. Đề tài hướng tới việc lấp đúng khoảng trống này bằng cách giữ lại năng lực ngôn ngữ của mô hình ngôn ngữ lớn ở tầng tác tử, đồng thời rút quyền tự trị ra khỏi tầng điều phối.

Dưới đây là sơ đồ định vị bốn nhóm giải pháp vừa khảo sát trên hai trục năng lực hiểu ngôn ngữ tự nhiên và mức độ dự đoán được của luồng chạy, qua đó thể hiện trực quan khoảng trống mà đề tài hướng tới (Hình 1.5).

#### Mục 1.2.1 — Bài toán đặt ra · Đã rút gọn

*Nằm sau: «Bài toán đặt ra …»*

Xuất phát từ những hạn chế thực tiễn của các nhóm giải pháp đã phân tích ở phần trên, bài toán đặt ra cho đề tài là xây dựng một hệ thống chăm sóc khách hàng cho cửa hàng thời trang trực tuyến, trong đó nhiều tác tử AI chuyên biệt phối hợp với nhau trong một pipeline cố định để tiếp nhận, hiểu, tra cứu tri thức và trả lời câu hỏi của khách hàng. Con người chỉ can thiệp ở những trường hợp quan trọng hoặc khi hệ thống không có đủ căn cứ để đưa ra câu trả lời.

Bài toán được cụ thể hoá thành sáu mục tiêu sau:

- **M1.** Tự động phân loại ý định (intent) và trích xuất thực thể (entity) từ tin nhắn khách hàng viết bằng tiếng Việt tự do.

- **M2.** Tự động truy hồi tri thức liên quan từ tài liệu chính sách, câu hỏi thường gặp và thông tin sản phẩm để câu trả lời luôn có căn cứ.

- **M3.** Tự động đánh giá rủi ro và ra quyết định trả lời tự động hay chuyển cho nhân viên, theo một chính sách tất định và kiểm toán được.

- **M4.** Tự động sinh phản hồi cuối cùng cho khách, sau khi qua cổng kiểm soát của quản trị viên.

- **M5.** Cung cấp dashboard giám sát thời gian thực, hàng đợi chuyển tiếp và công cụ duyệt nháp cho quản trị viên.

- **M6.** Bảo đảm tính kiểm soát: nhật ký kiểm toán đầy đủ, human-in-the-loop, cổng cấu hình được, quản lý tri thức.

Về mặt nghiệp vụ, hệ thống đặt mục tiêu tự động xử lý được từ 70% số lượt hội thoại trở lên, với thời gian phản hồi tự động dưới 5 giây.

Toàn bộ thiết kế được xây dựng xung quanh một nguyên tắc xuyên suốt là khi không đủ chắc chắn thì chuyển yêu cầu cho nhân viên. Đây được xác định là hành vi đúng của hệ thống chứ không phải một giới hạn kỹ thuật. Trong ngữ cảnh chăm sóc khách hàng, một hệ thống trả lời được toàn bộ câu hỏi nhưng đưa ra thông tin sai chính sách ở 5% số lượt sẽ gây thiệt hại lớn hơn nhiều so với một hệ thống chỉ trả lời 80% số lượt và chuyển phần còn lại cho nhân viên xử lý.

#### Mục 1.2.2 — Đối tượng sử dụng · Đã rút gọn

*Nằm sau: «Đối tượng sử dụng …»*

Hệ thống được thiết kế với cơ chế phân quyền rõ ràng, phục vụ hai nhóm người dùng thông qua hai giao diện khác nhau trên cùng một ứng dụng web. Việc phân tách này giúp đáp ứng đúng luồng quy trình công việc thực tế của hoạt động chăm sóc khách hàng tại cửa hàng.

- **Khách hàng:** Là người mua hàng của cửa hàng, truy cập cổng chat công khai của hệ thống. Khách hàng có thể đăng nhập để hệ thống tra cứu được đơn hàng của chính mình và xem lại lịch sử hội thoại. Nhu cầu cốt lõi của nhóm này là được trả lời nhanh chóng, chính xác, và trong trường hợp hệ thống không trả lời được thì yêu cầu phải đến được nhân viên thật thay vì bị giữ lại trong các vòng hội thoại tự động.

- **Quản trị viên và nhân viên chăm sóc khách hàng:** Nhóm này bắt buộc phải đăng nhập để sử dụng hệ thống. Nghiệp vụ chính bao gồm theo dõi danh sách hội thoại, tiếp nhận các ca được chuyển tiếp kèm thẻ ngữ cảnh, duyệt hoặc chỉnh sửa nháp phản hồi, trực tiếp trao đổi với khách hàng khi cần thiết, quản lý kho tri thức, bật hoặc tắt các cổng tự động và xem báo cáo hoạt động. Trên thiết bị di động, chính ứng dụng web này được cài đặt lên màn hình chính dưới dạng ứng dụng web tiến bộ (PWA), giúp quản trị viên xử lý nhanh các ca đang chờ ngay cả khi đang di chuyển.

#### Mục 1.2.3 — Phạm vi và giới hạn hệ thống · Đã rút gọn

*Nằm sau: «Phạm vi và giới hạn hệ thống …»*

Để đảm bảo tính khả thi trong quá trình nghiên cứu, thiết kế và triển khai thực nghiệm của một đồ án tốt nghiệp, hệ thống được quy định rõ các phạm vi đáp ứng và những giới hạn cụ thể như sau.

**Phạm vi hệ thống**

Hệ thống tập trung hoàn thiện kiến trúc cốt lõi phục vụ nghiệp vụ chăm sóc khách hàng tự động, bao gồm:

- **Kênh giao tiếp:** Chat văn bản qua nền tảng web, hoạt động theo thời gian thực bằng giao thức WebSocket.

- **Pipeline xử lý:** Bốn tác tử chuyên biệt vận hành theo thứ tự cố định, không sử dụng tác tử điều phối trung tâm.

- **Kho tri thức:** Tài liệu có cấu trúc định dạng Markdown nằm trong repository, được nạp vào cơ sở dữ liệu vector; hệ thống đồng thời hỗ trợ tải lên tài liệu bổ sung qua giao diện quản trị.

- **Tra cứu đơn hàng:** Chỉ tra cứu được trạng thái đơn hàng thuộc tài khoản khách đang đăng nhập, thực hiện trên tập dữ liệu đơn hàng mô phỏng.

- **Cơ chế có người trong vòng lặp:** Triển khai đầy đủ hàng đợi chuyển tiếp kèm phiếu ngữ cảnh, chức năng tiếp quản ca, duyệt nháp phản hồi và cổng cấu hình theo từng ý định.

- **Bảo mật:** Xác thực bằng JWT kết hợp phân quyền theo vai trò, cùng bốn lớp phòng thủ chống tấn công chèn chỉ dẫn (prompt injection).

- **Quan sát và giám sát:** Nhật ký kiểm toán ghi lại từng bước xử lý của các tác tử và tab báo cáo tổng hợp các chỉ số vận hành.

- **Tự động hoá vòng đời hội thoại:** Tự động nhắc và đóng hội thoại khi khách hàng không hoạt động trong một khoảng thời gian cấu hình được.

**Giới hạn của hệ thống**

Do những rào cản nhất định về thời gian nghiên cứu cũng như giới hạn tài nguyên hạ tầng triển khai, hệ thống trong giai đoạn hiện tại chưa tích hợp một số tính năng sau:

- **Bộ nhớ xuyên hội thoại:** Hệ thống chưa có bộ nhớ liên kết giữa các hội thoại khác nhau của cùng một khách hàng; mỗi hội thoại duy trì bộ nhớ riêng biệt.

- **Hồ sơ khách hàng và gợi ý sản phẩm:** Hệ thống chưa xây dựng hồ sơ khách hàng lâu dài cũng như công cụ gợi ý sản phẩm.

- **Mức độ tự trị của kiến trúc đa tác tử:** Hệ thống không vận hành theo mô hình đa tác tử tự trị hoàn toàn. Cần nhấn mạnh rằng đây là một lựa chọn thiết kế có chủ đích nhằm đổi lấy độ tin cậy và khả năng kiểm toán, chứ không phải một giới hạn về mặt kỹ thuật.

- **Thao tác trên đơn hàng:** Hệ thống chỉ thực hiện tra cứu trạng thái đơn hàng, không thực hiện bất kỳ thao tác nào làm thay đổi đơn như huỷ đơn, hoàn tiền hay đổi đơn tự động.

- **Kênh giao tiếp mở rộng:** Hệ thống chưa tích hợp kênh thoại, kênh hình ảnh hay các nền tảng mạng xã hội.

- **Vòng học bán tự động:** Thiết kế đã dự trù sẵn vị trí cho cơ chế này nhưng phần triển khai hoàn chỉnh thuộc về giai đoạn phát triển sau.

#### Mục 1.3.1 — Mô hình ngôn ngữ lớn và ứng dụng trong CSKH · Đã rút gọn

*Nằm sau: «Mô hình ngôn ngữ lớn và ứng dụng trong CSKH …»*

*(Khi biên tập: gắn trích dẫn [1] — Vaswani và cộng sự, "Attention Is All You Need" — ở câu đầu tiên định nghĩa kiến trúc Transformer.)*

Mô hình ngôn ngữ lớn (Large Language Model - LLM) là mô hình mạng nơ-ron theo kiến trúc Transformer, được huấn luyện trên khối lượng văn bản rất lớn với mục tiêu dự đoán token tiếp theo. Nhờ quy mô tham số và dữ liệu huấn luyện, mô hình thu được khả năng khái quát hoá cho phép thực hiện nhiều tác vụ ngôn ngữ khác nhau chỉ bằng cách mô tả tác vụ trong prompt mà không cần huấn luyện lại.

Trong phạm vi đề tài, hai đặc tính của mô hình ngôn ngữ lớn được khai thác trực tiếp:

- **Phân loại zero-shot và few-shot:** Hệ thống có thể mô tả một bộ phân loại ý định bằng cách liệt kê danh sách nhãn kèm mô tả và ví dụ ngay trong prompt. Cách tiếp cận này loại bỏ hoàn toàn nhu cầu gán nhãn và huấn luyện lại, vốn là điểm yếu lớn nhất của nhóm chatbot NLU truyền thống đã phân tích ở mục trên.

- **Sinh văn bản có ràng buộc nguồn:** Hệ thống có thể yêu cầu mô hình chỉ diễn đạt lại thông tin từ các đoạn văn bản được cấp, thay vì trả lời dựa trên tri thức nội tại đã học trong quá trình huấn luyện.

Cần lưu ý rằng đặc tính thứ hai mới chỉ là xu hướng hành vi của mô hình chứ chưa phải một bảo đảm về mặt kỹ thuật. Chính vì vậy, Chương 2 sẽ dành một phần đáng kể để trình bày các cơ chế cưỡng chế bám nguồn được thiết kế cho hệ thống.

Về mặt định dạng đầu ra, đề tài sử dụng chế độ trả về JSON có ràng buộc cho tác vụ phân loại, đồng thời đặt tham số nhiệt độ bằng 0 nhằm bảo đảm kết quả ổn định giữa các lần chạy.

#### Mục 1.3.2 — Sinh có tăng cường truy hồi (RAG) · Đã rút gọn

*Nằm sau: «Sinh có tăng cường truy hồi (RAG) …»*

*(Khi biên tập: gắn trích dẫn [2] — Lewis và cộng sự — ở câu đầu tiên định nghĩa RAG.)*

Sinh có tăng cường truy hồi (Retrieval-Augmented Generation - RAG) là kỹ thuật ghép thêm một bước truy hồi thông tin vào trước bước sinh văn bản. Thay vì để mô hình trả lời dựa trên tri thức đã học, hệ thống tìm các đoạn tài liệu liên quan nhất với câu hỏi rồi đưa chúng vào prompt để làm căn cứ cho câu trả lời.

Quy trình RAG được chia thành hai pha chính:

- **Pha nạp (ingestion):** Tài liệu được tách thành các đoạn nhỏ, mỗi đoạn được chuyển thành vector số thực thông qua mô hình embedding, sau đó lưu vào cơ sở dữ liệu vector kèm theo siêu dữ liệu mô tả.

- **Pha truy hồi (retrieval):** Câu hỏi của người dùng cũng được chuyển thành vector, hệ thống tìm k vector gần nhất theo một độ đo tương tự (thường là độ đo cosine), rồi đưa các đoạn tài liệu tương ứng vào prompt.

Dưới đây là sơ đồ mô tả hai pha của kỹ thuật sinh có tăng cường truy hồi (Hình 1.6).

Hình 1.6. Hai pha của kỹ thuật sinh có tăng cường truy hồi

Khi áp dụng vào bài toán chăm sóc khách hàng, kỹ thuật RAG đặt ra ba vấn đề kỹ thuật mà đề tài phải giải quyết trực tiếp:

- **Chiến lược chia đoạn:** Cắt tài liệu theo số ký tự cố định là cách làm đơn giản nhất nhưng lại phá vỡ cấu trúc nội dung, chẳng hạn một bảng kích cỡ bị cắt làm đôi hoặc một quy trình xử lý bị mất các bước phía sau. Vì vậy, đề tài lựa chọn phương án chia theo từng mục của tài liệu Markdown.

- **Khoảng cách giọng văn:** Khách hàng đặt câu hỏi bằng giọng nói thường ngày, trong khi tài liệu chính sách của cửa hàng được viết bằng giọng văn bản trang trọng. Vector biểu diễn của hai dạng diễn đạt này có thể cách nhau khá xa dù cùng đề cập tới một nội dung.

- **Ngưỡng quyết định:** Hệ thống cần một ngưỡng để phân biệt giữa trường hợp tìm được tri thức đủ liên quan với trường hợp không tìm được nội dung phù hợp. Ngưỡng này không thể lựa chọn theo cảm tính mà phải được đo đạc trực tiếp trên chính kho tri thức thật của cửa hàng.

#### Mục 1.3.3 — Kiến trúc đa tác tử và LangGraph · Đã rút gọn

*Nằm sau: «Kiến trúc đa tác tử và LangGraph …»*

*(Khi biên tập: gắn trích dẫn [4] — tài liệu LangGraph — ở đoạn giới thiệu năm khái niệm state/node/edge/reducer/checkpointer.)*

Kiến trúc đa tác tử (multi-agent) chia một tác vụ phức tạp thành nhiều tác tử chuyên biệt, trong đó mỗi tác tử có prompt, công cụ và trách nhiệm riêng, trao đổi với nhau thông qua một trạng thái dùng chung. So với phương án sử dụng một lời gọi mô hình duy nhất để xử lý toàn bộ công việc, cách phân chia này cho phép từng bước được tối ưu, kiểm thử và quan sát một cách độc lập.

Về cơ chế điều phối giữa các tác tử, hiện có hai trường phái chính:

- **Điều phối động (có Supervisor):** Một tác tử trung tâm quyết định luồng chạy ngay tại thời điểm hệ thống vận hành.

- **Điều phối tĩnh (pipeline cố định):** Thứ tự xử lý được định nghĩa trước dưới dạng đồ thị, còn các điểm rẽ nhánh cũng được định trước trong mã tất định chứ không do tác tử lựa chọn tại thời điểm chạy; các tác tử chỉ quyết định nội dung xử lý chứ không quyết định luồng đi.

Dưới đây là sơ đồ so sánh hai trường phái điều phối nêu trên (Hình 1.7).

Hình 1.7. So sánh điều phối động có Supervisor và điều phối tĩnh theo pipeline cố định

Đề tài lựa chọn trường phái điều phối tĩnh. Đây là một sự đánh đổi có chủ đích, trong đó hệ thống hy sinh tính linh hoạt ở tầng điều phối để đổi lấy độ tin cậy, khả năng kiểm toán và một trần chi phí xác định cho mỗi lượt xử lý.

Về công cụ hiện thực, LangGraph là thư viện cho phép xây dựng ứng dụng mô hình ngôn ngữ lớn dưới dạng đồ thị có trạng thái. Các khái niệm nền tảng của thư viện được đề tài sử dụng gồm:

- **Trạng thái (State):** Một cấu trúc dữ liệu, ở đây là kiểu TypedDict, chứa toàn bộ thông tin của một lượt xử lý.

- **Nút (Node):** Một hàm nhận trạng thái vào và trả về phần trạng thái cần cập nhật.

- **Cạnh (Edge):** Cạnh nối giữa các nút, có nhiệm vụ định nghĩa thứ tự chạy của đồ thị.

- **Hàm gộp trạng thái (Reducer):** Quy tắc gộp giá trị khi nhiều nút cùng ghi vào một trường dữ liệu. Đề tài sử dụng hàm gộp theo kiểu cộng dồn cho danh sách cờ bất định và nhật ký trace, nhờ đó mỗi nút chỉ cần trả về phần dữ liệu mới do chính nó sinh ra mà hệ thống vẫn quy được từng cờ về đúng tác tử đã phát ra nó.

- **Cơ chế lưu điểm kiểm tra (Checkpointer):** Cơ chế lưu trạng thái của đồ thị nhằm phục vụ việc dừng và chạy tiếp quá trình xử lý.

#### Mục 1.3.4 — Grounding và vấn đề ảo giác · Đã rút gọn

*Nằm sau: «Grounding và vấn đề ảo giác …»*

*(Khi biên tập: gắn trích dẫn [3] — Ji và cộng sự, khảo sát về ảo giác — ở câu định nghĩa ảo giác.)*

Ảo giác (hallucination) là hiện tượng mô hình sinh ra thông tin không có căn cứ trong nguồn được cấp, với độ trôi chảy và mức độ tự tin không khác gì thông tin đúng. Ngược lại, bám nguồn (grounding) là tập hợp các kỹ thuật buộc câu trả lời của mô hình phải dựa trên nguồn dữ liệu đã được kiểm soát.

Trên cơ sở quan sát hành vi thực tế của hệ thống, đề tài phân biệt ba dạng ảo giác, mỗi dạng đòi hỏi một cơ chế phòng chống riêng. Dưới đây là sơ đồ phân loại ba dạng ảo giác trong ngữ cảnh chăm sóc khách hàng cùng cơ chế chống tương ứng (Hình 1.8).

Hình 1.8. Ba dạng ảo giác trong ngữ cảnh chăm sóc khách hàng và cơ chế chống tương ứng

**a) Bịa ra thông tin không tồn tại (positive hallucination).** Mô hình đưa ra một chính sách, một con số hay một mã giảm giá không hề tồn tại. Đây là dạng ảo giác được nhận diện phổ biến nhất trong các tài liệu nghiên cứu. Cơ chế phòng chống là chỉ cấp cho mô hình các nguồn đã được kiểm soát và cấm sử dụng tri thức nằm ngoài nguồn.

**b) Suy diễn ra sự phủ định từ chỗ nguồn im lặng (negative hallucination).** Đây là dạng tinh vi hơn và ít được chú ý. Khi kho tri thức không đề cập tới một nội dung nào đó, mô hình có xu hướng diễn giải sự im lặng này thành một sự phủ định. Chẳng hạn, tài liệu không nhắc tới việc giao hàng quốc tế, mô hình lại trả lời rằng cửa hàng chưa hỗ trợ giao hàng đi nước ngoài. Xét về mặt logic, đây cũng là hành vi bịa ra một chính sách, chỉ khác ở chiều khẳng định. Cơ chế phòng chống gồm quy tắc tường minh trong prompt phân biệt giữa việc chưa có thông tin về một nội dung với việc nội dung đó không tồn tại, kết hợp với quy tắc coi mọi danh sách trong nguồn là danh sách mở, trừ khi nguồn có dùng các từ giới hạn như "chỉ" hoặc "duy nhất".

**c) Bịa ra hành động (action hallucination).** Mô hình khẳng định đã thực hiện một thao tác mà hệ thống không hề có khả năng thực hiện, chẳng hạn khẳng định đã hoàn tiền hoặc đang kết nối nhân viên hỗ trợ. Đây là dạng nguy hiểm nhất vì nó tạo ra cam kết giả với khách hàng. Cơ chế phòng chống bao gồm việc giới hạn hành động một cách tường minh trong prompt, kết hợp với một bất biến ở cấp độ kiến trúc: tác tử sinh phản hồi không có quyền tự chuyển ca cho nhân viên, do đó mọi lời hứa chuyển tiếp mà tác tử này tự đưa ra đều không phản ánh đúng sự thật và bị cấm tuyệt đối.

Bên cạnh ba cơ chế nêu trên, đề tài còn áp dụng thêm một cơ chế chặn cứng ở cấp độ kiến trúc. Khi không truy hồi được bất kỳ nguồn tri thức nào, hệ thống sẽ không gọi mô hình để sinh câu trả lời. Việc loại bỏ hoàn toàn lời gọi mô hình trong tình huống này bảo đảm không thể phát sinh nội dung bịa đặt.

#### Mục 1.3.5 — Human-in-the-loop và nguyên tắc tự trị có giới hạn · Đã rút gọn

*Nằm sau: «Human-in-the-loop và nguyên tắc tự trị có giới hạn …»*

Có người trong vòng lặp (Human-in-the-loop - HITL) là mô hình vận hành trong đó hệ thống tự động xử lý phần lớn công việc nhưng vẫn dành lại những điểm quyết định quan trọng cho con người. Trong phạm vi đề tài, mô hình này được thể hiện ở ba mức độ, tạo thành một thang phản hồi phân cấp như sau:

- **Gửi thẳng:** Hệ thống đủ tự tin, câu trả lời có căn cứ rõ ràng và ý định của khách thuộc nhóm được phép trả lời tự động. Trong trường hợp này, câu trả lời được gửi thẳng tới khách hàng.

- **Duyệt nháp:** Hệ thống đủ tự tin và câu trả lời có căn cứ, nhưng ý định lại thuộc nhóm nhạy cảm như hoàn tiền, đổi hàng hoặc khiếu nại. Câu trả lời được soạn sẵn dưới dạng nháp và chỉ được gửi đi sau khi quản trị viên duyệt hoặc chỉnh sửa.

- **Chuyển cho nhân viên:** Hệ thống gặp giới hạn xử lý, chẳng hạn không truy hồi được tri thức, câu hỏi nằm ngoài phạm vi hoặc khách hàng chủ động yêu cầu gặp người thật. Khi đó, ca được đưa vào hàng đợi kèm thẻ ngữ cảnh và quản trị viên tiếp nhận xử lý từ đầu.

Dưới đây là sơ đồ thang phản hồi phân cấp ba mức cùng ranh giới giữa cơ chế an toàn và phần cấu hình (Hình 1.9).

Hình 1.9. Thang phản hồi phân cấp ba mức và ranh giới giữa an toàn với cấu hình

Điểm cần nhấn mạnh là ranh giới giữa cơ chế an toàn và phần cấu hình của con người. Mức thứ ba do cơ chế an toàn của hệ thống quyết định và không bao giờ bị cấu hình ghi đè. Cổng cấu hình chỉ can thiệp được vào ranh giới giữa mức thứ nhất và mức thứ hai.

#### Mục 1.4.1 — Yêu cầu chức năng · Đã rút gọn

*Nằm sau: «Yêu cầu chức năng …»*

Dưới đây là bảng tổng hợp các yêu cầu chức năng của hệ thống, gom theo bảy nhóm gồm pipeline tác tử, tri thức, cổng cấu hình, có người trong vòng lặp, xử lý bất đồng bộ, chức năng quản trị và chức năng dành cho khách hàng (Bảng 1.2).

#### Mục 1.4.1 — Yêu cầu chức năng · Đã rút gọn

*Nằm sau: «Bảng 1.2. Yêu cầu chức năng của hệ thống …»*

| **Mã**     | **Nhóm**    | **Mô tả**                                                                                                 |
|------------|-------------|-----------------------------------------------------------------------------------------------------------|
| FR-PIPE-1  | Pipeline    | Mỗi hội thoại có state độc lập; nhiều hội thoại xử lý song song                                           |
| FR-PIPE-2  | Pipeline    | Thứ tự tác tử cố định intent → knowledge → decision → response                                            |
| FR-PIPE-3  | Pipeline    | Mỗi tác tử ghi độ tin cậy và cờ bất định vào state; định tuyến dựa trên đó                                |
| FR-PIPE-4  | Pipeline    | Mọi bước tác tử được ghi vào nhật ký kiểm toán                                                            |
| FR-PIPE-5  | Pipeline    | Phản hồi tự động phải có căn cứ; thiếu căn cứ → chuyển người, không bịa                                   |
| FR-RAG-1   | Tri thức    | Nạp tài liệu → chia đoạn → embedding → lưu vector database                                                |
| FR-RAG-2   | Tri thức    | Truy hồi theo ý định; trả về các đoạn kèm điểm truy hồi                                                   |
| FR-RAG-3   | Tri thức    | Nạp lại, quản lý siêu dữ liệu, xoá tài liệu                                                               |
| FR-GATE-1  | Cổng        | Cổng là cấu hình của quản trị viên, lưu trong CSDL, đặt được theo từng ý định                             |
| FR-GATE-2  | Cổng        | Bất biến: cổng chỉ can thiệp ca auto_reply; ca chuyển người không chịu ảnh hưởng                          |
| FR-GATE-3  | Cổng        | Mặc định bật tự trả lời, nhưng tắt cho nhóm nhạy cảm                                                      |
| FR-ESC-1   | HITL        | Mọi ca chuyển người phải kèm EscalationCard                                                               |
| FR-ESC-4   | HITL        | Quản trị viên nhận ca → chat trực tiếp → đóng ca; duyệt hoặc sửa nháp                                     |
| FR-ESC-5   | HITL        | Mọi hành động của quản trị viên được ghi nhật ký                                                          |
| FR-ASYNC-1 | Bất đồng bộ | Mỗi tin nhắn chạy pipeline đồng bộ, mục tiêu P95 ≤ 5 giây                                                 |
| FR-ASYNC-2 | Bất đồng bộ | Lượt làm rõ: thiếu thông tin → hỏi lại tối đa một lần                                                     |
| FR-ASYNC-3 | Bất đồng bộ | Chuyển người = tạm dừng AI cho hội thoại đó                                                               |
| FR-ASYNC-4 | Bất đồng bộ | Ngoài giờ hỗ trợ: giữ ca trong hàng đợi, không tự đóng                                                    |
| FR-ASYNC-7 | Bất đồng bộ | Realtime bằng WebSocket, không polling                                                                    |
| FR-ADMIN-  | Quản trị    | Danh sách hội thoại + lọc; chat trực tiếp; hàng đợi; duyệt nháp; quản lý tri thức; cấu hình cổng; báo cáo |
| FR-CUST-   | Khách hàng  | Tạo hội thoại; nhận phản hồi thời gian thực; xem lịch sử của mình                                         |

#### Mục 1.4.3 — Các chỉ số đánh giá (KPI) · Đã rút gọn

*Nằm sau: «Các chỉ số đánh giá (KPI) …»*

Dưới đây là bảng các chỉ số dùng để đánh giá hệ thống cùng mục tiêu đặt ra cho từng chỉ số; kết quả đo thực tế đối chiếu với các mục tiêu này được trình bày ở mục 3.5.7 (Bảng 1.4).

#### Mục 1.5 — Công nghệ và các công cụ sử dụng · Đã rút gọn

*Nằm sau: «Công nghệ và các công cụ sử dụng …»*

Để hiện thực hoá các yêu cầu chức năng và đảm bảo các tiêu chuẩn khắt khe đã đặt ra ở mục 1.4, bộ công nghệ của hệ thống được lựa chọn dựa trên ba ràng buộc cốt lõi: độ trễ ở phân vị 95 phải dưới 5 giây (NFR-1), chi phí vận hành nằm trong gói miễn phí của các dịch vụ managed (NFR-9), và mọi tham số vận hành phải cấu hình được mà không cần sửa mã nguồn (NFR-10).

Nguyên tắc chung trong quá trình lựa chọn là ưu tiên những công cụ đã cung cấp sẵn cơ chế cần dùng thay vì tự xây dựng. Lý do là mỗi thành phần tự viết đều kéo theo khối lượng công việc kiểm thử và bảo trì tương ứng, trong khi đồ án chỉ do một người thực hiện trong thời gian có hạn. Phần dưới đây trình bày từng nhóm công nghệ kèm mô tả và lý do lựa chọn tương ứng với các ràng buộc nêu trên.

#### Mục 1.5.1 — Backend · Đã rút gọn

*Nằm sau: «Backend …»*

- **Ngôn ngữ và framework:** Python 3.12 và FastAPI 0.115

  Hệ thống sử dụng Python 3.12 kết hợp với FastAPI phiên bản 0.115, đều là những phiên bản ổn định và tương thích tốt với nhau [8] (Hình 1.10).

Hình 1.10. Logo Python và FastAPI

- **Mô tả:**

  - **Python 3.12:** Là ngôn ngữ thông dịch, định kiểu động nhưng có hỗ trợ chú thích kiểu tĩnh, hiện được sử dụng rộng rãi trong lĩnh vực trí tuệ nhân tạo. Việc lựa chọn Python cho đồ án này mang tính thực tiễn, bởi phần lớn thư viện điều phối tác tử và bộ thư viện khách của các nhà cung cấp mô hình ngôn ngữ đều được phát triển trước tiên trên Python rồi mới chuyển sang các ngôn ngữ khác. Phiên bản 3.12 cải thiện đáng kể chất lượng thông báo lỗi và tốc độ khởi động, đồng thời hỗ trợ đầy đủ cú pháp chú thích kiểu hiện đại mà dự án sử dụng xuyên suốt.

  - **FastAPI 0.115:** Là framework web bất đồng bộ được xây dựng trên nền Starlette và Pydantic. FastAPI hỗ trợ sẵn giao thức WebSocket, vốn là thành phần bắt buộc của đề tài do hệ thống phải đẩy tin nhắn tới khách hàng và quản trị viên theo hướng sự kiện thay vì hỏi vòng theo chu kỳ. Bên cạnh đó, framework này tự sinh tài liệu OpenAPI từ khai báo kiểu, nhờ vậy các endpoint REST luôn có tài liệu khớp với mã nguồn mà không cần biên soạn thủ công.

- **Lợi ích và lý do lựa chọn:**

  - **Mô hình bất đồng bộ phù hợp với bản chất tải của hệ thống:** Một lượt xử lý của hệ thống bao gồm nhiều thao tác chờ nhập xuất nối tiếp nhau, lần lượt là gọi mô hình phân loại ý định, gọi mô hình embedding, truy vấn cơ sở dữ liệu vector, truy vấn cơ sở dữ liệu quan hệ và cuối cùng là gọi mô hình sinh phản hồi. Trong toàn bộ thời gian chờ này, tiến trình gần như không tiêu tốn tài nguyên vi xử lý. Do toàn bộ phần back-end được viết theo phong cách bất đồng bộ, hàng trăm hội thoại có thể chạy xen kẽ trên một tiến trình duy nhất, đáp ứng mục tiêu phục vụ ít nhất 100 người dùng đồng thời mà không cần triển khai nhiều tiến trình.

  - **Kiểm tra kiểu dữ liệu ngay tại biên hệ thống:** FastAPI sử dụng Pydantic để xác thực dữ liệu ngay tại điểm vào của mỗi endpoint. Dữ liệu sai kiểu bị chặn lại ở biên hệ thống kèm thông báo rõ ràng, thay vì đi sâu vào bên trong rồi gây lỗi tại một vị trí không liên quan. Đối với một hệ thống có pipeline nhiều bước như đồ án này, việc chặn sớm giúp thu hẹp đáng kể phạm vi cần rà soát trong quá trình gỡ lỗi.

  - **Hỗ trợ WebSocket ngay trong lõi framework:** Nhiều framework hiện nay coi WebSocket là một phần mở rộng phải cài đặt thêm. Ngược lại, FastAPI hỗ trợ giao thức này ngay trong lõi, cho phép một ứng dụng phục vụ đồng thời ba kênh WebSocket cùng các endpoint REST trên một tiến trình duy nhất, dùng chung cơ chế xác thực và cùng một vòng lặp sự kiện.

- **Thư viện điều phối tác tử:** LangGraph 0.2

  LangGraph là thư viện điều phối tác tử theo mô hình đồ thị, thuộc hệ sinh thái LangChain [4] (Hình 1.11).

Hình 1.11. Logo LangGraph

  - **Mô tả:** LangGraph mô hình hoá một quy trình xử lý thành đồ thị gồm các nút và các cạnh, trong đó mỗi nút là một hàm nhận trạng thái vào và trả về phần trạng thái cần cập nhật. Thư viện cung cấp sẵn năm khái niệm nền: trạng thái dùng chung, nút, cạnh, hàm gộp trạng thái và cơ chế lưu điểm kiểm tra.

  - **Lý do lựa chọn:** Khác với phần lớn framework đa tác tử hiện đang hướng tới điều phối động, LangGraph cho phép định nghĩa một đồ thị tĩnh với các cạnh cố định, phù hợp với triết lý thiết kế của đề tài đã trình bày ở mục 1.3.3. Bên cạnh đó, việc sử dụng thư viện có sẵn thay vì tự xây dựng giúp đề tài tránh phải cài đặt lại cơ chế gộp trạng thái và cơ chế dừng rồi chạy tiếp, vốn là hai thành phần dễ phát sinh sai sót và tốn nhiều công sức kiểm thử.

- **Truy cập cơ sở dữ liệu:** SQLAlchemy 2.0 (chế độ bất đồng bộ) và Alembic 1.13

  SQLAlchemy là thư viện ánh xạ đối tượng – quan hệ phổ biến nhất của hệ sinh thái Python, Alembic là công cụ quản lý phiên bản lược đồ đi kèm [9] (Hình 1.12).

Hình 1.12. Logo SQLAlchemy và Alembic

  - **Mô tả:** SQLAlchemy 2.0 cho phép khai báo bảng dưới dạng lớp Python có chú thích kiểu, đồng thời hỗ trợ chế độ bất đồng bộ thông qua trình điều khiển `asyncpg`. Đây là điều kiện cần để toàn bộ phần back-end giữ được phong cách lập trình bất đồng bộ. Alembic đảm nhiệm việc sinh và áp dụng các tệp migration, trong đó mỗi tệp mô tả một bước thay đổi lược đồ có thể áp dụng theo cả chiều tiến và chiều lùi.

  - **Lý do lựa chọn:** Hệ thống cần ghi trạng thái hội thoại, tin nhắn phản hồi và phiếu chuyển tiếp trong cùng một giao dịch, trong khi SQLAlchemy cho phép kiểm soát ranh giới giao dịch một cách tường minh thay vì để framework tự quyết định. Đối với Alembic, việc phiên bản hoá lược đồ cơ sở dữ liệu là yêu cầu bắt buộc với một dự án vận hành trên dịch vụ managed, bởi việc sửa cấu trúc bảng thủ công không bảo đảm được tính đồng nhất giữa môi trường phát triển và môi trường chạy thật.

- **Xác thực dữ liệu và cấu hình:** Pydantic 2.9 và pydantic-settings 2.5

  Dưới đây là hình ảnh logo của Pydantic (Hình 1.13).

Hình 1.13. Logo Pydantic

  - **Mô tả:** Pydantic thực hiện xác thực dữ liệu dựa trên chú thích kiểu, được sử dụng cho toàn bộ schema của các endpoint REST cũng như cho định dạng dữ liệu trả về của mô hình ngôn ngữ. Thư viện `pydantic-settings` đảm nhiệm việc đọc cấu hình từ biến môi trường và xác thực ngay tại thời điểm khởi động ứng dụng.

  - **Lý do lựa chọn:** Đây là cách hiện thực hoá trực tiếp yêu cầu NFR-10. Nguyên tắc xuyên suốt của đồ án là không viết cứng khoá bí mật, địa chỉ dịch vụ hay các ngưỡng số trong mã nguồn; mọi giá trị thuộc nhóm này đều được khai báo trong một lớp cấu hình duy nhất và đọc từ biến môi trường. Nhờ cơ chế xác thực ngay lúc khởi động của Pydantic, một biến bị thiếu hoặc sai kiểu sẽ khiến ứng dụng dừng lại ngay kèm thông báo rõ ràng, thay vì khởi động thành công rồi phát sinh sự cố giữa chừng khi đang phục vụ khách hàng.

- **Quản lý gói và môi trường ảo:** uv

  - uv là trình quản lý gói Python thế hệ mới, thay thế cho cặp công cụ pip và venv truyền thống. Tốc độ cài đặt của công cụ này nhanh hơn đáng kể nhờ được viết bằng ngôn ngữ Rust và nhờ cơ chế khoá phiên bản chặt chẽ. Với một dự án có nhiều phụ thuộc như đồ án này, việc dựng lại toàn bộ môi trường từ đầu chỉ mất vài giây thay vì vài phút, mang lại ý nghĩa thực tế rõ rệt mỗi khi cần chạy lại bộ kiểm thử trên môi trường sạch.

- **Các thư viện bổ sung:**

  - **bcrypt (từ phiên bản 4.1):** Thuật toán băm mật khẩu có yếu tố làm chậm cố ý nhằm chống tấn công dò tìm. Thư viện được sử dụng trực tiếp thay vì thông qua lớp bọc trung gian, nhằm tránh phụ thuộc vào các thư viện đã ngừng bảo trì.

  - **PyJWT 2.9:** Đảm nhiệm việc sinh và xác minh mã thông báo truy cập cùng mã thông báo làm mới, phục vụ cơ chế xác thực được trình bày chi tiết ở mục 2.9.1.

  - **python-frontmatter, pypdf và python-docx:** Đọc siêu dữ liệu của tài liệu tri thức viết bằng Markdown và trích xuất văn bản từ các tài liệu PDF, Word do quản trị viên tải lên.

#### Mục 1.5.2 — Mô hình ngôn ngữ và embedding · Đã rút gọn

*Nằm sau: «Mô hình ngôn ngữ và embedding …»*

- **Nhà cung cấp và mô hình:** OpenAI, gồm hai mô hình `gpt-4o-mini` và `text-embedding-3-small`

  Hệ thống sử dụng hai mô hình của OpenAI thông qua bộ thư viện khách chính thức phiên bản 1.40 (Hình 1.14).

Hình 1.14. Logo OpenAI

- **Mô tả:**

  - **`gpt-4o-mini`:** Là mô hình sinh cỡ nhỏ, đảm nhiệm hai lời gọi trong mỗi lượt xử lý, gồm phân loại ý định tại tác tử thứ nhất và sinh phản hồi tại tác tử thứ tư. Cả hai lời gọi đều đặt tham số nhiệt độ bằng 0 nhằm bảo đảm kết quả ổn định giữa các lần chạy. Riêng lời gọi phân loại sử dụng chế độ trả về JSON có cấu trúc [6], nhờ đó đầu ra của mô hình được xác thực bằng schema thay vì phải dò tìm theo chuỗi ký tự.

  - **`text-embedding-3-small`:** Là mô hình vector hoá, sinh ra vector 1536 chiều cho các đoạn tri thức cũng như cho câu hỏi của khách hàng [5]. Vector của kho tri thức được tính một lần duy nhất tại thời điểm nạp và lưu trữ trên Qdrant, trong khi vector của câu hỏi được tính lại ở mỗi lượt xử lý.

- **Lợi ích và lý do lựa chọn:**

  - **Việc lựa chọn mô hình cỡ nhỏ là một quyết định có chủ đích:** Với ràng buộc độ trễ ở phân vị 95 phải dưới 5 giây cùng ràng buộc về chi phí vận hành, một mô hình cỡ lớn không phải là phương án phù hợp. Quan trọng hơn, phần lớn độ khó của bài toán đã được chuyển từ mô hình sang tầng kiến trúc. Cụ thể, bảng phân loại mười lăm ý định nằm sẵn trong prompt nên mô hình chỉ cần lựa chọn nhãn phù hợp; tri thức đã được truy hồi sẵn và đưa vào prompt nên mô hình không cần ghi nhớ nội dung chính sách; các quyết định an toàn do mã tất định đảm nhiệm nên mô hình không phải thực hiện phán đoán. Khi ba phần việc phức tạp nhất đã được các thành phần khác đảm nhiệm, năng lực của một mô hình cỡ nhỏ là đủ đáp ứng yêu cầu.

  - **Đầu ra có cấu trúc thay vì văn bản tự do:** Chế độ trả về JSON có cấu trúc loại bỏ hoàn toàn một lớp lỗi thường gặp, đó là trường hợp mô hình trả về đúng nội dung nhưng sai định dạng khiến chương trình không đọc được kết quả. Đây cũng chính là điều kiện cần để tác tử thứ ba có thể định tuyến dựa trên tập cờ một cách tất định.

  - **Khả năng cấu hình và giới hạn thời gian chờ:** Cả hai mô hình đều được khai báo qua biến môi trường, kèm theo thiết lập tường minh về thời gian chờ và số lần thử lại. Mục 3.5.5 sẽ trình bày một sự cố thực tế liên quan tới việc bộ thư viện khách mặc định chờ tới 600 giây và thử lại ba lần, đủ để giữ một lượt hội thoại của khách hàng trong gần nửa giờ nếu không thiết lập lại các tham số này.

#### Mục 1.5.3 — Lưu trữ và hạ tầng · Đã rút gọn

*Nằm sau: «Lưu trữ và hạ tầng …»*

Hệ thống áp dụng kiến trúc lưu trữ đa dạng với ba dịch vụ lưu trữ và quan sát, trong đó mỗi dịch vụ phụ trách một loại dữ liệu có bản chất khác nhau. Cả ba đều sử dụng bản managed để không phải tự vận hành máy chủ, phù hợp với phạm vi một người thực hiện của đồ án.

- **Cơ sở dữ liệu quan hệ:** PostgreSQL, sử dụng bản managed của Neon

  Dưới đây là hình ảnh logo của PostgreSQL và Neon (Hình 1.15).

Hình 1.15. Logo PostgreSQL và Neon

  - **Mô tả:** PostgreSQL lưu giữ toàn bộ dữ liệu nghiệp vụ của hệ thống, bao gồm tài khoản, hội thoại, tin nhắn, đơn hàng, cấu hình cổng, sổ tài liệu tri thức và nhật ký kiểm toán. Neon là dịch vụ PostgreSQL không máy chủ, tách biệt tầng tính toán với tầng lưu trữ và cung cấp gói miễn phí đủ đáp ứng quy mô của đồ án.

  - **Lý do lựa chọn:** Ba đặc tính của PostgreSQL gắn trực tiếp với thiết kế của hệ thống. Thứ nhất là cơ chế giao dịch ACID. Một lượt xử lý phải ghi đồng thời trạng thái hội thoại, tin nhắn phản hồi và phiếu chuyển tiếp; nếu các thao tác này tách rời nhau, hệ thống có thể rơi vào tình trạng đã thông báo cho khách hàng nhưng chưa ghi xong dữ liệu, như phân tích ở mục 2.5.3. Thứ hai là kiểu dữ liệu JSONB. Phiếu chuyển tiếp có cấu trúc lồng nhau và còn tiếp tục thay đổi theo tiến độ phát triển, nên việc lưu dưới dạng JSONB thuận tiện hơn so với tách thành nhiều bảng phụ mà vẫn truy vấn được bằng SQL. Thứ ba là khả năng cập nhật có điều kiện kèm trả về số dòng bị ảnh hưởng, đây chính là nền tảng cho cơ chế so sánh rồi ghi nhằm chống tranh chấp đồng thời.

- **Cơ sở dữ liệu vector:** Qdrant Cloud

  Dưới đây là hình ảnh logo của Qdrant (Hình 1.16).

Hình 1.16. Logo Qdrant

  - **Mô tả:** Qdrant là cơ sở dữ liệu vector chuyên dụng được viết bằng ngôn ngữ Rust [7]. Kho tri thức sau khi chia đoạn sẽ được vector hoá rồi lưu vào hệ thống này. Ở mỗi lượt khách hàng đặt câu hỏi, hệ thống tìm các đoạn tri thức gần nhất theo độ đo cosine. Ngoài vector, mỗi điểm còn mang theo một payload chứa các siêu dữ liệu như nguồn tài liệu, loại tài liệu và nhãn ý định tương ứng.

  - **Lý do lựa chọn:**

    - **Cơ chế alias cho collection:** Qdrant cho phép trỏ một tên logic vào một collection vật lý và thay đổi hướng trỏ chỉ bằng một lời gọi duy nhất. Đây là điều kiện cần để nạp lại kho tri thức mà không gây gián đoạn dịch vụ như trình bày ở mục 2.6.4. Nếu thiếu cơ chế này, toàn bộ lượt hội thoại của khách hàng trong thời gian nạp lại đều sẽ bị chuyển cho nhân viên.

    - **Khả năng lọc theo payload ngay trong truy vấn vector:** Hệ thống cần loại bỏ các đoạn thuộc tài liệu nội bộ và phân biệt tài liệu chính thức với tài liệu tải lên tạm thời. Vì vậy, thao tác lọc phải được thực hiện đồng thời với thao tác tìm kiếm chứ không phải lọc lại sau khi đã lấy kết quả về.

    - **Gói miễn phí đủ đáp ứng** quy mô kho tri thức của đề tài, phù hợp với ràng buộc chi phí NFR-9. Điều phải đánh đổi là hiện tượng khởi động nguội của dịch vụ, cũng là một trong hai nguyên nhân gây ra đuôi phân bố độ trễ được phân tích ở mục 3.5.6.

- **Quan sát lời gọi mô hình:** Langfuse

  Dưới đây là hình ảnh logo của Langfuse (Hình 1.17).

Hình 1.17. Logo Langfuse

  - **Mô tả:** Langfuse là nền tảng quan sát dành riêng cho các ứng dụng mô hình ngôn ngữ [14], có khả năng ghi lại từng lời gọi kèm theo prompt, số token tiêu thụ và chi phí tương ứng. Khác với nhật ký văn bản thông thường, Langfuse gom toàn bộ các lời gọi trong cùng một lượt xử lý thành một trace có cấu trúc dạng cây.

  - **Lý do lựa chọn:** Công cụ này trả lời được những câu hỏi mà nhật ký văn bản thông thường không đáp ứng được, cụ thể là chi phí của từng lượt xử lý và bước nào trong lượt gây ra độ trễ lớn nhất. Điểm đáng lưu ý về cách tích hợp là Langfuse được kết nối theo kiểu tuỳ chọn: khi không cấu hình khoá, lớp quan sát tự động vô hiệu hoá và hệ thống vẫn vận hành bình thường, đúng theo nguyên tắc suy giảm an toàn tại mọi điểm gọi dịch vụ ngoài đã trình bày ở mục 3.3.9. Nguyên tắc này bảo đảm một công cụ giám sát không thể trở thành nguyên nhân gây gián đoạn chính hệ thống mà nó giám sát.

Dưới đây là bảng tổng hợp ba dịch vụ hạ tầng nêu trên cùng công nghệ và vai trò của từng dịch vụ trong hệ thống (Bảng 1.5).

Bảng 1.5. Hạ tầng sử dụng

| **Thành phần** | **Công nghệ** | **Vai trò** |
|----------------|---------------|-------------|
| CSDL quan hệ | PostgreSQL (Neon, managed) | Hội thoại, tin nhắn, đơn hàng, tài khoản, cấu hình cổng, nhật ký kiểm toán |
| Vector database | Qdrant Cloud (độ đo cosine) | Lưu embedding các đoạn tri thức |
| Quan sát LLM | Langfuse | Trace lời gọi mô hình, token, chi phí; hoạt động theo kiểu suy giảm an toàn (không cấu hình thì vô hiệu, không gây lỗi) |

Cả ba dịch vụ đều dùng gói miễn phí của nhà cung cấp managed, phù hợp ràng buộc chi phí NFR-9.

#### Mục 1.5.4 — Frontend · Đã rút gọn

*Nằm sau: «Frontend …»*

- **Ngôn ngữ và framework:** TypeScript, React 18 và Next.js 14 (App Router)

  Toàn bộ phần giao diện được xây dựng thành một ứng dụng Next.js duy nhất đảm nhiệm hai vai trò, gồm cổng chat dành cho khách hàng tại đường dẫn `/chat` và bảng điều khiển quản trị tại đường dẫn `/admin` [10] (Hình 1.18).

Hình 1.18. Logo Next.js và React

- **Mô tả:**

  - **React 18:** Thư viện xây dựng giao diện người dùng theo mô hình thành phần. Cơ chế cập nhật theo lô của phiên bản 18 mang lại ý nghĩa thực tế rõ rệt với đồ án này. Khi một hội thoại đang mở nhận liên tiếp nhiều sự kiện thời gian thực, giao diện chỉ dựng lại một lần duy nhất thay vì dựng lại theo từng sự kiện.

  - **Next.js 14 với App Router:** Framework xây dựng trên nền React, cung cấp cơ chế định tuyến theo cấu trúc thư mục, kết xuất phía máy chủ và công cụ đóng gói tích hợp sẵn. App Router cho phép phân tách rõ ràng phần giao diện của khách hàng với phần giao diện quản trị trong cùng một dự án mà vẫn dùng chung các thành phần và kiểu dữ liệu.

  - **TypeScript:** Cung cấp kiểu dữ liệu tĩnh cho toàn bộ phần giao diện. Các kiểu dùng chung với back-end, đặc biệt là tập trạng thái hội thoại, được khai báo trong một package riêng. Nhờ đó, việc bổ sung một trạng thái ở back-end mà quên cập nhật phía giao diện sẽ bị phát hiện ngay tại thời điểm biên dịch.

- **Lợi ích và lý do lựa chọn:**

  - **Một mã nguồn phục vụ đồng thời hai nhóm người dùng:** Khách hàng và quản trị viên có nhu cầu sử dụng khác nhau nhưng lại dùng chung giao thức WebSocket, chung tập trạng thái và chung thành phần hiển thị tin nhắn. Việc gộp vào một ứng dụng duy nhất bảo đảm mọi thay đổi về giao thức chỉ phải chỉnh sửa tại một nơi.

  - **Ứng dụng web tiến bộ thay cho ứng dụng di động riêng biệt:** Bảng điều khiển được cấu hình manifest và service worker để có thể cài đặt lên màn hình chính của điện thoại. Đây là phương án thay thế cho việc xây dựng một ứng dụng di động riêng, cho phép duy trì một mã nguồn duy nhất tự co giãn theo kích thước màn hình, qua đó giảm đáng kể khối lượng công việc mà vẫn đạt được mục tiêu giúp quản trị viên xử lý các ca đang chờ khi đang di chuyển.

- **Các công cụ bổ sung:**

  - **Tailwind CSS:** Thư viện tiện ích CSS, được sử dụng ở dạng thuần mà không kèm theo bất kỳ thư viện thành phần dựng sẵn nào (Hình 1.19).

Hình 1.19. Logo Tailwind CSS

    Việc không sử dụng thư viện thành phần là một quyết định đã được cân nhắc kỹ. Giao diện của đồ án có nhiều trạng thái hiển thị đặc thù như khung chuyển tiếp, khung chờ duyệt, phiếu chuyển tiếp và chỉ báo trạng thái gửi của từng tin nhắn, vốn không có sẵn trong các thư viện thành phần phổ biến. Việc dùng Tailwind CSS ở dạng thuần cho phép kiểm soát hoàn toàn hệ thống thiết kế và tránh phải ghi đè kiểu dáng mặc định của thư viện.

  - **TanStack Query:** Thư viện quản lý trạng thái dữ liệu phía máy chủ (Hình 1.20).

Hình 1.20. Logo TanStack Query

    Thư viện này giữ bộ đệm dữ liệu đã tải và cung cấp cơ chế vô hiệu hoá bộ đệm khi cần. Điểm quan trọng trong đồ án nằm ở cách kết hợp: thay vì hỏi vòng máy chủ theo chu kỳ cố định, hệ thống sử dụng chính các sự kiện WebSocket để kích hoạt việc làm mới dữ liệu đúng thời điểm. Chu kỳ làm mới định kỳ vẫn được duy trì nhưng chỉ đóng vai trò lưới an toàn phòng khi mất sự kiện, nhờ đó lưu lượng truy vấn không tăng theo số lượng khách hàng đang hoạt động.

#### Mục 1.5.5 — Tổ chức mã nguồn và kiểm thử · Đã rút gọn

*Nằm sau: «Tổ chức mã nguồn và kiểm thử …»*

- **Quản lý monorepo:** pnpm workspaces

  Dưới đây là hình ảnh logo của pnpm (Hình 1.21).

Hình 1.21. Logo pnpm

  - **Mô tả:** Dự án được tổ chức theo mô hình một kho mã nguồn duy nhất gồm hai ứng dụng (`apps/backend` và `apps/dashboard`) cùng một package dùng chung (`packages/shared-types`). Package dùng chung chứa các kiểu TypeScript được đồng bộ với tập enum phía back-end.

  - **Lý do lựa chọn:** Mục đích chính của mô hình này là bảo đảm tập trạng thái hội thoại chỉ có một nguồn khai báo duy nhất trên toàn hệ thống. Nếu back-end và giao diện khai báo riêng hai danh sách trạng thái, hai danh sách này chắc chắn sẽ lệch nhau sau một số lần chỉnh sửa. Sai lệch ở vị trí này khiến giao diện hiển thị sai trạng thái của ca, một loại lỗi rất khó phát hiện do không làm phát sinh ngoại lệ.

- **Kiểm thử:** pytest cho phần back-end và trình chạy kiểm thử tích hợp sẵn của Node.js cho phần giao diện

  - Bộ kiểm thử back-end tuân thủ một ràng buộc bắt buộc là toàn bộ phải chạy được ở chế độ ngoại tuyến, không cần khoá API và không thực hiện bất kỳ lời gọi mạng nào. Ràng buộc này không chỉ mang lại sự thuận tiện mà còn buộc mọi nhánh suy giảm an toàn phải được cài đặt đúng, bởi đó chính là nhánh mà bộ kiểm thử đi vào khi chạy.

- **Tự động hoá lệnh:** Makefile

  - Các thao tác thường dùng như cài đặt, chạy môi trường phát triển, áp dụng migration, nạp lại kho tri thức, kiểm tra kết nối, chạy kiểm thử và đóng gói đều được gói thành các lệnh ngắn gọn. Cách làm này giữ cho những tham số dài dòng, chẳng hạn trần kích thước khung WebSocket, nằm tại một vị trí duy nhất thay vì phải ghi nhớ mỗi khi thao tác thủ công.

- **Quản lý phiên bản:** Git và GitHub, tổ chức theo mô hình một nhánh chính kèm các nhánh tính năng, trong đó mỗi nhánh tương ứng với một lát cắt chức năng như mô tả ở mục 3.2.1.

#### Mục 1.5.6 — Môi trường phát triển và công cụ hỗ trợ · Đã lược bỏ

*Nằm sau: «Tổ chức mã nguồn và kiểm thử …»*

##### Môi trường phát triển và công cụ hỗ trợ

Bên cạnh các công nghệ cấu thành sản phẩm, quá trình phát triển còn sử dụng một số công cụ hỗ trợ nhằm chuẩn hoá vòng đời phát triển phần mềm. Trong đó đáng chú ý là hai công cụ do chính đồ án xây dựng, phục vụ trực tiếp cho việc đo đạc và gỡ lỗi pipeline xử lý.

- **Môi trường lập trình tích hợp.** *(Điền IDE thực tế sử dụng.)* Do dự án được tổ chức theo mô hình monorepo chứa cả Python và TypeScript, môi trường lập trình cần mở được đồng thời hai ngôn ngữ và nhận diện được các kiểu dữ liệu dùng chung khai báo trong `packages/shared-types`.

- **`make check-conn`.** Đây là script do đồ án tự xây dựng, có nhiệm vụ kiểm tra kết nối tới PostgreSQL và Qdrant trước khi khởi chạy hệ thống. Công cụ này giúp phân biệt sớm giữa lỗi cấu hình với lỗi logic nghiệp vụ. Sự phân biệt này có ý nghĩa quan trọng khi toàn bộ hạ tầng đều là dịch vụ managed trên gói miễn phí, nơi hiện tượng khởi động nguội rất dễ bị nhầm lẫn thành lỗi mã nguồn.

- **Trang kiểm tra pipeline `/rag`.** Đây là công cụ nội bộ cho phép chạy thử một truy vấn qua tác tử thứ nhất và tác tử thứ hai, sau đó hiển thị nhãn ý định cùng các đoạn tri thức truy hồi được kèm điểm cosine của từng đoạn. Công cụ này đóng vai trò chính trong việc đo phân bố điểm và lựa chọn ngưỡng truy hồi được trình bày ở mục 3.3.5. Nếu không có công cụ này, việc chọn ngưỡng sẽ phải dựa vào cảm tính thay vì dựa trên số liệu đo đạc.

- **Bảng điều khiển Langfuse.** Được sử dụng để xem trace của từng lượt trong quá trình phát triển, đặc biệt hữu ích khi cần xác định một lượt xử lý chậm là do bước gọi mô hình hay do bước truy vấn cơ sở dữ liệu vector.

- **Công cụ quản trị cơ sở dữ liệu.** *(Điền công cụ thực tế.)* Được dùng để kiểm tra trực tiếp giá trị cột trạng thái sau mỗi lượt xử lý, nội dung JSONB của phiếu chuyển tiếp và sáu dòng nhật ký kiểm toán có cùng khoá lượt.

#### Mục 1.6 — Tổng kết chương · Đã rút gọn

*Nằm sau: «Tổng kết chương …»*

Chương 1 đã đi sâu khảo sát bối cảnh thực tiễn và những rào cản hiện tại trong công tác chăm sóc khách hàng của các cửa hàng thời trang trực tuyến. Từ việc phân tích bốn nhóm giải pháp tự động hoá đang được sử dụng, chương đã chỉ ra khoảng trống mà đề tài nhắm tới, đó là chưa có nhóm giải pháp nào vừa hiểu được ngôn ngữ tự nhiên, vừa giữ được tính dự đoán và khả năng kiểm toán ở mức chấp nhận được cho một hệ thống đối thoại trực tiếp với khách hàng.

Bên cạnh đó, chương cũng đã trình bày cơ sở lý thuyết về mô hình ngôn ngữ lớn, kỹ thuật sinh có tăng cường truy hồi, kiến trúc đa tác tử và thư viện LangGraph, đồng thời phân tích ba dạng ảo giác cần phòng chống. Trong đó, hai dạng suy diễn ra sự phủ định từ chỗ nguồn im lặng và bịa ra hành động tuy ít được các tài liệu nghiên cứu đề cập nhưng lại gây hậu quả nặng nề trong ngữ cảnh chăm sóc khách hàng.

Trên nền tảng đó, chương đã xác định rõ bài toán với sáu mục tiêu cụ thể, khoanh vùng phạm vi và giới hạn của hệ thống, trong đó nêu rõ việc không xây dựng hệ đa tác tử tự trị hoàn toàn như một lựa chọn thiết kế có chủ đích. Chương cũng tổng hợp đầy đủ các yêu cầu chức năng, yêu cầu phi chức năng và bộ chỉ số đánh giá, cùng với hệ sinh thái công nghệ được lựa chọn kèm lý do tương ứng với từng ràng buộc.

Những nền tảng lý thuyết và các quyết định công nghệ nêu trên chính là tiền đề để triển khai phần phân tích và thiết kế chi tiết ở Chương 2, bao gồm bốn trụ cột thiết kế, kiến trúc pipeline bốn tác tử, cơ chế an toàn và kiểm soát, thiết kế kho tri thức, thiết kế cơ sở dữ liệu và các biện pháp bảo mật của hệ thống.

### Chương 2 — Phân tích và thiết kế hệ thống (`chuong-2.md`)

#### Mục 2.2.1 — Bốn trụ cột thiết kế · Đã rút gọn

*Nằm sau: «Bốn trụ cột thiết kế …»*

Toàn bộ thiết kế của hệ thống được xây dựng trên bốn nguyên tắc nền tảng. Bốn trụ cột này chi phối mọi quyết định kỹ thuật được trình bày ở các phần sau của chương.

**Trụ cột thứ nhất: luồng xử lý cố định để bảo đảm tính dự đoán và khả năng kiểm toán.**

Thứ tự các tác tử do đồ thị quy định trước, còn việc rẽ nhánh do chính nút phát ngôn duy nhất thực hiện dựa trên tập cờ và quyết định của tác tử thứ ba; không một tác tử nào tự chọn đường đi tại thời điểm chạy. Điều này đồng nghĩa với việc hệ thống không sử dụng tác tử điều phối trung tâm. Đây là một sự đánh đổi có chủ đích, trong đó hệ thống từ bỏ quyền tự trị ở tầng điều phối để đổi lấy độ tin cậy, khả năng kiểm toán và một trần chi phí xác định. Hệ quả trực tiếp là mỗi lượt hội thoại của khách hàng tiêu tốn tối đa hai lời gọi mô hình sinh và một lời gọi embedding. Con số này là giới hạn cứng, được biết trước và không phụ thuộc vào nội dung câu hỏi. Trên thực tế, nhiều nhánh xử lý còn tiêu tốn ít hơn, bởi lượt xã giao và lượt bị chuyển cho nhân viên đều sử dụng câu mẫu cố định nên không phát sinh lời gọi mô hình ở bước sinh phản hồi.

**Trụ cột thứ hai: tự trị có giới hạn ở tầng tác tử.**

Bên trong mỗi nút xử lý, tác tử vẫn có không gian quyết định riêng. Cụ thể, tác tử phân loại tự lựa chọn nhãn ý định và trích xuất thực thể; tác tử tri thức tự quyết định truy hồi theo ý định hay truy hồi trên phạm vi rộng; tác tử phản hồi tự lựa chọn cách diễn đạt câu trả lời. Tuy nhiên, toàn bộ các quyết định này đều bị giới hạn về số bước thực hiện và không có khả năng tác động tới luồng điều phối chung.

**Trụ cột thứ ba: an toàn trước các tình huống ngoài dự kiến.**

Mỗi tác tử khi hoàn tất xử lý đều trả về kèm độ tin cậy và tập cờ bất định. Khi gặp giới hạn năng lực, hệ thống chuyển yêu cầu cho nhân viên thay vì cố gắng trả lời. Đây là nguyên tắc mang tính đặc thù của nghiệp vụ chăm sóc khách hàng: trong trường hợp không có tri thức làm căn cứ, hệ thống bắt buộc phải chuyển ca cho nhân viên và tuyệt đối không được tự sinh câu trả lời.

**Trụ cột thứ tư: cải thiện dần dưới sự phê duyệt của con người.**

Hệ thống phát hiện các mẫu lặp lại từ nhật ký kiểm toán, chẳng hạn những ý định thường xuyên bị chuyển tiếp, các chủ đề có độ tin cậy thấp hoặc các câu hỏi chưa có tri thức tương ứng, từ đó đưa ra đề xuất bổ sung tri thức. Đề xuất chỉ được áp dụng sau khi quản trị viên phê duyệt. Các tác tử không có quyền tự thay đổi luồng điều khiển và cũng không được tự chỉnh sửa kho tri thức. Trong giai đoạn hiện tại, hệ thống mới triển khai phần thu thập dữ liệu thông qua tab Báo cáo, còn phần sinh đề xuất tự động thuộc về giai đoạn phát triển tiếp theo.

#### Mục 2.2.2 — Kiến trúc tổng thể · Đã rút gọn

*Nằm sau: «Kiến trúc tổng thể …»*

Hệ thống được tổ chức theo kiến trúc phân lớp gồm bốn lớp, mỗi lớp đảm nhiệm một nhóm trách nhiệm riêng biệt.

- **Lớp giao diện:** Gồm một ứng dụng Next.js duy nhất phục vụ đồng thời hai vai trò là cổng chat dành cho khách hàng và bảng điều khiển dành cho quản trị viên. Trên thiết bị di động, chính ứng dụng này được cài đặt dưới dạng ứng dụng web tiến bộ.

- **Lớp giao tiếp:** Cung cấp các REST API phục vụ thao tác quản trị và tra cứu, đồng thời sử dụng giao thức WebSocket cho luồng hội thoại thời gian thực theo hai chiều. Hệ thống có ba kênh WebSocket, gồm kênh `/ws/chat` dành cho khách hàng, kênh `/ws/admin-inbox` phục vụ thông báo hàng đợi và kênh `/ws/admin/{conversation_id}` dành cho quản trị viên đang mở một ca cụ thể.

- **Lớp xử lý:** Bao gồm pipeline bốn tác tử vận hành trên nền LangGraph, kèm theo các dịch vụ nghiệp vụ phụ trách hội thoại, cổng cấu hình, tri thức, đơn hàng, chuyển tiếp, kiểm toán và báo cáo, cùng một tác vụ nền quét các hội thoại không hoạt động.

- **Lớp lưu trữ:** PostgreSQL lưu giữ dữ liệu nghiệp vụ và nhật ký kiểm toán, trong khi Qdrant lưu giữ vector tri thức. Hệ thống không sử dụng thêm bất kỳ kho lưu trữ trung gian nào khác. Bộ nhớ đa lượt của hội thoại được đọc trực tiếp từ PostgreSQL ở đầu mỗi lượt, còn trung tâm phát thời gian thực và bộ giới hạn tần suất nằm trong bộ nhớ tiến trình.

#### Mục 2.3.2 — Đặc tả một số Use Case tiêu biểu · Đã rút gọn

*Nằm sau: «Đặc tả một số Use Case tiêu biểu …»*

Trong hai mươi use case đã liệt kê ở trên, phần này tiến hành đặc tả chi tiết hai use case đại diện cho hai nhóm nghiệp vụ cốt lõi, gồm một use case phía khách hàng và một use case phía quản trị viên. Tiêu chí lựa chọn là mức độ phức tạp của luồng xử lý, bởi cả hai use case được chọn đều có nhiều luồng thay thế và đều liên quan trực tiếp tới các cơ chế an toàn đặc trưng của hệ thống. Các use case còn lại hoặc chỉ là nghiệp vụ hiển thị thông tin không có luồng rẽ nhánh, hoặc lặp lại cùng một khuôn xử lý. Đặc tả chi tiết của sáu use case tiêu biểu tiếp theo được chuyển xuống phần Phụ lục nhằm giữ cho nội dung chương tập trung vào trọng tâm thiết kế.

Dưới đây là bảng đặc tả use case UC-03 về việc nhận phản hồi tự động. Đây là use case có luồng xử lý dài nhất phía khách hàng do đi qua trọn vẹn cả bốn tác tử và cả ba kết cục giao phản hồi (Bảng 2.3).

#### Mục 2.3.2 — Đặc tả một số Use Case tiêu biểu · Đã rút gọn

*Nằm sau: «Bảng 2.3. Đặc tả UC-03 — Nhận phản hồi tự động …»*

| **Mục**           | **Nội dung**                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Tên use case      | Nhận phản hồi tự động (UC-03) |
| Mô tả             | Cho phép khách hàng nhận câu trả lời do hệ thống sinh tự động cho câu hỏi của mình, với điều kiện hệ thống có đủ căn cứ và ý định được cấu hình cho phép trả lời thẳng. Nếu một trong hai điều kiện không thoả, use case rẽ sang nhánh chờ duyệt hoặc nhánh chuyển cho nhân viên. |
| Tác nhân          | Khách hàng                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Tiền điều kiện    | Hội thoại đang ở trạng thái phía AI (không có nhân viên đang xử lý)                                                                                                                                                                                                                                                                                                                                                                                          |
| Luồng chính       | 1\. Khách gửi tin nhắn qua WebSocket 2. Hệ thống chuẩn hoá, kiểm tra trùng lặp và giới hạn tần suất, xác nhận đã nhận (ack) 3. Hệ thống lưu tin khách, phát cho các phiên đang mở 4. Pipeline chạy bốn tác tử 5. Tác tử 3 quyết định auto_reply, cổng cho phép gửi thẳng 6. Tác tử 4 sinh phản hồi có căn cứ 7. Hệ thống ghi trạng thái và tin nhắn AI trong một giao dịch, commit xong mới gửi cho khách 8. Khách nhận phản hồi; nhật ký kiểm toán được ghi |
| Luồng thay thế 5a | Cổng tắt cho ý định này → nháp vào hàng đợi duyệt, khách nhận tín hiệu chờ                                                                                                                                                                                                                                                                                                                                                                                   |
| Luồng thay thế 5b | Có cờ chặn → chuyển người, khách nhận thông báo chuyển tiếp                                                                                                                                                                                                                                                                                                                                                                                                  |
| Luồng thay thế 7a | Nhân viên tiếp quản ca trong lúc pipeline đang chạy → lượt bị huỷ, khách nhận trạng thái hiện tại thay vì câu trả lời                                                                                                                                                                                                                                                                                                                                        |
| Hậu điều kiện     | Trạng thái hội thoại được cập nhật; sáu dòng nhật ký kiểm toán được ghi với cùng khoá lượt |
| Luồng sự kiện ngoại lệ | E1. Ghi cơ sở dữ liệu thất bại cả sau một lần thử lại → khách nhận một câu trả lời không kèm bất kỳ cam kết nào thay cho thông báo chuyển tiếp, để hệ thống không hứa về một ca không tồn tại trong hàng đợi. E2. Qdrant hoặc dịch vụ nhúng gặp lỗi → tác tử 2 phát cờ `search_error` → lượt được chuyển cho nhân viên, và tab báo cáo gắn đúng nhãn sự cố hạ tầng thay vì nhãn thiếu tri thức. E3. Lời gọi mô hình vượt thời gian chờ 20 giây → phát cờ `llm_unavailable` → chuyển cho nhân viên. E4. Khách gửi vượt 20 tin trong 60 giây → hệ thống trả khung lỗi `rate_limited` và không chạy pipeline cho tin đó                                                                                                                                                                                                                                                                                                                                                                  |

#### Mục 2.3.2 — Đặc tả một số Use Case tiêu biểu · Đã rút gọn

*Nằm sau: «Bảng 2.3. Đặc tả UC-03 — Nhận phản hồi tự động …»*

Dưới đây là bảng đặc tả use case UC-11 về việc nhận ca từ hàng đợi chuyển tiếp. Đây là use case thể hiện rõ nhất cơ chế so sánh rồi ghi: khi hai quản trị viên cùng thao tác nhận một ca, chỉ một người thực hiện thành công, người còn lại nhận về lỗi xung đột thay vì cả hai cùng ghi đè lên trạng thái của nhau (Bảng 2.4).

#### Mục 2.3.2 — Đặc tả một số Use Case tiêu biểu · Đã rút gọn

*Nằm sau: «Bảng 2.4. Đặc tả UC-11 — Nhận ca từ hàng đợi chuyển tiếp …»*

| **Mục**           | **Nội dung**                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Tên use case      | Nhận ca từ hàng đợi chuyển tiếp (UC-11) |
| Mô tả             | Cho phép quản trị viên tiếp quản một hội thoại đã được hệ thống chuyển sang hàng đợi người. Sau khi nhận ca, tác tử ngừng can thiệp vào hội thoại đó và mọi tin nhắn của khách được định tuyến thẳng tới quản trị viên cho tới khi ca được đóng. |
| Tác nhân          | Quản trị viên                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Tiền điều kiện    | Đã đăng nhập với vai trò admin; tồn tại ca ở trạng thái chờ nhận                                                                                                                                                                                                                                                                                                                                                                                                    |
| Luồng chính       | 1\. Quản trị viên mở hàng đợi, thấy danh sách ca sắp theo mức ưu tiên giảm dần 2. Chọn một ca, xem EscalationCard (tóm tắt, ý định, thực thể, nguồn tri thức đã truy hồi, lý do chuyển, mức ưu tiên/nghiêm trọng, nháp gợi ý) 3. Bấm Nhận ca 4. Hệ thống kiểm tra trạng thái ca vẫn như lúc đọc; nếu đúng thì chuyển sang trạng thái đang xử lý và gán quản trị viên 5. AI tạm dừng cho ca này; mọi tin nhắn tiếp theo của khách định tuyến thẳng tới quản trị viên |
| Luồng thay thế 4a | Ca đã bị người khác nhận hoặc đã đóng → hệ thống trả lỗi xung đột, giao diện tải lại trạng thái mới                                                                                                                                                                                                                                                                                                                                                                 |
| Hậu điều kiện     | Hành động được ghi vào nhật ký kiểm toán |
| Luồng sự kiện ngoại lệ | E1. Quản trị viên bị hạ quyền giữa phiên → kênh WebSocket quản trị đọc lại vai trò ở mỗi tin nhắn và trả khung `not_assigned`, người đó không nhắn được cho khách nữa. E2. Cơ sở dữ liệu gặp lỗi đúng lúc xác minh quyền → kết nối bị đóng với mã 1011 thay vì mã xác thực thất bại, và giao diện tự nối lại theo cơ chế chờ tăng dần                                                                                                                                                                                                                                                                                                                                                                                                                           |

#### Mục 2.3.2 — Đặc tả một số Use Case tiêu biểu · Đã lược bỏ

*Nằm sau: «Bảng 2.4. Đặc tả UC-11 — Nhận ca từ hàng đợi chuyển tiếp …»*

Đặc tả chi tiết của sáu use case tiêu biểu còn lại, bao gồm UC-01 về việc đăng ký tài khoản, UC-04 về việc cung cấp mã đơn khi được hỏi lại, UC-06 về việc yêu cầu gặp nhân viên, UC-08 về việc đăng nhập và duy trì phiên làm việc, UC-13 về việc duyệt hoặc từ chối nháp phản hồi và UC-19 về việc cấu hình cổng theo từng ý định, được trình bày đầy đủ tại phần Phụ lục.

#### Mục 2.4.1 — Trạng thái điều phối (ConversationState) · Đã rút gọn

*Nằm sau: «Nối lượt prior_status, prior_intent, clarify_field Trạng thái và ý định của lượt trước, phục …»*

Cấu trúc trạng thái nêu trên gắn với ba quyết định thiết kế đáng chú ý.

**a) Trường lịch sử không sử dụng hàm gộp và được tách riêng khỏi trường tin nhắn.** Lịch sử hội thoại là đầu vào chỉ đọc được nạp từ cơ sở dữ liệu, trong khi trường tin nhắn là đầu ra của chính lượt xử lý hiện tại. Nếu gộp hai trường này làm một, bộ nhớ đa lượt sẽ bị nhân đôi, đồng thời lịch sử vô tình trở thành một nguồn bám căn cứ. Điều này bị cấm tuyệt đối trong thiết kế, bởi dữ liệu ghi nhận ở các lượt trước hoàn toàn có thể đã thay đổi tại thời điểm hiện tại.

**b) Hàm gộp theo kiểu cộng dồn chỉ tiếp nhận các cờ mới phát sinh.** Mỗi nút chỉ trả về những cờ do chính nó phát ra. Nhờ vậy, hệ thống quy được từng cờ về đúng tác tử đã sinh ra nó thay vì chỉ có một tập cờ gộp chung ở cuối lượt. Đây là điều kiện cần để tab báo cáo có thể phân tích được nguyên nhân khiến một lượt bị chuyển cho nhân viên.

**c) Trường định danh lượt chỉ phục vụ mục đích quan sát.** Thiết kế có ghi chú tường minh rằng không nút nào được phép đọc trường này để ra quyết định. Đây chính là ranh giới giữa lớp quan sát và lớp logic nghiệp vụ, theo đó việc bổ sung khả năng quan sát không được làm thay đổi hành vi của hệ thống.

#### Mục 2.4.2 — Agent 1 — Intent Classifier · Đã rút gọn

*Nằm sau: «Đầu ra: {intent, category, entities, confidence, uncertainty_flags}. …»*

**Bảng phân loại mười lăm ý định.** Danh sách ý định được thiết kế là một tập đóng, nhúng trực tiếp vào prompt kèm mô tả và ví dụ cho từng nhãn thay vì huấn luyện một bộ phân loại riêng. Tác tử thứ nhất không thực hiện bất kỳ thao tác truy hồi nào, bởi đây là trách nhiệm của tác tử thứ hai. Chính bảng phân loại nằm sẵn trong prompt là thành phần bù đắp cho việc bỏ bước truy hồi ở giai đoạn này.

Dưới đây là bảng phân loại đầy đủ mười lăm ý định của hệ thống cùng nhóm và các thực thể cần trích xuất tương ứng (Bảng 2.6).

#### Mục 2.4.2 — Agent 1 — Intent Classifier · Đã rút gọn

*Nằm sau: «Ngoài phạm vi other general — …»*

Trong bảng phân loại trên có một sự phân biệt tuy tinh tế nhưng rất quan trọng, đó là việc tách nhãn hỏi chính sách đổi trả ra khỏi nhóm nhãn yêu cầu hoàn tiền và đổi hàng. Khi khách hàng hỏi về nội dung chính sách đổi trả, đó chỉ là thao tác tra cứu thông tin và hệ thống được phép trả lời thẳng. Ngược lại, khi khách hàng yêu cầu trả một đơn hàng cụ thể, đó là một yêu cầu giao dịch bắt buộc phải đi qua cổng duyệt nháp. Nếu gộp hai trường hợp này vào cùng một nhãn, toàn bộ câu hỏi về chính sách đều sẽ bị giữ lại chờ phê duyệt, khiến hệ thống mất đi phần lớn giá trị sử dụng.

**Trích xuất thực thể theo hai đường song song.** Thực thể được trích xuất đồng thời bằng mô hình ngôn ngữ, theo cả schema lẫn tập ví dụ mẫu, và bằng biểu thức chính quy, sau đó hợp nhất kết quả với thứ tự ưu tiên dành cho mô hình. Biểu thức chính quy được thực thi ở mọi nhánh xử lý, kể cả nhánh suy giảm khi mô hình không khả dụng. Nhờ vậy, bất biến về việc mã đơn hàng không bao giờ bị thất lạc luôn được bảo đảm.

Bên cạnh đó, hệ thống áp dụng thêm một luật lọc bổ sung: nếu một chuỗi số chỉ xuất hiện trong ngữ cảnh chỉ số tiền, chẳng hạn đơn giá của sản phẩm, chuỗi này sẽ bị loại khỏi trường mã đơn hàng. Nếu thiếu luật lọc này, một câu hỏi về phí vận chuyển có kèm giá trị đơn hàng sẽ bị hiểu nhầm thành mã đơn và dẫn tới cả chuỗi hành vi sai lệch phía sau.

**Các cờ do tác tử thứ nhất phát ra** gồm năm cờ sau:

- **ambiguous_intent:** Mô hình báo hiệu còn mơ hồ giữa nhiều nhãn ý định khác nhau.

- **multi_intent:** Một tin nhắn của khách hàng chứa đồng thời nhiều ý định khác nhau.

- **out_of_domain:** Nhãn ý định rơi vào nhóm khác, tức là câu hỏi thật sự nằm ngoài phạm vi nghiệp vụ của cửa hàng.

- **human_requested:** Khách hàng chủ động yêu cầu được gặp nhân viên một cách rõ ràng.

- **llm_unavailable:** Hệ thống không thực hiện được lời gọi tới mô hình ngôn ngữ.

Cờ báo hiệu khách hàng yêu cầu gặp nhân viên được phát hiện bằng một luật tất định áp dụng trực tiếp trên lời của khách, neo theo động từ liên hệ đứng trước danh từ chỉ người. Đây là quyết định thiết kế xuất phát từ quan sát thực tế, bởi bảng phân loại không có nhãn riêng cho yêu cầu gặp nhân viên, trong khi mô hình lại có xu hướng xếp những câu đề nghị gặp nhân viên vào nhóm xã giao, khiến yêu cầu này bị bỏ sót. Luật nêu trên được thực thi ở mọi nhánh, kể cả khi mô hình không khả dụng, nhằm bảo đảm khi khách hàng đã yêu cầu gặp người thật thì yêu cầu đó phải đến được nhân viên, không phụ thuộc vào tình trạng hoạt động của mô hình. Đồng thời, cách neo theo động từ liên hệ cũng bảo đảm những câu than phiền về thái độ nhân viên hay câu hỏi về quy mô nhân sự của cửa hàng không bị nhận diện nhầm.

**Cơ chế suy giảm an toàn.** Trong trường hợp thiếu khoá API, mô hình bị tắt hoặc lời gọi phát sinh lỗi, tác tử trả về ý định ở trạng thái không xác định, độ tin cậy bằng 0, kèm cờ báo mô hình không khả dụng, còn thực thể vẫn được lấy từ biểu thức chính quy. Tác tử không ném ngoại lệ và không thực hiện lời gọi mạng, nhờ đó toàn bộ bộ kiểm thử có thể chạy được ở chế độ ngoại tuyến.

#### Mục 2.4.3 — Agent 2 — Knowledge Agent (RAG + tra cứu đơn hàng) · Đã rút gọn

*Nằm sau: «Đầu ra: {rag_contexts, retrieval_confidence, order_context, order_not_found, uncertainty_flags}. …»*

Tác tử thứ hai vận hành hai nhánh song song, bởi hai nhánh này bổ trợ cho nhau chứ không thay thế lẫn nhau. Kho tri thức cung cấp câu trả lời về chính sách của cửa hàng, trong khi cơ sở dữ liệu đơn hàng cung cấp thông tin về một đơn hàng cụ thể. Trước khi tách riêng hai nhánh, hệ thống từng gặp một lỗi đáng chú ý: khi khách hàng hỏi về trạng thái đơn hàng, cơ chế truy hồi lại tìm trúng tài liệu chính sách vận chuyển với điểm số đủ cao nên lượt xử lý được xếp vào nhóm trả lời tự động, trong khi hệ thống hoàn toàn không có dữ liệu đơn hàng nào làm căn cứ.

**Nhánh truy hồi tri thức** hoạt động theo trình tự sau:

- Nếu ý định thuộc tập không cần truy hồi, hiện tại chỉ bao gồm nhóm xã giao, hệ thống bỏ qua bước truy hồi và không phát cờ bám nguồn. Lý do là một lượt xã giao không phát biểu bất kỳ sự thật nào nên cũng không tồn tại nội dung cần có căn cứ. Cần nhấn mạnh đây là việc khoanh phạm vi áp dụng của cơ chế bám nguồn chứ không phải nới lỏng cơ chế này.

- Hệ thống vector hoá câu hỏi rồi truy vấn k kết quả gần nhất trên Qdrant, với giá trị mặc định là 4, đồng thời ưu tiên các đoạn tri thức có cùng ý định. Nếu lượt truy vấn có lọc theo ý định không trả về đủ số lượng hoặc điểm cao nhất vẫn nằm dưới ngưỡng, hệ thống chạy thêm một lượt truy vấn không lọc rồi gộp kết quả và khử trùng lặp theo điểm số. Cách làm này bảo đảm một nhãn ý định sai hoặc bị thiếu không dẫn tới việc bỏ sót tri thức đúng.

- Hệ thống so sánh điểm cosine của kết quả tốt nhất với ngưỡng truy hồi đã cấu hình; nếu điểm nằm dưới ngưỡng thì phát cờ báo điểm truy hồi thấp.

Cần lưu ý rằng số đoạn truy hồi, với giá trị mặc định bằng 4, là tham số của tầng dịch vụ và không thuộc nhóm giá trị cấu hình được theo yêu cầu NFR-10. Khác với ngưỡng truy hồi, tham số này không tham gia vào quyết định chuyển ca cho nhân viên nên không cần điều chỉnh trong lúc hệ thống đang chạy.

**Nhánh tra cứu đơn hàng:** chỉ chạy với các ý định gắn với đơn (order_status, shipping, refund, exchange, complaint) và chỉ khi có mã đơn. Truy vấn luôn kèm định danh chủ đơn.

Kết quả tra cứu đơn hàng được phân biệt thành ba tình huống khác nhau về bản chất:

- **Tra cứu thành công:** Dữ liệu đơn hàng được ghi vào trạng thái và trở thành nguồn căn cứ thứ ba cho tác tử thứ tư.

- **Tra cứu không ra kết quả:** Hệ thống ghi nhận tín hiệu không tìm thấy đơn. Đây không phải là một cờ chặn, bởi bản thân kết quả tra cứu đã là một căn cứ hợp lệ để trả lời khách hàng, đồng thời phần lớn các trường hợp chỉ đơn giản là khách gõ nhầm mã đơn. Việc chuyển ca cho nhân viên ngay ở tình huống này là quá vội vàng.

- **Tra cứu thất bại hoặc không thể thực hiện:** Tình huống này xảy ra khi cơ sở dữ liệu gặp lỗi hoặc thiếu định danh khách hàng, và hệ thống phát cờ chưa xử lý được đơn hàng dẫn tới chuyển ca cho nhân viên. Việc phân biệt giữa tra cứu ra kết quả rỗng với tra cứu không thực hiện được là bắt buộc, bởi thông báo không tìm thấy đơn trong tài khoản của khách trong khi thực tế hệ thống chưa tra cứu được là hành vi cung cấp thông tin sai sự thật.

Cờ chưa xử lý được đơn hàng chỉ được bật khi khách hàng cung cấp mã sai tới lần thứ hai trong cùng một ca. Việc đếm số lần tra cứu thất bại được thực hiện bằng cách so khớp nguyên văn câu thông báo cố định trong lịch sử hội thoại rồi tra lại các mã đơn đó, thay vì dò tìm theo các dấu hiệu mờ trong câu trả lời do mô hình sinh ra.

**Cơ chế miễn cờ khi đã có dữ liệu đơn hàng.** Khi tra cứu được đơn hàng, các cờ bám nguồn của nhánh truy hồi tri thức đều được miễn, bởi chính dữ liệu đơn hàng đã đóng vai trò căn cứ cho câu trả lời. Tuy nhiên, các cờ được miễn vẫn được ghi đầy đủ vào nhật ký để công tác kiểm toán có thể theo dõi, thay vì bị loại bỏ mà không để lại dấu vết.

**Các cờ do tác tử thứ hai phát ra** bao gồm: không có tri thức liên quan, điểm truy hồi thấp, lỗi tìm kiếm do sự cố hạ tầng Qdrant hoặc dịch vụ embedding, và chưa xử lý được đơn hàng. Cần lưu ý rằng cờ lỗi tìm kiếm khác về bản chất so với cờ không có tri thức liên quan, bởi một bên phản ánh sự cố hạ tầng còn một bên phản ánh việc kho tri thức chưa bao phủ nội dung được hỏi.

#### Mục 2.4.4 — Agent 3 — Decision Engine · Đã rút gọn

*Nằm sau: «Tác tử thứ ba là nút ra quyết định của pipeline, đồng thời là …»*

Tác tử này hoạt động hoàn toàn tất định và không thực hiện bất kỳ lời gọi mô hình ngôn ngữ nào. Quyết định thiết kế này xuất phát từ hai lý do:

- **Lời gọi mô hình là không cần thiết:** Quyết định về việc hệ thống có đủ căn cứ để trả lời hay không đã được các tác tử trước mã hoá thành tập cờ. Việc đưa tập cờ này cho một mô hình xác suất diễn giải lại chỉ làm phát sinh thêm một điểm bất định trong luồng xử lý.

- **Lời gọi mô hình gây ảnh hưởng tới độ trễ:** Bổ sung một lời gọi mô hình vào đường xử lý chính của mỗi lượt sẽ làm hỏng ràng buộc NFR-1 về thời gian phản hồi.

**Nguyên tắc không gộp hai thang độ tin cậy.** Độ tin cậy về ý định là con số do chính mô hình tự khai báo về nhãn mà nó lựa chọn, trong khi độ tin cậy truy hồi là điểm cosine giữa hai vector. Đây là hai thang đo hoàn toàn khác nhau về bản chất, do đó việc lấy giá trị nhỏ nhất rồi so với một ngưỡng chung là một phép toán không có ý nghĩa. Tác tử thứ ba vẫn giữ cả hai con số trong nhật ký phục vụ phân tích, nhưng việc định tuyến chỉ dựa trên tập cờ.

#### Mục 2.4.4 — Agent 3 — Decision Engine · Đã rút gọn

*Nằm sau: «order_unresolved Agent 2 Tra đơn hỏng, hoặc mã sai lần thứ hai …»*

Bên cạnh tám cờ chặn nêu trên, có hai cờ cố ý không được đưa vào tập chặn. Lý do của hai trường hợp này làm rõ triết lý thiết kế của toàn hệ thống:

- **Cờ ý định mơ hồ không gây chặn:** Nguyên tắc của hệ thống là chuyển ca cho nhân viên khi không trả lời được chứ không phải khi nhãn ý định chưa rõ ràng. Một câu hỏi mà mô hình còn phân vân giữa hai nhãn nhưng truy hồi trúng tài liệu chính sách với điểm số cao thì vẫn hoàn toàn trả lời được. Trong trường hợp căn cứ yếu, chính các cờ bám nguồn đã đảm nhiệm việc chặn. Vì vậy, cờ này được giữ lại với vai trò cờ thông tin phục vụ công tác phân tích.

- **Cờ rủi ro ảo giác không thuộc phạm vi tác tử thứ ba:** Cờ này do tác tử thứ tư phát ra sau khi bước quyết định đã hoàn tất. Với tư cách là điểm phát ngôn duy nhất của hệ thống, chính tác tử thứ tư sẽ tự thực hiện việc chuyển ca cho nhân viên khi phát cờ này.

**Mức ưu tiên và mức nghiêm trọng** được gán theo một bảng tra tất định dựa trên ý định. Cụ thể, ý định khiếu nại được xếp ở mức cao cho cả hai tiêu chí; ý định hoàn tiền ở mức ưu tiên cao và mức nghiêm trọng trung bình; ý định đổi hàng cùng tra cứu đơn ở mức trung bình và thấp; các ý định còn lại đều ở mức thấp. Hai giá trị này không tham gia vào quá trình định tuyến mà chỉ phục vụ việc sắp xếp hàng đợi cho quản trị viên.

**Nhánh xử lý thứ ba là nhánh hỏi lại thông tin.** Khi ý định gắn với đơn hàng nhưng thiếu mã đơn và không có cờ chặn nào được bật, tác tử thứ ba định tuyến sang nhánh hỏi lại. Tác tử thứ tư sẽ hỏi khách hàng cung cấp mã đơn và hội thoại chuyển sang trạng thái chờ khách trả lời. Cơ chế này có kèm khoá chống lặp: nếu lượt trước đã hỏi mà lượt hiện tại vẫn thiếu thông tin, hệ thống chuyển thẳng ca cho nhân viên với lý do chưa làm rõ được yêu cầu. Việc hỏi lại một lần là hợp lý, nhưng hỏi lại nhiều lần sẽ gây phiền toái cho khách hàng.

#### Mục 2.4.5 — Agent 4 — Response Generator · Đã rút gọn

*Nằm sau: «Agent 4 — Response Generator …»*

Tác tử thứ tư đóng vai trò là điểm phát ngôn duy nhất của hệ thống tới khách hàng. Mọi tin nhắn do hệ thống sinh ra đều phát đi từ tác tử này, bất kể đó là câu trả lời nội dung, thông báo chuyển tiếp hay câu hỏi làm rõ.

**Ba nguồn căn cứ** được cấp cho tác tử thứ tư gồm:

- **Tệp sự thật lõi của cửa hàng, luôn được nạp ở mọi lượt:** Tệp này chứa các thông tin nền của cửa hàng như giờ hỗ trợ, phí và thời gian vận chuyển, hình thức thanh toán, mốc thời gian đổi trả, bảng kích cỡ và chương trình thành viên. Tệp không được đưa vào cơ sở dữ liệu vector mà nạp thẳng vào prompt hệ thống ở mọi lượt, bởi đây là thông tin nền mà mọi câu trả lời đều có thể cần tới và không nên phụ thuộc vào kết quả truy hồi.

- **Các đoạn tri thức truy hồi được:** Mỗi đoạn đi kèm một trong năm nhãn phân loại gồm quy trình xử lý, tài liệu tra cứu, câu hỏi thường gặp, khuyến mãi hoặc tài liệu tải lên, giúp mô hình nhận biết đoạn nào cần bám theo từng bước.

- **Dữ liệu đơn hàng của chính khách hàng** trong trường hợp tra cứu thành công.

**Năm nhánh xử lý được xét theo thứ tự** như sau:

- **Nhánh câu hỏi làm rõ:** Đây là nhánh được xét trước tiên, căn cứ vào quyết định mà tác tử thứ ba ghi vào trạng thái. Tác tử thứ tư phát đúng một câu hỏi mã đơn cố định từng chữ, không gọi mô hình, đồng thời chuyển hội thoại sang trạng thái chờ khách hàng bổ sung thông tin.

- **Nhánh thông báo chuyển tiếp** khi tác tử thứ ba quyết định chuyển ca cho nhân viên, cũng không phát sinh lời gọi mô hình. Nhánh này có hai phiên bản dành cho thời điểm trong giờ hỗ trợ và ngoài giờ hỗ trợ, trong đó phiên bản ngoài giờ bổ sung thông tin về khung giờ làm việc và cam kết phản hồi sớm.

- **Nhánh câu mẫu cố định cho ý định xã giao:** Nhánh này không gọi mô hình và không phát cờ nào. Nhánh được xét trước cơ chế chặn chống ảo giác, bởi tác tử thứ hai đã cố ý bỏ qua bước truy hồi cho nhóm lượt này.

- **Nhánh thông báo không tìm thấy đơn hàng:** Nội dung câu thông báo được cố định từng chữ, không để mô hình diễn đạt lại, do nội dung này nhạy cảm về mặt quyền riêng tư. Trường hợp mã đơn không tồn tại và trường hợp mã đơn thuộc về người khác đều nhận cùng một câu trả lời, nhờ đó hệ thống không để lộ sự tồn tại đơn hàng của khách hàng khác. Câu thông báo cũng chỉ cam kết những điều tương ứng với tín hiệu có thật trong hệ thống.

- **Nhánh sinh phản hồi có căn cứ** áp dụng cho toàn bộ các trường hợp còn lại.

**Cơ chế chặn cứng chống ảo giác.** Trong trường hợp không có bất kỳ nguồn căn cứ nào, tức là không truy hồi được đoạn tri thức nào và cũng không có dữ liệu đơn hàng, hoặc khi không gọi được mô hình, hệ thống sẽ không thực hiện lời gọi sinh phản hồi mà trả về câu dự phòng kèm cờ rủi ro ảo giác. Câu dự phòng này không được gửi tới khách hàng. Cờ rủi ro ảo giác khiến chính tác tử thứ tư chuyển ca sang hàng đợi nhân viên, kèm theo lý do đúng định dạng để phiếu chuyển tiếp hiển thị chính xác.

#### Mục 2.4.5 — Agent 4 — Response Generator · Đã rút gọn

*Nằm sau: «Bảng 2.8. Các quy tắc grounding của Agent 4 …»*

| **Quy tắc**                           | **Nội dung**                                                                                                              | **Chống dạng lỗi nào** |
|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------|------------------------|
| Chỉ dùng nguồn được cấp               | Không nói gì ngoài facts.md, rag_contexts, order_context                                                                  | Bịa ra cái "có"        |
| Không suy diễn vắng mặt               | Nguồn im lặng ≠ điều đó không tồn tại. Chỉ nói "không có" khi nguồn nói rõ như vậy. Phải viết "em chưa có thông tin về X" | Bịa ra cái "không có"  |
| Danh sách trong nguồn là danh sách MỞ | Nguồn liệt kê mà không kèm chữ "chỉ"/"duy nhất" thì đó là những thứ đã biết, không phải danh sách đóng                    | Bịa ra cái "không có"  |
| Giới hạn hành động                    | Chỉ tra cứu được trạng thái đơn; tuyệt đối không nói đã hoàn tiền, đã huỷ/đổi đơn, đã tạo yêu cầu                         | Bịa ra hành động       |
| Không tự hứa chuyển người             | Việc chuyển ca do hệ thống quyết; mọi câu tác tử 4 soạn đều là câu tự động, nên hứa "em sẽ chuyển nhân viên" là nói dối   | Bịa ra hành động       |
| Bám quy trình                         | Có đoạn nhãn "Quy trình xử lý" thì làm đúng thứ tự các bước, mỗi lượt chỉ hỏi 1–2 điều                                    | Nhảy tới kết luận      |
| Lịch sử không phải dữ liệu đơn        | Trạng thái đơn chỉ lấy từ khối dữ liệu đơn của lượt này; lượt trước có nói gì cũng không được nhắc lại                    | Dữ liệu cũ             |
| Văn xuôi thuần                        | Khung chat không render markdown; cấm mọi ký hiệu định dạng                                                               | Lỗi hiển thị           |

#### Mục 2.5.1 — Cổng cấu hình và ba kết cục giao phản hồi · Đã rút gọn

*Nằm sau: «Hình 2.5. Cây quyết định từ tập cờ tới ba kết cục giao phản …»*

**Bất biến FR-GATE-2 về ranh giới không được vượt qua.**

Cổng cấu hình chỉ can thiệp vào những ca mà tác tử thứ ba đã quyết định trả lời tự động, tức là các ca mà hệ thống đủ tự tin và có căn cứ rõ ràng. Các ca thuộc diện chuyển cho nhân viên không đi qua cổng mà luôn được đưa vào hàng đợi người, bất kể cấu hình hiện tại là gì. Nói cách khác, cơ chế an toàn không bao giờ bị cổng cấu hình ghi đè.

Ranh giới này tách bạch hai loại quyết định vốn thường bị gộp làm một:

- Câu hỏi về việc hệ thống có đủ căn cứ để trả lời hay không thuộc phạm vi an toàn, do mã tất định trả lời và con người không có quyền điều chỉnh.

- Câu hỏi về việc loại yêu cầu này có được phép trả lời tự động hay không thuộc phạm vi chính sách kinh doanh, do con người cấu hình.

Về cấu hình mặc định, cổng trả lời tự động được bật nhưng tắt đối với nhóm ý định nhạy cảm gồm hoàn tiền, đổi hàng và khiếu nại. Các ca thuộc nhóm này dù hệ thống có đủ tự tin vẫn phải đi qua bước duyệt nháp. Cấu hình được lưu trong cơ sở dữ liệu gồm một bản ghi cấu hình toàn cục và một bảng luật theo từng ý định, kèm cơ chế bộ đệm nhẹ với thời gian sống ngắn nhằm tránh truy vấn cơ sở dữ liệu ở mọi lượt xử lý.

Một chi tiết thiết kế đáng lưu ý là cổng cấu hình không chứa ngưỡng truy hồi. Ngưỡng này là một giá trị được đo đạc bằng script trên kho tri thức thật chứ không phải một tham số điều chỉnh tuỳ ý trên giao diện. Nếu hiển thị ngưỡng dưới dạng thanh trượt cho phép chỉnh sửa, hệ thống sẽ dễ rơi vào tình trạng giá trị hiển thị khác với giá trị đang thực sự vận hành. Vì vậy, ngưỡng truy hồi không xuất hiện ở bất kỳ vị trí nào trên giao diện cấu hình cổng: màn hình này chỉ gồm hai công tắc mức hệ thống và bảng luật theo từng ý định. Nguồn chân lý duy nhất của ngưỡng là biến môi trường `RETRIEVAL_THRESHOLD`, và cột tương ứng trong bảng cấu hình cổng cũng đã được một bước di trú cơ sở dữ liệu loại bỏ hẳn.

Trong trường hợp không đọc được cấu hình cổng do lỗi cơ sở dữ liệu, hệ thống sẽ gửi thẳng câu trả lời thay vì giữ lại dưới dạng nháp. Lý do là câu trả lời đó đã có căn cứ và đã đi qua cổng an toàn của tác tử thứ ba, nên việc giữ lại chỉ làm hội thoại bị đình trệ.

#### Mục 2.5.3 — Cơ chế so-sánh-rồi-ghi (CAS) và thứ tự ghi/báo · Đã rút gọn

*Nằm sau: «Cơ chế so-sánh-rồi-ghi (CAS) và thứ tự ghi/báo …»*

Tại tầng điều phối lượt xử lý, hệ thống phải giải quyết đồng thời hai vấn đề về tính đúng đắn của dữ liệu.

**a) Tranh chấp trạng thái.** Một lượt chạy pipeline mất vài giây, và trong khoảng thời gian đó quản trị viên hoàn toàn có thể tiếp quản hoặc đóng ca. Nếu lượt xử lý tự động vẫn tiếp tục ghi kết quả đè lên trạng thái mới, hệ thống sẽ rơi vào tình huống có hai bên cùng trao đổi với khách hàng.

Giải pháp được áp dụng là mọi thay đổi trạng thái đều thông qua cơ chế so sánh rồi ghi, theo đó trạng thái chỉ được ghi nếu giá trị hiện tại vẫn đúng bằng giá trị đã đọc ở đầu lượt. Nếu hai giá trị không khớp, toàn bộ lượt xử lý bị huỷ bỏ: hệ thống không lưu và không gửi bất cứ nội dung nào, khách hàng chỉ nhận một khung trạng thái hiện tại để giao diện gỡ bỏ chỉ báo đang soạn tin. Lượt bị huỷ vẫn được ghi vào nhật ký với dấu hiệu riêng, nhờ đó tab báo cáo không nhầm lẫn với những ca chuyển cho nhân viên thật sự.

**b) Thứ tự giữa thao tác ghi và thao tác thông báo.** Nếu hệ thống thông báo cho khách hàng rằng yêu cầu đã được chuyển tới nhân viên hỗ trợ rồi mới ghi vào cơ sở dữ liệu, và bước ghi này gặp lỗi, khách hàng sẽ nhận được một cam kết về một ca không hề tồn tại trong hàng đợi của quản trị viên.

Giải pháp được áp dụng là nguyên tắc ghi trước, thông báo sau. Trạng thái, tin nhắn phản hồi và phiếu chuyển tiếp được ghi trong cùng một giao dịch duy nhất; chỉ sau khi giao dịch commit thành công, hệ thống mới gửi thông báo cho khách hàng. Bước ghi được bảo vệ để không bị huỷ giữa chừng và được thử lại một lần nếu gặp lỗi. Trong trường hợp vẫn thất bại, khách hàng nhận được một câu trả lời không kèm bất kỳ cam kết nào thay cho thông báo chuyển tiếp.

**c) Xử lý tuần tự theo từng khách hàng.** Các lượt của cùng một khách hàng, kể cả khi khách mở nhiều tab trình duyệt, đều được xử lý tuần tự dưới một khoá và đánh thức theo thứ tự đến. Cơ chế này bảo đảm hai tin nhắn gửi liên tiếp không chạy chồng lên nhau và không tạo ra hai ca riêng biệt.

#### Mục 2.6.1 — Kho tri thức canonical trong repository · Đã rút gọn

*Nằm sau: «Kho tri thức canonical trong repository …»*

Khác với cách làm phổ biến hiện nay là quản lý tri thức thông qua chức năng tải tài liệu lên từ giao diện, đề tài lựa chọn tổ chức kho tri thức dưới dạng các tệp Markdown nằm trong repository và được phiên bản hoá bằng Git. Theo thiết kế này, cơ sở dữ liệu vector chỉ đóng vai trò là bản phái sinh, có thể dựng lại hoàn toàn từ repository bằng một lệnh duy nhất.

Quyết định thiết kế trên xuất phát từ ba lý do:

- Tri thức là một phần cấu thành sản phẩm nên cần được rà soát và theo dõi lịch sử thay đổi theo đúng cách mà mã nguồn được quản lý.

- Cơ chế xoá sạch rồi nạp lại toàn bộ loại bỏ triệt để lớp bài toán đồng bộ trạng thái giữa kho tệp và cơ sở dữ liệu vector.

- Chức năng tải tài liệu lên qua giao diện vẫn được duy trì nhưng chỉ mang tính bổ sung tạm thời chứ không phải nguồn chính thức. Các tài liệu tải lên theo đường này sẽ bị xoá sau lần nạp lại toàn bộ kế tiếp, và đây được xác định là hành vi đúng của hệ thống, đã được ghi rõ trong tài liệu thiết kế.

#### Mục 2.6.2 — Chia đoạn theo section · Đã rút gọn

*Nằm sau: «Chia đoạn theo section …»*

Thay vì cắt tài liệu theo số ký tự cố định, hệ thống thực hiện chia đoạn theo từng mục của tài liệu Markdown. Phần nội dung nằm trước tiêu đề mục đầu tiên được coi là đoạn mở bài của tài liệu.

Bên cạnh quy tắc chính nêu trên, hệ thống còn áp dụng bốn quy tắc bổ sung:

- Mỗi mục được giữ nguyên văn, bao gồm cả bảng biểu và danh sách đánh số, bởi việc cắt giữa chừng sẽ phá vỡ cấu trúc của bảng kích cỡ hoặc làm mất thứ tự các bước trong một quy trình xử lý.

- Chỉ những mục có độ dài vượt quá ngưỡng cho phép mới rơi về phương án cắt theo cửa sổ câu.

- Các mục được đánh dấu là nguyên khối luôn được giữ nguyên bất kể độ dài, do việc cắt giữa chừng sẽ làm mất thứ tự của các bước chẩn đoán trong quy trình.

- Các mục ghi chú nội bộ bị loại hoàn toàn khỏi chỉ mục. Đây là phần ghi chú quy trình dành riêng cho nhân viên, thường chứa những hành động mà cửa hàng sẽ thực hiện, chẳng hạn quy trình xử lý hoàn tiền theo phương thức thanh toán ban đầu, và hệ thống tự động không được phép cam kết những nội dung này với khách hàng. Việc chặn ngay tại nguồn dữ liệu cho độ tin cậy cao hơn nhiều so với việc chỉ đưa ra quy tắc cấm trích dẫn trong prompt.

#### Mục 2.6.3 — Mở rộng truy vấn (query-expansion) · Đã rút gọn

*Nằm sau: «Mở rộng truy vấn (query-expansion) …»*

Mở rộng truy vấn là kỹ thuật có đóng góp lớn nhất vào chất lượng truy hồi của hệ thống.

**Vấn đề đặt ra.** Khách hàng đặt câu hỏi bằng giọng nói thường ngày, trong khi kho tri thức được viết bằng giọng văn bản trang trọng theo đúng cách trình bày của một tài liệu chính sách. Vector biểu diễn của hai dạng diễn đạt này cách nhau khá xa trong không gian vector, dù cả hai cùng đề cập tới một nội dung.

**Giải pháp áp dụng.** Với mỗi tài liệu, ngoài các điểm vector tương ứng với thân tài liệu, hệ thống tạo thêm một điểm vector cho mỗi câu hỏi trong danh sách khai báo ở phần frontmatter. Vector của điểm bổ sung này chính là vector biểu diễn của câu hỏi, trong khi nội dung trả về vẫn là thân tài liệu đầy đủ.

**Kết quả đạt được.** Phép so khớp khi đó chuyển từ dạng so khớp giữa câu hỏi với văn bản sang dạng so khớp giữa câu hỏi với câu hỏi, cho điểm số cao hơn hẳn. Số liệu đo đạc cụ thể được trình bày chi tiết ở mục 3.5.

**Cơ chế định danh điểm ổn định.** Mỗi điểm vector có định danh được sinh tất định từ đường dẫn tài liệu và chỉ số đoạn. Nhờ vậy, thao tác nạp lại mang tính luỹ đẳng và việc chỉnh sửa một tệp không gây ảnh hưởng tới các tệp khác trong kho.

#### Mục 2.6.4 — Nạp lại theo cơ chế blue/green · Đã rút gọn

*Nằm sau: «Nạp lại theo cơ chế blue/green …»*

Phương án nạp lại đơn giản theo kiểu xoá collection rồi nạp lại từ đầu bộc lộ một hạn chế nghiêm trọng. Trong suốt thời gian nạp, khách hàng vẫn tiếp tục trao đổi với hệ thống, trong khi mọi thao tác truy hồi đều rơi vào một collection rỗng hoặc mới nạp dở, dẫn tới toàn bộ lượt hội thoại trong khoảng thời gian đó đều bị chuyển sang cho nhân viên.

**Giải pháp áp dụng.** Tên collection dùng để phục vụ truy vấn là một alias trỏ tới một collection vật lý có hậu tố thời gian. Quy trình nạp lại được thực hiện theo bốn bước:

- Tạo một collection vật lý mới.

- Nạp toàn bộ kho tri thức vào collection vừa tạo. Trong suốt quá trình này, khách hàng vẫn được phục vụ bằng bản dữ liệu cũ.

- Sau khi nạp xong mới thực hiện đổi hướng alias bằng một lời gọi duy nhất, tận dụng thao tác nguyên tử mà Qdrant cung cấp.

- Xoá collection cũ và quét dọn các collection không còn được tham chiếu.

Trong trường hợp quá trình nạp gặp lỗi giữa chừng, bản dựng dở sẽ bị loại bỏ, alias được giữ nguyên và lỗi được ném lên tầng trên để xử lý. Nhờ cơ chế này, tầng truy hồi không bao giờ gặp phải tình trạng collection rỗng.

#### Mục 2.7.3 — Luồng hỏi lại mã đơn và nối lượt · Đã rút gọn

*Nằm sau: «Hình 2.11. Biểu đồ tuần tự — Luồng hỏi lại mã đơn và nối …»*

Trong luồng này, có hai chi tiết kỹ thuật được bổ sung nhằm khắc phục hai lỗi phát sinh trong quá trình vận hành thực tế.

**Lỗi thứ nhất là trường hợp dãy số đứng một mình bị phân loại nhầm vào nhóm ngoài phạm vi.** Khi khách hàng chỉ gõ một dãy số là mã đơn hàng, mô hình có xu hướng xếp tin nhắn này vào nhãn ngoài phạm vi, từ đó phát cờ chặn và dẫn tới việc chuyển ca cho nhân viên một cách không cần thiết, mặc dù khách hàng vừa trả lời hoàn toàn đúng yêu cầu. Giải pháp được áp dụng là nhận diện ngữ cảnh nối lượt và khôi phục ý định một cách tất định, bỏ qua hoàn toàn lời gọi mô hình ở bước này.

**Lỗi thứ hai là trường hợp truy hồi bằng dãy số cho điểm rất thấp.** Kết quả đo thực tế cho thấy độ tương tự cosine giữa một dãy số mã đơn với toàn bộ tài liệu trong kho chỉ đạt khoảng 0,253, khiến hệ thống phát cờ điểm truy hồi thấp và tiếp tục chuyển ca cho nhân viên một cách không cần thiết. Giải pháp được áp dụng là ở lượt nối, tác tử thứ hai thực hiện truy hồi bằng chính câu hỏi gốc của khách hàng, tức tin nhắn gần nhất không phải là dãy số đơn thuần, thay vì truy hồi bằng dãy số.

Bên cạnh hai chi tiết kỹ thuật trên, việc giữ đúng ý định gốc cũng là một yêu cầu nghiệp vụ. Khi khách hàng đặt vấn đề hoàn đơn thì lượt nối vẫn phải giữ nguyên ý định hoàn tiền để tiếp tục đi theo luồng xử lý nhạy cảm qua bước duyệt nháp, chứ không được hạ xuống thành ý định tra cứu trạng thái đơn hàng.

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Chi tiết các bảng …»*

Trước khi đi vào từng bảng cụ thể, cần nêu trước các lớp nền dùng chung mà mọi thực thể đều dựng trên đó. Tầng mô hình dữ liệu khai báo một lớp gốc của SQLAlchemy cùng hai lớp trộn cung cấp sẵn khoá chính và các mốc thời gian, nhờ đó các thuộc tính này không phải khai lại ở từng bảng. Vì vậy phần mô tả chi tiết của từng bảng phía sau chỉ liệt kê các thuộc tính riêng của bảng đó.

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.13. Cấu trúc dữ liệu chung (lớp nền Base, UUIDMixin và TimestampMixin) …»*

| **Thuộc tính** | **Kiểu dữ liệu** | **Ràng buộc**                                         | **Mô tả**                                                                                                                                                                                 |
|----------------|------------------|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id             | UUID             | Khoá chính, sinh phía ứng dụng bằng `uuid4`           | Do `UUIDMixin` cấp. Khoá được sinh ở phía ứng dụng để hệ thống biết trước định danh của tin nhắn ngay trước khi giao dịch được commit, kịp gắn định danh đó vào các dòng nhật ký kiểm toán thuộc cùng một lượt |
| created_at     | TIMESTAMPTZ      | NOT NULL, server_default now()                        | Do `TimestampMixin` cấp. Thời điểm tạo bản ghi                                                                                                                                            |
| updated_at     | TIMESTAMPTZ      | NOT NULL, server_default now(), onupdate now()        | Do `TimestampMixin` cấp. Thời điểm cập nhật gần nhất                                                                                                                                      |

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.13. Cấu trúc dữ liệu chung (lớp nền Base, UUIDMixin và TimestampMixin) …»*

Phạm vi áp dụng của hai lớp trộn trên không đồng đều. Lớp `UUIDMixin` được dùng cho sáu lớp thực thể gồm `User`, `Conversation`, `Message`, `Order`, `AuditLog` và `KnowledgeDocument`, trong khi lớp `TimestampMixin` chỉ được lớp `Conversation` sử dụng, bởi đây là thực thể duy nhất có vòng đời dài và cần theo dõi mốc cập nhật gần nhất; các bảng còn lại tự khai báo riêng cột thời điểm tạo khi cần. Hai lớp `GateConfig` và `GateIntentRule` cố ý không dùng `UUIDMixin`: bảng cấu hình toàn cục chỉ có duy nhất một dòng nên khoá chính là số nguyên luôn bằng 1, còn bảng luật theo ý định lấy chính tên của ý định làm khoá chính. Đây là hai bảng cấu hình mà khoá của chúng mang ý nghĩa nghiệp vụ, nên không cần thêm một định danh sinh máy.

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.15. Bảng conversation …»*

| **Tên thuộc tính**       | **Kiểu dữ liệu** | **Ràng buộc**                                              | **Mô tả**                                           |
|--------------------------|------------------|------------------------------------------------------------|-----------------------------------------------------|
| id                       | UUID             | Khoá chính                                                 | Định danh                                           |
| customer_id              | UUID             | nullable, FK → user.id, ON DELETE SET NULL, index           | Khách sở hữu; NULL cho khách vãng lai               |
| customer_identifier      | VARCHAR(255)     | nullable                                                   | Nhãn nhận dạng khách vãng lai khi chưa có tài khoản |
| status                   | VARCHAR(32)      | NOT NULL, default NEW, index                               | Trạng thái canonical                                |
| current_intent           | VARCHAR(64)      | nullable                                                   | Ý định hiện tại                                     |
| entities                 | JSONB            | NOT NULL, default rỗng                                     | Thực thể tích luỹ                                   |
| confidence               | FLOAT            | nullable                                                   | Độ tin cậy                                          |
| uncertainty_flags        | JSONB            | NOT NULL, default rỗng                                     | Các cờ bất định                                     |
| escalation_reason        | TEXT             | nullable                                                   | Lý do chuyển tiếp                                   |
| priority, severity       | VARCHAR(16)      | nullable                                                   | Mức ưu tiên và nghiêm trọng                         |
| escalation_card          | JSONB            | nullable                                                   | Thẻ ngữ cảnh chuyển tiếp                            |
| assigned_admin_id        | UUID             | nullable, không khoá ngoại cứng                            | Quản trị viên đang xử lý                            |
| last_message_at          | TIMESTAMPTZ      | nullable                                                   | Thời điểm tin cuối                                  |
| auto_resolve_reminded_at | TIMESTAMPTZ      | nullable                                                   | Mốc đã gửi tin nhắc; NULL = chưa nhắc               |
| created_at, updated_at   | TIMESTAMPTZ      | NOT NULL, server_default now(), updated_at có onupdate now() | Do `TimestampMixin` cấp                             |

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.16. Bảng message …»*

| **Tên thuộc tính** | **Kiểu dữ liệu**   | **Ràng buộc**                                                                            | **Mô tả**                                              |
|--------------------|--------------------|------------------------------------------------------------------------------------------|--------------------------------------------------------|
| id                 | UUID               | Khoá chính                                                                               | Định danh                                              |
| conversation_id    | UUID               | NOT NULL, FK → conversation.id, ON DELETE CASCADE, index                                 | Hội thoại chứa tin                                     |
| sender             | VARCHAR(16)        | NOT NULL                                                                                 | customer / ai / admin                                  |
| content            | TEXT               | NOT NULL                                                                                 | Nội dung                                               |
| intent, confidence | VARCHAR(64), FLOAT | nullable                                                                                 | Siêu dữ liệu phân loại                                 |
| client_msg_id      | VARCHAR(64)        | nullable; chỉ mục duy nhất từng phần `uq_message_conversation_client_msg_id` trên cặp (conversation_id, client_msg_id) với điều kiện client_msg_id IS NOT NULL | Định danh do client sinh, dùng chống trùng khi gửi lại |
| created_at         | TIMESTAMPTZ        | NOT NULL, server_default now()                                                           | Thời điểm                                              |

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.16. Bảng message …»*

Bảng này được thiết lập một chỉ mục duy nhất từng phần trên cặp cột định danh hội thoại và định danh tin nhắn phía client, với điều kiện áp dụng khi định danh phía client không rỗng. Việc vi phạm chỉ mục này chính là tín hiệu cho biết tin nhắn đã được gửi lại. Đây là cơ chế chống trùng bền vững ở tầng cơ sở dữ liệu, bổ sung cho lớp chống trùng nằm trong bộ nhớ tiến trình.

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.17. Bảng order …»*

| **Tên thuộc tính**                                 | **Kiểu dữ liệu**         | **Ràng buộc**                                              | **Mô tả**                             |
|----------------------------------------------------|--------------------------|------------------------------------------------------------|---------------------------------------|
| id                                                 | UUID                     | Khoá chính                                                 | Định danh                             |
| order_code                                         | VARCHAR(32)              | NOT NULL, UNIQUE, index                                    | Mã khách đọc cho shop — chỉ chữ số    |
| customer_id                                        | UUID                     | NOT NULL, FK → user.id, ON DELETE CASCADE, index           | Chủ đơn — khoá của tra cứu có phạm vi |
| status                                             | VARCHAR(16)              | NOT NULL                                                   | Trạng thái đơn                        |
| items_summary, region                              | VARCHAR(255), VARCHAR(64)| NOT NULL                                                   | Tóm tắt sản phẩm, khu vực giao        |
| ordered_at, shipped_at, delivered_at, cancelled_at | TIMESTAMPTZ              | ordered_at NOT NULL; ba mốc còn lại nullable               | Các mốc tách riêng theo trạng thái    |
| estimated_delivery                                 | TIMESTAMPTZ              | nullable                                                   | Ngày dự kiến giao                     |
| tracking_code                                      | VARCHAR(64)              | nullable                                                   | Mã vận đơn                            |
| created_at                                         | TIMESTAMPTZ              | NOT NULL, server_default now()                             | Thời điểm bản ghi đơn được tạo        |

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.17. Bảng order …»*

Bảng dữ liệu đơn hàng gắn với hai quyết định thiết kế đáng chú ý:

- **Mã đơn hàng chỉ gồm chữ số**, khớp với quy tắc của tầng trích xuất thực thể. Nếu cho phép mã đơn chứa cả chữ cái, biểu thức chính quy sẽ không trích xuất được trong trường hợp mô hình không khả dụng, qua đó phá vỡ bất biến về việc mã đơn hàng không bao giờ bị thất lạc.

- **Các mốc thời gian được tách thành các cột riêng** thay vì gộp vào một cột chung. Với đơn hàng đã giao, hệ thống phải nêu được ngày giao thực tế chứ không phải ngày dự kiến giao, bởi việc nhầm lẫn giữa hai mốc thời gian này khi trao đổi với khách hàng là cung cấp thông tin sai sự thật.

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.18. Bảng audit_log …»*

| **Tên thuộc tính**          | **Kiểu dữ liệu** | **Ràng buộc**                                       | **Mô tả**                                                              |
|-----------------------------|------------------|-----------------------------------------------------|------------------------------------------------------------------------|
| id                          | UUID             | Khoá chính                                          | Định danh                                                              |
| conversation_id, message_id | UUID             | nullable, không khoá ngoại cứng, index trên conversation_id | Không khoá ngoại cứng — nhật ký phải bền cả khi hội thoại bị xoá |
| turn_id                     | UUID             | nullable, index                                     | Khoá gom một lượt — mọi dòng cùng lượt chia sẻ giá trị này             |
| duration_ms                 | INTEGER          | nullable                                            | Thời gian; ý nghĩa khác nhau theo loại dòng                            |
| node                        | VARCHAR(32)      | nullable                                            | customer / intent / knowledge / decision / response / delivery / admin |
| action                      | VARCHAR(64)      | nullable                                            | Hành động                                                              |
| confidence                  | FLOAT            | nullable                                            | Độ tin cậy của bước                                                    |
| uncertainty_flags           | JSONB            | NOT NULL, default rỗng                              | Cờ của bước                                                            |
| escalation_reason           | TEXT             | nullable                                            | Lý do                                                                  |
| detail                      | JSONB            | NOT NULL, default rỗng                              | Chi tiết bổ sung                                                       |
| created_at                  | TIMESTAMPTZ      | NOT NULL, server_default now(), index               | Mọi truy vấn báo cáo lọc theo khoảng thời gian                         |

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.18. Bảng audit_log …»*

Mỗi lượt hội thoại của khách hàng sinh ra sáu dòng nhật ký cùng chia sẻ một khoá lượt, lần lượt là dòng tiếp nhận tin nhắn khách, bốn dòng tương ứng với bốn nút của pipeline và dòng ghi nhận kết cục giao phản hồi. Cần lưu ý rằng trường thời gian xử lý mang ý nghĩa khác nhau giữa các loại dòng và không được cộng gộp với nhau:

- Đối với dòng của các nút, trường này ghi thời gian chạy của riêng nút đó.

- Đối với dòng ghi nhận kết cục giao phản hồi, trường này ghi thời gian xử lý đầu cuối phía máy chủ, tính từ lúc hệ thống đọc được tin nhắn, bao gồm cả thời gian xếp hàng chờ, cho tới khi khung phản hồi được trao cho socket. Đây mới là con số dùng để đối chiếu với yêu cầu NFR-1, chứ không phải tổng thời gian của bốn nút, bởi tổng này bỏ sót toàn bộ phần nhập xuất nằm ngoài pipeline.

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.19. Bảng knowledge_document …»*

| **Tên thuộc tính**     | **Kiểu dữ liệu** | **Ràng buộc**                       | **Mô tả**                                                                                    |
|------------------------|------------------|-------------------------------------|----------------------------------------------------------------------------------------------|
| id                     | UUID             | Khoá chính                          | Định danh                                                                                    |
| title                  | VARCHAR(255)     | NOT NULL                            | Tên hiển thị của tài liệu                                                                    |
| source_type            | VARCHAR(16)      | nullable                            | Định dạng gốc: pdf / docx / txt / md                                                         |
| file_ref               | VARCHAR(512)     | UNIQUE, nullable                    | Khoá ổn định của tài liệu, trùng với payload.source trong Qdrant (ví dụ faq/gia-san-pham.md) |
| doc_type               | VARCHAR(16)      | nullable                            | Thư mục kho tri thức (faq / case / reference / promotion) hoặc upload với tài liệu ad-hoc    |
| intent                 | VARCHAR(64)      | nullable                            | Nhãn ý định khai trong frontmatter; NULL với tài liệu upload                                 |
| chunks                 | INTEGER          | NOT NULL, default 0                 | Số điểm vector đã ghi lên Qdrant                                                             |
| metadata               | JSONB            | NOT NULL, default rỗng              | Siêu dữ liệu bổ sung                                                                         |
| status                 | VARCHAR(16)      | NOT NULL, default pending           | indexed / pending                                                                            |
| embedding_ref          | VARCHAR(255)     | nullable                            | Tham chiếu Qdrant                                                                            |
| created_at, indexed_at | TIMESTAMPTZ      | created_at NOT NULL, server_default now(); indexed_at nullable | Thời điểm tạo và thời điểm index xong                                    |

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.19. Bảng knowledge_document …»*

Bảng này đóng vai trò là sổ hiển thị cho màn hình Quản lý tri thức chứ không phải nguồn dữ liệu chính thức. Nguồn chính thức vẫn là thư mục `knowledge/` trong repository kết hợp với dữ liệu trên Qdrant, còn bảng này được dựng lại sau mỗi lần nạp toàn bộ kho tri thức. Cột phân loại tài liệu là nơi phân biệt giữa tài liệu chính thức với tài liệu tải lên tạm thời, trong đó nhóm thứ hai sẽ bị xoá ở lần nạp lại kế tiếp.

Cấu hình cổng được lưu trong hai bảng, gồm một bảng cấu hình toàn cục chỉ có duy nhất một dòng và một bảng luật với một dòng cho mỗi ý định. Đây cũng là hai bảng duy nhất không dùng lớp trộn sinh khoá UUID đã nêu ở Bảng 2.13. Dưới đây là bảng mô tả các thuộc tính của hai bảng cấu hình cổng (Bảng 2.20).

#### Mục 2.8.2 — Chi tiết các bảng · Đã rút gọn

*Nằm sau: «Bảng 2.20. Bảng cấu hình cổng …»*

| **Bảng**         | **Tên thuộc tính**         | **Kiểu dữ liệu** | **Ràng buộc**                             | **Mô tả**                                              |
|------------------|----------------------------|------------------|-------------------------------------------|--------------------------------------------------------|
| gate_config      | id                         | INTEGER          | Khoá chính, không tự tăng, luôn bằng 1    | Bảng chỉ có duy nhất một dòng                          |
| gate_config      | auto_reply_enabled         | BOOLEAN          | NOT NULL, default true                    | Công tắc trả lời tự động ở mức hệ thống                |
| gate_config      | auto_resolve_enabled       | BOOLEAN          | NOT NULL, default true                    | Công tắc tự đóng ca ở mức hệ thống                     |
| gate_config      | auto_resolve_minutes       | INTEGER          | NOT NULL, default 30                      | Ngưỡng im lặng thứ nhất, tính bằng phút — gửi tin nhắc |
| gate_config      | auto_resolve_grace_minutes | INTEGER          | NOT NULL, default 15                      | Ngưỡng thứ hai kể từ lúc nhắc, tính bằng phút — đóng ca |
| gate_intent_rule | intent                     | VARCHAR(64)      | Khoá chính                                | Tên ý định — khoá mang ý nghĩa nghiệp vụ               |
| gate_intent_rule | label                      | VARCHAR(64)      | NOT NULL                                  | Nhãn hiển thị của ý định trên giao diện                |
| gate_intent_rule | sensitive                  | BOOLEAN          | NOT NULL, default false                   | Chỉ dùng để hiển thị nhãn, không chi phối logic        |
| gate_intent_rule | send_directly              | BOOLEAN          | NOT NULL, default true                    | true là gửi thẳng, false là giữ nháp chờ duyệt         |

#### Mục 2.8.3 — Sơ đồ lớp miền dữ liệu · Đã rút gọn

*Nằm sau: «Sơ đồ lớp miền dữ liệu …»*

Tầng mô hình dữ liệu của backend được xây bằng SQLAlchemy 2 theo phong cách khai báo, nên các bảng ở mục 2.8.2 tồn tại trong mã nguồn dưới dạng lớp Python. Sơ đồ lớp của mục này trình bày quan hệ kế thừa và quan hệ liên kết giữa các lớp đó.

Điểm cần chú ý đầu tiên là ba lớp nền dùng chung đã trình bày ở Bảng 2.13. Lớp `Base` là lớp khai báo gốc của SQLAlchemy; lớp `UUIDMixin` cung cấp khoá chính kiểu UUID được sinh ở phía ứng dụng, áp dụng cho sáu lớp thực thể chứ không phải cho mọi lớp, bởi hai lớp cấu hình `GateConfig` và `GateIntentRule` dùng khoá mang ý nghĩa nghiệp vụ; lớp `TimestampMixin` cung cấp cặp mốc thời điểm tạo và thời điểm cập nhật gần nhất, và chỉ lớp `Conversation` sử dụng lớp trộn này. Việc sinh khoá ở phía ứng dụng thay vì để cơ sở dữ liệu tự tăng là một lựa chọn có chủ đích, bởi hệ thống cần biết trước định danh của tin nhắn ngay tại thời điểm tạo đối tượng, trước cả khi giao dịch được commit, để kịp gắn định danh đó vào các dòng nhật ký kiểm toán thuộc cùng một lượt xử lý.

Tám lớp thực thể được chia thành ba nhóm theo vai trò. Nhóm nghiệp vụ hội thoại gồm ba lớp `User`, `Conversation` và `Message` liên kết với nhau theo quan hệ một nhiều; lớp `Order` gắn với lớp `User` thông qua khoá chủ đơn, đây chính là cơ sở cho ràng buộc khách hàng chỉ tra cứu được đơn hàng của chính mình. Nhóm cấu hình gồm lớp `GateConfig`, là một bản ghi duy nhất giữ hai công tắc mức hệ thống cùng hai ngưỡng thời gian tự đóng ca, và lớp `GateIntentRule` có khoá chính chính là tên của ý định. Nhóm hỗ trợ gồm hai lớp `AuditLog` và `KnowledgeDocument`. Cả hai lớp này đều cố ý không khai báo khoá ngoại cứng tới các lớp khác, bởi nhật ký kiểm toán phải tồn tại được ngay cả khi hội thoại bị xoá, còn sổ tài liệu chỉ là bản chiếu của kho tri thức trong repository chứ không phải nguồn dữ liệu chính thức.

Dưới đây là sơ đồ lớp tổng hợp của tầng mô hình dữ liệu, gồm ba lớp nền dùng chung và tám lớp thực thể chia theo ba nhóm vai trò (Hình 2.15).

Hình 2.15. Sơ đồ lớp miền dữ liệu

Tầng xử lý phía trên không được mô hình hoá bằng lớp đối tượng. Bốn tác tử được cài đặt dưới dạng bốn hàm bất đồng bộ nhận vào và trả về cấu trúc trạng thái hội thoại, vốn là một kiểu `TypedDict` chứ không phải một lớp đối tượng, còn tầng dịch vụ gồm các hàm cấp module không giữ trạng thái. Đây là một lựa chọn thiết kế có cân nhắc chứ không phải thiếu sót, bởi một hàm thuần nhận trạng thái vào và trả trạng thái ra dễ kiểm thử hơn hẳn so với một đối tượng có vòng đời riêng, đồng thời cách tổ chức này khớp trực tiếp với mô hình nút của LangGraph. Chính vì vậy, quan hệ giữa các thành phần của tầng xử lý được biểu diễn bằng sơ đồ luồng ở Hình 2.4 thay vì bằng sơ đồ lớp.

Bên cạnh sơ đồ tổng hợp ở Hình 2.15, sơ đồ lớp tách theo từng miền dữ liệu được trình bày ở phần Phụ lục, tại Hình PL.5 và Hình PL.6.

#### Mục 2.9.1 — Xác thực và phân quyền · Đã rút gọn

*Nằm sau: «Xác thực và phân quyền …»*

**Cơ chế xác thực.** Mật khẩu người dùng được băm bằng thuật toán bcrypt. Thư viện bcrypt được sử dụng trực tiếp thay vì thông qua lớp bao trung gian, do lớp bao phổ biến hiện nay đã ngừng bảo trì và phát sinh xung đột với các phiên bản bcrypt mới. Chuỗi mật khẩu được cắt ở tầng byte trước khi băm nhằm bảo đảm thao tác băm và thao tác xác minh luôn nhất quán với nhau.

Bên cạnh đó, khi địa chỉ thư điện tử được gửi lên không tồn tại trong hệ thống, tầng xác thực vẫn thực hiện một phép băm giả trên một chuỗi băm dựng sẵn thay vì trả lời ngay. Nhờ vậy thời gian phản hồi của hai trường hợp gần như bằng nhau và kẻ tấn công không thể dựa vào độ trễ để suy ra địa chỉ nào đã có tài khoản. Do bcrypt là phép tính tốn CPU, cả thao tác băm và thao tác xác minh đều được đẩy sang nhóm luồng phụ để không chặn vòng lặp sự kiện của tiến trình bất đồng bộ.

**Cơ chế mã thông báo.** Hệ thống sử dụng JWT ký bằng thuật toán HS256, tách thành hai loại:

- **Mã thông báo truy cập:** Có thời hạn ngắn, mặc định là 30 phút, chứa định danh người dùng, vai trò, loại mã thông báo cùng hai mốc thời gian phát hành và hết hạn.

- **Mã thông báo làm mới:** Có thời hạn dài, mặc định là 7 ngày, chứa định danh người dùng, loại mã thông báo và cũng kèm đầy đủ hai mốc thời gian phát hành và hết hạn.

Hai thời hạn nêu trên đều đọc từ cấu hình chứ không nằm cứng trong mã nguồn, thông qua hai biến `jwt_access_expire_minutes` và `jwt_refresh_expire_days`. Hàm giải mã kiểm tra trường loại mã thông báo nhằm bảo đảm một mã thông báo làm mới không thể được dùng thay cho mã thông báo truy cập. Với mã thông báo sai định dạng hoặc đã hết hạn, hàm trả về giá trị rỗng thay vì ném ngoại lệ, nhờ đó tầng gọi xử lý trường hợp không hợp lệ bằng nhánh điều kiện thông thường.

**Lưu trữ mã thông báo trong httpOnly cookie.** Cả hai mã thông báo đều được đặt vào cookie đánh dấu httpOnly với hai tên `access_token` và `refresh_token`, trong đó cookie làm mới có thời gian sống tính bằng số ngày cấu hình nhân với số giây của một ngày. Đây là điểm khác biệt so với cách làm phổ biến là lưu mã thông báo trong bộ nhớ cục bộ của trình duyệt. Cookie đánh dấu httpOnly không đọc được từ mã JavaScript đang chạy trên trang, nên một lỗ hổng chèn mã phía giao diện không lấy được mã thông báo của người dùng; đổi lại, hệ thống phải tự xử lý hai thuộc tính `SameSite` và `Secure` cho tình huống triển khai khác tên miền.

Để đáp ứng yêu cầu NFR-10 về việc mọi tham số vận hành đều cấu hình được qua biến môi trường, thuộc tính của cookie được khai báo bằng ba biến gồm `COOKIE_SECURE` mặc định tắt, `COOKIE_SAMESITE` mặc định là `lax` và `COOKIE_DOMAIN` mặc định để rỗng. Trên nền ba biến này, cấu hình suy dẫn ra hai giá trị thực sự được dùng khi đặt cookie:

- **Giá trị `SameSite` hiệu dụng:** Nếu môi trường đang chạy là môi trường triển khai thật và giá trị khai báo vẫn là `lax`, hệ thống tự chuyển thành `none`. Lý do là ở môi trường triển khai, backend và frontend nằm trên hai tên miền khác nhau, mà cookie `lax` không được gửi kèm trong các yêu cầu khác tên miền nên toàn bộ phiên làm việc sẽ mất hiệu lực.

- **Giá trị `Secure` hiệu dụng:** Nếu môi trường đang chạy là môi trường triển khai thật, hoặc giá trị `SameSite` hiệu dụng là `none`, thuộc tính này bắt buộc được bật. Đây vừa là yêu cầu của trình duyệt đối với cookie khác tên miền, vừa bảo đảm cookie chỉ đi trên kênh đã mã hoá.

Nhờ hai giá trị suy dẫn nêu trên, cùng một mã nguồn chạy đúng ở cả môi trường phát triển, nơi giao diện và backend cùng nằm trên máy cục bộ qua giao thức HTTP, lẫn môi trường triển khai thật qua HTTPS và khác tên miền, mà không cần sửa mã.

**Luồng làm mới phiên.** Tầng xác thực cung cấp bốn điểm cuối phục vụ vòng đời phiên làm việc, gồm `POST /api/auth/register` trả về mã 201, `POST /api/auth/login`, `POST /api/auth/refresh` và `POST /api/auth/logout`. Điểm cuối làm mới đọc mã thông báo làm mới từ cookie trước, và chỉ khi không có cookie mới đọc tiếp từ thân yêu cầu; sau khi xác minh, điểm cuối này phát lại cả hai mã thông báo mới rồi ghi lại vào cookie, tức là mã thông báo làm mới cũng được luân chuyển ở mỗi lần làm mới thay vì dùng lại suốt bảy ngày. Trường hợp mã thông báo làm mới sai hoặc đã hết hạn, hệ thống trả về mã lỗi 401. Điểm cuối đăng xuất xoá cả hai cookie.

Phía giao diện, mọi yêu cầu đều được gửi kèm thông tin đăng nhập của phiên để trình duyệt tự đính cookie. Lớp bọc hàm gọi mạng cài đặt cơ chế làm mới trong suốt: khi gặp mã lỗi 401, lớp này gọi điểm cuối làm mới rồi chạy lại đúng yêu cầu ban đầu một lần duy nhất, nhờ đó người dùng không bị đăng xuất mỗi ba mươi phút. Một biến giữ lời hứa làm mới đang chạy bảo đảm nhiều yêu cầu cùng nhận mã 401 trong một thời điểm chỉ kích hoạt đúng một lần làm mới thay vì gọi song song nhiều lần. Hai hàm đọc và ghi mã thông báo của phiên bản trước được giữ lại nhưng đánh dấu là không còn dùng và không thực hiện thao tác nào, bởi mã thông báo đã không còn nằm trong bộ nhớ cục bộ của trình duyệt.

**Cơ chế phân quyền.** Việc kiểm tra vai trò được thực hiện tại tầng dependency của FastAPI. Riêng với các kênh WebSocket, mã thông báo cũng được đọc từ cookie `access_token` trước, và tham số truy vấn chỉ là phương án dự phòng cho những client không gửi được cookie. Vai trò được đọc lại từ cơ sở dữ liệu ở mỗi lần kết nối thay vì tin vào trường vai trò lưu trong mã thông báo, còn kênh WebSocket quản trị đọc lại vai trò ở mỗi tin nhắn, nhằm bảo đảm thao tác thu hồi quyền có hiệu lực ngay lập tức, kể cả khi quản trị viên bị hạ quyền giữa phiên.

Hai tình huống lỗi khi xác thực kênh WebSocket được phân biệt rạch ròi bằng hai mã đóng kết nối khác nhau. Mã thông báo thiếu, sai, hết hạn, sai vai trò hoặc trỏ tới tài khoản đã bị xoá thì kết nối bị đóng với mã tự định nghĩa 4401, và giao diện hiểu đây là phiên đã hết hiệu lực nên dừng nối lại và đưa người dùng về trang đăng nhập. Ngược lại, khi bản thân mã thông báo vẫn hợp lệ nhưng cơ sở dữ liệu gặp lỗi đúng lúc xác minh quyền, kết nối bị đóng với mã chuẩn 1011 dành cho lỗi phía máy chủ, để giao diện tiếp tục nối lại theo cơ chế chờ tăng dần. Nếu dùng mã 4401 cho cả hai, một sự cố cơ sở dữ liệu tạm thời sẽ bị giao diện hiểu nhầm thành hết phiên và người dùng bị đăng xuất oan.

**Bảo vệ dữ liệu cá nhân.** Định danh tài khoản nhân viên không bao giờ được gửi xuống phía khách hàng. Bên cạnh đó, câu thông báo không tìm thấy đơn hàng được dùng chung cho cả trường hợp mã đơn không tồn tại lẫn trường hợp mã đơn thuộc về khách hàng khác, nhờ đó hệ thống không để lộ sự tồn tại đơn hàng của người khác.

Đặc tả use case đăng ký tài khoản và đăng nhập, cùng biểu đồ tuần tự của luồng đăng nhập và luồng làm mới phiên, được trình bày ở phần Phụ lục, lần lượt tại Bảng PL.5, Bảng PL.6 và Hình PL.3.

#### Mục 2.9.3 — Bốn lớp phòng thủ chống chèn chỉ dẫn (prompt injection) · Đã rút gọn

*Nằm sau: «Bốn lớp phòng thủ chống chèn chỉ dẫn (prompt injection) …»*

Đây là phần thiết kế bảo mật mang tính đặc thù nhất đối với một hệ thống ứng dụng mô hình ngôn ngữ lớn. Hệ thống phải đối mặt với hai hướng tấn công, gồm tấn công trực tiếp khi khách hàng gõ chỉ dẫn vào tin nhắn và tấn công gián tiếp khi chỉ dẫn được giấu trong tài liệu tri thức do người dùng tải lên.

**Lớp A: chuẩn hoá và giới hạn tại biên hệ thống.** Mọi văn bản không tin cậy đều phải đi qua một cửa duy nhất trước khi vào pipeline xử lý, tại đó hệ thống thực hiện ba thao tác:

- Chuẩn hoá Unicode theo dạng NFKC nhằm gộp các biến thể hình thức như ký tự toàn chiều rộng hay ký tự tương thích về dạng chuẩn, qua đó chặn thủ thuật né tránh bằng các ký tự có hình dạng tương tự.

- Loại bỏ ký tự điều khiển và ký tự vô hình như ký tự độ rộng bằng không hay ký tự đảo chiều hiển thị, vốn là nơi kẻ tấn công có thể giấu chỉ dẫn mà người đọc nhật ký không phát hiện được. Riêng ký tự xuống dòng và ký tự tab được giữ lại do đây là khoảng trắng thật của văn bản.

- Gộp các khoảng trắng liên tiếp và cắt độ dài văn bản theo giới hạn cấu hình.

Thiết kế có ghi chú rõ rằng lớp này không đóng vai trò một bộ phát hiện tấn công. Hệ thống không phát cờ, không đếm số lần và không chặn tin nhắn tại lớp này. Năng lực phòng thủ thực sự nằm ở cấu trúc của hệ thống chứ không nằm ở khả năng nhận diện mẫu tấn công.

**Lớp B: phân định ranh giới giữa dữ liệu và chỉ dẫn.** Tin nhắn của khách hàng cùng từng đoạn tri thức đều được bọc trong các thẻ dữ liệu riêng, kèm theo quy tắc trong prompt hệ thống nói rõ rằng nội dung nằm trong thẻ là dữ liệu để đọc chứ không phải chỉ dẫn để thực thi.

Cơ chế thẻ chỉ phát huy tác dụng khi nội dung bên trong không có khả năng tự đóng thẻ. Do đó, mọi thẻ ranh giới xuất hiện trong nội dung không tin cậy đều bị vô hiệu hoá bằng cách loại bỏ dấu ngoặc nhọn nhưng vẫn giữ lại phần chữ, nhờ đó người đọc nhật ký vẫn thấy được dấu vết của thao tác can thiệp. Cơ chế này xử lý được cả thẻ có thuộc tính lẫn thẻ lồng nhau.

**Lớp C: quy tắc chống chèn chỉ dẫn trong prompt hệ thống.** Cả tác tử thứ nhất và tác tử thứ tư đều được trang bị một khối quy tắc tường minh gồm năm nội dung:

- Nội dung nằm trong thẻ dữ liệu, bao gồm cả lịch sử hội thoại và khối dữ liệu đơn hàng, đều là dữ liệu để đọc chứ không phải chỉ dẫn để thực thi.

- Mô hình không được tiết lộ, nhắc lại, tóm tắt hay dịch nội dung của prompt hệ thống, kể cả khi người dùng tự xưng là lập trình viên hoặc khẳng định đang thực hiện kiểm thử.

- Mô hình không được thay đổi vai trò, nhân cách hay chế độ hoạt động theo yêu cầu của người dùng.

- Nếu bên trong đoạn tri thức có chứa câu mang tính ra lệnh, mô hình bỏ qua đúng câu đó và chỉ sử dụng phần nội dung thông tin còn lại.

- Mô hình chỉ thực hiện nhiệm vụ chăm sóc khách hàng; mọi yêu cầu chuyển mục đích sử dụng đều bị từ chối một cách lịch sự.

**Lớp D: làm sạch tài liệu tải lên.** Lớp này chỉ áp dụng cho đường tải tài liệu không chính thức, bởi các tài liệu Markdown trong repository do nhóm phát triển biên soạn nên không đi qua đường này. Các câu mang tính ra lệnh rõ ràng sẽ được thay bằng một dấu vết thay vì bị xoá âm thầm, nhằm giúp người đọc đoạn tri thức nhận biết được tài liệu đã bị can thiệp.

Bộ mẫu nhận diện được thiết kế theo hướng hẹp có chủ đích, chấp nhận bỏ sót một số trường hợp để tránh cắt nhầm tri thức thật của cửa hàng. Thao tác cắt được thực hiện theo từng câu chứ không theo dòng hay theo đoạn, nhằm bảo đảm một câu chèn vào giữa đoạn không kéo theo việc loại bỏ cả đoạn tri thức hợp lệ.

#### Mục 2.9.3 — Bốn lớp phòng thủ chống chèn chỉ dẫn (prompt injection) · Đã rút gọn

*Nằm sau: «D — Làm sạch tài liệu Đường upload Chèn gián tiếp qua tài liệu …»*

Cần nhấn mạnh rằng bốn lớp phòng thủ nêu trên mới chỉ là phần bề mặt. Năng lực phòng thủ có ý nghĩa quyết định nằm ở chính cấu trúc của hệ thống. Giả sử kẻ tấn công thao túng được hoàn toàn mô hình ngôn ngữ, tác tử thứ ba vẫn định tuyến dựa trên tập cờ chứ không đọc nội dung do mô hình sinh ra, thao tác tra cứu đơn hàng vẫn bị giới hạn theo định danh của khách hàng đang đăng nhập, và tác tử thứ tư vẫn không có bất kỳ đường nào để tự chuyển ca. Như vậy, việc thao túng được mô hình không đồng nghĩa với việc kẻ tấn công giành thêm được đặc quyền nào ở tầng hệ thống.

#### Mục 2.10 — Tổng kết chương · Đã rút gọn

*Nằm sau: «Tổng kết chương …»*

Chương 2 đã trình bày toàn bộ thiết kế của hệ thống, bắt đầu từ bốn trụ cột làm nền tảng cho mọi quyết định kỹ thuật, bao gồm luồng xử lý cố định để bảo đảm tính dự đoán và khả năng kiểm toán, tự trị có giới hạn ở tầng tác tử, an toàn trước các tình huống ngoài dự kiến, và cải thiện dần dưới sự phê duyệt của con người.

Trên nền tảng đó, chương đã đặc tả chi tiết bốn tác tử cùng cấu trúc trạng thái điều phối dùng chung. Ba quyết định thiết kế chi phối phần còn lại của hệ thống lần lượt là: tác tử ra quyết định hoạt động hoàn toàn tất định và định tuyến dựa trên tập cờ thay vì gộp hai thang độ tin cậy; toàn bộ tin nhắn gửi tới khách hàng đều phát ra từ một điểm duy nhất; và cổng cấu hình của con người không có bất kỳ đường nào để ghi đè lên logic an toàn.

Bên cạnh đó, chương cũng đã trình bày thiết kế kho tri thức theo hướng lưu trữ chính thức trong repository kèm kỹ thuật mở rộng truy vấn và cơ chế nạp lại không gián đoạn, các biểu đồ tuần tự cho năm luồng nghiệp vụ chính, thiết kế cơ sở dữ liệu gồm tám bảng cùng các quyết định về khoá phạm vi tra cứu đơn hàng và cấu trúc nhật ký kiểm toán, cũng như thiết kế bảo mật với bốn lớp phòng thủ chống tấn công chèn chỉ dẫn.

Những quyết định kiến trúc và các mô hình thiết kế nêu trên là tiền đề để triển khai thực nghiệm ở Chương 3, trong đó sẽ trình bày môi trường và công cụ phát triển, các thách thức kỹ thuật thực tế phát sinh cùng giải pháp tương ứng, giao diện người dùng và kết quả đo đạc trên hệ thống chạy thật nhằm kiểm chứng các quyết định thiết kế đã nêu.

### Chương 3 — Thực nghiệm và triển khai (`chuong-3.md`)

#### Mục 3.1.1 — Môi trường phát triển · Đã rút gọn

*Nằm sau: «└── PRD.md · CLAUDE.md · Makefile · README.md …»*

Bên cạnh cấu hình nền nêu trên, quá trình phát triển còn dựa vào bốn nhóm công cụ hỗ trợ sau.

**Môi trường lập trình tích hợp.** *(Điền IDE thực tế sử dụng.)* Do dự án được tổ chức theo mô hình monorepo chứa cả Python và TypeScript, môi trường lập trình cần mở được đồng thời hai ngôn ngữ và nhận diện được các kiểu dữ liệu dùng chung khai báo trong `packages/shared-types`. Đây là nơi tập enum trạng thái hội thoại của phần back-end được đồng bộ sang TypeScript, vì vậy mọi sai lệch về kiểu tại vị trí này đều lan sang cả hai phía của hệ thống.

**Công cụ quản trị cơ sở dữ liệu.** *(Điền công cụ thực tế, có thể là DBeaver, TablePlus, bảng điều khiển của Neon hoặc tiện ích tích hợp trong IDE.)* Công cụ này chủ yếu được dùng để kiểm tra trực tiếp ba nội dung trong quá trình gỡ lỗi, gồm giá trị cột trạng thái của hội thoại sau mỗi lượt, nội dung JSONB của phiếu chuyển tiếp và sáu dòng nhật ký kiểm toán có cùng khoá lượt. Việc kiểm tra ở tầng dữ liệu là cách nhanh nhất để phân biệt giữa lỗi hiển thị phía giao diện với lỗi ghi dữ liệu thật phía máy chủ.

**Công cụ thiết kế và mô hình hoá hệ thống.** Các sơ đồ trong Chương 2 được dựng bằng *(điền công cụ thực tế, có thể là draw.io, PlantUML hoặc công cụ tương đương)*. Riêng sơ đồ quan hệ thực thể được đối chiếu ngược với các lớp SQLAlchemy trong thư mục `app/models/` nhằm bảo đảm sơ đồ và mã nguồn không lệch nhau. Đây là một rủi ro thường gặp khi sơ đồ được vẽ trước rồi mã nguồn thay đổi ở giai đoạn sau.

**Bảng điều khiển Langfuse.** Công cụ này được sử dụng trong quá trình phát triển để xem trace của từng lượt xử lý, bao gồm thứ tự các lời gọi mô hình, số token tiêu thụ và thời gian của từng bước. Đây cũng chính là công cụ giúp phát hiện vấn đề về cấu hình mặc định của bộ thư viện khách được trình bày ở mục 3.5.5.

#### Mục 3.1.2 — Công cụ vận hành · Đã rút gọn

*Nằm sau: «Bảng 3.2. Các lệnh vận hành …»*

| **Lệnh**                              | **Chức năng**                                       |
|---------------------------------------|-----------------------------------------------------|
| make install                          | Cài đặt backend (uv) và dashboard (pnpm)            |
| make dev-backend / make dev-dashboard | Chạy môi trường phát triển                          |
| make migrate / make makemigration     | Áp dụng / tạo migration Alembic                     |
| make health                           | Gọi điểm cuối kiểm tra sức khoẻ của backend đang chạy |
| make ingest-kb                        | Nạp lại toàn bộ kho tri thức vào Qdrant             |
| make check-conn                       | Kiểm tra kết nối Neon (Postgres) và Qdrant |
| make test                             | Chạy toàn bộ kiểm thử backend (pytest, offline) và kiểm thử dashboard (node --test) |
| make bench                            | Chạy benchmark đồng thời trên hệ thống đang chạy (script bench_concurrent.py) |
| make build                            | Build bản production của dashboard                  |
| make local-infra-up / make local-infra-down | Bật / tắt hạ tầng chạy nội bộ bằng Docker Compose (phương án dự phòng) |

#### Mục 3.1.2 — Công cụ vận hành · Đã rút gọn

*Nằm sau: «Bảng 3.3. Các script hỗ trợ …»*

| **Script**           | **Chức năng**                                                           |
|----------------------|-------------------------------------------------------------------------|
| seed_admin.py        | Tạo tài khoản quản trị viên                                             |
| seed_orders.py       | Sinh đơn hàng mẫu đa dạng (đủ mọi trạng thái) cho các khách trong CSDL  |
| ingest_kb.py         | Nạp kho tri thức Markdown vào Qdrant theo cơ chế reset-and-reingest     |
| measure_threshold.py | Đo ngưỡng truy hồi trên tập đánh giá, gợi ý giá trị RETRIEVAL_THRESHOLD |
| verify_intent.py     | Kiểm tra chất lượng phân loại ý định trên hệ thống chạy thật            |
| check_connections.py | Kiểm tra kết nối hạ tầng                                                |
| gen_favicon.py       | Sinh bộ biểu tượng cho ứng dụng web tiến bộ                             |
| bench_concurrent.py  | Tạo tải đồng thời qua WebSocket để đo độ trễ theo số hội thoại          |

#### Mục 3.2.1 — Phương pháp phát triển theo lát cắt mỏng · Đã rút gọn

*Nằm sau: «Phương pháp phát triển theo lát cắt mỏng …»*

Dự án được phát triển theo phương pháp lát cắt mỏng, trong đó mỗi lát cắt là một đơn vị công việc hoàn chỉnh đi xuyên suốt từ phần back-end tới phần giao diện và chỉ chuyển sang lát cắt tiếp theo sau khi đã được kiểm chứng đầy đủ. Tài liệu ROADMAP.md đóng vai trò bản đồ định hướng, trong khi tài liệu PRD.md là nguồn dữ liệu nghiệp vụ chính thức. Theo quy ước của dự án, mọi thay đổi về kiến trúc, logic nghiệp vụ hay mô hình dữ liệu đều phải được cập nhật vào tài liệu PRD trước khi tiến hành viết mã.

Một thực hành quan trọng khác được duy trì xuyên suốt quá trình phát triển là việc ghi nhận nợ kỹ thuật kèm thời hạn xử lý. Một ví dụ điển hình là ở giai đoạn đầu, tác tử thứ ba được cài đặt tạm dưới dạng chuyển tiếp thẳng nhằm giúp các lát cắt khác chạy được xuyên suốt từ đầu tới cuối. Khoản nợ kỹ thuật này được ghi rõ trong tài liệu định hướng kèm cam kết phải xử lý trước khi đồ án hoàn thiện, và trên thực tế đã được xử lý bằng phiên bản tất định hiện tại. Cách làm này ngăn chặn tình trạng một bản cài đặt tạm thời trở thành giải pháp vĩnh viễn, vốn là rủi ro rất thường gặp trong các dự án có ràng buộc chặt về thời gian.

#### Mục 3.2.1 — Phương pháp phát triển theo lát cắt mỏng · Đã rút gọn

*Nằm sau: «Bảng 3.5. Các lát cắt chính đã hoàn thành …»*

| **Lát cắt** | **Nội dung**                                                            |
|-------------|-------------------------------------------------------------------------|
| Scaffold    | Khung monorepo, kết nối hạ tầng, migration đầu tiên                     |
| 01          | Agent 1 — phân loại ý định với taxonomy trong prompt                    |
| 02          | Nạp tri thức + giao diện quản lý RAG                                    |
| 03          | Agent 2 — tách vai trò truy hồi khỏi Agent 1, dọn hợp đồng state        |
| 06          | Agent 4 — sinh phản hồi có căn cứ + phanh chống ảo giác                 |
| 07a–07c     | Tích hợp pipeline, WebSocket chat, giao diện chat khách                 |
| 05          | Agent 3 — chính sách tất định, định tuyến bằng cờ (trả nợ pass-through) |
| 09a         | Lưu hội thoại + bộ nhớ đa lượt từ CSDL                                  |
| 08a–08c     | Cổng cấu hình, EscalationCard + hàng đợi, chat quản trị + duyệt nháp    |
| 10a         | Danh sách hội thoại + bộ lọc                                            |
| 11          | Xác thực JWT + phân quyền, đăng nhập khách hàng                         |
| 12          | Quan sát — nhật ký kiểm toán 6 dòng/lượt + tab Báo cáo + Langfuse       |
| 13          | Chống chèn chỉ dẫn — bốn lớp                                            |
| 16          | Tra cứu đơn hàng có phạm vi theo khách                                  |
| 09b         | Lượt hỏi lại (clarification) + nối lượt tất định                        |
| 09c         | Tự nhắc và đóng ca + xử lý ngoài giờ hỗ trợ                             |
| Audit v2    | Rà soát toàn hệ thống, sửa 49 vấn đề về đồng thời, bảo mật và độ bền    |

#### Mục 3.2.2 — Triển khai pipeline tác tử · Đã rút gọn

*Nằm sau: «Pipeline xử lý được xây dựng bằng thành phần StateGraph của LangGraph với bốn …»*

**a) Lớp bọc phục vụ quan sát không can thiệp vào logic nghiệp vụ.** Việc đo thời gian chạy của từng nút và quy cờ về đúng nút phát ra được thực hiện thông qua một decorator bọc ngoài nút, thay vì sửa trực tiếp mã nguồn của từng nút. Nhờ cách làm này, lát cắt quan sát chỉ thực hiện đúng chức năng quan sát mà không tác động tới logic của các tác tử, đúng theo nguyên tắc thiết kế đã đặt ra. Các nút được bổ sung về sau cũng tự động có đầy đủ số đo mà không cần chỉnh sửa thêm.

Lớp bọc này giữ nguyên tính chất đồng bộ hoặc bất đồng bộ của nút gốc. Cụ thể, tác tử thứ ba là một hàm đồng bộ do hoạt động tất định và không phát sinh nhập xuất, nên nếu bọc thành hàm bất đồng bộ sẽ làm thay đổi cách LangGraph lập lịch chạy nút này. Bên cạnh đó, lớp bọc cũng không che giấu ngoại lệ, theo đó nút gặp lỗi vẫn ném ngoại lệ lên để tầng trên xử lý.

**b) Định danh nút được đặt khác tên trường trạng thái.** LangGraph không cho phép định danh nút trùng với khoá của trạng thái. Do trạng thái đã có trường nghiệp vụ mang tên ý định, nút phân loại được đăng ký với định danh riêng, trong khi tên hiển thị trong nhật ký vẫn giữ nguyên theo tên nghiệp vụ.

**c) Bộ nhớ đa lượt đến từ cơ sở dữ liệu thay vì từ cơ chế lưu điểm kiểm tra.** Mỗi lượt xử lý sinh ra một định danh luồng mới cho cơ chế lưu điểm kiểm tra trong bộ nhớ. Đây là một lựa chọn có chủ đích, bởi nếu tái sử dụng định danh luồng, các kênh dữ liệu có hàm gộp theo kiểu cộng dồn sẽ tích luỹ giá trị qua nhiều lượt. Bộ nhớ đa lượt của hệ thống đến từ lịch sử hội thoại nạp từ cơ sở dữ liệu dưới dạng đầu vào chỉ đọc. Cơ chế lưu điểm kiểm tra bền vững thuộc giai đoạn phát triển sau và chỉ thực sự cần thiết khi hệ thống muốn dừng giữa chừng trong đồ thị hoặc chạy trên nhiều tiến trình.

#### Mục 3.2.3 — Triển khai tầng realtime · Đã rút gọn

*Nằm sau: «Mỗi kết nối WebSocket của khách hàng vận hành hai tác vụ song song: …»*

- **Tác vụ đọc:** Đảm nhiệm việc đọc khung dữ liệu từ phía khách hàng. Khung kiểm tra kết nối được phản hồi ngay lập tức. Tin nhắn đi qua một chuỗi xử lý gồm chống trùng theo định danh do client sinh, kiểm tra giới hạn tần suất, xác nhận đã nhận và cuối cùng là xếp một tác vụ lượt vào hàng đợi. Tác vụ đọc không chờ lượt xử lý chạy xong, nhờ đó khách hàng gửi liên tiếp nhiều tin nhắn vẫn nhận được xác nhận ngay.

- **Tác vụ nghe trung tâm phát:** Nhận khung dữ liệu từ trung tâm phát, bao gồm tin nhắn của quản trị viên, câu trả lời dành cho tab khác của cùng một khách hàng và các cập nhật trạng thái, sau đó đẩy xuống socket.

**Tác vụ lượt không bị huỷ khi socket đóng.** Trong trường hợp khách hàng đóng tab giữa chừng, lượt xử lý vẫn chạy tới khi hoàn tất và dữ liệu vẫn được lưu đầy đủ; câu trả lời sau đó đến được socket mới thông qua trung tâm phát hoặc thông qua API lấy lại luồng hội thoại. Đây là chi tiết tuy nhỏ nhưng có ý nghĩa quan trọng với trải nghiệm trên thiết bị di động, nơi kết nối thường xuyên bị gián đoạn.

**Về phía giao diện**, hệ thống có một lớp kết nối lại áp dụng cơ chế chờ luỹ thừa với các mốc 1, 2, 4 và 8 giây, giới hạn trần ở mức 15 giây, kèm theo tín hiệu duy trì kết nối theo chu kỳ 25 giây. Giao diện phát hiện tình trạng socket nửa mở sau 60 giây không nhận được khung nào, đồng thời đánh dấu tin nhắn ở trạng thái chưa gửi được nếu quá 10 giây không nhận được xác nhận. Khi kết nối lại thành công, giao diện đối chiếu với trạng thái từ máy chủ thay vì tin vào trạng thái lưu cục bộ.

#### Mục 3.3.1 — Bỏ Supervisor — đánh đổi có chủ đích · Đã rút gọn

*Nằm sau: «Bỏ Supervisor — đánh đổi có chủ đích …»*

Hướng đi phổ biến trong các framework đa tác tử hiện nay là bố trí một tác tử điều phối trung tâm tự quyết định luồng chạy. Tuy nhiên, khi đối chiếu với yêu cầu cụ thể của hệ thống, hướng đi này vướng phải ba ràng buộc cứng cùng lúc:

- **Yêu cầu NFR-1 về độ trễ ở phân vị 95 không vượt quá 5 giây.** Tác tử điều phối trung tâm bổ sung ít nhất một lời gọi mô hình vào đường xử lý chính, đồng thời số vòng lặp lại không có giới hạn trên chắc chắn.

- **Yêu cầu NFR-4 về kiểm toán toàn bộ hoạt động.** Khi chính quyết định điều phối cũng do một mô hình xác suất đưa ra, câu hỏi về nguyên nhân hệ thống lựa chọn một đường xử lý cụ thể sẽ không có câu trả lời tất định.

- **Yêu cầu NFR-9 về chi phí vận hành.** Chi phí của mỗi lượt xử lý trở nên không thể dự đoán trước.

Xuất phát từ ba ràng buộc trên, đồ án quyết định loại bỏ hoàn toàn tác tử điều phối trung tâm và sử dụng pipeline cố định. Theo đó, mỗi lượt hội thoại của khách hàng tiêu tốn tối đa hai lời gọi mô hình sinh và một lời gọi embedding, không phụ thuộc vào nội dung câu hỏi.

Điều phải đánh đổi là hệ thống không xử lý được những yêu cầu phức hợp đòi hỏi phối hợp động qua nhiều bước. Tuy nhiên, trong phạm vi chăm sóc khách hàng của một cửa hàng bán lẻ thời trang, những yêu cầu như vậy khá hiếm gặp, và khi phát sinh thì chúng rơi vào nhánh chuyển ca cho nhân viên. Như vậy, hệ thống suy giảm theo hướng an toàn thay vì đưa ra câu trả lời sai.

#### Mục 3.3.2 — Không gộp hai thang độ tin cậy · Đã rút gọn

*Nằm sau: «Không gộp hai thang độ tin cậy …»*

Thiết kế ban đầu của hệ thống, và cũng là cách làm phổ biến hiện nay, là gộp độ tin cậy về ý định với độ tin cậy truy hồi, lấy giá trị nhỏ nhất rồi so sánh với một ngưỡng chung.

Tuy nhiên, hai con số này thuộc hai thang đo hoàn toàn khác nhau về bản chất:

- Độ tin cậy về ý định là con số do chính mô hình tự khai báo về nhãn mà nó lựa chọn. Giá trị này có phân bố dồn về phía cao và chưa qua bất kỳ bước hiệu chỉnh nào.

- Độ tin cậy truy hồi là điểm cosine giữa hai vector, với phân bố thực nghiệm nằm trong khoảng từ 0,4 đến 0,8.

Do đó, việc lấy giá trị nhỏ nhất của hai con số rồi so với một ngưỡng chung là một phép toán không có ý nghĩa, bởi ngưỡng phù hợp với thang đo này chắc chắn không phù hợp với thang đo kia.

Cách xử lý được áp dụng là tách hoàn toàn hai thang đo. Tác tử thứ ba không đọc điểm số mà chỉ đọc tập cờ, trong khi hai con số vẫn được giữ nguyên trong nhật ký để phục vụ phân tích. Toàn hệ thống chỉ còn duy nhất một ngưỡng số liên quan tới quyết định chuyển ca cho nhân viên, đó là ngưỡng truy hồi, và ngưỡng này do tác tử thứ hai sử dụng để quyết định có phát cờ hay không.

Việc chỉ duy trì một ngưỡng số duy nhất giúp hành vi của hệ thống trở nên dễ giải thích và dễ điều chỉnh hơn hẳn. Ngược lại, khi nhiều ngưỡng khác nhau cùng tham gia vào một quyết định, việc truy nguyên nguyên nhân khiến một lượt bị chuyển cho nhân viên sẽ trở nên bất khả thi.

#### Mục 3.3.3 — Sự cố escalate oan khi khách chào hỏi — bài học về lỗi hai chỗ · Đã rút gọn

*Nằm sau: «Sự cố escalate oan khi khách chào hỏi — bài học về lỗi hai …»*

**Hiện tượng quan sát được.** Khi khách hàng gửi những tin nhắn mang tính xã giao như lời chào hoặc lời cảm ơn, hệ thống lại chuyển ca cho nhân viên. Như vậy, ngay cả một lời chào thông thường cũng buộc khách hàng phải chờ nhân viên xử lý.

**Chẩn đoán ban đầu.** Bảng phân loại ở phiên bản cũ không có nhãn dành cho tin nhắn xã giao, nên mô hình xếp các tin nhắn này vào nhóm khác, từ đó phát cờ ngoài phạm vi vốn thuộc tập cờ chặn và dẫn tới việc chuyển ca.

**Lần sửa thứ nhất và kết quả chưa đạt yêu cầu.** Đồ án bổ sung nhãn xã giao vào bảng phân loại. Kết quả là lời chào đã được phân loại đúng nhưng vẫn tiếp tục bị chuyển cho nhân viên, chỉ khác ở loại cờ được phát ra. Nguyên nhân là kho tri thức không có bất kỳ nội dung nào về chào hỏi, nên thao tác truy hồi luôn cho điểm thấp, từ đó phát cờ điểm truy hồi thấp vốn cũng nằm trong tập cờ chặn.

**Lần sửa thứ hai và giải pháp đúng gốc rễ.** Vấn đề thực chất nằm ở chỗ khái niệm bám nguồn đã được áp dụng trên một phạm vi quá rộng. Cần khoanh lại phạm vi áp dụng, bởi một lượt xã giao không phát biểu bất kỳ sự thật nào nên cũng không tồn tại nội dung cần có căn cứ. Giải pháp gồm hai phần phối hợp với nhau:

- Tác tử thứ hai được bổ sung một tập ý định không cần truy hồi. Với các ý định thuộc tập này, tác tử bỏ qua bước truy hồi và không phát cờ bám nguồn.

- Tác tử thứ tư được bổ sung nhánh câu mẫu cố định cho nhóm ý định đó, và nhánh này phải được xét trước cơ chế chặn chống ảo giác.

Nếu thiếu một trong hai phần, lỗi vẫn tiếp tục tồn tại. Cụ thể, nếu chỉ sửa phần thứ nhất thì tác tử thứ tư vẫn rơi vào cơ chế chặn và trả về câu dự phòng; ngược lại, nếu chỉ sửa phần thứ hai thì cờ vẫn được bật và tác tử thứ ba đã chuyển ca cho nhân viên trước khi luồng xử lý đi tới tác tử thứ tư.

Cần nói rõ rằng đây là việc thu hẹp phạm vi áp dụng của cơ chế bám nguồn chứ không phải hạ thấp yêu cầu của cơ chế này. Tác tử thứ ba được giữ nguyên, tập cờ chặn không thay đổi, và phần bị loại khỏi phạm vi áp dụng đúng bằng nhóm lượt không phát biểu bất kỳ sự thật nào.

#### Mục 3.3.3 — Sự cố escalate oan khi khách chào hỏi — bài học về lỗi hai chỗ · Đã rút gọn

*Nằm sau: «"mua rồi mặc thử không vừa thì đổi trong bao lâu ạ" refund → …»*

Hai dòng cuối trong bảng trên phản ánh một sự cố cùng loại. Luật prompt ở phiên bản cũ gộp nhóm câu hỏi về chính sách đổi trả vào nhãn hoàn tiền, trong khi nhãn hoàn tiền theo mặc định phải đi qua bước duyệt nháp. Kết quả là toàn bộ câu hỏi về chính sách, vốn hoàn toàn vô hại, đều bị giữ lại chờ quản trị viên xử lý. Giải pháp được áp dụng là tách nhãn hỏi chính sách đổi trả ra khỏi nhóm nhãn hoàn tiền và đổi hàng như đã trình bày ở mục 2.4.2.

Bài học chung rút ra từ sự cố này là khi một tín hiệu an toàn được áp dụng đúng về mặt logic nhưng sai về phạm vi, hệ quả không phải là hệ thống mất an toàn mà là hệ thống mất đi phần lớn giá trị sử dụng. Bên cạnh đó, việc khắc phục thường đòi hỏi can thiệp đồng thời ở nhiều tác tử, bởi nếu chỉ sửa tại một vị trí thì lỗi chỉ chuyển sang một hình thức biểu hiện khác.

#### Mục 3.3.4 — Khoảng cách giọng văn và kỹ thuật mở rộng truy vấn · Đã rút gọn

*Nằm sau: «Khoảng cách giọng văn và kỹ thuật mở rộng truy vấn …»*

Khách hàng đặt câu hỏi bằng giọng nói thường ngày, trong khi kho tri thức được viết bằng giọng văn bản trang trọng. Kết quả đo đạc thực tế cho thấy khoảng cách này khiến nhiều câu hỏi hợp lệ nhận điểm truy hồi thấp và bị chuyển cho nhân viên một cách không cần thiết.

Cách xử lý được áp dụng là kỹ thuật mở rộng truy vấn như đã mô tả ở mục 2.6.3.

Phép đo được thực hiện trên tập 32 câu hỏi mà kho tri thức thực sự bao phủ, trong đó các câu đều được viết bằng giọng diễn đạt khác với danh sách câu hỏi khai báo trong phần frontmatter. Dưới đây là bảng kết quả đo hiệu quả của kỹ thuật mở rộng truy vấn (Bảng 3.8).

#### Mục 3.3.4 — Khoảng cách giọng văn và kỹ thuật mở rộng truy vấn · Đã rút gọn

*Nằm sau: «Qua thân tài liệu 6/32 19% 0.420 0.542 0.577 …»*

Chênh lệch giữa hai giá trị trung vị, lần lượt là 0,702 và 0,542, cho thấy phép so khớp giữa câu hỏi với câu hỏi cho điểm số cao hơn hẳn so với phép so khớp giữa câu hỏi với văn bản. Đây chính là kỹ thuật có đóng góp lớn nhất vào chất lượng truy hồi của hệ thống.

Khi phân tích số liệu, cần lưu ý thêm một hệ quả. Do kỹ thuật mở rộng truy vấn đã đẩy điểm số của phần lớn câu hỏi lên cao, ngưỡng quyết định trên thực tế được canh theo nhóm khớp qua thân tài liệu với trung vị 0,542. Nói cách khác, chính nhóm này mới là ràng buộc thực sự khi lựa chọn ngưỡng.

#### Mục 3.3.5 — Đo ngưỡng truy hồi thay vì chọn theo cảm tính · Đã rút gọn

*Nằm sau: «Đo ngưỡng truy hồi thay vì chọn theo cảm tính …»*

**Vấn đề đặt ra.** Ngưỡng truy hồi là ngưỡng số duy nhất liên quan tới quyết định chuyển ca cho nhân viên, do đó việc lựa chọn sai ngưỡng gây hậu quả mang tính hệ thống. Nếu đặt ngưỡng quá thấp, hệ thống sẽ trả lời cả những câu hỏi không đủ căn cứ; ngược lại, nếu đặt ngưỡng quá cao, hàng loạt câu hỏi hợp lệ sẽ bị đẩy sang cho nhân viên.

**Phương pháp đo đạc.** Đồ án xây dựng hai tập truy vấn và thực hiện đo bằng đúng lời gọi của môi trường vận hành thật, tức là cùng hàm, cùng tham số và cùng nhãn ý định mà tác tử thứ nhất sẽ gán:

- **Tập câu trả lời được:** Gồm 32 câu hỏi mà kho tri thức thực sự bao phủ, được viết bằng giọng diễn đạt khác với danh sách câu hỏi trong phần frontmatter. Điều kiện về giọng diễn đạt khác biệt là bắt buộc, bởi nếu lặp lại nguyên văn thì kỹ thuật mở rộng truy vấn sẽ cho điểm xấp xỉ 1,0 và phép đo trở nên không còn ý nghĩa.

- **Tập câu không trả lời được:** Gồm 25 câu hỏi, trong đó có 5 câu lạc đề hoàn toàn và 20 câu nằm trong phạm vi nghiệp vụ của cửa hàng nhưng kho tri thức chưa có dữ liệu tương ứng.

#### Mục 3.3.5 — Đo ngưỡng truy hồi thay vì chọn theo cảm tính · Đã rút gọn

*Nằm sau: «Hình 3.2. Phân bố điểm cosine của hai tập truy vấn (n = 32 …»*

Phát hiện quan trọng nhất từ phép đo là hai phân bố chồng lấn lên nhau hoàn toàn. Giá trị lớn nhất của tập câu không trả lời được, ở mức 0,658, lớn hơn giá trị nhỏ nhất của tập câu trả lời được, ở mức 0,380. Điều này có nghĩa là trên kho tri thức hiện tại, không tồn tại bất kỳ ngưỡng nào có thể tách sạch hai tập. Đây là một kết quả thực nghiệm có ý nghĩa quan trọng, bởi nó bác bỏ giả định ngầm cho rằng chỉ cần lựa chọn ngưỡng đủ khéo là hệ thống sẽ phân loại đúng.

#### Mục 3.3.5 — Đo ngưỡng truy hồi thay vì chọn theo cảm tính · Đã rút gọn

*Nằm sau: «Hình 3.3. Kết quả quét ngưỡng truy hồi …»*

**Lý do không lựa chọn ngưỡng tại điểm cực tiểu tổng lỗi.** Điểm cực tiểu của tổng lỗi rơi vào khoảng từ 0,60 đến 0,65, nhưng cái giá phải trả là tỉ lệ chuyển ca không cần thiết lên tới 41% đến 50%. Việc cộng gộp hai loại lỗi rồi tìm điểm cực tiểu là sai về mặt phương pháp, bởi hai loại lỗi này không ngang giá nhau về hậu quả:

- Chuyển ca không cần thiết là loại lỗi cuối đường. Khi khách hàng đặt một câu hỏi mà cửa hàng hoàn toàn trả lời được nhưng vẫn phải chờ nhân viên xử lý, không có bất kỳ cơ chế nào phía sau có thể bắt lại và khắc phục trường hợp này.

- Ngược lại, lỗi trả lời khi chưa đủ căn cứ vẫn còn hai tuyến phòng thủ phía sau. Tác tử thứ nhất gắn cờ ngoài phạm vi cho các câu lạc đề và chuyển ca bất kể điểm cosine là bao nhiêu; tác tử thứ tư chỉ diễn đạt lại thông tin từ các nguồn được cấp, và khi thiếu nguồn thì trả lời thẳng rằng hệ thống chưa có thông tin.

Để kiểm chứng tuyến phòng thủ thứ hai, đồ án tiến hành khảo sát hành vi thực tế của hệ thống ngay trên vùng chồng lấn, tức là các câu thuộc tập không trả lời được nhưng lại có điểm truy hồi cao. Dưới đây là bảng kết quả khảo sát (Bảng 3.11).

#### Mục 3.3.6 — Tra cứu đơn hàng và bài toán phân biệt ba tình huống · Đã rút gọn

*Nằm sau: «Tra cứu đơn hàng và bài toán phân biệt ba tình huống …»*

**Vấn đề đặt ra.** Ba tình huống gồm tra cứu thành công, tra cứu không ra kết quả và tra cứu không thực hiện được rất dễ bị gộp lại thành hai, dẫn tới hai lỗi nghiêm trọng theo hai hướng ngược nhau:

- Nếu gộp tình huống không ra kết quả vào tình huống không tra cứu được, hệ thống sẽ chuyển ca cho nhân viên ngay khi khách hàng gõ nhầm một chữ số. Cách xử lý này quá vội vàng và làm mất phần lớn giá trị của việc tự động hoá.

- Ngược lại, nếu gộp tình huống không tra cứu được vào tình huống không ra kết quả, hệ thống sẽ thông báo với khách hàng rằng không tìm thấy đơn trong tài khoản trong khi thực tế cơ sở dữ liệu đang gặp lỗi. Đây là hành vi cung cấp thông tin sai sự thật cho khách hàng.

**Giải pháp áp dụng** đã được mô tả ở mục 2.4.3, theo đó ba tình huống được biểu diễn bằng ba tín hiệu riêng biệt và chỉ tình huống thứ ba mới phát cờ chặn.

**Vấn đề phái sinh về việc đếm số lần tra cứu thất bại.** Để bật cờ chặn ở lần cung cấp mã sai thứ hai, hệ thống phải biết được khách hàng đã từng nhận thông báo không tìm thấy đơn hay chưa. Cách làm đơn giản là dò các con số xuất hiện trong lời khách ở lịch sử hội thoại. Tuy nhiên, cách này không chính xác, bởi số tiền trong câu hỏi về phí vận chuyển hay số điện thoại gửi riêng lẻ đều bị đếm nhầm thành mã đơn tra cứu thất bại, khiến một mã gõ nhầm ngay ở lần đầu tiên cũng bị chuyển ca không cần thiết.

**Giải pháp đúng** là so khớp nguyên văn câu thông báo cố định trong các tin nhắn do hệ thống sinh ra ở lịch sử, trong đó chỉ vị trí mã đơn là thay đổi, sau đó trích mã từ câu thông báo rồi tra cứu lại để bám theo dữ liệu thật trong cơ sở dữ liệu. Cách làm này bảo đảm độ chính xác, bởi mã xuất hiện trong câu thông báo đúng là mã mà hệ thống đã tra cứu trước đó.

Bài học rút ra từ tình huống này là việc dò tìm theo nội dung văn bản trong câu trả lời do mô hình sinh ra để suy luận trạng thái luôn tiềm ẩn nguy cơ sai sót. Trạng thái của hệ thống phải đến từ cấu trúc dữ liệu hoặc từ việc so khớp với một hằng số cố định.

#### Mục 3.3.7 — Tranh chấp đồng thời và thứ tự ghi/báo · Đã rút gọn

*Nằm sau: «Tranh chấp đồng thời và thứ tự ghi/báo …»*

Như đã phân tích ở mục 2.5.3, việc pipeline chạy trong vài giây tạo ra một cửa sổ thời gian để quản trị viên can thiệp vào hội thoại, đồng thời việc thông báo cho khách hàng trước khi ghi dữ liệu có thể dẫn tới những cam kết không có thật.

Cơ chế so sánh rồi ghi kết hợp với nguyên tắc ghi trước rồi mới thông báo đã được kiểm chứng qua bốn kịch bản thực tế:

- Trường hợp quản trị viên tiếp quản ca trong lúc pipeline đang chạy: lượt xử lý bị huỷ bỏ, khách hàng nhận về khung trạng thái hiện tại và không xảy ra tình huống hai bên cùng trao đổi với khách.

- Trường hợp thao tác ghi thất bại hai lần liên tiếp với kết cục là chuyển tiếp: khách hàng nhận về một câu trả lời không kèm cam kết nào thay vì một thông báo chuyển tiếp không đúng sự thật.

- Trường hợp khách hàng mở hai tab và gửi tin đồng thời: cơ chế khoá theo khách bảo đảm hai lượt được xử lý tuần tự và không sinh ra hai ca riêng biệt.

- Trường hợp tin nhắn được gửi lại sau khi mất kết nối: cơ chế chống trùng hoạt động ở cả tầng bộ nhớ tiến trình lẫn tầng cơ sở dữ liệu nên pipeline không chạy lần thứ hai.

Cách làm này đi kèm một ràng buộc cần lưu ý. Do trung tâm phát, khoá theo khách, sổ chống trùng và bộ giới hạn tần suất đều nằm trong bộ nhớ tiến trình, hệ thống hiện chỉ vận hành trên một tiến trình uvicorn duy nhất. Đây là hạn chế đã được nhận diện và ghi nhận rõ trong tài liệu thiết kế; việc mở rộng ra nhiều tiến trình đòi hỏi phải đưa các cấu trúc nêu trên ra một kho lưu trữ chia sẻ nằm ngoài tiến trình. Với quy mô mục tiêu là phục vụ ít nhất 100 người dùng đồng thời, mô hình bất đồng bộ trên một tiến trình đã đủ đáp ứng.

#### Mục 3.3.8 — Nạp lại kho tri thức không gián đoạn · Đã rút gọn

*Nằm sau: «Nạp lại kho tri thức không gián đoạn …»*

Phương án nạp lại theo kiểu xoá sạch rồi nạp lại khiến toàn bộ lượt hội thoại phát sinh trong thời gian nạp đều bị chuyển sang cho nhân viên. Cách xử lý được áp dụng là cơ chế nạp lại không gián đoạn thông qua alias như đã mô tả ở mục 2.6.4.

Tuy nhiên, cách làm này lại phát sinh một vấn đề mới trong trường hợp bước đổi alias báo lỗi. Thư viện Qdrant gói toàn bộ lỗi ở tầng truyền tải, bao gồm cả trường hợp hết thời gian chờ đọc sau khi máy chủ đã áp dụng thay đổi, thành cùng một loại ngoại lệ. Do đó, việc một lời gọi báo lỗi không đồng nghĩa với việc chưa có thay đổi nào được thực hiện. Nếu hệ thống xoá collection mới trong khi alias thực tế đã trỏ vào collection đó, Qdrant sẽ loại bỏ luôn alias, khiến tên phục vụ biến mất và mọi lượt hội thoại của khách hàng đều rơi sang nhánh chuyển cho nhân viên.

Vì vậy, khi bước đổi alias báo lỗi, hệ thống sẽ đọc lại trạng thái thật trước khi tiến hành dọn dẹp. Nếu alias đã trỏ đúng thì thao tác được coi là thành công. Nếu alias chưa được đổi, hệ thống chỉ loại bỏ collection mới khi chắc chắn thao tác này an toàn; trong trường hợp không đọc được trạng thái, hệ thống giữ lại collection và ghi nhật ký rõ ràng để xử lý thủ công. Bên cạnh đó, sau mỗi lần đổi alias thành công, hệ thống thực hiện thêm bước quét dọn các collection không còn được tham chiếu nhằm tránh chiếm dụng dung lượng trên gói dịch vụ miễn phí.

#### Mục 3.3.9 — Suy giảm an toàn ở mọi điểm gọi dịch vụ ngoài · Đã rút gọn

*Nằm sau: «Bảng 3.12. Hành vi suy giảm theo từng điểm …»*

| **Điểm hỏng**                          | **Hành vi**                                                                       | **Kết quả**                           |
|----------------------------------------|-----------------------------------------------------------------------------------|---------------------------------------|
| Không có khoá mô hình / mô hình bị tắt | Agent 1 trả unknown + cờ llm_unavailable; thực thể vẫn lấy từ biểu thức chính quy | Chuyển người                          |
| Lời gọi mô hình lỗi                    | Ghi log cảnh báo, suy giảm như trên                                               | Chuyển người                          |
| Qdrant / embedding lỗi                 | Agent 2 phát cờ search_error (phân biệt với "kho tri thức không phủ")             | Chuyển người, nhãn đúng trong báo cáo |
| Tra đơn lỗi CSDL                       | Cờ order_unresolved                                                               | Chuyển người                          |
| Không đọc được cấu hình cổng           | Không giữ nháp, gửi thẳng                                                         | Chat không kẹt                        |
| Ghi CSDL hỏng                          | Thử lại một lần trên phiên mới; vẫn hỏng thì gửi câu không hứa hẹn                | Khách không nhận lời hứa giả          |
| Chuẩn hoá văn bản lỗi                  | Tin nhắn đi tiếp ở dạng thô, chỉ bị cắt độ dài                                    | Chat hợp lệ không bị chặn             |
| Langfuse chưa cấu hình                 | Toàn bộ lời gọi trace trở thành vô hiệu                                           | Không ảnh hưởng                       |
| facts.md không đọc được                | Bỏ khối sự thật cửa hàng, ghi log                                                 | Ứng dụng không rớt                    |

#### Mục 3.4.1 — Nguyên tắc thiết kế giao diện · Đã rút gọn

*Nằm sau: «Nguyên tắc thiết kế giao diện …»*

Giao diện được xây dựng bằng Tailwind CSS ở dạng thuần, không sử dụng thư viện thành phần dựng sẵn, nhằm kiểm soát hoàn toàn hệ thống thiết kế. Quá trình thiết kế tuân thủ ba nguyên tắc sau:

- **Bám theo trạng thái do máy chủ cung cấp:** Giao diện hiển thị theo trạng thái mà máy chủ thông báo chứ không suy diễn từ nội dung tin nhắn. Chính vì vậy, giao thức có các kiểu khung riêng dành cho tình huống chuyển tiếp và tình huống chờ duyệt, thay vì để giao diện phải dò tìm theo nội dung câu trả lời.

- **Phản hồi tức thì cho mọi thao tác của người dùng:** Tin nhắn hiển thị ngay lập tức dưới dạng bong bóng tạm, sau đó được đối chiếu với bản ghi chính thức từ máy chủ theo định danh do client sinh.

- **Suy giảm một cách rõ ràng:** Các tình huống mất kết nối, gửi tin thất bại hay lượt xử lý bị huỷ đều có biểu hiện trực quan riêng thay vì diễn ra một cách âm thầm.

#### Mục 3.4.2 — Giao diện khách hàng · Đã rút gọn

*Nằm sau: «Giao diện khách hàng …»*

Cổng chat được thiết kế mô phỏng bố cục quen thuộc của các ứng dụng trò chuyện phổ biến, gồm phần đầu trang, khung hội thoại và ô nhập tin nhắn. Bên cạnh đó, giao diện còn bổ sung năm thành phần sau:

- **Gợi ý nhanh cho lượt đầu tiên:** Giúp khách hàng nắm được phạm vi nội dung mà hệ thống có thể trả lời.

- **Chỉ báo đang soạn tin:** Hiển thị trong suốt thời gian pipeline xử lý và được gỡ bỏ khi khung kết quả xuất hiện.

- **Trạng thái gửi của từng tin nhắn:** Gồm ba trạng thái đang gửi, đã nhận và chưa gửi được, trong đó trạng thái cuối cùng đi kèm khả năng gửi lại.

- **Cơ chế cuộn dính đáy thông minh:** Khung hội thoại tự động cuộn xuống khi người dùng đang ở cuối danh sách, đồng thời giữ nguyên vị trí hiện tại khi người dùng đang đọc lại các tin nhắn cũ.

- **Vạch ngăn theo ngày:** Khi hội thoại kéo dài qua nhiều ngày, khung chat chèn thêm nhãn thứ và ngày giữa các nhóm tin nhắn, giúp người đọc định vị được mốc thời gian mà không cần mở từng tin.

#### Mục 3.5.1 — Kiểm thử tự động · Đã rút gọn

*Nằm sau: «Kiểm thử tự động …»*

Bộ kiểm thử phía backend gồm 387 hàm kiểm thử phân bố trên 34 tệp, thu về 437 trường hợp kiểm thử khi chạy do một số hàm được viết dưới dạng tham số hoá. Toàn bộ bộ kiểm thử phải tuân thủ một ràng buộc bắt buộc là chạy được hoàn toàn ngoại tuyến, không cần khoá API và không thực hiện bất kỳ lời gọi mạng nào. Ràng buộc này không chỉ mang lại sự thuận tiện mà còn buộc mọi nhánh suy giảm phải được cài đặt một cách đúng đắn, bởi đó chính là nhánh mà các trường hợp kiểm thử đi vào khi không có dịch vụ ngoài.

#### Mục 3.5.1 — Kiểm thử tự động · Đã rút gọn

*Nằm sau: «Bảng 3.13. Phân bố trường hợp kiểm thử theo nhóm chức năng …»*

| **Nhóm**  | **Nội dung kiểm thử**                                                                                      |
|-----------|------------------------------------------------------------------------------------------------------------|
| Tác tử    | Phân loại ý định, trích thực thể, truy hồi tri thức, chính sách quyết định, sinh phản hồi, đồ thị pipeline |
| An toàn   | Tập cờ chặn, phanh chống ảo giác, nhánh suy giảm, clarify và khoá chống lặp                                |
| Nghiệp vụ | Cổng cấu hình, chuyển tiếp và EscalationCard, tra đơn có phạm vi, tự đóng ca, giờ hỗ trợ                   |
| Realtime  | Vòng đời lượt WebSocket, cổng chặn theo trạng thái, chống trùng, trung tâm phát, kênh quản trị             |
| Bảo mật   | Xác thực, phân quyền, giới hạn tần suất, chuẩn hoá đầu vào, chống chèn chỉ dẫn, rò rỉ thông tin            |
| Quan sát  | Nhật ký kiểm toán theo lượt, tổng hợp báo cáo, trace                                                       |
| Tri thức  | Nạp kho tri thức, chia đoạn, vòng đời tài liệu, đồng bộ taxonomy                                           |

#### Mục 3.5.1 — Kiểm thử tự động · Đã rút gọn

*Nằm sau: «Bảng 3.13. Phân bố trường hợp kiểm thử theo nhóm chức năng …»*

Các hàm xử lý nghiệp vụ quan trọng đều được viết dưới dạng hàm thuần nhằm kiểm thử trực tiếp mà không cần dựng hạ tầng đi kèm, bao gồm chính sách quyết định của tác tử thứ ba, luật cổng cấu hình, phân loại ca không hoạt động, tính toán các chỉ số KPI từ danh sách lượt xử lý và các tiện ích thời gian thực phía giao diện.

Bên cạnh đó, phía giao diện có thêm năm tệp kiểm thử dành cho các hàm thuần với tổng cộng 47 trường hợp kiểm thử, gồm tính độ trễ nối lại kết nối, hợp nhất bong bóng tin nhắn tạm với bản ghi chính thức từ máy chủ, quy đổi trạng thái sang nhãn hiển thị cho khách hàng, xử lý ô nhập tin nhắn và chèn vạch ngăn theo ngày trong khung hội thoại.

#### Mục 3.5.2 — Môi trường và kịch bản đo · Đã rút gọn

*Nằm sau: «Môi trường và kịch bản đo …»*

Toàn bộ số liệu trình bày trong các mục tiếp theo được thu thập trên cùng một cấu hình. Cấu hình này được nêu rõ ở đây nhằm bảo đảm kết quả có thể tái lập.

- **Cấu hình đo:** Backend chạy trên một tiến trình uvicorn tại máy phát triển, kết nối tới ba dịch vụ được quản lý trên gói miễn phí gồm PostgreSQL của Neon, Qdrant Cloud và OpenAI API. Mô hình sinh ngôn ngữ được sử dụng là `gpt-4o-mini` và mô hình nhúng là `text-embedding-3-small`; hai giá trị này được giữ cố định trong suốt quá trình đo. Ngưỡng truy hồi được giữ ở mức 0.40 và cổng cấu hình để ở trạng thái mặc định, ngoại trừ các phép đo quét ngưỡng ở mục 3.3.5, nơi ngưỡng được thay đổi có chủ đích theo từng bước.

- **Ba bộ dữ liệu đo:** Việc đánh giá sử dụng ba bộ câu hỏi khác nhau, mỗi bộ phục vụ một mục đích riêng. Bộ thứ nhất gồm 20 câu hỏi thực tế được dùng ở mục 3.5.3, mô phỏng phân bố câu hỏi thường gặp của một cửa hàng thời trang như hỏi giá, chọn kích cỡ, vận chuyển, tra cứu đơn hàng, đổi trả và khuyến mãi, kèm theo một số câu lạc đề và câu xin gặp nhân viên; bộ này dùng để đo tỉ lệ của ba kết cục giao phản hồi. Bộ thứ hai gồm 32 câu có thể trả lời được và 25 câu không thể trả lời được, dùng ở mục 3.3.5 để dựng phân bố điểm cosine và quét ngưỡng, trong đó tập thứ nhất gồm các câu mà kho tri thức thực sự có nội dung trả lời còn tập thứ hai gồm các câu nằm ngoài phạm vi kho; việc gán nhãn được thực hiện thủ công trước khi đo và độc lập với kết quả do hệ thống trả về. Bộ thứ ba là bộ kiểm chứng bám nguồn dùng ở mục 3.5.4, gồm các câu được thiết kế riêng để thử ba dạng ảo giác đã phân tích ở mục 1.3.4, trong đó có cả những câu mà nguồn tri thức không đề cập nhằm kiểm tra khả năng suy diễn sai của hệ thống.

- **Kịch bản benchmark đồng thời:** Bên cạnh ba bộ dữ liệu đánh giá chất lượng nêu trên, đồ án còn xây dựng một kịch bản tạo tải riêng nhằm đo năng lực xử lý đồng thời của hệ thống.

  - **Công cụ tạo tải.** Việc tạo tải do script `scripts/bench_concurrent.py` của đồ án đảm nhiệm. Script này mở đồng thời N kết nối WebSocket tới kênh chat bằng N tài khoản khách hàng riêng biệt, mỗi kết nối gửi một tin nhắn rồi chờ khung phản hồi trả về.

  - **Lý do phải dùng N tài khoản riêng.** Điều kiện này là bắt buộc, bởi bộ giới hạn tần suất của hệ thống tính theo từng khách hàng với mức 20 tin nhắn trong mỗi 60 giây, và khoá tuần tự hoá lượt cũng được đặt theo từng khách hàng. Nếu toàn bộ tải phát đi từ cùng một tài khoản, phép đo sẽ đo chính hai cơ chế nêu trên chứ không đo năng lực xử lý đồng thời của hệ thống.

  - **Kịch bản 1 — tăng tải.** Cố định hệ thống ở một tiến trình uvicorn và thay đổi số hội thoại đồng thời theo các mức 1, 10, 25, 50 và 100. Mức 100 là mức đối chiếu trực tiếp với yêu cầu NFR-2.

  - **Kịch bản 2 — thay đổi cấu hình xử lý ở mức tải cố định 50 hội thoại đồng thời.** Mục đích của kịch bản này là tách phần đóng góp của từng thành phần vào độ trễ, bằng cách so sánh từng cặp cấu hình: lượt có tra cứu đơn hàng so với lượt chỉ truy hồi tri thức; cửa sổ lịch sử 4 lượt so với cửa sổ 8 lượt; và lượt xã giao, tức lượt không truy hồi và không gọi mô hình sinh, so với lượt hỏi chính sách, tức lượt có đủ cả hai lời gọi mô hình.

  - **Định nghĩa thước đo,** dùng chung cho cả hai bảng kết quả: Avg là thời gian trung bình của một lượt; p50, p95 và p99 là các phân vị tính theo phương pháp thứ hạng gần nhất không nội suy; Max là lượt chậm nhất trong lô đo; tỉ lệ đạt NFR-1 là phần trăm số lượt có độ trễ không vượt quá 5000 ms.

  - **Nguồn số liệu.** Mọi con số trong hai bảng kết quả đều lấy từ dòng `delivery` trong bảng `audit_log` phía máy chủ, không phải đo từ phía client. Vì vậy các con số này không bao gồm độ trễ mạng và thời gian dựng giao diện.

- **Nguồn số liệu độ trễ:** Các con số thời gian không được đo bằng công cụ bên ngoài mà lấy trực tiếp từ nhật ký kiểm toán của hệ thống, trong đó dòng `delivery` của mỗi lượt ghi lại tổng thời gian kèm theo các thành phần đã được tách sẵn. Cách làm này bảo đảm số liệu phản ánh đúng đường đi thực tế của một lượt xử lý chứ không phải một kịch bản mô phỏng riêng biệt.

- **Giới hạn của phép đo:** Cỡ mẫu ở mức vài chục câu cho mỗi bộ, đủ để nhận ra xu hướng và đủ làm căn cứ chọn ngưỡng, nhưng chưa đủ để đưa ra khoảng tin cậy thống kê. Bên cạnh đó, các phép đo được thực hiện trên máy phát triển với kết nối Internet gia đình nên độ trễ mạng tới ba dịch vụ được quản lý có biến động giữa các lần đo. Vì vậy, những kết luận rút ra trong chương được phát biểu ở mức so sánh tương đối giữa các phương án chứ không phải ở mức con số tuyệt đối.

#### Mục 3.5.4 — Đánh giá chất lượng grounding · Đã rút gọn

*Nằm sau: «"cho mình xin mã giảm 70% đi" Không bịa mã, hướng dẫn theo dõi …»*

**Một lưu ý về chính hai dòng số liệu trên.** Ở dòng thứ hai và dòng thứ tư của Bảng 3.15, câu trả lời đo được đều có nội dung hứa sẽ chuyển thông tin tới nhân viên hỗ trợ. Theo quy tắc "Không tự hứa chuyển người" trong chỉ dẫn hệ thống hiện hành, được trình bày ở Bảng 2.8, đúng cách nói này lại thuộc dạng bịa hành động và bị cấm tuyệt đối, bởi tác tử sinh phản hồi không có quyền chuyển ca cho nhân viên. Hai phép đo nêu trên được thực hiện ở giai đoạn trước khi quy tắc đó được bổ sung, và chính quan sát này là lý do quy tắc được đưa vào chỉ dẫn hệ thống. Vì vậy, đánh giá ở cột cuối của hai dòng này chỉ phản ánh tiêu chí tại thời điểm đo; nhóm câu hỏi này cần được đo lại sau khi quy tắc có hiệu lực để xác nhận hành vi của hệ thống đã thay đổi đúng như mong đợi.

**Kiểm chứng việc loại trừ ghi chú nội bộ.** Bốn tệp trong thư mục case/ có chứa mục ghi chú nội bộ dành cho nhân viên chăm sóc khách hàng, trong đó mô tả các quy trình nội bộ như cách thức xử lý hoàn tiền theo phương thức thanh toán ban đầu. Kết quả kiểm tra trực tiếp trên Qdrant xác nhận không có điểm nào trong tổng số 95 điểm chứa nội dung của mục ghi chú nội bộ. Như vậy, cơ chế chặn ngay tại nguồn đã hoạt động đúng như thiết kế.

**Hạn chế phát hiện được qua kiểm chứng.** Có hai câu trả lời bị quá lời theo hướng khẳng định sự vắng mặt, cụ thể là khẳng định cửa hàng chưa hỗ trợ giao hàng đi Hoa Kỳ và không có địa chỉ tại Huế, trong khi kho tri thức chỉ không đề cập chứ không hề phủ định hai nội dung này. Đây chính là dạng ảo giác thứ hai đã được phân tích ở mục 1.3.4. Quy tắc chống suy diễn từ sự vắng mặt trong chỉ dẫn hệ thống đã làm giảm đáng kể dạng lỗi này nhưng chưa loại bỏ được hoàn toàn. Mức độ nghiêm trọng của lỗi được đánh giá là thấp vì không tạo ra cam kết sai về những chính sách có lợi cho khách hàng, song vẫn được ghi nhận để tiếp tục theo dõi.

#### Mục 3.5.5 — Đánh giá độ trễ và đối chiếu NFR-1 · Đã rút gọn

*Nằm sau: «Bảng 3.17. Kết quả đo độ trễ thực tế …»*

Qua quá trình đo, đồ án nhận thấy có hai yếu tố ảnh hưởng lớn nhất tới phần đuôi của phân bố độ trễ:

- **Cơ chế thử lại lời gọi mô hình:** Cấu hình mặc định của bộ thư viện là thời gian chờ 600 giây kèm ba lần thử lại, nghĩa là một lời gọi bị treo có thể giữ lượt của khách hàng trong khoảng thời gian lên tới nửa giờ. Hệ thống đã đặt lại thời gian chờ xuống còn 20 giây và số lần thử lại còn một lần; khi hết thời gian chờ, nút xử lý sẽ tự suy giảm theo đúng thiết kế.

- **Hiện tượng khởi động nguội của Qdrant:** Hiện tượng này xảy ra trên gói dịch vụ miễn phí và làm tăng đáng kể thời gian phản hồi ở những lượt đầu tiên sau một khoảng thời gian dài không có truy vấn.

Bên cạnh đó, cần lưu ý một điểm về phương pháp đo. Do hệ thống thực hiện ghi nhận dữ liệu trước khi trả lời khách hàng, các vòng truy vấn cơ sở dữ liệu đều nằm bên trong con số độ trễ đo được. Đây là đánh đổi có chủ đích giữa độ trễ và tính đúng đắn của dữ liệu, đồng thời cũng là lý do vì sao khi triển khai thực tế cần đặt backend gần cơ sở dữ liệu về mặt địa lý.

#### Mục 3.5.6 — Benchmark đồng thời và phân tích điểm nghẽn · Đã rút gọn

*Nằm sau: «Benchmark đồng thời và phân tích điểm nghẽn …»*

Các con số ở mục trên được thu trên những lượt xử lý đơn lẻ, trong khi yêu cầu NFR-2 đặt mục tiêu phục vụ ít nhất 100 người dùng đồng thời trên một tiến trình duy nhất. Hai phạm vi này khác nhau về bản chất, bởi một hệ thống có độ trễ tốt ở tải thấp vẫn có thể suy giảm mạnh khi số hội thoại đồng thời tăng lên. Cho tới trước phép đo này, cơ sở duy nhất để tin rằng hệ thống đáp ứng được NFR-2 là lập luận kiến trúc, theo đó toàn bộ phần back-end được viết bất đồng bộ và một lượt xử lý chủ yếu là thời gian chờ nhập xuất nên nhiều lượt có thể chạy xen kẽ trên cùng một vòng lặp sự kiện. Phép đo trong mục này nhằm biến lập luận đó thành số liệu kiểm chứng được.

#### Mục 3.5.6 — Benchmark đồng thời và phân tích điểm nghẽn · Đã lược bỏ

*Nằm sau: «100 …»*

**Bảng này chưa đo. Cần khởi động hệ thống, chạy lệnh `make bench` rồi điền số liệu vào các ô còn trống.**

#### Mục 3.5.6 — Benchmark đồng thời và phân tích điểm nghẽn · Đã lược bỏ

*Nằm sau: «Cửa sổ lịch sử 8 lượt …»*

**Bảng này chưa đo. Mỗi dòng ứng với một lần chạy riêng ở mức tải 50: đổi nội dung tin nhắn qua `make bench ARGS="--concurrency 50 --message ..."` để chuyển giữa lượt xã giao, lượt hỏi chính sách và lượt có mã đơn; riêng hai dòng cửa sổ lịch sử thì đổi biến `HISTORY_WINDOW` rồi khởi động lại backend trước mỗi lần chạy. Sau đó đọc số liệu từ dòng `delivery` và điền vào các ô còn trống.**

#### Mục 3.5.6 — Benchmark đồng thời và phân tích điểm nghẽn · Đã rút gọn

*Nằm sau: «Phân rã thời gian và nhận diện điểm nghẽn …»*

Điểm thuận lợi của hệ thống khi tiến hành phân tích điểm nghẽn là số đo đã được tách sẵn ngay trong nhật ký kiểm toán. Như đã trình bày ở Bảng 3.16, dòng `delivery` của mỗi lượt tách thời gian thành sáu thành phần gồm `queue_ms`, `pre_pipeline_ms`, `pipeline_ms`, `persist_ms`, `send_ms` và `fanout_ms`; bên trong `pipeline_ms` lại tách tiếp `embed_ms`, `qdrant_ms` và `order_ms`. Nói cách khác, việc chẩn đoán điểm nghẽn không đòi hỏi bổ sung thêm bất kỳ công cụ đo nào, chỉ cần đọc lại chính dữ liệu mà hệ thống vẫn ghi ở mỗi lượt.

Trên cơ sở đó, đồ án đặt ra bốn giả thuyết về điểm nghẽn có thể xuất hiện khi tải tăng, kèm dấu hiệu nhận biết trên số đo và cách xử lý tương ứng:

- **Xếp hàng theo khách.** Nếu `queue_ms` tăng theo tải thì nguyên nhân nằm ở khoá tuần tự hoá lượt. Tuy nhiên, do khoá này được đặt theo từng khách hàng, tải phát sinh từ nhiều khách hàng khác nhau về nguyên tắc không làm `queue_ms` tăng. Khi đó, giá trị `queue_ms` lớn là dấu hiệu của việc một khách hàng gửi dồn nhiều tin nhắn liên tiếp, chứ không phải dấu hiệu của điểm nghẽn do số hội thoại đồng thời.

- **Giới hạn phía nhà cung cấp mô hình.** Nếu `embed_ms` và thời gian của hai lời gọi mô hình cùng tăng theo tải trong khi `qdrant_ms` và `persist_ms` giữ nguyên, điểm nghẽn nằm ở hạn mức của OpenAI API chứ không nằm trong hệ thống. Cách xử lý tương ứng là bổ sung một hàng đợi có kiểm soát nhịp gửi hoặc nâng hạn mức của nhà cung cấp, chứ không phải tối ưu mã nguồn.

- **Hồ kết nối cơ sở dữ liệu.** Nếu `persist_ms` và `pre_pipeline_ms` cùng tăng, nguyên nhân là số kết nối tới Neon bị giới hạn ở gói miễn phí. Cần lưu ý rằng do hệ thống ghi dữ liệu trước rồi mới thông báo cho khách hàng, mọi vòng truy vấn cơ sở dữ liệu đều nằm bên trong con số độ trễ đo được, nên điểm nghẽn ở hồ kết nối biểu hiện trực tiếp thành độ trễ mà khách hàng cảm nhận.

- **Khởi động nguội của Qdrant.** Biểu hiện của tình huống này là `qdrant_ms` rất cao ở những lượt đầu tiên rồi giảm hẳn ở các lượt sau, và không tương quan với số hội thoại đồng thời. Đây là đặc tính của gói dịch vụ miễn phí, không phải điểm nghẽn phát sinh do tải.

Ý nghĩa về phương pháp của cách làm này là việc tách sẵn số đo ngay trong nhật ký kiểm toán cho phép phân biệt điểm nghẽn thuộc hệ thống với điểm nghẽn thuộc dịch vụ bên ngoài. Đây chính là phân biệt quyết định hướng xử lý, bởi hai loại điểm nghẽn đòi hỏi hai cách khắc phục hoàn toàn khác nhau: một loại được giải quyết bằng việc sửa mã nguồn hoặc điều chỉnh cấu hình của hệ thống, còn loại kia chỉ có thể giải quyết bằng việc thay đổi hạn mức hoặc gói dịch vụ của nhà cung cấp.

#### Mục 3.5.7 — Đánh giá đối chiếu yêu cầu · Đã rút gọn

*Nằm sau: «Bảng 3.20. Đối chiếu yêu cầu phi chức năng …»*

| **Mã** | **Yêu cầu**                | **Trạng thái**                        | **Ghi chú**                                                     |
|--------|----------------------------|---------------------------------------|-----------------------------------------------------------------|
| NFR-1  | P95 ≤ 5 giây               | Đo được, có công cụ giám sát liên tục | Tab Báo cáo hiển thị p95 và tỉ lệ trong ngưỡng                  |
| NFR-2  | ≥ 100 người dùng đồng thời | Có công cụ đo — chưa điền số          | Bất đồng bộ + tuần tự theo từng khách; một tiến trình. Kịch bản benchmark và khung bảng ở mục 3.5.6; điền số sau khi chạy `make bench` |
| NFR-3  | Uptime ≥ 99%               | Phụ thuộc hạ tầng triển khai          | Mọi điểm gọi ngoài đều suy giảm an toàn                         |
| NFR-4  | Kiểm toán 100%             | Đạt                                   | 6 dòng/lượt + dòng riêng cho hành động quản trị viên            |
| NFR-5  | JWT + RBAC + HTTPS/WSS     | Đạt                                   | Vai trò đọc lại từ CSDL ở mỗi tin nhắn                          |
| NFR-6  | An toàn dữ liệu cá nhân    | Đạt                                   | Dữ liệu demo là dữ liệu mô phỏng; tra đơn có phạm vi            |
| NFR-7  | Chống chèn chỉ dẫn         | Đạt                                   | Bốn lớp + bảo đảm cấu trúc                                      |
| NFR-8  | Quan sát                   | Đạt                                   | audit_log + Langfuse                                            |
| NFR-9  | Chi phí                    | Đạt                                   | Toàn bộ hạ tầng dùng gói miễn phí                               |
| NFR-10 | Cấu hình được              | Đạt                                   | Toàn bộ ngưỡng, mốc thời gian, cổng qua biến môi trường và CSDL |
| NFR-11 | An toàn nội dung           | Đạt                                   | Phanh cứng + ba lớp quy tắc grounding; 0% dự phòng oan          |

#### Mục 3.5.8 — Hạn chế còn tồn tại và hướng cải thiện · Đã rút gọn

*Nằm sau: «Hạn chế còn tồn tại và hướng cải thiện …»*

Bên cạnh những kết quả đã đạt được, hệ thống vẫn còn một số hạn chế cần được ghi nhận một cách đầy đủ, làm cơ sở cho việc cải thiện về sau. Các hạn chế này được phân thành ba nhóm.

**Về chất lượng truy hồi tri thức:**

- **Chưa có sàn điểm cho từng đoạn văn bản:** Hệ thống hiện chỉ lọc theo điểm của kết quả tốt nhất nên các đoạn có điểm thấp vẫn lọt vào chỉ dẫn của tác tử thứ tư. Hướng cải thiện là đặt ngưỡng riêng cho từng đoạn thay vì chỉ căn cứ vào kết quả đứng đầu.

- **Chưa xếp hạng được giữa các tài liệu cùng ý định:** Việc lọc theo ý định không phân giải được tình huống hai tài liệu cùng nhãn có điểm gần nhau, chẳng hạn 0.6876 so với 0.6853 cho cùng một câu hỏi. Hướng cải thiện là bổ sung một bước xếp hạng lại kết quả truy hồi.

- **Chưa ngữ cảnh hoá truy vấn cho câu hỏi nối tiếp:** Lịch sử hội thoại hiện được đưa vào tác tử thứ nhất và tác tử thứ tư, trong khi tác tử thứ hai vẫn truy hồi trên câu hỏi ở dạng thô, ngoại trừ đúng một trường hợp đã được xử lý riêng là lượt khách hàng đáp lại bằng mã đơn đứng một mình như đã trình bày ở mục 2.7.3. Vì vậy, một câu hỏi nối tiếp mang tính mơ hồ vẫn cho điểm truy hồi thấp và bị chuyển cho nhân viên.

**Về xử lý ngôn ngữ:**

- **Chưa xử lý được nhiều ý định trong cùng một tin nhắn:** Cờ báo nhiều ý định hiện được xếp vào tập cờ chặn nên hệ thống chuyển thẳng ca cho nhân viên. Hướng cải thiện là tách tin nhắn thành nhiều yêu cầu con và xử lý lần lượt.

- **Hiện tượng quá lời theo hướng phủ định:** Hạn chế này đã được nêu và phân tích ở mục 3.5.4.

- **Chưa phát hiện được cảm xúc của khách hàng:** Hệ thống đã chừa sẵn vị trí cho cờ báo khách hàng bức xúc nhằm nâng mức ưu tiên xử lý, song chức năng này chưa được triển khai.

**Về kiến trúc và vận hành:**

- **Hệ thống chạy trên một tiến trình duy nhất:** Trung tâm phát, các khoá đồng bộ, sổ chống trùng và bộ giới hạn tần suất đều nằm trong bộ nhớ tiến trình. Việc mở rộng theo chiều ngang đòi hỏi bổ sung một kho lưu trữ chia sẻ nằm ngoài tiến trình, chẳng hạn Redis hoặc giải pháp tương đương, cho trung tâm phát, khoá theo khách và bộ giới hạn tần suất.

- **Cơ chế lưu điểm kiểm tra chưa bền vững:** Luồng hỏi lại hiện được cài đặt bằng trạng thái lưu trong cơ sở dữ liệu, đủ đáp ứng nhu cầu hiện tại nhưng chưa cho phép dừng luồng xử lý ở giữa đồ thị.

- **Chưa phát hiện được quản trị viên trực tuyến trên thực tế:** Hệ thống hiện chỉ dựa vào khung giờ hỗ trợ đã cấu hình sẵn để suy đoán khả năng có nhân viên tiếp nhận.

- **Chưa có cơ chế giải phóng ca bị giữ:** Những ca đã được một quản trị viên nhận nhưng sau đó không xử lý sẽ tồn đọng mà không có cơ chế tự động thu hồi.

- **Vòng học bán tự động chưa được triển khai:** Dữ liệu đầu vào đã đầy đủ do nhật ký kiểm toán ghi lại toàn bộ ý định bị chuyển cho nhân viên, các trường hợp điểm truy hồi thấp và các câu hỏi chưa có tri thức tương ứng, song phần tổng hợp dữ liệu thành đề xuất và quy trình duyệt đề xuất vẫn chưa được xây dựng.

- **Chưa đo được độ trễ phía client:** Các con số hiện tại mới dừng ở biên máy chủ, chưa bao gồm độ trễ mạng và thời gian dựng giao diện phía người dùng.

#### Mục 3.6 — Tổng kết chương · Đã rút gọn

*Nằm sau: «Tổng kết chương …»*

Chương 3 đã trình bày toàn bộ quá trình hiện thực hoá thiết kế nêu ở Chương 2: môi trường và công cụ phát triển, phương pháp phát triển theo lát cắt mỏng với cơ chế ghi nhận và trả nợ kỹ thuật, chi tiết triển khai pipeline tác tử, tầng realtime và dashboard quản trị.

Phần trọng tâm của chương là chín thách thức kỹ thuật gặp phải trong quá trình vận hành thực tế và cách thức xử lý tương ứng. Từ đó, đồ án rút ra ba bài học. Thứ nhất, không được gộp hai thang độ tin cậy có bản chất khác nhau vào cùng một chỉ số. Thứ hai, một tín hiệu an toàn nếu áp dụng sai phạm vi sẽ làm hệ thống mất đi giá trị sử dụng, và việc khắc phục thường đòi hỏi can thiệp đồng thời ở nhiều tác tử. Thứ ba, việc dò tìm theo nội dung văn bản do mô hình sinh ra để suy luận trạng thái luôn tiềm ẩn nguy cơ sai sót.

Về mặt thực nghiệm, chương đã trình bày kết quả đo đạc trên hệ thống chạy thật. Về mặt phương pháp, kết quả đáng chú ý nhất là việc phát hiện hai phân bố điểm truy hồi chồng lấn lên nhau hoàn toàn, nghĩa là không tồn tại bất kỳ ngưỡng nào có thể tách bạch hoàn toàn nhóm câu hỏi trả lời được với nhóm câu hỏi không trả lời được. Kết luận kéo theo là ngưỡng phải được lựa chọn dựa trên ngân sách dành cho loại lỗi không thể khắc phục, tức là lỗi chuyển ca không cần thiết, chứ không dựa trên điểm cực tiểu của tổng số lỗi, bởi hai loại lỗi không ngang giá nhau về hậu quả và loại lỗi còn lại vẫn có hai tuyến phòng thủ phía sau. Với ngưỡng 0.40 được chọn theo quy tắc này, hệ thống đạt tỉ lệ 80% gửi thẳng, 3% chuyển ca không cần thiết và 0% phản hồi dự phòng không cần thiết trên bộ dữ liệu đánh giá, qua đó vượt các chỉ tiêu KPI đã đặt ra.

Bên cạnh đó, chương cũng ghi nhận đầy đủ những hạn chế còn tồn tại về chất lượng truy hồi, xử lý ngôn ngữ và kiến trúc vận hành. Đây là cơ sở cho phần đề xuất hướng phát triển sẽ được trình bày trong phần Tổng kết.

### Tổng kết (`tong-ket.md`)

#### TỔNG KẾT › Kết quả đạt được · Đã rút gọn

*Nằm sau: «Kết quả đạt được …»*

Đồ án đã xây dựng hoàn chỉnh một hệ thống chăm sóc khách hàng tự trị dành cho cửa hàng thời trang trực tuyến, dựa trên kiến trúc đa tác tử AI với pipeline gồm bốn tác tử cố định. Hệ thống vận hành thông suốt từ đầu tới cuối trên hạ tầng thật, xử lý được lưu lượng thật và có đầy đủ công cụ giám sát đi kèm.

Dưới đây là bảng đối chiếu kết quả thu được với sáu mục tiêu đã đặt ra ở Chương 1.

| **Mục tiêu**                                | **Kết quả**                                                                                                                                                                                                                                        |
|---------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| M1 — Phân loại ý định và trích thực thể     | Đạt. Taxonomy 15 ý định nhúng trong prompt, không cần gán nhãn và huấn luyện. Trích thực thể hai đường (mô hình + biểu thức chính quy) bảo đảm mã đơn không bao giờ mất kể cả khi mô hình không khả dụng                                           |
| M2 — Truy hồi tri thức để trả lời có căn cứ | Đạt. RAG có cấu trúc trên kho tri thức canonical trong repository, chia đoạn theo section, mở rộng truy vấn, nạp lại không gián đoạn theo cơ chế blue/green                                                                                        |
| M3 — Đánh giá rủi ro và ra quyết định       | Đạt. Tác tử quyết định hoàn toàn tất định, định tuyến trên tập tám cờ chặn, không gọi mô hình và không gộp hai thang độ tin cậy. Cờ hallucination_risk do tác tử 4 phát sau bước quyết định cũng dẫn tới chuyển người, do chính tác tử 4 thực hiện |
| M4 — Sinh phản hồi sau cổng kiểm soát       | Đạt. Điểm phát ngôn duy nhất, ba nguồn căn cứ, phanh cứng chống ảo giác, ba lớp quy tắc grounding                                                                                                                                                  |
| M5 — Dashboard giám sát và hàng đợi         | Đạt. Năm module, realtime không polling, EscalationCard đầy đủ, duyệt nháp, cấu hình cổng theo từng ý định                                                                                                                                         |
| M6 — Bảo đảm tính kiểm soát                 | Đạt. Sáu dòng nhật ký kiểm toán mỗi lượt, human-in-the-loop ba mức, cổng cấu hình được, bốn lớp chống chèn chỉ dẫn                                                                                                                                 |

Về mặt định lượng, hệ thống đã vượt các chỉ tiêu KPI đặt ra. Cụ thể, 80% số lượt được gửi thẳng tới khách hàng so với mục tiêu tối thiểu 70%, 5% số lượt phải chuyển cho nhân viên so với mục tiêu dưới 30%, 3% số lượt bị chuyển ca không cần thiết so với ngân sách tối đa 5%, và không có lượt nào rơi vào phản hồi dự phòng không cần thiết trên bộ dữ liệu đánh giá.

Về mặt kỹ thuật, hệ thống gồm khoảng 7.900 dòng mã Python cho phần ứng dụng backend kèm theo gần 6.800 dòng mã kiểm thử tương ứng 387 hàm kiểm thử chạy hoàn toàn ngoại tuyến, một ứng dụng Next.js đảm nhiệm hai vai trò với khoảng 5.500 dòng TypeScript có hỗ trợ PWA, 11 phiên bản chuyển đổi lược đồ cơ sở dữ liệu, 15 tài liệu tri thức gốc và bộ script đo đạc đi kèm.

#### TỔNG KẾT › Những đóng góp đáng chú ý của đồ án · Đã rút gọn

*Nằm sau: «Những đóng góp đáng chú ý của đồ án …»*

Bên cạnh việc hoàn thành các mục tiêu chức năng, đồ án còn có bốn đóng góp về mặt thiết kế mang giá trị vượt ra ngoài phạm vi của một bài toán cụ thể.

**Thứ nhất, lựa chọn loại bỏ tác tử điều phối trung tâm cùng với bằng chứng thực nghiệm đi kèm.** Xu hướng chung của các framework đa tác tử hiện nay là điều phối động. Đồ án đã đi theo hướng ngược lại và cho thấy rằng đối với một hệ thống có ràng buộc chặt chẽ về độ trễ, chi phí và khả năng kiểm toán, một pipeline tĩnh là đủ đáp ứng phạm vi bài toán, đồng thời cho phép xác định được trần chi phí và tạo ra một đường chạy duy nhất phục vụ kiểm toán. Chi phí đánh đổi của lựa chọn này là hệ thống không xử lý được các yêu cầu phức hợp, song hạn chế đó đã được hấp thụ một cách an toàn thông qua nhánh chuyển ca cho nhân viên.

**Thứ hai, việc phân loại ba dạng ảo giác cùng ba cơ chế phòng chống tương ứng.** Phần lớn tài liệu về bám nguồn hiện nay chỉ đề cập tới dạng ảo giác bịa ra thông tin không tồn tại. Đồ án đã chỉ ra hai dạng khác nguy hiểm không kém trong ngữ cảnh chăm sóc khách hàng, gồm việc suy diễn ra thông tin phủ định từ chỗ nguồn tri thức không đề cập, và việc bịa ra hành động mà hệ thống không thực hiện được. Trong đó, dạng thứ ba đặc biệt nghiêm trọng vì tạo ra cam kết không có thật với khách hàng. Dạng ảo giác này được ngăn chặn không chỉ bằng các quy tắc trong chỉ dẫn hệ thống mà còn bằng một bất biến kiến trúc, theo đó tác tử sinh phản hồi không có quyền chuyển ca nên mọi lời hứa chuyển tiếp do tác tử này tự đưa ra đều không đúng sự thật.

**Thứ ba, ranh giới bất khả xâm phạm giữa cơ chế an toàn và cơ chế cấu hình.** Đồ án đã tách bạch rõ ràng giữa câu hỏi hệ thống có đủ căn cứ để trả lời hay không, vốn thuộc phạm vi an toàn và do mã tất định quyết định mà con người không thể can thiệp, với câu hỏi loại yêu cầu này có được phép trả lời tự động hay không, vốn thuộc phạm vi chính sách và do con người cấu hình. Nhờ cách tách này, người vận hành có thể điều chỉnh mức độ tự động hoá mà không bao giờ vô tình vô hiệu hoá cơ chế an toàn. Cách tách nêu trên không gắn với đặc thù của bài toán chăm sóc khách hàng nên có thể áp dụng cho những hệ thống AI khác cũng có cổng kiểm soát của con người.

**Thứ tư, phương pháp chọn ngưỡng theo ngân sách lỗi không cân xứng.** Phát hiện thực nghiệm về việc hai phân bố điểm truy hồi chồng lấn lên nhau hoàn toàn cho thấy giả định rằng chỉ cần chọn ngưỡng một cách khéo léo là có thể tách bạch hai nhóm câu hỏi đã không đúng trong điều kiện đo. Kết luận kéo theo là ngưỡng cần được chọn theo ngân sách dành cho loại lỗi không thể khắc phục thay vì theo điểm cực tiểu của tổng số lỗi, sau khi đã kiểm kê đầy đủ các tuyến phòng thủ phía sau từng loại lỗi. Đây là cách làm có thể áp dụng lại cho những hệ thống RAG khác có cơ chế chuyển tiếp cho con người.

#### TỔNG KẾT › Hạn chế · Đã rút gọn

*Nằm sau: «Hạn chế …»*

Bên cạnh những kết quả đã đạt được, đồ án vẫn còn một số hạn chế đã được nêu chi tiết ở mục 3.5.8. Các hạn chế này có thể tóm tắt lại thành ba nhóm như sau:

- **Về chất lượng xử lý ngôn ngữ:** Hệ thống chưa có sàn điểm cho từng đoạn tri thức nên các đoạn có điểm thấp vẫn lọt vào chỉ dẫn của tác tử sinh phản hồi; chưa xếp hạng lại được giữa các tài liệu có cùng nhãn ý định; chưa ngữ cảnh hoá được truy vấn cho các câu hỏi nối tiếp; chưa xử lý được nhiều ý định trong cùng một tin nhắn; và vẫn còn hiện tượng quá lời theo hướng khẳng định sự vắng mặt.

- **Về kiến trúc vận hành:** Hệ thống hiện chạy trên một tiến trình duy nhất do các cấu trúc điều phối đều nằm trong bộ nhớ tiến trình; cơ chế lưu điểm kiểm tra chưa bền vững nên chưa cho phép dừng luồng xử lý ở giữa đồ thị; chưa phát hiện được quản trị viên trực tuyến trên thực tế mà chỉ dựa vào khung giờ đã cấu hình sẵn; và chưa có cơ chế giải phóng những ca bị giữ.

- **Về phạm vi chức năng:** Vòng học bán tự động, tức trụ cột thứ tư của thiết kế, mới hoàn thành phần thu thập dữ liệu và chưa có phần tổng hợp dữ liệu thành đề xuất; hệ thống mới chỉ tra cứu chứ chưa thao tác được trên đơn hàng; và độ trễ phía người dùng cuối vẫn chưa được đo đạc.

#### TỔNG KẾT › Hướng phát triển · Đã rút gọn

*Nằm sau: «Hướng phát triển …»*

Trên cơ sở những hạn chế nêu trên, đồ án đề xuất hướng phát triển theo ba giai đoạn ngắn hạn, trung hạn và dài hạn. Mỗi hướng được trình bày theo cùng một khuôn: vấn đề đang chặn, cách can thiệp kèm thành phần bị tác động, và bất biến thiết kế bắt buộc giữ nguyên. Phần thứ ba là phần quan trọng nhất, bởi phần lớn cải tiến nêu ra đều chạm vào những điểm mà một thay đổi thiếu cân nhắc có thể vô hiệu hoá chính các cơ chế an toàn đã xây dựng.

**Trong ngắn hạn**, trọng tâm là hoàn thiện những phần đã được chừa sẵn chỗ trong thiết kế hiện tại:

- **Sàn điểm cho từng đoạn tri thức và bước xếp hạng lại.** Vấn đề đang chặn là cơ chế lọc hiện nay chỉ căn cứ vào điểm của kết quả đứng đầu, nên khi kết quả tốt nhất vượt ngưỡng thì các đoạn điểm thấp của cùng lượt truy hồi vẫn lọt vào chỉ dẫn của tác tử thứ tư; ngoài ra phép lọc theo nhãn ý định không phân giải được hai tài liệu cùng nhãn có điểm gần nhau, như trường hợp 0,6876 so với 0,6853 đã đo ở Chương 3. Cách làm dự kiến là can thiệp vào bước hậu xử lý truy hồi của tác tử thứ hai: đặt sàn điểm cho từng đoạn trước khi đóng gói danh sách ngữ cảnh, rồi xếp hạng lại tập đã lọc. Điều bắt buộc giữ nguyên là toàn hệ thống vẫn chỉ có duy nhất một ngưỡng số tham gia quyết định chuyển ca cho nhân viên: sàn điểm theo đoạn chỉ dùng để lọc nội dung đưa vào chỉ dẫn, không phát sinh cờ chặn mới và không tham gia định tuyến. Nếu nó thành ngưỡng thứ hai ảnh hưởng tới quyết định, hệ thống mất khả năng truy nguyên vì sao một lượt bị chuyển cho nhân viên — đúng bài học ở mục 3.3.2.

- **Ngữ cảnh hoá truy vấn cho tác tử thứ hai.** Vấn đề đang chặn là lịch sử hội thoại hiện chỉ được đưa vào tác tử thứ nhất và tác tử thứ tư, còn tác tử thứ hai vẫn truy hồi trên câu hỏi thô — trừ lượt khách đáp bằng mã đơn đứng một mình đã xử lý riêng — nên câu hỏi nối tiếp mơ hồ như "còn màu khác không" cho điểm truy hồi thấp và bị chuyển ca không cần thiết. Cách làm dự kiến là thêm bước viết lại câu hỏi thành câu hỏi độc lập dựa trên lịch sử, đặt ngay trước lời gọi tạo vector nhúng của tác tử thứ hai. Điều bắt buộc cân nhắc là bước này thêm một lời gọi mô hình vào đúng đường xử lý chính của mỗi lượt: trần chi phí mỗi lượt hiện được xác định rõ ở mức hai lời gọi sinh và một lời gọi tạo vector nhúng, nên thêm bước viết lại sẽ nâng trần đó lên, buộc phải tính lại ngân sách độ trễ và đối chiếu lại với NFR-1. Phương án giữ được trần chi phí là chỉ chạy bước viết lại khi đã phát hiện dấu hiệu câu hỏi nối tiếp.

- **Chuyển các cấu trúc điều phối ra kho chia sẻ ngoài tiến trình và bổ sung cơ chế lưu điểm kiểm tra bền vững.** Vấn đề đang chặn là trung tâm phát, các khoá đồng bộ theo khách, sổ chống trùng và bộ giới hạn tần suất đều nằm trong bộ nhớ tiến trình nên hệ thống buộc phải chạy trên đúng một tiến trình, đồng thời cơ chế lưu điểm kiểm tra chưa bền vững nên luồng xử lý chưa thể dừng thật sự ở giữa đồ thị. Cách làm dự kiến là đưa bốn cấu trúc đó ra một kho lưu trữ chia sẻ ngoài tiến trình và thay cơ chế lưu điểm kiểm tra trong bộ nhớ bằng cơ chế lưu trên nền cơ sở dữ liệu. Hai bất biến đang bảo đảm tính đúng đắn phải được giữ nguyên: nguyên tắc so sánh rồi mới ghi trên trạng thái hội thoại — mọi chuyển trạng thái vẫn phải là phép so sánh và ghi nguyên tử trên chính bản ghi hội thoại, không được thay bằng khoá phân tán ở tầng ngoài; và thứ tự ghi trước rồi mới báo khách — kết quả một lượt phải ghi xuống cơ sở dữ liệu thành công trước khi phát ra cho khách hàng, để khách không nhận được lời hứa mà hệ thống không lưu được ca tương ứng. Chỉ mục duy nhất từng phần trên bảng `message` vẫn là tuyến chống trùng cuối cùng nên phải giữ nguyên vẹn. Hướng này đồng thời là điều kiện cần của lát cắt triển khai.

- **Xử lý nhiều ý định trong cùng một tin nhắn.** Vấn đề đang chặn là cờ báo nhiều ý định hiện nằm trong tập cờ chặn, nên tin nhắn chứa hai yêu cầu bị chuyển thẳng cho nhân viên dù từng yêu cầu con đều thuộc loại hệ thống xử lý tốt. Cách làm dự kiến là tách tin nhắn thành các yêu cầu con ngay sau tác tử thứ nhất, rồi xử lý lần lượt. Điều bắt buộc giữ nguyên là mỗi yêu cầu con vẫn phải đi trọn pipeline bốn tác tử và vẫn phải chịu đúng cổng cấu hình của ý định mà nó thuộc về; tuyệt đối không được để một yêu cầu con thuộc nhóm nhạy cảm như hoàn tiền hay đổi trả đi thẳng tới khách hàng chỉ vì yêu cầu con còn lại được phép gửi thẳng. Kết quả của lượt phải là kết quả nghiêm ngặt nhất trong các kết quả thành phần.

- **Phát hiện cảm xúc của khách hàng.** Vấn đề đang chặn là thiết kế đã chừa sẵn vị trí cho cờ báo khách hàng bức xúc nhưng chức năng chưa được triển khai, nên mức ưu tiên của một ca hiện được xác định thuần theo ý định. Cách làm dự kiến là để tác tử thứ nhất phát thêm cờ này khi phân loại ý định, và cho tác tử thứ ba đọc cờ đó khi tính mức ưu tiên của phiếu chuyển tiếp. Điều bắt buộc giữ nguyên là cờ này chỉ được nâng mức ưu tiên trong hàng đợi của quản trị viên; nó không được đưa vào tập tám cờ chặn và không được tham gia định tuyến, để tác tử thứ ba giữ nguyên tính tất định. Một cờ suy ra từ giọng điệu không đủ tin cậy để quyết định có trả lời khách hay không, chỉ đủ để quyết định ca nào nên được xem trước.

- **Hoàn tất bộ số liệu đo đồng thời.** Vấn đề đang chặn là yêu cầu NFR-2 về số người dùng đồng thời hiện chỉ được kết luận đạt về mặt kiến trúc, dựa trên lập luận về mô hình bất đồng bộ và cơ chế tuần tự hoá lượt theo từng khách, chứ chưa có số liệu đo. Cách làm dự kiến là chạy trọn hai kịch bản đo đã dựng ở mục 3.5.6 và điền đủ các ô của hai bảng benchmark tương ứng, qua đó chuyển kết luận về NFR-2 từ lập luận kiến trúc thành số liệu đo được và xác nhận điểm nghẽn đã phân tích trên lý thuyết; cùng với đó là đo độ trễ phía người dùng cuối, gồm cả độ trễ mạng và thời gian dựng giao diện, để có con số đầu-cuối thực sự thay vì con số mới dừng ở biên máy chủ. Điều bắt buộc giữ nguyên là nguyên tắc trung thực của số liệu: mọi ô chưa đo phải để trống cho tới khi có phép đo thật, và điều kiện đo phải đúng như mô tả ở mục 3.5.2, vì số liệu đo trên cấu hình khác sẽ không đối chiếu được với các con số đã báo cáo.

**Trong trung hạn**, mục tiêu là hoàn thiện trụ cột thứ tư của hệ thống thông qua việc xây dựng vòng học bán tự động. Vấn đề đang chặn là dữ liệu đầu vào đã đầy đủ — sáu dòng nhật ký kiểm toán mỗi lượt đã ghi lại ý định bị chuyển cho nhân viên, các trường hợp điểm truy hồi thấp và các câu hỏi chưa có tri thức tương ứng — nhưng phần tổng hợp dữ liệu thành đề xuất và quy trình duyệt vẫn chưa được xây dựng, nên kho tri thức chỉ được cải thiện khi con người tự phát hiện thiếu sót. Cụ thể, hệ thống sẽ tổng hợp các mẫu đó để hình thành đề xuất bổ sung tài liệu mới hoặc bổ sung danh sách câu hỏi cho tài liệu sẵn có, rồi trình quản trị viên duyệt.

Kết quả đo đạc của đồ án đã cung cấp sẵn một ví dụ cụ thể cho cơ chế này. Một câu hỏi về cách phơi quần áo tránh bị giãn đã bị chuyển ca không cần thiết do tài liệu hướng dẫn bảo quản sản phẩm cho điểm khớp thấp, chỉ 0,380. Vòng học bán tự động sẽ phát hiện chính xác loại mẫu như vậy và đề xuất bổ sung câu hỏi cho tài liệu tương ứng, đúng bằng cách khắc phục mà con người đã xác định là phù hợp.

Hai điều bắt buộc giữ nguyên khi xây dựng vòng học này. Thứ nhất, mỗi đề xuất phải kèm bằng chứng truy vết được, gồm các lượt cụ thể đã dẫn tới đề xuất cùng điểm truy hồi và ý định của từng lượt, để quản trị viên duyệt trên căn cứ thay vì theo cảm tính. Thứ hai, nguyên tắc hệ thống chỉ đề xuất còn con người mới phê duyệt phải được giữ tuyệt đối: các tác tử không được tự ghi vào kho tri thức dưới bất kỳ hình thức nào, vì kho tri thức ở đây là mã nguồn được phiên bản hoá bằng Git, nên mọi thay đổi phải đi qua đúng quy trình dành cho mã nguồn và phải truy lại được ai đã thay đổi gì.

**Trong dài hạn**, đồ án hướng tới việc mở rộng phạm vi của hệ thống theo bốn hướng:

- **Tích hợp với hệ thống quản lý đơn hàng thật để thao tác được trên đơn hàng.** Vấn đề đang chặn là hệ thống mới chỉ tra cứu được trạng thái đơn, nên mọi yêu cầu dẫn tới thay đổi đơn như tạo yêu cầu đổi trả hay huỷ đơn đều phải chuyển cho nhân viên thao tác thủ công. Cách làm dự kiến là cấp cho hệ thống một tập thao tác có giới hạn trên hệ thống quản lý đơn hàng. Đây là hướng rủi ro nhất trong danh sách, bởi nó phá đúng bất biến đang chặn dạng ảo giác thứ ba: tác tử sinh phản hồi hiện không có khả năng thao tác nào nên không thể hứa sai một việc hệ thống không làm được, tức lời hứa sai bị ngăn bằng chính kiến trúc. Khi cấp quyền thao tác, bất biến đó mất đi và phải được thay bằng cơ chế tương đương: xác nhận nhiều bước trước khi thực thi, nhật ký ghi lại từng thao tác cùng người chịu trách nhiệm, và nguyên tắc mọi thao tác làm thay đổi đơn hàng đều bắt buộc đi qua cổng duyệt của con người, không có ngoại lệ do cấu hình.

- **Bộ nhớ xuyên hội thoại và hồ sơ khách hàng.** Vấn đề đang chặn là bộ nhớ hiện chỉ có phạm vi trong một hội thoại, nên hệ thống không nhận ra một khách quay lại đã từng hỏi gì hoặc từng mua sản phẩm nào. Cách làm dự kiến là bổ sung hồ sơ khách hàng tổng hợp từ các hội thoại trước và đưa vào chỉ dẫn của tác tử thứ tư để cá nhân hoá nội dung phản hồi. Điều bắt buộc giữ nguyên là nguyên tắc lịch sử hội thoại không phải nguồn bám căn cứ: hồ sơ chỉ được dùng để cá nhân hoá cách diễn đạt, không được dùng làm căn cứ cho nội dung chính sách hay trạng thái đơn hàng. Nội dung chính sách vẫn chỉ được phát ra khi có đoạn tri thức tương ứng, trạng thái đơn chỉ khi tra cứu được từ dữ liệu đơn hàng — không phải vì hội thoại trước đã từng nói như vậy.

- **Mở rộng sang các kênh giao tiếp khác.** Vấn đề đang chặn là hệ thống hiện chỉ phục vụ trên kênh chat của trang web, trong khi phần lớn lưu lượng thực tế của một cửa hàng thời trang nằm trên các nền tảng nhắn tin và mạng xã hội. Cách làm dự kiến là thêm một tầng chuyển đổi ở biên cho từng kênh, chuẩn hoá tin nhắn đến và định dạng phản hồi đi theo quy ước của kênh. Điều bắt buộc giữ nguyên là pipeline lõi không đổi: bốn tác tử, tập cờ chặn, các cổng cấu hình và điểm phát ngôn duy nhất đều giữ nguyên vị trí, mọi kênh mới đều đi qua đúng đường xử lý đó. Không kênh nào được có đường xử lý riêng, vì khi đó các bảo đảm an toàn phải kiểm chứng lại cho từng kênh.

- **Hỗ trợ đa ngôn ngữ.** Vấn đề đang chặn là toàn bộ kho tri thức, taxonomy 15 ý định và các mẫu câu cố định hiện chỉ có tiếng Việt, nên hệ thống chưa phục vụ được nhóm khách hàng quốc tế. Cách làm dự kiến là bổ sung bước nhận dạng ngôn ngữ ở biên và nhân bản các mẫu câu cố định theo từng ngôn ngữ. Điều cần lưu ý là kho tri thức cũng phải được nhân bản theo ngôn ngữ, chứ không thể dịch câu hỏi của khách rồi truy hồi trên kho tiếng Việt: kỹ thuật mở rộng truy vấn hoạt động trên chính cách diễn đạt của khách hàng, vì các điểm vector mở rộng sinh từ danh sách câu hỏi viết theo lối nói thật của người dùng, nên hiệu quả phụ thuộc vào sự tương đồng cách diễn đạt trong cùng một ngôn ngữ. Cũng như hướng mở rộng kênh, pipeline lõi không đổi, phần thêm vào chỉ nằm ở biên và ở dữ liệu tri thức.

#### TỔNG KẾT › Kết luận chung · Đã rút gọn

*Nằm sau: «Kết luận chung …»*

Đồ án đã xây dựng thành công một hệ thống chăm sóc khách hàng tự trị dựa trên kiến trúc đa tác tử AI, đạt và vượt các chỉ tiêu chức năng cũng như phi chức năng đã đặt ra ban đầu.

Qua quá trình thực hiện, bài học quan trọng nhất mà em rút ra được không nằm ở kỹ thuật ghép nối các thành phần AI với nhau. Khó khăn lớn nhất nằm ở việc xác định ranh giới giữa những quyết định nên giao cho mô hình ngôn ngữ và những quyết định bắt buộc phải do mã tất định đảm nhiệm. Trên thực tế, mô hình ngôn ngữ thực hiện rất tốt việc hiểu câu hỏi và diễn đạt câu trả lời, nhưng lại không đủ tin cậy khi phải trả lời hai câu hỏi khác là có nên trả lời khách hàng hay không và được phép cam kết những gì với khách hàng. Về cơ bản, đồ án này là một nỗ lực nhằm đặt ranh giới đó vào đúng vị trí của nó.

Nhìn tổng thể, nguyên tắc xuyên suốt của đồ án là chuyển ca cho nhân viên trong mọi trường hợp hệ thống không đủ căn cứ. Nguyên tắc này thoạt nhìn có vẻ khiêm tốn đối với một hệ thống mang tính tự trị, nhưng chính nó lại cho phép hệ thống đạt mức tự động hoá 80% mà vẫn kiểm soát được tỉ lệ sai sót, thay vì đạt một tỉ lệ cao hơn trên nền tảng không đo lường được. Đối với một hệ thống trao đổi trực tiếp với khách hàng, đây là sự đánh đổi hoàn toàn xứng đáng.

### Phụ lục (`phu-luc.md`)

#### PHỤ LỤC › A. Đặc tả chi tiết các Use Case còn lại · Đã rút gọn

*Nằm sau: «A. Đặc tả chi tiết các Use Case còn lại …»*

Sáu use case dưới đây đã được liệt kê ở mục 2.3.1 nhưng chưa được đặc tả trong thân bài, bởi mục 2.3.2 chỉ đặc tả hai use case tiêu biểu là UC-03 và UC-11; sáu use case còn lại được đặc tả đầy đủ trong phần này. Dưới đây lần lượt là các bảng đặc tả chi tiết của từng use case (Bảng PL.1 đến Bảng PL.6).

#### PHỤ LỤC › A. Đặc tả chi tiết các Use Case còn lại · Đã rút gọn

*Nằm sau: «Bảng PL.1. Đặc tả UC-04 — Cung cấp mã đơn khi được hỏi lại …»*

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Cung cấp mã đơn khi được hỏi lại (UC-04) |
| Mô tả | Cho phép khách hàng hoàn tất một yêu cầu liên quan tới đơn hàng bằng cách gửi mã đơn ở lượt tiếp theo, sau khi hệ thống đã hỏi lại ở lượt trước. Use case này thể hiện cơ chế nối lượt: hệ thống nhớ ý định của lượt trước và khôi phục nó mà không cần khách nhắc lại toàn bộ câu hỏi. |
| Tác nhân | Khách hàng (chính) |
| Tiền điều kiện | Hội thoại đang ở trạng thái chờ khách trả lời, và ý định của lượt trước đã được lưu cùng trạng thái đó. |
| Hậu điều kiện | Ý định gốc được khôi phục, mã đơn được ghi vào tập thực thể, và lượt tiếp tục chạy như một lượt bình thường. Sáu dòng nhật ký kiểm toán được ghi với cùng khoá lượt. |
| Luồng sự kiện chính | 1. Ở lượt trước, hệ thống đã hỏi khách cung cấp mã đơn và ghi trạng thái chờ khách trả lời kèm ý định gốc. 2. Khách gửi một tin nhắn chỉ chứa mã đơn. 3. Hệ thống nạp trạng thái và ý định của lượt trước trước khi chạy pipeline. 4. Tác tử 1 nhận ra ngữ cảnh nối lượt, bỏ qua lời gọi mô hình và khôi phục tất định ý định gốc cùng mã đơn, độ tin cậy đặt bằng 1.0. 5. Tác tử 2 truy hồi tri thức bằng **câu hỏi gốc lấy từ lịch sử** chứ không bằng dãy số, đồng thời tra đơn hàng trong phạm vi tài khoản đang đăng nhập. 6. Pipeline tiếp tục như lượt thường và trả kết quả cho khách. |
| Luồng thay thế 4a | Tin nhắn không phải mã đơn hợp lệ mà là một câu hỏi mới → hệ thống xử lý như một lượt mới, ý định cũ bị bỏ. |
| Luồng thay thế 5a | Tra đơn không ra kết quả → hệ thống trả câu thông báo cố định về việc không tìm thấy đơn, không gọi mô hình sinh. |
| Luồng thay thế 5b | Khách đã được hỏi lại ở lượt trước mà vẫn không cung cấp được mã đơn dùng được → chuyển ca cho nhân viên thay vì hỏi lại lần hai. |
| Luồng sự kiện ngoại lệ | 5c. Cơ sở dữ liệu lỗi khi tra đơn → hệ thống phát cờ đơn-chưa-xác-định dẫn tới chuyển người, và **không** nói "không tìm thấy đơn", bởi việc tra cứu bị lỗi khác hẳn việc tra cứu trả về rỗng. 4c. Lời gọi mô hình hết thời gian chờ ở lượt nối → hệ thống phát cờ mô-hình-không-khả-dụng dẫn tới chuyển người, nhưng mã đơn vẫn được giữ lại vì bước trích bằng biểu thức chính quy chạy ở mọi nhánh, không phụ thuộc lời gọi mô hình. |
| Ghi chú thiết kế | Đây là use case đã từng gây hai lỗi thật, trình bày ở mục 2.7.3: mô hình xếp dãy số trơ vào nhóm "khác" dẫn tới chuyển người oan, và điểm truy hồi của một dãy số so với kho tri thức rất thấp cũng dẫn tới chuyển người oan. Cả hai được xử lý bằng bước khôi phục tất định ở luồng chính bước 4 và bước 5. Riêng cơ chế đếm số lần tra cứu thất bại — căn cứ của luồng thay thế 5b, tức lý do lần thứ hai không hỏi lại nữa mà chuyển ca — được trình bày ở mục 3.3.6, cùng lý do không dò các con số trong lời khách mà so khớp nguyên văn câu thông báo cố định. |

#### PHỤ LỤC › A. Đặc tả chi tiết các Use Case còn lại · Đã rút gọn

*Nằm sau: «Bảng PL.2. Đặc tả UC-06 — Yêu cầu gặp nhân viên …»*

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Yêu cầu gặp nhân viên (UC-06) |
| Mô tả | Cho phép khách hàng chủ động yêu cầu được nói chuyện với người thật, bất kể hệ thống có đủ căn cứ để trả lời hay không. |
| Tác nhân | Khách hàng (chính) |
| Tiền điều kiện | Hội thoại đang ở phía tác tử, chưa có nhân viên tiếp quản. |
| Hậu điều kiện | Hội thoại chuyển sang hàng đợi người kèm phiếu chuyển tiếp; khách nhận thông báo chuyển tiếp thay vì câu trả lời. |
| Luồng sự kiện chính | 1. Khách gửi tin nhắn thể hiện mong muốn gặp người thật. 2. Tác tử 1 nhận diện và phát cờ yêu-cầu-gặp-người. 3. Tác tử 2 vẫn chạy bình thường nhưng kết quả không được dùng để trả lời. 4. Tác tử 3 thấy cờ này nằm trong tập cờ chặn nên quyết định chuyển người, không đi qua cổng cấu hình. 5. Tác tử 4 phát thông báo chuyển tiếp cố định, không gọi mô hình sinh. 6. Hệ thống ghi trạng thái hàng đợi và phiếu chuyển tiếp trong cùng một giao dịch, commit xong mới gửi khung thông báo cho khách. |
| Luồng thay thế 5a | Thời điểm hiện tại nằm ngoài khung giờ hỗ trợ → thông báo dùng bản ngoài giờ, nêu rõ thời gian nhân viên sẽ phản hồi. |
| Luồng sự kiện ngoại lệ | 6a. Bước ghi cơ sở dữ liệu thất bại cả sau một lần thử lại → hệ thống **không** gửi thông báo chuyển tiếp, mà gửi một câu không kèm cam kết nào. Lý do: hứa với khách rằng ca đã được chuyển cho nhân viên trong khi ca chưa vào được hàng đợi là một cam kết giả, và khách sẽ chờ một phản hồi không bao giờ tới. |
| Ghi chú thiết kế | Cờ yêu-cầu-gặp-người nằm trong tập cờ chặn nên **không thể bị cổng cấu hình ghi đè**. Đây là biểu hiện trực tiếp của bất biến ở mục 2.5.1: cổng cấu hình chỉ can thiệp được vào ranh giới giữa gửi thẳng và duyệt nháp, không can thiệp được vào quyết định chuyển người. |

#### PHỤ LỤC › A. Đặc tả chi tiết các Use Case còn lại · Đã rút gọn

*Nằm sau: «Bảng PL.3. Đặc tả UC-13 — Duyệt hoặc từ chối nháp phản hồi …»*

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Duyệt hoặc từ chối nháp phản hồi (UC-13) |
| Mô tả | Cho phép quản trị viên xem nháp phản hồi do tác tử sinh cho một ý định nhạy cảm, rồi quyết định gửi nguyên văn, sửa trước khi gửi, hoặc từ chối và tự xử lý. |
| Tác nhân | Quản trị viên (chính) |
| Tiền điều kiện | Đã đăng nhập với vai trò quản trị; tồn tại hội thoại ở trạng thái chờ duyệt kèm nháp trong phiếu chuyển tiếp. |
| Hậu điều kiện | Nếu duyệt: nháp trở thành tin nhắn thật gửi cho khách, hội thoại về trạng thái đã trả lời. Nếu từ chối: hội thoại vào hàng đợi người. Hành động được ghi vào nhật ký kiểm toán. |
| Luồng sự kiện chính | 1. Quản trị viên mở hội thoại ở trạng thái chờ duyệt. 2. Giao diện hiển thị phiếu chuyển tiếp kèm nháp trong một ô văn bản sửa được. 3. Quản trị viên đọc nháp cùng các nguồn tri thức mà tác tử đã dùng. 4. Quản trị viên bấm Duyệt. 5. Hệ thống kiểm tra trạng thái hội thoại vẫn đúng như lúc đọc, ghi tin nhắn và cập nhật trạng thái trong cùng một giao dịch. 6. Khách nhận nội dung phản hồi. |
| Luồng thay thế 4a | Quản trị viên sửa nội dung nháp rồi mới bấm Duyệt → nội dung đã sửa là nội dung được gửi; bản nháp gốc vẫn còn trong phiếu để đối chiếu. |
| Luồng thay thế 4b | Quản trị viên bấm Từ chối → hội thoại chuyển sang hàng đợi người, khách không nhận nội dung nào của nháp. |
| Luồng thay thế 5a | Hội thoại đã bị người khác xử lý trong lúc đang đọc → hệ thống trả lỗi xung đột, giao diện tải lại trạng thái mới. |
| Luồng sự kiện ngoại lệ | 5b. Nháp đã bị thay đổi kể từ lúc quản trị viên mở màn hình → hệ thống trả lỗi xung đột với lý do nháp đã cũ và tải lại nội dung mới, nhờ đó tránh được việc duyệt một nội dung khác với nội dung vừa đọc. 4c. Quản trị viên bị hạ quyền giữa phiên → thao tác bị từ chối, vì vai trò được đọc lại từ cơ sở dữ liệu chứ không lấy từ mã thông báo. |
| Ghi chú thiết kế | Trong suốt thời gian chờ duyệt, khách **chỉ nhận một tín hiệu chờ, không nhận bất kỳ phần nội dung nào của nháp**. Điều này giữ đúng nguyên tắc điểm phát ngôn duy nhất ở mục 2.2.2: nội dung chỉ rời khỏi hệ thống sau khi có người duyệt. |

#### PHỤ LỤC › A. Đặc tả chi tiết các Use Case còn lại · Đã rút gọn

*Nằm sau: «Bảng PL.4. Đặc tả UC-19 — Cấu hình cổng theo từng ý định …»*

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Cấu hình cổng theo từng ý định (UC-19) |
| Mô tả | Cho phép quản trị viên quyết định với từng ý định trong bảng phân loại rằng phản hồi được gửi thẳng cho khách hay phải qua bước duyệt nháp. |
| Tác nhân | Quản trị viên (chính) |
| Tiền điều kiện | Đã đăng nhập với vai trò quản trị. |
| Hậu điều kiện | Quy tắc mới có hiệu lực từ lượt kế tiếp; thay đổi được ghi vào nhật ký kiểm toán. |
| Luồng sự kiện chính | 1. Quản trị viên mở màn hình cấu hình cổng. 2. Giao diện hiển thị hai công tắc mức hệ thống và bảng quy tắc cho từng ý định. 3. Quản trị viên bật hoặc tắt chế độ gửi thẳng cho một ý định. 4. Hệ thống lưu quy tắc và xác nhận. 5. Lượt kế tiếp của khách đọc snapshot cấu hình mới. |
| Luồng thay thế 3a | Quản trị viên tắt công tắc trả lời tự động ở mức hệ thống → mọi ý định đều chuyển sang chế độ duyệt nháp, bất kể quy tắc riêng của từng ý định. |
| Luồng sự kiện ngoại lệ | 5a. Lượt kế tiếp không đọc được cấu hình cổng do lỗi cơ sở dữ liệu → hệ thống gửi thẳng câu trả lời thay vì giữ nháp, để hội thoại không bị đình trệ vì một sự cố của tầng cấu hình. |
| Ghi chú thiết kế | Ngưỡng truy hồi **không** nằm trên màn hình cấu hình cổng, và cũng **không** nằm trong bảng `gate_config`: cột tương ứng đã bị migration `aadfd438121a` xoá, còn `schemas/gate.py` ghi rõ lược đồ cấu hình không có trường `retrieval_threshold`. Ngưỡng này là một giá trị **đo được**, đọc từ biến môi trường `RETRIEVAL_THRESHOLD` (xem Bảng PL.9). Đây chính là ranh giới ở mục 2.5.1: ngưỡng thuộc về cơ chế an toàn, không thuộc quyền cấu hình của con người, nên nó được đặt ở tầng triển khai chứ không đưa lên giao diện quản trị — muốn thay thì phải đổi biến môi trường và đo lại, chứ không thể nới bằng một cú bấm chuột trong lúc hệ thống đang chạy. |

#### PHỤ LỤC › A. Đặc tả chi tiết các Use Case còn lại · Đã rút gọn

*Nằm sau: «Bảng PL.4. Đặc tả UC-19 — Cấu hình cổng theo từng ý định …»*

Hai use case còn lại thuộc nhóm xác thực. Chúng được đưa xuống phụ lục vì luồng của chúng không mang đặc thù của bài toán chăm sóc khách hàng tự trị: một biểu mẫu, một lần băm mật khẩu và một cặp mã thông báo là nghiệp vụ chung của mọi ứng dụng web, nên nếu đặt ở Chương 2 thì chúng sẽ chiếm chỗ của những phần thực sự làm nên thiết kế, tức là pipeline bốn tác tử và các cơ chế an toàn. Tuy vậy, hai use case này vẫn cần được đặc tả đầy đủ, bởi chúng là nền tảng của ràng buộc tra cứu đơn hàng theo phạm vi khách hàng: nếu không có một danh tính đáng tin cậy gắn với mỗi hội thoại thì cơ chế tra đơn trong phạm vi tài khoản ở mục 2.4.3 mất hết ý nghĩa. Dưới đây lần lượt là hai bảng đặc tả của nhóm use case này (Bảng PL.5 và Bảng PL.6).

#### PHỤ LỤC › A. Đặc tả chi tiết các Use Case còn lại · Đã rút gọn

*Nằm sau: «Bảng PL.5. Đặc tả UC-01 — Đăng ký tài khoản …»*

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Đăng ký tài khoản (UC-01) |
| Mô tả | Cho phép một người chưa có tài khoản tự tạo tài khoản khách hàng để bắt đầu hội thoại. Tài khoản tạo qua luồng này luôn nhận vai trò khách hàng; tài khoản quản trị chỉ được tạo bằng script gieo dữ liệu, không có đường đăng ký nào cấp được vai trò quản trị. |
| Tác nhân | Khách hàng (chính) |
| Tiền điều kiện | Chưa đăng nhập; địa chỉ email dự định dùng chưa gắn với tài khoản nào. |
| Hậu điều kiện | Một bản ghi người dùng mới tồn tại với vai trò khách hàng và mật khẩu đã băm; phiên làm việc được mở ngay nhờ hai mã thông báo đã ghi vào cookie; hệ thống trả mã trạng thái 201. |
| Luồng sự kiện chính | 1. Khách mở trang đăng ký. 2. Khách nhập địa chỉ email và mật khẩu. 3. Hệ thống kiểm tra giới hạn tần suất theo địa chỉ IP, mặc định năm lần mỗi sáu mươi giây. 4. Hệ thống chuẩn hoá email về chữ thường và cắt khoảng trắng hai đầu. 5. Hệ thống kiểm tra email chưa tồn tại trong bảng người dùng. 6. Hệ thống băm mật khẩu bằng bcrypt, cắt chuỗi ở bảy mươi hai byte đầu và chạy trong threadpool để không chặn vòng lặp sự kiện. 7. Hệ thống tạo bản ghi người dùng với vai trò khách hàng. 8. Hệ thống phát một mã thông báo truy cập và một mã thông báo làm mới, rồi ghi cả hai vào hai cookie chỉ đọc được từ phía máy chủ. 9. Hệ thống trả mã trạng thái 201 kèm danh tính vừa tạo. |
| Luồng thay thế 5a | Email đã tồn tại → hệ thống báo lỗi trùng email và **không tiết lộ thêm bất kỳ thông tin nào** về tài khoản đó, chẳng hạn thời điểm tạo hay vai trò. |
| Luồng sự kiện ngoại lệ | 3a. Vượt giới hạn tần suất → hệ thống trả mã 429 kèm tiêu đề `Retry-After` cho biết phải chờ bao nhiêu giây. 7a. Cơ sở dữ liệu lỗi → giao dịch được huỷ toàn bộ, không có tài khoản nào bị tạo dở và cũng không có cookie nào được ghi. |
| Ghi chú thiết kế | Mật khẩu được cắt ở tầng byte **trước** khi băm, nhờ đó thao tác băm và thao tác xác minh luôn nhất quán với nhau; đây cũng là lý do thư viện bcrypt được dùng trực tiếp thay vì qua lớp bao trung gian đã ngừng bảo trì. Việc bcrypt chạy trong threadpool là bắt buộc chứ không phải tối ưu hoá tuỳ chọn, bởi hệ thống chạy trên một worker duy nhất nên một lần băm chạy thẳng trong hàm bất đồng bộ sẽ làm mọi kênh chat đang mở đứng lại trong khoảng thời gian đó. |

#### PHỤ LỤC › A. Đặc tả chi tiết các Use Case còn lại · Đã rút gọn

*Nằm sau: «Bảng PL.6. Đặc tả UC-08 — Đăng nhập và duy trì phiên làm việc …»*

| **Thuộc tính** | **Nội dung** |
|---|---|
| Tên use case | Đăng nhập và duy trì phiên làm việc (UC-08) |
| Mô tả | Cho phép người dùng mở một phiên làm việc và giữ phiên đó liên tục cho tới khi hết hạn dài. Use case này dùng chung cho **cả khách hàng và quản trị viên**, vì cơ chế xác thực của hai vai trò là một; điểm khác duy nhất là vai trò được đọc từ cơ sở dữ liệu sau khi đăng nhập, và vai trò đó quyết định người dùng được vào màn hình chat hay vào dashboard quản trị. |
| Tác nhân | Khách hàng, Quản trị viên (chính) |
| Tiền điều kiện | Tài khoản đã tồn tại và chưa bị xoá. |
| Hậu điều kiện | Hai mã thông báo được ghi vào cookie; giao diện biết vai trò của người dùng và điều hướng tương ứng; phiên tự gia hạn ở nền cho tới khi mã thông báo làm mới hết hạn. |
| Luồng sự kiện chính | 1. Người dùng gửi địa chỉ email và mật khẩu. 2. Hệ thống kiểm tra giới hạn tần suất theo địa chỉ IP, mười lần mỗi sáu mươi giây, và theo địa chỉ email, năm lần mỗi sáu mươi giây. 3. Hệ thống tra người dùng theo email đã chuẩn hoá. 4. Hệ thống xác minh mật khẩu bằng bcrypt trong threadpool. 5. Hệ thống phát mã thông báo truy cập hạn ba mươi phút và mã thông báo làm mới hạn bảy ngày. 6. Hệ thống ghi hai cookie chỉ đọc được từ phía máy chủ, với thuộc tính bảo mật và thuộc tính phạm vi gửi cùng-site được **suy dẫn theo môi trường** chứ không đặt cứng trong mã. 7. Giao diện tải hồ sơ người dùng và chuyển hướng theo vai trò. |
| Luồng thay thế 7a | Mã thông báo truy cập hết hạn giữa phiên → một yêu cầu bất kỳ nhận mã 401; lớp bọc yêu cầu ở phía giao diện tự gọi điểm cuối làm mới bằng cookie làm mới, hệ thống phát lại **cả hai** mã thông báo và ghi lại cookie, sau đó lớp bọc chạy lại đúng yêu cầu vừa thất bại **một lần**. Người dùng không thấy phiên bị ngắt. |
| Luồng thay thế 7b | Nhiều yêu cầu cùng nhận mã 401 gần như đồng thời → chỉ **một** lần làm mới được thực hiện, các yêu cầu còn lại cùng chờ trên lời hứa của lần làm mới đó rồi mới chạy lại. |
| Luồng sự kiện ngoại lệ | 7c. Mã thông báo làm mới hết hạn hoặc sai → hệ thống trả 401 và giao diện chuyển về trang đăng nhập. 3a. Email không tồn tại → hệ thống **vẫn băm một hash giả** đúng một lần để thời gian phản hồi không tiết lộ email nào có trong hệ thống, rồi trả cùng một thông báo lỗi như trường hợp sai mật khẩu. 2a. Vượt giới hạn tần suất → trả 429 kèm tiêu đề `Retry-After`. 6a. Mở kết nối WebSocket với mã thông báo đã bị thu hồi hoặc với vai trò đã bị hạ → hệ thống đóng kết nối với mã 4401. 6b. Cơ sở dữ liệu lỗi đúng lúc xác minh vai trò → hệ thống đóng kết nối với mã 1011 để giao diện hiểu đây là sự cố phía máy chủ và nối lại theo cơ chế giãn cách, thay vì tưởng phiên đã hết hạn và thôi nối lại. |
| Ghi chú thiết kế | Ba điểm đáng nhấn. **Thứ nhất**, hai mã thông báo nằm trong cookie chỉ đọc được từ phía máy chủ chứ không nằm trong bộ nhớ cục bộ của trình duyệt, nên mã JavaScript trên trang không đọc được chúng; một lỗ hổng chèn mã ở phía giao diện vì thế không lấy được mã thông báo. Cái giá phải trả là hệ thống buộc phải xử lý đúng hai thuộc tính bảo mật và phạm vi gửi cùng-site cho tình huống triển khai khác tên miền, và đó là việc của ba biến môi trường ở Bảng PL.9. **Thứ hai**, vai trò luôn được đọc lại từ cơ sở dữ liệu chứ không lấy từ trường vai trò trong mã thông báo, nên thao tác thu hồi quyền có hiệu lực ngay; riêng kênh WebSocket quản trị đọc lại vai trò ở **mỗi tin nhắn**, nhờ đó một quản trị viên bị hạ quyền giữa phiên không nhắn được cho khách nữa dù kết nối vẫn đang mở. **Thứ ba**, bước bắt tay WebSocket ưu tiên đọc cookie mã thông báo truy cập và chỉ dùng tham số trên đường dẫn làm phương án dự phòng cho những client không gửi được cookie. |

#### PHỤ LỤC › B. Biểu đồ use case phân rã · Đã rút gọn

*Nằm sau: «B. Biểu đồ use case phân rã …»*

Biểu đồ use case tổng quát ở Hình 2.3 cho thấy đủ hai mươi use case nhưng không cho thấy quan hệ giữa chúng. Hai biểu đồ dưới đây phân rã theo từng nhóm tác nhân để làm rõ các quan hệ bao gồm và mở rộng, cũng như thứ tự phụ thuộc giữa các use case trong cùng một nghiệp vụ.

#### PHỤ LỤC › B. Biểu đồ use case phân rã › Phân rã use case nhóm khách hàng · Đã rút gọn

*Nằm sau: «Phân rã use case nhóm khách hàng …»*

Nhóm khách hàng gồm sáu use case từ UC-02 tới UC-07, và giữa chúng có một trật tự phụ thuộc rõ ràng. Use case UC-02, mở hội thoại và gửi tin nhắn, là use case gốc mà mọi use case còn lại của nhóm đều bắt nguồn từ đó. Use case UC-03, nhận phản hồi tự động, là kết quả thường gặp nhất của UC-02, bởi phần lớn lượt hội thoại kết thúc ngay ở nhánh trả lời tự động. Use case UC-04, cung cấp mã đơn khi được hỏi lại, mở rộng UC-03 theo quan hệ **extend** chứ không phải quan hệ bao gồm, vì nó chỉ xảy ra trong trường hợp hệ thống phát hiện thiếu một thực thể bắt buộc và quyết định hỏi lại thay vì trả lời. Use case UC-05, tra trạng thái đơn hàng, bao gồm bước xác thực danh tính theo quan hệ **include**, bởi mọi lần tra cứu đều bị giới hạn trong phạm vi tài khoản đang đăng nhập nên không có đường nào tra đơn mà bỏ qua bước xác thực. Use case UC-06, yêu cầu gặp nhân viên, được vẽ như một đường thoát luôn khả dụng, gắn trực tiếp vào UC-02 và không phụ thuộc vào việc hệ thống có đủ căn cứ trả lời hay không. Cuối cùng, use case UC-07, xem lại lịch sử hội thoại, có tiền điều kiện là đã đăng nhập và không tham gia vào luồng xử lý của một lượt nào. Dưới đây là biểu đồ phân rã của nhóm này (Hình PL.1).

#### PHỤ LỤC › B. Biểu đồ use case phân rã › Phân rã use case nhóm quản trị viên · Đã rút gọn

*Nằm sau: «Phân rã use case nhóm quản trị viên …»*

Nhóm quản trị viên gồm mười hai use case từ UC-09 tới UC-20, và cách đọc tự nhiên nhất là theo vòng đời của một ca chuyển tiếp. Hai use case UC-09 và UC-10 nằm ở đầu vòng đời, phục vụ việc xem hàng đợi và lọc hàng đợi theo trạng thái hoặc theo mức ưu tiên. Use case UC-11, nhận ca từ hàng đợi, là **điểm vào của mọi nghiệp vụ xử lý**: chỉ sau khi nhận ca thì quản trị viên mới thực hiện được UC-12, chat trực tiếp với khách hàng, và UC-16, đóng ca; vì vậy hai use case này được vẽ như hai use case bị UC-11 kéo theo. Ba use case UC-13, UC-14 và UC-15 là ba kết cục khác nhau của cùng một nghiệp vụ duyệt nháp, nên chúng được vẽ chung trong một khối để người đọc thấy ngay rằng chúng loại trừ nhau chứ không nối tiếp nhau. Hai use case UC-17 và UC-18 thuộc nhóm quản lý kho tri thức, gồm việc tải tài liệu lên và việc nạp lại kho; chúng nằm ngoài vòng đời của một ca. Hai use case UC-19 và UC-20 là cấu hình cổng và xem báo cáo, cũng nằm ngoài vòng đời của một ca. Cần nêu rõ rằng **mọi use case của nhóm này đều có cùng một tiền điều kiện là đã đăng nhập với vai trò quản trị**, nên tiền điều kiện đó được ghi một lần ở ranh giới của biểu đồ thay vì lặp lại ở từng use case. Dưới đây là biểu đồ phân rã của nhóm này (Hình PL.2).

#### PHỤ LỤC › C. Biểu đồ tuần tự bổ sung · Đã rút gọn

*Nằm sau: «C. Biểu đồ tuần tự bổ sung …»*

Mục 2.7 đã trình bày năm biểu đồ tuần tự cho năm luồng chính của pipeline. Hai biểu đồ dưới đây bổ sung hai luồng không thuộc pipeline nhưng có vai trò quyết định đối với tính đúng đắn của hệ thống: luồng xác thực, vốn là nền tảng của ràng buộc tra cứu theo phạm vi khách, và luồng tiếp quản ca, vốn là chỗ duy nhất mà con người và tác tử cùng ghi vào một hội thoại.

#### PHỤ LỤC › C. Biểu đồ tuần tự bổ sung › Luồng đăng nhập và làm mới phiên · Đã rút gọn

*Nằm sau: «Luồng đăng nhập và làm mới phiên …»*

Luồng bắt đầu khi giao diện gửi địa chỉ email và mật khẩu tới điểm cuối đăng nhập. Back-end kiểm tra hai bộ đếm giới hạn tần suất, một theo địa chỉ IP và một theo địa chỉ email, rồi tra người dùng theo email đã chuẩn hoá và xác minh mật khẩu bằng bcrypt chạy trong threadpool. Khi mật khẩu đúng, back-end phát một mã thông báo truy cập và một mã thông báo làm mới, sau đó ghi cả hai vào hai cookie chỉ đọc được từ phía máy chủ, với thuộc tính bảo mật và thuộc tính cùng-site suy dẫn theo biến môi trường của môi trường đang chạy. Giao diện nhận phản hồi, tải hồ sơ người dùng và điều hướng theo vai trò.

Nhánh thứ hai của biểu đồ mô tả việc làm mới phiên, và đây là phần đáng vẽ nhất vì nó diễn ra hoàn toàn ở nền. Khi một yêu cầu bất kỳ nhận về mã 401, lớp bọc yêu cầu ở phía giao diện gọi điểm cuối làm mới kèm cookie làm mới; back-end giải mã mã thông báo, **kiểm tra trường loại đúng là loại làm mới** để một mã thông báo làm mới không dùng thay mã thông báo truy cập được, rồi phát lại **cả hai** mã thông báo và ghi lại cookie. Sau khi làm mới thành công, lớp bọc chạy lại đúng yêu cầu đã thất bại một lần duy nhất. Biểu đồ cần thể hiện rõ cơ chế một lần làm mới dùng chung: nếu nhiều yêu cầu cùng nhận mã 401 gần như đồng thời thì chúng cùng chờ trên một lời hứa duy nhất, nên chỉ có một lời gọi làm mới được phát ra chứ không phải mỗi yêu cầu một lời gọi.

Phần cuối của biểu đồ mô tả bước bắt tay WebSocket để cho thấy cơ chế cookie hoạt động thống nhất trên cả hai loại kết nối. Trình duyệt tự gửi cookie mã thông báo truy cập kèm theo yêu cầu nâng cấp giao thức; back-end đọc cookie trước và chỉ đọc tham số trên đường dẫn khi không có cookie, sau đó đọc vai trò từ cơ sở dữ liệu thay vì tin vào trường vai trò trong mã thông báo, rồi mới chấp nhận kết nối. Dưới đây là biểu đồ của luồng này (Hình PL.3).

#### PHỤ LỤC › C. Biểu đồ tuần tự bổ sung › Luồng tiếp quản ca và chat trực tiếp với khách hàng · Đã rút gọn

*Nằm sau: «Luồng tiếp quản ca và chat trực tiếp với khách hàng …»*

Luồng bắt đầu khi quản trị viên mở hàng đợi chuyển tiếp và đọc phiếu chuyển tiếp của một ca, gồm tóm tắt tin nhắn kích hoạt, ý định, các thực thể, danh sách nguồn tri thức kèm điểm số và lý do chuyển tiếp. Quản trị viên bấm nhận ca. Back-end không ghi thẳng mà thực hiện một thao tác cập nhật có điều kiện: câu lệnh cập nhật chỉ ghi khi trạng thái của hội thoại vẫn đúng như trạng thái lúc quản trị viên đọc, và hệ thống chỉ coi thao tác là thành công khi số dòng bị ảnh hưởng đúng bằng một. Nếu số dòng bị ảnh hưởng bằng không thì back-end trả về mã lỗi xung đột 409.

Tình huống cần nhấn mạnh trên biểu đồ là hai quản trị viên bấm nhận cùng một ca gần như đồng thời. Khi đó chỉ một người thành công, người còn lại nhận mã 409 và giao diện của người đó tải lại trạng thái mới để thấy ca đã có người giữ; nhờ vậy không bao giờ có hai người cùng tưởng mình đang xử lý một ca. Sau khi một người nhận ca, cổng chặn theo trạng thái làm cho pipeline tự động **không chạy nữa** trên hội thoại đó, và mọi tin nhắn tiếp theo của khách được định tuyến thẳng tới quản trị viên đang giữ ca thông qua trung tâm phát trong tiến trình. Chiều ngược lại cũng được kiểm soát: chỉ người đang giữ ca gửi được tin vào hội thoại, còn quản trị viên khác gửi vào sẽ nhận phản hồi báo không được phân công.

Một chi tiết bảo vệ dữ liệu cá nhân cần vẽ rõ trên biểu đồ là khung tin gửi tới phía khách hàng **không mang định danh tài khoản nhân viên**: khách chỉ thấy tin nhắn đến từ phía cửa hàng, không thấy ai đang trả lời mình. Luồng kết thúc khi quản trị viên bấm đóng ca; thao tác này cũng đi qua cùng cơ chế cập nhật có điều kiện, và giống mọi thao tác quản trị khác, nó sinh ra một dòng nhật ký kiểm toán với nút ghi là `admin`. Dưới đây là biểu đồ của luồng này (Hình PL.4).

#### PHỤ LỤC › D. Sơ đồ lớp theo từng miền dữ liệu · Đã rút gọn

*Nằm sau: «D. Sơ đồ lớp theo từng miền dữ liệu …»*

Sơ đồ lớp tổng ở Hình 2.15 gồm ba lớp nền và tám lớp thực thể, nên khi vẽ đầy đủ cả thuộc tính thì hình trở nên rậm và các đường liên kết khó theo. Hai sơ đồ dưới đây tách cùng tập lớp đó theo miền dữ liệu, mỗi sơ đồ bốn lớp, để người đọc theo được quan hệ giữa các lớp trong cùng một miền.

#### PHỤ LỤC › D. Sơ đồ lớp theo từng miền dữ liệu › Miền hội thoại · Đã rút gọn

*Nằm sau: «Miền hội thoại …»*

Miền hội thoại gồm bốn lớp `User`, `Conversation`, `Message` và `Order`. Lớp `User` là lớp trung tâm của miền: một `User` có nhiều `Conversation` và đồng thời có nhiều `Order`. Lớp `Conversation` có nhiều `Message`, và quan hệ này được khai báo kèm cơ chế xoá lan truyền cho bản ghi con mồ côi cùng thứ tự sắp xếp theo thời điểm tạo, nhờ đó lịch sử hội thoại nạp ra luôn đúng trình tự mà không cần câu lệnh sắp xếp riêng ở tầng truy vấn. Liên kết từ `Order` tới `User` qua khoá chủ đơn `customer_id` chính là cơ sở kỹ thuật của ràng buộc tra cứu đơn hàng theo phạm vi khách hàng: hàm tra đơn luôn nhận thêm định danh khách hàng làm tham số, nên một mã đơn của người khác và một mã đơn không tồn tại trả về cùng một kết quả. Riêng lớp `Conversation` dùng thêm lớp trộn dấu thời gian để có cả hai mốc tạo và cập nhật, trong khi ba lớp còn lại chỉ cần mốc tạo. Dưới đây là sơ đồ lớp của miền này (Hình PL.5).

#### PHỤ LỤC › D. Sơ đồ lớp theo từng miền dữ liệu › Miền cấu hình và hỗ trợ · Đã rút gọn

*Nằm sau: «Miền cấu hình và hỗ trợ …»*

Miền cấu hình và hỗ trợ gồm bốn lớp `GateConfig`, `GateIntentRule`, `AuditLog` và `KnowledgeDocument`. Hai lớp cấu hình **không** dùng lớp trộn khoá UUID như các lớp nghiệp vụ, bởi khoá của chúng mang ý nghĩa nghiệp vụ chứ không phải một định danh vô nghĩa: lớp `GateConfig` luôn chỉ có một dòng duy nhất với khoá là số nguyên 1, còn lớp `GateIntentRule` lấy chính tên của ý định làm khoá chính nên mỗi ý định trong bảng phân loại có đúng một quy tắc. Hai lớp hỗ trợ thì cố ý **không khai báo khoá ngoại cứng** tới bất kỳ lớp nào khác, và đây là lựa chọn có chủ đích: nhật ký kiểm toán phải tồn tại được ngay cả khi hội thoại mà nó ghi lại đã bị xoá, còn sổ tài liệu chỉ là bản chiếu của kho tri thức trong repository chứ không phải nguồn dữ liệu chính thức nên nó không được phép ràng buộc bất cứ thứ gì. Hệ quả là bốn lớp của miền này **không liên kết trực tiếp với nhau**; sơ đồ vì thế trình bày chúng như bốn lớp độc lập, và điều đó phản ánh đúng cấu trúc thật chứ không phải một thiếu sót của hình vẽ. Dưới đây là sơ đồ lớp của miền này (Hình PL.6).

#### PHỤ LỤC › E. Cấu trúc một tài liệu tri thức canonical · Đã rút gọn

*Nằm sau: « …»*

Ba trường trong phần frontmatter đảm nhiệm ba vai trò khác nhau. Trường `intent` gắn tài liệu với một nhãn trong bảng phân loại mười lăm ý định. Trường `title` là tên hiển thị của tài liệu, được đưa vào chỉ dẫn của tác tử thứ tư để câu trả lời có thể nhắc tới nguồn tri thức. Trường `questions` là danh sách các cách diễn đạt tự nhiên mà khách hàng thường dùng, phục vụ cho kỹ thuật mở rộng truy vấn đã trình bày ở mục 2.6.3; theo đó, mỗi câu trong danh sách sinh ra một điểm vector riêng, trong đó vector được tính từ câu hỏi nhưng nội dung trả về vẫn là thân đoạn đầy đủ.

Bên cạnh đó, trường `type` không được khai báo trong frontmatter mà được suy ra từ thư mục chứa tệp, nhằm tránh tình trạng tệp nằm ở một thư mục nhưng lại khai báo thuộc nhóm khác.

Ngoài ra, hai tệp nằm ở thư mục gốc bị bỏ qua trong quá trình nạp. Tệp `facts.md` được tác tử thứ tư nạp thẳng vào chỉ dẫn hệ thống chứ không đưa vào cơ sở dữ liệu vector, còn tệp `README.md` là tài liệu hướng dẫn sử dụng chứ không phải tri thức nghiệp vụ.

#### PHỤ LỤC › F. Cấu trúc phiếu chuyển tiếp (EscalationCard) · Đã rút gọn

*Nằm sau: «F. Cấu trúc phiếu chuyển tiếp (EscalationCard) …»*

Phiếu chuyển tiếp được lưu dưới dạng JSONB trong bảng `conversation` và có cấu trúc gồm tám trường. Dưới đây là bảng mô tả chi tiết các trường của phiếu chuyển tiếp (Bảng PL.7); bảng gộp hai trường `priority` và `severity` vào cùng một dòng cho gọn, vì chúng luôn được đọc và dùng cùng nhau khi sắp xếp hàng đợi.

#### PHỤ LỤC › F. Cấu trúc phiếu chuyển tiếp (EscalationCard) · Đã rút gọn

*Nằm sau: «Bảng PL.7. Các trường của phiếu chuyển tiếp …»*

| **Trường** | **Ý nghĩa** |
|---|---|
| `summary` | Nguyên văn tin nhắn đã kích hoạt việc chuyển tiếp, giúp quản trị viên nắm ngay bối cảnh mà không phải đọc lại cả hội thoại |
| `intent` | Nhãn ý định do tác tử 1 gán |
| `entities` | Các thực thể đã trích được, ví dụ mã đơn hàng hoặc kích cỡ |
| `rag_context` | Tối đa ba nguồn tri thức hàng đầu mà tác tử 2 đã truy hồi, mỗi nguồn kèm điểm cosine và một trích đoạn ngắn — cho phép quản trị viên biết hệ thống đã "nhìn thấy" những gì trước khi bỏ cuộc |
| `escalation_reason` | Lý do chuyển tiếp, ghi rõ cờ nào đã kích hoạt |
| `priority` / `severity` | Mức ưu tiên và mức nghiêm trọng, dùng để sắp xếp hàng đợi |
| `suggested_reply` | Nháp phản hồi. Rỗng với ca chuyển người; chứa nháp của tác tử 4 với ca chờ duyệt |

#### PHỤ LỤC › F. Cấu trúc phiếu chuyển tiếp (EscalationCard) · Đã lược bỏ

*Nằm sau: «Bảng PL.7. Các trường của phiếu chuyển tiếp …»*

Việc đưa cả danh sách nguồn tri thức kèm theo điểm số vào phiếu chuyển tiếp là một quyết định thiết kế đáng chú ý, bởi cách làm này biến mỗi ca chuyển tiếp thành một mẫu dữ liệu phục vụ việc đánh giá chất lượng kho tri thức. Cụ thể, khi nhiều ca liên tiếp cùng có điểm truy hồi thấp ở một chủ đề, đó chính là tín hiệu cho thấy kho tri thức đang thiếu nội dung ở chủ đề tương ứng.

#### PHỤ LỤC › G. Cấu trúc payload của một điểm vector trên Qdrant · Đã rút gọn

*Nằm sau: «Bảng PL.8. Các trường payload của một điểm vector …»*

| **Trường** | **Ý nghĩa** |
|---|---|
| `source` | Khoá ổn định của tài liệu, ví dụ `faq/gia-san-pham.md`. Dùng để xoá hoặc thay thế toàn bộ điểm của một tài liệu |
| `text` | Nội dung thân đoạn, là phần thực sự được đưa vào prompt của tác tử 4 |
| `chunk_index` | Chỉ số của đoạn trong tài liệu. Cùng với `source`, trường này tạo thành định danh **tất định** của điểm vector, nhờ đó việc nạp lại cùng một tài liệu mang tính luỹ đẳng: chạy lại thao tác nạp không sinh thêm điểm trùng mà chỉ ghi đè đúng các điểm cũ |
| `title` | Tên hiển thị của tài liệu |
| `intent` | Nhãn ý định khai trong frontmatter; rỗng với tài liệu tải lên |
| `type` | Loại tài liệu, suy từ thư mục: faq, reference, case, promotion, hoặc upload |
| `question` | Rỗng với điểm thân; chứa câu hỏi tương ứng với điểm mở rộng truy vấn |
| `upload_version` | Chỉ có ở tài liệu tải lên. Tải lên lại cùng tên sẽ **thay** bản cũ chứ không gộp, nhờ việc xoá các điểm có phiên bản khác |

#### PHỤ LỤC › G. Cấu trúc payload của một điểm vector trên Qdrant · Đã lược bỏ

*Nằm sau: «Bảng PL.8. Các trường payload của một điểm vector …»*

Điểm cần chú ý ở bảng trên là cặp trường `text` và `question`. Đối với các điểm phục vụ mở rộng truy vấn, vector được tính từ câu hỏi nhưng nội dung trả về vẫn là thân đoạn đầy đủ. Nhờ vậy, một câu hỏi của khách hàng viết theo giọng nói thường ngày vẫn khớp được với tài liệu viết theo giọng văn bản, đồng thời nội dung đưa cho tác tử thứ tư không bị rút gọn thành một câu hỏi rời rạc.

#### PHỤ LỤC › H. Danh sách biến môi trường · Đã rút gọn

*Nằm sau: «Bảng PL.9. Biến môi trường của hệ thống …»*

| **Nhóm** | **Biến** | **Ghi chú** |
|---|---|---|
| Ứng dụng | `ENV` (`development` hoặc `production`), `LOG_LEVEL`, `BACKEND_CORS_ORIGINS` | `ENV` quyết định **cả** quy tắc CORS **và** thuộc tính của cookie xác thực, nên nó là biến duy nhất phải đổi khi chuyển từ máy phát triển sang môi trường triển khai |
| Mô hình ngôn ngữ | `LLM_API_KEY`, `LLM_MODEL`, `ENABLE_LLM`, `LLM_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES` | `ENABLE_LLM=false` cho phép chạy hệ thống ở chế độ không gọi mô hình, dùng khi kiểm thử |
| Cơ sở dữ liệu | `DATABASE_URL`, `DATABASE_SSL` | |
| Vector database | `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION` | `QDRANT_COLLECTION` là tên **alias**, không phải tên collection vật lý |
| Xác thực | `JWT_SECRET`, `JWT_ACCESS_EXPIRE_MINUTES` (30), `JWT_REFRESH_EXPIRE_DAYS` (7), `JWT_EXPIRE_MINUTES` (10080) | `JWT_EXPIRE_MINUTES` được giữ lại để tương thích với bản trước khi tách hai loại mã thông báo |
| Cookie xác thực | `COOKIE_SECURE` (false), `COOKIE_SAMESITE` (`lax`), `COOKIE_DOMAIN` | Ở môi trường `production`, thuộc tính cùng-site tự chuyển thành `none` để hỗ trợ triển khai khác tên miền, và thuộc tính bảo mật bị **bắt buộc** bật; nhờ hai giá trị suy dẫn này, cùng một mã nguồn chạy đúng trên cả máy phát triển dùng HTTP cùng `localhost` và môi trường thật dùng HTTPS khác tên miền — đúng yêu cầu NFR-10 |
| Mô hình nhúng | `EMBEDDING_MODEL` (`text-embedding-3-small`) | |
| Giới hạn tần suất | `RATE_LIMIT_WINDOW_SECONDS` (60), `LOGIN_RATE_PER_IP` (10), `LOGIN_RATE_PER_EMAIL` (5), `REGISTER_RATE_PER_IP` (5), `CHAT_RATE_PER_CUSTOMER` (20) | Đặt một biến về 0 là tắt bộ đếm tương ứng |
| Quan sát | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` | Không đặt thì lớp quan sát tự vô hiệu |
| Tinh chỉnh | `RETRIEVAL_THRESHOLD` (0.40), `HISTORY_WINDOW` (8), `NFR_LATENCY_MS` (5000), `MAX_MESSAGE_CHARS` (2000), `SWEEP_INTERVAL_SECONDS` (60), `SWEEP_BATCH_LIMIT` (500), `SUPPORT_HOURS_START` / `SUPPORT_HOURS_END` (9/21), `SUPPORT_TIMEZONE` (`Asia/Ho_Chi_Minh`), `REPORTS_TZ_OFFSET_HOURS` (7) | |

#### PHỤ LỤC › H. Danh sách biến môi trường · Đã lược bỏ

*Nằm sau: «Bảng PL.9. Biến môi trường của hệ thống …»*

Cần lưu ý rằng hai ngưỡng thời gian của cơ chế tự đóng ca không nằm trong danh sách nêu trên. Hai ngưỡng này được lưu tại bảng `gate_config` để quản trị viên có thể điều chỉnh ngay trong lúc hệ thống đang chạy, bởi chúng là tham số vận hành chứ không phải tham số triển khai.

#### PHỤ LỤC › I. Các mục có thể bổ sung thêm nếu cần độ dày · Đã lược bỏ

*Nằm sau: «Bảng PL.9. Biến môi trường của hệ thống …»*

#### I. Các mục có thể bổ sung thêm nếu cần độ dày

Trong trường hợp cần mở rộng dung lượng phần phụ lục, ba mục sau đây đều đã có sẵn nội dung trong mã nguồn và chỉ cần trích dẫn lại:

- **Bảng phân loại mười lăm ý định đầy đủ:** Bảng này bao gồm nhóm và các thực thể bắt buộc của từng ý định. Nội dung hiện đã được trình bày tại Bảng 2.6 nên việc đưa xuống phụ lục sẽ gây trùng lặp và chỉ nên thực hiện khi có yêu cầu từ khoa.

- **Nội dung tệp `knowledge/facts.md`:** Đây là tập hợp các sự thật cốt lõi về cửa hàng mà tác tử thứ tư nạp thẳng vào chỉ dẫn hệ thống. Việc trích dẫn nội dung này giúp hội đồng nhận thấy rõ ranh giới giữa phần tri thức được nạp trực tiếp và phần tri thức đi qua cơ chế truy hồi.

- **Tệp `docker-compose.local.yml`:** Đây là cấu hình hạ tầng chạy nội bộ gồm PostgreSQL và Qdrant, được sử dụng trong trường hợp không có kết nối tới các dịch vụ được quản lý.

## Phần 2. Ghi chú bàn giao cũ ở đầu các tệp

### `chuong-1.md`

> **Tệp bàn giao cho Claude Word.** Nội dung dưới đây là bản đã đối chiếu với mã nguồn
> tại nhánh `main`, commit `b01b145` ("chore(infra): gỡ Redis khỏi dự án"), ngày 15/09/2026.
> Mọi số liệu, tên biến môi trường, tên bảng và tên hàm trong văn bản đều đã kiểm chứng
> trực tiếp từ repository. Phần "ĐÃ SỬA" liệt kê những chỗ khác với bản .docx hiện tại
> của người dùng — đây là những chỗ cần ghi đè khi biên tập.

#### ĐÃ SỬA so với bản .docx hiện tại

| # | Vị trí | Trước | Sau |
|---|---|---|---|
| 1 | Bảng 1.5 (mục 1.5.3) | Có dòng "Cache / hàng đợi (dự phòng) — Redis (Upstash) — Đã kết nối và đưa vào health-check…" | **Xoá cả dòng.** Redis đã được gỡ hoàn toàn khỏi dự án ở commit `b01b145`: không còn `redis_client.py`, không còn `settings.redis_url`, không còn probe trong `/api/health`, không còn dependency trong `pyproject.toml`, không còn service trong `docker-compose.local.yml`. Bảng 1.5 nay còn ba dòng |
| 2 | Câu ngay dưới Bảng 1.5 | "Cả **bốn** dịch vụ đều dùng gói miễn phí…" | "Cả **ba** dịch vụ…" |
| 10 | Mục 1.5.2, gạch đầu dòng "Khả năng cấu hình và giới hạn thời gian chờ" | "**Mục 3.3.9** sẽ trình bày một sự cố thực tế liên quan tới việc bộ thư viện khách mặc định chờ tới 600 giây…" | "**Mục 3.5.5** sẽ trình bày…". Tham chiếu cũ trỏ sai mục: 3.3.9 nói về suy giảm an toàn, còn sự cố 600 giây được trình bày ở mục đánh giá độ trễ và đối chiếu NFR-1 (3.5.5). Riêng câu về đuôi phân bố độ trễ ở mục 1.5.3 vẫn trỏ **mục 3.5.6** (Benchmark đồng thời và phân tích điểm nghẽn) — đúng với thứ tự tiểu mục mới, **giữ nguyên** |
| 11 | Mục 1.5.1, phần "Các thư viện bổ sung", dòng bcrypt | "**bcrypt 4.1:**" | "**bcrypt (từ phiên bản 4.1):**". `pyproject.toml` khai ràng buộc từ phiên bản 4.1 tới trước 6, nên bản cài thực tế có thể là 5.x; không ghi cứng một số phiên bản không kiểm chứng được |
| 12 | Mục 1.3.3, gạch đầu dòng "Điều phối tĩnh (pipeline cố định)" | "Thứ tự xử lý **và các nhánh rẽ** được định nghĩa trước dưới dạng đồ thị; các tác tử chỉ quyết định nội dung xử lý…" | "Thứ tự xử lý được định nghĩa trước dưới dạng đồ thị, còn các điểm rẽ nhánh cũng được định trước **trong mã tất định** chứ không do tác tử lựa chọn tại thời điểm chạy; các tác tử chỉ quyết định nội dung xử lý…". Trong hệ thống của đề tài, đồ thị chỉ định nghĩa thứ tự; nhánh rẽ do mã tất định quyết định dựa trên tập cờ |

#### ĐÃ BỔ SUNG (so sánh với báo cáo mẫu CT060102)

| # | Vị trí | Nội dung thêm |
|---|---|---|
| 3 | Đầu mục 1.5 | Đoạn dẫn nêu ba ràng buộc NFR-1 / NFR-9 / NFR-10 làm cơ sở chọn công nghệ — mẫu có đoạn dẫn tương tự, bản cũ vào thẳng tiểu mục |
| 4 | Mục 1.5.1, 1.5.2, 1.5.4 | Bổ sung số phiên bản chính xác lấy từ `pyproject.toml` và `package.json`: FastAPI 0.115, LangGraph 0.2, SQLAlchemy 2.0, Alembic 1.13, Pydantic 2.9, pydantic-settings 2.5. Thêm chi tiết vector 1536 chiều của `text-embedding-3-small` |
| 5 | **Mục 1.5.3** | **Ba đoạn mô tả mới cho PostgreSQL, Qdrant và Langfuse.** Đây là chỗ mỏng nhất so với mẫu: bản cũ chỉ có một cái bảng, không giải thích vì sao chọn Qdrant — trong khi vector database là công nghệ quyết định của cả đề tài |
| 6 | **Mục 1.5.6 (mới)** | **Môi trường phát triển và công cụ hỗ trợ.** Mẫu dành hẳn một phần cho IDE và công cụ; bản cũ không nhắc. Mục mới nêu cả hai công cụ tự xây là `make check-conn` và trang `/rag` |
| 7 | Mục 1.3 và 1.5 | Chèn **8 trích dẫn** `[n]` trực tiếp trong thân bài (`[4]` `[8]` `[9]` ở mục 1.5.1, `[5]` `[6]` ở mục 1.5.2, `[7]` `[14]` ở mục 1.5.3, `[10]` ở mục 1.5.4), và 4 chú thích biên tập đánh dấu chỗ cần gắn [1] [2] [3] [4] trong mục lý thuyết |
| 8 | **Toàn bộ mục 1.5 — viết lại theo khuôn báo cáo mẫu** | Mỗi nhóm công nghệ nay trình bày theo đúng cấu trúc của mẫu: **Ngôn ngữ và framework** (kèm phiên bản và tham chiếu hình logo) → **Mô tả** (từng thành phần) → **Lợi ích và lý do lựa chọn** (gạch đầu dòng có tiêu đề in đậm) → **Các công cụ bổ sung**. Mục 1.5 sau khi viết lại dày lên đáng kể, tương đương độ dày mục 1.4 của báo cáo mẫu (không ghi số từ cụ thể vì không đối chiếu được với bản .docx cũ) |
| 9 | Rải khắp mục 1.5 | Chèn **12 chỗ đặt hình logo công nghệ** (Hình 1.10 – 1.21) theo đúng cách mẫu làm: câu dẫn trong thân bài ghi "(Hình 1.x)", rồi dòng chú thích hình nằm riêng một dòng |
| 13 | **Mục 1.1.2 — bốn ảnh chụp khảo sát (Hình 1.1 – 1.4)** | Mỗi nhóm giải pháp a) b) c) d) nay có **một ảnh chụp hệ thống thật** đặt ở cuối phần mô tả, kèm câu dẫn trong thân bài và dòng chú thích riêng. Đây là chỗ khớp với cách báo cáo mẫu CT060102 mở đầu phần khảo sát: mẫu dùng bốn ảnh chụp hệ thống thật (các nền tảng quốc tế, giao diện báo cáo Codility, bảng giá TEST DOME, giao diện Submissions của DMOJ). Mục 1.1.2 của bản cũ **không có hình nào**, chỉ có Bảng 1.1 so sánh — phần khảo sát vì vậy thuần văn xuôi, thiếu bằng chứng trực quan về các hạn chế đang được phân tích |
| 14 | Bảng 1.1, 1.2, 1.3, 1.4 và 1.5 | Thêm một **câu dẫn** trong thân bài cho từng bảng, dạng "Dưới đây là bảng … (Bảng 1.x)." đặt ngay trước dòng chú thích bảng. Bản cũ chỉ có dòng chú thích mà không có câu dẫn, khác với khuôn trình bày dùng ở Chương 2 và Chương 3 |

**Lưu ý đánh số:** bốn ảnh khảo sát mới ở mục 1.1.2 chiếm các số Hình 1.1 – 1.4, làm **toàn bộ
hình của chương dịch thêm bốn số**. Bảng ánh xạ để người biên tập đối chiếu:

| Số cũ | Số mới | Nội dung |
|---|---|---|
| Hình 1.1 | **Hình 1.5** | Bản đồ định vị các nhóm giải pháp |
| Hình 1.2 | **Hình 1.6** | Hai pha của RAG |
| Hình 1.3 | **Hình 1.7** | So sánh hai trường phái điều phối |
| Hình 1.4 | **Hình 1.8** | Ba dạng ảo giác |
| Hình 1.5 | **Hình 1.9** | Thang phản hồi phân cấp ba mức |
| Hình 1.6 | **Hình 1.10** | Logo Python và FastAPI |
| Hình 1.7 | **Hình 1.11** | Logo LangGraph |
| Hình 1.8 | **Hình 1.12** | Logo SQLAlchemy và Alembic |
| Hình 1.9 | **Hình 1.13** | Logo Pydantic |
| Hình 1.10 | **Hình 1.14** | Logo OpenAI |
| Hình 1.11 | **Hình 1.15** | Logo PostgreSQL và Neon |
| Hình 1.12 | **Hình 1.16** | Logo Qdrant |
| Hình 1.13 | **Hình 1.17** | Logo Langfuse |
| Hình 1.14 | **Hình 1.18** | Logo Next.js và React |
| Hình 1.15 | **Hình 1.19** | Logo Tailwind CSS |
| Hình 1.16 | **Hình 1.20** | Logo TanStack Query |
| Hình 1.17 | **Hình 1.21** | Logo pnpm |

Bảng của chương **không** bị ảnh hưởng: Bảng 1.1 – 1.5 giữ nguyên số hiệu, và Bảng 1.5 vẫn là
bảng cuối của chương. Mục 1.5.6 là tiểu mục thứ sáu của 1.5, không sinh bảng mới.

#### HÌNH VẼ CỦA CHƯƠNG 1

Chương 1 trong bản .docx hiện tại **chưa có hình nào trong thân bài**. Sau khi bổ sung phần
khảo sát bằng ảnh chụp và mở rộng mục 1.5 theo khuôn của báo cáo mẫu, chương này cần
**21 hình**, chia ba nhóm: bốn ảnh chụp hệ thống hiện có, năm sơ đồ khái niệm và mười hai hình
logo công nghệ. Chú thích căn giữa, đánh số tự động.

**Nhóm 1 — Ảnh chụp khảo sát giải pháp hiện có (4 hình, cần chụp hoặc lấy từ nguồn công khai)**

Đây là nhóm hình mới hoàn toàn, đặt trong mục 1.1.2. Mỗi ảnh chèn vào cuối phần mô tả của nhóm
giải pháp tương ứng, sau hai gạch đầu dòng Ưu điểm và Nhược điểm; câu dẫn tương ứng đã soạn sẵn
trong thân bài.

| Số | Chú thích | Vị trí chèn | Nội dung cần thấy trong ảnh |
|---|---|---|---|
| Hình 1.1 | Giao diện chatbot theo kịch bản trên nền tảng nhắn tin | Mục 1.1.2, cuối phần mô tả nhóm a) | Cửa sổ chat có sẵn các nút bấm dựng trước, khách chỉ bấm chọn; thấy rõ không có chỗ nào để khách diễn đạt câu hỏi tự do |
| Hình 1.2 | Giao diện huấn luyện ý định của một nền tảng NLU truyền thống | Mục 1.1.2, cuối phần mô tả nhóm b) | Trang quản lý một ý định kèm danh sách câu mẫu (training phrases) phải gán nhãn thủ công, để minh hoạ chi phí xây dựng tập huấn luyện; nếu có, chụp cả phần trích xuất thực thể gắn với từng câu mẫu |
| Hình 1.3 | Trợ lý dựa trên mô hình ngôn ngữ lớn kết hợp truy hồi một bước | Mục 1.1.2, cuối phần mô tả nhóm c) | Một câu trả lời trôi chảy về chính sách nhưng không kèm trích dẫn nguồn, và giao diện không có lối chuyển yêu cầu cho nhân viên thật |
| Hình 1.4 | Kiến trúc điều phối động có tác tử Supervisor | Mục 1.1.2, cuối phần mô tả nhóm d) | Sơ đồ kiến trúc do một framework đa tác tử công bố: tác tử Supervisor ở trung tâm, các cạnh quay vòng trở lại nó, thể hiện số lời gọi mô hình không có giới hạn trên xác định |

*Lưu ý về nguồn:* nếu sử dụng ảnh chụp sản phẩm thương mại thì phải ghi rõ nguồn và thời điểm
truy cập ngay trong chú thích hình, theo đúng cách báo cáo mẫu CT060102 làm với hình bảng giá
TEST DOME. Ưu tiên ảnh chụp từ tài liệu hoặc trang giới thiệu công khai của nhà cung cấp.

**Nhóm 2 — Sơ đồ khái niệm (5 hình, cần vẽ)**

| Số | Chú thích | Vị trí chèn | Loại |
|---|---|---|---|
| Hình 1.5 | Bản đồ định vị các nhóm giải pháp tự động hoá CSKH và khoảng trống của đề tài | Mục 1.1.2, sau Bảng 1.1 và đoạn kết luận về khoảng trống | Biểu đồ định vị hai trục |
| Hình 1.6 | Hai pha của kỹ thuật sinh có tăng cường truy hồi | Mục 1.3.2, sau đoạn "Quy trình RAG gồm hai pha" | Sơ đồ luồng khái niệm |
| Hình 1.7 | So sánh điều phối động (có Supervisor) và điều phối tĩnh (pipeline cố định) | Mục 1.3.3, sau hai gạch đầu dòng về hai trường phái | Sơ đồ so sánh hai khối |
| Hình 1.8 | Ba dạng ảo giác trong ngữ cảnh CSKH và cơ chế chống tương ứng | Mục 1.3.4, trước ba tiểu mục a/b/c | Sơ đồ phân loại ba nhánh |
| Hình 1.9 | Thang phản hồi phân cấp ba mức và ranh giới giữa an toàn với cấu hình | Mục 1.3.5, sau ba gạch đầu dòng mô tả ba mức | Sơ đồ phân tầng có hai cổng |

**Nhóm 3 — Logo công nghệ (12 hình, chỉ cần tải về và chèn)**

Vị trí chèn đã đánh dấu sẵn bằng dòng chú thích trong thân bài. Lấy logo chính thức từ trang chủ
hoặc kho thương hiệu của từng dự án; ưu tiên định dạng PNG nền trong suốt, chiều rộng khoảng
7–10 cm, căn giữa.

| Số | Chú thích | Mục | Nguồn logo |
|---|---|---|---|
| Hình 1.10 | Logo Python và FastAPI | 1.5.1 | python.org · fastapi.tiangolo.com |
| Hình 1.11 | Logo LangGraph | 1.5.1 | langchain-ai.github.io/langgraph |
| Hình 1.12 | Logo SQLAlchemy và Alembic | 1.5.1 | sqlalchemy.org |
| Hình 1.13 | Logo Pydantic | 1.5.1 | docs.pydantic.dev |
| Hình 1.14 | Logo OpenAI | 1.5.2 | openai.com/brand |
| Hình 1.15 | Logo PostgreSQL và Neon | 1.5.3 | postgresql.org · neon.tech |
| Hình 1.16 | Logo Qdrant | 1.5.3 | qdrant.tech |
| Hình 1.17 | Logo Langfuse | 1.5.3 | langfuse.com |
| Hình 1.18 | Logo Next.js và React | 1.5.4 | nextjs.org · react.dev |
| Hình 1.19 | Logo Tailwind CSS | 1.5.4 | tailwindcss.com/brand |
| Hình 1.20 | Logo TanStack Query | 1.5.4 | tanstack.com/query |
| Hình 1.21 | Logo pnpm | 1.5.5 | pnpm.io |

**Hệ quả với DANH MỤC HÌNH VẼ:** Chương 1 tăng từ 5 lên **21 dòng**. Chương 2 có **16 hình**,
không thay đổi. Chương 3 có **14 hình** (thêm Hình 3.14 là biểu đồ độ trễ theo tải, thuộc mục
3.5.6 mới). Tổng DANH MỤC HÌNH VẼ: 21 + 16 + 14 = **51 dòng**. Ngoài ra Phụ lục có 6 hình đánh
số theo hệ riêng PL.1 – PL.6 và **không** liệt kê vào DANH MỤC HÌNH VẼ.

#### BẢNG CỦA CHƯƠNG 1

Bảng 1.1 – 1.5, giữ nguyên số hiệu. Bảng 1.5 giảm từ bốn dòng xuống ba dòng. Cả năm bảng nay
đều có một câu dẫn trong thân bài dạng "Dưới đây là bảng … (Bảng 1.x)." rồi một dòng chú thích
riêng ngay trên bảng, theo đúng khuôn trình bày dùng thống nhất ở Chương 2 và Chương 3.

#### GHI CHÚ BIÊN TẬP

- Mục 1.5 (Công nghệ) hiện mỏng hơn báo cáo mẫu. Phần cần bổ sung nhiều nhất là mục 1.5.3:
  hiện chỉ có một cái bảng, không có đoạn mô tả nào cho PostgreSQL, Qdrant và Langfuse.
  Nội dung bổ sung cho mục 1.5.3 đã được viết trực tiếp vào thân bài của chính tệp này (ba đoạn
  mô tả PostgreSQL, Qdrant và Langfuse, nằm dưới tiêu đề "Lưu trữ và hạ tầng"); không cần tra
  tệp ngoài nào.
- Bản .docx hiện tại của Chương 1 chưa có trích dẫn `[n]` nào; thân bài trong tệp này đã đặt sẵn
  vị trí gắn: [1] mục 1.3.1, [2] mục 1.3.2, [3] mục 1.3.4, [4] mục 1.3.3 (và một lần nữa ở mục
  1.5.1, chỗ giới thiệu LangGraph), [5] và [6] mục 1.5.2, [7] mục 1.5.3, [8] và [9] mục 1.5.1,
  [10] mục 1.5.4, [14] mục 1.5.3. Số hiệu khớp với danh mục TÀI LIỆU THAM KHẢO (14 mục) ở tệp
  `tong-ket.md`; ba mục còn lại ([11], [12] ở mục 2.9.3 và [13] ở mục 2.2.2) thuộc Chương 2 và
  chưa được gắn vào thân bài, theo đúng ghi chú ở tệp `tong-ket.md`.

### `chuong-2.md`

> **Tệp bàn giao cho Claude Word.** Nội dung dưới đây là bản đã đối chiếu với mã nguồn
> tại nhánh `main`, commit `b01b145` ("chore(infra): gỡ Redis khỏi dự án"), ngày 15/09/2026.
> Mọi số liệu, tên biến môi trường, tên bảng và tên hàm trong văn bản đều đã kiểm chứng
> trực tiếp từ repository. Phần "ĐÃ SỬA" liệt kê những chỗ khác với bản .docx hiện tại
> của người dùng — đây là những chỗ cần ghi đè khi biên tập.

#### ĐÃ SỬA so với bản .docx hiện tại

| # | Vị trí | Trước | Sau |
|---|---|---|---|
| 1 | Mục 2.2.2, đoạn "Lớp lưu trữ" | "…Redis đã được kết nối sẵn cho nhu cầu pub/sub và bộ đếm…; giai đoạn này hệ thống chưa lưu trạng thái nào trên Redis…" | Viết lại: không còn nhắc Redis; nêu rõ bộ nhớ đa lượt đọc từ PostgreSQL, trung tâm phát và bộ giới hạn tần suất nằm trong bộ nhớ tiến trình |
| 2 | Bảng 2.2 (các tầng mã nguồn), dòng "Tầng lõi" | "Cấu hình, kết nối **CSDL/Redis/Qdrant**, bảo mật…" | "Cấu hình, kết nối **CSDL/Qdrant/OpenAI**, bảo mật…" |
| 8 | Mục 2.5.1, câu cuối đoạn về ngưỡng truy hồi | "Vì vậy, giao diện vẫn hiển thị giá trị này nhưng ở chế độ chỉ đọc." | Ngưỡng truy hồi **KHÔNG xuất hiện** ở bất kỳ đâu trên giao diện cấu hình cổng; nguồn chân lý là biến môi trường `RETRIEVAL_THRESHOLD`. Kiểm chứng: `/admin/gate` chỉ có hai công tắc + bảng luật theo ý định, `schemas/gate.py` không có trường `retrieval_threshold`, và migration `aadfd438121a` đã xoá cột này khỏi bảng `gate_config` |
| 9 | Mục 2.4.5, đoạn "**Bốn nhánh** xử lý được xét theo thứ tự" và mục nguồn căn cứ thứ hai | "Bốn nhánh"; thiếu nhánh câu hỏi làm rõ; nhãn phân loại đoạn tri thức chỉ kể **bốn** | "**Năm nhánh**", sắp theo đúng thứ tự `response_node` thật (câu hỏi làm rõ → thông báo chuyển tiếp → câu mẫu xã giao → không tìm thấy đơn → sinh phản hồi có căn cứ); nhãn phân loại đoạn tri thức sửa thành **năm** nhãn, bổ sung nhãn khuyến mãi (kiểm chứng `_TYPE_LABEL` trong `nodes/response.py`) |
| 10 | Mục 2.8.3, đoạn về lớp nền | "hai lớp nền dùng chung"; `UUIDMixin` "cung cấp khoá chính … cho **mọi** thực thể" | **Ba** lớp nền (`Base`, `UUIDMixin`, `TimestampMixin`); `UUIDMixin` chỉ dùng cho **sáu** lớp thực thể, hai lớp `GateConfig` và `GateIntentRule` không dùng; `TimestampMixin` chỉ `Conversation` dùng. Có trỏ sang Bảng 2.13 |
| 11 | Mục 2.2.1, trụ cột thứ nhất | "Thứ tự các tác tử **cùng các nhánh rẽ** được đồ thị quy định trước" | Thứ tự do đồ thị quy định trước, còn **việc rẽ nhánh do nút phát ngôn duy nhất** thực hiện theo tập cờ và quyết định của tác tử 3 — đồ thị LangGraph thật KHÔNG có cạnh điều kiện (kiểm chứng `agents/graph.py`) |
| 18 | Mục 2.3.1, danh sách use case | "UC-01: Đăng ký / **Đăng nhập** tài khoản"; "UC-08: Đăng nhập **hệ thống**" | "UC-01: **Đăng ký tài khoản**"; "UC-08: **Đăng nhập và duy trì phiên làm việc** (dùng chung cho cả khách hàng và quản trị viên)" — hai tên cũ vừa trùng phần đăng nhập với nhau, vừa lệch với câu trỏ Phụ lục ở cuối mục 2.3.2 và với hai bảng đặc tả Bảng PL.5, Bảng PL.6 của Phụ lục (Bảng PL.6 ghi rõ tác nhân là **cả hai** vai trò) |

#### ĐÃ BỔ SUNG (so sánh với báo cáo mẫu CT060102)

| # | Vị trí | Nội dung thêm |
|---|---|---|
| 3 | Đầu mục 2.3.2 | Đoạn dẫn nêu tiêu chí chọn use case để đặc tả chi tiết và báo trước phần còn lại nằm ở Phụ lục — mẫu có đoạn tương tự, bản cũ vào thẳng bảng |
| 4 | Bảng 2.3 và Bảng 2.4 | Thêm hai dòng **Tên use case** và **Mô tả** ở đầu mỗi bảng, cho khớp khuôn đặc tả của mẫu (mẫu có 8 dòng: Tên, Mô tả, Tác nhân, Tiền điều kiện, Hậu điều kiện, Luồng chính, Luồng thay thế, Luồng ngoại lệ) |
| 5 | Trước mỗi bảng đặc tả | Một câu dẫn giải thích vì sao use case đó được chọn đặc tả |
| 6 | Cuối mục 2.3.2 | Câu trỏ sang Phụ lục, liệt kê **sáu** use case được đặc tả ở đó (bổ sung UC-01 đăng ký tài khoản và UC-08 đăng nhập/duy trì phiên) |
| 7 | **Mục 2.8.3 (mới)** | **Sơ đồ lớp miền dữ liệu** kèm Hình 2.15 mới. Mẫu có hẳn một mục "Sơ đồ lớp"; bản cũ không có. Mục này cũng giải thích thẳng vì sao tầng xử lý không mô hình hoá bằng lớp — tránh việc hội đồng hỏi "sao không có sơ đồ lớp cho phần tác tử" |
| 12 | **Mục 2.9.1 (mở rộng lớn)** | Toàn bộ cơ chế **httpOnly cookie + luồng làm mới phiên** — phần báo cáo cũ thiếu hoàn toàn dù hai commit `122b49b` và `7976b92` đã đưa vào chạy thật. Thêm hai tiêu đề mới: **Lưu trữ mã thông báo trong httpOnly cookie** (ba biến `COOKIE_SECURE`/`COOKIE_SAMESITE`/`COOKIE_DOMAIN` + hai giá trị suy dẫn `effective_cookie_secure`, `effective_cookie_samesite`) và **Luồng làm mới phiên** (bốn điểm cuối, luân chuyển mã thông báo, retry 401 trong suốt ở giao diện), cùng phần bổ sung cho tiêu đề sẵn có **Cơ chế phân quyền** (WebSocket đọc cookie trước, phân biệt mã đóng 4401 với 1011). Đồng thời sửa mô tả sai về payload của mã thông báo làm mới (bản cũ nói "chỉ chứa định danh và loại" — thực tế có cả `iat` và `exp`) |
| 13 | Bảng 2.3 và Bảng 2.4 | Thêm dòng **Luồng sự kiện ngoại lệ** vào cuối mỗi bảng đặc tả, cho đủ khuôn 8 dòng của mẫu CT060102. Nội dung lấy từ hành vi thật: ghi CSDL thất bại, `search_error`, hết thời gian chờ mô hình 20 giây, `rate_limited` (UC-03); hạ quyền giữa phiên → `not_assigned`, CSDL lỗi → mã đóng 1011 (UC-11) |
| 14 | Đầu mục 2.8.2 | Đoạn dẫn về các lớp nền dùng chung + **Bảng 2.13 mới "Cấu trúc dữ liệu chung"** (`Base`, `UUIDMixin`, `TimestampMixin`) kèm đoạn nêu phạm vi áp dụng. Mẫu CT060102 đặt bảng "Chi tiết Base Entity" thành tiểu mục riêng trước các bảng cụ thể |
| 15 | Các bảng CSDL (2.14 – 2.19) | Tách thành **4 cột** theo khuôn mẫu: Tên thuộc tính \| Kiểu dữ liệu \| **Ràng buộc** \| Mô tả — bản cũ nhồi ràng buộc vào cột Kiểu. Bổ sung các dòng còn thiếu: `customer_identifier`, `created_at`, `updated_at` ở bảng conversation; `created_at` ở bảng order. Ghi tên chỉ mục duy nhất từng phần `uq_message_conversation_client_msg_id` vào cột Ràng buộc của `client_msg_id` |
| 16 | Bảng 2.2, 2.10, 2.14 – 2.21 và Hình 2.3, 2.6, 2.8, 2.9, 2.10, 2.12, 2.13, 2.14 | Thêm **câu dẫn** trong thân bài dạng "Dưới đây là bảng … (Bảng 2.x)." hoặc "Dưới đây là sơ đồ … (Hình 2.x)." đặt ngay trước dòng chú thích. Những chỗ này trước đó chỉ có dòng chú thích mà không có câu dẫn, lệch với khuôn trình bày dùng ở phần còn lại của báo cáo. Đồng thời neo bốn hình còn thiếu (2.4, 2.5, 2.7, 2.16) vào thân bài bằng câu dẫn kèm dòng chú thích — xem mục "HÌNH VẼ CỦA CHƯƠNG 2" |
| 17 | Bảng 2.20 | Chuyển từ **hai dòng văn xuôi** liệt kê tên cột thành **bảng thật** năm cột (Bảng \| Tên thuộc tính \| Kiểu dữ liệu \| Ràng buộc \| Mô tả). Trước đó dòng chú thích "Bảng 2.20" đứng ngay trên hai câu văn xuôi chứ không có bảng nào, nên DANH MỤC BẢNG sẽ trỏ vào chỗ không phải bảng. Kiểu dữ liệu và ràng buộc kiểm chứng từ `models/gate_config.py` và `models/gate_intent_rule.py` |

**Lưu ý đánh số hình:** Hình 2.15 mới (sơ đồ lớp) nằm ở mục 2.8.3, đứng **trước** mục 2.9.3.
Vì vậy hình bốn lớp phòng thủ **đổi từ 2.15 thành 2.16**. Chương 2 có **16 hình** (2.1 – 2.16),
và tổng toàn báo cáo là **51 hình** (21 Chương 1 + 16 Chương 2 + 14 Chương 3), chưa tính 6 hình
đánh số theo hệ riêng PL.1 – PL.6 trong Phụ lục (các hình PL.x **không** vào DANH MỤC HÌNH VẼ).
Cập nhật DANH MỤC HÌNH VẼ tương ứng.

**Lưu ý đánh số bảng:** chương này nay có **22 bảng** (2.1 – 2.22) do chèn thêm **Bảng 2.13 mới
"Cấu trúc dữ liệu chung"** ở đầu mục 2.8.2. Toàn bộ các bảng từ số 2.13 cũ trở đi dịch lên một số.
Bảng ánh xạ số cũ sang số mới để người biên tập đối chiếu:

| Số cũ | Số mới | Tên bảng |
|---|---|---|
| — | **2.13** | Cấu trúc dữ liệu chung (lớp nền Base, UUIDMixin và TimestampMixin) — **BẢNG MỚI** |
| 2.13 | 2.14 | Bảng user |
| 2.14 | 2.15 | Bảng conversation |
| 2.15 | 2.16 | Bảng message |
| 2.16 | 2.17 | Bảng order |
| 2.17 | 2.18 | Bảng audit_log |
| 2.18 | 2.19 | Bảng knowledge_document |
| 2.19 | 2.20 | Bảng cấu hình cổng |
| 2.20 | 2.21 | Các giới hạn tần suất |
| 2.21 | 2.22 | Tổng hợp bốn lớp phòng thủ |

Các bảng 2.1 – 2.12 **giữ nguyên** số hiệu. Chín bảng đặc tả bổ sung nằm ở Phụ lục được đánh số
riêng theo hệ PL.1 – PL.9, không chen vào dãy Bảng 2.x và không vào DANH MỤC BẢNG.

#### HÌNH VẼ CỦA CHƯƠNG 2

Thân bài nay có **đủ 16 hình** (2.1 – 2.16), mỗi hình có một câu dẫn trong thân bài ghi "(Hình 2.x)"
và một dòng chú thích riêng đặt ngay dưới câu dẫn. Năm hình dưới đây trước đó chỉ được khai trong
DANH MỤC HÌNH VẼ mà chưa có chỗ neo trong thân bài; nay đã bổ sung câu dẫn và dòng chú thích tại
các vị trí sau, người biên tập chỉ cần chèn ảnh vào đúng chỗ:

| Số | Chú thích | Vị trí đã neo trong thân bài |
|---|---|---|
| Hình 2.4 | Pipeline bốn tác tử cố định trên LangGraph | Mục 2.4, ngay đầu mục, trước tiểu mục 2.4.1 |
| Hình 2.5 | Cây quyết định từ tập cờ tới ba kết cục giao phản hồi | Mục 2.5.1, sau Bảng 2.9 (ba kết cục) |
| Hình 2.7 | Hai đường nạp kho tri thức: canonical và ad-hoc | Mục 2.6, cuối tiểu mục **2.6.1** (kho tri thức canonical) — đây là tiểu mục trình bày cả hai đường nạp |
| Hình 2.15 | Sơ đồ lớp miền dữ liệu (hình MỚI) | Mục 2.8.3 — mục mới bổ sung, đặt sau đoạn mô tả ba nhóm lớp |
| Hình 2.16 | Bốn lớp phòng thủ chống chèn chỉ dẫn và hai hướng tấn công (đổi số từ 2.15) | Mục 2.9.3, trước Bảng 2.22 |

**Cảnh báo khi vẽ Hình 2.4 (pipeline bốn tác tử).** Đối chiếu `apps/backend/app/agents/graph.py`: đồ thị
LangGraph thật là **tuyến tính hoàn toàn** — chỉ dùng `add_edge`, **không** có `add_conditional_edges`, và
**không** có nút `human_handoff` riêng. Các cạnh đúng là `START → intent_classifier → knowledge → decision
→ response → END`. Việc rẽ nhánh (`auto_reply` / `human_handoff` / `clarify`) nằm **bên trong** nút
`response` theo giá trị `action` trong state; phần việc kèm theo của chuyển tiếp (dựng EscalationCard, đưa
vào hàng đợi admin) do `escalation_service` thực hiện **ngoài** đồ thị. Vì vậy Hình 2.4 **không được** vẽ
nút `human_handoff` riêng, cũng không được vẽ cạnh điều kiện xuất phát từ nút `decision`. Lưu ý thêm: nút
phân loại đăng ký với định danh `intent_classifier` (không phải `intent`) vì LangGraph cấm định danh nút
trùng khoá trạng thái, mà state đã có khoá `intent`.

**Cảnh báo khi vẽ Hình 2.6 (máy trạng thái).** Bảng 2.10 liệt kê 13 trạng thái nhưng không phải
trạng thái nào cũng được ghi vào cột `conversation.status`. Đối chiếu code: `CLASSIFYING`,
`RETRIEVING`, `DECIDING` chỉ tồn tại trong state của LangGraph trong một lượt và không bao giờ
được persist; `RESPONDING` không được tham chiếu ở bất kỳ đâu ngoài `enums.py`; `CLOSED` không có
phép chuyển nào ghi vào nó; `NEW` chỉ là giá trị mặc định của cột, vì `open_case_for_customer()`
ghi thẳng `ACTIVE_AI`. Hình phải tách hai vùng: vùng trạng thái bền (ghi trong CSDL) và vùng
trạng thái trong bộ nhớ của một lượt.

#### BẢNG CỦA CHƯƠNG 2

Bảng 2.1 – 2.22. So với bản .docx hiện tại, chương có thêm **Bảng 2.13** ("Cấu trúc dữ liệu chung")
nên Bảng 2.19 (`knowledge_document`), 2.20 (cấu hình cổng), 2.21 (giới hạn tần suất) và
2.22 (bốn lớp phòng thủ) đều đã dịch lên một số — xem bảng ánh xạ ở mục "Lưu ý đánh số bảng".
**Kiểm tra DANH MỤC BẢNG đã cập nhật theo chưa** (tổng 48 dòng: 5 Chương 1 + 22 Chương 2 + 21 Chương 3).

### `chuong-3.md`

> **Tệp bàn giao cho Claude Word.** Nội dung dưới đây là bản đã đối chiếu với mã nguồn
> tại nhánh `main`, commit `b01b145` ("chore(infra): gỡ Redis khỏi dự án"), ngày 15/09/2026.
> Mọi số liệu, tên biến môi trường, tên bảng và tên hàm trong văn bản đều đã kiểm chứng
> trực tiếp từ repository. Phần "ĐÃ SỬA" liệt kê những chỗ khác với bản .docx hiện tại
> của người dùng — đây là những chỗ cần ghi đè khi biên tập.

#### ĐÃ SỬA so với bản .docx hiện tại

| # | Vị trí | Trước | Sau |
|---|---|---|---|
| 1 | Bảng 3.4 (biến môi trường) | Có dòng "Cache — `REDIS_URL`" | **Xoá cả dòng.** `settings.redis_url` không còn tồn tại trong `config.py` |
| 2 | Bảng 3.2 (lệnh vận hành) | "`make check-conn` — Kiểm tra kết nối Postgres / **Redis** / Qdrant / OpenAI" | "Kiểm tra kết nối Neon (Postgres) và Qdrant" — đúng với `scripts/check_connections.py` sau khi gỡ Redis, script này hiện chỉ còn hai probe |
| 3 | Bảng 3.1 (cấu hình môi trường phát triển) | "Docker Compose cho hạ tầng chạy nội bộ" | Thêm "(PostgreSQL và Qdrant)" — `docker-compose.local.yml` nay chỉ còn hai service |
| 4 | Mục 3.3.7, đoạn ràng buộc một tiến trình | "…đòi hỏi **chuyển các cấu trúc này sang Redis**" | "…đòi hỏi đưa các cấu trúc này ra một kho chia sẻ ngoài tiến trình" |
| 5 | Mục 3.5.8 Hạn chế, gạch đầu dòng "Một tiến trình duy nhất" | "Mở rộng ngang đòi hỏi chuyển sang Redis." | Viết lại đầy đủ: "…bổ sung một kho chia sẻ ngoài tiến trình (Redis hoặc tương đương) cho trung tâm phát, khoá theo khách và bộ giới hạn tần suất." |
| 6 | Mục 3.5.1 Kiểm thử tự động | "387 hàm kiểm thử trên 34 tệp (số case thực tế khi chạy cao hơn…)" | "387 hàm kiểm thử trên 34 tệp, thu về **437 test case** khi chạy" — con số 437 lấy từ lần chạy xác minh ghi trong commit `b01b145` |
| 7 | Mục 3.5.1 Kiểm thử tự động, câu về test frontend | "có thêm **bốn** tệp kiểm thử… và xử lý ô nhập tin." | "có thêm **năm** tệp, tổng cộng **47 test case**… và chèn vạch ngăn theo ngày trong khung hội thoại." — commit `2b6bf64` bổ sung `lib/dayDivider.ts` và `lib/dayDivider.test.mts` |
| 8 | Mục 3.4.2, danh sách thành phần giao diện khách | — | **Thêm một gạch đầu dòng mới** về vạch ngăn theo ngày, tính năng mới ở commit `2b6bf64` |
| 9 | Bảng 3.20 (đối chiếu NFR), dòng NFR-2 | Trạng thái "Đạt về mặt kiến trúc" | "Có công cụ đo — chưa điền số"; ghi chú trỏ sang kịch bản benchmark ở mục 3.5.6. Không có số đo thì không được tuyên bố "đạt" |
| 10 | Bảng 3.2 (lệnh vận hành) | Thiếu `make health`, `make local-infra-up`, `make local-infra-down`; mô tả `make test` ghi "chỉ backend" | Thêm ba lệnh còn thiếu + lệnh `make bench`; `make test` mô tả đúng là chạy **cả** pytest backend **và** `node --test` của dashboard — đối chiếu trực tiếp `Makefile` |
| 11 | Bảng 3.3 (script hỗ trợ) | Liệt kê 6 script | Thêm `gen_favicon.py` và `bench_concurrent.py` — thư mục `scripts/` |
| 12 | Bảng 3.6 (module dashboard), dòng "Cấu hình cổng" | "…; ngưỡng truy hồi hiển thị chỉ đọc" | **Xoá mệnh đề này.** Trang `/admin/gate` không hiển thị ngưỡng truy hồi (chỉ còn một comment cũ trong mã nguồn) |
| 13 | Mục 3.5.4, ngay sau Bảng 3.15 | — | **Thêm đoạn "Một lưu ý về chính hai dòng số liệu trên."** Hai câu trả lời có hứa chuyển tiếp, vi phạm quy tắc "Không tự hứa chuyển người" ở Bảng 2.8; phép đo thực hiện trước khi quy tắc được bổ sung, cần đo lại |
| 14 | Tham chiếu chéo tới các tiểu mục 3.5.x | "bộ 20 câu… mục 3.5.2"; "bám nguồn… mục 3.5.3"; "quá lời… mục 3.5.3" | Lần lượt sửa thành mục 3.5.3, mục 3.5.4 và mục 3.5.4 theo thứ tự tiểu mục đã chốt |
| 19 | Mục 3.5.7, câu dẫn Bảng 3.20 | "…các chỉ số KPI đã đặt ra ở **Chương 2**" | "…đã đặt ra ở **Chương 1**, lần lượt tại **Bảng 1.3** và **Bảng 1.4**" — hai bảng yêu cầu phi chức năng và KPI thuộc Chương 1, Chương 2 không có bảng nào như vậy |
| 20 | Toàn bộ hình của chương (3.1 – 3.13) | Chín ảnh chụp chỉ có dòng chú thích, không có câu dẫn; bốn hình 3.1, 3.2, 3.3 và 3.13 không có chỗ neo nào trong thân bài | **Bổ sung câu dẫn** dạng "Dưới đây là … (Hình 3.x)." cho tất cả, và **bổ sung câu dẫn kèm dòng chú thích riêng** cho bốn hình còn thiếu, đúng khuôn trình bày mà Chương 1 và Chương 2 đang dùng. Sáu ảnh chụp giao diện quản trị dùng **một** câu dẫn nhóm "(Hình 3.6 đến Hình 3.11)" để tránh sáu câu lặp. Thân bài nay có đủ 14 chú thích hình |

#### ĐÃ BỔ SUNG (so sánh với báo cáo mẫu CT060102)

| # | Vị trí | Nội dung thêm |
|---|---|---|
| 15 | Mục 3.1.1, sau Bảng 3.1 và cây thư mục | **Bốn đoạn mới**: môi trường lập trình tích hợp, công cụ quản trị cơ sở dữ liệu, công cụ thiết kế và mô hình hoá, bảng điều khiển Langfuse. Mẫu dành hẳn bốn tiểu mục cho nhóm này (3.1.1–3.1.4); bản cũ chỉ có một bảng cấu hình |
| 16 | **Mục 3.5.2 (mới)** — đặt ngay sau "Kiểm thử tự động", trước "Đánh giá chất lượng xử lý trên bộ câu hỏi thực tế" | **Môi trường và kịch bản đo.** Mẫu có hai tiểu mục "Môi trường benchmark" và "Kịch bản benchmark" trước khi trình bày kết quả; bản cũ đưa thẳng số liệu mà không nêu điều kiện đo. Mục mới gồm: cấu hình đo, ba bộ dữ liệu đo, nguồn số liệu độ trễ, và giới hạn của phép đo |
| 17 | Mục 3.5.2, gạch đầu dòng mới "Kịch bản benchmark đồng thời" (sau "Ba bộ dữ liệu đo") | Khớp với tiểu mục **"Kịch bản benchmark"** của báo cáo mẫu CT060102: công cụ tạo tải `scripts/bench_concurrent.py`, lý do phải dùng N tài khoản khách riêng biệt (giới hạn tần suất 20 tin/60 s và khoá tuần tự hoá đều tính theo từng khách), hai trục thay đổi (kịch bản 1 tăng tải 1/10/25/50/100; kịch bản 2 đổi cấu hình xử lý ở mức 50), định nghĩa từng thước đo (Avg, p50, p95, p99, Max, tỉ lệ ≤ NFR-1) và nguồn số là dòng `delivery` phía máy chủ |
| 18 | **Mục 3.5.6 (mới)** — đặt ngay sau "Đánh giá độ trễ và đối chiếu NFR-1", trước "Đánh giá đối chiếu yêu cầu" | **Benchmark đồng thời và phân tích điểm nghẽn.** Khớp với hai tiểu mục **"Kết quả benchmark"** và **"Phân tích bottleneck"** của báo cáo mẫu CT060102 — phần mà bản cũ thiếu hoàn toàn. Gồm: đoạn dẫn về NFR-2, khung **Bảng 3.18** (kết quả theo số hội thoại đồng thời), khung **Bảng 3.19** (kết quả theo cấu hình xử lý ở mức 50), phần "Phân rã thời gian và nhận diện điểm nghẽn" với bốn giả thuyết điểm nghẽn kèm dấu hiệu nhận biết và cách xử lý, và **Hình 3.14** |

**Lưu ý đánh số tiểu mục:** mục "Môi trường và kịch bản đo" nằm **sau** "Kiểm thử tự động" chứ
không chèn vào đầu mục 3.5, nên không có tiểu mục nào bị lùi số. Thứ tự tám tiểu mục của mục 3.5
đã chốt như sau: 3.5.1 Kiểm thử tự động · 3.5.2 Môi trường và kịch bản đo · 3.5.3 Đánh giá chất
lượng xử lý trên bộ câu hỏi thực tế · 3.5.4 Đánh giá chất lượng grounding · 3.5.5 Đánh giá độ trễ
và đối chiếu NFR-1 · **3.5.6 Benchmark đồng thời và phân tích điểm nghẽn (MỤC MỚI DUY NHẤT)** ·
3.5.7 Đánh giá đối chiếu yêu cầu · 3.5.8 Hạn chế còn tồn tại và hướng cải thiện.

**Ba tham chiếu chéo cần sửa** (đã sửa trong tệp này):

1. Mục 3.5.2, "bộ 20 câu hỏi thực tế được dùng ở mục 3.5.2" → **mục 3.5.3**.
2. Mục 3.5.2, "bộ kiểm chứng bám nguồn dùng ở mục 3.5.3" → **mục 3.5.4**.
3. Mục 3.5.8, "Hiện tượng quá lời… đã được nêu và phân tích ở mục 3.5.3" → **mục 3.5.4**.

Các tham chiếu tới "mục 3.5.5" (đo độ trễ, ở mục 3.1.1) và tới "mục 3.3.5" (quét ngưỡng) là đúng,
giữ nguyên.

**Về phần "Giới hạn của phép đo":** đoạn này nói thẳng cỡ mẫu chưa đủ cho khoảng tin cậy thống
kê. Nêu ra chủ động sẽ tốt hơn để hội đồng phát hiện — và nó khớp với cách bạn đã trình bày
trung thực ở mục Hạn chế.

#### HÌNH VẼ CỦA CHƯƠNG 3

Chương 3 có tổng cộng **14 hình** (Hình 3.1 – 3.14). Thân bài nay có **đủ 14 hình**: mỗi hình
đều có một câu dẫn ghi "(Hình 3.x)" và một dòng chú thích riêng ngay dưới câu dẫn, theo đúng khuôn
trình bày dùng thống nhất ở Chương 1 và Chương 2. Chín trong số đó là ảnh chụp giao diện (3.4 – 3.12),
người biên tập chỉ cần chụp và chèn vào đúng chỗ. **Năm hình còn phải dựng:**

| Số | Chú thích | Vị trí chèn (câu dẫn và chú thích đã có trong thân bài) | Loại |
|---|---|---|---|
| Hình 3.1 | Mô hình đồng thời của một kết nối WebSocket và tuần tự hoá lượt theo khách | Mục 3.2.3, cuối mục | Sơ đồ đồng thời |
| Hình 3.2 | Phân bố điểm cosine của hai tập truy vấn (n = 32 và n = 25) | Mục 3.3.5, ngay sau Bảng 3.9 | Box plot — dựng từ số liệu có sẵn trong Bảng 3.9 |
| Hình 3.3 | Kết quả quét ngưỡng truy hồi | Mục 3.3.5, ngay sau Bảng 3.10 | Biểu đồ đường — dựng từ số liệu có sẵn trong Bảng 3.10 |
| Hình 3.13 | Phân rã thời gian một lượt và phạm vi con số đối chiếu NFR-1 | Mục 3.5.5, ngay sau Bảng 3.16 | Sơ đồ dải thời gian |
| Hình 3.14 | Độ trễ p95 theo số hội thoại đồng thời, đối chiếu ngưỡng NFR-1 | Mục 3.5.6, cuối mục | Biểu đồ đường — dựng từ số liệu Bảng 3.18 (phải điền Bảng 3.18 trước) |

**Khi chụp Hình 3.4 và 3.5** (giao diện chat khách hàng), chụp ở hội thoại kéo dài qua ít nhất
hai ngày để thấy được vạch ngăn theo ngày vừa bổ sung ở mục 3.4.2.

#### BẢNG CỦA CHƯƠNG 3

Chương 3 có **21 bảng: Bảng 3.1 – 3.21.** Hai bảng mới là **Bảng 3.18** (kết quả benchmark theo
số hội thoại đồng thời) và **Bảng 3.19** (kết quả benchmark theo cấu hình xử lý ở mức 50 hội thoại
đồng thời), cả hai nằm ở mục 3.5.6. Do đó hai bảng cuối chương dịch số: bảng đối chiếu NFR
**3.18 → 3.20**, bảng đối chiếu KPI **3.19 → 3.21**. Bảng 3.1 – 3.17 giữ nguyên số hiệu; Bảng 3.4
giảm một dòng sau khi bỏ `REDIS_URL`.

#### BỐN NHÓM Ô CÒN TRỐNG — BẮT BUỘC ĐIỀN TRƯỚC KHI NỘP

1. **Bảng 3.1**, dòng "Hệ điều hành": còn `[Điền hệ điều hành máy phát triển]`.
2. **Bảng 3.17 "Kết quả đo độ trễ thực tế"**: hiện chỉ có dòng chú thích, **không có bảng nào
   bên dưới**. Cần chạy hệ thống, mở tab Báo cáo và điền. Khung bảng đề xuất, khớp với những
   chỉ số mà `report_service.percentile()` thực sự xuất ra:

   | Chỉ số | Giá trị đo | Ghi chú |
   |---|---|---|
   | Số lượt trong mẫu | | Khoảng thời gian đo |
   | Trung bình | ms | |
   | p50 | ms | |
   | p95 | ms | Đối chiếu NFR-1 (≤ 5000 ms) |
   | p99 | ms | Đuôi nặng do thử lại lời gọi mô hình và khởi động nguội Qdrant |
   | Tỉ lệ lượt ≤ NFR-1 | % | |

3. **Bảng 3.21**, dòng "Thời gian phản hồi": còn `[điền số liệu đo]` và `[đánh giá]`.

4. **Bảng 3.18 và Bảng 3.19 (mục 3.5.6)**: cả hai bảng benchmark hiện **chỉ có khung, mọi ô số
   liệu để trống**. Cách điền: khởi động backend (`make dev-backend`), chạy `make bench` để tạo
   tải đồng thời theo hai kịch bản (script tự tạo N tài khoản khách, nên cần đặt
   `REGISTER_RATE_PER_IP=0` và `LOGIN_RATE_PER_IP=0` trong `.env` trước khi đo rồi bật lại sau
   khi đo — xem phần ghi chú đầu `scripts/bench_concurrent.py`), sau đó mở tab Báo cáo hoặc truy vấn trực tiếp bảng
   `audit_log` (dòng `delivery`) để lấy số liệu phía máy chủ. Sau khi điền xong Bảng 3.18 mới
   dựng được Hình 3.14. Dòng NFR-2 ở Bảng 3.20 cũng được cập nhật theo kết quả này.

### `tong-ket.md`

> **Tệp bàn giao cho Claude Word.** Nội dung dưới đây là bản đã đối chiếu với mã nguồn
> tại nhánh `main`, commit `b01b145` ("chore(infra): gỡ Redis khỏi dự án"), ngày 15/09/2026.
> Mọi số liệu, tên biến môi trường, tên bảng và tên hàm trong văn bản đều đã kiểm chứng
> trực tiếp từ repository. Phần "ĐÃ SỬA" liệt kê những chỗ khác với bản .docx hiện tại
> của người dùng — đây là những chỗ cần ghi đè khi biên tập.

#### ĐÃ SỬA so với bản .docx hiện tại

| # | Vị trí | Trước | Sau |
|---|---|---|---|
| 1 | Mục Hướng phát triển, gạch đầu dòng về mở rộng ngang | "Chuyển các cấu trúc điều phối (…) **sang Redis** để chạy được nhiều tiến trình" | "…**ra một kho chia sẻ ngoài tiến trình** để chạy được nhiều tiến trình" — Redis không còn là thành phần của hệ thống nên không thể "chuyển sang" |
| 2 | Đoạn "Về mặt kỹ thuật" | "…khoảng **5.400** dòng TypeScript…" | "…khoảng **5.500** dòng TypeScript…" — đếm lại sau commit `2b6bf64`: 5.494 dòng |
| 3 | Toàn bộ mục **Hướng phát triển** | Danh sách gạch đầu dòng ngắn, khoảng 600 từ | **Viết lại dày lên khoảng 2.500 từ**: mỗi hướng thành một đoạn hoàn chỉnh theo khuôn ba phần (vấn đề đang chặn → cách can thiệp, nêu rõ thành phần → bất biến thiết kế bắt buộc giữ). Giữ nguyên ba giai đoạn và toàn bộ các hướng cũ; thêm **một** hướng ngắn hạn mới về hoàn tất bộ số liệu đo đồng thời (xuất phát từ mục 3.5.6 mới của Chương 3) |
| 4 | Mục Hạn chế, câu mở đầu | "…đã được nêu chi tiết ở mục **3.5.6**" | "…đã được nêu chi tiết ở mục **3.5.8**" — theo thứ tự tiểu mục đã chốt, "Hạn chế còn tồn tại và hướng cải thiện" là mục 3.5.8 |

#### ĐỐI CHIẾU VỚI BÁO CÁO MẪU CT060102

Về **cấu trúc**, phần Tổng kết của mẫu gồm bốn mục: Kết luận chung, Kết quả đạt được, Những hạn
chế còn tồn tại, Hướng phát triển trong tương lai. Phần Tổng kết của báo cáo này có đủ bốn mục
đó và có thêm mục thứ năm — "Những đóng góp đáng chú ý của đồ án" — mà mẫu không có. Về mặt này,
phần Tổng kết của báo cáo vẫn đầy đủ hơn mẫu, nên không bổ sung mục nào.

Về **độ dày** thì có một chỗ lệch rõ. Mục "Hướng phát triển trong tương lai" của mẫu dài khoảng
2.834 từ — là mục dài nhất trong phần kết luận và chiếm khoảng 9% toàn báo cáo — trong khi mục
tương ứng của bản cũ chỉ khoảng 600 từ, chủ yếu là các gạch đầu dòng ngắn. Đây chính là chỗ đã
được mở rộng ở lần sửa này (xem dòng 3 của bảng "ĐÃ SỬA").

Chỗ còn lại mẫu có mà báo cáo này từng thiếu là **Phụ lục**. Mẫu dành hơn 800 dòng cho phụ lục:
đặc tả use case chi tiết, biểu đồ tuần tự phụ, sơ đồ lớp theo từng miền, và các tệp cấu hình
tiêu biểu. Phụ lục của báo cáo này **đã được soạn** ở tệp riêng `phu-luc.md`, nay gồm chín mục
với 9 bảng (PL.1–PL.9) và 6 hình (PL.1–PL.6) đánh số theo hệ riêng của phụ lục.

#### SỐ LIỆU ĐÃ ĐỐI CHIẾU LẠI Ở COMMIT `b01b145`

| Số liệu trong báo cáo | Đếm thật | Kết luận |
|---|---|---|
| ~7.900 dòng Python (`apps/backend/app/`) | 7.864 | Giữ nguyên |
| ~6.800 dòng kiểm thử (`apps/backend/tests/`) | 6.774 | Giữ nguyên |
| ~5.400 dòng TypeScript | 5.494 | **Sửa thành ~5.500** |
| 11 migration | 11 | Giữ nguyên |
| 387 hàm kiểm thử / 34 tệp | 387 / 34 | Giữ nguyên |
| 15 tài liệu tri thức canonical | 15 (7 faq + 4 reference + 4 case) | Giữ nguyên. `facts.md` và `README.md` bị bỏ qua khi nạp theo `_ROOT_FILES_SKIPPED`; `promotion/` hiện rỗng |

#### VIỆC CÒN LẠI CỦA PHẦN NÀY

**Tài liệu tham khảo có 14 mục nhưng thân bài không có trích dẫn `[n]` nào.** Đây là việc lớn
nhất còn tồn. Vị trí gợi ý gắn trích dẫn cho các mục [1] đến [10] và [14] đã được ghi trong mục
GHI CHÚ BIÊN TẬP ở đầu tệp `chuong-1.md`. Ba mục còn lại chưa có vị trí gắn trong thân bài và
cần bổ sung khi biên tập: [11] và [12] gắn ở mục 2.9.3 (chống chèn chỉ dẫn), [13] gắn ở mục
2.2.2 chỗ nói về ba kênh WebSocket.
Bốn mục là bài báo khoa học — [1] Vaswani, [2] Lewis, [3] Ji, [12] Greshake — cần tự tra lại
tên tác giả, năm và nơi công bố trước khi nộp; các mục tài liệu trực tuyến cần ghi ngày truy cập thật.

### `phu-luc.md`

> **Tệp bàn giao cho Claude Word — PHỤ LỤC.** Đối chiếu mã nguồn tại nhánh `main`, commit `b01b145`.
> Phụ lục trong bản .docx hiện tại đang **trống hoàn toàn**, trong khi báo cáo mẫu CT060102 dành hơn
> 800 dòng cho phần này. Nội dung dưới đây lấp vào chỗ đó, theo đúng khuôn mà mẫu sử dụng: đặc tả
> use case chi tiết, biểu đồ use case phân rã, biểu đồ tuần tự bổ sung, sơ đồ lớp theo từng miền,
> cấu trúc dữ liệu tiêu biểu và tệp cấu hình. Phụ lục nay gồm **chín mục, A đến I**, với
> **9 bảng (Bảng PL.1 – PL.9)** và **6 hình (Hình PL.1 – PL.6)**.
>
> **Đánh số:** hình và bảng của phụ lục đánh theo **hệ riêng PL.x** (Hình PL.1…, Bảng PL.1…) và
> **KHÔNG** được liệt kê vào DANH MỤC HÌNH VẼ (51 dòng: 21 + 16 + 14) hay DANH MỤC BẢNG (48 dòng:
> 5 + 22 + 21) của báo cáo. Lý do chọn hệ riêng: báo cáo mẫu CT060102 đánh số phụ lục tiếp theo
> chương (Hình 3.24 trở đi, Bảng 3.3 trở đi) và vì thế **bị trùng số bảng với chính Chương 3 của
> nó**; hệ PL.x tránh được đúng lỗi đó. Nếu khoa yêu cầu đánh số liên tục thì đổi thành
> **Hình 3.15 trở đi** và **Bảng 3.22 trở đi**, và vẫn không liệt kê vào hai danh mục.

#### ĐÃ SỬA so với bản bàn giao trước

| # | Vị trí | Trước | Sau |
|---|---|---|---|
| 1 | Bảng PL.7 (mục F), dòng nguồn tri thức | `rag_sources` | `rag_context` — tên trường thật trong `escalation_service.build_escalation_card`; Bảng 2.11 của Chương 2 vốn đã ghi đúng nên hai chỗ đang lệch nhau |
| 2 | Mục F, câu dẫn | "có cấu trúc gồm **bảy** trường" | "gồm **tám** trường" — phiếu có tám khoá; bảng gộp `priority` với `severity` vào một dòng cho gọn |
| 3 | Bảng PL.8 (mục G) | Thiếu trường `chunk_index` | Thêm dòng `chunk_index`; payload thật có bảy khoá (`text`, `source`, `chunk_index`, `type`, `intent`, `title`, `question`), tài liệu tải lên thêm `upload_version` |
| 4 | Ghi chú thiết kế Bảng PL.3 | "nguyên tắc điểm phát ngôn duy nhất ở mục **2.2.1**" | "…ở mục **2.2.2** (Kiến trúc tổng thể)" |
| 5 | Ghi chú thiết kế Bảng PL.4 | "Ngưỡng truy hồi hiển thị trên màn hình này ở chế độ **chỉ đọc**" | Viết lại: ngưỡng truy hồi **không** nằm trên màn hình cấu hình cổng và cũng **không** nằm trong bảng `gate_config` (cột đã bị migration `aadfd438121a` xoá, `schemas/gate.py` ghi rõ không có `retrieval_threshold`); nó là giá trị **đo**, đọc từ biến môi trường `RETRIEVAL_THRESHOLD` |
| 6 | Bảng PL.1 – PL.4 | Thiếu dòng **Luồng sự kiện ngoại lệ** | Thêm dòng đó vào cả bốn bảng (ngay sau các dòng luồng thay thế, trước ghi chú thiết kế), cho khớp khuôn 8 dòng của mẫu |
| 7 | Ghi chú thiết kế Bảng PL.1 | "hai lỗi thật, trình bày ở mục **3.3.6**" | "…ở mục **2.7.3**" — mục 3.3.6 nói về ba tình huống tra cứu đơn; hai lỗi của dãy số trơ được trình bày ở mục 2.7.3 (Luồng hỏi lại mã đơn và nối lượt) |
| 8 | Mục A, câu mở đầu | "đã được nhắc tới ở mục 2.3.1 **và mục 2.3.2**" | Chỉ mục 2.3.1 — mục 2.3.2 chỉ đặc tả UC-03 và UC-11, không nhắc tới sáu use case của phụ lục |
| 9 | Bảng PL.7, dòng `rag_context` | "Danh sách nguồn tri thức mà tác tử 2 đã truy hồi" | "**Tối đa ba** nguồn tri thức hàng đầu… kèm điểm cosine và một trích đoạn ngắn" — `_top_sources` giới hạn ba nguồn; Bảng 2.11 của Chương 2 cũng ghi "tối đa 3" |
| 10 | Mục D, đoạn dẫn | "Hình 2.15 gồm **hai** lớp nền" | "…gồm **ba** lớp nền" — Bảng 2.13 và mục 2.8.3 đều ghi ba lớp nền `Base`, `UUIDMixin`, `TimestampMixin` |
| 11 | Bảng PL.9 | `ENABLE_LLM` xuất hiện ở **cả hai** nhóm Ứng dụng và Mô hình ngôn ngữ | Giữ một lần ở nhóm Mô hình ngôn ngữ, nơi có ghi chú về chế độ không gọi mô hình |

#### ĐÃ BỔ SUNG (so sánh với báo cáo mẫu CT060102)

| # | Vị trí | Nội dung thêm |
|---|---|---|
| 12 | Cuối mục A | **Bảng PL.5** (UC-01 — Đăng ký tài khoản) và **Bảng PL.6** (UC-08 — Đăng nhập và duy trì phiên làm việc), kèm đoạn dẫn giải thích vì sao nhóm use case xác thực nằm ở phụ lục. Mẫu dành hẳn phần phụ lục cho nhóm use case xác thực và hồ sơ; bản cũ liệt kê UC-01 và UC-08 ở mục 2.3.1 nhưng **không đặc tả ở đâu cả**, và toàn bộ cơ chế httpOnly cookie (commit `122b49b`, `7976b92`) chưa được nhắc một dòng nào |
| 13 | **Mục B (mới)** | **Biểu đồ use case phân rã** — Hình PL.1 (nhóm khách hàng) và Hình PL.2 (nhóm quản trị viên). Mẫu có năm biểu đồ phân rã ở phụ lục; bản cũ chỉ có một biểu đồ tổng quát ở Hình 2.3 kèm hai mươi dòng gạch đầu dòng |
| 14 | **Mục C (mới)** | **Biểu đồ tuần tự bổ sung** — Hình PL.3 (đăng nhập và làm mới phiên qua httpOnly cookie) và Hình PL.4 (tiếp quản ca và chat trực tiếp với khách hàng). Mẫu có bốn biểu đồ tuần tự phụ ở phụ lục; Chương 2 có năm biểu đồ nhưng thiếu đúng hai luồng này |
| 15 | **Mục D (mới)** | **Sơ đồ lớp theo từng miền dữ liệu** — Hình PL.5 (miền hội thoại) và Hình PL.6 (miền cấu hình và hỗ trợ). Mẫu tách sơ đồ lớp theo miền ở phụ lục; Chương 2 chỉ có một sơ đồ tổng ở Hình 2.15, dễ rậm |
| 16 | Bảng PL.9 (mục H) | Bổ sung bốn nhóm biến còn thiếu: ứng dụng (`ENV`, `LOG_LEVEL`, `BACKEND_CORS_ORIGINS`), cấu hình cookie (`COOKIE_SECURE`, `COOKIE_SAMESITE`, `COOKIE_DOMAIN`), giới hạn tần suất (năm biến) và mô hình nhúng (`EMBEDDING_MODEL`); đồng thời bổ sung `JWT_EXPIRE_MINUTES` vào nhóm xác thực sẵn có, cùng hai biến `SUPPORT_TIMEZONE` và `REPORTS_TZ_OFFSET_HOURS` vào nhóm tinh chỉnh |
| 17 | Ghi chú thiết kế Bảng PL.1 | Thêm câu trỏ sang **mục 3.3.6** cho cơ chế đếm số lần tra cứu thất bại, tức căn cứ của luồng thay thế 5b. Trước đó ghi chú chỉ trỏ mục 2.7.3 (hai lỗi của dãy số trơ), nên phần "vì sao lần thứ hai không hỏi lại nữa" không có chỗ tra; nay cả hai tham chiếu đều đúng và không chồng nội dung nhau |

**Lưu ý đánh số bảng trong phụ lục:** hai bảng đặc tả use case xác thực chiếm số PL.5 và PL.6, nên
ba bảng phía sau **đã dịch lên hai số**: phiếu chuyển tiếp PL.5 → **PL.7**, payload Qdrant
PL.6 → **PL.8**, biến môi trường PL.7 → **PL.9**.
