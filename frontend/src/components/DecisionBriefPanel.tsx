import type { DecisionBriefResponse } from '../types/decisionBrief'

type Props = {
  brief: DecisionBriefResponse | null
  loading: boolean
  generating: boolean
  error: string | null
  priorityReady: boolean
  onGenerate: () => void
}

export function DecisionBriefPanel({
  brief,
  loading,
  generating,
  error,
  priorityReady,
  onGenerate,
}: Props) {
  return (
    <section className="analysis-panel" aria-labelledby="decision-brief-heading">
      <h2 id="decision-brief-heading">AI-assisted decision brief</h2>
      <p className="analysis-advisory">
        Summarizes trusted evidence. The AI does not set priority or make the product decision.
      </p>

      {!priorityReady ? (
        <p>Calculate priority before generating a decision brief.</p>
      ) : (
        <button type="button" onClick={onGenerate} disabled={generating}>
          {generating ? 'Generating…' : brief ? 'Regenerate decision brief' : 'Generate decision brief'}
        </button>
      )}

      {loading ? <p>Loading decision brief…</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      {!loading && !brief && priorityReady && !error ? (
        <p>No decision brief yet.</p>
      ) : null}

      {brief ? (
        <div className="decision-brief-content">
          <h3>Problem</h3>
          <p>{brief.problem}</p>
          <h3>Evidence</h3>
          <p>{brief.evidence_summary}</p>
          <h3>Why it matters</h3>
          <p>{brief.why_it_matters}</p>
          <h3>Risks &amp; unknowns</h3>
          <ul>
            {brief.risks_and_unknowns.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <h3>Recommended next step</h3>
          <p>{brief.recommended_next_step}</p>
        </div>
      ) : null}

      {!loading && error === 'decision_brief_unavailable' ? (
        <p role="status">Decision brief unavailable.</p>
      ) : null}
    </section>
  )
}
