import type { FeatureAnalysisResponse } from '../types/featureAnalysis'

type Props = {
  analysisState: FeatureAnalysisResponse | null
  loading: boolean
  running: boolean
  error: string | null
  onRunAnalysis: () => void
}

function formatLabel(value: string): string {
  return value.replaceAll('_', ' ')
}

export function FeatureAnalysisPanel({
  analysisState,
  loading,
  running,
  error,
  onRunAnalysis,
}: Props) {
  if (loading) {
    return (
      <section className="analysis-panel" aria-labelledby="analysis-heading">
        <h2 id="analysis-heading">AI Analysis</h2>
        <p>Loading analysis…</p>
      </section>
    )
  }

  const processing = analysisState?.processing_state
  const hasStructuredAnalysis =
    analysisState?.analysis &&
    (processing === 'AI_COMPLETE' || processing === 'AI_PARTIAL')

  if (!analysisState) {
    return (
      <section className="analysis-panel" aria-labelledby="analysis-heading">
        <h2 id="analysis-heading">AI Analysis</h2>
        <p className="analysis-advisory">AI analysis is advisory and does not set product priority.</p>
        <p>Not analyzed yet.</p>
        <button type="button" onClick={onRunAnalysis} disabled={running}>
          {running ? 'Analyzing…' : 'Run AI analysis'}
        </button>
        {error ? <p className="form-error">{error}</p> : null}
      </section>
    )
  }

  if (processing === 'MANUAL_REVIEW_REQUIRED' && !hasStructuredAnalysis) {
    return (
      <section className="analysis-panel" aria-labelledby="analysis-heading">
        <h2 id="analysis-heading">AI Analysis</h2>
        <p className="analysis-advisory">AI analysis is advisory and does not set product priority.</p>
        <p role="status">
          {analysisState.message ?? 'AI analysis is currently unavailable. Manual review is required.'}
        </p>
        <button type="button" onClick={onRunAnalysis} disabled={running}>
          {running ? 'Analyzing…' : 'Retry analysis'}
        </button>
        {error ? <p className="form-error">{error}</p> : null}
      </section>
    )
  }

  if (running) {
    return (
      <section className="analysis-panel" aria-labelledby="analysis-heading">
        <h2 id="analysis-heading">AI Analysis</h2>
        <p role="status">Analyzing…</p>
      </section>
    )
  }

  if (!hasStructuredAnalysis) {
    return null
  }

  const { analysis, ai_metadata } = analysisState
  if (!analysis) return null

  const lowConfidence = analysis.confidence === 'LOW'
  const fallbackNote = ai_metadata?.used_fallback ? 'Analyzed with Gemini fallback.' : null

  return (
    <section className="analysis-panel" aria-labelledby="analysis-heading">
      <h2 id="analysis-heading">AI-assisted analysis</h2>
      <p className="analysis-advisory">AI analysis is advisory and does not set product priority.</p>
      {fallbackNote ? <p className="analysis-meta">{fallbackNote}</p> : null}
      {lowConfidence ? (
        <p className="analysis-warning" role="status">
          This analysis has low confidence and should be reviewed by a human.
        </p>
      ) : null}
      <dl className="analysis-fields">
        <div>
          <dt>Summary</dt>
          <dd>{analysis.summary}</dd>
        </div>
        <div>
          <dt>Underlying need</dt>
          <dd>{analysis.underlying_need}</dd>
        </div>
        <div>
          <dt>Theme</dt>
          <dd>{formatLabel(analysis.theme)}</dd>
        </div>
        <div>
          <dt>Customer impact</dt>
          <dd>{formatLabel(analysis.customer_impact)}</dd>
        </div>
        <div>
          <dt>Urgency</dt>
          <dd>{formatLabel(analysis.urgency)}</dd>
        </div>
        <div>
          <dt>Confidence</dt>
          <dd>{formatLabel(analysis.confidence)}</dd>
        </div>
        <div>
          <dt>Rationale</dt>
          <dd>{analysis.rationale}</dd>
        </div>
      </dl>
      {error ? <p className="form-error">{error}</p> : null}
    </section>
  )
}
