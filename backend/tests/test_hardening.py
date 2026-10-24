"""Roles, audit log, anomaly check, alert retries, rate limiting, multilingual PDF."""
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app import models as m, delivery, security, ratelimit, db as dbmod
from app.db import SessionLocal
from tests.conftest import make_asha

c = TestClient(app)
ADM, REV, VIEW = {"X-API-Key": "k"}, {"X-API-Key": "rk"}, {"X-API-Key": "vk"}
OK = {"q1": "25_35", "q2": "yes", "q3": "none", "q4": "no", "q5": "no", "q6": "yes"}
NOT_ADV = {**OK, "q2": "no"}

def mk_hosp(name, district, govt=True):
    with SessionLocal() as db:
        h = m.Hospital(name=name, district=district, is_govt=govt); db.add(h); db.commit(); return h.id

_KEYS = {}
def key_for(district):
    if district not in _KEYS: _KEYS[district] = [make_asha(district)[1], make_asha(district)[1]]
    return _KEYS[district]

_flip = {}
def session(district="Udupi", hid=None, answers=None, lang="en", key=None):
    ks = key_for(district); _flip[district] = _flip.get(district, -1) + 1   # alternate between two ASHAs so hospital flags can form
    sid = c.post("/sessions", json={"lang": lang, "district": district, "hospital_id": hid}, headers={"X-Asha-Key": key or ks[_flip[district] % 2]}).json()["session_id"]
    if answers: c.post(f"/sessions/{sid}/answers", json={"answers": answers})
    return sid

# ---------- PDF ----------
@pytest.mark.parametrize("lang", ["en", "hi", "kn"])
def test_slip_in_every_language(lang):
    hid = mk_hosp(f"Govt {lang}", "Udupi"); sid = session(hid=hid, answers=OK, lang=lang)
    r = c.get(f"/sessions/{sid}/slip.pdf"); assert r.status_code == 200 and r.content[:4] == b"%PDF"
    assert b"Noto" in r.content   # a real Unicode font is embedded, not Helvetica
def test_slip_lang_override():
    sid = session(answers=OK, lang="en"); assert c.get(f"/sessions/{sid}/slip.pdf", params={"lang": "kn"}).status_code == 200

# ---------- roles + audit ----------
def test_roles():
    assert c.get("/dashboard/map").status_code == 401
    assert c.get("/dashboard/map", headers={"X-API-Key": "nope"}).status_code == 401
    assert c.get("/dashboard/map", headers=VIEW).status_code == 200
    assert c.get("/dashboard/flags", headers=VIEW).status_code == 403
    assert c.get("/dashboard/flags", headers=REV).status_code == 200
    assert c.get("/dashboard/anomalies", headers=VIEW).status_code == 403
    assert c.get("/admin/audit", headers=REV).status_code == 403
    assert c.post("/admin/hospitals", json=[{"name": "X", "district": "Y"}], headers=REV).status_code == 403
    assert c.get("/dashboard/map", headers=ADM).status_code == 200   # admin can do everything

def test_audit_log_records_access_and_has_no_pii():
    sid = session(answers={**OK, "q5": "yes"}); c.post("/alerts", json={"session_id": sid, "consent": True})
    c.get("/dashboard/flags", headers=REV); c.get("/dashboard/map", headers={"X-API-Key": "wrong"})
    e = c.get("/admin/audit", headers=ADM).json()["entries"]; acts = {x["action"] for x in e}
    assert {"flags.read", "denied:viewer", "alert.created"} <= acts
    assert all(sid not in str(x) for x in e)                       # session ids never enter the log
    assert all("rk" not in x["actor"] and len(x["actor"]) <= 8 for x in e)   # only a short key fingerprint

def test_production_refuses_weak_admin_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production"); monkeypatch.setenv("ADMIN_API_KEY", "change-me")
    with pytest.raises(RuntimeError): security.check_config()
    monkeypatch.setenv("ADMIN_API_KEY", "a-long-random-secret"); security.check_config()

def test_flag_review_workflow():
    hid = mk_hosp("Review Me", "Udupi", False)
    for _ in range(3): session(hid=hid, answers=OK)
    f = [x for x in c.get("/dashboard/flags", headers=REV).json()["flagged"] if x["hospital_id"] == hid][0]
    assert f["review"]["status"] == "open"
    assert c.post(f"/dashboard/flags/{hid}/review", json={"status": "reviewing", "note": "asked DHO"}, headers=VIEW).status_code == 403
    assert c.post(f"/dashboard/flags/{hid}/review", json={"status": "reviewing", "note": "asked DHO"}, headers=REV).status_code == 200
    f = [x for x in c.get("/dashboard/flags", headers=REV).json()["flagged"] if x["hospital_id"] == hid][0]
    assert f["review"]["status"] == "reviewing" and f["review"]["note"] == "asked DHO"
    assert c.post(f"/dashboard/flags/{hid}/review", json={"status": "bogus"}, headers=REV).status_code == 422

