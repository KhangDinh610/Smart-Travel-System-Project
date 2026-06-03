import { useState, useEffect } from "react";
import { ArrowLeft, Heart, Star, MapPin, Grid, List } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { LangToggle } from "./LangToggle";
import { type Lang, type Translations } from "../translations";
import { api, type User as ApiUser, type Product as ApiProduct } from "../../api";

interface SavedScreenProps {
  tr: Translations["home"]; // Reusing home translations for simplicity
  lang: Lang;
  setLang: (l: Lang) => void;
  user: ApiUser | null;
  savedItems: Set<number>;
  toggleSave: (id: number) => void;
  onProductClick: (id: number) => void;
  onNavigate: (s: any) => void;
  onLogout: () => void;
}

interface Product {
  id: number;
  name: string;
  price: string;
  tag: string;
  image: string;
  location: string;
  distance: string;
}

export function SavedScreen({ tr, lang, setLang, user, savedItems, toggleSave, onProductClick, onNavigate }: SavedScreenProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  useEffect(() => {
    async function fetchSavedProducts() {
      try {
        const apiProducts = await api.getProducts(undefined, undefined, lang);
        const formattedProducts: Product[] = apiProducts.map(p => ({
          id: p.id,
          name: p.name,
          price: p.price.toLocaleString("vi-VN") + " VNĐ",
          tag: p.tag || "General",
          image: p.image_url || "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?q=80&w=600",
          location: p.shop_address || "Local Shop",
          distance: "1.0 km"
        }));
        
        // Filter only saved items
        const saved = formattedProducts.filter(p => savedItems.has(p.id));
        setProducts(saved);
      } catch (error) {
        console.error("Failed to fetch saved products:", error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchSavedProducts();
  }, [savedItems]);

  const handleToggleSave = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    toggleSave(id);
  };

  return (
    <div className="flex flex-col min-h-screen w-full" style={{ background: "#FDF3EB" }}>
      {/* Header */}
      <header
        className="flex items-center gap-4 px-6 lg:px-8 py-4"
        style={{ background: "white", borderBottom: "1px solid #F5CBA7", position: "sticky", top: 0, zIndex: 10 }}
      >
        <button
          onClick={() => onNavigate("home")}
          className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-orange-50 transition-all"
          style={{ color: "#7A4528", fontSize: "14px", fontWeight: 600 }}
        >
          <ArrowLeft size={16} /> {lang === "vi" ? "Trở lại" : "Back"}
        </button>
        
        <h1 style={{ color: "#3D2314", fontSize: "18px", fontWeight: 800, flex: 1, textAlign: "center" }}>
          {lang === "vi" ? "Sản phẩm đã lưu" : "Saved Products"}
        </h1>

        <div className="flex items-center gap-2 ml-auto">
          <LangToggle lang={lang} setLang={setLang} />
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-y-auto px-6 lg:px-8 py-6 max-w-7xl mx-auto w-full">
        <div className="flex items-center justify-between mb-6">
          <p style={{ color: "#7A4528", fontSize: "14px", fontWeight: 600 }}>
            {products.length} {lang === "vi" ? "sản phẩm" : "items"}
          </p>
          <div className="flex rounded-xl overflow-hidden" style={{ border: "1px solid #F5CBA7" }}>
            <button onClick={() => setViewMode("grid")} className="p-2" style={{ background: viewMode === "grid" ? "#E2714A" : "white", color: viewMode === "grid" ? "white" : "#7A4528" }}>
              <Grid size={15} />
            </button>
            <button onClick={() => setViewMode("list")} className="p-2" style={{ background: viewMode === "list" ? "#E2714A" : "white", color: viewMode === "list" ? "white" : "#7A4528" }}>
              <List size={15} />
            </button>
          </div>
        </div>

        {isLoading ? (
          <p>Loading...</p>
        ) : products.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <Heart size={48} style={{ color: "#F5CBA7", marginBottom: "16px" }} />
            <h2 style={{ color: "#3D2314", fontSize: "20px", fontWeight: 800, marginBottom: "8px" }}>
              {lang === "vi" ? "Chưa có sản phẩm nào" : "No saved items yet"}
            </h2>
            <p style={{ color: "#7A4528", fontSize: "14px", maxWidth: "300px", marginBottom: "24px" }}>
              {lang === "vi" ? "Hãy khám phá và lưu lại những món quà yêu thích của bạn nhé!" : "Explore and save your favorite local souvenirs!"}
            </p>
            <button
              onClick={() => onNavigate("home")}
              className="px-6 py-3 rounded-xl transition-all hover:opacity-90"
              style={{ background: "linear-gradient(135deg, #E2714A, #C8562E)", color: "white", fontWeight: 700, fontSize: "15px" }}
            >
              {lang === "vi" ? "Khám phá ngay" : "Explore Now"}
            </button>
          </div>
        ) : viewMode === "grid" ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
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
                  <div onClick={(e) => handleToggleSave(product.id, e)} className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-full" style={{ background: "rgba(255,255,255,0.92)" }}>
                    <Heart size={15} style={{ color: savedItems.has(product.id) ? "#E2714A" : "#B07050" }} fill={savedItems.has(product.id) ? "#E2714A" : "none"} />
                  </div>
                </div>
                <div className="p-4">
                  <p style={{ color: "#3D2314", fontSize: "15px", fontWeight: 700, lineHeight: 1.3 }}>{product.name}</p>
                  <div className="flex items-center justify-between mt-3">
                    <span style={{ color: "#E2714A", fontSize: "18px", fontWeight: 900 }}>{product.price}</span>
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
                  <p style={{ color: "#3D2314", fontSize: "15px", fontWeight: 700 }}>{product.name}</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span style={{ color: "#E2714A", fontSize: "18px", fontWeight: 900 }}>{product.price}</span>
                  <div onClick={(e) => handleToggleSave(product.id, e)} className="w-8 h-8 flex items-center justify-center rounded-full" style={{ background: "#FDF3EB" }}>
                    <Heart size={15} style={{ color: savedItems.has(product.id) ? "#E2714A" : "#B07050" }} fill={savedItems.has(product.id) ? "#E2714A" : "none"} />
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
