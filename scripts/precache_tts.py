"""
Pre-cache common TTS phrases for offline use
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import edge_tts
from pathlib import Path
from service.AudioService import _cache_audio, CACHE_DIR, EDGE_VOICE

# Common phrases to pre-cache
COMMON_PHRASES = [
    "Xin chào, tôi là trợ lý ảo Pop",
    "Rất vui được gặp bạn",
    "Tôi có thể giúp gì cho bạn?",
    "Xin lỗi, tôi không hiểu ý bạn",
    "Bạn có thể nói lại không?",
    "Đang xử lý yêu cầu của bạn",
    "Hoàn tất",
    "Có lỗi xảy ra",
    "Tạm biệt, hẹn gặp lại",
    "Chúc bạn một ngày tốt lành",
    "Bật điều hòa",
    "Tắt đèn",
    "Mở trình duyệt",
    "Kiểm tra nhiệt độ",
    "Thời tiết hôm nay như thế nào?",
    "Giờ là mấy giờ?",
    "Hẹn giờ 5 phút",
    "Nhắc nhở uống nước",
    "Đọc tin nhắn",
    "Gửi tin nhắn",
]

async def generate_and_cache(text, voice=EDGE_VOICE):
    """Generate and cache a single phrase"""
    try:
        filename = f"temp_{hash(text)}.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)
        _cache_audio(text, filename, voice)
        os.remove(filename)
        print(f"✓ Cached: {text[:30]}...")
        return True
    except Exception as e:
        print(f"✗ Failed: {text[:30]}... - {e}")
        return False

async def main():
    print(f"Pre-caching {len(COMMON_PHRASES)} phrases...")
    print(f"Cache dir: {CACHE_DIR}")
    print(f"Voice: {EDGE_VOICE}")
    print("-" * 50)
    
    success = 0
    for phrase in COMMON_PHRASES:
        if await generate_and_cache(phrase):
            success += 1
    
    print("-" * 50)
    print(f"Done! {success}/{len(COMMON_PHRASES)} phrases cached")
    
    # List cached files
    import json
    index_file = CACHE_DIR / "index.json"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        print(f"Total cached: {len(index)} files")
        total_size = sum((CACHE_DIR / v).stat().st_size for v in index.values())
        print(f"Total size: {total_size / 1024:.1f} KB")

if __name__ == "__main__":
    import os
    asyncio.run(main())