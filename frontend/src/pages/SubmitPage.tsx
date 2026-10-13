import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { createFeatureRequest } from '../api/featureRequests'

const TITLE_MIN = 3
const TITLE_MAX = 120
const DESCRIPTION_MIN = 10
const DESCRIPTION_MAX = 4000

export function SubmitPage() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const validate = (): string | null => {
    const trimmedTitle = title.trim()
    const trimmedDescription = description.trim()
    if (trimmedTitle.length < TITLE_MIN || trimmedTitle.length > TITLE_MAX) {
      return `Title must be ${TITLE_MIN}-${TITLE_MAX} characters.`
    }
    if (trimmedDescription.length < DESCRIPTION_MIN || trimmedDescription.length > DESCRIPTION_MAX) {
      return `Description must be ${DESCRIPTION_MIN}-${DESCRIPTION_MAX} characters.`
    }
    return null
  }

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const created = await createFeatureRequest({
        title: title.trim(),
        description: description.trim(),
      })
      navigate(`/requests/${created.id}`)
    } catch {
      setError('Unable to submit the request. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="form-page">
      <Link to="/">← Back to discovery</Link>
      <h1>Submit a feature request</h1>
      <form onSubmit={onSubmit} className="request-form">
        <label htmlFor="title">Title</label>
        <input
          id="title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          maxLength={TITLE_MAX}
          required
        />
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          maxLength={DESCRIPTION_MAX}
          rows={6}
          required
        />
        {error ? (
          <p className="form-error" role="alert">
            {error}
          </p>
        ) : null}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Submitting…' : 'Submit request'}
        </button>
      </form>
    </section>
  )
}
