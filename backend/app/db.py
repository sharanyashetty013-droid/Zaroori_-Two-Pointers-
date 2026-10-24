import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

URL = os.getenv("DATABASE_URL", "sqlite:///./zaroori.db")
if URL.startswith("postgres://"):
    URL = URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(URL, connect_args={"check_same_thread": False} if URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_missing_columns():
    """create_all never alters existing tables. Add any new nullable/defaulted columns (e.g. alerts.attempts) in place."""
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    for t in Base.metadata.sorted_tables:
        if not insp.has_table(t.name): continue
        have = {c["name"] for c in insp.get_columns(t.name)}
        for c in t.columns:
            if c.name in have: continue
            typ = c.type.compile(engine.dialect)
            default = "" if c.default is None or not getattr(c.default, "is_scalar", False) else f" DEFAULT {int(c.default.arg) if isinstance(c.default.arg, bool) else repr(c.default.arg)}"
            with engine.begin() as cx: cx.execute(text(f'ALTER TABLE {t.name} ADD COLUMN {c.name} {typ}{default}'))
