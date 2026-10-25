import { createContext, useContext, useState } from 'react'
import { setKey } from './api'

const AuthContext = createContext()
const STORE = 'zaroori_asha'

function load() {
  try {
    return JSON.parse(localStorage.getItem(STORE))
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [asha, setAsha] = useState(() => {
    const saved = load()
    if (saved) setKey(saved.key)
    return saved
  })

  function login(profile) {
    localStorage.setItem(STORE, JSON.stringify(profile))
    setKey(profile.key)
    setAsha(profile)
  }

  function logout() {
    localStorage.removeItem(STORE)
    setKey(null)
    setAsha(null)
  }

  return (
    <AuthContext.Provider value={{ asha, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}