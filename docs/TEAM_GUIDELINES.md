# QUY TRÌNH PHỐI HỢP NHÓM (TEAM GUIDELINES)

## 1. Cơ cấu nhân sự & Vai trò
*   **BE 1 (Lead):** Quản trị hệ thống, DB Schema, API Contract, Logic chung.
*   **BE 2:** Phụ trách Module AI (Computer Vision, Vector Search).
*   **BE 3:** Phụ trách Module NLP (Chatbot RAG, LangChain).
*   **FE 1:** Thiết kế UI/UX, Quản lý State (React/Flutter).
*   **FE 2:** Tích hợp API, Xử lý hiển thị dữ liệu AI.

## 2. Giao thức liên lạc
*   **Hợp đồng dữ liệu (API Contract):** Mọi thay đổi về API phải được thống nhất giữa BE Lead và FE Team trước khi triển khai.
*   **Blockers:** Nếu gặp vấn đề không giải quyết được sau 2 giờ, phải báo ngay lên nhóm để hỗ trợ.

## 3. Quản lý Task
*   Sử dụng WBS (Work Breakdown Structure) trong file `plan.md`.
*   Mỗi thành viên tự cập nhật trạng thái Task của mình:
    - `[ ]` : Chưa làm
    - `[/]` : Đang làm
    - `[x]` : Đã xong & Đã test

## 4. Kiểm soát chất lượng (Quality Gate)
*   **No Code without Test:** Mọi tính năng BE phải kèm theo script test (như `test_ai_detection.py`).
*   **Peer Review:** Khuyến khích FE review code lẫn nhau và BE review code lẫn nhau để học hỏi và giảm lỗi.
*   **CT Thinking:** Ưu tiên các giải pháp có tính tối ưu cao, chia nhỏ module (Decomposition) và dễ bảo trì.

---
*Mục tiêu của chúng ta là sản phẩm hoàn thiện sau 4 tuần làm việc nghiêm túc.*
