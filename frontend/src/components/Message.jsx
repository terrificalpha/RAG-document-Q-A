export default function Message({ role, content, sources }) {
  return (
    <div className={`message ${role}`}>
      <div>{content}</div>
      {sources && sources.length > 0 && (
        <div className="sources">Sources: {sources.join(', ')}</div>
      )}
    </div>
  )
}
