import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import {
  AnalysisNotFoundError,
  analyzeFeatureRequest,
  getFeatureAnalysis,
} from '../api/featureAnalysis'
import { getFeatureRequest, supportFeatureRequest } from '../api/featureRequests'
import { calculatePriority, getPriority, PriorityNotFoundError } from '../api/priority'
import {
  DecisionBriefNotFoundError,
  generateDecisionBrief,
  getDecisionBrief,
} from '../api/decisionBrief'
import {
  DecisionNotFoundError,
  getProductDecision,
  submitProductDecision,
} from '../api/productDecision'
import { DecisionBriefPanel } from '../components/DecisionBriefPanel'
import { FeatureAnalysisPanel } from '../components/FeatureAnalysisPanel'
import { PriorityPanel } from '../components/PriorityPanel'
import { ProductDecisionPanel } from '../components/ProductDecisionPanel'
import { RelatedRequestsPanel } from '../components/RelatedRequestsPanel'
import {
  analyzeFeatureRelationships,
  getFeatureRelationships,
} from '../api/featureRelationships'
import { getSupporterKey } from '../lib/supporterKey'
import type { FeatureAnalysisResponse } from '../types/featureAnalysis'
import type { FeatureRequest } from '../types/featureRequest'
import type { RelationshipsResponse } from '../types/featureRelationships'
import type { DecisionBriefResponse } from '../types/decisionBrief'
import type { PriorityAssessmentResponse, StrategicAlignment } from '../types/priority'
import type { ProductDecisionResponse } from '../types/productDecision'

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
  const [relationships, setRelationships] = useState<RelationshipsResponse | null>(null)
  const [relationshipsLoading, setRelationshipsLoading] = useState(true)
  const [relationshipsRunning, setRelationshipsRunning] = useState(false)
  const [relationshipsError, setRelationshipsError] = useState<string | null>(null)
  const [relationshipsAnalyzed, setRelationshipsAnalyzed] = useState(false)
  const [priority, setPriority] = useState<PriorityAssessmentResponse | null>(null)
  const [priorityLoading, setPriorityLoading] = useState(true)
  const [priorityCalculating, setPriorityCalculating] = useState(false)
  const [priorityError, setPriorityError] = useState<string | null>(null)
  const [strategicAlignment, setStrategicAlignment] = useState<StrategicAlignment>('UNKNOWN')
  const [brief, setBrief] = useState<DecisionBriefResponse | null>(null)
  const [briefLoading, setBriefLoading] = useState(true)
  const [briefGenerating, setBriefGenerating] = useState(false)
  const [briefError, setBriefError] = useState<string | null>(null)
  const [decision, setDecision] = useState<ProductDecisionResponse | null>(null)
  const [decisionLoading, setDecisionLoading] = useState(true)
  const [decisionSubmitting, setDecisionSubmitting] = useState(false)
  const [decisionError, setDecisionError] = useState<string | null>(null)

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

  const runRelationships = useCallback(async () => {
    if (!requestId) return
    setRelationshipsRunning(true)
    setRelationshipsError(null)
    try {
      const data = await analyzeFeatureRelationships(requestId)
      setRelationships(data)
      setRelationshipsAnalyzed(true)
    } catch {
      setRelationshipsError('Unable to analyze related requests.')
    } finally {
      setRelationshipsRunning(false)
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

  useEffect(() => {
    if (!requestId) return
    let cancelled = false
    async function loadRelated() {
      const id = requestId
      if (!id) return
      setRelationshipsLoading(true)
      setRelationshipsError(null)
      try {
        const data = await getFeatureRelationships(id)
        if (!cancelled) {
          setRelationships(data)
          if (data.items.length > 0 || data.message) {
            setRelationshipsAnalyzed(true)
          }
        }
      } catch {
        if (!cancelled) {
          setRelationshipsError('Unable to load related requests.')
          setRelationships(null)
        }
      } finally {
        if (!cancelled) setRelationshipsLoading(false)
      }
    }
    void loadRelated()
    return () => {
      cancelled = true
    }
  }, [requestId])

  useEffect(() => {
    if (!requestId) return
    let cancelled = false
    void (async (id: string) => {
      setPriorityLoading(true)
      setPriorityError(null)
      try {
        const data = await getPriority(id)
        if (!cancelled) {
          setPriority(data)
          setStrategicAlignment(data.strategic_alignment)
        }
      } catch (err) {
        if (!cancelled && !(err instanceof PriorityNotFoundError)) {
          setPriorityError('Unable to load priority.')
        }
        if (!cancelled && err instanceof PriorityNotFoundError) {
          setPriority(null)
        }
      } finally {
        if (!cancelled) setPriorityLoading(false)
      }
    })(requestId)
    return () => {
      cancelled = true
    }
  }, [requestId])

  useEffect(() => {
    if (!requestId) return
    let cancelled = false
    void (async (id: string) => {
      setBriefLoading(true)
      setBriefError(null)
      try {
        const data = await getDecisionBrief(id)
        if (!cancelled) setBrief(data)
      } catch (err) {
        if (!cancelled && !(err instanceof DecisionBriefNotFoundError)) {
          setBriefError('Unable to load decision brief.')
        }
        if (!cancelled && err instanceof DecisionBriefNotFoundError) {
          setBrief(null)
        }
      } finally {
        if (!cancelled) setBriefLoading(false)
      }
    })(requestId)
    return () => {
      cancelled = true
    }
  }, [requestId])

  useEffect(() => {
    if (!requestId) return
    let cancelled = false
    void (async (id: string) => {
      setDecisionLoading(true)
      setDecisionError(null)
      try {
        const data = await getProductDecision(id)
        if (!cancelled) setDecision(data)
      } catch (err) {
        if (!cancelled && !(err instanceof DecisionNotFoundError)) {
          setDecisionError('Unable to load product decision.')
        }
        if (!cancelled && err instanceof DecisionNotFoundError) {
          setDecision(null)
        }
      } finally {
        if (!cancelled) setDecisionLoading(false)
      }
    })(requestId)
    return () => {
      cancelled = true
    }
  }, [requestId])

  const onCalculatePriority = async () => {
    if (!requestId) return
    setPriorityCalculating(true)
    setPriorityError(null)
    try {
      const data = await calculatePriority(requestId, strategicAlignment)
      setPriority(data)
    } catch {
      setPriorityError('Unable to calculate priority.')
    } finally {
      setPriorityCalculating(false)
    }
  }

  const onGenerateBrief = async () => {
    if (!requestId) return
    setBriefGenerating(true)
    setBriefError(null)
    try {
      const data = await generateDecisionBrief(requestId)
      setBrief(data)
    } catch (err) {
      if (err instanceof Error && err.message === 'decision_brief_unavailable') {
        setBriefError('decision_brief_unavailable')
      } else {
        setBriefError('Unable to generate decision brief.')
      }
    } finally {
      setBriefGenerating(false)
    }
  }

  const onSubmitDecision = async (payload: Parameters<typeof submitProductDecision>[1]) => {
    if (!requestId) return
    setDecisionSubmitting(true)
    setDecisionError(null)
    try {
      const data = await submitProductDecision(requestId, payload)
      setDecision(data)
    } catch {
      setDecisionError('Unable to submit product decision.')
    } finally {
      setDecisionSubmitting(false)
    }
  }

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
      <RelatedRequestsPanel
        data={relationships}
        loading={relationshipsLoading}
        running={relationshipsRunning}
        error={relationshipsError}
        hasAnalyzed={relationshipsAnalyzed}
        onAnalyze={() => void runRelationships()}
      />
      <PriorityPanel
        priority={priority}
        loading={priorityLoading}
        calculating={priorityCalculating}
        error={priorityError}
        strategicAlignment={strategicAlignment}
        onStrategicAlignmentChange={setStrategicAlignment}
        onCalculate={() => void onCalculatePriority()}
      />
      <DecisionBriefPanel
        brief={brief}
        loading={briefLoading}
        generating={briefGenerating}
        error={briefError}
        priorityReady={priority !== null}
        onGenerate={() => void onGenerateBrief()}
      />
      <ProductDecisionPanel
        priority={priority}
        decision={decision}
        loading={decisionLoading}
        submitting={decisionSubmitting}
        error={decisionError}
        onSubmit={(payload) => void onSubmitDecision(payload)}
      />
    </section>
  )
}
