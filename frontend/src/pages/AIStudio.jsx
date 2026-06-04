import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function AIStudio() {
  const navigate = useNavigate()
  const [topic, setTopic] = useState('')
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async (fn) => {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await fn()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const saveAsArticle = async () => {
    if (!result) return
    const content =
      result.content ||
      [result.introduction, result.body, result.conclusion].filter(Boolean).join('\n\n') ||
      JSON.stringify(result, null, 2)
    const title = result.title || result.topic || topic || 'مقال من AI'
    try {
      const a = await api.createArticle({
        title,
        content,
        summary: result.summary,
        keywords: (result.keywords || []).join(', '),
        status: 'draft',
      })
      navigate(`/articles/${a.id}`)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <>
      <header className="page-header">
        <h1>استوديو الذكاء الاصطناعي</h1>
        <p>توليد المحتوى العربي، SEO، التلخيص، والمزيد</p>
      </header>
      {error && <div className="error-msg">{error}</div>}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>مولد المحتوى العربي الذكي</h2>
        <div className="form-group">
          <label>موضوع المقال</label>
          <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="مثال: الذكاء الاصطناعي في التعليم" />
        </div>
        <div className="actions">
          <button
            type="button"
            className="btn-primary"
            disabled={loading || !topic.trim()}
            onClick={() => run(() => api.ai.arabicPackage(topic))}
          >
            توليد حزمة كاملة (مقدمة + خاتمة + SEO + هاشتاقات)
          </button>
          <button
            type="button"
            className="btn-ghost"
            disabled={loading || !topic.trim()}
            onClick={() => run(() => api.ai.generate({ topic }))}
          >
            توليد مقال
          </button>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>أدوات على نص</h2>
        <div className="form-group">
          <label>النص</label>
          <textarea value={text} onChange={(e) => setText(e.target.value)} rows={6} />
        </div>
        <div className="actions">
          <button type="button" className="btn-ghost" disabled={loading || !text.trim()} onClick={() => run(() => api.ai.summarize(text))}>تلخيص</button>
          <button type="button" className="btn-ghost" disabled={loading || !text.trim()} onClick={() => run(() => api.ai.titles(text))}>عناوين</button>
          <button type="button" className="btn-ghost" disabled={loading || !text.trim()} onClick={() => run(() => api.ai.seo('', text))}>SEO</button>
          <button type="button" className="btn-ghost" disabled={loading || !text.trim()} onClick={() => run(() => api.ai.keywords(text))}>كلمات مفتاحية</button>
          <button type="button" className="btn-ghost" disabled={loading || !text.trim()} onClick={() => run(() => api.ai.grammar(text))}>تصحيح</button>
        </div>
      </div>

      {loading && <p style={{ color: 'var(--muted)' }}>جاري المعالجة...</p>}

      {result && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2>النتيجة</h2>
            <div className="actions">
              <span className="badge badge-published">{result.source || 'ai'}</span>
              <button type="button" className="btn-primary" onClick={saveAsArticle}>حفظ كمقال</button>
            </div>
          </div>
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '0.95rem', lineHeight: 1.7 }}>
            {formatResult(result)}
          </pre>
        </div>
      )}
    </>
  )
}

function formatResult(obj) {
  if (obj.article) {
    const a = obj.article
    const lines = [
      `الموضوع: ${obj.topic}`,
      '',
      '--- المقال ---',
      a.title && `العنوان: ${a.title}`,
      a.introduction && `المقدمة:\n${a.introduction}`,
      a.body && `المحتوى:\n${a.body}`,
      a.conclusion && `الخاتمة:\n${a.conclusion}`,
      a.content && !a.body && a.content,
      a.hashtags?.length && `هاشتاقات: ${a.hashtags.join(' ')}`,
      a.keywords?.length && `كلمات: ${a.keywords.join(', ')}`,
      '',
      '--- SEO ---',
      obj.seo?.meta_title && `Meta: ${obj.seo.meta_title}`,
      obj.seo?.meta_description && `الوصف: ${obj.seo.meta_description}`,
      obj.title_suggestions?.length && `عناوين مقترحة:\n${obj.title_suggestions.map((t, i) => `${i + 1}. ${t}`).join('\n')}`,
    ]
    return lines.filter(Boolean).join('\n')
  }
  if (obj.titles) return obj.titles.map((t, i) => `${i + 1}. ${t}`).join('\n')
  if (obj.summary) return obj.summary
  if (obj.corrected) return obj.corrected
  if (obj.keywords) return obj.keywords.join(', ')
  if (obj.content) return obj.content
  return JSON.stringify(obj, null, 2)
}
