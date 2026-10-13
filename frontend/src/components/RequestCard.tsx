import { Link } from 'react-router-dom'

import type { FeatureRequest } from '../types/featureRequest'

type RequestCardProps = {
  request: FeatureRequest
  onSupport: (id: string) => void
  supportingId: string | null
}

function excerpt(text: string, max = 140): string {
  if (text.length <= max) return text
  return `${text.slice(0, max).trim()}…`
}

export function RequestCard({ request, onSupport, supportingId }: RequestCardProps) {
  const supported = request.supported_by_current_user === true
  const isSupporting = supportingId === request.id

  return (
    <article className="request-card">
      <div className="request-card-header">
        <h2>{request.title}</h2>
        <span className="status-badge">{request.status}</span>
      </div>
      <p className="request-description">{excerpt(request.description)}</p>
      <div className="request-meta">
        <span>{request.support_count} supporters</span>
        <span>{new Date(request.created_at).toLocaleDateString()}</span>
      </div>
      <div className="request-actions">
        <Link to={`/requests/${request.id}`}>View detail</Link>
        <button
          type="button"
          disabled={supported || isSupporting}
          onClick={() => onSupport(request.id)}
        >
          {supported ? 'Supported' : isSupporting ? 'Supporting…' : 'Support'}
        </button>
      </div>
    </article>
  )
}
