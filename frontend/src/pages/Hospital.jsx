import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { useT } from '../i18n'
import { getHospitals } from '../api'
import Shell from '../components/Shell'

export default function Hospital() {
  const { asha, logout } = useAuth()
  const t = useT()
  const navigate = useNavigate()
  const [hospitals, setHospitals] = useState([])
  const [status, setStatus] = useState('loading')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false
    getHospitals(asha.district)
      .then((data) => {
        if (cancelled) return
        setHospitals(Array.isArray(data) ? data : data.hospitals ?? [])
        setStatus('ok')
      })
      .catch((e) => {
        if (cancelled) return
        if (e.status === 401) {
          logout()
          navigate('/')
          return
        }
        setStatus('error')
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt])

  function retry() {
    setStatus('loading')
    setAttempt((n) => n + 1)
  }

  function choose(id) {
    navigate('/questions', { state: { hospitalId: id } })
  }

  return (
    <Shell title={t('hospitalTitle')} step="hospital" guide={t('guideHospital')}>
      <div className="sh-card">
        <h2>{t('hospitalTitle')}</h2>
        <p>{t('hospitalNote')}</p>
      </div>

      {status === 'loading' && <p className="sh-note">{t('loading')}</p>}

      {status === 'error' && (
        <div className="sh-card">
          <p className="sh-error">{t('noConn')}</p>
          <button className="sh-btn" onClick={retry}>{t('retry')}</button>
        </div>
      )}

      {status === 'ok' && (
        <div className="sh-rows">
          {hospitals.map((h) => (
            <button key={h.id} className="sh-row" onClick={() => choose(h.id)}>
              <span>{h.name}</span>
              <span aria-hidden="true">&#8250;</span>
            </button>
          ))}
        </div>
      )}

      <button className="sh-btn ghost" onClick={() => choose(null)}>
        {t('skip')}
      </button>
    </Shell>
  )
}