from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

import pytest
import requests

BASE_URL = "https://api.groq.com/openai/v1"


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


def _get_api_key() -> str:
    _load_env_file()
    key = os.environ.get("GROQ_API_KEY", "").strip()
    return key


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }


def _fetch_models() -> List[Dict[str, Any]]:
    try:
        resp = requests.get(f"{BASE_URL}/models", headers=_headers(), timeout=30)
    except requests.RequestException as exc:
        pytest.skip(f"Skipping live Groq connectivity test due to network/proxy issue: {exc}")
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("data", [])


def _select_groq_model(models: List[Dict[str, Any]]) -> str:
    ids = [str(m.get("id", "")) for m in models]
    preferred = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "groq/compound-mini",
    ]
    for model_id in preferred:
        if model_id in ids:
            return model_id
    for candidate in ids:
        if "llama" in candidate.lower() or "mixtral" in candidate.lower() or "gemma" in candidate.lower():
            return candidate
    if ids:
        return ids[0]
    raise AssertionError("No model ID returned by /models endpoint.")


def test_1_api_key_present() -> None:
    key = _get_api_key()
    if not key or "your_groq_api_key_here" in key:
        pytest.skip("Skipping live Groq connectivity test because GROQ_API_KEY is not configured.")


def test_2_models_endpoint_reachable() -> None:
    models = _fetch_models()
    assert isinstance(models, list), "Expected list from /models."
    assert len(models) > 0, "No models returned from /models."


def test_3_chat_completion_returns_text() -> None:
    models = _fetch_models()
    model = _select_groq_model(models)
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "Reply with exactly: CONNECTED"},
        ],
        "temperature": 0,
        "max_tokens": 20,
    }
    resp = requests.post(f"{BASE_URL}/chat/completions", headers=_headers(), json=body, timeout=45)
    resp.raise_for_status()
    payload = resp.json()
    choices = payload.get("choices", [])
    assert choices, "No choices returned from chat completion."
    text = choices[0].get("message", {}).get("content", "")
    assert isinstance(text, str) and text.strip(), "Empty completion content returned."

