import os, logging, asyncio
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Literal
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import content as C, rules, models as m
from .db import Base, engine, get_db, add_missing_columns
from .pdf import make_slip
from . import ai, anomaly, delivery
from .ai_api import router as ai_router
from .security import require, audit, check_config, Actor
from .ratelimit import RateLimit
from . import asha as A

THRESH = int(os.getenv("FLAG_THRESHOLD", "3")); MIN_ASHAS = int(os.getenv("FLAG_MIN_ASHAS", "2")); WINDOW = int(os.getenv("FLAG_WINDOW_DAYS", "90"))
Lang = Literal["en", "hi", "kn"]

check_config()
Base.metadata.create_all(engine); add_missing_columns()

@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(delivery.retry_loop())   # retries alerts whose first delivery failed
    yield
    task.cancel()

app = FastAPI(title="Zaroori? API", version="1.1", lifespan=lifespan)
app.add_middleware(RateLimit)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "*").split(","), allow_methods=["*"], allow_headers=["*"])
app.include_router(ai_router)
app.include_router(A.router)

def get_session(sid: str, db: Session) -> m.CaseSession:
    s = db.get(m.CaseSession, sid)
    if not s: raise HTTPException(404, "session not found")
    return s

class StartIn(BaseModel):
    lang: Lang = "en"
    district: str | None = None      # optional now: defaults to the ASHA's own district
    hospital_id: int | None = None   # hospital that advised surgery (optional)
class AnswersIn(BaseModel):
    answers: dict[str, str]
class AlertIn(BaseModel):
    session_id: str
    consent: bool

def build_result(s: m.CaseSession, lang: str, db: Session) -> dict:
    hosp = db.query(m.Hospital).filter(m.Hospital.district == s.district, m.Hospital.is_govt == True).limit(5).all()  # noqa: E712
    qs, src = ai.questions_for(s, lang, db) if s.advised else ([], "none")
    r = {"session_id": s.id, "completed": s.completed, "advised": s.advised, "coercion": s.coercion,
         "headline": C.pick(C.HEADLINE if s.advised else C.NOT_ADVISED, lang), "note": C.pick(C.NOTE, lang),
         "doctor_questions": qs, "questions_source": src,
         "hospitals": [{"id": h.id, "name": h.name, "district": h.district} for h in hosp]}
    if s.coercion:
        al = db.query(m.Alert).filter(m.Alert.session_id == s.id).first()
        r["alert"] = {"title": C.pick(C.ALERT_TITLE, lang), "text": C.pick(C.ALERT_TEXT, lang), "helplines": C.HELPLINES, "can_send_alert": al is None,
                      "sent": al is not None, "delivery": al.status if al else None}   # delivery: queued | sent | failed
    return r

@app.get("/health")
def health(): return {"ok": True}

@app.get("/questions")
def questions(lang: Lang = "en"):
    return [{"id": q["id"], "text": C.pick(q["text"], lang), "options": [{"value": o["v"], "label": C.pick(o["label"], lang)} for o in q["options"]]} for q in C.QUESTIONS]

@app.get("/hospitals")
def hospitals(district: str, db: Session = Depends(get_db)):
    return [{"id": h.id, "name": h.name, "district": h.district, "is_govt": h.is_govt} for h in db.query(m.Hospital).filter(m.Hospital.district == district).all()]

@app.post("/sessions", status_code=201)
def start(b: StartIn, db: Session = Depends(get_db), asha: m.Asha | None = Depends(A.current_asha)):
    if b.hospital_id and not db.get(m.Hospital, b.hospital_id): raise HTTPException(400, "unknown hospital_id")
    district = (b.district or "").strip()
    if asha:
        if district and district.lower() != asha.district.lower(): raise HTTPException(403, "this ASHA account is for a different district")
        district = asha.district; A.check_daily_cap(db, asha)
    if not district: raise HTTPException(422, "district is required")
    s = m.CaseSession(lang=b.lang, district=district, hospital_id=b.hospital_id, asha_id=asha.id if asha else None)
    db.add(s); db.commit(); return {"session_id": s.id}

