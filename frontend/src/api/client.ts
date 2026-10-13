import { getApiBaseUrl } from '../config'

export class ApiError extends Error {
  readonly status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const url = `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`
  let response: Response
  try {
    response = await fetch(url, { signal, headers: { Accept: 'application/json' } })
  } catch {
    throw new ApiError('Network request failed')
  }
  if (!response.ok) {
    throw new ApiError(`Request failed with status ${response.status}`, response.status)
  }
  return (await response.json()) as T
}

export async function apiPost<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
  const url = `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`
  let response: Response
  try {
    response = await fetch(url, {
      method: 'POST',
      signal,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new ApiError('Network request failed')
  }
  if (!response.ok) {
    throw new ApiError(`Request failed with status ${response.status}`, response.status)
  }
  return (await response.json()) as T
}
