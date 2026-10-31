// Mirrors the backend contract in docs/openapi.json. Do not change field names.

export interface Employee {
  employee_id: string
  name: string
  department: string
  designation: string
  email: string
  status: 'Active' | 'Inactive'
}

export interface ReviewPeriod {
  review_period_id: number
  name: string
  period_type: 'Monthly' | 'Quarterly' | 'Half-Yearly' | 'Annual'
  start_date: string
  end_date: string
  status: 'Open' | 'Closed'
}

export interface ReviewCreate {
  employee_id: string
  review_period_id: number
  quality_rating: number
  delivery_rating: number
  teamwork_rating: number
  comments: string
}

export interface Review {
  review_id: number
  employee_id: string
  employee_name: string
  department: string
  designation: string
  review_period_id: number
  review_period_name: string
  period_type: string
  quality_rating: number
  delivery_rating: number
  teamwork_rating: number
  average_rating: number
  comments: string
  created_at: string
}

export interface ReviewCreated {
  message: string
  review: Review
}

export interface ReviewPage {
  items: Review[]
  total: number
  page: number
  page_size: number
  total_pages: number
  average_rating: number | null
}

export interface ReviewFilters {
  employee_id?: string
  review_period_id?: number
  page: number
  page_size: 5 | 10
}

export const RATING_FIELDS = [
  { key: 'quality_rating', label: 'Quality' },
  { key: 'delivery_rating', label: 'Delivery' },
  { key: 'teamwork_rating', label: 'Teamwork' },
] as const
