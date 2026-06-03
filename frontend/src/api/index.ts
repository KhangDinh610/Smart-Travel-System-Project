const BASE_URL = "/api/v1";

export interface User {
  uid: string;
  email: string;
  token?: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  tag?: string;
  image_url?: string;
  category?: string;
  shop_id: number;
  shop_address?: string;
}

export interface Shop {
  id: number;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  shop_type: string;
  opening_hours: string;
}

export interface HistoryItem {
  id: number;
  user_id: string;
  product_id: string;
  shop_id: number;
  timestamp: string;
}

export interface ChatSession {
  id: number;
  user_id: string;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  sender: "user" | "ai";
  text: string;
  timestamp: string;
}

const getToken = () => {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    return user.token || "mock_token_demo";
  } catch {
    return "mock_token_demo";
  }
};

const authHeaders = () => ({
  "Content-Type": "application/json",
  "Authorization": `Bearer ${getToken()}`
});

export const api = {
  async register(email: string, password: string): Promise<{ uid: string }> {
    const res = await fetch(`${BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      let detail = "Action failed";
      try {
        const err = await res.json();
        detail = err.detail || detail;
      } catch (e) {
        console.error("Could not parse error response", e);
      }
      throw new Error(detail);
    }
    const text = await res.text();
    return text ? JSON.parse(text) : {};
  },

  async login(email: string, password: string): Promise<User> {
    const res = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      let detail = "Login failed";
      try {
        const err = await res.json();
        detail = err.detail || detail;
      } catch (e) {
        console.error("Could not parse login error response", e);
      }
      throw new Error(detail);
    }
    const text = await res.text();
    return text ? JSON.parse(text) : {} as User;
  },

  async loginWithFirebase(token: string): Promise<User> {
    const res = await fetch(`${BASE_URL}/login/firebase`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });
    if (!res.ok) {
      let detail = "Firebase login failed";
      try {
        const err = await res.json();
        detail = err.detail || detail;
      } catch (e) {
        console.error("Could not parse firebase login error response", e);
      }
      throw new Error(detail);
    }
    const text = await res.text();
    return text ? JSON.parse(text) : {} as User;
  },

  async getProducts(search?: string, category?: string, lang: string = "vi"): Promise<Product[]> {
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (category) params.append("category", category);
    params.append("lang", lang);
    const queryString = params.toString();
    const url = `${BASE_URL}/products?${queryString}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch products");
    return res.json();
  },

  async getProduct(id: number, lang: string = "vi"): Promise<Product> {
    const res = await fetch(`${BASE_URL}/products/${id}?lang=${lang}`);
    if (!res.ok) throw new Error("Failed to fetch product");
    return res.json();
  },

  async getRelatedProducts(productId: number, lang: string = "vi"): Promise<Product[]> {
    const res = await fetch(`${BASE_URL}/products/${productId}/related?lang=${lang}`);
    if (!res.ok) throw new Error("Failed to fetch related products");
    return res.json();
  },

  async getShop(shopId: number): Promise<Shop> {
    const res = await fetch(`${BASE_URL}/shops/${shopId}`);
    if (!res.ok) throw new Error("Failed to fetch shop");
    return res.json();
  },

  async chat(message: string, userId: string): Promise<{ reply: string }> {
    const res = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ message, user_id: userId }),
    });
    if (!res.ok) throw new Error("Chat failed");
    return res.json();
  },

  async createChatSession(title: string): Promise<ChatSession> {
    const res = await fetch(`${BASE_URL}/chat/sessions`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error("Failed to create chat session");
    return res.json();
  },

  async getChatSessions(): Promise<ChatSession[]> {
    const res = await fetch(`${BASE_URL}/chat/sessions`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch chat sessions");
    return res.json();
  },

  async getChatMessages(sessionId: number): Promise<ChatMessage[]> {
    const res = await fetch(`${BASE_URL}/chat/sessions/${sessionId}/messages`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch chat messages");
    return res.json();
  },

  async sendChatMessage(sessionId: number, text: string): Promise<ChatMessage> {
    const res = await fetch(`${BASE_URL}/chat/sessions/${sessionId}/message`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error("Failed to send chat message");
    return res.json();
  },

  async createHistory(userId: string, productId: string, shopId: number): Promise<HistoryItem> {
    const res = await fetch(`${BASE_URL}/history`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ user_id: userId, product_id: productId, shop_id: shopId }),
    });
    if (!res.ok) throw new Error("Failed to create history");
    return res.json();
  },

  async getWishlist(userId: string): Promise<{ product_ids: number[] }> {
    const res = await fetch(`${BASE_URL}/wishlist/${userId}`, {
      headers: { "Authorization": `Bearer ${getToken()}` }
    });
    if (!res.ok) throw new Error("Failed to fetch wishlist");
    return res.json();
  },

  async toggleWishlist(userId: string, productId: number): Promise<{ status: string }> {
    const res = await fetch(`${BASE_URL}/wishlist`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ user_id: userId, product_id: productId }),
    });
    if (!res.ok) throw new Error("Failed to toggle wishlist");
    return res.json();
  },

  async getNotifications(userId: string): Promise<any[]> {
    const res = await fetch(`${BASE_URL}/notifications/${userId}`);
    if (!res.ok) throw new Error("Failed to fetch notifications");
    return res.json();
  },

  async visualSearch(file: File): Promise<{ products: any[] }> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${BASE_URL}/visual-search`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Visual search failed");
    return res.json();
  },
  
  async scanProduct(file: File): Promise<{ analysis: string }> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${BASE_URL}/scan-product`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Product scan failed");
    return res.json();
  },

  async getHistory(userId: string, lang: string = "vi"): Promise<any[]> {
    const res = await fetch(`${BASE_URL}/history/${userId}?lang=${lang}`, {
      headers: { "Authorization": `Bearer ${getToken()}` }
    });
    if (!res.ok) throw new Error("Failed to fetch history");
    return res.json();
  },

  async detectDuplicate(description: string, userId: string): Promise<{ score: number; text?: string; match_type: string }> {
    const res = await fetch(`${BASE_URL}/detect-duplicate`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ description, user_id: userId }),
    });
    if (!res.ok) throw new Error("Failed to detect duplicate");
    return res.json();
  },

  async triggerSync(): Promise<{ message: string }> {
    const res = await fetch(`${BASE_URL}/sync`, {
      method: "POST",
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error("Sync failed");
    return res.json();
  }
};
