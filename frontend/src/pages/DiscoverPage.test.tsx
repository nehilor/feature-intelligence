import { screen } from '@testing-library/dom'
import { cleanup, render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { DiscoverPage } from './DiscoverPage'

vi.mock('../lib/supporterKey', () => ({
  getSupporterKey: () => 'test-supporter',
}))

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('DiscoverPage', () => {
  it('shows loading then list items', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          items: [
            {
              id: '1',
              title: 'Export reports to CSV',
              description: 'Need CSV export for finance workflows and reporting.',
              status: 'SUBMITTED',
              support_count: 2,
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
              supported_by_current_user: false,
            },
          ],
          total: 1,
          limit: 10,
          offset: 0,
        }),
      }),
    )
    render(
      <MemoryRouter>
        <DiscoverPage />
      </MemoryRouter>,
    )
    expect(screen.getByText(/loading requests/i)).toBeInTheDocument()
    expect(await screen.findByText('Export reports to CSV')).toBeInTheDocument()
  })

  it('shows empty repository state', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ items: [], total: 0, limit: 10, offset: 0 }),
      }),
    )
    render(
      <MemoryRouter>
        <DiscoverPage />
      </MemoryRouter>,
    )
    expect(await screen.findByText(/no feature requests yet/i)).toBeInTheDocument()
  })

  it('shows API failure without crashing', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    render(
      <MemoryRouter>
        <DiscoverPage />
      </MemoryRouter>,
    )
    expect(await screen.findByRole('alert')).toHaveTextContent(/unable to load feature requests/i)
  })
})
