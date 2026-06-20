## 12. Đánh giá giải pháp (Evaluation)

Việc đánh giá hệ thống Smart Travel System được thực hiện liên tục thông qua một vòng lặp: Đánh giá, Tinh chỉnh, Triển khai và Mô phỏng. Với kiến trúc hệ thống 5 lớp (Frontend, Backend API, Services, Database, Infrastructure), quá trình này dựa trên các nguyên tắc đo lường bằng chỉ số cụ thể, so sánh với các yêu cầu của bài toán du lịch thông minh và sử dụng phản hồi để tối ưu hóa luồng xử lý dữ liệu.

### 1. Mục tiêu đánh giá (Objectives)

Hệ thống được đo lường dựa trên 5 mục tiêu cốt lõi:

* **Tính chính xác (Correctness):** Đảm bảo luồng xử lý nghiệp vụ luôn trả về kết quả đúng. Đặc biệt với *AI Chatbot* và *Visual Search*, hệ thống phải sinh câu trả lời chính xác dựa trên ngữ cảnh và tìm ra đúng địa điểm tương đồng thông qua thuật toán so khớp KNN trên Vector DB.
* **Hiệu suất (Efficiency):** Đánh giá tốc độ và mức độ tiêu thụ tài nguyên của các API. Trọng tâm là thời gian định tuyến của Backend API (FastAPI), tốc độ trích xuất vector đặc trưng từ ảnh (Visual Search), thời gian sinh văn bản của AI và độ trễ khi truy vấn CSDL truyền thống lẫn Vector DB.
* **Độ mạnh mẽ (Robustness):** Khả năng xử lý các trường hợp ngoại lệ (edge cases) ở cả luồng đầu vào và nghiệp vụ. Ví dụ: xử lý token xác thực hết hạn, ảnh upload bị mờ/thiếu sáng, câu hỏi nhập vào chatbot không rõ nghĩa, hoặc dữ liệu thu thập từ scraper bị lỗi cấu trúc.
* **Khả năng mở rộng (Scalability):** Đảm bảo kiến trúc ứng dụng container hóa (Docker/Docker-compose) vẫn chịu tải tốt khi lượng người dùng tăng cao, dung lượng Vector DB phình to hoặc cần bổ sung thêm các dịch vụ AI mới vào lớp Backend Services.
* **Tính khả dụng (Usability / Practicality):** Đảm bảo giải pháp mang lại trải nghiệm tương tác cao thông qua lớp Frontend (React/Vite/Tailwind). Thời gian phản hồi từ lúc Client gửi HTTP REST Request đến khi nhận được JSON trả về phải đủ nhanh để đáp ứng kỳ vọng thực tế của du khách.

### 2. Phương pháp và Công cụ (Methods & Tools)

| Phương pháp | Ứng dụng trong dự án | Công cụ đề xuất |
| :--- | :--- | :--- |
| **Unit Testing** | Kiểm thử độc lập các module lõi ở lớp Backend Services (ví dụ: `ai_service.py`, `visual_search.py`, `full_scraper.py`) và các hàm tính toán khoảng cách vector (KNN) bao gồm cả các trường hợp tiêu biểu và ngoại lệ. | pytest |
| **Benchmarking** | Đo lường thời gian chạy (runtime), tiêu thụ bộ nhớ và băng thông của FastAPI, cũng như độ trễ của cơ sở dữ liệu. So sánh hiệu năng xử lý song song của các container. | Python timeit, cProfile, JMeter / Postman |
| **User Feedback** | Thu thập ý kiến của người dùng về độ mượt mà của giao diện (React UI), mức độ hữu ích của AI Chatbot và độ chính xác của tính năng tìm kiếm địa điểm bằng hình ảnh. | Google Forms |

### 3. Các vấn đề tiềm ẩn cần tránh (Potential Issues)

Trong quá trình đánh giá hệ thống, nhóm nhận diện và cam kết tránh các cạm bẫy sau:

* **Dữ liệu thử nghiệm thiên lệch:** Tránh việc chỉ kiểm thử tính năng Visual Search và AI trên các tập dữ liệu "sạch" (đã chuẩn hóa) mà bỏ qua các trường hợp thực tế xấu nhất (ảnh du lịch bị che khuất, truy vấn sai chính tả hoặc dữ liệu seed/crawl bị nhiễu).
* **Tối ưu hóa phiến diện:** Tránh việc chỉ tập trung làm đẹp giao diện Frontend hoặc giảm thời gian phản hồi API mà bỏ qua sự tiêu thụ bộ nhớ (RAM) của mô hình AI, dẫn đến tình trạng "thắt cổ chai" (bottleneck) tại lớp Backend Services khi triển khai thực tế.
* **Đánh giá chủ quan:** Mọi nhận định về chất lượng kiến trúc hoặc tính dễ bảo trì phải được đo lường cụ thể (ví dụ: thời gian deploy qua Docker, số lượng bug phát sinh), không dựa trên cảm tính. Cần tránh thiên kiến xác nhận khi chỉ báo cáo các truy vấn AI thành công mà phớt lờ các câu trả lời hallucination (ảo giác).
* **Thiếu đánh giá tổng hợp đa chiều:** Kiến trúc nhiều lớp luôn đi kèm với độ phức tạp. Cần đánh giá sự đánh đổi (trade-offs) giữa tốc độ xử lý mạng, độ phức tạp của Vector DB, độ trễ sinh text của AI và chi phí vận hành server.

### 4. Checklist kiểm tra (Evaluation Checklist)

Trước khi đóng gói phiên bản cuối, kiến trúc hệ thống cần vượt qua các câu hỏi kiểm tra sau:

* Các API endpoint (FastAPI) và thuật toán AI / Visual Search có xử lý chính xác 100% các dữ liệu đầu vào hợp lệ và trả về đúng JSON contract không?
* Hệ thống đã được kiểm thử với dữ liệu thực tế (ảnh chụp đa dạng góc độ, câu hỏi thực tế của du khách) chưa?
* Các chỉ số về độ trễ mạng (từ Frontend đến Backend), mức hao tốn tài nguyên của Docker containers và thời gian truy vấn DB đã được đo lường đầy đủ chưa?
* Cấu trúc 5 lớp hiện tại và sự đánh đổi tài nguyên của các dịch vụ AI có phù hợp, khả thi để giải quyết bài toán du lịch thông minh trong thực tế không?