import os
import asyncio
import threading
import time
import hashlib
import json
import re
from pathlib import Path

# Try to import audio libraries
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import nemo.collections.asr as asr
    NEMO_AVAILABLE = True
except ImportError:
    NEMO_AVAILABLE = False

try:
    from magpie_tts import MagpieTTS
    MAGPIE_AVAILABLE = True
except ImportError:
    MAGPIE_AVAILABLE = False

try:
    import gtts
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False

# Vietnamese voice for Edge TTS
EDGE_VOICE = "vi-VN-HoaiMyNeural"  # Giọng nữ
MAGPIE_VOICE = "sofia" # Giọng Sofia cho Magpie-TTS

# Cache directory for TTS audio
CACHE_DIR = Path("cache/tts")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_INDEX_FILE = CACHE_DIR / "index.json"

def _get_cache_size_mb():
    """Get current cache size in MB"""
    total = 0
    for f in CACHE_DIR.glob("*.mp3"):
        total += f.stat().st_size
    return total / (1024 * 1024)

def _cleanup_cache():
    """Clean up orphaned cache files only (files not in index)"""
    index = _load_cache_index()
    removed = 0
    
    # Clean up orphaned files (files not in index)
    indexed_files = set(index.values())
    for f in CACHE_DIR.glob("*.mp3"):
        if f.name not in indexed_files:
            f.unlink(missing_ok=True)
            removed += 1
    
    if removed:
        _save_cache_index(index)
        print(f"[Cache] Cleaned up {removed} orphaned files, size: {_get_cache_size_mb():.1f} MB")

