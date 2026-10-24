import os, pytest
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ.update(ADMIN_API_KEY="k", REVIEWER_API_KEY="rk", VIEWER_API_KEY="vk")
for f in ("test.db",):
    if os.path.exists(f): os.remove(f)

@pytest.fixture(autouse=True)
def _fresh_limiter(monkeypatch):
    """Limiter off by default (bulk test setup would trip it); rate-limit tests turn it back on."""
    from app import ratelimit; ratelimit.reset(); monkeypatch.setenv("RATE_LIMIT_DISABLED", "1"); yield; ratelimit.reset()

_n = 0
def make_asha(district="Udupi", contact=""):
    """Create an ASHA straight in the DB. Returns (asha_id, key)."""
    global _n; _n += 1
    from app.db import SessionLocal; from app import models as m, asha as A
    key = f"asha_test_{_n}_{os.urandom(4).hex()}"
    with SessionLocal() as db:
        a = m.Asha(code=A.new_code(db), district=district, contact=contact, key_hash=A.hash_key(key)); db.add(a); db.commit(); return a.id, key
