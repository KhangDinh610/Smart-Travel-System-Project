import streamlit as st
import time

def render_camera_view():
    st.markdown("<h1 style='text-align: center;'>📸 Quét Ảnh (Nhận diện sản phẩm)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Kéo thả hoặc tải ảnh sản phẩm lên từ thiết bị để hệ thống nhận diện.</p>", unsafe_allow_html=True)

    image_data = st.file_uploader("Kéo thả ảnh vào đây hoặc bấm để chọn ảnh", type=["png", "jpg", "jpeg"])

    if image_data:
        st.success("Đã nhận ảnh! Đang phân tích...")
        st.image(image_data, caption="Ảnh đã tải lên", width=300)
        
        with st.spinner("Đang gửi ảnh tới AI (Mock API)..."):
            time.sleep(1.5) # Simulate processing delay
            
        st.warning("⚠️ Độ tin cậy thấp (45%). Không thể nhận diện chính xác.")
        st.markdown("### Có phải bạn đang tìm những sản phẩm này?")
        
        # Mock similar products
        similar_products = [
            {"id": 1, "name": "Nón Lá Truyền Thống", "price": "50,000 VND", "confidence": 55},
            {"id": 2, "name": "Mũ Tre", "price": "40,000 VND", "confidence": 42},
            {"id": 3, "name": "Mũ Lát Đi Biển", "price": "60,000 VND", "confidence": 38}
        ]
        
        # Display as cards
        cols = st.columns(3)
        for i, product in enumerate(similar_products):
            with cols[i]:
                st.info(f"**{product['name']}**")
                st.write(f"Giá: {product['price']}")
                st.caption(f"Độ khớp: {product['confidence']}%")
                if st.button("Xem chi tiết", key=f"btn_scan_{product['id']}"):
                    st.success("Tính năng chi tiết sẽ được phát triển sau.")

