import { useEffect, useState } from 'react'
import { BASE } from '../api'
import '../shell.css'

async function call(path, key, method = 'GET', body) {
  const res = await fetch(BASE + path, {
    method,
    headers: { 'x-api-key': key, 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(String(res.status))
  return res.json()
}

const TABS = [
  { key: 'overview', label: 'Overview', d: 'M3 12l9-8 9 8M5 10v10h14V10' },
  { key: 'districts', label: 'Districts', d: 'M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11zM12 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z' },
  { key: 'flags', label: 'Hospital flags', d: 'M5 21V4M5 4h11l-2 4 2 4H5' },
  { key: 'alerts', label: 'Alerts', d: 'M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0' },
]

function Icon({ d }) {
  return (
    <svg className="sh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={d} />
    </svg>
  )
}

function Bar({ label, value, max }) {
  const pct = max ? Math.min(100, Math.round((value / max) * 100)) : 0
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>{label}</span><b>{value}</b></div>
      <div style={{ height: 10, borderRadius: 999, background: '#eee9ff', marginTop: 6 }}>
        <div style={{ width: pct + '%', height: '100%', borderRadius: 999, background: '#6b4df0' }} />
      </div>
    </div>
  )
}

export default function Officials() {
  const [key, setKey] = useState('')
  const [map, setMap] = useState(null)
  const [flags, setFlags] = useState(null)
  const [alerts, setAlerts] = useState(null)
  const [tab, setTab] = useState('overview')
  const [note, setNote] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    document.body.classList.add('shell-bg')
    return () => document.body.classList.remove('shell-bg')
  }, [])

  async function load() {
    setErr(''); setNote('')
    try {
      setMap(await call('/dashboard/map', key))
    } catch (e) {
      setMap(null)
      setErr(e.message === '401' || e.message === '403' ? 'This key is not allowed.' : 'Could not reach the server.')
      return
    }
    try { setAlerts(await call('/dashboard/alerts', key)) } catch { setAlerts(null) }
    try { setFlags(await call('/dashboard/flags', key)) }
    catch { setFlags(null); setNote('This key can see the counts but not the hospital flags.') }
  }

  async function review(id, status) {
    try { await call(`/dashboard/flags/${id}/review`, key, 'POST', { status, note: '' }); load() }
    catch { setErr('Could not save the review.') }
  }

  function close() { setMap(null); setFlags(null); setAlerts(null); setKey(''); setTab('overview') }

  const districts = map?.districts ?? []
  const total = (f) => districts.reduce((s, d) => s + (d[f] || 0), 0)
  const home = () => window.location.assign('/landing.html')

  return (
    <div className="sh-frame">
      <aside className="sh-side">
        <div className="sh-brand" onClick={home} style={{ cursor: 'pointer' }}>
          <div className="sh-logo">?</div>
          <div className="sh-word">Zaroori<span>?</span></div>
        </div>
        <nav className="sh-nav">
          {TABS.map((t) => (
            <div key={t.key} onClick={() => map && setTab(t.key)}
              className={'sh-nav-item' + (tab === t.key ? ' on' : '')}
              style={{ cursor: map ? 'pointer' : 'default', opacity: map ? 1 : 0.5 }}>
              <Icon d={t.d} />{t.label}
              <span className="sh-nav-end">{tab === t.key && <span className="sh-dot" />}</span>
            </div>
          ))}
        </nav>
        <div className="sh-profile">
          <div className="sh-avatar">O</div>
          <div className="sh-profile-text">
            <div className="sh-profile-name">{map ? 'Health official' : 'Not signed in'}</div>
            <div className="sh-profile-sub">{map ? 'Signed in' : 'Enter your key to open'}</div>
          </div>
          {map && <button className="sh-logout" onClick={close} title="Close"><Icon d="M15 17l5-5-5-5M20 12H9M9 4H5v16h4" /></button>}
        </div>
      </aside>

      <main className="sh-main">
        <div className="sh-top">
          <div className="sh-top-row">
            <div>
              <div className="sh-hello">For health officials</div>
              <h1 className="sh-title">{!map ? 'Open the dashboard' : TABS.find((t) => t.key === tab).label}</h1>
            </div>
          </div>
        </div>

        {!map && (
          <div className="sh-grid">
            <div>
              <div className="sh-card">
                <p>Enter your officials key. It is kept only on this screen and is never saved.</p>
                <input type="password" value={key} onChange={(e) => setKey(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && load()} placeholder="Officials key"
                  style={{ width: '100%', padding: 14, borderRadius: 14, border: '1px solid #d8d2f5', marginBottom: 12, boxSizing: 'border-box' }} />
                <button className="sh-btn" onClick={load}>Open dashboard</button>
                {err && <p style={{ color: '#c0392b' }}>{err}</p>}
              </div>
            </div>
            <aside className="sh-guide">
              <div className="sh-guide-label">Privacy</div>
              <p>No names, phone numbers or Aadhaar. A flag means “please check”. It is not an accusation.</p>
            </aside>
          </div>
        )}

        {map && tab === 'overview' && (
          <>
            <div className="sh-tiles">
              <div className="sh-tile pink"><div><div className="sh-tile-label">Cases</div><div className="sh-tile-value">{total('cases')}</div></div></div>
              <div className="sh-tile lilac"><div><div className="sh-tile-label">Districts</div><div className="sh-tile-value">{districts.length}</div></div></div>
              <div className="sh-tile blue"><div><div className="sh-tile-label">Hospital flags</div><div className="sh-tile-value">{flags ? flags.flagged.length : '–'}</div></div></div>
            </div>
            <div className="sh-grid">
              <div>
                <div className="sh-card">
                  <Bar label="Surgery advised" value={total('advised_surgery')} max={total('cases')} />
                  <Bar label="Coercion signals" value={total('coercion')} max={total('cases')} />
                  <Bar label="Alerts sent" value={total('alerts')} max={total('cases')} />
                </div>
              </div>
              <aside className="sh-guide">
                <div className="sh-guide-label">How to read this</div>
                <p>Totals across completed cases only. Open Districts for the split, or Hospital flags for places to check.</p>
              </aside>
            </div>
          </>
        )}

        {map && tab === 'districts' && (
          <div className="sh-card">
            {districts.length === 0 && <p>No completed cases yet.</p>}
            {districts.map((d) => (
              <div key={d.district} style={{ padding: '12px 0', borderTop: '1px solid #eee9ff' }}>
                <b>{d.district}</b>
                <div style={{ color: '#6b6690' }}>
                  Cases {d.cases} · Surgery advised {d.advised_surgery} · Coercion {d.coercion} · Alerts {d.alerts}
                </div>
              </div>
            ))}
          </div>
        )}

        {map && tab === 'flags' && (
          <div className="sh-card">
            {note && <p>{note}</p>}
            {flags && flags.flagged.length === 0 && (
              <p>No hospital is flagged. A flag needs at least {flags.threshold} cases from {flags.min_ashas} different ASHAs within {flags.window_days} days.</p>
            )}
            {flags?.flagged.map((f) => (
              <div key={f.hospital_id} style={{ padding: '12px 0', borderTop: '1px solid #eee9ff' }}>
                <b>{f.hospital}</b>, {f.district}
                <div style={{ color: '#6b6690' }}>{f.cases} cases · {f.ashas} ASHAs · status: {f.review.status}</div>
                <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                  {['reviewing', 'dismissed', 'escalated'].map((s) => (
                    <button key={s} className="sh-btn ghost" onClick={() => review(f.hospital_id, s)}>{s}</button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
        {map && tab === 'alerts' && (
          <div className="sh-card">
            {!alerts && <p>This key cannot see alerts.</p>}
            {alerts && alerts.alerts.length === 0 && <p>No alerts yet.</p>}
            {alerts && alerts.alerts.length > 0 && (
              <p>{alerts.alerts.length} alerts · {alerts.failed} failed · {alerts.mock_deliveries} test deliveries (not really sent)</p>
            )}
            {alerts?.alerts.map((a) => (
              <div key={a.id} style={{ padding: '12px 0', borderTop: '1px solid #eee9ff' }}>
                <b>{a.district}</b> · {a.status}
                <div style={{ color: '#6b6690' }}>via {a.channel} · {a.attempts} tries · {a.created_at ? new Date(a.created_at).toLocaleString() : ''}</div>
              </div>
            ))}
          </div>
        )}
        {map && err && <p style={{ color: '#c0392b' }}>{err}</p>}
      </main>
    </div>
  )
}
