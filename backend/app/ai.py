"""AI features. Every AI output is validated; on any doubt we fall back to reviewed templates.
AI can RAISE a coercion signal, never lower one. AI never diagnoses or advises for/against surgery."""
import json, re
from sqlalchemy.orm import Session
from . import llm, content as C, rules

NAME = {"en": "English", "hi": "Hindi", "kn": "Kannada"}
EXTRA_BLOCK = ["ऑपरेशन मत", "सर्जरी मत", "ऑपरेशन न कराएं", "ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ ಮಾಡಿಸಬೇಡಿ", "ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ ಬೇಡ"]
DIAG = re.compile(r"\byou (have|need|must have|should have)\b.{0,40}(cancer|fibroid|infection|surgery|operation|tumou?r)", re.I)
RULES = ("You support Zaroori?, a tool ASHA health workers use with village women who were advised to remove their womb. "
         "Never diagnose. Never say or imply she should or should not have surgery. Never name medicines or doses. "
         "Only encourage: a second opinion, asking the doctor questions, knowing her rights, and calling helplines (Women Helpline 181, emergency 112). "
         "Use very simple words and short sentences, for someone who cannot read. Do not include names or any personal details.")
FALLBACK_ASK = C.t("I can't answer medical questions. Please ask the doctor, or call the Women Helpline 181. If you are in danger, call 112.",
                   "मैं मेडिकल सवालों के जवाब नहीं दे सकती। कृपया डॉक्टर से पूछिए, या महिला हेल्पलाइन 181 पर कॉल कीजिए। खतरा हो तो 112 पर कॉल कीजिए।",
                   "ನಾನು ವೈದ್ಯಕೀಯ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ವೈದ್ಯರನ್ನು ಕೇಳಿ, ಅಥವಾ ಮಹಿಳಾ ಸಹಾಯವಾಣಿ 181ಕ್ಕೆ ಕರೆ ಮಾಡಿ. ಅಪಾಯದಲ್ಲಿದ್ದರೆ 112ಕ್ಕೆ ಕರೆ ಮಾಡಿ.")

def safe(text: str) -> bool:
    low = text.lower()
    return not any(b in low for b in C.BLOCKLIST + EXTRA_BLOCK) and not DIAG.search(low)

def _json(text: str | None):
    if not text: return None
    try: return json.loads(re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip())
    except Exception: return None

def questions_for(s, lang: str, db: Session) -> tuple[list[str], str]:
    """Personalised doctor questions (AI) with cached result; falls back to the reviewed template bank."""
    cache = s.ai_questions or {}
    if lang in cache: return cache[lang], "ai"
    a = s.answers or {}
    if llm.available() and rules.is_complete(a):
        out = _json(llm.complete(RULES + f" Reply only in {NAME[lang]}.",
            f"Situation codes: reason_given={a.get('q3')}, second_doctor_agrees={a.get('q4')}, age_band={a.get('q1')}. "
            'Write 5 or 6 short questions she can ask the doctor before deciding. Return JSON only: {"questions": ["..."]}', json_mode=True))
        qs = out.get("questions") if isinstance(out, dict) else None
        if isinstance(qs, list) and 3 <= len(qs) <= 7 and all(isinstance(q, str) and 5 < len(q) <= 180 and safe(q) for q in qs):
            s.ai_questions = {**cache, lang: qs}; db.commit(); return qs, "ai"
    return [C.pick(q, lang) for q in C.DOCTOR_QUESTIONS], "template"

def ask(question: str, lang: str) -> dict:
    if llm.available():
        txt = llm.complete(RULES + f" Reply only in {NAME[lang]}, in at most 4 short sentences. If she asks for medical advice or a diagnosis, "
                           "say you cannot give it and tell her to ask a doctor. If she may be in danger, tell her to call 112.", question[:500], max_tokens=300)
        if txt and safe(txt): return {"answer": txt.strip(), "source": "ai"}
    return {"answer": C.pick(FALLBACK_ASK, lang), "source": "fallback"}

def extract(text: str, lang: str) -> dict | None:
    """ASHA types or dictates what the woman said; AI proposes answers. ASHA confirms before saving. Text is never stored."""
    if not llm.available(): return None
    out = _json(llm.complete(RULES + " Extract answers from what an ASHA worker wrote. Do not guess. Omit anything unclear.",
        "Allowed values: q1 under25|25_35|over35; q2 yes|no (doctor advised womb removal); q3 pain|bleeding|growth|none|dk; q4 yes|no|dk (second doctor agrees); "
        "q5 yes|no (someone pressuring her); q6 yes|no (feels free to say no). coercion_signal = true if there is ANY sign of pressure, threat, money or job pressure. "
        f'Return JSON only: {{"answers": {{}}, "coercion_signal": false, "unclear": []}}\nText ({NAME[lang]}): {text[:1500]}', json_mode=True, max_tokens=400))
    if not isinstance(out, dict) or not isinstance(out.get("answers"), dict): return None
    ans = {k: v for k, v in out["answers"].items() if k in rules.VALID and v in rules.VALID[k]}
    return {"answers": ans, "coercion_signal": bool(out.get("coercion_signal")) or rules.is_coercion(ans),
            "unclear": [q for q in rules.VALID if q not in ans]}
