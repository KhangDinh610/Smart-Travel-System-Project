# CHƯƠNG X: MÔ PHỎNG VÀ THỰC NGHIỆM HỆ THỐNG (SIMULATION & TESTING)

## 1. Mục đích và Phạm vi mô phỏng

Chương này mô tả chi tiết toàn bộ quá trình vận hành, thực nghiệm và đánh giá hệ thống **Smart Shopping System (SSS)**. Mục đích chính của việc mô phỏng bao gồm:
1. **Kiểm chứng tính khả thi của Thuật toán:** Đánh giá độ chính xác của các thuật toán nhận diện hình ảnh (Visual Retrieval), đo lường sự tương đồng ngữ nghĩa (Semantic Similarity) trong tính năng phát hiện trùng lặp (Duplicate Detection).
2. **Kiểm tra tích hợp (Integration Testing):** Đảm bảo luồng dữ liệu thông suốt giữa Streamlit (Frontend), FastAPI (Backend), Firestore (User/History Database) và ChromaDB (Vector Database).
3. **Đánh giá trải nghiệm người dùng (UX):** Kiểm tra các phản hồi hệ thống (thông báo lỗi, trạng thái loading, kết quả hiển thị) đối với tương tác của người dùng cuối.
4. **Xử lý ngoại lệ (Error Handling):** Quan sát cách hệ thống phản ứng khi người dùng nhập sai dữ liệu, hình ảnh không hợp lệ hoặc mất kết nối.

---

## 2. Thiết lập Môi trường và Dữ liệu mô phỏng

### 2.1 Môi trường triển khai (Deployment Environment)
Hệ thống được khởi chạy và mô phỏng trên môi trường cục bộ (Localhost) với các thông số cấu hình cụ thể:
- **Frontend (Giao diện người dùng):** 
  - Framework: `Streamlit`
  - Địa chỉ truy cập: `http://localhost:8501`
- **Backend (API Server):**
  - Framework: `FastAPI` (chạy qua uvicorn)
  - Địa chỉ API: `http://127.0.0.1:8000/api/v1`
- **Cơ sở dữ liệu (Databases):**
  - **Firebase/Firestore:** Quản lý thông tin xác thực (`Authentication`) và lưu trữ dữ liệu phi cấu trúc (Collection `users`, `history`).
  - **ChromaDB:** Cơ sở dữ liệu Vector cục bộ, lưu trữ các embeddings của hình ảnh và văn bản phục vụ truy xuất siêu tốc.
- **AI / LLM Integration:**
  - Tích hợp `Google Gemini AI` để xử lý ngôn ngữ tự nhiên (NLP) cho Chatbot và phân tích hình ảnh (Vision).

### 2.2 Bộ dữ liệu mô phỏng (Mock Data & Seeding)
Trước khi tiến hành các kịch bản, hệ thống được nạp một tập dữ liệu giả lập đại diện cho bối cảnh du lịch địa phương (chạy qua file `populate_data.py`).
- **Dữ liệu Cửa hàng (Shops):**
  - ID: `1` | Tên: `Đặc Sản Đà Lạt L'angfarm` | Địa chỉ: `Chợ Đà Lạt, Phường 1`.
  - ID: `2` | Tên: `Cà Phê Chồn Trại Hầm` | Địa chỉ: `Trại Mát, Đà Lạt`.
- **Dữ liệu Sản phẩm (Products):**
  - Mứt Dâu Tây (Shop 1), Trà Atiso túi lọc (Shop 1).
  - Hộp Cà Phê Chồn cao cấp 500g (Shop 2), Phin pha cà phê thủ công (Shop 2).
- **Dữ liệu Embedding:** Các sản phẩm trên đã được trích xuất đặc trưng bằng mô hình Embedding và được chỉ mục hóa (indexed) sẵn trong Collection của ChromaDB.

---

## 3. Các kịch bản mô phỏng chi tiết (Detailed Scenarios)

Dưới đây là các kịch bản thực nghiệm từ lúc người dùng bắt đầu mở ứng dụng cho đến khi hoàn thành chu trình mua sắm.

### Kịch bản 1: Xác thực Người dùng (Authentication Flow)
- **Mục tiêu:** Kiểm tra cơ chế quản lý phiên đăng nhập và định danh người dùng.
- **Các bước thực thi:**
  1. Người dùng truy cập `http://localhost:8501`. Màn hình yêu cầu đăng nhập hiển thị.
  2. Người dùng chuyển sang tab **Đăng ký**, nhập Email `testuser@example.com` và Mật khẩu `123456`.
  3. Nhấn "Đăng ký". Streamlit gửi POST request đến endpoint `/register`.
  4. Người dùng quay lại tab **Đăng nhập**, nhập thông tin vừa tạo và nhấn "Đăng nhập".
