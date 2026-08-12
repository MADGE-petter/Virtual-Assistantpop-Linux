import os
import threading
import time
from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import audio libraries
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
    import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False

# Magpie-TTS voice
MAGPIE_VOICE = "sofia"  # Giọng Sofia cho Magpie-TTS


class AudioService:
    def __init__(self, view=None):
        self.view = view
        self.assistant_name = "Pop"

        # Initialize Local Models
        self.stt_model = None
        if NEMO_AVAILABLE:
            try:
                logger.info("[STT] Loading Parakeet-CTC-0.6B-VI...")
                self.stt_model = asr.models.ASRModel.from_pretrained(model_name="nvidia/stt_vi_parakeet_ctc_0.6b")
                logger.info("[STT] Parakeet-CTC loaded successfully")
            except Exception as e:
                logger.error(f"[STT] Error loading Parakeet: {e}")

        self.tts_model = None
        if MAGPIE_AVAILABLE:
            try:
                logger.info("[TTS] Loading Magpie-TTS (Sofia)...")
                self.tts_model = MagpieTTS(voice=MAGPIE_VOICE)
                logger.info("[TTS] Magpie-TTS loaded successfully")
            except Exception as e:
                logger.error(f"[TTS] Error loading Magpie: {e}")

        # "Cửa một chiều": Lock đảm bảo chỉ 1 hướng hoạt động
        self.gate_lock = threading.Lock()
        self.is_speaking = False  # Loa đang mở?
        self.is_listening = False  # Mic đang mở?

        # Cooldown sau khi nói (giảm nghe chéo)
        self.post_speak_cooldown = 0.3  # 0.3s cooldown
        self.last_speak_end_time = 0

    def speak(self, text, update_ui=True):
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

            logger.info(f"[BOT] {text}")

            # Use Magpie-TTS (Local)
            if MAGPIE_AVAILABLE and PLAYSOUND_AVAILABLE and self.tts_model:
                try:
                    audio_path = self.tts_model.generate(text)
                    playsound.playsound(audio_path, True)
                    return
                except Exception as e:
                    logger.error(f"[Magpie TTS] Error: {e}")

            # No TTS available - just wait
            time.sleep(1)

        finally:
            self.is_speaking = False
            self.last_speak_end_time = time.time()
            self._mic_warmup()
            self.gate_lock.release()

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

            # Try Parakeet-CTC (Local)
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
                    logger.error(f"[STT Parakeet] Error: {e}")

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
