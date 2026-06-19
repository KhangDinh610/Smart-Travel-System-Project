## Đánh giá giải pháp (Evaluation)

Việc đánh giá hệ thống Smart Shopping được thực hiện liên tục thông qua một vòng lặp: Đánh giá, Tinh chỉnh, Triển khai và Mô phỏng. Quá trình này dựa trên các nguyên tắc đo lường bằng chỉ số cụ thể, so sánh với các yêu cầu của bài toán và sử dụng phản hồi để cải thiện thuật toán.

### 1. Mục tiêu đánh giá (Objectives)

Hệ thống được đo lường dựa trên 5 mục tiêu cốt lõi:

* **Tính chính xác (Correctness):** Đảm bảo thuật toán luôn trả về kết quả đúng. Đối với module *Duplicate Detection*, tính chính xác phải đặt lên hàng đầu để cảnh báo đúng sản phẩm khách đã mua, tránh việc hy sinh tính chính xác để đổi lấy tốc độ.
* **Hiệu suất (Efficiency):** Đánh giá tốc độ chạy của thuật toán và mức độ sử dụng tài nguyên. Đặc biệt tập trung vào thời gian trích xuất vector embedding (Visual Retrieval) và tốc độ truy vấn trên VectorDB.
* **Độ mạnh mẽ (Robustness):** Khả năng xử lý các trường hợp ngoại lệ (edge cases) hoặc dữ liệu đầu vào không hợp lệ, chẳng hạn như ảnh upload bị mờ, thiếu sáng, hoặc thao tác nhập log mua sắm bị sai định dạng.
* **Khả năng mở rộng (Scalability):** Đảm bảo hệ thống vẫn hoạt động tốt khi lượng dữ liệu lớn hoặc kiến trúc trở nên phức tạp.
* **Tính khả dụng (Usability / Practicality):** Đảm bảo giải pháp dễ sử dụng và có thể triển khai tốt trong môi trường thực tế. Một thuật toán nhanh nhất cũng vô dụng nếu trải nghiệm người dùng (UX) kém hoặc bỏ qua bối cảnh thực tế của du khách.

### 2. Phương pháp và Công cụ (Methods & Tools)

| Phương pháp | Ứng dụng trong dự án | Công cụ đề xuất |
| :--- | :--- | :--- |
| **Unit Testing** | Kiểm thử từng hàm và module độc lập (ví dụ: hàm tính Cosine Similarity) bao gồm cả các trường hợp tiêu biểu và ngoại lệ. | pytest |
| **Benchmarking** | Đo lường thời gian chạy (runtime), bộ nhớ và băng thông khi AI Assistant xử lý NLP. So sánh hiệu năng giữa các phiên bản thuật toán. | Python timeit, cProfile |
| **User Feedback** | Thu thập ý kiến của du khách và chủ cửa hàng về tính hiệu quả thực tế của các gợi ý mua sắm. | Google Forms |

### 3. Các vấn đề tiềm ẩn cần tránh (Potential Issues)

Trong quá trình đánh giá hệ thống, nhóm nhận diện và cam kết tránh các cạm bẫy sau:

* **Dữ liệu thử nghiệm thiên lệch:** Tránh việc chỉ kiểm thử trên các tập dữ liệu ngẫu nhiên mà bỏ qua các trường hợp xấu nhất (worst-case) hoặc các đặc tính thực tế của dữ liệu như tính phân cụm.
* **Tối ưu hóa phiến diện:** Tránh việc chỉ tập trung đo lường thời gian chạy (runtime) mà bỏ qua mức độ tiêu thụ bộ nhớ (RAM), độ trễ mạng hay giới hạn tài nguyên, dẫn đến lỗi khi mở rộng hệ thống. Không tối ưu hóa duy nhất một chỉ số (ví dụ: giảm độ trễ) mà phá hủy các chỉ số quan trọng khác.
* **Đánh giá chủ quan:** Mọi nhận định về chất lượng code hoặc tính dễ bảo trì phải được đo lường bằng các chỉ số cụ thể, không dựa trên cảm tính. Đồng thời, cần tránh thiên kiến xác nhận (Confirmation Bias) khi chỉ thu thập các bằng chứng ủng hộ giải pháp của nhóm mà phớt lờ các kết quả trái ngược.
* **Thiếu đánh giá tổng hợp đa chiều:** Nhóm hiểu rằng hầu như không có giải pháp nào là hoàn hảo ở mọi mặt, do đó cần đánh giá sự đánh đổi (trade-offs) giữa tốc độ, bộ nhớ, độ chính xác, sự đơn giản và chi phí.

### 4. Checklist kiểm tra (Evaluation Checklist)

Trước khi đóng gói phiên bản cuối, hệ thống cần vượt qua các câu hỏi kiểm tra sau:

* Giải pháp có đạt độ chính xác 100% trên toàn bộ các dữ liệu đầu vào hợp lệ không?
* Hệ thống đã được kiểm thử trên dữ liệu thực tế và các đầu vào thuộc trường hợp xấu nhất (worst-case) chưa?
* Các chỉ số về thời gian, bộ nhớ, chi phí tài nguyên và khả năng mở rộng đã được đo lường đầy đủ chưa?
* Sự đánh đổi (trade-offs) của các thuật toán hiện tại có phù hợp với yêu cầu thực tế của bài toán mua sắm du lịch không?