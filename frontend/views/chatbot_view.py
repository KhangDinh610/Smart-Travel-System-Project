import streamlit as st
import time
import json
import os
import uuid
from datetime import datetime

CHAT_SESSIONS_FILE = "chat_sessions.json"

def load_chat_sessions():
    if os.path.exists(CHAT_SESSIONS_FILE):
        try:
            with open(CHAT_SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_chat_sessions(sessions):
    try:
        with open(CHAT_SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Lỗi khi lưu lịch sử chat: {e}")

def create_new_session():
    return str(uuid.uuid4())

def get_session_title(messages):
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"]
            return title[:30] + "..." if len(title) > 30 else title
    return "Cuộc trò chuyện mới"

def render_chatbot_view():
    # CSS để tùy chỉnh giao diện
    st.markdown("""
        <style>
            /* Mở rộng tin nhắn chat */
            .stChatMessage {
                max-width: 100% !important;
            }
            /* Mở rộng khung nhập liệu chat */
            .stChatInputContainer, [data-testid="stChatInput"] {
                max-width: 100% !important;
            }
            /* Styling cho khung lịch sử */
            .history-title {
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    sessions = load_chat_sessions()

    # Khởi tạo state hiển thị panel lịch sử
    if "show_history_panel" not in st.session_state:
        st.session_state.show_history_panel = True

    # Khởi tạo ID cuộc trò chuyện hiện tại
    if "current_chat_id" not in st.session_state:
        if sessions:
            # Chọn cuộc trò chuyện gần nhất
            st.session_state.current_chat_id = list(sessions.keys())[-1]
        else:
            new_id = create_new_session()
            sessions[new_id] = {
                "title": "Cuộc trò chuyện mới",
                "timestamp": datetime.now().isoformat(),
                "messages": [
                    {"role": "assistant", "content": "Chào bạn! Tôi là trợ lý mua sắm AI. Tôi có thể giúp bạn tìm quà lưu niệm gì hôm nay?"}
                ]
            }
            save_chat_sessions(sessions)
            st.session_state.current_chat_id = new_id

    current_id = st.session_state.current_chat_id

    # Đảm bảo current_id có tồn tại
    if current_id not in sessions:
        if sessions:
            current_id = list(sessions.keys())[-1]
        else:
            current_id = create_new_session()
            sessions[current_id] = {
                "title": "Cuộc trò chuyện mới",
                "timestamp": datetime.now().isoformat(),
                "messages": [
                    {"role": "assistant", "content": "Chào bạn! Tôi là trợ lý mua sắm AI. Tôi có thể giúp bạn tìm quà lưu niệm gì hôm nay?"}
                ]
            }
            save_chat_sessions(sessions)
        st.session_state.current_chat_id = current_id

    messages = sessions[current_id]["messages"]

    # Header của chatbot
    st.markdown("<h2 style='text-align: center;'>🤖 Trợ lý Mua sắm AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Hãy hỏi tôi về các sản phẩm hoặc gợi ý quà lưu niệm!</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Nút toggle đóng/mở lịch sử dưới dấu gạch ngang
    col_toggle, _ = st.columns([2, 8])
    with col_toggle:
        btn_text = "📖 Ẩn lịch sử" if st.session_state.show_history_panel else "📖 Mở lịch sử"
        if st.button(btn_text, use_container_width=True):
            st.session_state.show_history_panel = not st.session_state.show_history_panel
            st.rerun()

    # Layout cột hoặc full width dựa vào toggle
    if st.session_state.show_history_panel:
        history_col, chat_col = st.columns([3, 7])
    else:
        history_col = None
        chat_col = st.container()

    if history_col is not None:
        with history_col:
            st.markdown("<div class='history-title'>💬 Lịch sử trò chuyện</div>", unsafe_allow_html=True)
            if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
                new_id = create_new_session()
                sessions[new_id] = {
                    "title": "Cuộc trò chuyện mới",
                    "timestamp": datetime.now().isoformat(),
                    "messages": [
                        {"role": "assistant", "content": "Chào bạn! Tôi là trợ lý mua sắm AI. Tôi có thể giúp bạn tìm quà lưu niệm gì hôm nay?"}
                    ]
                }
                save_chat_sessions(sessions)
                st.session_state.current_chat_id = new_id
                st.rerun()

            st.markdown("---")
            
            # Container cho danh sách trò chuyện
            for s_id, s_data in reversed(list(sessions.items())):
                is_current = (s_id == current_id)
                
                if st.session_state.get("renaming_session_id") == s_id:
                    new_title = st.text_input("Tên mới", value=s_data.get("title", "Cuộc trò chuyện"), key=f"rename_{s_id}")
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("Lưu", key=f"save_{s_id}", use_container_width=True):
                            sessions[s_id]["title"] = new_title
                            save_chat_sessions(sessions)
                            st.session_state.renaming_session_id = None
                            st.rerun()
                    with col_cancel:
                        if st.button("Hủy", key=f"cancel_{s_id}", use_container_width=True):
                            st.session_state.renaming_session_id = None
                            st.rerun()
                    st.markdown("---")
                else:
                    btn_label = s_data.get("title", "Cuộc trò chuyện")
                    if is_current:
                        btn_label = f"📍 {btn_label}"
                    
                    # Chia cột cho Title, Edit, Delete
                    col_name, col_edit, col_del = st.columns([6, 2, 2])
                    with col_name:
                        if st.button(btn_label, key=f"session_{s_id}", use_container_width=True):
                            st.session_state.current_chat_id = s_id
                            st.rerun()
                    with col_edit:
                        if st.button("✏️", key=f"edit_{s_id}", help="Đổi tên"):
                            st.session_state.renaming_session_id = s_id
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_{s_id}", help="Xóa"):
                            if len(sessions) > 1:
                                del sessions[s_id]
                                if current_id == s_id:
                                    st.session_state.current_chat_id = list(sessions.keys())[-1]
                            else:
                                sessions[s_id]["messages"] = [
                                    {"role": "assistant", "content": "Chào bạn! Tôi là trợ lý mua sắm AI. Tôi có thể giúp bạn tìm quà lưu niệm gì hôm nay?"}
                                ]
                                sessions[s_id]["title"] = "Cuộc trò chuyện mới"
                            save_chat_sessions(sessions)
                            st.rerun()

    with chat_col:
        # Display chat messages from history on app rerun
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Nhập tin nhắn (thử hỏi về 'nón lá')..."):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            
            # Add user message to chat history
            messages.append({"role": "user", "content": prompt})
            
            # Cập nhật tiêu đề dựa vào tin nhắn đầu tiên
            if sessions[current_id]["title"] == "Cuộc trò chuyện mới":
                sessions[current_id]["title"] = get_session_title(messages)
                
            sessions[current_id]["timestamp"] = datetime.now().isoformat()
            sessions[current_id]["messages"] = messages
            save_chat_sessions(sessions)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Mock AI response logic
                if "hat" in prompt.lower() or "nón lá" in prompt.lower():
                    response_text = "Tôi rất khuyến khích mua Nón Lá. Đây là một biểu tượng truyền thống của Việt Nam. Dưới đây là thông tin chi tiết:"
                    product_card = {
                        "name": "Nón Lá (Conical Hat)",
                        "price": "50,000 VND",
                        "origin": "Huế, Việt Nam",
                        "desc": "Biểu tượng vượt thời gian của văn hóa Việt Nam, thường được đội cùng Áo Dài.",
                        "image": "https://images.unsplash.com/photo-1582298538104-fe2e74c878f4?auto=format&fit=crop&q=80&w=400"
                    }
                else:
                    response_text = "Nghe thú vị đấy! Bạn có thể cho tôi biết thêm chi tiết về loại quà lưu niệm bạn đang tìm không?"
                    product_card = None

                # Simulate stream of response
                for chunk in response_text.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # Show product card if applicable
                if product_card:
                    st.markdown("---")
                    col_img, col_info = st.columns([1, 2])
                    with col_img:
                        st.image(product_card["image"], use_container_width=True)
                    with col_info:
                        st.subheader(product_card["name"])
                        st.markdown(f"**Giá:** {product_card['price']}")
                        st.markdown(f"**Xuất xứ:** {product_card['origin']}")
                        st.markdown(f"**Mô tả:** {product_card['desc']}")
                        if st.button("Thêm vào Nhật ký (Log)", key=f"btn_{len(messages)}"):
                            st.success(f"Đã thêm {product_card['name']} vào nhật ký mua sắm!")
                            
            # Add assistant response to chat history
            messages.append({"role": "assistant", "content": full_response})
            sessions[current_id]["messages"] = messages
            save_chat_sessions(sessions)
