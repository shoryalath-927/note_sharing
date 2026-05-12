import { Link } from 'react-router-dom'

const BADGE_CLASS = {
  'Top Pick': 'badge-top',
  'Highly Rated': 'badge-high',
  'Good': 'badge-good',
  'Average': 'badge-avg',
  'Needs Review': 'badge-avg',
}

function ScoreBar({ label, value, max = 10 }) {
  const pct = Math.round((value / max) * 100)
  const color = pct >= 70 ? 'var(--accent2)' : pct >= 50 ? 'var(--gold)' : '#e07070'
  return (
    <div style={{ marginBottom: '0.35rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--ink3)', marginBottom: '0.15rem' }}>
        <span>{label}</span><span>{value}/10</span>
      </div>
      <div style={{ height: '5px', background: 'var(--paper3)', borderRadius: '3px', overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '3px', transition: 'width 0.5s' }} />
      </div>
    </div>
  )
}

function Stars({ rating, count }) {
  return (
    <span style={{ fontSize: '0.8rem', color: 'var(--ink3)' }}>
      {'★'.repeat(Math.round(rating))}{'☆'.repeat(5 - Math.round(rating))} {rating > 0 ? `${rating.toFixed(1)} (${count})` : 'No ratings yet'}
    </span>
  )
}

export default function NoteCard({ note }) {
  const score = note.recommendation_score || 0
  const scoreClass = score >= 70 ? 'score-high' : score >= 45 ? 'score-mid' : 'score-low'
  const badge = note.badge || 'Average'

  return (
    <Link to={`/note/${note.id}`} style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
      <div style={{
        background: 'white',
        border: '1px solid var(--paper3)',
        borderRadius: 'var(--radius)',
        padding: '1.2rem',
        transition: 'all 0.2s',
        cursor: 'pointer',
      }}
        onMouseEnter={e => { e.currentTarget.style.boxShadow = 'var(--shadow-lg)'; e.currentTarget.style.borderColor = 'var(--accent-light)' }}
        onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.borderColor = 'var(--paper3)' }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.8rem' }}>
          <div style={{ flex: 1, marginRight: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', marginBottom: '0.3rem', flexWrap: 'wrap' }}>
              <span className={`badge ${BADGE_CLASS[badge] || 'badge-avg'}`}>{badge}</span>
              {note.rank && <span style={{ fontSize: '0.75rem', color: 'var(--ink3)' }}>#{note.rank}</span>}
            </div>
            <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '0.2rem', color: 'var(--ink)' }}>{note.filename}</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--ink3)' }}>by {note.uploader_name} · Sem {note.semester}</div>
          </div>
          <div className={`score-ring ${scoreClass}`} title="Recommendation score">{score}</div>
        </div>

        {/* Summary */}
        {note.summary && (
          <p style={{ fontSize: '0.83rem', color: 'var(--ink2)', marginBottom: '0.8rem', lineHeight: 1.5 }}>
            {note.summary.slice(0, 120)}{note.summary.length > 120 ? '...' : ''}
          </p>
        )}

        {/* Score bars */}
        <div style={{ marginBottom: '0.8rem' }}>
          <ScoreBar label="Handwriting" value={note.handwriting_score} />
          <ScoreBar label="Content" value={note.content_depth_score} />
          <ScoreBar label="Layout" value={note.layout_score} />
        </div>

        {/* Tags */}
        {note.topic_tags?.length > 0 && (
          <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap', marginBottom: '0.6rem' }}>
            {note.topic_tags.slice(0, 4).map(tag => (
              <span key={tag} style={{ background: 'var(--paper2)', color: 'var(--ink2)', padding: '0.15rem 0.5rem', borderRadius: '20px', fontSize: '0.72rem' }}>
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Footer */}
        <div style={{ borderTop: '1px solid var(--paper3)', paddingTop: '0.6rem', marginTop: '0.2rem' }}>
          <Stars rating={note.star_rating} count={note.rating_count} />
        </div>
      </div>
    </Link>
  )
}
