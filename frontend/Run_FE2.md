# Hệ thống Mua sắm Thông minh - Frontend

Đây là ứng dụng frontend cho **Hệ thống Mua sắm Thông minh**, được xây dựng hoàn toàn bằng **Streamlit** (Python).

## 🚀 Tính năng

1. **Bản đồ (Map)**: Hiển thị các cửa hàng và điểm mua sắm, nhận diện vị trí người dùng.
2. **Trợ lý AI (Chatbot)**: Giao diện chat để gợi ý quà lưu niệm (Mock API).
3. **Quét Ảnh (Camera)**: Sử dụng camera hoặc tải ảnh lên để nhận diện sản phẩm tương tự (Mock API).
4. **Ghi chép Mua sắm (Log)**: Lưu lại giao dịch và cảnh báo trùng lặp.

## 📁 Cấu trúc thư mục

```text
frontend/
├── app.py                  # Tệp chính chạy ứng dụng Streamlit
├── requirements.txt        # Các thư viện phụ thuộc
├── .streamlit/
│   └── config.toml         # Cấu hình giao diện (Dark Mode)
└── views/
    ├── map_view.py         # Giao diện bản đồ Folium
    ├── chatbot_view.py     # Giao diện Chatbot AI
    ├── camera_view.py      # Giao diện Quét ảnh & Upload
    └── purchase_view.py    # Giao diện Ghi chép mua sắm
```

## 🛠️ Cài đặt & Chạy ứng dụng

Bạn cần cài đặt [Python](https://www.python.org/) trên máy tính.

1. **Di chuyển vào thư mục frontend**:
   ```bash
   cd frontend
   ```

2. **Cài đặt thư viện**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Khởi động ứng dụng Streamlit**:
   ```bash
   python -m streamlit run app.py
   ```
   *Lệnh này sẽ mở ứng dụng trên trình duyệt tại địa chỉ `http://localhost:8501`.*
