"""Same-day alert delivery with retries. First attempt runs right after she consents; anything that fails is retried
with exponential backoff (30s, 1m, 2m ... capped at 1h) by a background loop, up to ALERT_MAX_ATTEMPTS, then marked failed
(visible in /dashboard/alerts; an admin can re-queue with POST /admin/alerts/retry)."""
import os, asyncio, logging
from datetime import timedelta
from sqlalchemy import update
from sqlalchemy.orm import Session
from . import models as m
from .db import SessionLocal
from .notify import send_alert
from .security import audit
log = logging.getLogger("zaroori")

def max_attempts() -> int: return int(os.getenv("ALERT_MAX_ATTEMPTS", "8"))
def backoff(attempts: int) -> timedelta: return timedelta(seconds=min(30 * 2 ** max(attempts - 1, 0), 3600))

def attempt(alert_id: int) -> str | None:
    """Try to deliver one alert. Returns its new status, or None if someone else already claimed it."""
    with SessionLocal() as db:
        # claim: push next_try_at forward so two workers never send the same alert twice
        claimed = db.execute(update(m.Alert).where(m.Alert.id == alert_id, m.Alert.status == "queued", m.Alert.next_try_at <= m.now())
                             .values(next_try_at=m.now() + timedelta(minutes=2))).rowcount
        db.commit()
        if not claimed: return None
        al = db.get(m.Alert, alert_id)
        asha = db.get(m.Asha, al.asha_id) if al.asha_id else None
        ok, err, channel = send_alert(al.id, al.district, al.slip_code or "", asha_code=asha.code if asha else "", asha_contact=asha.contact if asha else "")
        al.attempts += 1
        if ok:
            al.status, al.notified_at, al.next_try_at, al.last_error, al.channel = "sent", m.now(), None, None, channel
            db.commit(); audit(db, "system", "", "alert.sent", f"alert {al.id} via {channel} (attempt {al.attempts})")
        elif al.attempts >= max_attempts():
            al.status, al.next_try_at, al.last_error = "failed", None, (err or "")[:200]
            db.commit(); audit(db, "system", "", "alert.failed", f"alert {al.id} gave up after {al.attempts} attempts")
        else:
            al.next_try_at, al.last_error = m.now() + backoff(al.attempts), (err or "")[:200]
            db.commit(); audit(db, "system", "", "alert.retry", f"alert {al.id} attempt {al.attempts} failed; next in {int(backoff(al.attempts).total_seconds())}s")
        return al.status

def process_due() -> int:
    with SessionLocal() as db:
        ids = [i for (i,) in db.query(m.Alert.id).filter(m.Alert.status == "queued", m.Alert.next_try_at <= m.now()).all()]
    return sum(1 for i in ids if attempt(i) is not None)

def requeue_failed(db: Session) -> int:
    n = db.query(m.Alert).filter(m.Alert.status == "failed").update({"status": "queued", "attempts": 0, "next_try_at": m.now(), "last_error": None})
    db.commit(); return n

async def retry_loop():
    every = int(os.getenv("ALERT_RETRY_SECONDS", "60"))
    while True:
        try: await asyncio.to_thread(process_due)
        except Exception: log.exception("alert retry loop error")
        await asyncio.sleep(every)
