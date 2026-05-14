# API Documentation - Smart Shopping System (SSS)

Tài liệu này cung cấp chi tiết về các điểm cuối (endpoints) của API cho hệ thống Smart Shopping System.

## 1. Thông tin chung
- **Base URL:** `http://localhost:8000/api/v1`
- **Format:** JSON
- **Phiên bản:** 1.0.0

---

## 2. Quản lý Cửa hàng (Shops)

### 2.1. Lấy danh sách cửa hàng
- **Endpoint:** `GET /shops`
- **Mô tả:** Trả về danh sách tất cả các cửa hàng hiện có trong hệ thống.
- **Phản hồi (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Co.op Mart",
    "address": "Dist 1, HCM",
    "latitude": 10.7769,
    "longitude": 106.7009
  }
]
```

### 2.2. Tạo cửa hàng mới
- **Endpoint:** `POST /shops`
- **Mô tả:** Thêm một cửa hàng mới vào cơ sở dữ liệu.
- **Yêu cầu (Body):**
```json
{
  "name": "WinMart",
  "address": "Dist 7, HCM",
  "latitude": 10.7289,
  "longitude": 106.7067
}
```
- **Phản hồi (200 OK):**
```json
{
  "id": 2,
  "name": "WinMart",
  "address": "Dist 7, HCM",
  "latitude": 10.7289,
  "longitude": 106.7067
}
```

---

## 3. Lịch sử mua sắm (History)

### 3.1. Lấy lịch sử mua sắm
- **Endpoint:** `GET /history`
- **Tham số (Query):** `user_id` (tùy chọn) - Lọc theo ID người dùng.
- **Phản hồi (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": "user_123",
    "product_id": "prod_456",
    "shop_id": 1,
    "timestamp": "2024-03-20T10:00:00"
  }
]
```

### 3.2. Ghi nhận mua sắm
- **Endpoint:** `POST /history`
- **Yêu cầu (Body):**
```json
{
  "user_id": "user_123",
  "product_id": "prod_456",
  "shop_id": 1
}
```
- **Phản hồi (200 OK):**
```json
{
  "id": 100,
  "user_id": "user_123",
  "product_id": "prod_456",
  "shop_id": 1,
  "timestamp": "2024-03-20T10:05:00"
}
```

---

## 4. Logic AI (AI Logic)

### 4.1. Kiểm tra trùng lặp sản phẩm
- **Endpoint:** `POST /detect-duplicate`
- **Mô tả:** Sử dụng AI để kiểm tra xem một sản phẩm đã tồn tại dựa trên mô tả văn bản.
- **Yêu cầu (Query Param):** `description` (string)
- **Phản hồi (200 OK):**
```json
{
  "is_duplicate": true,
  "confidence": 0.95,
  "matched_product_id": 1,
  "message": "Potential duplicate found (Score: 0.95)"
}
```

### 4.2. Chatbot hỗ trợ (Gemini)
- **Endpoint:** `POST /chat`
- **Mô tả:** Chat với trợ lý mua sắm thông minh (sử dụng Gemini 1.5 Flash).
- **Yêu cầu (Body):**
```json
{
  "message": "Tôi nên mua gì để nấu món Phở?",
  "user_id": "user_123"
}
```
- **Phản hồi (200 OK):**
```json
{
  "reply": "Để nấu Phở, bạn cần bánh phở, thịt bò/gà, quế, hồi, thảo quả..."
}
```

### 4.3. Quét sản phẩm qua ảnh (Multimodal)
- **Endpoint:** `POST /scan-product`
- **Mô tả:** Gửi ảnh sản phẩm để Gemini phân tích tên và thông tin.
- **Yêu cầu (Form-data):** `file` (Binary image)
- **Phản hồi (200 OK):**
```json
{
  "analysis": "Đây là Sữa tươi Vinamilk ít đường, dung tích 180ml..."
}
```

---

## 5. Hệ thống (System)

### 5.1. Health Check
- **Endpoint:** `GET /health` (tại root: `/health`)
- **Mô tả:** Kiểm tra trạng thái hoạt động của server.
- **Phản hồi (200 OK):**
```json
{
  "status": "healthy",
  "env": "development",
  "version": "1.0.0"
}
```

---
