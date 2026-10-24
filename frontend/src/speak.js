const VOICE_LANG = { en: 'en-IN', hi: 'hi-IN', kn: 'kn-IN' }

export function speak(text, lang) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = VOICE_LANG[lang]
  u.rate = 0.9
  window.speechSynthesis.speak(u)
}