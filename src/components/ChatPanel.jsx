import { useEffect, useRef, useState } from 'react'
import { ArrowUp, Bot, Scale, UserRound, X } from 'lucide-react'

export default function ChatPanel({ contractId, filename, onClose }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: `Ask me about risks, clauses, legal terms, or negotiation points in ${filename}.`,
    },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const listRef = useRef(null)

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  async function send(event) {
    event.preventDefault()
    const question = input.trim()
    if (!question || sending) return
    setInput('')
    setMessages((current) => [...current, { role: 'user', text: question }])
    setSending(true)
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contract_id: contractId, message: question }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'The assistant could not respond.')
      setMessages((current) => [
        ...current,
        { role: 'assistant', text: data.answer, sources: data.sources, refused: data.refused },
      ])
    } catch (error) {
      setMessages((current) => [...current, { role: 'assistant', text: error.message, error: true }])
    } finally {
      setSending(false)
    }
  }

  return (
    <aside className="chat-panel" aria-label="Contract assistant">
      <header className="chat-header">
        <div className="chat-avatar"><Scale size={19} /></div>
        <div>
          <h2>Contract assistant</h2>
          <p><span className="live-dot" /> Grounded in this contract</p>
        </div>
        {onClose && <button className="chat-close" onClick={onClose} aria-label="Close contract assistant"><X size={19} /></button>}
      </header>

      <div className="chat-messages" ref={listRef} aria-live="polite">
        {messages.map((message, index) => (
          <div className={`message ${message.role} ${message.error ? 'error' : ''}`} key={`${message.role}-${index}`}>
            <span className="message-icon">
              {message.role === 'assistant' ? <Bot size={16} /> : <UserRound size={16} />}
            </span>
            <div>
              <p>{message.text}</p>
              {message.sources?.length > 0 && (
                <div className="source-list">
                  {message.sources.slice(0, 3).map((source) => <span key={source}>{source}</span>)}
                </div>
              )}
            </div>
          </div>
        ))}
        {sending && <div className="message assistant"><span className="message-icon"><Bot size={16} /></span><div className="typing"><i /><i /><i /></div></div>}
      </div>

      <form className="chat-form" onSubmit={send}>
        <label htmlFor="chat-input" className="sr-only">Ask about this contract</label>
        <textarea
          id="chat-input"
          rows="2"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) send(event)
          }}
          placeholder="Ask about a clause or legal term…"
        />
        <button type="submit" aria-label="Send question" disabled={!input.trim() || sending}><ArrowUp size={18} /></button>
      </form>
      <p className="chat-scope">Contract questions only · Not legal advice</p>
    </aside>
  )
}
