import { useState, useEffect } from "react";
import {
  ArrowLeft, Star, MapPin, Navigation, Heart, Share2,
  MessageCircle, ChevronRight, Sparkles, Clock, Shield,
  Compass, Home, Bookmark, User, Send, X, AlertTriangle, Menu, LogOut
} from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { LangToggle } from "./LangToggle";
import { type Lang, type Translations } from "../translations";
import { api, type User as ApiUser, type Product as ApiProduct, type Shop as ApiShop } from "../../api";

const GALLERY = [
  "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx2aWV0bmFtZXNlJTIwbGFudGVybiUyMGhvaSUyMGFuJTIwdHJhZGl0aW9uYWwlMjBjcmFmdHxlbnwxfHx8fDE3NzkyMDMzNjZ8MA&ixlib=rb-4.1.0&q=80&w=900",
];

interface ProductDetailScreenProps {
  tr: Translations["product"];
  lang: Lang;
  setLang: (l: Lang) => void;
  user: ApiUser | null;
  productId: number | null;
  onBack: () => void;
  savedItems: Set<number>;
  toggleSave: (id: number) => void;
  onNavigate: (s: any) => void;
  onAskAI: (product: ApiProduct) => void;
  onProductClick: (id: number) => void;
  onLogout: () => void;
}

