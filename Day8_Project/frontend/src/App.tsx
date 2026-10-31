import { Navigate, Route, Routes } from 'react-router'
import { Sidebar } from './components/Sidebar'
import { MyReviewsPage } from './pages/MyReviewsPage'
import { ReviewDetailPage } from './pages/ReviewDetailPage'
import { SubmitReviewPage } from './pages/SubmitReviewPage'

export function App() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <Routes>
          <Route path="/" element={<Navigate to="/reviews" replace />} />
          <Route path="/submit" element={<SubmitReviewPage />} />
          <Route path="/reviews" element={<MyReviewsPage />} />
          <Route path="/reviews/:reviewId" element={<ReviewDetailPage />} />
          <Route path="*" element={<p>Page not found.</p>} />
        </Routes>
      </main>
    </div>
  )
}
