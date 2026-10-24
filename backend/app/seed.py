"""python -m app.seed  -> DEMO data only (clearly labelled). Not real cases."""
import random
from .db import Base, engine, SessionLocal
from . import models as m, rules, asha as A

random.seed(7); Base.metadata.create_all(engine)
DIST = ["Udupi", "Dakshina Kannada", "Raichur", "Koppal", "Ballari", "Belagavi"]
with SessionLocal() as db:
    if db.query(m.Hospital).count(): print("already seeded"); raise SystemExit
    hs = []
    for d in DIST:
        for i, govt in enumerate([True, False]):
            h = m.Hospital(name=f"DEMO {d} {'Government' if govt else 'Private'} Hospital {i+1}", district=d, is_govt=govt, is_demo=True); db.add(h); hs.append(h)
    db.commit()
    demo = []   # two DEMO ASHA accounts so demo flags can form (a flag needs 2+ ASHAs). Their keys are thrown away, nobody can log in as them.
    for _ in range(2):
        a = m.Asha(code=A.new_code(db), district="Udupi", label="DEMO", key_hash=A.hash_key(A.new_key())); db.add(a); db.commit(); demo.append(a)
    hot = hs[5]  # one hospital above the flag threshold
    for n in range(40):
        h = hot if n < 4 else random.choice(hs); adv = n < 4 or random.random() < .3
        a = {"q1": random.choice(["under25", "25_35", "over35"]), "q2": "yes" if adv else "no", "q3": random.choice(["pain", "bleeding", "growth", "none", "dk"]),
             "q4": random.choice(["yes", "no", "dk"]), "q5": random.choice(["yes", "no", "no"]), "q6": random.choice(["yes", "yes", "no"])}
        db.add(m.CaseSession(lang="en", district=h.district, hospital_id=h.id, asha_id=demo[n % 2].id, age_band=a["q1"], answers=a, completed=True,
                             advised=rules.is_advised(a), coercion=rules.is_coercion(a)))
    db.commit(); print("seeded demo hospitals + 40 demo cases")
