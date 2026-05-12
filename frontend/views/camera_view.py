import streamlit as st
import time

def render_camera_view():
    st.markdown("<h1 style='text-align: center;'>📸 Camera Scan (Nhận diện sản phẩm)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Chụp hoặc tải ảnh sản phẩm lên để hệ thống nhận diện và tìm kiếm sản phẩm tương tự.</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📷 Chụp ảnh (Camera)", "📁 Tải ảnh lên"])
    
    image_data = None
    
    with tab1:
        camera_image = st.camera_input("Sử dụng camera của bạn")
        if camera_image:
            image_data = camera_image
            
    with tab2:
        uploaded_image = st.file_uploader("Hoặc chọn ảnh từ thiết bị", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            image_data = uploaded_image

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
