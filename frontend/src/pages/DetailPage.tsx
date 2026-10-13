import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import {
  AnalysisNotFoundError,
  analyzeFeatureRequest,
  getFeatureAnalysis,
} from '../api/featureAnalysis'
import { getFeatureRequest, supportFeatureRequest } from '../api/featureRequests'
import { FeatureAnalysisPanel } from '../components/FeatureAnalysisPanel'
import { getSupporterKey } from '../lib/supporterKey'
import type { FeatureAnalysisResponse } from '../types/featureAnalysis'
import type { FeatureRequest } from '../types/featureRequest'

export function DetailPage() {
  const { requestId } = useParams()
  const [request, setRequest] = useState<FeatureRequest | null>(null)
  const [analysis, setAnalysis] = useState<FeatureAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [analysisLoading, setAnalysisLoading] = useState(true)
  const [runningAnalysis, setRunningAnalysis] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [supporting, setSupporting] = useState(false)
  const autoAnalyzeAttempted = useRef(false)

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

  const loadAnalysis = useCallback(async () => {
    if (!requestId) return null
    setAnalysisLoading(true)
    setAnalysisError(null)
    try {
      const data = await getFeatureAnalysis(requestId)
      setAnalysis(data)
      return data
    } catch (err) {
      if (err instanceof AnalysisNotFoundError) {
        setAnalysis(null)
        return null
      }
      setAnalysisError('Unable to load AI analysis.')
      setAnalysis(null)
      return null
    } finally {
      setAnalysisLoading(false)
    }
  }, [requestId])

  const runAnalysis = useCallback(async () => {
    if (!requestId) return
    setRunningAnalysis(true)
    setAnalysisError(null)
    try {
      const data = await analyzeFeatureRequest(requestId)
      setAnalysis(data)
    } catch {
      setAnalysisError('Unable to run AI analysis.')
    } finally {
      setRunningAnalysis(false)
    }
  }, [requestId])

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

  useEffect(() => {
    if (!requestId) return
    let cancelled = false
    async function bootstrapAnalysis() {
      if (!requestId) return
      const current = await loadAnalysis()
      if (cancelled || autoAnalyzeAttempted.current) return
      if (current === null) {
        autoAnalyzeAttempted.current = true
        setRunningAnalysis(true)
        try {
          const result = await analyzeFeatureRequest(requestId)
          if (!cancelled) setAnalysis(result)
        } catch {
          if (!cancelled) setAnalysisError('Unable to run AI analysis.')
        } finally {
          if (!cancelled) setRunningAnalysis(false)
        }
      }
    }
    void bootstrapAnalysis()
    return () => {
      cancelled = true
    }
  }, [requestId, loadAnalysis])

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
      <section aria-labelledby="original-request-heading">
        <h2 id="original-request-heading">Original Request</h2>
        <p className="detail-description">{request.description}</p>
      </section>
      <p>
        <strong>{request.support_count}</strong> supporters · Created{' '}
        {new Date(request.created_at).toLocaleString()}
      </p>
      <button type="button" disabled={supported || supporting} onClick={() => void onSupport()}>
        {supported ? 'Supported' : supporting ? 'Supporting…' : 'Support'}
      </button>
      {error ? <p className="form-error">{error}</p> : null}
      <FeatureAnalysisPanel
        analysisState={analysis}
        loading={analysisLoading}
        running={runningAnalysis}
        error={analysisError}
        onRunAnalysis={() => void runAnalysis()}
      />
    </section>
  )
}
