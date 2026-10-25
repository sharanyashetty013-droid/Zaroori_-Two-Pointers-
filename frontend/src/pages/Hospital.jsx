import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { useLanguage } from '../LanguageContext'
import { getHospitals } from '../api'

const t = (en, hi, kn) => ({ en, hi, kn })
const TEXT = {
  title: t('Which hospital advised surgery?', 'किस अस्पताल ने ऑपरेशन की सलाह दी?', 'ಯಾವ ಆಸ್ಪತ್ರೆ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆಯ ಸಲಹೆ ನೀಡಿತು?'),
  note: t('This is optional. It is not a report against anyone.', 'यह वैकल्पिक है। यह किसी के ख़िलाफ़ शिकायत नहीं है।', 'ಇದು ಐಚ್ಛಿಕ. ಇದು ಯಾರ ವಿರುದ್ಧವೂ ದೂರು ಅಲ್ಲ.'),
  skip: t('Not sure / skip', 'पता नहीं / छोड़ें', 'ಗೊತ್ತಿಲ್ಲ / ಬಿಟ್ಟುಬಿಡಿ'),
  loading: t('Loading…', 'लोड हो रहा है…', 'ಲೋಡ್ ಆಗುತ್ತಿದೆ…'),
  noConn: t('No connection', 'कनेक्शन नहीं है', 'ಸಂಪರ್ಕ ಇಲ್ಲ'),
  retry: t('Try again', 'फिर कोशिश करें', 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ'),
}

export default function Hospital() {
  const { asha, logout } = useAuth()
  const { lang } = useLanguage()
  const navigate = useNavigate()
  const [hospitals, setHospitals] = useState([])
  const [status, setStatus] = useState('loading')

  async function load() {
    setStatus('loading')
    try {
      const data = await getHospitals(asha.district)
      console.log('HOSPITALS RESPONSE (remove later):', data)
      setHospitals(Array.isArray(data) ? data : data.hospitals ?? [])
      setStatus('ok')
    } catch (e) {
      if (e.status === 401) {
        logout()
        navigate('/')
        return
      }
      setStatus('error')
    }
  }

  useEffect(() => {
    load()
  }, [])

  function choose(id) {
    navigate('/questions', { state: { hospitalId: id } })
  }

  return (
    <div>
      <div className="card">
        <h1>{TEXT.title[lang]}</h1>
        <p>{TEXT.note[lang]}</p>
      </div>

      {status === 'loading' && <p>{TEXT.loading[lang]}</p>}

      {status === 'error' && (
        <div className="card">
          <p className="error-msg">{TEXT.noConn[lang]}</p>
          <button className="btn-big" onClick={load}>{TEXT.retry[lang]}</button>
        </div>
      )}

      {status === 'ok' &&
        hospitals.map((h) => (
          <button key={h.id} className="btn-big" onClick={() => choose(h.id)}>
            {h.name}
          </button>
        ))}

      <button className="btn-big btn-outline" onClick={() => choose(null)}>
        {TEXT.skip[lang]}
      </button>
    </div>
  )
}