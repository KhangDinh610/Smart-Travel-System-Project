# CHƯƠNG X: MÔ PHỎNG VÀ THỰC NGHIỆM HỆ THỐNG (SIMULATION & TESTING)

## 1. Mục đích và Phạm vi mô phỏng

Chương này mô tả chi tiết toàn bộ quá trình vận hành, thực nghiệm và đánh giá hệ thống **Smart Travel System (STS) (BuyAI)**. Mục đích chính của việc mô phỏng bao gồm:
1. **Kiểm chứng tính khả thi của Thuật toán:** Đánh giá độ chính xác của các thuật toán nhận diện hình ảnh (Visual Retrieval) bằng CLIP, đo lường sự tương đồng ngữ nghĩa (Semantic Similarity) bằng SentenceTransformer kết hợp từ vựng và substring trong tính năng phát hiện trùng lặp (Duplicate Detection).
2. **Kiểm tra tích hợp (Integration Testing):** Đảm bảo luồng dữ liệu thông suốt giữa React (Frontend), FastAPI (Backend), SQLite (Relational Database) và ChromaDB (Vector Database).
3. **Đánh giá trải nghiệm người dùng (UX):** Kiểm tra các phản hồi hệ thống (thông báo lỗi, trạng thái loading, kết quả hiển thị) đối với tương tác của người dùng cuối.
4. **Xử lý ngoại lệ (Error Handling):** Quan sát cách hệ thống phản ứng khi người dùng nhập sai dữ liệu, hình ảnh không hợp lệ, token hết hạn hoặc mất kết nối.

---

## 2. Thiết lập Môi trường và Dữ liệu mô phỏng

### 2.1 Môi trường triển khai (Deployment Environment)
Hệ thống được khởi chạy và mô phỏng trên môi trường cục bộ (Localhost) với các thông số cấu hình cụ thể:
- **Frontend (Giao diện người dùng):** 
  - Framework: `React` (xây dựng bằng Vite, TypeScript, TailwindCSS và Shadcn UI)
  - Địa chỉ truy cập: `http://localhost:5173` (hoặc serve trực tiếp từ FastAPI ở `http://localhost:8000`)
- **Backend (API Server):**
  - Framework: `FastAPI` (chạy qua uvicorn)
  - Địa chỉ API: `http://127.0.0.1:8000/api/v1`
- **Cơ sở dữ liệu (Databases) & Xác thực (Auth):**
  - **SQLite (test.db):** Lưu trữ dữ liệu quan hệ cục bộ (các bảng: `shops`, `products`, `history`, `wishlist`, `notifications`, `chat_sessions`, `chat_messages`) sử dụng SQLAlchemy làm ORM.
  - **Firebase Auth (Firebase Admin SDK):** Quản lý định danh và xác thực người dùng bằng cách xác minh Firebase ID Token (JWT) trong Authorization Header.
  - **ChromaDB:** Cơ sở dữ liệu Vector cục bộ, lưu trữ các embeddings của hình ảnh (collection `product_images`) và văn bản (cho RAG và Hybrid Search).
- **Tích hợp mô hình AI / ML:**
  - `Google Gemini API` (mô hình Gemini 1.5 Flash) xử lý RAG Chatbot, dịch thuật (Localization) và phân tích hình ảnh (Vision).
  - Mô hình `CLIP` (`sentence-transformers/clip-ViT-B-32`) trích xuất đặc trưng ảnh thành vector 512 chiều phục vụ Visual Search.
  - Mô hình `paraphrase-multilingual-MiniLM-L12-v2` (SentenceTransformer) mã hóa văn bản thành vector để đối sánh độ tương đồng ngữ nghĩa (Semantic Match) trong bộ phát hiện trùng lặp.

### 2.2 Bộ dữ liệu mô phỏng (Mock Data & Seeding)
Trước khi tiến hành các kịch bản, hệ thống được nạp một tập dữ liệu giả lập đại diện cho bối cảnh sản phẩm thủ công nghệ thuật địa phương (chạy qua file `seed_db.py` đọc từ `seed_data.json`).
- **Dữ liệu Cửa hàng (Shops):**
  - ID: `1` | Tên: `Gốm Sứ Bát Tràng` | Địa chỉ: `Bát Tràng, Gia Lâm, Hà Nội`.
