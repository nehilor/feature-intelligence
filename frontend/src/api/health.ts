import { apiGet } from './client'

export type HealthResponse = {
  status: string
}

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiGet<HealthResponse>('/api/health', signal)
}
