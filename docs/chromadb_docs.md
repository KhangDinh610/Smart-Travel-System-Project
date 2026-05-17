# Tài liệu Quản lý và Sử dụng ChromaDB - Smart Shopping System (SSS)

Tài liệu này tổng hợp toàn bộ các thành phần, hàm và logic liên quan đến **ChromaDB** (Vector Database) được sử dụng để triển khai các tính năng AI trong dự án.

---

## 1. Vai trò của ChromaDB trong dự án
Khác với SQLite lưu trữ dữ liệu truyền thống, ChromaDB đóng vai trò là **"Bộ não AI"**, lưu trữ dữ liệu dưới dạng **Vector Embeddings**. Điều này cho phép hệ thống thực hiện:
- **Semantic Search:** Tìm kiếm theo ý nghĩa thay vì chỉ so khớp từ khóa.
- **RAG (Retrieval-Augmented Generation):** Cung cấp ngữ cảnh thực tế cho Chatbot Gemini.
- **Duplicate Detection:** Phát hiện trùng lặp sản phẩm dựa trên độ tương đồng ngữ nghĩa.

---

## 2. Các File và Hàm quan trọng

### 2.1. File `backend/vector_db.py` (Nền tảng)
Đây là nơi cấu hình và khởi tạo ChromaDB.

*   **`class VectorDB`**: Lớp quản lý kết nối và các thao tác với Vector Store.
*   **`__init__`**: 
    *   Sử dụng `PersistentClient` để lưu trữ dữ liệu bền vững tại `backend/chroma_db`.
    *   Sử dụng mô hình `paraphrase-multilingual-MiniLM-L12-v2` (hỗ trợ tốt tiếng Việt) để chuyển văn bản thành vector.
*   **`add_documents(ids, documents, metadatas)`**: Thêm dữ liệu sản phẩm vào ChromaDB.
*   **`query(query_texts, n_results)`**: Tìm kiếm top $n$ kết quả có độ tương đồng Cosine cao nhất với câu truy vấn.
*   **`vector_db` (Singleton)**: Thực thể duy nhất được chia sẻ toàn hệ thống.

### 2.2. File `backend/api_contract.py` (Logic Nghiệp vụ)
Nơi điều phối các hoạt động của AI dựa trên dữ liệu từ ChromaDB.

*   **`sync_db_to_vector()`**: Đọc toàn bộ sản phẩm từ SQLite và nạp vào ChromaDB khi khởi động hệ thống.
*   **`chat()` (Endpoint)**: Thực hiện kỹ thuật RAG. Truy vấn ChromaDB để lấy thông tin sản phẩm liên quan và gửi kèm vào Prompt cho Gemini.
*   **`detect_duplicate()` (Endpoint)**: Truy vấn ChromaDB để kiểm tra xem mô tả sản phẩm mới có trùng lặp với dữ liệu đã có (sản phẩm cửa hàng + lịch sử mua sắm) hay không.
*   **`create_history()` (Endpoint)**: Khi người dùng ghi nhận mua sắm, hàm này tự động đẩy sản phẩm đó vào ChromaDB ngay lập tức để AI cập nhật tri thức.

### 2.3. File `backend/main.py` (Khởi động)
*   **Lệnh `sync_db_to_vector()`**: Được gọi ngay khi server bắt đầu chạy để đảm bảo dữ liệu Vector luôn đồng bộ với dữ liệu SQLite local.

---

## 3. Luồng dữ liệu AI
1.  **Dữ liệu thô:** Nằm trong SQLite (`test.db`).
2.  **Đồng bộ:** `sync_db_to_vector()` chuyển dữ liệu thô sang dạng Vector trong ChromaDB.
3.  **Xử lý yêu cầu:**
    - Người dùng đặt câu hỏi/kiểm tra trùng lặp.
    - Hệ thống truy vấn ChromaDB để lấy "Top matches".
    - Kết quả được dùng để trả lời trực tiếp hoặc làm ngữ cảnh cho Gemini AI.

---

## 4. Lưu ý về Bảo mật và Triển khai
- **Lưu trữ local:** Thư mục `backend/chroma_db` chứa dữ liệu nhị phân và đã được cấu hình trong `.gitignore` để không push lên GitHub (tránh nặng repository).
- **Tự động khởi tạo:** Dữ liệu Vector sẽ tự động được tái tạo từ SQLite thông qua hàm Sync mỗi khi deploy code ở môi trường mới.
