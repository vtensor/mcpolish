"""LLM client adapter.

Spec accepted: `provider:model_id`, e.g. `openai:gpt-5`, `anthropic:claude-opus-4-7`,
`ollama:llama3.1`. The actual provider SDK is imported lazily so the core
package doesn't take the dependency unless `--llm` is used.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from mcpolish.exceptions import LLMError
from mcpolish.llm.cache import LLMCache
from mcpolish.logging import get_logger

log = get_logger(__name__)


class LLMBackend(Protocol):
    name: str

    def complete(self, prompt: str) -> str: ...


@dataclass
class LLMClient:
    """Caches + retries around the underlying provider call.

    Rules call `client.judge(rule_id=..., prompt=...)` and get a one-line
    verdict string. On LLM failure the client logs and returns "OK" so the
    rule degrades to a no-op rather than aborting the lint.
    """

    backend: LLMBackend
    cache: LLMCache
    model_id: str

    def judge(self, *, rule_id: str, prompt: str) -> str:
        key = LLMCache.key(rule_id, self.model_id, prompt)
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        try:
            response = self.backend.complete(prompt).strip().splitlines()[0].strip()
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            log.warning("llm call failed for %s: %s", rule_id, exc)
            return "OK"
        self.cache.put(
            key, rule_id=rule_id, model_id=self.model_id, response=response
        )
        return response


def build_client(spec: str, *, cache_path: Path | None = None) -> LLMClient:
    provider, _, model = spec.partition(":")
    if not provider or not model:
        raise LLMError(f"--llm expects 'provider:model_id', got {spec!r}")
    if cache_path is None:
        cache_path = Path.home() / ".cache" / "mcpolish" / "llm.db"
    cache = LLMCache(cache_path)
    backend = _build_backend(provider.lower(), model)
    return LLMClient(backend=backend, cache=cache, model_id=spec)


def _build_backend(provider: str, model: str) -> LLMBackend:
    if provider == "openai":
        return _OpenAIBackend(model=model)
    if provider == "anthropic":
        return _AnthropicBackend(model=model)
    if provider == "ollama":
        return _OllamaBackend(model=model)
    raise LLMError(f"unsupported LLM provider {provider!r}")


# ---------------------------------------------------------------------------
# Backends - lazy import of the SDK so the core package is dependency-free.
# ---------------------------------------------------------------------------


@dataclass
class _OpenAIBackend:
    name: str = "openai"
    model: str = ""

    def complete(self, prompt: str) -> str:
        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise LLMError("pip install mcpolish[llm] to use --llm openai:*") from exc
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise LLMError("OPENAI_API_KEY not set")
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0,
        )
        return resp.choices[0].message.content or "OK"


@dataclass
class _AnthropicBackend:
    name: str = "anthropic"
    model: str = ""

    def complete(self, prompt: str) -> str:
        try:
            import anthropic  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise LLMError("pip install mcpolish[llm] to use --llm anthropic:*") from exc
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMError("ANTHROPIC_API_KEY not set")
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=self.model,
            max_tokens=120,
            messages=[{"role": "user", "content": prompt}],
        )
        for block in resp.content:
            if getattr(block, "type", "") == "text":
                return block.text
        return "OK"


@dataclass
class _OllamaBackend:
    name: str = "ollama"
    model: str = ""

    def complete(self, prompt: str) -> str:
        import json
        import urllib.request

        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        body = json.dumps(
            {"model": self.model, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{host}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"ollama call failed: {exc}") from exc
        return payload.get("response", "OK")
