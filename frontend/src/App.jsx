import { useState } from 'react'
import ChatWindow from './components/ChatWindow.jsx'
import UploadPanel from './components/UploadPanel.jsx'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

export default function App() {
  const [documents, setDocuments] = useState([])
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [asking, setAsking] = useState(false)
  const [isPressed, setIsPressed] = useState(false)

  function handleUploaded(data) {
    setDocuments((prev) =>
      prev.includes(data.filename) ? prev : [...prev, data.filename]
    )
  }

  async function handleAsk(e) {
    e.preventDefault()
    const q = question.trim()
    if (!q || asking) return

    // Trigger rounded-square button compression effect
    setIsPressed(true)
    setTimeout(() => setIsPressed(false), 200)

    setMessages((prev) => [...prev, { role: 'user', content: q }])
    setQuestion('')
    setAsking(true)

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `Request failed (${res.status})`)
      }

      const data = await res.json()
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'error', content: err.message },
      ])
    } finally {
      setAsking(false)
    }
  }

  return (
    <div className="app-container" style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 20px' }}>
      {/* Header */}
      <header className="app-header glass-panel" style={{ padding: '24px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="gradient-text" style={{ margin: 0, fontSize: '2rem', fontWeight: 700 }}>RAG Document Q&amp;A</h1>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginTop: '4px' }}>
            Powered locally with Ollama &amp; HuggingFace Embeddings
          </div>
        </div>
        <span className="neon-pill">
          {documents.length} doc{documents.length === 1 ? '' : 's'} indexed
        </span>
      </header>

      {/* Upload Panel */}
      <section className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
        <UploadPanel apiBase={API_BASE} documents={documents} onUploaded={handleUploaded} />
      </section>

      {/* Chat Container */}
      <section className="glass-panel" style={{ padding: '20px', marginBottom: '24px', minHeight: '380px', display: 'flex', flexDirection: 'column' }}>
        <ChatWindow messages={messages} />

        {/* Jiggly Winking Glass Loader Bubble */}
        {asking && (
          <div className="jiggle-bubble">
            <span className="winking-dot" />
            <span style={{ fontSize: '0.88rem', fontWeight: 500, color: '#38bdf8', letterSpacing: '0.3px' }}>
              Searching documents &amp; thinking…
            </span>
          </div>
        )}
      </section>

      {/* Composer Input Form */}
      <form className="composer glass-panel" onSubmit={handleAsk} style={{ display: 'flex', gap: '12px', padding: '12px' }}>
        <input
          type="text"
          placeholder={documents.length ? 'Ask a question about your documents…' : 'Upload a document first'}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={documents.length === 0 || asking}
          style={{
            flex: 1,
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid var(--border-neon)',
            borderRadius: '10px',
            padding: '12px 16px',
            color: 'var(--text-primary)',
            fontSize: '1rem',
            outline: 'none',
            transition: 'all 0.2s ease',
          }}
        />
        <button
          type="submit"
          className={`square-ask-button ${isPressed ? 'neon-button-pressed' : ''}`}
          disabled={documents.length === 0 || asking || !question.trim()}
        >
          {asking ? 'Searching…' : 'Ask'}
        </button>
      </form>
    </div>
  )
}