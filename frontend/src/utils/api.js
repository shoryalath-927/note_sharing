const BASE = '/api'

export async function uploadNote(formData) {
  const res = await fetch(`${BASE}/notes/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
}

export async function getNotes({ subject, semester, branch, limit = 20, offset = 0 } = {}) {
  const params = new URLSearchParams()
  if (subject) params.set('subject', subject)
  if (semester) params.set('semester', semester)
  if (branch) params.set('branch', branch)
  params.set('limit', limit)
  params.set('offset', offset)
  const res = await fetch(`${BASE}/notes/?${params}`)
  return res.json()
}

export async function getNote(id) {
  const res = await fetch(`${BASE}/notes/${id}`)
  if (!res.ok) throw new Error('Note not found')
  return res.json()
}

export async function rateNote(id, stars) {
  const params = new URLSearchParams({ stars })
  const res = await fetch(`${BASE}/notes/${id}/rate?${params}`, { method: 'POST' })
  return res.json()
}

export async function getSubjects() {
  const res = await fetch(`${BASE}/notes/subjects`)
  return res.json()
}

export async function searchNotes({ q, subject, semester, limit = 10 } = {}) {
  const params = new URLSearchParams({ q })
  if (subject) params.set('subject', subject)
  if (semester) params.set('semester', semester)
  params.set('limit', limit)
  const res = await fetch(`${BASE}/search/?${params}`)
  return res.json()
}

export async function pollNoteStatus(id, maxWait = 120000) {
  const interval = 3000
  const start = Date.now()
  while (Date.now() - start < maxWait) {
    const note = await getNote(id)
    if (note.status === 'scored' || note.status === 'failed') return note
    await new Promise(r => setTimeout(r, interval))
  }
  throw new Error('Scoring timed out')
}
