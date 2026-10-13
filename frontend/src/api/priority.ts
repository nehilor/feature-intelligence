import type { PriorityAssessmentResponse, StrategicAlignment } from '../types/priority'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export class PriorityNotFoundError extends Error {
  constructor() {
    super('priority_not_found')
    this.name = 'PriorityNotFoundError'
  }
}

export async function getPriority(requestId: string): Promise<PriorityAssessmentResponse> {
  const response = await fetch(`${API_BASE}/api/feature-requests/${requestId}/priority`)
  if (response.status === 404) {
    const body = (await response.json()) as { detail?: string }
    if (body.detail === 'priority_not_found') {
      throw new PriorityNotFoundError()
    }
  }
  if (!response.ok) {
    throw new Error('Failed to load priority')
  }
  return response.json() as Promise<PriorityAssessmentResponse>
}

export async function calculatePriority(
  requestId: string,
  strategicAlignment: StrategicAlignment,
): Promise<PriorityAssessmentResponse> {
  const response = await fetch(`${API_BASE}/api/feature-requests/${requestId}/priority`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ strategic_alignment: strategicAlignment }),
  })
  if (!response.ok) {
    throw new Error('Failed to calculate priority')
  }
  return response.json() as Promise<PriorityAssessmentResponse>
}
