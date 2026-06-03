# SouvenirAI - Smart Shopping Assistant

SouvenirAI là một ứng dụng hỗ trợ mua sắm thông minh sử dụng AI để giúp khách du lịch tìm kiếm và khám phá các đặc sản địa phương, đồ thủ công mỹ nghệ và quà lưu niệm độc đáo.

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

### 1. Yêu cầu hệ thống
- Docker và Docker Compose.
- File `.env` và các tệp cấu hình Firebase trong thư mục `backend/`.

### 2. Chạy ứng dụng bằng Docker (Khuyên dùng)

Hợp nhất toàn bộ hệ thống vào một cổng duy nhất (8000).

```bash
docker-compose up --build
```

Truy cập: `http://localhost:8000`

### 3. Cài đặt thủ công (Dành cho nhà phát triển)

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

Vui lòng không commit các file chứa secret key. Sử dụng file `.env.example` để tạo file `.env` cá nhân.

Các file cần bảo mật:
- `.env`
- `backend/serviceAccountKey.json`
- `backend/gcp-vision-key.json`
