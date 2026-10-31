import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router'
import { api } from '../api/client'
import { RatingBadge, RatingBar } from '../components/RatingBadge'
import { formatDate } from '../format'
import { RATING_FIELDS, type Review } from '../types'

export function ReviewDetailPage() {
  const { reviewId } = useParams()
  const location = useLocation()
  const backTo = (location.state as { from?: string } | null)?.from ?? '/reviews'
  const [review, setReview] = useState<Review | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    setReview(null)
    setError(null)
    api
      .getReview(Number(reviewId))
      .then((r) => active && setReview(r))
      .catch((err: Error) => active && setError(err.message))
    return () => {
      active = false
    }
  }, [reviewId])

  return (
    <section>
      <Link to={backTo} className="btn btn-link back">
        ‹ Back to reviews
      </Link>

      {error && <div className="alert alert-error">{error}</div>}
      {!review && !error && <p className="muted">Loading…</p>}

      {review && (
        <>
          <header className="page-header detail-header">
            <div>
              <h1>{review.employee_name}</h1>
              <p className="muted">
                {review.employee_id} · {review.designation} · {review.department}
              </p>
            </div>
            <div className="detail-average">
              <span className="muted small">Average rating</span>
              <RatingBadge value={review.average_rating} />
            </div>
          </header>

          <div className="detail-grid">
            <div className="card">
              <h2>Ratings</h2>
              {RATING_FIELDS.map(({ key, label }) => (
                <RatingBar key={key} label={label} value={review[key]} />
              ))}
              <p className="muted small formula">
                Average = ({review.quality_rating} + {review.delivery_rating} + {review.teamwork_rating}) ÷ 3 ={' '}
                {review.average_rating.toFixed(2)}
              </p>
            </div>

            <div className="card">
              <h2>Review</h2>
              <dl className="detail-list">
                <dt>Review period</dt>
                <dd>
                  {review.review_period_name} ({review.period_type})
                </dd>
                <dt>Submitted</dt>
                <dd>{formatDate(review.created_at)}</dd>
                <dt>Review ID</dt>
                <dd>#{review.review_id}</dd>
              </dl>
            </div>

            <div className="card detail-comments">
              <h2>Comments</h2>
              <p className="comments">{review.comments}</p>
            </div>
          </div>

          <p>
            <Link to={`/reviews?employee_id=${review.employee_id}`}>
              See all reviews for {review.employee_name} ›
            </Link>
          </p>
        </>
      )}
    </section>
  )
}
