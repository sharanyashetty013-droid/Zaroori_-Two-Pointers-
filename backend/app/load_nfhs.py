"""python -m app.load_nfhs data/nfhs.csv   (columns: district,indicator,value,source). Use REAL NFHS numbers only."""
import csv, sys
from .db import Base, engine, SessionLocal
from . import models as m

Base.metadata.create_all(engine)
with SessionLocal() as db, open(sys.argv[1], newline="", encoding="utf-8") as f:
    n = 0
    for r in csv.DictReader(f):
        db.add(m.NfhsStat(district=r["district"].strip(), indicator=r["indicator"].strip(), value=float(r["value"]), source=r.get("source", "NFHS"))); n += 1
    db.commit(); print(f"loaded {n} rows")
