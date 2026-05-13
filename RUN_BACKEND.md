# Hướng dẫn chạy Backend

## Bước 1: Vào thư mục backend
```bash
cd /Users/khoahoang/Desktop/Smart-Travel-System-Project/backend
```

## Bước 2: Chạy Backend
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend sẽ khởi động ở `http://127.0.0.1:8000`

**Nếu gặp lỗi port đang sử dụng**, chạy:
```bash
# Tìm process dùng port 8000
lsof -i :8000

# Nếu cần kill process:
kill -9 <PID>

# Hoặc dùng port khác:
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

## Bước 3: Kiểm tra Backend
- Health check: `http://127.0.0.1:8000/health`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Ghi chú quan trọng

**Nếu không có Firebase:**
- Backend vẫn chạy được nhưng Firestore sẽ disconnect
- Dữ liệu sẽ dùng fallback data trong `ai_utils.py`
- Phần Chatbot và Recommendation sẽ vẫn hoạt động

**Nếu có Firebase:**
- Tạo file `.env` trong thư mục backend:
  ```
  FIREBASE_WEB_API_KEY=your_key
  GOOGLE_CLIENT_ID=your_id
  GOOGLE_CLIENT_SECRET=your_secret
  ```

## Troubleshooting

### Lỗi: "The default Firebase app does not exist"
 **Đã sửa** - Backend sẽ chạy bình thường mà không cần Firebase

### Lỗi: "Port 8000 already in use"
```bash
# Kill process cũ
kill -9 $(lsof -t -i :8000)
```

### Lỗi: "Cannot import module X"
```bash
# Cài đặt lại dependencies
pip install -r requirements.txt
```