# ---------- anomaly ----------
def test_anomaly_detects_outlier_only():
    a, b = mk_hosp("Outlier Hospital", "AnomalyLand", False), mk_hosp("Normal Hospital", "AnomalyLand", False)
    for _ in range(10): session("AnomalyLand", a, OK)
    for i in range(12): session("AnomalyLand", b, OK if i == 0 else NOT_ADV)
    r = c.get("/dashboard/anomalies", headers=REV).json()
    names = [x["hospital"] for x in r["anomalies"]]
    assert "Outlier Hospital" in names and "Normal Hospital" not in names
    o = [x for x in r["anomalies"] if x["hospital"] == "Outlier Hospital"][0]
    assert o["rate"] == 1.0 and o["comparison"] == "district" and o["p_adjusted"] < 0.05 and "not an accusation" in r["note"].lower()

def test_anomaly_ignores_small_samples_and_similar_rates():
    a, b = mk_hosp("Tiny", "SmallLand", False), mk_hosp("Peer1", "SmallLand", False)
    for _ in range(3): session("SmallLand", a, OK)          # below ANOMALY_MIN_CASES
    for i in range(12): session("SmallLand", b, OK if i % 2 else NOT_ADV)
    assert not [x for x in c.get("/dashboard/anomalies", headers=REV).json()["anomalies"] if x["district"] == "SmallLand"]

def test_anomaly_attaches_nfhs_context():
    with SessionLocal() as db:
        db.add(m.NfhsStat(district="CtxLand", indicator="Women who have had a hysterectomy (%)", value=3.1, source="TEST")); db.commit()
    a, b = mk_hosp("Ctx Outlier", "CtxLand", False), mk_hosp("Ctx Peer", "CtxLand", False)
    for _ in range(10): session("CtxLand", a, OK)
    for _ in range(12): session("CtxLand", b, NOT_ADV)
    r = c.get("/dashboard/anomalies", headers=REV).json(); o = [x for x in r["anomalies"] if x["district"] == "CtxLand"][0]
    assert r["nfhs_loaded"] and o["nfhs_context"]["value"] == 3.1

# ---------- alert retries ----------
def _alert_row(aid):
    with SessionLocal() as db: a = db.get(m.Alert, aid); return a.status, a.attempts, a.channel, a.next_try_at, a.last_error

def test_alert_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr(delivery, "send_alert", lambda i, d, code="", **k: (False, "email: SMTPException", "none"))
    sid = session(answers={**OK, "q6": "no"}); aid = c.post("/alerts", json={"session_id": sid, "consent": True}).json()["alert_id"]
    st, n, ch, nxt, err = _alert_row(aid)
    assert (st, n) == ("queued", 1) and nxt > m.now() and "SMTP" in err      # first try failed, scheduled for retry
    assert delivery.process_due() == 0                                         # not due yet
    with SessionLocal() as db: db.get(m.Alert, aid).next_try_at = m.now() - timedelta(seconds=1); db.commit()
    monkeypatch.setattr(delivery, "send_alert", lambda i, d, code="", **k: (True, None, "email"))
    assert delivery.process_due() >= 1
    st, n, ch, nxt, err = _alert_row(aid); assert (st, n, ch, nxt, err) == ("sent", 2, "email", None, None)
    assert c.get(f"/sessions/{sid}/result").json()["alert"]["delivery"] == "sent"

def test_alert_gives_up_then_admin_requeues(monkeypatch):
    monkeypatch.setenv("ALERT_MAX_ATTEMPTS", "2")
    monkeypatch.setattr(delivery, "send_alert", lambda i, d, code="", **k: (False, "webhook: ConnectError", "none"))
    sid = session(answers={**OK, "q5": "yes"}); aid = c.post("/alerts", json={"session_id": sid, "consent": True}).json()["alert_id"]
    with SessionLocal() as db: db.get(m.Alert, aid).next_try_at = m.now() - timedelta(seconds=1); db.commit()
    delivery.process_due(); assert _alert_row(aid)[:2] == ("failed", 2)
    assert c.get("/dashboard/alerts", headers=REV).json()["failed"] >= 1
    assert c.post("/admin/alerts/retry", headers=REV).status_code == 403
    assert c.post("/admin/alerts/retry", headers=ADM).json()["requeued"] >= 1
    monkeypatch.setattr(delivery, "send_alert", lambda i, d, code="", **k: (True, None, "webhook")); delivery.process_due()
    assert _alert_row(aid)[0] == "sent"

