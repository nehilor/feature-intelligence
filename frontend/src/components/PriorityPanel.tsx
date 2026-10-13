import type { PriorityAssessmentResponse, StrategicAlignment } from '../types/priority'

type Props = {
  priority: PriorityAssessmentResponse | null
  loading: boolean
  calculating: boolean
  error: string | null
  strategicAlignment: StrategicAlignment
  onStrategicAlignmentChange: (value: StrategicAlignment) => void
  onCalculate: () => void
}

const ALIGNMENT_OPTIONS: { value: StrategicAlignment; label: string }[] = [
  { value: 'UNKNOWN', label: 'Unknown' },
  { value: 'LOW', label: 'Low' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'HIGH', label: 'High' },
]

export function PriorityPanel({
  priority,
  loading,
  calculating,
  error,
  strategicAlignment,
  onStrategicAlignmentChange,
  onCalculate,
}: Props) {
  return (
    <section className="analysis-panel priority-panel" aria-labelledby="priority-heading">
      <h2 id="priority-heading">Priority</h2>
      <p className="analysis-advisory">
        Deterministic score from support, relationships, AI impact/urgency, and human strategic
        alignment. This is not an AI-generated priority.
      </p>

      <div className="priority-human-input">
        <label htmlFor="strategic-alignment">Strategic alignment (human input)</label>
        <select
          id="strategic-alignment"
          value={strategicAlignment}
          onChange={(event) =>
            onStrategicAlignmentChange(event.target.value as StrategicAlignment)
          }
        >
          {ALIGNMENT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <button type="button" onClick={onCalculate} disabled={calculating}>
          {calculating ? 'Calculating…' : priority ? 'Recalculate priority' : 'Calculate priority'}
        </button>
      </div>

      {loading ? <p>Loading priority…</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      {!loading && !priority ? (
        <p>No priority assessment yet. Choose strategic alignment and calculate.</p>
      ) : null}

      {priority ? (
        <>
          {priority.evidence_completeness === 'PARTIAL' ? (
            <p className="partial-evidence" role="status">
              Partial evidence — some inputs may be missing (for example AI analysis unavailable or
              strategic alignment unknown).
            </p>
          ) : null}
          <div className="system-recommendation">
            <h3>System recommendation</h3>
            <p className="priority-level">{priority.priority_level}</p>
            <p>
              Score {priority.total_score} / 100
            </p>
          </div>
          <ul className="priority-breakdown">
            <li>
              Demand {priority.breakdown.demand.score} / {priority.breakdown.demand.max_score}
            </li>
            <li>
              Customer Impact {priority.breakdown.customer_impact.score} /{' '}
              {priority.breakdown.customer_impact.max_score}
            </li>
            <li>
              Urgency {priority.breakdown.urgency.score} / {priority.breakdown.urgency.max_score}
            </li>
            <li>
              Strategic Alignment {priority.breakdown.strategic_alignment.score} /{' '}
              {priority.breakdown.strategic_alignment.max_score}
            </li>
          </ul>
          <p className="priority-evidence-counts">
            {priority.breakdown.demand.support_count} direct supporters ·{' '}
            {priority.breakdown.demand.relationship_signal_count} related request signals
          </p>
        </>
      ) : null}
    </section>
  )
}
