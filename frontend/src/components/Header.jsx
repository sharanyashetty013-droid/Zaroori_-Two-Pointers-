import { useAuth } from '../AuthContext'

export default function Header() {
  const { asha } = useAuth()
  if (!asha) return null
  return (
    <div className="topbar">
      <div className="logo-chip">?</div>
      <div>
        <div className="topbar-title">Zaroori?</div>
        <div className="topbar-sub">ASHA {asha.code} · {asha.district}</div>
      </div>
    </div>
  )
}