import { screen } from '@testing-library/dom'
import { cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('App', () => {
  it('renders product shell and discovery area', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const url = String(input)
        if (url.includes('/api/health')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ status: 'ok' }),
          })
        }
        return Promise.resolve({
          ok: true,
          json: async () => ({ items: [], total: 0, limit: 10, offset: 0 }),
        })
      }),
    )
    render(<App />)
    expect(screen.getByRole('link', { name: 'Feature Intelligence' })).toBeInTheDocument()
    expect(await screen.findByText(/no feature requests yet/i)).toBeInTheDocument()
  })
})
