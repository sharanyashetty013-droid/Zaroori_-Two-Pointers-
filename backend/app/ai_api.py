import logging
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Literal
from . import ai, llm, tts, content as C, models as m
from .db import get_db
from .security import require, audit, Actor
log = logging.getLogger("zaroori")

router = APIRouter()
Lang = Literal["en", "hi", "kn"]

class AskIn(BaseModel):
    question: str
    lang: Lang = "en"
class ExtractIn(BaseModel):
    text: str
    lang: Lang = "en"
    session_id: str | None = None

@router.get("/ai/status")
def status(): return {"llm": llm.provider(), "tts": "gtts", "note": "Without an API key, AI features use reviewed templates."}

@router.post("/ai/ask")
def ask(b: AskIn): return ai.ask(b.question, b.lang)

@router.post("/ai/extract")
def extract(b: ExtractIn, db: Session = Depends(get_db)):
    out = ai.extract(b.text, b.lang)
    if out is None: raise HTTPException(503, "AI not available; answer the questions with the buttons")
    if b.session_id and out["coercion_signal"]:
        s = db.get(m.CaseSession, b.session_id)
        if s: s.ai_coercion = True; s.coercion = True; db.commit()   # AI can only raise the signal
    return out

@router.get("/tts")
def speak(text: str, lang: Lang = "en"):
    if not text.strip() or len(text) > 400: raise HTTPException(400, "text must be 1 to 400 characters")
    try: return Response(tts.speak(text, lang), media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
    except Exception: raise HTTPException(503, "voice service unavailable; use the device voice instead")

@router.get("/tts/question/{qid}")
def speak_question(qid: str, lang: Lang = "en"):
    q = next((x for x in C.QUESTIONS if x["id"] == qid), None)
    if not q: raise HTTPException(404, "unknown question")
    labels = ". ".join(C.pick(o["label"], lang) for o in q["options"])
    return speak(f"{C.pick(q['text'], lang)} {labels}", lang)


# ---------- Voice for every screen, in en / hi / kn ----------
def _audio(text: str, lang: str) -> Response:
    try: return Response(tts.speak(text, lang), media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
    except Exception: raise HTTPException(503, "voice service unavailable; use the device voice instead")

def result_text(advised: bool, doctor_qs: list[str], lang: str) -> str:
    """Exactly what the result screen says: headline, doctor questions, then the not-a-diagnosis note."""
    parts = [C.pick(C.HEADLINE if advised else C.NOT_ADVISED, lang)]
    if advised and doctor_qs: parts += [C.pick(C.SLIP_Q_HEAD, lang)] + list(doctor_qs)
    parts.append(C.pick(C.NOTE, lang))
    return ". ".join(parts)

def alert_text(lang: str) -> str:
    """Red screen: her right to say no, then each helpline with digits spoken one by one."""
    calls = [f"{C.pick(C.HELPLINE_NAMES[h['number']], lang)}. {C.pick(C.CALL, lang)} {' '.join(h['number'])}" for h in C.HELPLINES if h["number"] in C.HELPLINE_NAMES]
    return ". ".join([C.pick(C.ALERT_TITLE, lang), C.pick(C.ALERT_TEXT, lang)] + calls)

@router.get("/tts/result/{sid}")
def speak_result(sid: str, lang: Lang | None = None, db: Session = Depends(get_db)):
    """Reads the whole result screen aloud in the chosen language (defaults to the session language)."""
    s = db.get(m.CaseSession, sid)
    if not s: raise HTTPException(404, "session not found")
    lang = lang or s.lang
    qs = ai.questions_for(s, lang, db)[0] if s.advised else []
    return _audio(result_text(s.advised, qs, lang), lang)

@router.get("/tts/alert/{sid}")
def speak_alert(sid: str, lang: Lang | None = None, db: Session = Depends(get_db)):
    """Reads the red screen aloud: rights and helplines. Only for sessions where coercion was reported."""
    s = db.get(m.CaseSession, sid)
    if not s: raise HTTPException(404, "session not found")
    if not s.coercion: raise HTTPException(409, "no coercion reported for this session")
    lang = lang or s.lang
    return _audio(alert_text(lang), lang)

def _warm_all():
    done = 0
    for lang in C.L:
        texts = [f"{C.pick(q['text'], lang)} " + ". ".join(C.pick(o["label"], lang) for o in q["options"]) for q in C.QUESTIONS]
        texts += [result_text(True, [C.pick(d, lang) for d in C.DOCTOR_QUESTIONS], lang), result_text(False, [], lang), alert_text(lang)]
        for t in texts:
            try: tts.speak(t, lang); done += 1
            except Exception as e: log.error("tts warm failed (%s): %s", lang, type(e).__name__)
    log.info("tts warm finished: %d clips", done)

@router.post("/admin/tts/warm")
def warm(bg: BackgroundTasks, db: Session = Depends(get_db), who: Actor = Depends(require("admin"))):
    """Pre-generates all fixed audio (6 questions, result, red screen) in en, hi and kn so voice works fast and survives a weak connection."""
    audit(db, who.role, who.actor, "tts.warm"); bg.add_task(_warm_all)
    return {"queued": len(C.L) * (len(C.QUESTIONS) + 3), "languages": list(C.L)}
