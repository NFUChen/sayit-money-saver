import functools
import threading
from typing import Callable


def threaded(func: Callable):
    """Decorator to run a function in a separate thread."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

    return wrapper
