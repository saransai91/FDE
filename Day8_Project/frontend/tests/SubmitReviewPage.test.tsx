import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { vi, type Mocked } from 'vitest'
import { api as realApi, ApiError } from '../src/api/client'
import { SubmitReviewPage, validate } from '../src/pages/SubmitReviewPage'
import { employees, makeReview, periods } from './fixtures'

vi.mock('../src/api/client', async (orig) => ({
  ...(await orig<typeof import('../src/api/client')>()),
  api: { listEmployees: vi.fn(), listReviewPeriods: vi.fn(), createReview: vi.fn() },
}))
const api = realApi as Mocked<typeof realApi>

beforeEach(() => {
  api.listEmployees.mockResolvedValue(employees)
  api.listReviewPeriods.mockResolvedValue(periods)
})

function renderPage() {
  render(
    <MemoryRouter>
      <SubmitReviewPage />
    </MemoryRouter>,
  )
}

async function fillForm(comments = 'Great sprint') {
  const user = userEvent.setup()
  await screen.findByRole('option', { name: /John Smith/ })
  const [employee, period] = screen.getAllByRole('combobox')
  await user.selectOptions(employee, 'EMP101')
  await user.selectOptions(period, '6')
  await user.click(screen.getByLabelText(/Quality 4/))
  await user.click(screen.getByLabelText(/Delivery 5/))
  await user.click(screen.getByLabelText(/Teamwork 4/))
  if (comments) await user.type(screen.getByPlaceholderText(/What went well/), comments)
  return user
}

test('dropdowns are filled from master data and only list active employees', async () => {
  renderPage()
  const [employee, period] = await screen.findAllByRole('combobox')
  await screen.findByRole('option', { name: /John Smith/ })

  expect(within(employee).getAllByRole('option').map((o) => o.textContent)).toEqual([
    'Select employee…',
    'John Smith (EMP101) – Engineering',
    'Sarah Johnson (EMP102) – Engineering',
  ])
  expect(within(period).getByRole('option', { name: 'Q3 2026 (Quarterly)' })).toBeInTheDocument()
})

test('shows validation errors and does not call the API when the form is empty', async () => {
  renderPage()
  await screen.findByRole('option', { name: /John Smith/ })
  await userEvent.click(screen.getByRole('button', { name: 'Submit review' }))

  expect(screen.getByText('Select an employee')).toBeInTheDocument()
  expect(screen.getByText('Select a review period')).toBeInTheDocument()
  expect(screen.getByText('Quality rating is required')).toBeInTheDocument()
  expect(screen.getByText('Comments are mandatory')).toBeInTheDocument()
  expect(api.createReview).not.toHaveBeenCalled()
})

test('comments are mandatory even when everything else is filled', async () => {
  renderPage()
  const user = await fillForm('')
  await user.type(screen.getByPlaceholderText(/What went well/), '   ')
  await user.click(screen.getByRole('button', { name: 'Submit review' }))

  expect(screen.getByText('Comments are mandatory')).toBeInTheDocument()
  expect(api.createReview).not.toHaveBeenCalled()
})

test('shows the live average and submits the review', async () => {
  api.createReview.mockResolvedValue({
    message: 'Review submitted successfully',
    review: makeReview({ review_id: 42, quality_rating: 4, delivery_rating: 5, teamwork_rating: 4, average_rating: 4.33 }),
  })
  renderPage()
  const user = await fillForm()

  expect(screen.getByLabelText('Average rating 4.33')).toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: 'Submit review' }))

  expect(api.createReview).toHaveBeenCalledWith({
    employee_id: 'EMP101',
    review_period_id: 6,
    quality_rating: 4,
    delivery_rating: 5,
    teamwork_rating: 4,
    comments: 'Great sprint',
  })
  const success = await screen.findByRole('status')
  expect(success).toHaveTextContent('Review submitted for John Smith (Q3 2026)')
  expect(within(success).getByRole('link', { name: 'View review' })).toHaveAttribute('href', '/reviews/42')
})

test('shows the server error for a duplicate review', async () => {
  api.createReview.mockRejectedValue(new ApiError(409, 'John Smith already has a review for Q3 2026'))
  renderPage()
  const user = await fillForm()
  await user.click(screen.getByRole('button', { name: 'Submit review' }))

  expect(await screen.findByRole('alert')).toHaveTextContent('already has a review')
})

test('validate() rules', () => {
  const ok = { employee_id: 'E', review_period_id: '1', quality_rating: 1, delivery_rating: 5, teamwork_rating: 3, comments: 'x' }
  expect(validate(ok)).toEqual({})
  expect(validate({ ...ok, teamwork_rating: 0 })).toHaveProperty('teamwork_rating')
  expect(validate({ ...ok, quality_rating: 6 })).toHaveProperty('quality_rating')
})
