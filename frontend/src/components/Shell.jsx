import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { useLanguage } from '../LanguageContext'
import { useT } from '../i18n'
import '../shell.css'

const STEPS = [
  { key: 'language', label: 'stepLanguage', d: 'M3 5h12M9 3v2m1.5 0c-.5 3-2.5 6-6 8m2-4c1 1.5 3 3 5.5 4M13 21l4-10 4 10m-6.5-3h5' },
  { key: 'hospital', label: 'stepHospital', d: 'M4 21V8l8-5 8 5v13M9 21v-6h6v6M12 8v4M10 10h4' },
  { key: 'questions', label: 'stepQuestions', d: 'M9 9a3 3 0 1 1 4 2.8c-.7.4-1 1-1 1.7M12 17h.01M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z' },
  { key: 'result', label: 'stepResult', d: 'M7 3h7l4 4v14H7zM14 3v4h4M9 13h6M9 17h6' },
  { key: 'help', label: 'stepHelp', d: 'M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 11c0 5.5-7 10-7 10z' },
]

const LANG_BUTTONS = [
  { code: 'en', label: 'EN' },
  { code: 'hi', label: 'हि' },
  { code: 'kn', label: 'ಕ' },
]

function Icon({ d }) {
  return (
    <svg className="sh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={d} />
    </svg>
  )
}

function Ring({ value, total }) {
  const c = 2 * Math.PI * 15
  return (
    <svg className="sh-ring" viewBox="0 0 36 36" aria-hidden="true">
      <circle className="track" cx="18" cy="18" r="15" />
      <circle className="bar" cx="18" cy="18" r="15" strokeDasharray={`${(value / total) * c} ${c}`} />
    </svg>
  )
}

export default function Shell({ title, step, tiles = false, exit = true, guide, children }) {
  const { asha, logout } = useAuth()
  const { lang, setLang } = useLanguage()
  const t = useT()
  const navigate = useNavigate()

  useEffect(() => {
    document.body.classList.add('shell-bg')
    return () => document.body.classList.remove('shell-bg')
  }, [])

  const current = STEPS.findIndex((s) => s.key === step)

  function doLogout() {
    logout()
    navigate('/')
  }

  function quickExit() {
    window.location.replace('/neutral')
  }

  return (
    <div className="sh-frame">
      <aside className="sh-side">
        <div className="sh-brand">
          <div className="sh-logo">?</div>
          <div className="sh-word">Zaroori<span>?</span></div>
        </div>

        <nav className="sh-nav">
          {STEPS.map((s, i) => (
            <div
              key={s.key}
              className={'sh-nav-item' + (i === current ? ' on' : '') + (i < current ? ' done' : '')}
            >
              <Icon d={s.d} />
              {t(s.label)}
              <span className="sh-nav-end">
                {i < current && (
                  <span className="sh-tick"><Icon d="M5 12l5 5 9-10" /></span>
                )}
                {i === current && <span className="sh-dot" />}
              </span>
            </div>
          ))}
        </nav>

        <div className="sh-profile">
          <div className="sh-avatar">{(asha?.code || 'A').charAt(0)}</div>
          <div className="sh-profile-text">
            <div className="sh-profile-name">{asha?.code}</div>
            <div className="sh-profile-sub">{asha?.district}</div>
          </div>
          <button className="sh-logout" onClick={doLogout} aria-label={t('logout')} title={t('logout')}>
            <Icon d="M15 17l5-5-5-5M20 12H9M9 4H5v16h4" />
          </button>
        </div>
      </aside>

      <main className="sh-main">
        <div className="sh-top">
          <div className="sh-top-row">
            <div className="sh-brand sh-brand-m">
              <div className="sh-logo">?</div>
              <div className="sh-word">Zaroori<span>?</span></div>
            </div>
          </div>
          <div className="sh-top-row">
            <div>
              <div className="sh-hello">{t('asha')} {asha?.code}</div>
              <h1 className="sh-title">{title}</h1>
            </div>
            <div className="sh-tools">
              <div className="sh-langs">
                {LANG_BUTTONS.map((l) => (
                  <button
                    key={l.code}
                    className={lang === l.code ? 'on' : ''}
                    onClick={() => setLang(l.code)}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
              {exit && (
                <button className="sh-exit" onClick={quickExit} aria-label={t('exit')}>
                  <Icon d="M18 6L6 18M6 6l12 12" />
                  {t('exit')}
                </button>
              )}
            </div>
          </div>
        </div>

        {current >= 0 && (
          <div className="sh-mob">
            <div className="sh-mob-meta">{current + 1} / {STEPS.length} · {t(STEPS[current].label)}</div>
            <div className="sh-mob-bar" aria-hidden="true">
              {STEPS.map((s, i) => (
                <div key={s.key} className={'sh-seg' + (i < current ? ' done' : '') + (i === current ? ' on' : '')} />
              ))}
            </div>
          </div>
        )}

        {tiles && (
          <div className="sh-tiles">
            <div className="sh-tile pink">
              <div className="sh-tile-icon"><Icon d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0" /></div>
              <div>
                <div className="sh-tile-label">{t('ashaCode')}</div>
                <div className="sh-tile-value">{asha?.code}</div>
              </div>
            </div>
            <div className="sh-tile lilac">
              <div className="sh-tile-icon"><Icon d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11zM12 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" /></div>
              <div>
                <div className="sh-tile-label">{t('district')}</div>
                <div className="sh-tile-value">{asha?.district}</div>
              </div>
            </div>
            {current >= 0 && (
              <div className="sh-tile blue">
                <div className="sh-tile-icon"><Ring value={current + 1} total={STEPS.length} /></div>
                <div>
                  <div className="sh-tile-label">{t(STEPS[current].label)}</div>
                  <div className="sh-tile-value">{current + 1} / {STEPS.length}</div>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="sh-grid">
          <div>{children}</div>
          {guide && (
            <aside className="sh-guide">
              <div className="sh-guide-label">{t('forAsha')}</div>
              <p>{guide}</p>
            </aside>
          )}
        </div>

        <button className="sh-btn ghost sh-logout-m" onClick={doLogout}>{t('logout')}</button>
      </main>
    </div>
  )
}