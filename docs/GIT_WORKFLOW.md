# QUY TRÌNH GITHUB WORKFLOW - SMART SHOPPING SYSTEM

## 1. Nguyên tắc chung
*   **Trunk-based Development:** Nhánh `main` luôn luôn phải ở trạng thái chạy được (deployable).
*   **Feature Branches:** Mọi tính năng mới hoặc sửa lỗi đều phải thực hiện trên nhánh riêng.
*   **Pull Requests (PR):** Mọi code trước khi vào `main` đều phải qua PR và được ít nhất 1 thành viên khác review.

## 2. Quy tắc đặt tên Nhánh (Branch Naming)
Cấu trúc: `loại-nhánh/tên-ngắn-gọn`
*   `feat/` : Tính năng mới (Ví dụ: `feat/ai-detector`)
*   `fix/` : Sửa lỗi (Ví dụ: `fix/db-connection`)
*   `docs/` : Cập nhật tài liệu (Ví dụ: `docs/git-workflow`)
*   `refactor/` : Tối ưu hóa code nhưng không đổi tính năng.

## 3. Quy tắc Commit (Commit Message)
Sử dụng chuẩn **Conventional Commits**: `<type>: <description>`
*   `feat: thêm module trích xuất đặc trưng ảnh`
*   `fix: sửa lỗi crash khi nhận ảnh rỗng`
*   `docs: cập nhật hướng dẫn cài đặt`

*Lưu ý: Mỗi commit chỉ nên giải quyết một vấn đề duy nhất (Atomic Commit).*

## 4. Chu trình làm việc (Workflow Steps)
1.  `git checkout main` & `git pull origin main` (Luôn bắt đầu từ code mới nhất).
2.  `git checkout -b feat/tên-tính-năng` (Tạo nhánh mới).
3.  Thực hiện code & Test local.
4.  `git add .` & `git commit -m "feat: mô tả"` (Commit thường xuyên).
5.  `git push origin feat/tên-tính-năng`.
6.  Tạo **Pull Request** trên GitHub, tag Reviewer.
7.  Sau khi được Approve, thực hiện **Merge** và xóa nhánh feature.

---
*Tài liệu dành cho nhóm phát triển dự án Smart Shopping System.*