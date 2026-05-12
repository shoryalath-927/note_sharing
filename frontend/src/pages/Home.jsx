import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getSubjects, getNotes, searchNotes } from '../utils/api.js'
import NoteCard from '../components/NoteCard.jsx'

const SUBJECT_ICONS = {
  'Mathematics': '∑', 'Computer Science': '💻', 'Electronics': '⚡',
  'Electrical Engineering': '🔌', 'Data Structures': '🌳', 'Algorithms': '⚙️',
  'Operating Systems': '🖥️', 'Database Management': '🗄️',
  'Computer Networks': '🌐', 'Machine Learning': '🤖',
  'Physics': '⚛️', 'Chemistry': '🧪', 'Mechanical Engineering': '🔧',
}

export default function Home() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q')
  const [subjects, setSubjects] = useState([])
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        if (query) {
          const res = await searchNotes({ q: query, limit: 20 })
          setNotes(res.results || [])
          setSubjects([])
        } else {
          const [subRes, notesRes] = await Promise.all([getSubjects(), getNotes({ limit: 6 })])
          setSubjects(subRes.subjects || [])
          setNotes(notesRes.notes || [])
        }
      } catch (e) {
        console.error(e)
      }
      setLoading(false)
    }
    load()
  }, [query])

  if (loading) return (
    <div className="container" style={{ textAlign: 'center', padding: '4rem 0' }}>
      <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto 1rem' }} />
      <p style={{ color: 'var(--ink3)' }}>Loading...</p>
    </div>
  )

  return (
    <div className="container">
      {/* Hero */}
      {!query && (
        <div style={{ textAlign: 'center', padding: '2.5rem 0 2rem' }}>
          <h1 style={{ marginBottom: '0.5rem' }}>
            Find the <em>Best</em> Handwritten Notes
          </h1>
          <p style={{ color: 'var(--ink3)', fontSize: '1.05rem', marginBottom: '2rem' }}>
            AI-scored · Peer-rated · BTech subjects
          </p>
        </div>
      )}

      {/* Search results */}
      {query && (
        <div>
          <h2 style={{ marginBottom: '1.5rem' }}>Results for "{query}" <span style={{ fontSize: '1rem', color: 'var(--ink3)', fontFamily: 'DM Sans' }}>({notes.length} notes)</span></h2>
          {notes.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--ink3)' }}>
              <p>No notes found. <Link to="/upload">Upload the first one!</Link></p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.2rem' }}>
              {notes.map(n => <NoteCard key={n.id} note={n} />)}
            </div>
          )}
        </div>
      )}

      {/* Subject grid */}
      {!query && subjects.length > 0 && (
        <section style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ marginBottom: '1.2rem' }}>Browse by Subject</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '0.8rem' }}>
            {subjects.map(s => (
              <Link key={s.subject} to={`/subject/${encodeURIComponent(s.subject)}`} style={{ textDecoration: 'none' }}>
                <div style={{
                  background: 'white', border: '1px solid var(--paper3)',
                  borderRadius: 'var(--radius)', padding: '1rem', textAlign: 'center',
                  transition: 'all 0.15s',
                }}
                  onMouseEnter={e => { e.currentTarget.style.boxShadow = 'var(--shadow)'; e.currentTarget.style.borderColor = 'var(--accent-light)' }}
                  onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.borderColor = 'var(--paper3)' }}
                >
                  <div style={{ fontSize: '1.8rem', marginBottom: '0.4rem' }}>
                    {SUBJECT_ICONS[s.subject] || '📄'}
                  </div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--ink)', marginBottom: '0.2rem' }}>{s.subject}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--ink3)' }}>{s.note_count} notes · Top {s.top_score}</div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Top notes */}
      {!query && (
        <section>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
            <h2>Top Rated Notes</h2>
          </div>
          {notes.length === 0 ? (
            <div style={{
              textAlign: 'center', padding: '3rem',
              background: 'white', borderRadius: 'var(--radius)',
              border: '1px dashed var(--paper3)', color: 'var(--ink3)'
            }}>
              <p style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📝</p>
              <p>No notes yet. <Link to="/upload">Be the first to upload!</Link></p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.2rem' }}>
              {notes.map(n => <NoteCard key={n.id} note={n} />)}
            </div>
          )}
        </section>
      )}
    </div>
  )
}
