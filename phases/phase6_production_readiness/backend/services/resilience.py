from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    cooldown_seconds: int = 30
    failure_count: int = 0
    open_until_epoch: float = 0.0

    def allow_request(self) -> bool:
        return time.time() >= self.open_until_epoch

    def record_success(self) -> None:
        self.failure_count = 0
        self.open_until_epoch = 0.0

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.open_until_epoch = time.time() + self.cooldown_seconds

