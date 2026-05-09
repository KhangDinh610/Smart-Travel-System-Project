# BÁO CÁO ĐỒ ÁN CUỐI KỲ
# MÔN TƯ DUY TÍNH TOÁN

---

<div align="center">

## SMART SHOPPING SYSTEM

| Thông tin | Chi tiết |
|-----------|----------|
| **Học kỳ** | Học kỳ II – Năm học 2025–2026 |
| **Mã môn học** | CSC10014 |
| **Tên môn học** | Tư duy Tính toán (Computational Thinking) |
| **Mã lớp** | CQ2024/6 |
| **Mã nhóm** | Nhóm 06 |
| **Giảng viên** | Hồ Tuấn Thanh, Mai Anh Tuấn |
| **Trợ giảng** | Phạm Nguyễn Sơn Tùng |
| **Ngày cập nhật** | 22/04/2026 09:00 |

### Danh sách thành viên nhóm

| MSSV | Họ và Tên |
|------|-----------|
| 24120332 | Đinh Công Khang |
| 24120090 | Đặng Hồng Minh |
| 24120215 | Nguyễn Ngọc Phúc |
| 24120245 | Trần Lê Đức Việt |
| 24120344 | Hoàng Trần Minh Khoa |

</div>

---

## MỤC LỤC

