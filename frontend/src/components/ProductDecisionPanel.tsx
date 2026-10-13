import { useState } from 'react'

import type { PriorityAssessmentResponse } from '../types/priority'
import type {
  ProductDecisionResponse,
  ProductDecisionType,
  ReviewerPriority,
} from '../types/productDecision'

type Props = {
  priority: PriorityAssessmentResponse | null
  decision: ProductDecisionResponse | null
  loading: boolean
  submitting: boolean
  error: string | null
  onSubmit: (payload: {
    decision: ProductDecisionType
    reviewer_priority?: ReviewerPriority
    override_reason?: string
    reviewer_note?: string
  }) => void
}

const REVIEWER_PRIORITIES: ReviewerPriority[] = ['LOW', 'MEDIUM', 'HIGH']

export function ProductDecisionPanel({
  priority,
  decision,
  loading,
  submitting,
  error,
  onSubmit,
}: Props) {
  const [mode, setMode] = useState<ProductDecisionType | null>(null)
  const [reviewerPriority, setReviewerPriority] = useState<ReviewerPriority>('MEDIUM')
  const [overrideReason, setOverrideReason] = useState('')
  const [reviewerNote, setReviewerNote] = useState('')
  const [clientError, setClientError] = useState<string | null>(null)

  const resetForm = () => {
    setMode(null)
    setOverrideReason('')
    setReviewerNote('')
    setClientError(null)
  }

  const submit = (decisionType: ProductDecisionType) => {
    setClientError(null)
    if (decisionType === 'OVERRIDDEN') {
      const trimmed = overrideReason.trim()
      if (trimmed.length < 10) {
        setClientError('Override reason must be at least 10 characters.')
        return
      }
      if (priority && reviewerPriority === priority.priority_level) {
        setClientError('Override priority must differ from the system recommendation.')
        return
      }
      onSubmit({
        decision: decisionType,
        reviewer_priority: reviewerPriority,
        override_reason: trimmed,
      })
      return
    }
    if (decisionType === 'DEFERRED' || decisionType === 'REJECTED') {
      onSubmit({
        decision: decisionType,
        reviewer_note: reviewerNote.trim() || undefined,
      })
      return
    }
    onSubmit({ decision: decisionType })
  }

  if (loading) {
    return (
      <section className="analysis-panel" aria-labelledby="product-decision-heading">
        <h2 id="product-decision-heading">Product decision</h2>
        <p>Loading decision…</p>
      </section>
    )
  }

  if (!priority) {
    return (
      <section className="analysis-panel" aria-labelledby="product-decision-heading">
        <h2 id="product-decision-heading">Product decision</h2>
        <p>Calculate priority before recording a product decision.</p>
      </section>
    )
  }

  const decisionSnapshot = decision?.system_recommendation_at_decision

  return (
    <section className="analysis-panel" aria-labelledby="product-decision-heading">
      <h2 id="product-decision-heading">Product decision</h2>
      <p className="analysis-advisory">Human judgment is separate from the deterministic system score.</p>

      {decision && decisionSnapshot ? (
        <div className="system-recommendation" data-testid="decision-time-system-recommendation">
          <h3>System recommendation at decision time</h3>
          <p className="priority-level">{decisionSnapshot.priority_level}</p>
          <p>
            {decisionSnapshot.total_score} / 100
          </p>
        </div>
      ) : (
        <div className="system-recommendation" data-testid="current-system-recommendation">
          <h3>System recommendation (current)</h3>
          <p className="priority-level">{priority.priority_level}</p>
          <p>
            {priority.total_score} / 100
          </p>
        </div>
      )}

      {decision ? (
        <div className="human-decision-record">
          <h3>Product decision</h3>
          <p>
            <strong>{decision.decision}</strong>
            {decision.decision === 'OVERRIDDEN' && decision.reviewer_priority ? (
              <> → {decision.reviewer_priority}</>
            ) : null}
          </p>
          {decision.override_reason ? <p>Reason: {decision.override_reason}</p> : null}
          {decision.reviewer_note ? <p>Note: {decision.reviewer_note}</p> : null}
        </div>
      ) : (
        <p>Not reviewed yet.</p>
      )}

      <div className="decision-actions">
        <button type="button" disabled={submitting} onClick={() => submit('APPROVED')}>
          Approve
        </button>
        <button type="button" disabled={submitting} onClick={() => setMode('OVERRIDDEN')}>
          Override
        </button>
        <button type="button" disabled={submitting} onClick={() => setMode('DEFERRED')}>
          Defer
        </button>
        <button type="button" disabled={submitting} onClick={() => setMode('REJECTED')}>
          Reject
        </button>
      </div>

      {mode === 'OVERRIDDEN' ? (
        <div className="override-form">
          <label htmlFor="reviewer-priority">Reviewer priority</label>
          <select
            id="reviewer-priority"
            value={reviewerPriority}
            onChange={(event) => setReviewerPriority(event.target.value as ReviewerPriority)}
          >
            {REVIEWER_PRIORITIES.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>
          <label htmlFor="override-reason">Override reason</label>
          <textarea
            id="override-reason"
            value={overrideReason}
            onChange={(event) => setOverrideReason(event.target.value)}
            rows={3}
          />
          <button type="button" disabled={submitting} onClick={() => submit('OVERRIDDEN')}>
            Submit override
          </button>
          <button type="button" onClick={resetForm}>
            Cancel
          </button>
        </div>
      ) : null}

      {(mode === 'DEFERRED' || mode === 'REJECTED') && (
        <div className="note-form">
          <label htmlFor="reviewer-note">Reviewer note (optional)</label>
          <textarea
            id="reviewer-note"
            value={reviewerNote}
            onChange={(event) => setReviewerNote(event.target.value)}
            rows={2}
          />
          <button
            type="button"
            disabled={submitting}
            onClick={() => submit(mode)}
          >
            Submit {mode === 'DEFERRED' ? 'defer' : 'reject'}
          </button>
          <button type="button" onClick={resetForm}>
            Cancel
          </button>
        </div>
      )}

      {clientError ? <p className="form-error">{clientError}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}
    </section>
  )
}