@app.post("/sessions/{sid}/answers")
def answer(sid: str, b: AnswersIn, db: Session = Depends(get_db)):
    s = get_session(sid, db); bad = rules.invalid(b.answers)
    if bad: raise HTTPException(422, f"invalid answers: {bad}")
    a = {**(s.answers or {}), **b.answers}
    s.answers, s.age_band = a, a.get("q1")
    s.completed, s.advised, s.coercion = rules.is_complete(a), rules.is_advised(a), rules.is_coercion(a) or s.ai_coercion
    db.commit(); return build_result(s, s.lang, db)

@app.get("/sessions/{sid}/result")
def result(sid: str, lang: Lang | None = None, db: Session = Depends(get_db)):
    s = get_session(sid, db); return build_result(s, lang or s.lang, db)

@app.get("/sessions/{sid}/slip.pdf")
def slip(sid: str, lang: Lang | None = None, db: Session = Depends(get_db)):
    s = get_session(sid, db); lang = lang or s.lang
    if not s.completed: raise HTTPException(409, "finish all 6 questions first")
    names = [h.name for h in db.query(m.Hospital).filter(m.Hospital.district == s.district, m.Hospital.is_govt == True).limit(5)]  # noqa: E712
    pdf = make_slip(s.id[:8].upper(), s.district, names, ai.questions_for(s, lang, db)[0], lang)
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="zaroori-slip-{s.id[:8]}.pdf"'})

@app.post("/alerts", status_code=201)
def alert(b: AlertIn, bg: BackgroundTasks, db: Session = Depends(get_db)):
    if not b.consent: raise HTTPException(400, "consent is required before sharing")
    s = get_session(b.session_id, db)
    if not s.coercion: raise HTTPException(409, "no coercion reported for this session")
    if db.query(m.Alert).filter(m.Alert.session_id == s.id).first(): raise HTTPException(409, "alert already sent")
    al = m.Alert(session_id=s.id, asha_id=s.asha_id, district=s.district, slip_code=s.id[:8].upper(), status="queued", next_try_at=m.now()); db.add(al); db.commit()
    audit(db, "system", "", "alert.created", f"alert {al.id} in {s.district}")   # alert id + district only, never the session id
    bg.add_task(delivery.attempt, al.id)   # first try right now; the retry loop handles failures
    return {"alert_id": al.id, "status": "queued"}

@app.get("/dashboard/flags")
def flags(db: Session = Depends(get_db), who: Actor = Depends(require("reviewer"))):
    from sqlalchemy import func, and_
    cutoff = m.now() - timedelta(days=WINDOW)
    q = (db.query(m.Hospital.id, m.Hospital.name, m.Hospital.district, func.count(m.CaseSession.id), func.count(func.distinct(m.CaseSession.asha_id)))
         .join(m.CaseSession, m.CaseSession.hospital_id == m.Hospital.id)
         .filter(m.CaseSession.advised == True, m.CaseSession.completed == True, m.CaseSession.created_at >= cutoff)  # noqa: E712
         .group_by(m.Hospital.id, m.Hospital.name, m.Hospital.district).having(and_(func.count(m.CaseSession.id) >= THRESH, func.count(func.distinct(m.CaseSession.asha_id)) >= MIN_ASHAS)))   # one ASHA alone can never flag a hospital
    rev = {r.hospital_id: r for r in db.query(m.FlagReview).all()}
    audit(db, who.role, who.actor, "flags.read")
    return {"threshold": THRESH, "min_ashas": MIN_ASHAS, "window_days": WINDOW, "note": "A flag means: please check. It is not an accusation.",
            "flagged": [{"hospital_id": i, "hospital": n, "district": d, "cases": c, "ashas": na,
                         "review": {"status": rev[i].status, "note": rev[i].note, "updated_at": rev[i].updated_at} if i in rev else {"status": "open", "note": ""}}
                        for i, n, d, c, na in q.all()]}

class ReviewIn(BaseModel):
    status: Literal["open", "reviewing", "dismissed", "escalated"]
    note: str = ""   # keep it free of names or personal details

@app.post("/dashboard/flags/{hospital_id}/review")
def review_flag(hospital_id: int, b: ReviewIn, db: Session = Depends(get_db), who: Actor = Depends(require("reviewer"))):
    if not db.get(m.Hospital, hospital_id): raise HTTPException(404, "hospital not found")
    r = db.get(m.FlagReview, hospital_id) or m.FlagReview(hospital_id=hospital_id); r.status, r.note, r.reviewer, r.updated_at = b.status, b.note[:300], who.actor, m.now()
    db.add(r); db.commit(); audit(db, who.role, who.actor, "flags.review", f"hospital {hospital_id} -> {b.status}")
    return {"hospital_id": hospital_id, "status": r.status}

