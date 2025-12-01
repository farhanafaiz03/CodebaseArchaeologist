"""Simple LLM wrapper used by agents.

This module exposes `call_llm(prompt, ...)` which will try to call
OpenAI's ChatCompletion API if `openai` is available and
`OPENAI_API_KEY` is set in the environment. Otherwise it returns a
harmless stub (the prompt truncated) so the repository remains usable
without credentials during development and static analysis.
"""
from typing import Optional
import os
import logging


def call_llm(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 512, temperature: float = 0.0) -> str:
    """Call an LLM to get a text response.

    Attempts to use the `openai` package and the `OPENAI_API_KEY`
    environment variable. If the library or key is unavailable, a
    deterministic stub response is returned so the rest of the code can
    run and static analyzers (like Pylance) can resolve the import.
    """
    try:
        import openai  # type: ignore

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.warning("OPENAI_API_KEY not set; returning stub response from call_llm")
            return _stub_response(prompt)

        openai.api_key = api_key

        # Use ChatCompletion API (works with openai v2.x compatibility layer)
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Compatibility: handle different response shapes safely
        try:
            message = resp['choices'][0]['message']['content']
        except Exception:
            # fallback for older/newer shapes
            message = resp['choices'][0].get('text', '')

        return message.strip()

    except Exception as exc:  # pragma: no cover - best-effort runtime behavior
        logging.warning("call_llm: openai call failed (%s); returning stub", exc)
        return _stub_response(prompt)


def _stub_response(prompt: str, length: int = 100) -> str:
    """Return a stable, trimmed representation of the prompt for local use."""
    cleaned = " ".join(prompt.split())
    return f"[LLM STUB] {cleaned[:length]}{'...' if len(cleaned) > length else ''}"
