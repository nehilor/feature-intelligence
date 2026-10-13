import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { PriorityPanel } from './PriorityPanel'
import type { PriorityAssessmentResponse } from '../types/priority'

const samplePriority: PriorityAssessmentResponse = {
  feature_request_id: 'req-1',
  priority_level: 'HIGH',
  total_score: 78,
  formula_version: 'priority_formula_v1',
  evidence_completeness: 'COMPLETE',
  strategic_alignment: 'HIGH',
  breakdown: {
    demand: { score: 30, max_score: 40, support_count: 4, relationship_signal_count: 2 },
    customer_impact: { value: 'HIGH', score: 25, max_score: 25 },
    urgency: { value: 'LOW', score: 3, max_score: 15 },
    strategic_alignment: { value: 'HIGH', score: 20, max_score: 20 },
  },
}

describe('PriorityPanel', () => {
  afterEach(() => {
    cleanup()
  })

  it('shows empty state before assessment', () => {
    render(
      <PriorityPanel
        priority={null}
        loading={false}
        calculating={false}
        error={null}
        strategicAlignment="UNKNOWN"
        onStrategicAlignmentChange={() => {}}
        onCalculate={() => {}}
      />,
    )
    expect(screen.getByText(/No priority assessment yet/i)).toBeInTheDocument()
  })

  it('renders score breakdown and evidence counts', () => {
    render(
      <PriorityPanel
        priority={samplePriority}
        loading={false}
        calculating={false}
        error={null}
        strategicAlignment="HIGH"
        onStrategicAlignmentChange={() => {}}
        onCalculate={() => {}}
      />,
    )
    expect(screen.getByText('HIGH')).toBeInTheDocument()
    expect(screen.getByText(/Score 78 \/ 100/i)).toBeInTheDocument()
    expect(screen.getByText(/4 direct supporters/i)).toBeInTheDocument()
    expect(screen.getByText(/Demand 30 \/ 40/i)).toBeInTheDocument()
  })

  it('shows partial evidence indicator', () => {
    render(
      <PriorityPanel
        priority={{ ...samplePriority, evidence_completeness: 'PARTIAL' }}
        loading={false}
        calculating={false}
        error={null}
        strategicAlignment="HIGH"
        onStrategicAlignmentChange={() => {}}
        onCalculate={() => {}}
      />,
    )
    expect(screen.getByText(/Partial evidence/i)).toBeInTheDocument()
  })

  it('calls calculate when button clicked', () => {
    const onCalculate = vi.fn()
    render(
      <PriorityPanel
        priority={null}
        loading={false}
        calculating={false}
        error={null}
        strategicAlignment="MEDIUM"
        onStrategicAlignmentChange={() => {}}
        onCalculate={onCalculate}
      />,
    )
    fireEvent.click(screen.getByRole('button', { name: /Calculate priority/i }))
    expect(onCalculate).toHaveBeenCalled()
  })
})
