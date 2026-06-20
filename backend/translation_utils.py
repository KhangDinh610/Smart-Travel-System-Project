import re

# Dictionary of common terms for Vietnamese ceramics and souvenirs
VN_EN_MAP = {
    r"bộ ấm chén": "Tea Set",
    r"ấm chén": "Tea Set",
    r"bộ ấm trà": "Tea Set",
    r"ấm trà": "Teapot",
    r"chén": "Cup",
    r"tách": "Cup",
    r"ly sứ": "Ceramic Mug",
    r"cốc": "Mug",
    r"bình hoa": "Flower Vase",
    r"lọ hoa": "Vase",
    r"lục bình": "Decorative Vase",
    r"tranh": "Painting",
    r"tượng": "Statue",
    r"đèn": "Lamp",
    r"đĩa": "Plate",
    r"bát": "Bowl",
    r"chén đĩa": "Tableware Set",
    r"quà tặng": "Gift Set",
    r"gốm sứ": "Ceramic",
    r"gốm": "Pottery",
    r"sứ": "Porcelain",
    r"bát tràng": "Bat Trang",
    r"cao cấp": "Premium",
    r"đẹp": "Elegant",
    r"in logo": "Logo Printed",
    r"vẽ tay": "Hand-painted",
    r"men rạn": "Crackle Glaze",
    r"men hỏa biến": "Flambé Glaze",
    r"khảm": "Inlaid",
    r"đắp nổi": "Embossed",
    r"hoa sen": "Lotus",
    r"thuận buồm xuôi gió": "Smooth Sailing",
    r"tài lộc": "Wealth & Luck",
    r"tứ quý": "Four Seasons",
}

def smart_translate_name(vn_name: str) -> str:
    """
    Generate a decent English name for a product based on Vietnamese keywords.
    Useful as a fast fallback when AI translation is unavailable.
    """
    name_lower = vn_name.lower()
    found_terms = []
    
    # Extract known terms
    for vn_regex, en_term in VN_EN_MAP.items():
        if re.search(vn_regex, name_lower):
            if en_term not in found_terms:
                found_terms.append(en_term)
    
    if not found_terms:
        return vn_name # Final fallback
        
    # Categorize matches
    materials = [t for t in found_terms if t in ["Ceramic", "Porcelain", "Pottery"]]
    core_products = [t for t in found_terms if t in ["Tea Set", "Teapot", "Vase", "Mug", "Cup", "Painting", "Statue", "Lamp", "Tableware Set", "Bowl", "Plate"]]
    others = [t for t in found_terms if t not in materials and t not in core_products]
    
    parts = []
    
    # Premium / Bat Trang
    if "Premium" in others:
        parts.append("Premium")
        others.remove("Premium")
    if "Bat Trang" in others:
        parts.append("Bat Trang")
        others.remove("Bat Trang")
        
    # Materials
    if materials:
        parts.append("/".join(materials))
        
    # Products
    if core_products:
        parts.append("/".join(core_products))
        
    # Others (like Logo Printed)
    if others:
        # Filter out style markers we append at the end
        style_markers = ["Lotus", "Hand-painted", "Crackle Glaze", "Flambé Glaze"]
        details = [o for o in others if o not in style_markers]
        if details:
            parts.append(f"({', '.join(details)})")
            
    # Add Styles/Themes at the end
    styles = []
    if "Lotus" in found_terms: styles.append("Lotus Design")
    if "Hand-painted" in found_terms: styles.append("Hand-painted")
    if "Crackle Glaze" in found_terms: styles.append("Crackle Glaze")
    if "Flambé Glaze" in found_terms: styles.append("Flambé Glaze")
    
    if styles:
        parts.append(f"- {' & '.join(styles)}")
        
    result = " ".join(parts)
    return result if result else vn_name
