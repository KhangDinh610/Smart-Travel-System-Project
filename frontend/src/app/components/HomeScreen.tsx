import { useState, useEffect } from "react";
import {
  Search, Camera, ChevronDown, Bell, Home, MessageCircle,
  Bookmark, User, Star, MapPin, Sparkles, TrendingUp, Heart,
  Compass, Settings, LogOut, Grid, List, SlidersHorizontal, Menu, X
} from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { LangToggle } from "./LangToggle";
import { type Lang, type Translations } from "../translations";

import { api, type User as ApiUser, type Product as ApiProduct } from "../../api";

interface Product {
  id: number;
  name: string;
  price: string;
  tag: string;
  image: string;
  location: string;
  distance: string;
}

const CATEGORY_KEYS = ["all", "food", "crafts", "clothing", "art", "gifts"] as const;
const CATEGORY_EMOJIS: Record<string, string> = { all: "✨", food: "🍜", crafts: "🏺", clothing: "👘", art: "🎨", gifts: "🎁" };

interface HomeScreenProps {
  tr: Translations["home"];
  lang: Lang;
  setLang: (l: Lang) => void;
  user: ApiUser | null;
  savedItems: Set<number>;
  toggleSave: (id: number) => void;
  onProductClick: (id: number) => void;
  onChatClick: () => void;
  onNavigate: (s: any) => void;
  onLogout: () => void;
}

