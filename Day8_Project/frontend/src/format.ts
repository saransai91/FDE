export const formatRating = (n: number | null | undefined) => (n == null ? '–' : n.toFixed(2))

export const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })

/** Tone used to color an average rating: low < 2.5 <= mid < 3.75 <= high. */
export const ratingTone = (n: number) => (n >= 3.75 ? 'high' : n >= 2.5 ? 'mid' : 'low')
