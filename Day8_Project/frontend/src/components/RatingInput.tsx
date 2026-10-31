interface Props {
  label: string
  name: string
  value: number
  onChange: (value: number) => void
  error?: string
}

const LABELS = ['Poor', 'Below expectations', 'Meets expectations', 'Exceeds expectations', 'Outstanding']

/** A 1–5 rating picker rendered as a radio group of numbered buttons. */
export function RatingInput({ label, name, value, onChange, error }: Props) {
  return (
    <fieldset className="rating-input" aria-invalid={!!error}>
      <legend>
        {label} <span className="required">*</span>
      </legend>
      <div className="rating-options" role="radiogroup" aria-label={label}>
        {[1, 2, 3, 4, 5].map((n) => (
          <label key={n} className={`rating-option ${value === n ? 'selected' : ''}`} title={LABELS[n - 1]}>
            <input
              type="radio"
              name={name}
              value={n}
              checked={value === n}
              onChange={() => onChange(n)}
              aria-label={`${label} ${n} - ${LABELS[n - 1]}`}
            />
            {n}
          </label>
        ))}
      </div>
      <span className="hint">{value ? LABELS[value - 1] : 'Select 1 (poor) to 5 (outstanding)'}</span>
      {error && <span className="field-error">{error}</span>}
    </fieldset>
  )
}
