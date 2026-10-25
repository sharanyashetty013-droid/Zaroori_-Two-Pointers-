"""Role-based dashboard access + audit log.
Keys (env): VIEWER_API_KEY (map only) < REVIEWER_API_KEY (flags, anomalies, alerts) < ADMIN_API_KEY (everything).
Send as header  X-API-Key. A higher role can do everything a lower one can."""
import os, hmac, hashlib
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from .db import get_db
from . import models as m

RANK = {"viewer": 1, "reviewer": 2, "admin": 3}
WEAK = {"", "dev-admin-key", "change-me"}

def _keys() -> dict[str, str]:
    admin = os.getenv("ADMIN_API_KEY", "dev-admin-key")
    ks = {"admin": admin, "reviewer": os.getenv("REVIEWER_API_KEY", ""), "viewer": os.getenv("VIEWER_API_KEY", "")}
    return {r: k for r, k in ks.items() if k}

def check_config():
    """Refuse to boot in production with a guessable admin key."""
    if os.getenv("APP_ENV") == "production" and os.getenv("ADMIN_API_KEY", "") in WEAK:
        raise RuntimeError("Set a strong ADMIN_API_KEY before running with APP_ENV=production")
    if os.getenv("APP_ENV") == "production" and os.getenv("ASHA_LOGIN_REQUIRED", "1") == "0":
        raise RuntimeError("ASHA_LOGIN_REQUIRED=0 is for local demos only; remove it before running with APP_ENV=production")

def fingerprint(key: str) -> str: return hashlib.sha256(key.encode()).hexdigest()[:8]

def audit(db: Session, role: str, actor: str, action: str, detail: str = ""):
    db.add(m.AuditLog(role=role, actor=actor, action=action[:80], detail=detail[:300])); db.commit()

class Actor:
    def __init__(self, role: str, actor: str): self.role, self.actor = role, actor

def require(min_role: str):
    def dep(x_api_key: str = Header(default=""), db: Session = Depends(get_db)) -> Actor:
        role = None
        for r, k in _keys().items():   # compare against every key so timing does not reveal which one matched
            if hmac.compare_digest(x_api_key.encode(), k.encode()) and (role is None or RANK[r] > RANK[role]): role = r
        if role is None:
            audit(db, "none", "", f"denied:{min_role}"); raise HTTPException(401, "valid API key required")
        if RANK[role] < RANK[min_role]:
            audit(db, role, fingerprint(x_api_key), f"forbidden:{min_role}"); raise HTTPException(403, f"{min_role} role required")
        return Actor(role, fingerprint(x_api_key))
    return dep