def test_alert_is_claimed_once(monkeypatch):
    calls = []; monkeypatch.setattr(delivery, "send_alert", lambda i, d, code="", **k: (calls.append(i), (True, None, "email"))[1])
    sid = session(answers={**OK, "q5": "yes"}); aid = c.post("/alerts", json={"session_id": sid, "consent": True}).json()["alert_id"]
    assert delivery.attempt(aid) is None and calls.count(aid) == 1   # background task already delivered it; a second worker must not resend

def test_mock_delivery_is_visible(monkeypatch):
    for k in ("NGO_EMAIL", "SMTP_HOST", "ALERT_WEBHOOK_URL"): monkeypatch.delenv(k, raising=False)
    sid = session(answers={**OK, "q5": "yes"}); aid = c.post("/alerts", json={"session_id": sid, "consent": True}).json()["alert_id"]
    assert _alert_row(aid)[:3] == ("sent", 1, "mock")   # dashboard can show this was NOT really delivered

def test_notify_webhook(monkeypatch):
    from app import notify; seen = {}
    class R:
        def raise_for_status(self): pass
    monkeypatch.setenv("ALERT_WEBHOOK_URL", "http://hook.test/x"); monkeypatch.delenv("NGO_EMAIL", raising=False)
    monkeypatch.setattr(notify.httpx, "post", lambda url, json, timeout: (seen.update(url=url, body=json), R())[1])
    ok, err, ch = notify.send_alert(7, "Udupi"); assert ok and ch == "webhook" and seen["body"]["district"] == "Udupi" and "Udupi" in seen["body"]["text"]

# ---------- rate limiting ----------
def test_rate_limit_on_writes(monkeypatch):
    monkeypatch.delenv("RATE_LIMIT_DISABLED")
    monkeypatch.setenv("RATE_WRITE_PER_MIN", "3")
    k = make_asha()[1]
    codes = [c.post("/sessions", json={"district": "Udupi"}, headers={"X-Asha-Key": k}).status_code for _ in range(5)]
    assert codes == [201, 201, 201, 429, 429]
    assert c.get("/health").status_code == 200   # health checks are never limited

def test_rate_limit_on_dashboard_slows_key_guessing(monkeypatch):
    monkeypatch.delenv("RATE_LIMIT_DISABLED")
    monkeypatch.setenv("RATE_AUTH_PER_MIN", "4")
    codes = [c.get("/dashboard/map", headers={"X-API-Key": f"guess{i}"}).status_code for i in range(6)]
    assert codes == [401] * 4 + [429] * 2

def test_forwarded_for_not_spoofable_behind_proxy(monkeypatch):
    monkeypatch.delenv("RATE_LIMIT_DISABLED")
    monkeypatch.setenv("RATE_WRITE_PER_MIN", "2"); monkeypatch.setenv("TRUSTED_PROXY_HOPS", "1")
    k = make_asha()[1]
    codes = [c.post("/sessions", json={"district": "Udupi"}, headers={"X-Forwarded-For": f"9.9.9.{i}, 5.5.5.5", "X-Asha-Key": k}).status_code for i in range(3)]
    assert codes == [201, 201, 429]   # client-supplied first entry is ignored; the proxy-appended one counts

# ---------- schema upgrade ----------
def test_add_missing_columns_on_old_db(monkeypatch, tmp_path):
    from sqlalchemy import create_engine, inspect
    e = create_engine(f"sqlite:///{tmp_path}/old.db")
    with e.begin() as cx: cx.execute(text("CREATE TABLE alerts (id INTEGER PRIMARY KEY, session_id VARCHAR(36), district VARCHAR(80), status VARCHAR(20), created_at DATETIME, notified_at DATETIME)"))
    monkeypatch.setattr(dbmod, "engine", e); dbmod.add_missing_columns()
    cols = {x["name"] for x in inspect(e).get_columns("alerts")}; assert {"attempts", "next_try_at", "last_error", "channel"} <= cols
    with e.begin() as cx: cx.execute(text("INSERT INTO alerts (id, session_id, district, status) VALUES (1,'s','d','new')"))
    with e.connect() as cx: assert cx.execute(text("SELECT attempts FROM alerts")).scalar() == 0


# ---------- ASHA login ----------
def test_no_key_no_session_and_bad_key_rejected():
    assert c.post("/sessions", json={"district": "Udupi"}).status_code == 401
    assert c.post("/sessions", json={"district": "Udupi"}, headers={"X-Asha-Key": "asha_made_up"}).status_code == 401
    assert c.get("/asha/me").status_code == 401

