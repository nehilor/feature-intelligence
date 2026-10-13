import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useApiHealth } from '../hooks/useApiHealth'

type LayoutProps = {
  children: ReactNode
}

function apiStatusLabel(status: 'checking' | 'connected' | 'unavailable'): string {
  if (status === 'checking') return 'Checking'
  if (status === 'connected') return 'Connected'
  return 'Unavailable'
}

export function Layout({ children }: LayoutProps) {
  const { status } = useApiHealth()

  return (
    <div className="layout">
      <header className="header">
        <div>
          <Link to="/" className="brand">
            Feature Intelligence
          </Link>
          <p className="subtitle">Discover and support product requests</p>
        </div>
        <p className="api-pill" aria-live="polite">
          API: {apiStatusLabel(status)}
        </p>
      </header>
      <main className="content">{children}</main>
    </div>
  )
}
