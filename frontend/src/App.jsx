import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'
import Login from './pages/Login'
import LanguagePicker from './pages/LanguagePicker'
import Hospital from './pages/Hospital'
import Questions from './pages/Questions'
import Result from './pages/Result'
import Alert from './pages/Alert'
import Neutral from './pages/Neutral'
import Officials from './pages/Officials'
import QuickExit from './components/QuickExit'
import Header from './components/Header'

function RequireAuth({ children }) {
  const { asha } = useAuth()
  return asha ? children : <Navigate to="/" replace />
}

const NO_QUICK_EXIT = ['/', '/language','/hospital','/questions','/result', '/alert','/neutral','/officials']
const NO_HEADER = ['/','/language','/hospital','/questions','/result', '/alert', '/neutral','/officials']

export default function App() {
  const { pathname } = useLocation()
  return (
    <div className="app">
      {!NO_HEADER.includes(pathname) && <Header />}
      {!NO_QUICK_EXIT.includes(pathname) && <QuickExit />}
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/language" element={<RequireAuth><LanguagePicker /></RequireAuth>} />
        <Route path="/hospital" element={<RequireAuth><Hospital /></RequireAuth>} />
        <Route path="/questions" element={<RequireAuth><Questions /></RequireAuth>} />
        <Route path="/result" element={<RequireAuth><Result /></RequireAuth>} />
        <Route path="/alert" element={<RequireAuth><Alert /></RequireAuth>} />
        <Route path="/neutral" element={<Neutral />} />
        <Route path="/officials" element={<Officials />} />
      </Routes>
    </div>
  )
}