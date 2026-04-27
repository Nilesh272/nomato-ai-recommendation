from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict


class RateLimiter:
    def __init__(self, max_requests: int = 30, per_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self._events: Dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        bucket = self._events[key]
        while bucket and bucket[0] <= now - self.per_seconds:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True

