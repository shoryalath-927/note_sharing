import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Home from './pages/Home.jsx'
import Upload from './pages/Upload.jsx'
import Subject from './pages/Subject.jsx'
import NoteDetail from './pages/NoteDetail.jsx'

export default function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, padding: '2rem 0' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/subject/:subject" element={<Subject />} />
          <Route path="/note/:id" element={<NoteDetail />} />
        </Routes>
      </main>
      <footer style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--ink3)', fontSize: '0.85rem', borderTop: '1px solid var(--paper3)' }}>
        NoteShare AI — BTech Note Sharing Platform
      </footer>
    </div>
  )
}
