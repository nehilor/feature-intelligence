import { useCallback, useEffect, useState } from 'react'

import { fetchHealth } from '../api/health'
import type { ApiConnectivityStatus } from '../types/apiStatus'

export function useApiHealth(): {
  status: ApiConnectivityStatus
  retry: () => void
} {
  const [status, setStatus] = useState<ApiConnectivityStatus>('checking')
  const [attempt, setAttempt] = useState(0)

  const retry = useCallback(() => {
    setStatus('checking')
    setAttempt((value) => value + 1)
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    let cancelled = false

    async function load() {
      setStatus('checking')
      try {
        const health = await fetchHealth(controller.signal)
        if (cancelled) return
        setStatus(health.status === 'ok' ? 'connected' : 'unavailable')
      } catch {
        if (!cancelled) setStatus('unavailable')
      }
    }

    void load()
    return () => {
      cancelled = true
      controller.abort()
    }
  }, [attempt])

  return { status, retry }
}
