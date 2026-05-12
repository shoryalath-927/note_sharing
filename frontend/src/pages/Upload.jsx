import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadNote, pollNoteStatus } from '../utils/api.js'

const SUBJECTS = [
  'Mathematics', 'Computer Science', 'Electronics', 'Electrical Engineering',
  'Mechanical Engineering', 'Civil Engineering', 'Physics', 'Chemistry',
  'Data Structures', 'Algorithms', 'Operating Systems', 'Database Management',
  'Computer Networks', 'Software Engineering', 'Machine Learning',
  'Digital Electronics', 'Signals and Systems', 'Control Systems',
]

const SEMESTERS = [1, 2, 3, 4, 5, 6, 7, 8]

const STEPS = [
  { id: 'extract', label: 'Extracting text from PDF', icon: '📄' },
  { id: 'gemini', label: 'Scoring handwriting & layout (Gemini Vision)', icon: '✍️' },
  { id: 'groq', label: 'Scoring content depth (Groq AI)', icon: '🧠' },
  { id: 'embed', label: 'Generating search embeddings', icon: '🔍' },
  { id: 'done', label: 'Scoring complete!', icon: '✅' },
]

export default function Upload() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ uploader_name: '', subject: '', semester: '3', branch: 'BTech' })
  const [file, setFile] = useState(null)
  const [phase, setPhase] = useState('form') // form | uploading | scoring | done | error
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [noteId, setNoteId] = useState(null)

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

async function handleSubmit(e) {
    e.preventDefault()
    if (!file) { setError('Please select a PDF file'); return }
    if (!form.uploader_name.trim()) { setError('Please enter your name'); return }
    if (!form.subject) { setError('Please select a subject'); return }

    // PERFORM SIZE CHECK BEFORE CHANGING PHASE
    const MAX_SIZE_MB = 100; 
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

    if (file.size > MAX_SIZE_BYTES) {
      setError(`File too large. Max size is ${MAX_SIZE_MB}MB`);
      return; // Stops here, phase is still 'form', button is enabled
    }

    setError('')
    setPhase('uploading') // Only change phase once validation passes

    const fd = new FormData()
    fd.append('file', file)
    fd.append('uploader_name', form.uploader_name)
    fd.append('subject', form.subject)
    fd.append('semester', form.semester)
    fd.append('branch', form.branch)

    try {
      const res = await uploadNote(fd)
      setNoteId(res.note_id)
      setPhase('scoring')

      // Poll for completion
      let step = 0
      const pollInterval = setInterval(async () => {
        step = Math.min(step + 1, 3)
        setProgress(step)
      }, 5000)

      const scored = await pollNoteStatus(res.note_id)
      clearInterval(pollInterval)

      if (scored.status === 'failed') {
        setPhase('error')
        setError('Scoring failed. The note was saved but could not be scored.')
      } else {
        setProgress(4)
        setPhase('done')
        setTimeout(() => navigate(`/note/${res.note_id}`), 1500)
      }
    } catch (err) {
      setPhase('error')
      setError(err.message || 'Upload failed')
    }
  }

  if (phase === 'scoring' || phase === 'done') {
    return (
      <div className="container" style={{ maxWidth: 540, padding: '3rem 1.5rem' }}>
        <h2 style={{ marginBottom: '0.5rem' }}>Analyzing your notes</h2>
        <p style={{ color: 'var(--ink3)', marginBottom: '2rem' }}>This takes 20–60 seconds depending on PDF size</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {STEPS.map((step, i) => {
            const done = i <= progress
            const active = i === progress && phase !== 'done'
            return (
              <div key={step.id} style={{
                display: 'flex', alignItems: 'center', gap: '0.8rem',
                padding: '0.8rem 1rem',
                background: done ? 'var(--accent-light)' : 'white',
                border: `1px solid ${done ? 'var(--accent2)' : 'var(--paper3)'}`,
                borderRadius: 'var(--radius)',
                opacity: i > progress ? 0.4 : 1,
                transition: 'all 0.3s',
              }}>
                <span style={{ fontSize: '1.2rem' }}>{step.icon}</span>
                <span style={{ flex: 1, fontSize: '0.9rem', color: done ? 'var(--accent)' : 'var(--ink2)' }}>
                  {step.label}
                </span>
                {active && <div className="spinner" />}
                {done && i < progress && <span style={{ color: 'var(--accent)' }}>✓</span>}
              </div>
            )
          })}
        </div>
        {phase === 'done' && (
          <div style={{ textAlign: 'center', marginTop: '1.5rem', color: 'var(--accent)' }}>
            Redirecting to your note...
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="container" style={{ maxWidth: 540 }}>
      <h1 style={{ marginBottom: '0.4rem' }}>Share your notes</h1>
      <p style={{ color: 'var(--ink3)', marginBottom: '2rem' }}>
        Upload a handwritten PDF. Our AI scores it in under a minute.
      </p>

      {error && (
        <div style={{ background: '#fee2e2', color: 'var(--danger)', padding: '0.7rem 1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1.2rem', fontSize: '0.9rem' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* File drop */}
        <div
          style={{
            border: `2px dashed ${file ? 'var(--accent2)' : 'var(--paper3)'}`,
            borderRadius: 'var(--radius)', padding: '2rem', textAlign: 'center',
            background: file ? 'var(--accent-light)' : 'white', cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onClick={() => document.getElementById('pdf-input').click()}
          onDragOver={e => e.preventDefault()}
          onDrop={e => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f?.type === 'application/pdf') setFile(f) }}
        >
          <input id="pdf-input" type="file" accept=".pdf" style={{ display: 'none' }}
            onChange={e => setFile(e.target.files[0])} />
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{file ? '📄' : '⬆️'}</div>
          {file ? (
            <div>
              <div style={{ fontWeight: 600, color: 'var(--accent)' }}>{file.name}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--ink3)' }}>{(file.size / 1024 / 1024).toFixed(1)} MB</div>
            </div>
          ) : (
            <div>
              <div style={{ fontWeight: 500 }}>Click to select or drag & drop</div>
              <div style={{ fontSize: '0.82rem', color: 'var(--ink3)' }}>PDF only · max 100MB</div>
            </div>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.3rem' }}>Your name</label>
            <input name="uploader_name" value={form.uploader_name} onChange={handleChange} placeholder="e.g. Risha Sharma" style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.3rem' }}>Semester</label>
            <select name="semester" value={form.semester} onChange={handleChange} style={{ width: '100%' }}>
              {SEMESTERS.map(s => <option key={s} value={s}>Semester {s}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.3rem' }}>Subject</label>
          <select name="subject" value={form.subject} onChange={handleChange} style={{ width: '100%' }}>
            <option value="">Select subject...</option>
            {SUBJECTS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div style={{ background: 'var(--paper2)', borderRadius: 'var(--radius)', padding: '1rem', fontSize: '0.84rem', color: 'var(--ink2)' }}>
          <strong>What gets scored:</strong> Handwriting clarity (35%) · Content depth & syllabus match (45%) · Page layout & diagrams (20%)
        </div>

        <button type="submit" className="btn btn-primary" disabled={phase === 'uploading'} style={{ width: '100%', padding: '0.8rem', fontSize: '1rem', justifyContent: 'center' }}>
          {phase === 'uploading' ? <><div className="spinner" style={{ width: 16, height: 16 }} /> Uploading...</> : '🚀 Upload & Score'}
        </button>
      </form>
    </div>
  )
}
