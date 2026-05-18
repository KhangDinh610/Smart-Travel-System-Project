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
        # Sử dụng đúng tên model gemini-2.5-flash theo yêu cầu ban đầu
        self.model_name = 'gemini-2.5-flash'

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
                return response.text
            except Exception as e:
                error_msg = str(e)
                # Xử lý lỗi quá tải (503) hoặc quá giới hạn (429)
                if "503" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"Gemini API {model} đang quá tải. Đang thử lại lần {attempt+1} sau {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                return f"Error calling Gemini API: {error_msg}"
        return "Error: Maximum retries reached for Gemini API."

    async def get_chat_response(self, prompt: str, context: str = ""):
        """
        Gửi câu hỏi cho Gemini với ngữ cảnh (RAG).
        """
        full_prompt = f"Context: {context}\n\nUser Question: {prompt}" if context else prompt
        return await self._generate_with_retry(contents=full_prompt)

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
