from __future__ import annotations

import json
import logging
from statistics import quantiles
from typing import Dict, List


LOGGER = logging.getLogger("phase6")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)


class MetricsRegistry:
    def __init__(self) -> None:
        self.request_count = 0
        self.success_count = 0
        self.fallback_count = 0
        self.no_result_count = 0
        self.cache_hit_count = 0
        self.error_count = 0
        self._latencies_ms: List[float] = []

    def observe_latency(self, latency_ms: float) -> None:
        self._latencies_ms.append(latency_ms)

    def p95_latency_ms(self) -> float:
        if not self._latencies_ms:
            return 0.0
        if len(self._latencies_ms) < 2:
            return self._latencies_ms[0]
        return float(quantiles(self._latencies_ms, n=100)[94])

    def snapshot(self) -> Dict[str, float]:
        return {
            "request_count": self.request_count,
            "success_count": self.success_count,
            "fallback_count": self.fallback_count,
            "no_result_count": self.no_result_count,
            "cache_hit_count": self.cache_hit_count,
            "error_count": self.error_count,
            "p95_latency_ms": round(self.p95_latency_ms(), 2),
        }


def log_event(payload: dict) -> None:
    safe = dict(payload)
    if "api_key" in safe:
        safe["api_key"] = "***"
    LOGGER.info(json.dumps(safe))

