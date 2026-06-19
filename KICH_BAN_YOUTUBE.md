# Kịch bản Phân cảnh Thực tế (Shooting Script): BuyAI - Smart Shopping Assistant

**Dự án:** BuyAI (Smart Travel System)
**Người trình bày:** Sinh viên Công nghệ (Dev)
**Phong cách:** Tự tin, lưu loát, chuyên môn cao, đi thẳng vào vấn đề.

---

## SCENE 1: Mở đầu & Đặt vấn đề (Hook)

*   **Góc máy & Hành động (Visual/Action):**
    *   **A-roll (Quay mặt):** Cảnh quay bán thân người trình bày, ngồi trước background gọn gàng (có thể là màn hình máy tính phía sau). 
    *   Sau khoảng 10 giây, chuyển sang slide ngắn hoặc một video tư liệu cảnh khách du lịch lúng túng trong chợ.
    *   Chuyển tiếp (Transition) hiển thị to Logo **Tên dự án** ở giữa màn hình.

*   **Lời thoại (Voiceover):**
    "Chào thầy và các bạn. Chắc hẳn ai trong chúng ta khi đi du lịch nước ngoài hay đến một vùng miền lạ cũng từng gặp tình huống này: Mình nhìn thấy một món đồ thủ công mỹ nghệ rất đẹp, nhưng lại không biết tên nó là gì, ý nghĩa văn hóa đằng sau ra sao. Và thực tế nhất là... rào cản ngôn ngữ khiến mình rất ngại giao tiếp để hỏi giá.
    Để giải quyết 'nỗi đau' đó của khách du lịch, nhóm chúng em đã xây dựng **Tên dự án** - một Trợ lý mua sắm thông minh. Thay vì phải lên Google gõ tìm kiếm vô vọng, BuyAI cho phép du khách tìm ngay bằng hình ảnh và trò chuyện với trợ lý AI hiểu rõ cặn kẽ về các đặc sản bản địa."


---

## SCENE 2: Trình diễn Giao diện & Đăng nhập (UI/UX Showcase)

*   **Góc máy & Hành động (Visual/Action):**
    *   **B-roll (Quay màn hình ứng dụng):** Hiển thị màn hình Login trên trình duyệt.
    *   Chuột (Mouse cursor) di chuyển mượt mà, bấm vào nút "Sign in with Google hoặc tự tạo tài khoản".
    *   Quá trình đăng nhập tự động chạy qua, màn hình chuyển sang Trang chủ (Home) của app.
    *   Chuột bấm thử nút đổi Dark mode/Light mode để biểu diễn.

*   **Lời thoại (Voiceover):**
    "Nói qua một chút về kiến trúc Frontend. Nhóm em ưu tiên trải nghiệm người dùng nên đã sử dụng React kết hợp với TailwindCSS, giúp giao diện mượt mà và chuẩn responsive như một app di động thực thụ. 
    Như mọi người đang thấy, đây là màn hình đăng nhập. Nhóm đã tích hợp trực tiếp **Firebase Authentication** vào luồng hệ thống. Chỉ với một thao tác click, người dùng đã có thể login bằng Google cực kỳ bảo mật và tiện lợi. Giao diện cũng được trang bị đầy đủ chế độ Light/Dark mode."

---

## SCENE 3: Demo Tính năng Tìm kiếm (Semantic Search & Visual Search)

*   **Góc máy & Hành động (Visual/Action):**
    *   **B-roll (Quay màn hình ứng dụng):** Vẫn ở màn hình Home.
    *   Chuột click vào ô Search Bar. Người dùng gõ chậm rãi từ khóa tiếng Anh: *"Vietnamese traditional conical hat"*. Bấm Enter. Màn hình load 1 giây rồi hiện ra kết quả là "Nón lá" (tiếng Việt).
    *   Chuột bấm vào icon Camera trên thanh tìm kiếm. Bảng upload hiện ra.
    *   Người dùng chọn upload một file ảnh (ví dụ: ảnh chiếc bình gốm sứ hoa văn). 
    *   Màn hình có skeleton loading khoảng 1-2 giây rồi trả về danh sách các sản phẩm gốm tương tự.

*   **Lời thoại (Voiceover):**
    "Bây giờ em sẽ demo tính năng lõi của hệ thống. Đầu tiên là Semantic Search - tìm kiếm theo ngữ nghĩa. Giả sử em là một khách Mỹ, gõ vào từ khóa tiếng Anh là *'Vietnamese traditional conical hat'*. Hệ thống Backend được kết hợp với Vector Database là **ChromaDB** sẽ tự động hiểu ngữ nghĩa và trả về ngay kết quả chính xác là 'Nón lá' cùng các thông tin tiếng Việt.
    Nhưng tính năng 'ăn tiền' nhất phải là **Visual Search**. Em sẽ bấm vào icon Camera và upload một bức ảnh bình gốm mà em vô tình chụp được ở chợ. Hệ thống phân tích cực nhanh và ngay lập tức lọc ra các sản phẩm có hoa văn, kiểu dáng tương đương đang được bày bán xung quanh."


---

## SCENE 4: Trợ lý Ảo (AI Chatbot)

