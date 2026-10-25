# Zaroori? Backend (FastAPI)

Anonymous by design: no name, phone or ID is ever stored.

## Run
```
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then export the vars, or set them in Render
# python -m app.seed       # OPTIONAL dev-only demo data. Skip it for real use. Never attach fake cases to a real hospital.
uvicorn app.main:app --reload
```
Docs: http://localhost:8000/docs   |   Tests: `pytest`

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | /questions?lang=hi | 6 questions + options (en/hi/kn) |
| GET | /hospitals?district= | hospitals in a district |
| POST | /sessions | start anonymous session `{lang,hospital_id?}`. **Needs header `X-Asha-Key`.** District comes from the ASHA's account |
| GET | /asha/me | check an ASHA key (header `X-Asha-Key`): returns her code and district |
| POST | /admin/ashas | admin: create an ASHA `{district,label?,contact?}`. Returns her key ONCE |
| GET | /admin/ashas | admin: list ASHAs (never shows keys) |
| POST | /admin/ashas/{id}/deactivate, /activate, /new-key | admin: switch off, switch on, replace a lost key |
| POST | /sessions/{id}/answers | `{answers:{q1..q6}}` returns result |
| GET | /sessions/{id}/result?lang= | headline, doctor questions, govt hospitals, red alert block |
| GET | /sessions/{id}/slip.pdf?lang= | anonymous PDF slip in en / hi / kn (defaults to the session language) |
| POST | /alerts | `{session_id, consent:true}` sends NGO/officer alert |
| GET | /dashboard/map | cases + NFHS per district (**viewer**) |
| GET | /dashboard/flags | hospitals with 3+ cases + review status (**reviewer**) |
| POST | /dashboard/flags/{hospital_id}/review | `{status: open/reviewing/dismissed/escalated, note}` (**reviewer**) |
| GET | /dashboard/anomalies | statistical outliers vs district peers (**reviewer**) |
| GET | /dashboard/alerts?code= | alert delivery status, attempts, errors, mock vs real. `?code=` finds the alert for a slip code (**reviewer**) |
| GET | /admin/audit | who accessed what (**admin**) |
| POST | /admin/alerts/retry | re-queue alerts that gave up (**admin**) |

## AI features (set GEMINI_API_KEY or ANTHROPIC_API_KEY)
| Method | Path | What it does |
|---|---|---|
| GET | /ai/status | which AI provider is active |
| POST | /ai/ask | `{question, lang}` plain-language helper. Refuses medical advice, points to doctor/181/112 |
| POST | /ai/extract | `{text, lang, session_id?}` ASHA types or dictates what she said, AI proposes q1-q6 answers. ASHA confirms, then POST answers. Text is never stored |
| GET | /tts?text=&lang= | voice (mp3, cached) in en/hi/kn |
| GET | /tts/question/q1?lang=hi | reads a question and its options aloud |
| GET | /tts/result/{sid}?lang=kn | reads the whole result screen aloud (headline, doctor questions, note) |
| GET | /tts/alert/{sid}?lang=hi | reads the red screen aloud: her right to say no + helplines, digits one by one |
| POST | /admin/tts/warm | pre-generates all fixed audio in en, hi, kn so it is fast and works on weak internet (**admin**) |
| POST | /admin/hospitals | load your REAL hospital list (**admin**) |

Also: `GET /sessions/{id}/result` now returns AI-personalised doctor questions (`questions_source: "ai"`), cached per language.

**Safety design:** every AI output passes a blocklist and a no-diagnosis check. On any failure, timeout or missing key it falls back to the reviewed templates. AI can only RAISE the coercion signal, never lower it. Without a key everything still works with templates (`/ai/extract` returns 503, so use the buttons).
Voice uses gTTS (free, unofficial Google voice). For production, swap `app/tts.py` for Google Cloud Text-to-Speech.

## How the NGO reaches a woman who asks for help (no identity stored)
Every alert carries the **slip code** (the same 8 characters printed on her PDF slip), the district, and nothing else.
1. She gives consent on the red screen, so the alert is sent to the NGO or officer.
2. The NGO contact (or the local ASHA network) reaches out through the ASHA didi, or she calls the helpline herself.
3. She reads out the code on her slip. The reviewer opens `GET /dashboard/alerts?code=<CODE>` and matches the case.
The code identifies nobody on its own, so she stays anonymous unless she chooses to come forward.

## Rules
- Coercion = Q5 "yes" (someone pushing) OR Q6 "no" (not free to say no). Result returns `coercion:true` and an `alert` block (rights + helplines). The alert is sent only after she consents via `POST /alerts`.
- Flag = `FLAG_THRESHOLD` (3) advised-surgery cases at one hospital within `FLAG_WINDOW_DAYS` (90). A flag means "please check", never an accusation.
- Text never diagnoses or says "don't do surgery" (BLOCKLIST test in tests).

## Roles and audit log
Three keys, sent as `X-API-Key`: `VIEWER_API_KEY` (map) < `REVIEWER_API_KEY` (flags, anomalies, alerts) < `ADMIN_API_KEY` (everything). Flags never go to the viewer role because the PRD says flags go to a reviewer first.
Every dashboard read, review decision, denied login, alert creation and alert delivery is written to `audit_log`. It stores role, a short key fingerprint, action and a short detail. It never stores IPs or session ids.
With `APP_ENV=production` the app refuses to start if `ADMIN_API_KEY` is empty, `change-me` or `dev-admin-key`.

