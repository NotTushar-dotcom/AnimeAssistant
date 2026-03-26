"""
Aara Async Utilities
Threading and async helpers.
"""

import asyncio
import functools
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, TypeVar, Optional
from queue import Queue

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Global thread pool
_executor: Optional[ThreadPoolExecutor] = None


def get_executor() -> ThreadPoolExecutor:
    """Get or create global thread pool executor."""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="aara_")
    return _executor


def run_async(coro) -> Any:
    """
    Run an async coroutine from sync code.

    Args:
        coro: Coroutine to run

    Returns:
        Result of the coroutine
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # Already in async context - use nest_asyncio or create task
        return asyncio.ensure_future(coro)
    else:
        # Create new event loop
        return asyncio.run(coro)


def run_in_thread(func: Callable[..., T], *args, **kwargs) -> Future:
    """
    Run a function in a background thread.

    Args:
        func: Function to run
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Future object
    """
    executor = get_executor()
    return executor.submit(func, *args, **kwargs)


def debounce(wait: float) -> Callable:
    """
    Decorator to debounce function calls.

    Args:
        wait: Wait time in seconds

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        timer: Optional[threading.Timer] = None
        lock = threading.Lock()

        @functools.wraps(func)
        def debounced(*args, **kwargs):
            nonlocal timer

            def call():
                nonlocal timer
                timer = None
                func(*args, **kwargs)

            with lock:
                if timer is not None:
                    timer.cancel()
                timer = threading.Timer(wait, call)
                timer.start()

        return debounced
    return decorator


def throttle(interval: float) -> Callable:
    """
    Decorator to throttle function calls.

    Args:
        interval: Minimum interval between calls in seconds

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        last_call = [0.0]
        lock = threading.Lock()

        @functools.wraps(func)
        def throttled(*args, **kwargs):
            import time
            with lock:
                now = time.time()
                if now - last_call[0] >= interval:
                    last_call[0] = now
                    return func(*args, **kwargs)
                return None

        return throttled
    return decorator


class ThreadSafeQueue:
    """Thread-safe queue with additional utilities."""

    def __init__(self, maxsize: int = 0):
        """
        Initialize queue.

        Args:
            maxsize: Maximum queue size (0 for unlimited)
        """
        self._queue = Queue(maxsize=maxsize)

    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        """Put an item in the queue."""
        self._queue.put(item, block=block, timeout=timeout)

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """Get an item from the queue."""
        return self._queue.get(block=block, timeout=timeout)

    def empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.empty()

    def qsize(self) -> int:
        """Get queue size."""
        return self._queue.qsize()

    def clear(self) -> None:
        """Clear all items from queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except Exception:
                break


class BackgroundTask:
    """Runs a function repeatedly in a background thread."""

    def __init__(self, func: Callable, interval: float = 1.0):
        """
        Initialize background task.

        Args:
            func: Function to run
            interval: Interval between runs in seconds
        """
        self._func = func
        self._interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the background task."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.debug(f"Started background task: {self._func.__name__}")

    def stop(self) -> None:
        """Stop the background task."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self._interval * 2)
            self._thread = None
        logger.debug(f"Stopped background task: {self._func.__name__}")

    def _run_loop(self) -> None:
        """Main loop for the background task."""
        import time
        while self._running:
            try:
                self._func()
            except Exception as e:
                logger.error(f"Background task error: {e}")
            time.sleep(self._interval)

    @property
    def is_running(self) -> bool:
        """Check if task is running."""
        return self._running


def cleanup_executor() -> None:
    """Clean up the global thread pool executor."""
    global _executor
    if _executor is not None:
        _executor.shutdown(wait=True)
        _executor = None
