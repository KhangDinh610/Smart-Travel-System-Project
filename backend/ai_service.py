import os
import asyncio
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
if not load_dotenv():
    # If not found in current dir, try parent dir
    root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(root_env):
        load_dotenv(root_env)

class GeminiError(Exception):
    """Base class for Gemini service errors."""
    def __init__(self, message, details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class GeminiQuotaError(GeminiError):
    """Exception raised when Gemini API quota is exceeded."""
    def __init__(self, message, reset_time_msg="vui lòng thử lại sau 1 phút"):
        super().__init__(message)
        self.reset_time_msg = reset_time_msg

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("\n" + "="*50)
            print("CRITICAL ERROR: GEMINI_API_KEY is missing or invalid!")
            print("Please set a valid GEMINI_API_KEY in your .env file.")
            print("Get one at: https://ai.google.dev/gemini-api/docs/api-key")
            print("="*50 + "\n")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
        
        self.model_name = 'gemini-2.5-flash'
        self.last_usage_metadata = None
        self.cumulative_usage = {
            'prompt_tokens': 0,
            'candidates_tokens': 0,
            'total_tokens': 0
        }

    def get_last_cost(self) -> float:
        """Calculate the cost of the last API call in USD."""
        if not self.last_usage_metadata:
            return 0.0
        prompt_tokens = self.last_usage_metadata.prompt_token_count or 0
        candidates_tokens = self.last_usage_metadata.candidates_token_count or 0
        return (prompt_tokens * 0.075 + candidates_tokens * 0.30) / 1000000.0

    def get_cumulative_cost(self) -> float:
        """Calculate the total cost of all API calls in USD."""
        prompt_tokens = self.cumulative_usage['prompt_tokens']
        candidates_tokens = self.cumulative_usage['candidates_tokens']
        return (prompt_tokens * 0.075 + candidates_tokens * 0.30) / 1000000.0

    def reset_cumulative_usage(self):
        """Reset cumulative token counters."""
        self.cumulative_usage = {
            'prompt_tokens': 0,
            'candidates_tokens': 0,
            'total_tokens': 0
        }

    async def _generate_with_retry(self, contents, model=None):
        """
        Hỗ trợ retry khi gặp lỗi 503 hoặc giới hạn tốc độ (429).
        """
        if not self.client:
            raise GeminiError("Gemini client is not initialized due to missing API key.")

        if model is None:
            model = self.model_name
            
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents
                )
                
                # Track token usage
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    self.last_usage_metadata = response.usage_metadata
                    self.cumulative_usage['prompt_tokens'] += response.usage_metadata.prompt_token_count or 0
                    self.cumulative_usage['candidates_tokens'] += response.usage_metadata.candidates_token_count or 0
                    self.cumulative_usage['total_tokens'] += response.usage_metadata.total_token_count or 0

                if not response.text:
                    print(f"Gemini API returned empty text. Candidates: {response.candidates}")
                    return "AI: Xin lỗi, tôi không thể trả lời câu hỏi này vì lý do an toàn hoặc kỹ thuật."
                return response.text
            except Exception as e:
                error_msg = str(e)
                # Xử lý lỗi quá giới hạn (429)
                if "429" in error_msg:
                    if attempt < max_retries - 1:
                        # Wait longer for quota recovery (e.g. 15s, 25s, 35s...)
                        wait_time = 15 + attempt * 10
                        print(f"Gemini API {model} rate limited (429). Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    reset_suggestion = "vui lòng thử lại sau khoảng 1-2 phút (giới hạn RPM) hoặc ngày mai (giới hạn RPD)"
                    raise GeminiQuotaError(f"Hết lượt sử dụng AI (Quota Exceeded): {error_msg}", reset_suggestion)
                
                # Xử lý lỗi quá tải (503)
                if "503" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"Gemini API {model} overloaded (503). Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    raise GeminiError("Hệ thống AI hiện đang quá tải và không thể phản hồi sau nhiều lần thử.", error_msg)
                
                print(f"Gemini API Final Error: {error_msg}")
                raise GeminiError(f"Lỗi AI không xác định: {error_msg}", error_msg)
        
        raise GeminiError("Không nhận được phản hồi từ AI sau nhiều lần thử.")

    async def get_chat_response(self, prompt: str, context: str = ""):
        """
        Gửi câu hỏi cho Gemini với ngữ cảnh (RAG).
        """
        full_prompt = f"Bạn là một trợ lý mua sắm quà lưu niệm thông minh. Dựa vào thông tin sau đây để trả lời câu hỏi của người dùng.\nNgữ cảnh: {context}\n\nCâu hỏi của người dùng: {prompt}" if context else prompt
        
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
