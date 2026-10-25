export default function QuickExit() {
  function exit() {
    // Full page load: wipes everything held in memory.
    window.location.replace('/neutral')
  }
  return (
    <button className="quick-exit" onClick={exit} aria-label="Quick exit">
      ✕ Exit
    </button>
  )
}