def _load_cache_index():
    """Load cache index from disk"""
    if CACHE_INDEX_FILE.exists():
        try:
            with open(CACHE_INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_cache_index(index):
    """Save cache index to disk"""
    try:
        with open(CACHE_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except:
        pass

def _get_cache_key(text, voice=EDGE_VOICE):
    """Generate cache key from text and voice"""
    content = f"{voice}:{text}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def _get_cached_audio(text, voice=EDGE_VOICE):
    """Get cached audio file path if exists"""
    index = _load_cache_index()
    key = _get_cache_key(text, voice)
    if key in index:
        cache_file = CACHE_DIR / index[key]
        if cache_file.exists():
            return str(cache_file)
    return None

def _cache_audio(text, audio_file, voice=EDGE_VOICE):
    """Cache audio file"""
    index = _load_cache_index()
    key = _get_cache_key(text, voice)
    cache_file = CACHE_DIR / f"{key}.mp3"
    try:
        import shutil
        shutil.copy2(audio_file, cache_file)
        index[key] = f"{key}.mp3"
        _save_cache_index(index)
        # Periodic cleanup (every 10 new items)
        if len(index) % 10 == 0:
            _cleanup_cache()
    except Exception as e:
        print(f"[Cache] Error caching audio: {e}")


class AudioService: 
    def __init__(self, view=None, auto_learn=True, use_word_tts=False):
        self.view = view
        self.assistant_name = "Pop"
        self.auto_learn = auto_learn  # Tự động cache câu mới
        self.use_word_tts = use_word_tts  # Bật word-level TTS
        self._pending_cache = []  # Queue các câu cần cache
        self._cache_thread = None
        
        # Initialize Local Models
        self.stt_model = None
        if NEMO_AVAILABLE:
            try:
                print("[STT] Loading Parakeet-CTC-0.6B-VI...")
                self.stt_model = asr.models.ASRModel.from_pretrained(model_name="nvidia/stt_vi_parakeet_ctc_0.6b")
                print("[STT] Parakeet-CTC loaded successfully")
            except Exception as e:
                print(f"[STT] Error loading Parakeet: {e}")

        self.tts_model = None
        if MAGPIE_AVAILABLE:
            try:
                print("[TTS] Loading Magpie-TTS (Sofia)...")
                self.tts_model = MagpieTTS(voice=MAGPIE_VOICE)
                print("[TTS] Magpie-TTS loaded successfully")
            except Exception as e:
                print(f"[TTS] Error loading Magpie: {e}")
        
        _cleanup_cache()
        
        # "Cửa một chiều": Lock đảm bảo chỉ 1 hướng hoạt động
        self.gate_lock = threading.Lock()
        self.is_speaking = False  # Loa đang mở?
        self.is_listening = False  # Mic đang mở?
        
        # Cooldown sau khi nói (giảm nghe chéo)
        self.post_speak_cooldown = 0.3  # 0.3s cooldown
        self.last_speak_end_time = 0
        
    async def _edge_tts_speak_async(self, text, filename="sound.mp3"):
        """Async function để tạo audio bằng Edge TTS"""
        try:
            communicate = edge_tts.Communicate(text, EDGE_VOICE)
            await communicate.save(filename)
            return True
        except Exception as e:
            print(f"[Edge TTS] Error: {e}")
            return False
    
    def _edge_tts_speak(self, text, filename="sound.mp3"):
        """Sync wrapper cho Edge TTS"""
        try:
            asyncio.run(self._edge_tts_speak_async(text, filename))
            return True
        except Exception as e:
            print(f"[Edge TTS] Error: {e}")
            return False
        
    def speak(self, text, update_ui=True):
        # Queue for background caching (auto-learn)
        self._queue_for_cache(text)
        
        threading.Thread(
            target=self._speak_worker,
            args=(text, update_ui),
            daemon=True
        ).start()
        return True
    
    def _speak_worker(self, text, update_ui):
        self.gate_lock.acquire()
        self.is_speaking = True
        
        try:
            if update_ui and self.view:
                self.view.update_bot_text(text)
            
            print(f"[BOT] {text}")
            
            # 1. Try sentence-level cache first
            cached_file = _get_cached_audio(text, MAGPIE_VOICE if MAGPIE_AVAILABLE else EDGE_VOICE)
            if cached_file:
                print(f"[TTS Cache] Sentence cache hit")
                if PLAYSOUND_AVAILABLE:
                    playsound.playsound(cached_file, True)
                return
            
            # 2. Try Magpie-TTS (Local)
            if MAGPIE_AVAILABLE and PLAYSOUND_AVAILABLE:
                try:
                    audio_path = self.tts_model.generate(text)
                    playsound.playsound(audio_path, True)
                    _cache_audio(text, audio_path, MAGPIE_VOICE)
                    return
                except Exception as e:
                    print(f"[Magpie TTS] Error: {e}")

            # 3. Try word-level TTS (if enabled)
            if self.use_word_tts and self._speak_word_by_word(text):
                return
            
            # 4. Fallback to Edge TTS (sentence level)
            if EDGE_TTS_AVAILABLE and PLAYSOUND_AVAILABLE:
                if self._edge_tts_speak(text, "sound.mp3"):
                    playsound.playsound("sound.mp3", True)
                    _cache_audio(text, "sound.mp3", EDGE_VOICE)
                    if os.path.exists("sound.mp3"):
                        os.remove("sound.mp3")
                    return
            
            # 5. Fallback to gTTS
            if GTTS_AVAILABLE and PLAYSOUND_AVAILABLE:
                self._speak_gtts(text)
            else:
                time.sleep(1)
            
        finally:
            self.is_speaking = False
            self.last_speak_end_time = time.time()
            self._mic_warmup()
            self.gate_lock.release()
    
    def _split_to_words(self, text):
        """Split Vietnamese text into words"""
        words = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
        return [w for w in words if w.strip()]
    
    def _speak_word_by_word(self, text):
        """Speak by concatenating cached words"""
        words = self._split_to_words(text)
        cached_files = []
        missing_words = []
        
        for word in words:
            cached = _get_cached_audio(word, EDGE_VOICE)
            if cached:
                cached_files.append(cached)
            else:
                missing_words.append(word)
        
        # If all words cached, play concatenated
        if not missing_words and cached_files:
            print(f"[Word-TTS] Playing {len(words)} words from cache")
            for wav_file in cached_files:
                if PLAYSOUND_AVAILABLE:
                    playsound.playsound(wav_file, True)
            return True
        
        # Queue missing words for caching
        for word in missing_words:
            self._queue_for_cache(word)
        
        return False
    
    def _queue_for_cache(self, text):
        if self.auto_learn and not _get_cached_audio(text, EDGE_VOICE):
            self._pending_cache.append(text)
            if self._cache_thread is None or not self._cache_thread.is_alive():
                self._cache_thread = threading.Thread(target=self._background_cache_worker, daemon=True)
                self._cache_thread.start()
    
    def _background_cache_worker(self):
        while self._pending_cache:
            text = self._pending_cache.pop(0)
            try:
                if not _get_cached_audio(text, EDGE_VOICE):
                    print(f"[Auto-Learn] Caching: {text[:30]}...")
                    asyncio.run(self._edge_tts_speak_async(text, "temp_cache.mp3"))
                    _cache_audio(text, "temp_cache.mp3", EDGE_VOICE)
                    if os.path.exists("temp_cache.mp3"):
                        os.remove("temp_cache.mp3")
            except Exception as e:
                print(f"[Auto-Learn] Error caching: {e}")
            time.sleep(0.5)
    
    def _speak_gtts(self, text):
        """Fallback sang gTTS"""
        try:
            tts = gtts.gTTS(text=text, lang="vi", slow=False)
            tts.save("sound.mp3")
            playsound.playsound("sound.mp3", True)
            if os.path.exists("sound.mp3"):
                os.remove("sound.mp3")
        except Exception as e:
            print(f"[gTTS] Error: {e}")
            time.sleep(1)
    
    def _mic_warmup(self):
        time.sleep(0.1)  
    
    def listen(self, timeout=12, phrase_time_limit=10):
        if self.is_listening:
            return None
        
        time_since_speak = time.time() - self.last_speak_end_time
        if time_since_speak < self.post_speak_cooldown:
            return None
        got_lock = self.gate_lock.acquire(timeout=0.5)
        
        if not got_lock:
            return None
        
        try:
            self.is_listening = True
            
            if self.view:
                self.view.update_user_text("Đang lắng nghe...")
            
            # 1. Try Parakeet-CTC (Local)
            if NEMO_AVAILABLE and self.stt_model:
                try:
                    import sounddevice as sd
                    import numpy as np
                    import soundfile as sf
                    
                    # Record audio
                    fs = 16000
                    duration = phrase_time_limit
                    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
                    sd.wait()
                    
                    # Save to temp file for NeMo
                    temp_file = "temp_listen.wav"
                    sf.write(temp_file, recording.flatten(), fs)
                    
                    # Transcribe
                    transcriptions = self.stt_model.transcribe([temp_file])
                    text = transcriptions[0]
                    
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        
                    if text and text.strip():
                        return text
                except Exception as e:
                    print(f"[STT Parakeet] Error: {e}")

            # 2. Fallback to SpeechRecognition
            if SR_AVAILABLE:
                try:
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        r.pause_threshold = 0.8
                        r.energy_threshold = 300
                        audio = r.listen(source, phrase_time_limit=phrase_time_limit, timeout=timeout)
                        return r.recognize_google(audio, language="vi-VN")
                except Exception as e:
                    print(f"[STT Fallback] Error: {e}")
            
            return "..."
        finally:
            self.is_listening = False
            self.gate_lock.release()
    
    def get_text_with_retry(self, max_retries=3, retry_message=None):
        """Lấy text với cơ chế retry."""
        if retry_message is None:
            retry_message = f"{self.assistant_name} không nghe rõ, bạn có thể nói lại không?"
        
        for i in range(max_retries):
            text = self.listen()
            if text and text != "..." and text != 0:
                return text.lower()
            elif i < max_retries - 1:
                self.speak(retry_message)
        
        self.speak("Tôi không nghe rõ. Tôi sẽ hỏi lại sau.")
        return "..."
    
    def wait_until_speaking_done(self):
        while self.is_speaking:
            time.sleep(0.05)

    def is_gate_open(self):
        return not self.is_speaking
    
    def _mic_warmup(self):
        time.sleep(0.1)  
    
    def listen(self, timeout=12, phrase_time_limit=10):
        if self.is_listening:
            return None
        
        # Kiểm tra cooldown sau khi bot nói
        time_since_speak = time.time() - self.last_speak_end_time
        if time_since_speak < self.post_speak_cooldown:
            return None
        got_lock = self.gate_lock.acquire(timeout=0.5)
        
        if not got_lock:
            return None
        
        try:
            self.is_listening = True
            
            if self.view:
                self.view.update_user_text("Đang lắng nghe...")
            
            # 1. Try Parakeet-CTC (Local)
            if NEMO_AVAILABLE and self.stt_model:
                try:
                    import sounddevice as sd
                    import numpy as np
                    import soundfile as sf
                    
                    # Record audio
                    fs = 16000
                    duration = phrase_time_limit
                    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
                    sd.wait()
                    
                    # Save to temp file for NeMo
                    temp_file = "temp_listen.wav"
                    sf.write(temp_file, recording.flatten(), fs)
                    
                    # Transcribe
                    transcriptions = self.stt_model.transcribe([temp_file])
                    text = transcriptions[0]
                    
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        
                    if text and text.strip():
                        return text
                except Exception as e:
                    print(f"[STT Parakeet] Error: {e}")

            # 2. Fallback to SpeechRecognition
            if SR_AVAILABLE:
                try:
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        r.pause_threshold = 0.8
                        r.energy_threshold = 300
                        audio = r.listen(source, phrase_time_limit=phrase_time_limit, timeout=timeout)
                        return r.recognize_google(audio, language="vi-VN")
                except Exception as e:
                    print(f"[STT Fallback] Error: {e}")
            
            return "..."
        finally:
            self.is_listening = False
            self.gate_lock.release()
    
    def get_text_with_retry(self, max_retries=3, retry_message=None):
        """Lấy text với cơ chế retry."""
        if retry_message is None:
            retry_message = f"{self.assistant_name} không nghe rõ, bạn có thể nói lại không?"
        
        for i in range(max_retries):
            text = self.listen()
            if text and text != "..." and text != 0:
                return text.lower()
            elif i < max_retries - 1:
                self.speak(retry_message)
        
        self.speak("Tôi không nghe rõ. Tôi sẽ hỏi lại sau.")
        return "..."
    
    def wait_until_speaking_done(self):
        while self.is_speaking:
            time.sleep(0.05)

    def is_gate_open(self):
        return not self.is_speaking
