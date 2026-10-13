import { apiGet, apiPost } from './client'
import type {
  FeatureRequest,
  FeatureRequestListResponse,
  SupportResponse,
} from '../types/featureRequest'

export type ListParams = {
  q?: string
  sort?: 'recent' | 'supported'
  limit?: number
  offset?: number
  supporterKey?: string
}

function withSupporterQuery(path: string, supporterKey?: string): string {
  if (!supporterKey) return path
  const separator = path.includes('?') ? '&' : '?'
  return `${path}${separator}supporter_key=${encodeURIComponent(supporterKey)}`
}

export async function listFeatureRequests(params: ListParams = {}): Promise<FeatureRequestListResponse> {
  const search = new URLSearchParams()
  if (params.q) search.set('q', params.q)
  if (params.sort) search.set('sort', params.sort)
  if (params.limit !== undefined) search.set('limit', String(params.limit))
  if (params.offset !== undefined) search.set('offset', String(params.offset))
  const query = search.toString()
  const path = withSupporterQuery(
    `/api/feature-requests${query ? `?${query}` : ''}`,
    params.supporterKey,
  )
  return apiGet<FeatureRequestListResponse>(path)
}

export async function getFeatureRequest(
  id: string,
  supporterKey?: string,
): Promise<FeatureRequest> {
  return apiGet<FeatureRequest>(withSupporterQuery(`/api/feature-requests/${id}`, supporterKey))
}

export async function createFeatureRequest(payload: {
  title: string
  description: string
}): Promise<FeatureRequest> {
  return apiPost<FeatureRequest>('/api/feature-requests', payload)
}

export async function supportFeatureRequest(
  id: string,
  supporterKey: string,
): Promise<SupportResponse> {
  return apiPost<SupportResponse>(`/api/feature-requests/${id}/support`, {
    supporter_key: supporterKey,
  })
}
