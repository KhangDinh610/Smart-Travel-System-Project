import chromadb
from chromadb.utils import embedding_functions
import os

# Đường dẫn lưu trữ dữ liệu ChromaDB
CHROMA_DATA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

class VectorDB:
    def __init__(self, default_collection_name: str = "shopping_system"):
        # Sử dụng PersistentClient để lưu dữ liệu xuống đĩa
        self.client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        
        # Sử dụng SentenceTransformer làm embedding function mặc định
        # 'paraphrase-multilingual-MiniLM-L12-v2' hỗ trợ tốt tiếng Việt
        self.default_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name=default_collection_name,
            embedding_function=self.default_embedding_fn
        )

    def get_collection(self, name: str, embedding_function=None):
        """Lấy hoặc tạo một collection cụ thể"""
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=embedding_function
        )

    def add_documents(self, ids, documents, metadatas=None, collection=None):
        """Thêm tài liệu vào vector database (sử dụng embedding function của collection)"""
        target_collection = collection or self.collection
        target_collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def add_with_embeddings(self, ids, embeddings, metadatas=None, documents=None, collection_name="product_images"):
        """Thêm tài liệu với vector có sẵn (không dùng embedding function nội bộ)"""
        # Khi dùng embeddings có sẵn, collection không nên có embedding_function
        collection = self.client.get_or_create_collection(name=collection_name)
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query(self, query_texts=None, query_embeddings=None, n_results=3, where=None, collection_name=None):
        """Tìm kiếm các tài liệu tương đồng nhất"""
        if collection_name:
            collection = self.client.get_collection(name=collection_name)
        else:
            collection = self.collection

        if query_embeddings:
            return collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )
        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where
        )

    def reset_collections(self):
        """Xóa và khởi tạo lại các collection chính"""
        try:
            self.client.delete_collection(name="shopping_system")
        except:
            pass
        try:
            self.client.delete_collection(name="product_images")
        except:
            pass
            
        self.collection = self.client.get_or_create_collection(
            name="shopping_system",
            embedding_function=self.default_embedding_fn
        )
        # Re-create product_images without default embedding function (we provide them)
        self.client.get_or_create_collection(name="product_images")
        print("VectorDB collections reset successfully.")

    def delete_collection(self, name):
        """Xóa một collection"""
        self.client.delete_collection(name=name)

# Singleton instance
vector_db = VectorDB()