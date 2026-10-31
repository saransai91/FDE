import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { api } from '../api/client'
import { Pagination } from '../components/Pagination'
import { RatingBadge } from '../components/RatingBadge'
import { formatDate } from '../format'
import { useMasterData } from '../hooks'
import type { ReviewFilters, ReviewPage } from '../types'

/** Filters live in the URL so "Back" from the detail screen keeps them. */
function readFilters(params: URLSearchParams): ReviewFilters {
  const size = Number(params.get('page_size'))
  return {
    employee_id: params.get('employee_id') || undefined,
    review_period_id: Number(params.get('review_period_id')) || undefined,
    page: Math.max(1, Number(params.get('page')) || 1),
    page_size: size === 5 ? 5 : 10,
  }
}

export function MyReviewsPage() {
  const { employees, periods, error: loadError } = useMasterData()
  const [params, setParams] = useSearchParams()
  const filters = readFilters(params)
  const [data, setData] = useState<ReviewPage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const key = params.toString()
  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    api
      .listReviews(readFilters(new URLSearchParams(key)))
      .then((d) => active && setData(d))
      .catch((err: Error) => active && setError(err.message))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [key])

  const update = (changes: Partial<Record<keyof ReviewFilters, string | number | undefined>>) => {
    const next = new URLSearchParams(params)
    for (const [k, v] of Object.entries(changes)) {
      if (v === undefined || v === '') next.delete(k)
      else next.set(k, String(v))
    }
    if (!('page' in changes)) next.delete('page') // a filter change goes back to page 1
    setParams(next)
  }

  const selectedEmployee = employees.find((e) => e.employee_id === filters.employee_id)
  const selectedPeriod = periods.find((p) => p.review_period_id === filters.review_period_id)
  const scope = [selectedEmployee?.name ?? 'All employees', selectedPeriod?.name ?? 'all periods'].join(' · ')

  return (
    <section>
      <header className="page-header">
        <h1>My reviews</h1>
        <p className="muted">Search reviews by review period and employee.</p>
      </header>

      {(loadError || error) && <div className="alert alert-error">{loadError || error}</div>}

      <div className="card filters" role="search">
        <label className="field">
          <span>Review period</span>
          <select
            aria-label="Review period"
            value={filters.review_period_id ?? ''}
            onChange={(e) => update({ review_period_id: e.target.value })}
          >
            <option value="">All periods</option>
            {periods.map((p) => (
              <option key={p.review_period_id} value={p.review_period_id}>
                {p.name} ({p.period_type})
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Employee</span>
          <select
            aria-label="Employee"
            value={filters.employee_id ?? ''}
            onChange={(e) => update({ employee_id: e.target.value })}
          >
            <option value="">All employees</option>
            {employees.map((e) => (
              <option key={e.employee_id} value={e.employee_id}>
                {e.name} ({e.employee_id})
              </option>
            ))}
          </select>
        </label>
        <label className="field field-narrow">
          <span>Rows per page</span>
          <select aria-label="Rows per page" value={filters.page_size} onChange={(e) => update({ page_size: e.target.value })}>
            <option value={5}>5</option>
            <option value={10}>10</option>
          </select>
        </label>
        {(filters.employee_id || filters.review_period_id) && (
          <button type="button" className="btn btn-link" onClick={() => setParams(new URLSearchParams())}>
            Clear filters
          </button>
        )}
      </div>

      {data && (
        <div className="summary">
          <div className="stat">
            <span className="stat-label">Reviews</span>
            <span className="stat-value" data-testid="total-reviews">
              {data.total}
            </span>
          </div>
          <div className="stat">
            <span className="stat-label">Average rating · {scope}</span>
            <span className="stat-value" data-testid="overall-average">
              {data.average_rating == null ? '–' : <RatingBadge value={data.average_rating} />}
            </span>
          </div>
        </div>
      )}

      <div className="card table-card" aria-busy={loading}>
        <table>
          <thead>
            <tr>
              <th>Employee</th>
              <th>Department</th>
              <th>Review period</th>
              <th className="num">Quality</th>
              <th className="num">Delivery</th>
              <th className="num">Teamwork</th>
              <th className="num">Average</th>
              <th>Submitted</th>
              <th aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {data?.items.map((r) => (
              <tr key={r.review_id}>
                <td>
                  <div className="cell-primary">{r.employee_name}</div>
                  <div className="muted small">{r.employee_id}</div>
                </td>
                <td>{r.department}</td>
                <td>{r.review_period_name}</td>
                <td className="num">{r.quality_rating}</td>
                <td className="num">{r.delivery_rating}</td>
                <td className="num">{r.teamwork_rating}</td>
                <td className="num">
                  <RatingBadge value={r.average_rating} />
                </td>
                <td>{formatDate(r.created_at)}</td>
                <td>
                  <Link className="btn btn-small" to={`/reviews/${r.review_id}`} state={{ from: `/reviews?${key}` }}>
                    View
                  </Link>
                </td>
              </tr>
            ))}
            {data && data.items.length === 0 && (
              <tr>
                <td colSpan={9} className="empty">
                  No reviews match these filters.
                </td>
              </tr>
            )}
            {!data && loading && (
              <tr>
                <td colSpan={9} className="empty">
                  Loading…
                </td>
              </tr>
            )}
          </tbody>
        </table>
        {data && (
          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            total={data.total}
            pageSize={data.page_size}
            onPageChange={(page) => update({ page })}
          />
        )}
      </div>
    </section>
  )
}