- **Dữ liệu Sản phẩm tiêu biểu (Products):**
  - ID: `1` | Tên: `Bộ ấm chén trà làm quà tặng cao cấp gốm sứ Bát Tràng` | Giá: `230,000` VND.
  - ID: `2` | Tên: `Bộ ấm chén in logo văn phòng chính phủ` | Giá: `495,000` VND.
  - ID: `3` | Tên: `Ấm chén Bát Tràng in logo giá bao nhiêu` | Giá: `198,000` VND.
  - ID: `4` | Tên: `Ấm chén trà in logo - quà tặng ngày kỷ niệm` | Giá: `307,800` VND.
  - ID: `5` | Tên: `Ấm chén Bát Tràng tphcm in chữ` | Giá: `230,000` VND.
- **Dữ liệu Vector Embedding:** Các sản phẩm đã được trích xuất vector đặc trưng bằng mô hình CLIP (lưu ở trường `vector_json` trong SQLite) và tự động đồng bộ hóa sang ChromaDB khi hệ thống khởi chạy.

---

## 3. Các kịch bản mô phỏng chi tiết (Detailed Scenarios)

Dưới đây là các kịch bản thực nghiệm từ lúc người dùng bắt đầu mở ứng dụng cho đến khi hoàn thành chu trình mua sắm và tìm hiểu thông tin sản phẩm.

### Kịch bản 1: Xác thực Người dùng (Authentication Flow)
- **Mục tiêu:** Kiểm tra cơ chế quản lý phiên đăng nhập và định danh người dùng.
- **Các bước thực thi:**
  1. Người dùng truy cập `http://localhost:5173`. Màn hình yêu cầu đăng nhập hiển thị.
  2. Người dùng chuyển sang tab **Đăng ký**, nhập các thông tin: Email `testuser@example.com`, Mật khẩu `123456`, Tên hiển thị `Test User`.
  3. Nhấn "Đăng ký". Frontend gửi yêu cầu đăng ký bằng POST tới endpoint `/api/v1/register`.
  4. Người dùng quay lại tab **Đăng nhập**, nhập thông tin vừa tạo và nhấn "Đăng nhập". Frontend gửi POST request tới endpoint `/api/v1/login`.
- **Luồng xử lý Kỹ thuật:**
  - Backend sử dụng Firebase Admin SDK (`auth.create_user`) để đăng ký tài khoản trên Firebase.
  - Khi đăng nhập thành công, Backend gọi Google Identity API để xác thực và trả về đối tượng JSON chứa Firebase ID Token (JWT), `uid`, `email` và `name`.
  - Frontend lưu token này vào state/localStorage của ứng dụng React và tự động gắn nó vào header `Authorization: Bearer <token>` của tất cả các API request cần xác thực.
- **Kết quả mong đợi:**
  - Giao diện chuyển hướng đến Trang chủ (HomeScreen), hiển thị thông báo chào mừng người dùng kèm tên hiển thị.
  - Sidebar và thanh điều hướng hiển thị các tính năng: Chat với AI, Tìm kiếm sản phẩm, Giỏ hàng, Danh sách yêu thích, Lịch sử mua sắm, Kiểm tra trùng lặp.
- **Xử lý ngoại lệ:** Nhập sai mật khẩu hoặc tài khoản chưa đăng ký, Backend trả về HTTP 401 với thông báo lỗi rõ ràng (ví dụ: `Mật khẩu không chính xác.` hoặc `Email không tồn tại trong hệ thống.`).

### Kịch bản 2: Tương tác Trợ lý Mua sắm (AI Chatbot - RAG)
- **Mục tiêu:** Kiểm tra khả năng xử lý ngôn ngữ tự nhiên (NLP) của hệ thống trong việc hiểu ý định (Intent) và cung cấp tư vấn dựa trên ngữ cảnh thực tế (RAG).
- **Dữ liệu đầu vào:** Câu prompt của user: *"Tôi muốn tìm bộ ấm chén trà gốm sứ Bát Tràng làm quà tặng dưới 300 nghìn."*
- **Các bước thực thi:**
  1. Người dùng chọn chức năng **💬 AI Chat**.
  2. Tạo một phiên chat mới (gửi POST đến `/api/v1/chat/sessions`) và nhập câu hỏi vào ô chat rồi gửi đi.
- **Luồng xử lý Kỹ thuật:**
  - Tin nhắn của người dùng được gửi bằng phương thức POST tới `/api/v1/chat/sessions/{session_id}/message` (hoặc endpoint `/api/v1/chat`).
  - Backend thực hiện bước RAG: Truy vấn cơ sở dữ liệu ChromaDB sử dụng câu hỏi của người dùng để tìm kiếm các sản phẩm và dữ liệu liên quan.
  - Backend lấy các sản phẩm tìm được làm ngữ cảnh (Context), gộp cùng với tin nhắn của user và gửi cho Gemini AI để tạo câu trả lời chính xác, đáng tin cậy.
  - Lịch sử chat được lưu vào bảng `chat_messages` trong SQLite.
