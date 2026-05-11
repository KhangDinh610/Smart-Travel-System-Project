import math
import re
from typing import List, Dict, Optional, Tuple

from sentence_transformers import SentenceTransformer, util

try:
    from firebase_admin import firestore
except Exception:
    firestore = None

MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

FALLBACK_PRODUCTS = [
    {
        "id": "prod_1",
        "name": "Bánh pía Sóc Trăng",
        "description": "Đặc sản miền Tây, thích hợp làm quà tặng. Hương vị nhân đậu xanh, sầu riêng, thơm ngon.",
        "price": 120000,
        "rating": 4.4,
        "tags": ["đặc sản", "quà tặng", "bánh"],
        "shop_name": "Chợ Bến Thành",
        "shop_id": "shop_1",
        "shop_lat": 10.772, 
        "shop_lon": 106.698
    },
    {
        "id": "prod_2",
        "name": "Trà sữa matcha",
        "description": "Trà sữa matcha thơm mát, phù hợp cho bạn gái và làm quà tặng nhỏ xinh.",
        "price": 45000,
        "rating": 4.6,
        "tags": ["quà tặng", "trà sữa", "ngọt"],
        "shop_name": "Saigon Center",
        "shop_id": "shop_2",
        "shop_lat": 10.771,
        "shop_lon": 106.703
    },
    {
        "id": "prod_3",
        "name": "Cà phê sữa đá",
        "description": "Cà phê đặc trưng Việt Nam, thích hợp làm quà du lịch, vị đậm đà và thơm nồng.",
        "price": 30000,
        "rating": 4.3,
        "tags": ["cà phê", "đồ uống", "đặc sản"],
        "shop_name": "Vincom Center",
        "shop_id": "shop_3",
        "shop_lat": 10.762,
        "shop_lon": 106.689
    },
    {
        "id": "prod_4",
        "name": "Bánh tráng trộn",
        "description": "Món ăn vặt nổi tiếng Sài Gòn, gồm bánh tráng, trứng cút, đồ chua và rau răm.",
        "price": 50000,
        "rating": 4.2,
        "tags": ["ăn vặt", "đặc sản", "miền nam"],
        "shop_name": "Chợ Bến Thành",
        "shop_id": "shop_1",
        "shop_lat": 10.772,
        "shop_lon": 106.698
    }
]

FALLBACK_SHOPS = [
    {
        "id": "shop_1",
        "name": "Chợ Bến Thành",
        "address": "Quận 1, TP.HCM",
        "latitude": 10.772,
        "longitude": 106.698,
        "rating": 4.1,
        "tags": ["chợ", "đặc sản", "du lịch"]
    },
    {
        "id": "shop_2",
        "name": "Saigon Center",
        "address": "Quận 1, TP.HCM",
        "latitude": 10.771,
        "longitude": 106.703,
        "rating": 4.3,
        "tags": ["trung tâm thương mại", "quà tặng", "đồ uống"]
    },
    {
        "id": "shop_3",
        "name": "Vincom Center",
        "address": "Quận 1, TP.HCM",
        "latitude": 10.762,
        "longitude": 106.689,
        "rating": 4.2,
        "tags": ["trung tâm thương mại", "cà phê", "quà lưu niệm"]
    }
]


