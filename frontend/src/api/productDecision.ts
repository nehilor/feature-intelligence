import { getApiBaseUrl } from '../config'

import type { ProductDecisionCreate, ProductDecisionResponse } from '../types/productDecision'

export class DecisionNotFoundError extends Error {
  constructor() {
    super('decision_not_found')
    this.name = 'DecisionNotFoundError'
  }
}

export async function getProductDecision(requestId: string): Promise<ProductDecisionResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/feature-requests/${requestId}/decision`)
  if (response.status === 404) {
    const body = (await response.json()) as { detail?: string }
    if (body.detail === 'decision_not_found') {
      throw new DecisionNotFoundError()
    }
  }
  if (!response.ok) {
    throw new Error('Failed to load product decision')
  }
  return response.json() as Promise<ProductDecisionResponse>
}

export async function submitProductDecision(
  requestId: string,
  payload: ProductDecisionCreate,
): Promise<ProductDecisionResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/feature-requests/${requestId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Failed to submit product decision')
  }
  return response.json() as Promise<ProductDecisionResponse>
}
