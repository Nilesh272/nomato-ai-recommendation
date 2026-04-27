from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL_FALLBACK = "llama-3.1-8b-instant"


def _load_env_file() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _api_key() -> str:
    _load_env_file()
    return os.environ.get("GROQ_API_KEY", "").strip()

def _truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _base_url() -> str:
    _load_env_file()
    return os.environ.get("GROQ_BASE_URL", GROQ_BASE_URL).strip() or GROQ_BASE_URL


def _configured_model() -> str:
    _load_env_file()
    return os.environ.get("GROQ_MODEL", "").strip()


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }


def _session() -> requests.Session:
    # Some networks require proxy env vars (HTTP(S)_PROXY) for outbound HTTPS + DNS.
    # Keep this configurable so local/corporate networks can work without code edits.
    session = requests.Session()
    session.trust_env = _truthy("GROQ_TRUST_ENV", default=False)
    return session


def _get_default_model() -> str:
    response = _session().get(f"{_base_url()}/models", headers=_headers(), timeout=30)
    response.raise_for_status()
    models = response.json().get("data", [])
    preferred = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]
    ids = [str(item.get("id", "")) for item in models]
    for candidate in preferred:
        if candidate in ids:
            return candidate
    if not ids:
        raise RuntimeError("No Groq models returned from /models.")
    return ids[0]


def invoke_groq_ranking(prompt: str, retries: int = 2) -> dict[str, Any]:
    if not _api_key():
        raise RuntimeError("GROQ_API_KEY missing. Add it to .env.")

    # Prefer an explicitly configured model to avoid a failing /models call.
    model = _configured_model()
    if not model:
        try:
            model = _get_default_model()
        except Exception:
            model = DEFAULT_MODEL_FALLBACK

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a recommendation ranking engine."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    attempt = 0
    last_err: Exception | None = None
    while attempt <= retries:
        try:
            resp = _session().post(
                f"{_base_url()}/chat/completions",
                headers=_headers(),
                json=body,
                timeout=45,
            )
            resp.raise_for_status()
            payload = resp.json()
            content = payload.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            parsed = json.loads(content)
            return {"raw_response": payload, "content_json": parsed}
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            attempt += 1
            if attempt <= retries:
                time.sleep(0.8 * attempt)
    raise RuntimeError(f"Groq call failed after retries: {last_err}")

