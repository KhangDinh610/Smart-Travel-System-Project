import streamlit as st
from views.map_view import render_map_view

# Cấu hình trang
st.set_page_config(
    page_title="Smart Shopping System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Quản lý State ứng dụng (App State Management)
if 'current_shop' not in st.session_state:
    st.session_state['current_shop'] = None
    
def main():
    st.sidebar.title("🛍️ Smart Shopping")
    st.sidebar.markdown("---")
    
    # Navigation menu
    menu = ["Bản đồ (Map)", "Chatbot (FE2)", "Camera Scan (FE2)"]
    choice = st.sidebar.radio("Điều hướng", menu)
    
    st.sidebar.markdown("---")
    st.sidebar.info("Vai trò FE1: Quản lý UI chính, Bản đồ, State ứng dụng.")

    if choice == "Bản đồ (Map)":
        render_map_view()
    elif choice == "Chatbot (FE2)":
        st.title("💬 Chatbot Assistant")
        st.info("Khu vực dành cho FE2 phát triển giao diện Chatbot.")
    elif choice == "Camera Scan (FE2)":
        st.title("📷 Nhận diện sản phẩm")
        st.info("Khu vực dành cho FE2 phát triển giao diện Camera/Quét ảnh.")

if __name__ == '__main__':
    main()
