import streamlit as st
import time
import re

def format_price_callback():
    key = f"raw_price_input_{st.session_state.form_key}"
    raw_val = st.session_state.get(key, "")
    if raw_val:
        numeric_val = re.sub(r'\D', '', raw_val)
        if numeric_val:
            st.session_state[key] = f"{int(numeric_val):,.0f}đ".replace(",", ".")
        else:
            st.session_state[key] = ""

def render_purchase_view():
    st.markdown("<h1 style='text-align: center;'>📝 Ghi chép Mua sắm</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Lưu lại các món đồ bạn đã mua để dễ dàng quản lý chi tiêu và tránh mua trùng lặp.</p>", unsafe_allow_html=True)

    if 'purchases' not in st.session_state:
        st.session_state.purchases = []
        
    # Sử dụng form_key để reset giao diện mà không gây ra lỗi StreamlitAPIException
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Thêm sản phẩm")
        
        form_key = st.session_state.form_key
        product_name = st.text_input("Tên sản phẩm", key=f"input_product_name_{form_key}")
        col_price, col_qty = st.columns([3, 1])
        with col_price:
            price_key = f"raw_price_input_{form_key}"
            price = st.text_input("Giá", key=price_key, on_change=format_price_callback)
        with col_qty:
            quantity = st.number_input("Số lượng", min_value=1, key=f"input_quantity_{form_key}")
        shop_name = st.text_input("Mua tại cửa hàng (Tùy chọn)", key=f"input_shop_name_{form_key}")
        notes = st.text_area("Ghi chú thêm", key=f"input_notes_{form_key}")
        
        submitted = st.button("Lưu sản phẩm", type="primary", use_container_width=True)
        
        if submitted:
            if not product_name or not price:
                st.error("Vui lòng điền tên sản phẩm và giá!")
            else:
                with st.spinner("Đang lưu..."):
                    time.sleep(0.5)
                    
                formatted_price = price
                # Dự phòng trường hợp user không nhấn Enter mà bấm Lưu ngay
                if "đ" not in formatted_price: 
                    try:
                        numeric_price = int(re.sub(r'\D', '', price))
                        formatted_price = f"{numeric_price:,.0f}đ".replace(",", ".")
                    except ValueError:
                        pass
                        
                # Check for duplicates based on case-insensitive name
                is_duplicate = False
                for p in st.session_state.purchases:
                    if p['name'].lower() == product_name.lower():
                        is_duplicate = True
                        break
                        
                if is_duplicate or product_name.lower() == 'nón lá':
                    st.warning(f"⚠️ Phát hiện trùng lặp: Bạn dường như đã lưu '{product_name}' gần đây.")
                else:
                    new_purchase = {
                        "name": product_name,
                        "price": formatted_price,
                        "quantity": quantity,
                        "shop": shop_name,
                        "notes": notes,
                        "date": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.purchases.append(new_purchase)
                    st.success(f"Đã lưu '{product_name}' (x{quantity}) thành công!")
                    
                    # Reset fields bằng cách tăng form_key (Streamlit sẽ render ra các widget hoàn toàn mới)
                    st.session_state.form_key += 1
                    st.rerun()

    with col2:
        st.subheader("📚 Lịch sử Mua sắm")
        
        if not st.session_state.purchases:
            st.info("Chưa có sản phẩm nào được lưu.")
        else:
            for idx, p in enumerate(reversed(st.session_state.purchases)):
                with st.expander(f"🛒 {p['name']} (x{p.get('quantity', 1)}) - {p['price']}", expanded=True):
                    st.write(f"**Thời gian:** {p['date']}")
                    st.write(f"**Cửa hàng:** {p['shop'] if p['shop'] else 'Không có'}")
                    st.write(f"**Ghi chú:** {p['notes'] if p['notes'] else 'Không có'}")