export function HomeScreen({ tr, lang, setLang, user, savedItems, toggleSave, onProductClick, onChatClick, onNavigate, onLogout }: HomeScreenProps) {
  const [activeNav, setActiveNav] = useState("home");
  const [activeCategory, setActiveCategory] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isVisualSearch, setIsVisualSearch] = useState(false);
  
  // AI Scanner state
  const [showScanModal, setShowScanModal] = useState(false);
  const [scanResult, setScanResult] = useState<string | null>(null);
  const [scannedImage, setScannedImage] = useState<string | null>(null);
  
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (isVisualSearch) return;
    const handler = setTimeout(() => {
      async function fetchProducts() {
        setIsLoading(true);
        try {
          const apiProducts = await api.getProducts(searchQuery, activeCategory, lang);
          const formattedProducts: Product[] = apiProducts.map(p => ({
            id: p.id,
            name: p.name,
            price: p.price.toLocaleString("vi-VN") + " VNĐ",
            tag: p.tag || "General",
            image: p.image_url || "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?q=80&w=600",
            location: p.shop_address || "Local Shop",
            distance: "1.0 km"
          }));
          setProducts(formattedProducts);
        } catch (error) {
          console.error("Failed to fetch products:", error);
        } finally {
          setIsLoading(false);
        }
      }
      fetchProducts();
    }, 300); // 300ms debounce

    return () => clearTimeout(handler);
  }, [searchQuery, activeCategory, lang]);

  const handleVisualSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsLoading(true);
    try {
      const res = await api.visualSearch(file);
      if (res.products && res.products.length > 0) {
        const searchedProducts: Product[] = res.products.map(p => ({
          id: p.id,
          name: p.name,
          price: (p.price || 0).toLocaleString("vi-VN") + " VNĐ",
          tag: p.tag || "Searched",
          image: "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?q=80&w=600", // Fallback
          location: p.shop_address || "Local Shop",
          distance: ""
        }));
        setProducts(searchedProducts);
        setIsVisualSearch(true);
      } else {
        alert("No similar products found.");
      }
    } catch (error) {
      console.error("Visual search error", error);
      alert("Failed to search visually.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleScanProduct = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => setScannedImage(e.target?.result as string);
    reader.readAsDataURL(file);

    setShowScanModal(true);
    setScanResult(null);
    
    try {
      const res = await api.scanProduct(file);
      setScanResult(res.analysis);
    } catch (error) {
      console.error("Scan error", error);
      setScanResult("Đã có lỗi xảy ra khi phân tích hình ảnh. Vui lòng thử lại sau.");
    }
  };

  const handleToggleSave = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    toggleSave(id);
  };

  const renderMarkdown = (text: string) => {
    const lines = text.split("\n");
    
    const renderInline = (inlineText: string) => {
      const parts = inlineText.split(/(\*\*.*?\*\*|\*.*?\*)/g);
      return parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return <strong key={i}>{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith("*") && part.endsWith("*")) {
          return <em key={i} style={{ fontStyle: "italic" }}>{part.slice(1, -1)}</em>;
        }
        return part;
      });
    };

    return lines.map((line, i) => {
      const trimmedLine = line.trim();
      
      if (trimmedLine === "---") {
        return <hr key={i} style={{ margin: "12px 0", border: "none", borderTop: "1.5px solid #F5CBA7" }} />;
      }

      if (line.startsWith("###")) {
        return (
          <h3 key={i} style={{ fontWeight: 800, fontSize: "16px", marginTop: "14px", marginBottom: "6px", color: "#E2714A" }}>
            {renderInline(line.replace(/^###\s*/, ""))}
          </h3>
        );
      }

      if (trimmedLine.startsWith("* ") || trimmedLine.startsWith("- ")) {
        return (
          <div key={i} className="flex gap-2 ml-2 mb-1.5">
            <span style={{ color: "#E2714A", fontWeight: 900 }}>•</span>
            <span style={{ flex: 1 }}>{renderInline(trimmedLine.replace(/^[*|-]\s*/, ""))}</span>
          </div>
        );
      }

      if (/^\d+\.\s/.test(trimmedLine)) {
        return (
          <div key={i} className="flex gap-2 mb-1.5">
            <span style={{ fontWeight: 800, color: "#E2714A", minWidth: "18px" }}>{trimmedLine.match(/^\d+\./)?.[0]}</span>
            <span style={{ flex: 1 }}>{renderInline(trimmedLine.replace(/^\d+\.\s*/, ""))}</span>
          </div>
        );
      }

      if (trimmedLine === "") {
        return <div key={i} style={{ height: "8px" }} />;
      }

      return (
        <p key={i} style={{ marginBottom: "4px", lineHeight: 1.6 }}>
          {renderInline(line)}
        </p>
      );
    });
  };

  const navItems = [
    { id: "home", icon: Home, label: tr.nav.home },
    { id: "chat", icon: MessageCircle, label: tr.nav.chat },
    { id: "saved", icon: Bookmark, label: tr.nav.saved },
  ];

  return (
    <div className="flex min-h-screen w-full" style={{ background: "#FDF3EB" }}>

      {/* ── Desktop Sidebar ── */}
      <aside
        className={`hidden lg:flex flex-col flex-shrink-0 transition-all duration-300 ${isSidebarOpen ? "w-64 xl:w-72" : "w-0 opacity-0 overflow-hidden"}`}
        style={{ background: "#3D2314", position: "sticky", top: 0, height: "100vh" }}
      >
        <div className="px-6 pt-8 pb-5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: "rgba(255,255,255,0.15)" }}>
              <Compass size={18} color="white" />
            </div>
            <span style={{ color: "white", fontSize: "18px", fontWeight: 800 }}>BuyAI</span>
          </div>
          <LangToggle lang={lang} setLang={setLang} />
        </div>

        <nav className="flex flex-col gap-1 px-3">
          {navItems.map(({ id, icon: Icon, label }) => {
            const isActive = activeNav === id;
            return (
              <button
                key={id}
                onClick={() => {
                  if (id === "saved" || id === "home" || id === "chat") {
                    onNavigate(id);
                    return;
                  }
                  setActiveNav(id);
                }}
                className="flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all"
                style={{ background: isActive ? "#E2714A" : "transparent", color: isActive ? "white" : "rgba(255,255,255,0.6)", fontWeight: isActive ? 700 : 500 }}
              >
                <Icon size={18} />
                <span style={{ fontSize: "14px" }}>{label}</span>
                </button>
            );
          })}
        </nav>

        <div className="px-4 mt-8">
          <p style={{ color: "rgba(255,255,255,0.35)", fontSize: "11px", fontWeight: 700, letterSpacing: "0.5px", textTransform: "uppercase", marginBottom: "10px" }}>
            {tr.browseByCategory}
          </p>
          <div className="flex flex-col gap-1">
            {CATEGORY_KEYS.map((key) => (
              <button
                key={key}
                onClick={() => { setActiveCategory(key); setIsVisualSearch(false); }}
                className="flex items-center gap-2.5 px-3 py-2 rounded-xl transition-all"
                style={{
                  background: activeCategory === key ? "rgba(226,113,74,0.2)" : "transparent",
                  color: activeCategory === key ? "#F4A261" : "rgba(255,255,255,0.5)",
                  fontWeight: activeCategory === key ? 700 : 400,
                }}
              >
                <span style={{ fontSize: "16px" }}>{CATEGORY_EMOJIS[key]}</span>
                <span style={{ fontSize: "13px" }}>{tr.categories[key as keyof typeof tr.categories]}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="mt-auto px-4 pb-6 flex flex-col gap-1">
          <button onClick={onLogout} className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5" style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px" }}>
            <LogOut size={16} /> {tr.signOut}
          </button>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="flex-1 flex flex-col min-w-0">

        {/* Top bar */}
        <header
          className="flex items-center gap-4 px-6 lg:px-8 py-4"
          style={{ background: "white", borderBottom: "1px solid #F5CBA7", position: "sticky", top: 0, zIndex: 10 }}
        >
          <div className="flex lg:hidden items-center gap-2 mr-1">
            <Compass size={20} style={{ color: "#E2714A" }} />
          </div>

          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="hidden lg:flex items-center justify-center p-2 rounded-xl hover:bg-orange-50 transition-colors"
          >
            <Menu size={24} style={{ color: "#E2714A" }} />
          </button>

          <div
            className="flex items-center gap-3 flex-1 max-w-2xl px-4 py-2.5 rounded-xl"
            style={{ background: "#FDF3EB", border: "1.5px solid #F5CBA7" }}
          >
            <div
              className="flex items-center gap-3 flex-1 cursor-text"
            >
              <Search size={17} style={{ color: "#B07050", flexShrink: 0 }} />
              <input 
                type="text" 
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setIsVisualSearch(false); }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    // Triggering search is handled by useEffect on searchQuery change
                    // but we can force clear visual search here too
                    setIsVisualSearch(false);
                  }
                }}
                placeholder={tr.searchPlaceholder}
                className="bg-transparent border-none outline-none flex-1 text-sm text-[#3D2314] placeholder-[#B07050]"
              />
              {searchQuery && (
                <button 
                  onClick={() => { setSearchQuery(""); setIsVisualSearch(false); }}
                  className="p-1 hover:bg-orange-100 rounded-full transition-colors"
                >
                  <X size={14} style={{ color: "#B07050" }} />
                </button>
              )}
            </div>
            <div className="flex gap-2">
              <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg" style={{ background: "white", border: "1px solid #F5CBA7", cursor: "pointer" }}>
                <Camera size={14} color="#E2714A" />
                <span className="hidden sm:inline" style={{ color: "#E2714A", fontSize: "12px", fontWeight: 700 }}>{lang === "vi" ? "Tìm bằng ảnh" : "Visual Search"}</span>
                <input type="file" accept="image/*" className="hidden" onChange={handleVisualSearch} />
              </label>
              <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all hover:opacity-90" style={{ background: "linear-gradient(135deg, #E2714A, #C8562E)", cursor: "pointer", boxShadow: "0 2px 8px rgba(226,113,74,0.3)" }}>
                <Sparkles size={14} color="white" />
                <span style={{ color: "white", fontSize: "12px", fontWeight: 700 }}>{tr.aiScan}</span>
                <input type="file" accept="image/*" className="hidden" onChange={handleScanProduct} />
              </label>
            </div>
          </div>

          <div className="flex items-center gap-2 ml-auto">
            <button className="lg:hidden flex items-center gap-1.5 px-3 py-2 rounded-xl" style={{ background: "#FDF3EB", border: "1px solid #F5CBA7" }}>
              <MapPin size={13} style={{ color: "#E2714A" }} />
              <span style={{ color: "#3D2314", fontSize: "12px", fontWeight: 600 }}>Hội An</span>
              <ChevronDown size={12} style={{ color: "#7A4528" }} />
            </button>

            <div className="lg:hidden">
              <LangToggle lang={lang} setLang={setLang} />
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl" style={{ background: "#FEF0EA", border: "1.5px solid #F5CBA7" }}>
              <User size={14} style={{ color: "#E2714A" }} />
              <span style={{ color: "#3D2314", fontSize: "13px", fontWeight: 700 }}>
                {user?.name || user?.email?.split('@')[0] || (lang === 'vi' ? 'Khách' : 'Guest')}
              </span>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 lg:px-8 py-6">

          {/* Mobile categories */}
          <div className="flex lg:hidden gap-2 overflow-x-auto pb-2 mb-5" style={{ scrollbarWidth: "none" }}>
            {CATEGORY_KEYS.map((key) => (
              <button
                key={key}
                onClick={() => { setActiveCategory(key); setIsVisualSearch(false); }}
                className="flex items-center gap-1.5 px-4 py-2 rounded-full whitespace-nowrap transition-all"
                style={{
                  background: activeCategory === key ? "#E2714A" : "white",
                  color: activeCategory === key ? "white" : "#7A4528",
                  fontWeight: activeCategory === key ? 700 : 500,
                  fontSize: "13px",
                  border: `1.5px solid ${activeCategory === key ? "#E2714A" : "#F5CBA7"}`,
                  boxShadow: activeCategory === key ? "0 4px 12px rgba(226,113,74,0.3)" : "none",
                }}
              >
                <span>{CATEGORY_EMOJIS[key]}</span>
                {tr.categories[key as keyof typeof tr.categories]}
              </button>
            ))}
          </div>

          {/* Section header */}
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              {isVisualSearch ? (
                <>
                  <Camera size={18} style={{ color: "#E2714A" }} />
                  <h2 style={{ color: "#3D2314", fontSize: "20px", fontWeight: 800 }}>{lang === "vi" ? "Kết quả tìm kiếm bằng ảnh" : "Visual Search Results"}</h2>
                  <button onClick={() => { setIsVisualSearch(false); setSearchQuery(""); }} className="ml-3 text-sm px-3 py-1 rounded-full bg-orange-100 text-orange-700 font-semibold hover:bg-orange-200">
                    {lang === "vi" ? "Hủy" : "Clear"}
                  </button>
                </>
              ) : (
                <>
                  <TrendingUp size={18} style={{ color: "#E2714A" }} />
                  <h2 style={{ color: "#3D2314", fontSize: "20px", fontWeight: 800 }}>{tr.recommendedFor}</h2>
                  <span className="px-2 py-0.5 rounded-full hidden sm:inline" style={{ background: "#FEF0EA", color: "#E2714A", fontSize: "12px", fontWeight: 700 }}>{tr.aiCurated}</span>
                </>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button className="flex items-center gap-1.5 px-3 py-2 rounded-xl" style={{ background: "white", border: "1px solid #F5CBA7", color: "#7A4528", fontSize: "13px" }}>
                <SlidersHorizontal size={13} /> {tr.filter}
              </button>
              <div className="flex rounded-xl overflow-hidden" style={{ border: "1px solid #F5CBA7" }}>
                <button onClick={() => setViewMode("grid")} className="p-2" style={{ background: viewMode === "grid" ? "#E2714A" : "white", color: viewMode === "grid" ? "white" : "#7A4528" }}>
                  <Grid size={15} />
                </button>
                <button onClick={() => setViewMode("list")} className="p-2" style={{ background: viewMode === "list" ? "#E2714A" : "white", color: viewMode === "list" ? "white" : "#7A4528" }}>
                  <List size={15} />
                </button>
              </div>
            </div>
          </div>

          {/* Products */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="animate-spin mb-4">
                <Sparkles size={32} color="#E2714A" />
              </div>
              <p style={{ color: "#7A4528", fontWeight: 600 }}>{lang === "vi" ? "Đang tìm kiếm sản phẩm..." : "Searching for products..."}</p>
            </div>
          ) : products.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 rounded-2xl bg-orange-50 flex items-center justify-center mb-4">
                <Search size={32} color="#B07050" opacity={0.5} />
              </div>
              <h3 style={{ color: "#3D2314", fontSize: "18px", fontWeight: 700 }}>{lang === "vi" ? "Không tìm thấy sản phẩm" : "No products found"}</h3>
              <p className="mt-2" style={{ color: "#7A4528", maxWidth: "300px" }}>
                {lang === "vi" ? "Thử tìm kiếm với từ khóa khác hoặc xóa bộ lọc." : "Try searching with different keywords or clear your filters."}
              </p>
              {searchQuery && (
                <button 
                  onClick={() => { setSearchQuery(""); setActiveCategory("all"); }}
                  className="mt-6 px-6 py-2 rounded-xl text-white font-bold"
                  style={{ background: "#E2714A" }}
                >
                  {lang === "vi" ? "Xóa tìm kiếm" : "Clear search"}
                </button>
              )}
            </div>
          ) : viewMode === "grid" ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-5">
              {products.map((product) => (
                <button
                  key={product.id}
                  onClick={() => onProductClick(product.id)}
                  className="text-left rounded-2xl overflow-hidden transition-all hover:scale-[1.02] hover:shadow-xl active:scale-98"
                  style={{ background: "white", boxShadow: "0 2px 16px rgba(61,35,20,0.08)" }}
                >
                  <div className="relative" style={{ height: "200px" }}>
                    <ImageWithFallback src={product.image} alt={product.name} className="w-full h-full object-cover" />
                    <div className="absolute top-3 left-3">
                      <span className="px-2 py-1 rounded-lg" style={{ background: "rgba(253,243,235,0.95)", color: "#E2714A", fontSize: "11px", fontWeight: 700 }}>{product.tag}</span>
                    </div>
                    <button onClick={(e) => handleToggleSave(product.id, e)} className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-full" style={{ background: "rgba(255,255,255,0.92)" }}>
                      <Heart size={15} style={{ color: savedItems.has(product.id) ? "#E2714A" : "#B07050" }} fill={savedItems.has(product.id) ? "#E2714A" : "none"} />
                    </button>
                  </div>
                  <div className="p-4">
                    <p style={{ color: "#3D2314", fontSize: "15px", fontWeight: 700, lineHeight: 1.3 }}>{product.name}</p>
                    <div className="flex items-center gap-1 mt-1.5">
                      <MapPin size={11} style={{ color: "#2A9D8F" }} />
                      <span style={{ color: "#7A4528", fontSize: "11px" }}>{product.location}</span>
                    </div>
                    <div className="flex items-center justify-between mt-3">
                      <span style={{ color: "#E2714A", fontSize: "18px", fontWeight: 900 }}>{product.price}</span>
                      <span className="px-3 py-1 rounded-lg" style={{ background: "#FEF0EA", color: "#E2714A", fontSize: "12px", fontWeight: 700 }}>View →</span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {products.map((product) => (
                <button
                  key={product.id}
                  onClick={() => onProductClick(product.id)}
                  className="flex items-center gap-4 p-4 rounded-2xl text-left transition-all hover:shadow-lg"
                  style={{ background: "white", boxShadow: "0 2px 12px rgba(61,35,20,0.06)" }}
                >
                  <div className="rounded-xl overflow-hidden flex-shrink-0" style={{ width: "90px", height: "90px" }}>
                    <ImageWithFallback src={product.image} alt={product.name} className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="inline-block px-2 py-0.5 rounded-lg mb-1" style={{ background: "#FEF0EA", color: "#E2714A", fontSize: "11px", fontWeight: 700 }}>{product.tag}</span>
                    <p style={{ color: "#3D2314", fontSize: "15px", fontWeight: 700 }}>{product.name}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <div className="flex items-center gap-1">
                        <MapPin size={11} style={{ color: "#2A9D8F" }} />
                        <span style={{ color: "#7A4528", fontSize: "12px" }}>{product.location}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span style={{ color: "#E2714A", fontSize: "18px", fontWeight: 900 }}>{product.price}</span>
                    <button onClick={(e) => handleToggleSave(product.id, e)} className="w-8 h-8 flex items-center justify-center rounded-full" style={{ background: "#FDF3EB" }}>
                      <Heart size={15} style={{ color: savedItems.has(product.id) ? "#E2714A" : "#B07050" }} fill={savedItems.has(product.id) ? "#E2714A" : "none"} />
                    </button>
                  </div>
                </button>
              ))}
            </div>
          )}

          <div style={{ height: "32px" }} />
        </div>
      </main>

      {/* Mobile bottom nav */}
      <div
        className="lg:hidden fixed bottom-0 left-0 right-0 flex items-center justify-around px-2 py-2"
        style={{ background: "white", borderTop: "1px solid #F5CBA7", boxShadow: "0 -4px 20px rgba(61,35,20,0.08)", zIndex: 20 }}
      >
        {navItems.map(({ id, icon: Icon, label }) => {
          const isActive = activeNav === id;
          return (
            <button
              key={id}
              onClick={() => { 
                if (id === "chat") {
                  onNavigate("chat");
                } else {
                  setActiveNav(id);
                }
              }}
              className="flex flex-col items-center gap-0.5 px-4 py-1.5"
            >
              <div className="w-8 h-8 flex items-center justify-center rounded-xl" style={{ background: isActive ? "#FEF0EA" : "transparent" }}>
                <Icon size={20} style={{ color: isActive ? "#E2714A" : "#B07050" }} />
              </div>
              <span style={{ color: isActive ? "#E2714A" : "#B07050", fontSize: "10px", fontWeight: isActive ? 700 : 500 }}>{label}</span>
            </button>
          );
        })}
      </div>

      {/* AI Scanner Modal */}
      {showScanModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(61,35,20,0.6)", backdropFilter: "blur(4px)" }} onClick={() => setShowScanModal(false)}>
          <div className="bg-white rounded-3xl w-full max-w-xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]" onClick={e => e.stopPropagation()}>
            <div className="p-5 border-b border-orange-100 flex justify-between items-center bg-orange-50/50">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-orange-500 flex items-center justify-center">
                  <Sparkles size={16} color="white" />
                </div>
                <h3 className="text-xl font-bold text-[#3D2314]">{lang === "vi" ? "AI Phân tích nguồn gốc" : "AI Souvenir Scanner"}</h3>
              </div>
              <button onClick={() => setShowScanModal(false)} className="p-2 bg-orange-100 rounded-full text-orange-700 hover:bg-orange-200">
                <X size={16} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              {scannedImage && (
                <div className="w-full h-48 rounded-2xl overflow-hidden mb-6 relative bg-gray-50 flex items-center justify-center border border-gray-100">
                  <img src={scannedImage} alt="Scanned" className="max-w-full max-h-full object-contain" />
                </div>
              )}
              
              {!scanResult ? (
                <div className="flex flex-col items-center justify-center py-10">
                  <div className="animate-spin mb-5">
                     <Sparkles size={28} color="#E2714A" />
                  </div>
                  <p className="text-[#7A4528] font-medium text-lg">{lang === "vi" ? "AI đang phân tích bức ảnh..." : "AI is analyzing the image..."}</p>
                  <p className="text-[#B07050] text-sm mt-2">{lang === "vi" ? "Quá trình này có thể mất vài giây" : "This might take a few seconds"}</p>
                </div>
              ) : (
                <div className="prose prose-orange prose-sm sm:prose-base max-w-none text-[#5A3020]">
                  {renderMarkdown(scanResult)}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
