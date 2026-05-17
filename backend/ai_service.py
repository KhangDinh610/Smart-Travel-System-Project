import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
        # Khởi tạo client thay vì dùng configure
        self.client = genai.Client(api_key=api_key)

    async def get_chat_response(self, prompt: str, context: str = ""):
        """
        Gửi câu hỏi cho Gemini với ngữ cảnh (RAG).
        """
        full_prompt = f"Context: {context}\n\nUser Question: {prompt}" if context else prompt
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"

    async def analyze_product_image(self, image_bytes: bytes):
        """
        Sử dụng tính năng Multimodal của Gemini để phân tích ảnh sản phẩm.
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    "Mô tả sản phẩm này bao gồm tên, thương hiệu và định lượng nếu có.",
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                ]
            )
            return response.text
        except Exception as e:
            return f"Error analyzing image: {str(e)}"

# Singleton instance
gemini_service = GeminiService()
