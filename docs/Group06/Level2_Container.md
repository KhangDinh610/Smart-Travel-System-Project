# Level 2: Container Diagram - Smart Shopping System (SSS)

Mô tả các thành phần phần mềm (Container) bên trong hệ thống SSS và cách chúng giao tiếp với nhau.

## Sơ đồ (Mermaid)

```mermaid
graph TB
    User((Du khách))

    subgraph "Smart Shopping System (SSS)"
        Frontend[Frontend: Streamlit App]
        Backend[Backend: FastAPI Server]
        SQLite[(SQLite: test.db)]
        ChromaDB[(ChromaDB: Vector Store)]
    end

    subgraph "External Systems"
        Firebase[Firebase Authentication]
        Gemini[Google Gemini AI Service]
    end

    %% Interactions
    User -- "Tương tác giao diện (HTTPS)" --> Frontend
    
    Frontend -- "Gửi yêu cầu REST API" --> Backend
    
    Backend -- "Quản lý dữ liệu SQL (SQLAlchemy)" --> SQLite
    Backend -- "Tìm kiếm tương đồng Vector" --> ChromaDB
    Backend -- "Xác thực tài khoản (Admin SDK)" --> Firebase
    Backend -- "Phân tích AI & RAG" --> Gemini

    %% Styling
    style Frontend fill:#3498db,color:#fff
    style Backend fill:#e67e22,color:#fff
    style SQLite fill:#2ecc71,color:#fff
    style ChromaDB fill:#9b59b6,color:#fff
```

## Chi tiết các Container

### 1. Frontend (Streamlit)
- **Công nghệ:** Python, Streamlit.
- **Trách nhiệm:** Giao diện Chatbot, form nhập lịch sử và khu vực xử lý hình ảnh.

### 2. Backend (FastAPI)
- **Công nghệ:** Python, FastAPI, Uvicorn.
- **Trách nhiệm:** Xử lý logic nghiệp vụ, điều phối yêu cầu đến các dịch vụ AI, quản lý xác thực và thực hiện thuật toán kiểm tra trùng lặp (Duplicate Detection).

### 3. SQLite (Database)
- **Công nghệ:** SQLite 3.
- **Trách nhiệm:** Lưu trữ dữ liệu quan hệ như thông tin cửa hàng, tài khoản người dùng và lịch sử mua sắm.

### 4. ChromaDB (Vector Store)
- **Công nghệ:** ChromaDB.
- **Trách nhiệm:** Lưu trữ và truy vấn các vector đặc trưng của sản phẩm phục vụ tính năng Visual Search.
