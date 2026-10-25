"""Per-IP sliding-window rate limit on EVERY endpoint (was: AI/voice only).
Behind Render's proxy set TRUSTED_PROXY_HOPS=1 so a client cannot spoof X-Forwarded-For."""
import os, time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_hits: dict[tuple, deque] = defaultdict(deque)

def _limits() -> dict[str, int]:
    return {"write": int(os.getenv("RATE_WRITE_PER_MIN", "20")),    # create session / alert
            "ai": int(os.getenv("RATE_AI_PER_MIN", "30")),          # LLM + voice (cost)
            "auth": int(os.getenv("RATE_AUTH_PER_MIN", "30")),      # dashboard/admin: slows key guessing
            "default": int(os.getenv("RATE_PER_MIN", "120"))}

def bucket(method: str, path: str) -> str:
    if path.startswith(("/ai/", "/tts")): return "ai"
    if path.startswith(("/dashboard", "/admin", "/asha")): return "auth"
    if method == "POST" and path in ("/sessions", "/alerts"): return "write"
    return "default"

def client_ip(request) -> str:
    hops = int(os.getenv("TRUSTED_PROXY_HOPS", "0"))
    xff = [x.strip() for x in request.headers.get("x-forwarded-for", "").split(",") if x.strip()]
    if hops and len(xff) >= hops: return xff[-hops]
    return request.client.host if request.client else "?"

def reset(): _hits.clear()

class RateLimit(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if os.getenv("RATE_LIMIT_DISABLED") == "1" or request.url.path == "/health": return await call_next(request)
        b = bucket(request.method, request.url.path); cap = _limits()[b]; now = time.time()
        q = _hits[(client_ip(request), b)]
        while q and now - q[0] > 60: q.popleft()
        if len(q) >= cap:
            return JSONResponse({"detail": "too many requests, wait a minute"}, 429, headers={"Retry-After": str(int(60 - (now - q[0])) + 1)})
        q.append(now)
        if len(_hits) > 20000:   # keep memory bounded
            for k in [k for k, v in _hits.items() if not v or now - v[-1] > 60]: _hits.pop(k, None)
        return await call_next(request)