def get_firestore_client():
    if firestore is None:
        return None
    try:
        return firestore.client()
    except Exception:
        return None


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Return kilometers
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class KnowledgeBase:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        self.documents: List[Dict] = []
        self.embeddings = None
        self._build_documents()

    def _build_documents(self):
        db = get_firestore_client()
        docs: List[Dict] = []

        if db:
            try:
                products = db.collection("products").stream()
                for product in products:
                    data = product.to_dict() or {}
                    title = data.get("name", "Sản phẩm không tên")
                    text = f"{title}. {data.get('description', '')}."
                    shop_name = data.get("shop_name") or data.get("shop", "")
                    if shop_name:
                        text += f" Cửa hàng: {shop_name}."
                    docs.append({
                        "id": str(product.id),
                        "title": title,
                        "text": text,
                        "type": "product",
                        "source": "product",
                        "meta": data
                    })
            except Exception:
                docs = []

            try:
                shops = db.collection("shops").stream()
                for shop in shops:
                    data = shop.to_dict() or {}
                    title = data.get("name", "Cửa hàng không tên")
                    text = f"{title}. {data.get('address', '')}."
                    docs.append({
                        "id": str(shop.id),
                        "title": title,
                        "text": text,
                        "type": "shop",
                        "source": "shop",
                        "meta": data
                    })
            except Exception:
                pass

        if not docs:
            for item in FALLBACK_PRODUCTS:
                docs.append({
                    "id": item["id"],
                    "title": item["name"],
                    "text": f"{item['name']}. {item['description']}. Cửa hàng: {item['shop_name']}. Giá: {item['price']} VND.",
                    "type": "product",
                    "source": "fallback",
                    "meta": item
                })
            for item in FALLBACK_SHOPS:
                docs.append({
                    "id": item["id"],
                    "title": item["name"],
                    "text": f"{item['name']}. {item['address']}.",
                    "type": "shop",
                    "source": "fallback",
                    "meta": item
                })

        self.documents = docs
        if docs:
            self.embeddings = self.model.encode([doc["text"] for doc in docs], convert_to_tensor=True)
        else:
            self.embeddings = None

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.embeddings or not self.documents:
            return []
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        similarity_scores = util.cos_sim(query_embedding, self.embeddings)[0]
        top_indices = similarity_scores.argsort(descending=True)[:top_k].cpu().numpy().tolist()
        results = []
        for idx in top_indices:
            score = float(similarity_scores[idx].item())
            doc = self.documents[idx]
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "text": doc["text"],
                "type": doc["type"],
                "score": score,
                "meta": doc["meta"]
            })
        return results


class RAGChatbot:
    def __init__(self, model_name: str = MODEL_NAME):
        self.kb = KnowledgeBase(model_name=model_name)

    def build_prompt(self, query: str, retrieved: List[Dict], history: Optional[List[str]] = None) -> str:
        prompt = [
            f"Bạn là trợ lý mua sắm thông minh. Người dùng hỏi: '{query}'.",
            "Dưới đây là những thông tin liên quan từ dữ liệu sản phẩm và cửa hàng:",
        ]
        for idx, item in enumerate(retrieved, start=1):
            prompt.append(f"{idx}. {item['title']}: {item['text']} (Độ phù hợp: {item['score']:.2f})")
        if history:
            prompt.append("Người dùng đã mua những sản phẩm sau đây, vì vậy hãy ưu tiên tránh gợi ý trùng lặp:")
            for product_id in history:
                prompt.append(f"- {product_id}")
        prompt.append("Trả lời ngắn gọn, rõ ràng, gợi ý ít nhất 2 sản phẩm hoặc cửa hàng phù hợp.")
        return "\n".join(prompt)

    def generate_answer(self, query: str, retrieved: List[Dict], history: Optional[List[str]] = None) -> str:
        if not retrieved:
            return "Xin lỗi, tôi chưa tìm thấy dữ liệu phù hợp ngay bây giờ. Bạn có thể thử mô tả chi tiết hơn." 

        lines = [f"Tôi đã đọc yêu cầu của bạn: '{query}'."]
        if history:
            lines.append("Tôi đã xem qua lịch sử mua sắm của bạn và sẽ cố gắng tránh gợi ý trùng lặp.")
        lines.append("Dưới đây là các gợi ý phù hợp nhất mà tôi tìm thấy:")
        for idx, item in enumerate(retrieved, start=1):
            summary = item["meta"].get("description") if isinstance(item["meta"], dict) else item["text"]
            lines.append(f"{idx}. {item['title']}: {summary} (Độ phù hợp {item['score']:.2f})")
        lines.append("Nếu bạn muốn chi tiết hơn, hãy hỏi thêm về từng gợi ý.")
        return "\n".join(lines)


