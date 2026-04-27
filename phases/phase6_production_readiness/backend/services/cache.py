from __future__ import annotations

import time
from typing import Dict, Optional, Tuple


class TTLCache:
    def __init__(self, ttl_seconds: int = 120) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Tuple[float, dict]] = {}

    def get(self, key: str) -> Optional[dict]:
        value = self._store.get(key)
        if value is None:
            return None
        expires_at, payload = value
        if expires_at < time.time():
            del self._store[key]
            return None
        return payload

    def set(self, key: str, payload: dict) -> None:
        self._store[key] = (time.time() + self.ttl_seconds, payload)

