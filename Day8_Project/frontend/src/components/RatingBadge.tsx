import { formatRating, ratingTone } from '../format'

/** Colored pill showing an average rating, e.g. "4.33". */
export function RatingBadge({ value, label }: { value: number; label?: string }) {
  return (
    <span className={`rating-badge tone-${ratingTone(value)}`} aria-label={label ?? `Average rating ${formatRating(value)}`}>
      {formatRating(value)}
    </span>
  )
}

/** Horizontal bar for a single 1–5 rating parameter. */
export function RatingBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="rating-bar">
      <span className="rating-bar-label">{label}</span>
      <div className="rating-bar-track" aria-hidden="true">
        <div className={`rating-bar-fill tone-${ratingTone(value)}`} style={{ width: `${(value / 5) * 100}%` }} />
      </div>
      <span className="rating-bar-value" aria-label={`${label} rating`}>
        {value} / 5
      </span>
    </div>
  )
}
