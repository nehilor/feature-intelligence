import { apiGet, apiPost } from './client'
import type { RelationshipsResponse } from '../types/featureRelationships'

export async function getFeatureRelationships(requestId: string): Promise<RelationshipsResponse> {
  return apiGet<RelationshipsResponse>(`/api/feature-requests/${requestId}/relationships`)
}

export async function analyzeFeatureRelationships(requestId: string): Promise<RelationshipsResponse> {
  return apiPost<RelationshipsResponse>(`/api/feature-requests/${requestId}/relationships/analyze`, {})
}
