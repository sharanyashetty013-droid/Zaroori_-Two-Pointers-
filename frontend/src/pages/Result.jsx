import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { RESULT, HOSPITALS } from '../data/result'
import { speak } from '../speak'

export default function Result() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const { lang } = useLanguage()
  const [hospital, setHospital] = useState('')
  const answers = state?.answers

  const spoken = [
    RESULT.headline[lang],
    RESULT.body[lang],
    RESULT.askTitle[lang],
    ...RESULT.ask.map((a) => a[lang]),
    RESULT.visitTitle[lang],
    RESULT.visitName[lang],
  ].join('. ')

  useEffect(() => {
    if (!answers) {
      navigate('/')
      return
    }
    speak(spoken, lang)
    return () => window.speechSynthesis.cancel()
  }, [])

  if (!answers) return null

  return (
    <div>
      <div className="card">
        <h1>{RESULT.headline[lang]}</h1>
        <p>{RESULT.body[lang]}</p>
        <button className="btn-big btn-violet" onClick={() => speak(spoken, lang)}>
          🔊 {RESULT.listen[lang]}
        </button>
      </div>

      <div className="card">
        <h2>{RESULT.askTitle[lang]}</h2>
        <ol className="ask-list">
          {RESULT.ask.map((a, i) => (
            <li key={i}>{a[lang]}</li>
          ))}
        </ol>
      </div>

      <div className="card">
        <h2>🏥 {RESULT.visitTitle[lang]}</h2>
        <p>{RESULT.visitName[lang]}</p>
      </div>

      {answers.doctorSaid === 'surgery' && (
        <div className="card">
          <h2>{RESULT.hospitalLabel[lang]}</h2>
          <select
            className="select"
            value={hospital}
            onChange={(e) => setHospital(e.target.value)}
          >
            <option value="">{RESULT.hospitalPick[lang]}</option>
            {HOSPITALS.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name}
              </option>
            ))}
          </select>
        </div>
      )}

      <button className="btn-big" onClick={() => navigate('/')}>
        {RESULT.startOver[lang]}
      </button>
    </div>
  )
}
