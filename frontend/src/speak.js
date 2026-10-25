import { BASE } from './api'

const VOICE_LANG = { en: 'en-IN', hi: 'hi-IN', kn: 'kn-IN' }
let current = null

export function stopSpeaking() {
  if (current) { current.pause(); current = null }
  if ('speechSynthesis' in window) window.speechSynthesis.cancel()
}

function browserSpeak(text, lang) {
  if (!('speechSynthesis' in window)) return
  const u = new SpeechSynthesisUtterance(text)
  u.lang = VOICE_LANG[lang]
  u.rate = 0.9
  window.speechSynthesis.speak(u)
}

export async function speak(text, lang, path) {
  stopSpeaking()
  try {
    const url0 = BASE + (path || `/tts?text=${encodeURIComponent(text)}&lang=${lang}`)
    const res = await fetch(url0)
    if (!res.ok) throw new Error('tts ' + res.status)
    const url = URL.createObjectURL(await res.blob())
    current = new Audio(url)
    await current.play()
  } catch (e) {
    console.warn('Backend TTS failed, using browser voice:', e)
    browserSpeak(text, lang)
  }
}
