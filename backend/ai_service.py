import os
import asyncio
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
        # Khởi tạo client
        self.client = genai.Client(api_key=api_key)
        # Sử dụng model ổn định (1.5-flash hoặc 2.0-flash-exp)
        self.model_name = 'gemini-1.5-flash'

    async def _generate_with_retry(self, contents, model=None):
        """
        Hỗ trợ retry khi gặp lỗi 503 hoặc giới hạn tốc độ.
        """
        if model is None:
            model = self.model_name
            
        max_retries = 3
        retry_delay = 2  # giây
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents
                )
                if not response.text:
                    # Trường hợp bị chặn bởi filter an toàn hoặc lỗi logic model
                    print(f"Gemini API returned empty text. Candidates: {response.candidates}")
                    return "AI: Xin lỗi, tôi không thể trả lời câu hỏi này vì lý do an toàn hoặc kỹ thuật."
                return response.text
            except Exception as e:
                error_msg = str(e)
                # Xử lý lỗi quá tải (503) hoặc quá giới hạn (429)
                if "503" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"Gemini API {model} đang quá tải (Lần {attempt+1}). Thử lại sau {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                print(f"Gemini API Final Error: {error_msg}")
                return "" # Trả về rỗng để caller xử lý tùy theo ngữ cảnh (dịch hay chat)
        return ""

    async def get_chat_response(self, prompt: str, context: str = ""):
        """
        Gửi câu hỏi cho Gemini với ngữ cảnh (RAG).
        """
        full_prompt = f"Bạn là một trợ lý mua sắm quà lưu niệm thông minh. Dựa vào thông tin sau đây để trả lời câu hỏi của người dùng.\nNgữ cảnh: {context}\n\nCâu hỏi của người dùng: {prompt}" if context else prompt
        
        response = await self._generate_with_retry(contents=full_prompt)
        
        if not response:
            return "Xin lỗi, hiện tại hệ thống AI đang bận hoặc gặp sự cố kết nối. Bạn vui lòng thử lại sau giây lát nhé!"
            
        return response

    async def analyze_product_image(self, image_bytes: bytes):
        """
        Sử dụng tính năng Multimodal của Gemini để phân tích ảnh sản phẩm.
        """
        contents = [
            "Mô tả sản phẩm này bao gồm tên, thương hiệu và định lượng nếu có.",
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        ]
        return await self._generate_with_retry(contents=contents)

# Singleton instance
gemini_service = GeminiService()
