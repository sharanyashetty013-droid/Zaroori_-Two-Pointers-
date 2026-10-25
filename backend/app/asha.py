"""ASHA login. Stops fake cases: only a request with a valid ASHA key can start a session.

- Admin creates one account per ASHA (POST /admin/ashas) and hands her the key ONCE. Only a hash of the key is stored.
- Each session stores the ASHA's short code (e.g. ASHA-4K7QX), never the woman's identity.
- A hospital flag needs cases from at least FLAG_MIN_ASHAS different ASHAs (see main.flags).
- An ASHA can only start sessions in her own district, and only ASHA_MAX_SESSIONS_PER_DAY per day (limits a stolen key).
- Alerts carry the ASHA code (and optional work contact) so the NGO reaches the woman through someone she trusts.
Set ASHA_LOGIN_REQUIRED=0 only for local demos. Production refuses to start with it off."""
import os, hashlib, secrets
from datetime import timedelta
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from .db import get_db
from . import models as m
from .security import require, audit, Actor

CODE_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"   # no 0/O/1/I/L, easy to read out on a phone

def login_required() -> bool: return os.getenv("ASHA_LOGIN_REQUIRED", "1") != "0"
def max_per_day() -> int: return int(os.getenv("ASHA_MAX_SESSIONS_PER_DAY", "30"))
def hash_key(key: str) -> str: return hashlib.sha256(key.encode()).hexdigest()   # keys are 192-bit random, so a plain hash is enough
def new_key() -> str: return "asha_" + secrets.token_urlsafe(24)

def new_code(db: Session) -> str:
    while True:
        code = "ASHA-" + "".join(secrets.choice(CODE_CHARS) for _ in range(5))
        if not db.query(m.Asha.id).filter(m.Asha.code == code).first(): return code

def current_asha(x_asha_key: str = Header(default=""), db: Session = Depends(get_db)) -> m.Asha | None:
    if not x_asha_key:
        if login_required():
            audit(db, "none", "", "denied:asha"); raise HTTPException(401, "ASHA login required (send header X-Asha-Key)")
        return None
    a = db.query(m.Asha).filter(m.Asha.key_hash == hash_key(x_asha_key.strip())).first()
    if not a or not a.active:
        audit(db, "none", "", "denied:asha"); raise HTTPException(401, "invalid or switched-off ASHA key")
    a.last_used_at = m.now(); db.commit()
    return a

def check_daily_cap(db: Session, a: m.Asha):
    since = m.now() - timedelta(days=1)
    n = db.query(func.count(m.CaseSession.id)).filter(m.CaseSession.asha_id == a.id, m.CaseSession.created_at >= since).scalar()
    if n >= max_per_day(): raise HTTPException(429, "daily session limit reached for this ASHA account")

router = APIRouter()

@router.get("/asha/me")
def me(a: m.Asha | None = Depends(current_asha)):
    """The app calls this right after the ASHA enters her key, to confirm it works and show her code and district."""
    if a is None: return {"code": None, "district": None, "login_required": False}
    return {"code": a.code, "district": a.district, "login_required": True}

class AshaIn(BaseModel):
    district: str
    label: str = ""     # admin-only note, e.g. the PHC or village. NOT her name unless you really need it.
    contact: str = ""   # her work phone. Included in alerts so the NGO can reach her. Optional.

def _view(a: m.Asha, sessions: int = 0) -> dict:
    return {"id": a.id, "code": a.code, "district": a.district, "label": a.label, "contact": a.contact, "active": a.active,
            "sessions": sessions, "created_at": a.created_at, "last_used_at": a.last_used_at}

@router.post("/admin/ashas", status_code=201)
def create_asha(b: AshaIn, db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    """Create an ASHA account. The key is shown ONCE in this response. It cannot be shown again, only replaced."""
    if not b.district.strip(): raise HTTPException(400, "district is required")
    key = new_key()
    a = m.Asha(code=new_code(db), district=b.district.strip(), label=b.label.strip()[:120], contact=b.contact.strip()[:40], key_hash=hash_key(key))
    db.add(a); db.commit(); audit(db, who.role, who.actor, "asha.create", f"{a.code} in {a.district}")
    return {**_view(a), "key": key, "note": "Give this key to the ASHA now. It will not be shown again."}

@router.get("/admin/ashas")
def list_ashas(db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    counts = dict(db.query(m.CaseSession.asha_id, func.count(m.CaseSession.id)).filter(m.CaseSession.asha_id.isnot(None)).group_by(m.CaseSession.asha_id).all())
    audit(db, who.role, who.actor, "asha.list")
    return {"ashas": [_view(a, counts.get(a.id, 0)) for a in db.query(m.Asha).order_by(m.Asha.id).all()]}

def _get(db: Session, aid: int) -> m.Asha:
    a = db.get(m.Asha, aid)
    if not a: raise HTTPException(404, "ASHA not found")
    return a

@router.post("/admin/ashas/{aid}/deactivate")
def deactivate(aid: int, db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    a = _get(db, aid); a.active = False; db.commit(); audit(db, who.role, who.actor, "asha.deactivate", a.code); return _view(a)

@router.post("/admin/ashas/{aid}/activate")
def activate(aid: int, db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    a = _get(db, aid); a.active = True; db.commit(); audit(db, who.role, who.actor, "asha.activate", a.code); return _view(a)

@router.post("/admin/ashas/{aid}/new-key")
def new_key_for(aid: int, db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    """Lost or leaked key: issue a new one. The old key stops working immediately."""
    a = _get(db, aid); key = new_key(); a.key_hash = hash_key(key); db.commit(); audit(db, who.role, who.actor, "asha.newkey", a.code)
    return {**_view(a), "key": key, "note": "Old key no longer works. Give this one to the ASHA now."}
