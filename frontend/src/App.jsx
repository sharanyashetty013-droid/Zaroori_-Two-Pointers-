import { Routes, Route } from 'react-router-dom'
import LanguagePicker from './pages/LanguagePicker'
import Questions from './pages/Questions'
import Result from './pages/Result'
import Alert from './pages/Alert'
import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<LanguagePicker />} />
        <Route path="/questions" element={<Questions />} />
        <Route path="/result" element={<Result />} />
        <Route path="/alert" element={<Alert />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </div>
  )
}