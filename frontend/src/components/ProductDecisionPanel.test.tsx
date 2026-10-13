import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { ProductDecisionPanel } from './ProductDecisionPanel'
import type { PriorityAssessmentResponse } from '../types/priority'
import type { ProductDecisionResponse } from '../types/productDecision'

const currentPriority: PriorityAssessmentResponse = {
  feature_request_id: 'req-1',
  priority_level: 'HIGH',
  total_score: 83,
  formula_version: 'priority_formula_v1',
  evidence_completeness: 'COMPLETE',
  strategic_alignment: 'HIGH',
  breakdown: {
    demand: { score: 35, max_score: 40, support_count: 5, relationship_signal_count: 2 },
    customer_impact: { value: 'HIGH', score: 25, max_score: 25 },
    urgency: { value: 'LOW', score: 3, max_score: 15 },
    strategic_alignment: { value: 'HIGH', score: 20, max_score: 20 },
  },
}

const decisionAt78: ProductDecisionResponse = {
  feature_request_id: 'req-1',
  priority_assessment_id: 'pa-1',
  decision: 'OVERRIDDEN',
  reviewer_priority: 'MEDIUM',
  override_reason: 'Platform dependencies make immediate delivery impractical.',
  system_recommendation_at_decision: {
    priority_level: 'HIGH',
    total_score: 78,
    formula_version: 'priority_formula_v1',
    demand_score: 30,
    impact_score: 25,
    urgency_score: 3,
    strategic_alignment_score: 20,
  },
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('ProductDecisionPanel audit snapshot', () => {
  afterEach(() => {
    cleanup()
  })

  it('shows decision-time system score, not recalculated current priority', () => {
    render(
      <ProductDecisionPanel
        priority={currentPriority}
        decision={decisionAt78}
        loading={false}
        submitting={false}
        error={null}
        onSubmit={() => {}}
      />,
    )

    const block = screen.getByTestId('decision-time-system-recommendation')
    expect(block).toHaveTextContent('78 / 100')
    expect(block).not.toHaveTextContent('83 / 100')
    expect(screen.queryByTestId('current-system-recommendation')).not.toBeInTheDocument()
  })
})
