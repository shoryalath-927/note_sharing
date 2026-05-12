import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getNote, rateNote } from '../utils/api.js'

function ScoreGauge({ label, value, max = 10, description }) {
  const pct = Math.round((value / max) * 100)
  const color = pct >= 70 ? 'var(--accent2)' : pct >= 50 ? 'var(--gold)' : '#e07070'
  return (
    <div style={{ padding: '0.8rem', background: 'var(--paper)', borderRadius: 'var(--radius-sm)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
        <span style={{ fontWeight: 500, fontSize: '0.9rem' }}>{label}</span>
        <span style={{ fontFamily: 'DM Serif Display', fontSize: '1rem', color }}>{value}/10</span>
      </div>
      <div style={{ height: '8px', background: 'var(--paper3)', borderRadius: '4px', overflow: 'hidden', marginBottom: '0.3rem' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '4px' }} />
      </div>
      {description && <div style={{ fontSize: '0.78rem', color: 'var(--ink3)' }}>{description}</div>}
    </div>
  )
}

function StarRater({ currentRating, count, noteId, onRated }) {
  const [hover, setHover] = useState(0)
  const [submitted, setSubmitted] = useState(false)

  async function rate(stars) {
    if (submitted) return
    setSubmitted(true)
    const res = await rateNote(noteId, stars)
    onRated(res)
  }

  return (
    <div>
      <div style={{ fontWeight: 500, marginBottom: '0.4rem', fontSize: '0.9rem' }}>Rate this note</div>
      <div style={{ display: 'flex', gap: '0.3rem', marginBottom: '0.3rem' }}>
        {[1, 2, 3, 4, 5].map(s => (
          <span
            key={s}
            style={{ fontSize: '1.6rem', cursor: submitted ? 'default' : 'pointer', color: s <= (hover || currentRating) ? '#f59e0b' : '#d1d5db', transition: 'color 0.1s' }}
            onMouseEnter={() => !submitted && setHover(s)}
            onMouseLeave={() => setHover(0)}
            onClick={() => rate(s)}
          >★</span>
        ))}
      </div>
      <div style={{ fontSize: '0.8rem', color: 'var(--ink3)' }}>
        {currentRating > 0 ? `${currentRating.toFixed(1)} / 5 from ${count} student${count !== 1 ? 's' : ''}` : 'No ratings yet'}
      </div>
      {submitted && <div style={{ fontSize: '0.82rem', color: 'var(--accent)', marginTop: '0.3rem' }}>Thanks for rating!</div>}
    </div>
  )
}

export default function NoteDetail() {
  const { id } = useParams()
  const [note, setNote] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getNote(id).then(setNote).catch(e => setError(e.message)).finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="container" style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ width: 32, height: 32, margin: '0 auto' }} /></div>
  if (error || !note) return <div className="container" style={{ padding: '3rem', textAlign: 'center', color: 'var(--danger)' }}>Note not found.</div>

  const bd = note.score_breakdown || {}
  const scoreColor = note.final_score >= 70 ? 'var(--accent)' : note.final_score >= 45 ? 'var(--gold)' : 'var(--danger)'

  return (
    <div className="container" style={{ maxWidth: 760 }}>
      {/* Back */}
      <Link to="/" style={{ fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.3rem', marginBottom: '1.5rem', color: 'var(--ink3)' }}>
        ← Back
      </Link>

      {/* Header */}
      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '1.6rem', marginBottom: '0.3rem' }}>{note.filename}</h1>
          <p style={{ color: 'var(--ink3)', fontSize: '0.9rem' }}>
            by <strong>{note.uploader_name}</strong> · {note.subject} · Semester {note.semester}
          </p>
          {note.topic_tags?.length > 0 && (
            <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginTop: '0.6rem' }}>
              {note.topic_tags.map(t => (
                <span key={t} style={{ background: 'var(--paper2)', color: 'var(--ink2)', padding: '0.2rem 0.6rem', borderRadius: '20px', fontSize: '0.75rem' }}>{t}</span>
              ))}
            </div>
          )}
        </div>

        {/* Big score */}
        <div style={{ textAlign: 'center', minWidth: 100 }}>
          <div style={{ fontFamily: 'DM Serif Display', fontSize: '3rem', color: scoreColor, lineHeight: 1 }}>{note.recommendation_score}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--ink3)' }}>Recommendation score</div>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, marginTop: '0.3rem', color: 'var(--ink2)' }}>{note.badge || '—'}</div>
        </div>
      </div>

      {/* Status badge */}
      {note.status !== 'scored' && (
        <div style={{ background: 'var(--gold-light)', color: 'var(--gold)', padding: '0.6rem 1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem', fontSize: '0.9rem' }}>
          {note.status === 'pending' ? '⏳ Awaiting scoring...' : note.status === 'scoring' ? '🔄 Scoring in progress...' : '❌ Scoring failed'}
        </div>
      )}

      {/* Summary */}
      {note.summary && (
        <div style={{ background: 'white', border: '1px solid var(--paper3)', borderRadius: 'var(--radius)', padding: '1.2rem', marginBottom: '1.5rem' }}>
          <div style={{ fontWeight: 500, marginBottom: '0.4rem', fontSize: '0.9rem', color: 'var(--ink3)' }}>AI Summary</div>
          <p style={{ color: 'var(--ink)', lineHeight: 1.6 }}>{note.summary}</p>
        </div>
      )}

      {/* Score breakdown */}
      {note.status === 'scored' && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Score Breakdown</h3>
          <div style={{ background: 'white', border: '1px solid var(--paper3)', borderRadius: 'var(--radius)', padding: '1.2rem' }}>
            {/* Formula display */}
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap' }}>
              {[
                { label: 'Handwriting', weight: '35%', value: bd.handwriting_component },
                { label: 'Content', weight: '45%', value: bd.content_component },
                { label: 'Layout', weight: '20%', value: bd.layout_component },
              ].map((item, i) => (
                <span key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  {i > 0 && <span style={{ color: 'var(--ink3)' }}>+</span>}
                  <span style={{ background: 'var(--paper2)', padding: '0.2rem 0.5rem', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
                    {item.value} × {item.weight}
                  </span>
                </span>
              ))}
              <span style={{ color: 'var(--ink3)' }}>=</span>
              <span style={{ fontFamily: 'DM Serif Display', fontSize: '1.2rem', color: scoreColor }}>{note.final_score}</span>
            </div>

            <div style={{ display: 'grid', gap: '0.6rem' }}>
              <ScoreGauge label="Handwriting clarity" value={note.handwriting_score} description={bd.gemini_notes?.handwriting} />
              <ScoreGauge label="Page layout & organization" value={note.layout_score} description={bd.gemini_notes?.layout} />
              <ScoreGauge label="Diagrams & drawings" value={note.diagram_score} description={bd.gemini_notes?.diagrams} />
              <ScoreGauge label="Content depth & completeness" value={note.content_depth_score} description={bd.groq_notes?.content} />
              <ScoreGauge label="Syllabus match" value={note.subject_match_score} description={bd.groq_notes?.subject} />
            </div>

            {bd.sources && (
              <div style={{ marginTop: '0.8rem', fontSize: '0.75rem', color: 'var(--ink3)', display: 'flex', gap: '0.8rem' }}>
                <span>Vision: {bd.sources.vision || 'N/A'}</span>
                <span>Content: {bd.sources.content || 'N/A'}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Rating */}
      <div style={{ background: 'white', border: '1px solid var(--paper3)', borderRadius: 'var(--radius)', padding: '1.2rem', marginBottom: '1.5rem' }}>
        <StarRater
          currentRating={note.star_rating}
          count={note.rating_count}
          noteId={note.id}
          onRated={res => setNote(n => ({ ...n, star_rating: res.new_rating, rating_count: res.rating_count, recommendation_score: res.recommendation_score }))}
        />
      </div>

      {/* View PDF link */}
      <div>
        <a
          href={`http://localhost:8000/uploads/${note.saved_filename}`}
          target="_blank"
          rel="noreferrer"
          className="btn btn-outline"
        >
          📄 View original PDF
        </a>
      </div>
    </div>
  )
}
