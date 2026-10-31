import { NavLink } from 'react-router'

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">★</span>
        <span>Performance Reviews</span>
      </div>
      <nav aria-label="Main">
        <NavLink to="/submit" className="nav-link">
          Submit reviews
        </NavLink>
        <NavLink to="/reviews" className="nav-link">
          My reviews
        </NavLink>
      </nav>
      <p className="sidebar-footer">Manager view</p>
    </aside>
  )
}