- [1. Thành viên nhóm](#1-thành-viên-nhóm)
- [2. Ý tưởng dự án](#2-ý-tưởng-dự-án)
  - [2.1 Phát biểu bài toán](#21-phát-biểu-bài-toán)
  - [2.2 Tầm nhìn sản phẩm](#22-tầm-nhìn-sản-phẩm)
  - [2.3 Đối tượng người dùng mục tiêu](#23-đối-tượng-người-dùng-mục-tiêu)
- [3. Phân tích và Phân rã bài toán](#3-phân-tích-và-phân-rã-bài-toán)
- [4. Tổng quan hệ thống](#4-tổng-quan-hệ-thống)
  - [4.1 Các bên liên quan](#41-các-bên-liên-quan)
  - [4.2 Các tác nhân chính](#42-các-tác-nhân-chính)
  - [4.3 Danh sách tính năng cốt lõi](#43-danh-sách-tính-năng-cốt-lõi)
  - [4.4 Giải thích tính năng cốt lõi](#44-giải-thích-tính-năng-cốt-lõi)
- [5. Nhận diện mẫu (Pattern Recognition)](#5-nhận-diện-mẫu-pattern-recognition)
- [6. Trừu tượng hóa (Abstraction)](#6-trừu-tượng-hóa-abstraction)
- [7. Thiết kế hệ thống và thuật toán](#7-thiết-kế-hệ-thống-và-thuật-toán)
  - [7.1 Công nghệ sử dụng](#71-công-nghệ-sử-dụng)
  - [7.2 Kiến trúc hệ thống](#72-kiến-trúc-hệ-thống)
- [8. Hiện thực hóa (Implementation)](#8-hiện-thực-hóa-implementation)
- [9. Kiểm thử (Testing)](#9-kiểm-thử-testing)
- [10. Demo](#10-demo)
- [11. Triển khai (Deployment)](#11-triển-khai-deployment)
- [12. Nhật ký làm việc](#12-nhật-ký-làm-việc)
- [13. Khai báo sử dụng AI](#13-khai-báo-sử-dụng-ai)
- [14. Kết luận và Hướng phát triển](#14-kết-luận-và-hướng-phát-triển)

---

## 1. Thành viên nhóm

| MSSV | Họ và Tên | Email | Vai trò / Trách nhiệm |
|------|-----------|-------|----------------------|
| 24120332 | Đinh Công Khang | 24120332@student.hcmus.edu.vn | Nhóm trưởng, Problem Analysis, Phân rã bài toán |
| 24120090 | Đặng Hồng Minh | 24120090@student.hcmus.edu.vn | Thành viên, Recommendation Engine, Data Normalization |
| 24120215 | Nguyễn Ngọc Phúc | 24120215@student.hcmus.edu.vn | Thành viên, Visual Product Retrieval, Image Processing |
| 24120245 | Trần Lê Đức Việt | 24120245@student.hcmus.edu.vn | Thành viên, AI Assistant, NLP Logic, RAG Development |
| 24120344 | Hoàng Trần Minh Khoa | 24120344@student.hcmus.edu.vn | Thành viên, Testing, Documentation, Purchase History Logic |

---

## 2. Ý tưởng dự án

### 2.1 Phát biểu bài toán
> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

**Vấn đề đang tồn tại:** Du khách khi mua sắm tại điểm du lịch thường gặp rào cản về ngôn ngữ, văn hóa dẫn đến việc thiếu thông tin minh bạch về sản phẩm địa phương. Hơn nữa, quyết định mua sắm thường thụ động và dễ dẫn đến việc mua trùng lặp các món quà hoặc sản phẩm lưu niệm tương tự nhau do khó ghi nhớ những gì đã mua trong suốt chuyến đi.
**Tại sao vấn đề này quan trọng:** Mua sắm là cầu nối trực tiếp để du khách trải nghiệm văn hóa bản địa. Một trải nghiệm mua sắm kém, mua nhầm đồ hoặc mua trùng lặp gây lãng phí, ảnh hưởng nghiêm trọng đến chất lượng chuyến đi và giảm động lực du lịch.
**Hiện tại:** Du khách thường dựa vào review trên mạng hoặc tự tìm kiếm thủ công, dễ bị "hớ giá" hoặc mua phải hàng kém chất lượng. Chưa có công cụ nào chuyên biệt để cá nhân hóa gợi ý quà tặng, nhận diện sản phẩm và đồng thời cảnh báo việc mua sắm trùng lặp.

### 2.2 Tầm nhìn sản phẩm
> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

**Sản phẩm sẽ làm gì:** Xây dựng một phân hệ Smart Shopping tự động hóa việc tìm kiếm và gợi ý địa điểm mua sắm, nhận diện sản phẩm qua ảnh chụp (kèm thông tin về ý nghĩa văn hóa), tư vấn mua sắm cá nhân hóa qua trợ lý AI và ghi nhận lịch sử mua sắm để cảnh báo trùng lặp.
**Giá trị mang lại:** Giúp du khách tiết kiệm thời gian, dễ dàng vượt qua rào cản ngôn ngữ, tìm được đúng sản phẩm mang đậm chất văn hóa địa phương mà không lo bị mua trùng hay mua "hớ".

### 2.3 Đối tượng người dùng mục tiêu
> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

| Nhóm người dùng | Mô tả | Nhu cầu chính |
|----------------|-------|---------------|
| **Du khách** | Khách du lịch trong & ngoài nước, không quen thuộc với địa phương. | Tìm sản phẩm phù hợp, vượt rào cản ngôn ngữ, xem ý nghĩa văn hóa, ghi nhận mua sắm nhanh để không mua trùng. |
| **Người bán hàng** | Chủ các cửa hàng, gian hàng tại địa điểm du lịch. | Tăng doanh thu, tiếp cận đúng đối tượng khách du lịch đang có nhu cầu thực sự. |

---

## 3. Phân tích và Phân rã bài toán

> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

Hệ thống được thiết kế theo nguyên tắc Functional Decomposition (Top-down) — phân rã theo chức năng tính toán cốt lõi. Bài toán lớn là "Hỗ trợ du khách mua sắm thông minh" được phân rã thành 4 module độc lập để giải quyết triệt để từng khía cạnh: Nhập liệu, Gợi ý, Nhận diện và Tư vấn.

### 3.1 Phân rã bài toán tổng thể

```text
Hệ thống Smart Shopping
├── Bài toán con 1: Xử lý dữ liệu đầu vào (M1 - Input Processing)
│   ├── Chuẩn hóa tọa độ GPS
│   └── Trích xuất đặc trưng hình ảnh
├── Bài toán con 2: Động cơ gợi ý (M2 - Recommendation Engine)
│   ├── Bộ lọc trùng lặp (Duplicate Filter)
│   └── Chấm điểm và Xếp hạng (Scoring & Ranking)
├── Bài toán con 3: Nhận diện sản phẩm bằng ảnh (M3 - Visual Product Retrieval)
│   ├── Trích xuất Vector Embedding
│   └── Truy xuất thông tin sản phẩm và ý nghĩa văn hóa
└── Bài toán con 4: Trợ lý ảo & Ghi nhận (M4 - AI Assistant & Logger)
    ├── Chatbot tư vấn qua ngôn ngữ tự nhiên (NLP / RAG)
    └── Ghi nhận lịch sử mua sắm (Purchase Logger)
```

### 3.2 Phân tích chi tiết từng bài toán con

> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

**Bài toán con 1: M1 - Input Processing**
Chịu trách nhiệm thu thập tọa độ người dùng, chuyển đổi sở thích thành vector dữ liệu chuẩn, trích xuất ảnh đầu vào để chuẩn bị cho các bước xử lý máy học.

**Bài toán con 2: M2 - Recommendation Engine**
Lọc các cửa hàng xung quanh theo khoảng cách. Tích hợp tính năng mới **Duplicate Filter** để loại bỏ hoặc đánh dấu những sản phẩm mà hệ thống phát hiện user đã mua. Sử dụng hàm Scoring: `w1·rating + w2·tag_match + w3·novelty` để trả về Top 10 cửa hàng tốt nhất.

**Bài toán con 3: M3 - Visual Product Retrieval**
Giải quyết rào cản ngôn ngữ. Du khách chỉ cần chụp ảnh sản phẩm, bài toán này sẽ dùng mạng CNN trích xuất vector đặc trưng, tìm kiếm sản phẩm tương tự bằng Cosine Similarity và trả về thông tin văn hóa, giá bán tham khảo.

**Bài toán con 4: M4 - AI Assistant & Logger**
Sử dụng LLM để đọc hiểu yêu cầu của người dùng (ví dụ: "Tìm quà cho bạn gái giá 500k"). Đồng thời cung cấp giao diện để người dùng log tay thông tin mua sắm (`{product_id, quantity, shop}`) nhằm cập nhật Context cho thuật toán tránh gợi ý trùng lặp (Duplicate Detection).

---

## 4. Tổng quan hệ thống

### 4.1 Các bên liên quan
> *[24120090 – Đặng Hồng Minh: Tác giả / Người review]*

| Bên liên quan | Vai trò | Mức độ ảnh hưởng |
|--------------|---------|-----------------|
| **Du khách** | Người dùng chính sử dụng ứng dụng để tìm kiếm, hỏi đáp AI và tránh mua trùng sản phẩm | Cao |
| **Người bán hàng** | Cung cấp thông tin sản phẩm, nhận khách hàng được điều hướng tới cửa hàng | Cao |

### 4.2 Các tác nhân chính
> *[24120090 – Đặng Hồng Minh: Tác giả / Người review]*

| Loại người dùng | Mô tả | Quyền hạn |
|----------------|-------|-----------|
| **Du khách (End-User)** | Người trải nghiệm hệ thống qua giao diện app/web | Xem bản đồ, upload ảnh nhận diện, chat với AI, ghi nhận lịch sử mua sắm cá nhân |

### 4.3 Danh sách tính năng cốt lõi
> *[24120215 – Nguyễn Ngọc Phúc: Tác giả / Người review]*

| STT | Tính năng | Mô tả ngắn | Độ ưu tiên |
|-----|-----------|-----------|------------|
| 1 | **Nhận diện sản phẩm từ ảnh** | Trả về tên, giá, ý nghĩa văn hóa từ ảnh chụp | Cao |
| 2 | **Tư vấn mua sắm Chatbot** | AI đàm thoại gợi ý quà tặng, có cảnh báo trùng | Cao |
| 3 | **Ghi nhận mua sắm (Purchase Log)** | Lưu lịch sử mua nhanh thủ công để AI học sở thích | Cao |
| 4 | **Cảnh báo trùng lặp (Duplicate Detection)** | Báo động khi sản phẩm gợi ý giống với sản phẩm đã mua | Cao |

### 4.4 Giải thích tính năng cốt lõi
> *[24120215 – Nguyễn Ngọc Phúc: Tác giả / Người review]*

**Tính năng 1: Nhận diện sản phẩm từ ảnh**
Thay vì cố gắng dịch ngôn ngữ trên bao bì, người dùng chỉ cần upload hình. Hệ thống chuyển thành vector, query trong VectorDB và trả về ngay nguồn gốc, giá chuẩn và đặc biệt là ý nghĩa văn hóa của sản phẩm đó (nếu có).

**Tính năng 2: Ghi nhận mua sắm & Cảnh báo trùng lặp**
Du khách nhập tay nhanh món đồ vừa mua (tên, số lượng). Dữ liệu này được lưu vào History. Khi AI Assistant gợi ý món quà mới, nó sẽ đối chiếu với History và lập tức hiện cảnh báo nếu món đồ tương tự đã được mua trước đó.

---

## 5. Nhận diện mẫu (Pattern Recognition)

> *[MSSV – Họ và Tên: Tác giả / Người review]*

> Trình bày chi tiết cách nhóm áp dụng kỹ thuật **nhận diện mẫu (Pattern Recognition)** trong dự án:
> - Những mẫu (patterns) nào đã được nhận diện trong bài toán?
> - Những mẫu này có ý nghĩa gì và được sử dụng như thế nào?
> - Bao gồm sơ đồ, bảng biểu, hình ảnh minh họa phù hợp.

### 5.1 Các mẫu được nhận diện

| Mẫu (Pattern) | Mô tả | Ứng dụng trong dự án |
|--------------|-------|---------------------|
| [Tên mẫu 1] | [Mô tả] | [Cách ứng dụng] |
| [Tên mẫu 2] | [Mô tả] | [Cách ứng dụng] |

### 5.2 Phân tích chi tiết

> *[MSSV – Họ và Tên: Tác giả / Người review]*

[Phân tích sâu hơn về từng mẫu, kèm sơ đồ/hình ảnh minh họa...]

---

## 6. Trừu tượng hóa (Abstraction)

> *[MSSV – Họ và Tên: Tác giả / Người review]*

> Trình bày chi tiết cách nhóm áp dụng kỹ thuật **trừu tượng hóa (Abstraction)** trong dự án:
> - Những thông tin nào được giữ lại (quan trọng)?
> - Những thông tin nào được bỏ qua (không cần thiết)?
> - Các mô hình trừu tượng nào được xây dựng?
> - Bao gồm sơ đồ, bảng biểu, hình ảnh minh họa phù hợp.

### 6.1 Mô hình trừu tượng

[Mô tả các mô hình trừu tượng hóa chính trong dự án...]

### 6.2 Các lớp trừu tượng

> *[MSSV – Họ và Tên: Tác giả / Người review]*

| Lớp | Mô tả | Thông tin giữ lại | Thông tin bỏ qua |
|-----|-------|------------------|-----------------|
| [Lớp 1] | [Mô tả] | [Thông tin] | [Thông tin] |
| [Lớp 2] | [Mô tả] | [Thông tin] | [Thông tin] |

[Kèm sơ đồ/hình ảnh minh họa...]

---

## 7. Thiết kế hệ thống và thuật toán

### 7.1 Công nghệ sử dụng
> *[MSSV – Họ và Tên: Tác giả / Người review]*

| Tầng | Công nghệ | Lý do lựa chọn |
|------|-----------|---------------|
| **Frontend** | [React / Vue / HTML...] | [Lý do] |
| **Backend** | [Node.js / Python / Java...] | [Lý do] |
| **Database** | [MySQL / MongoDB / PostgreSQL...] | [Lý do] |
| **AI/ML** | [TensorFlow / OpenAI API...] | [Lý do] |
| **Khác** | [Docker / AWS / Firebase...] | [Lý do] |

### 7.2 Kiến trúc hệ thống
> *[MSSV – Họ và Tên: Tác giả / Người review]*

> Sử dụng mô hình C4 (https://c4model.com/) làm tài liệu tham khảo để mô tả kiến trúc hệ thống.

#### 7.2.1 Mức độ 1 – System Context Diagram

[Mô tả và sơ đồ tổng quan hệ thống, người dùng tương tác với hệ thống như thế nào, các hệ thống bên ngoài...]

```
[Chèn sơ đồ System Context tại đây]
```

#### 7.2.2 Mức độ 2 – Container Diagram

> *[MSSV – Họ và Tên: Tác giả / Người review]*

[Mô tả các container (ứng dụng, database, microservices...) trong hệ thống...]

```
[Chèn sơ đồ Container tại đây]
```

#### 7.2.3 Mức độ 3 – Component Diagram (tùy chọn)

> *[MSSV – Họ và Tên: Tác giả / Người review]*

[Mô tả các component bên trong mỗi container...]

```
[Chèn sơ đồ Component tại đây]
```

#### 7.2.4 Thiết kế thuật toán chính

> *[MSSV – Họ và Tên: Tác giả / Người review]*

[Mô tả các thuật toán quan trọng được sử dụng, pseudocode hoặc flowchart...]

---

## 8. Hiện thực hóa (Implementation)

> *[MSSV – Họ và Tên: Tác giả / Người review]*

> Trình bày các thách thức trong quá trình triển khai và giải pháp đã áp dụng.

### 8.1 Thách thức và Giải pháp

**Thách thức 1: [Tên thách thức]**

> *[MSSV – Họ và Tên: Tác giả / Người review]*

- **Mô tả:** [Mô tả thách thức gặp phải...]
- **Giải pháp:** [Cách nhóm giải quyết...]
- **Kết quả:** [Kết quả đạt được...]

[Kèm code snippet, sơ đồ, hình ảnh minh họa nếu cần...]

```python
# Ví dụ code snippet
def example_function():
    pass
```

**Thách thức 2: [Tên thách thức]**

> *[MSSV – Họ và Tên: Tác giả / Người review]*

- **Mô tả:** [...]
- **Giải pháp:** [...]
- **Kết quả:** [...]

### 8.2 Các quyết định thiết kế quan trọng

> *[MSSV – Họ và Tên: Tác giả / Người review]*

[Ghi lại các quyết định thiết kế quan trọng và lý do đưa ra quyết định đó...]

---

## 9. Kiểm thử (Testing)

### 9.1 Danh sách test case
> *[MSSV – Họ và Tên: Tác giả / Người review]*

| STT | Tính năng | Mô tả Test Case | Đầu vào | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
|-----|-----------|----------------|---------|-----------------|----------------|-----------|
| TC01 | [Tính năng] | [Mô tả] | [Input] | [Expected] | [Actual] | ✅ Pass / ❌ Fail |
| TC02 | [Tính năng] | [Mô tả] | [Input] | [Expected] | [Actual] | ✅ Pass / ❌ Fail |
| TC03 | [Tính năng] | [Mô tả] | [Input] | [Expected] | [Actual] | ✅ Pass / ❌ Fail |

### 9.2 Báo cáo lỗi (Bug Report)
> *[MSSV – Họ và Tên: Tác giả / Người review]*

| ID | Mô tả lỗi | Mức độ | Trạng thái | Cách giải quyết |
|----|-----------|--------|-----------|----------------|
| BUG-01 | [Mô tả] | Cao / Trung bình / Thấp | Đã fix / Chưa fix | [Mô tả cách fix] |
| BUG-02 | [Mô tả] | Cao / Trung bình / Thấp | Đã fix / Chưa fix | [Mô tả cách fix] |

### 9.3 Kiểm thử người dùng (User Testing) *(nếu có)*
> *[MSSV – Họ và Tên: Tác giả / Người review]*

[Mô tả quá trình user testing, số lượng người tham gia, phương pháp, kết quả thu được...]

### 9.4 Cải tiến sau kiểm thử
> *[MSSV – Họ và Tên: Tác giả / Người review]*

[Những cải tiến được thực hiện dựa trên kết quả kiểm thử...]

---

## 10. Demo

> *[MSSV – Họ và Tên: Tác giả / Người review]*

### 10.1 Link Demo

| Loại | Link |
|------|------|
| 🎥 **Video Demo (YouTube)** | [https://youtube.com/...] |
| 🌐 **Website (nếu có)** | [https://...] |
| 💻 **Source Code** | [https://github.com/...] |

### 10.2 Ảnh chụp màn hình giao diện

**Màn hình 1: [Tên màn hình]**

> [Mô tả ngắn về màn hình này]

```
[Chèn ảnh chụp màn hình tại đây]
![Tên màn hình](./images/screenshot1.png)
```

**Màn hình 2: [Tên màn hình]**

> [Mô tả ngắn về màn hình này]

```
[Chèn ảnh chụp màn hình tại đây]
![Tên màn hình](./images/screenshot2.png)
```

**Màn hình 3: [Tên màn hình]**

> [Mô tả ngắn về màn hình này]

```
[Chèn ảnh chụp màn hình tại đây]
![Tên màn hình](./images/screenshot3.png)
```

---

## 11. Triển khai (Deployment)

> *[MSSV – Họ và Tên: Tác giả / Người review]*

### 11.1 Môi trường triển khai

| Thành phần | Chi tiết |
|-----------|---------|
| **Nền tảng** | [AWS / GCP / Heroku / VPS / ...] |
| **URL** | [https://...] |
| **Hệ điều hành** | [Ubuntu 22.04 / ...] |
| **Phiên bản Runtime** | [Node.js 18 / Python 3.10 / ...] |

### 11.2 Hướng dẫn triển khai

> *[MSSV – Họ và Tên: Tác giả / Người review]*

```bash
# Ví dụ các bước triển khai
git clone https://github.com/your-repo
cd your-project
npm install
npm run build
npm start
```

[Mô tả chi tiết các bước cấu hình và triển khai...]

---

## 12. Nhật ký làm việc

### 12.1 Kế hoạch làm việc (Plan)
> *[24120344 – Hoàng Trần Minh Khoa: Tác giả / Người review]*

| Tuần | Mốc thời gian | Công việc theo kế hoạch | Thành viên phụ trách |
|------|--------------|------------------------|---------------------|
| 1 | 01/03 – 07/03 | Problem Analysis, xác định Input/Output | Đinh Công Khang, Đặng Hồng Minh |
| 2 | 08/03 – 14/03 | Decomposition, rã hệ thống thành 4 module | Nguyễn Ngọc Phúc, Trần Lê Đức Việt |
| 3 | 15/03 – 21/03 | Nhận diện mẫu, Trừu tượng hóa & System Design | Đinh Công Khang, Hoàng Trần Minh Khoa |
| 4 | 22/03 – 28/03 | Implementation & Testing, tích hợp Duplicate Detection | Cả nhóm |

### 12.2 Công việc thực tế (Actual)
> *[24120344 – Hoàng Trần Minh Khoa: Tác giả / Người review]*

| Tuần | Khoảng thời gian | Công việc thực tế đã thực hiện | Thành viên thực hiện |
|------|-----------------|-------------------------------|---------------------|
| 1 | 01/03 – 07/03 | Cập nhật Problem Analysis, bỏ OCR theo hướng v2 | Đinh Công Khang |
| 2 | 08/03 – 14/03 | Xây dựng logic cho Module Recommendation & Vector DB | Đặng Hồng Minh, Nguyễn Ngọc Phúc |
| 3 | 15/03 – 21/03 | Chạy thử nghiệm AI Assistant RAG, Prompt Engineering | Trần Lê Đức Việt |
| 4 | 22/03 – 28/03 | Unit Test, viết báo cáo cuối kỳ, chuẩn bị Slide Demo | Hoàng Trần Minh Khoa, Cả nhóm |

### 12.3 Phân bổ khối lượng công việc
> *[24120344 – Hoàng Trần Minh Khoa: Tác giả / Người review]*

| MSSV | Họ và Tên | % Khối lượng công việc | Số giờ làm việc |
|------|-----------|----------------------|----------------|
| 24120332 | Đinh Công Khang | 20% | 40 giờ |
| 24120090 | Đặng Hồng Minh | 20% | 38 giờ |
| 24120215 | Nguyễn Ngọc Phúc | 20% | 38 giờ |
| 24120245 | Trần Lê Đức Việt | 20% | 40 giờ |
| 24120344 | Hoàng Trần Minh Khoa | 20% | 35 giờ |
| **Tổng** | | **100%** | **191 giờ** |

### 12.4 Công cụ sử dụng
> *[24120344 – Hoàng Trần Minh Khoa: Tác giả / Người review]*

| Mục đích | Công cụ |
|---------|---------|
| **Giao tiếp nhóm** | Zalo, Google Meet |
| **Quản lý dự án** | Trello |
| **Quản lý mã nguồn** | GitHub |
| **Quản lý tài liệu** | Google Drive, Notion |
| **Thiết kế System** | Draw.io, C4 Model |

### 12.5 Ảnh chụp màn hình công việc được phân công

> *[24120344 – Hoàng Trần Minh Khoa: Tác giả / Người review]*

*(Nhóm sẽ chèn ảnh screenshot từ Trello / Github vào đây sau)*

---

## 13. Khai báo sử dụng AI

> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

### 13.1 Danh sách công cụ AI đã sử dụng

| Công cụ AI | Mục đích sử dụng | Phần của dự án |
|-----------|-----------------|---------------|
| Claude / GPT-4o | Tạo file template báo cáo | Report của dự án |
| GitHub Copilot | Hỗ trợ code boilerplate cho các thuật toán | Phần Implementation của Recommendation Engine |

### 13.2 Chi tiết sử dụng AI

**Sử dụng 1: Claude – Tạo file template từ hướng dẫn**

- **Prompt đã sử dụng:** "Dựa vào các yêu cầu trong file hướng dẫn. Hãy giúp tôi tạo 1 file template báo cáo theo mẫu cho môn Tư duy tính toán. Yêu cầu xuất ra file template mẫu dưới định dạng markdown."
- **Kết quả nhận được:** File template kết quả đã tạo đầy đủ các cấu trúc theo file hướng dẫn.
- **Cách nhóm sử dụng kết quả:** Nhóm sử dụng cấu trúc markdown do AI tạo ra để điền nội dung thực tế của dự án Smart Shopping System vào, đảm bảo tuân thủ đúng yêu cầu định dạng của giảng viên.

### 13.3 Tuyên bố

> Nhóm xác nhận rằng toàn bộ nội dung được tạo ra bởi AI đã được kiểm tra, chỉnh sửa và chịu trách nhiệm bởi các thành viên trong nhóm. Nhóm hiểu và tuân thủ các quy định về sử dụng AI trong học thuật của nhà trường.

---

## 14. Kết luận và Hướng phát triển

### 14.1 Những gì đã thực hiện thành công
> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

- Đơn giản hóa thành công hệ thống từ 6 module (v1) xuống còn 4 module lõi (v2) hoạt động ổn định.
- Tích hợp thành công thuật toán **Duplicate Detection**, cảnh báo chính xác khi người dùng có ý định mua trùng sản phẩm đã có trong Purchase History.
- Trợ lý AI có khả năng nhận diện ý định và truy xuất được "ý nghĩa văn hóa" của các món quà lưu niệm.

### 14.2 Bài học kinh nghiệm
> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

**Về tư duy tính toán:**
- Nhóm học được cách không nên ôm đồm quá nhiều tính năng phức tạp (như OCR quét hóa đơn). Thay vào đó, việc Abstraction (lược bỏ cái không cần thiết) và tập trung vào các luồng tính năng thực dụng (ghi nhận bằng tay + Duplicate Detection) mang lại hiệu quả cao hơn nhiều cho bản mô phỏng.

**Về làm việc nhóm:**
- Phân chia module rõ ràng theo nguyên lý Decomposition giúp các thành viên code độc lập mà không bị conflict.

### 14.3 Hướng phát triển trong tương lai
> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

| Hướng phát triển | Mô tả | Độ ưu tiên |
|-----------------|-------|-----------|
| **Phát triển lại OCR Scanner** | Tích hợp lại mô hình tự động đọc hóa đơn khi tài nguyên server cho phép | Trung bình |
| **Mở rộng Vector Database** | Thêm data chi tiết về đặc sản của nhiều vùng miền Việt Nam hơn | Cao |
| **Gợi ý kết hợp (Combo)** | Đề xuất các combo sản phẩm mua chung (ví dụ: mua cafe thì gợi ý mua thêm phin pha) | Trung bình |

### 14.4 Góp ý cho Giảng viên, Trợ giảng và Môn học
> *[24120332 – Đinh Công Khang: Tác giả / Người review]*

**Đối với Giảng viên và Trợ giảng:**
- Cảm ơn các Thầy và Trợ giảng đã tư vấn để nhóm mạnh dạn loại bỏ các phần rườm rà (tối ưu đường đi, ngân sách) ở bản cập nhật v2, giúp đồ án trở nên khả thi và bám sát vào tính ứng dụng cốt lõi hơn.

---

*— Hết báo cáo —*

*Cập nhật lần cuối: 22/04/2026 09:00*