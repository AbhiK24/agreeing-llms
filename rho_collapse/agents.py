"""LLM client abstraction.

Four providers, one interface: `.complete(prompt) -> str`.
Web search, tools, function calling are all explicitly disabled — we want
raw model outputs so that inter-agent correlation isn't confounded by
retrieval calls sharing the same web sources.
"""
from __future__ import annotations

import os
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class AgentError(Exception):
    """Raised when an agent cannot produce a response after retries."""


class PermanentAgentError(AgentError):
    """Raised when a call fails with a non-retryable error (auth, invalid
    model, bad request). Skips retry entirely."""


# Substrings that mark an error as non-retryable. We check on stringified
# exception messages because SDK exception hierarchies differ across
# providers and stringly-typed matching is the least-fragile common ground.
_PERMANENT_MARKERS = (
    "401", "403", "404",
    "authentication",
    "unauthorized",
    "invalid api key",
    "no such model",
    "model not found",
    "invalid model",
    "invalid request",
)


def _is_permanent(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(m in msg for m in _PERMANENT_MARKERS)


@dataclass
class Completion:
    text: str
    tokens_in: int
    tokens_out: int
    latency_ms: int


class Agent(ABC):
    """Base class. Subclasses implement one provider each."""

    def __init__(
        self,
        model: str,
        seed: int = 1,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_retries: int = 5,
    ) -> None:
        self.model = model
        self.seed = seed
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

    @abstractmethod
    def _call(self, prompt: str) -> Completion:
        ...

    def complete(self, prompt: str) -> Completion:
        """Retry transient failures with jittered exponential backoff.
        Permanent failures (auth, invalid model, 4xx-not-429) fail fast."""
        wait = 2.0
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._call(prompt)
            except Exception as e:
                # Fail fast on non-retryable errors — no point burning
                # 5 rounds of backoff on a bad API key.
                if _is_permanent(e):
                    raise PermanentAgentError(
                        f"{self.__class__.__name__} permanent failure: {e}"
                    ) from e
                if attempt == self.max_retries:
                    raise AgentError(
                        f"{self.__class__.__name__} failed after {attempt} tries: {e}"
                    ) from e
                # Jittered exponential backoff for 429 / 5xx / timeouts.
                time.sleep(wait + random.uniform(0, wait * 0.3))
                wait *= 2

    @property
    def family(self) -> str:
        return self.__class__.__name__.replace("Agent", "").lower()


# ── Anthropic (Claude) ──────────────────────────────────────────────────────

class AnthropicAgent(Agent):
    """Claude via the anthropic SDK.

    Note: the Anthropic API does not support a `seed` parameter today, so
    stochasticity in the D1 same-family cell comes from temperature > 0
    across independent calls. The `seed` field is retained for logging.
    """

    def __init__(self, model: str = "claude-sonnet-4-6", **kw) -> None:
        super().__init__(model=model, **kw)
        from anthropic import Anthropic

        self._client = Anthropic()  # reads ANTHROPIC_API_KEY

    def _call(self, prompt: str) -> Completion:
        t0 = time.time()
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = int((time.time() - t0) * 1000)
        text = resp.content[0].text if resp.content else ""
        return Completion(
            text=text,
            tokens_in=resp.usage.input_tokens,
            tokens_out=resp.usage.output_tokens,
            latency_ms=latency_ms,
        )


# ── OpenAI (GPT) ────────────────────────────────────────────────────────────

class OpenAIAgent(Agent):
    def __init__(self, model: str = "gpt-5-mini", **kw) -> None:
        super().__init__(model=model, **kw)
        from openai import OpenAI

        self._client = OpenAI()  # reads OPENAI_API_KEY

    def _call(self, prompt: str) -> Completion:
        t0 = time.time()
        kwargs: dict[str, Any] = dict(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        # OpenAI supports `seed` on chat.completions for reproducibility.
        kwargs["seed"] = self.seed
        resp = self._client.chat.completions.create(**kwargs)
        latency_ms = int((time.time() - t0) * 1000)
        text = resp.choices[0].message.content or ""
        u = resp.usage
        return Completion(
            text=text,
            tokens_in=u.prompt_tokens,
            tokens_out=u.completion_tokens,
            latency_ms=latency_ms,
        )


# ── Google (Gemini) ─────────────────────────────────────────────────────────

class GoogleAgent(Agent):
    def __init__(self, model: str = "gemini-2.5-pro", **kw) -> None:
        super().__init__(model=model, **kw)
        from google import genai

        self._client = genai.Client()  # reads GOOGLE_API_KEY / GEMINI_API_KEY

    def _call(self, prompt: str) -> Completion:
        t0 = time.time()
        resp = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
                "seed": self.seed,
            },
        )
        latency_ms = int((time.time() - t0) * 1000)
        text = (resp.text or "").strip()
        usage = getattr(resp, "usage_metadata", None)
        tokens_in = getattr(usage, "prompt_token_count", 0) if usage else 0
        tokens_out = getattr(usage, "candidates_token_count", 0) if usage else 0
        return Completion(
            text=text,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
        )


