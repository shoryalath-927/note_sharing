import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getNotes } from '../utils/api.js'
import NoteCard from '../components/NoteCard.jsx'

export default function Subject() {
  const { subject } = useParams()
  const decoded = decodeURIComponent(subject)
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [semester, setSemester] = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      const res = await getNotes({ subject: decoded, semester: semester || undefined, limit: 30 })
      setNotes(res.notes || [])
      setLoading(false)
    }
    load()
  }, [decoded, semester])

  return (
    <div className="container">
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ marginBottom: '0.3rem' }}>{decoded}</h1>
        <p style={{ color: 'var(--ink3)' }}>{notes.length} notes · ranked by AI score + peer rating</p>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.9rem', color: 'var(--ink3)', alignSelf: 'center' }}>Filter:</span>
        {['', '1', '2', '3', '4', '5', '6', '7', '8'].map(s => (
          <button key={s} className={`btn ${semester === s ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setSemester(s)} style={{ padding: '0.35rem 0.8rem', fontSize: '0.82rem' }}>
            {s ? `Sem ${s}` : 'All'}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}><div className="spinner" style={{ width: 28, height: 28, margin: '0 auto' }} /></div>
      ) : notes.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--ink3)' }}>
          No notes yet for this subject/semester.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.2rem' }}>
          {notes.map(n => <NoteCard key={n.id} note={n} />)}
        </div>
      )}
    </div>
  )
}
