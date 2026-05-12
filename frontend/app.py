import streamlit as st
from views.map_view import render_map_view
from views.chatbot_view import render_chatbot_view
from views.camera_view import render_camera_view
from views.purchase_view import render_purchase_view

# Cấu hình trang
st.set_page_config(
    page_title="Smart Shopping System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI synchronization with React (Dark Mode, layout)
st.markdown("""
<style>
    /* Điều chỉnh padding của main block */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    /* Bo góc cho iframe (nếu còn) và các container khác */
    iframe {
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    /* Tùy chỉnh sidebar */
    [data-testid="stSidebar"] {
        background-color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

# Quản lý State ứng dụng (App State Management)
if 'current_shop' not in st.session_state:
    st.session_state['current_shop'] = None
    
def main():
    st.sidebar.title("🛍️ Smart Shopping")
    st.sidebar.markdown("---")
    
    # Navigation menu
    menu = ["Bản đồ (Map)", "Trợ lý AI (Chatbot)", "Quét Ảnh (Camera)", "Ghi chép Mua sắm (Log)"]
    choice = st.sidebar.radio("Điều hướng", menu)

    if choice == "Bản đồ (Map)":
        render_map_view()
    elif choice == "Trợ lý AI (Chatbot)":
        render_chatbot_view()
    elif choice == "Quét Ảnh (Camera)":
        render_camera_view()
    elif choice == "Ghi chép Mua sắm (Log)":
        render_purchase_view()

if __name__ == '__main__':
    main()
