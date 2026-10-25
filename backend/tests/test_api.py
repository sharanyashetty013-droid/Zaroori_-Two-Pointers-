import os
from fastapi.testclient import TestClient
from app.main import app
from app import content as C
from app.db import SessionLocal
from app import models as m
from tests.conftest import make_asha
c = TestClient(app); A = {"X-API-Key": "k"}
OK = {"q1": "25_35", "q2": "yes", "q3": "none", "q4": "no", "q5": "no", "q6": "yes"}

def hosp():
    with SessionLocal() as db:
        h = m.Hospital(name="Test Govt", district="Udupi", is_govt=True); db.add(h); db.commit(); return h.id

_DEF = {}
def asha_key(district="Udupi", fresh=False):
    if fresh or district not in _DEF: _DEF[district] = make_asha(district)[1]
    return _DEF[district]

def new(hid=None, lang="en", key=None):
    r = c.post("/sessions", json={"lang": lang, "district": "Udupi", "hospital_id": hid}, headers={"X-Asha-Key": key or asha_key()}); return r.json()["session_id"]

def test_flow_and_slip():
    hid = hosp(); sid = new(hid)
    r = c.post(f"/sessions/{sid}/answers", json={"answers": OK}).json()
    assert r["completed"] and r["advised"] and not r["coercion"] and "second opinion" in r["headline"].lower() and len(r["doctor_questions"]) == 5
    p = c.get(f"/sessions/{sid}/slip.pdf"); assert p.status_code == 200 and p.content[:4] == b"%PDF"

def test_hindi_and_invalid():
    sid = new(lang="hi"); r = c.post(f"/sessions/{sid}/answers", json={"answers": OK}).json()
    assert "दूसरी राय" in r["headline"]
    assert c.post(f"/sessions/{sid}/answers", json={"answers": {"q1": "bogus"}}).status_code == 422

def test_coercion_needs_consent():
    sid = new(); r = c.post(f"/sessions/{sid}/answers", json={"answers": {**OK, "q5": "yes"}}).json()
    assert r["coercion"] and r["alert"]["can_send_alert"] and r["alert"]["helplines"]
    assert c.post("/alerts", json={"session_id": sid, "consent": False}).status_code == 400
    assert c.post("/alerts", json={"session_id": sid, "consent": True}).status_code == 201
    assert c.post("/alerts", json={"session_id": sid, "consent": True}).status_code == 409
    ok = new(); c.post(f"/sessions/{ok}/answers", json={"answers": OK})
    assert c.post("/alerts", json={"session_id": ok, "consent": True}).status_code == 409

def test_flag_rule_and_auth():
    with SessionLocal() as db:
        h = m.Hospital(name="Hot Hospital", district="Udupi", is_govt=False); db.add(h); db.commit(); hid = h.id
    for _ in range(3):
        sid = new(hid, key=make_asha()[1]); c.post(f"/sessions/{sid}/answers", json={"answers": OK})   # 3 cases from 3 different ASHAs
    assert c.get("/dashboard/flags").status_code == 401
    names = [f["hospital"] for f in c.get("/dashboard/flags", headers=A).json()["flagged"]]
    assert "Hot Hospital" in names
    assert any(d["district"] == "Udupi" for d in c.get("/dashboard/map", headers=A).json()["districts"])

def test_blocklist():
    def strings(x):
        if isinstance(x, str): yield x.lower()
        elif isinstance(x, dict):
            for v in x.values(): yield from strings(v)
        elif isinstance(x, list):
            for v in x: yield from strings(v)
    allt = list(strings([C.HEADLINE, C.NOTE, C.NOT_ADVISED, C.DOCTOR_QUESTIONS, C.ALERT_TEXT, C.ALERT_TITLE]))
    assert not [t for t in allt for b in C.BLOCKLIST if b in t]

# ---------- AI layer (LLM and TTS mocked) ----------
import json
from app import llm, tts, ai

def test_ai_fallback_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False); monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = c.post("/ai/ask", json={"question": "Should I do the surgery?", "lang": "en"}).json()
    assert r["source"] == "fallback" and "181" in r["answer"]
    assert c.post("/ai/extract", json={"text": "x"}).status_code == 503

