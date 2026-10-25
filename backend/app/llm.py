"""Provider-agnostic LLM call over plain REST. Set GEMINI_API_KEY (free from Google AI Studio) or ANTHROPIC_API_KEY."""
import os, logging
import httpx
log = logging.getLogger("zaroori")

def provider() -> str | None:
    if os.getenv("GEMINI_API_KEY"): return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"): return "anthropic"
    return None

def available() -> bool: return provider() is not None

def complete(system: str, user: str, json_mode: bool = False, max_tokens: int = 700) -> str | None:
    """Returns text, or None on any failure so callers fall back safely."""
    p = provider()
    try:
        if p == "gemini":
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            cfg = {"temperature": 0.2, "maxOutputTokens": max_tokens}
            if json_mode: cfg["responseMimeType"] = "application/json"
            r = httpx.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                           params={"key": os.getenv("GEMINI_API_KEY")}, timeout=20,
                           json={"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": cfg})
            r.raise_for_status(); return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        if p == "anthropic":
            r = httpx.post("https://api.anthropic.com/v1/messages", timeout=20,
                           headers={"x-api-key": os.getenv("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"},
                           json={"model": os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5"), "max_tokens": max_tokens, "temperature": 0.2,
                                 "system": system, "messages": [{"role": "user", "content": user}]})
            r.raise_for_status(); return r.json()["content"][0]["text"]
    except Exception as e:
        log.error("LLM call failed: %s", e)
    return None