*   **Góc máy & Hành động (Visual/Action):**
    *   **B-roll (Quay màn hình ứng dụng):** Từ kết quả tìm kiếm gốm sứ ở Scene 3, bấm vào một sản phẩm cụ thể.
    *   Bấm mở cửa sổ Chatbot. 
    *   Gõ vào đoạn chat: *"Món đồ gốm này có ý nghĩa gì trong văn hóa Việt Nam?"*
    *   Bot sinh ra text trả lời dần dần (typing effect).

*   **Lời thoại (Voiceover):**
    "Khi đã tìm thấy món đồ, nếu du khách muốn biết thêm thông tin thì sao? Họ chỉ cần mở Chatbot lên. Ví dụ em hỏi: *'Món đồ gốm này có ý nghĩa gì?'*.
    Trợ lý ảo này được 'bơm' sức mạnh bởi model **Gemini 1.5 Flash**. Thay vì trả lời chung chung, nó được cung cấp context (ngữ cảnh) của chính món đồ chúng ta đang xem để đưa ra lời tư vấn cực kỳ sát với thực tế, giống như một hướng dẫn viên du lịch vậy."



---

## SCENE 5: Điểm nhấn Kỹ thuật số 1 (Visual Search Optimization)

*   **Góc máy & Hành động (Visual/Action):**
    *   **B-roll (Quay màn hình IDE - VS Code):** Chuyển cảnh sang màn hình code đang mở giao diện tối.
    *   Bên cây thư mục (Explorer) bên trái, mở rộng thư mục `backend`, click đúp mở file `visual_search.py`.
    *   Dùng chuột bôi đen (highlight) nguyên hàm **`def preprocess_image(self, image: Image.Image):`** (từ dòng `removed = remove(image)` đến lúc convert sang RGB).

*   **Lời thoại (Voiceover):**
    "Để đạt được độ mượt mà và chính xác như demo, có hai điểm tối ưu trong Backend mà nhóm em rất tự hào.
    Thứ nhất là ở luồng xử lý ảnh Visual Search. Thầy cô có thể thấy trên màn hình là file **`visual_search.py`**. Thay vì đưa thẳng ảnh thô do người dùng chụp vào model AI, bên em đã xây dựng hàm **`preprocess_image`**. Trong này, nhóm dùng thư viện `rembg` để tự động bóc tách background lộn xộn, chuyển nó thành nền trong suốt, sau đó đắp thêm một lớp nền trắng tinh trước khi đưa vào model CLIP của OpenAI để trích xuất vector. Kỹ thuật tiền xử lý này giúp độ chính xác của vector sinh ra tăng lên đột biến."



---

## SCENE 6: Điểm nhấn Kỹ thuật số 2 (Rate Limit Handling)

*   **Góc máy & Hành động (Visual/Action):**
    *   **B-roll (Quay màn hình IDE - VS Code):** Click sang tab file `ai_service.py` đã mở sẵn.
    *   Kéo cuộn trang (scroll) xuống hàm **`async def _generate_with_retry`**.
    *   Dùng chuột bôi đen đoạn `try... except` và dòng `await asyncio.sleep(wait_time)` bên trong block bắt lỗi 503.

*   **Lời thoại (Voiceover):**
    "Điểm tối ưu kỹ thuật thứ hai nằm ở file **`ai_service.py`**. Khi dùng LLM qua API như Gemini, app rất dễ bị crash nếu gặp lỗi Rate Limit (429) hoặc Server Overloaded (503). 
    Để giải quyết triệt để, nhóm em không gọi API chay mà thiết kế hàm **`_generate_with_retry`** áp dụng thuật toán **Exponential Backoff Retry**. Thầy cô có thể thấy ở đoạn code này, khi bắt được lỗi 503, hệ thống sẽ không ném lỗi ra ngoài mà tự động ép server `asyncio.sleep()` một khoảng thời gian chờ được nhân đôi lên sau mỗi lần thử thất bại. Nhờ cơ chế bất đồng bộ (async), server vẫn nhận request khác bình thường mà luồng AI không bao giờ bị sập, đảm bảo tính High Availability (tính sẵn sàng cao) cho ứng dụng."



---

## SCENE 7: Tổng kết & Hướng đi (Conclusion)

*   **Góc máy & Hành động (Visual/Action):**
    *   **A-roll (Quay mặt):** Chuyển lại cảnh quay người trình bày.
    *   Mỉm cười thân thiện.
    *   Cuối cùng chuyển sang một Slide chứa thông tin "Thanks for watching" kèm tên các thành viên.

*   **Lời thoại (Voiceover):**
    "Như vậy, **Tên dự án** không chỉ dừng lại ở một ứng dụng quản lý dữ liệu thông thường, mà nó đã tích hợp khép kín một luồng công nghệ từ Vector Database cho đến LLM Multimodal.
    Trong phase tiếp theo, nhóm em định hướng sẽ tích hợp thêm AR để du khách có thể 'ướm thử' sản phẩm trong không gian thực và đính kèm bản đồ Google Maps dẫn đường trực tiếp tới các cửa hàng.
    Đó là toàn bộ phần trình bày đồ án của nhóm. Em xin cảm ơn thầy cô và các bạn đã lắng nghe. Nhóm em rất mong nhận được những câu hỏi và góp ý từ hội đồng ạ."


