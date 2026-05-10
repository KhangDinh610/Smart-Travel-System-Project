import os
import streamlit as st
import api_client

# Cấu hình giao diện
st.set_page_config(page_title="Smart Shopping - Duplicate Detection", page_icon="🛍️", layout="centered")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "key2")
REDIRECT_URI = "http://localhost:8501"

if "token" not in st.session_state:
    st.session_state.token = None

def main():
    st.title("🛍️ Smart Shopping System")
    st.subheader("Tính năng: Cảnh báo trùng lặp (Duplicate Detection)")
    
    # OAuth handling
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        st.query_params.clear()
        with st.spinner("Đang xác thực với Google..."):
            data, error = api_client.login_google(code, REDIRECT_URI)
            if error:
                st.error(f"Đăng nhập Google thất bại: {error}")
            else:
                st.session_state.token = data.get("idToken")
                st.rerun()

    if st.session_state.token is None:
        show_auth_page()
    else:
        show_main_page()

def show_auth_page():
    tab1, tab2 = st.tabs(["🔒 Đăng nhập", "✍️ Đăng ký"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Mật khẩu", type="password", key="login_pass")
        if st.button("Đăng nhập", type="primary"):
            data, error = api_client.login(email, password)
            if error: st.error(error)
            else:
                st.session_state.token = data.get("idToken")
                st.rerun()
        
        st.divider()
        google_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&response_type=code&scope=openid%20email%20profile&redirect_uri={REDIRECT_URI}"
        st.markdown(f'<a href="{google_url}" target="_self">Đăng nhập bằng Google</a>', unsafe_allow_html=True)

    with tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
        if st.button("Đăng ký"):
            data, error = api_client.register(reg_email, reg_pass)
            if error: st.error(error)
            else: st.success("Đăng ký thành công! Hãy đăng nhập.")

def logout():
    st.session_state.token = None
    st.rerun()

def show_main_page():
    st.sidebar.button("Đăng xuất", on_click=logout)
    
    st.markdown("### Kiểm tra sản phẩm mới")
    with st.form("check_form"):
        prod_name = st.text_input("Tên sản phẩm (*)")
        prod_desc = st.text_area("Mô tả sản phẩm")
        submitted = st.form_submit_button("Kiểm tra trùng lặp", type="primary")
        
        if submitted:
            if not prod_name:
                st.warning("Vui lòng nhập tên sản phẩm.")
            else:
                with st.spinner("Đang phân tích similarity..."):
                    result, error = api_client.check_duplicate(st.session_state.token, prod_name, prod_desc)
                    if error:
                        st.error(error)
                    else:
                        if result["is_duplicate"]:
                            st.warning(result["message"])
                            matched = result['matched_item']
                            st.info(f"Sản phẩm khớp nhất: {matched['text']} (Trùng lặp: {matched['match_type']} - Lexical: {matched['lexical_score']:.2f}, Semantic: {matched['semantic_score']:.2f})")
                        else:
                            st.success(result["message"])
                            st.session_state["last_checked"] = {"name": prod_name, "desc": prod_desc}

    if "last_checked" in st.session_state:
        st.divider()
        st.write(f"Bạn có muốn thêm **{st.session_state['last_checked']['name']}** vào danh sách?")
        if st.button("Xác nhận thêm sản phẩm"):
            data, error = api_client.add_product(
                st.session_state.token, 
                st.session_state["last_checked"]["name"], 
                st.session_state["last_checked"]["desc"]
            )
            if error: st.error(error)
            else:
                st.success("Đã thêm sản phẩm thành công!")
                del st.session_state["last_checked"]

if __name__ == "__main__":
    main()
