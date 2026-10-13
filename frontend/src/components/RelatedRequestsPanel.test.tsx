import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { RelatedRequestsPanel } from './RelatedRequestsPanel'

describe('RelatedRequestsPanel', () => {
  it('shows not analyzed state', () => {
    render(
      <RelatedRequestsPanel
        data={null}
        loading={false}
        running={false}
        error={null}
        hasAnalyzed={false}
        onAnalyze={() => {}}
      />,
    )
    expect(screen.getByText('Not analyzed yet.')).toBeInTheDocument()
  })

  it('renders potential duplicate and related items', () => {
    render(
      <MemoryRouter>
        <RelatedRequestsPanel
          data={{
            feature_request_id: 'a',
            status: 'ok',
            items: [
              {
                feature_request_id: 'b',
                title: 'Download dashboard data',
                relationship: 'DUPLICATE',
                similarity_score: 0.9,
                confidence: 'HIGH',
                reason: 'Both concern external reporting.',
                support_count: 2,
              },
              {
                feature_request_id: 'c',
                title: 'Dark mode',
                relationship: 'DISTINCT',
                similarity_score: 0.2,
                confidence: 'HIGH',
                reason: 'Different problem.',
                support_count: 1,
              },
            ],
          }}
          loading={false}
          running={false}
          error={null}
          hasAnalyzed={true}
          onAnalyze={() => {}}
        />
      </MemoryRouter>,
    )
    expect(screen.getByText('Potential duplicate')).toBeInTheDocument()
    expect(screen.getByText('Download dashboard data')).toBeInTheDocument()
    expect(screen.queryByText('Dark mode')).not.toBeInTheDocument()
  })

  it('shows unavailable state', () => {
    render(
      <RelatedRequestsPanel
        data={{
          feature_request_id: 'a',
          status: 'embedding_unavailable',
          items: [],
          message: 'Relationship analysis is unavailable.',
        }}
        loading={false}
        running={false}
        error={null}
        hasAnalyzed={true}
        onAnalyze={() => {}}
      />,
    )
    expect(screen.getByText(/unavailable/i)).toBeInTheDocument()
  })
})