export function ProductDetailScreen({ tr, lang, setLang, user, productId, onBack, savedItems, toggleSave, onNavigate, onAskAI, onProductClick, onLogout }: ProductDetailScreenProps) {
  const [activeImage, setActiveImage] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [product, setProduct] = useState<ApiProduct | null>(null);
  const [shop, setShop] = useState<ApiShop | null>(null);
  const [related, setRelated] = useState<ApiProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [duplicateWarning, setDuplicateWarning] = useState<string | null>(null);

  const productGallery = product?.image_url ? [product.image_url] : GALLERY;

  useEffect(() => {
    async function fetchProduct() {
      if (!productId) {
        setIsLoading(false);
        return;
      }
      try {
        const fetchedProduct = await api.getProduct(productId, lang);
        setProduct(fetchedProduct);
        
        if (fetchedProduct.shop_id) {
          api.getShop(fetchedProduct.shop_id).then(setShop).catch(console.error);
        }

        // Fetch dynamic related products
        api.getRelatedProducts(productId, lang).then(setRelated).catch(console.error);

        // Also log history
        if (user && fetchedProduct) {
           api.createHistory(user.uid, String(productId), fetchedProduct.shop_id).catch(console.error);
           
           // Detect duplicate
           const targetText = fetchedProduct.name + " | " + (fetchedProduct.description || "");
           api.detectDuplicate(targetText, user.uid)
             .then(res => {
               if (res.score > 0.7 && res.text) {
                 const matchedName = res.text.split('|')[0].trim();
                 setDuplicateWarning(lang === "vi" 
                   ? `Có vẻ bạn đã xem/lưu món tương tự: ${matchedName}` 
                   : `You previously viewed/saved a similar item: ${matchedName}`);
               }
             })
             .catch(console.error);
        }
      } catch (error) {
        console.error("Failed to fetch product:", error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchProduct();
  }, [productId]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center h-screen" style={{ background: "#FDF3EB" }}>
        <p style={{ color: "#E2714A", fontWeight: 700 }}>{lang === "vi" ? "Đang tải..." : "Loading..."}</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen w-full" style={{ background: "#FDF3EB" }}>

      {/* ── Sidebar (desktop) ── */}
      <aside
        className={`hidden lg:flex flex-col flex-shrink-0 transition-all duration-300 ${isSidebarOpen ? "w-64 xl:w-72" : "w-0 opacity-0 overflow-hidden"}`}
        style={{ background: "#3D2314", position: "sticky", top: 0, height: "100vh" }}
      >
        <div className="px-6 pt-8 pb-6 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: "rgba(255,255,255,0.15)" }}>
              <Compass size={18} color="white" />
            </div>
            <span style={{ color: "white", fontSize: "18px", fontWeight: 800 }}>BuyAI</span>
          </div>
          <LangToggle lang={lang} setLang={setLang} />
        </div>

        <nav className="flex flex-col gap-1 px-3">
          {[
            { id: "home", icon: Home, label: lang === "vi" ? "Trang chủ" : "Home" },
            { id: "chat", icon: MessageCircle, label: lang === "vi" ? "AI Chat" : "AI Chat" },
            { id: "saved", icon: Bookmark, label: lang === "vi" ? "Đã lưu" : "Saved" },
          ].map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => {
                if (id === "home") onBack();
                else if (id === "chat" || id === "saved") onNavigate(id);
              }}
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-left hover:bg-white/10 transition-all"
              style={{ color: "rgba(255,255,255,0.55)", fontSize: "14px" }}
            >
              <Icon size={17} /> {label}
            </button>
          ))}
          <button
            onClick={onLogout}
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-left hover:bg-white/10 transition-all mt-auto mb-6"
            style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px" }}
          >
            <LogOut size={17} /> {lang === "vi" ? "Đăng xuất" : "Sign out"}
          </button>
        </nav>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">

        {/* Breadcrumb top bar */}
        <div
          className="flex items-center gap-3 px-6 lg:px-8 py-4"
          style={{ background: "white", borderBottom: "1px solid #F5CBA7", position: "sticky", top: 0, zIndex: 10 }}
        >
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="hidden lg:flex items-center justify-center p-2 rounded-xl hover:bg-orange-50 transition-colors"
          >
            <Menu size={24} style={{ color: "#E2714A" }} />
          </button>
          
          <button
            onClick={onBack}
            className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-orange-50 transition-all"
            style={{ color: "#7A4528", fontSize: "14px", fontWeight: 600 }}
          >
            <ArrowLeft size={16} /> {tr.back}
          </button>
          <span style={{ color: "#B07050" }}>/</span>
          <span style={{ color: "#B07050", fontSize: "14px" }}>{lang === "vi" ? "Hội An" : "Hoi An"}</span>
          <span style={{ color: "#B07050" }}>/</span>
          <span style={{ color: "#3D2314", fontSize: "14px", fontWeight: 600 }}>{product ? product.name : (lang === "vi" ? "Đèn lồng lụa Hội An" : "Hoi An Silk Lantern")}</span>

          <div className="ml-auto flex items-center gap-2">
            <div className="lg:hidden">
              <LangToggle lang={lang} setLang={setLang} />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 rounded-xl" style={{ background: "white", border: "1.5px solid #F5CBA7", color: "#7A4528", fontSize: "13px", fontWeight: 600 }}>
              <Share2 size={15} /> {tr.share}
            </button>
          </div>
        </div>

        {/* Two-column layout */}
        <div className="flex-1 px-6 lg:px-8 py-8">
          <div className="flex flex-col lg:flex-row gap-8 max-w-7xl">

            {/* LEFT — Gallery */}
            <div className="lg:w-1/2 xl:w-[55%] flex-shrink-0">
              <div className="rounded-3xl overflow-hidden" style={{ height: "420px", position: "relative" }}>
                <ImageWithFallback src={productGallery[0]} alt="Product" className="w-full h-full object-cover" />
              </div>

              {/* Where to Buy — desktop */}
              <div className="hidden lg:block mt-6">
                <h3 style={{ color: "#3D2314", fontSize: "18px", fontWeight: 800, marginBottom: "14px" }}>{tr.whereToBuy}</h3>
                <div className="rounded-2xl overflow-hidden p-4" style={{ background: "white", boxShadow: "0 4px 20px rgba(61,35,20,0.08)" }}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p style={{ color: "#3D2314", fontSize: "16px", fontWeight: 700 }}>{shop ? shop.name : (lang === "vi" ? "Xưởng đèn lồng Linh" : "Linh's Lantern Atelier")}</p>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <span style={{ color: "#7A4528", fontSize: "12px" }}>{shop?.shop_type || tr.localArtisanShop}</span>
                      </div>
                      <div className="flex items-center gap-1 mt-1.5">
                        <MapPin size={12} style={{ color: "#B07050" }} />
                        <span style={{ color: "#7A4528", fontSize: "13px" }}>{shop?.address || "38 Trần Hưng Đạo, Hội An"}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT — Product info */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <span className="px-3 py-1 rounded-lg" style={{ background: "#FEF0EA", color: "#E2714A", fontSize: "12px", fontWeight: 700 }}>{product?.tag || "Handicrafts"}</span>
                <span className="px-3 py-1 rounded-lg flex items-center gap-1" style={{ background: "#E6F6F4", color: "#2A9D8F", fontSize: "12px", fontWeight: 700 }}>
                  <Sparkles size={11} /> {tr.aiTopPick}
                </span>
              </div>

              <h1 style={{ color: "#3D2314", fontSize: "30px", fontWeight: 900, lineHeight: 1.15 }}>
                {product ? product.name : (lang === "vi" ? "Đèn Lồng Lụa Hội An" : "Hoi An Silk Lantern")}
              </h1>

              {duplicateWarning && (
                <div className="mt-4 p-3 rounded-xl flex items-start gap-3" style={{ background: "#FFFBEB", border: "1px solid #FDE68A" }}>
                  <AlertTriangle size={20} style={{ color: "#D97706", marginTop: "2px" }} />
                  <p style={{ color: "#92400E", fontSize: "14px", fontWeight: 600 }}>{duplicateWarning}</p>
                </div>
              )}

              <div className="flex items-center gap-3 mt-3">
                <div className="flex items-center gap-1">
                  <MapPin size={14} style={{ color: "#2A9D8F" }} />
                  <span style={{ color: "#7A4528", fontSize: "14px" }}>{lang === "vi" ? "Hội An, Việt Nam" : "Hoi An, Vietnam"}</span>
                </div>
              </div>

              <div className="flex items-end gap-3 mt-5">
                <span style={{ color: "#E2714A", fontSize: "28px", fontWeight: 900, lineHeight: 1 }}>
                  {product ? product.price.toLocaleString("vi-VN") : "312.500"} đ
                </span>
              </div>

              {/* Description */}
              <div className="mt-6 p-5 rounded-2xl" style={{ background: "linear-gradient(135deg, #FEF0EA 0%, #FDE8D5 100%)", border: "1px solid #F5CBA7" }}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: "#E2714A" }}>
                    <Sparkles size={14} color="white" />
                  </div>
                  <span style={{ color: "#E2714A", fontSize: "14px", fontWeight: 700 }}>{lang === "vi" ? "Mô tả sản phẩm" : "Description"}</span>
                </div>
                <p style={{ color: "#5A3020", fontSize: "14px", lineHeight: 1.8 }}>
                  {product?.description || "No description available."}
                </p>
              </div>

              {/* Where to Buy — mobile */}
              <div className="lg:hidden mt-6">
                <h3 style={{ color: "#3D2314", fontSize: "18px", fontWeight: 800, marginBottom: "12px" }}>{tr.whereToBuy}</h3>
                <div className="rounded-2xl overflow-hidden p-4" style={{ background: "white", boxShadow: "0 4px 20px rgba(61,35,20,0.08)" }}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p style={{ color: "#3D2314", fontSize: "15px", fontWeight: 700 }}>{shop ? shop.name : (lang === "vi" ? "Xưởng đèn lồng Linh" : "Linh's Lantern Atelier")}</p>
                      <p style={{ color: "#7A4528", fontSize: "12px" }}>{shop?.address || "38 Trần Hưng Đạo, Hội An"}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* CTAs */}
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => product && onAskAI(product)}
                  className="flex items-center gap-2 px-5 py-3.5 rounded-xl transition-all hover:opacity-90"
                  style={{ background: "#FEF0EA", border: "2px solid #E2714A", color: "#E2714A", fontWeight: 700, fontSize: "14px" }}
                >
                  <MessageCircle size={17} /> {lang === "vi" ? "Hỏi AI về sản phẩm" : "Ask AI about Product"}
                </button>
                <button
                  onClick={() => {
                    if (productId) toggleSave(productId);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl transition-all hover:opacity-90"
                  style={{ background: "linear-gradient(135deg, #E2714A, #C8562E)", color: "white", fontWeight: 700, fontSize: "15px", boxShadow: "0 4px 20px rgba(226,113,74,0.4)" }}
                >
                  <Heart size={17} fill={(productId && savedItems.has(productId)) ? "white" : "none"} /> {(productId && savedItems.has(productId)) ? tr.saved : tr.saveWishlist}
                </button>
              </div>
            </div>
          </div>

          {/* Related Products */}
          <div className="mt-12 max-w-7xl">
            <div className="flex items-center justify-between mb-5">
              <h3 style={{ color: "#3D2314", fontSize: "20px", fontWeight: 800 }}>{tr.relatedProducts}</h3>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {related.map((item) => (
                <button 
                  key={item.id} 
                  onClick={() => onProductClick(item.id)}
                  className="text-left rounded-2xl overflow-hidden transition-all hover:scale-[1.03] hover:shadow-xl" 
                  style={{ background: "white", boxShadow: "0 2px 12px rgba(61,35,20,0.08)" }}
                >
                  <div style={{ height: "130px" }}>
                    <ImageWithFallback src={item.image_url || GALLERY[0]} alt={item.name} className="w-full h-full object-cover" />
                  </div>
                  <div className="p-3">
                    <span className="inline-block px-1.5 py-0.5 rounded mb-1" style={{ background: "#FEF0EA", color: "#E2714A", fontSize: "10px", fontWeight: 700 }}>{item.tag || "Local"}</span>
                    <p style={{ color: "#3D2314", fontSize: "13px", fontWeight: 700, lineHeight: 1.3 }}>{item.name}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span style={{ color: "#E2714A", fontSize: "14px", fontWeight: 800 }}>{item.price.toLocaleString("vi-VN")} đ</span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
          <div style={{ height: "40px" }} />
        </div>
      </main>
    </div>
  );
}
