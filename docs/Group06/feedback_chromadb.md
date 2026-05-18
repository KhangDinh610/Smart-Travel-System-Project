# Thiếu sót cần bổ sung cho BE2 demo

Mục tiêu: hoàn thiện luồng ảnh -> CLIP -> ChromaDB -> trả về thông tin sản phẩm để user test demo.

## 1) Dữ liệu sản phẩm chưa có

Bảng products` trong 'test.db đang rỗng.

Cần thêm dữ liệu mẫu (shops + products) để demo có kết quả.

## 2) vector_json chưa được nạp

BE2 truy vấn ChromaDB bằng vector ảnh, cần vector_json là CLIP 512-dim (list float) cho từng sản phẩm.

Cần script để sinh 'vector_json' từ ảnh sản phẩm (CLIP) và lưu vào SQLite.

## 3) Đồng bộ sang ChromaDB image collection

Cần chạy hàm sync_image_collection_from_sqlite để nạp embeddings + metadata vào ChromaDB.

Nên bổ sung nút "Sync from SQLite" trong UI (tùy chọn) hoặc hướng dẫn chạy lệnh đồng bộ.

## 4) Thông tin sản phẩm cần trả về

Hiện database chưa có trường giá (price). Nếu cần trả về giá, cần bổ sung trường `price` trong schema hoặc lưu trong metadata khi đồng bộ.

Cần thống nhất metadata: `name`, `description`, `price`, `shop_name` shop_address`, `shop_id`.