import { useRef, useState } from 'react'

export default function UploadPanel({ apiBase, documents, onUploaded }) {
  const fileInput = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  async function handleFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${apiBase}/upload`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `Upload failed (${res.status})`)
      }
      const data = await res.json()
      onUploaded(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      if (fileInput.current) fileInput.current.value = ''
    }
  }

  return (
    <div className="panel">
      <div className="upload-row">
        <input
          ref={fileInput}
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleFileChange}
          disabled={uploading}
        />
        {uploading && <span className="badge">Indexing…</span>}
        {documents.map((d) => (
          <span key={d} className="doc-pill">{d}</span>
        ))}
      </div>
      {error && <div className="sources" style={{ color: 'var(--danger)', marginTop: '0.5rem' }}>{error}</div>}
    </div>
  )
}
