import streamlit as st
import requests
import io
from PIL import Image
from views.map_view import render_map_view

# Cấu hình trang
st.set_page_config(
    page_title="Smart Shopping System",
    page_icon="🛍️",
    layout="wide",
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

def login_section():
    st.sidebar.title("🔐 Xác thực")
    if not st.session_state['auth']['is_logged_in']:
        auth_mode = st.sidebar.radio("Chế độ", ["Đăng nhập", "Đăng ký"])
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Mật khẩu", type="password")
        
        if auth_mode == "Đăng nhập":
            if st.sidebar.button("Đăng nhập"):
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
                        st.sidebar.success(f"Chào mừng, {email}!")
                        st.rerun()
                    else:
                        st.sidebar.error(f"Sai email hoặc mật khẩu: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.sidebar.error(f"Không thể kết nối Backend: {e}")
        else:
            if st.sidebar.button("Đăng ký"):
                try:
                    res = requests.post(f"{API_BASE_URL}/register", json={"email": email, "password": password})
                    if res.status_code == 200:
                        st.sidebar.success("Đăng ký thành công! Hãy đăng nhập.")
                    else:
                        st.sidebar.error("Lỗi đăng ký: " + res.json().get('detail', ''))
                except Exception as e:
                    st.sidebar.error(f"Không thể kết nối Backend: {e}")
    else:
        st.sidebar.write(f"👤 Đang đăng nhập: **{st.session_state['auth']['user_id']}**")
        if st.sidebar.button("Đăng xuất"):
            st.session_state['auth'] = {"is_logged_in": False, "user_id": None, "token": None}
            st.rerun()

def main():
    login_section()
    
    st.sidebar.markdown("---")
    menu = ["📍 Bản đồ", "💬 Chatbot", "📝 Ghi nhận mua sắm", "🔍 Tìm kiếm thông minh", "🛡️ Kiểm tra trùng lặp"]
    choice = st.sidebar.radio("Điều hướng", menu)
    
    st.sidebar.markdown("---")
    st.sidebar.info("Hệ thống Mua sắm Thông minh (SSS)")

    if not st.session_state['auth']['is_logged_in'] and choice != "📍 Bản đồ":
        st.warning("⚠️ Vui lòng đăng nhập để sử dụng tính năng này.")
        return

    if choice == "📍 Bản đồ":
        render_map_view()
        
    elif choice == "💬 Chatbot":
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
        tab1, tab2 = st.tabs(["Scan sản phẩm (Gemini)", "Tìm kiếm hình ảnh (CLIP)"])
        
        with tab1:
            st.subheader("Phân tích chi tiết bằng Gemini AI")
            img_file = st.file_uploader("Tải ảnh sản phẩm", type=['jpg','png'], key="gemini")
            if img_file:
                st.image(img_file, width=300)
                if st.button("Phân tích ngay"):
                    res = requests.post(f"{API_BASE_URL}/scan-product", files={"file": img_file.getvalue()})
                    st.write(res.json().get("analysis", ""))

        with tab2:
            st.subheader("Trích xuất Vector bằng CLIP Model")
            img_search = st.file_uploader("Tải ảnh để tìm sản phẩm tương đồng", type=['jpg','png'], key="clip")
            if img_search:
                st.image(img_search, width=300)
                if st.button("Trích xuất Vector"):
                    res = requests.post(f"{API_BASE_URL}/visual-search", files={"file": img_search.getvalue()})
                    data = res.json()
                    st.json(data)

    elif choice == "🛡️ Kiểm tra trùng lặp":
        st.title("🛡️ Kiểm tra trùng lặp sản phẩm")
        st.write("Sử dụng AI để phát hiện sản phẩm đã tồn tại (Semantic & Lexical).")
        
        input_text = st.text_input("Nhập tên sản phẩm cần kiểm tra", placeholder="Ví dụ: Sữa Vinamilk 180ml")
        if st.button("Kiểm tra ngay"):
            with st.spinner("Đang đối soát..."):
                res = requests.post(f"{API_BASE_URL}/detect-duplicate", params={"description": input_text})
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