## Alert delivery and retries
`POST /alerts` queues the alert and tries once immediately. If email/webhook fails, a background loop retries with backoff (30s, 1m, 2m ... max 1h) up to `ALERT_MAX_ATTEMPTS`, then marks it `failed` (see `/dashboard/alerts`, re-queue with `/admin/alerts/retry`). Channels: SMTP email and/or `ALERT_WEBHOOK_URL`. With neither set, delivery is `channel: "mock"` so the dashboard shows it was only logged. For WhatsApp/SMS, point the webhook at your gateway. The retry loop runs inside the web process, so keep one worker on the free Render plan.

## Anomaly check
`/dashboard/anomalies` compares each hospital's share of "advised surgery" cases with the rest of its district (or the state if the district is too small) using a one-sided Fisher exact test, with Benjamini-Hochberg correction across hospitals. A hospital needs `ANOMALY_MIN_CASES` cases first. If NFHS rows with "hysterectomy" in the indicator name are loaded, they are attached as context. It is a prompt to check, not an accusation. Cases come from ASHA-assisted sessions, so rates are not population prevalence and must not be read against NFHS as if they were.

## Rate limiting
Per IP, every endpoint: 120/min default, 20/min for creating sessions and alerts, 30/min for AI/voice and for dashboard/admin (slows key guessing). On Render set `TRUSTED_PROXY_HOPS=1`. The counters are in memory, so they reset on restart and are per process.

## PDF fonts
Hindi and Kannada render with Noto Sans (OFL, in `app/fonts`) through fpdf2 + HarfBuzz shaping. Plain reportlab cannot shape these scripts, which is why it was replaced.

## Upgrading an existing database
New columns (`alerts.attempts` etc.) and tables are added automatically on startup.

## Before launch (TODO)
1. Verify helpline numbers in `app/content.py`.
2. Native-speaker review of Hindi and Kannada text.
3. Load REAL NFHS numbers: fill `data/nfhs_template.csv`, then `python -m app.load_nfhs data/nfhs_template.csv`. Use `GET /dashboard/map`.
4. Set `NGO_EMAIL` + SMTP vars for real alerts (otherwise it logs a MOCK ALERT).
5. Set a strong `ADMIN_API_KEY` and `CORS_ORIGINS` to your frontend URL.
6. Add your real hospitals: `POST /admin/hospitals` (or SQL insert).
7. Native-speaker review of the new slip labels in `app/content.py` (`SLIP_*`).
8. Set `APP_ENV=production`, a strong `REVIEWER_API_KEY` and `VIEWER_API_KEY`.

## Deploy on Render
Build: `pip install -r requirements.txt` | Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
Add a Render Postgres and set `DATABASE_URL`. Run `python -m app.seed` once from the Render shell for demo data.

## Frontend flow
start session -> GET /questions -> POST answers -> show result -> (red screen -> POST /alerts) -> GET slip.pdf

## ASHA login
1. Admin creates an account: `POST /admin/ashas` with `{"district":"Udupi","label":"PHC name","contact":"work phone"}`. The response has her `key`. It is shown once. Only a hash is stored.
2. The ASHA enters the key in the app. The app sends it on `POST /sessions` as header `X-Asha-Key`. `GET /asha/me` checks it.
3. A session stores her code (e.g. `ASHA-4K7QX`), never the woman's identity. She can only start sessions in her own district, up to `ASHA_MAX_SESSIONS_PER_DAY`.
4. A hospital flag needs `FLAG_THRESHOLD` cases from at least `FLAG_MIN_ASHAS` different ASHAs, so one person cannot flag a hospital alone. Sessions made before ASHA login have no ASHA and do not count toward flags.
5. Alerts include the ASHA code and her work contact, so the NGO reaches the woman through her. `/dashboard/alerts` shows `asha_code`.
Local demo without keys: `ASHA_LOGIN_REQUIRED=0`. Production refuses to start with it.

## Loading real data (no demo)
1. **Hospitals:** `POST /admin/hospitals` (header `X-API-Key: <ADMIN_API_KEY>`) with a JSON list, see `data/hospitals_template.json`. Use official government lists.
2. **NFHS:** fill `data/nfhs_template.csv`, then `python -m app.load_nfhs data/nfhs_template.csv`.
3. **Flags only come from real sessions.** Public data never flags a hospital. A flag needs 3+ real advised cases from 2+ different ASHAs, and a reviewer checks it before anything is done.

## Known limits (read before real use)
- ASHA login is built (see below). Keys are shared secrets: if an ASHA loses her phone, replace her key with `/admin/ashas/{id}/new-key`. There is no OTP or password reset yet.
- A district with very few ASHAs means the ASHA code plus the district could point to one small area. Keep the ASHA code out of anything public.
- Rate-limit counters live in memory and reset on restart.
- Helpline numbers and Hindi/Kannada text are unverified until a native speaker and an NGO check them.
- Get legal advice on data protection and consent wording before a real pilot.