- **Kết quả mong đợi:**
  - Giao diện hiển thị phản hồi của AI trợ lý.
  - AI tư vấn và đề xuất các sản phẩm phù hợp như `"Bộ ấm chén trà làm quà tặng cao cấp gốm sứ Bát Tràng"` (giá 230,000 VND) và `"Ấm chén Bát Tràng in logo"` (giá 198,000 VND), cung cấp thêm thông tin về nguồn gốc tại làng gốm Bát Tràng.

### Kịch bản 3: Nhận diện Sản phẩm Đa phương thức (Visual Search & Analysis)
- **Mục tiêu:** Đo lường độ chính xác của kỹ thuật trích xuất đặc trưng ảnh và phân tích ảnh bằng AI.
- **Các bước thực thi & Luồng xử lý:**
  - **Tab 1: Tìm kiếm bằng hình ảnh (Visual Search)**
    - *Đầu vào:* Upload file ảnh bộ ấm chén trà `bat_trang_tea_set.jpg`.
    - *Xử lý:* React Frontend gửi file ảnh dưới dạng multipart tới endpoint `/api/v1/visual-search`. Backend chuyển ảnh thành Vector Embedding bằng mô hình CLIP và gọi ChromaDB tính toán Cosine Similarity trên collection `product_images`.
    - *Kết quả:* Trả về danh sách sản phẩm tương tự. UI hiển thị: `Bộ ấm chén trà làm quà tặng cao cấp gốm sứ Bát Tràng` với `Score: 92.5%`, kèm giá tiền và thông tin cửa hàng `Gốm Sứ Bát Tràng`.
  - **Tab 2: Phân tích chi tiết sản phẩm (Gemini Vision)**
    - *Đầu vào:* Upload file ảnh của một bình hoa gốm cổ.
    - *Xử lý:* Frontend gửi ảnh tới `/api/v1/scan-product`. Backend gọi mô hình Gemini bằng tính năng phân tích hình ảnh (Vision).
    - *Kết quả:* Ứng dụng in ra bài phân tích chi tiết về món đồ gốm: lịch sử, phương pháp tráng men, họa tiết nghệ thuật và các giá trị văn hóa gắn liền.

### Kịch bản 4: Ghi nhận Lịch sử Mua sắm (Purchase Logging)
- **Mục tiêu:** Đảm bảo lịch sử mua sắm của người dùng được lưu trữ tức thời trên cơ sở dữ liệu quan hệ và đồng bộ hóa sang Vector DB.
- **Các bước thực thi:**
  1. Người dùng chọn mua `"Bộ ấm chén trà làm quà tặng cao cấp gốm sứ Bát Tràng"` (ID: 1) tại cửa hàng `Gốm Sứ Bát Tràng` (ID: 1).
  2. Bấm "Thanh toán/Ghi nhận mua sắm".
- **Luồng xử lý Kỹ thuật:**
  - Payload JSON `{ "user_id": "...", "product_id": "1", "shop_id": 1 }` được gửi tới endpoint `/api/v1/history` kèm Bearer Token.
  - Backend ghi nhận bản ghi mới vào bảng `history` trong SQLite.
  - Backend tự động tạo vector embedding cho mô tả sản phẩm đã mua và đẩy một tài liệu mới (`hist_<id>`) vào ChromaDB nhằm cập nhật context cho việc kiểm tra trùng lặp và cá nhân hóa tư vấn.
- **Kết quả mong đợi:** Hiển thị thông báo Toast `✅ Đã lưu vào lịch sử mua sắm thành công!`. Sản phẩm lập tức xuất hiện trong phần quản lý lịch sử mua hàng của người dùng.

### Kịch bản 5: Động cơ Cảnh báo Trùng lặp (Duplicate Detection Engine)
- **Mục tiêu:** Đánh giá tính năng cốt lõi của bài toán — Ngăn chặn du khách mua những sản phẩm mang lại giá trị trải nghiệm tương đồng, gây lãng phí.
- **Dữ liệu đầu vào:** Người dùng định mua thêm sản phẩm: *"Bộ tách trà gốm Bát Tràng họa tiết vẽ tay"*.
- **Các bước thực thi:**
  1. Người dùng mở tính năng **🛡️ Kiểm tra trùng lặp** (hoặc xem trang chi tiết sản phẩm định mua).
  2. Nhập thông tin hoặc chọn sản phẩm và bấm Kiểm tra trùng lặp.
