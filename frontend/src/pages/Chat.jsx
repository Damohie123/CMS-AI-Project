import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import './Chat.css'

const QUICK_COMMANDS = [
  { label: 'مساعدة', message: 'مساعدة' },
  { label: 'توليد مقال', message: 'اكتب مقالاً عن ' },
  { label: 'تلخيص', message: 'لخص: ' },
  { label: 'حزمة عربية', message: 'حزمة محتوى عن ' },
  { label: 'SEO', message: 'حسّن SEO: ' },
]

export default function Chat() {
  const [sessions, setSessions] = useState([])
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [speakingId, setSpeakingId] = useState(null)
  const bottomRef = useRef(null)

  const loadSessions = useCallback(async () => {
    const list = await api.chat.sessions()
    setSessions(list)
    return list
  }, [])

  const loadSession = async (id) => {
    const s = await api.chat.getSession(id)
    setActiveId(id)
    setMessages(s.messages || [])
  }

  const startNewChat = async () => {
    setError('')
    const s = await api.chat.createSession()
    await loadSessions()
    setActiveId(s.id)
    setMessages(s.messages || [])
  }

  useEffect(() => {
    loadSessions()
      .then((list) => {
        if (list.length > 0) loadSession(list[0].id)
        else startNewChat()
      })
      .catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const playTts = async (msg, speakText) => {
    const text = speakText || msg.content?.replace(/\*+/g, '').slice(0, 500)
    if (!text?.trim()) return
    setSpeakingId(msg.id)
    setError('')
    try {
      const audio = await api.tts(text)
      const src = audio.audio_base64
        ? `data:audio/mp3;base64,${audio.audio_base64}`
        : audio.url
      const el = new Audio(src)
      await el.play()
    } catch (e) {
      setError(e.message)
    } finally {
      setSpeakingId(null)
    }
  }

  const send = async () => {
    const text = input.trim()
    if (!text || !activeId || loading) return
    setInput('')
    setError('')
    setLoading(true)
    const optimistic = {
      id: `tmp-${Date.now()}`,
      role: 'user',
      content: text,
    }
    setMessages((m) => [...m, optimistic])
    try {
      const res = await api.chat.sendMessage(activeId, text)
      setMessages((m) => [
        ...m.filter((x) => x.id !== optimistic.id),
        res.user_message,
        { ...res.assistant_message, _speakText: res.speak_text },
      ])
      if (res.intent === 'tts' && res.speak_text) {
        playTts({ id: res.assistant_message.id }, res.speak_text)
      }
      await loadSessions()
    } catch (e) {
      setMessages((m) => m.filter((x) => x.id !== optimistic.id))
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="chat-page">
      <header className="page-header">
        <h1>المساعد الذكي</h1>
        <p>Chatbot متصل بتوليد المحتوى، التلخيص، SEO، وتحويل النص إلى صوت</p>
      </header>
      {error && <div className="error-msg">{error}</div>}

      <div className="chat-layout">
        <aside className="chat-sessions card">
          <button type="button" className="btn-primary chat-new-btn" onClick={startNewChat}>
            + محادثة جديدة
          </button>
          <ul>
            {sessions.map((s) => (
              <li key={s.id}>
                <button
                  type="button"
                  className={activeId === s.id ? 'session-item active' : 'session-item'}
                  onClick={() => loadSession(s.id)}
                >
                  <span className="session-title">{s.title}</span>
                  <span className="session-meta">{s.message_count} رسالة</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <div className="chat-main card">
          <div className="chat-messages">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-bubble ${msg.role === 'user' ? 'user' : 'assistant'}`}
              >
                <div className="bubble-meta">
                  <span>{msg.role === 'user' ? 'أنت' : 'المساعد'}</span>
                  {msg.intent && msg.role === 'assistant' && (
                    <span className="intent-tag">{msg.intent}</span>
                  )}
                  {msg.role === 'assistant' && (
                    <button
                      type="button"
                      className="tts-btn"
                      title="استماع"
                      disabled={speakingId === msg.id}
                      onClick={() => playTts(msg, msg._speakText)}
                    >
                      {speakingId === msg.id ? '⏳' : '🔊'}
                    </button>
                  )}
                </div>
                <div className="bubble-body">{renderContent(msg.content)}</div>
              </div>
            ))}
            {loading && (
              <div className="chat-bubble assistant">
                <div className="bubble-body typing">يكتب...</div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="quick-commands">
            {QUICK_COMMANDS.map((c) => (
              <button
                key={c.label}
                type="button"
                className="btn-ghost quick-cmd"
                onClick={() => setInput(c.message)}
              >
                {c.label}
              </button>
            ))}
          </div>

          <div className="chat-input-row">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="اكتب رسالتك... (Enter للإرسال)"
              rows={2}
            />
            <button type="button" className="btn-primary" onClick={send} disabled={loading || !input.trim()}>
              إرسال
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function renderContent(text) {
  if (!text) return null
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>
    }
    return <span key={i}>{part}</span>
  })
}
