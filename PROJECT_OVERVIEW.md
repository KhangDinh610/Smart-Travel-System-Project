# Project Overview: Smart Shopping System (TDTT)

Tài liệu này tổng hợp cấu trúc và các thành phần cốt lõi của dự án để hỗ trợ nâng cấp hệ thống.

---

## 1. Tổng quan Dự án
Hệ thống mua sắm thông minh hỗ trợ tìm kiếm sản phẩm bằng hình ảnh, văn bản (semantic search), phân tích sản phẩm bằng AI (Gemini), và chat tư vấn (RAG).

### Công nghệ chính:
- **Backend**: FastAPI (Python), SQLAlchemy (SQLite), ChromaDB (Vector DB), Firebase Admin (Auth).
- **Frontend**: React (Vite, TypeScript), Shadcn UI, Framer Motion, Firebase Client SDK.
- **AI/ML**: Google Gemini API, CLIP (Visual Search), Sentence-Transformers.
- **Infrastructure**: Docker, Docker Compose.

---

## 2. Cấu trúc thư mục

```text
C:\HKII_NH_25-26\TDTT\app\
├───backend\                # Mã nguồn Backend (FastAPI)
│   ├───main.py             # Entry point, khởi tạo app & middleware
│   ├───api_contract.py     # Định nghĩa Routes, Pydantic models & Logic xử lý API
│   ├───app.py              # Cấu hình phụ (Streamlit demo hoặc phụ trợ)
│   ├───database.py         # Cấu hình SQLAlchemy & Models (SQLite)
│   ├───vector_db.py        # Giao tiếp với ChromaDB (Vector Search)
│   ├───ai_service.py       # Tích hợp Google Gemini API
│   ├───visual_search.py    # Xử lý trích xuất vector ảnh (CLIP)
│   ├───detector_logic.py   # Logic phát hiện sản phẩm trùng lặp
│   ├───translation_utils.py # Tiện ích dịch thuật đa ngôn ngữ (Hybrid AI)
│   ├───auth_middleware.py  # Xác thực người dùng qua Firebase Token
│   ├───seed_db.py          # Script nạp dữ liệu mẫu
│   ├───requirements.txt    # Danh sách thư viện Python
│   └───chroma_db\          # Cơ sở dữ liệu Vector (Local)
├───frontend\               # Mã nguồn Frontend (React)
│   ├───src\
│   │   ├───api\            # Client API (Fetch/Axios wrapper)
│   │   │   └───index.ts    # Định nghĩa các hàm gọi API & Interfaces
│   │   ├───app\
│   │   │   ├───App.tsx      # Component chính điều hướng màn hình
│   │   │   ├───firebase.ts # Cấu hình Firebase Client
│   │   │   └───components\  # Các màn hình (Login, Home, Detail, Chat...)
│   │   ├───styles\         # Tailwind & Global CSS
│   │   └───main.tsx        # Entry point của React
│   ├───package.json        # Cấu hình Node.js & Dependencies
│   └───vite.config.ts      # Cấu hình Vite
├───docs\                   # Tài liệu dự án
├───docker-compose.yml      # Cấu hình chạy Docker container
└───Dockerfile              # Build image cho toàn bộ hệ thống
```

---

## 3. Các thành phần Backend quan trọng

### 3.1 `backend/api_contract.py`
Đây là tệp quan trọng nhất, chứa:
- **Models**: `Product`, `Shop`, `History`, `ChatSession`, `ChatMessage` (Pydantic).
- **Routes**:
    - `/register`, `/login`: Xác thực.
    - `/products`: Tìm kiếm thông minh (Kết hợp Semantic + Keyword).
    - `/chat`: Hệ thống RAG (Retrieval-Augmented Generation) sử dụng Gemini.
    - `/visual-search`: Tìm kiếm bằng hình ảnh.
    - `/scan-product`: Phân tích sản phẩm qua ảnh bằng Gemini.
    - `/detect-duplicate`: Kiểm tra trùng lặp sản phẩm trong lịch sử.

### 3.2 `backend/main.py`
- Khởi tạo FastAPI.
- Kết nối Firebase Admin.
- Tự động seeding dữ liệu nếu DB trống.
- Đồng bộ dữ liệu sang VectorDB khi khởi động.
- Serve Frontend tĩnh (dist folder) cùng port với API.

