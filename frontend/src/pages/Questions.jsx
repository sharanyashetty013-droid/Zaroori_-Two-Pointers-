import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { useT } from '../i18n'
import { QUESTIONS, UI } from '../data/questions'
import { speak } from '../speak'
import Shell from '../components/Shell'

export default function Questions() {
  const { lang } = useLanguage()
  const t = useT()
  const navigate = useNavigate()
  const { state } = useLocation()
  const hospitalId = state?.hospitalId ?? null
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState({})

  const q = QUESTIONS[index]
  const spoken = q.text[lang] + '. ' + q.options.map((o) => o.label[lang]).join('. ') + '.'

  useEffect(() => {
    speak(q.text[lang] + '. ' + q.options.map((o) => o.label[lang]).join('. ') + '.', lang)
    return () => window.speechSynthesis?.cancel()
  }, [q, lang])

  function choose(value) {
    const next = { ...answers, [q.id]: value }
    setAnswers(next)
    if (index < QUESTIONS.length - 1) {
      setIndex(index + 1)
    } else {
      navigate(next.pressure === 'yes' ? '/alert' : '/result', {
        state: { answers: next, hospitalId },
      })
    }
  }

  function goBack() {
    if (index > 0) setIndex(index - 1)
    else navigate('/hospital')
  }

  return (
    <Shell title={q.text[lang]} step="questions" guide={t('guideQ_' + q.id)}>
      <div className="sh-card">
        <div className="sh-mob-meta">
          {t('question')} {index + 1} / {QUESTIONS.length}
        </div>
        <div className="sh-mob-bar" aria-hidden="true">
          {QUESTIONS.map((x, i) => (
            <div key={x.id} className={'sh-seg' + (i < index ? ' done' : '') + (i === index ? ' on' : '')} />
          ))}
        </div>
        <button className="sh-listen" onClick={() => speak(spoken, lang)}>
          <svg className="sh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M11 5L6 9H3v6h3l5 4zM15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13" />
          </svg>
          {UI.listen[lang]}
        </button>
      </div>

      <div className="sh-rows">
        {q.options.map((o) => (
          <button
            key={o.value}
            className={'sh-row' + (answers[q.id] === o.value ? ' sel' : '')}
            onClick={() => choose(o.value)}
          >
            <span>{o.label[lang]}</span>
          </button>
        ))}
      </div>

      <button className="sh-btn ghost" onClick={goBack}>
        &#8592; {UI.back[lang]}
      </button>
    </Shell>
  )
}