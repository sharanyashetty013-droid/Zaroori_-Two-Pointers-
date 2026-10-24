import { useLocation } from 'react-router-dom'

export default function Result() {
  const { state } = useLocation()
  return (
    <div>
      <h1>Result</h1>
      <pre style={{ color: '#c9b8ff' }}>{JSON.stringify(state?.answers, null, 2)}</pre>
    </div>
  )
}