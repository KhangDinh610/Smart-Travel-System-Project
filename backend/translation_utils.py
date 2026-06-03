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
    
    # Check for Bat Trang specifically to put it in a good position
    is_bat_trang = "bát tràng" in name_lower
    
    # Extract known terms
    for vn_regex, en_term in VN_EN_MAP.items():
        if re.search(vn_regex, name_lower):
            if en_term not in found_terms:
                found_terms.append(en_term)
    
    if not found_terms:
        return vn_name # Final fallback
        
    # Reconstruct: [Premium] [Bat Trang] [Material] [Product] [Theme/Style]
    # This is a simple heuristic, but usually works well for product titles
    
    parts = []
    if "Premium" in found_terms: parts.append("Premium")
    if "Bat Trang" in found_terms: parts.append("Bat Trang")
    
    # Material
    if "Ceramic" in found_terms: parts.append("Ceramic")
    elif "Porcelain" in found_terms: parts.append("Porcelain")
    elif "Pottery" in found_terms: parts.append("Pottery")
    
    # Product Type (The "Core" of the name)
    core_products = ["Tea Set", "Teapot", "Vase", "Mug", "Cup", "Painting", "Statue", "Lamp", "Tableware Set", "Bowl", "Plate"]
    main_product = None
    for cp in core_products:
        if cp in found_terms:
            main_product = cp
            break
            
    if main_product:
        parts.append(main_product)
    else:
        # If no core product found, just add what we have
        for ft in found_terms:
            if ft not in ["Premium", "Bat Trang", "Ceramic", "Porcelain", "Pottery"]:
                parts.append(ft)
                
    # Add Style/Theme at the end
    if "Lotus" in found_terms: parts.append("- Lotus Design")
    if "Hand-painted" in found_terms: parts.append("(Hand-painted)")
    if "Crackle Glaze" in found_terms: parts.append("with Crackle Glaze")
    
    result = " ".join(parts)
    return result if result else vn_name
