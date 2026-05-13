import chromadb
from chromadb.utils import embedding_functions
import os

# Đường dẫn lưu trữ dữ liệu ChromaDB
CHROMA_DATA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

class VectorDB:
    def __init__(self, collection_name: str = "shopping_system"):
        # Sử dụng PersistentClient để lưu dữ liệu xuống đĩa
        self.client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        
        # Sử dụng SentenceTransformer làm embedding function mặc định
        # 'paraphrase-multilingual-MiniLM-L12-v2' hỗ trợ tốt tiếng Việt
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def add_documents(self, ids, documents, metadatas=None):
        """Thêm tài liệu vào vector database"""
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_texts, n_results=3, where=None):
        """Tìm kiếm các tài liệu tương đồng nhất"""
        return self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where
        )

    def delete_collection(self, name):
        """Xóa một collection"""
        self.client.delete_collection(name=name)

# Singleton instance
vector_db = VectorDB()