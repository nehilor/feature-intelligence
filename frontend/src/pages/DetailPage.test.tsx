import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { DetailPage } from './DetailPage'
import { AnalysisNotFoundError } from '../api/featureAnalysis'
import * as featureAnalysisApi from '../api/featureAnalysis'
import * as featureRequestsApi from '../api/featureRequests'

vi.mock('../api/featureRequests')
vi.mock('../api/featureAnalysis')

const mockRequest = {
  id: 'req-1',
  title: 'Export reports',
  description: 'Finance needs CSV export for reconciliation.',
  status: 'SUBMITTED' as const,
  support_count: 2,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  supported_by_current_user: false,
}

function renderDetail() {
  return render(
    <MemoryRouter initialEntries={['/requests/req-1']}>
      <Routes>
        <Route path="/requests/:requestId" element={<DetailPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('DetailPage AI analysis', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  beforeEach(() => {
    vi.mocked(featureRequestsApi.getFeatureRequest).mockResolvedValue(mockRequest)
    vi.mocked(featureAnalysisApi.analyzeFeatureRequest).mockResolvedValue({
      feature_request_id: 'req-1',
      processing_state: 'MANUAL_REVIEW_REQUIRED',
      message: 'AI analysis is currently unavailable. Manual review is required.',
    })
  })

  it('shows not analyzed state before analysis exists', async () => {
    vi.mocked(featureAnalysisApi.getFeatureAnalysis).mockRejectedValue(new AnalysisNotFoundError())
    vi.mocked(featureAnalysisApi.analyzeFeatureRequest).mockImplementation(
      () => new Promise(() => {}),
    )

    renderDetail()

    await waitFor(() => {
      expect(screen.getByText('Original Request')).toBeInTheDocument()
    })
    expect(screen.getByText(mockRequest.description)).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('Not analyzed yet.')).toBeInTheDocument()
    })
  })

  it('shows manual review when analysis failed previously', async () => {
    vi.mocked(featureAnalysisApi.getFeatureAnalysis).mockResolvedValue({
      feature_request_id: 'req-1',
      processing_state: 'MANUAL_REVIEW_REQUIRED',
      message: 'AI analysis is currently unavailable. Manual review is required.',
    })

    renderDetail()

    await waitFor(() => {
      expect(screen.getByText(/Manual review is required/i)).toBeInTheDocument()
    })
    expect(screen.queryByText('Not analyzed yet.')).not.toBeInTheDocument()
  })

  it('displays successful analysis fields', async () => {
    vi.mocked(featureAnalysisApi.getFeatureAnalysis).mockResolvedValue({
      feature_request_id: 'req-1',
      processing_state: 'AI_COMPLETE',
      analysis: {
        summary: 'Finance users need reporting export.',
        underlying_need: 'External reconciliation workflow.',
        theme: 'REPORTING_AND_DATA',
        customer_impact: 'HIGH',
        urgency: 'UNKNOWN',
        confidence: 'HIGH',
        rationale: 'Recurring finance reporting work.',
      },
      ai_metadata: {
        provider: 'openai',
        model: 'gpt-test',
        prompt_version: 'feature_triage_v1',
      },
    })

    renderDetail()

    await waitFor(() => {
      expect(screen.getByText('AI-assisted analysis')).toBeInTheDocument()
    })
    expect(screen.getByText('Finance users need reporting export.')).toBeInTheDocument()
    expect(screen.getByText('External reconciliation workflow.')).toBeInTheDocument()
    expect(screen.getByText(/REPORTING AND DATA/i)).toBeInTheDocument()
    expect(screen.getByText('Recurring finance reporting work.')).toBeInTheDocument()
    expect(screen.getByText('Customer impact')).toBeInTheDocument()
  })

  it('highlights low confidence analysis', async () => {
    vi.mocked(featureAnalysisApi.getFeatureAnalysis).mockResolvedValue({
      feature_request_id: 'req-1',
      processing_state: 'AI_COMPLETE',
      analysis: {
        summary: 'Summary.',
        underlying_need: 'Need.',
        theme: 'OTHER',
        customer_impact: 'UNKNOWN',
        urgency: 'UNKNOWN',
        confidence: 'LOW',
        rationale: 'Limited evidence.',
      },
      ai_metadata: {
        provider: 'openai',
        model: 'gpt-test',
        prompt_version: 'feature_triage_v1',
      },
    })

    renderDetail()

    await waitFor(() => {
      expect(screen.getByText(/low confidence/i)).toBeInTheDocument()
    })
  })

  it('keeps request visible when analysis fails', async () => {
    vi.mocked(featureAnalysisApi.getFeatureAnalysis).mockRejectedValue(new Error('fail'))
    vi.mocked(featureAnalysisApi.analyzeFeatureRequest).mockRejectedValue(new Error('fail'))
    renderDetail()
    await waitFor(() => {
      expect(screen.getAllByText(mockRequest.title).length).toBeGreaterThan(0)
    })
  })
})
