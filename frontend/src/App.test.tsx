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
  it('renders the application shell', () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
    render(<App />)
    expect(screen.getByRole('heading', { level: 1, name: 'Feature Intelligence' })).toBeInTheDocument()
    expect(screen.getByText(/application foundation is running/i)).toBeInTheDocument()
  })

  it('renders connected health state', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'ok' }),
      }),
    )
    render(<App />)
    expect(await screen.findByText('Connected')).toBeInTheDocument()
  })

  it('does not crash when backend is unavailable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    render(<App />)
    expect(await screen.findByText('Unavailable')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /retry connection/i })).toBeInTheDocument()
  })
})
