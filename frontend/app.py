import streamlit as st
import requests
import io
from PIL import Image

# Cấu hình trang
st.set_page_config(
    page_title="Smart Shopping System",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# --- State Management ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = {"is_logged_in": False, "user_id": None, "token": None}

if 'chat_messages' not in st.session_state:
    st.session_state['chat_messages'] = []

if 'current_shop' not in st.session_state:
    st.session_state['current_shop'] = None

def login_page():
    # Sử dụng columns để căn giữa form đăng nhập
    empty_l, col, empty_r = st.columns([1, 2, 1])
    
    with col:
        st.title("🛍️ Hệ thống SSS")
        st.subheader("Vui lòng đăng nhập")
        
        tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])
        
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Mật khẩu", type="password", key="login_password")
            if st.button("Đăng nhập", use_container_width=True):
                try:
                    res = requests.post(f"{API_BASE_URL}/login", json={"email": email, "password": password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state['auth'] = {
                            "is_logged_in": True, 
                            "user_id": data['email'], 
                            "token": data['token'],
                            "uid": data['uid']
                        }
                        st.success(f"Chào mừng, {email}!")
                        st.rerun()
                    else:
                        st.error(f"Sai email hoặc mật khẩu: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Không thể kết nối Backend: {e}")
        
        with tab2:
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Mật khẩu", type="password", key="reg_password")
            if st.button("Đăng ký", use_container_width=True):
                try:
                    res = requests.post(f"{API_BASE_URL}/register", json={"email": reg_email, "password": reg_password})
                    if res.status_code == 200:
                        st.success("Đăng ký thành công! Hãy đăng nhập.")
                    else:
                        st.error("Lỗi đăng ký: " + res.json().get('detail', ''))
                except Exception as e:
                    st.error(f"Không thể kết nối Backend: {e}")

def main():
    if not st.session_state['auth']['is_logged_in']:
        login_page()
        return

    # Sidebar for Logged in users
    st.sidebar.title("🛍️ SSS Menu")
    st.sidebar.write(f"👤 **{st.session_state['auth']['user_id']}**")
    if st.sidebar.button("Đăng xuất"):
        st.session_state['auth'] = {"is_logged_in": False, "user_id": None, "token": None}
        st.rerun()
    
    st.sidebar.markdown("---")
    menu = ["💬 Chatbot", "📝 Ghi nhận mua sắm", "🔍 Tìm kiếm thông minh", "🛡️ Kiểm tra trùng lặp"]
    choice = st.sidebar.radio("Điều hướng", menu)
    
    st.sidebar.markdown("---")
    st.sidebar.write("🛠️ **Hệ thống**")
    if st.sidebar.button("Đồng bộ dữ liệu (Sync)"):
        with st.spinner("Đang đồng bộ..."):
            try:
                res = requests.post(f"{API_BASE_URL}/sync")
                if res.status_code == 200:
                    st.sidebar.success("Đồng bộ thành công!")
                else:
                    st.sidebar.error("Lỗi đồng bộ.")
            except:
                st.sidebar.error("Lỗi kết nối.")
    
    st.sidebar.markdown("---")
    st.sidebar.info("Hệ thống Mua sắm Thông minh (SSS)")

    if choice == "💬 Chatbot":
        st.title("💬 Chatbot Trợ lý Mua sắm")
        for msg in st.session_state['chat_messages']:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if prompt := st.chat_input("Nhập câu hỏi..."):
            st.session_state['chat_messages'].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Đang trả lời..."):
                    res = requests.post(f"{API_BASE_URL}/chat", json={"message": prompt, "user_id": st.session_state['auth']['user_id']})
                    if res.status_code == 200:
                        reply = res.json().get("reply", "")
                        st.markdown(reply)
                        st.session_state['chat_messages'].append({"role": "assistant", "content": reply})

    elif choice == "📝 Ghi nhận mua sắm":
        st.title("📝 Ghi nhận mua sắm")
        with st.form("history_form"):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("Tên sản phẩm")
            with col2:
                shop_id = st.number_input("Mã cửa hàng", min_value=1, value=1)
            
            if st.form_submit_button("Lưu lịch sử"):
                res = requests.post(f"{API_BASE_URL}/history", json={
                    "user_id": st.session_state['auth']['user_id'],
                    "product_id": product_name,
                    "shop_id": shop_id
                })
                if res.status_code == 200:
                    st.success("✅ Đã ghi nhận thành công!")

    elif choice == "🔍 Tìm kiếm thông minh":
        st.title("🔍 Tìm kiếm & Phân tích hình ảnh")
        
        tab_search, tab_analyze = st.tabs(["Tìm kiếm bằng ảnh", "Phân tích Gemini"])
        
        with tab_search:
            st.subheader("Tìm kiếm sản phẩm tương tự (ChromaDB)")
            search_img = st.file_uploader("Tải ảnh sản phẩm để tìm", type=['jpg','png'], key="search_img")
            if search_img:
                st.image(search_img, width=200)
                if st.button("Tìm kiếm sản phẩm"):
                    with st.spinner("Đang tìm kiếm..."):
                        res = requests.post(f"{API_BASE_URL}/visual-search", files={"file": search_img.getvalue()})
                        if res.status_code == 200:
                            products = res.json().get("products", [])
                            if products:
                                for p in products:
                                    with st.container():
                                        col_a, col_b = st.columns([3, 1])
                                        with col_a:
                                            st.write(f"**{p['name']}**")
                                            st.write(f"Giá: {p['price']:,.0f} VNĐ")
                                            st.caption(f"📍 {p['shop_name']} - {p['shop_address']}")
                                        with col_b:
                                            st.metric("Score", f"{p['score']*100:.1f}%")
                                        st.divider()
                            else:
                                st.info("Không tìm thấy sản phẩm tương ứng.")
                        else:
                            st.error("Lỗi tìm kiếm.")

        with tab_analyze:
            st.subheader("Phân tích chi tiết bằng Gemini AI")
            img_file = st.file_uploader("Tải ảnh sản phẩm để mô tả", type=['jpg','png'], key="gemini")
            if img_file:
                st.image(img_file, width=300)
                if st.button("Phân tích ngay"):
                    res = requests.post(f"{API_BASE_URL}/scan-product", files={"file": img_file.getvalue()})
                    st.write(res.json().get("analysis", ""))

    elif choice == "🛡️ Kiểm tra trùng lặp":
        st.title("🛡️ Kiểm tra trùng lặp sản phẩm")
        st.write("Sử dụng AI để phát hiện sản phẩm đã tồn tại (Semantic & Lexical).")
        
        input_text = st.text_input("Nhập tên sản phẩm cần kiểm tra", placeholder="Ví dụ: Bánh trung thu")
        if st.button("Kiểm tra ngay"):
            with st.spinner("Đang đối soát..."):
                res = requests.post(f"{API_BASE_URL}/detect-duplicate", params={
                    "description": input_text,
                    "user_id": st.session_state['auth']['user_id']
                })
                if res.status_code == 200:
                    result = res.json()
                    score = result['score']
                    if score > 0.8:
                        st.error(f"⚠️ Phát hiện trùng lặp! (Độ tin cậy: {score:.2f})")
                        st.info(f"Sản phẩm khớp: **{result['text']}** (Kiểu khớp: {result['match_type']})")
                    else:
                        st.success(f"✅ Sản phẩm mới! (Điểm tương đồng cao nhất: {score:.2f})")
                    
                    with st.expander("Xem chi tiết kỹ thuật"):
                        st.write(f"- Semantic Score: {result['semantic_score']:.4f}")
                        st.write(f"- Lexical Score: {result['lexical_score']:.4f}")

if __name__ == '__main__':
    main()
