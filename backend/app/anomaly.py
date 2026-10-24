"""Hospital anomaly check = a prompt for a human to look, never an accusation.

For each hospital with enough completed cases in the window, compare its share of 'advised surgery' with the rest of its
district (or the rest of the state if the district is too small), using a one-sided Fisher exact test. P-values are
Benjamini-Hochberg adjusted across hospitals tested. NFHS district baselines (if loaded) are attached as context only.

Important limit: our cases come from ASHA-assisted sessions, so they are NOT a random sample of the population.
Rates here are not prevalence and must not be compared to NFHS as if they were. The NFHS number is context for the reviewer."""
import os
from math import comb
from datetime import timedelta
from sqlalchemy.orm import Session
from . import models as m

def _p_greater(a: int, n: int, A: int, N: int) -> float:
    """P(X >= a) where X ~ Hypergeometric(N total, A advised, n drawn). Exact, pure python."""
    den = comb(N, n)
    return min(1.0, sum(comb(A, k) * comb(N - A, n - k) for k in range(a, min(A, n) + 1)) / den)

def _bh(ps: list[float]) -> list[float]:
    n = len(ps); order = sorted(range(n), key=lambda i: ps[i]); adj = [0.0] * n; prev = 1.0
    for rank, i in reversed(list(enumerate(order, 1))): prev = min(prev, ps[i] * n / rank); adj[i] = prev
    return adj

def run(db: Session) -> dict:
    window = int(os.getenv("FLAG_WINDOW_DAYS", "90")); min_cases = int(os.getenv("ANOMALY_MIN_CASES", "8"))
    min_rest = int(os.getenv("ANOMALY_MIN_COMPARISON", "10")); alpha = float(os.getenv("ANOMALY_ALPHA", "0.05"))
    cutoff = m.now() - timedelta(days=window)
    rows = (db.query(m.CaseSession.hospital_id, m.Hospital.name, m.Hospital.district, m.CaseSession.advised)
            .join(m.Hospital, m.Hospital.id == m.CaseSession.hospital_id)
            .filter(m.CaseSession.completed == True, m.CaseSession.created_at >= cutoff).all())  # noqa: E712
    per: dict[int, dict] = {}
    for hid, name, dist, adv in rows:
        h = per.setdefault(hid, {"hospital_id": hid, "hospital": name, "district": dist, "n": 0, "a": 0}); h["n"] += 1; h["a"] += int(adv)
    tot_n, tot_a = sum(h["n"] for h in per.values()), sum(h["a"] for h in per.values())
    nfhs = {}
    for r in db.query(m.NfhsStat).filter(m.NfhsStat.indicator.ilike("%hysterectom%")).all(): nfhs[r.district] = {"indicator": r.indicator, "value": r.value, "source": r.source}
    tested = []
    for h in per.values():
        if h["n"] < min_cases: continue
        dn = sum(x["n"] for x in per.values() if x["district"] == h["district"]); da = sum(x["a"] for x in per.values() if x["district"] == h["district"])
        rest_n, rest_a, scope = dn - h["n"], da - h["a"], "district"
        if rest_n < min_rest: rest_n, rest_a, scope = tot_n - h["n"], tot_a - h["a"], "state"
        if rest_n < min_rest: continue
        N, A = h["n"] + rest_n, h["a"] + rest_a
        h.update(rate=round(h["a"] / h["n"], 3), comparison_rate=round(rest_a / rest_n, 3), comparison=scope, comparison_cases=rest_n,
                 p_value=_p_greater(h["a"], h["n"], A, N), nfhs_context=nfhs.get(h["district"]))
        tested.append(h)
    for h, q in zip(tested, _bh([h["p_value"] for h in tested])): h["p_adjusted"] = round(q, 4); h["p_value"] = round(h["p_value"], 4)
    hits = sorted([h for h in tested if h["p_adjusted"] < alpha and h["rate"] > h["comparison_rate"]], key=lambda h: h["p_adjusted"])
    return {"window_days": window, "min_cases": min_cases, "alpha": alpha, "hospitals_tested": len(tested), "anomalies": hits,
            "nfhs_loaded": bool(nfhs),
            "note": "A prompt for a human to check. Not an accusation. Cases come from ASHA-assisted sessions, not a random sample, so rates are not prevalence. NFHS values are context only."}