@app.get("/dashboard/anomalies")
def anomalies(db: Session = Depends(get_db), who: Actor = Depends(require("reviewer"))):
    audit(db, who.role, who.actor, "anomalies.read"); return anomaly.run(db)

@app.get("/dashboard/alerts")
def alert_status(code: str | None = None, db: Session = Depends(get_db), who: Actor = Depends(require("reviewer"))):
    """Delivery health of coercion alerts. Never includes session ids. ?code=ABC12345 finds the alert for a slip code a woman reads out."""
    audit(db, who.role, who.actor, "alerts.read")
    q = db.query(m.Alert)
    if code: q = q.filter(m.Alert.slip_code == code.strip().upper()[:8])
    rows = q.order_by(m.Alert.id.desc()).limit(200).all()
    ashas = {a.id: a for a in db.query(m.Asha).filter(m.Asha.id.in_([r.asha_id for r in rows if r.asha_id])).all()}
    return {"alerts": [{"asha_code": ashas[a.asha_id].code if a.asha_id in ashas else None, "asha_contact": ashas[a.asha_id].contact if a.asha_id in ashas else None, "id": a.id, "district": a.district, "status": a.status, "channel": a.channel, "slip_code": a.slip_code, "attempts": a.attempts, "last_error": a.last_error,
                        "created_at": a.created_at, "notified_at": a.notified_at, "next_try_at": a.next_try_at} for a in rows],
            "mock_deliveries": sum(1 for a in rows if a.channel == "mock"), "failed": sum(1 for a in rows if a.status == "failed")}

@app.get("/dashboard/map")
def dmap(db: Session = Depends(get_db), who: Actor = Depends(require("viewer"))):
    audit(db, who.role, who.actor, "map.read")
    out: dict = {}
    for s in db.query(m.CaseSession).filter(m.CaseSession.completed == True).all():  # noqa: E712
        d = out.setdefault(s.district, {"district": s.district, "cases": 0, "advised_surgery": 0, "coercion": 0, "alerts": 0, "nfhs": {}})
        d["cases"] += 1; d["advised_surgery"] += int(s.advised); d["coercion"] += int(s.coercion)
    for al in db.query(m.Alert).all(): out.setdefault(al.district, {"district": al.district, "cases": 0, "advised_surgery": 0, "coercion": 0, "alerts": 0, "nfhs": {}})["alerts"] += 1
    for n in db.query(m.NfhsStat).all():
        out.setdefault(n.district, {"district": n.district, "cases": 0, "advised_surgery": 0, "coercion": 0, "alerts": 0, "nfhs": {}})["nfhs"][n.indicator] = n.value
    return {"districts": sorted(out.values(), key=lambda x: x["district"])}

class HospitalIn(BaseModel):
    name: str
    district: str
    is_govt: bool = True

@app.post("/admin/hospitals", status_code=201)
def add_hospitals(items: list[HospitalIn], db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    """Load your REAL hospital list (bulk). Government hospitals show on the result and slip."""
    for i in items: db.add(m.Hospital(name=i.name.strip(), district=i.district.strip(), is_govt=i.is_govt))
    db.commit(); audit(db, who.role, who.actor, "hospitals.add", f"{len(items)} added"); return {"added": len(items)}

@app.post("/admin/alerts/retry")
def retry_failed(db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    n = delivery.requeue_failed(db); audit(db, who.role, who.actor, "alerts.requeue", f"{n} requeued"); return {"requeued": n}

@app.get("/admin/audit")
def audit_log(limit: int = 100, before_id: int | None = None, db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    q = db.query(m.AuditLog)
    if before_id: q = q.filter(m.AuditLog.id < before_id)
    rows = q.order_by(m.AuditLog.id.desc()).limit(min(max(limit, 1), 500)).all()
    return {"entries": [{"id": r.id, "ts": r.ts, "role": r.role, "actor": r.actor, "action": r.action, "detail": r.detail} for r in rows]}
