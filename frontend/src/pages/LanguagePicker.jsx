import { useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'kn', label: 'ಕನ್ನಡ' },
]

export default function LanguagePicker() {
  const { setLang } = useLanguage()
  const navigate = useNavigate()

  function choose(code) {
    setLang(code)
    navigate('/questions')
  }

  return (
    <div>
      <h1>Zaroori?</h1>
      <p>क्या यह ज़रूरी है? · ಇದು ಅಗತ್ಯವೇ?</p>
      <div className="card">
        <p>Choose a language · भाषा चुनें · ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ</p>
        {LANGUAGES.map((l) => (
          <button key={l.code} className="btn-big" onClick={() => choose(l.code)}>
            {l.label}
          </button>
        ))}
      </div>
    </div>
  )
}