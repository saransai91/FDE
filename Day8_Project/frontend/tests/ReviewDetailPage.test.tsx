import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router'
import { vi, type Mocked } from 'vitest'
import { api as realApi, ApiError } from '../src/api/client'
import { ReviewDetailPage } from '../src/pages/ReviewDetailPage'
import { makeReview } from './fixtures'

vi.mock('../src/api/client', async (orig) => ({
  ...(await orig<typeof import('../src/api/client')>()),
  api: { getReview: vi.fn() },
}))
const api = realApi as Mocked<typeof realApi>

function renderAt(url: string) {
  render(
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route path="/reviews/:reviewId" element={<ReviewDetailPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

test('shows full review details', async () => {
  api.getReview.mockResolvedValue(makeReview({ review_id: 7 }))
  renderAt('/reviews/7')

  expect(await screen.findByRole('heading', { name: 'John Smith' })).toBeInTheDocument()
  expect(api.getReview).toHaveBeenCalledWith(7)
  expect(screen.getByText('EMP101 · Senior Developer · Engineering')).toBeInTheDocument()
  expect(screen.getByLabelText('Quality rating')).toHaveTextContent('5 / 5')
  expect(screen.getByLabelText('Teamwork rating')).toHaveTextContent('4 / 5')
  expect(screen.getByText('Average = (5 + 5 + 4) ÷ 3 = 4.67')).toBeInTheDocument()
  expect(screen.getByText('Q3 2026 (Quarterly)')).toBeInTheDocument()
  expect(screen.getByText('Led the sprint demo.')).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /See all reviews for John Smith/ })).toHaveAttribute(
    'href',
    '/reviews?employee_id=EMP101',
  )
})

test('shows an error for a missing review', async () => {
  api.getReview.mockRejectedValue(new ApiError(404, 'Review 99 not found'))
  renderAt('/reviews/99')

  expect(await screen.findByText('Review 99 not found')).toBeInTheDocument()
})
