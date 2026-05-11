import os
import streamlit as st
import api_client

# Cấu hình giao diện
st.set_page_config(page_title="Smart Shopping - Duplicate Detection", page_icon="🛍️", layout="centered")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "key2")
REDIRECT_URI = "http://localhost:8501"

if "token" not in st.session_state:
    st.session_state.token = None

def _get_query_params():
    if hasattr(st, "query_params"):
        return st.query_params
    if hasattr(st, "experimental_get_query_params"):
        return st.experimental_get_query_params()
    return {}


def _clear_query_params():
    if hasattr(st, "query_params"):
        st.query_params.clear()
    elif hasattr(st, "experimental_set_query_params"):
        st.experimental_set_query_params(**{})


def main():
    st.title("🛍️ Smart Shopping System")
    st.subheader("Tính năng: Cảnh báo trùng lặp (Duplicate Detection)")
    
    # OAuth handling
    query_params = _get_query_params()
    if "code" in query_params:
        code_value = query_params.get("code")
        code = code_value[0] if isinstance(code_value, list) and code_value else code_value
        _clear_query_params()
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
            if error:
                st.error(error)
            else:
                token = data.get("idToken") if isinstance(data, dict) else None
                if token:
                    st.session_state.token = token
                    st.success("Đăng ký thành công và bạn đã được đăng nhập tự động.")
                    st.experimental_rerun()
                else:
                    st.success("Đăng ký thành công! Hãy đăng nhập.")
                    warning = data.get("warning") if isinstance(data, dict) else None
                    if warning:
                        st.warning(warning)

def logout():
    st.session_state.token = None
    st.rerun()

def show_main_page():
    st.sidebar.button("Đăng xuất", on_click=logout)

    tab_duplicate, tab_chatbot, tab_recommend = st.tabs(["🔍 Duplicate Detection", "🤖 NLP Chatbot", "⭐ Recommendation"])

    with tab_duplicate:
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
                if error:
                    st.error(error)
                else:
                    st.success("Đã thêm sản phẩm thành công!")
                    del st.session_state["last_checked"]

    with tab_chatbot:
        st.markdown("### Chatbot tư vấn mua sắm (RAG)")
        query = st.text_area("Hỏi trợ lý mua sắm của bạn", height=120)
        if st.button("Gửi câu hỏi cho Chatbot"):
            if not query.strip():
                st.warning("Vui lòng nhập câu hỏi hoặc yêu cầu.")
            else:
                with st.spinner("Đang tìm dữ liệu liên quan và tạo câu trả lời..."):
                    result, error = api_client.chatbot_ask(st.session_state.token, query)
                    if error:
                        st.error(error)
                    else:
                        st.success("Chatbot đã có câu trả lời:")
                        st.write(result.get("answer", "Không có câu trả lời."))
                        docs = result.get("retrieved_context", [])
                        if docs:
                            st.markdown("**Thông tin tham chiếu:**")
                            for doc in docs:
                                st.info(f"{doc['title']} (Loại: {doc['type']}, Độ phù hợp: {doc['score']:.2f})\n{doc['text']}")

    with tab_recommend:
        st.markdown("### Recommendation Engine")
        preference = st.text_input("Yêu cầu / Sở thích của bạn", value="Quà tặng giá thấp, đặc sản Việt Nam")
        budget = st.number_input("Ngân sách dự kiến (VND)", min_value=0, value=100000, step=10000)
        location_lat = st.number_input("Vĩ độ (latitude)", value=10.772, format="%.6f")
        location_lon = st.number_input("Kinh độ (longitude)", value=106.698, format="%.6f")
        top_k = st.slider("Số gợi ý", min_value=1, max_value=10, value=5)
        if st.button("Tìm gợi ý phù hợp"):
            with st.spinner("Đang tính toán gợi ý..."):
                result, error = api_client.get_recommendations(
                    st.session_state.token,
                    preference=preference,
                    budget=budget,
                    location_lat=location_lat,
                    location_lon=location_lon,
                    top_k=top_k
                )
                if error:
                    st.error(error)
                else:
                    recs = result.get("recommendations", [])
                    if not recs:
                        st.warning("Không tìm thấy gợi ý nào. Hãy thử điều chỉnh yêu cầu hoặc ngân sách.")
                    else:
                        for item in recs:
                            st.markdown(f"**{item['name']}** — {item['shop_name']} ({item['price']:,} VND, rating {item['rating']})")
                            st.caption(f"Score tổng: {item['score']:.4f} | Semantic: {item['semantic_score']:.4f} | Tag: {item['tag_score']:.4f} | Novelty: {item['novelty_score']:.4f} | Proximity: {item['proximity_score']:.4f} | Budget: {item['budget_score']:.4f}")
                            st.write(item['description'])
                            st.divider()

if __name__ == "__main__":
    main()
