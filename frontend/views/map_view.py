import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

def render_map_view():
    st.title("🗺️ Bản đồ Cửa hàng & Điểm mua sắm")
    st.markdown("Hiển thị các cửa hàng và gợi ý trên bản đồ.")
    
    # Dữ liệu mẫu (Mock Data) cho các cửa hàng (Week 2 requirement)
    sample_shops = [
        {"id": 1, "name": "Chợ Bến Thành", "lat": 10.7725, "lon": 106.6980, "type": "Chợ truyền thống", "rating": 4.5},
        {"id": 2, "name": "Saigon Centre", "lat": 10.7731, "lon": 106.7008, "type": "Trung tâm thương mại", "rating": 4.8},
        {"id": 3, "name": "Vincom Đồng Khởi", "lat": 10.7779, "lon": 106.7022, "type": "Trung tâm thương mại", "rating": 4.7},
        {"id": 4, "name": "Cửa hàng lưu niệm X", "lat": 10.7750, "lon": 106.7000, "type": "Quà lưu niệm", "rating": 4.2},
    ]
    df_shops = pd.DataFrame(sample_shops)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**📍 Xác định vị trí của bạn:**")
        location = streamlit_geolocation()
        
        user_lat, user_lon = 10.775, 106.700 # Tọa độ mặc định (TP.HCM)
        
        if location and 'latitude' in location and location['latitude'] is not None:
            user_lat = location['latitude']
            user_lon = location['longitude']
            st.success("Đã lấy được vị trí hiện tại của bạn!")
            
        # Khởi tạo bản đồ Folium ở trung tâm vị trí của bạn (hoặc mặc định)
        m = folium.Map(location=[user_lat, user_lon], zoom_start=15)
        
        # Đánh dấu vị trí của người dùng
        if location and 'latitude' in location and location['latitude'] is not None:
            folium.Marker(
                [user_lat, user_lon],
                popup=folium.Popup("<b>Vị trí của bạn</b>", max_width=200),
                tooltip="Bạn đang ở đây",
                icon=folium.Icon(color="red", icon="user")
            ).add_to(m)
        
        # Thêm các Marker cửa hàng lên bản đồ
        for idx, row in df_shops.iterrows():
            # Tạo popup cho từng cửa hàng
            popup_html = f"""
            <b>{row['name']}</b><br>
            <i>{row['type']}</i><br>
            ⭐ {row['rating']}/5
            """
            folium.Marker(
                [row['lat'], row['lon']], 
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=row['name'],
                icon=folium.Icon(color="blue", icon="shopping-cart")
            ).add_to(m)
        
        # Hiển thị bản đồ trong Streamlit
        st_data = st_folium(m, width=800, height=500)
        
    with col2:
        st.subheader("📍 Chi tiết")
        # Quản lý State: Nếu người dùng click vào một marker trên bản đồ
        if st_data and st_data.get("last_object_clicked"):
            lat_clicked = st_data["last_object_clicked"]["lat"]
            lon_clicked = st_data["last_object_clicked"]["lng"]
            
            # Tìm cửa hàng tương ứng
            # Do sai số float, ta làm tròn để tìm
            clicked_shop = df_shops[
                (df_shops['lat'].round(4) == round(lat_clicked, 4)) & 
                (df_shops['lon'].round(4) == round(lon_clicked, 4))
            ]
            
            if not clicked_shop.empty:
                shop_info = clicked_shop.iloc[0]
                st.session_state['current_shop'] = shop_info.to_dict()
                
        # Hiển thị thông tin cửa hàng đang được chọn (lấy từ state)
        if st.session_state.get('current_shop'):
            shop = st.session_state['current_shop']
            st.success(f"**{shop['name']}**")
            st.write(f"**Loại:** {shop['type']}")
            st.write(f"**Đánh giá:** ⭐ {shop['rating']}")
            if st.button("Xem sản phẩm"):
                st.info(f"Đang hiển thị sản phẩm của {shop['name']} (Sẽ kết nối Backend sau)")
        else:
            st.write("Hãy nhấp vào một điểm trên bản đồ để xem chi tiết cửa hàng.")
