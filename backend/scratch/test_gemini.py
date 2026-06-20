import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_service import gemini_service

async def test():
    api_key = os.getenv("GEMINI_API_KEY")
    print("API Key exists:", api_key is not None and len(api_key) > 0)
    if api_key:
        print("API Key first 4 chars:", api_key[:4])
    try:
        resp = await gemini_service.get_chat_response("Hello, are you active?")
        print("Gemini response:", resp)
    except Exception as e:
        print("Gemini test failed:", e)

if __name__ == "__main__":
    asyncio.run(test())
