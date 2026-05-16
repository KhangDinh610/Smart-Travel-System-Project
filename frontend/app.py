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
    
    # Navigation menu as framed buttons
    st.sidebar.markdown("### Điều hướng")
    
    menu_items = {
        "Bản đồ (Map)": {"icon": "🗺️", "title": "Bản đồ (Map)", "view": render_map_view},
        "Trợ lý AI (Chatbot)": {"icon": "💬", "title": "Trợ lý AI (Chatbot)", "view": render_chatbot_view},
        "Quét Ảnh (Camera)": {"icon": "📸", "title": "Quét Ảnh (Camera)", "view": render_camera_view},
        "Ghi chép Mua sắm (Log)": {"icon": "📝", "title": "Ghi chép Mua sắm (Log)", "view": render_purchase_view}
    }
    
    if "current_page" not in st.session_state or st.session_state.current_page not in menu_items:
        st.session_state.current_page = "Bản đồ (Map)"
        
    for key, data in menu_items.items():
        is_active = (st.session_state.current_page == key)
        label = f"{data['icon']} {data['title']}"
        if st.sidebar.button(label, use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.current_page = key
            st.rerun()

    choice = st.session_state.current_page
    menu_items[choice]["view"]()

if __name__ == '__main__':
    main()