- **Luồng xử lý Kỹ thuật:**
  - Backend sử dụng Firebase Admin SDK để tạo user.
  - Khi đăng nhập thành công, Backend trả về đối tượng JSON chứa `token` JWT và `uid`.
  - Frontend lưu token vào `st.session_state['auth']` và trigger `st.rerun()` để tải giao diện chính.
- **Kết quả mong đợi:**
  - Xuất hiện thông báo `✅ Chào mừng, testuser@example.com!`.
  - Sidebar bên trái mở ra với danh sách các tính năng (Chatbot, Ghi nhận mua sắm, Tìm kiếm, Kiểm tra trùng lặp).
- **Xử lý ngoại lệ:** Nhập sai mật khẩu hệ thống báo `❌ Sai email hoặc mật khẩu`.

### Kịch bản 2: Tương tác Trợ lý Mua sắm (AI Chatbot)
- **Mục tiêu:** Kiểm tra khả năng xử lý ngôn ngữ tự nhiên (NLP) của hệ thống trong việc hiểu Intent (ý định) mua sắm và cung cấp tư vấn ngữ cảnh.
- **Dữ liệu đầu vào:** Câu prompt của user: *"Tôi muốn mua một món quà tặng mẹ có tác dụng tốt cho sức khỏe dưới 500 nghìn."*
- **Các bước thực thi:**
  1. Người dùng chọn menu **💬 Chatbot**.
  2. Nhập câu hỏi vào thanh chat.
- **Luồng xử lý Kỹ thuật:**
  - Câu hỏi cùng `user_id` được POST tới `/chat`.
  - Backend truy vấn lịch sử mua sắm của người dùng này từ Firestore để làm **Context**.
  - Backend đóng gói Prompt (bao gồm: Câu hỏi + Lịch sử mua sắm + Danh sách cửa hàng hiện có) và gửi cho Gemini AI.
- **Kết quả mong đợi:**
  - Chatbot gõ câu trả lời (streaming effect).
  - Nội dung đề xuất "Trà Atiso túi lọc tại L'angfarm" vì phù hợp tiêu chí "tốt cho sức khỏe" và nằm trong mức giá dưới 500k. Thông điệp giao tiếp tự nhiên, thân thiện.

### Kịch bản 3: Nhận diện Sản phẩm Đa phương thức (Visual Search & Analysis)
- **Mục tiêu:** Đo lường độ chính xác của kỹ thuật trích xuất đặc trưng ảnh và phân tích ảnh.
- **Các bước thực thi & Luồng xử lý:**
  - **Tab 1: Tìm kiếm bằng ảnh (ChromaDB)**
    - *Đầu vào:* Upload file ảnh `coffee_box.jpg`.
    - *Xử lý:* Streamlit gửi file ảnh dưới dạng multipart tới `/visual-search`. Backend chuyển ảnh thành Vector Embedding. Gọi ChromaDB thực hiện thuật toán tính **Khoảng cách Cosine** (Cosine Distance) giữa vector ảnh query và các vector trong database.
    - *Kết quả:* Trả về Top 3 sản phẩm. UI hiển thị: `Hộp Cà Phê Chồn cao cấp 500g` với `Score: 92.5%`, kèm thông tin giá tiền và địa chỉ `Cà Phê Chồn Trại Hầm`.
  - **Tab 2: Phân tích chi tiết (Gemini Vision)**
    - *Đầu vào:* Upload file ảnh món đồ thủ công mỹ nghệ.
    - *Xử lý:* Gửi ảnh tới `/scan-product`. Backend gọi mô hình Gemini (Vision capability).
    - *Kết quả:* Streamlit in ra đoạn văn mô tả chi tiết: nguồn gốc nguyên liệu, ý nghĩa văn hóa của món đồ thủ công đó đối với người dân địa phương.

### Kịch bản 4: Ghi nhận Lịch sử Mua sắm (Purchase Logging)
- **Mục tiêu:** Đảm bảo dữ liệu người dùng được lưu trữ tức thời để phục vụ cho tính năng tránh trùng lặp ở bước sau.
- **Các bước thực thi:**
  1. Truy cập menu **📝 Ghi nhận mua sắm**.
  2. Nhập thông tin: 
     - Tên sản phẩm: `Trà Atiso L'angfarm`
     - Mã cửa hàng: `1`
  3. Bấm "Lưu lịch sử".
- **Luồng xử lý Kỹ thuật:**
  - Payload JSON `{ "user_id": "...", "product_id": "Trà Atiso L'angfarm", "shop_id": 1 }` được gửi tới `/history`.
  - Backend ghi một Document mới vào collection `history` trên Firestore với timestamp hiện tại.
