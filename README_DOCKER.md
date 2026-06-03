# Hướng dẫn chạy ứng dụng bằng Docker

Hệ thống đã được đóng gói gọn gàng vào 1 Dockerfile duy nhất giúp bạn có thể chạy toàn bộ Frontend và Backend chỉ với 1 câu lệnh.

## 1. Chuẩn bị
Trước khi build Docker, hãy đảm bảo các file sau đã có sẵn trong thư mục `backend/`:
- `serviceAccountKey.json` (Firebase Admin SDK)
- `gcp-vision-key.json` (Google Cloud Vision API - nếu dùng)

Và file `.env` ở thư mục gốc với các thông số cần thiết (API Keys).

## 2. Chạy bằng Docker Compose (Khuyên dùng)
Nếu bạn đã cài đặt Docker Desktop, chỉ cần chạy:

```bash
docker-compose up --build
```

Ứng dụng sẽ khả dụng tại: [http://localhost:8000](http://localhost:8000)

## 3. Chạy bằng Docker thuần
Nếu không dùng compose:

```bash
# Build image
docker build -t smart-shopping-app .

# Chạy container
docker run -p 8000:8000 --env-file .env smart-shopping-app
```

## Các tính năng đã được tối ưu cho Docker:
- **Multi-stage build:** Giúp giảm kích thước image.
- **Unified Port:** Cả Frontend và Backend chạy chung port 8000.
- **Auto-Sync:** Hệ thống tự động đồng bộ Vector DB khi khởi động.
- **Persistence:** Database và ChromaDB được lưu vào volumes để không mất dữ liệu khi tắt container.
