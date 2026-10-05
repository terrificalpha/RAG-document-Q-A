import React, { useEffect, useRef } from 'react'

export default function ChatWindow({ messages }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (!messages || messages.length === 0) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '280px', color: 'var(--text-muted)', fontSize: '0.95rem' }}>
        No messages yet. Ask a question to get started!
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '8px 4px', maxHeight: '450px', overflowY: 'auto' }}>
      {messages.map((msg, index) => {
        const isUser = msg.role === 'user'
        const isError = msg.role === 'error'

        return (
          <div
            key={index}
            style={{
              display: 'flex',
              justifyContent: isUser ? 'flex-end' : 'flex-start',
              width: '100%',
            }}
          >
            <div
              className={`animate-message ${isUser ? 'bubble-user' : isError ? 'bubble-error' : 'bubble-assistant'}`}
              style={{
                maxWidth: '80%',
                padding: '14px 18px',
                lineHeight: '1.55',
                fontSize: '0.96rem',
                color: '#ffffff',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              <div>{msg.content}</div>

              {/* Source citations rendering for Assistant responses */}
              {msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.15)', fontSize: '0.8rem', opacity: 0.85 }}>
                  <strong style={{ color: 'var(--neon-cyan)' }}>Sources: </strong>
                  {msg.sources.join(', ')}
                </div>
              )}
            </div>
          </div>
        )
      })}
      <div ref={bottomRef} />
    </div>
  )
}