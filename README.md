# BuyAI - Smart Shopping Assistant

BuyAI là một ứng dụng hỗ trợ mua sắm thông minh sử dụng AI để giúp khách du lịch tìm kiếm và khám phá các đặc sản địa phương, đồ thủ công mỹ nghệ và quà lưu niệm độc đáo.

## 🚀 Tính năng chính

- **Tìm kiếm thông minh (AI Search):** Hỗ trợ tìm kiếm đa ngôn ngữ (Anh/Việt) với khả năng hiểu ngữ nghĩa (Semantic Search) và tự động mở rộng từ khóa bằng Gemini AI.
- **AI Chatbot:** Trợ lý ảo tư vấn chi tiết về nguồn gốc, giá cả và ý nghĩa của các sản phẩm đặc sản.
- **Tìm kiếm bằng hình ảnh (Visual Search):** Sử dụng model CLIP để tìm kiếm sản phẩm tương đương từ ảnh chụp.
- **AI Scanner:** Phân tích nhanh thông tin sản phẩm qua ảnh chụp.
- **Đăng nhập Google:** Tích hợp Firebase Authentication giúp đăng nhập nhanh chóng và bảo mật.
- **Giao diện đa ngôn ngữ:** Tự động bản địa hóa (Localization) tên và mô tả sản phẩm sang tiếng Anh.

## 🛠️ Công nghệ sử dụng

- **Frontend:** React (TypeScript), Vite, TailwindCSS, Lucide Icons.
- **Backend:** FastAPI (Python), SQLAlchemy, SQLite.
- **AI/ML:** Google Gemini 1.5 Flash, ChromaDB (Vector DB), OpenAI CLIP, Sentence-Transformers.
- **Infrastructure:** Docker, Docker Compose, Firebase.

## 📦 Hướng dẫn cài đặt và chạy

### 1. Cài đặt thủ công (Dành cho nhà phát triển)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔒 Bảo mật và Cấu hình

Vui lòng không commit các file chứa secret key. Sử dụng file `.env.example` để tạo file `.env` cá nhân ở thư mục gốc của dự án.

Các file cần bảo mật:
- `.env`
- `backend/serviceAccountKey.json` (Tải từ Firebase Console -> Project Settings -> Service Accounts)
- `backend/gcp-vision-key.json` (Tùy chọn cho Google Vision API)

### ⚠️ Xử lý lỗi API Key

Nếu bạn gặp lỗi **"Missing API Key"** hoặc **"Firebase configuration is invalid"**:
1. Đảm bảo đã copy `.env.example` thành `.env` tại thư mục gốc.
2. Kiểm tra file `.env` đã có đầy đủ các biến sau chưa:
   - `GEMINI_API_KEY`: Lấy tại [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key).
   - `VITE_FIREBASE_API_KEY` và các biến `VITE_FIREBASE_*`: Lấy tại Firebase Console -> Project Settings -> General -> Your apps -> Web app.
3. Nếu chạy Docker, hãy chạy lại lệnh `docker-compose up --build` để cập nhật các biến môi trường vào quá trình build frontend.

