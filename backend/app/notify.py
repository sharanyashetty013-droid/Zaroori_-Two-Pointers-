"""Alert delivery. Channels: email (SMTP) and/or webhook (any WhatsApp/SMS gateway or Slack that accepts JSON).
With neither configured it logs a MOCK ALERT and reports channel "mock" so the dashboard shows it was not really sent.
Message carries district only, never identity."""
import os, smtplib, logging
from email.message import EmailMessage
import httpx
log = logging.getLogger("zaroori")

def _body(alert_id: int, district: str, slip_code: str = "", asha_code: str = "", asha_contact: str = "") -> str:
    code = f"Slip code: {slip_code}\n(If the woman calls you, ask her to read the code on her slip to match the case.)\n" if slip_code else ""
    who = (f"ASHA: {asha_code}" + (f" (work contact: {asha_contact})" if asha_contact else "") + "\nPlease reach the woman through this ASHA.\n") if asha_code else ""
    return (f"Zaroori? alert #{alert_id}\nDistrict: {district}\n{who}{code}"
            "A woman said she is being pressured into surgery and agreed to share this. "
            "Please contact the local ASHA network today. No personal details are stored.")

def send_alert(alert_id: int, district: str, slip_code: str = "", asha_code: str = "", asha_contact: str = "") -> tuple[bool, str | None, str]:
    """Returns (delivered, error, channel). Delivered if at least one configured channel worked."""
    body = _body(alert_id, district, slip_code, asha_code, asha_contact)
    to, host, hook = os.getenv("NGO_EMAIL"), os.getenv("SMTP_HOST"), os.getenv("ALERT_WEBHOOK_URL")
    email_on = bool(to and host)
    if not email_on and not hook:
        log.warning("[MOCK ALERT] %s", body); return True, None, "mock"
    ok, errs = [], []
    if email_on:
        try:
            msg = EmailMessage(); msg["Subject"] = f"Zaroori? URGENT alert - {district}"
            msg["From"] = os.getenv("SMTP_USER", "alerts@zaroori.local"); msg["To"] = to; msg.set_content(body)
            with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=15) as s:
                s.starttls()
                if os.getenv("SMTP_USER"): s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS", ""))
                s.send_message(msg)
            ok.append("email")
        except Exception as e: errs.append(f"email: {type(e).__name__}"); log.error("alert email failed: %s", e)
    if hook:
        try:
            r = httpx.post(hook, json={"text": body, "district": district, "alert_id": alert_id, "slip_code": slip_code, "asha_code": asha_code, "asha_contact": asha_contact}, timeout=15); r.raise_for_status(); ok.append("webhook")
        except Exception as e: errs.append(f"webhook: {type(e).__name__}"); log.error("alert webhook failed: %s", e)
    return bool(ok), ("; ".join(errs) or None), "+".join(ok) or "none"