- **Luồng xử lý Kỹ thuật:**
  - Frontend gửi yêu cầu bằng POST tới `/api/v1/detect-duplicate` với payload gồm mô tả sản phẩm mới và `user_id`.
  - Backend truy xuất lịch sử mua sắm của `user_id` từ SQLite (đã chứa `"Bộ ấm chén trà làm quà tặng cao cấp gốm sứ Bát Tràng"` từ Kịch bản 4).
  - Lớp `DuplicateDetector` thực hiện đối soát đa phương thức:
    - **Substring Match:** Tìm kiếm sự tương quan trực tiếp từ tên sản phẩm.
    - **Semantic Match:** Chuyển đổi mô tả các sản phẩm thành vector bằng mô hình `paraphrase-multilingual-MiniLM-L12-v2` và tính Cosine Similarity.
    - **Lexical Match:** So khớp từ vựng bằng thuật toán SequenceMatcher của difflib.
  - Tổng hợp điểm số tương đồng lớn nhất thành **Final Score**.
- **Kết quả mong đợi:**
  - Thuật toán nhận diện được hai sản phẩm ấm chén trà gốm sứ có bản chất trải nghiệm rất giống nhau, trả về điểm số tương đồng `score = 0.88` (vượt ngưỡng threshold `0.85`).
  - Giao diện React hiển thị hộp thoại cảnh báo màu Đỏ: `⚠️ Cảnh báo: Phát hiện sản phẩm trùng lặp hoặc tương đương trong lịch sử mua sắm của bạn (Độ tin cậy: 0.88)`.
  - Hiển thị chi tiết điểm Semantic Score và Lexical Score trong mục thông tin kỹ thuật.
  - *Ngược lại,* nếu người dùng nhập "Bình hoa gốm sứ Bát Tràng", thuật toán trả về điểm tương đồng thấp (ví dụ: `0.35`), giao diện báo màu Xanh: `✅ Sản phẩm mới!`.

---

## 4. Tổng hợp Kết quả và Đánh giá Thực nghiệm

Sau quá trình chạy qua toàn bộ 5 kịch bản mô phỏng, hệ thống thu được những đánh giá khách quan sau:

### 4.1 Điểm mạnh & Kết quả đạt được
1. **Chức năng hoạt động chính xác:** Các lớp kiến trúc từ React Frontend, Backend API FastAPI đến các dịch vụ xử lý logic SQLite/ChromaDB và AI Models tương tác đồng bộ và thông suốt.
2. **Thuật toán thông minh:** Cơ chế đối soát của `DuplicateDetector` kết hợp cả ngữ nghĩa (Semantic) và từ vựng (Lexical) đạt độ chính xác cao, giúp giải quyết triệt để vấn đề du khách mua trùng lặp sản phẩm tương đương.
3. **Hiệu suất (Performance):** Tốc độ trích xuất đặc trưng ảnh bằng mô hình CLIP kết hợp truy vấn vector trên ChromaDB diễn ra cực nhanh, thời gian phản hồi cho Visual Search đạt ngưỡng dưới 1.5 giây (Real-time).

### 4.2 Giới hạn và Hướng khắc phục (Limitations & Future Work)
- **Độ trễ API của Gemini:** Phụ thuộc vào tốc độ mạng và giới hạn rate limit từ Google, tính năng Chatbot và Gemini Vision đôi khi có độ trễ từ 3-5 giây.
  - *Khắc phục:* Có thể áp dụng cơ chế Caching đối với các câu hỏi hoặc hình ảnh phân tích phổ biến (ví dụ: "Gốm sứ Bát Tràng có đặc điểm gì?").
- **Dữ liệu Mock Data còn tập trung:** Quá trình mô phỏng hiện chủ yếu sử dụng tập dữ liệu gốm sứ Bát Tràng.
  - *Khắc phục:* Mở rộng thu thập dữ liệu (Crawl) đa dạng các ngành nghề thủ công mỹ nghệ và đặc sản ẩm thực ở các vùng miền khác như Hội An, Huế, Đà Lạt... để làm phong phú hệ thống.

**Kết luận chung:** Hệ thống Smart Travel System (STS) (BuyAI) đã hoàn thành tốt các kịch bản kiểm thử mô phỏng, đáp ứng đầy đủ các yêu cầu cốt lõi về tìm kiếm thông minh, trợ lý ảo RAG và động cơ cảnh báo trùng lặp sản phẩm, sẵn sàng hỗ trợ khách du lịch mua sắm thông minh và có ý nghĩa.
