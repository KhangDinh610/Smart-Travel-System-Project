import { useState, useEffect } from "react";
import { LoginScreen } from "./components/LoginScreen";
import { OnboardingScreen } from "./components/OnboardingScreen";
import { HomeScreen } from "./components/HomeScreen";
import { ProductDetailScreen } from "./components/ProductDetailScreen";
import { type Lang, t } from "./translations";
import { type User, api, type Product as ApiProduct } from "../api";

import { SavedScreen } from "./components/SavedScreen";
import { ChatScreen } from "./components/ChatScreen";

type Screen = "login" | "onboarding" | "home" | "product" | "saved" | "chat";

export default function App() {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });
  const [screen, setScreen] = useState<Screen>(user ? "home" : "login");
  const [lang, setLang] = useState<Lang>("en");
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [savedItems, setSavedItems] = useState<Set<number>>(new Set());
  const [initialChatSession, setInitialChatSession] = useState<number | undefined>();
  const [isOnline, setIsOnline] = useState(window.navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  useEffect(() => {
    if (user && isOnline) {
      localStorage.setItem("user", JSON.stringify(user));
      api.getWishlist(user.uid)
        .then(res => setSavedItems(new Set(res.product_ids)))
        .catch(console.error);
    } else if (!user) {
      localStorage.removeItem("user");
      setSavedItems(new Set());
    }
  }, [user, isOnline]);

  const toggleSave = async (id: number) => {
    if (!user) return;
    if (!isOnline) {
       alert(lang === "vi" ? "Đang ngoại tuyến. Vui lòng kết nối mạng." : "Currently offline. Please reconnect.");
       return;
    }
    
    // Optimistic UI update
    setSavedItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

    try {
      await api.toggleWishlist(user.uid, id);
    } catch (e) {
      console.error(e);
      // Revert if failed
      setSavedItems((prev) => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        return next;
      });
    }
  };

  const tr = t[lang];

  const handleProductChat = async (product: ApiProduct) => {
    if (!user) return;
    if (!isOnline) {
       alert(lang === "vi" ? "Cần kết nối mạng để chat với AI." : "Need internet to chat with AI.");
       return;
    }
    try {
      const title = lang === "vi" ? `Hỏi về ${product.name}` : `About ${product.name}`;
      const session = await api.createChatSession(title);
      const message = lang === "vi" 
        ? `Tôi muốn hỏi về sản phẩm: ${product.name}. Nó có đặc điểm gì nổi bật?`
        : `I want to ask about: ${product.name}. What makes it special?`;
      
      await api.sendChatMessage(session.id, message);
      
      setInitialChatSession(session.id);
      setScreen("chat");
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="w-full min-h-screen">
      {!isOnline && (
        <div 
          className="fixed top-0 left-0 right-0 z-[100] flex items-center justify-center gap-2 py-2 px-4"
          style={{ background: "#DC2626", color: "white", fontSize: "13px", fontWeight: 700, textAlign: "center" }}
        >
          <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
          {lang === "vi" ? "Mất kết nối mạng. Đang chờ kết nối lại..." : "No internet connection. Waiting for network..."}
        </div>
      )}
      {screen === "login" && (
        <LoginScreen
          tr={tr.login}
          lang={lang}
          setLang={setLang}
          onLogin={(userData: User & { is_new_user?: boolean }) => {
            setUser(userData);
            if (userData.is_new_user) {
              setScreen("onboarding");
            } else {
              setScreen("home");
            }
          }}
        />
      )}
      {screen === "onboarding" && (
        <OnboardingScreen
          tr={tr.onboarding}
          lang={lang}
          setLang={setLang}
          onComplete={() => {
            if (user) {
              const updatedUser = { ...user, is_new_user: false };
              setUser(updatedUser);
              localStorage.setItem("user", JSON.stringify(updatedUser));
            }
            setScreen("home");
          }}
          onLogout={() => {
            setUser(null);
            setScreen("login");
          }}
        />
      )}
      {screen === "home" && (
        <HomeScreen
          tr={tr.home}
          lang={lang}
          setLang={setLang}
          user={user}
          savedItems={savedItems}
          toggleSave={toggleSave}
          onProductClick={(id: number) => {
            setSelectedProductId(id);
            setScreen("product");
          }}
          onChatClick={() => {
             setInitialChatSession(undefined);
             setScreen("chat");
          }}
          onNavigate={(s: Screen) => setScreen(s)}
          onLogout={() => {
            setUser(null);
            setScreen("login");
          }}
        />
      )}
      {screen === "product" && (
        <ProductDetailScreen
          tr={tr.product}
          lang={lang}
          setLang={setLang}
          user={user}
          productId={selectedProductId}
          onBack={() => setScreen("home")}
          savedItems={savedItems}
          toggleSave={toggleSave}
          onNavigate={(s: Screen) => setScreen(s)}
          onAskAI={handleProductChat}
          onProductClick={(id: number) => {
            setSelectedProductId(id);
            // screen is already "product", but updating productId triggers re-fetch
          }}
          onLogout={() => {
            setUser(null);
            setScreen("login");
          }}
        />
      )}
      {screen === "chat" && (
        <ChatScreen
          tr={tr.home}
          lang={lang}
          setLang={setLang}
          user={user}
          onNavigate={(s: Screen) => setScreen(s)}
          initialSessionId={initialChatSession}
          onLogout={() => {
            setUser(null);
            setScreen("login");
          }}
        />
      )}
      {screen === "saved" && (
        <SavedScreen
          tr={tr.home} // Reuse home translations for now
          lang={lang}
          setLang={setLang}
          user={user}
          savedItems={savedItems}
          toggleSave={toggleSave}
          onProductClick={(id: number) => {
            setSelectedProductId(id);
            setScreen("product");
          }}
          onNavigate={(s: Screen) => setScreen(s)}
          onLogout={() => {
            setUser(null);
            setScreen("login");
          }}
        />
      )}
    </div>
  );
}
