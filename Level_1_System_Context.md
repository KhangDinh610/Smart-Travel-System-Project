graph TD
     User((Du khách / Người dùng))
     subgraph SSS [Smart Shopping System]
         System[Hệ thống SSS]
    6     end
    7
    8     Firebase[Firebase Auth/Rest API]
    9     Gemini[Google Gemini API]
   10     GCPVision[GCP Vision API / CLIP Model]
   11
   12     User -- "Tìm kiếm sản phẩm, Chatbot, Quét ảnh, Xem bản đồ" --> System
   13     System -- "Xác thực người dùng" --> Firebase
   14     System -- "Phân tích hình ảnh & Trả lời Chatbot" --> Gemini
   15     System -- "Trích xuất Vector hình ảnh" --> GCPVision