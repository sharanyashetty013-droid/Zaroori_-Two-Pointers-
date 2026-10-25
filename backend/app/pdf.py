"""Anonymous slip in English, Hindi or Kannada.
fpdf2 + uharfbuzz does the text shaping. Plain reportlab cannot shape Devanagari/Kannada
conjuncts, so Hindi/Kannada would come out broken. Fonts: Noto Sans (OFL), in app/fonts."""
import os
from datetime import date
from fpdf import FPDF
from . import content as C

FONTS = os.path.join(os.path.dirname(__file__), "fonts")
SCRIPT_FONT = {"en": "NotoSans", "hi": "NotoSansDevanagari", "kn": "NotoSansKannada"}

def _pdf(lang: str) -> FPDF:
    p = FPDF(format="A4"); p.set_margins(18, 18, 18); p.set_auto_page_break(True, 18)
    for fam in {"NotoSans", SCRIPT_FONT[lang]}:
        for style, suffix in (("", "Regular"), ("B", "Bold")):
            p.add_font(fam, style, os.path.join(FONTS, f"{fam}-{suffix}.ttf"))
    p.set_text_shaping(True)
    p.set_fallback_fonts(["NotoSans"])   # digits / latin district names inside Hindi or Kannada text
    p.add_page(); return p

def make_slip(code: str, district: str, hospitals: list[str], questions: list[str] | None = None, lang: str = "en") -> bytes:
    lang = lang if lang in SCRIPT_FONT else "en"; f = SCRIPT_FONT[lang]; p = _pdf(lang)
    def line(text, size, bold=False, gap=2, italic_grey=False):
        p.set_font(f, "B" if bold else "", size); p.set_text_color(90) if italic_grey else p.set_text_color(0)
        p.multi_cell(0, size * 0.55, text, new_x="LMARGIN", new_y="NEXT"); p.ln(gap)
    line(C.pick(C.SLIP_TITLE, lang), 20, True, 3)
    line(C.pick(C.SLIP_META, lang).format(code=code, date=f"{date.today():%d %b %Y}", district=district), 10, gap=6)
    line(C.pick(C.HEADLINE, lang), 15, True, 2)
    line(C.pick(C.NOTE, lang), 10.5, gap=6)
    line(C.pick(C.SLIP_Q_HEAD, lang), 13, True, 2)
    for i, q in enumerate(questions or [C.pick(d, lang) for d in C.DOCTOR_QUESTIONS], 1): line(f"{i}. {q}", 11, gap=1.5)
    p.ln(5); line(C.pick(C.SLIP_H_HEAD, lang), 13, True, 2)
    for n in hospitals[:5] or [C.pick(C.SLIP_NO_HOSP, lang)]: line(f"- {n}", 11, gap=1.5)
    p.ln(6); line(C.pick(C.SLIP_FOOT, lang), 9.5, gap=0, italic_grey=True)
    return bytes(p.output())
