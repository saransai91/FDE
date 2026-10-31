import { useState, type FormEvent } from 'react'
import { Link } from 'react-router'
import { api } from '../api/client'
import { RatingInput } from '../components/RatingInput'
import { RatingBadge } from '../components/RatingBadge'
import { useMasterData } from '../hooks'
import { RATING_FIELDS, type Review } from '../types'

type RatingKey = (typeof RATING_FIELDS)[number]['key']

interface FormState {
  employee_id: string
  review_period_id: string
  quality_rating: number
  delivery_rating: number
  teamwork_rating: number
  comments: string
}

const EMPTY: FormState = {
  employee_id: '',
  review_period_id: '',
  quality_rating: 0,
  delivery_rating: 0,
  teamwork_rating: 0,
  comments: '',
}

type Errors = Partial<Record<keyof FormState, string>>

export function validate(f: FormState): Errors {
  const errors: Errors = {}
  if (!f.employee_id) errors.employee_id = 'Select an employee'
  if (!f.review_period_id) errors.review_period_id = 'Select a review period'
  for (const { key, label } of RATING_FIELDS) {
    if (f[key] < 1 || f[key] > 5) errors[key] = `${label} rating is required`
  }
  if (!f.comments.trim()) errors.comments = 'Comments are mandatory'
  return errors
}

export function SubmitReviewPage() {
  const { employees, periods, error: loadError, loading } = useMasterData()
  const [form, setForm] = useState<FormState>(EMPTY)
  const [errors, setErrors] = useState<Errors>({})
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  const [created, setCreated] = useState<Review | null>(null)

  const activeEmployees = employees.filter((e) => e.status === 'Active')
  const openPeriods = periods.filter((p) => p.status === 'Open')
  const ratings = RATING_FIELDS.map(({ key }) => form[key])
  const liveAverage = ratings.every((r) => r > 0) ? ratings.reduce((a, b) => a + b, 0) / 3 : null

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((f) => ({ ...f, [key]: value }))
    setErrors((e) => ({ ...e, [key]: undefined }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setServerError(null)
    const found = validate(form)
    setErrors(found)
    if (Object.keys(found).length) return

    setSubmitting(true)
    try {
      const res = await api.createReview({
        employee_id: form.employee_id,
        review_period_id: Number(form.review_period_id),
        quality_rating: form.quality_rating,
        delivery_rating: form.delivery_rating,
        teamwork_rating: form.teamwork_rating,
        comments: form.comments.trim(),
      })
      setCreated(res.review)
      setForm(EMPTY)
    } catch (err) {
      setServerError((err as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section>
      <header className="page-header">
        <h1>Submit a review</h1>
        <p className="muted">Give feedback for a sprint or review period. All fields are required.</p>
      </header>

      {loadError && <div className="alert alert-error">{loadError}</div>}

      {created && (
        <div className="alert alert-success" role="status">
          Review submitted for <strong>{created.employee_name}</strong> ({created.review_period_name}) — average{' '}
          <RatingBadge value={created.average_rating} />. <Link to={`/reviews/${created.review_id}`}>View review</Link>
        </div>
      )}

      <form className="card form" onSubmit={handleSubmit} noValidate aria-busy={loading}>
        <div className="form-row">
          <label className="field">
            <span>
              Employee <span className="required">*</span>
            </span>
            <select
              value={form.employee_id}
              onChange={(e) => set('employee_id', e.target.value)}
              aria-invalid={!!errors.employee_id}
            >
              <option value="">Select employee…</option>
              {activeEmployees.map((e) => (
                <option key={e.employee_id} value={e.employee_id}>
                  {e.name} ({e.employee_id}) – {e.department}
                </option>
              ))}
            </select>
            {errors.employee_id && <span className="field-error">{errors.employee_id}</span>}
          </label>

          <label className="field">
            <span>
              Review period <span className="required">*</span>
            </span>
            <select
              value={form.review_period_id}
              onChange={(e) => set('review_period_id', e.target.value)}
              aria-invalid={!!errors.review_period_id}
            >
              <option value="">Select period…</option>
              {openPeriods.map((p) => (
                <option key={p.review_period_id} value={p.review_period_id}>
                  {p.name} ({p.period_type})
                </option>
              ))}
            </select>
            {errors.review_period_id && <span className="field-error">{errors.review_period_id}</span>}
          </label>
        </div>

        <div className="ratings-grid">
          {RATING_FIELDS.map(({ key, label }) => (
            <RatingInput
              key={key}
              name={key}
              label={label}
              value={form[key as RatingKey]}
              onChange={(v) => set(key, v)}
              error={errors[key]}
            />
          ))}
          <div className="average-preview">
            <span className="muted">Average rating</span>
            {liveAverage == null ? <span className="muted">–</span> : <RatingBadge value={liveAverage} />}
          </div>
        </div>

        <label className="field">
          <span>
            Comments <span className="required">*</span>
          </span>
          <textarea
            rows={5}
            maxLength={2000}
            value={form.comments}
            onChange={(e) => set('comments', e.target.value)}
            placeholder="What went well, what to improve…"
            aria-invalid={!!errors.comments}
          />
          <span className="hint">{form.comments.length} / 2000</span>
          {errors.comments && <span className="field-error">{errors.comments}</span>}
        </label>

        {serverError && (
          <div className="alert alert-error" role="alert">
            {serverError}
          </div>
        )}

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={() => (setForm(EMPTY), setErrors({}))}>
            Reset
          </button>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit review'}
          </button>
        </div>
      </form>
    </section>
  )
}
