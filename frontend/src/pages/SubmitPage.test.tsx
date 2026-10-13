import { screen } from '@testing-library/dom'
import { cleanup, render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { SubmitPage } from './SubmitPage'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('SubmitPage', () => {
  it('validates title and description', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <SubmitPage />
      </MemoryRouter>,
    )
    await user.type(screen.getByLabelText(/title/i), 'ab')
    await user.type(screen.getByLabelText(/description/i), 'too short')
    await user.click(screen.getByRole('button', { name: /submit request/i }))
    expect(await screen.findByRole('alert')).toHaveTextContent(/must be/i)
  })

  it('submits a valid request', async () => {
    const user = userEvent.setup()
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          id: 'new-id',
          title: 'New request title',
          description: 'New request description with enough detail.',
          status: 'SUBMITTED',
          support_count: 0,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        }),
      }),
    )
    render(
      <MemoryRouter>
        <SubmitPage />
      </MemoryRouter>,
    )
    await user.type(screen.getByLabelText(/title/i), 'New request title')
    await user.type(
      screen.getByLabelText(/description/i),
      'New request description with enough detail.',
    )
    await user.click(screen.getByRole('button', { name: /submit request/i }))
    expect(vi.mocked(fetch)).toHaveBeenCalled()
  })
})
