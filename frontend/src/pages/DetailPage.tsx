import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { getFeatureRequest, supportFeatureRequest } from '../api/featureRequests'
import { getSupporterKey } from '../lib/supporterKey'
import type { FeatureRequest } from '../types/featureRequest'

export function DetailPage() {
  const { requestId } = useParams()
  const [request, setRequest] = useState<FeatureRequest | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [supporting, setSupporting] = useState(false)

  const reload = async () => {
    if (!requestId) return
    setLoading(true)
    setError(null)
    try {
      const data = await getFeatureRequest(requestId, getSupporterKey())
      setRequest(data)
    } catch {
      setError('Unable to load this request.')
      setRequest(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!requestId) return
    let cancelled = false
    async function loadDetail() {
      if (!requestId) return
      setLoading(true)
      setError(null)
      try {
        const data = await getFeatureRequest(requestId, getSupporterKey())
        if (!cancelled) setRequest(data)
      } catch {
        if (!cancelled) {
          setError('Unable to load this request.')
          setRequest(null)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void loadDetail()
    return () => {
      cancelled = true
    }
  }, [requestId])

  const onSupport = async () => {
    if (!requestId) return
    setSupporting(true)
    try {
      await supportFeatureRequest(requestId, getSupporterKey())
      await reload()
    } catch {
      setError('Unable to record support.')
    } finally {
      setSupporting(false)
    }
  }

  if (loading) return <p>Loading request…</p>
  if (error && !request) {
    return (
      <div className="error-banner" role="alert">
        <p>{error}</p>
        <Link to="/">Back to discovery</Link>
      </div>
    )
  }
  if (!request) return null

  const supported = request.supported_by_current_user === true

  return (
    <section className="detail-page">
      <Link to="/">← Back to discovery</Link>
      <h1>{request.title}</h1>
      <p className="status-badge inline">{request.status}</p>
      <p className="detail-description">{request.description}</p>
      <p>
        <strong>{request.support_count}</strong> supporters · Created{' '}
        {new Date(request.created_at).toLocaleString()}
      </p>
      <button type="button" disabled={supported || supporting} onClick={() => void onSupport()}>
        {supported ? 'Supported' : supporting ? 'Supporting…' : 'Support'}
      </button>
      {error ? <p className="form-error">{error}</p> : null}
    </section>
  )
}