def test_admin_creates_asha_key_shown_once_and_only_hash_stored():
    assert c.post("/admin/ashas", json={"district": "Udupi"}).status_code == 401
    assert c.post("/admin/ashas", json={"district": "Udupi"}, headers=REV).status_code == 403
    r = c.post("/admin/ashas", json={"district": "Udupi", "label": "PHC Test", "contact": "9000000000"}, headers=ADM).json()
    key, code = r["key"], r["code"]; assert code.startswith("ASHA-") and key.startswith("asha_")
    lst = c.get("/admin/ashas", headers=ADM); assert key not in lst.text and any(a["code"] == code for a in lst.json()["ashas"])
    with SessionLocal() as db: assert db.query(m.Asha).filter(m.Asha.code == code).first().key_hash != key
    me = c.get("/asha/me", headers={"X-Asha-Key": key}).json(); assert me["code"] == code and me["district"] == "Udupi"
    sid = c.post("/sessions", json={"lang": "hi"}, headers={"X-Asha-Key": key})   # district defaults to hers
    assert sid.status_code == 201
    with SessionLocal() as db:
        s = db.get(m.CaseSession, sid.json()["session_id"]); assert s.district == "Udupi" and s.asha_id is not None

def test_asha_only_in_her_own_district_and_daily_cap(monkeypatch):
    _, key = make_asha("Udupi"); H = {"X-Asha-Key": key}
    assert c.post("/sessions", json={"district": "Bidar"}, headers=H).status_code == 403
    monkeypatch.setenv("ASHA_MAX_SESSIONS_PER_DAY", "2")
    assert [c.post("/sessions", json={}, headers=H).status_code for _ in range(3)] == [201, 201, 429]

def test_deactivate_and_new_key():
    r = c.post("/admin/ashas", json={"district": "Udupi"}, headers=ADM).json(); H = {"X-Asha-Key": r["key"]}
    assert c.post("/sessions", json={}, headers=H).status_code == 201
    assert c.post(f"/admin/ashas/{r['id']}/deactivate", headers=ADM).status_code == 200
    assert c.post("/sessions", json={}, headers=H).status_code == 401
    assert c.post(f"/admin/ashas/{r['id']}/activate", headers=ADM).status_code == 200
    assert c.post("/sessions", json={}, headers=H).status_code == 201
    k2 = c.post(f"/admin/ashas/{r['id']}/new-key", headers=ADM).json()["key"]
    assert c.post("/sessions", json={}, headers=H).status_code == 401 and c.post("/sessions", json={}, headers={"X-Asha-Key": k2}).status_code == 201
    assert c.post("/admin/ashas/99999/deactivate", headers=ADM).status_code == 404

def test_one_asha_alone_cannot_flag_a_hospital():
    hid = mk_hosp("Single ASHA Hospital", "SoloLand", False); k = make_asha("SoloLand")[1]
    for _ in range(4): session("SoloLand", hid, OK, key=k)
    assert hid not in [f["hospital_id"] for f in c.get("/dashboard/flags", headers=REV).json()["flagged"]]
    session("SoloLand", hid, OK, key=make_asha("SoloLand")[1])   # a second ASHA reports the same hospital
    f = [x for x in c.get("/dashboard/flags", headers=REV).json()["flagged"] if x["hospital_id"] == hid]
    assert len(f) == 1 and f[0]["ashas"] == 2 and f[0]["cases"] == 5

def test_alert_carries_asha_code_and_contact(monkeypatch):
    from app import notify
    aid, key = make_asha("Udupi", contact="9111111111")
    sid = session(answers={**OK, "q5": "yes"}, key=key)
    seen = []; monkeypatch.setattr(notify, "send_alert", lambda i, d, code="", asha_code="", asha_contact="": (seen.append((asha_code, asha_contact)), (True, None, "email"))[1])
    monkeypatch.setattr(delivery, "send_alert", notify.send_alert)
    assert c.post("/alerts", json={"session_id": sid, "consent": True}).status_code == 201
    with SessionLocal() as db: code = db.get(m.Asha, aid).code
    assert seen and seen[0] == (code, "9111111111")
    row = c.get("/dashboard/alerts", headers=REV, params={"code": sid[:8].upper()}).json()["alerts"][0]
    assert row["asha_code"] == code and "session_id" not in row
    body = notify._body(1, "Udupi", "ABC12345", code, "9111111111"); assert code in body and "ASHA" in body

def test_production_refuses_login_off(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production"); monkeypatch.setenv("ADMIN_API_KEY", "a-long-random-secret"); monkeypatch.setenv("ASHA_LOGIN_REQUIRED", "0")
    with pytest.raises(RuntimeError): security.check_config()

def test_login_off_allows_local_demo(monkeypatch):
    monkeypatch.setenv("ASHA_LOGIN_REQUIRED", "0")
    assert c.post("/sessions", json={"district": "Udupi"}).status_code == 201
    assert c.post("/sessions", json={}).status_code == 422   # district still needed when there is no ASHA