### 3.3 `backend/ai_service.py`
- Quản lý API Key của Google Gemini.
- Xử lý prompt để phân tích ảnh và sinh phản hồi chat.
- Xử lý lỗi quota và retry logic.

---

## 4. Các thành phần Frontend quan trọng

### 4.1 `frontend/src/api/index.ts`
- Định nghĩa các interface TypeScript đồng nhất với Backend.
- `api` object chứa các phương thức gọi API (`getProducts`, `visualSearch`, `sendChatMessage`...).
- Xử lý Bearer Token từ Firebase cho các request cần xác thực.

### 4.2 `frontend/src/app/App.tsx`
- Quản lý trạng thái đăng nhập (`user`).
- Điều hướng giữa các màn hình (`Screen` state).
- Quản lý đa ngôn ngữ (Vi/En).
- Xử lý trạng thái offline/online.

---

## 5. Danh sách API chính (Endpoints)

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| POST | `/api/v1/register` | Đăng ký user mới qua Firebase | No |
| POST | `/api/v1/login` | Đăng nhập email/password | No |
| GET | `/api/v1/products` | Tìm kiếm sản phẩm (Search/Filter/AI expansion) | No |
| GET | `/api/v1/products/{id}` | Chi tiết sản phẩm (kèm dịch thuật AI) | No |
| POST | `/api/v1/chat` | Chat với AI (RAG) | Yes |
| POST | `/api/v1/visual-search` | Tìm kiếm bằng hình ảnh (CLIP) | No |
| POST | `/api/v1/scan-product` | AI phân tích thuộc tính sản phẩm từ ảnh | No |
| POST | `/api/v1/detect-duplicate` | Kiểm tra sản phẩm đã mua trước đó | Yes |

---

## 6. Các Logic cốt lõi (Key Logic)

### 6.1 Luồng Tìm kiếm Sản phẩm (Hybrid Search)
Trong `backend/api_contract.py` -> `get_products`:
1. **AI Query Expansion**: Sử dụng Gemini để mở rộng từ khóa tìm kiếm (ví dụ: "trà" -> "trà thái nguyên, ấm chén, trà xanh, tea").
2. **Semantic Search**: Tìm kiếm vector trong ChromaDB bằng từ khóa đã mở rộng.
3. **Keyword Search**: Tìm kiếm truyền thống (LIKE) trong SQLite trên các cột `name`, `description` (cả VN và EN).
4. **Merge**: Kết hợp kết quả, ưu tiên kết quả từ Semantic Search.

### 6.2 Hệ thống RAG (Retrieval-Augmented Generation)
Trong `backend/api_contract.py` -> `send_chat_message`:
1. Nhận tin nhắn từ User.
2. Truy vấn ChromaDB để tìm các sản phẩm/lịch sử liên quan đến tin nhắn.
3. Gửi câu hỏi kèm theo "Context" (các sản phẩm tìm được) cho Gemini.
4. Gemini sinh câu trả lời dựa trên dữ liệu thực tế của hệ thống thay vì trả lời chung chung.

### 6.3 Tìm kiếm bằng hình ảnh (Visual Search)
Trong `backend/visual_search.py` & `backend/api_contract.py`:
1. Sử dụng model **CLIP** (`sentence-transformers/clip-ViT-B-32`) để chuyển ảnh thành vector 512 chiều.
2. Truy vấn collection `product_images` trong ChromaDB để tìm các vector gần nhất.

---

## 7. Hướng dẫn nâng cấp (Dành cho Claude)
Khi đưa dự án lên Claude Project, bạn có thể sử dụng file này làm "Context Map". Các yêu cầu nâng cấp có thể tập trung vào:
1. **Performance**: Tối ưu hóa việc load CLIP model hoặc ChromaDB query.
2. **Features**:
    - Thêm giỏ hàng (Cart logic).
    - Tích hợp thanh toán.
    - Nâng cấp hệ thống gợi ý sản phẩm dựa trên hành vi (Personalization).
3. **UI/UX**: Cải thiện giao diện bằng các component mới từ Shadcn.
4. **Security**: Siết chặt CORS và phân quyền người dùng (Role-based access).

---
*Tài liệu được tạo tự động bởi Gemini CLI vào ngày 16/06/2026.*
