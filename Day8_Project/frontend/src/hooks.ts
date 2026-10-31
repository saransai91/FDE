import { useEffect, useState } from 'react'
import { api } from './api/client'
import type { Employee, ReviewPeriod } from './types'

/** Loads the two master lists (employees, review periods) used by the dropdowns. */
export function useMasterData() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [periods, setPeriods] = useState<ReviewPeriod[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    Promise.all([api.listEmployees(), api.listReviewPeriods()])
      .then(([e, p]) => {
        if (!active) return
        setEmployees(e)
        setPeriods(p)
      })
      .catch((err: Error) => active && setError(err.message))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [])

  return { employees, periods, error, loading }
}
