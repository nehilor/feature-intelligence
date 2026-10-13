import { Link } from 'react-router-dom'

import type { RelationshipsResponse, RequestRelationshipType } from '../types/featureRelationships'

type Props = {
  data: RelationshipsResponse | null
  loading: boolean
  running: boolean
  error: string | null
  hasAnalyzed: boolean
  onAnalyze: () => void
}

function relationshipLabel(relationship: RequestRelationshipType): string {
  if (relationship === 'DUPLICATE') return 'Potential duplicate'
  if (relationship === 'RELATED') return 'Related request'
  return 'Distinct'
}

export function RelatedRequestsPanel({
  data,
  loading,
  running,
  error,
  hasAnalyzed,
  onAnalyze,
}: Props) {
  if (loading) {
    return (
      <section className="related-panel" aria-labelledby="related-heading">
        <h2 id="related-heading">Related requests</h2>
        <p>Loading related requests…</p>
      </section>
    )
  }

  const visibleItems =
    data?.items.filter((item) => item.relationship === 'DUPLICATE' || item.relationship === 'RELATED') ??
    []

  if (!hasAnalyzed && (!data || (visibleItems.length === 0 && !data.message))) {
    return (
      <section className="related-panel" aria-labelledby="related-heading">
        <h2 id="related-heading">Related requests</h2>
        <p className="analysis-advisory">
          Similarity suggestions are evidence only. Requests are never merged automatically.
        </p>
        <p>Not analyzed yet.</p>
        <button type="button" onClick={onAnalyze} disabled={running}>
          {running ? 'Checking related requests…' : 'Check related requests'}
        </button>
        {error ? <p className="form-error">{error}</p> : null}
      </section>
    )
  }

  if (running) {
    return (
      <section className="related-panel" aria-labelledby="related-heading">
        <h2 id="related-heading">Related requests</h2>
        <p role="status">Checking related requests…</p>
      </section>
    )
  }

  if (!data) {
    return null
  }

  if (data.status === 'embedding_unavailable' || data.status === 'classification_unavailable') {
    return (
      <section className="related-panel" aria-labelledby="related-heading">
        <h2 id="related-heading">Related requests</h2>
        <p role="status">{data.message ?? 'Relationship analysis is unavailable.'}</p>
        <button type="button" onClick={onAnalyze} disabled={running}>
          Retry
        </button>
        {error ? <p className="form-error">{error}</p> : null}
      </section>
    )
  }

  if (visibleItems.length === 0) {
    return (
      <section className="related-panel" aria-labelledby="related-heading">
        <h2 id="related-heading">Related requests</h2>
        <p>{data.message ?? 'No meaningful related requests found.'}</p>
        <button type="button" onClick={onAnalyze} disabled={running}>
          Check again
        </button>
      </section>
    )
  }

  return (
    <section className="related-panel" aria-labelledby="related-heading">
      <h2 id="related-heading">Related requests</h2>
      <p className="analysis-advisory">
        Similarity suggestions are evidence only. Requests are never merged automatically.
      </p>
      {data.status === 'partial' ? (
        <p className="analysis-warning" role="status">
          Some candidates could not be classified. Results may be incomplete.
        </p>
      ) : null}
      <ul className="related-list">
        {visibleItems.map((item) => (
          <li key={item.feature_request_id} className="related-card">
            <p className="related-label">{relationshipLabel(item.relationship)}</p>
            <h3>
              <Link to={`/requests/${item.feature_request_id}`}>{item.title}</Link>
            </h3>
            <p>{item.reason}</p>
            <p>
              Confidence: {item.confidence.replaceAll('_', ' ')} · {item.support_count} supporters
            </p>
            {item.confidence === 'LOW' ? (
              <p className="analysis-warning">Low confidence — review before any consolidation.</p>
            ) : null}
          </li>
        ))}
      </ul>
      {error ? <p className="form-error">{error}</p> : null}
    </section>
  )
}
