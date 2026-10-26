"""Small single-process login limiter for the local demonstration app."""

from collections import OrderedDict, deque
from math import ceil
from threading import Lock
from time import monotonic
from typing import Callable


class LoginRateLimiter:
    """Limit login POSTs per client IP using a sliding window and cooldown.

    This is intentionally an in-memory, single-process control. It is not a
    distributed rate limiter and must not be presented as production-ready.
    """

    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 60,
        block_seconds: int = 60,
        clock: Callable[[], float] = monotonic,
        max_clients: int = 4096,
    ) -> None:
        if max_attempts < 1 or window_seconds < 1 or block_seconds < 1:
            raise ValueError("Rate-limit values must be positive.")
        if max_clients < 1:
            raise ValueError("max_clients must be positive.")
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.block_seconds = block_seconds
        self.clock = clock
        self.max_clients = max_clients
        self._attempts: OrderedDict[str, deque[float]] = OrderedDict()
        self._blocked_until: dict[str, float] = {}
        self._lock = Lock()

    def try_consume(self, key: str) -> tuple[bool, int]:
        """Reserve one attempt, returning (allowed, retry_after_seconds)."""
        now = self.clock()
        with self._lock:
            blocked_until = self._blocked_until.get(key)
            if blocked_until is not None:
                if now < blocked_until:
                    return False, max(1, ceil(blocked_until - now))
                self._blocked_until.pop(key, None)
                self._attempts.pop(key, None)

            bucket = self._attempts.get(key)
            if bucket is None:
                bucket = deque()
                self._attempts[key] = bucket
            else:
                self._attempts.move_to_end(key)

            cutoff = now - self.window_seconds
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            # Requests beyond the window do not count. The current request is
            # allowed as long as fewer than max_attempts remain in the window.
            if len(bucket) >= self.max_attempts:
                self._blocked_until[key] = now + self.block_seconds
                return False, self.block_seconds

            bucket.append(now)
            if len(bucket) >= self.max_attempts:
                self._blocked_until[key] = now + self.block_seconds

            self._enforce_capacity()
            return True, 0

    def clear(self, key: str) -> None:
        """Clear throttling state after a successful authentication."""
        with self._lock:
            self._attempts.pop(key, None)
            self._blocked_until.pop(key, None)

    def _enforce_capacity(self) -> None:
        while len(self._attempts) > self.max_clients:
            oldest_key, _ = self._attempts.popitem(last=False)
            self._blocked_until.pop(oldest_key, None)
