"""Thread Manager - Utility để quản lý thread an toàn và nhất quán."""

import threading
from typing import Callable, Optional, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class ThreadManager:
    """Quản lý tạo và theo dõi thread daemon."""
    
    def __init__(self, name_prefix: str = "ThreadManager"):
        self.name_prefix = name_prefix
        self._threads: list[threading.Thread] = []
        self._lock = threading.Lock()
    
    def start_thread(
        self,
        target: Callable,
        args: tuple = (),
        kwargs: dict = None,
        name: str = None,
        daemon: bool = True,
        on_error: Callable[[Exception], None] = None
    ) -> threading.Thread:
        """
        Tạo và start thread mới.
        
        Args:
            target: Function to run
            args: Positional arguments
            kwargs: Keyword arguments
            name: Thread name (auto-generated if None)
            daemon: Whether thread is daemon (default True)
            on_error: Callback when thread raises exception
            
        Returns:
            Thread object
        """
        if kwargs is None:
            kwargs = {}
        
        def wrapped_target():
            try:
                target(*args, **kwargs)
            except Exception as e:
                logger.error(f"Thread {threading.current_thread().name} error: {e}")
                if on_error:
                    on_error(e)
        
        thread_name = name or f"{self.name_prefix}-{len(self._threads)}"
        thread = threading.Thread(
            target=wrapped_target,
            args=(),
            kwargs={},
            name=thread_name,
            daemon=daemon
        )
        
        with self._lock:
            self._threads.append(thread)
        
        thread.start()
        logger.debug(f"Started thread: {thread_name}")
        return thread
    
    def start_thread_simple(self, target: Callable, name: str = None, daemon: bool = True) -> threading.Thread:
        """Shortcut for simple target with no args."""
        return self.start_thread(target, name=name, daemon=daemon)
    
    def wait_for_all(self, timeout: float = None) -> bool:
        """Wait for all managed threads to complete."""
        with self._lock:
            threads = list(self._threads)
        
        all_done = True
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=timeout)
                if thread.is_alive():
                    all_done = False
        
        return all_done
    
    def get_active_count(self) -> int:
        """Get count of alive threads."""
        with self._lock:
            return sum(1 for t in self._threads if t.is_alive())
    
    def cleanup_finished(self) -> int:
        """Remove finished threads from tracking. Returns count removed."""
        with self._lock:
            before = len(self._threads)
            self._threads = [t for t in self._threads if t.is_alive()]
            return before - len(self._threads)


# Global default instance
_default_manager: Optional[ThreadManager] = None


def get_thread_manager(name_prefix: str = "Global") -> ThreadManager:
    """Get or create global thread manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = ThreadManager(name_prefix)
    return _default_manager


def run_in_background(
    target: Callable,
    args: tuple = (),
    kwargs: dict = None,
    name: str = None,
    daemon: bool = True,
    on_error: Callable[[Exception], None] = None
) -> threading.Thread:
    """Convenience function to run a function in background thread."""
    return get_thread_manager().start_thread(
        target, args, kwargs, name, daemon, on_error
    )