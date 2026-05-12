import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function SearchBar({ compact = false }) {
  const [q, setQ] = useState('')
  const navigate = useNavigate()

  function handleSearch(e) {
    e.preventDefault()
    if (q.trim()) navigate(`/?q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem' }}>
      <input
        type="text"
        value={q}
        onChange={e => setQ(e.target.value)}
        placeholder={compact ? 'Search notes by topic...' : 'Search by topic, subject, or keyword...'}
        style={{ flex: 1, minWidth: 0 }}
      />
      <button type="submit" className="btn btn-primary" style={{ whiteSpace: 'nowrap' }}>
        🔍 Search
      </button>
    </form>
  )
}
