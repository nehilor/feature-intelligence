import { getApiBaseUrl } from '../config'

import { ApiError, apiPost } from './client'
import type { FeatureAnalysisResponse } from '../types/featureAnalysis'

export class AnalysisNotFoundError extends Error {
  readonly name = 'AnalysisNotFoundError'
}

export async function getFeatureAnalysis(requestId: string): Promise<FeatureAnalysisResponse> {
  const url = `${getApiBaseUrl()}/api/feature-requests/${requestId}/analysis`
  let response: Response
  try {
    response = await fetch(url, { headers: { Accept: 'application/json' } })
  } catch {
    throw new ApiError('Network request failed')
  }
  if (response.status === 404) {
    let detail: unknown = null
    try {
      const body = (await response.json()) as { detail?: unknown }
      detail = body.detail
    } catch {
      // ignore parse errors
    }
    if (detail === 'analysis_not_found') {
      throw new AnalysisNotFoundError()
    }
    throw new ApiError('Feature request not found', 404)
  }
  if (!response.ok) {
    throw new ApiError(`Request failed with status ${response.status}`, response.status)
  }
  return (await response.json()) as FeatureAnalysisResponse
}

export async function analyzeFeatureRequest(requestId: string): Promise<FeatureAnalysisResponse> {
  return apiPost<FeatureAnalysisResponse>(`/api/feature-requests/${requestId}/analysis`, {})
}