# ── Together (Llama and other open-weights) ─────────────────────────────────

class TogetherAgent(Agent):
    def __init__(
        self,
        model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        **kw,
    ) -> None:
        super().__init__(model=model, **kw)
        from together import Together

        self._client = Together()  # reads TOGETHER_API_KEY

    def _call(self, prompt: str) -> Completion:
        t0 = time.time()
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            seed=self.seed,
        )
        latency_ms = int((time.time() - t0) * 1000)
        text = resp.choices[0].message.content or ""
        u = resp.usage
        return Completion(
            text=text,
            tokens_in=u.prompt_tokens,
            tokens_out=u.completion_tokens,
            latency_ms=latency_ms,
        )


# ── OpenRouter (Kimi, DeepSeek, Qwen, Doubao, GLM, etc.) ────────────────────

class OpenRouterAgent(Agent):
    """Unified OpenAI-compatible endpoint for many providers.

    Use this to reach Chinese-hosted models (Kimi K2, DeepSeek V3, Qwen 3,
    ByteDance Doubao, Zhipu GLM, MiniMax) with one key. Full model catalog:
    https://openrouter.ai/models. Model IDs look like:
        moonshotai/kimi-k2
        deepseek/deepseek-chat-v3
        qwen/qwen-3-max
        bytedance/doubao-1.5-pro
        z-ai/glm-4.6
    """

    def __init__(self, model: str, **kw) -> None:
        super().__init__(model=model, **kw)
        from openai import OpenAI

        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )

    def _call(self, prompt: str) -> Completion:
        t0 = time.time()
        kwargs: dict[str, Any] = dict(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            # OpenRouter forwards `seed` when the underlying provider accepts
            # it. Anthropic-backed models ignore it silently.
            seed=self.seed,
            # Explicitly disable any tool/search sidecar OpenRouter may offer.
            extra_body={"provider": {"allow_fallbacks": True}},
        )
        resp = self._client.chat.completions.create(**kwargs)
        latency_ms = int((time.time() - t0) * 1000)
        text = resp.choices[0].message.content or ""
        u = resp.usage
        return Completion(
            text=text,
            tokens_in=getattr(u, "prompt_tokens", 0),
            tokens_out=getattr(u, "completion_tokens", 0),
            latency_ms=latency_ms,
        )


# ── Factory ─────────────────────────────────────────────────────────────────

_PROVIDERS: dict[str, type[Agent]] = {
    "anthropic": AnthropicAgent,
    "openai": OpenAIAgent,
    "google": GoogleAgent,
    "together": TogetherAgent,
    "openrouter": OpenRouterAgent,
}

_ENV_KEY = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",  # also GEMINI_API_KEY works upstream
    "together": "TOGETHER_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def build_agent(
    provider: str,
    model: str,
    seed: int,
    temperature: float,
    max_tokens: int,
) -> Agent:
    if provider not in _PROVIDERS:
        raise ValueError(f"unknown provider: {provider}")
    # Google accepts either GOOGLE_API_KEY or GEMINI_API_KEY upstream.
    if provider == "google":
        if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
            raise EnvironmentError("missing GOOGLE_API_KEY / GEMINI_API_KEY")
    elif not os.getenv(_ENV_KEY[provider]):
        raise EnvironmentError(
            f"missing API key for {provider} (set {_ENV_KEY[provider]})"
        )
    cls = _PROVIDERS[provider]
    return cls(
        model=model,
        seed=seed,
        temperature=temperature,
        max_tokens=max_tokens,
    )
