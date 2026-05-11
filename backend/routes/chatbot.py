from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from auth_middleware import verify_firebase_token
from ai_utils import RAGChatbot

router = APIRouter(prefix="/chatbot", tags=["NLP Chatbot"])
chatbot = RAGChatbot()

class ChatRequest(BaseModel):
    query: str
    include_history: Optional[bool] = True

class ContextItem(BaseModel):
    id: str
    title: str
    text: str
    type: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    retrieved_context: List[ContextItem]

@router.post("/ask", response_model=ChatResponse)
def ask_chatbot(request: ChatRequest, user_info: dict = Depends(verify_firebase_token)):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu hỏi hoặc yêu cầu.")

    # Retrieve relevant documents from knowledge base
    retrieved = chatbot.kb.retrieve(request.query, top_k=4)
    answer = chatbot.generate_answer(request.query, retrieved)

    return {
        "answer": answer,
        "retrieved_context": [
            {
                "id": item["id"],
                "title": item["title"],
                "text": item["text"],
                "type": item["type"],
                "score": item["score"],
            }
            for item in retrieved
        ]
    }
