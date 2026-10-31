import type { Employee, Review, ReviewPage, ReviewPeriod } from '../src/types'

export const employees: Employee[] = [
  { employee_id: 'EMP101', name: 'John Smith', department: 'Engineering', designation: 'Senior Developer', email: 'john@example.com', status: 'Active' },
  { employee_id: 'EMP102', name: 'Sarah Johnson', department: 'Engineering', designation: 'Developer', email: 'sarah@example.com', status: 'Active' },
  { employee_id: 'EMP199', name: 'Gone Person', department: 'QA', designation: 'QA', email: 'gone@example.com', status: 'Inactive' },
]

export const periods: ReviewPeriod[] = [
  { review_period_id: 3, name: 'H2 2026', period_type: 'Half-Yearly', start_date: '2026-07-01', end_date: '2026-12-31', status: 'Open' },
  { review_period_id: 6, name: 'Q3 2026', period_type: 'Quarterly', start_date: '2026-07-01', end_date: '2026-09-30', status: 'Open' },
]

export function makeReview(overrides: Partial<Review> = {}): Review {
  return {
    review_id: 1,
    employee_id: 'EMP101',
    employee_name: 'John Smith',
    department: 'Engineering',
    designation: 'Senior Developer',
    review_period_id: 6,
    review_period_name: 'Q3 2026',
    period_type: 'Quarterly',
    quality_rating: 5,
    delivery_rating: 5,
    teamwork_rating: 4,
    average_rating: 4.67,
    comments: 'Led the sprint demo.',
    created_at: '2026-10-05T09:00:00Z',
    ...overrides,
  }
}

export function makePage(items: Review[], overrides: Partial<ReviewPage> = {}): ReviewPage {
  return {
    items,
    total: items.length,
    page: 1,
    page_size: 10,
    total_pages: items.length ? 1 : 0,
    average_rating: items.length ? items.reduce((s, r) => s + r.average_rating, 0) / items.length : null,
    ...overrides,
  }
}
