import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { QUESTIONS, UI } from '../data/questions'

const VOICE_LANG = { en: 'en-IN', hi: 'hi-IN', kn: 'kn-IN' }

function speak(text, lang) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = VOICE_LANG[lang]
  u.rate = 0.9
  window.speechSynthesis.speak(u)
}

export default function Questions() {
  const { lang } = useLanguage()
  const navigate = useNavigate()
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState({})

  const q = QUESTIONS[index]
  const spoken = q.text[lang] + '. ' + q.options.map((o) => o.label[lang]).join('. ') + '.'

  useEffect(() => {
    speak(spoken, lang)
    return () => window.speechSynthesis.cancel()
  }, [index, lang])

  function choose(value) {
    const next = { ...answers, [q.id]: value }
    setAnswers(next)
    if (index < QUESTIONS.length - 1) {
      setIndex(index + 1)
    } else {
      navigate(next.pressure === 'yes' ? '/alert' : '/result', { state: { answers: next } })
    }
  }

  return (
    <div>
      <div className="progress">
        {QUESTIONS.map((_, i) => (
          <span key={i} className={i <= index ? 'dot on' : 'dot'} />
        ))}
      </div>

      <div className="card">
        <h1>{q.text[lang]}</h1>
        <button className="btn-big btn-violet" onClick={() => speak(spoken, lang)}>
          🔊 {UI.listen[lang]}
        </button>
      </div>

      {q.options.map((o) => (
        <button key={o.value} className="btn-big" onClick={() => choose(o.value)}>
          {o.label[lang]}
        </button>
      ))}

      {index > 0 && (
        <button className="link-back" onClick={() => setIndex(index - 1)}>
          ← {UI.back[lang]}
        </button>
      )}
    </div>
  )
}
