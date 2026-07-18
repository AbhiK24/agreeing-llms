"""Rate limiter and error classification.

The rate limiter is the guardrail that stops us from bursting into 429s
during the full sweep. If any of these tests regress, the guardrail is
broken and the sweep will get throttled.
"""
from __future__ import annotations

import threading
import time

from rho_collapse.agents import _is_permanent
from rho_collapse.rate_limit import ModelLimits, RateLimiter, _TokenBucket


# ── Token bucket ────────────────────────────────────────────────────────────

def test_token_bucket_paces_calls() -> None:
    """5 calls at 5 tokens/s (burst=1) should take >= ~0.8s."""
    bucket = _TokenBucket(rate=5.0, burst=1)
    t0 = time.time()
    for _ in range(5):
        bucket.acquire()
    elapsed = time.time() - t0
    # 5 tokens at 5/s ≈ 0.8s after burning the initial burst
    assert elapsed >= 0.6, f"bucket did not pace: {elapsed:.2f}s"
    assert elapsed < 2.5, f"bucket over-paced: {elapsed:.2f}s"


def test_token_bucket_allows_burst() -> None:
    """burst tokens are immediately available."""
    bucket = _TokenBucket(rate=1.0, burst=5)
    t0 = time.time()
    for _ in range(5):
        bucket.acquire()
    assert time.time() - t0 < 0.1, "burst should be near-instantaneous"


# ── Concurrency limit ──────────────────────────────────────────────────────

def test_rate_limiter_caps_concurrency() -> None:
    """With max_concurrent=2, only 2 threads should be inside the slot at once."""
    lim = RateLimiter(limits={
        "M": ModelLimits(max_concurrent=2, requests_per_second=1000)
    })
    inside = 0
    peak = 0
    lock = threading.Lock()
    barrier = threading.Event()

    def worker():
        nonlocal inside, peak
        with lim.slot("M"):
            with lock:
                inside += 1
                peak = max(peak, inside)
            # Hold the slot long enough for peers to try acquiring.
            barrier.wait(timeout=0.5)
            with lock:
                inside -= 1

    threads = [threading.Thread(target=worker) for _ in range(6)]
    for t in threads:
        t.start()
    time.sleep(0.1)
    barrier.set()
    for t in threads:
        t.join(timeout=2)
    assert peak <= 2, f"peak in-flight {peak} > cap 2"


def test_rate_limiter_isolates_models() -> None:
    """A slow model must not block calls to a different model."""
    lim = RateLimiter(limits={
        "SLOW": ModelLimits(max_concurrent=1, requests_per_second=1000),
        "FAST": ModelLimits(max_concurrent=4, requests_per_second=1000),
    })
    started = threading.Event()
    fast_ok = threading.Event()

    def slow():
        with lim.slot("SLOW"):
            started.set()
            time.sleep(0.5)

    def fast():
        started.wait(timeout=1)
        with lim.slot("FAST"):
            fast_ok.set()

    t1 = threading.Thread(target=slow)
    t2 = threading.Thread(target=fast)
    t1.start()
    t2.start()
    fast_ok.wait(timeout=1)
    assert fast_ok.is_set(), "FAST model was blocked by SLOW model — cross-model bleed"
    t1.join(timeout=2)
    t2.join(timeout=2)


def test_rate_limiter_releases_slot_on_exception() -> None:
    """If a call raises, the concurrency slot must still be released."""
    lim = RateLimiter(limits={"M": ModelLimits(max_concurrent=1, requests_per_second=1000)})
    try:
        with lim.slot("M"):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    # If the slot leaked, this second acquire would deadlock — use a timer.
    acquired = threading.Event()

    def check():
        with lim.slot("M"):
            acquired.set()

    t = threading.Thread(target=check)
    t.start()
    t.join(timeout=1.0)
    assert acquired.is_set(), "slot was not released after exception — will deadlock the sweep"


# ── Permanent error classification ─────────────────────────────────────────

def test_permanent_error_recognises_auth() -> None:
    assert _is_permanent(Exception("HTTP 401 Unauthorized"))
    assert _is_permanent(Exception("Authentication failed"))
    assert _is_permanent(Exception("invalid api key"))


def test_permanent_error_recognises_bad_model() -> None:
    assert _is_permanent(Exception("model not found"))
    assert _is_permanent(Exception("404: no such model"))
    assert _is_permanent(Exception("Invalid model 'foo'"))


def test_transient_errors_are_not_classified_as_permanent() -> None:
    assert not _is_permanent(Exception("429 Too Many Requests"))
    assert not _is_permanent(Exception("500 Internal Server Error"))
    assert not _is_permanent(Exception("Connection timed out"))
    assert not _is_permanent(Exception("Read timeout"))
