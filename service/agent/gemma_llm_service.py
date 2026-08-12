"""
Gemma 4 E4B LLM Service - Dùng llama-cpp-python
Tối ưu cho: 4GB VRAM + 8GB RAM
"""

import os
from llama_cpp import Llama
from utils.logger import get_logger

logger = get_logger(__name__)


# Global singleton instance
_instance = None


class GemmaLLMService:
    """LLM Service dùng Gemma 4 E4B Q4_0 GGUF"""
    
    def __init__(
        self,
        model_path: str = "agent_gemma/gemma-4-E4B_q4_0-it.gguf",
        n_ctx: int = 2048,
        n_gpu_layers: int = 25,
        n_threads: int = 4,
        n_batch: int = 512,
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.n_threads = n_threads
        self.n_batch = n_batch
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._llm = None
    
    def load(self):
        """Load model vào memory"""
        logger.info(f"[GemmaLLM] Loading model from {self.model_path}...")
        logger.info(f"[GemmaLLM] Config: n_ctx={self.n_ctx}, n_gpu_layers={self.n_gpu_layers}, n_threads={self.n_threads}")
        
        self._llm = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_gpu_layers=self.n_gpu_layers,
            n_threads=self.n_threads,
            n_batch=self.n_batch,
            use_mmap=False,
            verbose=False
        )
        
        logger.info("[GemmaLLM] Model loaded successfully!")
        return self
    
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """
        Generate text từ prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Số token tối đa sinh ra (default: self.max_tokens)
            temperature: Temperature cho sampling (default: self.temperature)
        
        Returns:
            Generated text string
        """
        if not self._llm:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        response = self._llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["<|turn|>", "<|eos|>", "<|channel|>"]
        )
        
        return response['choices'][0]['text'].strip()
    
    def chat(self, messages: list, max_tokens: int = None) -> str:
        """
        Chat completion (đơn giản)
        
        Args:
            messages: List of {"role": "user"/"assistant", "content": "..."}
            max_tokens: Số token tối đa sinh ra
        
        Returns:
            Assistant response string
        """
        if not self._llm:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Build prompt từ messages
        prompt = self._build_prompt(messages)
        return self.generate(prompt, max_tokens=max_tokens)
    
    def _build_prompt(self, messages: list) -> str:
        """Build prompt từ messages (Gemma 4 chat format)"""
        prompt = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                prompt += f"<|turn|>\nuser\n{content}\n"
            elif role == 'assistant':
                prompt += f"<|turn|>\nmodel\n{content}\n"
            elif role == 'system':
                prompt += f"<|system|>\n{content}\n"
        
        prompt += "<|turn|>\nmodel\n"
        return prompt
    
    def is_loaded(self) -> bool:
        """Kiểm tra model đã load chưa"""
        return self._llm is not None
    
    def unload(self):
        """Unload model để giải phóng memory"""
        if self._llm:
            del self._llm
            self._llm = None
            logger.info("[GemmaLLM] Model unloaded")
    
    def get_memory_usage(self) -> dict:
        """Lấy thông tin memory usage"""
        import psutil
        process = psutil.Process()
        return {
            "ram_mb": process.memory_info().rss / 1024 / 1024,
            "vram_mb": 0  # Không đo được trực tiếp
        }


def get_gemma_service() -> GemmaLLMService:
    """Get singleton GemmaLLMService instance"""
    global _instance
    if _instance is None:
        _instance = GemmaLLMService()
        _instance.load()
    return _instance


def reset_gemma_service():
    """Reset singleton instance (for reload)"""
    global _instance
    if _instance is not None:
        _instance.unload()
        _instance = None