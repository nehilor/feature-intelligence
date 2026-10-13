import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { listFeatureRequests, supportFeatureRequest } from '../api/featureRequests'
import { RequestCard } from '../components/RequestCard'
import { getSupporterKey } from '../lib/supporterKey'
import type { FeatureRequest } from '../types/featureRequest'

const PAGE_SIZE = 10

export function DiscoverPage() {
  const [items, setItems] = useState<FeatureRequest[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [q, setQ] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [sort, setSort] = useState<'recent' | 'supported'>('recent')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [supportingId, setSupportingId] = useState<string | null>(null)
  const [hasLoadedOnce, setHasLoadedOnce] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function loadRequests() {
      setLoading(true)
      setError(null)
      try {
        const response = await listFeatureRequests({
          q: q || undefined,
          sort,
          limit: PAGE_SIZE,
          offset,
          supporterKey: getSupporterKey(),
        })
        if (cancelled) return
        setItems(response.items)
        setTotal(response.total)
        setHasLoadedOnce(true)
      } catch {
        if (!cancelled) {
          setError('Unable to load feature requests. Check that the backend is running.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void loadRequests()
    return () => {
      cancelled = true
    }
  }, [offset, q, sort])

  const reload = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await listFeatureRequests({
        q: q || undefined,
        sort,
        limit: PAGE_SIZE,
        offset,
        supporterKey: getSupporterKey(),
      })
      setItems(response.items)
      setTotal(response.total)
      setHasLoadedOnce(true)
    } catch {
      setError('Unable to load feature requests. Check that the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const onSearch = (event: React.FormEvent) => {
    event.preventDefault()
    setOffset(0)
    setQ(searchInput.trim())
  }

  const onSupport = async (id: string) => {
    setSupportingId(id)
    try {
      await supportFeatureRequest(id, getSupporterKey())
      await reload()
    } catch {
      setError('Unable to record support. Please try again.')
    } finally {
      setSupportingId(null)
    }
  }

  const emptyRepository = hasLoadedOnce && !loading && !error && total === 0 && !q
  const noSearchResults = hasLoadedOnce && !loading && !error && total === 0 && Boolean(q)

  return (
    <section>
      <div className="toolbar">
        <form className="search-form" onSubmit={onSearch}>
          <label htmlFor="search">Search requests</label>
          <input
            id="search"
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            placeholder="Search title or description"
          />
          <button type="submit">Search</button>
          {q ? (
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setSearchInput('')
                setQ('')
                setOffset(0)
              }}
            >
              Clear
            </button>
          ) : null}
        </form>
        <div className="sort-row">
          <label htmlFor="sort">Sort</label>
          <select
            id="sort"
            value={sort}
            onChange={(event) => {
              setSort(event.target.value as 'recent' | 'supported')
              setOffset(0)
            }}
          >
            <option value="recent">Most recent</option>
            <option value="supported">Most supported</option>
          </select>
          <Link className="primary-link" to="/requests/new">
            Submit request
          </Link>
        </div>
      </div>

      {loading ? <p>Loading requests…</p> : null}
      {error ? (
        <div className="error-banner" role="alert">
          <p>{error}</p>
          <button type="button" onClick={() => void reload()}>
            Retry
          </button>
        </div>
      ) : null}

      {emptyRepository ? (
        <div className="empty-state">
          <p>No feature requests yet.</p>
          <Link to="/requests/new">Submit the first request</Link>
        </div>
      ) : null}

      {noSearchResults ? (
        <div className="empty-state">
          <p>No requests match your search.</p>
          <button
            type="button"
            className="secondary"
            onClick={() => {
              setSearchInput('')
              setQ('')
              setOffset(0)
            }}
          >
            Clear search
          </button>
        </div>
      ) : null}

      <div className="request-list">
        {items.map((request) => (
          <RequestCard
            key={request.id}
            request={request}
            onSupport={onSupport}
            supportingId={supportingId}
          />
        ))}
      </div>

      {total > PAGE_SIZE ? (
        <div className="pagination">
          <button type="button" disabled={offset === 0} onClick={() => setOffset(offset - PAGE_SIZE)}>
            Previous
          </button>
          <span>
            {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
          </span>
          <button
            type="button"
            disabled={offset + PAGE_SIZE >= total}
            onClick={() => setOffset(offset + PAGE_SIZE)}
          >
            Next
          </button>
        </div>
      ) : null}
    </section>
  )
}
