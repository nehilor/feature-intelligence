import { useApiHealth } from './hooks/useApiHealth'
import './App.css'

function statusLabel(status: 'checking' | 'connected' | 'unavailable'): string {
  switch (status) {
    case 'checking':
      return 'Checking'
    case 'connected':
      return 'Connected'
    case 'unavailable':
      return 'Unavailable'
  }
}

export default function App() {
  const { status, retry } = useApiHealth()

  return (
    <main className="shell">
      <h1>Feature Intelligence</h1>
      <p className="tagline">Application foundation is running.</p>
      <section className="status-card" aria-live="polite">
        <h2>API status</h2>
        <p className={`status-value status-${status}`}>{statusLabel(status)}</p>
        {status === 'unavailable' ? (
          <button type="button" className="retry" onClick={retry}>
            Retry connection
          </button>
        ) : null}
      </section>
    </main>
  )
}
