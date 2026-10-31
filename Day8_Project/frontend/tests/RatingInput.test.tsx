import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { RatingInput } from '../src/components/RatingInput'

test('renders 5 options and reports the chosen value', async () => {
  const onChange = vi.fn()
  render(<RatingInput label="Quality" name="quality" value={0} onChange={onChange} />)

  expect(screen.getAllByRole('radio')).toHaveLength(5)
  await userEvent.click(screen.getByLabelText(/Quality 4/))
  expect(onChange).toHaveBeenCalledWith(4)
})

test('shows the selected value label and an error', () => {
  render(<RatingInput label="Delivery" name="delivery" value={5} onChange={() => {}} error="Delivery rating is required" />)

  expect(screen.getByLabelText(/Delivery 5/)).toBeChecked()
  expect(screen.getByText('Outstanding')).toBeInTheDocument()
  expect(screen.getByText('Delivery rating is required')).toBeInTheDocument()
})