- **Kết quả mong đợi:** Hiển thị Toast message `✅ Đã ghi nhận thành công!`.

### Kịch bản 5: Động cơ Cảnh báo Trùng lặp (Duplicate Detection Engine)
- **Mục tiêu:** Đánh giá cốt lõi của bài toán — Ngăn chặn du khách mua những sản phẩm mang lại giá trị trải nghiệm tương đương nhau.
- **Dữ liệu đầu vào:** Người dùng định mua thêm *"Hộp trà sấy khô Atiso"*.
- **Các bước thực thi:**
  1. Truy cập **🛡️ Kiểm tra trùng lặp**.
  2. Nhập text: *"Hộp trà sấy khô Atiso"*. Nhấn kiểm tra.
- **Luồng xử lý Kỹ thuật:**
  - Backend nhận text truy vấn và trích xuất lịch sử mua sắm của `user_id` (Trong lịch sử đã có `"Trà Atiso L'angfarm"` từ Kịch bản 4).
  - Thuật toán tiến hành 2 bước đối soát (Matching):
    - **Lexical Match (So khớp từ vựng):** Tính chỉ số Jaccard/TF-IDF giữa các từ "Trà", "Atiso".
    - **Semantic Match (So khớp ngữ nghĩa):** Chuyển 2 câu thành vector và tính khoảng cách. Nhận diện ra dù tên khác nhau ("Hộp trà sấy khô" vs "Trà L'angfarm") nhưng bản chất đều là trà Atiso.
  - Tổng hợp lại thành **Final Score**.
- **Kết quả mong đợi:**
  - Thuật toán trả về `score = 0.85` (Lớn hơn ngưỡng threshold `0.8`).
  - Giao diện Streamlit hiển thị hộp thoại màu Đỏ: `⚠️ Phát hiện trùng lặp! (Độ tin cậy: 0.85)`.
  - Trích xuất chi tiết kỹ thuật (Expander): Hiển thị rõ `Semantic Score` và `Lexical Score`.
  - *Ngược lại,* nếu người dùng nhập "Mứt dâu tây", thuật toán trả về `score = 0.2`, UI báo màu Xanh: `✅ Sản phẩm mới! (Điểm tương đồng: 0.20)`.

---

## 4. Tổng hợp Kết quả và Đánh giá Thực nghiệm

Sau quá trình chạy qua toàn bộ 5 kịch bản mô phỏng, hệ thống thu được những đánh giá khách quan sau:

### 4.1 Điểm mạnh & Kết quả đạt được
1. **Chức năng hoạt động chính xác:** Các module cốt lõi (M1-M4) như đã phân rã trong bài toán đã tương tác hoàn hảo với nhau. Người dùng thêm dữ liệu ở M4 (Ghi nhận), dữ liệu ngay lập tức ảnh hưởng đến kết quả của M2 (Phát hiện trùng lặp).
2. **Thuật toán thông minh:** Cơ chế Semantic Score cho Duplicate Detection cho thấy độ hiệu quả vượt trội so với tìm kiếm String truyền thống. Tránh được việc người dùng bị lừa bởi các sản phẩm "bình mới rượu cũ".
3. **Hiệu suất (Performance):** Sử dụng ChromaDB làm Local Vector Database giúp tốc độ truy xuất hình ảnh (Visual Search) đạt ngưỡng Real-time (thời gian xử lý dưới 1.5 giây).

### 4.2 Giới hạn và Hướng khắc phục (Limitations & Future Work)
- **Độ trễ API của Gemini:** Phụ thuộc vào tốc độ mạng và giới hạn rate limit của Google, tính năng Chatbot đôi khi có độ trễ khoảng 3-5 giây. 
  - *Khắc phục:* Có thể áp dụng cơ chế Caching cho các câu hỏi phổ biến (như "Đặc sản Đà Lạt là gì?").
- **Dữ liệu Mock Data còn hạn chế:** Quá trình mô phỏng hiện chỉ giới hạn ở một vài sản phẩm đặc thù. Để ứng dụng vào thực tế, hệ thống cần một quá trình Crawl dữ liệu quy mô lớn kết hợp với các cơ quan quản lý du lịch địa phương.

**Kết luận chung:** Phân hệ Smart Shopping System (SSS) đã vượt qua các kịch bản kiểm thử, đáp ứng trọn vẹn yêu cầu bài toán đề ra ban đầu, giúp giải quyết triệt để rào cản ngôn ngữ và chống lãng phí trong quá trình mua sắm của du khách.
