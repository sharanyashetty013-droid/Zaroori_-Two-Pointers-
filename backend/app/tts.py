import hashlib, os
from io import BytesIO
DIR = os.getenv("TTS_DIR", "./tts_cache")

def synth(text: str, lang: str) -> bytes:
    from gtts import gTTS   # free Google Translate voice; supports en, hi, kn
    buf = BytesIO(); gTTS(text=text, lang=lang).write_to_fp(buf); return buf.getvalue()

def speak(text: str, lang: str) -> bytes:
    os.makedirs(DIR, exist_ok=True)
    path = os.path.join(DIR, hashlib.sha1(f"{lang}|{text}".encode()).hexdigest() + ".mp3")
    if os.path.exists(path): return open(path, "rb").read()
    data = synth(text, lang); open(path, "wb").write(data); return data
