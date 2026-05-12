import { Link, useLocation } from 'react-router-dom'
import SearchBar from './SearchBar.jsx'

export default function Navbar() {
  const loc = useLocation()
  return (
    <nav style={{
      background: 'white',
      borderBottom: '1px solid var(--paper3)',
      padding: '0.8rem 0',
      position: 'sticky', top: 0, zIndex: 100,
      boxShadow: 'var(--shadow)'
    }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <Link to="/" style={{ fontFamily: 'DM Serif Display', fontSize: '1.3rem', color: 'var(--ink)', whiteSpace: 'nowrap' }}>
          📚 NoteShare <span style={{ color: 'var(--accent)' }}>AI</span>
        </Link>
        <div style={{ flex: 1 }}>
          <SearchBar compact />
        </div>
        <Link
          to="/upload"
          className="btn btn-primary"
          style={{ whiteSpace: 'nowrap', textDecoration: 'none' }}
        >
          + Upload Note
        </Link>
      </div>
    </nav>
  )
}
