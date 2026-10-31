import type { Employee, Review, ReviewCreate, ReviewCreated, ReviewFilters, ReviewPage, ReviewPeriod } from '../types'

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

function errorMessage(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown } | null)?.detail
  if (typeof detail === 'string') return detail
  // FastAPI validation errors: [{ loc, msg }, ...]
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join('; ')
  return `Request failed (${status})`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiError(0, 'Cannot reach the server. Is the backend running?')
  }
  const body = await res.json().catch(() => null)
  if (!res.ok) throw new ApiError(res.status, errorMessage(body, res.status))
  return body as T
}

export const api = {
  listEmployees: () => request<Employee[]>('/employees'),
  getEmployee: (id: string) => request<Employee>(`/employees/${encodeURIComponent(id)}`),
  listReviewPeriods: () => request<ReviewPeriod[]>('/review-periods'),
  listReviews: (f: ReviewFilters) => {
    const q = new URLSearchParams({ page: String(f.page), page_size: String(f.page_size) })
    if (f.employee_id) q.set('employee_id', f.employee_id)
    if (f.review_period_id) q.set('review_period_id', String(f.review_period_id))
    return request<ReviewPage>(`/reviews?${q}`)
  },
  getReview: (id: number) => request<Review>(`/reviews/${id}`),
  createReview: (body: ReviewCreate) =>
    request<ReviewCreated>('/reviews', { method: 'POST', body: JSON.stringify(body) }),
}