def test_ai_personalised_questions_and_guardrail(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    good = json.dumps({"questions": ["Why do I need this surgery now?", "Can I try another treatment first?", "What are the risks for me?"]})
    monkeypatch.setattr(llm, "complete", lambda *a, **k: good)
    sid = new(); r = c.post(f"/sessions/{sid}/answers", json={"answers": OK}).json()
    assert r["questions_source"] == "ai" and r["doctor_questions"][0].startswith("Why do I need")
    bad = json.dumps({"questions": ["Don't do surgery, it is bad", "Is it safe to wait?", "Ask about options?"]})
    monkeypatch.setattr(llm, "complete", lambda *a, **k: bad)
    sid2 = new(); r2 = c.post(f"/sessions/{sid2}/answers", json={"answers": OK}).json()
    assert r2["questions_source"] == "template" and len(r2["doctor_questions"]) == 5
    monkeypatch.setattr(llm, "complete", lambda *a, **k: "You need surgery for your fibroid.")
    assert c.post("/ai/ask", json={"question": "what do I do"}).json()["source"] == "fallback"

def test_ai_extract_validates_and_raises_coercion(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    out = json.dumps({"answers": {"q2": "yes", "q3": "BOGUS", "q5": "yes"}, "coercion_signal": False, "unclear": []})
    monkeypatch.setattr(llm, "complete", lambda *a, **k: out)
    sid = new(); r = c.post("/ai/extract", json={"text": "contractor says she must do it", "session_id": sid}).json()
    assert r["answers"] == {"q2": "yes", "q5": "yes"} and r["coercion_signal"] is True
    assert "q3" in r["unclear"]

def test_tts_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(tts, "DIR", str(tmp_path)); calls = []
    monkeypatch.setattr(tts, "synth", lambda t, l: (calls.append(1), b"ID3audio")[1])
    a = c.get("/tts", params={"text": "namaste", "lang": "hi"}); b = c.get("/tts", params={"text": "namaste", "lang": "hi"})
    assert a.status_code == 200 and a.content == b.content and len(calls) == 1
    assert c.get("/tts/question/q1", params={"lang": "kn"}).status_code == 200
    assert c.get("/tts", params={"text": "x" * 500}).status_code == 400

def test_admin_hospitals():
    assert c.post("/admin/hospitals", json=[{"name": "A", "district": "Udupi"}]).status_code == 401
    assert c.post("/admin/hospitals", json=[{"name": "Real Govt Hospital", "district": "Udupi"}], headers=A).json() == {"added": 1}


def test_alert_has_slip_code_and_lookup():
    sid = new(); c.post(f"/sessions/{sid}/answers", json={"answers": {**OK, "q5": "yes"}})
    assert c.post("/alerts", json={"session_id": sid, "consent": True}).status_code == 201
    code = sid[:8].upper()
    rows = c.get("/dashboard/alerts", headers=A, params={"code": code}).json()["alerts"]
    assert len(rows) == 1 and rows[0]["slip_code"] == code
    assert "session_id" not in rows[0]


def test_voice_for_every_screen_in_all_languages(monkeypatch, tmp_path):
    monkeypatch.setattr(tts, "DIR", str(tmp_path)); said = []
    monkeypatch.setattr(tts, "synth", lambda t, l: (said.append((l, t)), b"ID3audio")[1])
    sid = new(); c.post(f"/sessions/{sid}/answers", json={"answers": {**OK, "q5": "yes"}})
    for lang in ("en", "hi", "kn"):
        assert c.get(f"/tts/result/{sid}", params={"lang": lang}).status_code == 200
        assert c.get(f"/tts/alert/{sid}", params={"lang": lang}).status_code == 200
        assert c.get("/tts/question/q6", params={"lang": lang}).status_code == 200
    assert any("दूसरी राय" in t for l, t in said if l == "hi")
    assert any("ಎರಡನೇ ಅಭಿಪ್ರಾಯ" in t for l, t in said if l == "kn")
    assert any("1 8 1" in t for _, t in said)        # helpline digits are read one by one
    ok = new(); c.post(f"/sessions/{ok}/answers", json={"answers": OK})
    assert c.get(f"/tts/alert/{ok}").status_code == 409
    assert c.get("/tts/result/nope").status_code == 404

def test_tts_warm_needs_admin(monkeypatch, tmp_path):
    monkeypatch.setattr(tts, "DIR", str(tmp_path)); monkeypatch.setattr(tts, "synth", lambda t, l: b"ID3audio")
    assert c.post("/admin/tts/warm").status_code == 401
    r = c.post("/admin/tts/warm", headers=A); assert r.status_code == 200 and r.json()["queued"] == 27