class RecommendationEngine:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        self.products = self._load_products()
        self.product_embeddings = self.model.encode([p["text"] for p in self.products], convert_to_tensor=True) if self.products else None

    def _load_products(self) -> List[Dict]:
        db = get_firestore_client()
        products = []

        if db:
            try:
                raw_products = db.collection("products").stream()
                for doc in raw_products:
                    data = doc.to_dict() or {}
                    name = data.get("name", "Sản phẩm không tên")
                    desc = data.get("description", "")
                    text = f"{name}. {desc}."
                    products.append({
                        "id": str(doc.id),
                        "name": name,
                        "description": desc,
                        "text": text,
                        "price": float(data.get("price", 0) or 0),
                        "rating": float(data.get("rating", 3.5) or 3.5),
                        "tags": data.get("tags", []),
                        "shop_name": data.get("shop_name", data.get("shop", "")),
                        "shop_lat": float(data.get("shop_lat", 0) or 0),
                        "shop_lon": float(data.get("shop_lon", 0) or 0),
                    })
            except Exception:
                products = []

        if not products:
            for item in FALLBACK_PRODUCTS:
                products.append({
                    "id": item["id"],
                    "name": item["name"],
                    "description": item["description"],
                    "text": f"{item['name']}. {item['description']}.",
                    "price": item["price"],
                    "rating": item["rating"],
                    "tags": item["tags"],
                    "shop_name": item["shop_name"],
                    "shop_lat": item["shop_lat"],
                    "shop_lon": item["shop_lon"],
                })

        return products

    def _load_user_history(self, user_id: str) -> List[str]:
        db = get_firestore_client()
        if not db:
            return []
        try:
            entries = db.collection("history").where("user_id", "==", user_id).stream()
            return [entry.to_dict().get("product_id") for entry in entries if entry.to_dict().get("product_id")]
        except Exception:
            return []

    def _tag_match(self, preference: str, tags: List[str], text: str) -> float:
        if not preference:
            return 0.0
        words = set(re.findall(r"[\wàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+", preference.lower()))
        if not words:
            return 0.0
        tag_words = set(t.lower() for t in tags if isinstance(t, str))
        text_words = set(re.findall(r"[\wàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+", text.lower()))
        matched = len(words & (tag_words | text_words))
        return min(1.0, matched / max(1, len(words)))

    def _budget_score(self, price: float, budget: Optional[float]) -> float:
        if not budget or budget <= 0 or price <= 0:
            return 0.5
        diff = abs(price - budget)
        return max(0.0, 1.0 - min(diff / max(budget, price, 1), 1.0))

    def _proximity_score(self, user_lat: Optional[float], user_lon: Optional[float], shop_lat: float, shop_lon: float) -> float:
        if user_lat is None or user_lon is None or shop_lat == 0 or shop_lon == 0:
            return 0.5
        distance = haversine_distance(user_lat, user_lon, shop_lat, shop_lon)
        return max(0.0, 1.0 - min(distance / 20.0, 1.0))

    def recommend(
        self,
        user_id: str,
        preference: Optional[str] = None,
        budget: Optional[float] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        top_k: int = 5
    ) -> List[Dict]:
        if not self.products:
            return []

        history = self._load_user_history(user_id)
        query_embedding = None
        if preference:
            query_embedding = self.model.encode(preference, convert_to_tensor=True)

        scores = []
        for product in self.products:
            semantic_score = 0.0
            if query_embedding is not None:
                semantic_score = float(util.cos_sim(query_embedding, self.model.encode(product["text"], convert_to_tensor=True))[0].item())
            tag_score = self._tag_match(preference or "", product.get("tags", []), product.get("text", ""))
            novelty_score = 0.2 if product["id"] in history else 1.0
            proximity_score = self._proximity_score(location_lat, location_lon, product.get("shop_lat", 0), product.get("shop_lon", 0))
            budget_score = self._budget_score(product.get("price", 0), budget)
            rating_score = min(1.0, max(0.0, product.get("rating", 3.5) / 5.0))

            final_score = (
                0.35 * semantic_score
                + 0.20 * tag_score
                + 0.15 * rating_score
                + 0.15 * novelty_score
                + 0.10 * proximity_score
                + 0.05 * budget_score
            )

            scores.append({
                "product": product,
                "score": final_score,
                "semantic_score": semantic_score,
                "tag_score": tag_score,
                "novelty_score": novelty_score,
                "proximity_score": proximity_score,
                "budget_score": budget_score,
                "rating_score": rating_score,
            })

        ranked = sorted(scores, key=lambda item: item["score"], reverse=True)[:top_k]
        recommendations = []
        for item in ranked:
            product = item["product"]
            recommendations.append({
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "rating": product["rating"],
                "shop_name": product.get("shop_name", ""),
                "score": round(item["score"], 4),
                "semantic_score": round(item["semantic_score"], 4),
                "tag_score": round(item["tag_score"], 4),
                "novelty_score": round(item["novelty_score"], 4),
                "proximity_score": round(item["proximity_score"], 4),
                "budget_score": round(item["budget_score"], 4),
            })
        return recommendations
