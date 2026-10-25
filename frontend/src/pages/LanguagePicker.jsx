import { useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { useT } from '../i18n'
import Shell from '../components/Shell'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'kn', label: 'ಕನ್ನಡ' },
]

export default function LanguagePicker() {
  const { setLang } = useLanguage()
  const t = useT()
  const navigate = useNavigate()

  function choose(code) {
    setLang(code)
    navigate('/hospital')
  }

  return (
    <Shell title={t('chooseLanguage')} step="language" tiles exit={false} guide={t('guideStart')}>
      <div className="sh-card">
        <h2>{t('chooseLanguage')}</h2>
        <p>{t('chooseLanguageSub')}</p>
        <div className="sh-lang">
          {LANGUAGES.map((l) => (
            <button key={l.code} className="sh-btn" onClick={() => choose(l.code)}>
              {l.label}
            </button>
          ))}
        </div>
      </div>
    </Shell>
  )
}