# Kịch bản Thuyết trình Đồ án: BuyAI - Smart Shopping Assistant

**Thời lượng dự kiến:** 5 - 8 phút
**Người trình bày:** Sinh viên Công nghệ / Thành viên dự án
**Phong cách:** Tự tin, mạch lạc, nhấn mạnh vào tư duy giải quyết vấn đề.

---

## Bảng Kịch bản Chi tiết

| Thời gian (Timeline) | Hình ảnh hiển thị (Visual) | Lời thoại tiếng Việt (Voiceover) | Âm thanh (SFX/BGM) |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:15** | Quay mặt người thuyết trình (Camera chính), tươi tắn tự tin. | "Chào thầy cô và các bạn. Chắc hẳn ai trong chúng ta khi đi du lịch nước ngoài hoặc đến một vùng đất lạ cũng từng gặp phải tình huống: thấy một món đặc sản rất đẹp nhưng không biết tên nó là gì, ý nghĩa ra sao, và đặc biệt là... rào cản ngôn ngữ khiến chúng ta ngại hỏi giá." | Nhạc nền (BGM) Lofi nhẹ nhàng, tạo cảm giác hiện đại. |
| **0:15 - 1:00** | Slide ngắn hoặc màn hình chuyển sang logo **BuyAI**. | "Để giải bài toán đó, nhóm chúng mình đã xây dựng **BuyAI** - một Trợ lý mua sắm thông minh. Thay vì phải Google một cách vô vọng, BuyAI cho phép du khách tìm kiếm bằng hình ảnh và trò chuyện với một trợ lý AI hiểu rõ về các đặc sản địa phương." | Hiệu ứng chuyển cảnh (Woosh SFX). |
| **1:00 - 1:30** | Quay màn hình ứng dụng: Trang Đăng nhập và Trang chủ. Di chuột mượt mà. | "Về mặt giao diện, tụi mình sử dụng React kết hợp TailwindCSS để mang lại trải nghiệm mượt mà, chuẩn ứng dụng di động. Đây là màn hình đăng nhập, được tích hợp trực tiếp với Firebase Authentication để đảm bảo tính bảo mật và nhanh chóng. Giao diện cũng hỗ trợ Dark/Light mode đầy đủ." | SFX tiếng click chuột nhẹ khi thao tác. |
| **1:30 - 2:30** | Quay màn hình thao tác: Gõ tiếng Anh tìm kiếm món đồ, màn hình hiện kết quả tiếng Việt. | "Bây giờ mình sẽ demo tính năng Semantic Search. Giả sử mình là du khách Mỹ muốn tìm 'Vietnamese traditional conical hat', hệ thống sẽ quét trong ChromaDB và hiểu ngay ý định, trả về kết quả là 'Nón lá' cùng các thông tin bản địa." | BGM vẫn duy trì đều đặn. |
| **2:30 - 3:30** | Bấm vào icon Camera, Upload một bức ảnh (ví dụ ảnh gốm sứ/đồ thủ công). Chờ 1-2 giây rồi hiển thị kết quả. | "Tính năng ăn tiền nhất là Visual Search. Mình sẽ upload ảnh một chiếc bình gốm mình vừa chụp vội ở chợ. Mọi người có thể thấy hệ thống phản hồi rất nhanh, đưa ra các món hàng có họa tiết tương tự đang được bán tại các cửa hàng xung quanh." | SFX 'Ping' hoặc 'Success' nhẹ khi AI tìm ra kết quả. |
| **3:30 - 4:30** | Mở một sản phẩm, bấm vào màn hình Chatbot. Gõ câu hỏi: "Món này được làm từ chất liệu gì vậy?". | "Và khi du khách cần tư vấn sâu hơn, họ có thể chat trực tiếp với AI. Mình sẽ hỏi bot về chất liệu sản phẩm này. Trợ lý này được tích hợp mô hình Gemini 1.5 Flash, nó sẽ phân tích ngữ cảnh của món đồ hiện tại và trả lời một cách cực kỳ tự nhiên." | SFX gõ phím nhẹ. |
| **4:30 - 5:30** | Chuyển sang quay màn hình IDE (VS Code). Mở file **`backend/visual_search.py`**, bôi đen hàm **`preprocess_image`**. | "Để đạt được kết quả mượt mà như demo, đằng sau đó là một vài điểm tối ưu kỹ thuật mà nhóm mình rất tâm đắc. Đầu tiên là ở bài toán xử lý ảnh. Thầy cô có thể thấy trong file `visual_search.py`, ở hàm `preprocess_image`, nhóm không đẩy thẳng ảnh gốc vào model CLIP. Tụi mình dùng thư viện `rembg` để tự động tách nền ảnh thực tế, thay bằng nền trắng tĩnh. Việc này giúp trích xuất vector đặc trưng chính xác hơn rất nhiều so với để nguyên cái background lộn xộn ở chợ." | BGM nhỏ đi một chút để tập trung vào giọng giải thích kỹ thuật. |
| **5:30 - 6:30** | Chuyển sang file **`backend/ai_service.py`**, kéo xuống hàm **`_generate_with_retry`**. | "Điểm nhấn thứ hai là việc xử lý các API của bên thứ 3. Khi dùng LLM miễn phí như Gemini, ứng dụng rất dễ bị crash do dính lỗi Rate Limit - tức là lỗi 429 hoặc 503. Trong file `ai_service.py`, nhóm viết riêng một hàm `_generate_with_retry` sử dụng cơ chế **Exponential Backoff Retry**. Hệ thống tự động bắt lỗi và ép server ngủ một khoảng thời gian tăng dần theo cấp số nhân rồi mới thử lại. Nhờ vậy ứng dụng không bao giờ bị văng lỗi trực tiếp ra mặt người dùng." | Nhịp điệu nói nhanh và hào hứng hơn. |
| **6:30 - 7:30** | Quay lại màn hình ứng dụng, show một số tính năng nhỏ khác. Sau đó quay mặt người thuyết trình. | "Tóm lại, BuyAI không chỉ là một ứng dụng CRUD thông thường mà nó là một luồng tích hợp AI khép kín. Trong tương lai, nhóm dự định sẽ tích hợp thêm AR để du khách có thể 'ướm thử' sản phẩm vào không gian thực và thêm bản đồ dẫn đường tới shop." | Nhạc nền lớn dần (Crescendo). |
| **7:30 - 8:00** | Slide Thanks / Thông tin nhóm. | "Đó là toàn bộ phần demo hệ thống BuyAI. Cảm ơn thầy cô và các bạn đã theo dõi. Xin mời thầy cô đặt câu hỏi ạ." | Kết thúc nhạc. Fade out. |

---

## 📌 Ghi chú chuẩn bị trước khi quay:
1. **Chuẩn bị màn hình:** Mở sẵn tab trình duyệt chạy Frontend, VS Code mở sẵn tab file [visual_search.py](file:///Users/khoahoang/Smart-Travel-System-Project/backend/visual_search.py) và [ai_service.py](file:///Users/khoahoang/Smart-Travel-System-Project/backend/ai_service.py). Điều này giúp lúc Alt-Tab chuyển cảnh quay màn hình không bị khựng hay mất thời gian.
2. **Thao tác tay:** Lúc giải thích code (phút 4:30 - 6:30), hãy dùng con trỏ chuột bôi đen hoặc highlight đúng tên hàm `preprocess_image` và `_generate_with_retry` để điều hướng mắt của giảng viên tập trung vào chỗ bạn đang nói.
3. **Diễn tập:** Tập nói to đoạn giải thích kỹ thuật 2-3 lần trước khi bấm máy để đảm bảo phát âm mượt mà các từ khóa chuyên ngành như: *Exponential Backoff*, *Rate Limit*, *Semantic Search*, *Vector Database*.
