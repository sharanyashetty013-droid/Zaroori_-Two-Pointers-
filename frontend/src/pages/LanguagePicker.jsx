import { useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { useAuth } from '../AuthContext'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'kn', label: 'ಕನ್ನಡ' },
]

export default function LanguagePicker() {
  const { setLang } = useLanguage()
  const { asha, logout } = useAuth()
  const navigate = useNavigate()

  function choose(code) {
    setLang(code)
    navigate('/hospital')
  }

  return (
    <div>
      <div className="tiles">
        <div className="tile tile-pink">
          <span className="tile-label">ASHA code</span>
          <span className="tile-value">{asha.code}</span>
        </div>
        <div className="tile tile-blue">
          <span className="tile-label">District</span>
          <span className="tile-value">{asha.district}</span>
        </div>
      </div>

      <div className="card">
        <h1>Choose a language</h1>
        <p>भाषा चुनें · ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ</p>
        {LANGUAGES.map((l) => (
          <button key={l.code} className="btn-big" onClick={() => choose(l.code)}>
            {l.label}
          </button>
        ))}
      </div>

      <button
        className="link-back"
        onClick={() => {
          logout()
          navigate('/')
        }}
      >
        Log out
      </button>
    </div>
  )
}