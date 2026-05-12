import streamlit as st
import time

def render_chatbot_view():
    st.markdown("<h1 style='text-align: center;'>🤖 Trợ lý Mua sắm AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Hãy hỏi tôi về các sản phẩm hoặc gợi ý quà lưu niệm!</p>", unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Chào bạn! Tôi là trợ lý mua sắm AI. Tôi có thể giúp bạn tìm quà lưu niệm gì hôm nay?"}
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Nhập tin nhắn (thử hỏi về 'nón lá')..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

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
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(product_card["image"], use_container_width=True)
                with col2:
                    st.subheader(product_card["name"])
                    st.markdown(f"**Giá:** {product_card['price']}")
                    st.markdown(f"**Xuất xứ:** {product_card['origin']}")
                    st.markdown(f"**Mô tả:** {product_card['desc']}")
                    if st.button("Thêm vào Nhật ký (Log)"):
                        st.success(f"Đã thêm {product_card['name']} vào nhật ký mua sắm!")
                        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
