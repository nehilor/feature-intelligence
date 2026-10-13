import type { DecisionBriefResponse } from '../types/decisionBrief'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export class DecisionBriefNotFoundError extends Error {
  constructor() {
    super('decision_brief_not_found')
    this.name = 'DecisionBriefNotFoundError'
  }
}

export async function getDecisionBrief(requestId: string): Promise<DecisionBriefResponse> {
  const response = await fetch(`${API_BASE}/api/feature-requests/${requestId}/decision-brief`)
  if (response.status === 404) {
    const body = (await response.json()) as { detail?: string }
    if (body.detail === 'decision_brief_not_found') {
      throw new DecisionBriefNotFoundError()
    }
  }
  if (!response.ok) {
    throw new Error('Failed to load decision brief')
  }
  return response.json() as Promise<DecisionBriefResponse>
}

export async function generateDecisionBrief(requestId: string): Promise<DecisionBriefResponse> {
  const response = await fetch(`${API_BASE}/api/feature-requests/${requestId}/decision-brief`, {
    method: 'POST',
  })
  if (response.status === 503) {
    throw new Error('decision_brief_unavailable')
  }
  if (!response.ok) {
    throw new Error('Failed to generate decision brief')
  }
  return response.json() as Promise<DecisionBriefResponse>
}
