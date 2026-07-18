"""Per-model rate limiter.

Two constraints per model:
  1. `max_concurrent`  — at most N in-flight calls at once (semaphore).
  2. `requests_per_second`  — sustained throughput cap (token bucket).

Both are enforced by `RateLimiter.acquire(model_name)`. Callers should
wrap the API call in a `with limiter.slot(model_name):` block.
"""
from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class ModelLimits:
    max_concurrent: int = 4
    requests_per_second: float = 5.0


class _TokenBucket:
    """Standard leaky-bucket rate limiter.

    Tokens refill at `rate` per second, up to `burst` capacity. Each
    `acquire()` blocks until a token is available.
    """

    def __init__(self, rate: float, burst: int) -> None:
        self.rate = float(rate)
        self.burst = int(max(burst, 1))
        self.tokens = float(self.burst)
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.time()
                elapsed = now - self.last_refill
                self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
                self.last_refill = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                wait = (1.0 - self.tokens) / self.rate
            # Sleep OUTSIDE the lock so other threads can refill their view.
            time.sleep(max(wait, 0.001))


class RateLimiter:
    """Aggregates per-model concurrency + token buckets.

    Thread-safe. The `slot(model_name)` context manager blocks until both
    (a) a concurrency slot is available and (b) the token bucket allows the
    next call. Failures (`raise` inside the with-block) release the slot.
    """

    def __init__(self, limits: dict[str, ModelLimits] | None = None,
                 default: ModelLimits | None = None) -> None:
        self._default = default or ModelLimits()
        self._limits: dict[str, ModelLimits] = dict(limits or {})
        self._semaphores: dict[str, threading.Semaphore] = {}
        self._buckets: dict[str, _TokenBucket] = {}
        self._registry_lock = threading.Lock()

    def _get(self, model_name: str) -> tuple[threading.Semaphore, _TokenBucket]:
        with self._registry_lock:
            if model_name not in self._semaphores:
                lim = self._limits.get(model_name, self._default)
                self._semaphores[model_name] = threading.Semaphore(lim.max_concurrent)
                self._buckets[model_name] = _TokenBucket(
                    rate=lim.requests_per_second,
                    burst=max(lim.max_concurrent, 1),
                )
            return self._semaphores[model_name], self._buckets[model_name]

    @contextmanager
    def slot(self, model_name: str):
        sem, bucket = self._get(model_name)
        bucket.acquire()          # rate-limit first (may sleep)
        sem.acquire()             # then reserve a concurrency slot
        try:
            yield
        finally:
            sem.release()
