import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { vi, type Mocked } from 'vitest'
import { api as realApi } from '../src/api/client'
import { MyReviewsPage } from '../src/pages/MyReviewsPage'
import { employees, makePage, makeReview, periods } from './fixtures'

vi.mock('../src/api/client', async (orig) => ({
  ...(await orig<typeof import('../src/api/client')>()),
  api: { listEmployees: vi.fn(), listReviewPeriods: vi.fn(), listReviews: vi.fn() },
}))
const api = realApi as Mocked<typeof realApi>

const reviews = [
  makeReview({ review_id: 1 }),
  makeReview({ review_id: 2, employee_id: 'EMP102', employee_name: 'Sarah Johnson', quality_rating: 3, delivery_rating: 4, teamwork_rating: 4, average_rating: 3.67 }),
]

beforeEach(() => {
  api.listEmployees.mockResolvedValue(employees)
  api.listReviewPeriods.mockResolvedValue(periods)
  api.listReviews.mockResolvedValue(makePage(reviews))
})

function renderPage(url = '/reviews') {
  render(
    <MemoryRouter initialEntries={[url]}>
      <MyReviewsPage />
    </MemoryRouter>,
  )
}

test('lists reviews with rating values, average and a View link', async () => {
  renderPage()
  const row = (await screen.findByText('Sarah Johnson')).closest('tr')!
  const cells = within(row).getAllByRole('cell').map((c) => c.textContent)

  expect(cells.slice(1, 7)).toEqual(['Engineering', 'Q3 2026', '3', '4', '4', '3.67'])
  expect(within(row).getByRole('link', { name: 'View' })).toHaveAttribute('href', '/reviews/2')
  expect(screen.getByTestId('total-reviews')).toHaveTextContent('2')
  expect(screen.getByTestId('overall-average')).toHaveTextContent('4.17')
  expect(api.listReviews).toHaveBeenCalledWith({ page: 1, page_size: 10, employee_id: undefined, review_period_id: undefined })
})

test('filters by review period and employee', async () => {
  renderPage()
  await screen.findByRole('option', { name: /John Smith/ })
  const user = userEvent.setup()

  await user.selectOptions(screen.getByLabelText('Review period'), '6')
  expect(api.listReviews).toHaveBeenLastCalledWith(expect.objectContaining({ review_period_id: 6, page: 1 }))

  api.listReviews.mockResolvedValue(makePage([reviews[0]]))
  await user.selectOptions(screen.getByLabelText('Employee'), 'EMP101')
  expect(api.listReviews).toHaveBeenLastCalledWith(
    expect.objectContaining({ review_period_id: 6, employee_id: 'EMP101', page: 1 }),
  )
  expect(await screen.findByText(/John Smith · Q3 2026/)).toBeInTheDocument()
})

test('paginates with next / previous and page size', async () => {
  api.listReviews.mockResolvedValue(makePage(reviews, { total: 12, total_pages: 3, page_size: 5 }))
  renderPage('/reviews?page_size=5')
  const user = userEvent.setup()

  expect(await screen.findByText('Page 1 of 3')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /Previous/ })).toBeDisabled()

  api.listReviews.mockResolvedValue(makePage(reviews, { total: 12, total_pages: 3, page_size: 5, page: 2 }))
  await user.click(screen.getByRole('button', { name: /Next/ }))
  expect(api.listReviews).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2, page_size: 5 }))
  expect(await screen.findByText('Page 2 of 3')).toBeInTheDocument()

  await user.selectOptions(screen.getByLabelText('Rows per page'), '10')
  expect(api.listReviews).toHaveBeenLastCalledWith(expect.objectContaining({ page: 1, page_size: 10 }))
})

test('shows an empty state', async () => {
  api.listReviews.mockResolvedValue(makePage([]))
  renderPage('/reviews?employee_id=EMP102')

  expect(await screen.findByText('No reviews match these filters.')).toBeInTheDocument()
  expect(screen.getByTestId('overall-average')).toHaveTextContent('–')
})
