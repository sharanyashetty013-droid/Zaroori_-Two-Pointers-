from .content import QUESTIONS
VALID = {q["id"]: {o["v"] for o in q["options"]} for q in QUESTIONS}

def invalid(ans: dict) -> list[str]:
    return [f"{k}={v}" for k, v in ans.items() if k not in VALID or v not in VALID[k]]
def is_coercion(a: dict) -> bool: return a.get("q5") == "yes" or a.get("q6") == "no"
def is_advised(a: dict) -> bool: return a.get("q2") == "yes"
def is_complete(a: dict) -> bool: return all(k in a for k in VALID)
