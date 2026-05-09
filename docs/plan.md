# KẾ HOẠCH PHÁT TRIỂN DỰ ÁN: SMART SHOPPING SYSTEM (4 TUẦN)

## 1. Cấu trúc Nhân sự (Roles)
Dự án được chia theo mô hình **Backend (BE)** và **Frontend (FE)** với tỉ lệ 3 BE - 2 FE để đảm bảo xử lý tốt các tác vụ AI và dữ liệu nặng.

### Team Backend (3 người)
*   **BE 1 (Khang - Lead):** Thiết kế API, Database, Logic hệ thống & Cảnh báo trùng lặp (Duplicate Detection).
*   **BE 2 (A):** Xử lý Computer Vision (Nhận diện ảnh) & Quản lý Vector Database (ChromaDB).
*   **BE 3 (B):** Xây dựng NLP Chatbot (RAG) & Thuật toán gợi ý (Recommendation Engine).

### Team Frontend (2 người)
*   **FE 1 (C):** Xây dựng UI chính, Tích hợp Bản đồ (Maps API) & Quản lý State ứng dụng.
*   **FE 2 (D):** Xây dựng giao diện Camera (Scan sản phẩm), Giao diện Chatbot & Form ghi nhận mua sắm.

---

## 2. Work Breakdown Structure (WBS) & Lộ trình 4 tuần

### Tuần 1: Thiết kế & Hợp đồng dữ liệu (API Contract)
*Mục tiêu: Thống nhất giao thức kết nối để FE và BE có thể làm việc song song.*

| Team | Công việc chính | Đầu ra (Deliverables) |
| :--- | :--- | :--- |
| **Backend** | Thiết kế DB Schema; Viết tài liệu API (Swagger/Postman); Setup môi trường Cloud Vision & OpenAI API. | API Document, DB Initialization. |
| **Frontend** | Thiết kế Wireframe/Figma; Khởi tạo Project (React/Streamlit); Cài đặt thư viện Map & Camera. | Wireframe, Project Skeleton. |

### Tuần 2: Phát triển song song (Independent Development)
*Mục tiêu: BE xây dựng logic AI/Data, FE xây dựng giao diện tương tác.*

| Team | Công việc chính | Đầu ra (Deliverables) |
| :--- | :--- | :--- |
| **Backend** | **BE 1:** CRUD Shop & History; **BE 2:** Embedding ảnh & Search logic; **BE 3:** Prompt Engineering & Scoring logic. | Các module chức năng độc lập. |
| **Frontend** | **FE 1:** Màn hình Map với Marker dữ liệu mẫu; **FE 2:** Giao diện Camera (viewfinder) & Khung Chatbot. | UI tĩnh (Static UI) hoàn thiện. |

### Tuần 3: Tích hợp hệ thống (Integration)
*Mục tiêu: Kết nối FE với BE qua API thực tế.*

| Team | Công việc chính | Đầu ra (Deliverables) |
| :--- | :--- | :--- |
| **Backend** | Hoàn thiện logic Duplicate Detection; Tối ưu hóa RAG để giảm độ trễ Chatbot. | API hoàn thiện 100%. |
| **Frontend** | Kết nối API nhận diện ảnh; Đổ dữ liệu Shop từ DB lên Map; Xử lý hiển thị Product Card trong Chat. | Bản Beta chạy được luồng chính. |

### Tuần 4: Kiểm thử, Tối ưu & Đóng gói (QA & Deployment)
*Mục tiêu: Sửa lỗi, triển khai và chuẩn bị tài liệu bàn giao.*

| Team | Công việc chính | Đầu ra (Deliverables) |
| :--- | :--- | :--- |
| **Cả nhóm** | Test luồng End-to-End: Nhận diện -> Gợi ý -> Mua -> Log -> Cảnh báo trùng. | Hệ thống ổn định. |
| **Backend** | Triển khai server lên Cloud (Render/AWS). | Live API URL. |
| **Frontend** | Tối ưu UI/UX (Loading, Error messages); Đóng gói build sản phẩm. | Production App/Web URL. |

---
