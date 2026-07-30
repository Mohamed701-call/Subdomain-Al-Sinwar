"""Reusable retry decorator for flaky network sources (e.g. crt.sh, which
times out often on large domains)."""

import functools
import sys
import time
from typing import Tuple, Type


def retry(times: int = 3, delay: float = 3.0, backoff: float = 1.0,
          exceptions: Tuple[Type[BaseException], ...] = (Exception,)):
    """
    @retry(times=3, delay=3, exceptions=(requests.exceptions.Timeout,))
    def fetch(...): ...

    Retries up to `times` attempts, sleeping `delay * attempt_number *
    backoff` seconds between tries. Re-raises the last exception if every
    attempt fails.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < times:
                        wait = delay * attempt * backoff
                        print(f"[!] {func.__name__} failed (attempt {attempt}/{times}): {e}. "
                              f"Retrying in {wait:.1f}s...", file=sys.stderr)
                        time.sleep(wait)
            raise last_exc
        return wrapper
    return decorator