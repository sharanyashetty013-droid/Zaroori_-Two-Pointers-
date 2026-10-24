import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Hospital(Base):
    __tablename__ = "hospitals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    district: Mapped[str] = mapped_column(String(80), index=True)
    is_govt: Mapped[bool] = mapped_column(Boolean, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)

class Asha(Base):
    """A field worker account. Holds the ASHA's code and a HASH of her key, never the key itself and never anything about the women she helps."""
    __tablename__ = "ashas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    district: Mapped[str] = mapped_column(String(80), index=True)
    label: Mapped[str] = mapped_column(String(120), default="")
    contact: Mapped[str] = mapped_column(String(40), default="")
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class CaseSession(Base):  # anonymous: no name, phone or ID of any kind for the woman. Only the ASHA's code.
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lang: Mapped[str] = mapped_column(String(2), default="en")
    district: Mapped[str] = mapped_column(String(80), index=True)
    hospital_id: Mapped[int | None] = mapped_column(ForeignKey("hospitals.id"), nullable=True)
    asha_id: Mapped[int | None] = mapped_column(ForeignKey("ashas.id"), nullable=True, index=True)
    age_band: Mapped[str | None] = mapped_column(String(10), nullable=True)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    advised: Mapped[bool] = mapped_column(Boolean, default=False)
    coercion: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_coercion: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_questions: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), unique=True)
    asha_id: Mapped[int | None] = mapped_column(ForeignKey("ashas.id"), nullable=True)
    district: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(20), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # delivery tracking: status = queued -> sent | failed (retried with backoff until MAX attempts)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_try_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(200), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(40), nullable=True)   # mock | email | webhook | email+webhook
    slip_code: Mapped[str | None] = mapped_column(String(8), index=True, nullable=True)   # same code printed on her slip; lets her prove it is her case if she calls the NGO

class NfhsStat(Base):
    __tablename__ = "nfhs_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district: Mapped[str] = mapped_column(String(80), index=True)
    indicator: Mapped[str] = mapped_column(String(200))
    value: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(200), default="NFHS")

class AuditLog(Base):
    """Who touched what. No IPs, no session ids, no personal data. Actor = first 8 hex of sha256(api key)."""
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    role: Mapped[str] = mapped_column(String(20))
    actor: Mapped[str] = mapped_column(String(16), default="")
    action: Mapped[str] = mapped_column(String(80), index=True)
    detail: Mapped[str] = mapped_column(String(300), default="")

class FlagReview(Base):
    """A reviewer's decision on a flagged hospital. Flags are never public."""
    __tablename__ = "flag_reviews"
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospitals.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="open")   # open | reviewing | dismissed | escalated
    note: Mapped[str] = mapped_column(String(300), default="")
    reviewer: Mapped[str] = mapped_column(String(16), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now)
